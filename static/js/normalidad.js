(function() {
  const $input = document.getElementById('input-datos');
  const $res = document.getElementById('resultados');

  document.getElementById('btn-ejemplo').addEventListener('click', () => {
    // Datos simulados de pH de aloe vera
    const arr = [];
    for (let i = 0; i < 50; i++) {
      const u1 = Math.random(), u2 = Math.random();
      const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
      arr.push((6.0 + z * 0.3).toFixed(3));
    }
    $input.value = arr.join(', ');
  });

  document.getElementById('btn-analizar').addEventListener('click', async () => {
    const valores = parseNumbers($input.value);
    if (valores.length < 3) {
      return alert('Se requieren al menos 3 valores.');
    }
    try {
      const r = await api('/api/analisis/normalidad', { method: 'POST', body: { valores } });
      $res.style.display = 'block';
      document.getElementById('tabla-tests').innerHTML = tablaTests(r);
      renderDesc(r.descriptive);
      if (r.histogram.counts.length) dibujarHist(r.histogram);
      if (r.qq_plot.sample.length) dibujarQQ(r.qq_plot);
    } catch (e) {
      alert(e.message);
    }
  });

  function tablaTests(n) {
    const tests = [n.shapiro, n.anderson, n.dagostino];
    let html = '<table class="data-table"><thead><tr><th>Prueba</th><th>Estadístico</th><th>p-valor</th><th>¿Normal?</th><th>Interpretación</th></tr></thead><tbody>';
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
    return html + '</tbody></table>';
  }

  function renderDesc(d) {
    const items = [
      ['n', d.n, 0], ['Media', d.mean, 4], ['Mediana', d.median, 4],
      ['Desv. estándar', d.std, 4], ['Mínimo', d.min, 4], ['Máximo', d.max, 4],
      ['CV (%)', d.cv, 2], ['Asimetría', d.skewness, 4], ['Curtosis', d.kurtosis, 4],
    ];
    document.getElementById('descriptive').innerHTML = items.map(([l, v, dec]) => `
      <div class="metric-card">
        <div class="label">${l}</div>
        <div class="value">${fmt(v, dec)}</div>
      </div>`).join('');
  }

  function dibujarHist(h) {
    const widths = h.edges.slice(1).map((e, i) => e - h.edges[i]);
    const traces = [
      { x: h.centers, y: h.counts, type: 'bar', name: 'Frecuencia',
        marker: { color: UNIMAG.blueLt, opacity: 0.7 }, width: widths },
      { x: h.curve_x, y: h.curve_y, mode: 'lines', name: 'Curva normal',
        line: { color: UNIMAG.orange, width: 3 } },
    ];
    const layout = plotlyLayout('Histograma');
    layout.xaxis = { title: 'Valor' };
    layout.yaxis = { title: 'Frecuencia' };
    Plotly.newPlot('histograma', traces, layout, plotlyConfig);
  }

  function dibujarQQ(qq) {
    const minVal = Math.min(...qq.theoretical);
    const maxVal = Math.max(...qq.theoretical);
    const ySamMin = Math.min(...qq.sample);
    const ySamMax = Math.max(...qq.sample);
    const slope = (ySamMax - ySamMin) / (maxVal - minVal || 1);
    const intercept = ySamMin - slope * minVal;
    const traces = [
      { x: qq.theoretical, y: qq.sample, mode: 'markers', name: 'Cuantiles',
        marker: { color: UNIMAG.blue, size: 7 } },
      { x: [minVal, maxVal], y: [slope * minVal + intercept, slope * maxVal + intercept],
        mode: 'lines', name: 'Referencia', line: { color: UNIMAG.red, dash: 'dash', width: 2 } },
    ];
    const layout = plotlyLayout('Gráfico Q-Q (Normal)');
    layout.xaxis = { title: 'Cuantiles teóricos' };
    layout.yaxis = { title: 'Cuantiles muestrales' };
    Plotly.newPlot('qqplot', traces, layout, plotlyConfig);
  }
})();
