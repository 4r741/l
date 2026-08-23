# Documentación operativa — Giraldo

Documentación operativa y de gobierno, en HTML autocontenido y sin dependencias salvo
las tipografías de Google Fonts. Se abren en el navegador, se publican como estáticos
en cualquier hosting y se exportan a PDF paginado para repartir en papel.

| Archivo | Documento | Alcance |
| --- | --- | --- |
| **`inicio.html`** | Portada del sistema | Puerta de entrada: qué es cada documento y cómo se abre. Es el archivo por el que empezar |
| **`memoria.html`** | Tesis de Dirección (v6.0) | Documento de gobierno para la Junta Directiva, en seis partes: posición competitiva y foso, sistema operativo y cartera de innovación, economía unitaria y creación de valor de empresa, riesgos y pre-mortem, la decisión —palancas, asignación de capital, hoja de ruta y los quince acuerdos que se someten a aprobación— y la cifra: el puente hasta 1,2 M€ con su cartera de nueve campañas |
| **`deck.html`** | Presentación de Junta | Cuarenta y tres diapositivas en 16:9 derivadas de la tesis, con portada de declaración, separadores de parte, guion del ponente (tecla `N`) y ruta corta de doce (tecla `E`) |
| **`instrumentos/captura.html`** | Captura de la línea base (2026) | La misma hoja en el navegador: se rellena, calcula y guarda en el equipo, sin instalar nada |
| **`instrumentos/…xlsx`** | Captura de la línea base (2026) | La versión en libro de cálculo, para quien prefiera Excel: doce hojas mensuales, umbrales editables, semáforo automático y resumen anual con tendencia |
| **`manual.html`** | Manual Maestro de Operaciones (v6.0) | Documento troncal: 14 fases del recorrido, manuales por puesto, funciones de vanguardia, RACI, indicadores, incentivos y puesta en marcha |
| **`index.html`** | Protocolo de Experiencia Clínica · Primera Visita (v6.0) | Desarrollo detallado de las fases presenciales de la PV, con estándares transversales, casos especiales y anexos |
| **`otros.html`** | Otros documentos del sistema (v6.0) | Los catorce documentos que rodean a los otros dos: compendio maestro, verificación de 322 puntos, auditoría de la clínica adquirida, decisiones de Gerencia y V1–V11, programa de 100 días, dosier de 30 días, protocolos por perfil, 18 fichas de innovación, plan de marca y captación, cuaderno de campo del día 1, puesta en marcha por perfil, continuidad legal y financiera, el posicionamiento «No medias sonrisas» y el programa de cuidado GTC |

Todos comparten sistema de diseño y están enlazados entre sí; ninguno es anexo de otro.
La Tesis añade sobre ese sistema una capa editorial propia —portada de declaración,
aperturas de parte, citas destacadas, notas al margen y fichas de decisión— porque
se lee en una sala de juntas, no en un puesto de trabajo.

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

## Cómo se reconstruye

```bash
python3 build.py            # documentos + verificación de coherencia
python3 build.py --todo     # además libro de cálculo, exportaciones y PDF
```

Ningún archivo publicado se edita a mano: todos se generan. El orden importa y
lo fija `build.py` —las figuras salen del modelo, la Parte VI de las figuras y
del modelo, la Tesis ensambla todo eso y la presentación toma sus figuras de las
mismas fuentes—, y si un paso falla se detiene ahí, porque un sistema a medio
construir no se publica. Al final ejecuta el verificador.

| Carpeta | Qué contiene |
| --- | --- |
| `fuentes/` | Los bloques de contenido de la Tesis: apertura, cada parte, fichas de decisión, censo, anexos, la hoja editorial y la calculadora. Los que llevan sufijo `-generada` los produce un guion y no se editan |
| `generadores/` | Los nueve guiones que producen figuras, Parte VI, anexos, `memoria.html` y `deck.html` |
| `build-*.py` | Los generadores de la portada, la hoja de captura, el libro de cálculo, las exportaciones y los PDF |
| `modelo-campanas.py` | El modelo del que sale toda cifra de la Parte VI |
| `check-coherencia.py` | El verificador |
| `recalc.py` | Recálculo del libro con LibreOffice, invocado por `build-libro.py` |

Esto no era así hasta la revisión de agosto: los generadores de la Tesis y de la
presentación vivían en un directorio temporal, de modo que los dos documentos
más largos del sistema solo podían corregirse a mano. Un documento que no se
puede regenerar es un documento que, a la tercera edición, deja de cuadrar con
los demás.

## Versión única y verificación de coherencia

Todas las piezas comparten número de versión y fecha: **v6.0 · Agosto 2026**.
Antes de esta edición convivían cuatro numeraciones —5.5, 1.3, 2.0 y 1.0— y no
había forma de saber, mirando un documento, si estaba al día respecto de los
demás. Trece contradicciones se habían colado por ahí; están listadas, una a una,
en el §0.2 de la Tesis. La decimotercera la encontró el propio verificador.

```bash
python3 check-coherencia.py
```

Afirma veintiún hechos canónicos —cuántas fases tiene el recorrido y cuántas
la primera visita, cuántos indicadores, cuántos documentos operativos, qué
versión lleva cada archivo, cuántas hojas de acta, cuántas campañas, cuántas diapositivas— y falla
con código 1 si algún archivo dice otra cosa. Cubre también los nombres que
generan `build-export.py` y `build-pdf.py`, para que un PDF no salga marcado con
una versión que ya no existe; el interior del `.xlsx`, que es un zip de XML y se
audita igual que un HTML; y la numeración de las figuras. **Se ejecuta antes de
publicar.**

Un sistema que exige listas de verificación para todo lo demás no puede fiarse
de la memoria para comprobar su propia coherencia.

## El modelo de la cartera de campañas

```bash
python3 modelo-campanas.py            # la tabla, el puente y la concentración
python3 modelo-campanas.py --json     # los mismos datos, para figuras y documento
```

Ninguna cifra de la Parte VI está escrita a mano. Cada campaña declara cuánta
agenda ocupa, a qué tasa convierte y con qué ticket, y de ahí se deriva lo que
aporta. La regla que gobierna el cálculo es deliberadamente conservadora: **con
la agenda llena, una campaña no vale lo que factura, sino la diferencia entre el
paciente que trae y el paciente al que desplaza.**

De ahí salen tres resultados que no se buscaron:

- Las dos campañas más rentables son las dos más baratas —34× y 28×— y ninguna
  capta pacientes: trabajan sobre los que ya son del centro.
- Esas dos son el 63 % de lo que aporta la cartera. El colchón del 12 % no cubre
  que falle ninguna: si cae una, cae el objetivo.
- La única campaña con gasto externo relevante es la única con retorno directo
  negativo, porque en régimen de agenda llena desplaza visitas de más valor del
  que trae. Se aprueba igual, pero como habilitador de otras cuatro, no como
  campaña de retorno, y así consta.

`check-coherencia.py` ejecuta el modelo y comprueba que el documento no afirme
ningún número distinto del que ese modelo calcula. Lo hace leyendo el código
fuente y compilándolo en memoria, sin pasar por el sistema de importación: un
`.pyc` obsoleto podría validar contra un modelo viejo, y un verificador que da
verde por caché es peor que no tenerlo.

## Exportación a HTML autónomo

```bash
python3 build-export.py
```

Genera en `export/` ocho archivos que funcionan **sin conexión**, con las
tipografías incrustadas como data URI, más `LEEME.txt` y `Giraldo-HTML-v6.zip`
con el paquete entero listo para repartir:

| Archivo | Contenido |
| --- | --- |
| `Giraldo-INICIO-AQUI.html` | **La portada. Es el archivo por el que se empieza**: enlaza con los demás y explica qué es cada uno |
| `Captura-Linea-Base-Giraldo-v6.html` | La hoja de captura, lista para rellenar en el navegador |
| `Giraldo-TODO-EN-UNO-v6.html` | **Los siete documentos en un solo archivo**, con conmutador permanente arriba. Es el recomendado: no enlaza con ningún otro archivo, así que no hay nada que se rompa al guardarlo, renombrarlo o moverlo |
| `Tesis-Direccion-Giraldo-v6.html` | Solo la tesis. Se enlaza con los demás si conservan su nombre y están en la misma carpeta |
| `Presentacion-Junta-Giraldo-v6.html` | Solo la presentación, con guion del ponente y ruta corta |
| `Manual-Maestro-Giraldo-v6.html` | Solo el manual, con la misma condición |
| `Protocolo-Primera-Visita-Giraldo-v6.html` | Solo el protocolo, con la misma condición |
| `Otros-Documentos-Giraldo-v6.html` | Solo los otros documentos, con la misma condición |

La presentación y la hoja de captura anclan su JavaScript a su propio
contenedor —`.deck-raiz`, `.captura-raiz`— y buscan sus elementos por atributos
`data-`, no por identificador, para poder convivir dentro del archivo único con
los identificadores prefijados. El CSS de la presentación, que redefine `body`,
`table` y `.eyebrow`, se acota a `#doc-deck` con un reescritor de selectores.

El archivo único abre en la portada y admite enlaces profundos: `#doc-protocolo` abre el protocolo,
`#pv-f10` abre directamente su Fase 10 y `#ot-otros-marca` el plan de marca dentro
de `#doc-otros`. Los enlaces entre documentos —incluidos los
que apuntan a una sección concreta, como `manual.html#m13`— se convierten en
conmutadores internos que abren el otro documento y saltan a esa sección. La carpeta `export/` no se versiona
porque es regenerable.

## Tesis de Dirección (`memoria.html`)

No es un informe de situación: afirma qué creemos que es cierto sobre este mercado, qué
apostamos en consecuencia y bajo qué condiciones estaríamos equivocados. Conserva íntegros
los diez apartados de la Memoria v1.0 —renumerados— y los reordena en seis partes.

| Apartado | Contenido |
| --- | --- |
| Manifiesto | Las ocho reglas que ordenan el resto del documento, a partir de «no medias sonrisas» |
| §0 Control | Ficha del documento, marcas de naturaleza (hecho / modelo / pendiente) y cómo citar en acta |
| §0.1 Censo documental | Qué piezas existen, de qué clase y con qué propietario. La única fuente de la cifra «17 documentos operativos» |
| §0.2 Qué se reconcilió | Las trece contradicciones que arrastraba la 5.5 y cómo quedan resueltas |
| §1 Resumen ejecutivo | Qué está hecho, qué falta y qué se pide hoy |
| **I · La posición** | |
| §2 Tesis | Los tres segmentos desatendidos y los cinco indicadores que acreditan liderazgo |
| §3 Mapa competitivo | Las cuatro posiciones de la implantología en Vigo y por qué la cuarta está libre |
| §4 El foso | Qué se compra con dinero y qué no, con el tiempo de réplica de cada activo |
| **II · El sistema** | |
| §5 Sistema operativo | Qué se ha construido y qué garantiza tenerlo por escrito |
| §6 Cartera de innovación | Horizontes H1, H2 y H3, cada uno con su criterio de decisión |
| **III · La economía** | |
| §7 Línea base | Los cinco números pendientes y las seis preguntas incómodas sobre lo adquirido |
| §8 Economía unitaria | Escenarios a 36 meses, matriz de sensibilidad conversión × ticket medio y comprobación en directo de los tres supuestos |
| §9 El activo | Valor acumulado por paciente a cinco años, la escalera de valor de empresa y el múltiplo orientativo de cada peldaño |
| §10 Escalado | Los cinco pasos de un centro a una red, y por qué el orden es innegociable |
| **IV · El riesgo** | |
| §11 Riesgos | Cinco críticos con propietario y mitigación, siete de segundo orden y registro puntuado de diez con exposición, residual y disparador |
| §12 Pre-mortem | Seis causas de fracaso contadas desde 2029, con señal temprana y antídoto |
| §13 Cuadro de mando | Diez indicadores nucleares —ocho nucleares más los dos que exigen D13 y D14—, con diccionario de definiciones operativas: numerador, denominador, fuente y exclusiones |
| **V · La decisión** | |
| §14 Palancas | Cinco, ordenadas por coste de activación |
| §15 Asignación de capital | Orden de prelación en cinco prioridades y su única regla de excepción |
| §16 Hoja de ruta | Tres horizontes y tres puertas de paso |
| §17 Decisiones | D1 a D8 en tabla y D9 a D15 en ficha, con la alternativa descartada de cada una y el coste de no decidir cuantificado |
| §18 Supuestos | Todos los valores empleados en los modelos, con su origen, incluidos los de las nueve campañas |
| §19 Trazabilidad | Dónde se escribe cada acuerdo, cómo se verifica y en qué indicador se ve |
| **VI · La cifra** | |
| §20 El puente | De 720 k€ a 1,2 M€ bloque a bloque, con el colchón de no ejecución y la comprobación de si cabe en la agenda |
| §21 La cartera de campañas | Las nueve, con la visita que ocupan, su conversión, su ticket, lo que aportan, lo que cuestan y su retorno. Todo derivado del modelo |
| §22 Calendario y capacidad | Cuándo arranca cada una, la regla de no más de dos a la vez y la senda 890 · 1.060 · 1.200 |
| §23 Qué tiene que ser cierto | Las cinco condiciones del objetivo, el riesgo de publicidad sanitaria campaña a campaña y qué cuesta comprimir el plazo |
| Anexo A | Cuadernillo con las quince hojas de acta, una por decisión, listas para firmar |
| Anexo B | Una ficha por campaña: promesa, guion de apertura, contribución exigida, responsable y umbral de parada |

Las doce figuras son cálculos derivados de supuestos declarados, no datos de explotación:
coste real del descuento, primeras visitas necesarias según conversión, valor del paciente
a cinco años con y sin programa de cuidado, escenarios de facturación a 36 meses, matriz de
sensibilidad, valor acumulado por paciente, valor de empresa por peldaño, el puente hasta el
objetivo, el calendario de campañas, la composición de la cifra, el retorno de cada
campaña y la concentración de la cartera. Van numeradas 1 a 12 en el orden en
que se leen, y el número lo pone el generador: escribirlo a mano es lo que dejó
nueve figuras sin numerar y las otras tres desordenadas. Las paletas están
validadas para visión con deficiencia de color.

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
| 13 | «No medias sonrisas» | Posicionamiento y objetivo del centro: manifiesto, cinco pilares, qué significa por puesto y por fase, y cómo se comunica |
| 14 | GTC · Giraldo Te Cuida | El programa de cuidado anual: argumentos, speech por situación, objeciones, campaña, medición y marco legal |

## PDF paginado

```bash
python3 build-pdf.py
```

Genera en `export/pdf/` seis PDF: A4 con márgenes de encuadernación, cabecera de
clasificación, pie con «Página X de Y», encabezados de tabla repetidos al cambiar de
hoja y saltos controlados para que no se parta un cuadro por la mitad. Las quince
hojas de acta del Anexo A salen una por página, listas para rellenar a mano. La
presentación sale en apaisado 16:9, una diapositiva por página, y el guion del ponente
en A4 apaisado —hoja más alta— con la nota impresa bajo cada diapositiva. Requiere
Playwright con Chromium.

| PDF | Páginas |
| --- | --- |
| `Tesis-Direccion-Giraldo-v6.0.pdf` | 79 |
| `Manual-Maestro-Giraldo-v6.0.pdf` | 205 |
| `Otros-Documentos-Giraldo-v6.0.pdf` | 135 |
| `Protocolo-Primera-Visita-Giraldo-v6.0.pdf` | 90 |
| `Presentacion-Junta-Giraldo-v6.0.pdf` | 43 |
| `Guion-del-Ponente-Giraldo-v6.0.pdf` | 43 |

## Captura de la línea base (`instrumentos/`)

Existe en dos formatos con el mismo contenido y los mismos cálculos:
`captura.html`, que se rellena en el navegador y guarda en el propio equipo, y
`Captura-Linea-Base-Giraldo-2026.xlsx`, para quien prefiera un libro de cálculo.
Ambos se han verificado con los mismos valores de prueba y devuelven las mismas
cifras.

```bash
python3 build-libro.py     # genera y recalcula
```

openpyxl escribe las fórmulas sin valor en caché, así que el generador termina
pasando el libro por LibreOffice (`recalc.py`). No es un paso aparte que haya que
recordar: un libro publicado sin recalcular enseña casillas vacías a cualquier
lector que no calcule. La versión que declara la hoja «Instrucciones» tampoco se
teclea —la toma del verificador— y el propio verificador la comprueba dentro del
`.xlsx`, que es por donde se le escapó una vez.

`Captura-Linea-Base-Giraldo-2026.xlsx` es el instrumento del §7 y del §13: sin él, la
confesión de que faltan los cinco números se queda en confesión.

| Hoja | Contenido |
| --- | --- |
| Instrucciones | Qué se teclea, código de color y la regla de reporte |
| Definiciones | El diccionario de los diez indicadores; los umbrales se editan aquí una sola vez |
| `01` a `12` | Una hoja de captura por mes, con resultado y semáforo automáticos |
| Resumen anual | Los doce meses en una rejilla, con meses con dato, primero, último y tendencia |
| Los cinco números | Siete entradas y los cinco resultados calculados, incluido cuántas primeras visitas diarias exige el equilibrio |

Solo se teclean las casillas amarillas; el resto son fórmulas. Un indicador sin dato
aparece como `SIN DATO` y cuenta como rojo. Los resultados de los cinco números dicen
`pendiente` mientras falte una entrada, en lugar de dar una cifra inventada.

## Características comunes

- Filtro por puesto: atenúa las fases sin responsabilidad directa.
- Barra de navegación que centra automáticamente la sección activa.
- Modo claro único: los documentos se leen y se imprimen en papel; no hay modo oscuro ni conmutador de tema.
- Responsive y con hoja de estilos de impresión.
- Sin frameworks ni build: HTML, CSS y JavaScript sin dependencias.
- Todo se abre con doble clic, sin conexión y sin instalar nada; basta con mantener los archivos en la misma carpeta.
- La Tesis lleva una comprobación en directo de los supuestos económicos; en papel manda la matriz fija.
- La presentación se conduce con el teclado: `←` `→` `espacio` `Inicio` `Fin`, `N` guion del ponente, `E` ruta corta.

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

