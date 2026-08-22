#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera inicio.html: la puerta de entrada a todo el sistema documental.

    python3 build-inicio.py
"""
import re
from pathlib import Path

RAIZ = Path(__file__).parent
manual = (RAIZ / "manual.html").read_text(encoding="utf-8")
i = manual.index("<body>")
cabecera = manual[:i + len("<body>")]
cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                            "<title>Sistema documental Giraldo</title>")
cabecera = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="Puerta de entrada al sistema documental del Centro '
                  'de Excelencia Implantológica Giraldo: Tesis de Dirección, presentación de Junta, Manual '
                  'Maestro, Protocolo de Primera Visita, otros documentos del sistema y la hoja de captura '
                  'de la línea base.">', cabecera, count=1)

CSS = """
.puerta{display:grid;gap:1px;background:var(--line);border:1px solid var(--line);margin-top:1.6rem}
@media(min-width:820px){.puerta{grid-template-columns:repeat(2,minmax(0,1fr))}}
.puerta__ficha{
  background:var(--paper);padding:1.6rem;display:grid;gap:.6rem;align-content:start;
  text-decoration:none;color:inherit;transition:background .16s ease;min-width:0;
}
.puerta__ficha:hover{background:var(--surface)}
.puerta__ficha:hover h3{color:var(--accent-ink)}
.puerta__ficha--ancha{grid-column:1/-1;background:var(--accent-soft)}
.puerta__ficha--ancha:hover{background:rgba(14,124,116,.16)}
.puerta__ficha h3{font-size:var(--step-2);letter-spacing:-.015em}
.puerta__ficha p{color:var(--ink-2);font-size:.94rem;max-width:60ch}
.puerta__pie{
  margin-top:.4rem;display:flex;flex-wrap:wrap;gap:.4rem .9rem;
  font-family:var(--f-mono);font-size:.66rem;letter-spacing:.11em;
  text-transform:uppercase;color:var(--muted);
}
.puerta__pie b{color:var(--accent-ink);font-weight:400}
.puerta__flecha{font-family:var(--f-mono);color:var(--accent-ink);margin-left:auto}
"""
k = cabecera.rindex("</style>")
cabecera = cabecera[:k] + CSS + "\n" + cabecera[k:]

FICHAS = [
 ("memoria.html", "Tesis de Dirección", "v6.0 · 19 apartados · Anexo A",
  "El documento de gobierno. Posición competitiva y foso, sistema operativo y cartera de innovación, "
  "economía unitaria y creación de valor de empresa, riesgos y pre-mortem, y las catorce decisiones que "
  "se someten a la Junta. Incluye el cuadernillo con las catorce hojas de acta.",
  "57 páginas en papel · lectura 42′", True),
 ("deck.html", "Presentación de Junta", "v6.0 · 34 diapositivas · 16:9",
  "La tesis para proyectar. Se conduce con el teclado: <b>←</b> y <b>→</b> para pasar, "
  "<b>N</b> abre el guion del ponente con el minuto objetivo y la pregunta difícil, "
  "<b>E</b> filtra a la ruta corta de doce diapositivas para sesiones de veinte minutos.",
  "Proyección y guion del ponente", False),
 ("instrumentos/captura.html", "Captura de la línea base", "v6.0 · 10 indicadores",
  "El instrumento del §7 y del §13: doce hojas mensuales, semáforo automático, resumen anual con "
  "tendencia y los cinco números. Se rellena aquí mismo y se guarda en este equipo.",
  "Se rellena en el navegador", False),
 ("manual.html", "Manual Maestro de Operaciones", "v6.0 · 8 partes",
  "El documento troncal. Las catorce fases del recorrido del paciente, los manuales por puesto, la "
  "matriz RACI, los indicadores, el plan de incentivos y la puesta en marcha. Ocho partes "
  "numeradas, más el marco de vanguardia y los estándares transversales.",
  "204 páginas en papel", False),
 ("index.html", "Protocolo de Primera Visita", "v6.0 · 12 fases de la primera visita",
  "El detalle minuto a minuto de la visita que decide la conversión, con estándares transversales, "
  "casos especiales, guiones contrastados y anexos.",
  "90 páginas en papel", False),
 ("otros.html", "Otros documentos del sistema", "v6.0 · 14 documentos de apoyo",
  "Compendio maestro, verificación de 322 puntos, auditoría de la clínica adquirida, decisiones de "
  "Gerencia, programa de 100 días, protocolos por perfil, innovación, marca, «No medias sonrisas» y "
  "el programa Giraldo Te Cuida.",
  "135 páginas en papel", False),
]


def ficha(destino, titulo, etiqueta, texto, pie, ancha):
    return ('<a class="puerta__ficha%s" href="%s">\n'
            '        <p class="eyebrow">%s</p>\n'
            '        <h3>%s</h3>\n'
            '        <p>%s</p>\n'
            '        <p class="puerta__pie"><span>%s</span><span class="puerta__flecha">Abrir →</span></p>\n'
            '      </a>' % (" puerta__ficha--ancha" if ancha else "", destino, etiqueta, titulo, texto, pie))


CUERPO = """
<header class="topbar">
  <div class="wrap">
    <div class="topbar__in">
      <a class="brand" href="#portada">
        <span class="brand__mark">Sistema documental <b>Giraldo</b></span>
        <span class="brand__tag">v6.0 · Uso interno</span>
      </a>
    </div>
  </div>
</header>

<main>

<section class="hero" id="portada">
  <div class="wrap">
    <div class="hero__grid">
      <div>
        <p class="eyebrow">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
        <h1>No medias<br><em>sonrisas</em></h1>
        <p class="hero__lede">Seis documentos que se abren en cualquier navegador, sin instalar nada y sin conexión. Todos comparten la versión <strong>v6.0</strong>: si uno cambia lo bastante como para merecer versión nueva, la reciben todos.</p>
        <p class="hero__note">Uso interno y confidencial. Contiene información económica, laboral y estratégica. No se difunde fuera de la organización sin autorización expresa de la Dirección General.</p>
      </div>
      <dl class="specs">
        <div class="spec"><dt>Documentos operativos</dt><dd>17<small>Tres troncales y catorce de apoyo. El censo completo, en §0.1 de la Tesis</small></dd></div>
        <div class="spec"><dt>Decisiones abiertas</dt><dd>14<small>Se someten a la Junta Directiva</small></dd></div>
        <div class="spec"><dt>Puntos de verificación</dt><dd>322<small>Físicos, documentales, de sistemas y de proceso</small></dd></div>
        <div class="spec"><dt>Indicadores</dt><dd>10<small>Con definición operativa acordada</small></dd></div>
      </dl>
    </div>
  </div>
</section>
<div class="wrap"><div class="ticks ticks--tall" aria-hidden="true"></div></div>

<section class="section">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">El sistema</p>
      <h2>Qué es cada cosa</h2>
      <p>La Tesis dirige, la presentación convence, el Manual y el Protocolo ejecutan, Otros documentos sostiene y la hoja de captura mide. Sin la última, las cinco primeras se apoyan en supuestos.</p>
    </div>
    <div class="puerta">
      @@FICHAS@@
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Cómo se abren</p>
      <h2>Sin instalar nada</h2>
    </div>
    <div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr))">
      <div class="card"><p class="eyebrow">En este equipo</p><h3>Doble clic</h3><p>Cada archivo es una página completa: se abre en el navegador que tenga instalado, sin conexión y sin ningún programa adicional. Mantenga los seis en la misma carpeta para que los enlaces entre ellos funcionen.</p></div>
      <div class="card"><p class="eyebrow">En papel</p><h3>Imprimir</h3><p>Todos llevan hoja de estilos de impresión: A4 con cabecera de clasificación, numeración y tablas que repiten su encabezado. La presentación sale apaisada, una diapositiva por página.</p></div>
      <div class="card"><p class="eyebrow">Para repartir</p><h3>La carpeta entera</h3><p>Copie la carpeta completa en una memoria o envíela comprimida. No hay servidor, ni cuenta, ni dependencia externa: lo que ve aquí es todo lo que hace falta.</p></div>
    </div>
    <div class="callout" style="max-width:none">
      <p class="eyebrow">Una advertencia que no conviene saltarse</p>
      <p>Las cifras económicas de la Tesis y de la presentación son <strong>modelos sobre rangos del sector, marcados como tales</strong> en cada figura y registradas en su §18. No son datos del centro y no deben citarse como tales hasta que exista la línea base. Levantarla es exactamente para lo que sirve la hoja de captura.</p>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <div class="ticks" aria-hidden="true" style="margin-bottom:2rem"></div>
    <div class="foot__grid">
      <div>
        <p><strong>Centro de Excelencia Implantológica Giraldo</strong><br>Sistema documental · Uso interno y confidencial</p>
      </div>
      <div><p class="eyebrow">Lema</p><p>No medias sonrisas.<br>Ni medias decisiones.</p></div>
      <div><p class="eyebrow">Versiones</p><p>Versión única del sistema<br><strong>v6.0 · Agosto 2026</strong></p></div>
    </div>
  </div>
</footer>
""".replace("@@FICHAS@@", "\n      ".join(ficha(*f) for f in FICHAS))

(RAIZ / "inicio.html").write_text(cabecera + "\n" + CUERPO + "\n</body>\n</html>\n", encoding="utf-8")
print("inicio.html ·", (RAIZ / "inicio.html").stat().st_size // 1024, "KB")
