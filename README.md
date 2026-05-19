# Control Estadístico de Calidad — Frutas, Hortalizas y Plantas Medicinales

Aplicación web en Python que integra herramientas de **Control Estadístico de Calidad (CEC)**
para monitoreo y análisis de variables y atributos de calidad en productos agrícolas.

**Universidad del Magdalena · Control Estadístico de Procesos · 2026-1**

---

## Funcionalidades

### Variables continuas
- Gráficos **X̄-R** (subgrupos pequeños) y **X̄-S** (subgrupos grandes)
- Pruebas de normalidad (**Shapiro-Wilk**, **Anderson-Darling**, **D'Agostino-Pearson**)
- Histograma con curva normal teórica y gráfico **Q-Q**
- Índices de capacidad del proceso: **Cp, Cpk, Pp, Ppk**

### Atributos / defectos
- Gráficos **p, np, c, u**
- **Diagrama de Pareto** con identificación de las pocas vitales (regla 80/20)

### Análisis automático
- Detección de puntos fuera de control (±3σ)
- **6 reglas de Nelson** para patrones no aleatorios
- Estadística descriptiva completa

### Registro y trazabilidad
- Producto, característica, unidad, analista, lote, fecha
- Soporta mínimo 25 subgrupos por estudio (requisito académico)
- Persistencia en SQLite

### Exportación
- Reporte completo a **Excel** (3 hojas: trazabilidad, datos, resultados)
- Estilos con paleta corporativa de Unimagdalena

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.9+ · Flask 3 |
| Cálculos | NumPy, SciPy, Pandas |
| Exportación | OpenPyXL |
| Frontend | HTML/CSS personalizado + Plotly.js 2.35 |
| Marca | CDN oficial Universidad del Magdalena (logos + paleta) |
| Persistencia | SQLite (local) / `/tmp` (Vercel) |
| Despliegue | Vercel Serverless Functions |

---

## Estructura del proyecto

```
control/
├── api/
│   └── index.py             # Entry point Flask (Vercel)
├── app/
│   ├── routes.py            # Rutas Flask y API JSON
│   ├── database.py          # Capa SQLite
│   ├── excel_export.py      # Generación de Excel
│   └── statistics/
│       ├── constants.py     # Constantes de Shewhart (A2, D3, D4, B3, B4, d2, c4)
│       ├── normality.py     # Pruebas de normalidad
│       ├── control_charts.py# Gráficos X̄-R, X̄-S, p, np, c, u + reglas Nelson
│       ├── capability.py    # Cp, Cpk, Pp, Ppk
│       └── pareto.py        # Análisis de Pareto
├── templates/               # Plantillas Jinja2
├── static/
│   ├── css/unimag.css       # Estilos con paleta Unimagdalena
│   └── js/                  # Plotly + interacciones
├── data/                    # SQLite local
├── docs/                    # Documentación adicional
├── requirements.txt
├── vercel.json
└── README.md
```

---

## Ejecución local

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Arrancar servidor
python api/index.py --port 5050 --debug

# 3. Abrir en el navegador
open http://localhost:5050
```

> El puerto **5050** se usa en lugar de 5000 porque macOS ocupa 5000 con AirPlay.

---

## Despliegue en Vercel

### Pasos

1. **Crear cuenta** en [vercel.com](https://vercel.com) (gratuita).
2. Instalar la CLI:
   ```bash
   npm i -g vercel
   ```
3. Desde la carpeta del proyecto:
   ```bash
   vercel login
   vercel
   ```
4. Para producción:
   ```bash
   vercel --prod
   ```

### Alternativa: Git + Vercel Dashboard

1. Sube el repo a GitHub.
2. En el panel de Vercel: *Add New → Project → Import Git Repository*.
3. Vercel detecta `vercel.json` automáticamente. Click en **Deploy**.

### ⚠️ Importante sobre SQLite en Vercel

El filesystem de Vercel Serverless es **efímero**: los datos almacenados en `/tmp/control_calidad.db`
no persisten entre invocaciones. Esto es aceptable para **demo y sustentación**, pero
para uso real conviene migrar a una base de datos administrada.

#### Migración a Postgres (recomendado para producción)

1. Crear DB gratis en [neon.tech](https://neon.tech) o [supabase.com](https://supabase.com).
2. Agregar `psycopg[binary]` a `requirements.txt`.
3. Sustituir `app/database.py` por una capa Postgres con el mismo API.
4. Configurar la variable de entorno `DATABASE_URL` en Vercel.

---

## API REST (resumen)

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/estudios` | Crear estudio + cargar muestras |
| `GET`  | `/api/estudios` | Listar estudios |
| `GET`  | `/api/estudios/<id>` | Obtener un estudio con sus muestras |
| `DELETE`| `/api/estudios/<id>` | Eliminar estudio |
| `GET`  | `/api/estudios/<id>/excel` | Exportar a Excel |
| `POST` | `/api/analisis/normalidad` | Pruebas de normalidad + estadística descriptiva |
| `POST` | `/api/analisis/grafico` | Generar gráfico de control (tipo: xr, xs, p, np, c, u) |
| `POST` | `/api/analisis/capacidad` | Calcular Cp, Cpk, Pp, Ppk |
| `POST` | `/api/analisis/pareto` | Diagrama de Pareto |

---

## Ejemplos de productos compatibles

- **Frutas**: Mango, banano, aguacate, melón, ají topito
- **Hortalizas**: Cilantro
- **Plantas medicinales**: Sábila (aloe vera), manzanilla, menta, toronjil, caléndula,
  eucalipto, romero, hierbabuena, limoncillo, valeriana

Y características como: peso, diámetro, °Brix, pH, firmeza, color, textura,
humedad, aceites esenciales, principios activos, presencia de plagas/manchas,
defectos visuales, cumplimiento BPA/BPM, etc.

---

## Créditos

Aplicación desarrollada por estudiantes de Control Estadístico de Procesos 2026-1
para la Universidad del Magdalena. Uso de IA permitido para generación de código,
con arquitectura diseñada por los estudiantes.
