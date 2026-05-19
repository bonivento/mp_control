"""Conversión de fechas/horas a la zona horaria de Colombia (America/Bogota).

Las fechas se almacenan en UTC en la base de datos (mejor práctica). Esta
utilidad las convierte a hora local para mostrar al usuario.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta

try:
    from zoneinfo import ZoneInfo
    COLOMBIA_TZ = ZoneInfo("America/Bogota")
except Exception:
    # Fallback: Colombia no usa DST, así que UTC-5 fijo funciona bien.
    COLOMBIA_TZ = timezone(timedelta(hours=-5))


def _parse_iso(iso_str: str) -> datetime | None:
    """Acepta ISO con o sin zona horaria; si no la trae asume UTC."""
    if not iso_str:
        return None
    s = str(iso_str).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        # Intenta solo fecha
        try:
            dt = datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            try:
                dt = datetime.strptime(s[:10], "%Y-%m-%d")
            except ValueError:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def to_colombia(iso_str, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Convierte un timestamp ISO (asumido UTC si no trae zona) a hora Colombia."""
    dt = _parse_iso(iso_str)
    if dt is None:
        return iso_str or ""
    return dt.astimezone(COLOMBIA_TZ).strftime(fmt)


def colombia_date(iso_str) -> str:
    """Solo la fecha (YYYY-MM-DD) en Colombia."""
    return to_colombia(iso_str, fmt="%Y-%m-%d")


def colombia_datetime(iso_str) -> str:
    """Fecha y hora completas en Colombia (YYYY-MM-DD HH:MM:SS)."""
    return to_colombia(iso_str, fmt="%Y-%m-%d %H:%M:%S")


def colombia_friendly(iso_str) -> str:
    """Formato amigable: '19 may 2026, 10:35 a.m.'"""
    dt = _parse_iso(iso_str)
    if dt is None:
        return iso_str or ""
    local = dt.astimezone(COLOMBIA_TZ)
    meses = ["ene", "feb", "mar", "abr", "may", "jun",
             "jul", "ago", "sep", "oct", "nov", "dic"]
    hora12 = local.hour % 12 or 12
    am_pm = "a. m." if local.hour < 12 else "p. m."
    return f"{local.day:02d} {meses[local.month-1]} {local.year}, {hora12}:{local.minute:02d} {am_pm}"


def now_colombia_iso() -> str:
    """Hora actual de Colombia en ISO 8601 con offset (-05:00)."""
    return datetime.now(COLOMBIA_TZ).isoformat()
