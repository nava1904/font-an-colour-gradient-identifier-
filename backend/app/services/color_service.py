"""Color extraction service: dominant colors, gradients, and exact color sampling."""

import numpy as np
import cv2
from PIL import Image
from typing import List, Dict, Any, Optional
from io import BytesIO

from app.utils.color_ops import rgb_to_formats, rgb_to_lab, lab_to_rgb


def preprocess_image(image_bytes: bytes, max_side: int = 1024) -> np.ndarray:
    """Load image, convert to RGB, resize if needed. Returns numpy array (H, W, 3) uint8."""
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape
    if max(h, w) > max_side:
        scale = max_side / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        arr = cv2.resize(arr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return arr


def extract_dominant_colors(
    image_array: np.ndarray,
    k: int = 6,
    max_pixels: int = 400_000,
    use_lab: bool = True,
) -> List[Dict[str, Any]]:
    """
    Extract dominant colors using K-means in LAB space for perceptual accuracy.
    Returns list of dicts with hex, rgb, hsl, percentage.
    """
    h, w, _ = image_array.shape
    pixels = image_array.reshape(-1, 3).astype(np.float32)

    # Subsample if too many pixels
    n_pixels = pixels.shape[0]
    if n_pixels > max_pixels:
        rng = np.random.default_rng(42)
        idx = rng.choice(n_pixels, max_pixels, replace=False)
        pixels = pixels[idx]

    if use_lab:
        # Convert to LAB for perceptual clustering
        pixels_2d = pixels.reshape(-1, 1, 3)
        lab = rgb_to_lab(pixels_2d)
        pixels_for_kmeans = lab.reshape(-1, 3).astype(np.float32)
    else:
        pixels_for_kmeans = pixels

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.2)
    _, labels, centers = cv2.kmeans(
        pixels_for_kmeans,
        k,
        None,
        criteria,
        attempts=3,
        flags=cv2.KMEANS_PP_CENTERS,
    )

    if use_lab:
        centers_rgb = lab_to_rgb(centers.reshape(1, -1, 3)).reshape(-1, 3)
    else:
        centers_rgb = np.clip(centers, 0, 255).astype(np.uint8)

    # Compute percentage per cluster
    unique, counts = np.unique(labels, return_counts=True)
    total = labels.shape[0]
    percentages = {int(u): c / total * 100 for u, c in zip(unique, counts)}

    # Build result sorted by percentage (descending)
    results = []
    for i, rgb in enumerate(centers_rgb):
        pct = percentages.get(i, 0)
        fmt = rgb_to_formats(rgb)
        fmt["percentage"] = round(pct, 1)
        results.append(fmt)

    results.sort(key=lambda x: x["percentage"], reverse=True)
    return results


def detect_gradient_regions(image_array: np.ndarray) -> Optional[np.ndarray]:
    """
    Detect regions with smooth color transitions (gradient-like).
    Returns a mask or None. Uses variance along rows/cols as gradient indicator.
    """
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    # High variance in local patches suggests gradient
    kernel_size = 5
    blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    variance = np.abs(laplacian)
    # Normalize and threshold
    thresh = np.percentile(variance, 75)
    mask = variance > thresh
    return mask.astype(np.uint8)


def extract_gradient_stops(
    image_array: np.ndarray,
    num_stops: int = 5,
) -> Dict[str, Any]:
    """
    Extract color stops from gradient-like regions.
    Samples along horizontal, vertical, or diagonal based on detected gradient direction.
    """
    h, w, _ = image_array.shape

    # Sample along center row, center column, and diagonal
    center_row = image_array[h // 2, :, :]  # (w, 3)
    center_col = image_array[:, w // 2, :]  # (h, 3)

    # Diagonal: top-left to bottom-right
    diag_len = min(h, w)
    diag_indices = np.linspace(0, diag_len - 1, diag_len, dtype=int)
    diagonal = np.array(
        [image_array[i, i, :] for i in range(diag_len)],
        dtype=np.uint8,
    )

    # Compute variance to pick best sampling axis
    row_var = np.var(center_row, axis=0).sum()
    col_var = np.var(center_col, axis=0).sum()
    diag_var = np.var(diagonal, axis=0).sum()

    if diag_var >= row_var and diag_var >= col_var:
        samples = diagonal
        angle = 135
    elif col_var > row_var:
        samples = center_col
        angle = 90
    else:
        samples = center_row
        angle = 0

    # Sample evenly along chosen axis
    n = len(samples)
    indices = np.linspace(0, n - 1, num_stops, dtype=int) if n > 1 else [0]

    stops = []
    for i, idx in enumerate(indices):
        pos = (idx / (n - 1)) * 100 if n > 1 else 50
        rgb = samples[idx]
        fmt = rgb_to_formats(rgb)
        fmt["position"] = round(float(pos), 1)
        stops.append(fmt)

    return {
        "stops": stops,
        "angle": int(angle),
    }


def sample_exact_color(
    image_array: np.ndarray,
    x: int,
    y: int,
) -> Dict[str, Any]:
    """Sample exact color at pixel (x, y). Returns hex, rgb, hsl."""
    h, w, _ = image_array.shape
    x = max(0, min(x, w - 1))
    y = max(0, min(y, h - 1))
    rgb = image_array[y, x, :]
    fmt = rgb_to_formats(rgb)
    fmt["x"] = x
    fmt["y"] = y
    return fmt


def extract_all_colors(
    image_bytes: bytes,
    dominant_k: int = 6,
    gradient_stops: int = 5,
    sample_points: Optional[List[tuple]] = None,
) -> Dict[str, Any]:
    """
    Full color extraction: dominant, gradient, and optional exact samples.
    sample_points: list of (x, y) tuples for exact color sampling.
    """
    arr = preprocess_image(image_bytes)

    dominant = extract_dominant_colors(arr, k=dominant_k)

    gradient = extract_gradient_stops(arr, num_stops=gradient_stops)

    sampled = []
    if sample_points:
        for x, y in sample_points:
            sampled.append(sample_exact_color(arr, x, y))
    else:
        # Default: sample center and corners
        h, w = arr.shape[:2]
        default_points = [
            (w // 2, h // 2),
            (0, 0),
            (w - 1, 0),
            (w - 1, h - 1),
            (0, h - 1),
        ]
        for x, y in default_points:
            sampled.append(sample_exact_color(arr, x, y))

    return {
        "dominant": dominant,
        "gradient": gradient,
        "exact": {"sampled_points": sampled},
    }
