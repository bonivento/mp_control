// Vista de detalle del estudio: gráficos + análisis automático
(function() {
  const estudio = window.ESTUDIO;
  const muestras = window.MUESTRAS;
  const tipo = estudio.tipo_grafico;

  function aplanarVars() {
    return muestras.flatMap(m => m.valores);
  }

  function dibujarGraficoControl(chart, divId) {
    const layout = plotlyLayout(chart.title);
    layout.xaxis = { title: 'Subgrupo' };
    layout.yaxis = { title: 'Valor' };

    const ucl = Array.isArray(chart.ucl) ? chart.ucl : chart.subgroups.map(() => chart.ucl);
    const lcl = Array.isArray(chart.lcl) ? chart.lcl : chart.subgroups.map(() => chart.lcl);
    const cl = chart.subgroups.map(() => chart.cl);

    // Marcar puntos fuera de control en rojo
    const colores = chart.points.map((_, i) =>
      chart.out_of_control.includes(i + 1) ? UNIMAG.red : UNIMAG.blue
    );

    const traces = [
      { x: chart.subgroups, y: chart.points, mode: 'lines+markers',
        name: 'Datos', line: { color: UNIMAG.blue, width: 2 },
        marker: { color: colores, size: 8 } },
      { x: chart.subgroups, y: cl, mode: 'lines', name: 'LC',
        line: { color: UNIMAG.green, width: 2 } },
      { x: chart.subgroups, y: ucl, mode: 'lines', name: 'LSC',
        line: { color: UNIMAG.red, width: 2, dash: 'dash' } },
      { x: chart.subgroups, y: lcl, mode: 'lines', name: 'LIC',
        line: { color: UNIMAG.red, width: 2, dash: 'dash' } },
    ];

    Plotly.newPlot(divId, traces, layout, plotlyConfig);
  }

  function tablaResumen(chart, contenedor, titulo) {
    const html = `
      <div class="metric-card">
        <div class="label">${titulo} - LC (línea central)</div>
        <div class="value">${fmt(chart.cl, 4)}</div>
      </div>
      <div class="metric-card warn">
        <div class="label">${titulo} - LSC</div>
        <div class="value">${fmt(Array.isArray(chart.ucl) ? chart.ucl[0] : chart.ucl, 4)}</div>
      </div>
      <div class="metric-card warn">
        <div class="label">${titulo} - LIC</div>
        <div class="value">${fmt(Array.isArray(chart.lcl) ? chart.lcl[0] : chart.lcl, 4)}</div>
      </div>
      <div class="metric-card ${chart.out_of_control.length ? 'danger' : 'success'}">
        <div class="label">Puntos fuera de control</div>
        <div class="value">${chart.out_of_control.length}</div>
      </div>
    `;
    contenedor.insertAdjacentHTML('beforeend', html);
  }

  function renderTablaTests(n) {
    const tests = [n.shapiro, n.anderson, n.dagostino];
    let html = '<table class="data-table"><thead><tr><th>Prueba</th><th>Estadístico</th><th>p-valor</th><th>¿Normal? (α=0.05)</th><th>Interpretación</th></tr></thead><tbody>';
    tests.forEach(t => {
      if (t.error) {
        html += `<tr><td>${t.test}</td><td colspan="4" class="text-muted">${t.error}</td></tr>`;
      } else {
        const normal = t.normal ? '<span class="badge badge-green">Sí</span>' : '<span class="badge badge-red">No</span>';
        html += `<tr>
          <td>${t.test}</td>
          <td class="num">${fmt(t.statistic, 4)}</td>
          <td class="num">${t.p_value !== undefined ? fmt(t.p_value, 4) : '—'}</td>
          <td>${normal}</td>
          <td>${t.interpretation}</td>
        </tr>`;
      }
    });
    html += '</tbody></table>';
    return html;
  }

  function dibujarHistograma(h, divId) {
    const layout = plotlyLayout('Histograma + Curva Normal');
    layout.xaxis = { title: 'Valor' };
    layout.yaxis = { title: 'Frecuencia' };
    const widths = h.edges.slice(1).map((e, i) => e - h.edges[i]);
    const traces = [
      { x: h.centers, y: h.counts, type: 'bar', name: 'Frecuencia',
        marker: { color: UNIMAG.blueLt, opacity: 0.7 },
        width: widths },
      { x: h.curve_x, y: h.curve_y, mode: 'lines', name: 'Curva normal',
        line: { color: UNIMAG.orange, width: 3 } },
    ];
    Plotly.newPlot(divId, traces, layout, plotlyConfig);
  }

  function dibujarQQ(qq, divId) {
    const layout = plotlyLayout('Gráfico Q-Q (Normal)');
    layout.xaxis = { title: 'Cuantiles teóricos' };
    layout.yaxis = { title: 'Cuantiles muestrales' };
    const minVal = Math.min(...qq.theoretical);
    const maxVal = Math.max(...qq.theoretical);
    // Línea de referencia y=x escalada
    const ySamMin = Math.min(...qq.sample);
    const ySamMax = Math.max(...qq.sample);
    const slope = (ySamMax - ySamMin) / (maxVal - minVal || 1);
    const intercept = ySamMin - slope * minVal;
    const refY = [minVal, maxVal].map(x => slope * x + intercept);
    const traces = [
      { x: qq.theoretical, y: qq.sample, mode: 'markers', name: 'Cuantiles',
        marker: { color: UNIMAG.blue, size: 7 } },
      { x: [minVal, maxVal], y: refY, mode: 'lines', name: 'Referencia',
        line: { color: UNIMAG.red, width: 2, dash: 'dash' } },
    ];
    Plotly.newPlot(divId, traces, layout, plotlyConfig);
  }

  function renderDescriptive(d, divId) {
    const items = [
      ['n', d.n, ''], ['Media', d.mean, 4], ['Mediana', d.median, 4],
      ['Desv. estándar', d.std, 4], ['Varianza', d.var, 4],
      ['Mínimo', d.min, 4], ['Máximo', d.max, 4], ['Rango', d.range, 4],
      ['Q1', d.q1, 4], ['Q3', d.q3, 4], ['IQR', d.iqr, 4],
      ['Asimetría', d.skewness, 4], ['Curtosis', d.kurtosis, 4],
      ['CV (%)', d.cv, 2],
    ];
    document.getElementById(divId).innerHTML = items.map(([l, v, dec]) => `
      <div class="metric-card">
        <div class="label">${l}</div>
        <div class="value">${dec === '' ? v : fmt(v, dec)}</div>
      </div>
    `).join('');
  }

  function renderCapacidad(c, divId, chartId) {
    if (c.error) {
      document.getElementById(divId).innerHTML = `<div class="alert alert-warning">${c.error}</div>`;
      return;
    }
    const cards = [
      ['Media', c.mean, 4, ''],
      ['σ overall', c.sigma_overall, 4, ''],
      ['σ within', c.sigma_within, 4, ''],
      ['Cp', c.Cp, 3, c.Cp !== undefined ? (c.Cp >= 1.33 ? 'success' : (c.Cp >= 1 ? 'warn' : 'danger')) : ''],
      ['Cpk', c.Cpk, 3, c.Cpk !== undefined ? (c.Cpk >= 1.33 ? 'success' : (c.Cpk >= 1 ? 'warn' : 'danger')) : ''],
      ['Pp', c.Pp, 3, ''],
      ['Ppk', c.Ppk, 3, ''],
      ['% Fuera de spec', c.percent_out_of_spec, 4, ''],
      ['PPM fuera', c.ppm_out_of_spec, 0, ''],
    ];
    const html = cards.filter(([_, v]) => v !== undefined).map(([l, v, dec, cl]) => `
      <div class="metric-card ${cl}">
        <div class="label">${l}</div>
        <div class="value">${fmt(v, dec)}</div>
      </div>
    `).join('');
    document.getElementById(divId).innerHTML = html +
      (c.interpretation ? `<div class="alert alert-info" style="grid-column:1/-1">${c.interpretation}</div>` : '');

    // Gráfico de distribución vs especificaciones
    if (chartId && c.sigma_overall > 0) {
      const xMin = Math.min(c.mean - 4 * c.sigma_overall, c.lsl ?? Infinity);
      const xMax = Math.max(c.mean + 4 * c.sigma_overall, c.usl ?? -Infinity);
      const xs = [];
      const ys = [];
      const step = (xMax - xMin) / 200;
      for (let i = 0; i <= 200; i++) {
        const x = xMin + i * step;
        xs.push(x);
        const exp = -0.5 * ((x - c.mean) / c.sigma_overall) ** 2;
        ys.push(Math.exp(exp) / (c.sigma_overall * Math.sqrt(2 * Math.PI)));
      }
      const traces = [
        { x: xs, y: ys, type: 'scatter', mode: 'lines', fill: 'tozeroy',
          name: 'Distribución', line: { color: UNIMAG.blueLt } },
      ];
      const shapes = [];
      if (c.lsl !== null && c.lsl !== undefined) {
        shapes.push({ type: 'line', x0: c.lsl, x1: c.lsl, y0: 0, y1: Math.max(...ys),
          line: { color: UNIMAG.red, width: 3 } });
      }
      if (c.usl !== null && c.usl !== undefined) {
        shapes.push({ type: 'line', x0: c.usl, x1: c.usl, y0: 0, y1: Math.max(...ys),
          line: { color: UNIMAG.red, width: 3 } });
      }
      shapes.push({ type: 'line', x0: c.mean, x1: c.mean, y0: 0, y1: Math.max(...ys),
        line: { color: UNIMAG.green, width: 2, dash: 'dash' } });
      const layout = plotlyLayout('Distribución del proceso vs Especificaciones');
      layout.shapes = shapes;
      layout.xaxis = { title: 'Valor' };
      layout.yaxis = { title: 'Densidad' };
      Plotly.newPlot(chartId, traces, layout, plotlyConfig);
    }
  }

  function renderReglas(violations) {
    const div = document.getElementById('lista-reglas');
    if (!violations || violations.length === 0) {
      div.innerHTML = '<div class="alert alert-success">No se detectaron violaciones a las reglas de Nelson. El proceso parece estable.</div>';
      return;
    }
    let html = '<table class="data-table"><thead><tr><th>Punto (subgrupo)</th><th>Regla</th><th>Descripción</th></tr></thead><tbody>';
    violations.forEach(v => {
      html += `<tr><td>${v.point}</td><td><span class="badge badge-orange">R${v.rule}</span></td><td>${v.desc}</td></tr>`;
    });
    html += '</tbody></table>';
    div.innerHTML = html;
  }

  // ============ Ejecutar análisis ============
  async function ejecutar() {
    const resumen = document.getElementById('resumen-grafico');
    resumen.innerHTML = '';

    if (muestras.length < 2) {
      resumen.innerHTML = '<div class="alert alert-warning" style="grid-column:1/-1">No hay suficientes muestras para análisis.</div>';
      return;
    }

    let chartResp;
    let allViolations = [];
    try {
      if (tipo === 'xr') {
        const subgrupos = muestras.map(m => m.valores);
        chartResp = await api('/api/analisis/grafico', { method: 'POST',
          body: { tipo: 'xr', subgrupos } });
        dibujarGraficoControl(chartResp.x_chart, 'grafico-principal');
        dibujarGraficoControl(chartResp.r_chart, 'grafico-secundario');
        tablaResumen(chartResp.x_chart, resumen, 'X̄');
        tablaResumen(chartResp.r_chart, resumen, 'R');
        allViolations = [
          ...chartResp.x_chart.rules_violations.map(v => ({ ...v, chart: 'X̄' })),
          ...chartResp.r_chart.rules_violations.map(v => ({ ...v, chart: 'R' })),
        ];
      } else if (tipo === 'xs') {
        const subgrupos = muestras.map(m => m.valores);
        chartResp = await api('/api/analisis/grafico', { method: 'POST',
          body: { tipo: 'xs', subgrupos } });
        dibujarGraficoControl(chartResp.x_chart, 'grafico-principal');
        dibujarGraficoControl(chartResp.s_chart, 'grafico-secundario');
        tablaResumen(chartResp.x_chart, resumen, 'X̄');
        tablaResumen(chartResp.s_chart, resumen, 'S');
        allViolations = [
          ...chartResp.x_chart.rules_violations.map(v => ({ ...v, chart: 'X̄' })),
          ...chartResp.s_chart.rules_violations.map(v => ({ ...v, chart: 'S' })),
        ];
      } else if (tipo === 'p') {
        chartResp = await api('/api/analisis/grafico', { method: 'POST', body: {
          tipo: 'p',
          defectivos: muestras.map(m => m.valores[0]),
          tamanos: muestras.map(m => m.valores[1]),
        }});
        dibujarGraficoControl(chartResp, 'grafico-principal');
        document.getElementById('grafico-secundario').style.display = 'none';
        tablaResumen(chartResp, resumen, 'p');
        allViolations = chartResp.rules_violations;
      } else if (tipo === 'np') {
        chartResp = await api('/api/analisis/grafico', { method: 'POST', body: {
          tipo: 'np',
          defectivos: muestras.map(m => m.valores[0]),
          tamano: muestras[0].valores[1],
        }});
        dibujarGraficoControl(chartResp, 'grafico-principal');
        document.getElementById('grafico-secundario').style.display = 'none';
        tablaResumen(chartResp, resumen, 'np');
        allViolations = chartResp.rules_violations;
      } else if (tipo === 'c') {
        chartResp = await api('/api/analisis/grafico', { method: 'POST', body: {
          tipo: 'c',
          defectos: muestras.map(m => m.valores[0]),
        }});
        dibujarGraficoControl(chartResp, 'grafico-principal');
        document.getElementById('grafico-secundario').style.display = 'none';
        tablaResumen(chartResp, resumen, 'c');
        allViolations = chartResp.rules_violations;
      } else if (tipo === 'u') {
        chartResp = await api('/api/analisis/grafico', { method: 'POST', body: {
          tipo: 'u',
          defectos: muestras.map(m => m.valores[0]),
          tamanos: muestras.map(m => m.valores[1]),
        }});
        dibujarGraficoControl(chartResp, 'grafico-principal');
        document.getElementById('grafico-secundario').style.display = 'none';
        tablaResumen(chartResp, resumen, 'u');
        allViolations = chartResp.rules_violations;
      }
    } catch (e) {
      resumen.innerHTML = `<div class="alert alert-danger" style="grid-column:1/-1">Error: ${e.message}</div>`;
      return;
    }

    renderReglas(allViolations);

    // Para variables: normalidad y capacidad
    if (estudio.tipo === 'variable') {
      const flat = aplanarVars();
      try {
        const norm = await api('/api/analisis/normalidad', { method: 'POST', body: { valores: flat } });
        document.getElementById('tabla-normalidad').innerHTML = renderTablaTests(norm);
        if (norm.histogram && norm.histogram.counts && norm.histogram.counts.length) {
          dibujarHistograma(norm.histogram, 'histograma');
        }
        if (norm.qq_plot && norm.qq_plot.sample.length) {
          dibujarQQ(norm.qq_plot, 'qqplot');
        }
      } catch (e) {
        document.getElementById('tabla-normalidad').innerHTML =
          `<div class="alert alert-warning">${e.message}</div>`;
      }

      if (estudio.lsl !== null || estudio.usl !== null) {
        try {
          const cap = await api('/api/analisis/capacidad', { method: 'POST', body: {
            subgrupos: muestras.map(m => m.valores),
            lsl: estudio.lsl, usl: estudio.usl,
            tamano_subgrupo: estudio.tamano_subgrupo,
          }});
          renderCapacidad(cap, 'resumen-capacidad', 'grafico-capacidad');
        } catch (e) {
          document.getElementById('resumen-capacidad').innerHTML =
            `<div class="alert alert-warning">${e.message}</div>`;
        }
      } else {
        document.getElementById('resumen-capacidad').innerHTML =
          '<div class="alert alert-info">Define LSL y/o USL en el estudio para calcular índices de capacidad.</div>';
      }
    }
  }

  ejecutar();
})();
