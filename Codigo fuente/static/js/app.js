// ============================================================
// Utilidades y configuración global Plotly con paleta Unimag
// ============================================================
window.UNIMAG = {
  blue:    '#005CAB',
  blueLt:  '#0183EF',
  orange:  '#FF9400',
  green:   '#00A50B',
  red:     '#D62728',
  navy:    '#003A6B',
  purple:  '#3D01F1',
  gray:    '#5B6B7A',
};

window.plotlyLayout = function(title = '') {
  return {
    title: { text: title, font: { color: UNIMAG.navy, size: 16 } },
    paper_bgcolor: 'white',
    plot_bgcolor: '#fafcff',
    font: { family: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif', size: 12, color: '#003a6b' },
    margin: { t: 50, r: 30, b: 50, l: 60 },
    hovermode: 'closest',
    showlegend: true,
    legend: { orientation: 'h', y: -0.18, x: 0 },
  };
};

window.plotlyConfig = {
  responsive: true,
  displaylogo: false,
  toImageButtonOptions: { format: 'png', filename: 'grafico_cec', scale: 2 },
  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
};

// Tabs
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('tab')) {
    const tab = e.target.dataset.tab;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    e.target.classList.add('active');
    const panel = document.getElementById('panel-' + tab);
    if (panel) {
      panel.classList.add('active');
      // Redibujar Plotly al cambiar tab
      panel.querySelectorAll('.plotly-chart').forEach(el => {
        if (el._fullLayout) Plotly.Plots.resize(el);
      });
    }
  }
});

// Parser de datos tabulares pegados desde Excel/CSV
window.parseTabular = function(text) {
  const rows = text.trim().split(/\r?\n/).map(r =>
    r.split(/[\t,;]/).map(c => c.trim()).filter(c => c !== '')
  ).filter(r => r.length > 0);
  return rows;
};

// Parser de lista de números (separados por coma, espacio, etc.)
window.parseNumbers = function(text) {
  return text
    .split(/[\s,;]+/)
    .map(v => v.trim())
    .filter(v => v !== '')
    .map(v => parseFloat(v))
    .filter(v => !isNaN(v));
};

// API helper
window.api = async function(url, options = {}) {
  const opts = {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };
  if (opts.body && typeof opts.body !== 'string') {
    opts.body = JSON.stringify(opts.body);
  }
  const res = await fetch(url, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Error HTTP ${res.status}`);
  }
  return data;
};

// Mostrar feedback
window.flash = function(elId, message, type = 'info') {
  const el = document.getElementById(elId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
};

// Formatear número
window.fmt = function(n, decimals = 3) {
  if (n === null || n === undefined) return '—';
  if (typeof n !== 'number') return n;
  if (!isFinite(n)) return n.toString();
  return n.toLocaleString('es-CO', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};
