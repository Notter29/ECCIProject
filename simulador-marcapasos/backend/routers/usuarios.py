"""
Rutas de la API para gestión de usuarios (RF-01: Autenticación).
Contiene endpoints para registro e inicio de sesión de estudiantes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from schemas import UsuarioCrear, UsuarioRespuesta, UsuarioLogin, TokenRespuesta
from security import (
    crear_access_token,
    hash_password,
    obtener_usuario_actual,
    verificar_password_y_actualizar,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/registro", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_estudiante(datos: UsuarioCrear, db: Session = Depends(get_db)):
    """
    Registra un nuevo estudiante en el sistema.
    Verifica que el código estudiantil no esté duplicado y encripta la contraseña.
    Implementa: RF-01, RNF-16.
    """
    # Verificar si el código ya existe
    usuario_existente = db.query(Usuario).filter(
        Usuario.codigo_estudiantil == datos.codigo_estudiantil
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El código estudiantil '{datos.codigo_estudiantil}' ya está registrado."
        )

    # Crear el usuario con la contraseña encriptada
    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        codigo_estudiantil=datos.codigo_estudiantil,
        password_hash=hash_password(datos.password),
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.post("/login", response_model=TokenRespuesta)
def iniciar_sesion(credenciales: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Autentica a un estudiante con su código y contraseña.
    Devuelve información del usuario y un token simple de sesión.
    Implementa: RF-01.
    """
    usuario = db.query(Usuario).filter(
        Usuario.codigo_estudiantil == credenciales.codigo_estudiantil
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código estudiantil o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_valida, hash_actualizado = verificar_password_y_actualizar(
        credenciales.password, usuario.password_hash
    )
    if not password_valida:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código estudiantil o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta del estudiante está desactivada."
        )

    if hash_actualizado:
        usuario.password_hash = hash_actualizado
        db.commit()

    return TokenRespuesta(
        access_token=crear_access_token(usuario),
        token_type="bearer",
        usuario=usuario,
    )


@router.get("/{id_usuario}", response_model=UsuarioRespuesta)
def obtener_estudiante(
    id_usuario: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Obtiene el perfil público de un estudiante por su ID.
    """
    if usuario_actual.id_usuario != id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede consultar el perfil de otro estudiante.",
        )

    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el estudiante con ID {id_usuario}."
        )

    return usuario
