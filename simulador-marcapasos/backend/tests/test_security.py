import unittest
from datetime import datetime, timezone

import jwt
from passlib.context import CryptContext

from models import Usuario
from security import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    crear_access_token,
    hash_password,
    verificar_password_y_actualizar,
)


class SecurityTests(unittest.TestCase):
    def test_new_passwords_use_argon2id(self) -> None:
        password = "Frase-segura-ECCI-2026"
        hashed = hash_password(password)

        self.assertTrue(hashed.startswith("$argon2id$"))
        self.assertEqual(verificar_password_y_actualizar(password, hashed), (True, None))
        self.assertFalse(verificar_password_y_actualizar("incorrecta", hashed)[0])

    def test_legacy_bcrypt_hash_is_upgraded_after_verification(self) -> None:
        password = "Frase-segura-ECCI-2026"
        # Valid bcrypt hash for 'Frase-segura-ECCI-2026'
        legacy_hash = "$2b$12$Bi6kgXdN11IAJcAD717D7OpmsnH1TD83zRSoFkIDZ6Q9ymnOUoPqm"


        valid, upgraded_hash = verificar_password_y_actualizar(password, legacy_hash)

        self.assertTrue(valid)
        self.assertIsNotNone(upgraded_hash)
        self.assertTrue(upgraded_hash.startswith("$argon2id$"))

    def test_access_token_is_signed_and_expires(self) -> None:
        user = Usuario(id_usuario=27, codigo_estudiantil="ECCI-027")
        token = crear_access_token(user)

        claims = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        self.assertEqual(claims["sub"], "27")
        self.assertGreater(claims["exp"], datetime.now(timezone.utc).timestamp())


if __name__ == "__main__":
    unittest.main()
