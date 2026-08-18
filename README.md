# Protocolo de Experiencia Clínica — Excelencia Médica Giraldo

Sitio de una sola página con el protocolo operativo de la **Primera Visita (PV)** de
Clínica de Excelencia Médica Giraldo.

- **`index.html`** — documento completo, autocontenido (sin dependencias salvo las
  tipografías de Google Fonts). Se abre directamente en el navegador o se publica
  como estático en cualquier hosting.

## Contenido

| Bloque | Qué incluye |
| --- | --- |
| 01 Fundamentos | Cinco principios rectores y nota de calibración temporal |
| 02 Mapa de la visita | Distribución del tiempo por fase, filtro por rol y matriz de responsabilidad |
| 03 Flujo por roles | Diagrama de carriles con las siete entregas del paciente y los documentos que genera cada tramo |
| 04 Las 12 fases | Acciones, cronología minuto a minuto, percepción del paciente, guiones, casos especiales, registro en Hermes, errores frecuentes y criterio de salida |
| 05 Estándares transversales | Comunicación, entorno físico, seguridad clínica, protección de datos y gestión de agenda |
| 06 Casos especiales | Doce situaciones que obligan a adaptar el circuito sin perder sus garantías |
| 07 Trazabilidad | Qué se registra, quién responde, en qué plazo y qué pasa si falta |
| 08 Cuadro de mando | Seis indicadores y rúbrica de auditoría de PV sobre 100 puntos |
| 09 Formación | Incorporación de 30 días, certificación por rol y entrenamiento continuo |
| 10 Anexos | Biblioteca de guiones, preguntas frecuentes del paciente, errores frecuentes, checklist imprimible, glosario, gobernanza y control de cambios |

## Características

- Filtro por rol (Recepción · Director · Doctor · Auxiliar): atenúa las fases sin
  responsabilidad directa para leer el protocolo desde cada puesto.
- Barra de navegación que centra automáticamente la sección activa.
- Diagrama de carriles en SVG, sin librerías, legible en tema claro y oscuro.
- Tema claro y oscuro: sigue la preferencia del sistema y se puede alternar manualmente.
- Responsive y con hoja de estilos de impresión (los desplegables se imprimen abiertos).
- Sin frameworks ni build: HTML, CSS y ~110 líneas de JavaScript.

## Edición

Todo el contenido está en `index.html` como HTML plano. Cada fase es un
`<article class="phase">` con estos atributos:

```html
<article class="phase reveal" id="f05" data-roles="auxiliar doctor"
         data-min="15" data-label="Diagnóstico">
```

- `data-roles` — roles implicados, separados por espacios (alimenta el filtro).
- `data-min` — duración nominal en minutos (alimenta la barra de tiempos).
- `data-label` — nombre corto de la fase.
- `data-time` — texto alternativo para el tooltip cuando la fase no se mide en minutos
  (por ejemplo, `Pre-visita` en la Fase 1).

La barra de tiempos y el filtro se construyen en tiempo de carga a partir de esos
atributos: añadir o reordenar fases no requiere tocar el JavaScript.

### Componentes disponibles

| Clase | Uso |
| --- | --- |
| `.block` + `.block__title` | Bloque temático dentro de una fase |
| `.mini` | Cronología interna (definición `dt`/`dd` por tramo) |
| `.saydont` | Dos columnas: lenguaje preferido frente a lenguaje a evitar |
| `.special` | Rejilla de casos especiales |
| `.checks` | Lista con casillas de verificación |
| `.sheet` | Plantilla o guion en monoespaciada |
| `.callout` | Aviso crítico |
| `.gate` | Criterio de salida de la fase |
| `details.faq` | Pregunta frecuente desplegable |
| `figure.fig` | Diagrama SVG con pie de figura |
