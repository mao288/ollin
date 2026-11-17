"""Texturas procedurales para Tzitzimime: roca prehispánica, friso de grecas y nebulosa."""
import numpy as np
from PIL import Image, ImageDraw

rng = np.random.default_rng(7)


def spectral_noise(h, w, beta, seed):
    """Ruido periódico (tileable) por síntesis espectral."""
    r = np.random.default_rng(seed)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    f = np.sqrt(fx ** 2 + fy ** 2)
    f[0, 0] = 1
    amp = 1 / f ** (beta / 2)
    amp[0, 0] = 0
    phase = r.uniform(0, 2 * np.pi, (h, w))
    spec = amp * np.exp(1j * phase) * r.normal(1, 0.3, (h, w))
    n = np.real(np.fft.ifft2(spec))
    n -= n.min(); n /= n.max()
    return n


def periodic_blur(a, sigma):
    h, w = a.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))


def shade(height, strength, light=(-0.6, -0.7, 0.75)):
    gy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * strength
    gx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * strength
    nz = np.ones_like(height)
    norm = np.sqrt(gx ** 2 + gy ** 2 + nz ** 2)
    nx, ny, nz = -gx / norm, -gy / norm, nz / norm
    L = np.array(light); L = L / np.linalg.norm(L)
    lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    return lam


def ao(height, sigma=12):
    return np.clip(1 - (periodic_blur(height, sigma) - height) * 3.0, 0.35, 1.0)


def lerp_color(t, stops):
    """stops: list of (pos, (r,g,b))."""
    out = np.zeros(t.shape + (3,))
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1)
        k = ((t - p0) / (p1 - p0))[m][:, None]
        out[m] = np.array(c0) * (1 - k) + np.array(c1) * k
    return out


# ---------------------------------------------------------------- ROCA
def rock(N=1024):
    low = spectral_noise(N, N, 3.0, 1)
    mid = spectral_noise(N, N, 2.0, 2)
    fine = spectral_noise(N, N, 1.1, 3)

    # juntas de mampostería irregulares (periódicas: dibujamos en 3x3 y recortamos)
    big = Image.new("L", (N * 3, N * 3), 0)
    d = ImageDraw.Draw(big)
    rows = [0, 190, 400, 560, 770, 1024]
    rr = np.random.default_rng(5)
    for oy in range(3):
        for ox in range(3):
            X, Y = ox * N, oy * N
            for i in range(len(rows) - 1):
                y0, y1 = rows[i], rows[i + 1]
                # junta horizontal ondulada
                pts = [(X + x, Y + y0 + rr.normal(0, 3)) for x in range(0, N + 64, 64)]
                d.line(pts, fill=255, width=9)
                x = rr.integers(0, 200) if i % 2 else 0
                while x < N:
                    jx = X + x + rr.normal(0, 4)
                    d.line([(jx, Y + y0), (jx + rr.normal(0, 6), Y + y1)], fill=255, width=9)
                    x += rr.integers(230, 380)
    joints = np.asarray(big, dtype=float)[N:2 * N, N:2 * N] / 255
    # erosión: las juntas se comen el borde de forma irregular
    joints = periodic_blur(joints, 3.0)
    chip = spectral_noise(N, N, 1.6, 9)
    joints = np.clip(joints * 1.6 + (chip - 0.55) * joints * 2.2, 0, 1)

    # grecas talladas, pocas y gastadas
    carve = Image.new("L", (N, N), 0)
    dc = ImageDraw.Draw(carve)
    def fret(x, y, s):
        p = [(0, 4), (1, 4), (1, 3), (2, 3), (2, 2), (3, 2), (3, 1), (4, 1), (4, 0), (6, 0), (6, 1),
             (5, 1), (5, 2), (4, 2), (4, 3), (3, 3), (3, 4), (2, 4), (2, 5), (0, 5)]
        dc.polygon([(x + a * s, y + b * s) for a, b in p], fill=255)
    pass
    for cx, cy, r in [(860, 300, 30), (460, 470, 26)]:
        dc.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=9)
        dc.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=255)
    carve = periodic_blur(np.asarray(carve, float) / 255, 1.6)
    carve *= 0.55 + 0.45 * (chip > 0.35)

    height = 0.9 * low + 0.45 * mid + 0.12 * fine - 0.55 * joints - 0.22 * carve
    lam = shade(height, 160)
    occ = ao(height, 14)

    tone = periodic_blur(spectral_noise(N, N, 2.6, 4), 2)
    base = lerp_color(tone, [
        (0.0, (58, 50, 42)),     # piedra oscura
        (0.45, (92, 78, 60)),    # piedra volcánica cálida
        (0.75, (104, 86, 58)),   # ocre
        (1.0, (70, 76, 62)),     # musgo/jade apagado
    ])
    # rastros de pigmento rojo (grana) en las tallas
    pigment = np.clip(carve * 1.4, 0, 1)[..., None] * (spectral_noise(N, N, 1.8, 12) > 0.45)[..., None]
    base = base * (1 - pigment * 0.55) + np.array([128, 40, 30]) * pigment * 0.55

    light = (0.25 + 0.95 * lam) * occ
    img = np.clip(base * light[..., None], 0, 255).astype(np.uint8)
    Image.fromarray(img).save("rock.jpg", quality=82, optimize=True, progressive=True)
    Image.fromarray(img).resize((512, 512)).save("rock_preview.png")


# ---------------------------------------------------------------- FRISO
def frieze(W=1200, H=200):
    noise = spectral_noise(H, W, 2.0, 21)
    fine = spectral_noise(H, W, 1.1, 22)
    relief = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(relief)
    # bandas
    d.rectangle([0, 18, W, 30], fill=255)
    d.rectangle([0, H - 30, W, H - 18], fill=255)
    # xicalcoliuhqui (greca escalonada en espiral) en relieve, periodo 150
    s = 14
    shape = [(0, 8), (2, 8), (2, 6), (4, 6), (4, 4), (6, 4), (6, 2), (8, 2), (8, 0), (10, 0),
             (10, 6), (8, 6), (8, 4), (9, 4), (9, 2), (8.5, 2), (8.5, 1.5), (7, 1.5) ,(7,3), (5, 3), (5, 5), (3, 5), (3, 7), (1, 7), (1, 9.5), (0, 9.5)]
    for x in range(0, W, 150):
        d.polygon([(x + 5 + a * s, 42 + b * s * 0.85) for a, b in shape], fill=255)
    rel = periodic_blur(np.asarray(relief, float) / 255, 1.4)
    rel *= 0.75 + 0.25 * (spectral_noise(H, W, 1.5, 23) > 0.3)
    height = 0.35 * noise + 0.1 * fine + 0.55 * rel
    lam = shade(height, 120, light=(-0.5, -0.8, 0.7))
    occ = ao(height, 8)
    base = np.array([84, 79, 72]) * (0.85 + 0.3 * noise[..., None])
    img = np.clip(base * ((0.2 + 1.0 * lam) * occ)[..., None], 0, 255).astype(np.uint8)
    Image.fromarray(img).save("frieze.jpg", quality=84, optimize=True, progressive=True)


# ---------------------------------------------------------------- NEBULOSA
def nebula(W=1600, H=1000):
    a = spectral_noise(H, W, 3.2, 31)
    b = spectral_noise(H, W, 2.4, 32)
    c = spectral_noise(H, W, 2.8, 33)
    yy, xx = np.mgrid[0:H, 0:W]
    # densidad diagonal, como un brazo de vía láctea
    band = np.exp(-((yy / H - 0.15 - 0.55 * xx / W) ** 2) / 0.05)
    jade = np.clip((a - 0.45) * 2.2, 0, 1) * band
    ember = np.clip((b - 0.52) * 2.8, 0, 1) * band * 0.95
    dust = np.clip((0.5 - c) * 2.0, 0, 1) * band
    void = np.array([6, 6, 12])
    col = (void
           + jade[..., None] * np.array([34, 82, 74])
           + ember[..., None] * np.array([120, 52, 18])
           + band[..., None] * np.array([10, 9, 14]))
    col *= (1 - 0.6 * dust[..., None])
    img = np.clip(col, 0, 255).astype(np.uint8)
    Image.fromarray(img).save("nebula.jpg", quality=80, optimize=True, progressive=True)
    Image.fromarray(img).resize((800, 500)).save("nebula_preview.png")


rock(); frieze(); nebula()
print("ok")
