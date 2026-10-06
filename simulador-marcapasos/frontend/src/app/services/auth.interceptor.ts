import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { AuthStorageService } from './auth-storage';
import { environment } from '../../environments/environment';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const authStorage = inject(AuthStorageService);
  const apiOrigin = new URL(environment.apiBaseUrl).origin;
  const requestOrigin = new URL(request.url, window.location.origin).origin;
  const apiRequest = requestOrigin === apiOrigin;
  const tokenSent = apiRequest && Boolean(authStorage.token);
  const outgoingRequest = tokenSent
    ? request.clone({ setHeaders: { Authorization: `Bearer ${authStorage.token}` } })
    : request;

  return next(outgoingRequest).pipe(catchError((error: HttpErrorResponse) => {
    if (tokenSent && error.status === 401) {
      authStorage.limpiar();
      window.location.reload();
    }
    return throwError(() => error);
  }));
};