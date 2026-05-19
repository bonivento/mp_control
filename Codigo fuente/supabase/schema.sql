-- =========================================================
-- Esquema de base de datos para Supabase Postgres
-- Sistema de Control Estadístico de Calidad - Unimagdalena 2026-1
--
-- INSTRUCCIONES DE USO:
-- 1. Entrar al panel de Supabase del proyecto.
-- 2. Ir a SQL Editor → New query.
-- 3. Pegar este archivo completo y ejecutar.
-- 4. Verificar en Database → Tables que aparezcan: estudios, muestras.
--
-- Alternativa: la aplicación crea estas tablas automáticamente
-- en la primera invocación (CREATE TABLE IF NOT EXISTS).
-- =========================================================

-- Tabla: estudios
-- Almacena la trazabilidad y configuración de cada estudio de control.
CREATE TABLE IF NOT EXISTS public.estudios (
    id              BIGSERIAL PRIMARY KEY,
    nombre          TEXT NOT NULL,
    producto        TEXT NOT NULL,
    tipo            TEXT NOT NULL CHECK (tipo IN ('variable', 'atributo')),
    caracteristica  TEXT NOT NULL,
    unidad          TEXT,
    analista        TEXT,
    lote            TEXT,
    tipo_grafico    TEXT NOT NULL CHECK (tipo_grafico IN ('xr', 'xs', 'p', 'np', 'c', 'u')),
    lsl             DOUBLE PRECISION,
    usl             DOUBLE PRECISION,
    tamano_subgrupo INTEGER CHECK (tamano_subgrupo IS NULL OR (tamano_subgrupo BETWEEN 2 AND 25)),
    notas           TEXT,
    fecha_creacion  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  public.estudios            IS 'Estudios de control estadístico registrados';
COMMENT ON COLUMN public.estudios.tipo       IS 'variable (continua) o atributo (conteo)';
COMMENT ON COLUMN public.estudios.tipo_grafico IS 'xr, xs, p, np, c o u';
COMMENT ON COLUMN public.estudios.lsl        IS 'Límite inferior de especificación (opcional)';
COMMENT ON COLUMN public.estudios.usl        IS 'Límite superior de especificación (opcional)';

-- Tabla: muestras
-- Cada subgrupo del estudio. valores se guarda como JSONB:
--   - Variables (X̄-R/X̄-S): [v1, v2, ..., vn]
--   - p, np, u:              [defectivos, tamaño_muestra]
--   - c:                     [defectos]
CREATE TABLE IF NOT EXISTS public.muestras (
    id            BIGSERIAL PRIMARY KEY,
    estudio_id    BIGINT NOT NULL REFERENCES public.estudios(id) ON DELETE CASCADE,
    subgrupo      INTEGER NOT NULL CHECK (subgrupo >= 1),
    valores       JSONB NOT NULL,
    fecha_muestra TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  public.muestras IS 'Subgrupos / muestras asociados a cada estudio';

-- Índices
CREATE INDEX IF NOT EXISTS idx_muestras_estudio   ON public.muestras(estudio_id);
CREATE INDEX IF NOT EXISTS idx_estudios_fecha     ON public.estudios(fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS idx_estudios_producto  ON public.estudios(producto);
CREATE INDEX IF NOT EXISTS idx_estudios_tipo      ON public.estudios(tipo);

-- =========================================================
-- (Opcional) Row Level Security
-- Por defecto la app accede usando el rol "postgres" con DATABASE_URL,
-- que bypassea RLS. Si quieres exponer las tablas vía la API pública
-- de Supabase con el anon key, habilita RLS y define políticas.
-- Para esta app no es necesario.
-- =========================================================
-- ALTER TABLE public.estudios ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.muestras ENABLE ROW LEVEL SECURITY;

-- =========================================================
-- Vistas útiles (opcional)
-- =========================================================
CREATE OR REPLACE VIEW public.v_estudios_resumen AS
SELECT
    e.id,
    e.nombre,
    e.producto,
    e.tipo,
    e.caracteristica,
    e.tipo_grafico,
    e.analista,
    e.lote,
    e.fecha_creacion,
    COUNT(m.id) AS n_muestras
FROM public.estudios e
LEFT JOIN public.muestras m ON m.estudio_id = e.id
GROUP BY e.id
ORDER BY e.fecha_creacion DESC;

COMMENT ON VIEW public.v_estudios_resumen IS
    'Resumen rápido: cada estudio con su conteo de muestras asociadas';
