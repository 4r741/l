#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build-conceptos.py — la hoja de direcciones visuales, muy pulida.

Cuatro pieles MUY distintas de la misma portada de Clínica Alma, cada una
mostrada como una maqueta de verdad: cabecera, portada, cifras y un vistazo del
interior. Sirve para ELEGIR el rumbo antes de construir la web entera. Las
tipografías van incrustadas: se abre de doble clic y sin conexión.

    python3 build-conceptos.py   → conceptos.html
"""
import base64
import pathlib

RAIZ = pathlib.Path(__file__).parent
TIPOS = RAIZ / "fuentes" / "tipos"

EMBLEMA = (
    '<svg viewBox="0 0 128 118" fill="none" stroke="currentColor" '
    'stroke-width="4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M52 14 C47 6 39 7 38 17 C37 30 40 44 43 62 C44 72 50 78 53 68 '
    'C56 60 57 50 58 42 C59 50 60 60 63 68 C66 78 72 72 73 62 C76 44 79 30 78 17 '
    'C77 7 69 6 64 14 C61 19 55 19 52 14 Z"/>'
    '<path d="M44 54 C30 50 15 55 9 70 C24 76 40 71 46 58"/>'
    '<path d="M72 54 C86 50 101 55 107 70 C92 76 76 71 70 58"/>'
    '<path d="M20 78 C40 106 76 106 96 78"/></svg>')


def cara(familia, peso, arch):
    ruta = TIPOS / arch
    if not ruta.exists():
        return ""
    b64 = base64.b64encode(ruta.read_bytes()).decode()
    return ('@font-face{font-family:"%s";font-style:normal;font-weight:%s;'
            'font-display:swap;src:url(data:font/ttf;base64,%s) format("truetype")}'
            % (familia, peso, b64))


def fuentes():
    return "".join([
        cara("Roboto", "400", "Roboto-Regular.ttf"),
        cara("Roboto", "500", "Roboto-Medium.ttf"),
        cara("Roboto", "700", "Roboto-Bold.ttf"),
        cara("Outfit", "400", "Outfit-Regular.ttf"),
        cara("Outfit", "700", "Outfit-Bold.ttf"),
        cara("Fraunces", "100 900", "Fraunces-Variable.ttf"),
    ])


# Contenido común (mismo en las cuatro): portada + cifras + vistazo de interior.
CIFRAS = [("8", "Documentos"), ("135", "Apartados"), ("14", "Fases"), ("123′", "Primera visita")]
DOCS = [
    ("01", "Dirección", "La posición del centro y sus estándares"),
    ("02", "Primera visita", "123 minutos, fase a fase, sin sorpresas"),
    ("03", "Operaciones", "Cómo se ejecuta cada día, por escrito"),
]


def maqueta(letra, clase, subt, headline_html):
    nav = ('<nav class="nav"><span class="logo"><span class="emb">' + EMBLEMA +
           '</span>Clínica Alma</span>'
           '<a>El sistema</a><a>Primera visita</a><a>Los números</a>'
           '<a class="cta">Entrar</a></nav>')
    cifras = "".join(
        '<div class="chip"><b>%s</b><span>%s</span></div>' % c for c in CIFRAS)
    docs = "".join(
        '<article class="doc"><span class="doc__n">%s</span>'
        '<h4>%s</h4><p>%s</p><span class="doc__go">Abrir →</span></article>' % d
        for d in DOCS)
    return (
        '<section class="hoja">'
        '<div class="etq"><b>%s</b><span>%s</span></div>'
        '<div class="m %s">'
        + nav +
        '<header class="hero">'
        '<p class="eyebrow">Centro de Excelencia Implantológica · Ourense</p>'
        '<h2 class="h">%s</h2>'
        '<p class="sub">Todo el método del centro, ordenado y a la vista: ocho '
        'documentos y ciento treinta y cinco apartados que no dejan cabos sueltos.</p>'
        '<div class="acc"><a class="btn">Descubrir el método</a>'
        '<a class="btn2">Su primera visita</a></div>'
        '<div class="cifras">' + cifras + '</div>'
        '</header>'
        '<div class="peek">'
        '<div class="peek__cab"><span class="peek__k">El sistema · en ocho documentos</span>'
        '<h3>Ocho paradas, en orden</h3></div>'
        '<div class="docs">' + docs + '</div>'
        '</div>'
        '</div></section>'
    ) % (letra, subt, clase, headline_html)


CSS = r"""
*{box-sizing:border-box}
body{margin:0;background:#dcdce1;color:#111;
  font-family:"Roboto",-apple-system,Segoe UI,Arial,sans-serif;
  padding:2.4rem clamp(1rem,4vw,3rem) 4rem}
.intro{max-width:64rem;margin:0 auto 2.2rem}
.intro h1{font-size:1.55rem;margin:0 0 .5rem;font-weight:700}
.intro p{margin:.35rem 0;color:#333;line-height:1.6;font-size:1rem}
.intro b{color:#000}
.hoja{max-width:64rem;margin:0 auto 2.4rem;border-radius:16px;overflow:hidden;
  box-shadow:0 30px 70px -40px rgba(0,0,0,.6);border:1px solid rgba(0,0,0,.1)}
.etq{display:flex;align-items:baseline;gap:.7rem;padding:.75rem 1.2rem;
  background:#17171b;color:#fff;font-size:.84rem}
.etq b{font-size:1.05rem;background:#fff;color:#17171b;border-radius:6px;
  padding:.05rem .5rem}
.etq span{color:#a2a2ab}

.m{padding:0}
.nav{display:flex;align-items:center;gap:1.4rem;font-size:.74rem;flex-wrap:wrap;
  padding:1.1rem clamp(1.4rem,4vw,2.6rem);font-family:"Roboto",sans-serif}
.nav .logo{font-weight:700;margin-right:auto;display:flex;align-items:center;gap:.55rem;
  font-size:.98rem}
.nav .emb{width:1.7rem;height:1.7rem;display:inline-flex}
.nav .emb svg{width:100%;height:100%}
.nav a{opacity:.8;text-decoration:none;color:inherit;cursor:default}
.nav .cta{opacity:1;padding:.45rem 1rem;border-radius:99px;font-weight:600}
.hero{padding:clamp(1.6rem,4vw,3rem) clamp(1.4rem,4vw,2.6rem) clamp(1.8rem,4vw,2.6rem)}
.eyebrow{font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;margin:0 0 1rem;font-weight:600}
.h{margin:0 0 1.1rem;line-height:1}
.sub{font-size:1rem;line-height:1.6;max-width:40ch;margin:0 0 1.6rem}
.acc{display:flex;gap:.8rem;flex-wrap:wrap;align-items:center;margin-bottom:1.8rem}
.btn{padding:.75rem 1.4rem;border-radius:99px;font-size:.85rem;font-weight:600;text-decoration:none;cursor:default}
.btn2{font-size:.85rem;font-weight:600;text-decoration:none;cursor:default;padding:.2rem}
.cifras{display:flex;gap:.7rem;flex-wrap:wrap}
.chip{padding:.7rem .9rem;border-radius:12px;min-width:6rem}
.chip b{display:block;font-size:1.5rem;line-height:1}
.chip span{font-size:.64rem;letter-spacing:.06em;text-transform:uppercase;opacity:.75}
.peek{padding:clamp(1.6rem,4vw,2.4rem) clamp(1.4rem,4vw,2.6rem) clamp(2rem,5vw,3rem)}
.peek__cab{margin-bottom:1.2rem}
.peek__k{font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;font-weight:600}
.peek__cab h3{margin:.5rem 0 0;line-height:1.05}
.docs{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
.doc{padding:1.2rem;border-radius:12px}
.doc__n{font-size:.9rem;font-weight:700;opacity:.6}
.doc h4{margin:.5rem 0 .4rem;font-size:1.05rem}
.doc p{margin:0 0 1rem;font-size:.82rem;line-height:1.5;opacity:.85}
.doc__go{font-size:.74rem;font-weight:600}
@media(max-width:640px){.docs{grid-template-columns:1fr}}

/* ============ A · Clínico minimalista (blanco + azul) ============ */
.A{background:#fff;color:#18222c;font-family:"Outfit",sans-serif}
.A .nav .cta{background:#2563eb;color:#fff}
.A .logo .emb{color:#2563eb}
.A .eyebrow{color:#2563eb;font-family:"Roboto",sans-serif}
.A .h{font-weight:300;font-size:clamp(2.6rem,6.5vw,4rem);letter-spacing:-.03em}
.A .h b{font-weight:600}
.A .sub{color:#4a5a66;font-family:"Roboto",sans-serif}
.A .btn{background:#2563eb;color:#fff}
.A .btn2{color:#2563eb}
.A .cifras{border-top:1px solid #e6ecf3;padding-top:1.3rem}
.A .chip{background:#f4f8fd}
.A .chip b{color:#2563eb;font-weight:600}
.A .peek{background:#f7fafd;border-top:1px solid #e6ecf3}
.A .peek__k{color:#2563eb;font-family:"Roboto",sans-serif}
.A .doc{background:#fff;border:1px solid #e6ecf3}
.A .doc__go{color:#2563eb;font-family:"Roboto",sans-serif}

/* ============ B · Oscuro premium (tinta + oro, serif) ============ */
.B{background:#14181c;color:#ece7dd;font-family:"Roboto",sans-serif}
.B .nav .cta{border:1px solid #b99653;color:#e8cf9c}
.B .logo{color:#ece7dd} .B .logo .emb{color:#c8a25f}
.B .eyebrow{color:#c8a25f}
.B .h{font-family:"Fraunces",serif;font-weight:380;font-size:clamp(2.8rem,7.5vw,4.6rem);
  letter-spacing:-.01em;color:#f4efe4}
.B .h i{color:#d8b878}
.B .sub{color:#b6b0a4}
.B .btn{background:#b99653;color:#14181c}
.B .btn2{color:#d8b878}
.B .cifras{border-top:1px solid rgba(200,162,95,.25);padding-top:1.3rem}
.B .chip{background:rgba(185,150,83,.1)}
.B .chip b{color:#e6c88c;font-family:"Fraunces",serif;font-weight:400}
.B .peek{background:#0f1216;border-top:1px solid rgba(200,162,95,.2)}
.B .peek__k{color:#c8a25f}
.B .peek__cab h3{font-family:"Fraunces",serif;font-weight:400}
.B .doc{background:#171c21;border:1px solid rgba(200,162,95,.16)}
.B .doc h4{font-family:"Fraunces",serif;font-weight:500}
.B .doc__go{color:#d8b878}

/* ============ C · Editorial de color (bold + acento) ============ */
.C{background:#f7f4ee;color:#191614;font-family:"Roboto",sans-serif}
.C .nav .cta{background:#e0402a;color:#fff}
.C .logo .emb{color:#e0402a}
.C .eyebrow{color:#e0402a;font-weight:700}
.C .h{font-family:"Outfit",sans-serif;font-weight:700;font-size:clamp(2.7rem,8.5vw,5rem);
  letter-spacing:-.035em;text-transform:uppercase;line-height:.92}
.C .h span{color:#e0402a}
.C .sub{color:#3a352f;font-weight:500}
.C .btn{background:#191614;color:#fff}
.C .btn2{color:#e0402a}
.C .cifras{gap:0;border:2px solid #191614;border-radius:12px;overflow:hidden}
.C .chip{border-radius:0;border-right:2px solid #191614;flex:1;background:#fff}
.C .chip:last-child{border-right:0}
.C .chip b{font-family:"Outfit",sans-serif;font-weight:700}
.C .peek{background:#191614;color:#f7f4ee}
.C .peek__k{color:#f0a58f}
.C .peek__cab h3{font-family:"Outfit",sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:-.02em}
.C .doc{background:#221e1b;border:1px solid #39322d}
.C .doc__n{color:#e0402a;opacity:1}
.C .doc__go{color:#f0a58f}

/* ============ D · Suave corporativo (pastel + verde, redondeado) ============ */
.D{background:linear-gradient(165deg,#eef4f1 0%,#f7f2ec 100%);color:#22322d;
  font-family:"Outfit",sans-serif}
.D .nav .cta{background:#2f7d68;color:#fff}
.D .logo .emb{color:#2f7d68}
.D .eyebrow{color:#2f7d68;font-family:"Roboto",sans-serif}
.D .h{font-weight:700;font-size:clamp(2.5rem,6.5vw,3.9rem);letter-spacing:-.025em}
.D .h em{font-style:normal;color:#2f7d68}
.D .sub{color:#4c625b;font-family:"Roboto",sans-serif}
.D .btn{background:#2f7d68;color:#fff;box-shadow:0 12px 24px -12px rgba(47,125,104,.7)}
.D .btn2{color:#2f7d68}
.D .chip{background:#fff;box-shadow:0 8px 20px -12px rgba(0,0,0,.25);border-radius:16px}
.D .chip b{color:#2f7d68;font-weight:700}
.D .peek{border-top:1px solid rgba(47,125,104,.18)}
.D .peek__k{color:#2f7d68;font-family:"Roboto",sans-serif}
.D .doc{background:#fff;border-radius:18px;box-shadow:0 12px 30px -18px rgba(0,0,0,.3)}
.D .doc__go{color:#2f7d68;font-family:"Roboto",sans-serif}
"""


def main():
    hojas = [
        maqueta("A", "A", "Clínico minimalista · blanco y azul · sans limpia · confianza y claridad",
                'No medias <b>sonrisas</b>'),
        maqueta("B", "B", "Oscuro premium · tinta y oro · serif Fraunces · lujo y calma",
                'No medias <i>sonrisas</i>'),
        maqueta("C", "C", "Editorial de color · sans grande en mayúscula · un acento fuerte · energía",
                'No medias <span>sonrisas</span>'),
        maqueta("D", "D", "Suave corporativo · pastel y verde · redondeado · amable y actual",
                'No medias <em>sonrisas</em>'),
    ]
    intro = (
        '<div class="intro"><h1>Clínica Alma · cuatro direcciones visuales</h1>'
        '<p>El <b>contenido y la estructura no cambian</b> (el sistema interno: 8 '
        'documentos, 135 apartados). Aquí solo cambia el <b>aspecto</b>. Cada '
        'bloque es la misma web con una piel distinta: portada, cifras y un '
        'vistazo del interior.</p>'
        '<p>Dime <b>qué letra te gusta</b> —A, B, C o D— o mézclalas: «la C en '
        'azul en vez de rojo», «la B pero con fondo claro», «la A con la letra de '
        'la D»… Con eso construyo la web entera en esa dirección, de una vez.</p></div>')
    doc = (
        '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Clínica Alma · direcciones visuales</title>\n'
        '<style>' + fuentes() + '\n' + CSS + '</style>\n</head>\n<body>\n'
        + intro + "\n" + "\n".join(hojas) + "\n</body>\n</html>\n")
    salida = RAIZ / "conceptos.html"
    salida.write_text(doc, encoding="utf-8")
    print("conceptos.html · 4 direcciones · %d KB" % (len(doc.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()
