# Documentación técnica completa · GALIX PACESTAR

**Producto:** Simulador académico de marcapasos externos para Ingeniería Biomédica, Universidad ECCI.  
**Estado:** prototipo funcional con autenticación, simulación, sesiones, historial y tutor Noah.  
**Audiencia:** estudiantes, docentes, responsables de desarrollo y operación.

## 1. Propósito, alcance y seguridad académica

GALIX PACESTAR permite practicar con parámetros de estimulación y escenarios fisiológicos ficticios. El monitor ECG es una señal sintética generada en navegador; el motor del backend aplica reglas simplificadas y didácticas. El sistema no es un dispositivo médico, no está validado para uso clínico, no diagnostica y no debe usarse para decidir parámetros de pacientes.

No se deben introducir datos personales de pacientes en la aplicación ni en Noah. Solo deben usarse estudiantes de prueba y escenarios ficticios.

## 2. Funcionalidades disponibles

- Registro estudiantil, login y cierre de sesión.
- Hash Argon2id para contraseñas nuevas y upgrade de hashes bcrypt al autenticar cuentas heredadas.
- JWT bearer de duración corta y autorización de propiedad en perfil, sesiones e historial/telemetría.
- Selección de escenario; controles de PPM, corriente y sensibilidad; animación ECG en Canvas.
- Alta/finalización de sesión, registro de telemetría, puntaje e historial.
- Tutor Noah: guía de uso y explicación del resultado calculado por el backend; responde preguntas de texto y usa un proveedor LLM compatible opcionalmente.
- Interfaz de identidad ECCI, adaptable a móvil y con mensajes de uso académico.

## 3. Estructura actual del repositorio

```text
simulador-marcapasos/
  iniciar.bat
  README.md
  .gitignore
  docs/
    ARQUITECTURA_Y_BACKLOG.md
    DOCUMENTACION_TECNICA.md
  backend/
    main.py                 # composición FastAPI, CORS y routers
    config.py               # configuración de entorno y .env
    database.py             # engine SQLAlchemy y sesiones de BD
    models.py               # Usuario, SesionSimulacion, RegistroTelemetria
    schemas.py              # contratos Pydantic
    security.py             # Argon2id, JWT y usuario autenticado
    simulacion.py           # reglas académicas ECG/captura/puntaje
    noah_tutor.py           # tutor IA/local y prompt educativo
    routers/
      usuarios.py
      sesiones.py
      telemetria.py
      noah.py
    tests/
      test_security.py
  frontend/
    src/app/
      app.ts, app.html, app.scss
      components/
        auth-panel/          # registro/login
        monitor-ecg/         # monitor sintético
        panel-control/       # parámetros
        historial-sesiones/  # resultados anteriores
        noah-chat/           # chat Noah
      models/                # contratos TypeScript
      services/              # API, auth en memoria e interceptor
```

El backend ya está separado en módulos funcionales y routers por recurso; no es un archivo único. Aún no tiene una capa explícita `application/domain/repositories`: algunos routers consultan SQLAlchemy directamente. Esa extracción está descrita como evolución y no se considera terminada. El árbol actualizado y las 20 historias priorizadas están en [ARQUITECTURA_Y_BACKLOG.md](ARQUITECTURA_Y_BACKLOG.md).

## 4. Arquitectura adoptada y por qué

### 4.1 Estado actual

Arquitectura web de tres capas con cliente-servidor y backend modular:

1. **Presentación:** Angular standalone, componentes de interfaz, modelos y servicios HTTP.
2. **Aplicación/API:** FastAPI recibe/valida solicitudes, aplica dependencias de autenticación y registra routers de cuentas, prácticas, telemetría y Noah.
3. **Persistencia y reglas:** SQLAlchemy accede a SQLite local o PostgreSQL configurable; `simulacion.py` contiene los cálculos y `noah_tutor.py` maneja la interacción educativa.

```mermaid
flowchart LR
  Browser[Angular en navegador] -->|HTTP + bearer JWT| API[FastAPI]
  API --> Auth[Usuarios y seguridad]
  API --> Practice[Sesiones e historial]
  API --> Simulation[Motor fisiológico didáctico]
  API --> Noah[Tutor Noah]
  Auth --> DB[(SQLite local / PostgreSQL configurable)]
  Practice --> DB
  Simulation --> Practice
  Noah -->|contexto sintético, no identidad| LLM[Proveedor LLM opcional]
  Noah --> Local[Respuesta educativa local]
```

### 4.2 Evolución recomendada

Mantener límites de dominio (cuentas, prácticas, simulación, telemetría, tutor) y extraer gradualmente casos de uso y repositorios; desplegar inicialmente como API modular replicable. Separar un servicio de inferencia solo si su carga, equipo o ciclo de despliegue lo justifican. La recomendación es “no monolito organizacional”: cada módulo tiene dueño y contrato; no repartir prematuramente el prototipo en numerosos procesos sin observabilidad ni plataforma.

### 4.3 Alternativas evaluadas

| Alternativa | Ventaja | Coste/riesgo para este proyecto | Decisión |
|---|---|---|---|
| API modular por dominios (adoptada) | Límites comprensibles, desarrollo y pruebas sencillas, permite replicar el proceso | Debe extraerse lógica de routers y sustituirse SQLite para operación concurrente | Adecuada ahora; separar despliegues cuando se mida necesidad |
| Microservicios desde el inicio | Escalado independiente por servicio | Más despliegues, red, descubrimiento, consistencia, tracing y operación; límites de dominio aún no probados | No recomendada todavía; sí para Noah/inferencia o telemetría si las métricas lo justifican |
| Serverless | Escalado bajo demanda y menor gestión de servidores | Latencia fría, cuotas/proveedor, límites de conexión y trabajos persistentes/streaming | Alternativa para chat por eventos; no sustituye la API sin medir costos y latencia |
| Aplicación/monolito sin módulos | Instalación inicial sencilla | Mezcla seguridad, reglas, HTTP y persistencia; cambios/test se vuelven riesgosos | No usar; conservar separación de responsabilidades y APIs internas |

## 5. Flujo funcional

### Acceso

1. Angular envía código y contraseña a `POST /usuarios/login`.
2. El backend verifica bcrypt heredado o Argon2id actual y migra el hash bcrypt luego de un login válido.
3. Responde usuario público y JWT firmado, con expiración de 30 minutos.
4. `AuthStorageService` mantiene credencial en memoria; el interceptor agrega `Authorization: Bearer …` solo al origen API. Al recargar, el estudiante inicia sesión otra vez.
5. La API valida token y dueño en cada operación. Al recibir 401 en una llamada autenticada el cliente limpia la credencial.

### Práctica y resultados

1. El estudiante elige escenario y abre una sesión.
2. Ajusta PPM, corriente mA y sensibilidad mV. Canvas anima el ECG sintético localmente.
3. El backend valida rangos, aplica el umbral del escenario y registra telemetría; no confía en el resultado que declare el navegador.
4. Al finalizar se calcula puntaje y la pantalla permite revisar el historial.

### Noah

1. Desde el simulador, Angular envía texto y parámetros visibles; desde el historial envía además el `id_sesion` seleccionada, siempre con JWT.
2. El backend comprueba que la sesión pertenezca al usuario, toma el escenario guardado y calcula métricas desde telemetría; no confía en métricas históricas enviadas por el navegador.
3. Si existen `NOAH_LLM_BASE_URL`, `NOAH_LLM_API_KEY` y `NOAH_LLM_MODEL`, el servicio llama un endpoint de chat OpenAI-compatible con timeout de 12 segundos. El prompt delimita el uso educativo y prohíbe consejo para pacientes.
4. Si el proveedor no está configurado o falla, se usa respuesta local para guía/resultado/ayuda general.
5. La explicación cita eventos, capturas/fallos, rango de corriente, umbral y puntaje, y varía según si el alumno pregunta por la nota, la corriente o el patrón. Una sesión sin eventos se identifica como “sin telemetría”, no como fallo. Se devuelve el modo `llm` o `local`; los mensajes no se guardan. No se envían nombre, código estudiantil, JWT ni historial personal al proveedor. La concurrencia del proveedor tiene un límite por proceso (`NOAH_MAX_CONCURRENT_REQUESTS`, por defecto 8); si no hay cupo en 500 ms se usa guía local. En producción con réplicas se requiere además limitación compartida.

El modo local no es un modelo generativo: es una guía por reglas/temas frecuentes. Para habilitar conversación general con IA se necesita contratar/configurar un proveedor, revisar sus condiciones de privacidad, fijar presupuesto y probar su contenido con docentes. No hay una clave API incluida en el repositorio.

## 6. Modelo de datos

| Entidad | Campos relevantes | Relación |
|---|---|---|
| `Usuario` | `id_usuario`, nombre, código único, `password_hash`, activo, fecha de registro | Un usuario tiene muchas sesiones |
| `SesionSimulacion` | `id_sesion`, propietario, inicio/fin, escenario, puntaje | Pertenece a un usuario; agrupa telemetría |
| `RegistroTelemetria` | sesión, timestamp, PPM, mA, mV, estado calculado, evento | Pertenece a una sesión |

No hay entidad de paciente ni almacenamiento de conversaciones Noah. SQLite se crea localmente por defecto; para PostgreSQL se usa `DATABASE_URL=postgresql+psycopg://…`.

## 7. API disponible

Todas las rutas privadas usan `Authorization: Bearer <JWT>`. Login/registro y health-check son públicos; Noah, perfil, sesiones, historial y telemetría requieren token.

| Método y ruta | Acceso | Uso |
|---|---|---|
| `GET /` | Público | Liveness básico |
| `POST /usuarios/registro` | Público | Crear cuenta estudiantil |
| `POST /usuarios/login` | Público | Obtener token |
| `GET /usuarios/{id}` | Propietario | Perfil propio |
| `POST /sesiones/` | Propietario autenticado | Crear sesión propia |
| `PUT /sesiones/{id}/finalizar` | Propietario | Finalizar y calcular puntaje |
| `GET /sesiones/historial/{id_usuario}` | Propietario | Consultar historial propio |
| `POST /telemetria/` | Propietario | Guardar cambio en sesión activa |
| `POST /telemetria/simular` | Autenticado | Calcular señal sintética |
| `GET /telemetria/sesion/{id}` | Propietario | Ver eventos de una sesión propia |
| `POST /noah/chat` | Autenticado y propietario si incluye `id_sesion` | Pregunta de texto + explicación de estado actual o de sesión histórica seleccionada |

OpenAPI local: `http://localhost:8000/docs`. Códigos habituales: 401 no autenticado/token inválido, 403 recurso ajeno, 404 recurso inexistente, 409 transición conflictiva y 422 entrada inválida.

## 8. Seguridad, privacidad y límites de Noah

- Hash unidireccional Argon2id; bcrypt solo se mantiene para verificar/migrar usuarios existentes (`bcrypt<4.1` por compatibilidad con Passlib 1.7.4).
- JWT HS256 con expiración; en producción configurar clave aleatoria fuerte y estable con gestor de secretos. La clave de desarrollo se genera al proceso y reiniciar invalida tokens.
- Autorización por propietario, schemas con límites, cálculo del resultado en servidor y CORS por lista de orígenes.
- JWT en memoria, nunca `localStorage`; errores de autenticación genéricos; `.env`, bases y entornos virtuales ignorados por Git.
- Noah minimiza contexto y nunca recibe identidad; no enviar secretos, datos identificables ni PHI. Configurar retención cero/no entrenamiento del proveedor cuando esté disponible y firmado el acuerdo institucional pertinente.
- Mantener disclaimer académico. Escalar pregunta clínica al docente y a fuentes validadas; evaluar prompt injection, contenido dañino, alucinación, filtración entre usuarios y costo/rate limits.
- Requisitos pendientes de producción: rate limit distribuido, rotación/revocación de tokens, HTTPS, auditoría sin secretos, migraciones Alembic, respaldo/retención, política de privacidad ECCI, análisis OWASP y revisión humana del contenido biomédico.

## 9. Configuración y ejecución

Requisitos: Python 3, Node.js LTS y npm. Ver [README.md](../README.md) para `iniciar.bat` y comandos manuales.

Crear `backend/.env` desde `.env.example`. Ejemplo de desarrollo:

```dotenv
JWT_SECRET_KEY=<secreto aleatorio de al menos 32 bytes>
DATABASE_URL=sqlite:///./marcapasos.db
CORS_ORIGINS=http://localhost:4200,http://127.0.0.1:4200
```

Ejemplo PostgreSQL a configurar por ambiente:

```dotenv
DATABASE_URL=postgresql+psycopg://usuario:password@host:5432/galix
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=5
DB_POOL_TIMEOUT=30
```

No commitear secretos ni copiar el ejemplo literal a producción. La URL Angular hacia la API está centralizada en `frontend/src/environments/environment.ts` (`apiBaseUrl`); para producción reemplázala durante el build por el dominio HTTPS del balanceador.

Para usar proveedor Noah compatible con OpenAI:

```dotenv
NOAH_LLM_BASE_URL=https://<proveedor-aprobado>/v1
NOAH_LLM_API_KEY=<inyectado por gestor de secretos>
NOAH_LLM_MODEL=<modelo aprobado>
```

El `base URL` es el prefijo antes de `/chat/completions`. Sin las tres variables Noah trabaja en modo local.

## 10. Capacidad: 800 alumnos simultáneos

### Interpretación de la meta

En este proyecto, 800 simultáneos debe significar 800 sesiones autenticadas conectadas y activas, no 800 peticiones en un instante. El cálculo exacto depende de la tasa de cambios de controles, lecturas, telemetría y preguntas a Noah. La animación ECG se genera en navegador, lo que reduce trabajo del servidor, pero cada cambio de control y mensaje sí genera tráfico.

### Estado real frente al objetivo

La aplicación actual **no está certificada ni probada para 800 alumnos**. SQLite con escrituras de telemetría, un único proceso local, pool no calibrado, requests de telemetría no agrupadas y ausencia de rate-limit/cola/observabilidad hacen que no sea correcto prometer ese número aún. La configuración PostgreSQL por entorno es un paso preparatorio, no una prueba de capacidad.

### Topología objetivo inicial

```mermaid
flowchart LR
  Students[800 navegadores] --> CDN[CDN: Angular estático]
  Students --> LB[WAF / balanceador TLS]
  LB --> API1[FastAPI réplica A]
  LB --> API2[FastAPI réplica B]
  LB --> API3[FastAPI réplica N]
  API1 --> PG[PgBouncer]
  API2 --> PG
  API3 --> PG
  PG --> DB[(PostgreSQL HA)]
  API1 --> Redis[(Redis compartido: rate-limit/cache)]
  API2 --> Redis
  API3 --> Redis
  API1 --> Queue[Cola telemetría/tutor]
  Queue --> Worker[Workers con concurrencia limitada]
  Worker --> LLM[Proveedor Noah con cuota]
  API1 --> Obs[Logs, métricas y trazas]
  API2 --> Obs
  API3 --> Obs
```

Recomendaciones antes del piloto: servir Angular desde CDN; 3+ réplicas API stateless bajo autoscaling; PostgreSQL administrado; PgBouncer; Redis compartido para cuotas y rate limit; encolar telemetría si el patrón medido excede escritura directa; limitar concurrencia y presupuesto Noah; timeouts/reintentos con backoff; health/readiness, métricas y alertas. Las réplicas finales y pool deben salir de pruebas, no de esta ilustración.

### Modelo de conexiones

SQLAlchemy mantiene hasta `DB_POOL_SIZE + DB_MAX_OVERFLOW` conexiones por proceso. El máximo de clientes de aplicación estimado es `réplicas × workers_por_replica × (pool_size + max_overflow)`; deben añadirse migraciones, métricas, tareas y administración. PgBouncer debe limitar conexiones servidor a PostgreSQL por debajo del presupuesto `max_connections`, reservando conexiones para administración y failover. No fijar el pool de cada worker en 800.

### Prueba de carga exigida para declarar soporte

1. Medir con el mismo hardware, configuración, base de datos y proveedor que producción; usar datos sintéticos.
2. Ramp-up hasta 800 usuarios autenticados en 5 minutos, sostener 20 minutos y ejecutar una prueba de pico de 1.200 por 5 minutos.
3. Mezcla: login inicial; consulta historial; lectura de sesión; cambio de parámetros a ritmo representativo; telemetría según estrategia de lote; Noah con concurrencia/quota realista; incluir 10% de reconexiones.
4. Criterios iniciales a ratificar con ECCI: endpoints de API excluyendo inferencia p95 < 500 ms y p99 < 1.5 s; error HTTP inesperado < 1%; no pérdida de telemetría confirmada; consumo/pool sin crecimiento sostenido; recuperación automática de una réplica.
5. Noah se mide aparte: p95 < 15 s bajo cuota aprobada o degradación transparente al modo local; límites de concurrencia y gasto; cero exposición de identificadores/token en logs o llamadas externas.
6. Guardar scripts, versión de imagen, dataset sintético, gráficos p50/p95/p99, tasa de error, CPU/RAM, pool/locks DB, uso de LLM y coste por sesión; corregir y repetir hasta pasar dos ejecuciones consecutivas.

El script `backend/tests/load/k6-800.js` ejecuta el perfil sostenido de 800 VUs. Requiere k6 y un archivo local (no versionado) con al menos 800 cuentas sintéticas y tokens válidos, por ejemplo `[{"userId": 101, "token": "<jwt>"}, ...]`. Ejecútalo únicamente en una BD desechable/staging, porque crea sesiones y telemetría:

```powershell
k6 run -e API_URL=https://staging-api.example.edu -e TOKEN_FILE=student-tokens.json backend/tests/load/k6-800.js
```

Los umbrales son objetivos de aceptación propuestos, no resultados medidos. El perfil base no reemplaza el pico separado de 1.200 VUs. Para cumplir capacidad de producción falta implementar/probar cola o lotes de telemetría, Redis/rate-limit compartido, despliegue y observabilidad; el script no se ha ejecutado contra infraestructura de 800 VUs.

## 11. Calidad y comandos

Desde `frontend`: `npm ci`, `npm.cmd run build`, `npm.cmd test -- --watch=false`.  
Desde `backend`, con entorno virtual y requirements instalados: `python -m unittest discover -s tests -v`.  
Pruebas integrales adicionales requeridas: API con PostgreSQL, migración bcrypt, expiración/autorización horizontal, Noah local/proveedor con mocks, validación de escenarios, accesibilidad teclado/lector, OWASP y carga de 800 VUs.

Estado validado en desarrollo: build frontend, 2 tests Angular, 3 tests de hash/JWT, comprobación API de permisos y cálculo servidor, y revisión móvil del acceso. Esto no equivale a prueba de despliegue/800 VUs.

## 12. Roadmap técnico

1. Cerrar alcance pedagógico con docentes; revisar umbrales y lenguaje de todas las respuestas.
2. Migrar estructura a `api / application / domains / infrastructure`, añadir repositorios y Alembic sin cambiar contratos.
3. Elegir proveedor Noah, validar privacidad institucional, configurar secreto/cuota y pruebas adversariales; mantener fallback local.
4. Mover persistencia a PostgreSQL, desplegar stateless, añadir Redis, rate-limit y estrategia de telemetría en lotes/cola.
5. Instrumentar, ejecutar la prueba de 800 VUs y publicar informe; solo entonces anunciar la capacidad.
6. Completar historias pendientes: roles docentes, comparación/exportación, administración de escenarios, retención/borrado, CI y recuperación.
