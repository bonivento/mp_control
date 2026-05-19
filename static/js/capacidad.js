(function() {
  document.getElementById('btn-ejemplo').addEventListener('click', () => {
    const arr = [];
    for (let i = 0; i < 100; i++) {
      const u1 = Math.random(), u2 = Math.random();
      const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
      arr.push((50 + z * 1.5).toFixed(3));
    }
    document.getElementById('input-datos').value = arr.join(', ');
    document.getElementById('lsl').value = 45;
    document.getElementById('usl').value = 55;
  });

  document.getElementById('btn-calcular').addEventListener('click', async () => {
    const valores = parseNumbers(document.getElementById('input-datos').value);
    const lsl = document.getElementById('lsl').value;
    const usl = document.getElementById('usl').value;
    const n = document.getElementById('n').value;
    if (valores.length < 2) return alert('Ingresa al menos 2 valores.');
    if (!lsl && !usl) return alert('Define al menos un límite (LSL o USL).');

    try {
      const r = await api('/api/analisis/capacidad', { method: 'POST', body: {
        valores, lsl: lsl || null, usl: usl || null, tamano_subgrupo: n ? parseInt(n) : null
      }});
      if (r.error) return alert(r.error);
      mostrar(r);
    } catch (e) {
      alert(e.message);
    }
  });

  function mostrar(c) {
    document.getElementById('resultados').style.display = 'block';
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
    document.getElementById('indices').innerHTML = cards
      .filter(([_, v]) => v !== undefined)
      .map(([l, v, dec, cl]) => `
        <div class="metric-card ${cl}">
          <div class="label">${l}</div>
          <div class="value">${fmt(v, dec)}</div>
        </div>`).join('');
    document.getElementById('interpretacion').textContent = c.interpretation || '';

    if (c.sigma_overall > 0) {
      const xMin = Math.min(c.mean - 4 * c.sigma_overall, c.lsl ?? Infinity);
      const xMax = Math.max(c.mean + 4 * c.sigma_overall, c.usl ?? -Infinity);
      const xs = [], ys = [];
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
      const yMax = Math.max(...ys);
      if (c.lsl !== null && c.lsl !== undefined)
        shapes.push({ type: 'line', x0: c.lsl, x1: c.lsl, y0: 0, y1: yMax,
          line: { color: UNIMAG.red, width: 3 } });
      if (c.usl !== null && c.usl !== undefined)
        shapes.push({ type: 'line', x0: c.usl, x1: c.usl, y0: 0, y1: yMax,
          line: { color: UNIMAG.red, width: 3 } });
      shapes.push({ type: 'line', x0: c.mean, x1: c.mean, y0: 0, y1: yMax,
        line: { color: UNIMAG.green, width: 2, dash: 'dash' } });
      const layout = plotlyLayout('Distribución del proceso vs Especificaciones');
      layout.shapes = shapes;
      layout.xaxis = { title: 'Valor' };
      layout.yaxis = { title: 'Densidad' };
      Plotly.newPlot('grafico', traces, layout, plotlyConfig);
    }
  }
})();
