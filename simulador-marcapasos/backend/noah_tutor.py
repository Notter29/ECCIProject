"""Educational assistant for the GALIX PACESTAR simulator."""
import asyncio
import json
from typing import Any

import httpx

from config import (
    NOAH_LLM_API_KEY,
    NOAH_LLM_BASE_URL,
    NOAH_LLM_MODEL,
    NOAH_MAX_CONCURRENT_REQUESTS,
)

SYSTEM_PROMPT = """You are Noah, a patient educational tutor for biomedical engineering students.
Answer only from the supplied project specification, approved educational content, and synthetic simulation context.
Use natural Spanish, answer the student's exact question first, define units, and distinguish model output from clinical truth.
Avoid repeated greetings, generic praise, canned closings, and restating the same metric more than once.
When session analysis is present, explain its measured counts, capture percentage, scenario threshold,
and first/recent parameter records. Cite those concrete values and timestamps; do not give generic praise,
invent waveform details, or infer events that were not recorded. State when there is no telemetry.
Never browse the internet, recommend treatment or settings for a real patient, diagnose, or invent facts absent from context.
If asked for clinical advice, refuse that part and redirect to the instructor and validated clinical sources.
If the supplied context does not support an answer, say: "La información solicitada no se encuentra en la documentación incorporada al sistema."
Always state that this is an academic simulation, not a medical device or clinical decision tool."""


class NoahTutor:
    """Uses an optional OpenAI-compatible provider with a safe local fallback."""

    def __init__(self) -> None:
        self._provider_slots = asyncio.Semaphore(NOAH_MAX_CONCURRENT_REQUESTS)

    async def responder(self, pregunta: str, contexto: dict[str, Any]) -> tuple[str, str]:
        base_url = NOAH_LLM_BASE_URL
        api_key = NOAH_LLM_API_KEY
        model = NOAH_LLM_MODEL
        if not (base_url and api_key and model):
            return self._respuesta_local(pregunta, contexto), "local"

        payload = {
            "model": model,
            "temperature": 0.2,
            "max_tokens": 450,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"pregunta": pregunta, "simulacion": contexto},
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        acquired = False
        try:
            await asyncio.wait_for(self._provider_slots.acquire(), timeout=0.5)
            acquired = True
            async with httpx.AsyncClient(timeout=httpx.Timeout(12.0)) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                )
                response.raise_for_status()
                answer = response.json()["choices"][0]["message"]["content"]
                if isinstance(answer, str) and answer.strip():
                    return answer.strip(), "llm"
        except (asyncio.TimeoutError, httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
            pass
        finally:
            if acquired:
                self._provider_slots.release()
        return self._respuesta_local(pregunta, contexto), "local"

    @staticmethod
    def _respuesta_local(pregunta: str, contexto: dict[str, Any]) -> str:
        session = contexto.get("analisis_sesion")
        if session is not None:
            return NoahTutor._explicar_sesion(session, contexto["umbral_ma"], pregunta)

        normalized = pregunta.casefold()
        if any(word in normalized for word in ("paciente", "diagnóstico", "diagnostico", "tratamiento", "terapia", "dosis")):
            return (
                "No puedo diagnosticar ni recomendar tratamiento o parámetros para una persona. "
                "Puedo explicar únicamente el comportamiento de esta práctica sintética; consulta al docente "
                "y a fuentes clínicas validadas para asuntos asistenciales. Esta aplicación es académica, "
                "no un dispositivo médico."
            )
        if any(word in normalized for word in ("53401", "medtronic", "equipo", "fabricante", "qué es ", "que es ")):
            return (
                "Medtronic Model 53401 es el equipo de referencia indicado en la documentación del proyecto: "
                "un marcapasos externo temporal monocameral. El equipo físico contempla más modos, pero este "
                "software académico solo representa estimulación ventricular VVI y VOO."
            )
        if any(word in normalized for word in ("mantenimiento", "inspección", "inspeccion", "batería", "bateria", "cables", "conector")):
            return (
                "El módulo de mantenimiento es una lista educativa para revisar elementos como carcasa, "
                "controles, indicadores, baterías, conexiones y cables. No ejecuta pruebas eléctricas ni "
                "certifica un equipo; para instrucciones y advertencias específicas consulta la guía oficial "
                "del fabricante y al docente."
            )
        if "escenario" in normalized:
            return (
                "Puedes elegir Ritmo sinusal, Bradicardia, Ausencia de actividad ventricular simulada o "
                "Alteración de detección. Son escenarios matemáticos educativos: cada uno genera distinta "
                "actividad sintética para observar ECG, SENSE y PACE; no son ritmos clínicos."
            )
        if "vvi" in normalized and "voo" in normalized:
            return (
                "En este simulador, VVI representa estimulación ventricular a demanda: la actividad "
                "ventricular sintética detectada inhibe el pulso hasta el siguiente intervalo configurado. "
                "VOO representa estimulación ventricular asíncrona periódica y no usa detección para inhibir. "
                "Son modelos didácticos, no una reproducción de todos los algoritmos del equipo real."
            )
        if "vvi" in normalized:
            return (
                "VVI es el modo ventricular a demanda representado aquí: el modelo observa la actividad "
                "sintética; si la detecta, inhibe el pulso, y si transcurre el intervalo de RATE sin detección, "
                "genera un PACE virtual."
            )
        if "voo" in normalized:
            return (
                "VOO es el modo ventricular asíncrono de esta práctica: genera pulsos virtuales periódicos "
                "según RATE sin utilizar SENSE para inhibirlos."
            )
        if "sense" in normalized or "pace" in normalized or "pulso" in normalized:
            return (
                "PACE marca un pulso de estimulación virtual. SENSE indica que el modelo detectó actividad "
                "ventricular sintética en VVI; una detección inhibe el pulso programado. En VOO la detección "
                "no gobierna la estimulación. Si no ves una marca PACE, confirma que la práctica esté activa "
                "y considera que en VVI la actividad detectada inhibe el pulso hasta el siguiente intervalo "
                "RATE. Los indicadores son gráficos y educativos."
            )
        if "sensibilidad" in normalized or "sensitivity" in normalized:
            return (
                f"La sensibilidad actual es {contexto['sensibilidad_mv']} mV. En este modelo educativo, "
                "un umbral configurado menor representa mayor sensibilidad de detección: se compara con la "
                "amplitud sintética del escenario. La regla es simplificada y no equivale a una recomendación clínica."
            )
        if "output" in normalized or "salida" in normalized or "corriente" in normalized:
            estado_salida = "respuesta virtual habilitada" if contexto["captura_exitosa"] else "sin respuesta ventricular dibujada"
            return (
                f"OUTPUT es la salida virtual y está configurada en {contexto['corriente_ma']} mA. "
                f"En la regla pedagógica incorporada, el resultado actual es {estado_salida}; "
                f"el umbral interno del modelo es {contexto['umbral_ma']} mA. No es una salida eléctrica "
                "ni un umbral clínico."
            )
        if "rate" in normalized or "frecuencia" in normalized:
            return (
                f"RATE está configurada en {contexto['ppm']} ppm, es decir, pulsos virtuales por minuto. "
                "El valor determina el intervalo del temporizador de estimulación en el modelo. "
                "La señal es sintética y no sirve para ajustar un dispositivo real."
            )
        if "duración" in normalized or "duracion" in normalized or "pulse width" in normalized:
            return (
                "La duración del pulso se presenta fija en 1,5 ms según la especificación académica "
                "del proyecto; no se modifica en esta primera versión."
            )
        if "ecg" in normalized or "onda" in normalized or "señal" in normalized or "senal" in normalized:
            return (
                "El ECG que ves es una curva sintética generada por el simulador. La marca amarilla en la "
                "misma escala temporal representa un PACE virtual; el QRS dibujado después depende de la "
                "regla educativa de captura. No es una señal clínica ni debe interpretarse como tal."
            )
        if any(word in normalized for word in ("usar", "paso", "iniciar", "empez", "ajust", "como", "cómo")):
            return (
                "Para comenzar, elige un escenario de simulación educativa, selecciona VVI o VOO, revisa "
                "RATE (ppm), OUTPUT (mA virtual) y SENSITIVITY (mV), y pulsa Iniciar práctica. Cambia un "
                "parámetro a la vez y observa "
                "la onda y el indicador de captura; detén la práctica para cambiar de escenario. "
                "Usa Guardar simulación para registrar eventos y escribe tu propia conclusión. "
                "La señal es sintética y la herramienta es exclusivamente educativa."
            )
        if any(word in normalized for word in ("cegamiento", "blanking", "refractario")):
            return (
                "Según el manual técnico del Medtronic 53401, los períodos de cegamiento evitan la sobredetección: "
                "200 ms (+5/-30 ms) tras un evento estimulado (PACE) y 120 ms (+2/-30 ms) tras un evento detectado (SENSE). "
                "Durante este intervalo, el circuito de detección ignora despolarizaciones secundarias."
            )
        if any(word in normalized for word in ("sobredetección", "oversensing", "sobre detección")):
            return (
                "La sobredetección (oversensing) ocurre cuando el marcapasos detecta señales indeseadas "
                "(ondas T, miopotenciales o ruido EMI), resultando en subestimulación (under pacing). "
                "En la guía de resolución de problemas de Medtronic, la solución es girar el dial de SENSITIVITY "
                "en sentido horario para aumentar el valor en mV (hacer el equipo menos sensible)."
            )
        if any(word in normalized for word in ("subdetección", "undersensing", "sub detección")):
            return (
                "La subdetección (undersensing) ocurre cuando el marcapasos no 've' los latidos intrínsecos del paciente "
                "debido a un umbral de sensibilidad demasiado alto (mV elevado), emitiendo impulsos asíncronos a destiempo (over pacing). "
                "La solución es girar el dial de SENSITIVITY en sentido antihorario para reducir el valor en mV (mayor sensibilidad) "
                "hasta lograr un margen de seguridad 2:1."
            )
        if "pérdida de captura" in normalized or "loss of capture" in normalized or "perdidadecaptura" in normalized:
            return (
                "La pérdida de captura (loss of capture) ocurre cuando la espiga PACE se entrega pero no provoca la "
                "despolarización miocárdica (complejo QRS). En la guía Medtronic, se soluciona verificando conexiones de cables "
                "y aumentando el dial de OUTPUT (mA) hasta superar el umbral de estimulación con un margen de seguridad 2:1."
            )
        if any(word in normalized for word in ("limpieza", "desinfección", "desinfeccion", "alcohol", "autoclave")):
            return (
                "Según el manual de mantenimiento oficial del Medtronic 53401: debe limpiarse con toallitas de alcohol isopropílico al 70%. "
                "Para desinfección, requiere 15 min de exposición húmeda envuelto en paño húmedo dentro de una bolsa sellada. "
                "Está PROHIBIDO usar acetona, éteres, solventes clorados, máquinas lavadoras automáticas o autoclave (vapor/gas)."
            )
        if any(word in normalized for word in ("compatibilidad", "emc", "norma", "iec", "esd", "electromagnética", "electromagnetica")):
            return (
                "El Medtronic 53401 cumple con la norma IEC 60601-1-2:2007/AC:2010 y CISPR 11 Clase A. "
                "Posee inmunidad a descargas electrostáticas (ESD ±6 kV contacto, ±8 kV aire) y está diseñado para operar con "
                "cables de paciente de la familia 5433 y cables quirúrgicos 5832/5846."
            )
        if any(word in normalized for word in ("potencial", "biológico", "biologico", "nodo", "fase", "purkinje", "his", "naspe", "bpeg")):
            return (
                "Según los fundamentos biológicos del TFG del marcapasos: el potencial de membrana en reposo es ~ -90 mV. "
                "El potencial de acción consta de 5 fases: Fase 0 (despolarización rápida por Na+), Fase 1 (repolarización inicial), "
                "Fase 2 (meseta por Ca2+), Fase 3 (repolarización rápida por K+) y Fase 4 (reposo por bomba Na+/K+-ATPasa). "
                "El sistema de conducción va desde el Nódulo SA -> Nódulo AV -> Haz de His -> Fibras de Purkinje. "
                "El código NASPE/BPEG define VVI (Ventrículo estimulado, Ventrículo sensado, Inhibición por sensado)."
            )
        if any(word in normalized for word in ("captura", "umbral", "resultado", "simul")):
            estado = "captura exitosa" if contexto["captura_exitosa"] else "fallo de captura"
            return (
                f"En esta simulación de {contexto['escenario']}, el evento calculado es {estado}. "
                f"La salida virtual configurada es {contexto['corriente_ma']} mA y el umbral didáctico "
                f"interno es {contexto['umbral_ma']} mA; {contexto['descripcion']}. "
                "Compara esos valores y cambia un parámetro a la vez para observar su efecto. "
                "Es una regla del modelo académico, no una recomendación clínica."
            )
        return (
            "La información solicitada no se encuentra en la documentación incorporada al sistema. "
            "Puedo guiarte sobre VVI/VOO, RATE, OUTPUT, SENSITIVITY, ECG, PACE, SENSE, cegamiento (blanking), "
            "resolución de problemas (oversensing, undersensing, pérdida de captura), limpieza y compatibilidad EMC; "
            "para otros temas, consulta al docente. Esta herramienta es académica, no clínica."
        )

    @staticmethod
    def _explicar_sesion(
        session: dict[str, Any], umbral_ma: float, pregunta: str = ""
    ) -> str:
        total = session["total_eventos"]
        session_id = session["id_sesion"]
        scenario = session["escenario"]
        if total == 0:
            return (
                f"La sesión #{session_id} ({scenario}) no tiene eventos de telemetría guardados, "
                "así que no hay cambios de PPM, corriente o sensibilidad que pueda explicar ni una "
                "tasa de captura que calcular. Una sesión sin registros no equivale a una captura fallida. "
                "El modelo es académico y no representa una evaluación clínica."
            )

        successful = session["capturas_exitosas"]
        failed = session["fallos_captura"]
        rate = session["porcentaje_captura"]
        first = session.get("primer_evento")
        last = session.get("ultimo_evento")
        recent = session.get("eventos_recientes", [])
        failed_currents = list(dict.fromkeys(
            event["corriente_ma"] for event in recent if not event["captura_exitosa"]
        ))
        successful_currents = list(dict.fromkeys(
            event["corriente_ma"] for event in recent if event["captura_exitosa"]
        ))

        normalized_question = pregunta.casefold()
        if "puntaje" in normalized_question or "nota" in normalized_question:
            if session["puntaje_final"] is None:
                return (
                    f"La sesión #{session_id} sigue sin puntaje final porque aún no está cerrada. "
                    f"Hasta ahora hay {successful} capturas exitosas de {total} eventos ({rate}%). "
                    "Al finalizar, el modelo convierte esa proporción en un puntaje de 0 a 100."
                )
            return (
                f"La sesión #{session_id} terminó con {session['puntaje_final']}/100. "
                f"Ese valor corresponde a {successful} capturas exitosas de {total} eventos "
                f"({rate}%); los otros {failed} eventos quedaron como fallos según la regla del escenario. "
                "Es un indicador didáctico de esta práctica, no una calificación clínica."
            )

        if any(word in normalized_question for word in ("umbral", "corriente", "ma")):
            explanation = (
                f"En la sesión #{session_id}, el escenario {scenario} usa un umbral de {umbral_ma} mA. "
                f"Los valores registrados estuvieron entre {session['corriente_minima_ma']} y "
                f"{session['corriente_maxima_ma']} mA."
            )
            if failed_currents:
                explanation += f" En los eventos recientes, {', '.join(map(str, failed_currents))} mA se asociaron a fallo."
            if successful_currents:
                explanation += f" A {', '.join(map(str, successful_currents))} mA se registró captura."
            return explanation + " La interpretación aplica solo al modelo académico de esta práctica."

        if any(word in normalized_question for word in ("patrón", "cambio", "tiempo", "primero", "último")):
            if first and last:
                return (
                    f"El primer evento de la sesión #{session_id} fue {first['evento']} con "
                    f"{first['corriente_ma']} mA; el último fue {last['evento']} con "
                    f"{last['corriente_ma']} mA. En los {total} registros hubo {successful} capturas "
                    f"y {failed} fallos. El umbral de {scenario} es {umbral_ma} mA, así que el cambio "
                    "de corriente cruzó la regla que usa el simulador."
                )

        lines = [
            f"Revisé la sesión #{session_id} de {scenario}: {successful} de {total} eventos terminaron "
            f"en captura ({rate}%) y {failed} en fallo.",
            f"La corriente fue de {session['corriente_minima_ma']} a {session['corriente_maxima_ma']} mA; "
            f"el umbral didáctico es {umbral_ma} mA.",
        ]
        if failed_currents:
            lines.append(
                f"Los registros recientes con fallo incluyen {', '.join(map(str, failed_currents))} mA."
            )
        if successful_currents:
            lines.append(
                f"Los registros recientes con captura incluyen {', '.join(map(str, successful_currents))} mA."
            )
        if session["puntaje_final"] is not None:
            lines.append(f"El puntaje guardado al finalizar fue {session['puntaje_final']}/100.")

        lines.append(
            "Para estudiar el patrón, compara cada evento con el umbral y revisa qué cambió "
            "entre el primer y el último registro. Esta explicación usa solo telemetría guardada; "
            "no sustituye supervisión docente ni criterio clínico."
        )
        return " ".join(lines)


noah_tutor = NoahTutor()