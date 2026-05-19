# Manual de Usuario

## Sistema de Control Estadístico de Calidad
### Frutas, Hortalizas y Plantas Medicinales
**Universidad del Magdalena – 2026-1**

---

## 1. Acceso al sistema

Abre la URL del despliegue (local: `http://localhost:5050`, producción: la URL de Vercel).
En la pantalla principal verás:

- **Inicio**: lista de estudios registrados.
- **Nuevo Estudio**: formulario para registrar un nuevo control.
- **Normalidad**: herramienta independiente para evaluar normalidad.
- **Capacidad**: cálculo independiente de Cp/Cpk/Pp/Ppk.
- **Pareto**: diagrama de Pareto independiente.
- **Manual**: ayuda integrada.

---

## 2. Crear un nuevo estudio

1. Clic en **+ Nuevo estudio**.
2. Completa la **trazabilidad**:
   - Nombre del estudio (Ej. "Peso de mango Tommy")
   - Producto (Ej. Mango, Sábila, etc.)
   - Característica controlada (Ej. Peso, pH, Manchas)
   - Unidad (g, cm, %, °Bx, …)
   - Analista, Lote (opcional)
3. Selecciona el **tipo de gráfico**:
   - **X̄-R**: variables continuas, subgrupos de 2-9 mediciones.
   - **X̄-S**: variables continuas, subgrupos ≥ 10.
   - **p**: proporción de defectuosos (tamaño de muestra variable).
   - **np**: número de defectuosos (tamaño de muestra constante).
   - **c**: defectos por unidad (área constante).
   - **u**: defectos por unidad (área variable).
4. Para variables, opcionalmente define **LSL** y **USL** (límites de especificación)
   para que el sistema calcule capacidad del proceso.
5. Ingresa los datos:
   - **Variables**: cada fila es un subgrupo, cada columna una medición.
   - **Atributos**: cada fila es un subgrupo con su conteo.
   - Botones disponibles:
     - **+ Agregar subgrupo**: nueva fila.
     - **+25 subgrupos**: agrega 25 filas vacías de una vez.
     - **Pegar desde Excel**: copia datos desde Excel, click en el botón y pega (formato TSV).
     - **Datos de ejemplo**: rellena un dataset demo.
6. Clic en **Guardar estudio y analizar**.

> El sistema te advertirá si tienes menos de 25 subgrupos (el requisito académico).

---

## 3. Página de resultados del estudio

Al guardar, se abre la página del estudio con 4 pestañas:

### Gráfico de control
- Gráfico principal (X̄, p, np, c, o u).
- Gráfico secundario (R o S, según corresponda).
- Métricas: LC, LSC, LIC y conteo de puntos fuera de control.
- Los puntos rojos indican violaciones.

### Normalidad (solo variables)
- Tabla con resultados de Shapiro-Wilk, Anderson-Darling y D'Agostino.
- Estadística descriptiva (media, mediana, std, asimetría, curtosis, CV…).
- Histograma con curva normal superpuesta.
- Gráfico Q-Q.

### Capacidad del proceso (solo variables con LSL/USL)
- Índices Cp, Cpk, Pp, Ppk.
- Interpretación automática.
- Porcentaje y PPM fuera de especificación.
- Gráfico de la distribución vs los límites.

### Datos crudos
- Tabla con todos los subgrupos registrados.

### Reglas de Nelson
- Lista de violaciones detectadas por punto y regla.

---

## 4. Exportar a Excel

Desde la página del estudio, clic en **Exportar a Excel**. Se descarga un archivo `.xlsx`
con 3 hojas:

1. **Trazabilidad**: toda la información del estudio.
2. **Datos**: muestras registradas.
3. **Resultados**: salida completa del análisis estadístico (JSON estructurado para
   auditoría y rehacer análisis externos si se requiere).

---

## 5. Herramientas independientes

### Normalidad (`/normalidad`)
Pega o escribe valores numéricos separados por coma, espacio o salto de línea.
Útil para evaluar un conjunto de datos rápido sin registrar un estudio.

### Capacidad (`/capacidad`)
Define LSL/USL y pega los valores. El sistema calcula Cp, Cpk, Pp, Ppk.
Si los datos vienen en subgrupos, indica el tamaño para que use sigma within.

### Pareto (`/pareto`)
Agrega categorías y frecuencias. El sistema:
- Ordena de mayor a menor.
- Calcula porcentajes y porcentaje acumulado.
- Dibuja el diagrama de Pareto.
- Identifica las "pocas vitales" (≈80% del problema).

---

## 6. Interpretación de Cpk

| Valor       | Estado del proceso             |
|-------------|--------------------------------|
| ≥ 1.67      | Clase mundial                  |
| 1.33 – 1.67 | Capaz                          |
| 1.00 – 1.33 | Adecuado, control estricto     |
| 0.67 – 1.00 | Parcialmente capaz, mejorar    |
| < 0.67      | Incapaz, acción inmediata      |

---

## 7. Reglas de Nelson implementadas

1. **Regla 1**: 1 punto fuera de ±3σ.
2. **Regla 2**: 9 puntos consecutivos del mismo lado de la línea central.
3. **Regla 3**: 6 puntos consecutivos en tendencia (creciente o decreciente).
4. **Regla 4**: 14 puntos alternando arriba/abajo.
5. **Regla 5**: 2 de 3 puntos más allá de ±2σ del mismo lado.
6. **Regla 6**: 4 de 5 puntos más allá de ±1σ del mismo lado.

Una violación a cualquiera de estas reglas sugiere la presencia de una **causa asignable**
que debe investigarse.

---

## 8. Preguntas frecuentes

**P: ¿Cuántos subgrupos necesito?**
R: Mínimo 25 para validez estadística adecuada (estándar industrial). El sistema
también funciona con menos, pero advierte al usuario.

**P: ¿Puedo controlar varias características de un mismo producto?**
R: Sí. Crea un estudio por cada característica (Ej. "Peso de mango", "pH de mango").

**P: ¿Los datos se guardan en la nube si uso Vercel?**
R: No. Vercel Serverless usa filesystem efímero; los datos sólo persisten dentro
de la misma invocación. Para producción real, conectar una BD externa (Postgres).

**P: ¿Cómo interpreto el p-valor en las pruebas de normalidad?**
R: Si p > 0.05, no se rechaza la hipótesis de normalidad. Si p < 0.05, los datos
**no** son normales y deberías considerar transformaciones (log, Box-Cox) o
gráficos no paramétricos.
