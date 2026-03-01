"""Color conversion utilities, ΔE2000 perceptual distance, and format helpers."""

import numpy as np
from typing import Tuple, List


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB (0-255) to HEX string."""
    return "#{:02X}{:02X}{:02X}".format(
        int(np.clip(r, 0, 255)),
        int(np.clip(g, 0, 255)),
        int(np.clip(b, 0, 255)),
    )


def rgb_to_hsl(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """Convert RGB (0-255) to HSL (h: 0-360, s: 0-100, l: 0-100)."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2.0

    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6

    return (h * 360, s * 100, l * 100)


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Convert RGB (0-255) to LAB color space. Input shape: (N, 3) or (H, W, 3)."""
    from skimage.color import rgb2lab

    if rgb.max() > 1.0:
        rgb = rgb.astype(np.float64) / 255.0
    lab = rgb2lab(rgb)
    return lab


def lab_to_rgb(lab: np.ndarray) -> np.ndarray:
    """Convert LAB to RGB (0-255). Input shape: (N, 3) or (H, W, 3)."""
    from skimage.color import lab2rgb

    rgb = lab2rgb(lab)
    rgb = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    return rgb


def delta_e_ciede2000(lab1: np.ndarray, lab2: np.ndarray) -> np.ndarray:
    """
    Compute ΔE2000 (CIE2000) perceptual color difference.
    lab1, lab2: arrays of shape (N, 3) with L, a, b values.
    Returns array of shape (N,) or scalar.
    """
    from skimage.color import deltaE_ciede2000 as sk_delta_e

    return sk_delta_e(lab1, lab2)


def rgb_to_formats(rgb: np.ndarray) -> dict:
    """Convert single RGB array [r,g,b] to hex, rgb, hsl dict."""
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    h, s, l_val = rgb_to_hsl(r, g, b)
    return {
        "hex": rgb_to_hex(r, g, b),
        "rgb": [r, g, b],
        "hsl": [round(h, 1), round(s, 1), round(l_val, 1)],
    }


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Compute relative luminance for WCAG contrast."""
    r, g, b = rgb

    def _srgb_to_lin(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    R = _srgb_to_lin(r)
    G = _srgb_to_lin(g)
    B = _srgb_to_lin(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """Compute WCAG contrast ratio between two colors."""
    L1 = relative_luminance(rgb1)
    L2 = relative_luminance(rgb2)
    L1, L2 = (L1, L2) if L1 >= L2 else (L2, L1)
    return (L1 + 0.05) / (L2 + 0.05)


def get_accessible_text_color(rgb: Tuple[int, int, int]) -> str:
    """Return 'black' or 'white' for best contrast on given background."""
    black = (0, 0, 0)
    white = (255, 255, 255)
    return "black" if contrast_ratio(rgb, white) > contrast_ratio(rgb, black) else "white"
