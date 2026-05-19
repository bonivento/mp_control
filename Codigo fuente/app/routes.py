"""Rutas y endpoints API de la aplicación."""
from __future__ import annotations
import os
from flask import (
    Flask, render_template, request, jsonify, send_file, abort, redirect, url_for, flash
)
from io import BytesIO

from . import database as db
from .statistics import normality, control_charts, capability, pareto
from .excel_export import construir_excel
from .excel_import import parse_excel


def create_app() -> Flask:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "unimag-cec-2026-cambia-en-prod")

    @app.context_processor
    def inject_backend():
        return {"db_backend": db.BACKEND}

    # init_db es lazy; cada función lo llama internamente para evitar
    # fallos al importar cuando DATABASE_URL aún no está lista.
    try:
        db.init_db()
    except Exception as e:
        app.logger.warning(f"No se pudo inicializar la base de datos al arrancar: {e}")

    # ---------- Vistas HTML ----------

    @app.route("/")
    def index():
        try:
            estudios = db.listar_estudios()
            db_error = None
            db_hint = None
        except Exception as e:
            app.logger.error(f"Error listando estudios: {e}")
            estudios = []
            db_error = str(e)
            db_hint = _diagnose_db_error(db_error)
        return render_template(
            "index.html", estudios=estudios, db_error=db_error, db_hint=db_hint
        )

    @app.route("/registro")
    def registro():
        return render_template("registro.html")

    @app.route("/estudio/<int:estudio_id>")
    def estudio_detalle(estudio_id):
        estudio = db.obtener_estudio(estudio_id)
        if not estudio:
            abort(404)
        muestras = db.listar_muestras(estudio_id)
        return render_template("estudio.html", estudio=estudio, muestras=muestras)

    @app.route("/pareto")
    def pareto_view():
        return render_template("pareto.html")

    @app.route("/normalidad")
    def normalidad_view():
        return render_template("normalidad.html")

    @app.route("/capacidad")
    def capacidad_view():
        return render_template("capacidad.html")

    @app.route("/manual")
    def manual():
        return render_template("manual.html")

    @app.route("/informe")
    def informe():
        docs_dir = os.path.join(os.path.dirname(app.template_folder), "docs")
        manual_path = os.path.join(docs_dir, "Manual_Usuario.docx")
        informe_path = os.path.join(docs_dir, "Informe_Tecnico.docx")
        return render_template(
            "informe.html",
            manual_docx_disponible=os.path.isfile(manual_path),
            informe_docx_disponible=os.path.isfile(informe_path),
        )

    @app.get("/descargas/<path:filename>")
    def descargas(filename):
        docs_dir = os.path.join(os.path.dirname(app.template_folder), "docs")
        full = os.path.join(docs_dir, filename)
        if not os.path.isfile(full):
            abort(404)
        if filename.endswith(".docx"):
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif filename.endswith(".mmd"):
            mime = "text/plain"
        elif filename.endswith(".png"):
            mime = "image/png"
        else:
            mime = "application/octet-stream"
        return send_file(full, mimetype=mime, as_attachment=True, download_name=filename)

    @app.route("/plantillas")
    def plantillas():
        samples_dir = os.path.join(os.path.dirname(app.template_folder), "samples")
        files = []
        if os.path.isdir(samples_dir):
            for f in sorted(os.listdir(samples_dir)):
                if f.endswith(".xlsx"):
                    path = os.path.join(samples_dir, f)
                    files.append({
                        "name": f,
                        "size_kb": round(os.path.getsize(path) / 1024, 1),
                    })
        return render_template("plantillas.html", files=files)

    @app.get("/samples/<path:filename>")
    def descargar_sample(filename):
        samples_dir = os.path.join(os.path.dirname(app.template_folder), "samples")
        path = os.path.join(samples_dir, filename)
        if not os.path.isfile(path) or not filename.endswith(".xlsx"):
            abort(404)
        return send_file(
            path,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )

    @app.post("/api/estudios/upload")
    def api_subir_excel():
        if "archivo" not in request.files:
            return jsonify({"error": "No se recibió ningún archivo (campo 'archivo')."}), 400
        f = request.files["archivo"]
        if not f.filename or not f.filename.lower().endswith(".xlsx"):
            return jsonify({"error": "El archivo debe ser .xlsx"}), 400
        try:
            content = f.read()
            if len(content) > 5 * 1024 * 1024:
                return jsonify({"error": "Archivo demasiado grande (máx 5 MB)."}), 400
            payload = parse_excel(content)
            estudio_id = db.crear_estudio(payload)
            if payload.get("muestras"):
                db.agregar_muestras_bulk(estudio_id, payload["muestras"])
            return jsonify({
                "id": estudio_id,
                "muestras": len(payload.get("muestras", [])),
                "ok": True,
            }), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.exception("Error procesando Excel")
            return jsonify({"error": f"Error procesando el archivo: {e}"}), 500

    # ---------- API: Estudios ----------

    @app.post("/api/estudios")
    def api_crear_estudio():
        data = request.get_json(force=True, silent=True) or {}
        required = ["nombre", "producto", "tipo", "caracteristica", "tipo_grafico"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"error": f"Faltan campos requeridos: {', '.join(missing)}"}), 400
        try:
            estudio_id = db.crear_estudio(data)
            if data.get("muestras"):
                db.agregar_muestras_bulk(estudio_id, data["muestras"])
            return jsonify({"id": estudio_id, "ok": True}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.get("/api/estudios")
    def api_listar_estudios():
        return jsonify(db.listar_estudios())

    @app.get("/api/estudios/<int:estudio_id>")
    def api_obtener_estudio(estudio_id):
        estudio = db.obtener_estudio(estudio_id)
        if not estudio:
            return jsonify({"error": "Estudio no encontrado"}), 404
        estudio["muestras"] = db.listar_muestras(estudio_id)
        return jsonify(estudio)

    @app.delete("/api/estudios/<int:estudio_id>")
    def api_eliminar_estudio(estudio_id):
        ok = db.eliminar_estudio(estudio_id)
        if not ok:
            return jsonify({"error": "Estudio no encontrado"}), 404
        return jsonify({"ok": True})

    @app.post("/api/estudios/<int:estudio_id>/muestras")
    def api_agregar_muestras(estudio_id):
        if not db.obtener_estudio(estudio_id):
            return jsonify({"error": "Estudio no encontrado"}), 404
        payload = request.get_json(force=True, silent=True) or {}
        muestras = payload.get("muestras", [])
        if not muestras:
            return jsonify({"error": "Lista de muestras vacía"}), 400
        n = db.agregar_muestras_bulk(estudio_id, muestras)
        return jsonify({"agregadas": n})

    @app.delete("/api/estudios/<int:estudio_id>/muestras")
    def api_eliminar_muestras(estudio_id):
        n = db.eliminar_muestras(estudio_id)
        return jsonify({"eliminadas": n})

    # ---------- API: Análisis estadístico ----------

    @app.post("/api/analisis/normalidad")
    def api_normalidad():
        data = request.get_json(force=True, silent=True) or {}
        valores = data.get("valores") or []
        if not valores:
            return jsonify({"error": "Lista de valores vacía"}), 400
        try:
            valores = [float(v) for v in valores]
        except (TypeError, ValueError):
            return jsonify({"error": "Todos los valores deben ser numéricos"}), 400
        return jsonify(normality.run_all_normality_tests(valores))

    @app.post("/api/analisis/grafico")
    def api_grafico():
        """Genera gráfico de control según tipo."""
        data = request.get_json(force=True, silent=True) or {}
        tipo = (data.get("tipo") or "").lower()
        try:
            if tipo == "xr":
                subgrupos = [[float(v) for v in sg] for sg in data["subgrupos"]]
                return jsonify(control_charts.x_bar_r_chart(subgrupos))
            if tipo == "xs":
                subgrupos = [[float(v) for v in sg] for sg in data["subgrupos"]]
                return jsonify(control_charts.x_bar_s_chart(subgrupos))
            if tipo == "p":
                return jsonify(control_charts.p_chart(
                    [int(v) for v in data["defectivos"]],
                    [int(v) for v in data["tamanos"]],
                ))
            if tipo == "np":
                return jsonify(control_charts.np_chart(
                    [int(v) for v in data["defectivos"]],
                    int(data["tamano"]),
                ))
            if tipo == "c":
                return jsonify(control_charts.c_chart([int(v) for v in data["defectos"]]))
            if tipo == "u":
                return jsonify(control_charts.u_chart(
                    [int(v) for v in data["defectos"]],
                    [float(v) for v in data["tamanos"]],
                ))
            return jsonify({"error": f"Tipo de gráfico no soportado: {tipo}"}), 400
        except (KeyError, ValueError, TypeError) as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/api/analisis/capacidad")
    def api_capacidad():
        data = request.get_json(force=True, silent=True) or {}
        try:
            valores = data.get("valores") or data.get("subgrupos") or []
            lsl = data.get("lsl")
            usl = data.get("usl")
            n = data.get("tamano_subgrupo")
            lsl = float(lsl) if lsl not in (None, "") else None
            usl = float(usl) if usl not in (None, "") else None
            return jsonify(capability.capability_indices(
                valores, lsl, usl, subgroup_size=n
            ))
        except (ValueError, TypeError) as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/api/analisis/pareto")
    def api_pareto():
        data = request.get_json(force=True, silent=True) or {}
        try:
            return jsonify(pareto.pareto_analysis(
                data["categorias"],
                [int(v) for v in data["frecuencias"]],
            ))
        except (KeyError, ValueError, TypeError) as e:
            return jsonify({"error": str(e)}), 400

    # ---------- Exportación a Excel ----------

    @app.get("/api/estudios/<int:estudio_id>/excel")
    def api_excel(estudio_id):
        estudio = db.obtener_estudio(estudio_id)
        if not estudio:
            abort(404)
        muestras = db.listar_muestras(estudio_id)

        # Calcula resultados según tipo de gráfico
        resultados = _calcular_resultados(estudio, muestras)

        contenido = construir_excel(estudio, muestras, resultados)
        filename = f"estudio_{estudio_id}_{estudio['producto'].replace(' ', '_')}.xlsx"
        return send_file(
            BytesIO(contenido),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    return app


def _diagnose_db_error(err: str) -> str | None:
    """Devuelve una sugerencia legible según el patrón del error."""
    err_l = err.lower()
    # IPv6 / dirección no asignable → usuario usó conexión directa en Vercel
    if "cannot assign requested address" in err_l or (
        ":" in err and "port 5432" in err_l
    ):
        return (
            "Estás usando la conexión DIRECTA de Supabase (puerto 5432, IPv6 only), "
            "que NO funciona en Vercel. Cambia DATABASE_URL al "
            "**Transaction Pooler** (puerto 6543, IPv4): en Supabase → "
            "Project Settings → Database → Connection string → Transaction pooler. "
            "El hostname debe contener 'pooler.supabase.com' y el puerto 6543."
        )
    if "password authentication failed" in err_l:
        return (
            "La contraseña en DATABASE_URL no coincide con la del proyecto Supabase. "
            "Resetéala en Supabase → Settings → Database → Reset database password "
            "y actualiza la variable en Vercel."
        )
    if "could not translate host name" in err_l or "name or service not known" in err_l:
        return (
            "El hostname de DATABASE_URL es incorrecto. Verifica que esté tomado "
            "directamente del panel de Supabase (Project Settings → Database)."
        )
    if "timeout" in err_l or "timed out" in err_l:
        return (
            "Tiempo de espera agotado al conectar. Verifica la región del pooler "
            "y que el proyecto Supabase esté activo (no pausado)."
        )
    if "database_url no está configurada" in err_l:
        return (
            "Falta la variable DATABASE_URL. En Vercel: Settings → Environment "
            "Variables → New. Ver supabase/README.md para el formato."
        )
    return None


def _calcular_resultados(estudio: dict, muestras: list[dict]) -> dict:
    tipo = (estudio.get("tipo_grafico") or "").lower()
    if not muestras:
        return {"info": "Sin muestras registradas."}
    try:
        if tipo in ("xr", "xs"):
            subgrupos = [m["valores"] for m in muestras]
            chart = (control_charts.x_bar_r_chart if tipo == "xr"
                     else control_charts.x_bar_s_chart)(subgrupos)
            flat = [v for sg in subgrupos for v in sg]
            res = {"grafico_control": chart, "normalidad": normality.run_all_normality_tests(flat)}
            if estudio.get("lsl") is not None or estudio.get("usl") is not None:
                res["capacidad"] = capability.capability_indices(
                    subgrupos, estudio.get("lsl"), estudio.get("usl"),
                    subgroup_size=len(subgrupos[0]),
                )
            return res
        if tipo == "p":
            defectivos = [m["valores"][0] for m in muestras]
            tamanos = [m["valores"][1] for m in muestras]
            return {"grafico_control": control_charts.p_chart(defectivos, tamanos)}
        if tipo == "np":
            defectivos = [m["valores"][0] for m in muestras]
            n = muestras[0]["valores"][1]
            return {"grafico_control": control_charts.np_chart(defectivos, int(n))}
        if tipo == "c":
            defectos = [m["valores"][0] for m in muestras]
            return {"grafico_control": control_charts.c_chart(defectos)}
        if tipo == "u":
            defectos = [m["valores"][0] for m in muestras]
            tamanos = [m["valores"][1] for m in muestras]
            return {"grafico_control": control_charts.u_chart(defectos, tamanos)}
        return {"info": f"Tipo de gráfico no soportado para análisis automático: {tipo}"}
    except Exception as e:
        return {"error": str(e)}
