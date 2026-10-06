import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models import Usuario
from security import obtener_usuario_actual


class SimulationApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.session_factory = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        with self.session_factory() as db:
            self.user = Usuario(
                id_usuario=1,
                nombre="Estudiante de prueba",
                codigo_estudiantil="TEST-001",
                password_hash="not-used-by-test",
            )
            db.add(self.user)
            db.commit()

        def test_db():
            db = self.session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = test_db
        app.dependency_overrides[obtener_usuario_actual] = lambda: Usuario(
            id_usuario=1,
            nombre="Estudiante de prueba",
            codigo_estudiantil="TEST-001",
            esta_activo=True,
        )
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_practice_events_are_saved_with_configuration_and_result(self) -> None:
        session_response = self.client.post(
            "/sesiones/",
            json={"id_usuario": 1, "escenario_base": "Ausencia de actividad ventricular simulada"},
        )
        self.assertEqual(session_response.status_code, 201, session_response.text)
        session_id = session_response.json()["id_sesion"]

        simulation_response = self.client.post(
            "/simulaciones/",
            json={
                "id_sesion": session_id,
                "nombre_escenario": "Ausencia de actividad ventricular simulada",
                "modo": "VOO",
                "frecuencia_ppm": 60,
                "corriente_ma": 5.0,
                "sensibilidad_mv": 2.0,
                "duracion_pulso_ms": 1.5,
            },
        )
        self.assertEqual(simulation_response.status_code, 201, simulation_response.text)
        simulation_id = simulation_response.json()["id_simulacion"]

        for event_type, description in (
            ("SISTEMA", "Práctica iniciada"),
            ("PACE", "Pulso virtual visible; respuesta sintética"),
        ):
            event_response = self.client.post(
                f"/simulaciones/{simulation_id}/eventos",
                json={"tipo": event_type, "descripcion": description},
            )
            self.assertEqual(event_response.status_code, 201, event_response.text)

        evidence_bytes = b"\x89PNG\r\n\x1a\neducational-test-image"
        evidence_response = self.client.post(
            f"/simulaciones/{simulation_id}/evidencia",
            files={"file": ("practica.png", evidence_bytes, "image/png")},
        )
        self.assertEqual(evidence_response.status_code, 201, evidence_response.text)
        self.assertEqual(evidence_response.json()["nombre_archivo"], "practica.png")
        download_response = self.client.get(f"/simulaciones/{simulation_id}/evidencia")
        self.assertEqual(download_response.content, evidence_bytes)

        saved = self.client.put(
            f"/simulaciones/{simulation_id}/guardar",
            json={
                "modo": "VOO",
                "frecuencia_ppm": 60,
                "corriente_ma": 5.0,
                "sensibilidad_mv": 2.0,
                "resultado": "Correcto",
                "observaciones": "Se observa un marcador de pulso.",
                "conclusion": "VOO genera pulsos periódicos en el modelo.",
            },
        )
        self.assertEqual(saved.status_code, 200, saved.text)
        self.assertEqual(saved.json()["resultado"], "Correcto")

        history = self.client.get("/simulaciones/historial")
        self.assertEqual(history.status_code, 200, history.text)
        self.assertEqual(len(history.json()), 1)
        self.assertEqual(history.json()[0]["modo"], "VOO")
        self.assertEqual(len(history.json()[0]["eventos"]), 2)
        self.assertEqual(history.json()[0]["evidencia_nombre"], "practica.png")

    def test_noah_answers_mode_question_and_returns_source(self) -> None:
        with (
            patch("noah_tutor.NOAH_LLM_BASE_URL", ""),
            patch("noah_tutor.NOAH_LLM_API_KEY", ""),
            patch("noah_tutor.NOAH_LLM_MODEL", ""),
        ):
            response = self.client.post(
                "/noah/chat",
                json={
                    "pregunta": "¿Qué significa VOO?",
                    "escenario": "Ritmo sinusal",
                    "ppm": 60,
                    "corriente_ma": 5.0,
                    "sensibilidad_mv": 2.0,
                },
            )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["agente"], "Noah")
        self.assertIn("asíncrono", response.json()["respuesta"])
        self.assertTrue(response.json()["fuente"])


if __name__ == "__main__":
    unittest.main()
