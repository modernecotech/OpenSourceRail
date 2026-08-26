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
  compile: () => api.request("/api/compile", { method: "POST" }),
  revision: () => api.request("/api/revisions", { method: "POST" }),
  revisions: () => api.request("/api/revisions"),
  compareRevision: (id) => api.request(
    `/api/revisions/${encodeURIComponent(id)}/compare`
  ),
};

let view = null;
let selectedStation = null;
let selectedControl = null;
let projection = null;
let drag = null;
let mapMode = "select";
let revisions = null;
let comparison = null;
const lineColours = ["#56d39b", "#5eb9e8", "#e88859", "#a98aef", "#e96d95"];

const $ = (selector) => document.querySelector(selector);

async function load() {
  try {
    [view, revisions] = await Promise.all([api.project(), api.revisions()]);
    selectedStation = selectedStation
      ? view.snapshot.stations.find((item) => item.id === selectedStation.id) || null
      : null;
    selectedControl = selectedControl
      ? view.snapshot.line_control_points.find((item) => item.id === selectedControl.id) || null
      : null;
    render();
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
    path.setAttribute("class", "network-line");
    path.setAttribute("stroke", lineColours[index % lineColours.length]);
    path.dataset.line = feature.properties?.name || `line-${index + 1}`;
    path.addEventListener("click", createObjectFromMap);
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
    circle.addEventListener("click", () => selectStation(station.id));
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
      event.stopPropagation();
      selectControl(control.id);
    });
    svg.appendChild(circle);
  });
}

function startStationDrag(event) {
  const id = event.currentTarget.dataset.id;
  selectStation(id);
  drag = { id, node: event.currentTarget, kind: "station" };
  event.currentTarget.setPointerCapture(event.pointerId);
}

function startControlDrag(event) {
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
    } else {
      selectedStation = null;
      selectedControl = view.snapshot.line_control_points.find((item) => item.id === result.id);
    }
    render();
    toast(mapMode === "station"
      ? "Manual station created. Name it, adjust its archetype, or drag it before saving."
      : "Alignment control point created. Drag it, then save the line geometry intent.");
  } catch (error) {
    toast(error.message, true);
  }
}

document.querySelectorAll(".map-tool").forEach((button) => {
  button.addEventListener("click", () => {
    mapMode = button.dataset.mode;
    document.querySelectorAll(".map-tool").forEach((item) => {
      item.classList.toggle("active", item.dataset.mode === mapMode);
    });
    $("#map-hint").textContent = mapMode === "station"
      ? "Click a line to insert a manual station into the route and simulator topology."
      : mapMode === "control"
        ? "Click a line to add an alignment control point, then drag it."
        : "Select or drag an object to edit its intent.";
  });
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
  renderMap();
  renderStationInspector();
}

function selectControl(id) {
  selectedControl = view.snapshot.line_control_points.find((item) => item.id === id) || null;
  selectedStation = null;
  renderMap();
  renderStationInspector();
}

function renderStationInspector() {
  const form = $("#station-form");
  const controlForm = $("#control-form");
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
$("#service-day").addEventListener("change", renderServiceEditor);
$("#add-window").addEventListener("click", () => {
  $("#service-windows").insertAdjacentHTML("beforeend", windowRow());
  bindWindowButtons();
});

$("#service-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const line = $("#service-line").value;
  const day = $("#service-day").value;
  const windows = [...document.querySelectorAll("#service-windows tr")].map((row) => ({
    from: row.querySelector(".window-from").value,
    to: row.querySelector(".window-to").value,
    headway_min: Number(row.querySelector(".window-headway").value),
  }));
  try {
    view = await api.service(line, day, {
      line,
      day_type: day,
      service_start: $("#service-start").value,
      service_end: $("#service-end").value,
      windows,
    });
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
  const lineItems = controlItems + diff.lines.map((item) =>
    `<div class="revision-item"><strong>${escapeHtml(item.id)} · ${signed(item.length_delta_m, 1)} m</strong><small>${signed(item.station_delta)} stations</small></div>`
  ).join("") || '<p class="empty-diff">No line or alignment changes</p>';
  const serviceItems = diff.services.map((item) => {
    const plan = item.after || item.before;
    const span = plan ? ` · ${plan.service_start}–${plan.service_end} · ${plan.windows.length} windows` : "";
    return `<div class="revision-item"><strong>${escapeHtml(item.kind)} · ${escapeHtml(item.line)} · ${escapeHtml(item.day_type)}</strong><small>${signed(item.peak_fleet_delta)} fleet · ${signed(item.capacity_delta_pphpd)} pphpd · ${signed(item.daily_service_km_delta, 1)} km/day${span}</small></div>`;
  }
  ).join("") || '<p class="empty-diff">No service changes</p>';
  node.innerHTML = `
    <p>Comparing <strong>${escapeHtml(diff.base_revision_id)}</strong> with candidate <strong>${escapeHtml(diff.candidate_revision_id)}</strong></p>
    <div class="revision-summary">${summary.map(([value, label]) =>
      `<div class="revision-delta"><strong>${value}</strong><span>${label}</span></div>`
    ).join("")}</div>
    <div class="revision-groups">
      <div class="revision-group"><h3>Stations</h3>${stationItems}</div>
      <div class="revision-group"><h3>Lines</h3>${lineItems}</div>
      <div class="revision-group"><h3>Services</h3>${serviceItems}</div>
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

$("#reload").addEventListener("click", load);
$("#compile").addEventListener("click", async () => {
  try {
    const result = await api.compile();
    $("#operation-result").textContent = `Candidate compiled: ${result.path}`;
    await load();
    toast("Candidate compiled with its content hash and validation manifest.");
  } catch (error) {
    toast(error.message, true);
  }
});
$("#revision").addEventListener("click", async () => {
  try {
    const result = await api.revision();
    $("#operation-result").textContent =
      `Revision ${result.revision.revision_id} materialized. Suggested branch: ${result.revision.suggested_branch}; tag after approval: ${result.revision.suggested_tag}`;
    await load();
    toast("Immutable revision created. Review and commit it through GitHub.");
  } catch (error) {
    toast(error.message, true);
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
