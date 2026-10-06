"""
Modelos ORM del simulador educativo de marcapasos.
Incluye la base de usuarios, sesiones, simulaciones, telemetría y documentación técnica.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    codigo_estudiantil = Column(String(30), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    esta_activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sesiones = relationship("SesionSimulacion", back_populates="estudiante", cascade="all, delete-orphan")


class SesionSimulacion(Base):
    __tablename__ = "sesiones"

    id_sesion = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_inicio = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_fin = Column(DateTime, nullable=True)
    escenario_base = Column(String(100), nullable=False)
    puntaje_final = Column(Integer, nullable=True)

    estudiante = relationship("Usuario", back_populates="sesiones")
    registros = relationship("RegistroTelemetria", back_populates="sesion", cascade="all, delete-orphan")
    simulaciones = relationship("Simulacion", back_populates="sesion", cascade="all, delete-orphan")


class RegistroTelemetria(Base):
    __tablename__ = "telemetria"

    id_registro = Column(Integer, primary_key=True, index=True)
    id_sesion = Column(Integer, ForeignKey("sesiones.id_sesion"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    frecuencia_ppm = Column(Integer, nullable=False)
    corriente_ma = Column(Float, nullable=False)
    sensibilidad_mv = Column(Float, nullable=False)
    estado_captura = Column(Boolean, nullable=False)
    evento = Column(String(80), nullable=False)

    sesion = relationship("SesionSimulacion", back_populates="registros")


class Simulacion(Base):
    __tablename__ = "simulaciones"

    id_simulacion = Column(Integer, primary_key=True, index=True)
    id_sesion = Column(Integer, ForeignKey("sesiones.id_sesion"), nullable=False)
    nombre_escenario = Column(String(100), nullable=False)
    modo = Column(String(20), nullable=False, default="VVI")
    frecuencia_ppm = Column(Integer, nullable=False)
    corriente_ma = Column(Float, nullable=False)
    sensibilidad_mv = Column(Float, nullable=False)
    duracion_pulso_ms = Column(Float, nullable=False)
    resultado = Column(String(120), nullable=False, default="No definido")
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sesion = relationship("SesionSimulacion", back_populates="simulaciones")
    eventos = relationship("EventoSimulacion", back_populates="simulacion", cascade="all, delete-orphan")
    pruebas = relationship("PruebaFuncional", back_populates="simulacion", cascade="all, delete-orphan")
    evidencia = relationship(
        "EvidenciaPractica",
        back_populates="simulacion",
        cascade="all, delete-orphan",
        uselist=False,
    )

    @property
    def evidencia_nombre(self) -> str | None:
        return self.evidencia.nombre_archivo if self.evidencia else None


class EventoSimulacion(Base):
    __tablename__ = "eventos"

    id_evento = Column(Integer, primary_key=True, index=True)
    id_simulacion = Column(Integer, ForeignKey("simulaciones.id_simulacion"), nullable=False)
    tipo = Column(String(80), nullable=False)
    descripcion = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    simulacion = relationship("Simulacion", back_populates="eventos")


class PruebaFuncional(Base):
    __tablename__ = "pruebas"

    id_prueba = Column(Integer, primary_key=True, index=True)
    id_simulacion = Column(Integer, ForeignKey("simulaciones.id_simulacion"), nullable=False)
    nombre = Column(String(100), nullable=False)
    resultado = Column(String(120), nullable=False)
    aprobado = Column(Boolean, default=False)
    observaciones = Column(Text, nullable=True)

    simulacion = relationship("Simulacion", back_populates="pruebas")


class EvidenciaPractica(Base):
    __tablename__ = "evidencias_practica"

    id_evidencia = Column(Integer, primary_key=True, index=True)
    id_simulacion = Column(
        Integer,
        ForeignKey("simulaciones.id_simulacion"),
        nullable=False,
        unique=True,
    )
    nombre_archivo = Column(String(255), nullable=False)
    tipo_contenido = Column(String(80), nullable=False)
    contenido = Column(LargeBinary, nullable=False)
    fecha_subida = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    simulacion = relationship("Simulacion", back_populates="evidencia")


class DocumentoReferencia(Base):
    __tablename__ = "documentos"

    id_documento = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    categoria = Column(String(60), nullable=False)
    contenido = Column(Text, nullable=False)
    url_referencia = Column(String(255), nullable=True)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ConsultaIA(Base):
    __tablename__ = "consultas_ia"

    id_consulta = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    pregunta = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=False)
    fuente = Column(String(120), default="documentacion_aprobada")
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    usuario = relationship("Usuario")
