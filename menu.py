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
    "memoria.html": {
        "rotulo": "Plan de Dirección",
        "aria": "Secciones del Plan de Dirección",
        "grupos": [
            ("Apertura", None, [
                ("manifiesto", "", "La regla que ordena todo"),
                ("control", "00", "Control del documento"),
                ("censo", "", "Censo documental"),
                ("resumen", "01", "Resumen ejecutivo"),
            ]),
            ("Parte I · La posición", "parte-1", [
                ("tesis", "02", "Por qué este centro"),
                ("mapa", "03", "Mapa competitivo de Vigo"),
                ("foso", "04", "Lo que no se puede copiar"),
            ]),
            ("Parte II · El sistema", "parte-2", [
                ("sistema", "05", "El sistema operativo"),
                ("innovacion", "06", "Innovación en tres horizontes"),
            ]),
            ("Parte III · La economía", "parte-3", [
                ("linea-base", "07", "Los cinco números que faltan"),
                ("unidad", "08", "Economía por paciente"),
                ("activo", "09", "Cuánto vale el centro"),
                ("escalado", "10", "De un centro a una red"),
            ]),
            ("Parte IV · El riesgo", "parte-4", [
                ("riesgos", "11", "Registro de riesgos"),
                ("premortem", "12", "Pre-mortem a 2029"),
                ("mando", "13", "Cuadro de mando mensual"),
            ]),
            ("Parte V · La decisión", "parte-5", [
                ("palancas", "14", "Por dónde se crece"),
                ("capital", "15", "En qué se gasta primero"),
                ("ruta", "16", "Hoja de ruta y sus puertas"),
                ("decisiones", "17", "Las quince decisiones"),
                ("supuestos", "18", "Sobre qué se ha razonado"),
                ("trazabilidad", "19", "Dónde aterriza cada acuerdo"),
            ]),
            ("Parte VI · La cifra", "parte-6", [
                ("puente", "20", "De 720 k€ a 1,2 M€"),
                ("cartera", "21", "Las nueve campañas"),
                ("calendario", "22", "Calendario y capacidad"),
                ("cierto", "23", "Las cinco condiciones"),
            ]),
            ("Anexos", None, [
                ("acuerdos", "A", "Quince hojas de acta"),
                ("campanas", "B", "Nueve fichas de campaña"),
            ]),
        ],
    },

    "marketing.html": {
        "rotulo": "Plan Maestro de Marketing",
        "aria": "Secciones del Plan de Marketing",
        "grupos": [
            ("Apertura", None, [
                ("portada", "", "Portada"),
                ("control", "00", "Ficha de control"),
            ]),
            ("Parte I · La doctrina", "parte-1", [
                ("doctrina", "01", "Por qué este plan es distinto"),
                ("regla", "02", "La regla de la ficha"),
                ("nunca", "03", "Las ocho que no haremos"),
                ("legal", "04", "El marco legal sanitario"),
            ]),
            ("Parte II · El paciente", "parte-2", [
                ("estados", "05", "Los doce estados"),
                ("arquetipos", "06", "Los seis de la ría"),
                ("momentos", "07", "Los siete momentos de verdad"),
                ("asimetria", "08", "Lo que el paciente no sabe"),
            ]),
            ("Parte III · El catálogo", "parte-3", [
                ("catalogo", "09", "Las 76 acciones, con dueño"),
            ]),
            ("Parte IV · Las diez piezas", "parte-4", [
                ("piezas", "10", "Las diez piezas, una a una"),
            ]),
            ("Parte V · El territorio", "parte-5", [
                ("digital", "11", "La presencia digital"),
                ("ria", "12", "El mapa de la ría"),
                ("mar", "13", "La Campaña de Mar"),
            ]),
            ("Parte VI · La prioridad", "parte-6", [
                ("economia", "14", "Qué aporta cada grupo"),
                ("prioridad", "15", "Qué va primero"),
                ("presupuesto", "16", "Presupuesto y techo"),
            ]),
            ("Parte VII · El gobierno", "parte-7", [
                ("indicadores", "17", "Las ocho medidas del plan"),
                ("calendario", "18", "El calendario del ejercicio"),
                ("parada", "19", "Reglas de parada"),
            ]),
            ("Anexos", None, [
                ("anexo-legal", "A", "Semáforo legal por acción"),
                ("anexo-cartera", "B", "Correspondencia con la cartera"),
                ("anexo-trimestre", "C", "Activo este trimestre"),
            ]),
        ],
    },

    "manual.html": {
        "rotulo": "Manual Maestro",
        "aria": "Secciones del Manual Maestro",
        "grupos": [
            ("Apertura", None, [
                ("presentacion", "", "Un documento, tres usos"),
                ("indice", "", "Dónde está cada cosa"),
                ("vanguardia", "", "Marco de vanguardia"),
            ]),
            ("Las ocho partes", None, [
                ("p1", "I", "Fundamentos y principios"),
                ("estandares", "", "Estándares transversales"),
                ("p2", "II", "Las catorce fases"),
                ("p3", "III", "Matriz RACI"),
                ("p4", "IV", "Manuales por puesto"),
                ("p5", "V", "Funciones de vanguardia"),
                ("p6", "VI", "Indicadores e interdependencias"),
                ("p7", "VII", "Plan de incentivos"),
                ("p8", "VIII", "Puesta en marcha"),
            ]),
            ("Cierre", None, [
                ("anexos", "", "Anexos"),
                ("otros", "", "Otros documentos del sistema"),
                ("notas", "", "Lo que sigue abierto"),
            ]),
        ],
    },

    "index.html": {
        "rotulo": "Protocolo de Primera Visita",
        "aria": "Secciones del Protocolo",
        "grupos": [
            ("Apertura", None, [
                ("fundamentos", "", "Los cinco principios"),
                ("mapa", "", "La visita, minuto a minuto"),
                ("flujo", "", "Quién tiene al paciente"),
            ]),
            ("Las doce fases de la visita", None, [
                ("f01", "01", "Preparación previa"),
                ("f02", "02", "Acogida y recorrido"),
                ("f03", "03", "Alta y protección de datos"),
                ("f04", "04", "Historia clínica"),
                ("f05", "05", "Pruebas diagnósticas"),
                ("f06", "06", "Briefing Doctor–Director"),
                ("f07", "07", "Expectativas y exploración"),
                ("f08", "08", "Informe de Análisis Clínico"),
                ("f09", "09", "Diagnóstico 3D y plan"),
                ("f10", "10", "Propuesta económica y cierre"),
                ("f11", "11", "Cierre administrativo"),
                ("f12", "12", "Despedida y seguimiento"),
            ]),
            ("Cierre", None, [
                ("estandares", "", "Estándares de las doce fases"),
                ("casos", "", "Cuando no encaja el circuito"),
                ("continua", "", "Fases 13 y 14: qué sigue"),
                ("trazabilidad", "", "Qué queda registrado"),
                ("indicadores", "", "Cómo se mide si funciona"),
                ("formacion", "", "Formación y certificación"),
                ("anexos", "", "Anexos y material de apoyo"),
            ]),
        ],
    },

    "otros.html": {
        "rotulo": "Otros documentos",
        "aria": "Secciones de Otros documentos",
        "grupos": [
            ("Apertura", None, [
                ("presentacion", "", "Qué es cada cosa"),
                ("otros-mapa", "", "El sistema en cuatro niveles"),
            ]),
            ("Los catorce documentos", None, [
                ("otros-compendio", "01", "Compendio Maestro"),
                ("otros-verificacion", "02", "Verificación · 322 puntos"),
                ("otros-auditoria", "03", "Auditoría de la clínica"),
                ("otros-decisiones", "04", "Decisiones de Gerencia"),
                ("otros-100dias", "05", "Plan Director de 100 días"),
                ("otros-30dias", "06", "Los primeros 30 días"),
                ("otros-perfiles", "07", "Protocolos por perfil"),
                ("otros-innovacion", "08", "Innovación · 18 fichas"),
                ("otros-marca", "09", "Marca y captación"),
                ("otros-cuaderno", "10", "Cuaderno de campo · día 1"),
                ("otros-transicion-perfiles", "11", "Puesta en marcha por perfil"),
                ("otros-continuidad", "12", "Continuidad legal y financiera"),
                ("otros-posicionamiento", "13", "No medias sonrisas"),
                ("otros-gtc", "14", "GTC · Giraldo Te Cuida"),
            ]),
            ("Cierre", None, [
                ("otros-cierre", "", "Cómo encajan los catorce"),
            ]),
        ],
    },

    "instrumentos/captura.html": {
        "rotulo": "Línea base",
        "aria": "Secciones de la hoja de línea base",
        "grupos": [
            ("La hoja de línea base", None, [
                ("instrucciones", "", "Tres reglas y ninguna más"),
                ("definiciones", "", "Qué se cuenta y cómo"),
                ("captura", "", "Una hoja por mes"),
                ("anual", "", "Los doce meses de un vistazo"),
                ("cinco", "", "Los cinco números"),
            ]),
        ],
    },
}


# Los ocho documentos del sistema, para que el panel lleve también la salida
# hacia los demás. En un teléfono los enlaces entre documentos ocupaban cuatro
# filas de la barra —cuatrocientos treinta píxeles antes de la primera línea de
# texto—; aquí caben en cuatro renglones y la barra vuelve a ser una barra.
DOCS = [
    ("inicio.html", "Portada del sistema"),
    ("memoria.html", "Plan de Dirección"),
    ("deck.html", "Presentación de Junta"),
    ("manual.html", "Manual Maestro"),
    ("index.html", "Protocolo de Primera Visita"),
    ("otros.html", "Otros documentos"),
    ("marketing.html", "Plan de Marketing"),
    ("instrumentos/captura.html", "Línea base"),
]


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
