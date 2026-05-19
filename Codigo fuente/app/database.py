"""Capa de base de datos — dispatcher.

Si la variable de entorno DATABASE_URL está configurada se usa Postgres
(Supabase). En caso contrario, SQLite local para desarrollo.

Todos los módulos consumen este archivo sin importar el backend concreto.
"""
from __future__ import annotations
import os


def _backend_name() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return "postgres"
    return "sqlite"


BACKEND = _backend_name()

if BACKEND == "postgres":
    from .db_postgres import (
        init_db,
        crear_estudio,
        listar_estudios,
        obtener_estudio,
        eliminar_estudio,
        agregar_muestra,
        agregar_muestras_bulk,
        listar_muestras,
        eliminar_muestras,
    )
else:
    from .db_sqlite import (
        init_db,
        crear_estudio,
        listar_estudios,
        obtener_estudio,
        eliminar_estudio,
        agregar_muestra,
        agregar_muestras_bulk,
        listar_muestras,
        eliminar_muestras,
    )


__all__ = [
    "BACKEND",
    "init_db",
    "crear_estudio",
    "listar_estudios",
    "obtener_estudio",
    "eliminar_estudio",
    "agregar_muestra",
    "agregar_muestras_bulk",
    "listar_muestras",
    "eliminar_muestras",
]
