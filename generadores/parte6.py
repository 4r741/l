#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parte VI de la Tesis y sus supuestos, con las cifras traídas del modelo.
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"
import importlib.util

spec = importlib.util.spec_from_file_location("modelo", RAIZ / "modelo-campanas.py")
modelo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modelo)
D = modelo.calcula()
C, P = D["capacidad"], D["puente"]
POR = {f["cod"]: f for f in D["campanas"]}


def mil(v):
    """Miles con punto y signo menos tipográfico, no guion."""
    return "{:,}".format(int(round(v))).replace(",", ".").replace("-", "\u2212")


def k(cod):
    return mil(POR[cod]["aporte"] / 1000)


# a quién va, dónde se encuentra, por qué esa conversión y ese ticket
RETRATO = {
 "C1": ("Todo paciente que termina tratamiento", "No hay que encontrarlo: ya está sentado delante",
        "No ocupa agenda de primera visita"),
 "C2": ("Atrofia severa, rehabilitación completa, casos rechazados en otros centros",
        "Contenido propio, prescripción y segunda opinión",
        "Convierte la mitad porque llega decidido, y el plan es de rehabilitación"),
 "C3": ("Pacientes del centro sin visita en más de dieciocho meses",
        "Están en la base de datos: no hay que captarlos",
        "Confían, así que convierten bien, pero el caso suele ser ordinario"),
 "C4": ("Clínicas generalistas de la ría que no hacen implantología compleja",
        "Visita profesional, uno a uno",
        "La conversión más alta de la cartera: llegan enviados y con el caso acotado"),
 "C5": ("Ansiedad dental severa: años sin sentarse en un sillón",
        "Mensaje explícito; casi nunca preguntan",
        "Cuando por fin deciden, el plan acumulado es amplio"),
 "C6": ("Portadores de implantes, propios y de otros centros",
        "Agenda de recuerdo del higienista",
        "No ocupa agenda de primera visita"),
 "C7": ("Quien tiene un presupuesto de otro centro y dudas",
        "Oferta explícita en el mensaje y en recepción",
        "Convierte menos porque compara, pero el diagnóstico completo eleva el plan"),
 "C8": ("La base propia, en tratamiento y terminada",
        "Petición formal en el momento adecuado del recorrido",
        "La mayor confianza previa de todas: la conversión más alta del embudo abierto"),
 "C9": ("Quien busca activamente en Vigo y la ría",
        "Ficha de negocio, reseñas y contenido de casos",
        "Búsqueda fría: la calidad media más baja de la cartera"),
}

DEPENDE = {"C1": "D5 · D14", "C2": "—", "C3": "Inventario de cartera", "C4": "—",
           "C5": "<strong>D6</strong>", "C6": "—", "C7": "<strong>D1</strong>",
           "C8": "—", "C9": "<strong>D3 · D4</strong>"}

# riesgo de publicidad sanitaria: V11 del sistema de verificaciones
V11 = {
 "C1": ("Bajo", "Contrato de adhesión: es materia de consumo, no de publicidad sanitaria."),
 "C2": ("<strong>Alto</strong>", "Prohibido sugerir resultados garantizados o comparar con otros profesionales. Los casos publicados exigen consentimiento expreso y no pueden presentarse como resultado esperable."),
 "C3": ("Bajo", "Comunicación a pacientes propios, no publicidad."),
 "C4": ("Medio", "Comunicación entre profesionales; el acuerdo no puede incluir contraprestación económica por derivación."),
 "C5": ("<strong>Alto</strong>", "No puede prometerse ausencia de dolor ni presentarse la sedación como servicio general sin la habilitación de D6."),
 "C6": ("Bajo", "Recordatorio asistencial a pacientes con tratamiento previo."),
 "C7": ("Medio", "No puede formularse como comparación desfavorable con otro profesional ni como oferta de precio."),
 "C8": ("Bajo", "No puede incentivarse económicamente la recomendación."),
 "C9": ("<strong>Alto</strong>", "Toda pieza pasa por V11 antes de publicarse: es el canal con más superficie de exposición."),
}


def fila(cod):
    f, (quien, donde, porque) = POR[cod], RETRATO[cod]
    de_agenda = f["tipo"] == "agenda"
    return ('<tr><td class="num">%s</td><td><strong>%s</strong><small>%s</small></td>'
            '<td>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
            '<td class="num"><strong>%s k€</strong></td><td class="num">%s k€</td>'
            '<td class="num">%s</td><td>%s</td></tr>' % (
        f["cod"], f["nombre"], porque, quien,
        mil(f["pv"]) if de_agenda else "—",
        ("%.0f %%" % (f["conv"] * 100)) if de_agenda else "—",
        (mil(f["ticket"]) + " €") if de_agenda else "—",
        k(cod), mil(f["coste"] / 1000),
        ("%.1f×" % f["retorno"]) if f["retorno"] > 0 else '<span class="sem sem--rojo">negativo</span>',
        DEPENDE[cod]))


def fila_v11(cod):
    riesgo, nota = V11[cod]
    return ('<tr><td class="num">%s</td><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>'
            % (cod, POR[cod]["nombre"], riesgo, nota))


CODIGOS = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
dos = (POR["C6"]["aporte"] + POR["C1"]["aporte"]) / sum(f["aporte"] for f in D["campanas"])

DATOS = dict(
    pv_ano=mil(C["pv_ano"]), pv_hoy=mil(C["pv_heredadas"]),
    pv_dia_hoy=("%.1f" % C["pv_dia_hoy"]).replace(".", ","),
    valor_base=mil(C["valor_base"]), pv_camp=mil(C["pv_campanas"]), pv_libres=mil(C["pv_libres"]),
    base=mil(P["base"] / 1000), llenar=mil(P["llenar"] / 1000), mezcla=mil(P["mezcla"] / 1000),
    seguimiento=mil(P["seguimiento"] / 1000), planificado=mil(P["planificado"] / 1000),
    colchon=mil(-P["colchon"] / 1000), colchon_pct="%.0f" % (P["colchon_pct"] * 100),
    objetivo=mil(P["objetivo"] / 1000),
    coste=mil(D["coste_total"] / 1000),
    coste_pct=("%.1f" % (D["coste_total"] / P["objetivo"] * 100)).replace(".", ","),
    filas="\n          ".join(fila(c) for c in CODIGOS),
    filas_v11="\n          ".join(fila_v11(c) for c in CODIGOS),
    dos_pct="%.0f" % (dos * 100),
    c1=k("C1"), c2=k("C2"), c3=k("C3"), c4=k("C4"), c5=k("C5"),
    c6=k("C6"), c7=k("C7"), c8=k("C8"), c9=k("C9"),
    pv_final=mil((P["base"] + P["llenar"] + P["mezcla"]) / 1000),
)

# ---- §18 · los supuestos de la Parte VI, en el registro donde deben estar ----
def fila_supuesto(cod):
    f = POR[cod]
    if f["tipo"] == "agenda":
        detalle = ("%s primeras visitas al año · %.0f %% de conversión · %s € de ticket"
                   % (mil(f["pv"]), f["conv"] * 100, mil(f["ticket"])))
    else:
        detalle = " · ".join(p[2] for p in f["partes"])
    return ('<tr><td class="num">%s</td><td><strong>%s</strong></td><td>%s</td>'
            '<td>%s</td><td class="num">%s k€</td></tr>'
            % (f["cod"], f["nombre"], detalle, RETRATO[cod][2], mil(f["coste"] / 1000)))


SUPUESTOS = """<!--@SUPUESTOS6-->
    <h3 style="font-size:var(--step-2);margin:3.2rem 0 .5rem">S8 · Los supuestos de la cartera de campañas</h3>
    <p style="color:var(--ink-2);max-width:70ch">La Parte VI no añade supuestos nuevos sobre la clínica: reparte los que ya están en S1 a S7 entre nueve campañas. Lo que sí declara es cuánta agenda ocupa cada una y con qué rendimiento, y eso es lo que va aquí. <strong>Ninguno procede de una medición del centro.</strong> Todos viven en <code>modelo-campanas.py</code>, que se puede ejecutar y modificar; el guion de coherencia comprueba que este documento no diga nada distinto de lo que ese modelo calcula.</p>

    <div class="tablewrap">
      <table>
        <thead><tr><th>Cód.</th><th>Campaña</th><th>Qué se supone</th><th>Por qué ese rendimiento</th><th>Coste</th></tr></thead>
        <tbody>
          @FILAS@
        </tbody>
      </table>
    </div>
    <p class="t-fig__note">Valor de referencia con el que se compara toda campaña: {{valor_base}} € por primera visita (45 % × 1.800 €, supuestos S2 y S3). Margen de contribución del 40 %, supuesto S4.</p>

    <div class="callout" style="max-width:none">
      <p class="eyebrow">El supuesto más frágil de los nueve</p>
      <p>Los 130 pacientes al año que C3 supone recuperables de la cartera dormida. Es el único que no se apoya en ningún dato del sector ni en la experiencia del equipo: se apoya en que exista una cartera que nadie ha contado. Dos días de trabajo administrativo lo convertirían en un hecho, y hasta que eso ocurra conviene leer el puente sabiendo que este tramo puede no existir.</p>
    </div>
""".replace("@FILAS@", "\n          ".join(fila_supuesto(c) for c in CODIGOS))

(FUENTES / "tesis-supuestos-campanas.html").write_text(SUPUESTOS.replace("{{valor_base}}", mil(C["valor_base"])), encoding="utf-8")

plantilla = (FUENTES / "tesis-p6-plantilla.html").read_text(encoding="utf-8")
salida = plantilla
for clave, valor in DATOS.items():
    salida = salida.replace("{{%s}}" % clave, str(valor))
assert "{{" not in salida, salida[salida.index("{{"):salida.index("{{") + 60]
(FUENTES / "tesis-p6-generada.html").write_text(salida, encoding="utf-8")
print("Parte VI generada ·", len(salida), "bytes · cifras traídas del modelo")
