"""Fondos realistas para Ollin: nebulosa, agua del lago y muro de piedra volcánica.
Todo procedural (sin fotos de terceros). Requiere numpy, scipy y Pillow."""
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter
from scipy.spatial import cKDTree

import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'texturas_base.py')).read())  # spectral_noise, periodic_blur, shade, ao


def warp(img, dx, dy):
    h, w = img.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    return map_coordinates(img, [yy + dy, xx + dx], order=1, mode='wrap')


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ================================================================ NEBULOSA
def nebula(W=2400, H=1500):
    w1 = spectral_noise(H, W, 3.4, 101) - 0.5
    w2 = spectral_noise(H, W, 3.4, 102) - 0.5
    base = spectral_noise(H, W, 2.9, 103)
    n = warp(base, w1 * 260, w2 * 260)                 # nubes deformadas
    n2 = warp(spectral_noise(H, W, 2.6, 104), w2 * 180, -w1 * 180)
    fil = 1 - np.abs(2 * n2 - 1)                        # filamentos (ridged)
    fil = fil ** 5
    dustn = warp(spectral_noise(H, W, 2.7, 105), w1 * 140, w2 * 140)
    dust = (1 - np.abs(2 * dustn - 1)) ** 4             # carriles de polvo

    yy, xx = np.mgrid[0:H, 0:W]
    u, v = xx / W, yy / H
    # banda diagonal, como un brazo de vía láctea, con densidad variable
    band = np.exp(-((v - 0.2 - 0.55 * u) ** 2) / 0.07)
    band = band * (0.6 + 0.8 * spectral_noise(H, W, 3.6, 106))

    teal = smooth(0.38, 0.85, n) * band
    ember = smooth(0.45, 0.95, warp(base, -w2 * 200, w1 * 200)) * band * (0.4 + fil * 1.6)
    gold = fil * band * smooth(0.5, 0.9, n)

    em = (teal[..., None] * np.array([0.10, 0.36, 0.34])
          + ember[..., None] * np.array([0.55, 0.20, 0.07])
          + gold[..., None] * np.array([0.42, 0.30, 0.13])
          + band[..., None] * np.array([0.035, 0.03, 0.05]))
    em = np.stack([gaussian_filter(em[..., c], 1.4) for c in range(3)], -1)
    em *= (1 - 0.82 * (gaussian_filter(dust, 1.0) * band)[..., None])          # el polvo absorbe la luz

    # estrellas: ley de potencias en brillo, color por temperatura
    rng = np.random.default_rng(7)
    star = np.zeros((H, W, 3))
    N = 9000
    sx = rng.integers(0, W, N); sy = rng.integers(0, H, N)
    dens = band[sy, sx]
    keep = rng.random(N) < (0.25 + 0.75 * dens)
    sx, sy = sx[keep], sy[keep]
    b = rng.pareto(2.6, sx.size) * 0.18 + 0.05
    temps = rng.choice(4, sx.size, p=[0.18, 0.5, 0.22, 0.10])
    pal = np.array([[0.75, 0.85, 1.0], [1.0, 0.98, 0.95], [1.0, 0.9, 0.72], [1.0, 0.72, 0.5]])
    np.add.at(star, (sy, sx), (b[:, None] * pal[temps]))
    core = np.stack([gaussian_filter(star[..., c], 0.7) for c in range(3)], -1) * 6
    halo = np.stack([gaussian_filter(star[..., c], 4.0) for c in range(3)], -1) * 9
    em = em + core + halo * 0.6

    col = 1 - np.exp(-em * 1.6)                          # tono fílmico
    col = col * 0.92 + np.array([0.012, 0.012, 0.025])   # negro del espacio, no puro
    img = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(img).save('nebula2.jpg', quality=82, optimize=True, progressive=True)
    Image.fromarray(img).resize((800, 500), Image.LANCZOS).save('nebula2_preview.png')


# ================================================================ AGUA
def water(W=2400, H=1100):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    depth = yy / H                                       # 0 = horizonte, 1 = cerca
    # oleaje anisótropo: ondas alargadas en horizontal, más grandes cerca
    r1 = spectral_noise(512, 2048, 2.2, 201)
    r2 = spectral_noise(512, 2048, 1.6, 202)
    # perspectiva: cerca del horizonte las olas se comprimen en ambos ejes
    sy = (depth ** 0.5) * 900
    sxx = (xx - W / 2) / (depth + 0.06) * 0.06 + 1024
    rip = map_coordinates(r1, [sy, sxx * 0.22], order=1, mode='wrap') * 0.7 \
        + map_coordinates(r2, [sy * 2.1, sxx * 0.4], order=1, mode='wrap') * 0.3
    # cuerpo de agua: casi negro con tinte jade, más claro cerca del horizonte (reflejo del cielo)
    sky = np.exp(-depth * 5) * 0.10
    basec = np.array([0.018, 0.035, 0.036])
    col = basec + sky[..., None] * np.array([0.16, 0.34, 0.34])
    col = col * (0.55 + 0.95 * rip[..., None])
    # columna de luna: ancho que crece con la cercanía
    cx = W / 2
    width = 50 + depth * 520
    colmask = np.exp(-((xx - cx) / width) ** 2)
    glint = smooth(0.54, 0.70, rip) * colmask * 1.15
    soft = colmask * (0.25 + 0.75 * rip) * (1 - depth * 0.5)
    moon = np.array([1.0, 0.92, 0.76])
    col = col + soft[..., None] * moon * 0.26 + glint[..., None] * moon * 1.1
    # niebla fina sobre el horizonte
    col = col + np.exp(-depth * 30)[..., None] * np.array([0.05, 0.07, 0.07])
    col = 1 - np.exp(-col * 1.3)
    img = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(img).save('water.jpg', quality=82, optimize=True, progressive=True)
    Image.fromarray(img).resize((800, 367), Image.LANCZOS).save('water_preview.png')


# ================================================================ PIEDRA
def rock(N=1024, stones=46):
    rng = np.random.default_rng(31)
    # puntos de Voronoi con relajación ligera para piedras de tamaño parejo
    pts = rng.uniform(0, N, (stones, 2))
    for _ in range(2):
        rep = np.concatenate([pts + np.array([dx, dy]) * N for dx in (-1, 0, 1) for dy in (-1, 0, 1)])
        tree = cKDTree(rep)
        g = np.mgrid[0:N:8, 0:N:8].reshape(2, -1).T.astype(float)
        _, idx = tree.query(g)
        idx = idx % stones
        for k in range(stones):
            m = g[idx == k]
            if len(m): pts[k] = m.mean(0)
    rep = np.concatenate([pts + np.array([dx, dy]) * N for dx in (-1, 0, 1) for dy in (-1, 0, 1)])
    tree = cKDTree(rep)

    # bordes irregulares: deformamos las coordenadas antes de preguntar al Voronoi
    wx = (spectral_noise(N, N, 2.6, 301) - 0.5) * 70
    wy = (spectral_noise(N, N, 2.6, 302) - 0.5) * 70
    yy, xx = np.mgrid[0:N, 0:N].astype(float)
    q = np.stack([(yy + wy).ravel() % N, (xx + wx).ravel() % N], 1)
    d, ii = tree.query(q, k=2)
    edge = (d[:, 1] - d[:, 0]).reshape(N, N)            # distancia al borde de la piedra
    sid = (ii[:, 0] % stones).reshape(N, N)
    d0 = d[:, 0].reshape(N, N)

    # tipo de piedra por bloque: basalto, tezontle, andesita
    kind = rng.choice(3, stones, p=[0.5, 0.28, 0.22])
    tint = rng.normal(0, 0.06, stones)
    palette = {0: np.array([0.20, 0.19, 0.18]),   # basalto
               1: np.array([0.29, 0.18, 0.15]),   # tezontle
               2: np.array([0.33, 0.31, 0.28])}   # andesita

    # altura: cada piedra abombada, borde redondeado, mortero hundido
    mortar = 1 - smooth(4, 18, edge)
    dome = smooth(0, 60, edge) ** 0.6
    fine = spectral_noise(N, N, 1.2, 303)
    mid = spectral_noise(N, N, 2.0, 304)
    pores_n = spectral_noise(N, N, 0.9, 305)
    pores = smooth(0.74, 0.80, pores_n)                  # poros (sobre todo en tezontle)
    is_tez = (kind[sid] == 1).astype(float)
    pores = pores * (0.35 + 0.65 * is_tez)
    crack_n = warp(spectral_noise(N, N, 2.3, 306), wx * 0.5, wy * 0.5)
    cracks = smooth(0.965, 0.995, 1 - np.abs(2 * crack_n - 1)) * (1 - mortar)

    stone_n = spectral_noise(N, N, 2.8, 308)
    height = (dome * 0.9 + mid * 0.35 + fine * 0.05 + stone_n * 0.5
              - mortar * 0.55 - pores * 0.25 - cracks * 0.35)
    height = periodic_blur(height, 1.3)
    lam = shade(height, 105, light=(-0.55, -0.75, 0.62))
    occ = ao(height, 10)

    base = np.zeros((N, N, 3))
    for k in range(3):
        m = kind[sid] == k
        base[m] = palette[k]
    base *= (1 + tint[sid])[..., None]
    base *= (0.78 + 0.45 * mid[..., None]) * (0.85 + 0.3 * stone_n[..., None])
    # mortero: arena clara y sucia
    mort_col = np.array([0.30, 0.27, 0.22]) * (0.8 + 0.4 * fine[..., None])
    base = base * (1 - mortar[..., None]) + mort_col * mortar[..., None]
    # líquen/musgo apagado en partes bajas del mortero y bordes
    moss = smooth(0.62, 0.8, spectral_noise(N, N, 2.4, 307)) * (mortar * 0.8 + 0.2)
    base = base * (1 - 0.35 * moss[..., None]) + np.array([0.16, 0.19, 0.12]) * 0.35 * moss[..., None]
    pores_dark = 1 - 0.55 * pores

    light = (0.22 + 1.05 * lam) * occ * pores_dark
    col = base * light[..., None]
    col = 1 - np.exp(-col * 2.1)                         # tono fílmico
    img = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(img).save('rock2.jpg', quality=82, optimize=True, progressive=True)
    Image.fromarray(img).resize((512, 512), Image.LANCZOS).save('rock2_preview.png')


if __name__ == '__main__':
    import sys
    which = sys.argv[1:] or ['nebula', 'water', 'rock']
    for w in which:
        globals()[w]()
        print(w, 'ok')
