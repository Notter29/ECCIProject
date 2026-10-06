"""
Punto de entrada principal de la API REST del simulador didáctico.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from database import Base, engine
from routers import noah, sesiones, simulaciones, telemetria, usuarios

app = FastAPI(
    title="Simulador didáctico de marcapasos",
    description=(
        "Plataforma educativa para simular el comportamiento de un marcapasos externo temporal "
        "Monocameral de referencia Medtronic 53401. No es un dispositivo médico ni se utiliza para diagnóstico o tratamiento."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(usuarios.router)
app.include_router(sesiones.router)
app.include_router(telemetria.router)
app.include_router(simulaciones.router)
app.include_router(noah.router)


@app.get("/", tags=["Estado del servidor"])
def health_check():
    return {
        "estado": "Servidor activo",
        "servicio": "Simulador didáctico de marcapasos",
        "version": "1.0.0",
        "documentacion": "/docs",
        "alcance": "Educativo y académico. No para atención clínica.",
    }
