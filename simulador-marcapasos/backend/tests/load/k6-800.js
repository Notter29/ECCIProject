import http from 'k6/http';
import { check, sleep } from 'k6';

const api = __ENV.API_URL || 'http://127.0.0.1:8000';
const students = JSON.parse(open(__ENV.TOKEN_FILE || './student-tokens.json'));

export const options = {
  scenarios: {
    classroom: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { target: 800, duration: '5m' },
        { target: 800, duration: '20m' },
        { target: 0, duration: '2m' },
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{service:core}': ['p(95)<500', 'p(99)<1500'],
  },
};

export function setup() {
  if (students.length < 800) {
    throw new Error('TOKEN_FILE debe contener al menos 800 usuarios sintéticos.');
  }
  return { students };
}

let sessionId;

export default function (data) {
  const student = data.students[(__VU - 1) % data.students.length];
  const scenario = __VU % 2 === 0 ? 'Bloqueo AV III' : 'Bradicardia Sinusal';
  const current = 5.5;
  const headers = {
    Authorization: `Bearer ${student.token}`,
    'Content-Type': 'application/json',
  };

  if (!sessionId) {
    const sessionResponse = http.post(
      `${api}/sesiones/`,
      JSON.stringify({ id_usuario: student.userId, escenario_base: scenario }),
      { headers, tags: { service: 'core', name: 'create-session' } },
    );
    if (!check(sessionResponse, { 'session created': (response) => response.status === 201 })) {
      sleep(3);
      return;
    }
    sessionId = sessionResponse.json('id_sesion');
  }

  http.post(
    `${api}/telemetria/`,
    JSON.stringify({
      id_sesion: sessionId,
      frecuencia_ppm: 60,
      corriente_ma: current,
      sensibilidad_mv: 2,
    }),
    { headers, tags: { service: 'core', name: 'telemetry' } },
  );

  http.get(`${api}/sesiones/historial/${student.userId}`, {
    headers,
    tags: { service: 'core', name: 'history' },
  });

  if (__ITER % 10 === 0) {
    http.post(
      `${api}/noah/chat`,
      JSON.stringify({
        pregunta: 'Explica el resultado de esta simulación',
        escenario: scenario,
        ppm: 60,
        corriente_ma: current,
        sensibilidad_mv: 2,
      }),
      { headers, tags: { service: 'noah', name: 'noah-chat' } },
    );
  }

  sleep(3);
}
