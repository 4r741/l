#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El modelo de los seis puestos: qué responde cada uno y dónde está escrito.

No inventa nada. Cada perfil se compone de lo que el sistema ya dice de él en
cuatro sitios distintos —el Manual Maestro, la matriz RACI, el Protocolo de
Primera Visita y Otros documentos— que hasta ahora había que ir a buscar por
separado en cuatro archivos. Aquí se declara qué trozo de cada documento le
corresponde a quién; el guion que dibuja la página los reúne.
"""

# La matriz RACI del Manual, tal cual está publicada: catorce fases por seis
# columnas. R ejecuta, A responde del resultado, C se consulta, I se informa.
RACI_COLUMNAS = ["REC", "DC", "DR", "AUX", "DdC", "RAC"]
RACI = [
    ("1. Preparación previa",          ["R/A", "I", "—", "—", "I", "—"]),
    ("2. Recepción y tour",            ["R", "R/A", "—", "—", "—", "—"]),
    ("3. Anamnesis/RGPD y alta",       ["R/A", "R/A", "—", "—", "—", "—"]),
    ("4. Historial y consentimiento",  ["—", "I", "R/A", "—", "—", "—"]),
    ("5. Pruebas diagnósticas",        ["—", "I", "C", "R/A", "—", "—"]),
    ("6. Briefing",                    ["—", "R/A", "R/A", "I", "I", "—"]),
    ("7. Anamnesis de expectativas",   ["—", "I", "R/A", "C", "—", "—"]),
    ("8. IAC / solicitud / informe",   ["I", "R", "A", "—", "—", "—"]),
    ("9. Presentación",                ["—", "R", "R/A", "I", "—", "—"]),
    ("10. Propuesta y cierre",         ["I", "R/A", "C", "—", "I", "—"]),
    ("11. Cierre administrativo",      ["R/A", "A", "—", "—", "—", "I"]),
    ("12. Seguimiento",                ["R", "R/A", "—", "—", "—", "—"]),
    ("13. Circuito de producción",     ["I", "C", "C", "C", "I", "R/A"]),
    ("14. Mantenimiento",              ["C", "I", "C", "—", "I", "—"]),
]

QUE_ES = {
    "R": ("Ejecuta", "Hace el trabajo de esa fase."),
    "A": ("Responde", "Rinde cuentas del resultado, lo haya ejecutado o no."),
    "R/A": ("Ejecuta y responde", "Hace el trabajo y rinde cuentas de él."),
    "C": ("Se consulta", "Su criterio se pide antes de decidir, no después."),
    "I": ("Se informa", "Recibe el resultado; no decide ni ejecuta."),
    "—": ("No interviene", "Esa fase no pasa por sus manos."),
}

# ancla en el Protocolo de Primera Visita → fase de la matriz
FASES_PV = {
    "f01": 0, "f02": 1, "f03": 2, "f04": 3, "f05": 4, "f06": 5,
    "f07": 6, "f08": 7, "f09": 8, "f10": 9, "f11": 10, "f12": 11,
}

PERFILES = [
    dict(
        id="direccion", nombre="Dirección de Clínica", corto="Dirección",
        raci="DC", roles=("director", "dc"),
        que="Dirige la clínica y responde de que el sistema se cumpla. Es la única "
            "figura que puede autorizar una excepción, y la que rinde cuentas cuando "
            "algo se salta.",
        manual="m-direccion-clinica",
        bloques=[("Autoridad y sus límites", "m-g-2-autoridad-limites"),
                 ("Procedimientos", "m-g-3-procedimientos"),
                 ("Indicadores del puesto", "m-g-4-indicadores-direccion"),
                 ("Contingencias", "m-g-5-contingencias-ampliacion"),
                 ("Criterios de calidad", "m-g-5-criterios-calidad-ampliacion"),
                 ("Primeros 30 días en el puesto", "m-g-5-primeros-30-dias-puesto")],
        vanguardia=[],
    ),
    dict(
        id="doctor", nombre="Doctor", corto="Doctor",
        raci="DR", roles=("doctor", "dr"),
        que="Diagnostica, planifica y ejecuta el tratamiento. Responde del criterio "
            "clínico y de que el paciente entienda su caso antes de decidir.",
        manual="m-doctor",
        bloques=[("Cronograma de jornada", "m-d-2-cronograma-jornada"),
                 ("Procedimientos", "m-d-3-procedimientos"),
                 ("Errores documentados", "m-d-4-errores-documentados"),
                 ("Su papel comercial y sus límites", "m-d-4-ter-papel-comercial-limites"),
                 ("Indicadores del puesto", "m-d-5-indicadores-doctor"),
                 ("Contingencias", "m-d-6-contingencias-ampliacion"),
                 ("Criterios de calidad", "m-d-6-criterios-calidad-ampliacion"),
                 ("Primeros 30 días en el puesto", "m-d-6-primeros-30-dias-puesto")],
        vanguardia=[("2.1 · Preparación anticipada del caso", "m-funcion-2-1-preparacion-anticipada-caso"),
                    ("2.2 · Diagnóstico integral y predictivo", "m-funcion-2-2-diagnostico-integral-predictivo"),
                    ("2.3 · Planificación digital del tratamiento", "m-funcion-2-3-planificacion-digital-tratamientos"),
                    ("2.4 · Consentimiento informado real", "m-funcion-2-4-consentimiento-informado-real"),
                    ("2.5 · Ejecución clínica", "m-funcion-2-5-ejecucion-clinica"),
                    ("2.6 · Registro y trazabilidad", "m-funcion-2-6-registro-trazabilidad")],
    ),
    dict(
        id="recepcion", nombre="Recepción", corto="Recepción",
        raci="REC", roles=("recepcion", "rec"),
        que="La primera voz y la última. Gestiona la demanda, la agenda, el alta y "
            "el cierre administrativo, y es quien recupera al paciente que no vuelve.",
        manual="m-recepcion",
        bloques=[("Jornada minuto a minuto", "m-r-2-jornada-minuto-minuto"),
                 ("Procedimientos", "m-r-3-procedimientos"),
                 ("Su papel comercial real", "m-r-3-bis-papel-comercial-real"),
                 ("Indicadores del puesto", "m-r-4-indicadores-puesto"),
                 ("Contingencias", "m-r-5-contingencias-ampliacion"),
                 ("Criterios de calidad", "m-r-5-criterios-calidad-ampliacion"),
                 ("Primeros 30 días en el puesto", "m-r-5-primeros-30-dias-puesto")],
        vanguardia=[("1.1 · Gestión de la demanda", "m-funcion-1-1-gestion-demanda"),
                    ("1.2 · Arquitectura de agenda", "m-funcion-1-2-arquitectura-agenda"),
                    ("1.3 · Custodia documental", "m-funcion-1-3-custodia-documental"),
                    ("1.4 · Gestión económica de mostrador", "m-funcion-1-4-gestion-economica-mostrador"),
                    ("1.5 · Seguimiento y recuperación", "m-funcion-1-5-seguimiento-recuperacion")],
    ),
    dict(
        id="rac", nombre="RAC · Responsable de Producción", corto="RAC",
        raci="RAC", roles=("rac",),
        que="Responde del circuito de producción: que lo aceptado se fabrique, se "
            "coloque y se cierre. Tiene poder de bloqueo cuando un caso no está listo.",
        manual="m-rac-responsable-produccion",
        bloques=[("Poder de bloqueo", "m-c-2-poder-bloqueo"),
                 ("Procedimientos", "m-c-3-procedimientos"),
                 ("Indicadores del puesto", "m-c-4-indicadores-rac"),
                 ("Contingencias", "m-c-5-contingencias-ampliacion"),
                 ("Criterios de calidad", "m-c-5-criterios-calidad-ampliacion"),
                 ("Primeros 30 días en el puesto", "m-c-5-primeros-30-dias-puesto")],
        vanguardia=[],
    ),
    dict(
        id="auxiliar", nombre="Auxiliar", corto="Auxiliar",
        raci="AUX", roles=("auxiliar", "aux"),
        que="Sostiene el acto clínico: equipos listos, batería diagnóstica completa "
            "y esterilización trazable. Sin esto, la fase 5 no existe.",
        manual="m-auxiliar",
        bloques=[("Procedimientos", "m-x-2-procedimientos"),
                 ("Indicadores del puesto", "m-x-3-indicadores-auxiliar"),
                 ("Contingencias", "m-x-4-contingencias-ampliacion"),
                 ("Criterios de calidad", "m-x-4-criterios-calidad-ampliacion"),
                 ("Primeros 30 días en el puesto", "m-x-4-primeros-30-dias-puesto")],
        vanguardia=[("4.1 · Gestión de equipos", "m-funcion-4-1-gestion-equipos"),
                    ("4.2 · Batería diagnóstica", "m-funcion-4-2-bateria-diagnostica"),
                    ("4.3 · Esterilización y bioseguridad", "m-funcion-4-3-esterilizacion-bioseguridad")],
    ),
    dict(
        id="higienista", nombre="Higienista", corto="Higienista",
        raci=None, roles=("higienista", "hig"),
        que="El puesto del largo plazo: mantiene lo tratado, detecta pronto lo que "
            "se tuerce y sostiene la relación año tras año. Es R/A en la fase 14.",
        manual="m-higienista",
        bloques=[("Por qué este puesto es estratégico", "m-h-2-este-puesto-estrategico"),
                 ("Procedimientos", "m-h-3-procedimientos"),
                 ("Indicadores del puesto", "m-h-4-indicadores-higienista"),
                 ("Contingencias", "m-h-5-contingencias-ampliacion"),
                 ("Criterios de calidad", "m-h-5-criterios-calidad-ampliacion"),
                 ("Primeros 30 días en el puesto", "m-h-5-primeros-30-dias-puesto")],
        vanguardia=[("3.1 · Programa de mantenimiento", "m-funcion-3-1-programa-mantenimiento"),
                    ("3.2 · Detección precoz y derivación", "m-funcion-3-2-deteccion-precoz-derivacion"),
                    ("3.3 · Monitorización remota", "m-funcion-3-3-monitorizacion-remota"),
                    ("3.4 · El perfil Giraldo anual", "m-funcion-3-4-perfil-giraldo-anual")],
    ),
]


def raci_de(perfil):
    """Las catorce fases con el papel de ese perfil en cada una."""
    if not perfil["raci"]:
        # el higienista no tiene columna propia: la matriz lo dice en su nota
        return [(nombre, "C" if "Mantenimiento" in nombre else "—") for nombre, _ in RACI]
    i = RACI_COLUMNAS.index(perfil["raci"])
    return [(nombre, papeles[i]) for nombre, papeles in RACI]
