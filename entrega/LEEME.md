# Entrega · Sistema documental Alma v27.0

Los cuatro archivos que contienen el sistema entero. Cada uno se basta solo.

| Archivo | Qué es |
| --- | --- |
| `centro.html` | **La web del centro.** Abre con una portada a pantalla completa sobre fondo casi negro y cada sección entra subiendo un suspiro al bajar la página. Las imágenes están dibujadas dentro del propio archivo —no hay fotografías del centro y no se han usado de banco—: campos de líneas, arcos, tramas y anillos, todos sobre el mismo motivo, el arco dental de catorce posiciones. Los seis puestos llevan retrato. Nueve secciones —Inicio, Dirección, Presentación, Protocolos, Primera Visita, Operaciones, Marketing, Otros y Los números—; al pulsar una se despliegan sus apartados. Cada sección lleva su documento entero más el bloque que pide: el reloj de los 123 minutos y los carriles de quién tiene al paciente, la matriz RACI de los seis puestos, el mapa de las catorce fases, la tabla de 76 acciones que se filtra y el puente de 720.000 € a 1,2 M€. Encima de todo eso hay tres cosas nuevas: **diez recorridos guiados** (soy paciente, soy la Junta, es lunes por la mañana, marketing, y uno por cada uno de los seis puestos) con sus 76 paradas en orden; el **mapa interactivo de las catorce fases**, donde se pulsa una fase y se lee, y se vuelve al mapa; y el **lector**, que abre cualquier apartado encima de la página con «anterior», «siguiente», el paso en el que va —«Soy paciente · 2 / 8»— y un «volver» que devuelve al sitio exacto del que se salió. Las voces técnicas —RACI, RAC, CBCT, IAC, producto pendiente…— se explican en un pop-up al pulsarlas. **Protocolos** trae el manual de cada puesto entero, en desplegables, dentro de su propia ficha: no hay un enlace al Manual, está el texto. Y **Presentación** trae las 43 diapositivas de la Junta legibles una a una, con su minuto, su parte y el guion del ponente debajo. Una sola paleta manda en toda la web —un fondo casi negro, la tinta en hueso y una sola nota de verde apagado para lo que importa—, con la Instrument Serif en los titulares: los documentos traían cada uno la suya y aquí se dibujan todos igual, sin tocar una letra de lo escrito. Los 691 enlaces internos están comprobados uno a uno: ninguno muerto, y el que cambia de sección lo dice antes de pulsarlo. Doble clic y se abre, sin conexión. |
| `Alma-TODO-EN-UNO-v27.html` | Los ocho documentos en una página web. Doble clic y se abre en cualquier navegador, sin conexión y sin instalar nada. Cada documento abre en una rejilla bento: el nombre en negro, la cifra que manda en verde pleno y una tarjeta por parte con sus apartados. El texto se abre al pulsar. |
| `Sistema-Documental-Alma-v27.0.pdf` | Los mismos ocho documentos encuadernados en 631 páginas, con portada, índice paginado y **128 marcadores**: uno por documento y uno por apartado. Sus referencias cruzadas son ahora **saltos internos del cuaderno**: pulsar «la matriz RACI» lleva a la página donde está. |
| `Sistema-Documental-Alma-v27.0.docx` | El sistema entero en Word, con índice automático, 335 tablas y las 23 figuras incrustadas. Y, por primera vez, **navegable**: 748 marcadores y 278 saltos internos, de modo que «véase la Fase 14» sea un enlace y no una instrucción para buscar a mano. |

Dentro de todos ellos está **Protocolos por puesto**: se elige Dirección, Doctor,
Recepción, RAC, Auxiliar o Higienista y aparece, en un solo sitio, en qué fases
del recorrido interviene ese puesto y con qué papel, qué procedimientos tiene
escritos, qué funciones de vanguardia le tocan, con qué se le mide y qué se
espera de él los primeros treinta días. Cada línea lleva al documento donde
está el detalle: la vista señala, no sustituye. En `centro.html` no hace falta ni
eso: el protocolo del puesto y las fases a las que lleva están en la misma página.

## La piel de NŌTA · el giro estético

La estructura de la versión 32 se queda entera —la espina numérica arriba, los
diez recorridos, el mapa de las catorce fases, el lector, los 135 apartados y
las 76 acciones—; lo que cambia es la **piel**, tomada de una web de referencia
(NŌTA) que pedía justo esto: negro casi puro, mucho aire, una serif de display
para la voz y una sola nota de color.

**El fondo se apaga.** Se va el papel cálido y entra un fondo casi negro
(`#0A0A09`), con la tinta en hueso (`#F1EFE8`) y el verde de lo clínico rebajado
a una nota apagada, reservada para el acento del lema y lo que de verdad
importa. Una regla une el color de todo el sistema: los tokens antiguos que usan
el buscador, el tablero, el mapa conceptual, el índice y las tablas cosechadas
de los ocho documentos se redefinen a oscuro a la vez, de modo que nada queda en
isla clara. Las tres matrices que sí conservan celdas claras —el calendario de
las nueve campañas, la facturación por conversión y ticket, el catálogo por
plazo y coste— lo hacen a propósito: ahí el claro es un extremo de la escala, no
un descuido, y se leen como lo que son, mapas de calor.

**La voz, en Instrument Serif.** Los titulares pasan a la misma serif de display
de la referencia —«No medias / sonrisas» en la portada, con *sonrisas* en
cursiva y en verde—, incrustada en el propio archivo junto a la Archivo y la
mono: el `centro.html` sigue abriéndose de doble clic y sin pedir una sola letra
a la red.

**El movimiento, sin guion.** Cada bloque entra una vez, subiendo un suspiro, y
lo dibuja la propia barra de desplazamiento —sin GSAP, sin una línea de guion—;
quien pide «menos movimiento» en su sistema no ve ninguno.

Comprobado a mano tras el giro: ni un texto queda claro sobre claro ni oscuro
sobre oscuro en toda la web, nada se monta encima de nada en siete tamaños por
trece secciones, y los enlaces y las anclas siguen llegando a donde dicen. El
contenido es el mismo v32, palabra por palabra; solo cambió cómo se ve.

## La barra, no el rail · versión 32

En la 31 quité las doce capas y puse una espina fija a la izquierda. Tenía
razón: un índice pegado a la izquierda es una web de documentación cualquiera
—el patrón más convencional que existe— y encima se comía el tercio izquierdo
de cada pantalla. No era disruptivo; era lo de siempre con otra letra.

### El giro de verdad: una espina numérica arriba

La navegación deja de ser una columna y pasa a ser **una sola línea fina en lo
alto**, con las trece secciones convertidas en **números, 00 a 12**. El número
donde se está se enciende y despliega su nombre; los demás son solo cifras. De
un vistazo se ve cuántas secciones hay, en cuál se está y a qué distancia de
las otras —y no se pierde ni una línea de lo que se lee—. En un teléfono esa
misma tira de números se desliza a lo ancho.

El contenido, ya sin rail que lo empuje, respira a toda la anchura.

### Lo que se limpió, pantalla por pantalla

- **Los rectángulos grises** de las tarjetas de recorrido —placeholders de una
  imagen que ya no existía— fuera. Ahora cada recorrido es tipográfico: número,
  quién, título y cuántas paradas.
- El buscador, los atajos, el índice completo, el tablero de las catorce fases,
  el mapa conceptual y el elector de recorridos conservan su estilo.

### Un error propio, y cómo lo cazó el sistema

Al quitar las capas viejas me llevé por delante el CSS de varias funciones
—el buscador salía como una lista de píldoras amontonadas, el elector de
recorridos enseñaba las diez rutas a la vez—. Lo cazaron los comprobadores:
`verifica-duplicados.py` avisó de que un recorrido aparecía dos veces, y así
descubrí que el elector se había quedado sin su hoja. La solución: el estilo de
las funciones se conserva y va antes de la hoja nueva, de modo que la hoja
manda en la maqueta y cada pieza recupera su apariencia.

Comprobado sobre el archivo entregado: las 13 secciones llegan, cero cajas
grises, 930 enlaces con 0 externos y 0 rotos, buscador correcto, sin errores de
consola, nada encima de nada en 7 tamaños × 13 secciones, ninguna sección
repetida.

## Desde cero, de verdad · versión 31

Las veces anteriores que me pidió empezar de cero, puse **otra capa encima**.
Esta no.

### El problema de fondo, con números

La hoja de estilo eran **doce capas** apiladas a lo largo de veinte versiones:
seis dentro de la hoja base —12, 15, 16, 17, 18 y 19— y seis más por fuera
—21, 22, 23, 24, 26 y 30—. **Sesenta y nueve mil bytes de parches** en los que
cada arreglo anulaba media regla de otro. Por eso cada vez que se tocaba algo
se rompía otra cosa en un sitio distinto, y por eso la página parecía
apelotonada aunque cada pieza suelta estuviera bien.

Se han quitado las doce. En su lugar hay **una hoja sola de ocho mil bytes**,
escrita de arriba abajo, que no se contradice a sí misma en ningún punto.

**La presentación de los ocho documentos no se toca**: sus tablas, sus figuras
y sus fichas son la literatura y se quedan como están.

### El giro: una espina, no una pantalla que se abre

El índice era una pantalla completa que se abría encima. Era bonita y **era la
razón de que uno se perdiera**: al cerrarla no quedaba rastro de dónde estaba.

Ahora hay una **espina fija a la izquierda**, siempre puesta, que no hay que
abrir y no tapa nada:

- **Las trece secciones**, a un clic desde cualquier punto del sistema.
- **La sección en la que se está**, marcada con una raya verde.
- **Dónde se está**, escrito arriba: sección, parte y apartado.
- Debajo, **Buscar** y el **Índice** completo de los 135 apartados, que siguen
  estando para quien quiera el detalle.

En un teléfono la espina se convierte en una barra horizontal arriba, con las
mismas trece secciones.

### Lo que encontró el comprobador en mi propia reescritura

`verifica-choques.py` —el que se escribió en la versión 30— **paró mi primera
compilación**: en el reloj de los 123 minutos, «Preparación» se montaba sobre
«Acogida». Al estrechar la columna para dejar sitio a la espina, el tramo más
corto se quedó en 62 píxeles. Cada tramo mide lo que duró su fase, y en dos
minutos de ciento veintitrés no cabe un nombre por mucho ancho mínimo que se
le dé: ahora el rótulo se corta dentro de su tramo con puntos suspensivos, y el
nombre entero sigue al pasar el ratón y al abrir la fase.

Comprobado sobre el archivo entregado: **13 de 13 secciones** llegan y se
marcan, 930 enlaces con 0 externos y 0 rotos, el buscador responde, sin errores
de consola, **nada se monta encima de nada en 7 tamaños × 13 secciones**, y
ninguna sección enseña dos veces lo mismo.

## Que nada se monte encima de nada · versión 30

Usted mandó una captura de su portátil. En ella se veía lo que yo no había
visto nunca: **el rótulo del centro y las primeras cifras del censo corriendo
por debajo de la barra de arriba**, y todo apelotonado contra el borde
superior.

### Los tres choques, y de dónde venían

1. **En 1100, 1280 y 1366 —o sea, en cualquier portátil—** el rótulo y el censo
   quedaban tapados por la barra. **Lo provoqué yo en la versión 26**: el
   escalón de portátil quitaba el aire superior de la portada sin reservar el
   alto de una cabecera que está fija. Y la dirección que se añadió en la 29
   alargó el rótulo hasta partirlo en dos líneas, que era la gota.
2. **En todos los tamaños, incluido el monitor grande**, «sonrisas» se metía
   dentro de «Le devolvemos su sonrisa». El lema va a un interlineado de 0,94
   para que sus dos líneas queden apretadas, y a ese valor la caja mide menos
   que las letras: lo que sobresale cae sobre el párrafo siguiente.
3. **A 1024×640** las dos últimas cifras del censo caían sobre la línea del pie.

### El arreglo, y por qué es estable

La portada **sangra a propósito** hacia arriba para que su fondo oscuro pase por
debajo de la barra transparente. Eso se conserva. Lo que faltaba es que el
*texto* bajara otro tanto.

Y el alto de la barra **no es un número**: cambia cuando el rótulo de posición
se parte en dos líneas, y cambia otra vez en un teléfono. Cualquier valor fijo
acierta en un tamaño y falla en el resto —que es exactamente lo que pasaba—. Así
que ahora **lo mide el navegador** y lo publica en una variable, y la hoja
reserva ese alto exacto más un respiro. Si mañana la barra crece, el hueco
crece con ella.

### Por qué no lo había visto

Porque mis barridos medían **una sola cosa**: que nada se saliera de la pantalla
a lo ancho. Un texto encima de otro no se sale de la pantalla — se queda dentro,
encima de otro. Medir lo que es fácil de medir no es lo mismo que comprobar.

Desde esta versión hay **`verifica-choques.py`** en la compilación: recorre
**siete tamaños × trece secciones** midiendo caja contra caja, y **para la
entrega** si encuentra un texto encima de otro o por debajo de la barra.

No cuenta lo que se superpone a propósito —el número de sección es una marca de
agua detrás del titular, las diapositivas se componen en capas, los desplegables
cerrados guardan dentro cajas que no se ven—. Distinguir eso costó cuatro
pasadas: la primera versión avisaba 25.739 veces, y un guardián que avisa 25.739
veces no sirve para nada.

Está probado como se prueban estas cosas: **se volvió a meter el defecto a
propósito** y lo cazó con dieciséis avisos, señalando exactamente el rótulo del
centro y el censo; se arregló y pasó limpio.

## El centro está en Ourense · versiones 28 y 29

El lema no cambia: sigue siendo **«No medias sonrisas»**. La ciudad, sí, y eso
no era un dato de pie de página.

### Por qué no bastaba con cambiar la palabra

Vigo estaba **dentro del argumento** del Plan de Marketing. Tres piezas se
apoyaban en que es ciudad de mar:

- **Apartado 12, «El mapa de la ría»** — coronas y localidades reales (Cangas,
  Moaña, Baiona), «veinte minutos por mar».
- **Apartado 13, «La Campaña de Mar»** — «Vigo vive del mar»: flotas,
  cofradías, la ventana de tierra de quien embarca, con las acciones A69 a A72.
- **Apartado 6, arquetipo 3, «El que embarca»** — el tripulante cuyo calendario
  decide la marea.

Cambiar solo el nombre habría dejado «Ourense y la ría» y una campaña pesquera
tierra adentro. Eso no se manda.

### Qué se ha reescrito, y marcado como supuesto

Se mantiene la estructura de las tres piezas y cambia la sustancia, con la
misma convención de **«modelo · a contrastar»** que el documento ya usaba:

- **«El mapa de la provincia».** Cuatro coronas: la ciudad (O Couto, A Ponte,
  Mariñamansa, O Vinteún, A Carballeira), el área urbana (Barbadás, San Cibrao
  das Viñas, O Pereiro de Aguiar, Coles, Toén), las comarcas (Verín, Xinzo de
  Limia, Allariz, Celanova, O Carballiño, Ribadavia) y **el retorno**. El
  principio se conserva entero: el área de influencia se mide en minutos de
  puerta a sillón, no en kilómetros; lo que cambia es que aquí los minutos los
  deciden la autovía y la carretera de montaña, no la ría.
- **«La Campaña del Retorno».** El mismo razonamiento del original —un
  colectivo entero excluido por un problema de calendario, no de dinero— con el
  colectivo que en Ourense lo sufre: quien vive fuera y vuelve dos o tres
  semanas en agosto y en Navidad. Las acciones **A69 a A72** conservan sus
  códigos y cambian de destinatario: asociaciones de emigrantes, centros
  gallegos en el exterior y concellos en lugar de cofradías y armadores.
- **«Los seis de la provincia»**, con **«El que vuelve»** ocupando el lugar
  estructural de «El que embarca».
- **La figura FM4** pasa de «ventana de tierra por tipo de flota» a **«ventana
  de estancia por tipo de retorno»**, con sus cuatro colectivos y sus meses.
- **Las acciones A11 y A16** del catálogo, que nombraban el puerto, la conserva
  y las localidades de la ría.

### Una línea ética nueva, porque la anterior ya no aplicaba

El original tenía una regla que no se cruzaba: el informe de aptitud se emite
**para el tripulante, no para el armador**. Sin armador esa regla se queda sin
objeto, pero la tentación de esta campaña es otra y es igual de real: si alguien
se va el día 30, comprimir en tres semanas lo que necesita tres meses. La regla
nueva lo dice: **el calendario del paciente no manda sobre el calendario
clínico**. Si no cabe en la ventana, se planifica a dos estancias y se dice
claramente qué no se va a terminar este verano. Un centro que se llama «no
medias sonrisas» no entrega media boca porque el billete de vuelta tenga fecha.

### La dirección

**Centro de Excelencia Implantológica Alma · Calle Progreso 2 · Ourense.**

Va en las ocho líneas de dirección del sistema: la portada de la web, su pie,
el bloque de contacto, las portadas del Plan de Dirección, del Plan de
Marketing y del Manual de Operaciones, y las cabeceras del archivo único y del
PDF encuadernado. No va en las líneas de «lugar y fecha» de cada documento
—«Ourense · Versión 29.0 · Septiembre 2026»—, donde la ciudad sola es lo
convencional.

El código postal y la provincia anteriores —36203, Pontevedra— eran de Vigo y
se han quitado. No se han sustituido por unos nuevos: **si quiere el código
postal en la dirección, dígamelo y lo pongo.**

Comprobado recorriendo las trece secciones del archivo entregado: **cero
rastros** de la ciudad anterior, de lo marítimo y del nombre anterior; 919
enlaces con 0 externos y 0 rotos.

## La clínica se llama Alma · versión 27

El centro pasa a llamarse **Alma**. El cambio recorre el sistema entero: **698
sustituciones en 56 archivos**.

### Qué ha cambiado

- **El nombre del centro**, en todas sus formas: «Centro de Excelencia
  Implantológica Alma», «Centro Alma», «la manera Alma de hacer las cosas»,
  «Manual Maestro Alma», «Perfil Alma anual», «Recomienda Alma».
- **El programa de acompañamiento**: «Giraldo Te Cuida» pasa a **«Alma Te
  Cuida»** y su acrónimo **GTC a ATC**, en sus trece apartados del Plan de
  Marketing, en la cartera de campañas, en el glosario, en la figura y en los
  guiones de lo que Recepción le dice al paciente.
- **Los nombres de los cuatro archivos**: `Alma-TODO-EN-UNO-v27.html`,
  `Sistema-Documental-Alma-v27.0.pdf`, `Sistema-Documental-Alma-v27.0.docx`, y
  el libro de cálculo `Captura-Linea-Base-Alma-2026.xlsx`.

### Qué no ha cambiado, y por qué

**Los identificadores internos.** Cada apartado tiene una dirección —
`data-ap="gtc"`, `mk-k-gtc-giraldo-te-cuida`— y los 919 enlaces del sistema
apuntan a ellas. Renombrarlas rompería los enlaces sin que nadie ganara nada:
no se leen, no se ven y no se imprimen. Treinta y dos identificadores conservan
el nombre viejo en minúscula, a propósito.

**Todo lo demás de la literatura**: ni una palabra tocada más allá del nombre.

### Y un control para que no vuelva

`build-entrega.py` **para la entrega** si alguno de los cuatro archivos vuelve a
decir el nombre anterior. Se comprueba **con las mayúsculas puestas**, que es lo
que distingue el nombre visible del identificador interno.

Comprobado recorriendo las trece secciones del archivo entregado: **cero
apariciones** del nombre anterior en texto visible, 919 enlaces con 0 externos y
0 rotos, y «Alma Te Cuida» y «ATC» se encuentran en el buscador.

## El mapa del sistema, y el portátil · versión 26

### Un mapa conceptual, porque no había ninguno

La matriz RACI, el reloj de los 123 minutos y los carriles de responsabilidad
existían ya, y están bien donde están: dentro de sus documentos. Pero **ni
Inicio, ni Recorridos, ni el Mapa tenían un solo diagrama**, así que quien abría
esto por primera vez veía ocho documentos y ciento treinta y cinco apartados sin
saber qué relación guardaban entre sí.

La sección nueva, **El sistema**, lo enseña en una pantalla. Del lema cuelgan
las cuatro preguntas que sostienen un centro:

| | |
| --- | --- |
| **Qué se promete** | La posición, la economía y la decisión |
| **Cómo se hace** | El recorrido del paciente y quién responde |
| **Cómo llega el paciente** | Lo que se hace para que entre por la puerta |
| **Con qué se mide** | Sin números, cualquier objetivo es una opinión |

Debajo de cada una, sus piezas con su cuenta real —34 apartados de Dirección,
las 14 fases, los 6 puestos, la matriz RACI de 6×14, las 76 acciones, los 12
estados del paciente, los 5 números—. **Ninguna cifra está escrita a mano** y
las trece piezas llevan a donde se lee, comprobadas una a una.

### El índice enseña ya todas las opciones

Con el campo vacío hay **71 atajos en siete grupos**: las trece secciones, las
catorce fases, los siete grupos de marketing, los seis puestos, los ocho
documentos, los diez recorridos guiados y los conceptos que más se preguntan.
Todo a un toque, sin atravesar ninguna jerarquía.

### Un solo buscador

Había **dos**: la paleta que venía de antes y el campo del índice. Los dos
respondían a `Ctrl+K` y se abrían uno encima del otro. Como el del índice cubre
todo lo que cubría la paleta y además los conceptos, las fases, los puestos, los
grupos de marketing y las secciones, ahora todo lo que llamaba a la paleta
—`Ctrl+K`, `/` y el botón «Buscar»— abre el mismo: una caja, un atajo, una lista.

### Y hecha para un portátil

Una pantalla de 1280×800 deja unos **setecientos píxeles útiles** después de la
barra del navegador, no novecientos. Todo lo que estaba pedido «al alto de la
ventana» daba por bueno un monitor de sobremesa. Hay ahora un escalón propio
para el portátil que aprieta el aire vertical —la portada, las cabeceras de
sección, las filas del índice, los atajos— **sin tocar el tamaño de la letra que
se lee**. La portada pasa a caber en 586 píxeles.

## Lo que estaba duplicado, y por qué · versión 25

En la sección del Mapa **las catorce fases estaban escritas dos veces**: el
tablero que se añadió en la versión 22 y, debajo, la rejilla que ya las
dibujaba. Los mismos catorce nombres y los mismos minutos, una lista encima de
la otra.

El error es mío y tiene nombre. Al añadir el tablero me dije que ponerlo
**delante** de la rejilla era la manera de «no borrar nada». No lo era:
conservar no es duplicar. El texto de las fases vive en el Protocolo de Primera
Visita y en el Manual de Operaciones, y ahí sigue intacto, palabra por palabra;
lo que sobraba era una segunda lista de nombres. El tablero lleva todo lo que
llevaba la rejilla —número, nombre y minutos— y además dice dónde se lee cada
fase y por dónde va el recorrido.

También se decía **«Primera Visita» doce veces seguidas**, una debajo de cada
ficha. Eso es ruido, no información: ahora se dice una vez por tramo, en su
rótulo —«La primera visita · doce fases · 123 minutos · se leen en el Protocolo
de Primera Visita»—, que es además el que traía la rejilla.

La sección pasa de 3.693 a 2.069 píxeles.

### Y para que no vuelva a pasar

Hay un comprobador nuevo en la compilación, `verifica-duplicados.py`: recorre
las doce secciones y **para la entrega si alguna enseña dos veces el mismo
nombre junto**. Distingue lo que es defecto de lo que no: un índice de los seis
puestos y, tres mil píxeles más abajo, el manual de ese puesto, dicen su nombre
dos veces con toda la razón; lo que no vale es enseñarlo dos veces en la misma
pantalla.

Está probado como se prueban estas cosas: se volvió a meter la rejilla a
propósito y el comprobador cazó los once nombres repetidos; se quitó y pasó
limpio.

## Se entra escribiendo · versión 24

### Por qué el índice era un caos aunque estuviera bien dibujado

Era un árbol de doce ramas y ciento treinta y cinco hojas. Para llegar a una
fase de la primera visita había que **saber de antemano** que vivía dentro del
cuarto documento. Se le pedía al lector que conociera la estructura del sistema
antes de poder usarlo, y eso no lo arregla ninguna tipografía.

### Ahora se escribe

Un campo. Se escribe un apartado, un concepto —RACI, CBCT, GTC—, «fase 8»,
«recepción», «marketing», «puente»: lo que sea. Se busca **en todo a la vez**
—los 135 apartados, los 18 conceptos, las 14 fases, los 6 puestos, los 7 grupos
de marketing, los 8 documentos y los 10 recorridos— y se ordena por cuánto se
parece.

- **Sin acentos y sin mayúsculas**: «recepcion» encuentra «Recepción».
- **A trozos**: «preseco» encuentra «Presentación económica».
- **Por tipo y número**: «fase 8» va a la fase 08, el IAC.
- **Con el teclado**: `Ctrl+K` o `⌘K` desde cualquier sitio abre y pone el
  cursor dentro; `/` también. Flechas para elegir, `Enter` para entrar.
- **Un concepto se resuelve ahí mismo**: la definición aparece en el propio
  buscador, con su fuente, sin sacarle de donde está.

Todo ocurre dentro del archivo: no hay red, no se manda nada a ninguna parte y
funciona igual en un portátil sin conexión.

### Y con el campo vacío, los atajos

Debajo están, de un solo toque: **las catorce fases** de la visita con sus
minutos, **los siete grupos de marketing** con sus acciones, **los seis
puestos**, **los ocho documentos** y **los conceptos** que más se preguntan.
Eso es lo que casi todo el mundo viene a buscar, y ahora está a un clic sin
tener que atravesar ninguna jerarquía.

**El árbol completo sigue estando**, plegado bajo «Todo el índice», para quien
prefiera recorrerlo. No se ha quitado nada: se ha cambiado por dónde se entra.

### Y lo que estaba duplicado

En la sección del Mapa aparecían dos rótulos diciendo lo mismo: «La primera
visita · 12 fases» y «La primera visita · doce fases · 123 minutos». El primero
lo había añadido yo con el tablero de la versión 22; sobraba y se ha quitado.

## Un índice donde se sabe dónde se está · versión 23

### Los enlaces que no iban a ningún lado

Eran **dieciséis**, y estaban donde usted los veía: en el índice. Apuntaban a
archivos de fuera —`memoria.html`, `manual.html#m14`, `marketing.html#gtc`…—
que no existen cuando se abre `centro.html` solo, que es exactamente como se
entrega. Tres de ellos, además, seguían **congelados en la versión 8**: la
página ofrecía «Giraldo-TODO-EN-UNO-v8.html» mientras el sistema iba por la
veintidós.

- Las **ocho puertas** de los documentos ahora llevan a su sección.
- Las **cinco referencias** de «Lo mío» (el programa GTC y tres fases) se
  resuelven contra el mismo mapa que usa el resto de la página.
- Los **tres archivos de la entrega** ya no se enlazan: se dice cómo se llama
  cada uno, con la versión vigente. Un archivo hermano solo existe si se ha
  guardado los cuatro juntos, y un enlace que a veces muere es peor que un
  nombre bien escrito.

Y **la compilación ahora se para** si sobrevive un solo enlace a un archivo de
fuera. Es la única manera de que no vuelva a colarse uno.

### Por qué el índice era un caos

Se puede señalar con el dedo: los treinta y cuatro apartados de una sección se
repartían en **tres columnas**. El orden de lectura bajaba por la primera,
saltaba arriba a la segunda y volvía a bajar, así que el 12 quedaba a la
derecha del 1 y no había manera de seguir el hilo.

Ahora es **una sola columna, en orden**, con las partes como cabeceras de
verdad —APERTURA, PARTE I · LA POSICIÓN…— y cada apartado con su número.

### Y por qué no se sabía dónde se estaba

Porque no se decía en ninguna parte. Ahora, en cuatro sitios:

- **La barra de arriba lo lleva escrito siempre**: sección, parte y apartado,
  sin tener que abrir nada.
- **El índice marca el apartado en el que se está**, con su «está aquí».
- **La sección abierta se queda pegada arriba** mientras se recorren sus
  apartados, para no acabar leyendo una lista sin saber de qué sección es.
- **Al desplegar una sección, sube justo debajo de la barra**, con sus
  apartados a la vista. Antes se quedaba a media pantalla y sus apartados
  nacían por debajo del borde.

Además, las doce secciones **caben ahora de un vistazo**: cada fila medía
ciento doce píxeles y doce eran mil trescientos, así que había que desplazarse
para ver el índice entero, que es justo lo contrario de lo que sirve un índice.

## El tablero, y las dos puertas que faltaban · versión 22

### Por qué «Mapa» y «Recorridos» no funcionaban

Funcionaban: lo que no había era manera de llegar. Ninguna de las dos estaba
en el índice. En el ordenador se llegaba por la barra de arriba; en un
teléfono, donde la barra solo deja sitio para GIRALDO y el índice,
**únicamente desde los dos botones de la portada**. Quien estuviera leyendo
cualquier otra cosa no tenía ruta de vuelta.

Ahora están las dos en el índice, detrás de «Inicio», **sin tocar el orden de
los ocho documentos**: Lo mío · Inicio · Recorridos · El mapa · Dirección ·
Presentación · Protocolos · Primera Visita · Operaciones · Marketing · Otros ·
Los números.

### Y por qué «Recorridos» parecía roto

Porque la sección volcaba **los diez recorridos enteros, uno detrás de otro**:
dieciocho mil novecientos píxeles en un ordenador y veinticinco mil novecientos
en un teléfono. Se pulsaba y aparecía un muro, no un menú, y elegir uno solo
bajaba por el muro hasta él.

Ahora se elige primero: los diez delante, y se abre uno cada vez. Entrar pasa
de 18.900 a 3.002 píxeles en el ordenador, y de 25.916 a 5.039 en el teléfono.
**Los diez siguen estando**, y quien no tenga guiones los ve todos seguidos
como hasta ahora.

### El tablero de las catorce fases

El mapa ya estaba y **sigue estando debajo, entero**. Lo que faltaba era ver el
recorrido como recorrido: dónde se está, cuánto queda y qué viene después.

Las catorce fases son ahora un tablero que se va superando. Cada una se marca
al pasarla; la que toca queda encendida, las superadas en verde y las que
faltan, atenuadas. Arriba, el marcador: cuántas fases y cuántos de los 123
minutos lleva. Lo que se marca **se guarda en su propio navegador**, así que
puede seguir mañana donde lo dejó hoy, y nadie ve su recorrido.

**Una advertencia sobre el juego: apagado no es cerrado.** Cualquier fase se
abre siempre, se haya superado o no. Esto es un centro médico, no un
videojuego: nadie puede quedarse sin leer un protocolo porque no haya pulsado
antes el botón de otro. Lo atenuado indica por dónde va el camino; nunca es una
puerta.

Se intentó primero sobre el arco dental, que es la curva con la que se dibuja
todo lo demás aquí. No funciona, y el propio sistema ya lo sabía: catorce
fichas con nombre sobre una curva se montan unas encima de otras. El tablero es
una rejilla en orden —seis casillas por fila en pantalla ancha, una por fila en
un teléfono— que no choca nunca.

## La composición · versión 21

Lo que había era correcto y era anodino: una columna de sesenta y seis
caracteres centrada en mitad de la pantalla, con trescientos setenta píxeles
de nada a cada lado, los rótulos encima del texto y los avisos metidos en
cajas de color. Esa es la maqueta por defecto de cualquier cosa.

**No se ha quitado una sola palabra.** Lo que cambia es dónde se pone cada cosa.

### La hoja se compone como un libro

La hoja ya venía partida en tres carriles —un margen, la columna de texto y
otro margen— para que las tablas pudieran salirse a sangre. El margen de la
izquierda llevaba vacío desde el primer día. Ahora es la **columna del
aparato**: ahí cuelgan el número del apartado, el rótulo de la parte y el
estado, alineados a la derecha contra el texto, como las notas al margen de
un libro bien hecho. Lo ancho —tablas, fichas, figuras— se sale a las dos
columnas y respira. Y un titular que presenta una tabla se alinea con la
tabla, no con el párrafo.

### El detalle que no se ve y se nota

- **Los avisos ya no son cajas de color.** Una raya arriba y el rótulo colgado
  en el margen dicen lo mismo sin hacer ruido.
- **Las tres fichas comparten sus tres filas**, así que el titular de la
  tercera se apoya en la misma línea que el de la primera aunque una lleve
  distintivo y la otra no. Antes las tres bailaban.
- **Las tablas, a filete fino**, con la cabecera en versal pequeña. Se leen
  como un estado de cuentas, no como una hoja de cálculo.
- **Los titulares se reparten solos** en vez de dejar una palabra huérfana, y
  los párrafos no terminan en una sílaba suelta.
- **Las cifras alinean en columna** porque todas miden lo mismo, y el cero
  lleva barra para que no se confunda con la o.
- **El movimiento, el justo**: cada bloque entra una vez, subiendo un suspiro.
  Se dibuja con la propia barra de desplazamiento, sin una línea de guion, y
  quien tenga pedido «menos movimiento» en su sistema no ve ninguno.

### La portada, con la jerarquía en su sitio

La promesa iba a ciento cincuenta y ocho píxeles y el lema del centro a
ochenta y cuatro: la letra pequeña era la marca y la grande, la frase. Entre
las dos estiraban la portada hasta los mil seiscientos píxeles —casi dos
pantallas— y la frase se cortaba por abajo sin que se viera dónde acababa.

Ahora manda el lema, **«No medias sonrisas»**, que es lo que dice este centro
de sí mismo; la promesa va debajo, grande pero a su medida. La portada entra
entera en una pantalla, en el ordenador y en el teléfono, y los dos botones se
ven sin bajar.

### Lo que hay dentro, dicho en la portada

El sesenta por ciento derecho de la portada estaba vacío. Ahí va ahora el
**censo del sistema**: ocho documentos, 135 apartados, catorce fases del
recorrido, seis puestos con protocolo, 76 acciones de marketing y diez
recorridos guiados.

Ninguna de esas seis cifras está escrita a mano: **todas se cuentan sobre lo
que se acaba de generar**. Si mañana hay un apartado más, ahí pondrá uno más.
No son cifras del sector ni promesas de resultado —es el inventario de esta
entrega, y por eso no puede desmentir al sistema.

### Y el subrayado que no pedíamos

Al convertir los mandos en enlaces para que el sistema se navegue sin guiones
(versión 20), el navegador les puso su subrayado de serie: el índice entero
salía rayado, y los números y las cuentas con él. Corregido: son mandos, no
citas. Solo va subrayado el nombre de la sección en la que se está.

## Por qué no se pulsaba nada · versión 20

El índice seguía sin funcionar, y la causa no estaba en el índice.

Un archivo que se abre con doble clic acaba en sitios donde **no se ejecutan
guiones**: el visor de un teléfono, la vista previa de una aplicación de correo
o de mensajería, un navegador con los scripts bloqueados. En esos sitios la
página se pintaba **entera y perfecta** —la portada, el botón de «Índice», los
dos botones, la tipografía— y no respondía a un solo clic. Cada mando del
sistema era un `<button>` que movía el guion; sin guion, todos muertos.

Fallaba sin avisar, que es la peor manera de fallar: nada en la pantalla decía
que faltase nada, así que no había forma de saber que el problema era el visor
y no el documento.

Ahora el guion es una mejora, no un requisito:

- **Los mandos son enlaces de verdad.** Las diez filas del índice, las ocho
  puertas de los documentos, los botones de la portada y los de la barra de
  arriba ya no son botones: son `<a href="#…">`. Con guion, el guion manda y
  hace lo de siempre. Sin guion, el navegador salta por su cuenta.
- **Sin guion, el sistema se enseña entero.** Todas las secciones a la vista,
  todos los apartados desplegados y el índice quieto al principio: un documento
  largo con su índice de enlaces, que es lo que esto es por debajo. Los
  ochocientos setenta y seis enlaces internos saltan solos.
- **Lo que no puede funcionar, no se enseña.** Sin guion desaparecen el botón
  de «Índice», el buscador, la flecha de desplegar y el lector. Un mando muerto
  en la pantalla es una promesa que no se cumple.
- **Y se avisa, una vez y arriba del todo**, de que se está viendo la forma
  simple del sistema y de que basta guardar el archivo y abrirlo con un
  navegador para tenerlo entero.

Si al abrirlo aparece esa banda negra arriba, el archivo está bien: es el visor
el que no ejecuta guiones. **Guarde el archivo y ábralo con Safari, Chrome, Edge
o Firefox** y tendrá el índice plegable, los recorridos y el buscador.

## El índice, en el teléfono · versión 19

El índice no se desplegaba en el móvil, y la causa no era de estilo: **cada
sección llevaba dos contenedores anidados** para su lista de apartados, uno
dentro del otro. El guion abría el de fuera y el de dentro se quedaba oculto,
de modo que la sección se desplegaba y dejaba un hueco en blanco. En el
escritorio pasaba lo mismo y no se notaba porque la lista se pintaba de otro
modo. Ahora hay un solo contenedor y los treinta y cuatro apartados de
Dirección aparecen donde tienen que aparecer.

Con eso resuelto, el índice se ha hecho a la medida de un teléfono:

- **El rótulo del buscador cabe.** Decía «Escriba y el índice se queda con lo
  que busca» y se salía por la derecha; ahora dice «Buscar» y la cuenta de
  apartados va al otro extremo de la misma línea.
- **Cada sección es una fila, no un bloque.** Número, nombre, cuántos apartados
  tiene y flecha, en una línea. Antes cada una medía doscientos píxeles de alto
  y solo cabían seis en la pantalla.
- **Dos gestos, y distintos.** El **nombre** lleva a la sección y cierra el
  índice: en una pantalla pequeña, si el índice se queda delante no se ve lo
  que se acaba de elegir. La **flecha** despliega los apartados sin cerrar
  nada, y es un blanco de cuarenta y cuatro píxeles, que es lo que mide un
  dedo. En el escritorio, donde el índice y lo que se lee conviven, el nombre
  sigue haciendo las dos cosas.
- **Ninguna banda muerta.** «Lo mío» e «Inicio» no tienen subapartados, y sin
  embargo el borde derecho de su fila seguía comportándose como una flecha:
  se pulsaba y no ocurría nada. Ahora la flecha solo es flecha cuando hay algo
  que desplegar; en esas dos filas ese hueco pertenece al nombre, y llevan a su
  sección se pulse donde se pulse.
- **El teclado no salta solo.** Abrir el índice enfocaba el buscador y en un
  móvil eso levanta el teclado y se come media pantalla. Ahora solo se enfoca
  en escritorio.

## Otra paleta y otra disposición · versión 18

**La paleta.** Se va el azul cobalto y se va el blanco de pantalla. Entra un
papel cálido —el del papel de verdad, no el del monitor—, una tinta casi negra
con un punto de tierra y un solo color: un verde azulado profundo, que es el
color de lo clínico sin ser el azul corporativo de todo el mundo. Sigue siendo
negro, gris, blanco y un color, pero ninguno de los tres es el que era. El
cambio alcanza también a lo que traen los documentos: la regla que unifica su
color apuntaba al cobalto y ahora apunta al verde, de modo que las tablas, los
semáforos y las figuras heredadas cambian con el resto.

**La disposición.** Todo estaba apilado en una columna centrada: rótulo debajo
de rótulo, bloque debajo de bloque. Ahora la cabecera de cada bloque se abre en
dos: a la izquierda cómo se llama, a la derecha qué es. Es la retícula de una
publicación y no la de un formulario, y cambia la lectura de todas las pantallas
sin tocar una palabra. Bajo 900 píxeles vuelve a una columna.

**Y cabe en un teléfono.** La tabla de las setenta y seis acciones arrastraba la
página treinta y siete píxeles a la derecha en un móvil: se recorría toda la web
de lado. Ahora lo que no cabe se recorre dentro de su propia caja y nunca se
lleva la página consigo. Comprobado sección por sección a 390 píxeles: ni una
arrastra la ventana.

## Lo mío, en el bolsillo · versión 17

**Fuera los dibujos de fondo.** Las bandas llevaban detrás un campo de líneas
onduladas. Un fondo dibujado no dice nada que el titular no diga y compite con
él por la atención: lo que se lee peor es el titular. Ahora la portada de una
sección es su número enorme, su nombre y una frase, sobre papel, con una regla
que los separa. Es lo que hace una editorial cuando quiere que se lea el
titular. De paso, el archivo adelgaza 270 KB: el bloque de dibujos que ya no se
usa no viaja.

**Y una sección nueva: «Lo mío».** Un sistema de ciento treinta y cinco
apartados no cabe en la cabeza de nadie, y quien ocupa un puesto tampoco lo
necesita entero. Se elige el puesto una vez —queda recordado en ese teléfono— y
aparece lo suyo, pensado desde el móvil hacia arriba: una columna, botones que
se pulsan con el pulgar, texto grande y ni una tabla.

- **De qué responde.** Las fases del recorrido en las que entra: en negro las
  que ejecuta o de las que responde, en gris aquellas en las que se le consulta
  o se le informa. Recepción ve que abre el recorrido; el Doctor, que sostiene
  el centro; el Higienista, que entra en la catorce.
- **Qué se rompe si no lo hace.** No es una lista de tareas: es lo que deja de
  funcionar aguas abajo. «No escanear el mismo día» → «pérdida de trazabilidad
  legal: lo firmado, a efectos prácticos, no existe».
- **La primera visita, como es.** Las doce fases y los minutos que sostienen
  todo lo demás, en orden y con quién lleva cada una.
- **Lo que representa Alma.** El manifiesto entero, tal como está escrito en
  el Plan de Dirección.
- **Alma Te Cuida.** El documento del programa, completo.

Nada de esto es un resumen: es el mismo texto de los documentos, ordenado por
persona en vez de por documento.

## Lo que estaba desorganizado · versión 16

Tres cosas, y las tres del mismo origen: al subir el cuerpo de letra en la
versión 12, todo lo que medía en letras subió con él.

**El aire dejó de ser aire y se volvió socavón.** Una separación de diez
unidades pasó de ciento sesenta píxeles a casi doscientos, y las piezas de una
sección dejaron de tener relación entre ellas: flotaban. Ahora el aire se mide
en pantalla y no en letras —crece con la ventana, no con el cuerpo del texto— y
hay una escala de cinco pasos que usa todo el sitio.

**El índice de una sección dejaba media pantalla vacía.** El rótulo de la parte
a un lado y los apartados al otro dejaba quince unidades de columna en blanco a
la izquierda y las líneas empezando a media pantalla. Ahora el rótulo de la
parte es una línea sobre sus apartados, con su número a la izquierda y cuántos
tiene a la derecha, y los apartados llenan el ancho en tres columnas. La misma
jerarquía, el triple de densidad y ni un hueco.

**Y las tablas se cortaban.** Un apartado se lee en una columna de sesenta y
seis caracteres, que es lo que se lee cómodo; pero dentro hay tablas de cinco
columnas, rejillas de tarjetas y figuras dibujadas, y a todas ellas esa columna
les quedaba corta: se cortaban por la derecha a mitad de palabra y el resto no
existía. Ahora el texto sigue en su columna y lo ancho se sale a los lados,
centrado, con su propio desplazamiento si aun así no cabe.

## Sin mando a la vista · versión 15

La versión 14 cambió la barra de arriba por un lateral permanente. Era el mismo
error con otra forma: mando a la vista todo el rato, ocupando un quinto de la
pantalla, que es lo que hace que una página parezca un programa de los noventa.

**Arriba solo hay dos cosas: la marca y la palabra «Índice».** La cabecera no
tiene barra de secciones ni cajas ni cristal esmerilado: se apoya en el papel
con una raya de un pelo, y desaparece cuando debajo hay una banda a sangre, que
es cuando tiene sentido que no esté.

**El índice se pide y se va.** Al pulsarlo ocupa la pantalla entera, en blanco:
las nueve secciones a tamaño de titular, una por línea, con su número, cuántos
apartados tiene y una raya de separación. Se pulsa una y sus apartados se
despliegan ahí mismo, en tres columnas, ordenados por partes. Se abre por la
sección en la que se estaba, que es lo que casi siempre se venía a mirar.
Encima, un campo de filtro a tamaño de titular: se escribe y el índice se queda
con lo que se busca. `Esc` limpia el filtro; con el filtro vacío, `Esc` cierra
el índice. Elegir cualquier cosa lo cierra también.

**Y lo que queda en pantalla es lo que se lee.** La portada ocupa la pantalla
entera, las secciones abren con su banda y el texto empieza por debajo de la
cabecera, no a su misma altura: dos rótulos a la misma altura se leen como uno
partido.

## Otra estructura · versión 14

Las versiones anteriores fueron puliendo la misma web: una barra arriba con
nueve nombres y, debajo, nueve páginas larguísimas por las que había que bajar.
Esta cambia la estructura, no el acabado.

**Fuera la barra de arriba. Un raíl a la izquierda con el sistema entero.**
Siempre a la vista, siempre en el mismo sitio: las nueve secciones, y dentro de
cada una sus apartados con su parte y su número. Se pulsa una sección y se
despliega ahí mismo, sin tapar nada, porque el raíl vive en su columna y lo que
se lee vive en la suya. Una sección abierta cada vez: nueve listas abiertas a la
vez no son un índice, son una lista de ciento treinta y cinco líneas.

**Un filtro encima del índice.** Con ciento treinta y cinco apartados, buscar es
más rápido que recordar. Se escribe «campaña» y el árbol se queda con Dirección
y Marketing y sus cuatro líneas. `Intro` abre la primera; `Esc` limpia.

**Una sola cosa en pantalla.** El lector deja de ser una capa que tapa la
pantalla entera y pasa a ocupar el panel: el raíl se queda a la vista mientras
se lee, de modo que se puede saltar a otro apartado sin cerrar nada, y la línea
del apartado que se está leyendo se marca en el índice. Leer sin saber dónde
está uno en el índice era exactamente lo que pasaba antes.

**Y las bandas dejan de ser carteles.** La portada ocupaba una pantalla entera y
cada sección abría con otra: ahora son una entrada, no un cartel. Lo que se sale
a sangre se sale del panel y no de la pantalla, que es lo que antes metía las
bandas por debajo del raíl.

En pantalla estrecha el raíl entra por la izquierda con un botón, se apaga lo de
detrás y se cierra solo al elegir algo.

## Las cifras, dibujadas · versión 13

Hasta aquí los datos del sistema se enseñaban como se enseñan en un documento:
tablas, listas y barras horizontales. Se leen, pero no se ven. La versión 13 les
da la vuelta: cada cifra que importa se dibuja, con la misma mano con la que
están dibujadas las imágenes del centro —trazo fino, blanco, negro y un solo
color— y con la misma forma, **el arco dental de catorce posiciones**, que es la
forma del trabajo que se hace aquí. Que la figura y la imagen compartan la forma
no es un adorno: es lo que hace que las dos se lean como una sola cosa.

Son tres figuras, escritas a mano en SVG, sin ninguna biblioteca, y ninguna
inventa un número.

**El recorrido del paciente, de una sola mirada.** Las catorce fases colocadas
sobre el arco dental, que es además una sonrisa. Cada marca es una fase, su
posición es su sitio en el recorrido y su tamaño es lo que dura de verdad. En
azul, las fases en las que el paciente decide —el diagnóstico, la presentación
en 3D y la propuesta—, que son las que deciden si hay tratamiento y las que se
pierden de vista cuando el recorrido se lee como una lista de catorce. Cuáles
son no está tecleado: se buscan por su rótulo, de modo que si alguna vez cambian
de sitio el dibujo las sigue marcando donde estén.

**El puente, en cascada.** De los 720.000 € heredados al objetivo del tercer
ejercicio. Una barra por bloque decía cuánto aporta cada uno; una cascada dice
además dónde queda el total después de cada uno, que es la pregunta que se hace
de verdad delante de una Junta. Con la línea del objetivo cruzando el dibujo y
el acumulado escrito bajo cada bloque, se ve en qué punto exacto se cruza la
meta y cuánto colchón queda.

**Quién tiene el peso, y en qué fase.** Los seis puestos contra las catorce
fases, en puntos en vez de en letras. Ochenta y cuatro casillas con una letra
dentro obligan a leerlas una a una; el mismo dato en puntos enseña antes de leer
nada dónde se concentra el peso y en qué fases cambia de manos el paciente:
Recepción abre, el Doctor sostiene el centro del recorrido, Dirección aparece de
punta a punta y el Higienista solo entra en la catorce. Las letras de la matriz
siguen estando dentro de la ficha de cada puesto: el dibujo no las sustituye,
las ordena.

Las tres viven en `datos.py`, que es un lenguaje y no un adorno de una página:
dibujan con `currentColor` y con las variables de color del sitio, así que la
hoja de estilos manda sobre ellas y el archivo sigue abriéndose sin conexión.

## Lo que trae la versión 12

**La letra crece, y crece todo con ella.** Toda la web mide en unidades
relativas, así que subiendo la raíz sube el sistema entero y en proporción: el
cuerpo pasa de 16,5 a 19,5 píxeles, los rótulos pequeños de 9 a 13 —a 9 píxeles
con mucho espaciado un rótulo es un adorno, no un rótulo— y el aire entre líneas
crece con ellos. Los titulares se aprietan al crecer, que es lo que hace que un
titular grande parezca dibujado y no estirado. La barra de arriba es la única
que no crece: es mando y no lectura, y si subiera dejarían de caber las nueve
secciones en un portátil.

**Una paleta con un solo criterio.** Los grises eran seis tonos elegidos de uno
en uno; ahora son una escala con la misma distancia entre peldaños y un punto de
frío, para que el blanco no amarillee al lado del azul. Y el azul es más
profundo y menos eléctrico, para que a tamaño de titular acompañe en vez de
gritar. Sigue habiendo negro, gris, blanco y un solo color.

**El índice, redistribuido y segmentado.** Era una tirada de líneas en dos
columnas de CSS, que reparten por altura y no por sentido: quedaba desigual y el
rótulo de una parte podía acabar lejos de lo que rotula. Ahora cada parte del
documento es una **banda**: a la izquierda su número, su nombre y cuántos
apartados tiene —y se queda fija mientras se recorre—, a la derecha sus
apartados, que bajan por la primera columna y siguen por la segunda, que es como
se lee un índice numerado. Se ve la forma del documento de un golpe: cuántas
partes hay, cómo se llaman y qué pesa cada una.

**Los desplegables, modernos.** La fila entera es la zona que se pulsa, el signo
crece y gira, y el que está abierto se distingue del cerrado sin tener que
leerlo: una línea azul a la izquierda, el número en azul y el titular en negro.

## Marketing, ampliado

Cuatro bloques nuevos, todos sacados del mismo catálogo del que sale la tabla de
las setenta y seis. Ninguna cifra está tecleada.

- **Las siete apuestas del plan.** El plan no es una lista de acciones: son
  siete apuestas con un orden. Cada una con los estados del paciente sobre los
  que actúa, su número de acciones, cuántas no cuestan dinero, cuántas se
  empiezan ya y su techo de gasto al año.
- **Lo que se puede empezar el lunes sin gastar.** Las acciones que no cuestan
  dinero y no esperan a nadie: ni presupuesto, ni agencia, ni decisión de la
  Junta. Con quién sostiene cada una.
- **Quién sostiene el plan.** El reparto por puesto, con su barra: cuántas
  acciones, cuántas sin coste y hasta cuánto puede gastar cada uno. Un plan
  cuyo dueño es «marketing» no tiene dueño.
- **El marco: qué se puede decir y qué no.** Las tres franjas legales, cuántas
  acciones caen en cada una y qué obliga cada franja.

## Lo que trae la versión 11

**El menú se despliega y se vuelve a plegar.** Antes el índice de una sección se
abría solo al entrar en ella y se quedaba abierto tapando media pantalla, de
modo que para ver la sección había que adivinar que se cerraba volviendo a
pulsar el mismo nombre. Ahora hay dos gestos distintos y visibles: el **nombre**
lleva a la sección y deja la pantalla limpia para verla; la **flecha** de al
lado abre y cierra su índice sin moverse de sitio, y gira para decir en cuál
está. Estando ya dentro de una sección, su nombre hace lo mismo que la flecha.
`Esc` cierra el índice, y también lo cierra pulsar fuera.

**Las diapositivas son diapositivas.** Hay un proyector: se abre con «Proyectar
la sesión» o desde cualquier diapositiva con «Proyectar desde esta», ocupa la
pantalla entera y se pasa a la siguiente **pulsándola**. La banda de la
izquierda vuelve atrás; también valen las flechas del teclado, la barra
espaciadora, `Inicio` y `Fin`. Abajo se ve en cuál va —«12 / 37»—, en qué minuto
entra, a qué parte pertenece y un hilo de avance de la sesión.

Y lo que no cabe en una diapositiva se consulta **en un pop-up encima de ella,
sin quitarla de delante**: el guion del ponente con la pregunta difícil y su
respuesta, de qué apartado del Plan de Dirección sale y de qué naturaleza son
sus cifras. Un botón deja solo la ruta corta —las once que sostienen el
argumento cuando la sesión se queda en veinte minutos— y al cerrar se vuelve a
la diapositiva en la que se estaba, abierta y a la vista. Aquí no se ha escrito
ninguna diapositiva nueva: son las mismas que ya estaban, a tamaño de sala.

**Los índices, estructurados.** Un índice de sección era una tirada de líneas
repartida en dos columnas de CSS, y una columna de CSS reparte por altura y no
por sentido: el rótulo de una parte se quedaba al pie de una columna y sus
apartados aparecían en la siguiente, de modo que el índice decía una cosa y
ordenaba otra. Ahora cada parte es un bloque cerrado que no se puede partir, con
su nombre, **cuántos apartados tiene** y una línea de separación entre entradas.
Se ve la forma del documento antes de entrar en él.

## Lo que se ha arreglado en la versión 10

**La barra de navegación desaparecía.** Es el defecto de fondo detrás de lo que
se veía: al pasar de la primera pantalla, el índice de arriba se iba con el
papel y el resto de la web se leía sin navegación, con el texto pasando por
detrás de lo que quedaba pegado. La causa estaba escondida: la presentación es
una pantalla y su hoja de estilo trae `html,body{height:100%}`; al recoger su
literatura viene también su estilo, y esa línea le ponía a la web entera la
altura de la ventana —el cuerpo medía 900 píxeles con 10.592 de texto dentro—,
de modo que lo que estaba pegado arriba dejaba de estarlo en cuanto se acababa
la primera pantalla. Ahora la página recupera su altura y la barra se queda
donde tiene que estar, en las nueve secciones y a cualquier altura.

**El índice se cortaba a media línea.** Al desplegar una sección, sus apartados
se repartían en tres columnas de CSS, y una columna de CSS reparte el texto por
altura y no por sentido: el navegador cortaba por donde le tocaba —«06
Innovación: tres horizon…»— y esa media línea se leía encima del titular de la
banda de abajo. Ahora la pieza que no se puede partir es el grupo entero, así
que las columnas se llenan hasta arriba, sin huecos, y ninguna línea se parte.
El índice, además, es una hoja: se abre por encima de la página, apaga lo que
hay debajo y se desvanece por el borde inferior, de modo que una fila a medias
se lee como «hay más» y no como un error.

**La barra dejaba pasar el texto por detrás.** Sobre una banda a sangre el
cristal esmerilado es un acierto; sobre papel blanco era una mancha gris. Ahora
la barra se vuelve opaca en cuanto deja de estar sobre una banda, y se separa
del papel con una sombra de un pelo.

**Y el cambio de sección deja de ser un parpadeo.** La sección nueva entra
subiendo unos milímetros y su cabecera un instante después que el resto. Quien
tenga puesto en su sistema que no quiere animaciones no ve ninguna.

Además: el foco del teclado se ve igual en toda la web, los enlaces dentro del
texto se subrayan de izquierda a derecha al pasar por encima, y lo que se puede
pulsar se levanta un pelo al acercarse.

## Los cuatro archivos, enlace a enlace

La versión 8 comprobaba los enlaces de un archivo de los cuatro. Los otros tres
no los había mirado nadie, y tenían dos defectos de bulto:

**El PDF llevaba 264 enlaces al disco de la máquina que lo compiló.** Cada
documento se escribió para vivir junto a sus hermanos en una carpeta, y sus
referencias cruzadas —«véase la Fase 14», «la matriz RACI»— son enlaces a esos
archivos. Al encuadernar los ocho documentos en un solo cuaderno, esos enlaces
seguían apuntando a `file:///home/…/manual.html`: en el ordenador de cualquier
otro lector, no abren nada. Ahora los 264 son saltos internos del cuaderno y
caen en la página exacta: «la matriz RACI» va a la página 285, «Fase 07» a la
420. Y el cuaderno tenía ocho marcadores para 631 páginas —uno por documento—:
ahora tiene 128, uno por apartado, y se navega desde el panel del lector de PDF
sin hojear.

**El Word no tenía ni un enlace.** Ni un marcador. En un documento de
seiscientas páginas, «véase la Fase 14» era texto muerto: había que buscarla a
mano. Ahora lleva 748 marcadores y 278 saltos internos, y ninguno se queda sin
destino: lo que en la web es un enlace, en el Word es un salto, y lo que no
puede resolverse se queda en texto antes que llevar a ninguna parte.

**El archivo único tenía enlaces que existían y aun así no llevaban a nada.**
Mete los nueve documentos en la misma página y solo enseña uno; dentro de un
documento, además, hay cosas plegadas. Pulsar «Doctor · Su manual de puesto» en
el índice cambiaba de documento pero dejaba delante la ficha de Dirección, de
modo que el lector pulsaba y no se movía nada. Ahora, antes de ir a un sitio, se
abre lo que lo tapa: la ficha del puesto que toca, el desplegable cerrado, el
documento que no estaba abierto.

Las cuatro comprobaciones se ejecutan en cada construcción y paran el sistema si
fallan:

| Archivo | Qué se comprueba | Cómo |
| --- | --- | --- |
| `centro.html` | Los enlaces de las once secciones, pulsados uno a uno | `verifica-anclas.py` y `verifica-enlaces.py` |
| `Alma-TODO-EN-UNO` | Los enlaces de los nueve documentos, pulsados uno a uno con el documento abierto | `verifica-unico.py` |
| El PDF | Ni un enlace al disco de nadie; todo salto cae en una página que existe | `verifica-libro.py` |
| El Word | XML bien formado, todo hipervínculo con su marcador | `verifica-libro.py` |

## La entrega se construye sola

La carpeta se venía copiando a mano, y una copia a mano se olvida: en la versión
8 se entregó un `centro.html` que pedía las tipografías a Google al abrirse, de
modo que el archivo anunciado como «doble clic y funciona sin conexión» se veía
con otra letra en una sala sin red. Ahora la entrega la arma `build-entrega.py`,
que incrusta las tipografías y no deja salir nada que apunte al disco de esta
máquina, que pida algo a la red, que lleve otra versión o que nombre lo que no
puede nombrarse.

## Los enlaces

Ningún enlace de este sistema lleva a algo que no es. No es una promesa: es una
comprobación que se ejecuta cada vez que se construye, y que para la
construcción si falla.

`verifica-anclas.py` recorre cada enlace interno de los ocho documentos, busca
el titular del sitio al que aterriza y lo compara con lo que el enlace dice. No
compara cadenas —un índice bien escrito no repite el titular al que lleva—:
compara palabras con peso, entiende los números («fase 10» va a la fase 10) y
los romanos («Parte VIII» va a la parte 8), y admite que «manual» valga por
«manuales». Lo que sobrevive a eso se mira a mano, uno a uno, y se anota con su
motivo.

De ahí salieron dos enlaces torcidos, ya arreglados en el origen:

| Decía | Llevaba a | Ahora lleva a |
| --- | --- | --- |
| «Ver la matriz de obligaciones» | Manuales por puesto | Qué pasa exactamente cuando un puesto no cumple · **Matriz de obligaciones** |
| «Rúbrica de auditoría» | Cómo se mide si el protocolo funciona | **Rúbrica de auditoría de una Primera Visita** |

Además, en `centro.html` ningún enlace es ya un salto a ciegas: el que cambia de
sección lo lleva escrito al lado, y todos dicen, al pasar el ratón, el nombre
del apartado al que llegan.

Y se ha arreglado el defecto que hacía que un enlace correcto pareciera
equivocado: **un apartado puede tener catorce fases dentro**, y pulsar «Fase 14»
abría el apartado por el principio, en la fase 1. Ahora el lector va al punto
exacto que pedía el enlace, lo marca un momento para que se vea, y la cabecera
lo dice: «Manual Maestro · Las catorce fases del recorrido · **Mantenimiento y
seguimiento a largo plazo**».

Y no se aterriza en mitad de un texto. Cuando un enlace pide una parte de un
apartado —«Fase 14» dentro de las catorce fases, un procedimiento dentro de un
capítulo—, el lector **enseña esa parte**, empezando por su titular, con una
línea que dice de qué apartado es y un botón para ver el apartado entero. Se
llega siempre arriba de lo que se pidió.

La comprobación final no es de código: es de uso. Se abre la página, se pulsan
**los 691 enlaces de las once secciones, uno a uno**, y se mira dónde se
aterriza. Ninguno cae fuera de sitio. En el archivo único son **1.117**, y
también se pulsan todos, con cada documento abierto.

## Cada sección, explicada antes de entrar

Las ocho secciones abren igual, y por eso no hay que aprender a leerlas dos
veces:

1. **Una banda de imagen** con el nombre del documento y una frase de qué es.
2. **Tres columnas**: *qué es*, *para quién* y *qué se hace con esto*. Tres
   frases, ni una más.
3. **La extensión, declarada**: cuántos apartados —o diapositivas, o puestos—,
   cuántas palabras y cuánto lleva leerlo entero. Está contado sobre el texto
   que de verdad hay en la página, no estimado: Operaciones son 37.579 palabras
   y casi tres horas. Declararlo es lo que permite no leerlo entero sin
   sensación de estar saltándose algo.
4. **Lo propio de la sección**, el índice completo, y el botón **«Leerlo entero,
   seguido»**: con independencia de la extensión, el documento se puede leer de
   la primera línea a la última sin abrir nada.

## Por dónde se sigue

Al final de cada sección hay dos puertas: adónde lleva lo que se acaba de leer y
qué se encuentra al otro lado. No son «enlaces relacionados» calculados por
parecido: están escritas una a una. De Marketing se sigue a Los números —con qué
se mide si una acción funciona— y a Otros —el contrato del programa GTC—; de
Primera Visita, a Protocolos y a las fases 13 y 14.

## Las diapositivas, explicadas

Cada una de las cuarenta y tres se abre con la diapositiva tal cual se proyecta
y, debajo, todo lo que hace falta para pasarla:

- **En qué minuto entra y cuánto dura**, medido contra la diapositiva siguiente
  de la sesión. **Dónde va**: la apertura o la parte I a VI, y cuál es dentro de
  su parte. Si es de la ruta corta, lo dice.
- **Qué hay que decir al pasarla, y qué contestar**: el guion del ponente, que
  hasta ahora no salía de las notas del documento, con la pregunta difícil que
  viene detrás y su respuesta.
- **De dónde sale**: el apartado exacto del Plan de Dirección del que se extrae,
  con su nombre y su enlace. La diapositiva es el extracto; ahí está el
  razonamiento entero, con los supuestos declarados. Treinta y cuatro de las
  treinta y siete lo llevan; las otras tres son la apertura y el cierre, que no
  extraen de ningún apartado.
- **La naturaleza de sus cifras**: si la diapositiva marca *Modelo*, *Hecho* o
  *Pendiente*, se explica qué significa esa marca y dónde están los supuestos.

Y cada una de las siete partes abre con **cómo se conduce** —cuántas
diapositivas, cuántos minutos, en qué orden va y por qué ese orden— y **dónde se
tuerce**: lo que suele pasar en esa parte de la sesión y cómo se responde.

## Las funciones de cada puesto

Quien ocupa un puesto tiene que poder contestar, sin abrir nada, a «¿cuáles son
mis funciones?». Estaban escritas —cada manual de puesto lleva sus
procedimientos numerados— pero había que ir a buscarlas dentro del capítulo.
Ahora salen delante, en la ficha del puesto:

- **Su misión**, la frase con la que abre su capítulo. Recepción: «Ser el
  sistema nervioso del centro: todo entra y sale por aquí, y nada se pierde».
- **Sus funciones, una por línea**, con su código, cuándo se ejecuta, para qué
  sirve y —cuando lo tiene— el número con el que se comprueba que se está
  haciendo. Recepción tiene catorce; Doctor, cinco; Dirección, RAC, Auxiliar e
  Higienista, cuatro cada uno.
- **Sus funciones de vanguardia**, con la línea que define cada una. Doctor
  seis, Recepción cinco, Higienista cuatro, Auxiliar tres.

Todo sale de los procedimientos numerados de su propio manual, palabra por
palabra: aquí se ordena y se enseña, no se resume.

## Las obligaciones de cada puesto

El Manual termina con una tabla que no dice qué hace cada puesto, sino **qué se
rompe aguas abajo cuando no lo hace**. Es la definición operativa de una
obligación: no «hay que escanear», sino «si no se escanea el mismo día, lo
firmado a efectos prácticos no existe».

Esa tabla vivía en el Manual y había que ir a buscarla. Ahora cada puesto lleva
las suyas delante, en su propia ficha, en dos columnas: **si no se hace** y **lo
que se rompe**. Recepción tiene cuatro, RAC tres, y Dirección, Doctor y Auxiliar
dos cada uno. El Higienista no tiene fila en esa matriz, y la ficha lo dice y
explica por qué: su trabajo empieza donde termina el circuito de la primera
visita.

## La imagen

Una web sin una sola imagen se lee como un documento, y era exactamente lo que
le pasaba a esta. No hay fotografías del centro y no se han puesto de banco: la
imagen se dibuja en el propio archivo, con `imagenes.py`.

Son cinco piezas —un campo de líneas que se levanta, arcos concéntricos, una
trama de puntos, anillos interrumpidos y seis retratos— y todas salen del mismo
motivo: **el arco dental y sus catorce posiciones**, que es la forma del trabajo
del centro y el número de fases del recorrido del paciente. En los arcos, las
tres posiciones marcadas en azul son las tres fases en las que el paciente
decide: el diagnóstico, la presentación y el cierre.

Cada pieza se publica una sola vez y cada banda recorta un trozo distinto y le
da su color desde la hoja de estilos. Así, once cabeceras distintas cuestan lo
que cuestan cinco dibujos: unos 270 KB de un archivo que sigue abriéndose con un
doble clic y sin conexión.

Sobre una banda oscura, la barra de navegación se aparta: se vuelve transparente
y blanca, como se abre una web. En cuanto la banda pasa, vuelve a ser la barra
de siempre.

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
