"""Gráficos de control: X-R, X-S (variables) y p, np, c, u (atributos).

Cada función recibe los datos y devuelve un dict con:
- centerline (CL)
- upper_control_limit (UCL)
- lower_control_limit (LCL)
- points: lista de valores graficados por subgrupo
- subgroups: índices
- out_of_control: índices de puntos fuera de los límites
- rules_violations: violaciones de las reglas de Nelson
"""
from __future__ import annotations
import numpy as np
from .constants import get_constants_xr, get_constants_xs


def _nelson_rules(points: list[float], cl: float, ucl: float, lcl: float) -> list[dict]:
    """Aplica las 8 reglas de Nelson para detección de patrones."""
    if ucl == lcl:
        return []
    sigma = (ucl - cl) / 3.0
    if sigma == 0:
        return []
    n = len(points)
    p = np.array(points)
    violations = []

    # Regla 1: 1 punto fuera de 3 sigma (LCL/UCL)
    for i in range(n):
        if p[i] > ucl or p[i] < lcl:
            violations.append({"point": i + 1, "rule": 1, "desc": "Punto fuera de los límites de control (±3σ)"})

    # Regla 2: 9 puntos consecutivos del mismo lado de CL
    for i in range(8, n):
        window = p[i - 8 : i + 1]
        if np.all(window > cl) or np.all(window < cl):
            violations.append({"point": i + 1, "rule": 2, "desc": "9 puntos consecutivos del mismo lado de la línea central"})

    # Regla 3: 6 puntos consecutivos crecientes o decrecientes
    for i in range(5, n):
        window = p[i - 5 : i + 1]
        diffs = np.diff(window)
        if np.all(diffs > 0) or np.all(diffs < 0):
            violations.append({"point": i + 1, "rule": 3, "desc": "6 puntos consecutivos en tendencia"})

    # Regla 4: 14 puntos alternando arriba/abajo
    for i in range(13, n):
        window = p[i - 13 : i + 1] - cl
        signs = np.sign(window)
        if np.all(np.diff(signs) != 0) and not np.any(signs == 0):
            violations.append({"point": i + 1, "rule": 4, "desc": "14 puntos consecutivos alternando arriba/abajo"})

    # Regla 5: 2 de 3 puntos > 2σ del mismo lado
    for i in range(2, n):
        window = p[i - 2 : i + 1]
        above = np.sum(window > cl + 2 * sigma)
        below = np.sum(window < cl - 2 * sigma)
        if above >= 2 or below >= 2:
            violations.append({"point": i + 1, "rule": 5, "desc": "2 de 3 puntos consecutivos más allá de 2σ del mismo lado"})

    # Regla 6: 4 de 5 puntos > 1σ del mismo lado
    for i in range(4, n):
        window = p[i - 4 : i + 1]
        above = np.sum(window > cl + sigma)
        below = np.sum(window < cl - sigma)
        if above >= 4 or below >= 4:
            violations.append({"point": i + 1, "rule": 6, "desc": "4 de 5 puntos consecutivos más allá de 1σ del mismo lado"})

    return violations


def x_bar_r_chart(subgroups: list[list[float]]) -> dict:
    """Gráfico X̄-R: requiere subgrupos de igual tamaño (2-25)."""
    if len(subgroups) < 2:
        raise ValueError("Se requieren al menos 2 subgrupos.")
    n = len(subgroups[0])
    for i, sg in enumerate(subgroups):
        if len(sg) != n:
            raise ValueError(f"El subgrupo {i + 1} tiene tamaño distinto ({len(sg)} vs {n}).")

    arr = np.array(subgroups, dtype=float)
    means = arr.mean(axis=1)
    ranges = arr.max(axis=1) - arr.min(axis=1)
    x_bar_bar = float(means.mean())
    r_bar = float(ranges.mean())

    c = get_constants_xr(n)

    # Gráfico X̄
    x_ucl = x_bar_bar + c["A2"] * r_bar
    x_lcl = x_bar_bar - c["A2"] * r_bar

    # Gráfico R
    r_ucl = c["D4"] * r_bar
    r_lcl = c["D3"] * r_bar

    sigma_est = r_bar / c["d2"] if c["d2"] > 0 else 0.0

    return {
        "type": "X-R",
        "subgroup_size": n,
        "n_subgroups": len(subgroups),
        "sigma_estimated": sigma_est,
        "x_chart": {
            "title": "Gráfico X̄ (Media)",
            "subgroups": list(range(1, len(subgroups) + 1)),
            "points": means.tolist(),
            "cl": x_bar_bar,
            "ucl": float(x_ucl),
            "lcl": float(x_lcl),
            "out_of_control": [i + 1 for i, v in enumerate(means) if v > x_ucl or v < x_lcl],
            "rules_violations": _nelson_rules(means.tolist(), x_bar_bar, x_ucl, x_lcl),
        },
        "r_chart": {
            "title": "Gráfico R (Rango)",
            "subgroups": list(range(1, len(subgroups) + 1)),
            "points": ranges.tolist(),
            "cl": r_bar,
            "ucl": float(r_ucl),
            "lcl": float(r_lcl),
            "out_of_control": [i + 1 for i, v in enumerate(ranges) if v > r_ucl or v < r_lcl],
            "rules_violations": _nelson_rules(ranges.tolist(), r_bar, r_ucl, r_lcl),
        },
    }


def x_bar_s_chart(subgroups: list[list[float]]) -> dict:
    """Gráfico X̄-S: recomendado para n ≥ 10."""
    if len(subgroups) < 2:
        raise ValueError("Se requieren al menos 2 subgrupos.")
    n = len(subgroups[0])
    for i, sg in enumerate(subgroups):
        if len(sg) != n:
            raise ValueError(f"El subgrupo {i + 1} tiene tamaño distinto ({len(sg)} vs {n}).")

    arr = np.array(subgroups, dtype=float)
    means = arr.mean(axis=1)
    stds = arr.std(axis=1, ddof=1)
    x_bar_bar = float(means.mean())
    s_bar = float(stds.mean())

    c = get_constants_xs(n)

    x_ucl = x_bar_bar + c["A3"] * s_bar
    x_lcl = x_bar_bar - c["A3"] * s_bar
    s_ucl = c["B4"] * s_bar
    s_lcl = c["B3"] * s_bar

    sigma_est = s_bar / c["c4"] if c["c4"] > 0 else 0.0

    return {
        "type": "X-S",
        "subgroup_size": n,
        "n_subgroups": len(subgroups),
        "sigma_estimated": sigma_est,
        "x_chart": {
            "title": "Gráfico X̄ (Media)",
            "subgroups": list(range(1, len(subgroups) + 1)),
            "points": means.tolist(),
            "cl": x_bar_bar,
            "ucl": float(x_ucl),
            "lcl": float(x_lcl),
            "out_of_control": [i + 1 for i, v in enumerate(means) if v > x_ucl or v < x_lcl],
            "rules_violations": _nelson_rules(means.tolist(), x_bar_bar, x_ucl, x_lcl),
        },
        "s_chart": {
            "title": "Gráfico S (Desviación Estándar)",
            "subgroups": list(range(1, len(subgroups) + 1)),
            "points": stds.tolist(),
            "cl": s_bar,
            "ucl": float(s_ucl),
            "lcl": float(s_lcl),
            "out_of_control": [i + 1 for i, v in enumerate(stds) if v > s_ucl or v < s_lcl],
            "rules_violations": _nelson_rules(stds.tolist(), s_bar, s_ucl, s_lcl),
        },
    }


def p_chart(defectives: list[int], sample_sizes: list[int]) -> dict:
    """Gráfico p: proporción de unidades defectuosas. Tamaños variables permitidos."""
    if len(defectives) != len(sample_sizes):
        raise ValueError("Defectuosos y tamaños deben tener la misma longitud.")
    if len(defectives) < 2:
        raise ValueError("Se requieren al menos 2 subgrupos.")

    d = np.array(defectives, dtype=float)
    n = np.array(sample_sizes, dtype=float)
    p = d / n
    p_bar = float(d.sum() / n.sum())
    # Límites variables si los tamaños varían
    sigma_p = np.sqrt(p_bar * (1 - p_bar) / n)
    ucl = p_bar + 3 * sigma_p
    lcl = np.maximum(p_bar - 3 * sigma_p, 0)

    # Si los tamaños son constantes, usamos UCL/LCL escalares
    uniform = bool(np.all(n == n[0]))
    if uniform:
        ucl_val = float(ucl[0])
        lcl_val = float(lcl[0])
        violations = _nelson_rules(p.tolist(), p_bar, ucl_val, lcl_val)
    else:
        ucl_val = ucl.tolist()
        lcl_val = lcl.tolist()
        violations = []
        for i, v in enumerate(p):
            if v > ucl[i] or v < lcl[i]:
                violations.append({"point": i + 1, "rule": 1, "desc": "Punto fuera de los límites de control"})

    out_of_control = []
    for i, v in enumerate(p):
        if v > (ucl[i] if not uniform else ucl_val) or v < (lcl[i] if not uniform else lcl_val):
            out_of_control.append(i + 1)

    return {
        "type": "p",
        "title": "Gráfico p (proporción de defectuosos)",
        "subgroups": list(range(1, len(defectives) + 1)),
        "points": p.tolist(),
        "cl": p_bar,
        "ucl": ucl_val,
        "lcl": lcl_val,
        "uniform_limits": uniform,
        "out_of_control": out_of_control,
        "rules_violations": violations,
        "sample_sizes": sample_sizes,
    }


def np_chart(defectives: list[int], sample_size: int) -> dict:
    """Gráfico np: número de defectuosos. Tamaño de subgrupo CONSTANTE."""
    if len(defectives) < 2:
        raise ValueError("Se requieren al menos 2 subgrupos.")
    d = np.array(defectives, dtype=float)
    n = sample_size
    p_bar = float(d.sum() / (n * len(d)))
    np_bar = n * p_bar
    sigma = np.sqrt(np_bar * (1 - p_bar))
    ucl = np_bar + 3 * sigma
    lcl = max(np_bar - 3 * sigma, 0)
    return {
        "type": "np",
        "title": "Gráfico np (número de defectuosos)",
        "subgroups": list(range(1, len(defectives) + 1)),
        "points": d.tolist(),
        "cl": float(np_bar),
        "ucl": float(ucl),
        "lcl": float(lcl),
        "uniform_limits": True,
        "out_of_control": [i + 1 for i, v in enumerate(d) if v > ucl or v < lcl],
        "rules_violations": _nelson_rules(d.tolist(), float(np_bar), float(ucl), float(lcl)),
        "sample_size": n,
    }


def c_chart(defects: list[int]) -> dict:
    """Gráfico c: número de defectos por unidad. Tamaño de muestra constante."""
    if len(defects) < 2:
        raise ValueError("Se requieren al menos 2 muestras.")
    arr = np.array(defects, dtype=float)
    c_bar = float(arr.mean())
    sigma = np.sqrt(c_bar)
    ucl = c_bar + 3 * sigma
    lcl = max(c_bar - 3 * sigma, 0)
    return {
        "type": "c",
        "title": "Gráfico c (defectos por unidad)",
        "subgroups": list(range(1, len(defects) + 1)),
        "points": arr.tolist(),
        "cl": c_bar,
        "ucl": float(ucl),
        "lcl": float(lcl),
        "uniform_limits": True,
        "out_of_control": [i + 1 for i, v in enumerate(arr) if v > ucl or v < lcl],
        "rules_violations": _nelson_rules(arr.tolist(), c_bar, float(ucl), float(lcl)),
    }


def u_chart(defects: list[int], sample_sizes: list[float]) -> dict:
    """Gráfico u: defectos por unidad cuando el tamaño de muestra varía."""
    if len(defects) != len(sample_sizes):
        raise ValueError("Defectos y tamaños deben tener la misma longitud.")
    if len(defects) < 2:
        raise ValueError("Se requieren al menos 2 subgrupos.")
    d = np.array(defects, dtype=float)
    n = np.array(sample_sizes, dtype=float)
    u = d / n
    u_bar = float(d.sum() / n.sum())
    sigma_u = np.sqrt(u_bar / n)
    ucl = u_bar + 3 * sigma_u
    lcl = np.maximum(u_bar - 3 * sigma_u, 0)

    uniform = bool(np.all(n == n[0]))
    if uniform:
        ucl_val = float(ucl[0])
        lcl_val = float(lcl[0])
        violations = _nelson_rules(u.tolist(), u_bar, ucl_val, lcl_val)
    else:
        ucl_val = ucl.tolist()
        lcl_val = lcl.tolist()
        violations = []
        for i, v in enumerate(u):
            if v > ucl[i] or v < lcl[i]:
                violations.append({"point": i + 1, "rule": 1, "desc": "Punto fuera de los límites de control"})

    out_of_control = []
    for i, v in enumerate(u):
        if v > (ucl[i] if not uniform else ucl_val) or v < (lcl[i] if not uniform else lcl_val):
            out_of_control.append(i + 1)

    return {
        "type": "u",
        "title": "Gráfico u (defectos por unidad - tamaño variable)",
        "subgroups": list(range(1, len(defects) + 1)),
        "points": u.tolist(),
        "cl": u_bar,
        "ucl": ucl_val,
        "lcl": lcl_val,
        "uniform_limits": uniform,
        "out_of_control": out_of_control,
        "rules_violations": violations,
        "sample_sizes": sample_sizes,
    }
