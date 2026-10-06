"""Authenticated persistence endpoints for educational simulator practices."""
import re
from io import BytesIO
from datetime import datetime, timezone
from pathlib import PurePath

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import (
    EvidenciaPractica,
    EventoSimulacion,
    PruebaFuncional,
    RegistroTelemetria,
    SesionSimulacion,
    Simulacion,
    Usuario,
)
from schemas import (
    EventoSimulacionCrear,
    EventoSimulacionRespuesta,
    EvidenciaPracticaRespuesta,
    GuardarSimulacion,
    SimulacionCrear,
    SimulacionHistorialRespuesta,
    SimulacionRespuesta,
)
from security import obtener_usuario_actual
from simulacion import ESCENARIOS, calcular_puntaje_sesion, evaluar_captura

router = APIRouter(prefix="/simulaciones", tags=["Prácticas"])
MAX_EVIDENCE_BYTES = 5 * 1024 * 1024
IMAGE_SIGNATURES = {
    "image/jpeg": lambda content: content.startswith(b"\xff\xd8\xff"),
    "image/png": lambda content: content.startswith(b"\x89PNG\r\n\x1a\n"),
    "image/webp": lambda content: len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP",
}


def _get_owned_simulation(
    simulation_id: int, user: Usuario, db: Session
) -> Simulacion:
    simulation = (
        db.query(Simulacion)
        .join(SesionSimulacion)
        .filter(
            Simulacion.id_simulacion == simulation_id,
            SesionSimulacion.id_usuario == user.id_usuario,
        )
        .first()
    )
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la práctica solicitada.",
        )
    return simulation


@router.post("/", response_model=SimulacionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_simulacion(
    datos: SimulacionCrear,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
) -> Simulacion:
    sesion = (
        db.query(SesionSimulacion)
        .filter(SesionSimulacion.id_sesion == datos.id_sesion)
        .first()
    )
    if not sesion:
        raise HTTPException(status_code=404, detail="No se encontró la sesión.")
    if sesion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=403, detail="La sesión no pertenece al usuario.")
    if sesion.fecha_fin:
        raise HTTPException(status_code=409, detail="La sesión ya fue finalizada.")
    if datos.nombre_escenario not in ESCENARIOS:
        raise HTTPException(status_code=422, detail="El escenario no está disponible.")

    simulation = Simulacion(
        id_sesion=sesion.id_sesion,
        nombre_escenario=datos.nombre_escenario,
        modo=datos.modo,
        frecuencia_ppm=datos.frecuencia_ppm,
        corriente_ma=datos.corriente_ma,
        sensibilidad_mv=datos.sensibilidad_mv,
        duracion_pulso_ms=1.5,
        resultado="En curso",
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    return simulation


@router.post(
    "/{simulation_id}/eventos",
    response_model=EventoSimulacionRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_evento(
    simulation_id: int,
    datos: EventoSimulacionCrear,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
) -> EventoSimulacion:
    simulation = _get_owned_simulation(simulation_id, usuario_actual, db)
    session = simulation.sesion
    if session.fecha_fin:
        raise HTTPException(status_code=409, detail="La sesión ya fue finalizada.")

    event = EventoSimulacion(
        id_simulacion=simulation_id,
        tipo=datos.tipo,
        descripcion=datos.descripcion,
    )
    db.add(event)

    if datos.tipo == "PACE":
        captured, label = evaluar_captura(
            simulation.corriente_ma, simulation.nombre_escenario
        )
        db.add(
            RegistroTelemetria(
                id_sesion=session.id_sesion,
                frecuencia_ppm=simulation.frecuencia_ppm,
                corriente_ma=simulation.corriente_ma,
                sensibilidad_mv=simulation.sensibilidad_mv,
                estado_captura=captured,
                evento=label,
            )
        )

    db.commit()
    db.refresh(event)
    return event


@router.put("/{simulation_id}/guardar", response_model=SimulacionRespuesta)
def guardar_simulacion(
    simulation_id: int,
    datos: GuardarSimulacion,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
) -> Simulacion:
    simulation = _get_owned_simulation(simulation_id, usuario_actual, db)
    session = simulation.sesion
    if session.fecha_fin:
        raise HTTPException(status_code=409, detail="La práctica ya fue guardada.")

    simulation.modo = datos.modo
    simulation.frecuencia_ppm = datos.frecuencia_ppm
    simulation.corriente_ma = datos.corriente_ma
    simulation.sensibilidad_mv = datos.sensibilidad_mv
    simulation.resultado = datos.resultado

    total = (
        db.query(RegistroTelemetria)
        .filter(RegistroTelemetria.id_sesion == session.id_sesion)
        .count()
    )
    captures = (
        db.query(RegistroTelemetria)
        .filter(
            RegistroTelemetria.id_sesion == session.id_sesion,
            RegistroTelemetria.estado_captura.is_(True),
        )
        .count()
    )
    session.fecha_fin = datetime.now(timezone.utc)
    session.puntaje_final = calcular_puntaje_sesion(total, captures)
    db.add(
        PruebaFuncional(
            id_simulacion=simulation.id_simulacion,
            nombre="Práctica de simulación",
            resultado=datos.resultado,
            aprobado=datos.resultado == "Correcto",
            observaciones=(
                f"Observaciones: {datos.observaciones.strip() or 'Sin observaciones.'}\n"
                f"Conclusión del estudiante: {datos.conclusion.strip()}"
            ),
        )
    )
    db.commit()
    db.refresh(simulation)
    return simulation


@router.post(
    "/{simulation_id}/evidencia",
    response_model=EvidenciaPracticaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
async def subir_evidencia(
    simulation_id: int,
    file: UploadFile = File(...),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
) -> EvidenciaPractica:
    simulation = _get_owned_simulation(simulation_id, usuario_actual, db)
    if simulation.sesion.fecha_fin:
        raise HTTPException(status_code=409, detail="La práctica ya fue guardada.")
    content_type = file.content_type or ""
    signature_check = IMAGE_SIGNATURES.get(content_type)
    if not signature_check:
        raise HTTPException(
            status_code=415,
            detail="La evidencia debe ser una imagen JPEG, PNG o WebP.",
        )
    content = await file.read(MAX_EVIDENCE_BYTES + 1)
    if len(content) > MAX_EVIDENCE_BYTES:
        raise HTTPException(status_code=413, detail="La imagen supera el límite de 5 MB.")
    if not signature_check(content):
        raise HTTPException(
            status_code=415,
            detail="El contenido del archivo no coincide con su formato de imagen.",
        )

    raw_name = PurePath((file.filename or "evidencia").replace("\\", "/")).name
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", raw_name)[:255] or "evidencia"
    evidence = (
        db.query(EvidenciaPractica)
        .filter(EvidenciaPractica.id_simulacion == simulation_id)
        .first()
    )
    if evidence is None:
        evidence = EvidenciaPractica(id_simulacion=simulation_id)
        db.add(evidence)
    evidence.nombre_archivo = safe_name
    evidence.tipo_contenido = content_type
    evidence.contenido = content
    db.commit()
    db.refresh(evidence)
    await file.close()
    return evidence


@router.get("/{simulation_id}/evidencia")
def descargar_evidencia(
    simulation_id: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    simulation = _get_owned_simulation(simulation_id, usuario_actual, db)
    evidence = (
        db.query(EvidenciaPractica)
        .filter(EvidenciaPractica.id_simulacion == simulation_id)
        .first()
    )
    if evidence is None:
        raise HTTPException(status_code=404, detail="La práctica no tiene evidencia adjunta.")
    return StreamingResponse(
        BytesIO(evidence.contenido),
        media_type=evidence.tipo_contenido,
        headers={
            "Content-Disposition": f'attachment; filename="{evidence.nombre_archivo}"'
        },
    )


@router.get("/historial", response_model=list[SimulacionHistorialRespuesta])
def obtener_historial(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
) -> list[Simulacion]:
    return (
        db.query(Simulacion)
        .join(SesionSimulacion)
        .options(joinedload(Simulacion.eventos))
        .filter(SesionSimulacion.id_usuario == usuario_actual.id_usuario)
        .order_by(Simulacion.fecha_creacion.desc())
        .all()
    )
