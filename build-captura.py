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

CSS = """
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
                            "<title>Captura de la línea base · Giraldo</title>")
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
 ("margen", "Margen de contribución", "%", "Supuesto de trabajo del §18 mientras no haya escandallo propio.", "40"),
 ("ticket", "Ticket medio del caso aceptado", "€", "Supuesto de trabajo del §18. Se sustituye por el real.", "1800"),
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
        <span class="brand__mark">Captura de la <b>línea base</b></span>
        <span class="brand__tag">2026 · v1.0</span>
      </a>
      <a class="crosslink" href="../memoria.html">Tesis de Dirección</a>
      <a class="crosslink" href="../manual.html">Manual Maestro</a>
      <a class="crosslink" href="../index.html">Protocolo</a>
    </div>
    <nav class="strip" aria-label="Índice">
      <a href="#instrucciones">Instrucciones</a>
      <a href="#definiciones">Definiciones</a>
      <a href="#captura">Captura mensual</a>
      <a href="#anual">Resumen anual</a>
      <a href="#cinco">Los cinco números</a>
    </nav>
  </div>
</header>

<main>

<div class="printhead" aria-hidden="true"><b>Captura de la línea base · 2026 · v1.0</b><span>Centro de Excelencia Implantológica Giraldo · Uso interno · Confidencial</span></div>

<section class="hero" id="portada">
  <div class="wrap">
    <div class="hero__grid">
      <div>
        <p class="eyebrow">Instrumento del §7 y del §13 · Uso interno</p>
        <h1>Captura de la<br><em>línea base</em></h1>
        <p class="hero__lede">La Tesis declara que el centro no tiene todavía sus cinco números ni serie propia en ninguno de los diez indicadores. Esta hoja es lo que hace que dejen de faltar.</p>
        <p class="hero__note">Se rellena en el navegador y se guarda en este mismo equipo, sin enviar nada a ningún sitio. Un indicador sin dato aparece como <strong>SIN DATO</strong> y cuenta como rojo: es la regla de reporte del §13. Los resultados de los cinco números dicen <strong>pendiente</strong> mientras falte una entrada, en lugar de dar una cifra inventada.</p>
      </div>
      <dl class="specs">
        <div class="spec"><dt>Indicadores</dt><dd>10<small>Con definición operativa acordada</small></dd></div>
        <div class="spec"><dt>Meses</dt><dd>12<small>Una hoja de captura por mes</small></dd></div>
        <div class="spec"><dt>Los cinco números</dt><dd>7<small>Entradas que hacen falta para calcularlos</small></dd></div>
        <div class="spec"><dt>Dónde se guarda</dt><dd>Aquí<small>En el navegador de este equipo, en local</small></dd></div>
      </dl>
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

<section class="section" id="definiciones">
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
      <button class="boton" type="button" id="umbrales-defecto">Restaurar umbrales de origen</button>
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
        <tbody id="cuerpo-captura">
          @@CAPTURA@@
        </tbody>
      </table>
    </div>
    <div class="cap__barra">
      <p id="aviso">El indicador 5 se compara con el mes anterior: su sentido es «descendente», no un umbral fijo.</p>
      <button class="boton" type="button" id="guardar">Guardar copia</button>
      <button class="boton" type="button" id="cargar">Cargar copia</button>
      <button class="boton" type="button" id="imprimir">Imprimir</button>
      <button class="boton boton--riesgo" type="button" id="vaciar">Vaciar todo</button>
      <input type="file" id="fichero" accept="application/json,.json" hidden>
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
          <small style="margin-top:0">Margen, ticket, conversión y días vienen con los supuestos de trabajo del §18, que <strong>no son mediciones del centro</strong>. Sustitúyanse por los reales en cuanto existan; las otras tres casillas nacen vacías porque solo pueden salir de la contabilidad.</small></div>
    </div>
    <div class="cinco">
      <div class="cinco__caja"><i>1 · Costes fijos mensuales</i><b data-cinco="costes">pendiente</b><p>El primero de los cinco. Sin él no hay ninguno de los demás.</p></div>
      <div class="cinco__caja"><i>2 · Punto de equilibrio mensual</i><b data-cinco="equilibrio">pendiente</b><p>Facturación mensual necesaria para cubrir los costes fijos, dado el margen de contribución.</p></div>
      <div class="cinco__caja"><i>3 · Primeras visitas al día</i><b data-cinco="pvdia">pendiente</b><p>Cuántas hacen falta para llegar al equilibrio con la conversión y el ticket actuales.</p></div>
      <div class="cinco__caja"><i>4 · Producto pendiente heredado</i><b data-cinco="pendiente">pendiente</b><p>Caja ya cobrada que hay que convertir en producción. Es la palanca 1 del §14.</p></div>
      <div class="cinco__caja"><i>5 · Meses de colchón</i><b data-cinco="colchon">pendiente</b><p>Cuánto aguanta el centro sin ingresar nada. Por debajo de tres, es riesgo de Junta.</p></div>
    </div>
    <div class="rulebox" style="max-width:none">
      <p class="eyebrow">La cifra que más incomoda</p>
      <p id="lectura-pv">Las primeras visitas necesarias al día se comparan con la capacidad real de la agenda. Si salen más de las que caben, el problema no es comercial: es de conversión o de ticket.</p>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <div class="ticks" aria-hidden="true" style="margin-bottom:2rem"></div>
    <div class="foot__grid">
      <div>
        <p><strong>Centro de Excelencia Implantológica Giraldo</strong><br>Captura de la línea base · Ejercicio 2026</p>
        <p style="margin-top:.8rem">Documento de uso interno. Los datos se guardan únicamente en este equipo.</p>
      </div>
      <div><p class="eyebrow">Instrumento de</p><p>§7 · Línea base<br>§13 · Cuadro de mando</p></div>
      <div><p class="eyebrow">Documentos de referencia</p><p>Tesis de Dirección v2.0<br>Manual Maestro v5.5<br>Protocolo de Primera Visita v5.5</p></div>
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
  var cuerpo = document.getElementById("cuerpo-captura");

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

  var pestanas = Array.prototype.slice.call(document.querySelectorAll(".cap__mes"));
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
  var tablaDef = document.querySelector("#definiciones tbody");
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
  document.getElementById("umbrales-defecto").addEventListener("click", function(){
    estado.umbrales = {}; escribir(); pintaUmbrales(); pintaMes(); pintaAnual();
  });

  // ---------- resumen anual ----------
  function pintaAnual(){
    IND.forEach(function(d){
      var serie = [];
      for(var m = 0; m < 12; m++){
        var v = resultado(m, d.n);
        serie.push(v);
        var td = document.querySelector('[data-anual="' + d.n + '"][data-mes="' + m + '"]');
        td.textContent = v === null ? "·" : formatea(v, d.fmt);
        td.className = v === null ? "vacio" : "v";
      }
      var conDato = serie.filter(function(v){ return v !== null; });
      var primero = conDato.length ? conDato[0] : null;
      var ultimo = conDato.length ? conDato[conDato.length - 1] : null;
      pon("meses", d.n, String(conDato.length));
      pon("primero", d.n, primero === null ? "·" : formatea(primero, d.fmt));
      pon("ultimo", d.n, ultimo === null ? "·" : formatea(ultimo, d.fmt));
      var t = document.querySelector('[data-res="tend"][data-ind="' + d.n + '"]');
      if(conDato.length < 2){ t.innerHTML = '<span class="tend tend--igual">—</span>'; return; }
      var mejora = d.sentido === "mayor" ? ultimo > primero : ultimo < primero;
      var igual = ultimo === primero;
      t.innerHTML = igual ? '<span class="tend tend--igual">Estable</span>'
                  : mejora ? '<span class="tend tend--sube">Mejora</span>'
                           : '<span class="tend tend--baja">Empeora</span>';
    });
  }
  function pon(cual, i, texto){
    document.querySelector('[data-res="' + cual + '"][data-ind="' + i + '"]').textContent = texto;
  }

  // ---------- los cinco números ----------
  var entradas = Array.prototype.slice.call(document.querySelectorAll("[data-entrada]"));
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
    var b = document.querySelector('[data-cinco="' + cual + '"]');
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

    var lectura = document.getElementById("lectura-pv");
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
  document.getElementById("guardar").addEventListener("click", function(){
    var blob = new Blob([JSON.stringify(estado, null, 2)], {type:"application/json"});
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "captura-linea-base-giraldo-2026.json";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){ URL.revokeObjectURL(a.href); }, 1000);
  });
  var fichero = document.getElementById("fichero");
  document.getElementById("cargar").addEventListener("click", function(){ fichero.click(); });
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
        document.getElementById("aviso").textContent =
          "Ese archivo no es una copia válida de esta hoja. No se ha cambiado nada.";
      }
      fichero.value = "";
    };
    lector.readAsText(f);
  });
  document.getElementById("imprimir").addEventListener("click", function(){ window.print(); });
  document.getElementById("vaciar").addEventListener("click", function(){
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
destino.write_text(cabecera + "\n" + CUERPO + "\n" + JS + "\n</body>\n</html>\n", encoding="utf-8")
print("captura.html ·", destino.stat().st_size // 1024, "KB")
