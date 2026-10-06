# ESPECIFICACIÓN FUNCIONAL Y TÉCNICA DEL SOFTWARE

## Simulador didáctico inteligente de marcapasos externo

*Equipo biomédico de referencia:* Medtronic Model 53401  
*Tipo de proyecto:* Módulo didáctico inteligente  
*Propósito:* Educación, simulación y entrenamiento  
*Usuarios objetivo:* Estudiantes de Ingeniería Biomédica  
*Naturaleza:* Plataforma de simulación educativa  
*Versión inicial:* Prototipo académico

---

# 1. DESCRIPCIÓN GENERAL DEL PROYECTO

Se requiere desarrollar una plataforma web educativa que simule, con fines exclusivamente académicos, el funcionamiento de un marcapasos externo temporal monocameral tomando como equipo de referencia el *Medtronic Model 53401*.

El software debe permitir al estudiante comprender la relación entre:

*actividad cardíaca simulada → detección → decisión de estimulación → pulso de estimulación simulado → respuesta representada en el ECG.*

La plataforma debe integrar:

- información técnica del equipo;
- simulación de señales biomédicas;
- configuración de parámetros;
- visualización de señales en tiempo real;
- eventos y avisos didácticos;
- biblioteca documental;
- asistente IA;
- mantenimiento y evaluación funcional;
- registro de prácticas;
- historial;
- dashboard.

El software *NO debe controlar un marcapasos real, conectarse a un paciente, producir estimulación eléctrica física ni utilizarse para diagnóstico o tratamiento*.

---

# 2. EQUIPO DE REFERENCIA

## 2.1 Identificación

| Característica | Dato |
|---|---|
| Fabricante | Medtronic |
| Modelo | 53401 |
| Tipo | Marcapasos externo temporal de una sola cámara |
| Modos del equipo real | AAI, AOO, VVI, VOO |
| Estimulación | Auricular o ventricular |
| Diseño | Corriente constante |
| Alimentación | Dos baterías AA alcalinas de 1,5 V |
| Peso | 499 g |
| Altura | 20,27 cm |
| Ancho | 6,68 cm |
| Profundidad | 4,14 cm |
| Vida útil de servicio indicada | 7 años |

Medtronic describe el Model 53401 como un marcapasos externo temporal de una sola cámara y proporciona documentación de referencia, compatibilidad y formación para este modelo.

---

# 3. ALCANCE DEL SOFTWARE

Aunque el equipo físico 53401 permite estimulación auricular y ventricular y dispone de cuatro modos, el proyecto académico se limitará inicialmente a la *simulación ventricular monocameral* para reducir la complejidad.

## 3.1 Funciones que SÍ se implementarán

- Simulación de ECG.
- Simulación de actividad ventricular.
- Simulación de detección.
- Simulación de estimulación ventricular.
- Modo VVI.
- Modo VOO.
- Frecuencia de estimulación.
- Amplitud/salida de estimulación.
- Sensibilidad.
- Duración de pulso.
- Escenarios cardíacos didácticos.
- Visualización de ECG.
- Visualización de pulsos de estimulación.
- Eventos.
- Avisos didácticos.
- Registro de simulaciones.
- Pruebas funcionales simuladas.
- Biblioteca técnica.
- Asistente IA.
- Historial.
- Dashboard.

## 3.2 Funciones que NO se implementarán en la primera versión

- AAI.
- AOO.
- Estimulación auricular.
- Doble cámara.
- Rapid Atrial Pacing (RAP).
- Comunicación con marcapasos físico.
- Comunicación con paciente.
- Diagnóstico médico.
- Control de dispositivos médicos.
- Generación de estimulación eléctrica real.

El fabricante documenta AAI, AOO, VVI y VOO en el equipo real; la exclusión de AAI/AOO y RAP corresponde únicamente al *alcance académico definido para este software*.

---

# 4. ESTRUCTURA GENERAL DE LA PLATAFORMA

La plataforma debe contener *8 módulos principales*:

1. *Inicio / Dashboard*
2. *Conoce el equipo*
3. *Simulador*
4. *Monitor de señales*
5. *Asistente IA*
6. *Biblioteca técnica*
7. *Mantenimiento y evaluación*
8. *Registro e historial*

La barra lateral o barra superior debe permitir navegar entre estos módulos.

---

# 5. PÁGINA PRINCIPAL — INICIO

La página de inicio debe funcionar como dashboard general.

## 5.1 Encabezado

Debe mostrar:

*SIMULADOR DIDÁCTICO INTELIGENTE*

Subtítulo:

*Marcapasos externo temporal — Medtronic Model 53401*

Debe incluir una indicación visible:

> Plataforma educativa de simulación. No corresponde a un dispositivo médico ni debe utilizarse para atención clínica.

---

## 5.2 Barra de navegación

Debe contener:

- Inicio
- Equipo
- Simulador
- Señales
- Asistente IA
- Biblioteca
- Mantenimiento
- Historial

---

## 5.3 Tarjeta de estado

Mostrar:

- Estado del sistema.
- Equipo seleccionado.
- Estado de simulación.
- Modo actual.
- Última actividad.

Ejemplo:

*Estado:* Sistema listo  
*Equipo:* Medtronic 53401  
*Simulación:* Inactiva  
*Modo:* VVI

---

## 5.4 Accesos rápidos

Botones:

- *Iniciar simulación*
- *Conocer el equipo*
- *Consultar asistente IA*
- *Realizar prueba*
- *Ver historial*

---

## 5.5 Última actividad

Mostrar:

- última simulación;
- fecha;
- escenario;
- resultado.

Si no existen registros:

> No se han realizado simulaciones todavía.

---

# 6. MÓDULO 1 — CONOCE EL EQUIPO

Este módulo corresponde al componente de investigación técnica solicitado por el docente.

Debe contener las siguientes secciones.

## 6.1 Información general

- Fabricante.
- Modelo.
- Tipo.
- Uso previsto.
- Aplicaciones.
- Características principales.

---

## 6.2 Principio de funcionamiento

Explicar mediante texto y una representación gráfica:

text
Actividad cardíaca
       ↓
Detección
       ↓
Análisis del evento
       ↓
¿Debe estimular?
    ↙️       ↘️
   NO       SÍ
   ↓         ↓
Esperar   Pulso simulado
             ↓
       Respuesta ECG


Esta representación será didáctica y no pretende reproducir internamente todos los algoritmos del dispositivo real.

---

## 6.3 Variables fisiológicas

Registrar:

- actividad eléctrica cardíaca;
- frecuencia cardíaca;
- ritmo cardíaco;
- actividad ventricular;
- eventos de detección.

---

## 6.4 Parámetros de estimulación

Registrar:

- frecuencia;
- salida;
- sensibilidad;
- duración del pulso;
- modo.

---

## 6.5 Componentes

Mostrar:

- generador externo;
- controles;
- pantalla;
- compartimiento de baterías;
- conexiones;
- cable de paciente;
- sistema de estimulación.

La página técnica de Medtronic también documenta los cables de estimulación compatibles con el modelo.

---

## 6.6 Características físicas

Mostrar:

- dimensiones;
- peso;
- tipo de batería;
- vida útil de servicio.

---

## 6.7 Riesgos y advertencias

Esta sección debe utilizar únicamente información documentada por el fabricante.

Debe incluir, cuando corresponda:

- batería baja;
- problemas de conexión;
- problemas de cables;
- condiciones de funcionamiento;
- advertencias del fabricante.

No agregar riesgos no documentados.

---

# 7. MÓDULO 2 — SIMULADOR

Este es el núcleo de la aplicación.

La pantalla debe dividirse en:

### Panel izquierdo
Configuración.

### Panel central
Señal.

### Panel derecho
Estado.

---

# 8. PANEL DE CONFIGURACIÓN

## 8.1 Escenario

El usuario podrá seleccionar:

1. Ritmo sinusal.
2. Bradicardia.
3. Ausencia de actividad ventricular simulada.
4. Alteración de detección.

Todos deben estar identificados como *escenarios de simulación educativa*.

---

# 9. MODO DE ESTIMULACIÓN

El simulador debe permitir:

### VVI
Estimulación ventricular a demanda.

### VOO
Estimulación ventricular asíncrona.

El equipo real utiliza estos modos dentro de sus configuraciones monocamerales.

---

# 10. PARÁMETRO: FRECUENCIA

La interfaz debe mostrar:

*RATE / FRECUENCIA*

Unidad:

*ppm*

Rango técnico del equipo:

*30–200 ppm*

Incrementos documentados:

- 30–50 ppm: incremento de 5 ppm.
- 50–100 ppm: incremento de 2 ppm.
- 100–170 ppm: incremento de 5 ppm.
- 170–200 ppm: incremento de 6 ppm.

Tolerancia documentada para la frecuencia básica:

*±2 %*.

Estos valores aparecen en la documentación técnica del Model 53401.

### Interfaz

Debe incluir:

- campo numérico;
- control deslizante o dial virtual;
- botones + y −;
- unidad ppm;
- validación de límites.

---

# 11. PARÁMETRO: SALIDA

Nombre:

*OUTPUT / SALIDA*

Unidad:

*mA*

Rango:

*0,1–25 mA*

Incrementos:

- 0,1–0,4 mA → incrementos de 0,1 mA.
- 0,4–1,0 mA → incrementos de 0,2 mA.
- 1,0–5,0 mA → incrementos de 0,5 mA.
- 5,0–25 mA → incrementos de 1,0 mA.

La tolerancia documentada depende del rango y de la impedancia de carga. Para el simulador educativo se debe mostrar el valor configurado y aclarar que se trata de una *representación virtual*, no una salida eléctrica real.

---

# 12. PARÁMETRO: DURACIÓN DEL PULSO

Nombre:

*PULSE WIDTH / DURACIÓN*

Valor documentado:

*1,5 ms*

Tipo:

*Fijo*

Tolerancia documentada:

*±10 %*.

El usuario no debe modificar este parámetro en la primera versión, ya que se representa como característica fija del modelo de referencia.

---

# 13. PARÁMETRO: SENSIBILIDAD

Nombre:

*SENSITIVITY / SENSIBILIDAD*

Unidad:

*mV*

Rango documentado:

*0,4–20 mV*

El fabricante utiliza este control para establecer la sensibilidad de detección. La guía de referencia explica que el valor de sensibilidad determina el nivel al que el equipo detecta un latido.

La interfaz debe permitir modificar el valor dentro del rango técnico.

---

# 14. TABLA MAESTRA DE PARÁMETROS

El programador debe implementar inicialmente:

| Parámetro | Rango/valor | Unidad | Modificable |
|---|---:|---|---|
| Frecuencia | 30–200 | ppm | Sí |
| Salida | 0,1–25 | mA | Sí |
| Sensibilidad | 0,4–20 | mV | Sí |
| Duración del pulso | 1,5 | ms | No |
| Modo | VVI / VOO | — | Sí |
| Cámara simulada | Ventricular | — | No |

---

# 15. CONTROLES DEL SIMULADOR

Debe contener:

*▶️ INICIAR*

*Ⅱ PAUSAR*

*■ DETENER*

*↻ REINICIAR*

*💾 GUARDAR SIMULACIÓN*

---

# 16. LÓGICA DEL MODO VVI

El modo VVI debe representarse de forma didáctica:

text
ECG SIMULADO
      ↓
DETECCIÓN
      ↓
¿SE DETECTA ACTIVIDAD?
      ↙️              ↘️
    SÍ                NO
    ↓                  ↓
INHIBIR PULSO     ESPERAR TIEMPO
                       ↓
                  GENERAR PULSO


Cuando se detecte actividad ventricular simulada:

*SENSE → activo*

*PACE → inhibido*

Cuando no se detecte actividad dentro del intervalo correspondiente:

*PACE → activo*

---

# 17. LÓGICA DEL MODO VOO

En VOO no se utilizará la detección para inhibir la estimulación.

La lógica didáctica será:

text
Frecuencia configurada
        ↓
Temporizador
        ↓
Pulso de estimulación
        ↓
Temporizador
        ↓
Pulso de estimulación


La señal debe mostrar los pulsos de manera periódica según la frecuencia configurada.

---

# 18. MÓDULO 3 — MONITOR DE SEÑALES

Debe mostrar en tiempo real:

## Señal 1

*ECG SIMULADO*

## Señal 2

*PULSO DE ESTIMULACIÓN*

Los dos deben compartir una escala temporal para que el estudiante pueda relacionarlos.

Ejemplo conceptual:

text
ECG

       /\                 /\                 /\
      /  \_______________/  \_______________/


PULSO

          │                   │
          │                   │
──────────┴───────────────────┴──────────────


---

# 19. INDICADORES

Debe existir una sección visual:

*PACE*

Indicará cuándo el simulador genera un pulso.

*SENSE*

Indicará cuándo el simulador detecta actividad.

La guía del 53401 utiliza indicadores PACE y SENSE en la operación y en las pruebas de detección/estimulación.

---

# 20. EVENTOS EN TIEMPO REAL

Crear un registro visual:

text
14:32:10 — Simulación iniciada
14:32:12 — Actividad detectada
14:32:12 — PACE inhibido
14:32:16 — Actividad no detectada
14:32:16 — PACE generado


Los eventos deben guardar:

- hora;
- tipo;
- descripción;
- estado.

---

# 21. MÓDULO 4 — ASISTENTE IA

Debe existir como módulo independiente.

## Interfaz

Debe tener:

- historial de conversación;
- campo para pregunta;
- botón enviar;
- respuesta;
- fuente/documento utilizado.

---

# 22. FUENTES DE LA IA

La IA únicamente podrá utilizar:

1. documentación oficial del Medtronic 53401;
2. guía de referencia;
3. documentación técnica incorporada por el grupo;
4. protocolos elaborados por el grupo;
5. material académico aprobado.

La página oficial de Medtronic proporciona la guía de referencia y recursos de compatibilidad del Model 53401.

---

# 23. LÍMITES DE LA IA

La IA:

- no debe navegar libremente por Internet para responder;
- no debe inventar información;
- no debe proporcionar recomendaciones clínicas;
- no debe realizar diagnósticos;
- no debe modificar parámetros automáticamente;
- no debe ejecutar acciones sobre el simulador sin autorización del usuario;
- no debe presentar una simulación como resultado clínico.

Si la respuesta no está en la documentación:

> *"La información solicitada no se encuentra en la documentación incorporada al sistema."*

---

# 24. PREGUNTAS PRECONFIGURADAS

El asistente debe ofrecer botones de preguntas frecuentes:

### Equipo

- ¿Qué es el Medtronic 53401?
- ¿Cuál es su función?
- ¿Qué tipo de equipo es?

### Parámetros

- ¿Qué es RATE?
- ¿Qué es OUTPUT?
- ¿Qué es SENSITIVITY?
- ¿Qué es la duración del pulso?

### Modos

- ¿Qué significa VVI?
- ¿Qué significa VOO?
- ¿Cuál es la diferencia entre VVI y VOO?

### Señales

- ¿Qué representa el ECG?
- ¿Qué representa PACE?
- ¿Qué representa SENSE?
- ¿Por qué se genera un pulso?

### Mantenimiento

- ¿Qué elementos deben inspeccionarse?
- ¿Qué problemas pueden afectar el funcionamiento?
- ¿Qué debe verificarse funcionalmente?

---

# 25. MÓDULO 5 — BIBLIOTECA TÉCNICA

Debe funcionar como repositorio documental.

## Categorías

- Información del equipo.
- Manuales.
- Guías de referencia.
- Especificaciones.
- Componentes.
- Mantenimiento.
- Protocolos.
- Normativa.
- Material educativo.
- Fuentes de IA.

---

# 26. FUNCIONES DE LA BIBLIOTECA

El usuario podrá:

- abrir documentos;
- visualizar documentos;
- buscar por nombre;
- filtrar por categoría;
- consultar información;
- identificar documentos utilizados por la IA.

---

# 27. MÓDULO 6 — MANTENIMIENTO Y EVALUACIÓN

Este módulo debe estar orientado al *mantenimiento didáctico y a la evaluación funcional simulada*.

Debe dividirse en:

1. Inspección.
2. Lista de chequeo.
3. Prueba funcional.
4. Instrumentos requeridos.
5. Resultado.
6. Observaciones.
7. Conclusión.

---

# 28. LISTA DE CHEQUEO

La interfaz debe permitir marcar:

- Inspección visual.
- Carcasa.
- Controles.
- Pantalla/indicadores.
- Compartimiento de baterías.
- Conectores.
- Cables.
- Configuración.
- Detección.
- Estimulación.
- Indicadores PACE/SENSE.

Los elementos definitivos del protocolo deben mantenerse vinculados a la documentación técnica incorporada por el grupo.

---

# 29. PRUEBA FUNCIONAL DIDÁCTICA

La aplicación debe presentar la prueba por pasos:

### Paso 1
Identificación del equipo.

### Paso 2
Inspección.

### Paso 3
Configuración simulada.

### Paso 4
Generación de escenario.

### Paso 5
Observación de ECG.

### Paso 6
Observación de PACE/SENSE.

### Paso 7
Registro del resultado.

### Paso 8
Conclusión.

No se debe interpretar el resultado como certificación de un equipo médico real.

---

# 30. INSTRUMENTOS

Debe existir una sección donde se documenten los instrumentos requeridos para una evaluación técnica real, pero el software únicamente los mostrará como *información educativa*.

El sistema no debe asumir que un estudiante dispone de instrumentos clínicos reales.

---

# 31. MÓDULO 7 — REGISTRO DE PRUEBAS

Cada práctica debe poder guardarse.

Campos:

- ID.
- Usuario.
- Fecha.
- Hora.
- Escenario.
- Modo.
- Frecuencia.
- Salida.
- Sensibilidad.
- Duración del pulso.
- Duración de la simulación.
- Eventos.
- Resultado.
- Observaciones.
- Conclusión.
- Fotografía/evidencia.

---

# 32. EVIDENCIA FOTOGRÁFICA

Debe existir un botón:

*SUBIR EVIDENCIA*

El estudiante podrá adjuntar una fotografía.

El sistema debe almacenar:

- nombre;
- fecha;
- usuario;
- archivo relacionado con la prueba.

No se deben generar fotografías automáticamente.

---

# 33. RESULTADOS

El estudiante debe poder seleccionar:

- Correcto.
- Incorrecto.
- Requiere revisión.

También debe existir un campo de observaciones.

---

# 34. CONCLUSIONES

Debe existir un campo de texto:

*Conclusión de la prueba*

Este campo será escrito por el estudiante.

La IA no debe generar automáticamente conclusiones que puedan presentarse como resultados experimentales reales.

---

# 35. MÓDULO 8 — HISTORIAL

Debe mostrar todas las prácticas realizadas.

Columnas:

| Campo |
|---|
| ID |
| Fecha |
| Usuario |
| Escenario |
| Modo |
| Frecuencia |
| Resultado |

Debe permitir:

- buscar;
- filtrar;
- ordenar;
- abrir;
- consultar detalle.

---

# 36. DASHBOARD

El dashboard debe mostrar indicadores generales:

### Número de simulaciones

### Número de pruebas

### Número de consultas a IA

### Escenarios practicados

### Últimas actividades

### Historial de resultados

No utilizar métricas clínicas ni indicadores que puedan interpretarse como evaluación de pacientes.

---

# 37. BASE DE DATOS

## Tabla usuarios

- id
- nombre
- correo
- rol
- fecha_registro

## Tabla simulaciones

- id
- usuario_id
- fecha
- hora
- escenario
- modo
- frecuencia
- salida
- sensibilidad
- duracion_pulso
- duracion_simulacion
- resultado

## Tabla eventos

- id
- simulacion_id
- timestamp
- tipo
- descripcion
- estado

## Tabla pruebas

- id
- usuario_id
- fecha
- tipo
- resultado
- observaciones
- conclusion
- evidencia

## Tabla documentos

- id
- nombre
- categoria
- descripcion
- archivo
- fuente
- fecha_incorporacion

## Tabla consultas_ia

- id
- usuario_id
- fecha
- pregunta
- respuesta
- documentos_utilizados

---

# 38. ARQUITECTURA DEL SOFTWARE

La arquitectura recomendada es:

text
                    USUARIO
                       │
                       ▼
                  FRONTEND
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    SIMULADOR       DASHBOARD       ASISTENTE
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                    BACKEND
                       │
              ┌────────┴─────────┐
              │                  │
              ▼                  ▼
        BASE DE DATOS       BIBLIOTECA
                                 │
                                 ▼
                         BASE DE CONOCIMIENTO


---

# 39. MOTOR DE SIMULACIÓN

El motor debe recibir:

text
escenario
modo
frecuencia
salida
sensibilidad


Y generar:

text
ECG
eventos de detección
pulsos de estimulación
indicador PACE
indicador SENSE
estado del sistema


---

# 40. MOTOR DE SEÑALES

La señal debe ser *sintética y educativa*.

No debe utilizarse como ECG clínico real.

Debe poder modificar:

- frecuencia;
- regularidad;
- presencia/ausencia de eventos;
- relación temporal con el pulso de estimulación.

La forma de onda debe representar visualmente los eventos cardíacos necesarios para el aprendizaje.

---

# 41. ESCENARIOS

## Escenario A — Ritmo sinusal

- actividad regular;
- eventos detectables;
- frecuencia estable;
- permite observar detección.

## Escenario B — Bradicardia

- actividad ventricular lenta;
- permite observar cuándo interviene el sistema de estimulación.

## Escenario C — Ausencia de actividad ventricular simulada

- no se generan eventos ventriculares intrínsecos;
- permite observar estimulación programada.

## Escenario D — Problema de detección simulado

Permite alterar artificialmente la detección para enseñar la relación entre sensibilidad y detección.

Todos los escenarios deben identificarse como *simulaciones educativas*.

---

# 42. INDICADORES DE ESTADO

La aplicación debe utilizar estados claros:

### Verde / normal

Sistema funcionando según la simulación.

### Amarillo / aviso

Parámetro modificado o evento que requiere atención educativa.

### Rojo / evento

Condición simulada que requiere revisión.

Los colores deben utilizarse como lenguaje visual y no deben representar alarmas clínicas oficiales del equipo.

---

# 43. SISTEMA DE USUARIOS

Para el prototipo:

### Estudiante

Puede:

- realizar simulaciones;
- consultar documentos;
- utilizar IA;
- registrar pruebas;
- consultar sus registros.

### Administrador

Puede:

- cargar documentos;
- administrar biblioteca;
- administrar usuarios;
- configurar contenidos;
- revisar registros.

---

# 44. SEGURIDAD

El sistema debe incluir una advertencia visible:

> *Este software es un simulador educativo. Las señales, parámetros y resultados son simulados y no representan mediciones clínicas ni deben utilizarse para diagnóstico, tratamiento o toma de decisiones sobre pacientes.*

---

# 45. TRAZABILIDAD DE LA IA

Cada consulta realizada al asistente debe guardar:

- pregunta;
- respuesta;
- fecha;
- usuario;
- documentos utilizados.

Esto permitirá demostrar durante la sustentación que la IA trabaja con documentación incorporada.

---

# 46. REQUISITOS FUNCIONALES

### RF-01
El sistema debe permitir acceder al módulo Equipo.

### RF-02
El sistema debe permitir seleccionar escenarios.

### RF-03
El sistema debe permitir seleccionar VVI o VOO.

### RF-04
El sistema debe permitir configurar RATE.

### RF-05
El sistema debe permitir configurar OUTPUT.

### RF-06
El sistema debe permitir configurar SENSITIVITY.

### RF-07
El sistema debe mostrar el valor fijo de duración del pulso.

### RF-08
El sistema debe generar ECG simulado.

### RF-09
El sistema debe generar pulsos simulados.

### RF-10
El sistema debe mostrar PACE.

### RF-11
El sistema debe mostrar SENSE.

### RF-12
El sistema debe mostrar eventos.

### RF-13
El sistema debe permitir iniciar, pausar, detener y reiniciar.

### RF-14
El sistema debe guardar simulaciones.

### RF-15
El sistema debe permitir consultar el historial.

### RF-16
El sistema debe permitir consultar documentos.

### RF-17
El sistema debe permitir realizar preguntas a la IA.

### RF-18
La IA debe utilizar únicamente las fuentes autorizadas.

### RF-19
El sistema debe permitir realizar listas de chequeo.

### RF-20
El sistema debe registrar pruebas.

### RF-21
El sistema debe permitir cargar evidencias.

### RF-22
El sistema debe permitir registrar conclusiones.

### RF-23
El sistema debe mostrar dashboard.

---

# 47. REQUISITOS NO FUNCIONALES

## Usabilidad

La interfaz debe ser sencilla y comprensible para estudiantes.

## Rendimiento

Las señales deben visualizarse de forma continua sin retrasos perceptibles durante la simulación.

## Responsividad

Debe funcionar correctamente en computador y, si es posible, tablet.

## Seguridad

No debe existir conexión con dispositivos médicos físicos.

## Trazabilidad

Las prácticas y consultas deben quedar registradas.

## Mantenibilidad

Los escenarios y parámetros deben poder modificarse sin reconstruir toda la aplicación.

## Escalabilidad

La arquitectura debe permitir agregar posteriormente nuevos escenarios o equipos.

---

# 48. DIAGRAMA DE BLOQUES GENERAL

text
┌──────────────────────────────┐
│           USUARIO            │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│          INTERFAZ            │
│       APLICACIÓN WEB         │
└──────────────┬───────────────┘
               ↓
      ┌────────┴─────────┐
      ↓                  ↓
┌──────────────┐   ┌───────────────┐
│   MOTOR DE   │   │   SISTEMA IA  │
│ SIMULACIÓN   │   │               │
└──────┬───────┘   └───────┬───────┘
       ↓                   ↓
┌──────────────┐   ┌───────────────┐
│ GENERADOR DE │   │ BASE DE       │
│   SEÑALES    │   │ CONOCIMIENTO  │
└──────┬───────┘   └───────────────┘
       ↓
┌──────────────┐
│   EVENTOS /  │
│   REGISTROS  │
└──────┬───────┘
       ↓
┌──────────────┐
│ BASE DE DATOS│
└──────────────┘


---

# 49. FLUJO PRINCIPAL DEL USUARIO

text
INICIO
  ↓
Seleccionar módulo
  ↓
SIMULADOR
  ↓
Seleccionar escenario
  ↓
Seleccionar modo
  ↓
Configurar parámetros
  ↓
INICIAR
  ↓
Generar ECG
  ↓
Detectar actividad
  ↓
Aplicar lógica VVI/VOO
  ↓
Generar pulso simulado
  ↓
Mostrar PACE/SENSE
  ↓
Registrar eventos
  ↓
DETENER
  ↓
Guardar prueba
  ↓
Registrar observaciones
  ↓
Registrar conclusión
  ↓
Consultar historial


---

# 50. CASOS DE USO

## CU-01 — Consultar información del equipo

Actor: estudiante.

Resultado: visualiza información técnica del 53401.

## CU-02 — Ejecutar simulación

Actor: estudiante.

Resultado: obtiene ECG y pulsos simulados.

## CU-03 — Modificar parámetros

Actor: estudiante.

Resultado: observa cambios en la simulación.

## CU-04 — Consultar IA

Actor: estudiante.

Resultado: recibe respuesta basada en documentación autorizada.

## CU-05 — Realizar prueba

Actor: estudiante.

Resultado: completa una prueba funcional educativa.

## CU-06 — Registrar evidencia

Actor: estudiante.

Resultado: guarda fotografía, observaciones y conclusión.

## CU-07 — Consultar historial

Actor: estudiante.

Resultado: visualiza prácticas anteriores.

## CU-08 — Administrar documentación

Actor: administrador.

Resultado: incorpora documentos a la biblioteca y base de conocimiento.

---

# 51. CRITERIOS DE ACEPTACIÓN DEL SIMULADOR

El software se considerará funcional cuando:

1. El usuario pueda seleccionar un escenario.
2. Pueda seleccionar VVI o VOO.
3. Pueda configurar RATE.
4. Pueda configurar OUTPUT.
5. Pueda configurar SENSITIVITY.
6. El ECG se genere dinámicamente.
7. Los pulsos aparezcan correctamente.
8. PACE cambie según el comportamiento simulado.
9. SENSE cambie según los eventos simulados.
10. VVI responda a la detección simulada.
11. VOO genere estimulación periódica.
12. Los eventos queden registrados.
13. La simulación pueda guardarse.
14. La información aparezca en el historial.
15. La IA pueda consultar la documentación.
16. La IA rechace preguntas que no estén sustentadas.
17. Las pruebas puedan registrarse.
18. Las evidencias puedan adjuntarse.

---

# 52. CRITERIOS DE ACEPTACIÓN DE LA IA

La IA debe:

- responder utilizando documentación incorporada;
- identificar la información utilizada;
- evitar respuestas no sustentadas;
- indicar cuando no dispone de información;
- diferenciar información del equipo real de información del simulador;
- no realizar diagnóstico;
- no generar resultados experimentales;
- no sustituir la sustentación del estudiante.

---

# 53. CRITERIOS DE ACEPTACIÓN DEL REGISTRO

Una prueba solamente podrá guardarse como completa cuando tenga:

- escenario;
- modo;
- parámetros;
- resultado;
- observaciones;
- conclusión.

La fotografía será opcional dependiendo de la práctica.

---

# 54. FASES DE DESARROLLO

## ETAPA 1 — CONCEBIR

Entregar:

- investigación;
- arquitectura;
- diagramas;
- casos de uso;
- flujo;
- wireframes;
- diseño de base de datos;
- preguntas IA;
- fuentes;
- límites;
- cronograma;
- repositorio.

## ETAPA 2 — DISEÑAR E IMPLEMENTAR

Debe funcionar:

- simulador;
- ECG;
- pulsos;
- interfaz;
- base de datos;
- biblioteca;
- IA básica;
- registro.

## ETAPA 3 — OPERAR Y VALIDAR

Agregar:

- dashboard;
- historial;
- protocolos;
- manual técnico;
- manual de usuario;
- IA integrada;
- validación;
- escenario de prueba entre grupos.

---

# 55. DOCUMENTACIÓN TÉCNICA BASE

La documentación principal del proyecto debe ser:

*Medtronic Model 53401 — Reference Guide.*

La guía oficial documenta, entre otros aspectos, la detección, los umbrales de estimulación, los indicadores PACE/SENSE, los modos y el reemplazo de baterías.

También debe incorporarse como fuente principal la página oficial del producto y la página técnica del modelo.

---

# 56. RESTRICCIÓN FUNDAMENTAL DEL PROYECTO

El programador debe considerar esta regla como requisito obligatorio:

> *El software representa digitalmente el comportamiento de un equipo biomédico real para fines educativos. No se pretende construir un dispositivo médico ni reproducir físicamente la terapia. Todas las señales, eventos, parámetros y resultados generados por el software son simulaciones.*

---

# 57. RESULTADO FINAL ESPERADO

Al finalizar el desarrollo, el estudiante debe poder entrar a la plataforma y realizar el siguiente recorrido:

*Inicio → Conocer equipo → Seleccionar escenario → Configurar VVI/VOO → Configurar parámetros → Iniciar simulación → Observar ECG → Observar PACE/SENSE → Analizar eventos → Consultar IA → Realizar prueba → Registrar resultado → Adjuntar evidencia → Escribir conclusión → Guardar → Consultar historial.*

La plataforma debe sentirse como una *herramienta de entrenamiento de Ingeniería Biomédica*, no como una página informativa ni como un simple generador de gráficas.

---

# 58. FUENTES TÉCNICAS PRINCIPALES

1. Medtronic. Model 53401 — Single Chamber Temporary External Pacemaker. Documentación oficial del fabricante.  
2. Medtronic. Model 53401 — Reference Guide. Rev. 02/2024.  
3. Medtronic. Single-Chamber Temporary Pacemaker — Technical/Product Information.  
4. Medtronic. Temporary External Pacemakers — Pacing Systems.  

Las fuentes oficiales deben permanecer disponibles dentro de la biblioteca del proyecto y ser las referencias prioritarias para la información técnica del equipo.
