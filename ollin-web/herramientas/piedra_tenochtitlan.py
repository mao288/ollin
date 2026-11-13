"""Muro de Tenochtitlan: hiladas de piedra de corte burdo (tezontle, andesitas, basalto),
mortero de cal con arena volcánica y restos de estuco. Tileable en ambos ejes."""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'texturas_base.py')).read())

def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def build(N=1024, seed=5):
    rng = np.random.default_rng(seed)
    # ---- hiladas: alturas que suman N
    rows = []
    while sum(rows) < N - 150:
        rows.append(int(rng.integers(80, 175)))
    rows.append(N - sum(rows))
    ry = np.concatenate([[0], np.cumsum(rows)])
    # ---- piedras por hilada: anchos que suman N, con desfase
    stones = []   # por hilada: (offset, bordes)
    for r in rows:
        ws = []
        while sum(ws) < N - 260:
            ws.append(int(rng.integers(int(r * 0.8), int(r * 2.0))))
        ws.append(N - sum(ws))
        stones.append((int(rng.integers(0, N)), np.concatenate([[0], np.cumsum(ws)])))

    yy, xx = np.mgrid[0:N, 0:N].astype(float)
    wx = (spectral_noise(N, N, 2.4, 401) - 0.5) * 46 + (spectral_noise(N, N, 1.7, 402) - 0.5) * 16
    wy = (spectral_noise(N, N, 2.4, 403) - 0.5) * 34 + (spectral_noise(N, N, 1.7, 404) - 0.5) * 14
    X = (xx + wx) % N; Y = (yy + wy) % N

    ri = np.clip(np.searchsorted(ry, Y, side='right') - 1, 0, len(rows) - 1)
    dist = np.zeros((N, N)); sid = np.zeros((N, N), int)
    sid_base = np.cumsum([0] + [len(b) - 1 for _, b in stones])
    for r in range(len(rows)):
        m = ri == r
        off, b = stones[r]
        xl = (X[m] - off) % N
        k = np.clip(np.searchsorted(b, xl, side='right') - 1, 0, len(b) - 2)
        dx = np.minimum(xl - b[k], b[k + 1] - xl)
        dy = np.minimum(Y[m] - ry[r], ry[r + 1] - Y[m])
        # esquinas redondeadas/despostilladas: mínimo suave
        kk = 14.0
        d = -kk * np.log(np.exp(-dx / kk) + np.exp(-dy / kk))
        dist[m] = d; sid[m] = sid_base[r] + k
    nst = sid_base[-1]

    chip = spectral_noise(N, N, 1.9, 405)
    dist = dist - (chip - 0.5) * 18 - (spectral_noise(N, N, 1.3, 414) - 0.5) * 6                          # bordes mordidos

    # ---- material por piedra (proporciones del Templo Mayor)
    kinds = rng.choice(5, nst, p=[0.46, 0.10, 0.20, 0.16, 0.08])
    # 0 tezontle rojo, 1 tezontle negro, 2 andesita de lamprobolita (rosácea/violácea),
    # 3 andesita de piroxenos (gris), 4 basalto
    pal = np.array([[0.33, 0.18, 0.15], [0.15, 0.12, 0.12], [0.38, 0.32, 0.33],
                    [0.35, 0.34, 0.32], [0.19, 0.19, 0.19]])
    K = kinds[sid]
    var = rng.normal(0, 0.07, nst)[sid]

    mid = spectral_noise(N, N, 2.1, 406)
    fine = spectral_noise(N, N, 1.1, 407)
    face = spectral_noise(N, N, 2.8, 408)

    # ---- vesículas del tezontle (y pocas en andesita)
    pm = Image.new('L', (N, N), 0); dr = ImageDraw.Draw(pm)
    for _ in range(14000):
        x, y = rng.uniform(0, N, 2); r = rng.gamma(1.6, 1.4) + 0.6
        for ox in (-N, 0, N):
            for oy in (-N, 0, N):
                cx, cy = x + ox, y + oy
                if -10 < cx < N + 10 and -10 < cy < N + 10:
                    dr.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=255)
    pores = periodic_blur(np.asarray(pm, float) / 255, 0.6)
    pore_w = np.select([K == 0, K == 1, K == 2, K == 3], [1.0, 1.0, 0.25, 0.18], 0.1)
    pores = pores * pore_w

    # ---- mortero de cal con arena volcánica
    mortar = 1 - smooth(5, 19, dist)
    grains = smooth(0.62, 0.7, spectral_noise(N, N, 0.6, 409))

    # ---- restos de estuco (cal) en parches, agrietados
    st_n = spectral_noise(N, N, 3.2, 410)
    stucco = smooth(0.63, 0.68, st_n)
    cr = 1 - np.abs(2 * spectral_noise(N, N, 2.0, 411) - 1)
    st_cracks = smooth(0.97, 0.995, cr) * stucco

    dome = smooth(0, 42, dist) ** 0.6
    height = (dome * 0.8 + face * 0.45 + mid * 0.25 + fine * 0.06
              - mortar * 0.6 + grains * mortar * 0.05
              - pores * 0.35
              + stucco * 0.18 - st_cracks * 0.12)
    height = periodic_blur(height, 0.9)
    lam = shade(height, 115, light=(-0.55, -0.75, 0.62))
    occ = ao(height, 9)

    base = pal[K] * (1 + var)[..., None]
    # moteado: el tezontle rojo tiene vetas negras, la andesita rosácea manchas violáceas
    mott = spectral_noise(N, N, 1.8, 412)
    base = np.where((K == 0)[..., None], base * (0.75 + 0.5 * mott[..., None]) * (1 - 0.35 * smooth(0.65, 0.8, mott))[..., None], base)
    base = base * (0.82 + 0.36 * face[..., None])
    mort_col = np.array([0.40, 0.37, 0.32]) * (0.85 + 0.3 * fine[..., None]) * (1 - 0.3 * grains[..., None])
    base = base * (1 - mortar[..., None]) + mort_col * mortar[..., None]
    # estuco: cal crema con suciedad y rastros mínimos de pigmento rojo
    pig = smooth(0.6, 0.75, spectral_noise(N, N, 2.6, 413)) * 0.35
    st_col = np.array([0.66, 0.62, 0.55]) * (0.8 + 0.3 * mid[..., None])
    st_col = st_col * (1 - pig[..., None]) + np.array([0.55, 0.22, 0.16]) * pig[..., None]
    base = base * (1 - stucco[..., None]) + st_col * stucco[..., None]
    # mugre que escurre hacia abajo dentro de cada hilada
    rowpos = (Y - ry[ri]) / np.array(rows)[ri]
    grime = 1 - 0.18 * rowpos * (1 - stucco)

    light = (0.2 + 1.05 * lam) * occ * (1 - 0.6 * pores) * grime
    col = 1 - np.exp(-base * light[..., None] * 2.0)
    img = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(img).save('rock3.jpg', quality=82, optimize=True, progressive=True)
    Image.fromarray(img).resize((512, 512), Image.LANCZOS).save('rock3_preview.png')
    Image.fromarray(img).crop((200, 200, 712, 712)).save('rock3_crop.png')

build(); print('ok')
