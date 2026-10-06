import { ChangeDetectorRef, Component, Input, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NoahChatRequest } from '../../models/marcapasos.model';
import { MarcapasosService } from '../../services/marcapasos';

interface ChatMessage {
  author: 'student' | 'Noah';
  text: string;
  mode?: 'llm' | 'local';
  source?: string;
}

@Component({
  selector: 'app-noah-chat',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './noah-chat.html',
  styleUrl: './noah-chat.scss',
})
export class NoahChatComponent {
  @Input() escenario = 'Bradicardia Sinusal';
  @Input() ppm = 60;
  @Input() corrienteMa = 5;
  @Input() sensibilidadMv = 2;
  @Input() sesionId: number | null = null;

  private readonly service = inject(MarcapasosService);
  private readonly cdr = inject(ChangeDetectorRef);
  pregunta = '';
  enviando = false;
  mensajes: ChatMessage[] = [{
    author: 'Noah',
    text: 'Soy Noah, tu tutor de simulación. Puedo guiarte paso a paso y explicar los controles, modos y señales sintéticas. No diagnostico ni modifico el simulador por ti.',
    mode: 'local',
    source: 'Guía de uso académico',
  }];

  preguntarSugerencia(question: string): void {
    this.pregunta = question;
    this.enviar();
  }

  enviar(): void {
    const question = this.pregunta.trim();
    if (!question || this.enviando) return;

    this.mensajes.push({ author: 'student', text: question });
    this.pregunta = '';
    this.enviando = true;
    const request: NoahChatRequest = {
      pregunta: question,
      escenario: this.escenario,
      ppm: this.ppm,
      corriente_ma: this.corrienteMa,
      sensibilidad_mv: this.sensibilidadMv,
      ...(this.sesionId !== null ? { id_sesion: this.sesionId } : {}),
    };

    this.service.consultarNoah(request).subscribe({
      next: (response) => {
        this.mensajes.push({
          author: 'Noah',
          text: response.respuesta,
          mode: response.modo,
          source: response.fuente,
        });
        this.enviando = false;
        this.cdr.markForCheck();
      },
      error: (error: Error) => {
        this.mensajes.push({ author: 'Noah', text: `No pude responder en este momento. ${error.message}` });
        this.enviando = false;
        this.cdr.markForCheck();
      },
    });
  }
}