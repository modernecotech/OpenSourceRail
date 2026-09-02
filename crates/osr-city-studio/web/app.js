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
  gisManifest: () => api.request("/api/gis/manifest"),
  gisLayer: (id) => api.request(`/api/gis/layers/${encodeURIComponent(id)}`),
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
  createApproval: (body) => api.request("/api/approvals", {
    method: "POST", body: JSON.stringify(body),
  }),
  createDemandFlow: (body) => api.request("/api/demand/flows", {
    method: "POST", body: JSON.stringify(body),
  }),
  demandFlow: (id, body) => api.request(`/api/demand/flows/${encodeURIComponent(id)}`, {
    method: "PUT", body: JSON.stringify(body),
  }),
  deleteDemandFlow: (id) => api.request(`/api/demand/flows/${encodeURIComponent(id)}`, {
    method: "DELETE",
  }),
  civil: (body) => api.request("/api/civil", {
    method: "PUT", body: JSON.stringify(body),
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
let gisManifest = null;
let gisLayers = new Map();
let gisLayerState = new Map();
let selectedGisFeature = null;
let mapCamera = { x: 0, y: 0, width: 1000, height: 620 };
let mapPan = null;
let mapMode = "select";
let pendingLineStart = null;
let revisions = null;
let comparison = null;
let jobView = { adapters: [], jobs: [] };
let jobPollTimer = null;
let selectedArtifactPreview = null;
let selectedCoordinationAssetIds = new Set();
let selectedCivilSequence = null;
let civilPlaybackTimer = null;
let civilReviewState = {
  angle_deg: -35,
  stage: 0,
  layers: new Set(),
  groups: new Set(),
  systems: new Set(),
};
let operationBusy = false;
let selectedDemandFlowId = null;
const lineColours = ["#56d39b", "#5eb9e8", "#e88859", "#a98aef", "#e96d95"];
const workbenchContext = Object.fromEntries(new URLSearchParams(location.search));
const inWorkbench = window.parent !== window && location.pathname.startsWith("/studio");

const $ = (selector) => document.querySelector(selector);

function publishWorkbenchContext(patch) {
  Object.assign(workbenchContext, patch);
  if (inWorkbench) {
    window.parent.postMessage({ type: "osr:context", context: patch }, location.origin);
  }
}

function navigateWorkbench(module, patch = {}) {
  if (inWorkbench) {
    window.parent.postMessage({ type: "osr:navigate", module, context: patch }, location.origin);
  }
}

window.addEventListener("message", (event) => {
  if (event.origin === location.origin && event.data?.type === "osr:context") {
    Object.assign(workbenchContext, event.data.context || {});
  }
});

async function load() {
  try {
    const [nextView, nextRevisions, nextJobView, nextGisManifest] = await Promise.all([
      api.project(), api.revisions(), api.jobs(), api.gisManifest(),
    ]);
    const loadedLayers = await Promise.all(nextGisManifest.layers.map(async (layer) => [
      layer.id,
      layer.id === "candidate-network" ? nextView.corridor : await api.gisLayer(layer.id),
    ]));
    view = nextView;
    revisions = nextRevisions;
    jobView = nextJobView;
    gisManifest = nextGisManifest;
    gisLayers = new Map(loadedLayers);
    gisManifest.layers.forEach((layer) => {
      if (!gisLayerState.has(layer.id)) {
        gisLayerState.set(layer.id, {
          visible: layer.default_visible,
          opacity: layer.default_opacity,
        });
      }
    });
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
  renderGisLayerControls();
  renderMap();
  renderStationInspector();
  renderServiceSelectors();
  renderServiceEditor();
  renderDemandPlanner();
  renderCivilSettings();
  renderFindings();
  renderArtifacts();
  renderJobs();
  renderArtifactViewer();
  renderRevisionSelector();
  renderRevisionComparison();
  renderApprovals();
  const selectedAsset = selectedStation?.id || selectedControl?.id || selectedLine?.id;
  if (selectedAsset && selectedAsset !== workbenchContext.selected_asset) {
    publishWorkbenchContext({ selected_asset: selectedAsset });
  }
  $("#open-simulator").hidden = !inWorkbench || !workbenchContext.revision;
}

function renderCivilSettings() {
  const civil = view.snapshot.civil;
  $("#civil-span").value = String(civil.standard_span_m);
  $("#civil-unit-spans").value = String(civil.expansion_unit_spans);
  $("#civil-approach-height").value = civil.maximum_reinforced_soil_height_m;
  $("#civil-mould-cycle").value = civil.mould_cycle_target_h;
  $("#civil-open-method").value = civil.long_open_at_grade_method;
  $("#civil-constrained-method").value = civil.constrained_at_grade_method;
  $("#civil-compare-roads").checked = civil.compare_road_grade_separation;
  const unitLength = civil.standard_span_m * civil.expansion_unit_spans;
  const spansPerKm = Math.ceil(1000 / civil.standard_span_m);
  const unitsPerKm = Math.ceil(spansPerKm / civil.expansion_unit_spans);
  const bearingsPerKm = (spansPerKm + unitsPerKm) * 4;
  $("#civil-derived").innerHTML = `<strong>${unitLength.toFixed(0)} m thermal unit · ${unitsPerKm} deck gaps/km · ${bearingsPerKm} bearings/km</strong><span>Planning interfaces for twin track; project rail–structure and geotechnical release required.</span>`;
  const lineSelect = $("#civil-georef-line");
  const priorLine = lineSelect.value;
  lineSelect.innerHTML = view.snapshot.lines
    .map((line) => `<option value="${escapeHtml(line.id)}">${escapeHtml(line.name || line.id)}</option>`)
    .join("");
  if (view.snapshot.lines.some((line) => line.id === priorLine)) lineSelect.value = priorLine;
  else if (view.snapshot.lines.some((line) => line.id === $("#service-line").value)) lineSelect.value = $("#service-line").value;
  renderCivilGeoreferencing();
}

function setCivilGeoreferencingEnabled(enabled) {
  $("#civil-georef-fields").hidden = !enabled;
  $("#civil-georef-fields").querySelectorAll("input").forEach((input) => {
    input.disabled = !enabled;
    input.required = enabled;
  });
}

function renderCivilGeoreferencing() {
  const line = $("#civil-georef-line").value;
  const settings = (view.snapshot.civil.ifc_georeferencing || [])
    .find((item) => item.line === line);
  $("#civil-georef-enabled").checked = Boolean(settings);
  $("#civil-georef-crs").value = settings?.crs_name || "";
  $("#civil-georef-source").value = settings?.source || "";
  $("#civil-georef-eastings").value = settings?.eastings ?? 0;
  $("#civil-georef-northings").value = settings?.northings ?? 0;
  $("#civil-georef-height").value = settings?.orthogonal_height ?? 0;
  $("#civil-georef-abscissa").value = settings?.x_axis_abscissa ?? 1;
  $("#civil-georef-ordinate").value = settings?.x_axis_ordinate ?? 0;
  $("#civil-georef-scale").value = settings?.scale ?? 1;
  setCivilGeoreferencingEnabled(Boolean(settings));
}

$("#civil-georef-line").addEventListener("change", renderCivilGeoreferencing);
$("#civil-georef-enabled").addEventListener("change", (event) => {
  setCivilGeoreferencingEnabled(event.currentTarget.checked);
});

$("#civil-settings-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const georeferencedLine = $("#civil-georef-line").value;
    const ifcGeoreferencing = (view.snapshot.civil.ifc_georeferencing || [])
      .filter((item) => item.line !== georeferencedLine);
    if ($("#civil-georef-enabled").checked) {
      ifcGeoreferencing.push({
        line: georeferencedLine,
        crs_name: $("#civil-georef-crs").value,
        eastings: Number($("#civil-georef-eastings").value),
        northings: Number($("#civil-georef-northings").value),
        orthogonal_height: Number($("#civil-georef-height").value),
        x_axis_abscissa: Number($("#civil-georef-abscissa").value),
        x_axis_ordinate: Number($("#civil-georef-ordinate").value),
        scale: Number($("#civil-georef-scale").value),
        source: $("#civil-georef-source").value,
      });
    }
    view = await api.civil({
      standard_span_m: Number($("#civil-span").value),
      expansion_unit_spans: Number($("#civil-unit-spans").value),
      maximum_reinforced_soil_height_m: Number($("#civil-approach-height").value),
      long_open_at_grade_method: $("#civil-open-method").value,
      constrained_at_grade_method: $("#civil-constrained-method").value,
      mould_cycle_target_h: Number($("#civil-mould-cycle").value),
      compare_road_grade_separation: $("#civil-compare-roads").checked,
      ifc_georeferencing: ifcGeoreferencing,
    });
    revisions = await api.revisions();
    render();
    toast("Civil construction and IFC survey intent saved in the deterministic revision hash.");
  } catch (error) {
    toast(error.message, true);
  }
});

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
  const bounds = gisManifest?.bounds || (() => {
    const coordinates = corridorLines().flatMap((feature) => feature.geometry.coordinates);
    const xs = coordinates.map((point) => point[0]);
    const ys = coordinates.map((point) => point[1]);
    return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
  })();
  const [minX, minY, maxX, maxY] = bounds;
  const pad = 55;
  const width = 1000 - 2 * pad;
  const height = 620 - 2 * pad;
  const midLat = (minY + maxY) / 2;
  const lonScale = Math.cos(midLat * Math.PI / 180);
  const geographicWidth = Math.max((maxX - minX) * lonScale, Number.EPSILON);
  const geographicHeight = Math.max(maxY - minY, Number.EPSILON);
  const scale = Math.min(width / geographicWidth, height / geographicHeight);
  const drawnWidth = geographicWidth * scale;
  const drawnHeight = geographicHeight * scale;
  const left = (1000 - drawnWidth) / 2;
  const bottom = (620 + drawnHeight) / 2;
  return {
    point(lon, lat) {
      return [
        left + (lon - minX) * lonScale * scale,
        bottom - (lat - minY) * scale,
      ];
    },
    inverse(x, y) {
      return [
        minX + (x - left) / scale / lonScale,
        minY + (bottom - y) / scale,
      ];
    },
  };
}

function renderGisLayerControls() {
  if (!gisManifest) return;
  const categories = new Map();
  gisManifest.layers.forEach((layer) => {
    if (!categories.has(layer.category)) categories.set(layer.category, []);
    categories.get(layer.category).push(layer);
  });
  $("#gis-layers").innerHTML = [...categories.entries()].map(([category, layers]) => `
    <div class="gis-layer-category">${escapeHtml(category)}</div>
    ${layers.map((layer) => {
      const state = gisLayerState.get(layer.id);
      return `<div class="gis-layer-control" data-layer-control="${escapeHtml(layer.id)}">
        <input id="layer-${escapeHtml(layer.id)}" type="checkbox" ${state?.visible ? "checked" : ""}>
        <label for="layer-${escapeHtml(layer.id)}">${escapeHtml(layer.label)}<small>${layer.feature_count.toLocaleString()} features · ${escapeHtml(layer.source_kind)}</small></label>
        <input type="range" min="0" max="1" step="0.05" value="${state?.opacity ?? layer.default_opacity}" aria-label="${escapeHtml(layer.label)} opacity">
      </div>`;
    }).join("")}
  `).join("");
  $("#gis-layer-count").textContent = `(${gisManifest.layers.length})`;
  $("#gis-provenance").textContent = `${gisManifest.coordinate_reference_system} · local deterministic sources · ${gisManifest.attribution.join(" · ")}`;
  $("#map-attribution").textContent = gisManifest.attribution.find((item) => item.includes("OpenStreetMap")) || "";
  document.querySelectorAll("[data-layer-control]").forEach((control) => {
    const id = control.dataset.layerControl;
    control.querySelector('input[type="checkbox"]').addEventListener("change", (event) => {
      gisLayerState.get(id).visible = event.currentTarget.checked;
      renderMap();
    });
    control.querySelector('input[type="range"]').addEventListener("input", (event) => {
      gisLayerState.get(id).opacity = Number(event.currentTarget.value);
      const group = document.querySelector(`[data-gis-group="${CSS.escape(id)}"]`);
      if (group) group.setAttribute("opacity", event.currentTarget.value);
    });
  });
}

function svgPath(coordinates, close = false) {
  const commands = coordinates.map(([lon, lat], index) => {
    const [x, y] = projection.point(lon, lat);
    return `${index ? "L" : "M"} ${x.toFixed(2)} ${y.toFixed(2)}`;
  });
  if (close) commands.push("Z");
  return commands.join(" ");
}

function featureTitle(layer, properties) {
  return properties.name || properties.id || properties.station || layer.label;
}

function inspectGisFeature(layer, feature, index) {
  selectedGisFeature = { layer: layer.id, index };
  const properties = feature.properties || {};
  const entries = Object.entries(properties).filter(([, value]) => value !== null && value !== "");
  const panel = $("#gis-inspector");
  panel.hidden = false;
  panel.innerHTML = `<strong>${escapeHtml(layer.label)} · ${escapeHtml(featureTitle(layer, properties))}</strong><dl>${entries
    .map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(typeof value === "object" ? JSON.stringify(value) : value)}</dd>`)
    .join("")}</dl>`;
  renderMap();
}

function styleGisFeature(node, layerId, properties) {
  const value = Number(properties?.value || 0);
  node.style.setProperty("--value", value);
  if (layerId === "routing-demand") {
    node.setAttribute("fill", "#ff9f43");
    node.setAttribute("fill-opacity", String(0.12 + value * 0.68));
  } else if (layerId === "routing-cost") {
    node.setAttribute("fill", "#d86cff");
    node.setAttribute("fill-opacity", String(0.10 + value * 0.58));
  } else if (layerId === "routing-buildability") {
    node.setAttribute("fill", "#ed7676");
    node.setAttribute("fill-opacity", String(0.20 + value * 0.65));
  }
}

function appendGisGeometry(group, layer, feature, index) {
  const geometry = feature.geometry;
  if (!geometry) return;
  const properties = feature.properties || {};
  const selected = selectedGisFeature?.layer === layer.id && selectedGisFeature?.index === index;
  const addNode = (node, kind) => {
    node.setAttribute("class", `gis-feature ${kind}${selected ? " selected" : ""}`);
    node.dataset.layer = layer.id;
    node.dataset.featureIndex = index;
    styleGisFeature(node, layer.id, properties);
    const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
    title.textContent = `${layer.label} · ${featureTitle(layer, properties)}`;
    node.appendChild(title);
    node.addEventListener("click", (event) => {
      if (mapMode !== "select") return;
      event.stopPropagation();
      inspectGisFeature(layer, feature, index);
    });
    group.appendChild(node);
  };
  if (geometry.type === "Point") {
    const [x, y] = projection.point(...geometry.coordinates);
    const node = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    node.setAttribute("cx", x);
    node.setAttribute("cy", y);
    node.setAttribute("r", layer.id.includes("depots") ? 8 : layer.id.includes("interchanges") ? 7 : 4.5);
    addNode(node, "point");
    if (layer.id === "context-anchors" && properties.name && Number(properties.weight) >= 0.9) {
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", x + 7);
      label.setAttribute("y", y - 6);
      label.setAttribute("class", "gis-label");
      label.textContent = properties.name;
      group.appendChild(label);
    }
    return;
  }
  const paths = [];
  if (geometry.type === "LineString") paths.push([geometry.coordinates, false]);
  else if (geometry.type === "MultiLineString") geometry.coordinates.forEach((line) => paths.push([line, false]));
  else if (geometry.type === "Polygon") geometry.coordinates.forEach((ring) => paths.push([ring, true]));
  else if (geometry.type === "MultiPolygon") geometry.coordinates.forEach((polygon) => polygon.forEach((ring) => paths.push([ring, true])));
  paths.forEach(([coordinates, close]) => {
    const node = document.createElementNS("http://www.w3.org/2000/svg", "path");
    node.setAttribute("d", svgPath(coordinates, close));
    addNode(node, close ? "polygon" : "line");
  });
}

function renderGisLayers(svg) {
  if (!gisManifest) return;
  gisManifest.layers.filter((layer) => layer.id !== "candidate-network").forEach((layer) => {
    const state = gisLayerState.get(layer.id);
    if (!state?.visible) return;
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    group.setAttribute("class", "gis-layer");
    group.setAttribute("opacity", state.opacity);
    group.dataset.gisGroup = layer.id;
    (gisLayers.get(layer.id)?.features || []).forEach((feature, index) => {
      appendGisGeometry(group, layer, feature, index);
    });
    svg.appendChild(group);
  });
}

function renderMap() {
  projection = makeProjection();
  const svg = $("#network-map");
  svg.innerHTML = "";
  applyMapCamera();
  renderGisLayers(svg);
  const candidateState = gisLayerState.get("candidate-network") || { visible: true, opacity: 1 };
  const candidateGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
  candidateGroup.dataset.gisGroup = "candidate-network";
  candidateGroup.setAttribute("opacity", candidateState.opacity);
  candidateGroup.hidden = !candidateState.visible;
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
    candidateGroup.appendChild(path);
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
    candidateGroup.appendChild(circle);
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
    candidateGroup.appendChild(circle);
  });
  if (pendingLineStart) {
    const [x, y] = projection.point(pendingLineStart.lon, pendingLineStart.lat);
    const marker = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    marker.setAttribute("cx", x);
    marker.setAttribute("cy", y);
    marker.setAttribute("r", 9);
    marker.setAttribute("class", "pending-line-point");
    candidateGroup.appendChild(marker);
  }
  svg.appendChild(candidateGroup);
  renderMapScale();
}

function applyMapCamera() {
  $("#network-map").setAttribute(
    "viewBox",
    `${mapCamera.x} ${mapCamera.y} ${mapCamera.width} ${mapCamera.height}`,
  );
}

function eventToMap(event) {
  const svg = $("#network-map");
  const point = svg.createSVGPoint();
  point.x = event.clientX;
  point.y = event.clientY;
  const transformed = point.matrixTransform(svg.getScreenCTM().inverse());
  return [transformed.x, transformed.y];
}

function renderMapScale() {
  if (!projection) return;
  const [, lat] = projection.inverse(mapCamera.x + mapCamera.width / 2, mapCamera.y + mapCamera.height / 2);
  const [west] = projection.inverse(mapCamera.x, mapCamera.y + mapCamera.height / 2);
  const [east] = projection.inverse(mapCamera.x + mapCamera.width, mapCamera.y + mapCamera.height / 2);
  const visibleKm = Math.abs(east - west) * 111.32 * Math.cos(lat * Math.PI / 180);
  $("#map-scale").textContent = `${visibleKm.toFixed(1)} km across`;
}

function zoomMap(factor, centreX = mapCamera.x + mapCamera.width / 2, centreY = mapCamera.y + mapCamera.height / 2) {
  const nextWidth = Math.max(160, Math.min(1000, mapCamera.width * factor));
  const nextHeight = nextWidth * 0.62;
  const ratioX = (centreX - mapCamera.x) / mapCamera.width;
  const ratioY = (centreY - mapCamera.y) / mapCamera.height;
  mapCamera = {
    x: Math.max(0, Math.min(1000 - nextWidth, centreX - ratioX * nextWidth)),
    y: Math.max(0, Math.min(620 - nextHeight, centreY - ratioY * nextHeight)),
    width: nextWidth,
    height: nextHeight,
  };
  applyMapCamera();
  renderMapScale();
}

$("#map-zoom-in").addEventListener("click", () => zoomMap(0.72));
$("#map-zoom-out").addEventListener("click", () => zoomMap(1.38));
$("#map-fit").addEventListener("click", () => {
  mapCamera = { x: 0, y: 0, width: 1000, height: 620 };
  applyMapCamera();
  renderMapScale();
});

$("#network-map").addEventListener("wheel", (event) => {
  event.preventDefault();
  const [x, y] = eventToMap(event);
  zoomMap(event.deltaY < 0 ? 0.82 : 1.22, x, y);
}, { passive: false });

$("#network-map").addEventListener("pointerdown", (event) => {
  if (mapMode !== "pan") return;
  const [x, y] = eventToMap(event);
  mapPan = { x, y, cameraX: mapCamera.x, cameraY: mapCamera.y };
  event.currentTarget.setPointerCapture(event.pointerId);
});

function startStationDrag(event) {
  if (mapMode === "line" || mapMode === "pan") return;
  const id = event.currentTarget.dataset.id;
  drag = { id, node: event.currentTarget, kind: "station" };
  event.currentTarget.setPointerCapture(event.pointerId);
  selectedStation = view.snapshot.stations.find((item) => item.id === id) || null;
  selectedControl = null;
  selectedLine = null;
  if (selectedStation) publishWorkbenchContext({ selected_asset: selectedStation.id });
  renderStationInspector();
}

function startControlDrag(event) {
  if (mapMode === "line" || mapMode === "pan") return;
  event.stopPropagation();
  const id = event.currentTarget.dataset.id;
  drag = { id, node: event.currentTarget, kind: "control" };
  event.currentTarget.setPointerCapture(event.pointerId);
  selectedControl = view.snapshot.line_control_points.find((item) => item.id === id) || null;
  selectedStation = null;
  selectedLine = null;
  if (selectedControl) publishWorkbenchContext({ selected_asset: selectedControl.id });
  renderStationInspector();
}

async function createObjectFromMap(event) {
  if (drag || mapMode === "select") return;
  const [x, y] = eventToMap(event);
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
  if (mapMode === "station" || mapMode === "control") createObjectFromMap(event);
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
      : mapMode === "pan"
        ? "Drag the map to pan; use the wheel or +/− controls to zoom."
      : mapMode === "line"
        ? "Click two endpoints to create a line, terminal platforms, and weekly service plans."
      : mapMode === "control"
        ? "Click a line to add an alignment control point, then drag it."
        : "Select or drag an object to edit its intent.";
  });
});

$("#network-map").addEventListener("click", async (event) => {
  if (mapMode !== "line" || drag) return;
  const [x, y] = eventToMap(event);
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
  const [x, y] = eventToMap(event);
  const [lon, lat] = projection.inverse(x, y);
  $("#map-coordinates").textContent = `${lat.toFixed(6)}, ${lon.toFixed(6)} · ${gisManifest?.coordinate_reference_system || "EPSG:4326"}`;
  if (mapPan) {
    mapCamera.x = Math.max(0, Math.min(1000 - mapCamera.width, mapPan.cameraX + mapPan.x - x));
    mapCamera.y = Math.max(0, Math.min(620 - mapCamera.height, mapPan.cameraY + mapPan.y - y));
    applyMapCamera();
    renderMapScale();
    return;
  }
  if (!drag) return;
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

$("#network-map").addEventListener("pointerup", () => { drag = null; mapPan = null; });
$("#network-map").addEventListener("pointercancel", () => { drag = null; mapPan = null; });

function selectStation(id) {
  selectedStation = view.snapshot.stations.find((item) => item.id === id) || null;
  selectedControl = null;
  selectedLine = null;
  if (selectedStation) publishWorkbenchContext({ selected_asset: selectedStation.id });
  renderMap();
  renderStationInspector();
}

function selectControl(id) {
  selectedControl = view.snapshot.line_control_points.find((item) => item.id === id) || null;
  selectedStation = null;
  selectedLine = null;
  if (selectedControl) publishWorkbenchContext({ selected_asset: selectedControl.id });
  renderMap();
  renderStationInspector();
}

function selectLine(id) {
  selectedLine = view.snapshot.lines.find((item) => item.id === id) || null;
  selectedStation = null;
  selectedControl = null;
  if (selectedLine) publishWorkbenchContext({ selected_asset: selectedLine.id });
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

function renderDemandPlanner() {
  const demand = view.snapshot.demand || { periods: [], flows: [] };
  const periodNode = $("#demand-period");
  const previousPeriod = periodNode.value;
  const selectedFlow = demand.flows.find((flow) => flow.id === selectedDemandFlowId) || null;
  if (!selectedFlow) selectedDemandFlowId = null;
  periodNode.innerHTML = demand.periods.map((period) =>
    `<option value="${escapeHtml(period.id)}">${escapeHtml(period.name)} · ${escapeHtml(period.from)}–${escapeHtml(period.to)}</option>`
  ).join("");
  const desiredPeriod = selectedFlow?.period || previousPeriod;
  if (demand.periods.some((period) => period.id === desiredPeriod)) periodNode.value = desiredPeriod;

  const stationOptions = view.snapshot.stations.map((station) =>
    `<option value="${escapeHtml(station.id)}">${escapeHtml(station.name)} · ${escapeHtml(station.line)}</option>`
  ).join("");
  const originNode = $("#demand-origin");
  const destinationNode = $("#demand-destination");
  const oldOrigin = originNode.value;
  const oldDestination = destinationNode.value;
  originNode.innerHTML = stationOptions;
  destinationNode.innerHTML = stationOptions;
  if (selectedFlow) {
    originNode.value = selectedFlow.origin_station;
    destinationNode.value = selectedFlow.destination_station;
    $("#demand-passengers").value = selectedFlow.passengers_per_hour;
  } else {
    if (view.snapshot.stations.some((station) => station.id === oldOrigin)) originNode.value = oldOrigin;
    if (view.snapshot.stations.some((station) => station.id === oldDestination)) {
      destinationNode.value = oldDestination;
    } else if (destinationNode.options.length > 1) {
      destinationNode.selectedIndex = 1;
    }
  }
  originNode.disabled = Boolean(selectedFlow);
  destinationNode.disabled = Boolean(selectedFlow);
  $("#demand-form-title").textContent = selectedFlow ? `Edit ${selectedFlow.id}` : "Add planning flow";
  $("#cancel-demand").hidden = !selectedFlow;

  const period = periodNode.value;
  const flows = demand.flows.filter((flow) => flow.period === period);
  const metrics = new Map((view.snapshot.demand_metrics || []).map((metric) => [metric.flow_id, metric]));
  const stations = new Map(view.snapshot.stations.map((station) => [station.id, station]));
  const periodDefinition = demand.periods.find((item) => item.id === period);
  const totalDemand = flows.reduce((total, flow) => total + flow.passengers_per_hour, 0);
  const screened = flows.map((flow) => metrics.get(flow.id)).filter(Boolean);
  const maxUtilization = screened.reduce(
    (maximum, metric) => Math.max(maximum, metric.utilization_percent || 0),
    0,
  );
  $("#demand-summary").innerHTML = periodDefinition
    ? `<strong>${flows.length}</strong> OD flows · <strong>${totalDemand.toLocaleString()}</strong> entered passengers/hour · <strong>${maxUtilization.toFixed(1)}%</strong> highest indicative utilization · ${escapeHtml(periodDefinition.day_type)}`
    : "Configure a source-controlled planning period to begin.";
  $("#demand-flows").innerHTML = flows.length ? flows.map((flow) => {
    const metric = metrics.get(flow.id);
    const origin = stations.get(flow.origin_station);
    const destination = stations.get(flow.destination_station);
    const capacity = metric ? metric.capacity_pphpd.toLocaleString() : "—";
    const utilization = metric?.utilization_percent == null
      ? "unavailable"
      : `${metric.utilization_percent.toFixed(1)}%`;
    const status = metric?.status || "unavailable";
    const transfer = metric?.transfers ? "1 transfer screen" : "direct line screen";
    return `<tr data-demand-flow="${escapeHtml(flow.id)}">
      <td><span class="demand-route"><strong>${escapeHtml(origin?.name || flow.origin_station)} → ${escapeHtml(destination?.name || flow.destination_station)}</strong><small>${escapeHtml(flow.id)} · ${escapeHtml(transfer)}</small></span></td>
      <td>${flow.passengers_per_hour.toLocaleString()} pph</td>
      <td>${capacity} pphpd</td>
      <td><span class="demand-status ${escapeHtml(status)}">${escapeHtml(status.replaceAll("-", " "))} · ${escapeHtml(utilization)}</span></td>
      <td><span class="demand-actions"><button type="button" class="secondary" data-demand-edit="${escapeHtml(flow.id)}">Edit</button><button type="button" class="danger" data-demand-delete="${escapeHtml(flow.id)}">×</button></span></td>
    </tr>`;
  }).join("") : '<tr><td colspan="5" class="empty-diff">No OD planning flows in this period.</td></tr>';
}

$("#demand-period").addEventListener("change", () => {
  selectedDemandFlowId = null;
  renderDemandPlanner();
});

$("#cancel-demand").addEventListener("click", () => {
  selectedDemandFlowId = null;
  renderDemandPlanner();
});

$("#demand-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    if (selectedDemandFlowId) {
      view = await api.demandFlow(selectedDemandFlowId, {
        passengers_per_hour: Number($("#demand-passengers").value),
      });
      toast("OD demand updated; capacity screening and revision hash regenerated.");
    } else {
      const result = await api.createDemandFlow({
        period: $("#demand-period").value,
        origin_station: $("#demand-origin").value,
        destination_station: $("#demand-destination").value,
        passengers_per_hour: Number($("#demand-passengers").value),
      });
      view = result.project;
      selectedDemandFlowId = result.id;
      toast("OD demand added as deterministic project intent.");
    }
    revisions = await api.revisions();
    comparison = null;
    render();
  } catch (error) {
    toast(error.message, true);
  }
});

$("#demand-flows").addEventListener("click", async (event) => {
  const editButton = event.target.closest("[data-demand-edit]");
  if (editButton) {
    selectedDemandFlowId = editButton.dataset.demandEdit;
    renderDemandPlanner();
    return;
  }
  const deleteButton = event.target.closest("[data-demand-delete]");
  if (!deleteButton) return;
  const id = deleteButton.dataset.demandDelete;
  if (!window.confirm(`Remove ${id} from the candidate demand plan?`)) return;
  try {
    view = await api.deleteDemandFlow(id);
    if (selectedDemandFlowId === id) selectedDemandFlowId = null;
    revisions = await api.revisions();
    comparison = null;
    render();
    toast("OD demand removed; the revision comparison records the change.");
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
  $("#jobs").innerHTML = jobView.jobs.slice(0, 6).map((job) => {
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
    "field-evidence-brief", "survey-control-readiness", "ground-model-readiness", "surveyed-alignment-readiness", "route-station-fit-readiness", "drainage-ground-readiness",
    "field-evidence-readable", "survey-control-readable", "ground-model-readable", "surveyed-alignment-readable",
    "survey-receipt-manifest", "surveyed-alignment-manifest", "route-station-fit-manifest", "route-station-fit-readable", "drainage-ground-manifest", "drainage-ground-readable",
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
    if (changed) {
      selectedCoordinationAssetIds.clear();
      stopCivilPlayback();
      selectedCivilSequence = null;
      if (nextPreview.format === "json" && nextPreview.content.schema === "org.opensourcerail.bonsai-civil-ifc.v1") {
        const job = jobView.jobs.find((item) => item.id === jobId);
        const sequenceIndex = job?.artifacts.findIndex((item) => item.kind === "civil-4d-sequence") ?? -1;
        if (sequenceIndex >= 0) selectedCivilSequence = await api.jobArtifact(jobId, sequenceIndex);
        const disciplines = Object.keys(nextPreview.content.summary?.disciplines || {});
        const layers = nextPreview.content.layers?.length
          ? nextPreview.content.layers.map((layer) => layer.layer_id)
          : disciplines;
        civilReviewState = {
          angle_deg: -35,
          stage: selectedCivilSequence?.content?.tasks?.length || 0,
          layers: new Set(layers),
          groups: new Set((nextPreview.content.groups || []).map((group) => group.group_id)),
          systems: new Set((nextPreview.content.systems || []).map((system) => system.system_id)),
        };
      }
    }
    // Publish the selection only after companion evidence and review state are
    // ready, so API consumers and the GUI cannot observe a half-rendered
    // artifact transition.
    selectedArtifactPreview = nextPreview;
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
    $("#civil-review-controls").hidden = true;
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
  renderCivilReviewControls(preview);
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

function isCivilObjectIndex(preview = selectedArtifactPreview) {
  return preview?.format === "json"
    && preview.content?.schema === "org.opensourcerail.bonsai-civil-ifc.v1";
}

function civilStageAssetIds() {
  const tasks = selectedCivilSequence?.content?.tasks || [];
  if (!tasks.length || civilReviewState.stage >= tasks.length) return null;
  return new Set(tasks
    .slice(0, civilReviewState.stage)
    .flatMap((task) => task.assigned_asset_ids || []));
}

function renderCivilGraphic() {
  if (!isCivilObjectIndex()) return;
  const selectedIndex = document.querySelector(".artifact-object-button.selected")?.dataset.objectIndex;
  const canvas = $("#artifact-canvas");
  canvas.replaceChildren();
  const graphic = artifactGraphic(selectedArtifactPreview);
  $("#artifact-viewer-empty").hidden = graphic.some((group) => group.length > 0);
  if (graphic.some((group) => group.length > 0)) drawArtifactGraphic(canvas, graphic);
  if (selectedIndex !== undefined) {
    canvas.querySelector(`[data-object-index="${CSS.escape(selectedIndex)}"]`)?.classList.add("selected");
  }
}

function stopCivilPlayback() {
  if (civilPlaybackTimer) window.clearInterval(civilPlaybackTimer);
  civilPlaybackTimer = null;
}

function renderCivilReviewControls(preview) {
  const host = $("#civil-review-controls");
  host.hidden = !isCivilObjectIndex(preview);
  if (host.hidden) return;
  const disciplines = Object.keys(preview.content.summary?.disciplines || {});
  const layers = preview.content.layers?.length
    ? preview.content.layers
    : disciplines.map((discipline) => ({
      layer_id: discipline,
      name: discipline,
      asset_count: preview.content.summary.disciplines[discipline],
    }));
  const groups = preview.content.groups || [];
  const systems = preview.content.systems || [];
  const tasks = selectedCivilSequence?.content?.tasks || [];
  const stage = Math.min(civilReviewState.stage, tasks.length);
  const task = stage > 0 ? tasks[stage - 1] : null;
  const visibleAssets = artifactGraphic(preview).filter((group) => group.length > 0).length;
  host.innerHTML = `<h3>Interactive civil / 4D review</h3>
    <label>Rotate federation · ${civilReviewState.angle_deg}°
      <input id="civil-view-angle" type="range" min="-180" max="180" step="5" value="${civilReviewState.angle_deg}">
    </label>
    <small>Native IFC presentation layers</small>
    <div class="civil-discipline-list">${layers.map((layer) => `<label><input type="checkbox" data-civil-layer="${escapeHtml(layer.layer_id)}" ${civilReviewState.layers.has(layer.layer_id) ? "checked" : ""}>${escapeHtml(layer.name)} · ${layer.asset_count}</label>`).join("")}</div>
    <small>Native IFC coordination groups</small>
    <div class="civil-discipline-list">${groups.map((group) => `<label><input type="checkbox" data-civil-group="${escapeHtml(group.group_id)}" ${civilReviewState.groups.has(group.group_id) ? "checked" : ""}>${escapeHtml(group.name)} · ${group.asset_count}</label>`).join("")}</div>
    <small>Native IFC functional systems</small>
    <div class="civil-discipline-list">${systems.map((system) => `<label><input type="checkbox" data-civil-system="${escapeHtml(system.system_id)}" ${civilReviewState.systems.has(system.system_id) ? "checked" : ""}>${escapeHtml(system.name)} · ${system.asset_count}</label>`).join("")}</div>
    <label>Construction stage
      <input id="civil-stage" type="range" min="0" max="${tasks.length}" step="1" value="${stage}" ${tasks.length ? "" : "disabled"}>
    </label>
    <div class="civil-stage-actions"><button id="civil-playback" type="button" class="secondary" ${tasks.length ? "" : "disabled"}>${civilPlaybackTimer ? "Pause" : "Play 4D"}</button><span class="civil-stage-label">${stage}/${tasks.length} · ${visibleAssets} assets visible</span></div>
    <small>${task ? `${escapeHtml(task.id)} · ${escapeHtml(task.title)} · ${escapeHtml(task.qa_hold)} · ${(task.assigned_asset_ids || []).length} physical outputs · ${(task.review_gate_asset_ids || []).length} virtual review interfaces` : "Pre-construction state"}</small>`;
  host.querySelector("#civil-view-angle").addEventListener("input", (event) => {
    civilReviewState.angle_deg = Number(event.currentTarget.value);
    renderCivilGraphic();
    renderCivilReviewControls(preview);
  });
  host.querySelectorAll("[data-civil-layer]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) civilReviewState.layers.add(checkbox.dataset.civilLayer);
      else civilReviewState.layers.delete(checkbox.dataset.civilLayer);
      renderCivilGraphic();
      renderCivilReviewControls(preview);
    });
  });
  host.querySelectorAll("[data-civil-group]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) civilReviewState.groups.add(checkbox.dataset.civilGroup);
      else civilReviewState.groups.delete(checkbox.dataset.civilGroup);
      renderCivilGraphic();
      renderCivilReviewControls(preview);
    });
  });
  host.querySelectorAll("[data-civil-system]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) civilReviewState.systems.add(checkbox.dataset.civilSystem);
      else civilReviewState.systems.delete(checkbox.dataset.civilSystem);
      renderCivilGraphic();
      renderCivilReviewControls(preview);
    });
  });
  host.querySelector("#civil-stage").addEventListener("input", (event) => {
    stopCivilPlayback();
    civilReviewState.stage = Number(event.currentTarget.value);
    renderCivilGraphic();
    renderCivilReviewControls(preview);
  });
  host.querySelector("#civil-playback").addEventListener("click", () => {
    if (civilPlaybackTimer) {
      stopCivilPlayback();
      renderCivilReviewControls(preview);
      return;
    }
    if (civilReviewState.stage >= tasks.length) civilReviewState.stage = 0;
    civilPlaybackTimer = window.setInterval(() => {
      civilReviewState.stage += 1;
      renderCivilGraphic();
      if (civilReviewState.stage >= tasks.length) stopCivilPlayback();
      renderCivilReviewControls(preview);
    }, 650);
    renderCivilGraphic();
    renderCivilReviewControls(preview);
  });
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
    const angle = civilReviewState.angle_deg * Math.PI / 180;
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);
    const stageAssets = civilStageAssetIds();
    const iso = ([x, y, z]) => {
      const rotatedX = Number(x) * cos - Number(y) * sin;
      const rotatedY = Number(x) * sin + Number(y) * cos;
      return [rotatedX - rotatedY * .7, rotatedX * .24 + rotatedY * .38 - Number(z) * 2.4];
    };
    return (content.objects || []).map((item) => {
      if (!civilReviewState.layers.has(item.presentation_layer_id || item.discipline)) return [];
      if ((content.groups || []).length
        && !civilReviewState.groups.has(item.coordination_group_id)) return [];
      if ((content.systems || []).length
        && !civilReviewState.systems.has(item.functional_system_id)) return [];
      if (stageAssets && !stageAssets.has(item.asset_id)) return [];
      const box = item.bbox_m;
      if (!Array.isArray(box) || box.length !== 6) return [];
      const corners = [
        [box[0], box[1], box[2]], [box[3], box[1], box[2]],
        [box[3], box[4], box[2]], [box[0], box[4], box[2]],
        [box[0], box[1], box[5]], [box[3], box[1], box[5]],
        [box[3], box[4], box[5]], [box[0], box[4], box[5]],
      ].map(iso);
      return [0, 1, 2, 3, 0, 4, 5, 1, 5, 6, 2, 6, 7, 3, 7, 4].map((index) => corners[index]);
    });
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
      path.dataset.discipline = selectedArtifactPreview.content.objects[groupIndex]?.discipline || "unknown";
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
    const materials = new Map((content.materials || []).map((item) => [item.material_id, item]));
    const profiles = new Map((content.profiles || []).map((item) => [item.profile_id, item]));
    const documents = new Map((content.documents || []).map((item) => [item.document_id, item]));
    const groups = new Map((content.groups || []).map((item) => [item.group_id, item]));
    const systems = new Map((content.systems || []).map((item) => [item.system_id, item]));
    const layers = new Map((content.layers || []).map((item) => [item.layer_id, item]));
    const classification = content.classification || {};
    const objectItems = (content.objects || []).map((item) => {
      const material = materials.get(item.material_id);
      const profile = profiles.get(item.profile_id);
      const sourceDocuments = (item.document_ids || []).map((id) => documents.get(id)).filter(Boolean);
      const coordinationGroup = groups.get(item.coordination_group_id);
      const functionalSystem = systems.get(item.functional_system_id);
      const presentationLayer = layers.get(item.presentation_layer_id);
      const engineeringStatus = item.engineering_status
        ? Object.entries(item.engineering_status).map(([key, value]) => `${key} ${value}`).join("\n")
        : "not applicable";
      return {
        label: item.name,
        meta: `${item.ifc_class} · ${item.asset_class} · ${coordinationGroup?.name || "group unresolved"} · ${item.ifc_type_id || "untyped"} · ${item.material_id || "material unresolved"} · ${item.profile_id || "profile not applicable"} · ${sourceDocuments.length} source documents`,
        detail: [
          `asset ${item.asset_id}`,
          `IFC GUID ${item.ifc_guid}`,
          item.ifc_type_id
            ? `type ${item.ifc_type_id} · ${item.ifc_type_class} · ${item.ifc_type_predefined_type}\ntype IFC GUID ${item.ifc_type_guid}`
            : "type untyped · IFC4.3 has no IfcVirtualElementType",
          material
            ? `material ${material.material_id} · ${material.label} · ${material.category}\nmaterial status ${material.specification_status}`
            : "material unresolved · no safe native material association",
          profile
            ? `profile ${profile.profile_id} · ${profile.standard_designation}\nprofile ${profile.geometry_status} · cardinal point ${profile.cardinal_point} · ${profile.area_m2} m²`
            : "profile not applicable or unresolved",
          `classification ${item.classification_code} · ${item.classification_assignment}\nsystem ${classification.name} · ${classification.status}\nexternal mapping ${classification.external_mapping_status}`,
          coordinationGroup
            ? `coordination group ${coordinationGroup.group_id} · ${coordinationGroup.name}\nrole ${coordinationGroup.role}`
            : `coordination group ${item.coordination_group_id} · unresolved`,
          functionalSystem
            ? `functional system ${functionalSystem.system_id} · ${functionalSystem.name}\nIFC ${functionalSystem.ifc_class} · ${functionalSystem.ifc_predefined_type || "no predefined subtype"}\nrole ${functionalSystem.role} · ${functionalSystem.operational_status}`
            : `functional system ${item.functional_system_id || "not indexed"}`,
          presentationLayer
            ? `presentation layer ${presentationLayer.layer_id} · ${presentationLayer.name}\nscope ${presentationLayer.assignment_scope}`
            : `presentation layer ${item.presentation_layer_id || "not indexed"}`,
          `discipline ${item.discipline} · ${item.detail_mode}`,
          `bbox m ${item.bbox_m.join(", ")}`,
          `standard quantities ${(item.standard_quantity_sets || []).join(", ") || "none"}`,
          `source component ${item.source_component_id} · part role ${item.source_part_role}`,
          `bearing connections ${item.bearing_connection_count || 0} · ${(item.bearing_connection_ids || []).join(", ") || "none"}`,
          `engineering status\n${engineeringStatus}`,
          `source ${item.source_geometry}`,
          `source documents\n${sourceDocuments.map((document) => `${document.document_id} · ${document.location}\nsha256 ${document.sha256}`).join("\n")}`,
        ].join("\n"),
        coordinationTarget: item,
      };
    });
    const classificationItems = (classification.references || []).map((reference) => ({
      label: reference.name,
      meta: `${reference.code} · ${reference.classified_asset_count} assets · ${reference.assigned_type_ids.length} types`,
      detail: [
        `classification ${reference.code}`,
        `name ${reference.name}`,
        `system ${classification.name} · edition ${classification.edition}`,
        `status ${classification.status}`,
        `assignment ${reference.assignment}`,
        `classified assets ${reference.classified_asset_count}`,
        `assigned types ${reference.assigned_type_ids.join(", ") || "none"}`,
        `direct assets ${reference.direct_asset_ids.join(", ") || "none"}`,
        `external mapping ${classification.external_mapping_status}`,
      ].join("\n"),
    }));
    const groupItems = (content.groups || []).map((group) => ({
      label: group.name,
      meta: `${group.group_id} · ${group.asset_count} assets · ${group.role}`,
      detail: [
        `coordination group ${group.group_id}`,
        `IFC GUID ${group.ifc_guid}`,
        `IFC class ${group.ifc_class}`,
        `role ${group.role}`,
        `assets ${group.asset_count}`,
        `spatial meaning ${group.spatial_meaning}`,
        `system meaning ${group.system_meaning}`,
      ].join("\n"),
    }));
    const layerItems = (content.layers || []).map((layer) => ({
      label: layer.name,
      meta: `${layer.layer_id} · ${layer.asset_count} assets · ${layer.discipline}`,
      detail: [
        `presentation layer ${layer.layer_id}`,
        `IFC class ${layer.ifc_class}`,
        `name ${layer.name}`,
        `discipline ${layer.discipline}`,
        `assignment scope ${layer.assignment_scope}`,
        `representations ${layer.representation_count}`,
        `description ${layer.description}`,
        "semantics simple geometry grouping and visibility control only",
      ].join("\n"),
    }));
    const systemItems = (content.systems || []).map((system) => ({
      label: system.name,
      meta: `${system.system_id} · ${system.asset_count} assets · ${system.role}`,
      detail: [
        `functional system ${system.system_id}`,
        `IFC GUID ${system.ifc_guid}`,
        `IFC class ${system.ifc_class}`,
        `predefined type ${system.ifc_predefined_type || "not applicable"}`,
        `long name ${system.long_name || "not applicable"}`,
        `role ${system.role}`,
        `assets ${system.asset_count}`,
        `asset classes ${system.asset_classes.join(", ")}`,
        `semantics ${system.semantics}`,
        `spatial meaning ${system.spatial_meaning}`,
        `operational status ${system.operational_status}`,
        `membership ${system.membership_policy}`,
        `railway-part references ${system.spatial_part_names.join(", ")}`,
      ].join("\n"),
    }));
    const constraintItems = (content.constraints || []).map((constraint) => ({
      label: constraint.name,
      meta: `${constraint.evaluation_status} · ${constraint.constraint_grade} · ${constraint.objective_qualifier}`,
      detail: [
        `interface constraint ${constraint.constraint_id}`,
        `IFC class ${constraint.ifc_class}`,
        `grade ${constraint.constraint_grade}`,
        `qualifier ${constraint.objective_qualifier}`,
        `scope ${constraint.scope}`,
        `association intent ${constraint.association_intent}`,
        `related objects ${constraint.related_object_count}`,
        `related assets ${constraint.related_asset_ids.join(", ") || "none"}`,
        `related groups ${constraint.related_group_ids.join(", ") || "none"}`,
        `related systems ${constraint.related_system_ids.join(", ") || "none"}`,
        `external source documents ${(constraint.external_source_document_ids || []).join(", ") || "none"}`,
        `source linkage ${constraint.external_reference_relationship || "not indexed"}`,
        `evaluation ${constraint.evaluation_status}`,
        `observation ${constraint.observation}`,
        `source ${constraint.constraint_source}`,
        `metric status ${constraint.metric_status}`,
        constraint.metric
          ? `native metric ${constraint.metric.metric_id} · ${constraint.metric.ifc_class}\nbenchmark ${constraint.metric.benchmark} · observed ${constraint.metric.observed_value} ${constraint.metric.unit} · target ${constraint.metric.target_value} ${constraint.metric.unit}\nmeasure ${constraint.metric.measure_type} · reference path ${constraint.metric.reference_path_status}\nvalue source ${constraint.metric.value_source}`
          : "native metric none · qualitative source check",
      ].join("\n"),
    }));
    const propertyTemplateItems = (content.property_set_templates || []).map((template) => ({
      label: template.name,
      meta: `${template.template_type} · ${template.property_count} fields · ${template.matched_definition_count} definitions`,
      detail: [
        `property dictionary ${template.name}`,
        `IFC class ${template.ifc_class}`,
        `definition class ${template.definition_class}`,
        `template type ${template.template_type}`,
        `applicable entities ${template.applicable_entities.join(", ")}`,
        `fields ${template.property_count}`,
        `matched definitions ${template.matched_definition_count}`,
        `relationship-linked definitions ${template.linked_definition_count}`,
        `linkage ${template.linkage}`,
        `status ${template.status}`,
        `field dictionary\n${template.properties.map((property) => `${property.name} · ${property.template_type} · ${property.primary_measure_type || "quantity measure from template type"}`).join("\n")}`,
      ].join("\n"),
    }));
    const documentItems = (content.documents || []).map((document) => ({
      label: document.name,
      meta: `${document.document_id} · ${document.media_type} · ${document.associated_asset_ids.length} assets · ${document.associated_type_ids.length} types`,
      detail: [
        `document ${document.document_id}`,
        `location ${document.location}`,
        `revision ${document.revision}`,
        `status ${document.status} · registered with IFC project ${document.registered_with_project}`,
        `purpose ${document.purpose}`,
        `intended use ${document.intended_use}`,
        `scope ${document.scope}`,
        `associated assets ${document.associated_asset_ids.length} · types ${document.associated_type_ids.length}`,
        `associated constraints ${document.associated_constraint_count || 0} · ${(document.associated_constraint_ids || []).join(", ") || "none"}`,
      ].join("\n"),
    }));
    const alignmentItems = content.alignment ? [{
      label: content.alignment.name,
      meta: `${content.alignment.geometry_curve} · ${content.alignment.horizontal_segment_count} horizontal · ${content.alignment.vertical_segment_count} vertical segments`,
      detail: [
        `native alignment ${content.alignment.name}`,
        `IFC class ${content.alignment.ifc_class}`,
        `semantic model ${content.alignment.semantic_model}`,
        `geometry curve ${content.alignment.geometry_curve}`,
        `representations ${content.alignment.representation_identifiers.join(", ")}`,
        `control points ${content.alignment.control_point_count}`,
        `horizontal ${content.alignment.horizontal_segment_count} × ${content.alignment.horizontal_segment_type}`,
        `vertical ${content.alignment.vertical_segment_count} × ${content.alignment.vertical_segment_type}`,
        `length ${content.alignment.total_horizontal_length_m} m · start station ${content.alignment.start_station_m} m`,
        `stationing referents ${content.alignment.stationing_referent_count}`,
        `cant ${content.alignment.cant_status}`,
        `transitions ${content.alignment.transition_status}`,
        `release ${content.alignment.release_status}`,
      ].join("\n"),
    }] : [];
    const costScheduleItems = content.cost_schedule ? [{
      label: content.cost_schedule.name,
      meta: `${content.cost_schedule.predefined_type} · ${content.cost_schedule.item_count} alternatives · ${content.cost_schedule.currency}`,
      detail: [
        `cost schedule ${content.cost_schedule.schedule_id}`,
        `IFC class ${content.cost_schedule.ifc_class}`,
        `predefined type ${content.cost_schedule.predefined_type}`,
        `currency ${content.cost_schedule.currency}`,
        `unit basis ${content.cost_schedule.unit_basis}`,
        `maturity ${content.cost_schedule.maturity}`,
        `basis ${content.cost_schedule.basis}`,
        `source ${content.cost_schedule.source_path}`,
        `sha256 ${content.cost_schedule.source_sha256}`,
        `scope ${content.cost_schedule.scope_boundary}`,
      ].join("\n"),
    }, ...content.cost_schedule.items.map((rate) => ({
      label: rate.name,
      meta: `${rate.rate_id} · ${content.cost_schedule.currency} ${rate.rate_usd_per_route_km.toLocaleString()}/route-km`,
      detail: [
        `cost item ${rate.rate_id}`,
        `IFC class ${rate.ifc_class}`,
        `civil class ${rate.civil_class}`,
        `design target ${content.cost_schedule.currency} ${rate.rate_usd_per_route_km.toLocaleString()} per route-km`,
        `retained benchmark ${content.cost_schedule.currency} ${rate.benchmark_usd_per_route_km.toLocaleString()} per route-km`,
        `design / benchmark ${rate.design_to_benchmark_ratio}`,
        `unit basis ${rate.unit_basis_value_m.toLocaleString()} project metres`,
        `value category ${rate.cost_value_category}`,
        `quantity ${rate.quantity_status}`,
        `product assignment ${rate.product_assignment_status}`,
        `drivers\n${rate.drivers.map((driver) => `${driver.quantity} · ${driver.current_quantity} / ${driver.benchmark_quantity} · ratio ${driver.quantity_ratio}\n${driver.reason}`).join("\n") || "none published for this retained benchmark class"}`,
      ].join("\n"),
    }))] : [];
    const bearingConnectionItems = (content.bearing_connections || []).map((connection) => ({
      label: `${connection.relating_cap_asset_id} → ${connection.related_superstructure_asset_id}`,
      meta: `${connection.ifc_class} · ${connection.realizing_bearing_count} realizing bearings · ${connection.connection_type}`,
      detail: [
        `bearing connection ${connection.connection_id}`,
        `IFC GUID ${connection.ifc_guid}`,
        `IFC class ${connection.ifc_class}`,
        `cap ${connection.relating_cap_asset_id}`,
        `superstructure ${connection.related_superstructure_asset_id} · ${connection.related_superstructure_asset_class}`,
        `realizing bearings ${connection.realizing_bearing_asset_ids.join(", ")}`,
        `connection type ${connection.connection_type}`,
        `derivation ${connection.derivation}`,
        `release ${connection.release_status}`,
      ].join("\n"),
    }));
    const externalDecisionItems = (content.external_engineering_decisions || []).map((decision) => ({
      label: decision.title,
      meta: `${decision.decision_id} · ${decision.status} · ${decision.authority_required}`,
      detail: [
        `external engineering decision ${decision.decision_id}`,
        `status ${decision.status}`,
        `authority ${decision.authority_required}`,
        `required evidence\n${decision.evidence_required.join("\n")}`,
        `blocked capabilities\n${decision.blocked_capabilities.join("\n")}`,
        `safe current state ${decision.safe_current_state}`,
        `implementation closure ${content.capability_closure?.status || "not indexed"}`,
        `implementable open tasks ${content.capability_closure?.implementable_open_task_count ?? "not indexed"}`,
      ].join("\n"),
    }));
    return [...objectItems, ...classificationItems, ...groupItems, ...layerItems, ...constraintItems, ...propertyTemplateItems, ...documentItems, ...alignmentItems, ...costScheduleItems, ...systemItems, ...bearingConnectionItems, ...externalDecisionItems];
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
  host.innerHTML = `<h3>${preview.content.schema?.includes("bcf") ? "Coordination topics" : preview.content.schema?.includes("ids") ? "IDS specifications" : "IFC object, property-dictionary, constraint, layer, group, classification, and document inspector"}</h3>
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
  const createForm = $("#coordination-create-form");
  if (createForm && isCivilObjectIndex()) {
    const firstSelectedIndex = items.findIndex((item) =>
      item.coordinationTarget
      && selectedCoordinationAssetIds.has(item.coordinationTarget.asset_id)
    );
    createForm.hidden = firstSelectedIndex < 0;
    if (firstSelectedIndex >= 0) createForm.dataset.objectIndex = firstSelectedIndex;
  }
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
  const assetIds = items
    .map((item) => item.coordinationTarget?.asset_id)
    .filter((assetId) => assetId && selectedCoordinationAssetIds.has(assetId));
  if (!assetIds.length && target) assetIds.push(target.asset_id);
  if (!assetIds.length) return;
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
  if (preview.format === "json" && Array.isArray(content.alignment?.horizontal)) {
    return [[content.alignment.line_slug || "alignment", "line"], [content.alignment.horizontal?.length || 0, "horizontal elements"], [content.alignment.vertical?.length || 0, "vertical elements"], [`${content.alignment.design_speed_kmh || "—"} km/h`, "design speed"]];
  }
  if (preview.format === "json" && content.sim_duration_s !== undefined) {
    return [[content.scenario_name || "scenario", "scenario"], [`${content.sim_duration_s}s`, "duration"], [Number(content.total_train_km || 0).toFixed(1), "train km"], [content.invariant_violations?.length || 0, "invariant violations"]];
  }
  if (preview.format === "json" && content.schema === "org.opensourcerail.bonsai-civil-ifc.v1") {
    const coordinateReference = content.georeferencing?.native_ifc_georeferencing
      ? content.georeferencing.crs_name
      : "local grid";
    return [
      [content.summary?.assets || 0, "IFC assets"],
      [content.summary?.types || 0, "reusable IFC types"],
      [content.summary?.typed_assets || 0, "typed assets"],
      [content.summary?.native_bearings || 0, "native bridge bearings"],
      [content.summary?.bearing_connection_relationships || 0, "bearing-realized connections"],
      [content.summary?.bearing_connection_realizations || 0, "bearing connection realizations"],
      [content.summary?.connected_bearings || 0, "connected bearings"],
      [content.summary?.connected_pier_caps || 0, "connected pier caps"],
      [content.summary?.connected_superstructure_assets || 0, "connected superstructure assets"],
      [content.summary?.foundation_interfaces || 0, "virtual foundation interfaces"],
      [content.summary?.jacking_interfaces || 0, "bearing jacking interfaces"],
      [content.summary?.pier_caps || 0, "native pier caps"],
      [content.summary?.pier_columns || 0, "native pier columns"],
      [content.summary?.native_rolling_stock_vehicles || 0, "native rolling-stock vehicles"],
      [content.summary?.vehicle_base_quantity_sets || 0, "vehicle base-quantity sets"],
      [content.summary?.materials || 0, "declared material families"],
      [content.summary?.material_associated_assets || 0, "material-associated assets"],
      [content.summary?.profiles || 0, "native section profiles"],
      [content.summary?.profiled_assets || 0, "profile-extruded assets"],
      [content.summary?.classifications || 0, "native classification systems"],
      [content.summary?.classification_references || 0, "asset-class references"],
      [content.summary?.classified_assets || 0, "classified assets"],
      [content.summary?.coordination_groups || 0, "native coordination groups"],
      [content.summary?.grouped_assets || 0, "group-associated assets"],
      [content.summary?.functional_systems || 0, "native functional systems"],
      [content.summary?.built_systems || 0, "specialized built systems"],
      [content.summary?.system_associated_assets || 0, "system-associated assets"],
      [content.summary?.system_spatial_part_references || 0, "system / railway-part references"],
      [content.summary?.presentation_layers || 0, "native presentation layers"],
      [content.summary?.layer_associated_assets || 0, "layer-associated assets"],
      [content.summary?.interface_constraints || 0, "native interface constraints"],
      [content.summary?.interface_metrics || 0, "native interface metrics"],
      [content.summary?.qualitative_only_interface_constraints || 0, "qualitative-only interface constraints"],
      [content.summary?.interface_constraint_related_objects || 0, "constraint evidence links"],
      [content.summary?.interface_constraint_asset_links || 0, "constraint asset links"],
      [content.summary?.interface_constraint_group_links || 0, "constraint group links"],
      [content.summary?.interface_constraint_system_links || 0, "constraint system links"],
      [content.summary?.constraint_source_document_relationships || 0, "constraint source-document relationships"],
      [content.summary?.source_linked_constraint_resources || 0, "source-linked constraint resources"],
      [content.summary?.external_engineering_decisions || 0, "external engineering decisions"],
      [content.capability_closure?.implementable_open_task_count ?? "—", "implementable open IFC tasks"],
      [content.capability_closure?.status || "not indexed", "IFC capability closure"],
      [content.summary?.horizontal_alignment_segments || 0, "native horizontal alignment segments"],
      [content.summary?.vertical_alignment_segments || 0, "native vertical alignment segments"],
      [content.summary?.alignment_stationing_referents || 0, "alignment stationing referents"],
      [content.summary?.planning_rate_schedules || 0, "native planning schedules of rates"],
      [content.summary?.planning_rate_items || 0, "planning unit-rate alternatives"],
      [content.summary?.property_set_templates || 0, "native property-set templates"],
      [content.summary?.property_templates || 0, "typed template fields"],
      [content.summary?.template_matched_definitions || 0, "template-matched definitions"],
      [content.summary?.documents || 0, "hash-locked source documents"],
      [content.summary?.document_associated_assets || 0, "source-linked assets"],
      [content.summary?.construction_tasks || 0, "4D tasks"],
      [content.summary?.construction_output_tasks || 0, "tasks with physical outputs"],
      [content.summary?.scheduled_physical_assets || 0, "scheduled physical assets"],
      [content.summary?.virtual_review_gate_assets || 0, "virtual review-gate assets"],
      [content.summary?.interface_checks || 0, "interface checks"],
      [coordinateReference, "coordinate reference"],
      [content.ifc_schema || "IFC4X3", "coordination schema"],
    ];
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
  const demandItems = (diff.demand || []).map((item) => {
    const flow = item.after || item.before;
    const transition = item.before && item.after
      ? `${item.before.passengers_per_hour.toLocaleString()} → ${item.after.passengers_per_hour.toLocaleString()} pph`
      : `${flow.passengers_per_hour.toLocaleString()} pph`;
    return `<div class="revision-item"><strong>${escapeHtml(item.kind)} · ${escapeHtml(flow.origin_station)} → ${escapeHtml(flow.destination_station)}</strong><small>${escapeHtml(flow.period)} · ${escapeHtml(transition)} · ${escapeHtml(item.id)}</small></div>`;
  }).join("") || '<p class="empty-diff">No demand changes</p>';
  const georeferencingItems = (diff.ifc_georeferencing || []).map((item) => {
    const settings = item.after || item.before;
    const transition = item.before && item.after
      ? `${item.before.crs_name} → ${item.after.crs_name}`
      : settings.crs_name;
    return `<div class="revision-item"><strong>${escapeHtml(item.kind)} · ${escapeHtml(item.line)}</strong><small>${escapeHtml(transition)} · ${escapeHtml(settings.source)}</small></div>`;
  }).join("") || '<p class="empty-diff">No IFC survey-control changes</p>';
  node.innerHTML = `
    <p>Comparing <strong>${escapeHtml(diff.base_revision_id)}</strong> with candidate <strong>${escapeHtml(diff.candidate_revision_id)}</strong></p>
    <div class="revision-summary">${summary.map(([value, label]) =>
      `<div class="revision-delta"><strong>${value}</strong><span>${label}</span></div>`
    ).join("")}</div>
    <div class="revision-groups">
      <div class="revision-group"><h3>Stations</h3>${stationItems}</div>
      <div class="revision-group"><h3>Lines</h3>${lineItems}</div>
      <div class="revision-group"><h3>Services</h3>${serviceItems}</div>
      <div class="revision-group"><h3>Demand</h3>${demandItems}</div>
      <div class="revision-group"><h3>IFC survey control</h3>${georeferencingItems}</div>
      <div class="revision-group"><h3>Coordination</h3>${coordinationItems}</div>
    </div>`;
}

function renderApprovals() {
  const selector = $("#approval-revision");
  const previous = selector.value;
  const available = revisions?.revisions || [];
  selector.innerHTML = available.map((revision) =>
    `<option value="${escapeHtml(revision.revision_id)}">${escapeHtml(revision.revision_id)}${revision.is_current ? " · current" : ""}</option>`
  ).join("");
  if (available.some((revision) => revision.revision_id === previous)) selector.value = previous;
  selector.disabled = available.length === 0;
  $("#approval-form").querySelector('button[type="submit"]').disabled = available.length === 0;
  if (!$("#approval-date").value) $("#approval-date").value = new Date().toISOString().slice(0, 10);
  if (!$("#approval-reviewer").value && workbenchContext.actor) {
    $("#approval-reviewer").value = workbenchContext.actor;
  }
  if (!$("#approval-role").value && workbenchContext.role) {
    $("#approval-role").value = workbenchContext.role;
  }

  const decisions = [...(view.approvals?.decisions || [])].reverse();
  $("#approval-history").innerHTML = `<h3>Git-reviewable decision history</h3>${decisions.length
    ? decisions.map((decision) => `<article class="approval-card ${escapeHtml(decision.status)}">
        <strong>${escapeHtml(decision.status)} · ${escapeHtml(decision.revision_id)}</strong>
        <small>${escapeHtml(decision.reviewer)} · ${escapeHtml(decision.role)} · ${escapeHtml(decision.decided_on)}</small>
        <small>${escapeHtml(decision.review_reference)} · ${escapeHtml(decision.id)}</small>
        <p>${escapeHtml(decision.comment)}</p>
      </article>`).join("")
    : '<p class="empty-diff">No approval decisions recorded. Materialize and review a revision first.</p>'}`;
}

$("#approval-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const result = await api.createApproval({
      revision_id: $("#approval-revision").value,
      status: $("#approval-status").value,
      reviewer: $("#approval-reviewer").value.trim(),
      role: $("#approval-role").value.trim(),
      decided_on: $("#approval-date").value,
      review_reference: $("#approval-reference").value.trim(),
      comment: $("#approval-comment").value.trim(),
    });
    view = result.project;
    if ($("#approval-status").value === "approved") {
      const approved = revisions.revisions.find(
        (revision) => revision.revision_id === $("#approval-revision").value
      );
      if (approved) publishWorkbenchContext({
        revision: approved.revision_id,
        baseline_sha256: approved.content_sha256,
      });
    }
    renderGit();
    renderApprovals();
    toast(`${result.id} appended without changing the immutable design hash.`);
  } catch (error) {
    toast(error.message, true);
  }
});

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
    publishWorkbenchContext({ revision: result.revision.revision_id });
    $("#operation-result").textContent =
      `Revision ${result.revision.revision_id} materialized. Suggested branch: ${result.revision.suggested_branch}; tag after approval: ${result.revision.suggested_tag}`;
    await load();
    $("#approval-revision").value = result.revision.revision_id;
    toast("Immutable revision created. Review and commit it through GitHub.");
  } catch (error) {
    toast(error.message, true);
  } finally {
    setOperationBusy(false);
  }
});

$("#open-simulator").addEventListener("click", () => {
  navigateWorkbench("simulator", {
    revision: workbenchContext.revision,
    mode: "simulation",
  });
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
