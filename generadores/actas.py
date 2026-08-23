#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anexo A: una hoja de acta por decisión, lista para firmar.
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"

SALIDA = FUENTES / "tesis-anexo-a-actas.html"

# código, materia, plazo, qué se pide, alternativas A/B/C, documentos afectados, indicador
D = [
 ("D1", "Política de precios y tabla de descuentos", "Inmediato",
  "Aprobar la tipología cerrada de descuentos, sus porcentajes máximos por tipo, el tope de acumulación y quién autoriza cada tramo.",
  ["Tipología cerrada con tope de acumulación y autorización nominal por tramo",
   "Descuento máximo único sin tipología, autorizado siempre por Gerencia",
   "Mantener la situación actual y revisar en el primer trimestre"],
  "Manual Maestro, Parte VI · Protocolo, Fase 10", "Margen por caso y producto pendiente"),
 ("D2", "Garantías publicadas por tipo de tratamiento", "Inmediato",
  "Fijar los plazos de garantía por tipo de tratamiento que el centro asume por escrito ante el paciente.",
  ["Tabla de garantías publicada y entregada con cada presupuesto",
   "Garantía única de duración uniforme para todo tratamiento",
   "Sin garantía publicada, resolución caso a caso"],
  "Otros documentos, 12 · cartelería de sala", "Reclamaciones formales · indicador 3"),
 ("D3", "Arquitectura de marca y naming", "Primer trimestre",
  "Aprobar la arquitectura por verticales y ordenar la verificación legal de marca y dominios antes de cualquier adopción.",
  ["Arquitectura por verticales, condicionada a verificación registral previa",
   "Marca única sin verticales",
   "Aplazar hasta disponer del estudio de mercado"],
  "Otros documentos, 9 · marca y captación", "Captación por recomendación · indicador 8"),
 ("D4", "Presupuesto anual de captación y modelo de ejecución", "Primer trimestre",
  "Autorizar el porcentaje de facturación destinado a marca y captación, y el modelo de ejecución: interno, agencia o mixto.",
  ["Porcentaje fijo de facturación, ejecución mixta con responsable interno",
   "Importe cerrado anual con agencia externa",
   "Sin presupuesto propio hasta que la conversión esté en umbral"],
  "Otros documentos, 9 · economía unitaria", "Coste por primera visita captada"),
 ("D5", "Programa de cuidado: precio, catálogo y validación jurídica", "Inmediato",
  "Cerrar precio, catálogo de servicios y límites, y ordenar la validación jurídica del contrato de adhesión antes de comercializarlo.",
  ["Cerrar catálogo y precio ahora, comercializar tras dictamen jurídico favorable",
   "Lanzar con catálogo provisional y revisar tras los primeros contratos",
   "Aplazar el lanzamiento al segundo semestre"],
  "Otros documentos, 14 · Protocolo, Fases 10 a 12", "Mantenimiento activo · indicador 7"),
 ("D6", "Línea de sedación consciente", "Primer trimestre",
  "Autorizar —o posponer— la línea, condicionada a la verificación del alcance competencial con asesoría y colegio profesional.",
  ["Autorizar condicionada al informe favorable de alcance competencial",
   "Posponer la línea y derivar el segmento a un centro colaborador",
   "Descartar la línea en este horizonte"],
  "Manual Maestro, Parte V", "Casos del segmento de ansiedad severa"),
 ("D7", "Marco de inversión en flujo digital", "Segundo trimestre",
  "Aprobar el marco de inversión tecnológica y el criterio de retorno exigible a cada partida.",
  ["Marco con periodo de recuperación máximo exigible por partida",
   "Aprobación caso a caso por la Junta sin marco previo",
   "Congelar la inversión tecnológica hasta disponer de línea base"],
  "Manual Maestro, Parte VI · compras", "Documentación en el día · indicador 4"),
 ("D8", "Responsables funcionales y Comité de Transición", "Inmediato",
  "Designar con nombre al responsable de marca y reseñas, y confirmar la composición y periodicidad del Comité de Transición.",
  ["Designación nominal de las cuatro áreas y comité quincenal",
   "Designación nominal parcial, resto asumido por Dirección",
   "Mantener todas las áreas bajo Dirección"],
  "Manual Maestro, Parte III · RACI", "Bajas voluntarias · indicador 2"),
 ("D9", "Regla de cartera de innovación 70/20/10", "Esta sesión",
  "Aprobar el reparto orientativo entre horizontes H1, H2 y H3 y la regla de que ningún horizonte se financie con recursos comprometidos en otro.",
  ["Reparto 70/20/10 con revisión anual",
   "Decidir caso a caso según mérito de cada iniciativa",
   "Concentrar todo el esfuerzo en H1 durante el primer año"],
  "Otros documentos, 8 · §6 de la Tesis", "Reparto ejecutado frente al aprobado"),
 ("D10", "Orden de prelación del capital", "Esta sesión",
  "Aprobar las cinco prioridades —continuidad, foso, conversión, captación, capacidad— y la regla de excepción documentada.",
  ["Orden de prelación con excepción documentada y presentada en Junta",
   "Presupuesto por partidas contables sin orden de prelación",
   "Orden de prelación sin regla de excepción"],
  "§15 de la Tesis · presupuesto anual", "Ejecución por prioridad, trimestral"),
 ("D11", "Condición de apertura de segunda unidad", "Esta sesión",
  "Establecer que no se autoriza búsqueda de plaza ni compromiso inmobiliario sin acreditar los pasos 3 y 4 del §10.",
  ["Condición estricta: sin pasos 3 y 4 acreditados, no hay prospección",
   "Condición orientativa, con posibilidad de dispensa de la Junta",
   "Sin condición: decidir por oportunidad de mercado"],
  "§10 de la Tesis", "Un trimestre en umbral sin intervención de Dirección"),
 ("D12", "Suelo anual de inversión en el sistema", "Esta sesión",
  "Fijar un suelo anual de inversión en formación, verificación y documentación, expresado como porcentaje de facturación, irreducible sin acuerdo expreso.",
  ["Suelo porcentual irreducible sin acuerdo expreso de la Junta",
   "Partida anual revisable trimestralmente según resultado",
   "Sin suelo: gasto variable ajustable a la marcha del ejercicio"],
  "Presupuesto anual, partida de sistema", "Auditorías en fecha · indicador 10"),
 ("D13", "Disparadores de Junta extraordinaria", "Esta sesión",
  "Aprobar los cinco disparadores del pre-mortem como obligación automática de convocatoria, sin valoración previa de gravedad.",
  ["Los cinco disparadores, con convocatoria automática",
   "Los cinco disparadores, con convocatoria a criterio de Dirección",
   "Sin disparadores: convocatoria ordinaria trimestral"],
  "Anexo de gobernanza del Manual Maestro", "Indicadores 2, 3, 9 y 10"),
 ("D15", "Objetivo de facturación y horizonte", "Esta sesión",
  "Fijar la cifra de facturación anual y el ejercicio en que se exige, y aprobar la cartera de nueve campañas del §21 como contenido de D4.",
  ["1,2 M€ en el ejercicio tercero, con la senda 890 · 1.060 · 1.200",
   "1,2 M€ en dieciocho meses, anticipando la prioridad 5 del §15 y ampliando capacidad",
   "Aplazar la fijación del objetivo hasta disponer de línea base real"],
  "§20 a §23 de la Tesis · presupuesto anual", "Facturación anual frente a la senda de §22"),
 ("D14", "Programa de cuidado obligatorio en el cierre", "Tras D5",
  "Establecer que ofrecer el programa es punto verificable obligatorio del cierre de todo tratamiento, y medir la tasa de ofrecimiento además de la de contratación.",
  ["Obligatorio y medido, con umbral del 90 % de ofrecimiento",
   "Recomendado, medido pero sin umbral exigible",
   "A criterio comercial del profesional"],
  "Protocolo, Fase 12 · Otros documentos, 14", "Ofrecimiento del programa · indicador 9"),
]

LETRAS = "ABC"


def ficha(codigo, materia, plazo, pide, alternativas, documentos, indicador):
    opciones = "\n".join(
        '        <li><span class="acta__caja" aria-hidden="true"></span>'
        '<b>%s</b><span>%s</span></li>' % (LETRAS[i], alternativa)
        for i, alternativa in enumerate(alternativas))
    return '''    <article class="acta">
      <header class="acta__cab">
        <div><span class="acta__cod">%s</span><b>%s</b></div>
        <span class="mono">Registro de decisión nº ______ · Plazo: %s</span>
      </header>
      <div class="acta__cuerpo">
        <p class="acta__pide"><b>Qué se somete a acuerdo.</b> %s</p>
        <p class="acta__rot">Alternativas evaluadas · márquese la adoptada</p>
        <ul class="acta__ops">
%s
          <li><span class="acta__caja" aria-hidden="true"></span><b>D</b><span class="acta__linea">Otra: </span></li>
        </ul>
        <p class="acta__rot">Fundamento de la resolución</p>
        <div class="acta__pauta" aria-hidden="true"></div>
        <div class="acta__pauta" aria-hidden="true"></div>
        <div class="acta__rejilla">
          <div><span>Entrada en vigor</span><i></i></div>
          <div><span>Responsable de ejecución</span><i></i></div>
          <div><span>Próxima revisión</span><i></i></div>
          <div><span>Consulta previa realizada</span><i></i></div>
        </div>
        <dl class="acta__meta">
          <div><dt>Documentos afectados</dt><dd>%s</dd></div>
          <div><dt>Se verificará en</dt><dd>%s</dd></div>
        </dl>
        <p class="acta__rot">Comunicación del acuerdo</p>
        <div class="acta__rejilla acta__rejilla--3">
          <div><span>Destinatarios</span><i></i></div>
          <div><span>Canal</span><i></i></div>
          <div><span>Fecha</span><i></i></div>
        </div>
        <div class="acta__firmas">
          <div><span>Presidencia</span><i></i></div>
          <div><span>Secretaría</span><i></i></div>
          <div><span>Fecha de la sesión</span><i></i></div>
        </div>
      </div>
    </article>'''  % (codigo, materia, plazo, pide, opciones, documentos, indicador)


cuerpo = "\n\n".join(ficha(*fila) for fila in D)

bloque = '''<!--@ACTAS-->
<section class="section" id="acuerdos">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Anexo A · Cuadernillo de acuerdos</p>
      <h2>@CUANTAS@ hojas para salir de la sesión con el acta hecha</h2>
      <p>Una hoja por decisión, con las alternativas ya redactadas y espacio para la resolución, el fundamento, la fecha de entrada en vigor y las firmas. Se imprimen a una cara, se rellenan durante la sesión y se archivan. <strong>Sin este cuadernillo, la Junta sale con @cuantas@ acuerdos y un acta por redactar</strong>; con él, sale con @cuantas@ documentos firmados y con fecha.</p>
    </div>

    <div class="gate" style="max-width:none">
      <p class="eyebrow">Cómo se usa</p>
      <p>Marque la alternativa adoptada, escriba el fundamento en dos líneas —basta con dos— y fije la fecha de entrada en vigor. Un acuerdo sin fecha de entrada en vigor no llega al equipo, y un acuerdo cuyo fundamento no se anotó es un acuerdo que dentro de tres meses nadie sabrá por qué se tomó así. La opción D existe porque una Junta no está obligada a elegir entre las alternativas que le presentan.</p>
    </div>

%s
  </div>
</section>
''' % cuerpo

LETRA = {13: "Trece", 14: "Catorce", 15: "Quince", 16: "Dieciséis", 17: "Diecisiete"}
cuantas = LETRA.get(len(D), str(len(D)))
bloque = bloque.replace("@CUANTAS@", cuantas).replace("@cuantas@", cuantas.lower())
assert "@CUANTAS@" not in bloque and "@cuantas@" not in bloque, "queda alguna marca sin sustituir"

SALIDA.write_text(bloque, encoding="utf-8")
print("cuadernillo:", len(D), "fichas ·", SALIDA.stat().st_size, "bytes")
