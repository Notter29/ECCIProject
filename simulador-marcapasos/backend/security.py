"""Hash de contraseñas y autenticación JWT para la API."""
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from config import JWT_SECRET_KEY

password_hasher = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated=["bcrypt"],
    argon2__type="ID",
)
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


def hash_password(password: str) -> str:
    """
    Genera un hash Argon2id de una contraseña en texto plano.

    Args:
        password: Contraseña original del estudiante.

    Returns:
        String hash seguro para almacenar en la base de datos.
    """
    return password_hasher.hash(password)


def verificar_password(password_plano: str, password_hash: str) -> bool:
    """
    Compara una contraseña en texto plano con su hash almacenado.

    Args:
        password_plano: Contraseña ingresada por el usuario en el login.
        password_hash: Hash almacenado en la base de datos.

    Returns:
        True si la contraseña es correcta, False en caso contrario.
    """
    is_valid, _ = verificar_password_y_actualizar(password_plano, password_hash)
    return is_valid


def verificar_password_y_actualizar(
    password_plano: str, password_hash: str
) -> tuple[bool, str | None]:
    """Verifica un hash heredado y devuelve un hash Argon2id si debe migrarse."""
    if password_hash.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            import bcrypt
            if bcrypt.checkpw(password_plano.encode("utf-8"), password_hash.encode("utf-8")):
                return True, hash_password(password_plano)
            return False, None
        except Exception:
            return False, None
    if not password_hasher.identify(password_hash):
        return False, None
    try:
        return password_hasher.verify_and_update(password_plano, password_hash)
    except (ValueError, TypeError):
        return False, None


def crear_access_token(usuario: Usuario) -> str:
    """Firma un JWT de acceso corto; en producción configure JWT_SECRET_KEY."""
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario.id_usuario),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    """Valida el bearer token y resuelve el estudiante autenticado."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas o vencidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized

    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario or not usuario.esta_activo:
        raise unauthorized
    return usuario
