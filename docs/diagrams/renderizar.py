"""Renderiza los diagramas Mermaid a PNG usando matplotlib.

Como matplotlib no entiende Mermaid directamente, dibujamos los diagramas
equivalentes manualmente. Los archivos .mmd son la fuente canónica
(renderizables en GitHub o mermaid.live) y estos PNG son para embeber
en los archivos Word.

Uso:
    python docs/diagrams/renderizar.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

OUT = os.path.dirname(os.path.abspath(__file__))

# Paleta corporativa Unimagdalena
C_BLUE = "#005CAB"
C_BLUE_LT = "#0183EF"
C_ORANGE = "#FF9400"
C_GREEN = "#00A50B"
C_NAVY = "#003A6B"
C_BG_BLUE = "#E6F3FF"
C_BG_ORANGE = "#FFF8EC"
C_BG_GREEN = "#E6F9E3"
C_WHITE = "#FFFFFF"
C_GREY = "#5B6B7A"
C_GREY_BG = "#F1F5F9"


def _box(ax, x, y, w, h, text, color, bg, fontsize=10, weight="bold"):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.4, edgecolor=color, facecolor=bg,
    )
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center",
            fontsize=fontsize, weight=weight, color=C_NAVY,
            wrap=True)


def _arrow(ax, x1, y1, x2, y2, label="", color=C_NAVY, dashed=False,
           label_offset=0.1, label_pos=0.5, fontsize=8):
    ls = (0, (4, 2)) if dashed else "-"
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>,head_width=0.18,head_length=0.28",
            color=color, lw=1.3, linestyle=ls,
            shrinkA=2, shrinkB=4,
        ),
    )
    if label:
        lx = x1 + (x2 - x1) * label_pos
        ly = y1 + (y2 - y1) * label_pos + label_offset
        ax.text(lx, ly, label, ha="center", va="bottom",
                fontsize=fontsize, color=C_GREY, style="italic")


def _group(ax, x, y, w, h, title, color, bg):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=1.8, edgecolor=color, facecolor=bg, alpha=0.35,
    )
    ax.add_patch(box)
    ax.text(x + 0.18, y + h - 0.18, title, ha="left", va="top",
            fontsize=10.5, weight="bold", color=color)


# =========================================================
# 1) Arquitectura general
# =========================================================
def render_arquitectura():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Arquitectura del Sistema CEC — Unimagdalena 2026-1",
                 fontsize=14, weight="bold", color=C_NAVY, pad=14)

    # Cliente (izquierda, ancho)
    _group(ax, 0.4, 5.6, 3.4, 1.9, "Cliente · Navegador", C_BLUE, C_BG_BLUE)
    _box(ax, 0.7, 6.55, 2.8, 0.7, "Interfaz HTML + CSS\n(paleta Unimagdalena)", C_BLUE, C_WHITE, fontsize=9)
    _box(ax, 0.7, 5.78, 2.8, 0.7, "JavaScript + Plotly.js", C_BLUE, C_WHITE, fontsize=9)

    # Vercel (centro)
    _group(ax, 4.3, 3.0, 5.2, 4.5, "Vercel Serverless (Python 3.11)", C_ORANGE, C_BG_ORANGE)
    _box(ax, 4.6, 6.4, 4.6, 0.8, "Flask 3 · API REST\n(app/routes.py)", C_ORANGE, C_WHITE, fontsize=10)

    _box(ax, 4.6, 5.0, 1.4, 1.05, "Estadística\nstatistics/*\nnumpy · scipy", C_ORANGE, C_WHITE, fontsize=8)
    _box(ax, 6.2, 5.0, 1.4, 1.05, "Excel I/O\nopenpyxl", C_ORANGE, C_WHITE, fontsize=8)
    _box(ax, 7.8, 5.0, 1.4, 1.05, "Dispatcher\nBD\ndatabase.py", C_ORANGE, C_WHITE, fontsize=8)

    _box(ax, 4.6, 3.65, 4.6, 0.95, "psycopg 3\nprepare_threshold=None  (sin prepared statements)",
         C_NAVY, C_WHITE, fontsize=8)
    _box(ax, 4.6, 3.1, 4.6, 0.45, "Fallback local: SQLite (data/control_calidad.db)",
         C_NAVY, C_GREY_BG, fontsize=8, weight="normal")

    # Supabase (derecha)
    _group(ax, 10.0, 3.0, 1.85, 4.5, "Supabase · BaaS", C_GREEN, C_BG_GREEN)
    _box(ax, 10.1, 6.4, 1.65, 0.8, "Transaction\nPooler\n(IPv4 · :6543)", C_GREEN, C_WHITE, fontsize=9)
    _box(ax, 10.1, 5.0, 1.65, 1.05, "PostgreSQL\n\nestudios\nmuestras", C_GREEN, C_WHITE, fontsize=9)
    _box(ax, 10.1, 3.3, 1.65, 1.0, "SQL Editor\nschema.sql\nschema en init_db()",
         C_GREEN, "#f4faf3", fontsize=8, weight="normal")

    # CDNs (abajo)
    _group(ax, 0.4, 0.4, 11.45, 1.7, "Activos estáticos (servidos vía CDN)", C_GREY, C_GREY_BG)
    _box(ax, 0.7, 0.75, 3.4, 0.95, "CDN Unimagdalena\nescudo + paleta corporativa\ncdn.unimagdalena.edu.co",
         C_GREY, C_WHITE, fontsize=8, weight="normal")
    _box(ax, 4.4, 0.75, 3.4, 0.95, "Plotly.js CDN\ngráficos interactivos\ncdn.plot.ly",
         C_GREY, C_WHITE, fontsize=8, weight="normal")
    _box(ax, 8.1, 0.75, 3.5, 0.95, "Mermaid.js CDN\ndiagramas en /informe\ncdn.jsdelivr.net",
         C_GREY, C_WHITE, fontsize=8, weight="normal")

    # Flechas principales (de izquierda a derecha)
    _arrow(ax, 3.8, 6.5, 4.6, 6.8, "HTTPS · JSON", label_offset=0.06)
    _arrow(ax, 9.2, 4.1, 10.08, 6.6, "TCP · 6543", label_offset=0.1)
    _arrow(ax, 10.95, 6.4, 10.95, 6.07)  # pooler -> postgres

    # Flechas a CDN (punteadas)
    _arrow(ax, 2.1, 5.6, 2.1, 1.72, dashed=True, color=C_GREY)
    _arrow(ax, 6.1, 3.0, 6.1, 1.72, dashed=True, color=C_GREY, label="static assets",
           label_offset=0.05, label_pos=0.4, fontsize=7)
    _arrow(ax, 9.5, 3.0, 9.7, 1.72, dashed=True, color=C_GREY)

    out_path = os.path.join(OUT, "arquitectura.png")
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=C_WHITE)
    plt.close(fig)
    return out_path


# =========================================================
# 2) Diagrama de secuencia: subir Excel
# =========================================================
def render_flujo_datos():
    fig, ax = plt.subplots(figsize=(13, 8.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8.5)
    ax.axis("off")
    ax.set_title("Flujo de datos: subir Excel y obtener análisis",
                 fontsize=14, weight="bold", color=C_NAVY, pad=14)

    actores = [
        ("Analista",          C_NAVY,   C_WHITE),
        ("Navegador",         C_BLUE,   C_BG_BLUE),
        ("Flask\n(Vercel)",   C_ORANGE, C_BG_ORANGE),
        ("excel_import",      C_ORANGE, C_WHITE),
        ("statistics/*",      C_ORANGE, C_WHITE),
        ("Postgres\n(Supabase)", C_GREEN, C_BG_GREEN),
    ]
    n = len(actores)
    margin = 0.6
    spacing = (13 - 2 * margin) / (n - 1)
    xs = [margin + i * spacing for i in range(n)]
    y_top = 7.6
    y_bot = 0.3

    # Lifelines y encabezados
    for i, (name, col, bg) in enumerate(actores):
        _box(ax, xs[i] - 0.85, y_top, 1.7, 0.7, name, col, bg, fontsize=9)
        ax.plot([xs[i], xs[i]], [y_top - 0.05, y_bot + 0.6],
                color="#cbd5e1", linewidth=0.9, linestyle=(0, (2, 2)))

    pasos = [
        (0, 1, "1. Selecciona archivo .xlsx", "right"),
        (1, 2, "2. POST /api/estudios/upload (multipart)", "right"),
        (2, 3, "3. parse_excel(bytes)", "right"),
        (3, 2, "4. metadata + lista de muestras", "left"),
        (2, 5, "5. INSERT estudios + muestras (JSONB)", "right"),
        (5, 2, "6. estudio_id", "left"),
        (2, 1, "7. 201 { id, muestras, ok }", "left"),
        (1, 1, "8. redirect /estudio/{id}", "self"),
        (1, 2, "9. POST /api/analisis/grafico", "right"),
        (2, 4, "10. x_bar_r_chart(subgrupos)", "right"),
        (4, 2, "11. chart + reglas de Nelson", "left"),
        (2, 1, "12. JSON { puntos, límites, violaciones }", "left"),
        (1, 0, "13. Plotly.newPlot() — muestra al analista", "left"),
    ]
    available = (y_top - 0.2) - (y_bot + 0.6)
    step = available / (len(pasos) + 1)
    y = y_top - 0.5
    for src, dst, label, direction in pasos:
        y -= step
        col = C_BLUE_LT if direction == "right" else C_GREEN
        if direction == "self":
            # Mensaje hacia uno mismo (bucle pequeño)
            ax.annotate(
                "", xy=(xs[src] + 0.4, y - 0.05),
                xytext=(xs[src], y + 0.05),
                arrowprops=dict(
                    arrowstyle="-|>,head_width=0.18,head_length=0.28",
                    color=col, lw=1.2,
                    connectionstyle="arc3,rad=-1.0",
                ),
            )
            ax.text(xs[src] + 0.55, y, label, ha="left", va="center",
                    fontsize=8.5, color=C_NAVY)
        else:
            _arrow(ax, xs[src], y, xs[dst], y, color=col)
            mid_x = (xs[src] + xs[dst]) / 2
            ax.text(mid_x, y + 0.12, label, ha="center", va="bottom",
                    fontsize=8.5, color=C_NAVY)

    out_path = os.path.join(OUT, "flujo_datos.png")
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=C_WHITE)
    plt.close(fig)
    return out_path


# =========================================================
# 3) Modelo entidad-relación
# =========================================================
def render_modelo_datos():
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.5)
    ax.axis("off")
    ax.set_title("Modelo de datos — Supabase Postgres",
                 fontsize=14, weight="bold", color=C_NAVY, pad=14)

    def tabla(x, y, w, titulo, campos, color, bg):
        h_h = 0.55
        h_row = 0.34
        total_h = h_h + h_row * len(campos)
        # Encabezado
        ax.add_patch(FancyBboxPatch(
            (x, y + total_h - h_h), w, h_h,
            boxstyle="round,pad=0.02,rounding_size=0.0",
            linewidth=1.4, edgecolor=color, facecolor=color))
        ax.text(x + w/2, y + total_h - h_h/2, titulo,
                ha="center", va="center",
                color=C_WHITE, fontsize=11, weight="bold")
        # Cuerpo
        ax.add_patch(FancyBboxPatch(
            (x, y), w, total_h - h_h,
            boxstyle="round,pad=0.02,rounding_size=0.0",
            linewidth=1.4, edgecolor=color, facecolor=bg))
        for i, (nombre, tipo, tag) in enumerate(campos):
            yy = y + total_h - h_h - h_row * (i + 1) + h_row * 0.5
            etiqueta = f"{nombre}   {tipo}"
            ax.text(x + 0.18, yy, etiqueta, ha="left", va="center",
                    fontsize=9, color=C_NAVY,
                    weight=("bold" if tag in ("PK", "FK") else "normal"))
            if tag:
                col_tag = "#a8324a" if tag == "PK" else "#1d4ed8" if tag == "FK" else C_GREY
                ax.text(x + w - 0.18, yy, tag, ha="right", va="center",
                        fontsize=8, color=col_tag, weight="bold")

    estudios_campos = [
        ("id",                "BIGSERIAL",       "PK"),
        ("nombre",            "TEXT NOT NULL",   ""),
        ("producto",          "TEXT NOT NULL",   ""),
        ("tipo",              "TEXT",            ""),
        ("caracteristica",    "TEXT",            ""),
        ("unidad",            "TEXT",            ""),
        ("analista",          "TEXT",            ""),
        ("lote",              "TEXT",            ""),
        ("tipo_grafico",      "TEXT",            ""),
        ("lsl, usl",          "DOUBLE PRECISION",""),
        ("tamano_subgrupo",   "INTEGER",         ""),
        ("notas",             "TEXT",            ""),
        ("fecha_creacion",    "TIMESTAMPTZ",     ""),
    ]
    muestras_campos = [
        ("id",            "BIGSERIAL",     "PK"),
        ("estudio_id",    "BIGINT",        "FK"),
        ("subgrupo",      "INTEGER",       ""),
        ("valores",       "JSONB",         ""),
        ("fecha_muestra", "TIMESTAMPTZ",   ""),
    ]

    tabla(0.4, 0.5, 4.8, "estudios", estudios_campos, C_BLUE, "#f5fafe")
    tabla(6.5, 2.7, 4.2, "muestras", muestras_campos, C_GREEN, "#f4faf3")

    # Relación 1:N
    _arrow(ax, 5.25, 3.2, 6.48, 4.2, color=C_NAVY)
    ax.text(5.45, 4.3, "1 : N", fontsize=10, color=C_NAVY, weight="bold")
    ax.text(5.45, 3.95, "ON DELETE\nCASCADE", fontsize=8, color=C_GREY, style="italic")

    out_path = os.path.join(OUT, "modelo_datos.png")
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=C_WHITE)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    print("Renderizando diagramas a PNG…")
    for fn in (render_arquitectura, render_flujo_datos, render_modelo_datos):
        path = fn()
        size_kb = os.path.getsize(path) / 1024
        print(f"  ✓ {os.path.basename(path)} ({size_kb:.1f} KB)")
    print("Listo.")
