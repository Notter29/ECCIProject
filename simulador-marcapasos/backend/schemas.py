"""
Schemas de Pydantic para validación de datos de entrada/salida en la API.
Separa los modelos de red de los modelos ORM de base de datos.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────
# SCHEMAS DE USUARIO
# ─────────────────────────────────────────────────────────────────────

class UsuarioCrear(BaseModel):
    """Datos necesarios para registrar un nuevo estudiante."""
    nombre: str = Field(..., min_length=3, max_length=100, examples=["Andrés Torres"])
    codigo_estudiantil: str = Field(..., min_length=3, max_length=20, examples=["EST-2024-001"])
    password: str = Field(..., min_length=12, max_length=128, examples=["Frase-segura-para-laboratorio"])


class UsuarioLogin(BaseModel):
    """Credenciales para autenticación."""
    codigo_estudiantil: str
    password: str = Field(..., min_length=1, max_length=128)


class UsuarioRespuesta(BaseModel):
    """Datos públicos del usuario (nunca expone el hash)."""
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nombre: str
    codigo_estudiantil: str
    esta_activo: bool
    fecha_registro: datetime


# ─────────────────────────────────────────────────────────────────────
# SCHEMAS DE SESIÓN
# ─────────────────────────────────────────────────────────────────────

class SesionCrear(BaseModel):
    """Datos para iniciar una nueva sesión de simulación."""
    id_usuario: int
    escenario_base: str = Field(
        ...,
        examples=["Bradicardia Sinusal"],
        description="Uno de: Bradicardia Sinusal, Bloqueo AV I, Bloqueo AV III, Normal"
    )


class SesionRespuesta(BaseModel):
    """Respuesta al crear o consultar una sesión."""
    model_config = ConfigDict(from_attributes=True)

    id_sesion: int
    id_usuario: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    escenario_base: str
    puntaje_final: Optional[int]


# ─────────────────────────────────────────────────────────────────────
# SCHEMAS DE TELEMETRÍA
# ─────────────────────────────────────────────────────────────────────

class TelemetriaCrear(BaseModel):
    """
    Datos enviados por el frontend cada vez que el estudiante
    cambia un parámetro del marcapasos (PPM, mA o mV).
    """
    id_sesion: int
    frecuencia_ppm: int = Field(..., ge=30, le=200, description="Pulsos por minuto (30-200)")
    corriente_ma: float = Field(..., ge=0.1, le=25.0, description="Salida virtual en mA (0.1-25)")
    sensibilidad_mv: float = Field(..., ge=0.4, le=20.0, description="Sensibilidad en mV (0.4-20)")


class TelemetriaRespuesta(BaseModel):
    """Respuesta al registrar un evento de telemetría."""
    model_config = ConfigDict(from_attributes=True)

    id_registro: int
    id_sesion: int
    timestamp: datetime
    frecuencia_ppm: int
    corriente_ma: float
    sensibilidad_mv: float
    estado_captura: bool
    evento: str


# ─────────────────────────────────────────────────────────────────────
# SCHEMAS DE SIMULACIÓN (Motor de Cálculo)
# ─────────────────────────────────────────────────────────────────────

class ConfiguracionMarcapasos(BaseModel):
    """Parámetros enviados al motor de simulación para calcular la onda."""
    ppm: int = Field(..., ge=30, le=200)
    corriente_ma: float = Field(..., ge=0.1, le=25.0)
    sensibilidad_mv: float = Field(..., ge=0.4, le=20.0)
    escenario: str = Field(default="Bradicardia Sinusal")


class ResultadoSimulacion(BaseModel):
    """Resultado calculado por el motor fisiológico del backend."""
    captura_exitosa: bool
    evento: str
    ms_por_latido: float
    umbral_ma: float
    descripcion: str
    puntos_onda: List[float]  # Array de puntos Y para dibujar en el canvas


# ─────────────────────────────────────────────────────────────────────
# SCHEMAS GENERALES
# ─────────────────────────────────────────────────────────────────────

class TokenRespuesta(BaseModel):
    """Token JWT devuelto tras autenticación exitosa."""
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRespuesta


class HistorialRespuesta(BaseModel):
    """Historial completo de sesiones de un estudiante."""
    sesiones: List[SesionRespuesta]
    total_sesiones: int
    total_capturas_exitosas: int
    total_fallos: int


class NoahChatRequest(BaseModel):
    """Pregunta y estado actual opcional de una sesión histórica propia."""
    pregunta: str = Field(..., min_length=1, max_length=1500)
    escenario: str = Field(..., min_length=1, max_length=50)
    ppm: int = Field(..., ge=30, le=200)
    corriente_ma: float = Field(..., ge=0.1, le=25.0)
    sensibilidad_mv: float = Field(..., ge=0.4, le=20.0)
    id_sesion: Optional[int] = Field(default=None, gt=0)


class NoahChatResponse(BaseModel):
    """Respuesta educativa del agente Noah y datos calculados por el servidor."""
    agente: str = "Noah"
    respuesta: str
    modo: str
    captura_exitosa: bool
    evento: str
    umbral_ma: float
    fuente: str = "Documentación educativa incorporada y estado de la simulación"


class SimulacionCrear(BaseModel):
    id_sesion: int = Field(..., gt=0)
    nombre_escenario: str = Field(..., min_length=1, max_length=100)
    modo: str = Field(..., pattern="^(VVI|VOO)$")
    frecuencia_ppm: int = Field(..., ge=30, le=200)
    corriente_ma: float = Field(..., ge=0.1, le=25.0)
    sensibilidad_mv: float = Field(..., ge=0.4, le=20.0)
    duracion_pulso_ms: float = Field(default=1.5, ge=1.5, le=1.5)


class EventoSimulacionCrear(BaseModel):
    tipo: str = Field(..., min_length=1, max_length=80)
    descripcion: str = Field(..., min_length=1, max_length=1000)


class EventoSimulacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_evento: int
    id_simulacion: int
    tipo: str
    descripcion: str
    timestamp: datetime


class SimulacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_simulacion: int
    id_sesion: int
    nombre_escenario: str
    modo: str
    frecuencia_ppm: int
    corriente_ma: float
    sensibilidad_mv: float
    duracion_pulso_ms: float
    resultado: str
    fecha_creacion: datetime


class GuardarSimulacion(BaseModel):
    modo: str = Field(..., pattern="^(VVI|VOO)$")
    frecuencia_ppm: int = Field(..., ge=30, le=200)
    corriente_ma: float = Field(..., ge=0.1, le=25.0)
    sensibilidad_mv: float = Field(..., ge=0.4, le=20.0)
    resultado: str = Field(..., min_length=1, max_length=120)
    observaciones: str = Field(default="", max_length=2000)
    conclusion: str = Field(..., min_length=1, max_length=2000)


class SimulacionHistorialRespuesta(SimulacionRespuesta):
    eventos: List[EventoSimulacionRespuesta] = Field(default_factory=list)
    evidencia_nombre: Optional[str] = None


class EvidenciaPracticaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_evidencia: int
    id_simulacion: int
    nombre_archivo: str
    tipo_contenido: str
    fecha_subida: datetime
