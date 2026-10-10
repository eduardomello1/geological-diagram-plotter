const points = [];
const selectedIndices = new Set();
const undoStack = [];
const redoStack = [];
let isDirty = false;
const initial = {
  fields: [],
  points: [],
  templates: {},
  axes: ["A", "B", "C"],
  template: "general"
};

function api() { return window.pywebview.api; }
function syncDirtyState() {
  const bridge = window.pywebview && window.pywebview.api;
  if (bridge && typeof bridge.set_unexported_changes === "function") {
    bridge.set_unexported_changes(isDirty);
  }
}
function showStatus(message, error = true) {
  const status = document.getElementById("status");
  status.textContent = message;
  status.style.color = error ? "#a23b25" : "#267342";
}
function renderTable() {
  document.getElementById("points").innerHTML = points.map((point, index) => `
    <tr data-index="${index}" class="${selectedIndices.has(index) ? "selected" : ""}">
      <td class="selection-column"><input class="point-selection" type="checkbox" data-index="${index}" aria-label="selecionar ponto ${escapeHtml(point.name)}" ${selectedIndices.has(index) ? "checked" : ""}></td>
      <td><input data-key="name" value="${escapeHtml(point.name)}"></td>
      <td><input data-key="wo" type="number" min="0" step="any" value="${point.wo}"></td>
      <td><input data-key="en" type="number" min="0" step="any" value="${point.en}"></td>
      <td><input data-key="fs" type="number" min="0" step="any" value="${point.fs}"></td>
      <td><button class="remove-point" data-index="${index}" title="remover ponto" aria-label="remover ponto">X</button></td>
    </tr>`).join("");
  document.querySelectorAll("#points input[data-key]").forEach(input => input.addEventListener("change", editPoint));
  document.querySelectorAll(".point-selection").forEach(checkbox => checkbox.addEventListener("change", event => {
    toggleSelection(Number(event.target.dataset.index));
  }));
  document.querySelectorAll(".remove-point").forEach(button => button.addEventListener("click", () => {
    const index = Number(button.dataset.index);
    const indices = selectedIndices.has(index) && selectedIndices.size > 1
      ? [...selectedIndices] : [index];
    removePoints(indices);
  }));
  document.querySelectorAll("#points tr").forEach(row => row.addEventListener("click", event => {
    if (event.target.closest("input, button")) return;
    toggleSelection(Number(row.dataset.index));
  }));
  updateSelectAllCheckbox();
  updateBulkRemoveButton();
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[char]));
}
function editPoint(event) {
  const row = event.target.closest("tr");
  const point = points[Number(row.dataset.index)];
  const key = event.target.dataset.key;
  const value = key === "name" ? event.target.value : Number(event.target.value);
  if (Object.is(point[key], value)) return;
  recordHistory();
  point[key] = value;
  isDirty = true;
  syncDirtyState();
  updateChart();
  updateHistoryButtons();
}
function pointTrace() {
  const normalized = points.map(p => {
    const total = p.wo + p.en + p.fs;
    return total > 0 ? { a: p.wo * 100 / total, b: p.en * 100 / total, c: p.fs * 100 / total } : { a: 0, b: 0, c: 0 };
  });
  const axis = initial.axes;
  const trace = { type: "scatterternary", mode: "markers", uid: "sample-points", meta: { role: "samples" },
    a: normalized.map(p => p.a), b: normalized.map(p => p.b), c: normalized.map(p => p.c),
    text: points.map(p => p.name), customdata: points.map((_, i) => i),
    hovertemplate: `<b>%{text}</b><br>${axis[0]}: %{a:.2f}%<br>${axis[1]}: %{b:.2f}%<br>${axis[2]}: %{c:.2f}%<extra></extra>`,
    marker: { size: 11, color: "#202a33", opacity: 1, line: { color: "white", width: 1 } }, name: "Amostras", showlegend: false };
  if (selectedIndices.size) {
    trace.selectedpoints = [...selectedIndices];
    trace.selected = { marker: { opacity: 1 } };
    trace.unselected = { marker: { opacity: 0.25 } };
  }
  return trace;
}
function sampleTraceIndex(data) {
  return data.findIndex(trace => trace.meta && trace.meta.role === "samples");
}
function updateChart() {
  return Plotly.react("chart", [...initial.fields, pointTrace()], {
    template: "plotly_white",
    paper_bgcolor: "white",
    plot_bgcolor: "white",
    showlegend: false,
    ternary: { sum: 100, bgcolor: "white",
      aaxis: { title: { text: initial.axes[0] }, min: 0, linewidth: 1, linecolor: "#222", gridcolor: "#d5d9dc", showgrid: true },
      baxis: { title: { text: initial.axes[1] }, min: 0, linewidth: 1, linecolor: "#222", gridcolor: "#d5d9dc", showgrid: true },
      caxis: { title: { text: initial.axes[2] }, min: 0, linewidth: 1, linecolor: "#222", gridcolor: "#d5d9dc", showgrid: true } },
    margin: { t: 30, l: 55, r: 55, b: 75 }, legend: { orientation: "h" }, paper_bgcolor: "white"
  }, { responsive: true, displaylogo: false, modeBarButtonsToRemove: ["toImage"] }).then(bindChartEvents);
}
function bindChartEvents() {
  const chart = document.getElementById("chart");
  if (chart.dataset.eventsBound) return;
  chart.dataset.eventsBound = "true";
  chart.on("plotly_hover", event => {
    document.querySelectorAll("#points tr").forEach(row => row.classList.remove("active"));
    const index = event.points[0] && event.points[0].customdata;
    const row = document.querySelector(`#points tr[data-index="${index}"]`);
    if (index !== undefined && row) row.classList.add("active");
  });
  chart.on("plotly_unhover", () => document.querySelectorAll("#points tr").forEach(row => row.classList.remove("active")));
  chart.on("plotly_selected", event => {
    selectedIndices.clear();
    (event && event.points || []).forEach(point => {
      if (!point.data || !point.data.meta || point.data.meta.role !== "samples") return;
      const index = Number(point.customdata);
      if (Number.isInteger(index) && index >= 0 && index < points.length) selectedIndices.add(index);
    });
    renderTable();
  });
  chart.on("plotly_deselect", () => {
    selectedIndices.clear();
    renderTable();
  });
  chart.on("plotly_click", event => {
    const point = event && event.points && event.points[0];
    if (
      point &&
      point.customdata !== undefined &&
      point.data &&
      point.data.meta &&
      point.data.meta.role === "samples"
    ) toggleSelection(Number(point.customdata));
  });
}
function setPoints(items) {
  selectedIndices.clear();
  points.splice(0, points.length, ...items.map(p => ({ name: p.name, wo: Number(p.wo), en: Number(p.en), fs: Number(p.fs) })));
  renderTable(); updateChart();
}
function snapshot() {
  return points.map(point => ({ name: point.name, wo: point.wo, en: point.en, fs: point.fs }));
}
function recordHistory() {
  undoStack.push(snapshot());
  redoStack.length = 0;
  updateHistoryButtons();
}
function restoreSnapshot(items) {
  selectedIndices.clear();
  points.splice(0, points.length, ...items.map(point => ({ ...point })));
  renderTable();
  updateChart();
}
function undo() {
  if (!undoStack.length) return;
  redoStack.push(snapshot());
  restoreSnapshot(undoStack.pop());
  isDirty = true;
  syncDirtyState();
  updateHistoryButtons();
}
function redo() {
  if (!redoStack.length) return;
  undoStack.push(snapshot());
  restoreSnapshot(redoStack.pop());
  isDirty = true;
  syncDirtyState();
  updateHistoryButtons();
}
function toggleSelection(index) {
  if (!Number.isInteger(index) || index < 0 || index >= points.length) return;
  if (selectedIndices.has(index)) selectedIndices.delete(index);
  else selectedIndices.add(index);
  renderTable();
  const traceIndex = sampleTraceIndex(document.getElementById("chart").data);
  if (traceIndex >= 0) {
    Plotly.restyle("chart", {
      selectedpoints: selectedIndices.size ? [[...selectedIndices]] : [null],
      selected: selectedIndices.size ? [{ marker: { opacity: 1 } }] : [null],
      unselected: selectedIndices.size ? [{ marker: { opacity: 0.25 } }] : [null]
    }, [traceIndex]);
  }
}
function cloneForExport(graph) {
  const data = JSON.parse(JSON.stringify(graph.data));
  const layout = JSON.parse(JSON.stringify(graph.layout));
  const traceIndex = sampleTraceIndex(data);
  data.forEach(trace => {
    delete trace.selectedpoints;
    delete trace.selected;
    delete trace.unselected;
    if (trace.meta && trace.meta.role === "samples") {
      trace.marker = { ...(trace.marker || {}), opacity: 1 };
    }
  });
  return { data, layout };
}
function updateSelectAllCheckbox() {
  const checkbox = document.getElementById("select-all");
  const selectedCount = selectedIndices.size;
  checkbox.checked = points.length > 0 && selectedCount === points.length;
  checkbox.indeterminate = selectedCount > 0 && selectedCount < points.length;
}
function removePoints(indices) {
  const validIndices = [...new Set(indices)].filter(index => Number.isInteger(index) && index >= 0 && index < points.length);
  if (!validIndices.length) return;
  recordHistory();
  const removals = new Set(validIndices);
  points.splice(0, points.length, ...points.filter((_, index) => !removals.has(index)));
  selectedIndices.clear();
  renderTable();
  updateChart();
  isDirty = true;
  syncDirtyState();
  updateHistoryButtons();
}
function updateBulkRemoveButton() {
  const button = document.getElementById("remove-selected");
  button.hidden = selectedIndices.size === 0;
  button.textContent = `Remover selecionados (${selectedIndices.size})`;
}
function setTemplate(key) {
  const selected = initial.templates[key];
  initial.template = key;
  initial.axes = selected.axes;
  initial.fields = selected.fields;
  document.querySelectorAll("th[data-axis]").forEach(th => th.textContent = initial.axes[Number(th.dataset.axis)]);
  updateChart();
}
async function loadCsv() {
  try {
    const path = await api().choose_csv();
    if (!path) return;
    const importedPoints = await api().read_data(path);
    recordHistory();
    setPoints(importedPoints);
    isDirty = true;
    syncDirtyState();
    updateHistoryButtons();
    showStatus(`${points.length} ponto(s) importado(s).`, false);
  } catch (error) { showStatus(error.message); }
}
document.getElementById("load-csv").onclick = loadCsv;
document.getElementById("template").onchange = event => setTemplate(event.target.value);
document.getElementById("select-all").onchange = event => {
  selectedIndices.clear();
  if (event.target.checked) points.forEach((_, index) => selectedIndices.add(index));
  renderTable();
  updateChart();
};
document.getElementById("add-point").onclick = () => {
  recordHistory();
  points.push({name:`Amostra-${points.length + 1}`,wo:0,en:50,fs:50});
  renderTable();
  updateChart();
  isDirty = true;
  syncDirtyState();
  updateHistoryButtons();
};
document.getElementById("remove-selected").onclick = () => {
  if (selectedIndices.size) removePoints([...selectedIndices]);
};
document.getElementById("undo").onclick = undo;
document.getElementById("redo").onclick = redo;
document.addEventListener("keydown", event => {
  if (!event.ctrlKey) return;
  if (event.key.toLowerCase() === "z" && !event.shiftKey) {
    event.preventDefault();
    undo();
  } else if (event.key.toLowerCase() === "y" || (event.key.toLowerCase() === "z" && event.shiftKey)) {
    event.preventDefault();
    redo();
  }
});
document.querySelectorAll(".exports button").forEach(button => button.onclick = async () => {
  try {
    const format = button.dataset.format;
    const graph = document.getElementById("chart");
    const saved = await api().export_file(JSON.stringify(cloneForExport(graph)), format);
    if (saved) showStatus(`Arquivo exportado: ${saved}`, false);
  } catch (error) { showStatus(error.message); }
});
document.querySelectorAll(".table-exports button").forEach(button => button.onclick = async () => {
  try {
    const saved = await api().export_table(
      JSON.stringify(points),
      JSON.stringify(initial.axes),
      button.dataset.tableFormat,
      initial.template,
    );
    if (saved) {
      isDirty = false;
      syncDirtyState();
      showStatus(`Tabela exportada: ${saved}`, false);
    }
  } catch (error) { showStatus(error.message); }
});
function updateHistoryButtons() {
  document.getElementById("undo").disabled = !undoStack.length;
  document.getElementById("redo").disabled = !redoStack.length;
}
let initialized = false;
let initializationTimer = null;
async function initializeApplication() {
  const bridge = window.pywebview && window.pywebview.api;
  if (initialized || !bridge || typeof bridge.initial_data !== "function") return false;
  initialized = true;
  try {
    const payload = await bridge.initial_data();
    initial.templates = payload.templates;
    const picker = document.getElementById("template");
    picker.innerHTML = Object.entries(initial.templates).map(([key, value]) => `<option value="${key}">${escapeHtml(value.label)}</option>`).join("");
    picker.value = payload.template;
    initial.axes = initial.templates[payload.template].axes;
    setPoints(payload.points);
    undoStack.length = 0;
    redoStack.length = 0;
    isDirty = false;
    syncDirtyState();
    updateHistoryButtons();
    setTemplate(payload.template);
  } catch (error) {
    initialized = false;
    showStatus(error.message);
    return false;
  }
  return true;
}
window.addEventListener("pywebviewready", initializeApplication);
function waitForBridge() {
  initializeApplication().then(ready => {
    if (!ready && !initialized) initializationTimer = setTimeout(waitForBridge, 100);
  });
}
waitForBridge();
