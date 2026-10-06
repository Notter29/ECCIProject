import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Observable, of } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { AuthPanelComponent } from './components/auth-panel/auth-panel';
import { MonitorEcgComponent, MonitorEvent } from './components/monitor-ecg/monitor-ecg';
import { NoahChatComponent } from './components/noah-chat/noah-chat';
import {
  GuardarSimulacionRequest,
  LoginResponse,
  SimulacionHistorial,
  Usuario,
} from './models/marcapasos.model';
import { AuthStorageService } from './services/auth-storage';
import { MarcapasosService } from './services/marcapasos';

type ViewKey = 'inicio' | 'equipo' | 'simulador' | 'señales' | 'ia' | 'biblioteca' | 'mantenimiento' | 'historial';
type PacingMode = 'VVI' | 'VOO';
type SimulationStatus = 'idle' | 'running' | 'paused' | 'stopped';

interface Scenario {
  name: string;
  description: string;
  intrinsicRate: number;
  signalAmplitudeMv: number;
}

interface Beat {
  time: number;
  paced: boolean;
  captured: boolean;
}

interface PaceMarker {
  time: number;
  captured: boolean;
  x: number;
}

interface PracticeEvent {
  time: string;
  type: string;
  description: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, AuthPanelComponent, NoahChatComponent, MonitorEcgComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnDestroy {
  private readonly api = inject(MarcapasosService);
  private readonly auth = inject(AuthStorageService);
  private readonly cdr = inject(ChangeDetectorRef);
  private timerId: number | null = null;
  private simulationTime = 0;
  private nextIntrinsicAt = Number.POSITIVE_INFINITY;
  private lastVentricularActivityAt = 0;
  private nextPaceAt = 0;
  private paceIndicatorUntil = 0;
  private senseIndicatorUntil = 0;
  private readonly visibleWindowSeconds = 8;
  private readonly sampleCount = 401;
  private beats: Beat[] = [];
  private paceEvents: Array<{ time: number; captured: boolean }> = [];
  private senseEvents: number[] = [];

  readonly navItems: Array<{ key: ViewKey; label: string }> = [
    { key: 'inicio', label: 'Inicio' },
    { key: 'equipo', label: 'Equipo' },
    { key: 'simulador', label: 'Simulador' },
    { key: 'señales', label: 'Señales' },
    { key: 'ia', label: 'Noah' },
    { key: 'biblioteca', label: 'Biblioteca' },
    { key: 'mantenimiento', label: 'Mantenimiento' },
    { key: 'historial', label: 'Historial' },
  ];

  readonly scenarios: Scenario[] = [
    {
      name: 'Ritmo sinusal',
      description: 'Actividad ventricular sintética regular para observar detección e inhibición en VVI.',
      intrinsicRate: 72,
      signalAmplitudeMv: 3.5,
    },
    {
      name: 'Bradicardia',
      description: 'Actividad ventricular sintética lenta para observar la intervención del temporizador.',
      intrinsicRate: 35,
      signalAmplitudeMv: 3.5,
    },
    {
      name: 'Ausencia de actividad ventricular simulada',
      description: 'No se generan eventos ventriculares intrínsecos; los pulsos dependen del modo seleccionado.',
      intrinsicRate: 0,
      signalAmplitudeMv: 0,
    },
    {
      name: 'Alteración de detección',
      description: 'Señal sintética de baja amplitud para explorar el ajuste de sensibilidad.',
      intrinsicRate: 60,
      signalAmplitudeMv: 1,
    },
  ];

  activeView: ViewKey = 'inicio';
  user: Usuario | null = null;
  currentSessionId: number | null = null;
  currentSimulationId: number | null = null;
  selectedHistory: SimulacionHistorial | null = null;
  isSaving = false;
  isLoadingHistory = false;
  errorMessage = '';
  status: SimulationStatus = 'idle';
  mode: PacingMode = 'VVI';
  scenarioName = this.scenarios[1].name;
  rate = 60;
  outputMa = 5;
  sensitivityMv = 2;
  readonly pulseWidthMs = 1.5;
  observations = '';
  conclusion = '';
  practiceResult = 'Requiere revisión';
  evidenceFile: File | null = null;
  ecgPath = '';
  pulseTrackPath = '';
  paceMarkers: PaceMarker[] = [];
  senseMarkers: number[] = [];
  events: PracticeEvent[] = [];
  history: SimulacionHistorial[] = [];
  senseIndicator = false;
  paceIndicator = false;
  captureStatus = 'En espera';
  lastActivity = 'No hay prácticas guardadas.';
  checklist = {
    visual: false,
    casing: false,
    controls: false,
    display: false,
    battery: false,
    connectors: false,
    cables: false,
    configuration: false,
    detection: false,
    pacing: false,
    indicators: false,
  };

  get scenario(): Scenario {
    return this.scenarios.find((item) => item.name === this.scenarioName) ?? this.scenarios[1];
  }

  get isAuthenticated(): boolean {
    return this.user !== null && this.auth.token !== null;
  }

  get isRunning(): boolean {
    return this.status === 'running';
  }

  get captureSucceeded(): boolean {
    return this.outputMa >= this.educationalCaptureThreshold;
  }

  get educationalCaptureThreshold(): number {
    return 5;
  }

  get latestEvents(): PracticeEvent[] {
    return this.events.slice(0, 8);
  }

  get eventCount(): number {
    return this.history.reduce((count, item) => count + item.eventos.length, 0);
  }

  get practicedScenarioCount(): number {
    return new Set(this.history.map((item) => item.nombre_escenario)).size;
  }

  get checklistCompleted(): number {
    return Object.values(this.checklist).filter(Boolean).length;
  }

  get checklistCompletionPercent(): number {
    return Math.round((this.checklistCompleted / Object.keys(this.checklist).length) * 100);
  }

  resetChecklist(): void {
    this.checklist = {
      visual: false,
      casing: false,
      controls: false,
      display: false,
      battery: false,
      connectors: false,
      cables: false,
      configuration: false,
      detection: false,
      pacing: false,
      indicators: false,
    };
  }

  ngOnDestroy(): void {
    this.stopTimer();
  }

  onAuthenticated(response: LoginResponse): void {
    this.auth.guardar(response.access_token, response.usuario);
    this.user = response.usuario;
    this.errorMessage = '';
    this.activeView = 'inicio';
    this.loadHistory();
  }

  signOut(): void {
    this.stopTimer();
    this.auth.limpiar();
    this.user = null;
    this.currentSessionId = null;
    this.currentSimulationId = null;
    this.status = 'idle';
    this.events = [];
    this.activeView = 'inicio';
  }

  selectView(view: ViewKey): void {
    this.activeView = view;
    this.errorMessage = '';
    if (view === 'historial') {
      this.loadHistory();
    }
  }

  startPractice(): void {
    if (!this.user || this.isSaving) {
      return;
    }
    if (this.currentSimulationId !== null) {
      this.resumePractice();
      return;
    }

    this.errorMessage = '';
    this.activeView = 'simulador';
    this.isSaving = true;
    this.api.crearSesion({
      id_usuario: this.user.id_usuario,
      escenario_base: this.scenarioName,
    }).subscribe({
      next: (session) => {
        this.currentSessionId = session.id_sesion;
        this.api.crearSimulacion({
          id_sesion: session.id_sesion,
          nombre_escenario: this.scenarioName,
          modo: this.mode,
          frecuencia_ppm: this.rate,
          corriente_ma: this.outputMa,
          sensibilidad_mv: this.sensitivityMv,
          duracion_pulso_ms: 1.5,
        }).subscribe({
          next: (simulation) => {
            this.currentSimulationId = simulation.id_simulacion;
            this.isSaving = false;
            this.resetTrace();
            this.status = 'running';
            this.initializeTiming();
            this.addEvent('SISTEMA', 'Simulación educativa iniciada.');
            this.startTimer();
          },
          error: (error: Error) => {
            this.isSaving = false;
            this.errorMessage = error.message;
          },
        });
      },
      error: (error: Error) => {
        this.isSaving = false;
        this.errorMessage = error.message;
      },
    });
  }

  togglePause(): void {
    if (this.status === 'running') {
      this.status = 'paused';
      this.stopTimer();
      this.addEvent('SISTEMA', 'Simulación pausada por el estudiante.');
      return;
    }
    if (this.status === 'paused') {
      this.resumePractice();
    } else if (this.status === 'idle') {
      this.startPractice();
    }
  }

  stopPractice(): void {
    if (this.status !== 'running' && this.status !== 'paused') {
      return;
    }
    this.stopTimer();
    this.status = 'stopped';
    this.addEvent('SISTEMA', 'Simulación detenida. Guarda la práctica para finalizar el registro.');
  }

  restartPractice(): void {
    if (!this.currentSimulationId || this.isSaving) {
      this.startPractice();
      return;
    }
    this.resetTrace();
    this.simulationTime = 0;
    this.initializeTiming();
    this.status = 'running';
    this.addEvent('SISTEMA', 'Trazas reiniciadas; la práctica y su historial continúan.');
    this.startTimer();
  }

  savePractice(): void {
    if (!this.currentSimulationId || !this.conclusion.trim() || this.isSaving) {
      return;
    }
    this.stopTimer();
    this.status = 'stopped';
    this.isSaving = true;
    this.errorMessage = '';
    const payload: GuardarSimulacionRequest = {
      modo: this.mode,
      frecuencia_ppm: this.rate,
      corriente_ma: this.outputMa,
      sensibilidad_mv: this.sensitivityMv,
      resultado: this.practiceResult,
      observaciones: this.observations,
      conclusion: this.conclusion,
    };
    const simulationId = this.currentSimulationId;
    const evidenceUpload: Observable<unknown> = this.evidenceFile
      ? this.api.subirEvidencia(simulationId, this.evidenceFile)
      : of(null);
    evidenceUpload.pipe(
      switchMap(() => this.api.guardarSimulacion(simulationId, payload)),
    ).subscribe({
      next: () => {
        this.isSaving = false;
        this.lastActivity = `${this.scenarioName} · ${new Date().toLocaleString('es-CO')}`;
        this.addEvent('REGISTRO', 'Práctica guardada en el historial.');
        this.currentSessionId = null;
        this.currentSimulationId = null;
        this.status = 'idle';
        this.observations = '';
        this.conclusion = '';
        this.evidenceFile = null;
        this.loadHistory();
      },
      error: (error: Error) => {
        this.isSaving = false;
        this.errorMessage = error.message;
      },
    });
  }

  onScenarioChange(name: string): void {
    if (this.status === 'running' || this.currentSimulationId !== null) {
      return;
    }
    this.scenarioName = name;
    this.onParameterChange('Escenario actualizado.');
  }

  onRateChange(value: number | string): void {
    const rate = Number(value);
    if (Number.isFinite(rate)) {
      this.rate = this.nearest(this.validRates(), Math.min(200, Math.max(30, rate)));
      this.onParameterChange(`RATE configurado en ${this.rate} ppm.`);
    }
  }

  adjustRate(direction: -1 | 1): void {
    const rates = this.validRates();
    const index = rates.indexOf(this.rate);
    this.onRateChange(rates[Math.max(0, Math.min(rates.length - 1, index + direction))]);
  }

  onOutputChange(value: number | string): void {
    const output = Number(value);
    if (Number.isFinite(output)) {
      this.outputMa = this.nearest(this.validOutputs(), Math.min(25, Math.max(0.1, output)));
      this.onParameterChange(`OUTPUT virtual configurado en ${this.outputMa.toFixed(1)} mA.`);
    }
  }

  onSensitivityChange(value: number | string): void {
    const sensitivity = Number(value);
    if (Number.isFinite(sensitivity)) {
      this.sensitivityMv = Math.round(Math.min(20, Math.max(0.4, sensitivity)) * 10) / 10;
      this.onParameterChange(`SENSITIVITY configurada en ${this.sensitivityMv.toFixed(1)} mV.`);
    }
  }

  onModeChange(mode: PacingMode): void {
    this.mode = mode;
    this.onParameterChange(`Modo ${mode} seleccionado.`);
  }

  onEvidenceSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.evidenceFile = null;
    if (!file) {
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      this.errorMessage = 'La evidencia debe pesar 5 MB o menos.';
      input.value = '';
      return;
    }
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      this.errorMessage = 'Adjunta una imagen JPEG, PNG o WebP.';
      input.value = '';
      return;
    }
    this.evidenceFile = file;
    this.errorMessage = '';
  }

  explainHistory(item: SimulacionHistorial): void {
    this.selectedHistory = item;
    this.activeView = 'ia';
  }

  downloadEvidence(item: SimulacionHistorial): void {
    this.api.descargarEvidencia(item.id_simulacion).subscribe({
      next: (blob) => {
        const objectUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = objectUrl;
        link.download = item.evidencia_nombre ?? 'evidencia-practica';
        link.click();
        window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
      },
    });
  }

  loadHistory(): void {
    if (!this.user) {
      return;
    }
    this.isLoadingHistory = true;
    this.api.obtenerHistorialSimulaciones().subscribe({
      next: (history) => {
        this.history = history;
        this.isLoadingHistory = false;
        this.cdr.markForCheck();
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.isLoadingHistory = false;
        this.cdr.markForCheck();
      },
    });
  }

  private resumePractice(): void {
    if (!this.currentSimulationId) {
      return;
    }
    this.status = 'running';
    this.addEvent('SISTEMA', 'Simulación reanudada.');
    this.startTimer();
  }

  private initializeTiming(): void {
    const intrinsicRate = this.scenario.intrinsicRate;
    this.nextIntrinsicAt = intrinsicRate > 0 ? this.simulationTime + 0.25 : Number.POSITIVE_INFINITY;
    this.lastVentricularActivityAt = this.simulationTime;
    this.nextPaceAt = this.simulationTime + 0.1;
    this.paceIndicator = false;
    this.senseIndicator = false;
    this.captureStatus = 'En espera';
    this.renderTrace();
  }

  private startTimer(): void {
    this.stopTimer();
    this.timerId = window.setInterval(() => this.advanceSimulation(), 50);
  }

  private stopTimer(): void {
    if (this.timerId !== null) {
      window.clearInterval(this.timerId);
      this.timerId = null;
    }
  }

  private advanceSimulation(): void {
    this.simulationTime = Math.round((this.simulationTime + 0.05) * 100) / 100;
    this.paceIndicator = this.simulationTime < this.paceIndicatorUntil;
    this.senseIndicator = this.simulationTime < this.senseIndicatorUntil;

    while (this.nextIntrinsicAt <= this.simulationTime) {
      const beatTime = this.nextIntrinsicAt;
      this.beats.push({ time: beatTime, paced: false, captured: true });
      if (this.mode === 'VVI' && this.scenario.signalAmplitudeMv >= this.sensitivityMv) {
        this.lastVentricularActivityAt = beatTime;
        this.senseIndicatorUntil = beatTime + 0.18;
        this.senseEvents.push(beatTime);
        this.addEvent('SENSE', `Actividad sintética detectada (${this.scenario.signalAmplitudeMv.toFixed(1)} mV); PACE inhibido en VVI.`);
      } else if (this.mode === 'VVI') {
        this.addEvent('SENSE', `Actividad sintética no detectada con sensibilidad ${this.sensitivityMv.toFixed(1)} mV.`);
      }
      this.nextIntrinsicAt += 60 / this.scenario.intrinsicRate;
    }

    const pacingInterval = 60 / this.rate;
    if (this.mode === 'VOO') {
      while (this.nextPaceAt <= this.simulationTime) {
        this.emitPace(this.nextPaceAt);
        this.nextPaceAt += pacingInterval;
      }
    } else if (this.simulationTime - this.lastVentricularActivityAt >= pacingInterval) {
      this.emitPace(this.simulationTime);
      this.lastVentricularActivityAt = this.simulationTime;
    }

    this.beats = this.beats.filter((beat) => this.simulationTime - beat.time <= this.visibleWindowSeconds + 1);
    this.paceEvents = this.paceEvents.filter((event) => this.simulationTime - event.time <= this.visibleWindowSeconds);
    this.senseEvents = this.senseEvents.filter((time) => this.simulationTime - time <= this.visibleWindowSeconds);
    this.renderTrace();
  }

  private emitPace(time: number): void {
    const captured = this.captureSucceeded;
    this.paceEvents.push({ time, captured });
    this.paceIndicatorUntil = time + 0.16;
    if (captured) {
      this.beats.push({ time: time + 0.08, paced: true, captured: true });
      this.captureStatus = 'Captura simulada';
    } else {
      this.captureStatus = 'Sin respuesta simulada';
    }
    const description = captured
      ? `PACE generado en ${this.mode}; respuesta ventricular representada por el modelo didáctico.`
      : `PACE generado; no se dibuja respuesta ventricular porque OUTPUT es inferior al umbral didáctico de ${this.educationalCaptureThreshold.toFixed(1)} mA.`;
    this.addEvent('PACE', description);
  }

  private renderTrace(): void {
    const start = this.simulationTime - this.visibleWindowSeconds;
    const points: string[] = [];
    for (let index = 0; index < this.sampleCount; index += 1) {
      const time = start + (index / (this.sampleCount - 1)) * this.visibleWindowSeconds;
      const x = (index / (this.sampleCount - 1)) * 1000;
      const y = Math.max(24, Math.min(184, 106 - this.signalAt(time) * 48));
      points.push(`${index === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`);
    }
    this.ecgPath = points.join(' ');
    this.paceMarkers = this.paceEvents
      .map((event) => ({
        time: event.time,
        captured: event.captured,
        x: ((event.time - start) / this.visibleWindowSeconds) * 1000,
      }))
      .filter((event) => event.x >= 0 && event.x <= 1000);
    this.senseMarkers = this.senseEvents
      .map((time) => ((time - start) / this.visibleWindowSeconds) * 1000)
      .filter((x) => x >= 0 && x <= 1000);
    const track = ['M0,24 L1000,24'];
    for (const marker of this.paceMarkers) {
      track.push(`M${marker.x.toFixed(1)},24 L${marker.x.toFixed(1)},70`);
    }
    this.pulseTrackPath = track.join(' ');
  }

  private signalAt(time: number): number {
    let value = 0;
    for (const beat of this.beats) {
      const delta = time - beat.time;
      if (Math.abs(delta) > 0.6) {
        continue;
      }
      const qrsAmplitude = beat.paced ? (beat.captured ? 1.45 : 0) : 1;
      value += 0.12 * this.gaussian(delta + 0.18, 0.035);
      value -= 0.22 * this.gaussian(delta + 0.025, 0.012);
      value += qrsAmplitude * this.gaussian(delta, beat.paced ? 0.045 : 0.025);
      value -= 0.3 * this.gaussian(delta - 0.035, 0.018);
      value += 0.32 * this.gaussian(delta - 0.25, 0.08);
    }
    for (const pace of this.paceEvents) {
      const delta = time - pace.time;
      if (Math.abs(delta) < 0.035) {
        value -= 1.7 * this.gaussian(delta, 0.006);
      }
    }
    return value;
  }

  private gaussian(value: number, spread: number): number {
    return Math.exp(-(value * value) / (2 * spread * spread));
  }

  onMonitorEvent(event: MonitorEvent): void {
    if (this.isRunning) {
      this.addEvent(event.type, event.description);
    }
  }

  private addEvent(type: string, description: string): void {
    const event: PracticeEvent = {
      time: new Date().toLocaleTimeString('es-CO', { hour12: false }),
      type,
      description,
    };
    this.events = [event, ...this.events].slice(0, 40);
    if (!this.currentSimulationId || type === 'REGISTRO') {
      return;
    }
    this.api.registrarEventoSimulacion(this.currentSimulationId, {
      tipo: type,
      descripcion: description,
    }).subscribe({
      error: (error: Error) => {
        this.errorMessage = `No se pudo guardar el evento: ${error.message}`;
        this.cdr.markForCheck();
      },
    });
  }

  private onParameterChange(description: string): void {
    this.addEvent('CONFIGURACIÓN', description);
  }

  private resetTrace(): void {
    this.simulationTime = 0;
    this.beats = [];
    this.paceEvents = [];
    this.senseEvents = [];
    this.events = [];
    this.paceMarkers = [];
    this.senseMarkers = [];
    this.ecgPath = '';
    this.pulseTrackPath = 'M0,24 L1000,24';
  }

  private validRates(): number[] {
    const rates: number[] = [];
    for (let value = 30; value <= 50; value += 5) rates.push(value);
    for (let value = 52; value <= 100; value += 2) rates.push(value);
    for (let value = 105; value <= 170; value += 5) rates.push(value);
    for (let value = 176; value <= 200; value += 6) rates.push(value);
    if (rates[rates.length - 1] !== 200) rates.push(200);
    return rates;
  }

  private validOutputs(): number[] {
    const values = new Set<number>();
    for (let value = 0.1; value <= 0.4001; value += 0.1) values.add(Number(value.toFixed(1)));
    for (let value = 0.4; value <= 1.0001; value += 0.2) values.add(Number(value.toFixed(1)));
    for (let value = 1; value <= 5.0001; value += 0.5) values.add(Number(value.toFixed(1)));
    for (let value = 5; value <= 25; value += 1) values.add(Number(value.toFixed(1)));
    return [...values].sort((a, b) => a - b);
  }

  private nearest(values: number[], requested: number): number {
    return values.reduce((closest, value) =>
      Math.abs(value - requested) < Math.abs(closest - requested) ? value : closest,
    );
  }
}
