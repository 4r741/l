#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modelo de la cartera de campañas: de los supuestos a la cifra.

    python3 modelo-campanas.py            # tabla en pantalla
    python3 modelo-campanas.py --json     # datos para figuras y documento

Ninguna cifra de la Parte VI de la Tesis se escribe a mano: todas salen de
aquí. Cada campaña declara su universo, la parte de la agenda que ocupa, su
tasa de conversión y su ticket, y de ahí se deriva lo que aporta. Si un
supuesto cambia, se cambia en este archivo y el documento se regenera.

La regla que gobierna el modelo: **con la agenda llena, una campaña no vale
lo que factura, sino la diferencia entre el paciente que trae y el paciente
al que desplaza.** Es el criterio conservador y es el que se usa aquí.
"""
import json
import sys

# ---------------------------------------------------------------- capacidad
PV_DIA, DIAS, MESES = 4, 21, 12
PV_ANO = PV_DIA * DIAS * MESES                 # 1.008 primeras visitas al año

# ---------------------------------------------------------------- línea base
CONVERSION_BASE = 0.45                          # §18, supuesto de trabajo
TICKET_BASE = 1800                              # §18, supuesto de trabajo
VALOR_BASE = CONVERSION_BASE * TICKET_BASE      # 810 € por primera visita
MARGEN = 0.40                                   # margen de contribución, §18

FACTURACION_HEREDADA = 720_000                  # punto de partida, §7
PV_HEREDADAS = FACTURACION_HEREDADA / VALOR_BASE

# ---------------------------------------------------------------- campañas
# Las que compiten por la agenda: ocupan primeras visitas y valen la
# diferencia entre su rendimiento y el de la visita que desplazan.
AGENDA = [
    dict(cod="C2", nombre="«Su caso no es imposible»", pv=80, conv=0.50, ticket=3400, coste=14_000,
         razon="Casos complejos y rehabilitaciones: menos volumen, mucho más ticket."),
    dict(cod="C3", nombre="«Volvemos a llamarle»", pv=130, conv=0.48, ticket=1900, coste=3_000,
         razon="Pacientes propios: convierten bien porque ya confían, con ticket ordinario."),
    dict(cod="C4", nombre="Red de derivación", pv=70, conv=0.60, ticket=2400, coste=11_000,
         razon="Llegan enviados por un colega, con el caso ya acotado: la conversión más alta."),
    dict(cod="C5", nombre="«Sin miedo»", pv=55, conv=0.45, ticket=2800, coste=9_000,
         razon="Años sin tratarse: cuando deciden, el plan es amplio."),
    dict(cod="C7", nombre="«Segunda opinión, sin compromiso»", pv=70, conv=0.42, ticket=2600, coste=4_000,
         razon="Vienen a comparar: convierten menos, pero con diagnóstico completo y ticket alto."),
    dict(cod="C8", nombre="Prescripción de pacientes", pv=120, conv=0.55, ticket=2000, coste=1_000,
         razon="El canal de mayor confianza previa y coste casi nulo."),
    dict(cod="C9", nombre="Presencia digital y reseñas", pv=83, conv=0.40, ticket=1900, coste=34_000,
         razon="Búsqueda fría: la calidad media más baja de todas. Es habilitador, no productor."),
]

# Las que producen fuera del embudo de la primera visita.
FUERA = [
    dict(cod="C1", nombre="Giraldo Te Cuida", coste=6_000,
         partes=[("Cuotas netas de sustitución", 61_000,
                  "460 adheridos × 190 € de cuota, menos el 30 % que sustituye higienes ya facturables."),
                 ("Tratamiento detectado en la base adherida", 110_000,
                  "460 adheridos × 16 % que necesita tratamiento nuevo al año × 1.500 € de ticket medio.")],
         razon="No ocupa agenda de primera visita: produce sobre pacientes que ya son del centro."),
    dict(cod="C6", nombre="«La revisión que evita la cirugía»", coste=5_000,
         partes=[("Revisiones facturadas", 100_000,
                  "1.050 revisiones al año × 95 €, entre base propia y portadores de otros centros."),
                 ("Tratamiento detectado a tiempo", 72_000,
                  "1.050 revisiones × 6 % con hallazgo tratable × 1.150 € de ticket medio.")],
         razon="El mantenimiento paga su propia consulta y descubre el tratamiento antes de que sea caro."),
]


def calcula():
    pv_campanas = sum(c["pv"] for c in AGENDA)
    pv_libres = PV_ANO - pv_campanas
    if pv_libres < 0:
        raise SystemExit("Las campañas piden %d primeras visitas y la agenda solo tiene %d."
                         % (pv_campanas, PV_ANO))

    filas = []
    for c in AGENDA:
        valor = c["conv"] * c["ticket"]
        aporte = c["pv"] * (valor - VALOR_BASE)
        filas.append(dict(c, valor=valor, aporte=aporte, tipo="agenda",
                          retorno=aporte / c["coste"] if c["coste"] else None))
    for c in FUERA:
        aporte = sum(v for _, v, _ in c["partes"])
        filas.append(dict(c, pv=0, valor=None, aporte=aporte, tipo="fuera",
                          retorno=aporte / c["coste"] if c["coste"] else None))
    filas.sort(key=lambda f: f["cod"])

    # --- el puente, bloque a bloque ---
    llenar_agenda = (PV_ANO - PV_HEREDADAS) * VALOR_BASE
    mezcla = sum(f["aporte"] for f in filas if f["tipo"] == "agenda")
    seguimiento = sum(f["aporte"] for f in filas if f["tipo"] == "fuera")
    planificado = FACTURACION_HEREDADA + llenar_agenda + mezcla + seguimiento
    objetivo = 1_200_000
    colchon = planificado - objetivo

    return dict(
        capacidad=dict(pv_ano=PV_ANO, pv_heredadas=round(PV_HEREDADAS),
                       pv_dia_hoy=round(PV_HEREDADAS / (DIAS * MESES), 2),
                       pv_campanas=pv_campanas, pv_libres=pv_libres,
                       valor_base=VALOR_BASE),
        puente=dict(base=FACTURACION_HEREDADA, llenar=llenar_agenda, mezcla=mezcla,
                    seguimiento=seguimiento, planificado=planificado,
                    colchon=-colchon, objetivo=objetivo,
                    colchon_pct=colchon / planificado),
        campanas=filas,
        coste_total=sum(f["coste"] for f in filas),
    )


def mil(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def informe(d):
    c, p = d["capacidad"], d["puente"]
    print("CAPACIDAD")
    print("  Agenda instalada ............. %s primeras visitas al año (%d/día × %d × %d)"
          % (mil(c["pv_ano"]), PV_DIA, DIAS, MESES))
    print("  Ocupación heredada ........... %s PV (%.2f al día) → %s €"
          % (mil(c["pv_heredadas"]), c["pv_dia_hoy"], mil(FACTURACION_HEREDADA)))
    print("  Valor de una PV hoy .......... %d €  (%.0f %% × %s €)"
          % (c["valor_base"], CONVERSION_BASE * 100, mil(TICKET_BASE)))
    print("  Agenda que piden las campañas  %s PV · quedan %s libres"
          % (mil(c["pv_campanas"]), mil(c["pv_libres"])))
    print()
    print("CARTERA")
    print("  %-4s %-38s %5s %6s %8s %9s %9s %8s" %
          ("Cód", "Campaña", "PV", "Conv.", "Ticket", "Aporte", "Coste", "Retorno"))
    for f in d["campanas"]:
        print("  %-4s %-38s %5s %6s %8s %9s %9s %8s" % (
            f["cod"], f["nombre"][:38],
            mil(f["pv"]) if f["pv"] else "—",
            ("%.0f %%" % (f["conv"] * 100)) if f["valor"] else "—",
            mil(f["ticket"]) + " €" if f["valor"] else "—",
            mil(f["aporte"] / 1000) + " k",
            mil(f["coste"] / 1000) + " k",
            ("%.1f×" % f["retorno"]) if f["retorno"] and f["retorno"] > 0 else "negativo"))
    print("  %-4s %-38s %5s %6s %8s %9s %9s" % (
        "", "TOTAL", mil(c["pv_campanas"]), "", "",
        mil(sum(f["aporte"] for f in d["campanas"]) / 1000) + " k",
        mil(d["coste_total"] / 1000) + " k"))
    print("  Coste de la cartera sobre el objetivo: %.1f %%" % (d["coste_total"] / p["objetivo"] * 100))
    print()
    print("PUENTE")
    for rotulo, clave in (("Base heredada", "base"), ("Llenar la agenda", "llenar"),
                          ("Mejora de mezcla (campañas de agenda)", "mezcla"),
                          ("Seguimiento y recurrente (fuera del embudo)", "seguimiento")):
        print("  %-44s %10s €" % (rotulo, mil(p[clave])))
    print("  %-44s %10s €" % ("PLANIFICADO", mil(p["planificado"])))
    print("  %-44s %10s €  (%.1f %%)" % ("Colchón de no ejecución", mil(-p["colchon"]), p["colchon_pct"] * 100))
    print("  %-44s %10s €" % ("OBJETIVO", mil(p["objetivo"])))
    print()
    print("CONCENTRACIÓN · qué se cae si falla cada campaña")
    for f in sorted(d["campanas"], key=lambda f: -f["aporte"]):
        peso = f["aporte"] / (p["planificado"] - FACTURACION_HEREDADA - p["llenar"])
        print("  %-4s %-38s %9s k€  %5.1f %% de lo que aportan las campañas"
              % (f["cod"], f["nombre"][:38], mil(f["aporte"] / 1000), peso * 100))


if __name__ == "__main__":
    datos = calcula()
    if "--json" in sys.argv:
        print(json.dumps(datos, ensure_ascii=False, indent=1))
    else:
        informe(datos)
