// Subida de archivos Excel
(function() {
  const $file = document.getElementById('archivo-excel');
  const $btn = document.getElementById('btn-subir');
  const $feedback = document.getElementById('upload-feedback');
  if (!$btn) return;

  async function subir() {
    if (!$file.files || $file.files.length === 0) {
      $feedback.innerHTML = '<div class="alert alert-warning">Selecciona un archivo .xlsx primero.</div>';
      return;
    }
    const file = $file.files[0];
    if (!file.name.toLowerCase().endsWith('.xlsx')) {
      $feedback.innerHTML = '<div class="alert alert-danger">El archivo debe ser .xlsx</div>';
      return;
    }
    $btn.disabled = true;
    $btn.textContent = 'Subiendo…';
    $feedback.innerHTML = '<div class="alert alert-info">Procesando archivo, espera un momento…</div>';

    const fd = new FormData();
    fd.append('archivo', file);

    try {
      const res = await fetch('/api/estudios/upload', { method: 'POST', body: fd });
      const data = await res.json();
      if (!res.ok) {
        $feedback.innerHTML = `<div class="alert alert-danger"><strong>Error:</strong> ${data.error || 'fallo desconocido'}</div>`;
        $btn.disabled = false;
        $btn.textContent = 'Subir y analizar';
        return;
      }
      $feedback.innerHTML = `<div class="alert alert-success">
        Estudio #${data.id} creado con ${data.muestras} muestras. Redirigiendo…
      </div>`;
      setTimeout(() => { window.location.href = '/estudio/' + data.id; }, 800);
    } catch (e) {
      $feedback.innerHTML = `<div class="alert alert-danger">Error de red: ${e.message}</div>`;
      $btn.disabled = false;
      $btn.textContent = 'Subir y analizar';
    }
  }

  $btn.addEventListener('click', subir);
})();
