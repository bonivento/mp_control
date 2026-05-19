// Formulario de registro de estudios
(function() {
  const $tipo = document.getElementById('tipo');
  const $tipoGrafico = document.getElementById('tipo_grafico');
  const $n = document.getElementById('tamano_subgrupo');
  const $grupoN = document.getElementById('grupo-n');
  const $secVars = document.getElementById('seccion-variables');
  const $secAttrs = document.getElementById('seccion-atributos');
  const $tablaVarsHead = document.getElementById('encabezados-vars');
  const $tablaVarsBody = document.getElementById('cuerpo-vars');
  const $tablaAttrsBody = document.getElementById('cuerpo-attr');
  const $thDef = document.getElementById('th-defectos');
  const $thTam = document.getElementById('th-tamano');

  function modoAtributo() {
    return ['p', 'np', 'c', 'u'].includes($tipoGrafico.value);
  }

  function sincronizarTipo() {
    if (modoAtributo()) {
      $tipo.value = 'atributo';
      $secVars.style.display = 'none';
      $secAttrs.style.display = 'block';
      $grupoN.style.display = 'none';
      // Ajustar columnas atributo
      const t = $tipoGrafico.value;
      if (t === 'p') { $thDef.textContent = 'Defectivos'; $thTam.style.display = ''; }
      else if (t === 'np') { $thDef.textContent = 'Defectivos'; $thTam.style.display = ''; }
      else if (t === 'c') { $thDef.textContent = 'Defectos'; $thTam.style.display = 'none'; }
      else if (t === 'u') { $thDef.textContent = 'Defectos'; $thTam.style.display = ''; }
    } else {
      $tipo.value = 'variable';
      $secVars.style.display = 'block';
      $secAttrs.style.display = 'none';
      $grupoN.style.display = '';
      construirEncabezadosVars();
    }
  }

  function construirEncabezadosVars() {
    const n = Math.max(2, Math.min(25, parseInt($n.value) || 5));
    let html = '<th>Subgrupo</th>';
    for (let i = 1; i <= n; i++) html += `<th>Med. ${i}</th>`;
    html += '<th></th>';
    $tablaVarsHead.innerHTML = html;
    // Reajustar filas existentes
    $tablaVarsBody.querySelectorAll('tr').forEach(tr => ajustarFilaVars(tr, n));
  }

  function ajustarFilaVars(tr, n) {
    const tds = tr.querySelectorAll('td');
    const currentInputs = tr.querySelectorAll('input.med');
    const subg = tds[0].textContent;
    let html = `<td>${subg}</td>`;
    for (let i = 0; i < n; i++) {
      const v = currentInputs[i] ? currentInputs[i].value : '';
      html += `<td><input type="number" step="any" class="med" value="${v}"></td>`;
    }
    html += `<td><button type="button" class="btn btn-secondary btn-sm btn-rm">×</button></td>`;
    tr.innerHTML = html;
  }

  function agregarFilaVars() {
    const n = parseInt($n.value) || 5;
    const idx = $tablaVarsBody.querySelectorAll('tr').length + 1;
    const tr = document.createElement('tr');
    let html = `<td>${idx}</td>`;
    for (let i = 0; i < n; i++) html += `<td><input type="number" step="any" class="med"></td>`;
    html += `<td><button type="button" class="btn btn-secondary btn-sm btn-rm">×</button></td>`;
    tr.innerHTML = html;
    $tablaVarsBody.appendChild(tr);
  }

  function agregarFilaAttrs() {
    const idx = $tablaAttrsBody.querySelectorAll('tr').length + 1;
    const tr = document.createElement('tr');
    const showTam = $thTam.style.display !== 'none';
    tr.innerHTML = `
      <td>${idx}</td>
      <td><input type="number" min="0" class="def"></td>
      <td${showTam ? '' : ' style="display:none"'}><input type="number" min="1" class="tam"></td>
      <td><button type="button" class="btn btn-secondary btn-sm btn-rm">×</button></td>
    `;
    $tablaAttrsBody.appendChild(tr);
  }

  function renumerar(tbody) {
    tbody.querySelectorAll('tr').forEach((tr, i) => {
      tr.querySelector('td').textContent = i + 1;
    });
  }

  // Recolectar datos de los formularios
  function recolectarVars() {
    const subgrupos = [];
    $tablaVarsBody.querySelectorAll('tr').forEach(tr => {
      const vals = [...tr.querySelectorAll('input.med')]
        .map(i => parseFloat(i.value))
        .filter(v => !isNaN(v));
      if (vals.length > 0) subgrupos.push(vals);
    });
    return subgrupos;
  }

  function recolectarAttrs() {
    const data = [];
    $tablaAttrsBody.querySelectorAll('tr').forEach(tr => {
      const def = parseFloat(tr.querySelector('input.def').value);
      const tamInput = tr.querySelector('input.tam');
      const tam = tamInput ? parseFloat(tamInput.value) : null;
      if (!isNaN(def)) data.push({ def, tam });
    });
    return data;
  }

  // Event listeners
  $tipoGrafico.addEventListener('change', sincronizarTipo);
  $n.addEventListener('change', construirEncabezadosVars);
  $n.addEventListener('input', construirEncabezadosVars);

  document.getElementById('btn-add-row').addEventListener('click', agregarFilaVars);
  document.getElementById('btn-add-5').addEventListener('click', () => {
    for (let i = 0; i < 5; i++) agregarFilaVars();
  });
  document.getElementById('btn-add-25').addEventListener('click', () => {
    for (let i = 0; i < 25; i++) agregarFilaVars();
  });
  document.getElementById('btn-clear').addEventListener('click', () => {
    $tablaVarsBody.innerHTML = '';
  });

  document.getElementById('btn-add-row-attr').addEventListener('click', agregarFilaAttrs);
  document.getElementById('btn-add-25-attr').addEventListener('click', () => {
    for (let i = 0; i < 25; i++) agregarFilaAttrs();
  });
  document.getElementById('btn-clear-attr').addEventListener('click', () => {
    $tablaAttrsBody.innerHTML = '';
  });

  // Pegar desde Excel
  document.getElementById('btn-paste').addEventListener('click', async () => {
    const txt = prompt('Pega aquí los datos (TSV o CSV). Una fila = un subgrupo.');
    if (!txt) return;
    const rows = parseTabular(txt);
    if (rows.length === 0) return;
    const n = rows[0].length;
    if (n >= 2 && n <= 25) $n.value = n;
    construirEncabezadosVars();
    $tablaVarsBody.innerHTML = '';
    rows.forEach((row, idx) => {
      const tr = document.createElement('tr');
      let html = `<td>${idx + 1}</td>`;
      for (let i = 0; i < parseInt($n.value); i++) {
        html += `<td><input type="number" step="any" class="med" value="${row[i] || ''}"></td>`;
      }
      html += `<td><button type="button" class="btn btn-secondary btn-sm btn-rm">×</button></td>`;
      tr.innerHTML = html;
      $tablaVarsBody.appendChild(tr);
    });
  });

  document.getElementById('btn-paste-attr').addEventListener('click', () => {
    const txt = prompt('Pega los datos. 2 columnas: defectivos/defectos + tamaño. (1 columna para c o np)');
    if (!txt) return;
    const rows = parseTabular(txt);
    $tablaAttrsBody.innerHTML = '';
    rows.forEach((row) => {
      agregarFilaAttrs();
      const tr = $tablaAttrsBody.lastChild;
      tr.querySelector('input.def').value = row[0] || '';
      if (row[1] && tr.querySelector('input.tam')) {
        tr.querySelector('input.tam').value = row[1];
      }
    });
  });

  // Datos de ejemplo
  document.getElementById('btn-sample-data').addEventListener('click', () => {
    // Peso de mango (g) - 25 subgrupos de tamaño 5
    $n.value = 5;
    construirEncabezadosVars();
    $tablaVarsBody.innerHTML = '';
    const data = generarMuestraVariable(25, 5, 250, 15);
    data.forEach((sg, idx) => {
      const tr = document.createElement('tr');
      let html = `<td>${idx + 1}</td>`;
      for (let i = 0; i < 5; i++) {
        html += `<td><input type="number" step="any" class="med" value="${sg[i].toFixed(2)}"></td>`;
      }
      html += `<td><button type="button" class="btn btn-secondary btn-sm btn-rm">×</button></td>`;
      tr.innerHTML = html;
      $tablaVarsBody.appendChild(tr);
    });
    // Sugerir trazabilidad
    if (!document.querySelector('[name=nombre]').value) {
      document.querySelector('[name=nombre]').value = 'Peso de mango Tommy';
      document.querySelector('[name=producto]').value = 'Mango Tommy';
      document.querySelector('[name=caracteristica]').value = 'Peso';
      document.querySelector('[name=unidad]').value = 'g';
      document.querySelector('[name=analista]').value = 'Analista demo';
      document.querySelector('[name=lote]').value = 'L-2026-001';
      document.querySelector('[name=lsl]').value = '220';
      document.querySelector('[name=usl]').value = '290';
    }
  });

  document.getElementById('btn-sample-attr').addEventListener('click', () => {
    $tablaAttrsBody.innerHTML = '';
    const t = $tipoGrafico.value;
    // 25 subgrupos
    for (let i = 0; i < 25; i++) {
      agregarFilaAttrs();
      const tr = $tablaAttrsBody.lastChild;
      if (t === 'p') {
        const n = 100;
        const p = 0.05 + Math.random() * 0.04;
        tr.querySelector('input.def').value = Math.round(p * n);
        tr.querySelector('input.tam').value = n;
      } else if (t === 'np') {
        tr.querySelector('input.def').value = Math.round(2 + Math.random() * 5);
        tr.querySelector('input.tam').value = 50;
      } else if (t === 'c') {
        tr.querySelector('input.def').value = Math.round(3 + Math.random() * 6);
      } else if (t === 'u') {
        const n = 8 + Math.round(Math.random() * 6);
        tr.querySelector('input.def').value = Math.round(n * (0.4 + Math.random() * 0.5));
        tr.querySelector('input.tam').value = n;
      }
    }
    if (!document.querySelector('[name=nombre]').value) {
      document.querySelector('[name=nombre]').value = 'Defectos en lotes de aguacate';
      document.querySelector('[name=producto]').value = 'Aguacate Hass';
      document.querySelector('[name=caracteristica]').value = 'Frutos con manchas';
      document.querySelector('[name=analista]').value = 'Analista demo';
      document.querySelector('[name=lote]').value = 'L-2026-002';
    }
  });

  // Eliminar fila
  document.body.addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-rm')) {
      const tr = e.target.closest('tr');
      const tbody = tr.parentElement;
      tr.remove();
      renumerar(tbody);
    }
  });

  // Submit
  document.getElementById('form-estudio').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const tipoG = fd.get('tipo_grafico');
    const payload = {
      nombre: fd.get('nombre'),
      producto: fd.get('producto'),
      tipo: fd.get('tipo'),
      caracteristica: fd.get('caracteristica'),
      unidad: fd.get('unidad'),
      analista: fd.get('analista'),
      lote: fd.get('lote'),
      tipo_grafico: tipoG,
      lsl: fd.get('lsl') ? parseFloat(fd.get('lsl')) : null,
      usl: fd.get('usl') ? parseFloat(fd.get('usl')) : null,
      tamano_subgrupo: fd.get('tamano_subgrupo') ? parseInt(fd.get('tamano_subgrupo')) : null,
      notas: fd.get('notas'),
    };

    let muestras = [];
    if (modoAtributo()) {
      const data = recolectarAttrs();
      if (data.length < 2) {
        return flash('form-feedback', 'Se requieren al menos 2 subgrupos.', 'danger');
      }
      data.forEach((d, idx) => {
        const v = (tipoG === 'c') ? [d.def] : [d.def, d.tam];
        muestras.push({ subgrupo: idx + 1, valores: v });
      });
    } else {
      const subgrupos = recolectarVars();
      if (subgrupos.length < 2) {
        return flash('form-feedback', 'Se requieren al menos 2 subgrupos con valores.', 'danger');
      }
      subgrupos.forEach((sg, idx) => {
        muestras.push({ subgrupo: idx + 1, valores: sg });
      });
    }

    if (muestras.length < 25) {
      const ok = confirm(`Solo tienes ${muestras.length} subgrupos. El estándar recomienda al menos 25. ¿Continuar?`);
      if (!ok) return;
    }

    payload.muestras = muestras;
    try {
      const r = await api('/api/estudios', { method: 'POST', body: payload });
      window.location.href = '/estudio/' + r.id;
    } catch (err) {
      flash('form-feedback', err.message, 'danger');
    }
  });

  // Init
  sincronizarTipo();
  construirEncabezadosVars();

  // Generar muestras de ejemplo (distribución normal aproximada con Box-Muller)
  function generarMuestraVariable(nSub, n, media, sigma) {
    const data = [];
    for (let i = 0; i < nSub; i++) {
      const sg = [];
      // Algunos subgrupos ligeramente fuera para mostrar reglas
      const shift = (i === 7 || i === 18) ? sigma * 0.8 : 0;
      for (let j = 0; j < n; j++) {
        const u1 = Math.random();
        const u2 = Math.random();
        const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        sg.push(media + shift + z * sigma);
      }
      data.push(sg);
    }
    return data;
  }
})();
