# -*- coding: utf-8 -*-
"""El sistema documental contado como se cuenta un centro, no como un archivo.

La forma está tomada de las webs de las clínicas de referencia internacional
—la que se pidió de modelo fue whiteclinic.pt—, que no ordenan su contenido
por documentos sino por preguntas: quiénes somos, en qué creemos, cuál es
nuestro método, quién es el equipo, cómo es la primera consulta, qué hacemos,
con qué tecnología, cuáles son los hechos. Un paciente —o un miembro de la
Junta, o alguien que entra a trabajar el lunes— no llega preguntando «¿dónde
está el Manual Maestro?». Llega preguntando «¿qué se espera de mí?» o «¿qué le
pasa a un paciente el primer día?».

Esta es la capa que contesta esas preguntas. No añade ni una línea de
literatura nueva: cada entrada lleva a un apartado que ya existe, escrito, en
el documento donde manda. La estructura por documentos sigue intacta y sigue
siendo la que gobierna; esta es la otra puerta de la misma casa.

El nombre de la clínica que sirvió de modelo se queda aquí, en el código, y no
aparece en ningún documento publicado.
"""

# (documento, ancla, rótulo del enlace)
AREAS = [
    {
        "id": "a-quien-es-giraldo",
        "n": "00",
        "rotulo": "Quién es Giraldo",
        "pregunta": "¿Qué es este centro, qué promete y por qué se llama así lo que hace?",
        "que": "Un centro se define por lo que no está dispuesto a hacer. El nombre de "
               "todo esto es una frase: «No medias sonrisas». Aquí está qué significa, "
               "qué promete el centro a quien entra por la puerta y qué es exactamente "
               "lo que se ha construido para poder cumplirlo.",
        "enlaces": [
            ("memoria.html", "t-media-sonrisa-hace-medias-corte-nadie",
             "Qué es una media sonrisa, y por qué aquí no se hacen"),
            ("otros.html", "o-no-medias-sonrisas-posicionamiento-objetivo",
             "«No medias sonrisas» · el posicionamiento y el objetivo"),
            ("memoria.html", "t-este-centro-no-otro",
             "La promesa completa, y a quién se le hace"),
            ("memoria.html", "t-activo-llama-sistema-operativo-no-clinica",
             "El activo se llama sistema operativo, no clínica"),
        ],
    },
    {
        "id": "a-la-clinica",
        "n": "01",
        "rotulo": "La clínica",
        "pregunta": "¿Quiénes somos y dónde estamos parados?",
        "que": "La posición que ocupa el centro en Vigo, por qué es esa y no otra, "
               "y qué tiene que un competidor no puede comprar aunque tenga el dinero.",
        "enlaces": [
            ("memoria.html", "t-donde-estamos-parados-ahi", "Dónde estamos parados y por qué ahí"),
            ("memoria.html", "t-cuatro-formas-vender-implantes-vigo-dejamos",
             "Cuatro formas de vender implantes en Vigo, y la que dejamos libre"),
            ("memoria.html", "t-competidor-no-puede-comprar-aunque-tenga",
             "Lo que un competidor no puede comprar aunque tenga el dinero"),
            ("memoria.html", "t-ha-construido", "Qué se ha construido, pieza a pieza"),
        ],
    },
    {
        "id": "a-en-que-creemos",
        "n": "02",
        "rotulo": "En qué creemos",
        "pregunta": "¿Qué principio gobierna cada decisión, hasta la más pequeña?",
        "que": "Un centro se reconoce antes por lo que se prohíbe que por lo que ofrece. "
               "Aquí están el principio que gobierna todos los protocolos y las ocho "
               "cosas que no se harán nunca.",
        "enlaces": [
            ("manual.html", "m-principio-gobierna-todos-protocolos",
             "El principio que gobierna todos los protocolos"),
            ("manual.html", "m-fundamentos", "Fundamentos y principios rectores"),
            ("index.html", "p-cinco-principios-sostienen-doce-fases-primera",
             "Los cinco principios de la primera visita"),
            ("marketing.html", "k-creemos-nos-prohibimos-consecuencia",
             "Qué creemos, y qué nos prohibimos en consecuencia"),
            ("marketing.html", "k-ocho-no-haremos-nunca", "Las ocho que no haremos nunca"),
        ],
    },
    {
        "id": "a-el-metodo",
        "n": "03",
        "rotulo": "El método",
        "pregunta": "¿Cómo trabajamos, y qué compromiso adquiere el paciente con nosotros?",
        "que": "El programa Giraldo Te Cuida es el método con nombre: lo que el centro "
               "promete al paciente y lo que hace para cumplirlo. Debajo, los estándares "
               "transversales que valen para todo el mundo y en todo momento.",
        "enlaces": [
            ("otros.html", "o-gtc-giraldo-te-cuida", "GTC · Giraldo Te Cuida"),
            ("manual.html", "m-estandares-transversales-ampliacion",
             "Estándares transversales del centro"),
            ("manual.html", "m-documento-tres-usos", "Un documento, tres usos"),
            ("otros.html", "o-compendio-maestro-sistema-gestion",
             "Compendio Maestro del Sistema de Gestión"),
            ("otros.html", "o-como-encajan-catorce-documentos",
             "Cómo encajan los catorce documentos"),
        ],
    },
    {
        "id": "a-el-equipo",
        "n": "04",
        "rotulo": "El equipo",
        "pregunta": "¿Quién hace qué, y qué se espera exactamente de cada uno?",
        "que": "Seis puestos. Se elige el suyo y aparece en un solo sitio en qué fases "
               "interviene y con qué papel, qué procedimientos tiene escritos y con qué "
               "se le mide.",
        "enlaces": [
            ("protocolos.html", "s-elija-suyo", "Elija su puesto y vea todo lo suyo",
             ["perfil-direccion", "perfil-doctor", "perfil-recepcion",
              "perfil-rac", "perfil-auxiliar", "perfil-higienista"]),
            ("protocolos.html", "s-cumple-todos-puestos",
             "Lo que se cumple en todos los puestos, sea cual sea"),
            ("manual.html", "m-matriz-raci", "Matriz RACI · quién hace qué en cada fase"),
            ("manual.html", "m-manuales-puesto", "Los manuales de los seis puestos"),
            ("manual.html", "m-pasa-exactamente-cuando-puesto-no-cumple",
             "Qué pasa cuando un puesto no cumple"),
            ("otros.html", "o-protocolos-operativos-perfil", "Protocolos operativos por perfil"),
        ],
    },
    {
        "id": "a-primera-visita",
        "n": "05",
        "rotulo": "La primera visita",
        "pregunta": "¿Qué vive un paciente el día que entra por primera vez?",
        "que": "Ciento quince a ciento veinte minutos contados fase a fase, con quién "
               "tiene al paciente en cada momento y qué se hace cuando el circuito "
               "estándar no encaja.",
        "enlaces": [
            ("index.html", "p-doce-fases-primera-visita", "Las doce fases, una por una",
             ["f%02d" % n for n in range(1, 13)]),
            ("index.html", "p-115-120-minutos-escala", "Los 115 a 120 minutos, a escala"),
            ("index.html", "p-quien-tiene-paciente-cada-momento",
             "Quién tiene al paciente en cada momento"),
            ("index.html", "p-cuando-circuito-estandar-no-encaja",
             "Cuando el circuito estándar no encaja"),
            ("manual.html", "m-recepcion-sala-vip-tour", "Recepción, Sala VIP y tour"),
        ],
    },
    {
        "id": "a-lo-que-hacemos",
        "n": "06",
        "rotulo": "Lo que hacemos",
        "pregunta": "¿Qué recorre un paciente desde la primera llamada hasta el mantenimiento?",
        "que": "Catorce fases. La primera visita es el principio; después vienen el "
               "circuito de producción y el seguimiento a largo plazo, que es donde un "
               "centro se juega de verdad la reputación.",
        "enlaces": [
            ("manual.html", "m-recorrido-paciente", "El recorrido del paciente · catorce fases",
             ["m%02d" % n for n in range(1, 15)]),
            ("index.html", "p-donde-continua-recorrido", "Dónde continúa el recorrido"),
            ("marketing.html", "k-doce-estados", "Los doce estados del paciente"),
        ],
    },
    {
        "id": "a-con-que",
        "n": "07",
        "rotulo": "Con qué lo hacemos",
        "pregunta": "¿Qué tecnología se usa, y cómo entra una función nueva sin romper nada?",
        "que": "Las funciones de vanguardia por puesto, la vía por la que se incorpora "
               "una técnica nueva y los 322 puntos con los que se verifica que el centro "
               "está como tiene que estar.",
        "enlaces": [
            ("manual.html", "m-funciones-vanguardia-perfil", "Funciones de vanguardia por perfil"),
            ("manual.html", "m-como-entra-funcion-nueva-sin-romper",
             "Cómo entra una función nueva sin romper lo que funciona"),
            ("otros.html", "o-innovacion-aplicada-protocolo-18-fichas-implantacion",
             "Innovación aplicada · 18 fichas de implantación"),
            ("otros.html", "o-protocolo-maestro-verificacion-322-puntos-control",
             "Verificación del centro · 322 puntos"),
            ("index.html", "p-pruebas-diagnosticas-avanzadas-documentacion-fotogra",
             "Pruebas diagnósticas avanzadas"),
        ],
    },
    {
        "id": "a-como-llega",
        "n": "08",
        "rotulo": "Cómo llega el paciente",
        "pregunta": "¿Qué hace el centro para que alguien decida venir, y qué no hará nunca?",
        "que": "Setenta y seis acciones sobre los doce estados de la relación del paciente "
               "con su propia boca, con dueño y con techo de gasto. Treinta y dos de ellas "
               "no cuestan dinero.",
        "enlaces": [
            ("marketing.html", "k-doce-estados-seis-personas-siete-minutos",
             "Doce estados, seis personas y siete minutos"),
            ("marketing.html", "k-setenta-seis-acciones", "Las setenta y seis acciones"),
            ("marketing.html", "k-seis-ria", "Los seis de la ría"),
            ("marketing.html", "k-nadie-esta-haciendo-esta-ciudad",
             "Lo que nadie está haciendo en esta ciudad"),
            ("otros.html", "o-plan-director-marca-captacion", "Plan Director de marca y captación"),
        ],
    },
    {
        "id": "a-los-numeros",
        "n": "09",
        "rotulo": "Los números",
        "pregunta": "¿Con qué se mide todo esto, y qué sabemos de verdad hoy?",
        "que": "Diez indicadores y cinco números que aún no se tienen. Mientras no existan, "
               "cualquier objetivo comercial es una opinión: por eso la hoja de captura no "
               "es un anexo, es el instrumento.",
        "enlaces": [
            ("instrumentos/captura.html", "c-tres-reglas-ninguna-mas", "Tres reglas y ninguna más"),
            ("instrumentos/captura.html", "c-sin-ellos-cualquier-objetivo-comercial-opinion",
             "Sin ellos, cualquier objetivo comercial es una opinión"),
            ("memoria.html", "t-cinco-numeros-aun-no-tenemos", "Los cinco números que aún no tenemos"),
            ("manual.html", "m-indicadores-perfil", "Indicadores por perfil"),
            ("index.html", "p-como-mide-si-protocolo-funciona", "Cómo se mide si el protocolo funciona"),
            ("marketing.html", "k-ocho-medidas-plan", "Las ocho medidas del plan"),
        ],
    },
    {
        "id": "a-quien-decide",
        "n": "10",
        "rotulo": "Quién decide",
        "pregunta": "¿Qué se somete a la Junta, con qué criterio y en qué horizonte?",
        "que": "Lo que una web de clínica no enseña y un sistema de gobierno sí: las "
               "quince decisiones abiertas, los tres horizontes con criterios distintos y "
               "de dónde sale el dinero.",
        "enlaces": [
            ("memoria.html", "t-dos-minutos", "Dos minutos: de qué va todo esto"),
            ("memoria.html", "t-tres-horizontes-tres-criterios-decision-distintos",
             "Tres horizontes, tres criterios de decisión"),
            ("memoria.html", "t-donde-sale-dinero-destruye", "De dónde sale el dinero y qué lo destruye"),
            ("otros.html", "o-decisiones-gerencia-verificaciones-externas",
             "Decisiones de Gerencia y verificaciones externas"),
            ("otros.html", "o-auditoria-integral-clinica-adquirida",
             "Auditoría integral de la clínica adquirida"),
        ],
    },
    {
        "id": "a-puesta-marcha",
        "n": "11",
        "rotulo": "La puesta en marcha",
        "pregunta": "¿Qué pasa el día uno, y qué tiene que estar hecho a los cien días?",
        "que": "El sistema entero se pone en pie por orden: el primer día, los primeros "
               "treinta y el plan director de los cien, con lo que le toca a cada puesto.",
        "enlaces": [
            ("manual.html", "m-puesta-marcha", "Puesta en marcha del centro"),
            ("otros.html", "o-cuaderno-campo-dia-1", "Cuaderno de campo · Día 1"),
            ("otros.html", "o-dosier-ejecucion-primeros-30-dias", "Dosier de ejecución · los 30 días"),
            ("otros.html", "o-programa-integracion-transformacion-plan-director-10",
             "Plan Director de los primeros 100 días"),
            ("otros.html", "o-manual-puesta-marcha-operativa-perfil",
             "Manual de puesta en marcha por perfil"),
        ],
    },
]


def cuantas():
    return len(AREAS)


def enlaces():
    """Todos los destinos, para poder comprobar que existen."""
    for a in AREAS:
        for e in a["enlaces"]:
            yield a["id"], e[0], e[1], e[2]
            for extra in (e[3] if len(e) > 3 else []):
                yield a["id"], e[0], extra, e[2]


# De qué documento viene cada pieza. La literatura no se copia dos veces: se
# lee aquí y se dice de dónde sale, porque el documento sigue siendo el que
# manda y el que se cita en acta.
ORIGEN = {
    "memoria.html": "Plan de Dirección",
    "manual.html": "Manual Maestro de Operaciones",
    "index.html": "Protocolo de Primera Visita",
    "marketing.html": "Plan Maestro de Marketing",
    "otros.html": "Otros documentos del sistema",
    "instrumentos/captura.html": "Los números del centro",
    "protocolos.html": "Protocolos por puesto",
}
