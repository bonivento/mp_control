"""Backend SQLite — usado para desarrollo local cuando no hay DATABASE_URL.

En producción (Vercel) usamos Postgres/Supabase configurando la variable
DATABASE_URL; ver app/db_postgres.py.
"""
from __future__ import annotations
import os
import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime


def _resolve_db_path() -> str:
    env_path = os.environ.get("DB_PATH")
    if env_path:
        return env_path
    if os.environ.get("VERCEL"):
        return "/tmp/control_calidad.db"
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(base, "data"), exist_ok=True)
    return os.path.join(base, "data", "control_calidad.db")


DB_PATH = _resolve_db_path()


SCHEMA = """
CREATE TABLE IF NOT EXISTS estudios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    producto TEXT NOT NULL,
    tipo TEXT NOT NULL,                  -- 'variable' o 'atributo'
    caracteristica TEXT NOT NULL,        -- p. ej. 'Peso (g)', 'Manchas'
    unidad TEXT,
    analista TEXT,
    lote TEXT,
    tipo_grafico TEXT NOT NULL,          -- 'xr', 'xs', 'p', 'np', 'c', 'u'
    lsl REAL,
    usl REAL,
    tamano_subgrupo INTEGER,
    notas TEXT,
    fecha_creacion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS muestras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudio_id INTEGER NOT NULL,
    subgrupo INTEGER NOT NULL,           -- número de subgrupo (1..N)
    valores TEXT NOT NULL,               -- JSON: lista de valores o [defectivos, tamaño]
    fecha_muestra TEXT NOT NULL,
    FOREIGN KEY (estudio_id) REFERENCES estudios(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_muestras_estudio ON muestras(estudio_id);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def crear_estudio(payload: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO estudios
            (nombre, producto, tipo, caracteristica, unidad, analista, lote,
             tipo_grafico, lsl, usl, tamano_subgrupo, notas, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                datetime.utcnow().isoformat(),
            ),
        )
        return cur.lastrowid


def listar_estudios() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM estudios ORDER BY fecha_creacion DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def obtener_estudio(estudio_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM estudios WHERE id = ?", (estudio_id,)
        ).fetchone()
        return dict(row) if row else None


def eliminar_estudio(estudio_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM estudios WHERE id = ?", (estudio_id,))
        return cur.rowcount > 0


def agregar_muestra(estudio_id: int, subgrupo: int, valores: list) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO muestras (estudio_id, subgrupo, valores, fecha_muestra)
            VALUES (?, ?, ?, ?)""",
            (
                estudio_id,
                subgrupo,
                json.dumps(valores),
                datetime.utcnow().isoformat(),
            ),
        )
        return cur.lastrowid


def agregar_muestras_bulk(estudio_id: int, muestras: list[dict]) -> int:
    """muestras: [{subgrupo: N, valores: [...]}, ...]"""
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.executemany(
            """INSERT INTO muestras (estudio_id, subgrupo, valores, fecha_muestra)
            VALUES (?, ?, ?, ?)""",
            [
                (estudio_id, m["subgrupo"], json.dumps(m["valores"]), now)
                for m in muestras
            ],
        )
    return len(muestras)


def listar_muestras(estudio_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM muestras WHERE estudio_id = ? ORDER BY subgrupo ASC",
            (estudio_id,),
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["valores"] = json.loads(d["valores"])
            result.append(d)
        return result


def eliminar_muestras(estudio_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM muestras WHERE estudio_id = ?", (estudio_id,))
        return cur.rowcount
