# 🫀 GALIX PACESTAR — Simulador Didáctico de Marcapasos Temporal Externo

> **Proyecto Académico de Ingeniería Biomédica — Universidad ECCI**  
> *Equipo de Referencia:* **Medtronic Model 53401** (Marcapasos Temporal Monocameral Externo)

Plataforma web educativa e interactiva diseñada para la enseñanza de la estimulación cardíaca temporal, sensado ventricular sintético y visualización en tiempo real de electrocardiogramas (ECG).

---

## 📌 Descargo de Responsabilidad (Academic Disclaimer)

> **AVISO IMPORTANTE:** Esta plataforma es una herramienta estrictamente educativa desarrollada con fines académicos para estudiantes de Ingeniería Biomédica. **NO es un dispositivo médico, NO genera estimulación eléctrica real, NO debe conectarse a pacientes y NO debe utilizarse para diagnóstico o tratamiento clínico.**

---

## 🚀 ¿Cómo ejecutar el proyecto tras clonar de Git?

### Requisitos Previos
* **Python 3.10+** (Asegurarse de marcar la casilla "Add Python to PATH" durante la instalación).
* **Node.js LTS (v18 o superior)** y **npm**.

---

### Modo Automático (Windows)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/simulador-marcapasos.git
   cd simulador-marcapasos
   ```

2. **Ejecutar el script automático:**
   Haz **doble clic** en el archivo `iniciar.bat` (o ejecútalo desde CMD/PowerShell):
   ```cmd
   iniciar.bat
   ```

   *El script se encarga automáticamente de:*
   * Crear el entorno virtual Python (`backend/venv`).
   * Instalar las dependencias del backend (`requirements.txt`).
   * Instalar los módulos del frontend Angular (`npm ci`).
   * Iniciar el servidor Backend en `http://localhost:8000`.
   * Iniciar el servidor Frontend en `http://localhost:4200`.

3. **Abrir en el navegador:**
   * **Aplicación Web:** [http://localhost:4200](http://localhost:4200)
   * **Documentación API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Modo Manual / Multiplataforma (Linux / macOS / Windows)

Si prefieres ejecutar los servidores en consolas separadas:

#### 1. Iniciar Backend (FastAPI)
```bash
cd backend
python3 -m venv venv

# En Linux/macOS:
source venv/bin/activate
# En Windows (PowerShell):
.\venv\Scripts\activate

pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. Iniciar Frontend (Angular)
En una nueva terminal:
```bash
cd frontend
npm install
npm run start
```
Abre tu navegador en `http://localhost:4200`.

---

## 💻 Características Principales del Proyecto

### 1. 🫀 Monitor Biológico Dinámico a 60 FPS (*Canvas Oscilloscope*)
* **Trazado de barrido continuo (Wipe Beam Effect)**: Simula el comportamiento real de un monitor clínico de cuidados intensivos a 25 mm/s.
* **Canal Doble**: Canal 1 para ECG Ventricular sintético y Canal 2 para Impulso de Estimulación (PACE).
* **Indicadores LED y Auditivos**: Parpadeo en vivo de indicadores **PACE** (amarillo) y **SENSE** (azul), con tono de pulso de audio opcional (Web Audio API).

### 2. 🎛️ Panel de Control de Estimulación
* **Modos de Estimulación**: Modo síncrono a demanda (**VVI**) y asíncrono (**VOO**).
* **Parámetros Ajustables**:
  * `RATE` (Frecuencia): 30–200 ppm (escalonamientos exactos del fabricante: 5/2/5/6 ppm).
  * `OUTPUT` (Salida Virtual): 0,1–25 mA.
  * `SENSITIVITY` (Sensibilidad): 0,4–20 mV.
  * `PULSE WIDTH` (Duración de Pulso): 1,5 ms fijo de referencia.
* **Escenarios Didácticos**: *Ritmo Sinusal*, *Bradicardia*, *Ausencia de Actividad Ventricular*, *Alteración de Detección*.

### 3. 🤖 Tutor Educativo Inteligente (Noah)
* Asistente virtual especializado en la guía de referencia del Medtronic 53401 y la especificación del proyecto.
* Explica conceptos de **Períodos de Cegamiento (Blanking)** (200 ms tras PACE, 120 ms tras SENSE), resolución de problemas (*Loss of Capture*, *Oversensing*, *Undersensing*), normativa EMC (IEC 60601-1-2 / CISPR 11) y fisiología cardíaca (potencial de acción y sistema de conducción).
* Analiza de forma segura sesiones registradas en el historial sin emitir juicios clínicos.

### 4. 📋 Mantenimiento y Evaluación Funcional
* Lista de chequeo didáctica interactiva de 11 puntos (carcasa, conectores, cables, pantalla, baterías, etc.).
* Guía de pruebas técnicas y protocolos de limpieza/desinfección oficiales (alcohol isopropílico al 70%).

### 5. 📁 Registro e Historial de Prácticas
* Guardado persistente de simulaciones con resultado (*Correcto*, *Incorrecto*, *Requiere revisión*), observaciones y conclusión redactada por el estudiante.
* Soporte para adjuntar evidencia fotográfica (JPEG/PNG/WebP hasta 5 MB) almacenada de forma segura en la base de datos.

---

## 🛠️ Tecnologías Utilizadas

* **Frontend**: Angular 18 (Standalone Components, Signals, Canvas API a 60 FPS, SCSS).
* **Backend**: FastAPI (Python 3.10+, Uvicorn, Pydantic v2, SQLAlchemy ORM).
* **Base de Datos**: SQLite3 (`marcapasos.db`) con autenticación JWT y Argon2id / bcrypt.
* **Arquitectura**: Monolito modular desacoplado.

---

## 🏢 Créditos

* **Institución:** Universidad ECCI — Programa de Ingeniería Biomédica.
* **Proyecto:** GALIX PACESTAR · Prototipo de Simulación Académica.
