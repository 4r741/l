# Documentación operativa — Giraldo

Dos documentos web autocontenidos, sin dependencias salvo las tipografías de Google Fonts.
Se abren directamente en el navegador o se publican como estáticos en cualquier hosting.

| Archivo | Documento | Alcance |
| --- | --- | --- |
| **`manual.html`** | Manual Maestro de Operaciones (v4.0) | Documento troncal: 14 fases del recorrido, manuales por puesto, funciones de vanguardia, RACI, indicadores, incentivos y puesta en marcha |
| **`index.html`** | Protocolo de Experiencia Clínica · Primera Visita | Desarrollo detallado de las fases presenciales de la PV, con estándares transversales, casos especiales y anexos |

Ambos comparten sistema de diseño y están enlazados entre sí.

## Manual Maestro (`manual.html`)

| Parte | Contenido |
| --- | --- |
| Marco de vanguardia | Antelación sistematizada, los tres horizontes y los cinco pilares |
| I · Fundamentos | Ficha de control, nueve principios rectores, glosario, sistemas y puntos abiertos |
| II · Recorrido | Las 14 fases, con acciones, guiones, indicaciones de ejecución, KPI, errores y checklist de salida |
| III · Matriz RACI | Responsable, accountable, consultado e informado por fase |
| IV · Manuales por puesto | Recepción, Doctor, Higienista, Auxiliar, RAC, Dirección y la función transversal de compras |
| V · Funciones de vanguardia | Circuitos, reglas innegociables, límites e indicadores de cada función |
| VI · Interdependencias | Compras y proveedores, matriz de interdependencias y cuadro maestro de indicadores |
| VII · Plan de incentivos | Arquitectura, escala, pesos, fórmula de liquidación y gobernanza |
| VIII · Puesta en marcha | Las 72 horas previas y la mañana del día 1 |
| Anexos | Plantillas de reporte, checklists imprimibles y calendario de implantación |
| Notas de edición | Incoherencias detectadas entre documentos, para que Dirección las resuelva |

Seis diagramas en SVG (sin librerías) sustituyen a los esquemas de texto del documento
original: circuito de producción, programa de mantenimiento, gestión de huecos,
planificación digital, circuito de esterilización y circuito de compras.

## Protocolo de Primera Visita (`index.html`)

| Bloque | Qué incluye |
| --- | --- |
| 01 Fundamentos | Cinco principios rectores y nota de calibración temporal |
| 02 Mapa de la visita | Distribución del tiempo por fase, filtro por rol y matriz de responsabilidad |
| 03 Flujo por roles | Diagrama de carriles con las entregas del paciente y los documentos que genera |
| 04 Las 12 fases | Acciones, cronología, percepción del paciente, guiones, casos especiales, registro, errores y criterio de salida |
| 05 Estándares transversales | Comunicación, entorno, seguridad clínica, protección de datos y agenda |
| 06 Casos especiales | Situaciones que obligan a adaptar el circuito |
| 07 Trazabilidad | Qué se registra, quién responde y en qué plazo |
| 08 Cuadro de mando | Indicadores y rúbrica de auditoría |
| 09 Formación | Incorporación, certificación por rol y entrenamiento continuo |
| 10 Anexos | Guiones, preguntas frecuentes, errores, checklist imprimible, glosario y gobernanza |

## Características comunes

- Filtro por puesto: atenúa las fases sin responsabilidad directa.
- Barra de navegación que centra automáticamente la sección activa.
- Tema claro y oscuro, siguiendo la preferencia del sistema o manual.
- Responsive y con hoja de estilos de impresión.
- Sin frameworks ni build: HTML, CSS y ~110 líneas de JavaScript por página.

## Edición

Cada fase es un `<article class="phase">` con atributos que alimentan la interfaz:

```html
<article class="phase reveal" id="m05" data-roles="aux" data-label="Pruebas diagnósticas">
```

- `data-roles` — puestos implicados, separados por espacios (alimenta el filtro).
- `data-min` / `data-time` — duración, usada por la barra de tiempos de `index.html`.
- `data-label` — nombre corto de la fase.

### Componentes disponibles

| Clase | Uso |
| --- | --- |
| `.block` + `.block__title` | Bloque temático dentro de una fase |
| `.pr` | Ficha de procedimiento (PR-XX) con código, título y criticidad |
| `.rulebox` | Regla nuclear o principio innegociable |
| `.kpis` | Lista de indicador → objetivo |
| `.mini` | Cronología interna por tramos |
| `.saydont` | Lenguaje preferido frente a lenguaje a evitar |
| `.special` | Rejilla de casos especiales |
| `.checks` | Lista con casillas de verificación |
| `.sheet` | Plantilla o guion en monoespaciada |
| `.sem--rojo/naranja/amarillo/verde` | Semáforo de riesgo |
| `table.raci` | Matriz RACI con letras destacadas |
| `figure.flow` | Diagrama SVG con pie de figura |
| `.parthead` | Divisor de parte del manual |
