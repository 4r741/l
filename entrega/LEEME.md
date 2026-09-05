# Entrega · Sistema documental Giraldo v15.0

Los cuatro archivos que contienen el sistema entero. Cada uno se basta solo.

| Archivo | Qué es |
| --- | --- |
| `centro.html` | **La web del centro.** Abre con una portada a pantalla completa y cada sección entra por una banda de imagen a sangre, en día o en noche. Las imágenes están dibujadas dentro del propio archivo —no hay fotografías del centro y no se han usado de banco—: campos de líneas, arcos, tramas y anillos, todos sobre el mismo motivo, el arco dental de catorce posiciones. Los seis puestos llevan retrato. Nueve secciones —Inicio, Dirección, Presentación, Protocolos, Primera Visita, Operaciones, Marketing, Otros y Los números—; al pulsar una se despliegan sus apartados. Cada sección lleva su documento entero más el bloque que pide: el reloj de los 123 minutos y los carriles de quién tiene al paciente, la matriz RACI de los seis puestos, el mapa de las catorce fases, la tabla de 76 acciones que se filtra y el puente de 720.000 € a 1,2 M€. Encima de todo eso hay tres cosas nuevas: **diez recorridos guiados** (soy paciente, soy la Junta, es lunes por la mañana, marketing, y uno por cada uno de los seis puestos) con sus 76 paradas en orden; el **mapa interactivo de las catorce fases**, donde se pulsa una fase y se lee, y se vuelve al mapa; y el **lector**, que abre cualquier apartado encima de la página con «anterior», «siguiente», el paso en el que va —«Soy paciente · 2 / 8»— y un «volver» que devuelve al sitio exacto del que se salió. Las voces técnicas —RACI, RAC, CBCT, IAC, producto pendiente…— se explican en un pop-up al pulsarlas. **Protocolos** trae el manual de cada puesto entero, en desplegables, dentro de su propia ficha: no hay un enlace al Manual, está el texto. Y **Presentación** trae las 43 diapositivas de la Junta legibles una a una, con su minuto, su parte y el guion del ponente debajo. Una sola paleta manda en toda la web —negro, gris y blanco, y un azul cobalto profundo, contenido, para lo que importa—: los documentos traían cada uno la suya y aquí se dibujan todos igual, sin tocar una letra de lo escrito. Los 691 enlaces internos están comprobados uno a uno: ninguno muerto, y el que cambia de sección lo dice antes de pulsarlo. Doble clic y se abre, sin conexión. |
| `Giraldo-TODO-EN-UNO-v15.html` | Los ocho documentos en una página web. Doble clic y se abre en cualquier navegador, sin conexión y sin instalar nada. Cada documento abre en una rejilla bento: el nombre en negro, la cifra que manda en verde pleno y una tarjeta por parte con sus apartados. El texto se abre al pulsar. |
| `Sistema-Documental-Giraldo-v15.0.pdf` | Los mismos ocho documentos encuadernados en 631 páginas, con portada, índice paginado y **128 marcadores**: uno por documento y uno por apartado. Sus referencias cruzadas son ahora **saltos internos del cuaderno**: pulsar «la matriz RACI» lleva a la página donde está. |
| `Sistema-Documental-Giraldo-v15.0.docx` | El sistema entero en Word, con índice automático, 335 tablas y las 23 figuras incrustadas. Y, por primera vez, **navegable**: 748 marcadores y 278 saltos internos, de modo que «véase la Fase 14» sea un enlace y no una instrucción para buscar a mano. |

Dentro de todos ellos está **Protocolos por puesto**: se elige Dirección, Doctor,
Recepción, RAC, Auxiliar o Higienista y aparece, en un solo sitio, en qué fases
del recorrido interviene ese puesto y con qué papel, qué procedimientos tiene
escritos, qué funciones de vanguardia le tocan, con qué se le mide y qué se
espera de él los primeros treinta días. Cada línea lleva al documento donde
está el detalle: la vista señala, no sustituye. En `centro.html` no hace falta ni
eso: el protocolo del puesto y las fases a las que lleva están en la misma página.

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
| `Giraldo-TODO-EN-UNO` | Los enlaces de los nueve documentos, pulsados uno a uno con el documento abierto | `verifica-unico.py` |
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
