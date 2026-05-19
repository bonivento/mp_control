"""Pruebas de normalidad: Shapiro-Wilk, Anderson-Darling, D'Agostino."""
from __future__ import annotations
import numpy as np
from scipy import stats


def shapiro_wilk(data: list[float]) -> dict:
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) < 3:
        return {"test": "Shapiro-Wilk", "error": "Se requieren al menos 3 datos."}
    if len(arr) > 5000:
        arr = arr[:5000]
    stat, p = stats.shapiro(arr)
    return {
        "test": "Shapiro-Wilk",
        "statistic": float(stat),
        "p_value": float(p),
        "alpha": 0.05,
        "normal": bool(p > 0.05),
        "interpretation": (
            "Los datos siguen una distribución normal (no se rechaza H0)."
            if p > 0.05
            else "Los datos NO siguen una distribución normal (se rechaza H0)."
        ),
    }


def anderson_darling(data: list[float]) -> dict:
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) < 8:
        return {"test": "Anderson-Darling", "error": "Se requieren al menos 8 datos."}
    result = stats.anderson(arr, dist="norm")
    critical_5 = float(result.critical_values[2])  # 5% nivel
    normal = bool(result.statistic < critical_5)
    return {
        "test": "Anderson-Darling",
        "statistic": float(result.statistic),
        "critical_values": [float(v) for v in result.critical_values],
        "significance_levels": [float(s) for s in result.significance_level],
        "alpha": 0.05,
        "normal": normal,
        "interpretation": (
            "Los datos siguen una distribución normal (estadístico < valor crítico al 5%)."
            if normal
            else "Los datos NO siguen una distribución normal (estadístico ≥ valor crítico al 5%)."
        ),
    }


def dagostino(data: list[float]) -> dict:
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) < 20:
        return {"test": "D'Agostino-Pearson", "error": "Se requieren al menos 20 datos."}
    stat, p = stats.normaltest(arr)
    return {
        "test": "D'Agostino-Pearson",
        "statistic": float(stat),
        "p_value": float(p),
        "alpha": 0.05,
        "normal": bool(p > 0.05),
        "interpretation": (
            "Los datos siguen una distribución normal."
            if p > 0.05
            else "Los datos NO siguen una distribución normal."
        ),
    }


def qq_plot_data(data: list[float]) -> dict:
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    arr_sorted = np.sort(arr)
    n = len(arr_sorted)
    if n == 0:
        return {"theoretical": [], "sample": []}
    probs = (np.arange(1, n + 1) - 0.5) / n
    theoretical = stats.norm.ppf(probs)
    return {
        "theoretical": theoretical.tolist(),
        "sample": arr_sorted.tolist(),
    }


def histogram_data(data: list[float], bins: int = 10) -> dict:
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return {"bins": [], "counts": [], "edges": []}
    counts, edges = np.histogram(arr, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    # Curva normal teórica superpuesta
    mu, sigma = float(np.mean(arr)), float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    x_curve = np.linspace(arr.min(), arr.max(), 100) if len(arr) > 1 else np.array([])
    y_curve = (
        stats.norm.pdf(x_curve, mu, sigma) * len(arr) * (edges[1] - edges[0])
        if sigma > 0 else np.zeros_like(x_curve)
    )
    return {
        "counts": counts.tolist(),
        "edges": edges.tolist(),
        "centers": centers.tolist(),
        "curve_x": x_curve.tolist() if len(x_curve) else [],
        "curve_y": y_curve.tolist() if len(x_curve) else [],
        "mean": mu,
        "std": sigma,
    }


def run_all_normality_tests(data: list[float]) -> dict:
    return {
        "shapiro": shapiro_wilk(data),
        "anderson": anderson_darling(data),
        "dagostino": dagostino(data),
        "qq_plot": qq_plot_data(data),
        "histogram": histogram_data(data),
        "descriptive": descriptive_stats(data),
    }


def descriptive_stats(data: list[float]) -> dict:
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return {}
    return {
        "n": int(len(arr)),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
        "var": float(np.var(arr, ddof=1)) if len(arr) > 1 else 0.0,
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "range": float(np.max(arr) - np.min(arr)),
        "q1": float(np.percentile(arr, 25)),
        "q3": float(np.percentile(arr, 75)),
        "iqr": float(np.percentile(arr, 75) - np.percentile(arr, 25)),
        "skewness": float(stats.skew(arr)) if len(arr) > 2 else 0.0,
        "kurtosis": float(stats.kurtosis(arr)) if len(arr) > 3 else 0.0,
        "cv": float(np.std(arr, ddof=1) / np.mean(arr) * 100) if np.mean(arr) != 0 and len(arr) > 1 else 0.0,
    }
