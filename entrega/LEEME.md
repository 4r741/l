# Entrega · Sistema documental Giraldo v8.0

Los cuatro archivos que contienen el sistema entero. Cada uno se basta solo.

| Archivo | Qué es |
| --- | --- |
| `centro.html` | **La web del centro.** Nueve secciones —Inicio, Dirección, Presentación, Protocolos, Primera Visita, Operaciones, Marketing, Otros y Los números—; al pulsar una se despliegan sus apartados. Cada sección lleva su documento entero más el bloque que pide: el reloj de los 123 minutos y los carriles de quién tiene al paciente, la matriz RACI de los seis puestos, el mapa de las catorce fases, la tabla de 76 acciones que se filtra y el puente de 720.000 € a 1,2 M€. Encima de todo eso hay tres cosas nuevas: **diez recorridos guiados** (soy paciente, soy la Junta, es lunes por la mañana, marketing, y uno por cada uno de los seis puestos) con sus 76 paradas en orden; el **mapa interactivo de las catorce fases**, donde se pulsa una fase y se lee, y se vuelve al mapa; y el **lector**, que abre cualquier apartado encima de la página con «anterior», «siguiente», el paso en el que va —«Soy paciente · 2 / 8»— y un «volver» que devuelve al sitio exacto del que se salió. Las voces técnicas —RACI, RAC, CBCT, IAC, producto pendiente…— se explican en un pop-up al pulsarlas. **Protocolos** trae el manual de cada puesto entero, en desplegables, dentro de su propia ficha: no hay un enlace al Manual, está el texto. Y **Presentación** trae las 43 diapositivas de la Junta legibles una a una, con su minuto, su parte y el guion del ponente debajo. Una sola paleta manda en toda la web —negro, gris y blanco, y el azul para lo que importa—: los documentos traían cada uno la suya y aquí se dibujan todos igual, sin tocar una letra de lo escrito. Los 644 enlaces internos están comprobados uno a uno: ninguno muerto, y el que cambia de sección lo dice antes de pulsarlo. Doble clic y se abre, sin conexión. |
| `Giraldo-TODO-EN-UNO-v8.html` | Los ocho documentos en una página web. Doble clic y se abre en cualquier navegador, sin conexión y sin instalar nada. Cada documento abre en una rejilla bento: el nombre en negro, la cifra que manda en verde pleno y una tarjeta por parte con sus apartados. El texto se abre al pulsar. |
| `Sistema-Documental-Giraldo-v8.0.pdf` | Los mismos ocho documentos encuadernados en 630 páginas, con portada, índice paginado y un marcador por documento. |
| `Sistema-Documental-Giraldo-v8.0.docx` | El sistema entero en Word, con índice automático, 335 tablas y las 23 figuras incrustadas. |

Dentro de todos ellos está **Protocolos por puesto**: se elige Dirección, Doctor,
Recepción, RAC, Auxiliar o Higienista y aparece, en un solo sitio, en qué fases
del recorrido interviene ese puesto y con qué papel, qué procedimientos tiene
escritos, qué funciones de vanguardia le tocan, con qué se le mide y qué se
espera de él los primeros treinta días. Cada línea lleva al documento donde
está el detalle: la vista señala, no sustituye. En `centro.html` no hace falta ni
eso: el protocolo del puesto y las fases a las que lleva están en la misma página.

## Las dos secciones que se rehicieron

**Protocolos · todo lo de un puesto, en una página.** Se elige uno de los seis y aparece,
sin salir de ahí: en qué fases del recorrido entra y con qué papel —la franja de las catorce
y, debajo, las mismas fases con su nombre, que se abren al pulsarlas—, y su manual de puesto
**entero**, repartido en desplegables: qué es el puesto y de qué responde, su autoridad y sus
límites, sus procedimientos, sus indicadores, sus contingencias, sus criterios de calidad y
sus primeros treinta días. Debajo, sus funciones de vanguardia, una por desplegable y
completas. Es el mismo texto del Manual Maestro, palabra por palabra: aquí se copia, no se
resume. La barra de los seis puestos se queda arriba mientras se lee, para cambiar de puesto
sin volver a subir.

**Presentación · las 43 diapositivas, legibles.** Estaban en el archivo pero no se veían: una
presentación dibuja las diapositivas unas encima de otras y oculta todas menos la que toca,
que es lo que hace falta para proyectar y lo contrario de lo que hace falta para leer. Ahora
se despliegan, agrupadas en las siete partes que la propia sesión tiene, cada una con el
minuto en el que entra. Y cada una lleva debajo **el guion del ponente**, que hasta ahora no
salía de las notas del documento: qué hay que decir al pasarla, y qué se contesta a la
pregunta difícil que viene detrás. Un botón deja a la vista solo la ruta corta —las doce que
sostienen el argumento entero cuando la sesión se queda en veinte minutos—.

## Cómo se recorre `centro.html`

Hay tres maneras de entrar, y las tres llevan al mismo sitio:

1. **Por el índice.** Se pulsa una sección del menú y se despliegan sus
   apartados. Es la manera de leer el sistema entero, en el orden en que está
   escrito.
2. **Por un recorrido.** Se elige quién es usted —paciente, Junta, el equipo un
   lunes por la mañana, marketing, o cualquiera de los seis puestos— y la web
   le lleva parada por parada por lo que le toca leer, en orden y sin
   perderse. Debajo de cada parada dice cuántas quedan.
3. **Por el mapa.** Las catorce fases del recorrido del paciente, dibujadas.
   Se pulsa una fase, se lee, y se vuelve al mapa donde estaba.
4. **Por un desplegable.** En Protocolos y en Presentación el texto está en la
   propia página: se pulsa el titular y aparece debajo. Un enlace que apunte a
   algo que está dentro de un desplegable cerrado lo abre antes de llevarle.

El lector ocupa la pantalla entera para que no distraiga nada: se avanza con
las flechas de la cabecera o con las teclas `←` y `→`, y se cierra con «Volver»
o con `Esc`. Siempre devuelve al punto exacto del que se salió: ir y volver,
sin perder el hilo.

Para descargarlos desde GitHub: entre en el archivo y pulse **Download raw file**
(el icono de la flecha hacia abajo, arriba a la derecha). No use «Raw» a secas en
el HTML: el navegador lo abriría en vez de guardarlo.

El resto de la carpeta `export/` no está en el repositorio porque se regenera
entera con `python3 build.py --todo`. Estos cuatro sí, porque son la entrega.
