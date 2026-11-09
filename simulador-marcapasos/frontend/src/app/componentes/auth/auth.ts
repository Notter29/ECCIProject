import { ChangeDetectorRef, Component, EventEmitter, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MarcapasosService } from '../../services/marcapasos';
import { LoginRequest, LoginResponse, RegistroRequest } from '../../models/marcapasos.model';

@Component({
  selector: 'app-auth',
  imports: [CommonModule, FormsModule],
  templateUrl: './auth.html',
  styleUrl: './auth.scss',
})
export class Auth {
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
    this.cargando = true;
    this.mensaje = '';
    this.exito = false;
    this.service.registrarEstudiante(this.registroForm).subscribe({
      next: () => {
        this.exito = true;
        this.mensaje = 'Cuenta creada correctamente. Ya puedes iniciar sesión.';
        this.modo = 'login';
        this.loginForm.codigo_estudiantil = this.registroForm.codigo_estudiantil;
        this.registroForm = { nombre: '', codigo_estudiantil: '', password: '' };
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
