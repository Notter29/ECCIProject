import { ChangeDetectorRef, Component, EventEmitter, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MarcapasosService } from '../../services/marcapasos';
import { LoginRequest, LoginResponse, RegistroRequest } from '../../models/marcapasos.model';

@Component({
  selector: 'app-auth-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auth-panel.html',
  styleUrl: './auth-panel.scss',
})
export class AuthPanelComponent {
  @Output() authenticated = new EventEmitter<LoginResponse>();

  private readonly service = inject(MarcapasosService);
  private readonly cdr = inject(ChangeDetectorRef);
  modo: 'login' | 'registro' = 'login';
  mensaje = '';
  exito = false;
  cargando = false;
  loginForm: LoginRequest = { codigo_estudiantil: '', password: '' };
  registroForm: RegistroRequest = { nombre: '', codigo_estudiantil: '', password: '' };

  iniciarSesion(): void {
    this.cargando = true;
    this.mensaje = '';
    this.exito = false;
    this.service.login(this.loginForm).subscribe({
      next: (response) => {
        this.cargando = false;
        this.cdr.markForCheck();
        this.authenticated.emit(response);
      },
      error: (error: Error) => {
        this.mensaje = error.message;
        this.cargando = false;
        this.cdr.markForCheck();
      },
    });
  }

  registrar(): void {
    if (this.registroForm.password.length < 12) {
      this.mensaje = 'La contraseña debe tener al menos 12 caracteres.';
      this.exito = false;
      this.cdr.markForCheck();
      return;
    }

    this.cargando = true;
    this.mensaje = '';
    this.exito = false;
    this.service.registrarEstudiante(this.registroForm).subscribe({
      next: () => {
        this.loginForm = {
          codigo_estudiantil: this.registroForm.codigo_estudiantil,
          password: '',
        };
        this.modo = 'login';
        this.mensaje = 'Registro exitoso. Ahora inicia sesión.';
        this.exito = true;
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: (error: Error) => {
        this.mensaje = error.message;
        this.cargando = false;
        this.cdr.markForCheck();
      },
    });
  }
}