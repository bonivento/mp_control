"""Diagrama de Pareto: identificación del 80/20 de causas de defectos."""
import numpy as np


def pareto_analysis(categories: list[str], frequencies: list[int]) -> dict:
    if len(categories) != len(frequencies):
        raise ValueError("Categorías y frecuencias deben tener la misma longitud.")
    if len(categories) == 0:
        raise ValueError("Se requiere al menos una categoría.")

    pairs = sorted(zip(categories, frequencies), key=lambda x: x[1], reverse=True)
    sorted_cats = [p[0] for p in pairs]
    sorted_freqs = [int(p[1]) for p in pairs]

    total = sum(sorted_freqs)
    if total == 0:
        return {
            "categories": sorted_cats,
            "frequencies": sorted_freqs,
            "percentages": [0.0] * len(sorted_cats),
            "cumulative_percentages": [0.0] * len(sorted_cats),
            "vital_few": [],
            "total": 0,
        }

    percentages = [f / total * 100 for f in sorted_freqs]
    cumulative = np.cumsum(percentages).tolist()

    # Identificar "vital few": categorías hasta acumular ~80%
    vital_few = []
    for i, c in enumerate(cumulative):
        vital_few.append(sorted_cats[i])
        if c >= 80:
            break

    return {
        "categories": sorted_cats,
        "frequencies": sorted_freqs,
        "percentages": percentages,
        "cumulative_percentages": cumulative,
        "vital_few": vital_few,
        "total": total,
    }
