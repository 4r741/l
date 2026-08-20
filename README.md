# Documentación operativa — Giraldo

Tres documentos web autocontenidos, sin dependencias salvo las tipografías de Google Fonts.
Se abren directamente en el navegador o se publican como estáticos en cualquier hosting.

| Archivo | Documento | Alcance |
| --- | --- | --- |
| **`manual.html`** | Manual Maestro de Operaciones (v5.3) | Documento troncal: 14 fases del recorrido, manuales por puesto, funciones de vanguardia, RACI, indicadores, incentivos y puesta en marcha |
| **`index.html`** | Protocolo de Experiencia Clínica · Primera Visita (v5.3) | Desarrollo detallado de las fases presenciales de la PV, con estándares transversales, casos especiales y anexos |
| **`otros.html`** | Otros documentos del sistema (v1.1) | Los doce documentos que rodean a los otros dos: compendio maestro, verificación de 322 puntos, auditoría de la clínica adquirida, decisiones de Gerencia y V1–V11, programa de 100 días, dosier de 30 días, protocolos por perfil, 18 fichas de innovación, plan de marca y captación, cuaderno de campo del día 1, puesta en marcha por perfil y continuidad legal y financiera |

Los tres comparten sistema de diseño y están enlazados entre sí; ninguno es anexo de otro.

## Manual Maestro (`manual.html`)

| Parte | Contenido |
| --- | --- |
| Marco de vanguardia | Antelación sistematizada, los tres horizontes y los cinco pilares |
| I bis · Estándares transversales | Comunicación, seguridad clínica, emergencias médicas, protección de datos, plan de continuidad y orden de prioridades |
| I · Fundamentos | Ficha de control, nueve principios rectores, glosario, sistemas y puntos abiertos |
| II · Recorrido | Las 14 fases, con acciones, cronología minuto a minuto, percepción del paciente, guiones contrastados, casos especiales, contingencias, registro, KPI, errores y checklist de salida |
| III · Matriz RACI | Responsable, accountable, consultado e informado por fase |
| IV · Manuales por puesto | Recepción, Doctor, Higienista, Auxiliar, RAC, Dirección y compras, cada uno con misión, jornada, 26 procedimientos, contingencias, criterios de calidad e incorporación de 30 días |
| V · Funciones de vanguardia | Circuitos, reglas innegociables, límites e indicadores de cada función |
| VI · Interdependencias | Compras y proveedores, matriz de interdependencias y cuadro maestro de indicadores |
| VII · Plan de incentivos | Arquitectura, escala, pesos, fórmula de liquidación y gobernanza |
| VIII · Puesta en marcha | Las 72 horas previas y la mañana del día 1 |
| Anexos | Diez anexos: plantillas de reporte, cadencia, checklist de implantación, checklist imprimible de la PV, checklists por puesto, calendario, mapa maestro de documentos, ficha de auditoría trimestral, guion de reuniones y glosario de términos |
| Otros documentos del sistema | Compendio Maestro, Protocolo de Verificación de 322 puntos, Auditoría de la clínica adquirida y las 20 decisiones de gerencia con las 11 verificaciones externas |
| Notas de edición | Las diez incoherencias detectadas, con la decisión tomada en cada una, los puntos que siguen abiertos y el control de cambios |

Seis diagramas en SVG (sin librerías) sustituyen a los esquemas de texto del documento
original: circuito de producción, programa de mantenimiento, gestión de huecos,
planificación digital, circuito de esterilización y circuito de compras.

## Protocolo de Primera Visita (`index.html`)

| Bloque | Qué incluye |
| --- | --- |
| 01 Fundamentos | Cinco principios rectores y nota de calibración temporal |
| 02 Mapa de la visita | Distribución del tiempo por fase, filtro por rol y matriz de responsabilidad |
| 03 Flujo por roles | Diagrama de carriles con las entregas del paciente y los documentos que genera |
| 04 Las 12 fases | Acciones, cronología, percepción del paciente, guiones, casos especiales, política de descuentos, registro, errores y criterio de salida |
| 05 Estándares transversales | Comunicación, entorno, seguridad clínica, protección de datos, cartelería obligatoria, verificación observada del circuito y agenda |
| 06 Casos especiales | Situaciones que obligan a adaptar el circuito |
| 07 Trazabilidad | Qué se registra, quién responde y en qué plazo |
| 08 Cuadro de mando | Indicadores y rúbrica de auditoría |
| 09 Formación | Incorporación, certificación por rol y entrenamiento continuo |
| 10 Anexos | Guiones, preguntas frecuentes, errores, checklist imprimible, glosario, gobernanza y escalado de incidencias |

## Exportación a HTML autónomo

```bash
python3 build-export.py
```

Genera en `export/` cuatro archivos que funcionan **sin conexión**, con las
tipografías incrustadas como data URI:

| Archivo | Contenido |
| --- | --- |
| `Giraldo-Documentacion-Completa.html` | **Los tres documentos en un solo archivo**, con conmutador entre ellos. Es el recomendado: no depende de cómo se llame el archivo al guardarlo |
| `Manual-Maestro-Giraldo-v5.html` | Solo el manual. Se enlaza con los otros dos si conservan su nombre y están en la misma carpeta |
| `Protocolo-Primera-Visita-Giraldo.html` | Solo el protocolo, con la misma condición |
| `Otros-Documentos-Giraldo.html` | Solo los otros documentos, con la misma condición |

El archivo único admite enlaces profundos: `#doc-protocolo` abre el protocolo,
`#pv-f10` abre directamente su Fase 10 y `#ot-otros-marca` el plan de marca dentro
de `#doc-otros`. Los enlaces entre documentos —incluidos los
que apuntan a una sección concreta, como `manual.html#m13`— se convierten en
conmutadores internos que abren el otro documento y saltan a esa sección. La carpeta `export/` no se versiona
porque es regenerable.

## Otros documentos del sistema (`otros.html`)

| # | Documento | Qué aporta |
| --- | --- | --- |
| 1 | Compendio Maestro | Ordena la documentación en cuatro niveles, con seis consolidados |
| 2 | Verificación · 322 puntos | Recorrido físico por 12 zonas más documental, sistemas, procesos, economía y reputación |
| 3 | Auditoría de la clínica adquirida | El día 1 hora a hora y once áreas, una por semana |
| 4 | Decisiones de Gerencia | Las 20 decisiones y las 11 verificaciones externas V1–V11 |
| 5 | Programa de 100 días | Gobernanza, seis flujos de trabajo, tres puertas de paso y registro de riesgos |
| 6 | Dosier de 30 días | Cuatro semanas con guiones de llamada, plantillas y los cinco números |
| 7 | Protocolos por perfil | Parte asistencial y comercial de los seis puestos, con checklists y reportes |
| 8 | Innovación · 18 fichas | Protocolo, guion, contingencia e indicador de cada innovación |
| 9 | Marca y captación | Naming, siete segmentos y sus embudos, AEO, automatización y economía unitaria |
| 10 | Cuaderno de campo · día 1 | Página de emergencia, cronograma hora a hora, siete guiones difíciles, hojas de registro y semáforo |
| 11 | Puesta en marcha por perfil | Qué hace cada puesto durante la transición, con casuística y tabla de decisión rápida |
| 12 | Continuidad legal y financiera | Qué se transmite y qué no, huecos de cobertura, producto pendiente heredado, comunicación y plan de 4 semanas |

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

