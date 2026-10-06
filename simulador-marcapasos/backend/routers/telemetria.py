"""
Rutas de la API para telemetría y simulación en tiempo real.
Implementa RF-03 a RF-11 (parámetros, ECG, captura, fallo, alarmas).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import RegistroTelemetria, SesionSimulacion, Usuario
from schemas import TelemetriaCrear, TelemetriaRespuesta, ConfiguracionMarcapasos, ResultadoSimulacion
from simulacion import (
    evaluar_captura,
    calcular_ms_por_latido,
    generar_onda_ecg,
    ESCENARIOS,
)
from security import obtener_usuario_actual

router = APIRouter(prefix="/telemetria", tags=["Telemetría y Simulación"])


@router.post("/", response_model=TelemetriaRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_telemetria(
    datos: TelemetriaCrear,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Guarda un evento de telemetría cuando el estudiante cambia un parámetro.
    Determina automáticamente si hubo captura exitosa o fallo de captura.
    Implementa: RF-03, RF-04, RF-05, RF-09, RF-10, RF-12.
    """
    # Verificar que la sesión existe
    sesion = db.query(SesionSimulacion).filter(
        SesionSimulacion.id_sesion == datos.id_sesion
    ).first()

    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la sesión con ID {datos.id_sesion}."
        )

    if sesion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede registrar telemetría en sesiones de otro estudiante.",
        )

    if sesion.fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede registrar telemetría en una sesión ya finalizada."
        )

    # Calcular el evento médico basado en la lógica del motor
    captura, evento = evaluar_captura(datos.corriente_ma, sesion.escenario_base)

    nuevo_registro = RegistroTelemetria(
        id_sesion=datos.id_sesion,
        frecuencia_ppm=datos.frecuencia_ppm,
        corriente_ma=datos.corriente_ma,
        sensibilidad_mv=datos.sensibilidad_mv,
        estado_captura=captura,
        evento=evento,
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)

    return nuevo_registro


@router.post("/simular", response_model=ResultadoSimulacion)
def calcular_simulacion(
    config: ConfiguracionMarcapasos,
    _: Usuario = Depends(obtener_usuario_actual),
):
    """
    Motor de simulación: recibe los parámetros del marcapasos y devuelve
    la evaluación médica y los puntos matemáticos de la onda ECG.
    Este endpoint NO guarda en la base de datos, es solo de cálculo.
    Implementa: RF-07, RF-08, RF-09, RF-10, RNF-15.
    """
    captura, evento = evaluar_captura(config.corriente_ma, config.escenario)
    ms_latido = calcular_ms_por_latido(config.ppm)
    puntos = generar_onda_ecg(
        ppm=config.ppm,
        corriente_ma=config.corriente_ma,
        sensibilidad_mv=config.sensibilidad_mv,
        escenario=config.escenario,
    )

    escenario_info = ESCENARIOS.get(config.escenario, ESCENARIOS["Normal"])
    umbral = escenario_info["umbral_ma"]
    descripcion = escenario_info["descripcion"]

    return ResultadoSimulacion(
        captura_exitosa=captura,
        evento=evento,
        ms_por_latido=ms_latido,
        umbral_ma=umbral,
        descripcion=descripcion,
        puntos_onda=puntos,
    )


@router.get("/sesion/{id_sesion}", response_model=List[TelemetriaRespuesta])
def obtener_telemetria_sesion(
    id_sesion: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Devuelve todos los eventos de telemetría registrados en una sesión.
    Implementa: RF-13.
    """
    sesion = db.query(SesionSimulacion).filter(
        SesionSimulacion.id_sesion == id_sesion
    ).first()
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la sesión con ID {id_sesion}.",
        )
    if sesion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede consultar telemetría de otro estudiante.",
        )

    registros = db.query(RegistroTelemetria).filter(
        RegistroTelemetria.id_sesion == id_sesion
    ).order_by(RegistroTelemetria.timestamp.asc()).all()

    return registros
