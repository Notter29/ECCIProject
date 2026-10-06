/**
 * COMPONENTE 2: Panel de Control del Marcapasos
 * ─────────────────────────────────────────────────────────────────────
 * Expone los controles deslizantes (sliders) para configurar los tres
 * parámetros clínicos del marcapasos:
 *   - PPM  (Frecuencia de estimulación: 30–200 pulsos por minuto) [RF-03]
 *   - mA   (Corriente de salida: 0.1–20 mA)                       [RF-04]
 *   - mV   (Sensibilidad: 0.5–10 mV)                              [RF-05]
 *
 * También controla el inicio/pausa/detención de la simulación [RF-06]
 * y la selección de escenario clínico [RF-02].
 *
 * Patrón: usa @Output() con EventEmitter para comunicar cambios hacia
 * el componente padre (App), manteniendo este componente "tonto" (dumb).
 */
import {
  Component, Input, Output, EventEmitter,
  ChangeDetectionStrategy, OnInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule }  from '@angular/forms';
import { EscenarioClinico } from '../../models/marcapasos.model';

/** Estructura de los parámetros emitidos hacia el padre */
export interface ParametrosCambiados {
  ppm:             number;
  corriente_ma:    number;
  sensibilidad_mv: number;
  escenario:       string;
}

@Component({
  selector: 'app-panel-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './panel-control.html',
  styleUrls:   ['./panel-control.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PanelControlComponent implements OnInit {

  // ── INPUTS ────────────────────────────────────────────────────────
  @Input() simulando = false;

  // ── OUTPUTS ───────────────────────────────────────────────────────
  /** Emite cuando el usuario cambia cualquier parámetro */
  @Output() parametrosCambiados = new EventEmitter<ParametrosCambiados>();
  /** Emite para iniciar o pausar la simulación */
  @Output() toggleSimulacion    = new EventEmitter<void>();
  /** Emite para detener y reiniciar la simulación */
  @Output() detenerSimulacion   = new EventEmitter<void>();

  // ── ESTADO INTERNO DE LOS CONTROLES ──────────────────────────────
  ppm             = 60;
  corrienteMa     = 5.0;
  sensibilidadMv  = 2.0;
  escenarioSelec  = EscenarioClinico.BradicardiaSinusal;

  // Lista de escenarios clínicos disponibles (RF-02)
  readonly escenarios = Object.values(EscenarioClinico);

  // Configuraciones de los sliders (rango, paso, unidad)
  readonly sliderConfig = {
    ppm:  { min: 30,  max: 200, step: 1,   unit: 'PPM', label: 'Frecuencia',          icono: '⚡' },
    ma:   { min: 0.1, max: 20,  step: 0.1, unit: 'mA',  label: 'Corriente de Salida', icono: '🔋' },
    mv:   { min: 0.5, max: 10,  step: 0.5, unit: 'mV',  label: 'Sensibilidad',        icono: '📡' },
  };

  ngOnInit(): void {
    // Emitir valores iniciales al padre cuando el componente se monta
    this.emitirCambios();
  }

  // ── MÉTODOS PÚBLICOS ──────────────────────────────────────────────

  /** Notifica al padre cada vez que el usuario mueve un slider */
  alCambiarParametro(): void {
    this.emitirCambios();
  }

  /** Calcula el porcentaje de relleno del slider (para el estilo CSS) */
  calcularPorcentaje(valor: number, min: number, max: number): number {
    return ((valor - min) / (max - min)) * 100;
  }

  /** Determina si la corriente está por debajo del umbral de captura */
  get hayFalloCaptura(): boolean {
    return this.corrienteMa < 5.0;
  }

  /** Texto del botón principal según el estado */
  get textoBoton(): string {
    return this.simulando ? '⏸ PAUSAR' : '▶ INICIAR SIMULACIÓN';
  }

  onToggle(): void {
    this.toggleSimulacion.emit();
  }

  onDetener(): void {
    this.detenerSimulacion.emit();
  }

  // ── PRIVADOS ──────────────────────────────────────────────────────

  private emitirCambios(): void {
    this.parametrosCambiados.emit({
      ppm:             this.ppm,
      corriente_ma:    this.corrienteMa,
      sensibilidad_mv: this.sensibilidadMv,
      escenario:       this.escenarioSelec,
    });
  }
}
