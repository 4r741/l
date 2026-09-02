#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera instrumentos/captura.html: la hoja de captura, en el navegador.

    python3 build-captura.py

Mismo contenido y mismos cálculos que el libro de build-libro.py, pero se
rellena en el navegador y se guarda en el almacenamiento local del equipo.
Reutiliza el sistema de diseño del Manual Maestro.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).parent

# La versión no se teclea: sale de version.py, que es el único sitio donde vive.
_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA, CORTA = _v["VERSION"], _v["FECHA"], _v["CORTA"]


def sello(t):
    """Estampa la versión vigente en el documento antes de escribirlo.

    Los archivos fuente llevan @VERSION@ y @FECHA@ en vez del número, de modo
    que subir de versión sea cambiar una línea de version.py y no catorce
    archivos con catorce oportunidades de olvidarse de uno.
    """
    t = t.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA).replace("@CORTA@", CORTA)
    assert "@VERSION@" not in t and "@FECHA@" not in t
    return t



CSS = """
/* ---------------------------------------------------------------------------
   La portada del instrumento. Antes decía «el Plan de Dirección declara que el
   centro no tiene todavía sus cinco números ni serie propia en ninguno de los
   diez indicadores»: cierto, y sin embargo ilegible para quien no se sepa ya
   de memoria qué son esos cinco números y esos diez indicadores. Ahora lo
   primero que se lee es qué es esto, quién lo rellena, cuándo, qué hay que
   teclear y qué sale.
   --------------------------------------------------------------------------- */
.quees{
  display:grid;gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:var(--radio);overflow:hidden;
  margin-top:2rem;
}
@media(min-width:720px){.quees{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(min-width:1120px){.quees{grid-template-columns:repeat(3,minmax(0,1fr))}}
.quees__c{background:var(--surface);padding:1.25rem 1.35rem 1.35rem;min-width:0}
.quees__c .eyebrow{margin:0 0 .5rem}
.quees__c p{margin:0;font-size:.92rem;line-height:1.55;color:var(--ink-2)}

.ruta{margin-top:2rem;border-top:1px solid var(--line);padding-top:1.4rem}
.ruta>.eyebrow{margin:0 0 1rem}
.ruta ol{list-style:none;margin:0;padding:0;display:grid;gap:.85rem}
@media(min-width:900px){.ruta ol{grid-template-columns:repeat(4,minmax(0,1fr));gap:1.6rem}}
.ruta li{display:grid;grid-template-columns:2rem minmax(0,1fr);align-items:start;gap:.2rem}
.ruta b{
  font-family:var(--f-mono);font-size:.78rem;font-weight:500;color:#fff;
  background:var(--accent);width:1.5rem;height:1.5rem;border-radius:999px;
  display:grid;place-items:center;
}
.ruta span{font-size:.9rem;line-height:1.5;color:var(--ink-2)}
.ruta a{color:var(--accent-ink)}

/* ============================================================
   HOJA DE CAPTURA — mismo sistema de diseño, con celdas que se
   rellenan en el navegador y se guardan en el propio equipo.
   ============================================================ */
.cap__meses{
  display:flex;flex-wrap:wrap;gap:2px;margin:1.2rem 0 1.4rem;
  border:1px solid var(--line);padding:4px;background:var(--surface);
}
.cap__mes{
  font:inherit;font-family:var(--f-mono);font-size:.72rem;letter-spacing:.08em;
  text-transform:uppercase;background:transparent;border:0;color:var(--ink-2);
  padding:.5rem .75rem;cursor:pointer;border-bottom:2px solid transparent;
}
.cap__mes:hover{color:var(--accent-ink)}
.cap__mes[aria-selected="true"]{background:var(--paper);border-bottom-color:var(--accent);color:var(--ink)}
.cap__mes b{display:block;font-weight:400;font-size:.62rem;color:var(--muted);margin-top:.15rem}
.cap__mes[aria-selected="true"] b{color:var(--accent-ink)}

table.cap{min-width:1240px}
table.cap tbody td{vertical-align:middle}
table.cap tbody td:nth-child(2){min-width:19rem}
table.cap tbody td:nth-child(2) small{max-width:34ch}
table.anual{min-width:1180px}
table.cap input,table.cap select{
  font:inherit;font-family:var(--f-mono);font-size:.82rem;width:100%;
  border:1px solid var(--line);background:#FFFDE7;color:var(--ink);
  padding:.32rem .4rem;border-radius:2px;min-width:0;
}
table.cap input:focus,table.cap select:focus{outline:2px solid var(--accent);outline-offset:1px}
table.cap input[type=number]{text-align:right;font-variant-numeric:tabular-nums}
table.cap select{font-size:.74rem;letter-spacing:.02em}
table.cap input[readonly]{background:var(--surface);color:var(--muted)}
table.cap td.res{
  font-family:var(--f-mono);font-variant-numeric:tabular-nums;text-align:right;
  font-size:.92rem;color:var(--ink);white-space:nowrap;
}
table.cap td.est{text-align:center;white-space:nowrap}
.luz{
  display:inline-block;font-family:var(--f-mono);font-size:.64rem;letter-spacing:.09em;
  text-transform:uppercase;padding:.16rem .48rem;border-radius:3px;border:1px solid transparent;
}
.luz--verde{background:rgba(14,124,116,.14);color:var(--accent-ink);border-color:rgba(14,124,116,.3)}
.luz--ambar{background:rgba(168,99,27,.16);color:#8A5015;border-color:rgba(168,99,27,.34)}
.luz--rojo{background:rgba(168,27,27,.14);color:#8E1B1B;border-color:rgba(168,27,27,.32)}
.luz--gris{background:var(--surface-2);color:var(--muted);border-color:var(--line)}

.cap__barra{
  display:flex;flex-wrap:wrap;gap:.6rem 1rem;align-items:center;
  margin-top:1.2rem;padding-top:1rem;border-top:1px solid var(--line);
}
.cap__barra p{font-size:.82rem;color:var(--muted);margin-right:auto}
.boton{
  font:inherit;font-family:var(--f-mono);font-size:.68rem;letter-spacing:.1em;
  text-transform:uppercase;background:transparent;border:1px solid var(--line);
  color:var(--ink-2);padding:.42rem .85rem;border-radius:999px;cursor:pointer;
}
.boton:hover{border-color:var(--accent);color:var(--accent-ink)}
.boton--riesgo:hover{border-color:#8E1B1B;color:#8E1B1B}

/* resumen anual */
table.anual{font-size:.8rem}
table.anual td.v{
  font-family:var(--f-mono);font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap;
}
table.anual td.vacio{color:var(--muted);text-align:center}
.tend{font-family:var(--f-mono);font-size:.66rem;letter-spacing:.08em;text-transform:uppercase}
.tend--sube{color:var(--accent-ink)}
.tend--baja{color:#8E1B1B}
.tend--igual{color:var(--muted)}

/* los cinco números */
.cinco{display:grid;gap:1px;background:var(--line);border:1px solid var(--line);margin-top:1.4rem}
@media(min-width:900px){.cinco{grid-template-columns:repeat(5,minmax(0,1fr))}}
.cinco__caja{background:var(--paper);padding:1.15rem 1.2rem}
.cinco__caja i{
  display:block;font-style:normal;font-family:var(--f-mono);font-size:.62rem;
  letter-spacing:.13em;text-transform:uppercase;color:var(--muted);
}
.cinco__caja b{
  display:block;margin-top:.4rem;font-family:var(--f-display);font-weight:400;
  font-size:clamp(1.5rem,1.2rem + 1.3vw,2.2rem);line-height:1;letter-spacing:-.02em;
  color:var(--accent-ink);font-variation-settings:"opsz" 144;
}
.cinco__caja b.pend{color:var(--muted);font-size:1.05rem;font-style:italic}
.cinco__caja p{margin-top:.55rem;font-size:.8rem;color:var(--ink-2);line-height:1.45}

.entradas{display:grid;gap:1px;background:var(--line);border:1px solid var(--line);margin-top:1.2rem}
@media(min-width:760px){.entradas{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(min-width:1080px){.entradas{grid-template-columns:repeat(4,minmax(0,1fr))}}
.entradas>div{background:var(--paper);padding:.9rem 1rem;min-width:0}
.entradas label{display:block;font-family:var(--f-mono);font-size:.62rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);margin-bottom:.4rem}
.entradas input{
  font:inherit;font-family:var(--f-mono);font-size:.9rem;width:100%;text-align:right;
  border:1px solid var(--line);background:#FFFDE7;padding:.35rem .5rem;border-radius:2px;
  font-variant-numeric:tabular-nums;
}
.entradas small{display:block;margin-top:.4rem;font-size:.74rem;color:var(--muted);line-height:1.4}

@media print{
  .cap__meses,.cap__barra,.boton{display:none}
  table.cap input,table.cap select{border:0;background:#fff;padding:0}
  .luz{border:1px solid #999}
  .cinco__caja,.entradas>div{background:#fff}
  .seccion-mes{break-before:page}
}
"""

manual = (RAIZ / "manual.html").read_text(encoding="utf-8")
i = manual.index("<body>")
cabecera = manual[:i + len("<body>")]
cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                            "<title>Los números del centro · Giraldo</title>")
cabecera = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="Hoja de captura de la línea base del Centro de '
                  'Excelencia Implantológica Giraldo: doce meses, diez indicadores con definición '
                  'operativa, semáforo automático, resumen anual y los cinco números.">',
                  cabecera, count=1)
k = cabecera.rindex("</style>")
cabecera = cabecera[:k] + CSS + "\n" + cabecera[k:]

# ---------------------------------------------------------------- configuración
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

IND = [
 dict(n=1, nombre="Verificaciones regulatorias cerradas",
      num="Verificaciones V1–V11 con evidencia archivada y fechada", den="11 (fijo)", denfijo=11,
      fmt="pct", sentido="mayor", verde=1.0, ambar=0.8, publicado="11 de 11",
      fuente="Expediente de verificaciones externas",
      fuera="Nada: una verificación «en trámite» cuenta como no cerrada"),
 dict(n=2, nombre="Bajas voluntarias del equipo",
      num="Ceses a instancia de la persona trabajadora", den="Plantilla media del mes",
      fmt="pct1", sentido="menor", verde=0.0, ambar=0.05, publicado="0",
      fuente="Registro laboral",
      fuera="Fin de contrato temporal ya previsto e incapacidades temporales"),
 dict(n=3, nombre="Reclamaciones de pacientes heredados",
      num="Reclamaciones formales del mes", den=None,
      fmt="ent", sentido="menor", verde=0.0, ambar=1.0, publicado="0",
      fuente="Registro de incidencias",
      fuera="Quejas verbales resueltas en el acto y registradas como incidencia de nivel 1"),
 dict(n=4, nombre="Documentación digitalizada el mismo día",
      num="Actos con historia, consentimiento e imágenes en el día", den="Actos clínicos del día",
      fmt="pct", sentido="mayor", verde=0.98, ambar=0.90, publicado="100 %",
      fuente="Gestor de clínica", fuera="Nada"),
 dict(n=5, nombre="Producto pendiente",
      num="Importe aceptado y no terminado a fin de mes", den=None,
      fmt="eur", sentido="descendente", verde=0.0, ambar=0.0, publicado="Descendente",
      fuente="Informe de tratamientos abiertos",
      fuera="Presupuestos presentados y no aceptados"),
 dict(n=6, nombre="Tasa de conversión de la primera visita",
      num="PV del mes aceptadas y pagadas dentro de 60 días", den="Primeras visitas del mes",
      fmt="pct1", sentido="mayor", verde=0.45, ambar=0.35, publicado="Línea base y mejora",
      fuente="Agenda y presupuestos, cruzados",
      fuera="Urgencias, segundas opiniones y derivaciones a otro centro por criterio clínico"),
 dict(n=7, nombre="Pacientes en mantenimiento activo",
      num="Con revisión en 12 meses y próxima cita agendada", den="Pacientes con implantes del centro",
      fmt="pct1", sentido="mayor", verde=0.60, ambar=0.40, publicado="Creciente",
      fuente="Gestor de clínica",
      fuera="Pacientes con cita agendada pero sin ninguna asistencia en 12 meses"),
 dict(n=8, nombre="Captación por recomendación",
      num="PV cuyo origen declarado es la recomendación", den="Primeras visitas del mes",
      fmt="pct1", sentido="mayor", verde=0.30, ambar=0.20, publicado="Creciente",
      fuente="Campo obligatorio de origen en la ficha",
      fuera="Nada: el origen «no consta» permanece en el denominador"),
 dict(n=9, nombre="Ofrecimiento del programa de cuidado",
      num="Cierres con el ofrecimiento registrado", den="Cierres de tratamiento del mes",
      fmt="pct1", sentido="mayor", verde=0.90, ambar=0.80, publicado="90 %",
      fuente="Punto de verificación del cierre",
      fuera="Nada: se mide el ofrecimiento, no la contratación"),
 dict(n=10, nombre="Auditorías ejecutadas en fecha",
      num="Auditorías realizadas con resultado registrado", den="Auditorías programadas",
      fmt="pct", sentido="mayor", verde=1.0, ambar=0.5, publicado="100 %",
      fuente="Calendario de auditoría",
      fuera="Nada: una auditoría sin registro cuenta como no realizada"),
]

ENTRADAS = [
 ("costes", "Costes fijos mensuales", "€", "Nóminas, alquiler, suministros, seguros, cuotas y amortizaciones. Día 15.", ""),
 ("margen", "Margen de contribución", "%", "Supuesto de trabajo del apartado 18 mientras no haya escandallo propio.", "40"),
 ("ticket", "Ticket medio del caso aceptado", "€", "Supuesto de trabajo del apartado 18. Se sustituye por el real.", "1800"),
 ("conversion", "Tasa de conversión", "%", "Enlaza con el indicador 6 en cuanto haya tres meses de serie.", "45"),
 ("dias", "Días laborables al mes", "d", "Parámetro de capacidad.", "21"),
 ("tesoreria", "Tesorería disponible", "€", "Saldo libre de compromisos a fecha de corte. Día 21.", ""),
 ("pendiente", "Producto pendiente heredado", "€", "Importe cobrado o comprometido y no ejecutado. Día 15.", ""),
]

# ---------------------------------------------------------------- cuerpo
def tabla_definiciones():
    filas = []
    for d in IND:
        filas.append(
         '<tr><td class="num">{n}</td><td><strong>{nombre}</strong></td><td>{num}</td>'
         '<td>{den}</td><td>{fuente}</td><td>{fuera}</td>'
         '<td class="num"><input type="number" step="0.01" data-umbral="verde" data-ind="{n}" '
         'aria-label="Umbral verde del indicador {n}"></td>'
         '<td class="num"><input type="number" step="0.01" data-umbral="ambar" data-ind="{n}" '
         'aria-label="Umbral ámbar del indicador {n}"></td></tr>'
         .format(n=d["n"], nombre=d["nombre"], num=d["num"], den=d["den"] or "—",
                 fuente=d["fuente"], fuera=d["fuera"]))
    return "\n          ".join(filas)


def filas_captura():
    filas = []
    for d in IND:
        if d["den"] is None:
            den = '<td class="num" style="text-align:center;color:var(--muted)">—</td>'
        elif d.get("denfijo"):
            den = '<td class="num" style="text-align:right;color:var(--muted)">%d</td>' % d["denfijo"]
        else:
            den = ('<td><input type="number" min="0" step="any" data-campo="d" data-ind="%d" '
                   'aria-label="Denominador del indicador %d"></td>' % (d["n"], d["n"]))
        filas.append(
         '<tr data-fila="{n}"><td class="num">{n}</td><td><strong>{nombre}</strong>'
         '<small style="display:block;color:var(--muted);font-size:.78rem;margin-top:.15rem">{num}</small></td>'
         '<td><input type="number" min="0" step="any" data-campo="n" data-ind="{n}" '
         'aria-label="Numerador del indicador {n}"></td>'
         '{den}'
         '<td class="res" data-salida="res"></td>'
         '<td style="white-space:nowrap;color:var(--muted);font-size:.82rem">{pub}</td>'
         '<td class="est" data-salida="luz"></td>'
         '<td><select data-campo="estado" data-ind="{n}" aria-label="Estado del dato del indicador {n}">'
         '<option value=""></option><option>Definitivo</option><option>Provisional</option>'
         '<option>Estimado</option></select></td>'
         '<td><input type="text" data-campo="nota" data-ind="{n}" aria-label="Notas del indicador {n}"></td></tr>'
         .format(n=d["n"], nombre=d["nombre"], num=d["num"], den=den, pub=d["publicado"]))
    return "\n          ".join(filas)


def filas_anual():
    filas = []
    for d in IND:
        celdas = "".join('<td class="v" data-anual="%d" data-mes="%d"></td>' % (d["n"], m)
                         for m in range(12))
        filas.append(
         '<tr><td class="num">{n}</td><td>{nombre}</td>{celdas}'
         '<td class="v" data-res="meses" data-ind="{n}"></td>'
         '<td class="v" data-res="primero" data-ind="{n}"></td>'
         '<td class="v" data-res="ultimo" data-ind="{n}"></td>'
         '<td data-res="tend" data-ind="{n}"></td></tr>'
         .format(n=d["n"], nombre=d["nombre"], celdas=celdas))
    return "\n          ".join(filas)


def cajas_entradas():
    return "\n        ".join(
     '<div><label for="e-{c}">{r} <span style="color:var(--accent-ink)">{u}</span></label>'
     '<input id="e-{c}" type="number" step="any" data-entrada="{c}" value="{v}">'
     '<small>{n}</small></div>'.format(c=c, r=r, u=u, n=n, v=v)
     for c, r, u, n, v in ENTRADAS)


BOTONES_MES = "\n        ".join(
 '<button class="cap__mes" type="button" role="tab" data-mes="%d" aria-selected="%s">%s<b>%02d</b></button>'
 % (m, "true" if m == 0 else "false", MESES[m][:3], m + 1) for m in range(12))

CUERPO = ("""
<header class="topbar">
  <div class="wrap">
    <div class="topbar__in">
      <a class="brand" href="#portada">
        <span class="brand__mark">Los números del <b>centro</b></span>
        <span class="brand__tag">2026 · v@VERSION@</span>
      </a>
      <a class="crosslink" href="../memoria.html">Plan de Dirección</a>
      <a class="crosslink" href="../manual.html">Manual Maestro</a>
      <a class="crosslink" href="../index.html">Protocolo</a>
    </div>
    <nav class="strip" aria-label="Índice"></nav>
  </div>
</header>

<main class="captura-raiz">

<div class="printhead" aria-hidden="true"><b>Los números del centro · 2026 · v@VERSION@</b><span>Centro de Excelencia Implantológica Giraldo · Uso interno · Confidencial</span></div>

<section class="hero" id="portada">
  <div class="wrap">
    <p class="eyebrow">Instrumento de medición · Ejercicio 2026 · Uso interno</p>
    <h1>Los números del <em>centro</em></h1>
    <p class="hero__lede">Un cuaderno donde se apunta, mes a mes, lo que de verdad pasa en la clínica. Diez cosas que se cuentan y siete datos de contabilidad. Con eso, la hoja calcula sola los cinco números que la Junta necesita para decidir con hechos en vez de con impresiones.</p>

    <div class="quees">
      <div class="quees__c">
        <p class="eyebrow">Por qué existe</p>
        <p>Hoy el centro no tiene ni un solo mes medido. Todas las cifras económicas del Plan de Dirección son <strong>modelos sobre rangos del sector</strong>, no datos propios. Mientras siga así, cualquier objetivo comercial es una opinión bien argumentada. Esta hoja es la que convierte la opinión en dato.</p>
      </div>
      <div class="quees__c">
        <p class="eyebrow">Quién la rellena y cuándo</p>
        <p>Gerencia, <strong>una vez al mes</strong>, entre el día 15 y el 21. Se tarda unos veinte minutos: casi todo sale del gestor de clínica y de la contabilidad del mes. Hay doce hojas, una por mes del año.</p>
      </div>
      <div class="quees__c">
        <p class="eyebrow">Qué hay que teclear</p>
        <p>Solo las casillas amarillas. <strong>Diez indicadores</strong> —cuántos, sobre cuántos— y <strong>siete entradas</strong> de dinero y capacidad. El resultado, el semáforo de color, el resumen del año y la tendencia se calculan solos.</p>
      </div>
      <div class="quees__c">
        <p class="eyebrow">Qué sale de aquí</p>
        <p>Los <strong>cinco números</strong>: lo que cuesta tener el centro abierto, cuánto hay que facturar para no perder dinero, cuántas primeras visitas al día hacen falta para llegar ahí, cuánto trabajo cobrado queda por hacer y cuántos meses aguanta el centro sin ingresar nada.</p>
      </div>
      <div class="quees__c">
        <p class="eyebrow">Dónde se guarda</p>
        <p>En este mismo ordenador, dentro del navegador. <strong>No se envía nada a ningún sitio</strong> y no lo ve nadie más. Tampoco se sincroniza: para llevárselo a otro equipo hay que usar «Guardar copia» y «Cargar copia».</p>
      </div>
      <div class="quees__c">
        <p class="eyebrow">La regla que no se salta</p>
        <p>Un hueco se declara. Si un mes falta un dato, la casilla dice <strong>SIN DATO</strong> y cuenta como roja; los cinco números dicen <strong>pendiente</strong> en vez de dar una cifra inventada. Un número inventado es peor que un hueco reconocido.</p>
      </div>
    </div>

    <div class="ruta">
      <p class="eyebrow">De arriba abajo, este es el recorrido</p>
      <ol>
        <li><b>1</b><span>Se leen las <a href="#definiciones">definiciones</a>: qué cuenta y qué no cuenta en cada indicador, para que un mes se mida igual que el siguiente.</span></li>
        <li><b>2</b><span>Cada mes se rellena su <a href="#captura">hoja</a>: diez numeradores, diez denominadores y una nota de estado.</span></li>
        <li><b>3</b><span>El <a href="#anual">resumen anual</a> junta los doce meses en una rejilla y enseña la tendencia sin que nadie la calcule.</span></li>
        <li><b>4</b><span>Con las siete entradas de contabilidad salen <a href="#cinco">los cinco números</a>, que son los que van a la Junta.</span></li>
      </ol>
    </div>
  </div>
</section>
<div class="wrap"><div class="ticks ticks--tall" aria-hidden="true"></div></div>

<section class="section" id="instrucciones">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Cómo se usa</p>
      <h2>Tres reglas y ninguna más</h2>
    </div>
    <div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr))">
      <div class="card"><p class="eyebrow">Regla 1</p><h3>Solo se teclea lo amarillo</h3><p>Numeradores, denominadores y las siete entradas de los cinco números. El resultado, el semáforo, el resumen anual y la tendencia se calculan solos.</p></div>
      <div class="card"><p class="eyebrow">Regla 2</p><h3>Sin dato es rojo</h3><p>No se deja en blanco ni se sustituye por una impresión. Mientras no haya cifra, la casilla dice SIN DATO y cuenta como roja en la revisión de Junta.</p></div>
      <div class="card"><p class="eyebrow">Regla 3</p><h3>El 6 nace provisional</h3><p>La conversión tiene cohorte cerrada a sesenta días: el dato de un mes no es definitivo hasta dos meses después. Se marca en «Estado del dato» y se corrige en la revisión siguiente.</p></div>
    </div>
    <div class="callout" style="max-width:none">
      <p class="eyebrow">Dónde vive lo que escribe</p>
      <p>En el almacenamiento local de este navegador y de este equipo. No viaja a ningún servidor y no lo ve nadie más, pero tampoco se sincroniza: si abre el archivo en otro ordenador, empieza vacío. Para llevárselo, use <strong>Guardar copia</strong> —descarga un archivo con todo lo introducido— y <strong>Cargar copia</strong> en el otro equipo. Para el acta, <strong>Imprimir</strong> saca las doce hojas y el resumen en papel.</p>
    </div>
  </div>
</section>

<section class="section" id="definiciones" data-def>
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Definiciones</p>
      <h2>Qué se cuenta arriba, qué se cuenta abajo</h2>
      <p>Un indicador sin definición operativa no se puede medir dos meses seguidos de la misma manera. Los umbrales de las dos últimas columnas son <strong>supuestos de trabajo</strong>, no objetivos aprobados: se cambian aquí una sola vez y los recogen las doce hojas.</p>
    </div>
    <div class="tablewrap">
      <table>
        <thead><tr><th>#</th><th>Indicador</th><th>Numerador</th><th>Denominador</th><th>Fuente</th><th>Qué queda fuera</th><th>Verde si</th><th>Ámbar si</th></tr></thead>
        <tbody>
          @@DEFINICIONES@@
        </tbody>
      </table>
    </div>
    <div class="cap__barra">
      <p>Los umbrales se expresan en la misma unidad que el resultado: 0,45 significa 45 %.</p>
      <button class="boton" type="button" data-cap="umbrales-defecto">Restaurar umbrales de origen</button>
    </div>
  </div>
</section>

<section class="section seccion-mes" id="captura">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Captura mensual</p>
      <h2>Una hoja por mes</h2>
      <p>Elija el mes y rellene lo amarillo. Lo introducido se guarda al momento.</p>
    </div>
    <div class="cap__meses" role="tablist" aria-label="Mes">
        @@MESES@@
    </div>
    <div class="tablewrap">
      <table class="cap">
        <thead><tr><th>#</th><th>Indicador</th><th style="width:7.5rem">Numerador</th><th style="width:7.5rem">Denominador</th><th>Resultado</th><th>Umbral</th><th>Estado</th><th style="width:10.5rem">Estado del dato</th><th style="min-width:14rem">Notas</th></tr></thead>
        <tbody data-cap="cuerpo">
          @@CAPTURA@@
        </tbody>
      </table>
    </div>
    <div class="cap__barra">
      <p data-cap="aviso">El indicador 5 se compara con el mes anterior: su sentido es «descendente», no un umbral fijo.</p>
      <button class="boton" type="button" data-cap="guardar">Guardar copia</button>
      <button class="boton" type="button" data-cap="cargar">Cargar copia</button>
      <button class="boton" type="button" data-cap="imprimir">Imprimir</button>
      <button class="boton boton--riesgo" type="button" data-cap="vaciar">Vaciar todo</button>
      <input type="file" data-cap="fichero" accept="application/json,.json" hidden>
    </div>
  </div>
</section>

<section class="section" id="anual">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Resumen anual</p>
      <h2>Los doce meses en una rejilla</h2>
      <p><strong>Meses con dato</strong> es la medida honesta de cuánto se sabe realmente. La Junta debe exigir que llegue a doce.</p>
    </div>
    <div class="tablewrap">
      <table class="anual">
        <thead><tr><th>#</th><th style="min-width:15rem">Indicador</th>@@CABMESES@@<th>Meses</th><th>Primero</th><th>Último</th><th>Tendencia</th></tr></thead>
        <tbody id="cuerpo-anual">
          @@ANUAL@@
        </tbody>
      </table>
    </div>
    <p class="footnote">El indicador 5 mide euros: su tendencia «Mejora» significa que el producto pendiente baja.</p>
  </div>
</section>

<section class="section" id="cinco">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Los cinco números</p>
      <h2>Sin ellos, cualquier objetivo comercial es una opinión</h2>
      <p>Siete entradas y cinco resultados. Mientras falte una entrada, el resultado dice «pendiente»: un número inventado es peor que un hueco declarado.</p>
    </div>
    <div class="entradas">
        @@ENTRADAS@@
        <div style="background:var(--surface)"><label>Naturaleza de lo precargado</label>
          <small style="margin-top:0">Margen, ticket, conversión y días vienen con los supuestos de trabajo del apartado 18, que <strong>no son mediciones del centro</strong>. Sustitúyanse por los reales en cuanto existan; las otras tres casillas nacen vacías porque solo pueden salir de la contabilidad.</small></div>
    </div>
    <div class="cinco">
      <div class="cinco__caja"><i>1 · Costes fijos mensuales</i><b data-cinco="costes">pendiente</b><p>El primero de los cinco. Sin él no hay ninguno de los demás.</p></div>
      <div class="cinco__caja"><i>2 · Punto de equilibrio mensual</i><b data-cinco="equilibrio">pendiente</b><p>Facturación mensual necesaria para cubrir los costes fijos, dado el margen de contribución.</p></div>
      <div class="cinco__caja"><i>3 · Primeras visitas al día</i><b data-cinco="pvdia">pendiente</b><p>Cuántas hacen falta para llegar al equilibrio con la conversión y el ticket actuales.</p></div>
      <div class="cinco__caja"><i>4 · Producto pendiente heredado</i><b data-cinco="pendiente">pendiente</b><p>Caja ya cobrada que hay que convertir en producción. Es la palanca 1 del apartado 14.</p></div>
      <div class="cinco__caja"><i>5 · Meses de colchón</i><b data-cinco="colchon">pendiente</b><p>Cuánto aguanta el centro sin ingresar nada. Por debajo de tres, es riesgo de Junta.</p></div>
    </div>
    <div class="rulebox" style="max-width:none">
      <p class="eyebrow">La cifra que más incomoda</p>
      <p data-cap="lectura-pv">Las primeras visitas necesarias al día se comparan con la capacidad real de la agenda. Si salen más de las que caben, el problema no es comercial: es de conversión o de ticket.</p>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <div class="ticks" aria-hidden="true" style="margin-bottom:2rem"></div>
    <div class="foot__grid">
      <div>
        <p><strong>Centro de Excelencia Implantológica Giraldo</strong><br>Los números del centro · Ejercicio 2026</p>
        <p style="margin-top:.8rem">Documento de uso interno. Los datos se guardan únicamente en este equipo.</p>
      </div>
      <div><p class="eyebrow">Instrumento de</p><p>apartado 7 · Línea base<br>apartado 13 · Cuadro de mando</p></div>
      <div><p class="eyebrow">Documentos de referencia</p><p>Plan de Dirección v@VERSION@<br>Manual Maestro v@VERSION@<br>Protocolo de Primera Visita v@VERSION@</p></div>
    </div>
  </div>
</footer>
""".replace("@@DEFINICIONES@@", tabla_definiciones())
     .replace("@@MESES@@", BOTONES_MES)
     .replace("@@CAPTURA@@", filas_captura())
     .replace("@@ANUAL@@", filas_anual())
     .replace("@@ENTRADAS@@", cajas_entradas())
     .replace("@@CABMESES@@", "".join("<th>%s</th>" % m[:3] for m in MESES)))

JS = ("""<script>
(function(){
  "use strict";

  /* ---- por dónde sigue una tira que se desplaza ---- */
  (function(){
    if(window.__TIRAS__) return; window.__TIRAS__ = 1;
    var tiras = [].slice.call(document.querySelectorAll(".strip,.strip--nota,.cabecera__docs"));
    if(!tiras.length) return;
    function estado(t){
      var mas = t.scrollWidth - t.clientWidth;
      t.classList.toggle("hay-izq", mas > 2 && t.scrollLeft > 2);
      t.classList.toggle("hay-der", mas > 2 && t.scrollLeft < mas - 2);
    }
    tiras.forEach(function(t){
      estado(t);
      t.addEventListener("scroll", function(){ estado(t); }, {passive:true});
      if("ResizeObserver" in window) new ResizeObserver(function(){ estado(t); }).observe(t);
    });
    window.addEventListener("resize", function(){ tiras.forEach(estado); });
    /* al conmutar de documento la tira cambia de contenido sin que nada haga
       scroll: hay que volver a mirarla */
    document.addEventListener("click", function(){ setTimeout(function(){ tiras.forEach(estado); }, 60); }, true);
  })();


  /* ---- saltar al contenido ---- */
  (function(){
    if(document.querySelector(".saltar")) return;
    var a = document.createElement("a");
    a.className = "saltar";
    a.href = "#";
    a.textContent = "Saltar al contenido";
    function cuerpo(){
      var todos = [].slice.call(document.querySelectorAll("main"));
      for(var i = 0; i < todos.length; i++){
        if(todos[i].getBoundingClientRect().height > 0) return todos[i];
      }
      return todos[0] || null;
    }
    /* El destino se calcula al enfocar y no al cargar: en el archivo único el
       documento visible cambia, y con él el contenido al que hay que saltar. */
    a.addEventListener("focus", function(){
      var m = cuerpo();
      /* Si el contenido no tiene identificador se le pone uno, para que el
         enlace sea un enlace de verdad y no un «#» que solo funciona con
         guion. */
      if(m && !m.id) m.id = "contenido";
      a.href = (m && m.id) ? "#" + m.id : "#";
    });
    a.addEventListener("click", function(e){
      var m = cuerpo();
      if(!m) return;
      e.preventDefault();
      m.setAttribute("tabindex", "-1");
      m.focus();
      m.scrollIntoView({behavior:"instant", block:"start"});
    });
    document.body.insertBefore(a, document.body.firstChild);
  })();

  /* ---- una tabla ancha se recorre también con el teclado ---- */
  (function(){
    if(window.__TABLAS__) return; window.__TABLAS__ = 1;
    function limpio(el){
      return el ? el.textContent.trim().replace(/\s+/g, " ").slice(0, 70) : "";
    }
    function titulo(t){
      /* Lo más cercano por encima: primero los hermanos anteriores, que es donde
         suele estar el titular de la tabla; si no, el titular del apartado que
         la contiene. Una tabla anunciada solo como «tabla desplazable» no dice
         de qué es, y en Otros documentos hay veintiuna. */
      var n = t.previousElementSibling, saltos = 0;
      while(n && saltos < 5){
        if(/^H[2-5]$/.test(n.tagName)) return limpio(n);
        var h = n.querySelector && n.querySelector("h2,h3,h4,h5");
        if(h) return limpio(h);
        n = n.previousElementSibling; saltos++;
      }
      var caja = t.closest("section,article,.phase,.section");
      while(caja){
        var d = caja.querySelector("h2,h3,h4");
        if(d) return limpio(d);
        caja = caja.parentElement && caja.parentElement.closest("section,article");
      }
      return "";
    }
    function repasar(){
      [].slice.call(document.querySelectorAll(".tablewrap")).forEach(function(t){
        var ancha = t.scrollWidth > t.clientWidth + 2;
        if(ancha && !t.hasAttribute("tabindex")){
          t.setAttribute("tabindex", "0");
          t.setAttribute("role", "region");
          var q = titulo(t);
          t.setAttribute("aria-label", q ? "Tabla desplazable: " + q : "Tabla desplazable");
        } else if(!ancha && t.hasAttribute("tabindex")){
          t.removeAttribute("tabindex"); t.removeAttribute("role"); t.removeAttribute("aria-label");
        }
      });
    }
    repasar();
    window.addEventListener("resize", repasar);
    window.addEventListener("load", repasar);
    document.addEventListener("click", function(){ setTimeout(repasar, 80); }, true);
  })();


  /* ---- mapa del documento ---- */
  (function(){
    if(window.__MAPA__) return; window.__MAPA__ = 1;

    function construye(raiz, tira){
      var enlaces = [].slice.call(tira.querySelectorAll("a[href^='#']"));
      /* Con pocos apartados el mapa no aporta: la tira ya los enseña todos. */
      if(enlaces.length < 6) return null;
      var destinos = [];
      enlaces.forEach(function(a){
        var d = document.getElementById(a.getAttribute("href").slice(1));
        if(d) destinos.push({a:a, d:d, r:a.textContent.trim()});
      });
      if(destinos.length < 6) return null;

      var mapa = document.createElement("nav");
      mapa.className = "mapa";
      mapa.setAttribute("aria-label", "Mapa del documento");
      destinos.forEach(function(x, i){
        var b = document.createElement("button");
        b.type = "button";
        b.className = "mapa__m";
        b.dataset.i = String(i);
        b.setAttribute("aria-label", "Ir a " + x.r);
        var r = document.createElement("span");
        r.className = "mapa__r";
        r.textContent = x.r;
        b.appendChild(r);
        mapa.appendChild(b);
        x.b = b;
      });
      document.body.appendChild(mapa);
      return {mapa:mapa, destinos:destinos};
    }

    /* La altura de cada marca es la que ocupa su apartado, con un mínimo para
       que los cortos sigan siendo pulsables. */
    function reparte(m){
      var alto = m.mapa.clientHeight - (m.destinos.length - 1) * 2;
      var tramos = m.destinos.map(function(x, i){
        var fin = (i + 1 < m.destinos.length)
          ? m.destinos[i + 1].d.getBoundingClientRect().top + window.scrollY
          : document.documentElement.scrollHeight;
        return Math.max(1, fin - (x.d.getBoundingClientRect().top + window.scrollY));
      });
      var suma = tramos.reduce(function(a, b){ return a + b; }, 0) || 1;
      m.destinos.forEach(function(x, i){
        x.b.style.height = Math.max(9, Math.round(alto * tramos[i] / suma)) + "px";
      });
    }

    var estado = null;
    function arranca(){
      /* Dentro del archivo único solo vale la tira del documento que está
         abierto. Si ese documento no tiene tira —la portada y la presentación no
         la tienen—, no hay mapa: cayendo al primer `.strip` que apareciera se
         dibujaba el mapa de otro documento encima del que se está leyendo. */
      var tira = document.querySelector(".cabecera")
        ? document.querySelector(".cabecera .strip:not([hidden]):not(.strip--nota)")
        : (document.querySelector("#strip") || document.querySelector(".strip:not(.strip--nota)"));
      if(estado){ estado.mapa.remove(); estado = null; }
      if(!tira) return;
      estado = construye(document, tira);
      if(!estado) return;
      var m = estado;
      m.mapa.addEventListener("click", function(e){
        var b = e.target.closest(".mapa__m");
        if(!b) return;
        var x = m.destinos[+b.dataset.i];
        if(x) x.d.scrollIntoView({behavior:"instant", block:"start"});
      });
      reparte(m);
      window.addEventListener("resize", function(){ reparte(m); });
      marca();
    }

    function marca(){
      if(!estado) return;
      var y = window.scrollY + window.innerHeight * 0.35, actual = 0;
      estado.destinos.forEach(function(x, i){
        if(x.d.getBoundingClientRect().top + window.scrollY <= y) actual = i;
      });
      estado.destinos.forEach(function(x, i){
        x.b.setAttribute("aria-current", String(i === actual));
      });
    }
    window.addEventListener("scroll", marca, {passive:true});

    arranca();
    window.addEventListener("load", function(){ if(estado) reparte(estado); });
    /* En el archivo único el documento visible cambia y con él su mapa. */
    document.addEventListener("click", function(e){
      if(e.target.closest("[data-ir-a]")) setTimeout(arranca, 120);
    }, true);
  })();

  /* ---- volver arriba ---- */
  (function(){
    if(document.querySelector(".volver")) return;
    var quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var caja = document.createElement("div");
    caja.className = "volver";
    function boton(rotulo, etiqueta, dibujo){
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", etiqueta);
      b.innerHTML = dibujo + "<span>" + rotulo + "</span>";
      caja.appendChild(b);
      return b;
    }
    var FLECHA = '<svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true">' +
      '<path d="M6 10.5V2M6 2 2.2 5.8M6 2l3.8 3.8" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var LISTA = '<svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true">' +
      '<path d="M1.6 2.5h8.8M1.6 6h8.8M1.6 9.5h5.6" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round"/></svg>';
    boton("Arriba", "Volver al principio del documento", FLECHA)
      .addEventListener("click", function(){
        window.scrollTo({top:0, behavior: quieto ? "auto" : "smooth"});
      });
    document.body.appendChild(caja);
    var visible = false;
    function mirar(){
      var debe = window.scrollY > window.innerHeight * 1.2;
      if(debe !== visible){ visible = debe; caja.classList.toggle("se-ve", debe); }
    }
    mirar();
    window.addEventListener("scroll", mirar, {passive:true});
    window.addEventListener("resize", mirar);
  })();

  var IND = @@IND@@;
  var MESES = @@MESESJS@@;
  var LLAVE = "giraldo-captura-2026";

  var estado = leer();

  function leer(){
    var vacio = {umbrales:{}, meses:{}, entradas:{}};
    try {
      var crudo = localStorage.getItem(LLAVE);
      if(!crudo) return vacio;
      var d = JSON.parse(crudo);
      return {umbrales:d.umbrales||{}, meses:d.meses||{}, entradas:d.entradas||{}};
    } catch(e){ return vacio; }
  }
  function escribir(){
    try { localStorage.setItem(LLAVE, JSON.stringify(estado)); } catch(e){}
  }
  function def(i){ return IND.filter(function(d){ return d.n === i; })[0]; }
  function celda(mes, i){
    var m = estado.meses[mes] || (estado.meses[mes] = {});
    return m[i] || (m[i] = {});
  }
  function umbral(i, cual){
    var u = estado.umbrales[i];
    if(u && u[cual] !== undefined && u[cual] !== "") return parseFloat(u[cual]);
    return def(i)[cual];
  }

  // ---------- cálculo ----------
  function resultado(mes, i){
    var d = def(i), c = celda(mes, i);
    var num = parseFloat(c.n);
    if(isNaN(num)) return null;
    if(d.den === null) return num;
    var den = d.denfijo !== undefined ? d.denfijo : parseFloat(c.d);
    if(isNaN(den) || den === 0) return null;
    return num / den;
  }
  function luz(mes, i){
    var d = def(i), v = resultado(mes, i);
    if(v === null) return {t:"Sin dato", c:"rojo"};
    if(d.sentido === "descendente"){
      if(mes === 0) return {t:"Sin referencia", c:"gris"};
      var previo = resultado(mes - 1, i);
      if(previo === null) return {t:"Sin referencia", c:"gris"};
      if(v < previo) return {t:"Baja", c:"verde"};
      if(v === previo) return {t:"Igual", c:"ambar"};
      return {t:"Sube", c:"rojo"};
    }
    var verde = umbral(i, "verde"), ambar = umbral(i, "ambar");
    if(d.sentido === "mayor"){
      if(v >= verde) return {t:"Verde", c:"verde"};
      if(v >= ambar) return {t:"Ámbar", c:"ambar"};
    } else {
      if(v <= verde) return {t:"Verde", c:"verde"};
      if(v <= ambar) return {t:"Ámbar", c:"ambar"};
    }
    return {t:"Rojo", c:"rojo"};
  }
  function formatea(v, fmt){
    if(v === null || v === undefined || isNaN(v)) return "";
    if(fmt === "pct")  return Math.round(v * 100) + " %";
    if(fmt === "pct1") return (v * 100).toFixed(1).replace(".", ",") + " %";
    if(fmt === "eur")  return mil(v) + " €";
    if(fmt === "ent")  return mil(v);
    return String(v);
  }
  function mil(n){
    return Math.round(n).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, ".");
  }

  // ---------- captura mensual ----------
  var mesActivo = 0;
  var raiz = document.currentScript && document.currentScript.parentNode.querySelector(".captura-raiz")
             || document.querySelector(".captura-raiz");
  if(!raiz) return;
  function pieza(nombre){ return raiz.querySelector('[data-cap="' + nombre + '"]'); }
  var cuerpo = pieza("cuerpo");

  function pintaMes(){
    Array.prototype.forEach.call(cuerpo.querySelectorAll("tr[data-fila]"), function(tr){
      var i = parseInt(tr.getAttribute("data-fila"), 10);
      var d = def(i), c = celda(mesActivo, i);
      tr.querySelector('[data-campo="n"]').value = c.n === undefined ? "" : c.n;
      var cd = tr.querySelector('[data-campo="d"]');
      if(cd) cd.value = c.d === undefined ? "" : c.d;
      var ce = tr.querySelector('[data-campo="estado"]');
      ce.value = c.estado || (i === 6 ? "Provisional" : "");
      tr.querySelector('[data-campo="nota"]').value = c.nota || "";
      tr.querySelector('[data-salida="res"]').textContent = formatea(resultado(mesActivo, i), d.fmt);
      var l = luz(mesActivo, i);
      tr.querySelector('[data-salida="luz"]').innerHTML =
        '<span class="luz luz--' + l.c + '">' + l.t + '</span>';
    });
  }

  cuerpo.addEventListener("input", function(ev){
    var campo = ev.target.getAttribute("data-campo");
    if(!campo) return;
    var i = parseInt(ev.target.getAttribute("data-ind"), 10);
    var c = celda(mesActivo, i);
    c[campo] = ev.target.value;
    escribir(); pintaMes(); pintaAnual(); pintaCinco();
  });
  cuerpo.addEventListener("change", function(ev){
    if(ev.target.tagName === "SELECT"){
      var i = parseInt(ev.target.getAttribute("data-ind"), 10);
      celda(mesActivo, i).estado = ev.target.value;
      escribir();
    }
  });

  var pestanas = Array.prototype.slice.call(raiz.querySelectorAll(".cap__mes"));
  pestanas.forEach(function(b){
    b.addEventListener("click", function(){
      mesActivo = parseInt(b.getAttribute("data-mes"), 10);
      pestanas.forEach(function(o){
        o.setAttribute("aria-selected", o === b ? "true" : "false");
      });
      pintaMes();
    });
  });

  // ---------- definiciones ----------
  var tablaDef = raiz.querySelector("[data-def] tbody") || raiz.querySelector("table tbody");
  function pintaUmbrales(){
    Array.prototype.forEach.call(tablaDef.querySelectorAll("[data-umbral]"), function(inp){
      var i = parseInt(inp.getAttribute("data-ind"), 10);
      inp.value = umbral(i, inp.getAttribute("data-umbral"));
    });
  }
  tablaDef.addEventListener("input", function(ev){
    var cual = ev.target.getAttribute("data-umbral");
    if(!cual) return;
    var i = ev.target.getAttribute("data-ind");
    (estado.umbrales[i] = estado.umbrales[i] || {})[cual] = ev.target.value;
    escribir(); pintaMes(); pintaAnual();
  });
  pieza("umbrales-defecto").addEventListener("click", function(){
    estado.umbrales = {}; escribir(); pintaUmbrales(); pintaMes(); pintaAnual();
  });

  // ---------- resumen anual ----------
  function pintaAnual(){
    IND.forEach(function(d){
      var serie = [];
      for(var m = 0; m < 12; m++){
        var v = resultado(m, d.n);
        serie.push(v);
        var td = raiz.querySelector('[data-anual="' + d.n + '"][data-mes="' + m + '"]');
        td.textContent = v === null ? "·" : formatea(v, d.fmt);
        td.className = v === null ? "vacio" : "v";
      }
      var conDato = serie.filter(function(v){ return v !== null; });
      var primero = conDato.length ? conDato[0] : null;
      var ultimo = conDato.length ? conDato[conDato.length - 1] : null;
      pon("meses", d.n, String(conDato.length));
      pon("primero", d.n, primero === null ? "·" : formatea(primero, d.fmt));
      pon("ultimo", d.n, ultimo === null ? "·" : formatea(ultimo, d.fmt));
      var t = raiz.querySelector('[data-res="tend"][data-ind="' + d.n + '"]');
      if(conDato.length < 2){ t.innerHTML = '<span class="tend tend--igual">—</span>'; return; }
      var mejora = d.sentido === "mayor" ? ultimo > primero : ultimo < primero;
      var igual = ultimo === primero;
      t.innerHTML = igual ? '<span class="tend tend--igual">Estable</span>'
                  : mejora ? '<span class="tend tend--sube">Mejora</span>'
                           : '<span class="tend tend--baja">Empeora</span>';
    });
  }
  function pon(cual, i, texto){
    raiz.querySelector('[data-res="' + cual + '"][data-ind="' + i + '"]').textContent = texto;
  }

  // ---------- los cinco números ----------
  var entradas = Array.prototype.slice.call(raiz.querySelectorAll("[data-entrada]"));
  entradas.forEach(function(inp){
    var c = inp.getAttribute("data-entrada");
    if(estado.entradas[c] !== undefined) inp.value = estado.entradas[c];
    else estado.entradas[c] = inp.value;
    inp.addEventListener("input", function(){
      estado.entradas[c] = inp.value; escribir(); pintaCinco();
    });
  });
  function num(c){
    var v = parseFloat(estado.entradas[c]);
    return isNaN(v) ? null : v;
  }
  function ponCinco(cual, texto, pendiente){
    var b = raiz.querySelector('[data-cinco="' + cual + '"]');
    b.textContent = texto;
    b.className = pendiente ? "pend" : "";
  }
  function pintaCinco(){
    var costes = num("costes"), margen = num("margen"), ticket = num("ticket"),
        conv = num("conversion"), dias = num("dias"), tes = num("tesoreria"), pend = num("pendiente");
    ponCinco("costes", costes === null ? "pendiente" : mil(costes) + " €", costes === null);
    var equilibrio = (costes !== null && margen) ? costes / (margen / 100) : null;
    ponCinco("equilibrio", equilibrio === null ? "pendiente" : mil(equilibrio) + " €", equilibrio === null);
    var pvdia = (equilibrio !== null && ticket && conv && dias)
              ? equilibrio / (ticket * (conv / 100)) / dias : null;
    ponCinco("pvdia", pvdia === null ? "pendiente" : pvdia.toFixed(1).replace(".", ","), pvdia === null);
    ponCinco("pendiente", pend === null ? "pendiente" : mil(pend) + " €", pend === null);
    var colchon = (tes !== null && costes) ? tes / costes : null;
    ponCinco("colchon", colchon === null ? "pendiente" : colchon.toFixed(1).replace(".", ",") + " meses", colchon === null);

    var lectura = pieza("lectura-pv");
    if(pvdia === null){
      lectura.textContent = "Las primeras visitas necesarias al día se comparan con la capacidad real de la agenda. " +
        "Rellene costes fijos, margen, ticket, conversión y días para verlo.";
    } else {
      lectura.textContent = "Con estos supuestos hacen falta " + pvdia.toFixed(1).replace(".", ",") +
        " primeras visitas al día para llegar al equilibrio. Si la agenda no da para tantas, el problema " +
        "no es comercial: es de conversión o de ticket, y se resuelve en el Protocolo de Primera Visita, " +
        "no en la campaña.";
    }
  }

  // ---------- copia, impresión y vaciado ----------
  // Esta hoja se abre de tres maneras: como archivo suelto en el ordenador,
  // dentro del archivo único y publicada en la web. En las dos primeras el
  // enlace de descarga de siempre funciona; en la tercera el visor no deja que
  // una página se descargue nada por su cuenta y el botón se quedaba mudo, que
  // es lo peor que puede hacer un botón en la única hoja donde se teclean datos
  // que cuesta trabajo reunir. Se pide la vía del visor cuando existe y se cae
  // al enlace de siempre cuando no.
  var NOMBRE_COPIA = "captura-linea-base-giraldo-2026.json";

  function guardarPorEnlace(texto){
    var blob = new Blob([texto], {type:"application/json"});
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = NOMBRE_COPIA;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){ URL.revokeObjectURL(a.href); }, 1000);
  }

  var descargas;  // undefined = sin preguntar todavía; null = no hay
  function conDescargas(){
    if(descargas !== undefined) return Promise.resolve(descargas);
    if(!(window.claude && typeof window.claude.use === "function")){
      descargas = null;
      return Promise.resolve(null);
    }
    return Promise.resolve(window.claude.use("downloads")).then(function(d){
      descargas = d || null;
      return descargas;
    }, function(){ descargas = null; return null; });
  }

  pieza("guardar").addEventListener("click", function(){
    var texto = JSON.stringify(estado, null, 2);
    var aviso = pieza("aviso");
    conDescargas().then(function(d){
      if(!d){ guardarPorEnlace(texto); return; }
      return d.save({filename: NOMBRE_COPIA, data: texto}).then(function(){
        if(aviso) aviso.textContent = "Copia guardada: " + NOMBRE_COPIA;
      }, function(err){
        var cod = err && err.code;
        if(cod === "declined") return;               // dijo que no; no se insiste
        if(cod === "rate_limited"){
          if(aviso) aviso.textContent = "Hay otra descarga esperando respuesta. Inténtelo en un momento.";
          return;
        }
        guardarPorEnlace(texto);                      // último recurso
      });
    });
  });
  var fichero = pieza("fichero");
  pieza("cargar").addEventListener("click", function(){ fichero.click(); });
  fichero.addEventListener("change", function(){
    var f = fichero.files && fichero.files[0];
    if(!f) return;
    var lector = new FileReader();
    lector.onload = function(){
      try {
        var d = JSON.parse(lector.result);
        estado = {umbrales:d.umbrales||{}, meses:d.meses||{}, entradas:d.entradas||{}};
        escribir();
        entradas.forEach(function(inp){
          var c = inp.getAttribute("data-entrada");
          if(estado.entradas[c] !== undefined) inp.value = estado.entradas[c];
        });
        pintaUmbrales(); pintaMes(); pintaAnual(); pintaCinco();
      } catch(e){
        pieza("aviso").textContent =
          "Ese archivo no es una copia válida de esta hoja. No se ha cambiado nada.";
      }
      fichero.value = "";
    };
    lector.readAsText(f);
  });
  pieza("imprimir").addEventListener("click", function(){ window.print(); });
  pieza("vaciar").addEventListener("click", function(){
    if(!confirm("Se borra todo lo introducido en este equipo. ¿Continuar?")) return;
    estado = {umbrales:{}, meses:{}, entradas:{}};
    try { localStorage.removeItem(LLAVE); } catch(e){}
    entradas.forEach(function(inp){ estado.entradas[inp.getAttribute("data-entrada")] = inp.value; });
    pintaUmbrales(); pintaMes(); pintaAnual(); pintaCinco();
  });

  pintaUmbrales(); pintaMes(); pintaAnual(); pintaCinco();
})();
</script>
""".replace("@@IND@@", json.dumps([{k: d[k] for k in ("n", "den", "denfijo", "fmt",
                                                          "sentido", "verde", "ambar") if k in d}
                                       for d in IND], ensure_ascii=False))
       .replace("@@MESESJS@@", json.dumps(MESES, ensure_ascii=False)))

destino = RAIZ / "instrumentos" / "captura.html"
destino.parent.mkdir(parents=True, exist_ok=True)
destino.write_text(sello(cabecera + "\n" + CUERPO + "\n" + JS + "\n</body>\n</html>\n"), encoding="utf-8")
print("captura.html ·", destino.stat().st_size // 1024, "KB")
