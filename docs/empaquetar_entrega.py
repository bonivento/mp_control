"""Empaqueta el codigo fuente y documentos en la carpeta 'Codigo fuente/'.

Crea una copia limpia del proyecto lista para empaquetar como ZIP y subir
al campus virtual como entregable del trabajo final.

Uso:
    python docs/empaquetar_entrega.py

Estructura producida:
    Codigo fuente/
        api/
        app/
        static/
        templates/
        samples/
        supabase/
        docs/
            Manual_Usuario.docx
            Informe_Tecnico.docx
            Informe_Base_Datos.docx
            diagrams/
        README.md
        requirements.txt
        vercel.json
        .env.example
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "Codigo fuente")


# Carpetas a copiar completas (relativas a ROOT)
DIRS_TO_COPY = [
    "api",
    "app",
    "static",
    "templates",
    "samples",
    "supabase",
]

# Archivos sueltos a copiar
FILES_TO_COPY = [
    "README.md",
    "requirements.txt",
    "vercel.json",
    ".env.example",
    ".gitignore",
]

# Documentos a copiar a Codigo fuente/docs/ (no la carpeta docs entera,
# solo los artefactos relevantes para la entrega)
DOCS_TO_COPY = [
    "Manual_Usuario.docx",
    "Informe_Tecnico.docx",
    "Informe_Base_Datos.docx",
    "manual_usuario.md",
    "despliegue_vercel.md",
]

DIAGRAMS_TO_COPY = [
    "arquitectura.mmd", "arquitectura.png",
    "flujo_datos.mmd", "flujo_datos.png",
    "modelo_datos.mmd", "modelo_datos.png",
]


# Filtros de exclusion
IGNORE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", "*.pyo", ".DS_Store", "*.db",
)


def _clean_dest():
    if os.path.isdir(DEST):
        print(f"  · Limpiando {os.path.basename(DEST)}/ existente...")
        shutil.rmtree(DEST)
    os.makedirs(DEST, exist_ok=True)


def _copy_dirs():
    for d in DIRS_TO_COPY:
        src = os.path.join(ROOT, d)
        dst = os.path.join(DEST, d)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=IGNORE)
            print(f"  · {d}/ copiado")


def _copy_files():
    for f in FILES_TO_COPY:
        src = os.path.join(ROOT, f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(DEST, f))
            print(f"  · {f} copiado")


def _copy_docs():
    docs_dest = os.path.join(DEST, "docs")
    os.makedirs(docs_dest, exist_ok=True)
    for f in DOCS_TO_COPY:
        src = os.path.join(ROOT, "docs", f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(docs_dest, f))
            print(f"  · docs/{f} copiado")

    # Diagramas
    diagrams_dest = os.path.join(docs_dest, "diagrams")
    os.makedirs(diagrams_dest, exist_ok=True)
    for f in DIAGRAMS_TO_COPY:
        src = os.path.join(ROOT, "docs", "diagrams", f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(diagrams_dest, f))


def _crear_readme_entrega():
    """Pequeño README dentro de Codigo fuente/ para guiar al evaluador."""
    contenido = """# Trabajo Final — Control Estadístico de Procesos 2026-1

## Universidad del Magdalena
## Sistema de Control Estadístico de Calidad
### Frutas, hortalizas y plantas medicinales

---

## Contenido de la entrega

| Carpeta / archivo | Descripción |
|---|---|
| `api/` | Entry point para Vercel Serverless |
| `app/` | Código fuente Python (rutas, estadística, BD, Excel) |
| `static/` | CSS y JavaScript del frontend |
| `templates/` | Plantillas Jinja2 |
| `samples/` | Archivos Excel de prueba (en control / fuera de control) |
| `supabase/` | Esquema SQL y guía de configuración |
| `docs/` | Documentación del proyecto |
| `docs/Manual_Usuario.docx` | Manual de usuario completo |
| `docs/Informe_Tecnico.docx` | Informe técnico (5 secciones + referencias) |
| `docs/Informe_Base_Datos.docx` | Informe específico de la base de datos |
| `docs/diagrams/` | Diagramas como código (Mermaid) + PNG |
| `README.md` | Guía general del proyecto |
| `requirements.txt` | Dependencias Python |
| `vercel.json` | Configuración del despliegue |

## Acceso al sistema desplegado

URL: (la URL pública entregada por Vercel)

## Ejecución local

```bash
pip install -r requirements.txt
python api/index.py --port 5050 --debug
```

## Repositorio

GitHub: https://github.com/bonivento/mp_control
"""
    path = os.path.join(DEST, "ENTREGA.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"  · ENTREGA.md creado")


def empaquetar():
    print(f"Empaquetando entrega en: {os.path.basename(DEST)}/")
    _clean_dest()
    _copy_dirs()
    _copy_files()
    _copy_docs()
    _crear_readme_entrega()
    # Tamaño total
    total = 0
    n_files = 0
    for dirpath, _, filenames in os.walk(DEST):
        for f in filenames:
            total += os.path.getsize(os.path.join(dirpath, f))
            n_files += 1
    print(f"\n✓ Empaquetado completo: {n_files} archivos · {total/1024/1024:.2f} MB")
    print(f"  Carpeta lista en: {DEST}")
    print(f"\nPara entregar:")
    print(f"  cd '{ROOT}' && zip -r 'mp_control_entrega.zip' 'Codigo fuente/'")


if __name__ == "__main__":
    empaquetar()
