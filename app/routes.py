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
        except Exception as e:
            app.logger.error(f"Error listando estudios: {e}")
            estudios = []
            db_error = str(e)
        return render_template("index.html", estudios=estudios, db_error=db_error)

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
