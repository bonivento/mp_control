# Configuración de Supabase

URL del proyecto: `https://kicalhpqppkknqtjhtml.supabase.co`

---

## 1. Crear las tablas

### Opción A — Automática
La aplicación ejecuta `CREATE TABLE IF NOT EXISTS` en la primera petición.
Si configuras `DATABASE_URL` correctamente, las tablas se crean solas.

### Opción B — Manual (recomendada)
1. Entra al proyecto en Supabase.
2. Menú lateral → **SQL Editor** → **New query**.
3. Pega el contenido de `supabase/schema.sql`.
4. Click en **Run** (o `Cmd+Enter`).
5. Verifica en **Database → Tables** que aparezcan: `estudios`, `muestras`.

---

## 2. Obtener la URL de conexión

1. En Supabase, ve a **Project Settings → Database**.
2. Busca la sección **Connection string**.
3. Cambia el selector a **Transaction** (puerto **6543**) — recomendado para serverless.
4. Selecciona **URI**. Verás algo como:

   ```
   postgresql://postgres.kicalhpqppkknqtjhtml:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

5. Reemplaza `[YOUR-PASSWORD]` con la contraseña que definiste al crear el proyecto.

> **¿Por qué Transaction pooler?** Cada Lambda de Vercel obtiene una conexión del
> pool de Supabase y la libera al terminar. Evita el problema de "demasiadas
> conexiones" en serverless.

---

## 3. Configurar la variable de entorno

### En desarrollo local

Crea un archivo `.env` en la raíz (NO lo subas a git):

```bash
DATABASE_URL=postgresql://postgres.kicalhpqppkknqtjhtml:TU_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

Y carga al arrancar:

```bash
export $(cat .env | xargs) && python api/index.py --port 5050 --debug
```

### En Vercel

1. Ve a tu proyecto en Vercel.
2. **Settings → Environment Variables**.
3. Agrega:

| Name | Value | Environments |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres.kicalhpqppkknqtjhtml:TU_PASSWORD@...` | Production, Preview |
| `SECRET_KEY` | una cadena aleatoria larga | Production, Preview |

4. **Redeploy** el proyecto (Deployments → menú → Redeploy).

---

## 4. Verificación

- Abre la URL desplegada.
- Crea un estudio de prueba con datos de ejemplo.
- En Supabase, ve a **Table Editor → estudios** y confirma que aparezca el registro.
- En **muestras** deben estar los subgrupos.
- Refresca la página: los datos deben persistir entre invocaciones.

---

## 5. Diagnóstico de problemas

### "DATABASE_URL no está configurada"
La variable no llegó al runtime. Revisa Vercel → Settings → Environment Variables.

### "could not connect to server" / timeout
- Verifica que la URL usa el puerto **6543** (pooler) y no 5432 (directo).
- Confirma que la contraseña no tiene caracteres que requieran URL-encoding
  (si los tiene, codifícalos: `@` → `%40`, `#` → `%23`, etc.).

### "password authentication failed"
La contraseña es incorrecta. Resetéala en Supabase → Settings → Database →
Reset database password.

### Latencia alta en cold start
Normal en serverless. La primera invocación tras inactividad puede tardar 1-3s.
Las siguientes son rápidas.

---

## 6. Estructura de las tablas

### `estudios`
| Columna | Tipo | Notas |
|---|---|---|
| `id` | `BIGSERIAL` | PK |
| `nombre` | `TEXT` | requerido |
| `producto` | `TEXT` | requerido |
| `tipo` | `TEXT` | `'variable'` o `'atributo'` |
| `caracteristica` | `TEXT` | p. ej. "Peso", "pH" |
| `unidad` | `TEXT` | g, cm, °Bx, etc. |
| `analista` | `TEXT` | nombre del operario |
| `lote` | `TEXT` | identificador del lote |
| `tipo_grafico` | `TEXT` | `xr`, `xs`, `p`, `np`, `c`, `u` |
| `lsl`, `usl` | `DOUBLE PRECISION` | límites de especificación |
| `tamano_subgrupo` | `INTEGER` | 2..25 |
| `notas` | `TEXT` | observaciones |
| `fecha_creacion` | `TIMESTAMPTZ` | auto |

### `muestras`
| Columna | Tipo | Notas |
|---|---|---|
| `id` | `BIGSERIAL` | PK |
| `estudio_id` | `BIGINT` | FK → estudios.id, ON DELETE CASCADE |
| `subgrupo` | `INTEGER` | 1..N |
| `valores` | `JSONB` | array de mediciones / [defectivos, tamaño] |
| `fecha_muestra` | `TIMESTAMPTZ` | auto |

### Vista `v_estudios_resumen`
Estudios + número de muestras asociadas (útil para dashboard).
