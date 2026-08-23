#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anexo B: una ficha por campaña, con la cuenta que produce su cifra.
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"
import importlib.util

_spec = importlib.util.spec_from_file_location("modelo", RAIZ / "modelo-campanas.py")
_modelo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_modelo)
_D = _modelo.calcula()
MODELO = {f["cod"]: f for f in _D["campanas"]}
VALOR_BASE = _D["capacidad"]["valor_base"]


def _mil(v):
    return "{:,}".format(int(round(v))).replace(",", ".").replace("-", "\u2212")


def _derivacion(cod):
    """La operación que produce la cifra de esta campaña, escrita en una línea."""
    f = MODELO[cod]
    if f["tipo"] == "agenda":
        return ("%s visitas × (%.0f %% × %s € − %s €) = <strong>%s k€</strong>"
                % (_mil(f["pv"]), f["conv"] * 100, _mil(f["ticket"]), _mil(VALOR_BASE),
                   _mil(f["aporte"] / 1000)))
    partes = "<br>".join("<b>%s · %s k€</b> &nbsp;%s" % (nombre, _mil(valor / 1000), como)
                         for nombre, valor, como in f["partes"])
    return "%s<br><strong>Total: %s k€</strong>" % (partes, _mil(f["aporte"] / 1000))


SALIDA = FUENTES / "tesis-anexo-b-campanas.html"

# código, nombre, promesa, a quién, dónde se encuentra, qué se le ofrece,
# guion de apertura, canal y ritmo, aporte, coste, arranque, dueño,
# indicador, umbral de parada, depende de
C = [
 ("C1", "Giraldo Te Cuida", "Su tratamiento no termina cuando se coloca: empieza otra cosa",
  "Todo paciente que termina un tratamiento, sin excepción ni criterio comercial.",
  "No hay que encontrarlo: ya está sentado delante. La campaña vive dentro del cierre de la Fase 12.",
  "El programa de cuidado anual: revisiones, mantenimiento y prioridad de agenda, por una cuota.",
  "Antes de que se vaya, quiero explicarle cómo vamos a cuidar esto a partir de ahora. No es una venta: es cómo trabajamos.",
  "Punto de verificación obligatorio del cierre. Permanente, los doce meses.",
  88, "Bajo · contrato, cartelería y formación del cierre", "Permanente", "Dirección",
  "Indicador 9 · ofrecimiento por encima del 90 %",
  "Si el ofrecimiento baja del 90 % dos meses seguidos, se para todo lo demás y se corrige esto.",
  "D5 · catálogo y validación jurídica · D14 · obligatoriedad en el cierre"),

 ("C2", "«Su caso no es imposible»", "Le dijeron que no se podía. Vamos a mirarlo otra vez",
  "Atrofia severa, rehabilitación completa, fracasos previos, casos rechazados en otros centros.",
  "No busca precio: busca a alguien que se atreva. Llega por contenido, por prescripción y por segunda opinión.",
  "Un diagnóstico completo con CBCT y una respuesta honesta, incluida la de que no se puede.",
  "Tráigame lo que le dijeron. Vamos a ver el caso entero, no solo la zona que le duele, y le voy a decir la verdad.",
  "Casos propios documentados, colaboración con prescriptores, presencia en búsqueda. Arranque fuerte en enero y septiembre.",
  118, "Medio · tiempo clínico de diagnóstico y producción de contenido", "Enero y septiembre", "Dirección clínica",
  "Ticket medio de los casos aceptados y número de casos complejos al mes",
  "Si a los 60 días no hay al menos tres casos complejos aceptados, se revisa el mensaje antes de gastar más.",
  "Nada externo: casuística y CBCT ya están"),

 ("C3", "«Volvemos a llamarle»", "Hace tiempo que no le vemos y queremos saber cómo está",
  "Pacientes del propio centro sin visita en más de dieciocho meses.",
  "Están en la base de datos. La campaña más barata que existe y la primera que todo centro abandona.",
  "Una revisión sin coste y, si procede, retomar el tratamiento donde se dejó.",
  "Le llamo del centro. Veo que la última vez que vino fue hace dos años y quedó pendiente terminar. ¿Cómo está de eso?",
  "Teléfono, uno a uno, con guion escrito. Nunca correo masivo. Veinte llamadas al día durante ocho semanas.",
  104, "Muy bajo · solo tiempo de Recepción", "Febrero", "Recepción, con seguimiento diario de Gerencia",
  "Llamadas hechas, citas conseguidas y tratamientos retomados",
  "Si de 200 llamadas no salen 20 citas, el problema es el guion, no la cartera: se reescribe.",
  "Inventario de la cartera dormida, que nadie ha hecho todavía"),

 ("C4", "Red de derivación", "Le devolvemos a su paciente, y con el caso resuelto",
  "Clínicas generalistas de Vigo y la ría que no hacen implantología compleja.",
  "No es una campaña de pacientes: es de colegas. Se hace en persona, una a una.",
  "Resolver el caso que ellos no hacen y devolver al paciente para todo lo demás, por escrito.",
  "No queremos su paciente. Queremos el caso que usted no va a hacer, y devolvérselo terminado con el informe.",
  "Visita profesional del director clínico. Dos clínicas por semana. Acuerdo escrito de devolución.",
  96, "Medio · tiempo de Dirección y material profesional", "Junio", "Dirección clínica",
  "Clínicas con acuerdo firmado y pacientes derivados al trimestre",
  "Si tras veinte visitas no hay cinco acuerdos, el problema es la propuesta, no el mercado.",
  "Protocolo de derivación y compromiso de devolución por escrito"),

 ("C5", "«Sin miedo»", "Lleva años sin ir al dentista. No le vamos a reñir",
  "Ansiedad dental severa: personas que llevan años evitando el sillón.",
  "Es el segmento que menos se comunica y más lo agradece. Llega por mensaje explícito, casi nunca preguntando.",
  "Una primera visita sin instrumental, un circuito propio y sedación consciente si hace falta.",
  "La primera vez no le vamos a tocar nada. Solo vamos a hablar y a mirar. Usted dice cuándo paramos.",
  "Mensaje explícito en todos los canales, circuito diferenciado en el centro. Arranque en abril.",
  78, "Medio · circuito, formación y habilitación", "Abril", "Dirección clínica",
  "Pacientes atendidos del segmento y tasa de abandono entre primera visita y tratamiento",
  "Si la habilitación de sedación no está resuelta, la campaña no arranca: no se promete lo que no se puede dar.",
  "D6 · autorización de la línea de sedación consciente"),

 ("C6", "«La revisión que evita la cirugía»", "Un implante también se cuida, y cuesta mucho menos que rehacerlo",
  "Portadores de implantes, propios y de otros centros.",
  "Un segmento enorme y desatendido: casi nadie les llama, porque no produce caja inmediata.",
  "Revisión de mantenimiento con informe, y entrada natural al programa de cuidado.",
  "¿Cuándo le revisaron los implantes por última vez? Le explico qué pasa cuando no se revisan.",
  "Agenda de recuerdo del higienista e informe escrito al paciente. Arranque en octubre.",
  72, "Bajo · tiempo de higienista", "Octubre", "Higienista, con supervisión de Dirección",
  "Indicador 7 · pacientes en mantenimiento activo",
  "Si el mantenimiento activo no crece dos trimestres seguidos, se revisa el circuito de recuerdo.",
  "Indicador 7 definido y en captura"),

 ("C7", "«Segunda opinión, sin compromiso»", "Traiga el presupuesto que le han dado. Lo miramos juntos",
  "Quien ya tiene un plan de tratamiento de otro centro y no está seguro.",
  "Llega con la decisión medio tomada y con toda la información encima de la mesa. Convierte más que ningún otro.",
  "Diagnóstico completo propio y explicación de las diferencias, sin presión de cierre.",
  "No vengo a criticar a nadie. Vamos a mirar su caso desde cero y luego usted compara.",
  "Oferta explícita en el mensaje y en recepción. Arranque en mayo.",
  66, "Bajo", "Mayo", "Dirección",
  "Conversión específica del segmento frente a la conversión general",
  "Si acaba convirtiéndose en una negociación de precio, se suspende: destruye la política de D1.",
  "D1 · política de precios y tabla de descuentos"),

 ("C8", "Prescripción de pacientes", "Si le hemos tratado bien, dígaselo a quien lo necesite",
  "La base propia, en tratamiento y terminada.",
  "El canal más barato, el de mayor conversión y el único que nadie puede copiar.",
  "Nada material. Se pide, sencillamente, en el momento adecuado del recorrido.",
  "Si ha estado a gusto, lo que más nos ayuda es que se lo cuente a alguien que lo esté pasando como usted lo pasaba.",
  "Petición formal integrada en el protocolo, en el momento de mayor satisfacción. Permanente.",
  56, "Nulo", "Permanente", "Todo el equipo, con Dirección como responsable",
  "Indicador 8 · captación por recomendación",
  "Si la recomendación no crece con la base, es que la experiencia no está a la altura: se mira eso, no la campaña.",
  "Indicador 8 definido y campo de origen obligatorio"),

 ("C9", "Presencia digital y reseñas", "Que quien nos busque nos encuentre, y que al encontrarnos confíe",
  "Quien busca activamente en Vigo y la ría.",
  "Búsqueda, ficha de negocio y reseñas. Es el escaparate, no el vendedor.",
  "Información honesta, casos reales y respuesta a las preguntas que la gente hace de verdad.",
  "No hay guion: hay contenido. La pregunta que responde cada pieza es una que un paciente hizo en consulta.",
  "Ficha de negocio, reseñas pedidas sistemáticamente, contenido de casos. Todo el año salvo verano.",
  42, "Medio-alto · la única con gasto externo relevante", "Enero", "Responsable de marca, designado en D8",
  "Coste por primera visita captada y volumen de reseñas nuevas",
  "Si el coste por primera visita supera el margen de contribución del caso medio, se apaga.",
  "D3 · arquitectura de marca · D4 · presupuesto de captación"),
]


def ficha(c):
    (cod, nombre, promesa, quien, donde, oferta, guion, canal, _aporte, coste,
     arranque, dueno, indicador, parada, depende) = c
    f = MODELO[cod]
    aporte = f["aporte"] / 1000
    coste = "%s k€ al año" % _mil(f["coste"] / 1000)
    retorno = ("%.1f € por cada euro gastado" % f["retorno"] if f["retorno"] > 0
               else "negativo en régimen · se aprueba como habilitador, no como campaña")
    return '''    <article class="acta campana">
      <header class="acta__cab">
        <div><span class="acta__cod">%s</span><b>%s</b></div>
        <span class="mono">Arranque: %s · Aporta %s k€/año</span>
      </header>
      <div class="acta__cuerpo">
        <p class="campana__promesa">%s</p>
        <dl class="campana__campos">
          <div><dt>A quién</dt><dd>%s</dd></div>
          <div><dt>Dónde está</dt><dd>%s</dd></div>
          <div><dt>Qué se le ofrece</dt><dd>%s</dd></div>
          <div><dt>Canal y ritmo</dt><dd>%s</dd></div>
        </dl>
        <p class="acta__rot">De dónde sale la cifra</p>
        <p class="campana__cuenta">%s</p>
        <p class="acta__rot">Cómo se abre la conversación</p>
        <div class="script"><q>%s</q></div>
        <dl class="campana__campos campana__campos--pie">
          <div><dt>Contribución exigida</dt><dd><strong>%s k€ al año</strong>, en régimen</dd></div>
          <div><dt>Coste y retorno</dt><dd>%s · %s</dd></div>
          <div><dt>Responsable</dt><dd>%s</dd></div>
          <div><dt>Depende de</dt><dd>%s</dd></div>
          <div><dt>Cómo se mide</dt><dd>%s</dd></div>
          <div><dt>Umbral de parada</dt><dd>%s</dd></div>
        </dl>
        <div class="acta__rejilla acta__rejilla--3">
          <div><span>Fecha de arranque acordada</span><i></i></div>
          <div><span>Primera revisión (60 días)</span><i></i></div>
          <div><span>Resultado a la revisión</span><i></i></div>
        </div>
      </div>
    </article>''' % (cod, nombre, arranque, _mil(aporte), promesa, quien, donde, oferta, canal,
                     _derivacion(cod), guion, _mil(aporte), coste, retorno, dueno, depende, indicador, parada)


bloque = '''<!--@CAMPANAS-->
<section class="section" id="campanas">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Anexo B · Fichas de campaña</p>
      <h2>Nueve hojas para poner en marcha, no para leer</h2>
      <p>Una por campaña, con la promesa, a quién va dirigida, qué se le ofrece, cómo se abre la conversación, quién responde y —lo que casi nunca se escribe— <strong>en qué momento se para</strong>. Se imprimen, se reparten al responsable de cada una y se revisan a los sesenta días.</p>
    </div>

    <div class="gate" style="max-width:none">
      <p class="eyebrow">Cómo se usa una ficha</p>
      <p>La contribución exigida no es una previsión: es el compromiso que asume quien la firma. El umbral de parada no es pesimismo: es lo que impide que una campaña que no funciona siga consumiendo presupuesto y atención durante un año entero porque a nadie le apetece admitirlo. <strong>Una campaña sin umbral de parada no se cancela nunca.</strong></p>
    </div>

%s
  </div>
</section>
''' % "\n\n".join(ficha(c) for c in C)

SALIDA.write_text(bloque, encoding="utf-8")
print("fichas de campaña:", len(C), "·", SALIDA.stat().st_size, "bytes")
