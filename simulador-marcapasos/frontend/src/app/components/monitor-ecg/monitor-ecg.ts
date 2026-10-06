import {
  AfterViewInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnChanges,
  OnDestroy,
  Output,
  SimpleChanges,
  ViewChild,
  inject,
} from '@angular/core';
import { CommonModule } from '@angular/common';

export interface MonitorEvent {
  type: 'PACE' | 'SENSE' | 'SISTEMA';
  description: string;
}

@Component({
  selector: 'app-monitor-ecg',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './monitor-ecg.html',
  styleUrls: ['./monitor-ecg.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MonitorEcgComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() ppm = 60;
  @Input() corrienteMa = 5.0;
  @Input() sensibilidadMv = 2.0;
  @Input() simulando = false;
  @Input() escenario = 'Bradicardia';
  @Input() modo: 'VVI' | 'VOO' = 'VVI';
  @Input() pulseWidthMs = 1.5;

  @Output() eventEmitted = new EventEmitter<MonitorEvent>();

  @ViewChild('ecgCanvas', { static: true })
  canvasRef!: ElementRef<HTMLCanvasElement>;

  private readonly cdr = inject(ChangeDetectorRef);

  // Canvas context & animation state
  private ctx!: CanvasRenderingContext2D;
  private animFrameId = 0;
  private audioCtx: AudioContext | null = null;
  audioEnabled = false;

  // Sweep cursor positioning
  private cursorX = 0;
  private lastCursorX = 0;
  private lastEcgY = 0;
  private lastPulseY = 0;

  // Simulation timing (in seconds)
  private clockTime = 0;
  private lastPaceTime = -100;
  private lastSenseTime = -100;
  private lastVentricularActivityTime = 0;
  private nextIntrinsicBeatTime = 0;
  private nextPaceScheduledTime = 0;

  // Visual LED indicators
  paceIndicatorActive = false;
  senseIndicatorActive = false;
  private paceIndicatorUntil = 0;
  private senseIndicatorUntil = 0;

  // Buffer of active historical wave events for rendering
  private activeBeats: Array<{ time: number; paced: boolean; captured: boolean }> = [];
  private activePaces: Array<{ time: number; captured: boolean }> = [];
  private activeSenses: number[] = [];

  get educationalCaptureThreshold(): number {
    return 5.0; // mA threshold for educational capture
  }

  get captureSucceeded(): boolean {
    return this.corrienteMa >= this.educationalCaptureThreshold;
  }

  get scenarioIntrinsicRate(): number {
    switch (this.escenario) {
      case 'Ritmo sinusal':
        return 72;
      case 'Bradicardia':
        return 35;
      case 'Ausencia de actividad ventricular simulada':
        return 0;
      case 'Alteración de detección':
        return 60;
      default:
        return 35;
    }
  }

  get scenarioAmplitudeMv(): number {
    switch (this.escenario) {
      case 'Alteración de detección':
        return 1.0; // Low voltage signal
      case 'Ausencia de actividad ventricular simulada':
        return 0;
      default:
        return 3.5; // Normal R-wave amplitude
    }
  }

  ngAfterViewInit(): void {
    this.initCanvas();
    this.resetSimulationTiming();
    this.startAnimationLoop();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.ctx) {
      if (changes['escenario'] || changes['modo'] || changes['ppm']) {
        this.resetSimulationTiming();
      }
    }
  }

  ngOnDestroy(): void {
    this.stopAnimationLoop();
    if (this.audioCtx) {
      this.audioCtx.close().catch(() => {});
    }
  }

  toggleAudio(): void {
    this.audioEnabled = !this.audioEnabled;
    if (this.audioEnabled && !this.audioCtx) {
      const AudioCtxClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioCtxClass) {
        this.audioCtx = new AudioCtxClass();
      }
    }
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  }

  private initCanvas(): void {
    const canvas = this.canvasRef.nativeElement;
    const parentWidth = canvas.parentElement?.clientWidth || 900;
    const height = 340; // Height for dual channel (ECG + Pulse)

    canvas.width = parentWidth * (window.devicePixelRatio || 1);
    canvas.height = height * (window.devicePixelRatio || 1);
    canvas.style.width = `${parentWidth}px`;
    canvas.style.height = `${height}px`;

    this.ctx = canvas.getContext('2d')!;
    this.ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);

    this.drawBackgroundGrid(parentWidth, height);
    this.lastEcgY = height * 0.35;
    this.lastPulseY = height * 0.82;
  }

  private resetSimulationTiming(): void {
    this.clockTime = 0;
    this.cursorX = 0;
    this.lastCursorX = 0;
    this.lastVentricularActivityTime = 0;
    this.activeBeats = [];
    this.activePaces = [];
    this.activeSenses = [];

    const intrinsicRate = this.scenarioIntrinsicRate;
    this.nextIntrinsicBeatTime = intrinsicRate > 0 ? 0.3 : Number.POSITIVE_INFINITY;
    this.nextPaceScheduledTime = 60 / this.ppm;

    if (this.canvasRef) {
      const canvas = this.canvasRef.nativeElement;
      const width = canvas.parentElement?.clientWidth || 900;
      const height = 340;
      this.drawBackgroundGrid(width, height);
    }
  }

  private drawBackgroundGrid(width: number, height: number): void {
    const ctx = this.ctx;
    ctx.fillStyle = '#061311'; // Dark medical monitor background
    ctx.fillRect(0, 0, width, height);

    // Minor grid lines (5px equivalent)
    ctx.strokeStyle = '#10332c';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < width; x += 12) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 12) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Major grid lines (every 5 minor squares = 60px)
    ctx.strokeStyle = '#1a5247';
    ctx.lineWidth = 1.0;
    for (let x = 0; x < width; x += 60) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 60) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Channel baseline dividers & headers
    ctx.strokeStyle = '#266c5d';
    ctx.lineWidth = 1.2;

    // ECG Baseline
    ctx.beginPath();
    ctx.moveTo(0, height * 0.35);
    ctx.lineTo(width, height * 0.35);
    ctx.stroke();

    // Divider between channels
    ctx.strokeStyle = '#1b3b35';
    ctx.beginPath();
    ctx.moveTo(0, height * 0.65);
    ctx.lineTo(width, height * 0.65);
    ctx.stroke();

    // Pulse Baseline
    ctx.strokeStyle = '#266c5d';
    ctx.beginPath();
    ctx.moveTo(0, height * 0.85);
    ctx.lineTo(width, height * 0.85);
    ctx.stroke();

    // Channel Text Labels
    ctx.font = '10px "IBM Plex Mono", monospace';
    ctx.fillStyle = '#6de0c7';
    ctx.fillText('CANAL 1: ECG VENTRICULAR SINTÉTICO (10 mm/mV · 25 mm/s)', 12, 18);
    ctx.fillStyle = '#f5c643';
    ctx.fillText('CANAL 2: PULSO DE ESTIMULACIÓN (PACE VIRTUAL)', 12, height * 0.68 + 14);
  }

  private startAnimationLoop(): void {
    const frameRateMs = 16.6; // ~60 FPS
    let lastTimestamp = performance.now();

    const animate = (now: number) => {
      const deltaSeconds = Math.min((now - lastTimestamp) / 1000, 0.05);
      lastTimestamp = now;

      if (this.simulando) {
        this.stepSimulation(deltaSeconds);
      }

      this.animFrameId = requestAnimationFrame(animate);
    };

    this.animFrameId = requestAnimationFrame(animate);
  }

  private stopAnimationLoop(): void {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = 0;
    }
  }

  private stepSimulation(deltaSeconds: number): void {
    const canvas = this.canvasRef.nativeElement;
    const width = canvas.parentElement?.clientWidth || 900;
    const height = 340;

    // Sweep speed: complete canvas width in 6.0 seconds
    const sweepSpeedPxPerSec = width / 6.0;
    this.clockTime += deltaSeconds;

    // Update indicator timer states
    this.paceIndicatorActive = this.clockTime < this.paceIndicatorUntil;
    this.senseIndicatorActive = this.clockTime < this.senseIndicatorUntil;
    this.cdr.markForCheck();

    // 1. Process Intrinsic Heart Beats
    const intrinsicRate = this.scenarioIntrinsicRate;
    if (intrinsicRate > 0 && this.clockTime >= this.nextIntrinsicBeatTime) {
      const beatTime = this.nextIntrinsicBeatTime;
      const detected = this.modo === 'VVI' && this.scenarioAmplitudeMv >= this.sensibilidadMv;

      this.activeBeats.push({ time: beatTime, paced: false, captured: true });
      if (detected) {
        this.lastVentricularActivityTime = beatTime;
        this.senseIndicatorUntil = this.clockTime + 0.22;
        this.activeSenses.push(beatTime);
        this.playBeepSound(650);
        this.eventEmitted.emit({
          type: 'SENSE',
          description: `Actividad sintética detectada (${this.scenarioAmplitudeMv.toFixed(1)} mV); pulso inhibido en VVI.`,
        });
      }
      this.nextIntrinsicBeatTime += 60 / intrinsicRate;
    }

    // 2. Process Pacemaker Pacing Logic (VVI / VOO)
    const pacingIntervalSec = 60 / this.ppm;
    if (this.modo === 'VOO') {
      if (this.clockTime >= this.nextPaceScheduledTime) {
        this.triggerPace(this.clockTime);
        this.nextPaceScheduledTime = this.clockTime + pacingIntervalSec;
      }
    } else {
      // VVI Demand Pacing
      if (this.clockTime - this.lastVentricularActivityTime >= pacingIntervalSec) {
        this.triggerPace(this.clockTime);
        this.lastVentricularActivityTime = this.clockTime;
      }
    }

    // Clean up old events outside 8-second window
    this.activeBeats = this.activeBeats.filter((b) => this.clockTime - b.time <= 8);
    this.activePaces = this.activePaces.filter((p) => this.clockTime - p.time <= 8);
    this.activeSenses = this.activeSenses.filter((t) => this.clockTime - t <= 8);

    // 3. Render Sweep Line Wipe Frame
    const nextCursorX = (this.cursorX + deltaSeconds * sweepSpeedPxPerSec) % width;
    const wipeWidth = 24;

    // Erase trailing sweep sector
    const ctx = this.ctx;
    ctx.fillStyle = '#061311';
    if (nextCursorX < this.cursorX) {
      // Wrap around screen boundary
      ctx.fillRect(this.cursorX, 0, width - this.cursorX, height);
      ctx.fillRect(0, 0, nextCursorX + wipeWidth, height);
      this.drawBackgroundGridSection(this.cursorX, width - this.cursorX, height, width);
      this.drawBackgroundGridSection(0, nextCursorX + wipeWidth, height, width);
      this.lastCursorX = 0;
      this.cursorX = 0;
    } else {
      ctx.fillRect(this.cursorX, 0, wipeWidth, height);
      this.drawBackgroundGridSection(this.cursorX, wipeWidth, height, width);
    }

    // Calculate dynamic signal points at current X
    const currentSampleTime = this.clockTime;
    const ecgY = this.computeEcgY(currentSampleTime, height);
    const pulseY = this.computePulseY(currentSampleTime, height);

    // Draw Channel 1: ECG Trace
    ctx.shadowBlur = this.captureSucceeded ? 8 : 12;
    ctx.shadowColor = this.captureSucceeded ? '#6de0c7' : '#ff947e';
    ctx.strokeStyle = this.captureSucceeded ? '#76dfc6' : '#ff947e';
    ctx.lineWidth = 2.2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    ctx.moveTo(this.lastCursorX, this.lastEcgY);
    ctx.lineTo(nextCursorX, ecgY);
    ctx.stroke();

    // Draw Channel 2: Pacing Pulse Trace
    ctx.shadowBlur = 6;
    ctx.shadowColor = '#f5c643';
    ctx.strokeStyle = '#f5c643';
    ctx.lineWidth = 2.0;

    ctx.beginPath();
    ctx.moveTo(this.lastCursorX, this.lastPulseY);
    ctx.lineTo(nextCursorX, pulseY);
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Draw Bright Sweep Beam Cursor
    ctx.fillStyle = '#ffffff';
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#ffffff';
    ctx.beginPath();
    ctx.arc(nextCursorX, ecgY, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(nextCursorX, pulseY, 2.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    this.lastCursorX = nextCursorX;
    this.cursorX = nextCursorX;
    this.lastEcgY = ecgY;
    this.lastPulseY = pulseY;
  }

  private drawBackgroundGridSection(startX: number, width: number, height: number, totalWidth: number): void {
    const ctx = this.ctx;
    const endX = startX + width;

    // Minor lines
    ctx.strokeStyle = '#10332c';
    ctx.lineWidth = 0.5;
    for (let x = Math.floor(startX / 12) * 12; x <= endX; x += 12) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 12) {
      ctx.beginPath();
      ctx.moveTo(startX, y);
      ctx.lineTo(endX, y);
      ctx.stroke();
    }

    // Major lines
    ctx.strokeStyle = '#1a5247';
    ctx.lineWidth = 1.0;
    for (let x = Math.floor(startX / 60) * 60; x <= endX; x += 60) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 60) {
      ctx.beginPath();
      ctx.moveTo(startX, y);
      ctx.lineTo(endX, y);
      ctx.stroke();
    }

    // Baselines
    ctx.strokeStyle = '#266c5d';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(startX, height * 0.35);
    ctx.lineTo(endX, height * 0.35);
    ctx.stroke();

    ctx.strokeStyle = '#1b3b35';
    ctx.beginPath();
    ctx.moveTo(startX, height * 0.65);
    ctx.lineTo(endX, height * 0.65);
    ctx.stroke();

    ctx.strokeStyle = '#266c5d';
    ctx.beginPath();
    ctx.moveTo(startX, height * 0.85);
    ctx.lineTo(endX, height * 0.85);
    ctx.stroke();
  }

  private triggerPace(time: number): void {
    const captured = this.captureSucceeded;
    this.activePaces.push({ time, captured });
    this.paceIndicatorUntil = this.clockTime + 0.20;

    if (captured) {
      this.activeBeats.push({ time: time + 0.08, paced: true, captured: true });
      this.playBeepSound(880);
    } else {
      this.playBeepSound(400);
    }

    const description = captured
      ? `PACE generado en modo ${this.modo}; despolarización ventricular capturada.`
      : `PACE generado; no hay respuesta ventricular (salida ${this.corrienteMa.toFixed(1)} mA < umbral ${this.educationalCaptureThreshold.toFixed(1)} mA).`;

    this.eventEmitted.emit({ type: 'PACE', description });
  }

  private computeEcgY(time: number, height: number): number {
    const centerY = height * 0.35;
    let signalMv = 0;

    // Sum ECG wave contributions
    for (const beat of this.activeBeats) {
      const delta = time - beat.time;
      if (Math.abs(delta) > 0.6) continue;

      const qrsAmp = beat.paced ? (beat.captured ? 1.4 : 0) : 1.0;
      // P wave
      signalMv += 0.14 * this.gaussian(delta + 0.18, 0.035);
      // Q wave
      signalMv -= 0.25 * this.gaussian(delta + 0.025, 0.012);
      // R wave (QRS peak)
      signalMv += qrsAmp * 1.2 * this.gaussian(delta, beat.paced ? 0.045 : 0.022);
      // S wave
      signalMv -= 0.35 * this.gaussian(delta - 0.035, 0.018);
      // T wave
      signalMv += 0.35 * this.gaussian(delta - 0.25, 0.08);
    }

    // Sum PACE sharp vertical spike artifacts
    for (const pace of this.activePaces) {
      const delta = time - pace.time;
      if (Math.abs(delta) < 0.035) {
        signalMv -= 2.2 * this.gaussian(delta, 0.005);
      }
    }

    // Add baseline noise scaled by sensitivity setting
    signalMv += (Math.random() - 0.5) * 0.04 * (this.sensibilidadMv / 2.0);

    return centerY - signalMv * 36; // 36px per mV scaling
  }

  private computePulseY(time: number, height: number): number {
    const pulseBaselineY = height * 0.85;
    let pulseDeflection = 0;

    for (const pace of this.activePaces) {
      const delta = time - pace.time;
      if (delta >= 0 && delta <= (this.pulseWidthMs / 1000) * 20) {
        // Square pulse marker
        pulseDeflection = pace.captured ? 32 : 16;
      }
    }

    return pulseBaselineY - pulseDeflection;
  }

  private gaussian(x: number, spread: number): number {
    return Math.exp(-(x * x) / (2 * spread * spread));
  }

  private playBeepSound(frequencyHz: number): void {
    if (!this.audioEnabled || !this.audioCtx) return;
    try {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(frequencyHz, this.audioCtx.currentTime);

      gain.gain.setValueAtTime(0.08, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.07);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.07);
    } catch {
      // Audio playback blocked or uninitialized
    }
  }
}
