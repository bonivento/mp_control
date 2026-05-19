(function() {
  const $body = document.getElementById('cuerpo');

  function agregarFila(cat = '', freq = '') {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="text" class="cat" value="${cat}" placeholder="Ej. Manchas"></td>
      <td><input type="number" class="freq" min="0" value="${freq}"></td>
      <td><button type="button" class="btn btn-secondary btn-sm btn-rm">×</button></td>
    `;
    $body.appendChild(tr);
  }

  document.getElementById('btn-add').addEventListener('click', () => agregarFila());

  document.getElementById('btn-clear').addEventListener('click', () => {
    $body.innerHTML = '';
  });

  document.getElementById('btn-ejemplo').addEventListener('click', () => {
    $body.innerHTML = '';
    const data = [
      ['Manchas', 45], ['Daños por plagas', 28], ['Golpes/magulladuras', 22],
      ['Defectos de color', 12], ['Frutos podridos', 8], ['Material extraño', 5],
      ['Empaque inadecuado', 3], ['Etiquetado incorrecto', 2],
    ];
    data.forEach(([c, f]) => agregarFila(c, f));
  });

  document.body.addEventListener('click', e => {
    if (e.target.classList.contains('btn-rm')) {
      e.target.closest('tr').remove();
    }
  });

  document.getElementById('btn-generar').addEventListener('click', async () => {
    const categorias = [], frecuencias = [];
    $body.querySelectorAll('tr').forEach(tr => {
      const c = tr.querySelector('.cat').value.trim();
      const f = parseInt(tr.querySelector('.freq').value);
      if (c && !isNaN(f)) {
        categorias.push(c);
        frecuencias.push(f);
      }
    });
    if (categorias.length === 0) return alert('Agrega al menos una categoría con frecuencia.');

    try {
      const r = await api('/api/analisis/pareto', { method: 'POST', body: { categorias, frecuencias } });
      mostrar(r);
    } catch (e) {
      alert(e.message);
    }
  });

  function mostrar(r) {
    document.getElementById('resultados').style.display = 'block';
    const traces = [
      { x: r.categories, y: r.frequencies, type: 'bar', name: 'Frecuencia',
        marker: { color: UNIMAG.blue }, yaxis: 'y' },
      { x: r.categories, y: r.cumulative_percentages, type: 'scatter',
        mode: 'lines+markers', name: '% Acumulado',
        line: { color: UNIMAG.orange, width: 3 },
        marker: { size: 8, color: UNIMAG.orange },
        yaxis: 'y2' },
    ];
    const layout = plotlyLayout('Diagrama de Pareto');
    layout.xaxis = { title: 'Categoría', tickangle: -25 };
    layout.yaxis = { title: 'Frecuencia', color: UNIMAG.blue };
    layout.yaxis2 = { title: '% Acumulado', overlaying: 'y', side: 'right',
                      range: [0, 105], color: UNIMAG.orange };
    layout.shapes = [{
      type: 'line', x0: -0.5, x1: r.categories.length - 0.5, y0: 80, y1: 80,
      yref: 'y2', line: { color: UNIMAG.red, width: 2, dash: 'dash' },
    }];
    layout.annotations = [{
      x: r.categories.length - 1, y: 80, yref: 'y2', text: 'Regla 80/20',
      showarrow: false, font: { color: UNIMAG.red }, xanchor: 'right',
    }];
    Plotly.newPlot('grafico', traces, layout, plotlyConfig);

    document.getElementById('vital-few').innerHTML =
      `<strong>Pocas vitales (≈80% del problema):</strong> ${r.vital_few.join(', ')}.<br>
       Concentra los esfuerzos de mejora en estas categorías.`;

    let html = '<table class="data-table"><thead><tr><th>#</th><th>Categoría</th><th>Frecuencia</th><th>%</th><th>% Acumulado</th></tr></thead><tbody>';
    r.categories.forEach((c, i) => {
      const inVital = r.vital_few.includes(c);
      html += `<tr ${inVital ? 'style="background:#fff8ec"' : ''}>
        <td>${i + 1}</td><td><strong>${c}</strong></td>
        <td class="num">${r.frequencies[i]}</td>
        <td class="num">${fmt(r.percentages[i], 2)}</td>
        <td class="num">${fmt(r.cumulative_percentages[i], 2)}</td>
      </tr>`;
    });
    html += '</tbody></table>';
    document.getElementById('tabla-resumen').innerHTML = html;
  }
})();
