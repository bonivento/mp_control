// Filtros y eliminación en la lista de estudios anteriores
(function() {
  const $texto = document.getElementById('filtro-texto');
  const $tipo = document.getElementById('filtro-tipo');
  const $graf = document.getElementById('filtro-grafico');
  const $orden = document.getElementById('filtro-orden');
  const $contador = document.getElementById('contador-estudios');
  const $tabla = document.getElementById('tabla-estudios');
  const $sin = document.getElementById('sin-resultados');
  if (!$tabla) return;

  const tbody = $tabla.querySelector('tbody');
  const filasOriginales = [...tbody.querySelectorAll('tr')];
  const total = filasOriginales.length;

  function aplicarFiltros() {
    const q = ($texto.value || '').trim().toLowerCase();
    const tFiltro = $tipo.value;
    const gFiltro = $graf.value;
    const ord = $orden.value;

    let visibles = filasOriginales.filter(tr => {
      if (q && !tr.dataset.busqueda.includes(q)) return false;
      if (tFiltro && tr.dataset.tipo !== tFiltro) return false;
      if (gFiltro && tr.dataset.grafico !== gFiltro) return false;
      return true;
    });

    // Ordenar
    visibles.sort((a, b) => {
      switch (ord) {
        case 'fecha-asc':
          return a.dataset.fecha.localeCompare(b.dataset.fecha);
        case 'fecha-desc':
          return b.dataset.fecha.localeCompare(a.dataset.fecha);
        case 'nombre-asc':
          return a.dataset.nombre.localeCompare(b.dataset.nombre);
        case 'producto-asc':
          return a.dataset.producto.localeCompare(b.dataset.producto);
        default:
          return 0;
      }
    });

    // Re-render
    filasOriginales.forEach(tr => tr.style.display = 'none');
    visibles.forEach(tr => {
      tbody.appendChild(tr);
      tr.style.display = '';
    });

    $contador.textContent = `Mostrando ${visibles.length} de ${total} estudios.`;
    $sin.style.display = visibles.length === 0 ? '' : 'none';
  }

  [$texto, $tipo, $graf, $orden].forEach(el => {
    el && el.addEventListener('input', aplicarFiltros);
    el && el.addEventListener('change', aplicarFiltros);
  });

  // Eliminar estudio
  document.body.addEventListener('click', async (e) => {
    if (!e.target.classList.contains('btn-eliminar')) return;
    const id = e.target.dataset.id;
    const nombre = e.target.dataset.nombre;
    if (!confirm(`¿Eliminar el estudio "${nombre}" (#${id})?\nEsta acción es irreversible y borra también sus muestras.`)) {
      return;
    }
    e.target.disabled = true;
    try {
      const res = await fetch(`/api/estudios/${id}`, { method: 'DELETE' });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || `HTTP ${res.status}`);
      }
      const tr = e.target.closest('tr');
      tr.remove();
      const idx = filasOriginales.indexOf(tr);
      if (idx >= 0) filasOriginales.splice(idx, 1);
      aplicarFiltros();
    } catch (err) {
      alert('No se pudo eliminar: ' + err.message);
      e.target.disabled = false;
    }
  });
})();
