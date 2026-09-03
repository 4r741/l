# Entrega · Sistema documental Giraldo v8.0

Los cuatro archivos que contienen el sistema entero. Cada uno se basta solo.

| Archivo | Qué es |
| --- | --- |
| `centro.html` | **La web del centro.** Nueve secciones —Inicio, Dirección, Presentación, Protocolos, Primera Visita, Operaciones, Marketing, Otros y Los números—; al pulsar una se despliegan sus apartados. Cada sección lleva su documento entero más el bloque que pide: el reloj de los 123 minutos y los carriles de quién tiene al paciente, la matriz RACI de los seis puestos, el mapa de las catorce fases, la tabla de 76 acciones que se filtra y el puente de 720.000 € a 1,2 M€. Encima de todo eso hay tres cosas nuevas: **diez recorridos guiados** (soy paciente, soy la Junta, es lunes por la mañana, marketing, y uno por cada uno de los seis puestos) con sus 76 paradas en orden; el **mapa interactivo de las catorce fases**, donde se pulsa una fase y se lee, y se vuelve al mapa; y el **lector**, que abre cualquier apartado encima de la página con «anterior», «siguiente», el paso en el que va —«Soy paciente · 2 / 8»— y un «volver» que devuelve al sitio exacto del que se salió. Las voces técnicas —RACI, RAC, CBCT, IAC, producto pendiente…— se explican en un pop-up al pulsarlas. Una sola paleta manda en toda la web —negro, gris y blanco, y el azul para lo que importa—: los documentos traían cada uno la suya y aquí se dibujan todos igual, sin tocar una letra de lo escrito. Los 644 enlaces internos están comprobados uno a uno: ninguno muerto, y el que cambia de sección lo dice antes de pulsarlo. Doble clic y se abre, sin conexión. |
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

El lector ocupa la pantalla entera para que no distraiga nada: se avanza con
las flechas de la cabecera o con las teclas `←` y `→`, y se cierra con «Volver»
o con `Esc`. Siempre devuelve al punto exacto del que se salió: ir y volver,
sin perder el hilo.

Para descargarlos desde GitHub: entre en el archivo y pulse **Download raw file**
(el icono de la flecha hacia abajo, arriba a la derecha). No use «Raw» a secas en
el HTML: el navegador lo abriría en vez de guardarlo.

El resto de la carpeta `export/` no está en el repositorio porque se regenera
entera con `python3 build.py --todo`. Estos cuatro sí, porque son la entrega.
