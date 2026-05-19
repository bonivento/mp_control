"""Backend Postgres / Supabase usando psycopg.

Se activa automáticamente cuando la variable de entorno DATABASE_URL está
configurada. En Vercel, conviene usar el "Transaction pooler" de Supabase
(puerto 6543) para serverless.

Ejemplo de URL:
  postgresql://postgres.<project_ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres

Cada función abre y cierra su propia conexión, lo cual es seguro para
serverless cuando se usa el pooler.
"""
from __future__ import annotations
import os
import json
from contextlib import contextmanager
from datetime import datetime

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()


SCHEMA = """
CREATE TABLE IF NOT EXISTS estudios (
    id              BIGSERIAL PRIMARY KEY,
    nombre          TEXT NOT NULL,
    producto        TEXT NOT NULL,
    tipo            TEXT NOT NULL,
    caracteristica  TEXT NOT NULL,
    unidad          TEXT,
    analista        TEXT,
    lote            TEXT,
    tipo_grafico    TEXT NOT NULL,
    lsl             DOUBLE PRECISION,
    usl             DOUBLE PRECISION,
    tamano_subgrupo INTEGER,
    notas           TEXT,
    fecha_creacion  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS muestras (
    id            BIGSERIAL PRIMARY KEY,
    estudio_id    BIGINT NOT NULL REFERENCES estudios(id) ON DELETE CASCADE,
    subgrupo      INTEGER NOT NULL,
    valores       JSONB NOT NULL,
    fecha_muestra TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_muestras_estudio ON muestras(estudio_id);
CREATE INDEX IF NOT EXISTS idx_estudios_fecha   ON estudios(fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS idx_estudios_producto ON estudios(producto);
"""


@contextmanager
def get_conn():
    """Abre una conexión por petición. Apto para el pooler de Supabase.

    IMPORTANTE: prepare_threshold=None desactiva prepared statements. El
    Transaction Pooler de Supabase (PgBouncer en modo transaction) reutiliza
    conexiones físicas entre clientes, así que las prepared statements no
    sobreviven entre transacciones y producen errores como
    'prepared statement "_pg3_0" already exists'.
    """
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL no está configurada.")
    conn = psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
        autocommit=False,
        prepare_threshold=None,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


_DB_INITIALIZED = False


def init_db():
    """Crea las tablas si no existen. Solo lo hace una vez por proceso."""
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        return
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)
    _DB_INITIALIZED = True


def _row_to_dict(row: dict) -> dict:
    """Normaliza una fila: ISO en fechas, valores JSON parseados."""
    if not row:
        return row
    d = dict(row)
    if "fecha_creacion" in d and isinstance(d["fecha_creacion"], datetime):
        d["fecha_creacion"] = d["fecha_creacion"].isoformat()
    if "fecha_muestra" in d and isinstance(d["fecha_muestra"], datetime):
        d["fecha_muestra"] = d["fecha_muestra"].isoformat()
    return d


# ---------------- Estudios ----------------

def crear_estudio(payload: dict) -> int:
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO estudios
                (nombre, producto, tipo, caracteristica, unidad, analista, lote,
                 tipo_grafico, lsl, usl, tamano_subgrupo, notas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id""",
                (
                    payload["nombre"],
                    payload["producto"],
                    payload["tipo"],
                    payload["caracteristica"],
                    payload.get("unidad"),
                    payload.get("analista"),
                    payload.get("lote"),
                    payload["tipo_grafico"],
                    payload.get("lsl"),
                    payload.get("usl"),
                    payload.get("tamano_subgrupo"),
                    payload.get("notas"),
                ),
            )
            return cur.fetchone()["id"]


def listar_estudios() -> list[dict]:
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM estudios ORDER BY fecha_creacion DESC")
            return [_row_to_dict(r) for r in cur.fetchall()]


def obtener_estudio(estudio_id: int) -> dict | None:
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM estudios WHERE id = %s", (estudio_id,))
            row = cur.fetchone()
            return _row_to_dict(row) if row else None


def eliminar_estudio(estudio_id: int) -> bool:
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM estudios WHERE id = %s", (estudio_id,))
            return cur.rowcount > 0


# ---------------- Muestras ----------------

def agregar_muestra(estudio_id: int, subgrupo: int, valores: list) -> int:
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO muestras (estudio_id, subgrupo, valores)
                VALUES (%s, %s, %s) RETURNING id""",
                (estudio_id, subgrupo, Jsonb(valores)),
            )
            return cur.fetchone()["id"]


def agregar_muestras_bulk(estudio_id: int, muestras: list[dict]) -> int:
    if not muestras:
        return 0
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO muestras (estudio_id, subgrupo, valores)
                VALUES (%s, %s, %s)""",
                [(estudio_id, m["subgrupo"], Jsonb(m["valores"])) for m in muestras],
            )
    return len(muestras)


def listar_muestras(estudio_id: int) -> list[dict]:
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM muestras WHERE estudio_id = %s ORDER BY subgrupo ASC",
                (estudio_id,),
            )
            return [_row_to_dict(r) for r in cur.fetchall()]


def eliminar_muestras(estudio_id: int) -> int:
    init_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM muestras WHERE estudio_id = %s", (estudio_id,))
            return cur.rowcount
