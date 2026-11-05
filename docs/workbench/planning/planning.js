"use strict";
const $ = (id) => document.getElementById(id);
const base = "../../design-engine/current/planning/";
const repository = "../../../";
let manifest, index, original, plan, layers, edits = [], epoch = 0;
const pricedRun = new URLSearchParams(location.search).get("pricedRun");
const pricedMode = /^[0-9a-f]{32}$/.test(pricedRun || "");
const svgNS = "http://www.w3.org/2000/svg";
const colours = ["#14786d", "#8754a0", "#c58132", "#337bb6", "#ad4f5b"];
const contextColours = {
  boundaries: "#657184",
  buildings: "#73777c",
  earth: "#9b896a",
  landuse: "#648553",
  places: "#9c4d78",
  roads: "#a15f2a",
  water: "#287bb8",
};
const contextNames = {
  boundaries: "Boundaries",
  buildings: "Buildings",
  earth: "Terrain",
  landuse: "Land use",
  places: "Places",
  roads: "Roads",
  water: "Water",
};
const clean = (n) => {
  if (typeof n !== "number" || !Number.isFinite(n))
    throw Error("Finite numeric input required");
  return n;
};
function status(text, error = false) {
  $("status").textContent = text;
  $("status").dataset.error = String(error);
}
function editStatus(text, error = false) {
  $("edit-status").textContent = text;
  $("edit-status").dataset.error = String(error);
}
async function sha256(raw) {
  return [...new Uint8Array(await crypto.subtle.digest("SHA-256", raw))]
    .map((x) => x.toString(16).padStart(2, "0"))
    .join("");
}
async function inflate(raw, maximum) {
  const reader = new Blob([raw]).stream().pipeThrough(new DecompressionStream("gzip")).getReader();
  let count = 0;
  const chunks = [];
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    count += value.length;
    if (count > maximum) {
      await reader.cancel();
      throw Error("Inflated planning payload exceeds byte budget");
    }
    chunks.push(value);
  }
  const all = new Uint8Array(count);
  let offset = 0;
  for (const chunk of chunks) {
    all.set(chunk, offset);
    offset += chunk.length;
  }
  return all;
}
async function bytes(name) {
  const expected = manifest.files_sha256[name];
  if (!/^[0-9a-f]{64}$/.test(expected || ""))
    throw Error("Missing planning payload digest");
  const response = await fetch(base + name, { cache: "no-store" });
  if (!response.ok) throw Error("Missing planning payload");
  const raw = new Uint8Array(await response.arrayBuffer());
  if (raw.length > 32 * 1024 * 1024)
    throw Error("Planning payload exceeds byte budget");
  if ((await sha256(raw)) !== expected)
    throw Error("Planning payload differs from its receipt");
  return name.endsWith(".gz") ? inflate(raw, 64 * 1024 * 1024) : raw;
}
async function json(name) {
  return JSON.parse(new TextDecoder().decode(await bytes(name)));
}
async function currentMapContext(p) {
  const reference = p.map_context;
  if (!reference) return null;
  const relative = reference.path;
  if (
    !/^cities\/catalogue\/[^/]+\/[^/]+\/[^/]+\/map-context\.json\.gz$/.test(relative || "") ||
    !/^[0-9a-f]{64}$/.test(reference.sha256 || "") ||
    p.source_sha256?.[relative] !== reference.sha256 ||
    reference.role !==
      "Geographic context only; not survey, route-clearance, demand, engineering or operating evidence"
  )
    throw Error("Current city map context is not bound to its planning revision");
  const url = new URL(
    relative.split("/").map(encodeURIComponent).join("/"),
    new URL(repository, document.baseURI),
  );
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw Error("Current city map context is unavailable");
  const raw = new Uint8Array(await response.arrayBuffer());
  if (raw.length > 32 * 1024 * 1024)
    throw Error("Current city map context exceeds its byte budget");
  if ((await sha256(raw)) !== reference.sha256)
    throw Error("Current city map context differs from its source digest");
  const value = JSON.parse(new TextDecoder().decode(await inflate(raw, 64 * 1024 * 1024)));
  if (!value || typeof value.layers !== "object" || Array.isArray(value.layers))
    throw Error("Current city map context has an unsupported layer set");
  if (
    !Array.isArray(value.bounds_wsen) || value.bounds_wsen.length !== 4 ||
    value.bounds_wsen.some((n) => typeof n !== "number" || !Number.isFinite(n))
  )
    throw Error("Current city map context has invalid display bounds");
  return value;
}
function mapLayers(p, context) {
  const contextLayers = Object.entries(context?.layers || {})
    .filter(([id, features]) => /^[a-z0-9_-]{1,80}$/.test(id) && Array.isArray(features))
    .map(([key, features]) => ({
      id: `context-${key}`,
      key,
      name: contextNames[key] || key.replaceAll("_", " "),
      features,
      renderable: features.length <= 50000,
    }));
  return {
    bounds: context?.bounds_wsen || null,
    attribution: context?.attribution || [],
    context: contextLayers,
    layers: [
      { id: "alignments", name: "Proposed route geometry", available: true, features: p.lines.map((line) => ({ geometry: { type: "LineString", coordinates: line.coordinates }, properties: { id: line.id } })) },
      { id: "operating-stops", name: "Proposed stop locations", available: true, features: p.lines.flatMap((line) => line.stops.map((stop) => ({ geometry: { type: "Point", coordinates: [stop.lon, stop.lat] }, properties: { id: stop.id } }))) },
      { id: "transfers", name: "Transfer references", available: true, features: (p.interchanges || []).map((item) => ({ geometry: { type: "Point", coordinates: [item.lon, item.lat] }, properties: { id: item.id } })) },
      { id: "revision-changes", name: "Proposed route revisions", available: true, features: [] },
    ],
  };
}
function option(parent, value, label) {
  const element = document.createElement("option");
  element.value = value;
  element.textContent = label;
  parent.append(element);
}
function point(line, chainage) {
  let remaining = chainage;
  for (let i = 1; i < line.coordinates.length; i++) {
    const a = line.coordinates[i - 1], b = line.coordinates[i], length = distance(a, b);
    if (remaining <= length || i === line.coordinates.length - 1) {
      const fraction = length ? remaining / length : 0;
      return a.map((value, j) => value + fraction * (b[j] - value));
    }
    remaining -= length;
  }
  throw Error("Empty route");
}
function distance(a, b) {
  const radians = Math.PI / 180, lat1 = a[1] * radians, lat2 = b[1] * radians;
  const h = Math.sin((lat2 - lat1) / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin((b[0] - a[0]) * radians / 2) ** 2;
  return 6371008.8 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(Math.max(0, 1 - h)));
}
function line() {
  return plan.lines.find((item) => item.id === $("line").value);
}
function setStops(preferred) {
  const selectedLine = line();
  if (!selectedLine) return;
  $("stop").replaceChildren();
  for (const stop of selectedLine.stops) option($("stop"), stop.id, stop.id);
  $("headway").value = selectedLine.headway_s;
  const selected = selectedLine.stops.some((stop) => stop.id === preferred) ? preferred : selectedLine.stops[0]?.id;
  $("stop").value = selected || "";
  setStop();
  if (pricedMode) $("priced-geometry").value=JSON.stringify({coordinates:selectedLine.coordinates,
    stops:selectedLine.stops.map(s=>({id:s.id,chainage_m:s.chainage_m,dwell_s:s.dwell_s})),
    shape:selectedLine.shape,design_speed_cap_m_s:selectedLine.design_speed_cap_m_s,
    reason:"Explicit route and station revision for calculated comparison"},null,2);
}
function setStop() {
  const selectedLine = line(), selectedStop = selectedLine?.stops.find((item) => item.id === $("stop").value);
  if (!selectedStop) return;
  $("chainage").value = selectedStop.chainage_m.toFixed(3);
  $("chainage").max = selectedLine.length_m;
  $("dwell").value = selectedStop.dwell_s;
}
function apply(edit) {
  const trial = structuredClone(plan), selectedLine = trial.lines.find((item) => item.id === edit.line);
  if (edit.kind === "add-stop") {
    if (typeof edit.stop !== "string" || !/^[a-z0-9][a-z0-9-]{0,80}$/.test(edit.stop) || edits.some((item) => item.kind === "add-stop" && item.stop === edit.stop) || trial.lines.some((item) => item.stops.some((stop) => stop.id === edit.stop))) throw Error("Unique bounded proposed stop ID required");
    const chainage = clean(edit.chainage_m), dwell = clean(edit.dwell_s);
    if (chainage <= 0 || chainage >= selectedLine.length_m) throw Error("New station must lie inside route endpoints");
    if (dwell < 10 || dwell > 3600) throw Error("Dwell outside planning bounds");
    const [lon, lat] = point(selectedLine, chainage);
    selectedLine.stops.push({ id: edit.stop, chainage_m: chainage, lon, lat, dwell_s: dwell, access_and_transfer_reassessment_required: true });
    selectedLine.stops.sort((a, b) => a.chainage_m - b.chainage_m);
  } else if (edit.kind === "move-stop") {
    const stop = selectedLine.stops.find((item) => item.id === edit.stop);
    if (!stop) throw Error("Unknown stop");
    stop.chainage_m = clean(edit.chainage_m);
    if (stop.chainage_m < 0 || stop.chainage_m > selectedLine.length_m) throw Error("Station outside route");
    [stop.lon, stop.lat] = point(selectedLine, stop.chainage_m);
  } else if (edit.kind === "retire-stop") {
    if (!selectedLine.stops.some((item) => item.id === edit.stop)) throw Error("Unknown stop");
    if (selectedLine.stops.length <= 2) throw Error("At least two proposed stations must remain");
    if (trial.od.some((row) => row.origin === edit.stop || row.destination === edit.stop)) throw Error("Revise OD rows before retiring a station");
    selectedLine.stops = selectedLine.stops.filter((item) => item.id !== edit.stop);
  } else if (edit.kind === "set-service") {
    selectedLine.headway_s = clean(edit.headway_s);
    if (selectedLine.headway_s < 10 || selectedLine.headway_s > 86400) throw Error("Headway outside planning bounds");
    clean(edit.dwell_s);
    if (edit.dwell_s < 10 || edit.dwell_s > 3600) throw Error("Dwell outside planning bounds");
    for (const stop of selectedLine.stops) stop.dwell_s = edit.dwell_s;
  } else if (edit.kind === "replace-line-geometry" && pricedMode) {
    if (!Array.isArray(edit.coordinates) || edit.coordinates.length<2 || edit.coordinates.length>20000 || !Array.isArray(edit.stops) || edit.stops.length<2) throw Error("Bounded route and explicit stations required");
    for (const p of edit.coordinates) if (!Array.isArray(p)||p.length!==2||!Number.isFinite(p[0])||!Number.isFinite(p[1])||Math.abs(p[0])>180||Math.abs(p[1])>90) throw Error("Valid longitude/latitude required");
    if (!["radial","ring"].includes(edit.shape)) throw Error("Explicit route topology required");
    if (edit.shape==="ring" && JSON.stringify(edit.coordinates[0])!==JSON.stringify(edit.coordinates.at(-1))) throw Error("Ring route must close");
    selectedLine.coordinates=structuredClone(edit.coordinates);selectedLine.shape=edit.shape;
    selectedLine.length_m=0;for(let i=1;i<edit.coordinates.length;i++)selectedLine.length_m+=distance(edit.coordinates[i-1],edit.coordinates[i]);
    if(selectedLine.length_m<1)throw Error("Collapsed route");
    const seen=new Set();selectedLine.stops=edit.stops.map(s=>{
      if(typeof s.id!=="string"||seen.has(s.id)||clean(s.chainage_m)<0||s.chainage_m>selectedLine.length_m||clean(s.dwell_s)<10||s.dwell_s>3600)throw Error("Explicit ordered unique station anchors required");
      seen.add(s.id);const [lon,lat]=point(selectedLine,s.chainage_m);return {...s,lon,lat,access_and_transfer_reassessment_required:true};
    });
    selectedLine.design_speed_cap_m_s=clean(edit.design_speed_cap_m_s);
    if(selectedLine.design_speed_cap_m_s<=0||selectedLine.design_speed_cap_m_s>40)throw Error("Bounded design speed required");
  } else if (edit.kind === "straighten-line") {
    const oldLength = selectedLine.length_m;
    selectedLine.coordinates = [selectedLine.coordinates[0], selectedLine.coordinates.at(-1)];
    selectedLine.length_m = distance(...selectedLine.coordinates);
    if (selectedLine.length_m < 1) throw Error("Collapsed alignment");
    for (const stop of selectedLine.stops) {
      stop.chainage_m *= selectedLine.length_m / oldLength;
      [stop.lon, stop.lat] = point(selectedLine, stop.chainage_m);
    }
  } else if (edit.kind === "set-od") {
    if (!Array.isArray(edit.rows) || edit.rows.length > 100000) throw Error("Bounded OD rows required");
    const ids = new Set(trial.lines.flatMap((item) => item.stops.map((stop) => stop.id))), seen = new Set();
    for (const row of edit.rows) {
      const key = row.origin + ">" + row.destination;
      if (!ids.has(row.origin) || !ids.has(row.destination) || row.origin === row.destination || seen.has(key) || !["synthetic", "observed-unaccepted"].includes(row.basis)) throw Error("Invalid OD identity or basis");
      if (clean(row.trips_per_day) < 0 || row.trips_per_day > 1e8) throw Error("Invalid demand");
      seen.add(key);
    }
    trial.od = structuredClone(edit.rows);
  } else throw Error("Unknown edit");
  for (const currentLine of trial.lines) for (let i = 1; i < currentLine.stops.length; i++) if (currentLine.stops[i].chainage_m <= currentLine.stops[i - 1].chainage_m) throw Error("Station order conflict; revise the neighbouring stops");
  plan = trial;
  edits.push(structuredClone(edit));
  render();
  setStops(edit.kind === "retire-stop" ? $("stop").value : (edit.stop || $("stop").value));
  editStatus(`${edits.length} proposed changes. Access, demand, structures, controls and delivery require reassessment.`);
}
function nextStopId() {
  const ids = new Set([...plan.lines.flatMap((item) => item.stops.map((stop) => stop.id)), ...edits.filter((item) => item.kind === "add-stop").map((item) => item.stop)]);
  for (let i = 1; i <= 100000; i++) {
    const id = `proposal-stop-${String(i).padStart(3, "0")}`;
    if (!ids.has(id)) return id;
  }
  throw Error("Proposed station identity range exhausted");
}
function action(callback) {
  try { callback(); } catch (error) { editStatus(error.message, true); }
}
function projectContextGeometry(geometry, project, paths) {
  if (!geometry || typeof geometry !== "object") return;
  const position = (coordinate) => {
    if (!Array.isArray(coordinate) || coordinate.length < 2 || !coordinate.slice(0, 2).every(Number.isFinite)) return null;
    const value = project(coordinate);
    return value.every(Number.isFinite) ? value : null;
  };
  const addLine = (coordinates, close = false) => {
    if (!Array.isArray(coordinates) || coordinates.length < 2) return;
    const points = coordinates.map(position);
    if (points.some((value) => value === null)) return;
    paths[close ? "areas" : "lines"].push("M" + points.map((value) => `${value[0]} ${value[1]}`).join("L") + (close ? "Z" : ""));
  };
  const addPoint = (coordinate) => {
    const value = position(coordinate);
    if (!value) return;
    paths.points.push(`M${value[0] - 2.2} ${value[1]}a2.2 2.2 0 1 0 4.4 0a2.2 2.2 0 1 0 -4.4 0`);
  };
  switch (geometry.type) {
    case "Point": addPoint(geometry.coordinates); break;
    case "MultiPoint": for (const coordinate of geometry.coordinates || []) addPoint(coordinate); break;
    case "LineString": addLine(geometry.coordinates); break;
    case "MultiLineString": for (const line of geometry.coordinates || []) addLine(line); break;
    case "Polygon": for (const ring of geometry.coordinates || []) addLine(ring, true); break;
    case "MultiPolygon": for (const polygon of geometry.coordinates || []) for (const ring of polygon) addLine(ring, true); break;
    case "GeometryCollection": for (const item of geometry.geometries || []) projectContextGeometry(item, project, paths); break;
    default: break;
  }
}
function appendContextPaths(svg, layer, project) {
  const paths = { areas: [], lines: [], points: [] };
  for (const feature of layer.features) projectContextGeometry(feature.geometry, project, paths);
  const colour = contextColours[layer.key] || "#72777f";
  for (const [kind, d] of Object.entries(paths)) {
    if (!d.length) continue;
    const element = document.createElementNS(svgNS, "path");
    element.setAttribute("d", d.join(""));
    element.setAttribute("stroke", colour);
    element.setAttribute("fill", kind === "areas" || kind === "points" ? colour : "none");
    element.setAttribute("stroke-width", kind === "lines" ? (layer.key === "roads" ? "0.75" : "1.1") : "0.55");
    element.setAttribute("fill-opacity", kind === "areas" ? "0.13" : "0.82");
    element.setAttribute("stroke-opacity", kind === "points" ? "0.72" : "0.62");
    element.setAttribute("fill-rule", "evenodd");
    element.dataset.contextLayer = layer.key;
    svg.append(element);
  }
}
function render() {
  const all = plan.lines.flatMap((item) => item.coordinates), xs = all.map((value) => value[0]), ys = all.map((value) => value[1]);
  let minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const bounds = layers.bounds;
  if (bounds) {
    minX = Math.min(minX, bounds[0]); minY = Math.min(minY, bounds[1]);
    maxX = Math.max(maxX, bounds[2]); maxY = Math.max(maxY, bounds[3]);
  }
  const lonScale = 111320 * Math.cos((minY + maxY) / 2 * Math.PI / 180);
  const width = (maxX - minX) * lonScale, height = (maxY - minY) * 111320;
  const scale = Math.min(920 / (width || 1), 620 / (height || 1));
  const padX = (1000 - width * scale) / 2, padY = (700 - height * scale) / 2;
  const x = (value) => padX + (value[0] - minX) * lonScale * scale;
  const y = (value) => 700 - padY - (value[1] - minY) * 111320 * scale;
  const project = (value) => [x(value), y(value)];
  const svg = $("map");
  svg.replaceChildren();
  for (const layer of layers.context) {
    if (!layer.renderable || !document.querySelector(`[data-layer="${layer.id}"]`)?.checked) continue;
    appendContextPaths(svg, layer, project);
  }
  for (const [j, layer] of layers.layers.entries()) {
    if (!document.querySelector(`[data-layer="${layer.id}"]`)?.checked) continue;
    let features = layer.features;
    if (layer.id === "alignments") features = plan.lines.map((item) => ({ geometry: { type: "LineString", coordinates: item.coordinates }, properties: { id: item.id } }));
    if (layer.id === "operating-stops") features = plan.lines.flatMap((item) => item.stops.map((stop) => ({ geometry: { type: "Point", coordinates: [stop.lon, stop.lat] }, properties: { id: stop.id } })));
    if (layer.id === "revision-changes") features = edits.filter((item) => item.line).map((item) => ({ geometry: { type: "LineString", coordinates: plan.lines.find((currentLine) => currentLine.id === item.line).coordinates }, properties: { id: item.kind } }));
    for (const feature of features) {
      const geometry = feature.geometry;
      if (!geometry) continue;
      let element;
      if (geometry.type === "Point") {
        element = document.createElementNS(svgNS, "circle");
        element.setAttribute("cx", x(geometry.coordinates)); element.setAttribute("cy", y(geometry.coordinates));
        element.setAttribute("r", layer.id === "operating-stops" ? 4 : layer.id === "transfers" ? 5 : 2.3);
        element.setAttribute("fill-opacity", ".72");
      } else if (geometry.type === "LineString") {
        element = document.createElementNS(svgNS, "polyline");
        element.setAttribute("points", geometry.coordinates.map((value) => `${x(value)},${y(value)}`).join(" "));
        element.setAttribute("fill", "none"); element.setAttribute("stroke-width", layer.id === "alignments" ? "2.5" : "1");
      } else continue;
      element.setAttribute("stroke", colours[j % colours.length]);
      if (geometry.type === "Point") element.setAttribute("fill", colours[j % colours.length]);
      if (layer.id === "revision-changes") element.classList.add("proposed");
      if (layer.id === "alignments" && feature.properties.id === $("line").value) { element.setAttribute("stroke", "#bc4f32"); element.setAttribute("stroke-width", "4"); }
      if (layer.id === "operating-stops") element.addEventListener("click", () => {
        const owner = plan.lines.find((currentLine) => currentLine.stops.some((stop) => stop.id === feature.properties.id));
        $("line").value = owner.id; setStops(); $("stop").value = feature.properties.id; setStop(); render();
      });
      const title = document.createElementNS(svgNS, "title"); title.textContent = String(feature.properties?.id || layer.name); element.append(title); svg.append(element);
    }
  }
  $("issues").replaceChildren();
  for (const currentLine of plan.lines) {
    if (currentLine.headway_s < currentLine.planning_minimum_headway_s) {
      const item = document.createElement("li");
      item.textContent = `${currentLine.id}: below the selected v0.6 service headway target of ${currentLine.planning_minimum_headway_s} s; this is not a protected-headway result`;
      $("issues").append(item);
    }
    for (let i = 1; i < currentLine.stops.length; i++) if (currentLine.stops[i].chainage_m - currentLine.stops[i - 1].chainage_m < 1500) {
      const item = document.createElement("li"); item.textContent = currentLine.id + ": below the 1,500 m planning comparison; access and transfer review required"; $("issues").append(item);
    }
  }
  $("export").disabled = edits.length === 0; $("reset").disabled = edits.length === 0;
}
async function loadCity() {
  const current = ++epoch;
  status("Verifying current planning revision and source-bound map context…");
  original = null; plan = null; layers = null; edits = [];
  for (const id of ["map", "layers", "line", "stop", "issues"]) $(id).replaceChildren();
  $("map-caption").textContent = "No verified city loaded."; $("revision").textContent = ""; $("import").disabled = true; $("reset").disabled = true;
  $("map-context-attribution").textContent = "";
  for (const id of ["line", "stop", "move", "add-stop", "retire-stop", "service", "straighten", "set-od", "export"]) $(id).disabled = true;
  try {
    const row = index.cities.find((item) => item.city === $("city").value); let currentPlan = await json(row.plan);
    if (current !== epoch) return;
    if (currentPlan.city !== row.city || currentPlan.revision_sha256 !== row.revision_sha256 || currentPlan.selection_id !== index.selection_id) throw Error("Incompatible current geography or candidate identity");
    if(pricedMode) {
      const prefix="/api/city-studies/"+pricedRun+"/artifacts/";
      const response=await fetch(prefix+"manifest.json",{cache:"no-store"});
      if(!response.ok)throw Error("Verified priced city study unavailable; open the local Workbench");
      const record=await response.json(),payload=await fetch(prefix+"planning.json",{cache:"no-store"});
      if(!payload.ok)throw Error("Priced planning base unavailable");
      const raw=new Uint8Array(await payload.arrayBuffer());
      if(raw.length>32*1024*1024||(await sha256(raw))!==record.files_sha256?.["planning.json"])throw Error("Priced planning base differs from its manifest");
      const imported=JSON.parse(new TextDecoder().decode(raw));
      if(imported.city!==row.city||imported.selection_id!==index.selection_id||imported.schema!=="osr-owner-builder-plan/1"||!imported.outline_context?.seed)throw Error("Priced planning identity differs");
      if(["design_complete","physical_validation","manufacturing_release","physical_release","engineering_accepted","movement_authority","procurement_released"].some(k=>imported[k]!==false))throw Error("Planning import cannot grant release");
      currentPlan=imported;$("city").disabled=true;$("priced-controls").hidden=false;$("planning-advisories").open=false;$("handoff-help").textContent="This priced edit bundle is based on the exact calculated study above. Recalculate these edits to produce a new costed outline, fleet, delivery schedule and disabled business drafts. Download the bundle to retain its source identity and review history. Actual construction, purchasing and physical operation require separate approval.";
    }
    const context = await currentMapContext(currentPlan);
    if (current !== epoch) return;
    original = currentPlan; plan = structuredClone(currentPlan); layers = mapLayers(currentPlan, context); edits = [];
    $("revision").textContent = `Current geography revision ${currentPlan.revision_sha256}; ${currentPlan.lines.length} route proposals use the selected v0.6 service defaults.`;
    $("line").replaceChildren(); for (const currentLine of currentPlan.lines) option($("line"), currentLine.id, currentLine.id); setStops();
    $("layers").replaceChildren();
    const controls = [
      ...layers.context.map((item) => ({ ...item, available: item.renderable, checked: ["roads", "water", "places"].includes(item.key) })),
      ...layers.layers.map((item) => ({ ...item, checked: true })),
    ];
    for (const item of controls) {
      const label = document.createElement("label"), input = document.createElement("input");
      input.type = "checkbox"; input.dataset.layer = item.id; input.disabled = item.available === false; input.checked = item.checked;
      input.addEventListener("change", render);
      const note = item.available === false ? " · display limit 50,000 features" : ` (${item.features.length})`;
      label.append(input, document.createTextNode(` ${item.name}${note}`)); $("layers").append(label);
    }
    for (const attribution of layers.attribution) {
      if (!attribution || typeof attribution.name !== "string") continue;
      const item = document.createElement("div");
      const source = document.createElement("a");
      source.textContent = attribution.name;
      let safeUrl = null;
      try {
        const parsed = new URL(attribution.url);
        if (parsed.protocol === "https:" && ["www.openstreetmap.org", "www.naturalearthdata.com", "protomaps.com"].includes(parsed.hostname)) safeUrl = parsed.href;
      } catch {}
      if (safeUrl) { source.href = safeUrl; source.target = "_blank"; source.rel = "noopener noreferrer"; }
      else source.removeAttribute("href");
      item.append(source);
      if (typeof attribution.license === "string" && attribution.license) {
        const license = document.createElement("span"); license.textContent = ` · ${attribution.license}`; item.append(license);
      }
      $("map-context-attribution").append(item);
    }
    for (const id of ["line", "stop", "move", "add-stop", "retire-stop", "service", "straighten", "set-od", "import"]) $(id).disabled = false;
    if(pricedMode) {$("straighten").disabled=true;$("revision").textContent=`Priced city planning base ${currentPlan.revision_sha256}; source outline ${currentPlan.source_outline_evaluation_id}. Geometry edits use explicit station anchors.`;}
    $("map-caption").textContent = `${currentPlan.city}: source-verified city geography and route context. Lines, stops, service and OD edits remain proposals.`;
    $("od").value = JSON.stringify(plan.od, null, 2); editStatus("No local changes."); render();
    status("Current planning geography and map-context source bytes verified.");
  } catch (error) {
    if (current === epoch) status("Planning held: " + error.message, true);
  }
}
$("line").addEventListener("change", () => { setStops(); render(); });
$("stop").addEventListener("change", setStop);
$("city").addEventListener("change", loadCity);
$("move").addEventListener("click", () => action(() => apply({ kind: "move-stop", line: line().id, stop: $("stop").value, chainage_m: Number($("chainage").value) })));
$("add-stop").addEventListener("click", () => action(() => { apply({ kind: "add-stop", line: line().id, stop: $("new-stop-id").value.trim() || nextStopId(), chainage_m: Number($("chainage").value), dwell_s: Number($("dwell").value) }); $("new-stop-id").value = ""; }));
$("retire-stop").addEventListener("click", () => action(() => apply({ kind: "retire-stop", line: line().id, stop: $("stop").value })));
$("service").addEventListener("click", () => action(() => apply({ kind: "set-service", line: line().id, headway_s: Number($("headway").value), dwell_s: Number($("dwell").value) })));
$("straighten").addEventListener("click", () => action(() => apply({ kind: "straighten-line", line: line().id })));
$("set-od").addEventListener("click", () => action(() => apply({ kind: "set-od", rows: JSON.parse($("od").value) })));
$("reset").addEventListener("click", () => { plan = structuredClone(original); edits = []; setStops(); render(); editStatus("Local proposal discarded."); });
function editBundle() {
  const actor = $("author").value.trim(); if (!actor) throw Error("Named planning author required");
  return pricedMode ? {schema:"osr-priced-planning-edits/1",city:original.city,base_revision_sha256:original.revision_sha256,
    actor,edits,seed_id:original.official_seed_id,source_outline_evaluation_id:original.source_outline_evaluation_id}
    : {schema:"osr-planning-edit-bundle/1",city:original.city,base_revision_sha256:original.revision_sha256,actor,edits};
}
$("export").addEventListener("click", () => action(() => {
  const value=editBundle();
  const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2) + "\n"], { type: "application/json" }));
  const anchor = document.createElement("a"); anchor.href = url; anchor.download = original.city + "-planning-edits.json"; anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}));
$("import").addEventListener("change", () => action(async () => {
  try {
    const file = $("import").files[0]; if (!file || file.size > 4 * 1024 * 1024) throw Error("Bounded edit file required");
    const value = JSON.parse(await file.text());
    if (value.schema !== (pricedMode?"osr-priced-planning-edits/1":"osr-planning-edit-bundle/1") || value.city !== original.city || value.base_revision_sha256 !== original.revision_sha256 || !Array.isArray(value.edits) || value.edits.length > 1000) throw Error("Stale or incompatible edit bundle");
    const oldPlan = plan, oldEdits = edits;
    try { plan = structuredClone(original); edits = []; for (const item of value.edits) apply(item); $("author").value = String(value.actor || ""); }
    catch (error) { plan = oldPlan; edits = oldEdits; render(); throw error; }
  } catch (error) { editStatus(error.message, true); }
}));
$("priced-replace").addEventListener("click",()=>action(()=>apply({kind:"replace-line-geometry",line:line().id,...JSON.parse($("priced-geometry").value)})));
$("priced-recost").addEventListener("click",async()=>{
  const button=$("priced-recost"),status=$("priced-status");button.disabled=true;
  try {
    const response=await fetch("/api/city-studies",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({city_slug:original.city,base_study_id:pricedRun,edit_bundle:editBundle()})});
    let job=await response.json();if(!response.ok)throw Error(job.error||"Another city calculation is running");
    const deadline=Date.now()+150000;
    while(job.state==="running"&&Date.now()<deadline){status.textContent="Recalculating the edited mapped network and delivery plan…";await new Promise(r=>setTimeout(r,1000));const r=await fetch("/api/city-studies/"+job.job_id,{cache:"no-store"});job=await r.json();if(!r.ok)throw Error(job.error||"City status unavailable");}
    if(job.state!=="completed")throw Error(job.error||"Calculation did not complete; artifacts retained");
    const s=job.summary;status.textContent=`${s.outline_acceptance==="accepted"?"Outline accepted":"Priced proposal requires revision"}: ${s.trainsets} trains, central installed US$${(s.installed_capital_usd.base/1e6).toFixed(1)}m. Requested service and any failures are retained.`;
    const links=$("priced-links");links.replaceChildren();
    for(const [file,label] of [["summary.json","Calculated prices and outcomes"],["delivery-plan.json","Production/construction schedule"],["business-drafts.json","Disabled business drafts"]]){const a=document.createElement("a");a.href=job.artifact_url+file;a.textContent=label;links.append(a);}
    const again=document.createElement("a");again.href=`?city=${encodeURIComponent(original.city)}&pricedRun=${job.job_id}`;again.textContent="Continue editing this calculated revision";links.append(again);
  } catch(error){status.textContent=error.message;}finally{button.disabled=false;}
});
try {
  const currentResponse = await fetch("../../design-engine/current/manifest.json", { cache: "no-store" });
  if (!currentResponse.ok) throw Error("Current engineering publication unavailable");
  const currentManifest = await currentResponse.json(), response = await fetch(base + "manifest.json", { cache: "no-store" });
  if (!response.ok) throw Error("Current planning publication unavailable");
  const manifestRaw = new Uint8Array(await response.arrayBuffer()), currentBound = currentManifest.files_sha256?.["planning/manifest.json"];
  if ((await sha256(manifestRaw)) !== currentBound) throw Error("Planning publication is not bound to current engineering evidence");
  manifest = JSON.parse(new TextDecoder().decode(manifestRaw));
  if (manifest.schema !== "osr-current-planning-inputs/1" || manifest.selection_id !== currentManifest.selection_id || ["engineering_accepted", "physical_accepted", "installed_mass_complete", "manufacturing_release", "operating_release"].some((key) => manifest[key] !== false)) throw Error("Current planning publication identity differs");
  index = await json("index.json");
  if (index.selection_id !== currentManifest.selection_id || index.city_count !== index.cities.length || ["candidate_id", "body_candidate_id", "support_component_id", "propulsion_component_id"].some((key) => index.selected_candidate?.[key] !== currentManifest[key])) throw Error("Current city index differs from selected candidate");
  $("city").replaceChildren(); for (const city of index.cities) option($("city"), city.city, city.label);
  const requestedCity = new URLSearchParams(location.search).get("city");
  const defaultCity = index.cities.some((city) => city.city === requestedCity)
    ? requestedCity
    : index.cities.some((city) => city.city === "baghdad") ? "baghdad" : index.cities[0].city;
  $("city").value = defaultCity;
  $("city").disabled = false; await loadCity();
} catch (error) { status("Planning held: " + error.message, true); }
