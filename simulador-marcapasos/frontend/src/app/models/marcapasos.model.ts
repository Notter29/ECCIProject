/**
 * Modelos de datos del frontend que reflejan los schemas del backend.
 * Tipado fuerte con TypeScript para seguridad en toda la app.
 */

// ─────────────────────────────────────────────────────────────────────
// ENUMS
// ─────────────────────────────────────────────────────────────────────

export enum EscenarioClinico {
  RitmoSinusal = 'Ritmo sinusal',
  Bradicardia = 'Bradicardia',
  AusenciaActividad = 'Ausencia de actividad ventricular simulada',
  AlteracionDeteccion = 'Alteración de detección',
  // Kept for sessions created by earlier versions of the application.
  BradicardiaSinusal = 'Bradicardia Sinusal',
  BloqueoAVI        = 'Bloqueo AV I',
  BloqueoAVIII      = 'Bloqueo AV III',
  Normal            = 'Normal',
}

// ─────────────────────────────────────────────────────────────────────
// USUARIO
// ─────────────────────────────────────────────────────────────────────

export interface Usuario {
  id_usuario:          number;
  nombre:              string;
  codigo_estudiantil:  string;
  esta_activo:         boolean;
  fecha_registro:      string;
}

export interface LoginRequest {
  codigo_estudiantil: string;
  password:           string;
}

export interface LoginResponse {
  access_token: string;
  token_type:   string;
  usuario:      Usuario;
}

export interface RegistroRequest {
  nombre:             string;
  codigo_estudiantil: string;
  password:           string;
}

// ─────────────────────────────────────────────────────────────────────
// SESIÓN
// ─────────────────────────────────────────────────────────────────────

export interface Sesion {
  id_sesion:      number;
  id_usuario:     number;
  fecha_inicio:   string;
  fecha_fin:      string | null;
  escenario_base: string;
  puntaje_final:  number | null;
}

export interface SesionCrearRequest {
  id_usuario:     number;
  escenario_base: string;
}

export interface HistorialResponse {
  sesiones:                 Sesion[];
  total_sesiones:           number;
  total_capturas_exitosas:  number;
  total_fallos:             number;
}

// ─────────────────────────────────────────────────────────────────────
// TELEMETRÍA Y SIMULACIÓN
// ─────────────────────────────────────────────────────────────────────

export interface TelemetriaRequest {
  id_sesion:       number;
  frecuencia_ppm:  number;
  corriente_ma:    number;
  sensibilidad_mv: number;
}

export interface TelemetriaResponse {
  id_registro:     number;
  id_sesion:       number;
  timestamp:       string;
  frecuencia_ppm:  number;
  corriente_ma:    number;
  sensibilidad_mv: number;
  estado_captura:  boolean;
  evento:          string;
}

export interface ConfiguracionMarcapasos {
  ppm:             number;
  corriente_ma:    number;
  sensibilidad_mv: number;
  escenario:       string;
}

export interface ResultadoSimulacion {
  captura_exitosa: boolean;
  evento:          string;
  ms_por_latido:   number;
  umbral_ma:       number;
  descripcion:     string;
  puntos_onda:     number[];
}

export interface NoahChatRequest {
  pregunta:         string;
  escenario:        string;
  ppm:              number;
  corriente_ma:     number;
  sensibilidad_mv:  number;
  id_sesion?:       number;
}

export interface NoahChatResponse {
  agente:            string;
  respuesta:         string;
  modo:              'llm' | 'local';
  captura_exitosa:   boolean;
  evento:            string;
  umbral_ma:         number;
  fuente:            string;
}

export interface SimulacionCrearRequest {
  id_sesion: number;
  nombre_escenario: string;
  modo: 'VVI' | 'VOO';
  frecuencia_ppm: number;
  corriente_ma: number;
  sensibilidad_mv: number;
  duracion_pulso_ms: 1.5;
}

export interface EventoSimulacionRequest {
  tipo: string;
  descripcion: string;
}

export interface EventoSimulacion {
  id_evento: number;
  id_simulacion: number;
  tipo: string;
  descripcion: string;
  timestamp: string;
}

export interface SimulacionHistorial {
  id_simulacion: number;
  id_sesion: number;
  nombre_escenario: string;
  modo: 'VVI' | 'VOO';
  frecuencia_ppm: number;
  corriente_ma: number;
  sensibilidad_mv: number;
  duracion_pulso_ms: number;
  resultado: string;
  fecha_creacion: string;
  eventos: EventoSimulacion[];
  evidencia_nombre: string | null;
}

export interface GuardarSimulacionRequest {
  modo: 'VVI' | 'VOO';
  frecuencia_ppm: number;
  corriente_ma: number;
  sensibilidad_mv: number;
  resultado: string;
  observaciones: string;
  conclusion: string;
}

// ─────────────────────────────────────────────────────────────────────
// ESTADO LOCAL DEL SIMULADOR (para el componente principal)
// ─────────────────────────────────────────────────────────────────────

export interface EstadoSimulador {
  simulando:       boolean;
  ppm:             number;
  corriente_ma:    number;
  sensibilidad_mv: number;
  escenario:       EscenarioClinico;
  captura_exitosa: boolean;
  evento:          string;
  alarma_activa:   boolean;
}
