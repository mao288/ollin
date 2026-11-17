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


