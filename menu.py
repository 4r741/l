#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El menú de secciones: un solo modelo para los seis documentos.

Hasta ahora cada documento llevaba su índice escrito a mano en la cabecera, y
se notaba: la memoria numeraba «00, 0.1, 01», el marketing decía «apartado 3»,
otros documentos usaba «1 ·» y el manual solo romanos. Cuatro cuentas distintas
en un sistema que se presenta como uno. Peor aún, las treinta y cuatro entradas
de la memoria vivían en una fila que se desplazaba a lo ancho: en un ratón sin
rueda horizontal —o en un móvil que no adivina que aquello se arrastra— la
mitad del documento no existía.

Aquí está el modelo entero y el que lo dibuja. Una cuenta sola: las partes son
encabezados de grupo, los apartados llevan su número de dos cifras y los anexos
van con letra. Y el menú deja de ser una fila: es un panel que se abre y enseña
todo de golpe, en columnas, sin nada que arrastrar.

    grupos = [(rótulo del grupo, ancla del grupo o None, [(ancla, nº, rótulo)])]

El número puede ir vacío: hay entradas que no son apartados —la portada, el
manifiesto, el censo— y forzarles un número era justamente el problema.
"""

import posixpath

# --------------------------------------------------------------------------
#  El modelo
# --------------------------------------------------------------------------

MENUS = {
    # La portada también lleva menú. Antes era el único documento sin barra
    # útil: se entraba y no había forma de saltar a ninguna parte, ni de esta
    # página ni del sistema, más que bajando seis pantallas.
    "inicio.html": {
        "rotulo": "Portada del sistema",
        "aria": "Secciones de la portada",
        "grupos": [
            ("Esta página", None, [
                ("por-areas", "", "El centro, contado por áreas"),
                ("documentos", "", "Los ocho documentos del sistema"),
                ("indice", "", "Buscar en todo el sistema"),
                ("cifras", "", "Sobre la naturaleza de las cifras"),
            ]),
        ],
    },

    # La vista operativa: el protocolo del centro desde cada puesto. No es un
    # documento más, es una entrada distinta a los que ya hay.
    "protocolos.html": {
        "rotulo": "Protocolos por puesto",
        "aria": "Secciones de Protocolos por puesto",
        "grupos": [
            ("Esta página", None, [
                ("portada", "", "Para qué sirve esta vista"),
                ("puestos", "", "Los seis puestos: elija el suyo"),
                ("comun", "", "Lo que se cumple en todos los puestos"),
            ]),
        ],
    },

    "memoria.html": {
        "rotulo": "Plan de Dirección",
        "aria": "Secciones del Plan de Dirección",
        "grupos": [
            ("Apertura", None, [
                ("manifiesto", "", "El manifiesto: la regla que ordena todo"),
                ("control", "00", "Control del documento y cómo se cita"),
                ("censo", "", "Censo de los 17 documentos del sistema"),
                ("resumen", "01", "Resumen ejecutivo en dos minutos"),
            ]),
            ("Parte I · La posición", "parte-1", [
                ("tesis", "02", "Por qué este centro y no otro"),
                ("mapa", "03", "Mapa competitivo de Vigo y el hueco libre"),
                ("foso", "04", "El foso: lo que un competidor no puede comprar"),
            ]),
            ("Parte II · El sistema", "parte-2", [
                ("sistema", "05", "El sistema operativo que se ha construido"),
                ("innovacion", "06", "Innovación: tres horizontes, tres criterios"),
            ]),
            ("Parte III · La economía", "parte-3", [
                ("linea-base", "07", "Los cinco números que aún no tenemos"),
                ("unidad", "08", "Economía por paciente: qué gobierna el resultado"),
                ("activo", "09", "Cuánto vale el centro, y por qué"),
                ("escalado", "10", "Escalado: de un centro a una red"),
            ]),
            ("Parte IV · El riesgo", "parte-4", [
                ("riesgos", "11", "Registro de riesgos, con dueño y fecha"),
                ("premortem", "12", "Pre-mortem: es 2029 y ha fracasado"),
                ("mando", "13", "Cuadro de mando: con qué se dirige cada mes"),
            ]),
            ("Parte V · La decisión", "parte-5", [
                ("palancas", "14", "Palancas: por dónde se crece y en qué orden"),
                ("capital", "15", "Asignación de capital: en qué se gasta antes"),
                ("ruta", "16", "Hoja de ruta y sus tres puertas de paso"),
                ("decisiones", "17", "Las quince decisiones que se someten a la Junta"),
                ("supuestos", "18", "Supuestos: sobre qué se ha razonado"),
                ("trazabilidad", "19", "Trazabilidad: dónde aterriza cada acuerdo"),
            ]),
            ("Parte VI · La cifra", "parte-6", [
                ("puente", "20", "El puente: de 720 k€ a 1,2 M€, bloque a bloque"),
                ("cartera", "21", "La cartera de nueve campañas"),
                ("calendario", "22", "Calendario y capacidad del año"),
                ("cierto", "23", "Las cinco condiciones que tienen que ser ciertas"),
            ]),
            ("Anexos", None, [
                ("acuerdos", "A", "Cuadernillo: quince hojas de acta"),
                ("campanas", "B", "Nueve fichas de campaña, para poner en marcha"),
            ]),
        ],
    },

    "marketing.html": {
        "rotulo": "Plan Maestro de Marketing",
        "aria": "Secciones del Plan de Marketing",
        "grupos": [
            ("Apertura", None, [
                ("portada", "", "Portada"),
                ("control", "00", "Ficha de control del documento"),
            ]),
            ("Parte I · La doctrina", "parte-1", [
                ("doctrina", "01", "Por qué este plan no es un plan al uso"),
                ("regla", "02", "La regla de la ficha: qué gana el paciente"),
                ("nunca", "03", "Las ocho cosas que no haremos nunca"),
                ("legal", "04", "El marco legal de la publicidad sanitaria"),
            ]),
            ("Parte II · El paciente", "parte-2", [
                ("estados", "05", "Los doce estados del paciente"),
                ("arquetipos", "06", "Los seis pacientes de la ría"),
                ("momentos", "07", "Los siete momentos de verdad"),
                ("asimetria", "08", "La asimetría: lo que el paciente no sabe"),
            ]),
            ("Parte III · El catálogo", "parte-3", [
                ("catalogo", "09", "Las 76 acciones, con dueño y coste"),
            ]),
            ("Parte IV · Las diez piezas", "parte-4", [
                ("piezas", "10", "Las diez piezas que nadie hace en Vigo"),
            ]),
            ("Parte V · El territorio", "parte-5", [
                ("digital", "11", "La presencia digital, y para qué sirve"),
                ("ria", "12", "El mapa de la ría: dónde está el paciente"),
                ("mar", "13", "La Campaña de Mar, verano a verano"),
            ]),
            ("Parte VI · La prioridad", "parte-6", [
                ("economia", "14", "Qué aporta cada grupo de acciones"),
                ("prioridad", "15", "Qué va primero, y por qué"),
                ("presupuesto", "16", "Presupuesto y techo de gasto"),
            ]),
            ("Parte VII · El gobierno", "parte-7", [
                ("indicadores", "17", "Las ocho medidas del plan"),
                ("calendario", "18", "El calendario del ejercicio"),
                ("parada", "19", "Reglas de parada: cuándo se corta"),
            ]),
            ("Parte VIII · El programa", "parte-8", [
                ("gtc", "20", "Giraldo Te Cuida: el programa de acompañamiento"),
            ]),
            ("Anexos", None, [
                ("anexo-legal", "A", "Semáforo legal, acción por acción"),
                ("anexo-cartera", "B", "Correspondencia con la cartera de campañas"),
                ("anexo-trimestre", "C", "Lo que se activa este trimestre"),
            ]),
        ],
    },

    "manual.html": {
        "rotulo": "Manual Maestro",
        "aria": "Secciones del Manual Maestro",
        "grupos": [
            ("Apertura", None, [
                ("presentacion", "", "Un documento, tres usos"),
                ("indice", "", "Índice: dónde está cada cosa"),
                ("vanguardia", "", "Marco de vanguardia y los cinco pilares"),
            ]),
            ("Las ocho partes", None, [
                ("p1", "I", "Fundamentos y principios rectores"),
                ("estandares", "", "Estándares transversales del centro"),
                ("p2", "II", "Las catorce fases del recorrido"),
                ("p3", "III", "Matriz RACI: quién hace qué en cada fase"),
                ("p4", "IV", "Manuales de los seis puestos"),
                ("p5", "V", "Funciones de vanguardia por perfil"),
                ("p6", "VI", "Indicadores e interdependencias"),
                ("p7", "VII", "Plan de incentivos y retribución variable"),
                ("p8", "VIII", "Puesta en marcha del centro"),
            ]),
            ("Cierre", None, [
                ("anexos", "", "Anexos: plantillas y checklists"),
                ("otros", "", "Otros documentos del sistema"),
                ("notas", "", "Puntos que siguen abiertos"),
            ]),
        ],
    },

    "index.html": {
        "rotulo": "Protocolo de Primera Visita",
        "aria": "Secciones del Protocolo",
        "grupos": [
            ("Apertura", None, [
                ("fundamentos", "", "Los cinco principios de la visita"),
                ("mapa", "", "La visita entera, minuto a minuto"),
                ("flujo", "", "Quién tiene al paciente en cada momento"),
            ]),
            ("Las doce fases de la visita", None, [
                ("f01", "01", "Preparación previa y primera llamada"),
                ("f02", "02", "Acogida y recorrido por la tecnología"),
                ("f03", "03", "Alta, RGPD y protección de datos"),
                ("f04", "04", "Historia clínica y consentimiento"),
                ("f05", "05", "Pruebas diagnósticas y fotografía"),
                ("f06", "06", "Briefing entre Doctor y Director"),
                ("f07", "07", "Expectativas y exploración clínica"),
                ("f08", "08", "Informe de Análisis Clínico (IAC)"),
                ("f09", "09", "Presentación del diagnóstico en 3D"),
                ("f10", "10", "Propuesta económica y cierre"),
                ("f11", "11", "Cierre administrativo y digitalización"),
                ("f12", "12", "Despedida y seguimiento estratégico"),
            ]),
            ("Cierre", None, [
                ("estandares", "", "Estándares comunes a las doce fases"),
                ("casos", "", "Casos especiales: cuando no encaja"),
                ("continua", "", "Fases 13 y 14: producción y mantenimiento"),
                ("trazabilidad", "", "Qué queda registrado y quién responde"),
                ("indicadores", "", "Cómo se mide si el protocolo funciona"),
                ("formacion", "", "Formación y certificación por rol"),
                ("anexos", "", "Anexos: guiones y preguntas frecuentes"),
            ]),
        ],
    },

    "otros.html": {
        "rotulo": "Otros documentos",
        "aria": "Secciones de Otros documentos",
        "grupos": [
            ("Apertura", None, [
                ("presentacion", "", "Qué es cada cosa y cuándo se abre"),
                ("otros-mapa", "", "El sistema en cuatro niveles"),
            ]),
            ("Los catorce documentos", None, [
                ("otros-compendio", "01", "Compendio Maestro del sistema de gestión"),
                ("otros-verificacion", "02", "Verificación del centro · 322 puntos"),
                ("otros-auditoria", "03", "Auditoría integral de la clínica adquirida"),
                ("otros-decisiones", "04", "Decisiones de Gerencia y verificaciones"),
                ("otros-100dias", "05", "Plan Director de los primeros 100 días"),
                ("otros-30dias", "06", "Dosier de ejecución de los 30 días"),
                ("otros-perfiles", "07", "Protocolos operativos por perfil"),
                ("otros-innovacion", "08", "Innovación aplicada · 18 fichas"),
                ("otros-marca", "09", "Plan Director de marca y captación"),
                ("otros-cuaderno", "10", "Cuaderno de campo del día 1"),
                ("otros-transicion-perfiles", "11", "Manual de puesta en marcha por perfil"),
                ("otros-continuidad", "12", "Continuidad legal, financiera y de sistemas"),
                ("otros-posicionamiento", "13", "«No medias sonrisas» · posicionamiento"),
                ("otros-gtc", "14", "GTC · vive en el Plan de Marketing"),
            ]),
            ("Cierre", None, [
                ("otros-cierre", "", "Cómo encajan los catorce documentos"),
            ]),
        ],
    },

    "instrumentos/captura.html": {
        "rotulo": "Los números del centro",
        "aria": "Secciones de la hoja de los números del centro",
        "grupos": [
            ("La hoja de cada mes", None, [
                ("instrucciones", "", "Tres reglas y ninguna más"),
                ("definiciones", "", "Qué se cuenta y cómo se cuenta"),
                ("captura", "", "Una hoja por cada mes del año"),
                ("anual", "", "Los doce meses en una rejilla"),
                ("cinco", "", "Los cinco números que resumen el año"),
            ]),
        ],
    },
}


# Los ocho documentos del sistema, para que el panel lleve también la salida
# hacia los demás. En un teléfono los enlaces entre documentos ocupaban cuatro
# filas de la barra —cuatrocientos treinta píxeles antes de la primera línea de
# texto—; aquí caben en cuatro renglones y la barra vuelve a ser una barra.
DOCS = [
    ("inicio.html", "Inicio"),
    ("centro.html", "El centro, por áreas"),
    ("memoria.html", "Dirección"),
    ("deck.html", "Presentación de Junta"),
    ("protocolos.html", "Protocolos por puesto"),
    ("index.html", "Primera Visita"),
    ("manual.html", "Operaciones"),
    ("marketing.html", "Marketing"),
    ("otros.html", "Otros documentos"),
    ("instrumentos/captura.html", "Los números del centro"),
]


# Dos de las entradas de arriba no son documentos: son puertas. La portada
# reparte y el sitio por áreas trae literatura de los ocho, pero ninguno añade
# uno nuevo. Quien cuente documentos tiene que descontarlos.
NO_SON_DOCUMENTOS = {"inicio.html", "centro.html"}


def _hacia(desde, hasta):
    """La ruta relativa entre dos documentos del sistema."""
    return posixpath.relpath(hasta, posixpath.dirname(desde) or ".")


def _otros(archivo):
    filas = "".join('<a href="%s"><b></b><span>%s</span></a>' % (_hacia(archivo, f), r)
                    for f, r in DOCS if f != archivo)
    return ('<div class="menu__g menu__g--docs">'
            '<p class="menu__gt"><span>El sistema documental</span></p>%s</div>' % filas)


# --------------------------------------------------------------------------
#  El dibujo
# --------------------------------------------------------------------------

def _entrada(ancla, numero, rotulo):
    """Una línea del panel.

    El ancla va pegada a `<a href=` y sin más atributos a propósito: el índice
    de la portada y el archivo único leen el menú con `<a href="#x">`, y ese
    contrato vale más que la comodidad de poner aquí una clase.
    """
    return ('<a href="#%s"><b>%s</b><span>%s</span></a>'
            % (ancla, numero, rotulo))


def _grupo(rotulo, ancla, entradas):
    cab = ('<p class="menu__gt"><a href="#%s">%s</a></p>' % (ancla, rotulo)
           if ancla else '<p class="menu__gt"><span>%s</span></p>' % rotulo)
    return ('<div class="menu__g">%s%s</div>'
            % (cab, "".join(_entrada(*e) for e in entradas)))


def dibuja(archivo, sangria="      "):
    """El `<nav>` completo de un documento, listo para pegar en la cabecera."""
    m = MENUS[archivo]
    grupos = "".join(_grupo(*g) for g in m["grupos"]) + _otros(archivo)
    n = sum(len(g[2]) + (1 if g[1] else 0) for g in m["grupos"])
    partes = [
        '<nav class="strip" id="strip" aria-label="%s">' % m["aria"],
        '  <details class="menu">',
        '    <summary class="menu__b">',
        '      <span class="menu__rejilla" aria-hidden="true"></span>',
        '      <span class="menu__b__txt">Índice</span>',
        '      <span class="menu__b__n">%d</span>' % n,
        '    </summary>',
        '    <div class="menu__panel">',
        '      <div class="menu__cols">%s</div>' % grupos,
        '    </div>',
        '  </details>',
        '  <p class="menu__aqui" data-aqui>%s</p>' % m["rotulo"],
        '</nav>',
    ]
    return ("\n" + sangria).join(partes)


def cuantas(archivo):
    """Cuántos destinos ofrece el menú de un documento."""
    return sum(len(g[2]) + (1 if g[1] else 0) for g in MENUS[archivo]["grupos"])
