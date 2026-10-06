"""
Motor de simulación educativa del marcapasos.
Contiene reglas sintéticas para calcular:
  - Si hay captura exitosa o fallo de captura
  - Los puntos matemáticos de la onda ECG para cada escenario
  - El umbral dinámico de corriente según el escenario clínico
"""
import math
from typing import List


# ─────────────────────────────────────────────────────────────────────
# Regla interna simplificada del modelo educativo; no es un dato clínico.
# ─────────────────────────────────────────────────────────────────────

UMBRAL_MA_CAPTURA = 5.0

ESCENARIOS = {
    "Ritmo sinusal": {
        "ppm_base": 72,
        "descripcion": "Actividad ventricular regular generada por el escenario educativo.",
        "umbral_ma": 5.0,
        "frecuencia_intrinseca": 72,
        "amplitud_intrinseca_mv": 3.5,
    },
    "Bradicardia": {
        "ppm_base": 35,
        "descripcion": "Actividad ventricular lenta generada por el escenario educativo.",
        "umbral_ma": 5.0,
        "frecuencia_intrinseca": 35,
        "amplitud_intrinseca_mv": 3.5,
    },
    "Ausencia de actividad ventricular simulada": {
        "ppm_base": 0,
        "descripcion": "El escenario no genera eventos ventriculares intrínsecos.",
        "umbral_ma": 5.0,
        "frecuencia_intrinseca": 0,
        "amplitud_intrinseca_mv": 0.0,
    },
    "Alteración de detección": {
        "ppm_base": 60,
        "descripcion": "Escenario educativo con señal de baja amplitud para observar el efecto del control de sensibilidad.",
        "umbral_ma": 5.0,
        "frecuencia_intrinseca": 60,
        "amplitud_intrinseca_mv": 1.0,
    },
    # Legacy names remain accepted for previously saved sessions and API clients.
    "Bradicardia Sinusal": {
        "ppm_base": 40,
        "descripcion": "Escenario educativo legado de actividad ventricular lenta.",
        "umbral_ma": 5.0,
        "frecuencia_intrinseca": 35,
        "amplitud_intrinseca_mv": 3.5,
    },
    "Bloqueo AV I": {
        "ppm_base": 60,
        "descripcion": "Escenario educativo legado con actividad ventricular regular.",
        "umbral_ma": 5.0,
        "frecuencia_intrinseca": 60,
        "amplitud_intrinseca_mv": 3.5,
    },
    "Bloqueo AV III": {
        "ppm_base": 30,
        "descripcion": "Escenario educativo legado con actividad ventricular lenta.",
        "umbral_ma": 5.0,
        "frecuencia_intrinseca": 30,
        "amplitud_intrinseca_mv": 3.5,
    },
    "Normal": {
        "ppm_base": 75,
        "descripcion": "Escenario educativo legado de actividad ventricular regular.",
        "umbral_ma": 5.0,
        "frecuencia_intrinseca": 75,
        "amplitud_intrinseca_mv": 3.5,
    },
}


def evaluar_captura(corriente_ma: float, escenario: str) -> tuple[bool, str]:
    """
    Evalúa la regla virtual de respuesta definida para esta simulación educativa.

    Args:
        corriente_ma: Corriente de salida configurada en mA.
        escenario: Nombre del escenario educativo activo.

    Returns:
        Tupla (captura_exitosa: bool, descripcion_evento: str)
    """
    umbral = ESCENARIOS.get(escenario, ESCENARIOS["Normal"])["umbral_ma"]

    if corriente_ma >= umbral:
        return True, "Captura Exitosa"
    else:
        return False, "Fallo de Captura"


def calcular_ms_por_latido(ppm: int) -> float:
    """
    Convierte PPM a milisegundos por latido.
    Fórmula: ms = 60,000 / PPM

    Args:
        ppm: Frecuencia de estimulación en pulsos por minuto.

    Returns:
        Milisegundos entre cada latido.
    """
    if ppm <= 0:
        raise ValueError("Los PPM deben ser mayores a 0.")
    return 60_000.0 / ppm


def generar_onda_ecg(
    ppm: int,
    corriente_ma: float,
    sensibilidad_mv: float,
    escenario: str,
    num_puntos: int = 300,
) -> List[float]:
    """
    Genera matemáticamente los puntos Y de la onda ECG completa para un ciclo.
    Simula: Espiga → (QRS si captura) → T wave → línea base.

    El algoritmo usa funciones matemáticas para dibujar una forma de onda
    sintética, que no debe interpretarse como una señal clínica real.

    Args:
        ppm: Pulsos por minuto.
        corriente_ma: Corriente de salida en mA.
        sensibilidad_mv: Sensibilidad del sensor en mV.
        escenario: Nombre del escenario educativo.
        num_puntos: Cantidad de puntos del array de salida.

    Returns:
        Lista de valores Y (en unidades de pantalla) para renderizar en el canvas.
    """
    captura, _ = evaluar_captura(corriente_ma, escenario)
    puntos: List[float] = []

    # This threshold is an invented rule of the educational model, not a clinical value.
    amplitud_qrs = 80.0 if captura else 0.0  # Si no hay captura, no hay respuesta ventricular
    amplitud_espiga = -150.0                  # Espiga siempre visible (artefacto del marcapasos)
    ruido_base = min(sensibilidad_mv, 20.0) * 0.15

    # Posiciones relativas de los eventos dentro del ciclo normalizado [0, 1]
    pos_espiga = 0.05       # La espiga aparece al 5% del ciclo
    pos_qrs = 0.12          # El QRS estimulado comienza al 12%
    pos_onda_t = 0.40       # La onda T aparece al 40%

    for i in range(num_puntos):
        t = i / num_puntos  # Tiempo normalizado [0, 1]
        y = 0.0

        # 1. Espiga del marcapasos (pulso vertical angosto)
        delta_espiga = t - pos_espiga
        y += amplitud_espiga * math.exp(-(delta_espiga ** 2) / (2 * 0.0003 ** 2))

        if captura:
            # 2. Onda Q (deflexión negativa pequeña antes del QRS)
            delta_q = t - (pos_qrs - 0.02)
            y += -amplitud_qrs * 0.15 * math.exp(-(delta_q ** 2) / (2 * 0.003 ** 2))

            # 3. Complejo QRS (onda R ancha — marcapasos genera QRS más amplio que el sinusal)
            delta_qrs = t - pos_qrs
            y += amplitud_qrs * math.exp(-(delta_qrs ** 2) / (2 * 0.006 ** 2))

            # 4. Onda S (deflexión negativa tras el QRS)
            delta_s = t - (pos_qrs + 0.03)
            y += -amplitud_qrs * 0.25 * math.exp(-(delta_s ** 2) / (2 * 0.004 ** 2))

            # 5. Onda T (repolarización ventricular)
            delta_t = t - pos_onda_t
            y += amplitud_qrs * 0.35 * math.exp(-(delta_t ** 2) / (2 * 0.02 ** 2))

        # 6. Ruido eléctrico de base (realismo del monitor biomédico)
        y += math.sin(i * 12.9898) * ruido_base

        puntos.append(round(y, 3))

    return puntos


def calcular_puntaje_sesion(total_registros: int, capturas_exitosas: int) -> int:
    """
    Calcula un puntaje educativo para la sesión finalizada (0-100).
    Premia al estudiante por mantener captura exitosa.

    Args:
        total_registros: Total de eventos registrados en la sesión.
        capturas_exitosas: Cuántos de esos eventos tuvieron captura exitosa.

    Returns:
        Puntaje entero entre 0 y 100.
    """
    if total_registros == 0:
        return 0
    porcentaje = capturas_exitosas / total_registros
    return min(100, int(porcentaje * 100))
