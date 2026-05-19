"""Índices de capacidad del proceso: Cp, Cpk, Pp, Ppk."""
from __future__ import annotations
import numpy as np
from .constants import d2 as D2_CONST, c4 as C4_CONST


def capability_indices(
    data: list[float],
    lsl: float | None,
    usl: float | None,
    subgroup_size: int | None = None,
    sigma_method: str = "overall",
) -> dict:
    """Calcula índices de capacidad.

    - Cp, Cpk usan sigma_within (estimado a partir de R̄/d2 o S̄/c4 si hay subgrupos).
    - Pp, Ppk usan sigma_overall (desviación estándar muestral).

    Args:
        data: lista plana de mediciones, o lista de listas (subgrupos).
        lsl: límite inferior de especificación.
        usl: límite superior de especificación.
        subgroup_size: si data es plano y se conocen subgrupos.
        sigma_method: 'overall' (default), 'within_R' o 'within_S'.
    """
    if lsl is None and usl is None:
        return {"error": "Se requiere al menos un límite de especificación (LSL o USL)."}

    # Aplanar
    if data and isinstance(data[0], (list, tuple)):
        subgroups = [list(map(float, sg)) for sg in data]
        flat = [v for sg in subgroups for v in sg]
        n = len(subgroups[0])
    else:
        flat = list(map(float, data))
        subgroups = None
        n = subgroup_size

    arr = np.array(flat, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) < 2:
        return {"error": "Se requieren al menos 2 datos."}

    mean = float(arr.mean())
    sigma_overall = float(arr.std(ddof=1))

    # Sigma within
    sigma_within = sigma_overall
    if subgroups and n and 2 <= n <= 25:
        sgs = np.array(subgroups, dtype=float)
        if sigma_method == "within_S" or n >= 10:
            s_bar = float(sgs.std(axis=1, ddof=1).mean())
            sigma_within = s_bar / C4_CONST[n] if C4_CONST[n] > 0 else sigma_overall
        else:
            r_bar = float((sgs.max(axis=1) - sgs.min(axis=1)).mean())
            sigma_within = r_bar / D2_CONST[n] if D2_CONST[n] > 0 else sigma_overall

    result = {
        "mean": mean,
        "sigma_overall": sigma_overall,
        "sigma_within": sigma_within,
        "lsl": lsl,
        "usl": usl,
        "n": int(len(arr)),
    }

    # Cp y Pp requieren ambos límites
    if lsl is not None and usl is not None:
        if sigma_within > 0:
            result["Cp"] = (usl - lsl) / (6 * sigma_within)
        if sigma_overall > 0:
            result["Pp"] = (usl - lsl) / (6 * sigma_overall)

    # Cpk y Ppk
    cpk_lower = (mean - lsl) / (3 * sigma_within) if (lsl is not None and sigma_within > 0) else None
    cpk_upper = (usl - mean) / (3 * sigma_within) if (usl is not None and sigma_within > 0) else None
    ppk_lower = (mean - lsl) / (3 * sigma_overall) if (lsl is not None and sigma_overall > 0) else None
    ppk_upper = (usl - mean) / (3 * sigma_overall) if (usl is not None and sigma_overall > 0) else None

    if cpk_lower is not None and cpk_upper is not None:
        result["Cpk"] = min(cpk_lower, cpk_upper)
    elif cpk_lower is not None:
        result["Cpk"] = cpk_lower
    elif cpk_upper is not None:
        result["Cpk"] = cpk_upper

    if ppk_lower is not None and ppk_upper is not None:
        result["Ppk"] = min(ppk_lower, ppk_upper)
    elif ppk_lower is not None:
        result["Ppk"] = ppk_lower
    elif ppk_upper is not None:
        result["Ppk"] = ppk_upper

    # Interpretación
    if "Cpk" in result:
        cpk = result["Cpk"]
        if cpk >= 1.67:
            interp = "Proceso de clase mundial (Cpk ≥ 1.67)."
        elif cpk >= 1.33:
            interp = "Proceso capaz (1.33 ≤ Cpk < 1.67)."
        elif cpk >= 1.00:
            interp = "Proceso adecuado pero requiere control estricto (1.00 ≤ Cpk < 1.33)."
        elif cpk >= 0.67:
            interp = "Proceso parcialmente capaz, requiere mejoras (0.67 ≤ Cpk < 1.00)."
        else:
            interp = "Proceso incapaz (Cpk < 0.67), requiere acción inmediata."
        result["interpretation"] = interp

    # Porcentaje fuera de especificación (asumiendo normalidad)
    from scipy import stats as _st
    out_pct = 0.0
    if lsl is not None and sigma_overall > 0:
        out_pct += float(_st.norm.cdf(lsl, mean, sigma_overall)) * 100
    if usl is not None and sigma_overall > 0:
        out_pct += float(1 - _st.norm.cdf(usl, mean, sigma_overall)) * 100
    result["ppm_out_of_spec"] = out_pct * 10000  # partes por millón
    result["percent_out_of_spec"] = out_pct

    return result
