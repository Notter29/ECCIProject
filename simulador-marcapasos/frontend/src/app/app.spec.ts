import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { App } from './app';
import { MarcapasosService } from './services/marcapasos';

describe('App', () => {
  const apiMock = {
    obtenerHistorialSimulaciones: () => of([]),
    crearSesion: () => of({
      id_sesion: 7,
      id_usuario: 3,
      fecha_inicio: '2026-10-06T12:00:00Z',
      fecha_fin: null,
      escenario_base: 'Ausencia de actividad ventricular simulada',
      puntaje_final: null,
    }),
    crearSimulacion: () => of({
      id_simulacion: 8,
      id_sesion: 7,
      nombre_escenario: 'Ausencia de actividad ventricular simulada',
      modo: 'VOO' as const,
      frecuencia_ppm: 60,
      corriente_ma: 5,
      sensibilidad_mv: 2,
      duracion_pulso_ms: 1.5,
      resultado: 'En curso',
      fecha_creacion: '2026-10-06T12:00:00Z',
      eventos: [],
      evidencia_nombre: null,
    }),
    registrarEventoSimulacion: () => of({
      id_evento: 1,
      id_simulacion: 8,
      tipo: 'PACE',
      descripcion: 'Pulso virtual',
      timestamp: '2026-10-06T12:00:00Z',
    }),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [{ provide: MarcapasosService, useValue: apiMock }],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should show the ECCI sign-in screen before authentication', () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('GALIX PACESTAR');
    expect(compiled.textContent).toContain('ECCI');
    expect(compiled.textContent).toContain('no es un dispositivo médico');
  });

  it('tracks and resets the educational maintenance checklist', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.checklist.visual = true;
    app.checklist.controls = true;

    expect(app.checklistCompleted).toBe(2);
    expect(app.checklistCompletionPercent).toBe(18);

    app.resetChecklist();
    expect(app.checklistCompleted).toBe(0);
    expect(app.checklistCompletionPercent).toBe(0);
  });

  it('starts VOO and renders aligned virtual pacing pulses', async () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    app.onAuthenticated({
      access_token: 'test-token',
      token_type: 'bearer',
      usuario: {
        id_usuario: 3,
        nombre: 'Estudiante',
        codigo_estudiantil: 'TEST-003',
        esta_activo: true,
        fecha_registro: '2026-10-06T12:00:00Z',
      },
    });
    app.mode = 'VOO';
    app.scenarioName = 'Ausencia de actividad ventricular simulada';
    app.selectView('simulador');
    app.startPractice();
    fixture.detectChanges();

    await new Promise((resolve) => window.setTimeout(resolve, 180));
    fixture.detectChanges();

    expect(app.status).toBe('running');
    expect(app.paceMarkers.length).toBeGreaterThan(0);
    expect(fixture.nativeElement.textContent).toContain('PULSO DE ESTIMULACIÓN');
    expect(fixture.nativeElement.textContent).toContain('VOO');
    app.ngOnDestroy();
  });
});
