# Guía de Despliegue en Vercel

## Pre-requisitos

- Cuenta en [vercel.com](https://vercel.com) (gratis para proyectos personales).
- [Node.js](https://nodejs.org) instalado (para la CLI).
- Código del proyecto descargado.

---

## Opción A — Despliegue con la CLI de Vercel

```bash
# 1. Instala la CLI globalmente
npm install -g vercel

# 2. Inicia sesión
vercel login
# (te enviará un email con un enlace mágico)

# 3. Desde la carpeta del proyecto
cd /ruta/al/proyecto/control

# 4. Despliegue de prueba (preview)
vercel
# Te hace algunas preguntas:
#   ? Set up and deploy? [Y/n] y
#   ? Which scope? <selecciona tu cuenta>
#   ? Link to existing project? [y/N] n
#   ? What's your project's name? control-calidad
#   ? In which directory is your code located? ./
# Vercel detecta vercel.json y despliega.

# 5. Despliegue a producción
vercel --prod
```

Al terminar te entrega una URL del tipo `https://control-calidad-xxxxx.vercel.app`.

---

## Opción B — Despliegue desde Git (recomendado para el trabajo final)

1. **Sube el código a GitHub**:
   ```bash
   cd control
   git init
   git add .
   git commit -m "Sistema CEC Unimagdalena 2026-1"
   git branch -M main
   git remote add origin https://github.com/<tu-usuario>/control-calidad.git
   git push -u origin main
   ```

2. En el **dashboard de Vercel**:
   - Click en **Add New → Project**.
   - Selecciona **Import Git Repository**.
   - Autoriza acceso a tu repositorio.
   - Vercel detecta `vercel.json` y `requirements.txt` automáticamente.
   - Click en **Deploy**.

3. Espera ~30-60 segundos. Listo: la app está en línea.

4. Cada `git push` a `main` despliega una nueva versión.

---

## Configuración de variables de entorno (opcional)

En **Project Settings → Environment Variables**:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave para sesiones Flask (cambia el valor por defecto) |
| `DATABASE_URL` | Si migras a Postgres (Neon/Supabase) |
| `DB_PATH` | Override de la ruta SQLite (default: `/tmp/control_calidad.db`) |

---

## Comprobaciones post-despliegue

- Abre la URL principal — debe cargar el escudo Unimagdalena y el dashboard.
- Crea un estudio de prueba con datos de ejemplo.
- Verifica que la exportación a Excel funciona.
- Ten en cuenta que **al refrescar después de un tiempo, los datos pueden perderse**
  (filesystem efímero de Vercel). Para sustentación, ten preparado un archivo de
  datos para repoblar rápidamente.

---

## Limitaciones de Vercel Free

- **Tamaño del bundle**: 50 MB descomprimido por función. Nuestras dependencias
  (Flask + numpy + scipy + pandas + openpyxl) caben sin problema.
- **Timeout**: 10 segundos por petición. Suficiente para los cálculos del sistema.
- **Filesystem**: solo `/tmp` es escribible y se vacía entre invocaciones frías.

---

## Troubleshooting

### "Module not found" tras desplegar
Asegúrate de que `requirements.txt` está en la raíz y `api/index.py` también.

### Error 500 al guardar estudios
Probablemente la BD no se inicializó. Verifica que `/tmp` es escribible (lo es en Vercel).
Reintenta tras un nuevo deploy.

### Los logos del CDN no cargan
Vercel proxy de imágenes funciona; si bloquea, verifica conectividad al
`cdn.unimagdalena.edu.co`.

### Cold start lento
Primera petición tras inactividad puede tardar 2-3s mientras se inicializa el
contenedor. Las siguientes son rápidas.
