# Protocolo de Experiencia Clínica — Excelencia Médica Giraldo

Sitio de una sola página con el protocolo operativo de la **Primera Visita (PV)** de
Clínica de Excelencia Médica Giraldo.

- **`index.html`** — documento completo, autocontenido (sin dependencias salvo las
  tipografías de Google Fonts). Se abre directamente en el navegador o se publica
  como estático en cualquier hosting.

## Contenido

| Bloque | Qué incluye |
| --- | --- |
| Fundamentos | Cinco principios rectores y nota de calibración temporal |
| Mapa de la visita | Distribución del tiempo por fase, filtro por rol y matriz de responsabilidad |
| Las 12 fases | Objetivo, acciones, guiones, registro obligatorio en Hermes y criterio de salida |
| Trazabilidad | Qué se registra, quién responde, en qué plazo y qué pasa si falta |
| Cuadro de mando | Seis indicadores de ejecución y de resultado |
| Anexos | Errores frecuentes, glosario y gobernanza del documento |

## Características

- Filtro por rol (Recepción · Director · Doctor · Auxiliar): atenúa las fases sin
  responsabilidad directa para leer el protocolo desde cada puesto.
- Tema claro y oscuro: sigue la preferencia del sistema y se puede alternar manualmente.
- Responsive y con hoja de estilos de impresión para editar la versión en papel.
- Sin frameworks ni build: HTML, CSS y ~90 líneas de JavaScript.

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

La barra de tiempos y el filtro se construyen en tiempo de carga a partir de esos
atributos: añadir o reordenar fases no requiere tocar el JavaScript.
