"""
Rutas de la API para gestión de sesiones de simulación.
Implementa RF-12 (Registro en Base de Datos) y RF-13 (Historial de Prácticas).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from models import SesionSimulacion, RegistroTelemetria, Usuario
from schemas import SesionCrear, SesionRespuesta, HistorialRespuesta
from simulacion import calcular_puntaje_sesion, ESCENARIOS
from security import obtener_usuario_actual

router = APIRouter(prefix="/sesiones", tags=["Sesiones"])


@router.post("/", response_model=SesionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_sesion(
    datos: SesionCrear,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Inicia una nueva sesión de simulación para un estudiante.
    Valida que el escenario clínico sea válido y que el usuario exista.
    Implementa: RF-02, RF-12.
    """
    if datos.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede crear sesiones para otro estudiante.",
        )

    # Validar que el escenario clínico sea uno de los soportados
    if datos.escenario_base not in ESCENARIOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Escenario '{datos.escenario_base}' no válido. Opciones: {list(ESCENARIOS.keys())}"
        )

    nueva_sesion = SesionSimulacion(
        id_usuario=datos.id_usuario,
        escenario_base=datos.escenario_base,
    )
    db.add(nueva_sesion)
    db.commit()
    db.refresh(nueva_sesion)

    return nueva_sesion


@router.put("/{id_sesion}/finalizar", response_model=SesionRespuesta)
def finalizar_sesion(
    id_sesion: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Cierra una sesión activa, calcula el puntaje final y lo persiste.
    Implementa: RF-13, RF-14.
    """
    sesion = db.query(SesionSimulacion).filter(SesionSimulacion.id_sesion == id_sesion).first()

    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la sesión con ID {id_sesion}."
        )

    if sesion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede finalizar sesiones de otro estudiante.",
        )

    if sesion.fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta sesión ya fue finalizada."
        )

    # Calcular puntaje según desempeño del estudiante
    total = db.query(RegistroTelemetria).filter(
        RegistroTelemetria.id_sesion == id_sesion
    ).count()
    exitosas = db.query(RegistroTelemetria).filter(
        RegistroTelemetria.id_sesion == id_sesion,
        RegistroTelemetria.estado_captura == True
    ).count()

    sesion.fecha_fin = datetime.now(timezone.utc)
    sesion.puntaje_final = calcular_puntaje_sesion(total, exitosas)

    db.commit()
    db.refresh(sesion)

    return sesion


@router.get("/historial/{id_usuario}", response_model=HistorialRespuesta)
def obtener_historial(
    id_usuario: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Devuelve el historial completo de prácticas de un estudiante.
    Implementa: RF-13.
    """
    if id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede consultar el historial de otro estudiante.",
        )

    sesiones = db.query(SesionSimulacion).filter(
        SesionSimulacion.id_usuario == id_usuario
    ).order_by(SesionSimulacion.fecha_inicio.desc()).all()

    # Estadísticas globales del estudiante
    total_capturas = db.query(RegistroTelemetria).join(SesionSimulacion).filter(
        SesionSimulacion.id_usuario == id_usuario,
        RegistroTelemetria.estado_captura == True
    ).count()

    total_fallos = db.query(RegistroTelemetria).join(SesionSimulacion).filter(
        SesionSimulacion.id_usuario == id_usuario,
        RegistroTelemetria.estado_captura == False
    ).count()

    return HistorialRespuesta(
        sesiones=sesiones,
        total_sesiones=len(sesiones),
        total_capturas_exitosas=total_capturas,
        total_fallos=total_fallos,
    )
