/**
 * Servicio principal de comunicación con la API del Simulador de Marcapasos.
 * Encapsula todas las llamadas HTTP, separando la lógica de red de los componentes.
 * Patrón: Service Layer — los componentes NUNCA llaman a HttpClient directamente.
 */
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

import {
  LoginRequest, LoginResponse, RegistroRequest, Usuario,
  SesionCrearRequest, Sesion, HistorialResponse,
  TelemetriaRequest, TelemetriaResponse,
  ConfiguracionMarcapasos, ResultadoSimulacion,
  NoahChatRequest, NoahChatResponse, SimulacionCrearRequest,
  EventoSimulacionRequest, EventoSimulacion, SimulacionHistorial,
  GuardarSimulacionRequest,
} from '../models/marcapasos.model';

@Injectable({
  providedIn: 'root',
})
export class MarcapasosService {
  private readonly apiUrl = environment.apiBaseUrl;

  private http = inject(HttpClient);

  // ─────────────────────────────────────────────────────────────────
  // USUARIOS (RF-01)
  // ─────────────────────────────────────────────────────────────────

  /** Registra un nuevo estudiante en el sistema */
  registrarEstudiante(datos: RegistroRequest): Observable<Usuario> {
    return this.http.post<Usuario>(`${this.apiUrl}/usuarios/registro`, datos)
      .pipe(catchError(this.manejarError));
  }

  /** Autentica al estudiante con código y contraseña */
  login(credenciales: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/usuarios/login`, credenciales)
      .pipe(catchError(this.manejarError));
  }

  /** Obtiene el perfil de un estudiante por ID */
  obtenerEstudiante(idUsuario: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/usuarios/${idUsuario}`)
      .pipe(catchError(this.manejarError));
  }

  // ─────────────────────────────────────────────────────────────────
  // SESIONES (RF-02, RF-13)
  // ─────────────────────────────────────────────────────────────────

  /** Inicia una nueva sesión de simulación */
  crearSesion(datos: SesionCrearRequest): Observable<Sesion> {
    return this.http.post<Sesion>(`${this.apiUrl}/sesiones/`, datos)
      .pipe(catchError(this.manejarError));
  }

  /** Finaliza una sesión y calcula el puntaje */
  finalizarSesion(idSesion: number): Observable<Sesion> {
    return this.http.put<Sesion>(`${this.apiUrl}/sesiones/${idSesion}/finalizar`, {})
      .pipe(catchError(this.manejarError));
  }

  /** Obtiene el historial de prácticas de un estudiante */
  obtenerHistorial(idUsuario: number): Observable<HistorialResponse> {
    return this.http.get<HistorialResponse>(`${this.apiUrl}/sesiones/historial/${idUsuario}`)
      .pipe(catchError(this.manejarError));
  }

  // ─────────────────────────────────────────────────────────────────
  // TELEMETRÍA Y SIMULACIÓN (RF-03 a RF-12)
  // ─────────────────────────────────────────────────────────────────

  /** Registra un evento de telemetría (cambio de parámetro) en la BD */
  registrarTelemetria(datos: TelemetriaRequest): Observable<TelemetriaResponse> {
    return this.http.post<TelemetriaResponse>(`${this.apiUrl}/telemetria/`, datos)
      .pipe(catchError(this.manejarError));
  }

  /**
   * Llama al motor de simulación del backend para obtener:
   * - Si hubo captura exitosa o fallo
   * - Los puntos matemáticos de la onda ECG
   * No guarda en base de datos — es solo cálculo.
   */
  calcularSimulacion(config: ConfiguracionMarcapasos): Observable<ResultadoSimulacion> {
    return this.http.post<ResultadoSimulacion>(`${this.apiUrl}/telemetria/simular`, config)
      .pipe(catchError(this.manejarError));
  }

  /** Obtiene todos los registros de telemetría de una sesión */
  obtenerTelemetriaSesion(idSesion: number): Observable<TelemetriaResponse[]> {
    return this.http.get<TelemetriaResponse[]>(`${this.apiUrl}/telemetria/sesion/${idSesion}`)
      .pipe(catchError(this.manejarError));
  }

  /** Consulta al tutor educativo Noah con la configuración visible del simulador. */
  consultarNoah(datos: NoahChatRequest): Observable<NoahChatResponse> {
    return this.http.post<NoahChatResponse>(`${this.apiUrl}/noah/chat`, datos)
      .pipe(catchError(this.manejarError));
  }

  crearSimulacion(datos: SimulacionCrearRequest): Observable<SimulacionHistorial> {
    return this.http.post<SimulacionHistorial>(`${this.apiUrl}/simulaciones/`, datos)
      .pipe(catchError(this.manejarError));
  }

  registrarEventoSimulacion(
    idSimulacion: number,
    datos: EventoSimulacionRequest,
  ): Observable<EventoSimulacion> {
    return this.http.post<EventoSimulacion>(
      `${this.apiUrl}/simulaciones/${idSimulacion}/eventos`,
      datos,
    ).pipe(catchError(this.manejarError));
  }

  guardarSimulacion(
    idSimulacion: number,
    datos: GuardarSimulacionRequest,
  ): Observable<SimulacionHistorial> {
    return this.http.put<SimulacionHistorial>(
      `${this.apiUrl}/simulaciones/${idSimulacion}/guardar`,
      datos,
    ).pipe(catchError(this.manejarError));
  }

  obtenerHistorialSimulaciones(): Observable<SimulacionHistorial[]> {
    return this.http.get<SimulacionHistorial[]>(`${this.apiUrl}/simulaciones/historial`)
      .pipe(catchError(this.manejarError));
  }

  subirEvidencia(idSimulacion: number, archivo: File): Observable<{
    id_evidencia: number;
    id_simulacion: number;
    nombre_archivo: string;
    tipo_contenido: string;
    fecha_subida: string;
  }> {
    const formData = new FormData();
    formData.append('file', archivo, archivo.name);
    return this.http.post<{
      id_evidencia: number;
      id_simulacion: number;
      nombre_archivo: string;
      tipo_contenido: string;
      fecha_subida: string;
    }>(`${this.apiUrl}/simulaciones/${idSimulacion}/evidencia`, formData)
      .pipe(catchError(this.manejarError));
  }

  descargarEvidencia(idSimulacion: number): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/simulaciones/${idSimulacion}/evidencia`,
      { responseType: 'blob' },
    ).pipe(catchError(this.manejarError));
  }

  // ─────────────────────────────────────────────────────────────────
  // MANEJO CENTRALIZADO DE ERRORES HTTP
  // ─────────────────────────────────────────────────────────────────

  private manejarError(error: HttpErrorResponse): Observable<never> {
    let mensaje = 'Error desconocido.';

    if (error.status === 0) {
      mensaje = '❌ No se puede conectar al servidor. ¿Está el backend corriendo en el puerto 8000?';
    } else if (error.status === 401) {
      mensaje = '🔒 Credenciales incorrectas.';
    } else if (error.status === 404) {
      mensaje = '🔍 Recurso no encontrado.';
    } else if (error.status === 409) {
      mensaje = `⚠️ Conflicto: ${this.detalleError(error.error?.detail) || 'Ya existe este recurso.'}`;
    } else if (error.status === 422) {
      mensaje = this.detalleValidacion(error.error?.detail);
    } else if (error.error?.detail) {
      mensaje = `Error del servidor: ${this.detalleError(error.error.detail)}`;
    }

    console.error('[MarcapasosService]', error);
    return throwError(() => new Error(mensaje));
  }

  private detalleError(detail: unknown): string {
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return this.detalleValidacion(detail);
    return '';
  }

  private detalleValidacion(detail: unknown): string {
    if (!Array.isArray(detail)) {
      return 'Revisa los datos ingresados. La contraseña debe tener al menos 12 caracteres.';
    }

    const errors = detail.map((item: unknown) => {
      if (!item || typeof item !== 'object') return '';
      const issue = item as { loc?: unknown; type?: unknown };
      const location = Array.isArray(issue.loc) ? issue.loc[issue.loc.length - 1] : '';
      if (location === 'password' && issue.type === 'string_too_short') {
        return 'La contraseña debe tener al menos 12 caracteres.';
      }
      if (location === 'nombre' && issue.type === 'string_too_short') {
        return 'El nombre debe tener al menos 3 caracteres.';
      }
      if (location === 'codigo_estudiantil' && issue.type === 'string_too_short') {
        return 'El código estudiantil debe tener al menos 3 caracteres.';
      }
      return '';
    }).filter(Boolean);

    return errors.length ? errors.join(' ') : 'Revisa los datos ingresados.';
  }
}
