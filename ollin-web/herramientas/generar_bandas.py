"""Genera las páginas de banda de Ollin a partir de datos/bandas.json.

Uso (desde la carpeta del sitio):
    python3 herramientas/generar_bandas.py

Escribe she-no-more.html, cemican.html y anna-fiori.html. Lo que esté vacío o entre
[corchetes] en el JSON se muestra en la página como placeholder marcado "pendiente".
"""
import html
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "datos", "bandas.json")


def e(s):
    return html.escape(str(s or ""), quote=True)


def pendiente(v):
    return (not v) or (isinstance(v, str) and v.strip().startswith("["))


def txt(v, vacio="Pendiente"):
    """Texto normal o, si falta, un placeholder visible."""
    if pendiente(v):
        return f'<span class="ph">{e(v) if v else vacio}</span>'
    return e(v)


def ig_handle(url):
    if not url:
        return ""
    u = url.rstrip("/").split("/")[-1].lstrip("@")
    return "@" + u


def ig_url(v):
    if not v:
        return ""
    if v.startswith("http"):
        return v
    return "https://www.instagram.com/" + v.lstrip("@") + "/"


NAV = """<nav class="nav" aria-label="Principal">
  <a class="nav__logo" href="index.html">Ollin</a>
  <div class="nav__links">
    <a href="index.html#concepto">Concepto</a>
    <a href="index.html#bandas">Bandas</a>
    <a href="index.html#lugar">El Lunario</a>
    <a class="nav__cta" href="index.html#avisame">Avísame</a>
  </div>
</nav>"""

COSMOS = """<div class="cosmos" aria-hidden="true">
  <div class="cosmos__layer" data-depth="0.06"><div class="cosmos__nebula cosmos__nebula--a"></div></div>
  <div class="cosmos__layer" data-depth="0.16"><div class="cosmos__nebula cosmos__nebula--b"></div></div>
  <div class="cosmos__layer" data-depth="0.28"><div class="cosmos__nebula cosmos__nebula--c"></div></div>
</div>
<canvas class="sky" id="sky" aria-hidden="true"></canvas>"""


def pagina(b, prev, nxt):
    nombre = e(b["nombre"])

    # portada
    if b.get("logo"):
        marca = f'<img class="bp__logo" src="{e(b["logo"])}" alt="{nombre}">'
    else:
        marca = f'<h1 class="bp__name">{nombre}</h1>'
    if b.get("foto"):
        foto = f'<figure class="bp__foto"><img src="{e(b["foto"])}" alt="{nombre} en vivo"><figcaption>{e(b.get("credito_foto"))}</figcaption></figure>'
    else:
        foto = '<div class="bp__foto bp__foto--ph ph-box" role="img" aria-label="Foto pendiente"><span>Foto de la banda<br>pendiente</span></div>'
    titulo_oculto = f'<h1 class="sr-only">{nombre}</h1>' if b.get("logo") else ""

    hitos = "".join(f"<li>{txt(h)}</li>" for h in b.get("hitos", []))

    miembros = []
    for m in b.get("integrantes", []):
        if m.get("foto"):
            mf = f'<img class="miembro__foto" src="{e(m["foto"])}" alt="">'
        else:
            mf = '<div class="miembro__foto miembro__foto--ph" aria-hidden="true"></div>'
        if m.get("instagram"):
            mig = f'<a class="miembro__ig" href="{e(ig_url(m["instagram"]))}" rel="noopener">{e(ig_handle(ig_url(m["instagram"])))}</a>'
        else:
            mig = '<span class="miembro__ig ph">@instagram</span>'
        miembros.append(f"""        <li class="miembro">
          {mf}
          <p class="miembro__nombre">{txt(m.get("nombre"))}</p>
          <p class="miembro__rol">{txt(m.get("rol"))}</p>
          {mig}
        </li>""")
    miembros = "\n".join(miembros)

    canciones = "".join(
        f'<li><span class="tracks__t">{txt(c["titulo"])}</span><span class="tracks__why">{txt(c.get("porque"))}</span></li>'
        for c in b.get("canciones", []))

    if b.get("spotify_embed"):
        player = (f'<iframe class="player" title="Reproductor de Spotify de {nombre}" src="{e(b["spotify_embed"])}" '
                  'width="100%" height="352" loading="lazy" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>')
    else:
        player = '<div class="player ph-box"><span>Reproductor de Spotify pendiente<br>(pega el link de embed en bandas.json)</span></div>'

    discos = []
    for d in b.get("discografia", []):
        if d.get("portada"):
            cov = f'<img class="disco__portada" src="{e(d["portada"])}" alt="">'
        else:
            cov = '<div class="disco__portada disco__portada--ph" aria-hidden="true"></div>'
        tipo = f'{e(d["tipo"])} · ' if d.get("tipo") else ""
        cuerpo = f'{cov}<p class="disco__titulo">{txt(d.get("titulo"))}</p><p class="disco__anio">{tipo}{txt(d.get("anio"))}</p>'
        if d.get("link"):
            cuerpo = f'<a href="{e(d["link"])}" rel="noopener">{cuerpo}</a>'
        discos.append(f'<li class="disco">{cuerpo}</li>')
    discos = "".join(discos)

    redes = []
    etiquetas = [("instagram", "Instagram"), ("spotify", "Spotify"), ("youtube", "YouTube"),
                 ("facebook", "Facebook"), ("tiktok", "TikTok"), ("patreon", "Patreon"),
                 ("tienda", "Tienda"), ("web", "Sitio web")]
    opcionales = {"tiktok", "patreon"}           # solo aparecen si la banda los tiene
    for k, lab in etiquetas:
        v = b.get("redes", {}).get(k)
        if not v and k in opcionales:
            continue
        if v:
            redes.append(f'<a href="{e(v)}" rel="noopener">{lab}</a>')
        else:
            redes.append(f'<span class="ph">{lab}</span>')
    redes = "\n          ".join(redes)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{nombre} · Ollin, Lunario 11 de julio de 2027</title>
  <meta name="description" content="{nombre} en Ollin: algo se mueve en el ombligo de la luna. Lunario del Auditorio Nacional, domingo 11 de julio de 2027.">
  <meta name="theme-color" content="#07070D">
  <meta property="og:title" content="{nombre} en Ollin">
  <meta property="og:image" content="og-image.jpg">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..125,300..800&family=Rubik+Dirt&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="banda.css">
</head>
<body class="pagina-banda">
<!-- Generado por herramientas/generar_bandas.py desde datos/bandas.json. No edites a mano: edita el JSON y vuelve a generar. -->

{COSMOS}

{NAV}

<header class="hero bp__hero">
  <div class="hero__inner">
    <p class="bp__evento"><a href="index.html">Ollin</a>, 11 de julio de 2027, Lunario</p>
    {titulo_oculto}{marca}
    <p class="bp__altura">{e(b.get("altura"))}</p>
    <p class="bp__verbo">Esa noche vienen a <strong>{txt(b.get("verbo"))}</strong></p>
    <dl class="bp__facts">
      <div><dt>De</dt><dd>{txt(b.get("origen"))}</dd></div>
      <div><dt>Desde</dt><dd>{txt(b.get("inicio"))}</dd></div>
      <div><dt>Suena a</dt><dd>{txt(b.get("sonido"))}</dd></div>
    </dl>
  </div>
</header>

<main>
<div class="tierra">
<div class="horizonte" aria-hidden="true"></div>

<section class="bp__sec wrap">
  <div class="bp__grid losa">
    {foto}
    <div>
      <h2 class="h-display">Su camino</h2>
      <p class="lead">{txt(b.get("trayectoria"))}</p>
      <h3 class="bp__sub">Momentos que los definen</h3>
      <ul class="bp__hitos">{hitos}</ul>
    </div>
  </div>
</section>

<section class="bp__sec wrap" aria-labelledby="integrantes-title">
  <div class="losa">
    <h2 class="h-display" id="integrantes-title">Integrantes</h2>
    <ul class="miembros">
{miembros}
    </ul>
  </div>
</section>

<section class="bp__sec wrap" aria-labelledby="escucha-title">
  <div class="bp__grid losa">
    <div>
      <h2 class="h-display" id="escucha-title">Empieza por</h2>
      <ul class="tracks">{canciones}</ul>
    </div>
    {player}
  </div>
</section>

<section class="bp__sec wrap" aria-labelledby="disco-title">
  <div class="losa">
    <h2 class="h-display" id="disco-title">Discografía</h2>
    <ul class="discos">{discos}</ul>
    <h3 class="bp__sub">Síguelos</h3>
    <p class="bp__redes">
          {redes}
    </p>
  </div>
</section>

<nav class="bp__sec wrap bp__nav" aria-label="Otras bandas">
  <a class="bp__puerta losa" href="{prev["slug"]}.html"><span class="bp__dir">Anterior</span><span class="bp__pname">{e(prev["nombre"])}</span><span class="bp__palt">{e(prev.get("altura"))}</span></a>
  <a class="bp__puerta losa" href="{nxt["slug"]}.html"><span class="bp__dir">Siguiente</span><span class="bp__pname">{e(nxt["nombre"])}</span><span class="bp__palt">{e(nxt.get("altura"))}</span></a>
</nav>
<p class="bp__sec wrap bp__volver">
  <a class="btn btn--ghost" href="index.html">Volver a Ollin</a>
  <a class="btn btn--primary" href="index.html#avisame">Avísame cuando salgan los boletos</a>
</p>

</div><!-- /tierra -->
</main>

<footer class="footer">
  <div class="wrap footer__grid">
    <p class="footer__name">Ollin</p>
    <p><a href="she-no-more.html">She No More</a> <a href="cemican.html">Cemican</a> <a href="anna-fiori.html">Anna Fiori</a></p>
    <p class="footer__small">Algo se mueve en el ombligo de la luna. Domingo 11 de julio de 2027, Lunario del Auditorio Nacional. 🤘</p>
  </div>
</footer>

<script src="main.js"></script>
</body>
</html>
"""


def main():
    with open(DATOS, encoding="utf-8") as f:
        bandas = json.load(f)["bandas"]
    n = len(bandas)
    for i, b in enumerate(bandas):
        out = os.path.join(RAIZ, f'{b["slug"]}.html')
        with open(out, "w", encoding="utf-8") as f:
            f.write(pagina(b, bandas[(i - 1) % n], bandas[(i + 1) % n]))
        print("escrito", os.path.relpath(out, RAIZ))


if __name__ == "__main__":
    main()
