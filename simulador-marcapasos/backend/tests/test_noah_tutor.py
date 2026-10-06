import unittest
from unittest.mock import patch

from noah_tutor import NoahTutor


class NoahTutorTests(unittest.IsolatedAsyncioTestCase):
    async def test_explains_server_simulation_context_without_provider(self) -> None:
        tutor = NoahTutor()
        context = {
            "escenario": "Bloqueo AV III",
            "ppm": 60,
            "corriente_ma": 5.0,
            "sensibilidad_mv": 2.0,
            "captura_exitosa": False,
            "evento": "Fallo de Captura",
            "umbral_ma": 6.0,
            "descripcion": "Escenario de práctica",
        }

        with (
            patch("noah_tutor.NOAH_LLM_BASE_URL", ""),
            patch("noah_tutor.NOAH_LLM_API_KEY", ""),
            patch("noah_tutor.NOAH_LLM_MODEL", ""),
        ):
            answer, mode = await tutor.responder("Explica mi captura", context)

        self.assertEqual(mode, "local")
        self.assertIn("fallo de captura", answer)
        self.assertIn("6.0 mA", answer)
        self.assertIn("no una recomendación clínica", answer)

    async def test_guides_student_through_simulator(self) -> None:
        context = {
            "escenario": "Normal",
            "ppm": 60,
            "corriente_ma": 5.0,
            "sensibilidad_mv": 2.0,
            "captura_exitosa": True,
            "evento": "Captura Exitosa",
            "umbral_ma": 5.0,
            "descripcion": "Referencia",
        }

        answer = NoahTutor._respuesta_local("¿Cómo inicio la simulación?", context)

        self.assertIn("elige un escenario", answer)
        self.assertIn("educativa", answer)

    def test_answers_equipment_scenario_maintenance_and_pacing_questions(self) -> None:
        context = {
            "escenario": "Ausencia de actividad ventricular simulada",
            "ppm": 60,
            "corriente_ma": 5.0,
            "sensibilidad_mv": 2.0,
            "captura_exitosa": True,
            "evento": "PACE",
            "umbral_ma": 5.0,
            "descripcion": "Escenario educativo",
        }

        equipment_answer = NoahTutor._respuesta_local("¿Qué es el Medtronic Model 53401?", context)
        scenario_answer = NoahTutor._respuesta_local("¿Qué escenarios puedo practicar?", context)
        maintenance_answer = NoahTutor._respuesta_local("¿Qué revisa el módulo de mantenimiento?", context)
        pulse_answer = NoahTutor._respuesta_local("¿Por qué no veo un pulso PACE?", context)

        self.assertIn("marcapasos externo temporal monocameral", equipment_answer)
        self.assertIn("Alteración de detección", scenario_answer)
        self.assertIn("No ejecuta pruebas eléctricas", maintenance_answer)
        self.assertIn("confirma que la práctica esté activa", pulse_answer)

    def test_explains_persisted_session_metrics_and_recent_events(self) -> None:
        session = {
            "id_sesion": 18,
            "escenario": "Bloqueo AV III",
            "total_eventos": 4,
            "capturas_exitosas": 2,
            "fallos_captura": 2,
            "porcentaje_captura": 50.0,
            "corriente_minima_ma": 4.0,
            "corriente_maxima_ma": 6.0,
            "primer_evento": {
                "timestamp": "2026-10-01T09:00:00",
                "corriente_ma": 4.0,
            },
            "ultimo_evento": {
                "timestamp": "2026-10-01T09:03:00",
                "corriente_ma": 6.0,
                "evento": "Captura Exitosa",
            },
            "eventos_recientes": [
                {"corriente_ma": 4.0, "captura_exitosa": False},
                {"corriente_ma": 6.0, "captura_exitosa": True},
            ],
            "puntaje_final": 50,
        }

        answer = NoahTutor._explicar_sesion(session, 6.0)

        self.assertIn("sesión #18", answer)
        self.assertIn("2 de 4 eventos terminaron en captura (50.0%)", answer)
        self.assertIn("4.0 a 6.0 mA", answer)
        self.assertIn("50/100", answer)

    def test_distinguishes_session_without_telemetry_from_capture_failure(self) -> None:
        answer = NoahTutor._explicar_sesion({
            "id_sesion": 19,
            "escenario": "Normal",
            "total_eventos": 0,
        }, 5.0)

        self.assertIn("no tiene eventos de telemetría", answer)
        self.assertIn("no equivale a una captura fallida", answer)

    def test_answers_score_question_with_the_session_formula(self) -> None:
        session = {
            "id_sesion": 22,
            "escenario": "Normal",
            "total_eventos": 4,
            "capturas_exitosas": 3,
            "fallos_captura": 1,
            "porcentaje_captura": 75.0,
            "puntaje_final": 75,
        }

        answer = NoahTutor._explicar_sesion(session, 5.0, "¿Por qué obtuve este puntaje?")

        self.assertIn("75/100", answer)
        self.assertIn("3 capturas exitosas de 4 eventos (75.0%)", answer)
        self.assertIn("indicador didáctico", answer)

    def test_answers_current_question_with_observed_threshold_pattern(self) -> None:
        session = {
            "id_sesion": 23,
            "escenario": "Bloqueo AV III",
            "total_eventos": 2,
            "capturas_exitosas": 1,
            "fallos_captura": 1,
            "porcentaje_captura": 50.0,
            "corriente_minima_ma": 4.0,
            "corriente_maxima_ma": 6.0,
            "eventos_recientes": [
                {"corriente_ma": 4.0, "captura_exitosa": False},
                {"corriente_ma": 6.0, "captura_exitosa": True},
            ],
        }

        answer = NoahTutor._explicar_sesion(session, 6.0, "¿Qué pasó con la corriente?")

        self.assertIn("umbral de 6.0 mA", answer)
        self.assertIn("4.0 mA se asociaron a fallo", answer)
        self.assertIn("A 6.0 mA se registró captura", answer)


if __name__ == "__main__":
    unittest.main()