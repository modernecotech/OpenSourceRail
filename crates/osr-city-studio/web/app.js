const api = {
  async request(path, options = {}) {
    const response = await fetch(path, {
      headers: { "content-type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `Request failed: ${response.status}`);
    return payload;
  },
  project: () => api.request("/api/project"),
  station: (id, body) => api.request(`/api/stations/${encodeURIComponent(id)}`, {
    method: "PUT", body: JSON.stringify(body),
  }),
  createStation: (line, body) => api.request(
    `/api/lines/${encodeURIComponent(line)}/stations`,
    { method: "POST", body: JSON.stringify(body) },
  ),
  deleteStation: (id) => api.request(`/api/stations/${encodeURIComponent(id)}`, {
    method: "DELETE",
  }),
  createLine: (body) => api.request("/api/lines", {
    method: "POST", body: JSON.stringify(body),
  }),
  line: (id, body) => api.request(`/api/lines/${encodeURIComponent(id)}`, {
    method: "PUT", body: JSON.stringify(body),
  }),
  deleteLine: (id) => api.request(`/api/lines/${encodeURIComponent(id)}`, {
    method: "DELETE",
  }),
  createControl: (line, body) => api.request(
    `/api/lines/${encodeURIComponent(line)}/control-points`,
    { method: "POST", body: JSON.stringify(body) },
  ),
  control: (id, body) => api.request(`/api/control-points/${encodeURIComponent(id)}`, {
    method: "PUT", body: JSON.stringify(body),
  }),
  service: (line, day, body) => api.request(
    `/api/services/${encodeURIComponent(line)}/${encodeURIComponent(day)}`,
    { method: "PUT", body: JSON.stringify(body) },
  ),
  bulkService: (body) => api.request("/api/services/bulk", {
    method: "PUT", body: JSON.stringify(body),
  }),
  coordination: (id, body) => api.request(`/api/coordination/${encodeURIComponent(id)}`, {
    method: "PUT", body: JSON.stringify(body),
  }),
  createCoordination: (body) => api.request("/api/coordination", {
    method: "POST", body: JSON.stringify(body),
  }),
  compile: () => api.request("/api/compile", { method: "POST" }),
  revision: () => api.request("/api/revisions", { method: "POST" }),
  revisions: () => api.request("/api/revisions"),
  compareRevision: (id) => api.request(
    `/api/revisions/${encodeURIComponent(id)}/compare`
  ),
  jobs: () => api.request("/api/jobs"),
  job: (id) => api.request(`/api/jobs/${encodeURIComponent(id)}`),
  jobArtifact: (id, index) => api.request(
    `/api/jobs/${encodeURIComponent(id)}/artifacts/${encodeURIComponent(index)}`
  ),
  startJob: (adapter, body) => api.request(`/api/jobs/${encodeURIComponent(adapter)}`, {
    method: "POST", body: JSON.stringify(body),
  }),
};

let view = null;
let selectedStation = null;
let selectedControl = null;
let selectedLine = null;
let projection = null;
let drag = null;
let mapMode = "select";
let pendingLineStart = null;
let revisions = null;
let comparison = null;
let jobView = { adapters: [], jobs: [] };
let jobPollTimer = null;
let selectedArtifactPreview = null;
let selectedCoordinationAssetIds = new Set();
let operationBusy = false;
const lineColours = ["#56d39b", "#5eb9e8", "#e88859", "#a98aef", "#e96d95"];

const $ = (selector) => document.querySelector(selector);

async function load() {
  try {
    [view, revisions, jobView] = await Promise.all([api.project(), api.revisions(), api.jobs()]);
    selectedStation = selectedStation
      ? view.snapshot.stations.find((item) => item.id === selectedStation.id) || null
      : null;
    selectedControl = selectedControl
      ? view.snapshot.line_control_points.find((item) => item.id === selectedControl.id) || null
      : null;
    selectedLine = selectedLine
      ? view.snapshot.lines.find((item) => item.id === selectedLine.id) || null
      : null;
    render();
    if (!selectedArtifactPreview) selectDefaultArtifact();
  } catch (error) {
    toast(error.message, true);
  }
}

function render() {
  renderGit();
  renderSummary();
  renderMap();
  renderStationInspector();
  renderServiceSelectors();
  renderServiceEditor();
  renderFindings();
  renderArtifacts();
  renderJobs();
  renderArtifactViewer();
  renderRevisionSelector();
  renderRevisionComparison();
}

function renderGit() {
  const git = view.git;
  const node = $("#git-status");
  const head = git.head ? git.head.slice(0, 9) : "no-head";
  node.textContent = `${git.branch || "detached"} @ ${head} · ${git.dirty ? "working changes" : "clean"}`;
  node.classList.toggle("dirty", git.dirty);
}

function renderSummary() {
  const s = view.snapshot.summary;
  const cards = [
    [s.route_km.toFixed(1), "route km"],
    [s.station_count, "station platforms"],
    [s.locked_station_count, "locked stations"],
    [s.manual_station_count, "manual stations"],
    [s.manual_line_count, "manual lines"],
    [s.moved_station_count, "moved stations"],
    [s.edited_line_count, "edited lines"],
    [s.peak_fleet, "maximum line fleet"],
    [Math.round(s.weekly_service_km).toLocaleString(), "weekly service km"],
  ];
  $("#summary").innerHTML = cards.map(([value, label]) =>
    `<div class="summary-card"><strong>${escapeHtml(value)}</strong><span>${label}</span></div>`
  ).join("");
}

function corridorLines() {
  return (view.corridor.features || []).filter(
    (feature) => feature.geometry?.type === "LineString"
  );
}

function makeProjection() {
  const coordinates = corridorLines().flatMap((feature) => feature.geometry.coordinates);
  view.snapshot.stations.forEach((station) => coordinates.push([station.lon, station.lat]));
  const xs = coordinates.map((point) => point[0]);
  const ys = coordinates.map((point) => point[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const pad = 55;
  const width = 1000 - 2 * pad;
  const height = 620 - 2 * pad;
  return {
    point(lon, lat) {
      return [
        pad + ((lon - minX) / (maxX - minX || 1)) * width,
        620 - pad - ((lat - minY) / (maxY - minY || 1)) * height,
      ];
    },
    inverse(x, y) {
      return [
        minX + ((x - pad) / width) * (maxX - minX),
        minY + (((620 - pad) - y) / height) * (maxY - minY),
      ];
    },
  };
}

function renderMap() {
  projection = makeProjection();
  const svg = $("#network-map");
  svg.innerHTML = "";
  corridorLines().forEach((feature, index) => {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    const points = feature.geometry.coordinates.map(([lon, lat]) => projection.point(lon, lat));
    path.setAttribute("d", points.map(([x, y], i) => `${i ? "L" : "M"} ${x.toFixed(2)} ${y.toFixed(2)}`).join(" "));
    const lineId = feature.properties?.name || `line-${index + 1}`;
    const line = view.snapshot.lines.find((item) => item.id === lineId);
    path.setAttribute(
      "class",
      `network-line ${line?.state === "manual" ? "manual" : ""} ${selectedLine?.id === lineId ? "selected" : ""}`
    );
    path.setAttribute("stroke", lineColours[index % lineColours.length]);
    path.dataset.line = lineId;
    path.addEventListener("click", handleLineClick);
    svg.appendChild(path);
  });

  const movedIds = new Set(view.snapshot.changes.map((change) => change.id));
  view.snapshot.stations.forEach((station) => {
    const [x, y] = projection.point(station.lon, station.lat);
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", x);
    circle.setAttribute("cy", y);
    circle.setAttribute("r", station.archetype.includes("interchange") ? 10 : 8);
    circle.setAttribute(
      "class",
      `station ${station.state} ${movedIds.has(station.id) ? "moved" : ""} ${selectedStation?.id === station.id ? "selected" : ""}`
    );
    circle.dataset.id = station.id;
    const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
    title.textContent = `${station.name} · ${station.line} · ${station.state}`;
    circle.appendChild(title);
    circle.addEventListener("pointerdown", startStationDrag);
    circle.addEventListener("click", (event) => {
      if (mapMode === "line") return;
      event.stopPropagation();
      selectStation(station.id);
    });
    svg.appendChild(circle);
  });
  view.snapshot.line_control_points.forEach((control) => {
    const [x, y] = projection.point(control.lon, control.lat);
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    circle.setAttribute("x", x - 7);
    circle.setAttribute("y", y - 7);
    circle.setAttribute("width", 14);
    circle.setAttribute("height", 14);
    circle.setAttribute("rx", 3);
    circle.setAttribute(
      "class",
      `control-point ${selectedControl?.id === control.id ? "selected" : ""}`
    );
    circle.dataset.id = control.id;
    circle.addEventListener("pointerdown", startControlDrag);
    circle.addEventListener("click", (event) => {
      if (mapMode === "line") return;
      event.stopPropagation();
      selectControl(control.id);
    });
    svg.appendChild(circle);
  });
  if (pendingLineStart) {
    const [x, y] = projection.point(pendingLineStart.lon, pendingLineStart.lat);
    const marker = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    marker.setAttribute("cx", x);
    marker.setAttribute("cy", y);
    marker.setAttribute("r", 9);
    marker.setAttribute("class", "pending-line-point");
    svg.appendChild(marker);
  }
}

function startStationDrag(event) {
  if (mapMode === "line") return;
  const id = event.currentTarget.dataset.id;
  selectStation(id);
  drag = { id, node: event.currentTarget, kind: "station" };
  event.currentTarget.setPointerCapture(event.pointerId);
}

function startControlDrag(event) {
  if (mapMode === "line") return;
  event.stopPropagation();
  const id = event.currentTarget.dataset.id;
  selectControl(id);
  drag = { id, node: event.currentTarget, kind: "control" };
  event.currentTarget.setPointerCapture(event.pointerId);
}

async function createObjectFromMap(event) {
  if (drag || mapMode === "select") return;
  const rect = $("#network-map").getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * 1000;
  const y = ((event.clientY - rect.top) / rect.height) * 620;
  const [lon, lat] = projection.inverse(x, y);
  try {
    const line = event.currentTarget.dataset.line;
    const result = mapMode === "station"
      ? await api.createStation(line, {
        name: `New ${line} station`,
        lat,
        lon,
        archetype: "standard",
        reason: "Designer-created in City Studio",
      })
      : await api.createControl(line, {
        source_lat: lat,
        source_lon: lon,
        reason: "Interactive alignment control point",
      });
    view = result.project;
    revisions = await api.revisions();
    comparison = null;
    if (mapMode === "station") {
      selectedStation = view.snapshot.stations.find((item) => item.id === result.id);
      selectedControl = null;
      selectedLine = null;
    } else {
      selectedStation = null;
      selectedControl = view.snapshot.line_control_points.find((item) => item.id === result.id);
      selectedLine = null;
    }
    render();
    toast(mapMode === "station"
      ? "Manual station created. Name it, adjust its archetype, or drag it before saving."
      : "Alignment control point created. Drag it, then save the line geometry intent.");
  } catch (error) {
    toast(error.message, true);
  }
}

function handleLineClick(event) {
  if (mapMode === "select") {
    event.stopPropagation();
    selectLine(event.currentTarget.dataset.line);
    return;
  }
  if (mapMode !== "line") createObjectFromMap(event);
}

document.querySelectorAll(".map-tool").forEach((button) => {
  button.addEventListener("click", () => {
    mapMode = button.dataset.mode;
    if (mapMode !== "line") pendingLineStart = null;
    document.querySelectorAll(".map-tool").forEach((item) => {
      item.classList.toggle("active", item.dataset.mode === mapMode);
    });
    $("#map-hint").textContent = mapMode === "station"
      ? "Click a line to insert a manual station into the route and simulator topology."
      : mapMode === "line"
        ? "Click two endpoints to create a line, terminal platforms, and weekly service plans."
      : mapMode === "control"
        ? "Click a line to add an alignment control point, then drag it."
        : "Select or drag an object to edit its intent.";
  });
});

$("#network-map").addEventListener("click", async (event) => {
  if (mapMode !== "line" || drag) return;
  const rect = event.currentTarget.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * 1000;
  const y = ((event.clientY - rect.top) / rect.height) * 620;
  const [lon, lat] = projection.inverse(x, y);
  if (!pendingLineStart) {
    pendingLineStart = { lat, lon };
    renderMap();
    toast("First line endpoint set. Click the second endpoint to generate the line.");
    return;
  }
  try {
    const result = await api.createLine({
      name: `New line ${view.snapshot.lines.length + 1}`,
      start_lat: pendingLineStart.lat,
      start_lon: pendingLineStart.lon,
      end_lat: lat,
      end_lon: lon,
      routing: $("#line-routing").value,
      reason: "Designer-created in City Studio",
    });
    pendingLineStart = null;
    view = result.project;
    revisions = await api.revisions();
    comparison = null;
    selectedLine = view.snapshot.lines.find((item) => item.id === result.id);
    selectedStation = null;
    selectedControl = null;
    render();
    toast(`${selectedLine.routing_method} line created with two terminals and service plans for every day type.`);
  } catch (error) {
    toast(error.message, true);
  }
});

$("#network-map").addEventListener("pointermove", (event) => {
  if (!drag) return;
  const rect = event.currentTarget.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * 1000;
  const y = ((event.clientY - rect.top) / rect.height) * 620;
  const [lon, lat] = projection.inverse(x, y);
  if (drag.kind === "station") {
    drag.node.setAttribute("cx", x);
    drag.node.setAttribute("cy", y);
    selectedStation.lat = lat;
    selectedStation.lon = lon;
    $("#station-lat").value = lat.toFixed(7);
    $("#station-lon").value = lon.toFixed(7);
    if (selectedStation.state !== "manual") {
      $("#station-state").value = "preferred";
      selectedStation.state = "preferred";
    }
    $("#station-change").textContent = "Unsaved map movement — save the station intent to persist it.";
  } else {
    drag.node.setAttribute("x", x - 7);
    drag.node.setAttribute("y", y - 7);
    selectedControl.lat = lat;
    selectedControl.lon = lon;
    $("#control-lat").value = lat.toFixed(7);
    $("#control-lon").value = lon.toFixed(7);
    $("#control-change").textContent = "Unsaved alignment movement — save to regenerate the corridor.";
  }
});

$("#network-map").addEventListener("pointerup", () => { drag = null; });
$("#network-map").addEventListener("pointercancel", () => { drag = null; });

function selectStation(id) {
  selectedStation = view.snapshot.stations.find((item) => item.id === id) || null;
  selectedControl = null;
  selectedLine = null;
  renderMap();
  renderStationInspector();
}

function selectControl(id) {
  selectedControl = view.snapshot.line_control_points.find((item) => item.id === id) || null;
  selectedStation = null;
  selectedLine = null;
  renderMap();
  renderStationInspector();
}

function selectLine(id) {
  selectedLine = view.snapshot.lines.find((item) => item.id === id) || null;
  selectedStation = null;
  selectedControl = null;
  renderMap();
  renderStationInspector();
}

function renderStationInspector() {
  const form = $("#station-form");
  const controlForm = $("#control-form");
  const lineForm = $("#line-form");
  if (selectedLine) {
    form.hidden = true;
    controlForm.hidden = true;
    lineForm.hidden = false;
    const isManual = selectedLine.state === "manual";
    $("#station-title").textContent = selectedLine.name || selectedLine.id;
    $("#line-id").value = selectedLine.id;
    $("#line-name").value = selectedLine.name || selectedLine.id;
    $("#line-name").readOnly = !isManual;
    $("#line-shape").value = selectedLine.shape;
    $("#line-length").value = (selectedLine.length_m / 1000).toFixed(3);
    $("#line-routing-method").value = selectedLine.routing_method || "generated-source";
    $("#line-routing-sources").value = (selectedLine.routing_source_ids || []).join("\n") || "None";
    $("#line-demand-weight").value = selectedLine.demand_weight ?? "Not applicable";
    $("#line-state").value = selectedLine.state;
    $("#line-reason").value = selectedLine.reason || "";
    $("#line-reason").readOnly = !isManual;
    $("#delete-line").hidden = !isManual;
    $("#save-line").hidden = !isManual;
    return;
  }
  lineForm.hidden = true;
  if (selectedControl) {
    form.hidden = true;
    controlForm.hidden = false;
    $("#station-title").textContent = `${selectedControl.line} alignment`;
    $("#control-id").value = selectedControl.id;
    $("#control-line").value = selectedControl.line;
    $("#control-lat").value = selectedControl.lat.toFixed(7);
    $("#control-lon").value = selectedControl.lon.toFixed(7);
    $("#control-state").value = selectedControl.state;
    $("#control-influence").value = selectedControl.influence_m;
    $("#control-reason").value = selectedControl.reason || "";
    $("#control-change").textContent = selectedControl.distance_m > 0.01
      ? `Moved ${selectedControl.distance_m.toFixed(1)} m from its source corridor.`
      : "At source corridor coordinates.";
    return;
  }
  controlForm.hidden = true;
  if (!selectedStation) {
    $("#station-title").textContent = "Select a station";
    form.hidden = true;
    return;
  }
  form.hidden = false;
  const isManual = selectedStation.state === "manual";
  $("#station-title").textContent = selectedStation.name;
  $("#station-id").value = selectedStation.id;
  $("#station-line").value = selectedStation.line;
  $("#station-name").value = selectedStation.name;
  $("#station-name").readOnly = !isManual;
  $("#station-archetype").value = selectedStation.archetype;
  $("#station-archetype").disabled = !isManual;
  $("#station-lat").value = selectedStation.lat.toFixed(7);
  $("#station-lon").value = selectedStation.lon.toFixed(7);
  $("#station-state").value = selectedStation.state;
  [...$("#station-state").options].forEach((option) => {
    option.disabled = isManual ? !["manual", "retired"].includes(option.value) : option.value === "manual";
  });
  $("#station-reason").value = selectedStation.reason || "";
  $("#delete-station").hidden = !isManual;
  const change = view.snapshot.changes.find((item) => item.id === selectedStation.id);
  $("#station-change").textContent = change
    ? `Moved ${change.distance_m.toFixed(1)} m from its source position.`
    : isManual ? "Manual station inserted at its source corridor position." : "At generated baseline coordinates.";
}

$("#station-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const isManual = selectedStation.state === "manual";
    const body = {
      state: $("#station-state").value,
      lat: Number($("#station-lat").value),
      lon: Number($("#station-lon").value),
      reason: $("#station-reason").value.trim(),
    };
    if (isManual) {
      body.name = $("#station-name").value.trim();
      body.archetype = $("#station-archetype").value;
    }
    view = await api.station(selectedStation.id, body);
    selectedStation = view.snapshot.stations.find((item) => item.id === selectedStation.id);
    revisions = await api.revisions();
    comparison = null;
    render();
    toast("Station intent saved. The project now has Git-visible working changes.");
  } catch (error) {
    toast(error.message, true);
  }
});

$("#delete-station").addEventListener("click", async () => {
  if (!selectedStation || selectedStation.state !== "manual") return;
  if (!window.confirm(`Retire ${selectedStation.name} from the candidate network?`)) return;
  try {
    view = await api.deleteStation(selectedStation.id);
    selectedStation = null;
    revisions = await api.revisions();
    comparison = null;
    render();
    toast("Manual station retired. The revision comparison will record its removal.");
  } catch (error) {
    toast(error.message, true);
  }
});

$("#control-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    view = await api.control(selectedControl.id, {
      state: $("#control-state").value,
      lat: Number($("#control-lat").value),
      lon: Number($("#control-lon").value),
      influence_m: Number($("#control-influence").value),
      reason: $("#control-reason").value.trim(),
    });
    selectedControl = view.snapshot.line_control_points.find(
      (item) => item.id === selectedControl.id
    );
    revisions = await api.revisions();
    comparison = null;
    render();
    toast("Line geometry regenerated; GIS, route length and simulator distances are updated.");
  } catch (error) {
    toast(error.message, true);
  }
});

$("#line-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selectedLine || selectedLine.state !== "manual") return;
  try {
    view = await api.line(selectedLine.id, {
      name: $("#line-name").value.trim(),
      state: "manual",
      reason: $("#line-reason").value.trim(),
    });
    selectedLine = view.snapshot.lines.find((item) => item.id === selectedLine.id);
    revisions = await api.revisions();
    comparison = null;
    render();
    toast("Manual line intent saved for Git review.");
  } catch (error) {
    toast(error.message, true);
  }
});

$("#delete-line").addEventListener("click", async () => {
  if (!selectedLine || selectedLine.state !== "manual") return;
  if (!window.confirm(`Retire ${selectedLine.name} and its manual terminals?`)) return;
  try {
    view = await api.deleteLine(selectedLine.id);
    selectedLine = null;
    revisions = await api.revisions();
    comparison = null;
    render();
    toast("Manual line, terminals, controls, and service plans retired together.");
  } catch (error) {
    toast(error.message, true);
  }
});

function renderServiceSelectors() {
  const lineNode = $("#service-line");
  const dayNode = $("#service-day");
  const oldLine = lineNode.value || view.snapshot.lines[0]?.id;
  const oldDay = dayNode.value || view.service_plan.day_types[0]?.id;
  lineNode.innerHTML = view.snapshot.lines.map((line) =>
    `<option value="${escapeHtml(line.id)}">${escapeHtml(line.id)}</option>`
  ).join("");
  dayNode.innerHTML = view.service_plan.day_types.map((day) =>
    `<option value="${escapeHtml(day.id)}">${escapeHtml(day.name)}</option>`
  ).join("");
  if ([...lineNode.options].some((option) => option.value === oldLine)) lineNode.value = oldLine;
  if ([...dayNode.options].some((option) => option.value === oldDay)) dayNode.value = oldDay;
  renderCopyServiceDays();
}

function renderCopyServiceDays() {
  const target = $("#copy-service-day");
  if (!target) return;
  const selected = target.value;
  const current = $("#service-day").value;
  target.innerHTML = view.service_plan.day_types
    .filter((day) => day.id !== current)
    .map((day) => `<option value="${escapeHtml(day.id)}">${escapeHtml(day.name)}</option>`)
    .join("");
  if ([...target.options].some((option) => option.value === selected)) target.value = selected;
}

function currentServicePlan() {
  return view.service_plan.line_plans.find(
    (plan) => plan.line === $("#service-line").value && plan.day_type === $("#service-day").value
  );
}

function renderServiceEditor() {
  const plan = currentServicePlan();
  if (!plan) return;
  $("#service-start").value = plan.service_start;
  $("#service-end").value = plan.service_end === "24:00" ? "23:59" : plan.service_end;
  $("#service-windows").innerHTML = plan.windows.map((window) => windowRow(window)).join("");
  const metric = view.snapshot.service_metrics.find(
    (item) => item.line === plan.line && item.day_type === plan.day_type
  );
  $("#service-metric").innerHTML = metric
    ? `<strong>${metric.peak_fleet} trainsets</strong> peak fleet · <strong>${metric.peak_capacity_pphpd.toLocaleString()}</strong> passengers/hour/direction · <strong>${Math.round(metric.daily_service_km).toLocaleString()} km</strong> per service day · ${metric.cycle_time_min.toFixed(1)} min cycle`
    : "";
  bindWindowButtons();
}

function windowRow(window = { from: "09:00", to: "10:00", headway_min: 12 }) {
  const capacity = Math.floor(360 * 60 / Number(window.headway_min || 1));
  return `<tr>
    <td><input class="window-from" type="time" value="${window.from}"></td>
    <td><input class="window-to" type="time" value="${window.to === "24:00" ? "23:59" : window.to}"></td>
    <td><input class="window-headway" type="number" min="1" max="120" value="${window.headway_min}"> min</td>
    <td class="capacity">${capacity.toLocaleString()} pphpd</td>
    <td><button type="button" class="remove-window secondary" title="Remove">×</button></td>
  </tr>`;
}

function bindWindowButtons() {
  document.querySelectorAll(".remove-window").forEach((button) => {
    button.addEventListener("click", () => button.closest("tr").remove());
  });
  document.querySelectorAll(".window-headway").forEach((input) => {
    input.addEventListener("input", () => {
      const capacity = Math.floor(360 * 60 / Number(input.value || 1));
      input.closest("tr").querySelector(".capacity").textContent = `${capacity.toLocaleString()} pphpd`;
    });
  });
}

$("#service-line").addEventListener("change", renderServiceEditor);
$("#service-day").addEventListener("change", () => {
  renderCopyServiceDays();
  renderServiceEditor();
});
$("#add-window").addEventListener("click", () => {
  $("#service-windows").insertAdjacentHTML("beforeend", windowRow());
  bindWindowButtons();
});

function servicePlanFromEditor(dayType = $("#service-day").value) {
  return {
    line: $("#service-line").value,
    day_type: dayType,
    service_start: $("#service-start").value,
    service_end: $("#service-end").value,
    windows: [...document.querySelectorAll("#service-windows tr")].map((row) => ({
      from: row.querySelector(".window-from").value,
      to: row.querySelector(".window-to").value,
      headway_min: Number(row.querySelector(".window-headway").value),
    })),
  };
}

$("#apply-headway").addEventListener("click", async () => {
  const factor = Number($("#headway-factor").value);
  if ($("#headway-scope").value === "all") {
    try {
      const result = await api.bulkService({
        day_type: $("#service-day").value,
        line_ids: [],
        percent: Math.round(factor * 100),
      });
      view = result.project;
      revisions = await api.revisions();
      comparison = null;
      render();
      toast(`${result.updated_line_plans} route plans adjusted atomically for ${$("#service-day").value}.`);
    } catch (error) {
      toast(error.message, true);
    }
    return;
  }
  document.querySelectorAll("#service-windows .window-headway").forEach((input) => {
    input.value = Math.max(1, Math.min(120, Math.round(Number(input.value) * factor)));
    input.dispatchEvent(new Event("input", { bubbles: true }));
  });
  $("#service-form").requestSubmit();
});

$("#copy-service-plan").addEventListener("click", async () => {
  const targetDay = $("#copy-service-day").value;
  if (!targetDay) return;
  const plan = servicePlanFromEditor(targetDay);
  try {
    view = await api.service(plan.line, targetDay, plan);
    revisions = await api.revisions();
    comparison = null;
    render();
    toast(`${plan.line} service copied to ${targetDay}; fleet and capacity metrics regenerated.`);
  } catch (error) {
    toast(error.message, true);
  }
});

$("#service-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const line = $("#service-line").value;
  const day = $("#service-day").value;
  try {
    view = await api.service(line, day, servicePlanFromEditor(day));
    revisions = await api.revisions();
    comparison = null;
    render();
    toast("Service plan saved and deterministic fleet/capacity metrics regenerated.");
  } catch (error) {
    toast(error.message, true);
  }
});

function renderFindings() {
  const findings = view.snapshot.findings;
  $("#findings").innerHTML = findings.length
    ? findings.map((finding) =>
      `<div class="finding ${finding.severity}"><strong>${escapeHtml(finding.code)}</strong><small>${escapeHtml(finding.message)}${finding.object_id ? ` · ${escapeHtml(finding.object_id)}` : ""}</small></div>`
    ).join("")
    : '<div class="finding info"><strong>Validation passing</strong><small>Source locks, intent and service plans are consistent.</small></div>';
}

function renderArtifacts() {
  $("#artifacts").innerHTML = view.artifacts.map((artifact) =>
    `<div class="artifact ${artifact.exists ? "" : "missing"}"><strong>${escapeHtml(artifact.category)} · ${escapeHtml(artifact.label)}</strong><small>${escapeHtml(artifact.path)} · ${artifact.exists ? "available" : "not generated"}</small></div>`
  ).join("");
}

function renderJobs() {
  $("#job-adapters").innerHTML = jobView.adapters.map((adapter) =>
    `<div class="job-adapter"><div><strong>${escapeHtml(adapter.category)} · ${escapeHtml(adapter.label)}</strong><small>${escapeHtml(adapter.description)}</small></div><button type="button" data-job-adapter="${escapeHtml(adapter.id)}" ${operationBusy ? "disabled" : ""}>Run</button></div>`
  ).join("");
  document.querySelectorAll("[data-job-adapter]").forEach((button) => {
    button.addEventListener("click", () => startEngineeringJob(button.dataset.jobAdapter));
  });
  $("#jobs").innerHTML = jobView.jobs.slice(0, 4).map((job) => {
    const artifacts = job.artifacts.length
      ? `<div class="job-artifacts">${job.artifacts.map((artifact, index) => {
        const key = `${job.id}:${index}`;
        const active = selectedArtifactPreview
          && `${selectedArtifactPreview.job_id}:${selectedArtifactPreview.artifact_index}` === key;
        return `<button type="button" class="job-artifact-button ${active ? "active" : ""}" data-job-id="${escapeHtml(job.id)}" data-artifact-index="${index}" title="${escapeHtml(artifact.path)}">${escapeHtml(artifact.kind)} · ${escapeHtml(artifact.sha256.slice(0, 12))}</button>`;
      }).join("")}</div>`
      : "";
    const log = job.log_tail
      ? `<details class="job-log"><summary>Captured log</summary><pre>${escapeHtml(job.log_tail)}</pre></details>`
      : "";
    return `<div class="job-card ${escapeHtml(job.status)}"><div class="job-title"><strong>${escapeHtml(job.label)}</strong><span class="job-status">${escapeHtml(job.status)}</span></div><small>${escapeHtml(job.phase)} · ${job.progress_percent}% · ${escapeHtml(job.revision_id)}</small><div class="job-progress"><i style="width:${job.progress_percent}%"></i></div><small class="job-command">${escapeHtml(job.command.join(" "))}</small>${job.error ? `<small class="error">${escapeHtml(job.error)}</small>` : ""}${artifacts}${log}</div>`;
  }).join("") || '<div class="artifact missing"><strong>No engineering jobs yet</strong><small>Run an allowlisted adapter above; arbitrary shell commands are never accepted.</small></div>';
  document.querySelectorAll("[data-artifact-index]").forEach((button) => {
    button.addEventListener("click", () => openJobArtifact(
      button.dataset.jobId,
      Number(button.dataset.artifactIndex),
      true,
    ));
  });
  scheduleJobPoll();
}

async function selectDefaultArtifact() {
  const preferredKinds = [
    "civil-bim-index", "civil-ids-report", "civil-bcf3-index",
    "civil-bim-validation", "civil-4d-sequence",
    "gis-network", "alignment-input", "alignment-review", "simulation-result",
    "landxml", "railml", "stakeout", "manifest", "snapshot", "job-log",
  ];
  for (const job of jobView.jobs) {
    for (const kind of preferredKinds) {
      const index = job.artifacts.findIndex((artifact) => artifact.kind === kind);
      if (index >= 0) {
        await openJobArtifact(job.id, index, false);
        return;
      }
    }
  }
}

async function openJobArtifact(jobId, index, shouldScroll) {
  try {
    const nextPreview = await api.jobArtifact(jobId, index);
    const changed = !selectedArtifactPreview
      || selectedArtifactPreview.job_id !== nextPreview.job_id
      || selectedArtifactPreview.artifact_index !== nextPreview.artifact_index;
    selectedArtifactPreview = nextPreview;
    if (changed) selectedCoordinationAssetIds.clear();
    renderJobs();
    renderArtifactViewer();
    if (shouldScroll) {
      $("#artifact-viewer").scrollIntoView({ behavior: "smooth", block: "start" });
    }
  } catch (error) {
    toast(error.message, true);
  }
}

function renderArtifactViewer() {
  const preview = selectedArtifactPreview;
  const canvas = $("#artifact-canvas");
  canvas.replaceChildren();
  if (!preview) {
    $("#artifact-viewer-title").textContent = "Select a generated artifact";
    $("#artifact-verification").textContent = "Awaiting verified artifact";
    $("#artifact-verification").classList.remove("verified");
    $("#artifact-viewer-empty").hidden = false;
    $("#artifact-metrics").replaceChildren();
    $("#artifact-objects").replaceChildren();
    $("#artifact-objects").hidden = true;
    $("#artifact-provenance").textContent = "";
    $("#artifact-source").hidden = true;
    return;
  }
  $("#artifact-viewer-title").textContent = `${preview.artifact.kind} · ${preview.format}`;
  $("#artifact-verification").textContent = preview.sha256_verified ? "SHA-256 verified" : "Unverified";
  $("#artifact-verification").classList.toggle("verified", preview.sha256_verified);
  const graphic = artifactGraphic(preview);
  $("#artifact-viewer-empty").hidden = graphic.length > 0;
  if (graphic.length) drawArtifactGraphic(canvas, graphic);
  const metrics = artifactMetrics(preview, graphic);
  $("#artifact-metrics").innerHTML = metrics.map(([value, label]) =>
    `<div class="artifact-metric"><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></div>`
  ).join("");
  renderArtifactObjects(preview);
  $("#artifact-provenance").textContent = `${preview.artifact.path}\n${preview.artifact.size_bytes.toLocaleString()} bytes\nsha256:${preview.artifact.sha256}\njob:${preview.job_id}`;
  const source = typeof preview.content === "string"
    ? preview.content
    : JSON.stringify(preview.content, null, 2);
  const maximum = 60_000;
  $("#artifact-source-text").textContent = source.length > maximum
    ? `${source.slice(0, maximum)}\n\n… browser source preview limited to ${maximum.toLocaleString()} characters`
    : source;
  $("#artifact-source").hidden = false;
}

function artifactGraphic(preview) {
  const content = preview.content;
  if (preview.format === "geojson" && Array.isArray(content.features)) {
    return content.features
      .filter((feature) => feature.geometry?.type === "LineString")
      .map((feature) => feature.geometry.coordinates.map(([x, y]) => [Number(x), Number(y)]));
  }
  if (preview.format === "json" && Array.isArray(content.points)) {
    return [content.points.map((point) => [Number(point[0]), Number(point[1])])];
  }
  if (preview.format === "json" && Array.isArray(content.alignment?.horizontal)) {
    const points = content.alignment.horizontal.map((element) => {
      const geometry = Object.values(element)[0];
      return geometry?.start_xy
        ? [Number(geometry.start_xy[0]), Number(geometry.start_xy[1])]
        : null;
    }).filter(Boolean);
    return points.length ? [points] : [];
  }
  if (preview.format === "json" && content.schema === "org.opensourcerail.bonsai-civil-ifc.v1") {
    const iso = ([x, y, z]) => [Number(x) - Number(y) * .7, Number(x) * .24 + Number(y) * .38 - Number(z) * 2.4];
    return (content.objects || []).map((item) => {
      const box = item.bbox_m;
      if (!Array.isArray(box) || box.length !== 6) return [];
      const corners = [
        [box[0], box[1], box[2]], [box[3], box[1], box[2]],
        [box[3], box[4], box[2]], [box[0], box[4], box[2]],
        [box[0], box[1], box[5]], [box[3], box[1], box[5]],
        [box[3], box[4], box[5]], [box[0], box[4], box[5]],
      ].map(iso);
      return [0, 1, 2, 3, 0, 4, 5, 1, 5, 6, 2, 6, 7, 3, 7, 4].map((index) => corners[index]);
    }).filter((points) => points.length);
  }
  if (preview.format === "landxml") {
    const xml = new DOMParser().parseFromString(content, "application/xml");
    const points = Array.from(xml.getElementsByTagNameNS("*", "Start")).map((node) =>
      node.textContent.trim().split(/\s+/).slice(0, 2).map(Number)
    ).filter((point) => point.every(Number.isFinite));
    const ends = Array.from(xml.getElementsByTagNameNS("*", "End"));
    if (ends.length) {
      const last = ends.at(-1).textContent.trim().split(/\s+/).slice(0, 2).map(Number);
      if (last.every(Number.isFinite)) points.push(last);
    }
    return points.length ? [points] : [];
  }
  if (preview.format === "csv") {
    const rows = content.trim().split(/\r?\n/).slice(1).map((row) => row.split(","));
    const points = rows.map((row) => [Number(row[1]), Number(row[2])])
      .filter((point) => point.every(Number.isFinite));
    return points.length ? [points] : [];
  }
  return [];
}

function drawArtifactGraphic(svg, groups) {
  const points = groups.flat();
  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const spanX = Math.max(maxX - minX, 1e-9);
  const spanY = Math.max(maxY - minY, 1e-9);
  const scale = Math.min(820 / spanX, 340 / spanY);
  const project = ([x, y]) => [40 + (x - minX) * scale, 380 - (y - minY) * scale];
  const civilObjects = selectedArtifactPreview?.content?.schema === "org.opensourcerail.bonsai-civil-ifc.v1";
  groups.forEach((group, groupIndex) => {
    if (group.length < 2) return;
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("class", "artifact-preview-line");
    if (civilObjects) {
      path.classList.add("inspectable");
      path.dataset.objectIndex = groupIndex;
      path.addEventListener("click", () => selectArtifactObject(groupIndex));
    }
    path.setAttribute("d", group.map((point, index) => {
      const [x, y] = project(point);
      return `${index ? "L" : "M"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    }).join(" "));
    svg.append(path);
    [group[0], group.at(-1)].forEach((point) => {
      const [x, y] = project(point);
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("class", "artifact-preview-point");
      circle.setAttribute("cx", x.toFixed(2));
      circle.setAttribute("cy", y.toFixed(2));
      circle.setAttribute("r", "5");
      svg.append(circle);
    });
  });
}

function artifactInspectorItems(preview) {
  const content = preview.content;
  if (preview.format === "json" && content.schema === "org.opensourcerail.bonsai-civil-ifc.v1") {
    return (content.objects || []).map((item) => ({
      label: item.name,
      meta: `${item.ifc_class} · ${item.asset_class}`,
      detail: [
        `asset ${item.asset_id}`,
        `IFC GUID ${item.ifc_guid}`,
        `discipline ${item.discipline} · ${item.detail_mode}`,
        `bbox m ${item.bbox_m.join(", ")}`,
        `source ${item.source_geometry}`,
      ].join("\n"),
      coordinationTarget: item,
    }));
  }
  if (preview.format === "json" && content.schema === "org.opensourcerail.bonsai-civil-bcf-index.v1") {
    return (content.topics || []).map((topic) => ({
      label: topic.title,
      meta: `${topic.status} · ${topic.ifc_guids.length} IFC selection${topic.ifc_guids.length === 1 ? "" : "s"}`,
      detail: `${topic.description}\n\ntopic ${topic.topic_guid}\nassets ${topic.asset_ids.join(", ") || "alignment reference"}`,
      coordination: topic.issue_id ? topic : null,
    }));
  }
  if (preview.format === "json" && content.schema === "org.opensourcerail.bonsai-civil-ids-report.v1") {
    return (content.specifications || []).map((specification) => ({
      label: specification.name,
      meta: `${specification.status ? "PASS" : "FAIL"} · ${specification.total_checks_pass}/${specification.total_checks} checks`,
      detail: `${specification.description || "Information delivery requirement"}\n\n${specification.applicability.join("\n")}`,
    }));
  }
  return [];
}

function renderArtifactObjects(preview) {
  const host = $("#artifact-objects");
  const items = artifactInspectorItems(preview);
  const hasCoordinationTargets = items.some((item) => item.coordinationTarget);
  host.replaceChildren();
  host.hidden = !items.length;
  if (!items.length) return;
  const tools = hasCoordinationTargets ? `<div class="artifact-object-tools">
      <input id="artifact-object-filter" type="search" placeholder="Filter IFC assets" aria-label="Filter IFC assets">
      <button id="select-visible-assets" type="button" class="secondary">Select visible</button>
      <button id="clear-selected-assets" type="button" class="secondary">Clear</button>
      <span id="artifact-selection-count" class="artifact-selection-count">0 assets selected</span>
    </div>` : "";
  host.innerHTML = `<h3>${preview.content.schema?.includes("bcf") ? "Coordination topics" : preview.content.schema?.includes("ids") ? "IDS specifications" : "IFC object inspector"}</h3>
    ${tools}
    <div class="artifact-object-list">${items.map((item, index) => `<div class="artifact-object-row" data-object-row="${index}" data-search="${escapeHtml(`${item.label} ${item.meta}`.toLowerCase())}">${item.coordinationTarget ? `<input class="artifact-object-check" type="checkbox" data-asset-index="${index}" aria-label="Include ${escapeHtml(item.label)} in coordination topic">` : ""}<button type="button" class="artifact-object-button" data-object-index="${index}"><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.meta)}</small></button></div>`).join("")}</div>
    <pre class="artifact-object-detail"></pre>
    <form id="coordination-review-form" class="coordination-review-form" hidden>
      <p>Working-draft decision</p>
      <label>Status<select name="status"><option value="open">Open</option><option value="in-progress">In progress</option><option value="resolved">Resolved</option><option value="closed">Closed</option></select></label>
      <label>Assignee<input name="assignee" maxlength="120" placeholder="Discipline or responsible person"></label>
      <label>Resolution<textarea name="resolution" maxlength="2000" placeholder="Required before resolving or closing"></textarea></label>
      <label>Reviewed by<input name="reviewed_by" maxlength="120" placeholder="Required before resolving or closing"></label>
      <button type="submit">Save Git-reviewable decision</button>
      <small>The selected job artifact remains immutable. Rerun the civil BIM job to issue a BCF reflecting this decision.</small>
    </form>
    <form id="coordination-create-form" class="coordination-review-form" hidden>
      <p>New issue for selected IFC assets</p>
      <label>Title<input name="title" minlength="4" maxlength="160" required placeholder="Describe the coordination decision needed"></label>
      <label>Description<textarea name="description" minlength="12" maxlength="2000" required placeholder="State the conflict, required evidence, and acceptance boundary"></textarea></label>
      <label>Assignee<input name="assignee" maxlength="120" placeholder="Discipline or responsible person"></label>
      <button type="submit">Create Git-reviewable BCF topic</button>
      <small>A deterministic topic ID is derived from this content and the selected stable asset IDs. Rerun the civil BIM job to generate it.</small>
    </form>`;
  host.querySelectorAll(".artifact-object-button").forEach((button) => {
    button.addEventListener("click", () => selectArtifactObject(Number(button.dataset.objectIndex)));
  });
  host.querySelectorAll("[data-asset-index]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const target = items[Number(checkbox.dataset.assetIndex)]?.coordinationTarget;
      if (!target) return;
      if (checkbox.checked) selectedCoordinationAssetIds.add(target.asset_id);
      else selectedCoordinationAssetIds.delete(target.asset_id);
      updateArtifactAssetSelection(items);
    });
  });
  host.querySelector("#artifact-object-filter")?.addEventListener("input", (event) => {
    const query = event.currentTarget.value.trim().toLowerCase();
    host.querySelectorAll("[data-object-row]").forEach((row) => {
      row.hidden = query && !row.dataset.search.includes(query);
    });
  });
  host.querySelector("#select-visible-assets")?.addEventListener("click", () => {
    host.querySelectorAll("[data-object-row]:not([hidden]) [data-asset-index]").forEach((checkbox) => {
      const target = items[Number(checkbox.dataset.assetIndex)]?.coordinationTarget;
      if (target) selectedCoordinationAssetIds.add(target.asset_id);
    });
    updateArtifactAssetSelection(items);
  });
  host.querySelector("#clear-selected-assets")?.addEventListener("click", () => {
    selectedCoordinationAssetIds.clear();
    updateArtifactAssetSelection(items);
  });
  host.querySelector("#coordination-review-form")?.addEventListener("submit", saveCoordinationDecision);
  host.querySelector("#coordination-create-form")?.addEventListener("submit", createCoordinationIssue);
  selectArtifactObject(0);
}

function updateArtifactAssetSelection(items = artifactInspectorItems(selectedArtifactPreview)) {
  document.querySelectorAll("[data-asset-index]").forEach((checkbox) => {
    const target = items[Number(checkbox.dataset.assetIndex)]?.coordinationTarget;
    checkbox.checked = Boolean(target && selectedCoordinationAssetIds.has(target.asset_id));
    checkbox.closest(".artifact-object-row")?.classList.toggle("included", checkbox.checked);
  });
  const count = $("#artifact-selection-count");
  if (count) count.textContent = `${selectedCoordinationAssetIds.size} asset${selectedCoordinationAssetIds.size === 1 ? "" : "s"} selected`;
}

function selectArtifactObject(index) {
  const items = artifactInspectorItems(selectedArtifactPreview);
  if (!items[index]) return;
  document.querySelectorAll(".artifact-object-button").forEach((button) => {
    button.classList.toggle("selected", Number(button.dataset.objectIndex) === index);
  });
  document.querySelectorAll("#artifact-canvas .artifact-preview-line[data-object-index]").forEach((path) => {
    path.classList.toggle("selected", Number(path.dataset.objectIndex) === index);
  });
  const detail = $("#artifact-objects .artifact-object-detail");
  if (detail) detail.textContent = items[index].detail;
  const form = $("#coordination-review-form");
  const createForm = $("#coordination-create-form");
  if (createForm) {
    createForm.hidden = !items[index].coordinationTarget;
    createForm.dataset.objectIndex = index;
    if (items[index].coordinationTarget && selectedCoordinationAssetIds.size === 0) {
      selectedCoordinationAssetIds.add(items[index].coordinationTarget.asset_id);
    }
    updateArtifactAssetSelection(items);
  }
  if (!form) return;
  const topic = items[index].coordination;
  form.hidden = !topic;
  form.dataset.objectIndex = index;
  if (!topic) return;
  const draft = view.snapshot.coordination?.issues?.find((issue) => issue.id === topic.issue_id) || topic;
  form.elements.status.value = draft.status || topic.intent_status || "open";
  form.elements.assignee.value = draft.assignee || "";
  form.elements.resolution.value = draft.resolution || "";
  form.elements.reviewed_by.value = draft.reviewed_by || "";
}

async function createCoordinationIssue(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const index = Number(form.dataset.objectIndex);
  const items = artifactInspectorItems(selectedArtifactPreview);
  const target = items[index]?.coordinationTarget;
  if (!target) return;
  const assetIds = items
    .map((item) => item.coordinationTarget?.asset_id)
    .filter((assetId) => assetId && selectedCoordinationAssetIds.has(assetId));
  if (!assetIds.length) assetIds.push(target.asset_id);
  try {
    const result = await api.createCoordination({
      title: form.elements.title.value.trim(),
      description: form.elements.description.value.trim(),
      assignee: form.elements.assignee.value.trim(),
      asset_ids: assetIds,
    });
    view = result.project;
    form.reset();
    renderGit();
    renderSummary();
    renderFindings();
    renderRevisionSelector();
    toast(`${result.id} created for ${assetIds.length} IFC asset${assetIds.length === 1 ? "" : "s"}. Rerun civil BIM to emit the topic.`);
  } catch (error) {
    toast(error.message, true);
  }
}

async function saveCoordinationDecision(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const index = Number(form.dataset.objectIndex);
  const item = artifactInspectorItems(selectedArtifactPreview)[index];
  const topic = item?.coordination;
  if (!topic) return;
  const body = {
    status: form.elements.status.value,
    assignee: form.elements.assignee.value.trim(),
    resolution: form.elements.resolution.value.trim(),
    reviewed_by: form.elements.reviewed_by.value.trim(),
  };
  try {
    view = await api.coordination(topic.issue_id, body);
    renderGit();
    renderSummary();
    renderFindings();
    renderRevisionSelector();
    selectArtifactObject(index);
    toast(`${topic.issue_id} saved to project intent. Rerun civil BIM before BCF issue.`);
  } catch (error) {
    toast(error.message, true);
  }
}

function artifactMetrics(preview, graphic) {
  const content = preview.content;
  if (preview.format === "geojson") {
    const features = content.features || [];
    return [[features.length, "features"], [graphic.length, "line strings"], [features.filter((item) => item.geometry?.type === "Point").length, "points"], ["GeoJSON", "exchange format"]];
  }
  if (preview.format === "json" && Array.isArray(content.points)) {
    return [[content.line_slug || "alignment", "line"], [content.points.length, "survey points"], [`${content.design_speed_kmh || "—"} km/h`, "design speed"], ["local XYZ", "coordinate frame"]];
  }
  if (preview.format === "json" && content.alignment) {
    return [[content.alignment.line_slug || "alignment", "line"], [content.alignment.horizontal?.length || 0, "horizontal elements"], [content.alignment.vertical?.length || 0, "vertical elements"], [`${content.alignment.design_speed_kmh || "—"} km/h`, "design speed"]];
  }
  if (preview.format === "json" && content.sim_duration_s !== undefined) {
    return [[content.scenario_name || "scenario", "scenario"], [`${content.sim_duration_s}s`, "duration"], [Number(content.total_train_km || 0).toFixed(1), "train km"], [content.invariant_violations?.length || 0, "invariant violations"]];
  }
  if (preview.format === "json" && content.schema === "org.opensourcerail.bonsai-civil-ifc.v1") {
    return [[content.summary?.assets || 0, "IFC assets"], [content.summary?.construction_tasks || 0, "4D tasks"], [content.summary?.interface_checks || 0, "interface checks"], [content.ifc_schema || "IFC4X3", "coordination schema"]];
  }
  if (preview.format === "json" && content.schema === "org.opensourcerail.bonsai-civil-ids-report.v1") {
    return [[content.total_specifications_pass, `of ${content.total_specifications} IDS specifications`], [content.total_checks_pass, `of ${content.total_checks} checks`], [content.status ? "PASS" : "FAIL", "information delivery"], ["IDS 1.0", "requirements standard"]];
  }
  if (preview.format === "json" && content.schema === "org.opensourcerail.bonsai-civil-bcf-index.v1") {
    return [[content.open_topic_count ?? content.topic_count, "open / active topics"], [content.topics.reduce((sum, topic) => sum + topic.ifc_guids.length, 0), "IFC selections"], [content.bcf_version, "BCF version"], [content.topic_count, "retained topic records"]];
  }
  if (preview.format === "ifc") {
    const classes = [...content.matchAll(/=IFC[A-Z0-9]+\(/g)].length;
    return [[classes, "STEP entities"], [(content.match(/IFCTASK\(/g) || []).length, "4D tasks"], [(content.match(/IFCRAILWAYPART\(/g) || []).length, "railway parts"], ["IFC4.3", "coordination schema"]];
  }
  if (["landxml", "railml"].includes(preview.format)) {
    const xml = new DOMParser().parseFromString(content, "application/xml");
    const count = (name) => xml.getElementsByTagNameNS("*", name).length;
    return [[preview.format === "landxml" ? "LandXML 1.2" : "railML 3.2", "exchange format"], [count("Alignment") || count("track"), "alignments / tracks"], [count("Line") || count("radiusChange"), "geometry elements"], [count("speedChange"), "speed changes"]];
  }
  if (preview.format === "csv") {
    return [[content.trim().split(/\r?\n/).length - 1, "stakeout rows"], [graphic.flat().length, "plotted points"], ["CSV", "exchange format"], ["local XYZ", "coordinate frame"]];
  }
  if (preview.format === "ids") {
    const xml = new DOMParser().parseFromString(content, "application/xml");
    return [[xml.getElementsByTagNameNS("*", "specification").length, "IDS specifications"], [xml.getElementsByTagNameNS("*", "property").length, "property requirements"], ["IDS 1.0", "requirements standard"], ["XML", "exchange format"]];
  }
  if (preview.format === "bcf") {
    return [[content.container, "coordination container"], [content.size_bytes.toLocaleString(), "bytes"], ["3", "indexed topics"], ["verified", "content state"]];
  }
  if (preview.format === "json") {
    return [[Object.keys(content).length, "top-level fields"], ["JSON", "structured format"], [preview.artifact.size_bytes.toLocaleString(), "bytes"], ["verified", "content state"]];
  }
  return [[content.split(/\r?\n/).length, "lines"], [preview.format, "format"], [preview.artifact.size_bytes.toLocaleString(), "bytes"], ["verified", "content state"]];
}

async function startEngineeringJob(adapter) {
  const body = {};
  if (adapter === "simulation") body.day_type = $("#service-day").value;
  if (["alignment-exchange", "civil-bim"].includes(adapter)) body.line = $("#service-line").value;
  try {
    const job = await api.startJob(adapter, body);
    jobView.jobs.unshift(job);
    renderJobs();
    toast(`${job.label} queued with captured logs and artifact hashing.`);
  } catch (error) {
    toast(error.message, true);
  }
}

function scheduleJobPoll() {
  window.clearTimeout(jobPollTimer);
  if (!jobView.jobs.some((job) => ["queued", "running"].includes(job.status))) return;
  jobPollTimer = window.setTimeout(async () => {
    try {
      jobView = await api.jobs();
      renderJobs();
      renderArtifacts();
    } catch (error) {
      toast(error.message, true);
    }
  }, 800);
}

function renderRevisionSelector() {
  const selector = $("#revision-base");
  const selected = selector.value;
  const items = revisions?.revisions || [];
  selector.innerHTML = items.map((revision) =>
    `<option value="${escapeHtml(revision.revision_id)}">${escapeHtml(revision.revision_id)}${revision.is_current ? " · current" : ""}</option>`
  ).join("");
  if (items.some((revision) => revision.revision_id === selected)) selector.value = selected;
  selector.disabled = items.length === 0;
  $("#compare-revision").disabled = items.length === 0;
}

function signed(value, digits = 0) {
  const rounded = Number(value).toFixed(digits);
  return Number(value) > 0 ? `+${rounded}` : rounded;
}

function renderRevisionComparison() {
  const node = $("#revision-comparison");
  if (!comparison) {
    node.innerHTML = revisions?.revisions?.length
      ? `Choose a materialized revision and compare it with candidate <strong>${escapeHtml(revisions.candidate_revision_id)}</strong>.`
      : "Materialize a revision to establish a review baseline.";
    return;
  }
  const diff = comparison;
  const summary = [
    [signed(diff.summary.route_km, 3), "route km"],
    [signed(diff.summary.station_count), "stations"],
    [signed(diff.summary.manual_station_count), "manual stations"],
    [signed(diff.summary.manual_line_count), "manual lines"],
    [signed(diff.summary.peak_fleet), "peak fleet"],
    [signed(diff.summary.weekly_service_km, 1), "weekly service km"],
  ];
  const stationItems = diff.stations.map((item) => {
    const station = item.after || item.before;
    const movement = item.movement_m ? ` · ${item.movement_m.toFixed(1)} m` : "";
    return `<div class="revision-item"><strong>${escapeHtml(item.kind)} · ${escapeHtml(station.name)}</strong><small>${escapeHtml(item.id)} · ${escapeHtml(station.line)}${movement}</small></div>`;
  }).join("") || '<p class="empty-diff">No station changes</p>';
  const controlItems = diff.controls.map((item) => {
    const control = item.after || item.before;
    const movement = item.movement_m ? ` · ${item.movement_m.toFixed(1)} m` : "";
    return `<div class="revision-item"><strong>${escapeHtml(item.kind)} control · ${escapeHtml(control.line)}</strong><small>${escapeHtml(item.id)}${movement}</small></div>`;
  }).join("");
  const lineItems = controlItems + diff.lines.map((item) => {
    const line = item.after || item.before;
    const kind = item.before && item.after ? "modified" : item.after ? "added" : "removed";
    const routing = line.routing_method || (line.state === "manual" ? "direct" : "generated-source");
    const sources = line.routing_source_ids?.length ? ` · ${line.routing_source_ids.length} locked sources` : "";
    return `<div class="revision-item"><strong>${kind} · ${escapeHtml(line.name || item.id)}</strong><small>${escapeHtml(item.id)} · ${escapeHtml(routing)}${sources} · ${signed(item.length_delta_m, 1)} m · ${signed(item.station_delta)} stations</small></div>`;
  }).join("") || '<p class="empty-diff">No line or alignment changes</p>';
  const serviceItems = diff.services.map((item) => {
    const plan = item.after || item.before;
    const span = plan ? ` · ${plan.service_start}–${plan.service_end} · ${plan.windows.length} windows` : "";
    return `<div class="revision-item"><strong>${escapeHtml(item.kind)} · ${escapeHtml(item.line)} · ${escapeHtml(item.day_type)}</strong><small>${signed(item.peak_fleet_delta)} fleet · ${signed(item.capacity_delta_pphpd)} pphpd · ${signed(item.daily_service_km_delta, 1)} km/day${span}</small></div>`;
  }
  ).join("") || '<p class="empty-diff">No service changes</p>';
  const coordinationItems = (diff.coordination || []).map((item) => {
    const issue = item.after || item.before;
    const transition = item.before && item.after ? `${item.before.status} → ${item.after.status}` : issue.status;
    return `<div class="revision-item"><strong>${escapeHtml(item.kind)} · ${escapeHtml(item.id)}</strong><small>${escapeHtml(transition)}${issue.reviewed_by ? ` · ${escapeHtml(issue.reviewed_by)}` : ""}</small></div>`;
  }).join("") || '<p class="empty-diff">No coordination changes</p>';
  node.innerHTML = `
    <p>Comparing <strong>${escapeHtml(diff.base_revision_id)}</strong> with candidate <strong>${escapeHtml(diff.candidate_revision_id)}</strong></p>
    <div class="revision-summary">${summary.map(([value, label]) =>
      `<div class="revision-delta"><strong>${value}</strong><span>${label}</span></div>`
    ).join("")}</div>
    <div class="revision-groups">
      <div class="revision-group"><h3>Stations</h3>${stationItems}</div>
      <div class="revision-group"><h3>Lines</h3>${lineItems}</div>
      <div class="revision-group"><h3>Services</h3>${serviceItems}</div>
      <div class="revision-group"><h3>Coordination</h3>${coordinationItems}</div>
    </div>`;
}

$("#compare-revision").addEventListener("click", async () => {
  const revisionId = $("#revision-base").value;
  if (!revisionId) return;
  try {
    comparison = (await api.compareRevision(revisionId)).comparison;
    renderRevisionComparison();
    toast("Semantic revision comparison generated from deterministic snapshots.");
  } catch (error) {
    toast(error.message, true);
  }
});

function setOperationBusy(busy) {
  operationBusy = busy;
  ["#reload", "#compile", "#revision"].forEach((selector) => {
    const button = $(selector);
    if (button) button.disabled = busy;
  });
  document.querySelectorAll("[data-job-adapter]").forEach((button) => {
    button.disabled = busy;
  });
}

$("#reload").addEventListener("click", async () => {
  if (operationBusy) return;
  setOperationBusy(true);
  try {
    await load();
    toast("Project intent, revisions, and engineering jobs reloaded.");
  } finally {
    setOperationBusy(false);
  }
});
$("#compile").addEventListener("click", async () => {
  if (operationBusy) return;
  setOperationBusy(true);
  try {
    const result = await api.compile();
    $("#operation-result").textContent = `Candidate compiled: ${result.path}`;
    await load();
    toast("Candidate compiled with its content hash and validation manifest.");
  } catch (error) {
    toast(error.message, true);
  } finally {
    setOperationBusy(false);
  }
});
$("#revision").addEventListener("click", async () => {
  if (operationBusy) return;
  setOperationBusy(true);
  try {
    const result = await api.revision();
    $("#operation-result").textContent =
      `Revision ${result.revision.revision_id} materialized. Suggested branch: ${result.revision.suggested_branch}; tag after approval: ${result.revision.suggested_tag}`;
    await load();
    toast("Immutable revision created. Review and commit it through GitHub.");
  } catch (error) {
    toast(error.message, true);
  } finally {
    setOperationBusy(false);
  }
});

function toast(message, isError = false) {
  const node = $("#toast");
  node.textContent = message;
  node.classList.toggle("error", isError);
  node.classList.add("show");
  window.clearTimeout(toast.timer);
  toast.timer = window.setTimeout(() => node.classList.remove("show"), 4500);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

load();
