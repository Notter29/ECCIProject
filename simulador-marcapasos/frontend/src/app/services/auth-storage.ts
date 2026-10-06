import { Injectable } from '@angular/core';
import { Usuario } from '../models/marcapasos.model';

@Injectable({ providedIn: 'root' })
export class AuthStorageService {
  private accessToken: string | null = null;
  private currentUser: Usuario | null = null;

  get token(): string | null {
    return this.accessToken;
  }

  get usuario(): Usuario | null {
    return this.accessToken ? this.currentUser : null;
  }

  guardar(token: string, usuario: Usuario): void {
    this.accessToken = token;
    this.currentUser = usuario;
  }

  limpiar(): void {
    this.accessToken = null;
    this.currentUser = null;
  }
}