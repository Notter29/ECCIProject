/**
 * COMPONENTE 3: Historial de Sesiones
 * ─────────────────────────────────────────────────────────────────────
 * Muestra el historial de prácticas de laboratorio del estudiante:
 *   - Lista de sesiones con fecha, escenario y puntaje (RF-13)
 *   - Estadísticas globales: total de capturas exitosas vs fallos
 *   - Retroalimentación educativa con tips según el desempeño (RF-14)
 *   - Botón para cargar el historial desde el backend
 *
 * Es un componente "contenedor" (smart): llama directamente al servicio
 * y gestiona su propio estado de carga.
 */
import {
  Component, EventEmitter, Input, OnChanges, Output, SimpleChanges,
  ChangeDetectionStrategy, ChangeDetectorRef, inject,
} from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { MarcapasosService } from '../../services/marcapasos';
import { HistorialResponse, Sesion, TelemetriaResponse } from '../../models/marcapasos.model';

@Component({
  selector: 'app-historial-sesiones',
  standalone: true,
  imports: [CommonModule, DatePipe],
  templateUrl: './historial-sesiones.html',
  styleUrls:   ['./historial-sesiones.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HistorialSesionesComponent implements OnChanges {

  // ── INPUT ──────────────────────────────────────────────────────────
  /** ID del usuario autenticado — cuando cambia, recarga el historial */
  @Input() idUsuario: number | null = null;
  @Output() explicarSesion = new EventEmitter<Sesion>();

  // ── ESTADO INTERNO ────────────────────────────────────────────────
  historial: HistorialResponse | null = null;
  cargando  = false;
  error     = '';
  sesionSeleccionada: Sesion | null = null;
  registrosSesion: TelemetriaResponse[] = [];
  cargandoTelemetria = false;
  errorTelemetria = '';

  private svc = inject(MarcapasosService);
  private cdr = inject(ChangeDetectorRef);

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['idUsuario'] && this.idUsuario !== null) {
      this.cargarHistorial();
    }
  }

  // ── CARGA DE DATOS ────────────────────────────────────────────────

  cargarHistorial(): void {
    if (!this.idUsuario) return;

    this.sesionSeleccionada = null;
    this.registrosSesion = [];
    this.cargando = true;
    this.error    = '';
    this.cdr.markForCheck();

    this.svc.obtenerHistorial(this.idUsuario).subscribe({
      next: (data) => {
        this.historial = data;
        this.cargando  = false;
        this.cdr.markForCheck();
      },
      error: (err: Error) => {
        this.error    = err.message;
        this.cargando = false;
        this.cdr.markForCheck();
      },
    });
  }

  seleccionarSesion(sesion: Sesion): void {
    this.sesionSeleccionada = sesion;
    this.registrosSesion = [];
    this.cargandoTelemetria = true;
    this.errorTelemetria = '';
    this.cdr.markForCheck();

    this.svc.obtenerTelemetriaSesion(sesion.id_sesion).subscribe({
      next: (registros) => {
        this.registrosSesion = registros;
        this.cargandoTelemetria = false;
        this.cdr.markForCheck();
      },
      error: (err: Error) => {
        this.errorTelemetria = err.message;
        this.cargandoTelemetria = false;
        this.cdr.markForCheck();
      },
    });
  }

  solicitarExplicacion(): void {
    if (this.sesionSeleccionada) {
      this.explicarSesion.emit(this.sesionSeleccionada);
    }
  }

  get porcentajeCapturasSesion(): number {
    if (this.registrosSesion.length === 0) return 0;
    const exitosas = this.registrosSesion.filter((registro) => registro.estado_captura).length;
    return Math.round((exitosas / this.registrosSesion.length) * 100);
  }

  get capturasSesion(): number {
    return this.registrosSesion.filter((registro) => registro.estado_captura).length;
  }

  get fallosSesion(): number {
    return this.registrosSesion.length - this.capturasSesion;
  }

  // ── HELPERS DE VISUALIZACIÓN ──────────────────────────────────────

  /** Porcentaje de capturas exitosas (para la barra de progreso) */
  get porcentajeExito(): number {
    if (!this.historial) return 0;
    const total = this.historial.total_capturas_exitosas + this.historial.total_fallos;
    return total === 0 ? 0 : Math.round((this.historial.total_capturas_exitosas / total) * 100);
  }

  /** Tip educativo basado en el desempeño del estudiante (RF-14) */
  get tipEducativo(): string {
    const pct = this.porcentajeExito;
    if (pct >= 90) return '🏆 Excelente dominio del umbral de captura. Prueba el escenario Bloqueo AV III.';
    if (pct >= 70) return '📚 Buen progreso. Recuerda: a mayor impedancia del electrodo, mayor corriente necesaria.';
    if (pct >= 50) return '💡 Tip: El umbral de 5 mA es el mínimo de seguridad. Usa margen de ×2 en clínica real.';
    return '⚠️ Practica más. Asegúrate de superar el umbral de corriente antes de iniciar la simulación.';
  }

  /** Color del badge de puntaje según el valor */
  colorPuntaje(puntaje: number | null): string {
    if (!puntaje) return 'puntaje-sin-datos';
    if (puntaje >= 90) return 'puntaje-excelente';
    if (puntaje >= 70) return 'puntaje-bueno';
    if (puntaje >= 50) return 'puntaje-regular';
    return 'puntaje-bajo';
  }

  /** Devuelve el ícono del escenario clínico */
  iconoEscenario(escenario: string): string {
    const iconos: Record<string, string> = {
      'Bradicardia Sinusal': '🐢',
      'Bloqueo AV I':        '🔶',
      'Bloqueo AV III':      '🔴',
      'Normal':              '✅',
    };
    return iconos[escenario] ?? '🫀';
  }

  /** Verifica si una sesión está finalizada */
  estaFinalizada(sesion: Sesion): boolean {
    return sesion.fecha_fin !== null;
  }

  trackBySesion(_: number, sesion: Sesion): number {
    return sesion.id_sesion;
  }
}
