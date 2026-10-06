"""Authenticated chat endpoint for the Noah educational tutor."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from database import get_db
from models import ConsultaIA, RegistroTelemetria, SesionSimulacion, Usuario
from schemas import NoahChatRequest, NoahChatResponse
from security import obtener_usuario_actual
from simulacion import ESCENARIOS, evaluar_captura
from noah_tutor import noah_tutor

router = APIRouter(prefix="/noah", tags=["Tutor Noah"])


@router.post("/chat", response_model=NoahChatResponse)
async def conversar_con_noah(
    datos: NoahChatRequest,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
) -> NoahChatResponse:
    """Answers a student question and explains the server-evaluated simulator state."""
    escenario_nombre = datos.escenario
    analisis_sesion = None
    if datos.id_sesion is not None:
        sesion = db.query(SesionSimulacion).filter(
            SesionSimulacion.id_sesion == datos.id_sesion
        ).first()
        if not sesion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró la sesión seleccionada.",
            )
        if sesion.id_usuario != usuario_actual.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede solicitar análisis de una sesión ajena.",
            )
        escenario_nombre = sesion.escenario_base
        analisis_sesion = _resumir_sesion(db, sesion)

    escenario = ESCENARIOS.get(escenario_nombre)
    if not escenario:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El escenario no está disponible en el simulador.",
        )

    corriente_evaluada = datos.corriente_ma
    if analisis_sesion and analisis_sesion["ultimo_evento"]:
        corriente_evaluada = analisis_sesion["ultimo_evento"]["corriente_ma"]
    captura, evento = evaluar_captura(corriente_evaluada, escenario_nombre)
    contexto = {
        "escenario": escenario_nombre,
        "ppm": datos.ppm,
        "corriente_ma": corriente_evaluada,
        "sensibilidad_mv": datos.sensibilidad_mv,
        "captura_exitosa": captura,
        "evento": evento,
        "umbral_ma": escenario["umbral_ma"],
        "descripcion": escenario["descripcion"],
        "analisis_sesion": analisis_sesion,
    }
    respuesta, modo = await noah_tutor.responder(datos.pregunta, contexto)
    fuente = (
        "Contexto de práctica y documentación educativa incorporada"
        if analisis_sesion
        else "Guía de uso del simulador y parámetros definidos en especificaciones.md"
    )
    db.add(
        ConsultaIA(
            id_usuario=usuario_actual.id_usuario,
            pregunta=datos.pregunta,
            respuesta=respuesta,
            fuente=fuente,
        )
    )
    db.commit()
    return NoahChatResponse(
        respuesta=respuesta,
        modo=modo,
        captura_exitosa=captura,
        evento=evento,
        umbral_ma=escenario["umbral_ma"],
        fuente=fuente,
    )


def _resumir_sesion(db: Session, sesion: SesionSimulacion) -> dict:
    """Builds bounded, de-identified facts for Noah from persisted telemetry."""
    summary = db.query(
        func.count(RegistroTelemetria.id_registro),
        func.coalesce(
            func.sum(case((RegistroTelemetria.estado_captura.is_(True), 1), else_=0)),
            0,
        ),
        func.coalesce(
            func.sum(case((RegistroTelemetria.estado_captura.is_(False), 1), else_=0)),
            0,
        ),
        func.min(RegistroTelemetria.corriente_ma),
        func.max(RegistroTelemetria.corriente_ma),
    ).filter(RegistroTelemetria.id_sesion == sesion.id_sesion).one()

    total, successful, failed, min_current, max_current = summary
    first_event = db.query(RegistroTelemetria).filter(
        RegistroTelemetria.id_sesion == sesion.id_sesion
    ).order_by(RegistroTelemetria.timestamp.asc()).first()
    recent_events = db.query(RegistroTelemetria).filter(
        RegistroTelemetria.id_sesion == sesion.id_sesion
    ).order_by(RegistroTelemetria.timestamp.desc()).limit(8).all()
    recent_events.reverse()

    def event_data(record: RegistroTelemetria | None) -> dict | None:
        if record is None:
            return None
        return {
            "timestamp": record.timestamp.isoformat(),
            "frecuencia_ppm": record.frecuencia_ppm,
            "corriente_ma": record.corriente_ma,
            "sensibilidad_mv": record.sensibilidad_mv,
            "captura_exitosa": record.estado_captura,
            "evento": record.evento,
        }

    return {
        "id_sesion": sesion.id_sesion,
        "escenario": sesion.escenario_base,
        "fecha_inicio": sesion.fecha_inicio.isoformat(),
        "fecha_fin": sesion.fecha_fin.isoformat() if sesion.fecha_fin else None,
        "puntaje_final": sesion.puntaje_final,
        "total_eventos": total,
        "capturas_exitosas": successful,
        "fallos_captura": failed,
        "porcentaje_captura": round(successful * 100 / total, 1) if total else None,
        "corriente_minima_ma": min_current,
        "corriente_maxima_ma": max_current,
        "primer_evento": event_data(first_event),
        "ultimo_evento": event_data(recent_events[-1] if recent_events else None),
        "eventos_recientes": [event_data(record) for record in recent_events],
    }