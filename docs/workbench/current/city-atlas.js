/* Source-bound city result viewer. No external tiles, libraries or network requests. */
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const palette = ["#176c9c", "#b04a40", "#527c30", "#8754a0", "#bd761d", "#168078", "#a34274"];
  const contextColours = { boundaries: "#7b8492", buildings: "#8c9290", earth: "#9b896a", landuse: "#7d9b69", places: "#875c78", roads: "#bb9b77", water: "#74adc7" };
  const contextNames = { boundaries: "Boundaries", buildings: "Buildings", earth: "Terrain", landuse: "Land use", places: "Places", roads: "Roads", water: "Water" };
  const finite = value => typeof value === "number" && Number.isFinite(value);
  const first = (...values) => values.find(value => value !== undefined && value !== null);
  const number = (value, digits = 0) => finite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: digits }) : "Not established";
  const unit = (value, suffix, digits = 0) => finite(value) ? number(value, digits) + " " + suffix : "Not established";
  const money = value => finite(value) ? (Math.abs(value) >= 1e6 ? "$" + number(value / 1e6, 2) + "m" : "$" + number(value)) : "Not established";
  const minutes = value => finite(value) ? unit(value / 60, "min", 1) : "Not established";
  const human = value => String(value).replaceAll("_", " ").replaceAll("-", " ");
  const short = value => typeof value === "string" ? value.slice(0, 16) : "Not supplied";
  function node(tag, cls, text) {
    const element = document.createElement(tag);
    if (cls) element.className = cls;
    if (text !== undefined) element.textContent = String(text);
    return element;
  }
  function svgNode(tag, attributes = {}) {
    const element = document.createElementNS(NS, tag);
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, String(value));
    return element;
  }
  function button(text, callback, cls = "") {
    const element = node("button", cls, text); element.type = "button";
    element.addEventListener("click", callback); return element;
  }
  function fact(parent, label, value) { parent.append(node("dt", "", label), node("dd", "", value)); }
  function validPosition(value) { return Array.isArray(value) && value.length >= 2 && value.slice(0, 2).every(finite); }
  function position(item) {
    if (!item) return null;
    return [item.coordinates, item.geometry?.coordinates,
      finite(item.lon) && finite(item.lat) ? [item.lon, item.lat] : null, item.platform_coordinates].find(validPosition) || null;
  }
  function stopId(stop) { return String(first(stop.id, stop.operational_stop_id, stop.stop_id, stop.station_id, stop.original_stop_id, "Unnamed stop")); }
  function base(value) { return finite(value) ? value : value?.base; }
  function scalar(value) {
    if (value === null || value === undefined) return "Not established";
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (finite(value)) return number(value, 3);
    if (typeof value === "string") return value;
    if (Array.isArray(value) && value.every(item => typeof item !== "object")) return value.map(scalar).join(" · ");
    if (typeof value === "object" && finite(value.base)) return ["low", "base", "high"].map(key => number(value[key], 2)).join(" / ");
    return null;
  }
  function readable(parent, value, depth = 0) {
    if (value === null || value === undefined) { parent.append(node("p", "atlas-note", "Not supplied in this result.")); return; }
    const simple = scalar(value);
    if (simple !== null) { parent.append(node("p", "", simple)); return; }
    if (depth > 3) { parent.append(node("p", "atlas-note", "Further nested records are retained in the downloadable result.")); return; }
    if (Array.isArray(value)) {
      const list = node("ul", "atlas-readable-list");
      for (const item of value.slice(0, 80)) { const li = node("li"); readable(li, item, depth + 1); list.append(li); }
      parent.append(list);
      if (value.length > 80) parent.append(node("p", "atlas-note", `${value.length - 80} additional records are retained in the result download.`));
    } else {
      const dl = node("dl", "atlas-facts");
      for (const [key, item] of Object.entries(value)) {
        const text = scalar(item);
        if (text !== null) fact(dl, human(key), text);
        else { const dt = node("dt", "", human(key)), dd = node("dd"); readable(dd, item, depth + 1); dl.append(dt, dd); }
      }
      parent.append(dl);
    }
  }
  function expandable(parent, title, value) {
    if (value === undefined || value === null) return;
    const details = node("details", "atlas-disclosure"); details.append(node("summary", "", title));
    const body = node("div", "atlas-disclosure-body"); readable(body, value); details.append(body); parent.append(details);
  }
  function featurePath(geometry, project, paths) {
    if (!geometry) return;
    const line = (coordinates, close) => {
      if (!Array.isArray(coordinates) || coordinates.length < 2 || !coordinates.every(validPosition)) return;
      paths[close ? "areas" : "lines"].push("M" + coordinates.map(point => project(point).join(",")).join("L") + (close ? "Z" : ""));
    };
    const point = coordinates => {
      if (!validPosition(coordinates)) return;
      const [x, y] = project(coordinates); paths.points.push(`M${x - 1.6},${y}a1.6,1.6 0 1 0 3.2,0a1.6,1.6 0 1 0 -3.2,0`);
    };
    switch (geometry.type) {
      case "Point": point(geometry.coordinates); break;
      case "MultiPoint": (geometry.coordinates || []).forEach(point); break;
      case "LineString": line(geometry.coordinates); break;
      case "MultiLineString": (geometry.coordinates || []).forEach(item => line(item)); break;
      case "Polygon": (geometry.coordinates || []).forEach(item => line(item, true)); break;
      case "MultiPolygon": (geometry.coordinates || []).forEach(polygon => polygon.forEach(item => line(item, true))); break;
      case "GeometryCollection": (geometry.geometries || []).forEach(item => featurePath(item, project, paths)); break;
      default: break;
    }
  }
  function render(packet, geometry, options = {}) {
    if (!packet || packet.schema !== "osr-city-atlas/1" || !Array.isArray(packet.lines)) throw Error("A source-bound osr-city-atlas/1 result is required");
    if (new Set(packet.lines.map(line => line.line_id)).size !== packet.lines.length) throw Error("Duplicate city line identities");
    const root = typeof options.container === "string" ? document.querySelector(options.container) : options.container || document.getElementById("city-atlas");
    if (!root) throw Error("City atlas container is missing");
    if (root._cityAtlas) root._cityAtlas.destroy();
    root.replaceChildren(); root.hidden = false; root.classList.add("city-atlas");
    const host = root.closest("#city-outline-results"); if (host) host.classList.add("city-atlas-active");
    const abort = new AbortController(), signal = abort.signal;
    const lines = packet.lines.map((line, index) => ({ ...line, colour: /^#[0-9a-f]{6}$/i.test(line.colour || line.color || "") ? line.colour || line.color : palette[index % palette.length] }));
    geometry = geometry || packet.geometry;
    const context = options.contextVerified === true ? options.context : null;
    let selected = lines[0]?.line_id, selectedStop = null, destroyed = false;
    const routePoints = lines.flatMap(line => (line.coordinates || []).filter(validPosition));
    for (const feature of geometry?.features || []) {
      if (feature.geometry?.type === "LineString") routePoints.push(...feature.geometry.coordinates.filter(validPosition));
      if (feature.geometry?.type === "Point" && validPosition(feature.geometry.coordinates)) routePoints.push(feature.geometry.coordinates);
    }
    if (!routePoints.length) throw Error("City result contains no displayable geographic coordinates");
    let west = Infinity, east = -Infinity, south = Infinity, north = -Infinity;
    for (const [lon, lat] of routePoints) { west = Math.min(west, lon); east = Math.max(east, lon); south = Math.min(south, lat); north = Math.max(north, lat); }
    const lonScale = 111320 * Math.max(.01, Math.cos((north + south) / 2 * Math.PI / 180));
    const widthM = Math.max(1, (east - west) * lonScale), heightM = Math.max(1, (north - south) * 111320);
    const projectionScale = Math.min(850 / widthM, 530 / heightM), left = (1000 - widthM * projectionScale) / 2, top = (640 - heightM * projectionScale) / 2;
    const project = point => [left + (point[0] - west) * lonScale * projectionScale, top + (north - point[1]) * 111320 * projectionScale];
    const initialView = { x: 0, y: 0, w: 1000, h: 640 }; let view = { ...initialView };
    const heading = node("div", "atlas-heading"), titleGroup = node("div");
    titleGroup.append(node("p", "eyebrow", "City atlas · calculated network"), node("h3", "atlas-title", `${packet.city?.name || "City"}${packet.city?.country ? ", " + packet.city.country : ""}`));
    const stage = node("span", "atlas-stage", packet.evidence?.outline_acceptance === "requires-revision"
      ? "Calculated proposal · requires revision" : "Analytical outline · physical approval pending");
    heading.append(titleGroup, stage); root.append(heading);
    const identity = packet.identity || {}, summary = packet.summary || {}, costs = packet.costs || {};
    root.append(node("p", "atlas-subtitle", `${human(identity.selected_alignment_kind || "Declared alignment")} · ${lines.length} lines · ${short(packet.packet_id)} result`));
    if (options.downloadUrl) {
      try {
        const url = new URL(options.downloadUrl, document.baseURI);
        if (["https:", "http:"].includes(url.protocol)) { const link = node("a", "atlas-download", "Download this source-bound result"); link.href = url.href; root.append(link); }
      } catch (_) { /* The visible result does not require a download URL. */ }
    }
    const localGIS = ["127.0.0.1", "localhost", "[::1]"].includes(location.hostname);
    if (localGIS && packet.city?.slug === "samawah" && !identity.workflow_evaluation_id) {
      const comparison = node("section", "atlas-revision-comparison"); comparison.id = "samawah-station-merge";
      comparison.append(node("h4", "atlas-section-title", "Compare the proposed station merge"));
      comparison.append(node("p", "atlas-note", "Recalculate the published network and the midpoint consolidation of the 79.977 m marker pair under the same vehicle and service assumptions."));
      const compare = button("Compare Samawah station merge", async () => {
        compare.disabled = true; result.replaceChildren();
        const read = async (url, options = {}) => {
          const response = await fetch(url, { ...options, signal }); const value = await response.json();
          if (!response.ok) throw Error(value.error || "The comparison request failed");
          return value;
        };
        const calculate = async (request, label) => {
          progress.textContent = `${label} · checking verified results`;
          let job = await read("/api/city-studies", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(request) });
          const reused = job.cache_hit === true; const deadline = performance.now() + 600000;
          while (["queued", "running"].includes(job.state) && performance.now() < deadline) {
            progress.textContent = job.state === "queued" ? `${label} · waiting for reserved resources` : `${label} · calculating`;
            await new Promise(resolve => setTimeout(resolve, 400));
            job = await read(`/api/city-studies/${job.job_id}`);
          }
          if (job.state !== "completed") throw Error(job.error || `${label} did not complete within its budget`);
          return { ...job, reused };
        };
        try {
          progress.textContent = "Preparing the source-bound station edit";
          const proposal = await read("/api/city-studies/scenarios/samawah-station-merge");
          const [before, after] = await Promise.all([calculate(proposal.baseline_request, "Published-marker control"), calculate(proposal.revised_request, "Midpoint consolidation")]);
          progress.textContent = "Comparing verified quantities and costs";
          const url = `/api/city-studies/comparisons/${before.job_id}/${after.job_id}`;
          const response = await read(url); const report = response.report;
          comparison.dataset.baselineJob = before.job_id; comparison.dataset.revisedJob = after.job_id;
          comparison.dataset.cacheReused = String(before.reused && after.reused);
          const table = node("table", "samawah-merge-metrics"), head = node("thead"), labels = node("tr");
          for (const title of ["Measure", "Before", "Proposed merge", "Change"]) labels.append(node("th", "", title));
          head.append(labels); table.append(head); const rows = node("tbody");
          const metric = (value, measure) => !finite(value) ? "Not established" : measure.unit === "USD" ? money(value) : number(value, 4);
          for (const measure of report.metrics) {
            const row = node("tr"); row.dataset.metric = measure.key;
            row.append(node("th", "", `${measure.label}${measure.unit ? ` (${measure.unit})` : ""}`));
            for (const field of ["before", "after", "delta"]) row.append(node("td", "", metric(measure[field], measure)));
            rows.append(row);
          }
          table.append(rows); const scroll = node("div", "atlas-table-scroll"); scroll.append(table); result.append(scroll);
          const costs = node("table", "samawah-merge-costs"), costHead = node("tr");
          for (const title of ["Cost scope", "Before: low / base / high", "After: low / base / high", "Base change"]) costHead.append(node("th", "", title));
          const costHeader = node("thead"); costHeader.append(costHead); costs.append(costHeader); const costRows = node("tbody");
          const cases = value => ["low", "base", "high"].map(key => money(value?.[key])).join(" / ");
          for (const [scope, values] of Object.entries(report.cost_scopes)) {
            const row = node("tr"); row.append(node("th", "", human(scope)), node("td", "", cases(values.before)), node("td", "", cases(values.after)), node("td", "", money(values.delta?.base))); costRows.append(row);
          }
          costs.append(costRows); const costScroll = node("div", "atlas-table-scroll"); costScroll.append(costs); result.append(node("h4", "atlas-section-title", "Fourteen cost scopes"), costScroll);
          const findings = node("details", "atlas-disclosure"); findings.append(node("summary", "", "Changed quantities, assumptions and unresolved inputs"));
          findings.append(node("pre", "atlas-comparison-details", JSON.stringify({ quantities: report.quantities, lines: report.lines, unresolved_inputs: report.unresolved_inputs }, null, 2))); result.append(findings);
          const trace = node("details", "atlas-disclosure"); trace.append(node("summary", "", "Design and result identities")); trace.append(node("pre", "atlas-comparison-details", JSON.stringify(report.identities, null, 2))); result.append(trace);
          const downloads = node("div", "atlas-comparison-downloads");
          for (const [label, href] of [["Download comparison", url], ["Project integration holds", `/api/city-studies/projects/${before.job_id}/${after.job_id}`], ["Door module research proposal", "/api/v07/door-module"], ["Before dossier", `/api/city-studies/${before.job_id}/artifacts/result.json`], ["Revised dossier", `/api/city-studies/${after.job_id}/artifacts/result.json`], ["Revised delivery draft", `/api/city-studies/${after.job_id}/artifacts/delivery-plan.json`]]) {
            const link = node("a", "atlas-download", label); link.href = href; link.download = label.toLowerCase().replaceAll(" ", "-") + ".json"; downloads.append(link);
          }
          result.append(downloads);
          progress.textContent = `Comparison complete · ${before.reused && after.reused ? "both verified calculations reused" : "calculated and verified"}`;
        } catch (error) { if (!destroyed) progress.textContent = `Unable to compare: ${error.message}`; }
        finally { compare.disabled = false; }
      });
      compare.id = "samawah-merge-compare";
      const progress = node("p", "atlas-note", "The original mapped markers and published results are preserved."); progress.id = "samawah-merge-status"; progress.setAttribute("aria-live", "polite");
      const result = node("div", "atlas-comparison-results"); comparison.append(compare, progress, result);
      const doorPanel = node("section", "atlas-door-module"); doorPanel.id = "samawah-door-module";
      const doorStatus = node("p", "atlas-note"); const doorDetails = node("div");
      const openDoor = node("button", "", "Open door operator manufacturing proposal"); openDoor.id = "samawah-door-open";
      openDoor.addEventListener("click", async () => {
        openDoor.disabled = true; doorStatus.textContent = "Loading the candidate-linked module…";
        try {
          const response = await fetch("/api/v07/door-module", {signal}); const module = await response.json();
          if (!response.ok) throw Error(module.reason || module.error || "Module unavailable");
          if (destroyed) return;
          doorDetails.replaceChildren(); doorPanel.dataset.moduleId = module.module_id;
          doorDetails.append(node("h4", "", "Door operator manufacturing and maintenance"));
          const quantities = Object.values(module.assembly_quantities);
          doorDetails.append(node("p", "", `${quantities.reduce((n, q) => n + q.distinct_parts, 0)} part types · ${quantities.reduce((n, q) => n + q.pieces_per_opening, 0)} pieces per opening · ${module.opening_count_per_train} openings per train`));
          doorDetails.append(node("p", "atlas-note", `Known gross stock and allowance subtotal: ${module.nominal_mass.base.known_subtotal_kg_per_opening.toFixed(3)} kg/opening. Installed mass and centre of gravity remain unknown.`));
          doorStatus.textContent = "Research child proposal · installation, approved fits and inspection evidence remain open";
          doorDetails.append(node("p", "atlas-note", `Module candidate ${module.candidate_id.slice(0, 12)} descends from corridor reference ${module.parent_candidate_id.slice(0, 12)}. Corridor fleet and cost results do not transfer to this child.`));
          const label = node("label", "", "Inspect a part and its removal route "); const select = node("select"); select.id = "samawah-door-part";
          for (const part of module.parts) { const option = node("option", "", part.name); option.value = part.id; select.append(option); }
          label.append(select); doorDetails.append(label); const detail = node("div", "atlas-door-part"); doorDetails.append(detail);
          const showPart = () => {
            const part = module.parts.find(p => p.id === select.value); detail.replaceChildren();
            detail.append(node("p", "", `${part.quantity_per_opening} per opening · ${part.quantity_per_train} per train · ${part.make_buy === "buy-qualified" ? "Purchase proposal; supplier qualification required" : "Proposed " + human(part.make_buy)}`));
            detail.append(node("h5", "", "Manufacturing route")); const route = node("ol");
            for (const operation of part.manufacturing) route.append(node("li", "", operation)); detail.append(route);
            detail.append(node("p", "", `Fit and tolerance basis: ${part.tolerance_and_fits}`));
            detail.append(node("h5", "", "Inspection and QA")); const inspections = node("ul");
            for (const check of part.inspection_plan) inspections.append(node("li", "", `${check.criterion} — approved limit and observed result required`)); detail.append(inspections);
            detail.append(node("h5", "", "Removal and maintenance"), node("p", "", part.maintenance_removal), node("p", "atlas-note", part.maintenance_plan.interval_basis));
            const trace = node("details", "atlas-disclosure"); trace.append(node("summary", "", "Part source identity"), node("p", "", part.component_definition_id)); detail.append(trace);
          };
          select.addEventListener("change", showPart); showPart();
          const missing = node("details", "atlas-disclosure"); missing.append(node("summary", "", "Evidence needed for this module")); const list = node("ul");
          for (const finding of module.unresolved_inputs) list.append(node("li", "", `${finding.needed}. Affects: ${finding.affects.join(", ")}.`)); missing.append(list); doorDetails.append(missing);
          const link = node("a", "atlas-download", "Download source-bound module package"); link.href = "/api/v07/door-module"; link.download = "door-module.json"; doorDetails.append(link);
        } catch (error) { if (!destroyed) doorStatus.textContent = `Unable to open module: ${error.message}`; }
        finally { openDoor.disabled = false; }
      });
      doorPanel.append(openDoor, doorStatus, doorDetails); comparison.append(doorPanel); root.append(comparison);
    }
    const studyId = options.studyId || /^\/api\/city-atlas\/study\/([a-f0-9]{32})$/.exec(options.downloadUrl || "")?.[1];
    if (localGIS && (!packet.identity?.workflow_evaluation_id || /^[a-f0-9]{32}$/.test(studyId || "")) && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(packet.city?.slug || "") && /^[a-f0-9]{64}$/.test(packet.packet_id || "")) {
      const gis = node("a", "atlas-download", "Download editable RustGIS project and source tables");
      gis.href = studyId ? `/api/rustgis/study/${studyId}/${packet.packet_id}.zip` : `/api/rustgis/${packet.city.slug}/${packet.packet_id}.zip`;
      gis.download = `${packet.city.slug}-rustgis.zip`; root.append(gis);
      const panel = node("details", "atlas-disclosure"), form = node("form", "atlas-native-import");
      panel.append(node("summary", "", "Import native GIS edits and recalculate"));
      form.append(node("p", "atlas-note", "Upload the edited .rgis from this export. Routes, stations and declared service fields become a new priced outline; published results are preserved. Embedded coordinates must remain WGS84 longitude/latitude."));
      const input = (title, name, type, value, maximum) => {
        const label = node("label", "", title), field = node("input");field.name = name;field.type = type;field.required = true;
        if (value) field.value = value;if (maximum) field.maxLength = maximum;label.append(field);form.append(label);return field;
      };
      const file = input("Edited native project", "project", "file");file.accept = ".rgis,application/json";
      const actor = input("Planning author", "actor", "text", "", 150);
      const reason = input("Reason for this change", "reason", "text", "Native GIS route/station revision", 1000);
      const submit = node("button", "", "Import and recalculate");submit.type = "submit";
      const progress = node("p", "atlas-note");progress.setAttribute("role", "status");form.append(submit, progress);panel.append(form);root.append(panel);
      form.addEventListener("submit", async event => {
        event.preventDefault();submit.disabled = true;
        try {
          const upload = file.files?.[0];if (!upload || !/\.rgis$/i.test(upload.name) || upload.size > 32 * 1024 * 1024) throw Error("Choose one .rgis JSON project no larger than 32 MiB");
          const query = new URLSearchParams({actor: actor.value, reason: reason.value, data_crs: "EPSG:4326"});
          if (studyId) query.set("base_study_id", studyId);
          progress.textContent = "Checking native geometry and its source base…";
          const response = await fetch(`/api/rustgis/import/${packet.city.slug}/${packet.packet_id}?${query}`, {method: "POST", headers: {"Content-Type": "application/json"}, body: upload, signal});
          const imported = await response.json();if (!response.ok) throw Error(imported.error || "Native revision was refused");
          if (imported.state === "no-op") {progress.textContent = "Geometry and service are unchanged. Styling/camera edits require no new railway calculation.";return;}
          let job = imported.job;const deadline = Date.now() + 600000;
          while (["queued", "running"].includes(job?.state) && Date.now() < deadline) {
            progress.textContent = job?.state === "queued" ? "Waiting for available CPU, memory and disk reservations…" : "Recalculating route quantities, service, fleet, all costs and delivery drafts…";
            await new Promise(resolve => setTimeout(resolve, 1000));
            const poll = await fetch(`/api/city-studies/${job.job_id}`, {signal});job = await poll.json();
            if (!poll.ok) throw Error(job.error || "Calculation status unavailable");
          }
          if (job?.state !== "completed") throw Error(job?.error || "Calculation did not finish within its budget; inputs and logs remain retained");
          if (typeof options.onImported === "function") await options.onImported(job);
          else {
            const update = await fetch(`/api/city-atlas/study/${job.job_id}`, {signal});const revised = await update.json();
            if (!update.ok || revised.identity?.workflow_evaluation_id !== job.summary?.evaluation_id || revised.city?.slug !== packet.city.slug) throw Error("Revised map and calculation identities differ");
            render(revised, null, {...options, container: root, studyId: job.job_id, downloadUrl: `/api/city-atlas/study/${job.job_id}`});
          }
        } catch (error) {if (!destroyed) progress.textContent = `Unable to import: ${error.message}`;}
        finally {submit.disabled = false;}
      }, {signal});
    }
    const metrics = node("div", "atlas-metrics");
    const summaryRoute = first(summary.route_km, finite(summary.route_m) ? summary.route_m / 1000 : null);
    const routeKm = finite(summaryRoute) ? summaryRoute : lines.every(line => finite(line.route_m)) ? lines.reduce((sum, line) => sum + line.route_m, 0) / 1000 : null;
    const totalFleet = first(summary.trainsets, summary.total_trainsets, packet.resources?.total_trainsets);
    for (const [label, value] of [["Mapped route", unit(routeKm, "km", 1)], ["Operational stations", number(summary.operational_station_complexes)], ["Fleet including reserve", unit(totalFleet, "trainsets")], ["Installed capital · base", money(base(costs.installed_capital_usd))], ["Whole-life NPV · base", money(base(costs.whole_life_npv_usd))]]) {
      const card = node("div", "atlas-metric"); card.append(node("span", "", label), node("strong", "", value)); metrics.append(card);
    }
    root.append(metrics);
    const layout = node("div", "atlas-layout"), mapColumn = node("div", "atlas-map-column"), mapFrame = node("div", "atlas-map-frame");
    const svg = svgNode("svg", { viewBox: "0 0 1000 640", tabindex: "0", role: "group", "aria-label": "Interactive city network. Drag to pan. Arrow keys pan; plus and minus zoom; Home fits the network." });
    svg.classList.add("atlas-map");
    const svgTitle = svgNode("title"); svgTitle.textContent = `${packet.city?.name || "City"} calculated railway network`; svg.append(svgTitle);
    const contextGroup = svgNode("g", { "aria-hidden": "true" }), originalsGroup = svgNode("g", { "aria-hidden": "true" }), connectorsGroup = svgNode("g", { "aria-hidden": "true" }), routesGroup = svgNode("g"), stationsGroup = svgNode("g"), labelsGroup = svgNode("g", { "aria-hidden": "true" });
    svg.append(contextGroup, originalsGroup, connectorsGroup, routesGroup, stationsGroup, labelsGroup); mapFrame.append(svg);
    const controls = node("div", "atlas-map-controls"); controls.setAttribute("aria-label", "Map controls");
    controls.append(button("+", () => zoom(.7), "atlas-zoom"), button("−", () => zoom(1 / .7), "atlas-zoom"), button("Fit network", fit));
    controls.children[0].setAttribute("aria-label", "Zoom in"); controls.children[1].setAttribute("aria-label", "Zoom out"); mapFrame.append(controls);
    const northArrow = node("div", "atlas-north", "↑\nN"); northArrow.setAttribute("aria-label", "North is up"); mapFrame.append(northArrow);
    const scale = node("div", "atlas-scale"), scaleBar = node("div", "atlas-scale-bar"), scaleLabel = node("span"); scale.append(scaleBar, scaleLabel); mapFrame.append(scale);
    const mapHint = node("p", "atlas-map-hint", "Drag to pan · + / − to zoom · select a route or station");
    mapColumn.append(mapFrame, mapHint);
    const layers = node("div", "atlas-layers");
    const layerToggle = (label, group, checked) => {
      const wrap = node("label"), input = node("input"); input.type = "checkbox"; input.checked = checked; group.style.display = checked ? "" : "none";
      input.addEventListener("change", () => { group.style.display = input.checked ? "" : "none"; }); wrap.append(input, document.createTextNode(label)); layers.append(wrap);
    };
    if (context?.layers && typeof context.layers === "object") {
      for (const [key, features] of Object.entries(context.layers)) {
        if (!Array.isArray(features) || features.length > 50000 || !/^[a-z0-9_-]{1,80}$/.test(key)) continue;
        const group = svgNode("g"), paths = { areas: [], lines: [], points: [] };
        for (const feature of features) featurePath(feature.geometry, project, paths);
        for (const [kind, values] of Object.entries(paths)) if (values.length) {
          group.append(svgNode("path", { d: values.join(""), stroke: contextColours[key] || "#8c9290", fill: kind === "lines" ? "none" : contextColours[key] || "#8c9290", "fill-opacity": kind === "areas" ? ".25" : ".7", "stroke-width": key === "roads" ? ".7" : ".8", "vector-effect": "non-scaling-stroke", "fill-rule": "evenodd" }));
        }
        contextGroup.append(group); layerToggle(contextNames[key] || human(key), group, ["roads", "water", "places", "landuse"].includes(key));
      }
    }
    layerToggle("Original / access markers", originalsGroup, true); layerToggle("Platforms / access walks", connectorsGroup, true); layerToggle("Station names", labelsGroup, false);
    mapColumn.append(layers);
    const attribution = node("div", "atlas-attribution");
    if (context) {
      attribution.append(document.createTextNode("Geographic context · source bytes verified by the Workbench. "));
      for (const source of context.attribution || []) {
        if (typeof source?.name !== "string") continue;
        let element = node("span", "", source.name);
        try { const url = new URL(source.url); if (["https:", "http:"].includes(url.protocol)) { element = node("a", "", source.name); element.href = url.href; element.target = "_blank"; element.rel = "noopener noreferrer"; } } catch (_) { /* Attribution name remains visible. */ }
        attribution.append(element, document.createTextNode(source.license ? ` · ${source.license}. ` : ". "));
      }
    } else attribution.textContent = "Verified geographic context is unavailable for this result. Route and station coordinates remain visible.";
    attribution.append(node("span", "", " Geographic context is not survey, clearance, demand or operating evidence.")); mapColumn.append(attribution);
    const sidebar = node("aside", "atlas-sidebar"), lineNav = node("nav", "atlas-line-nav"); lineNav.setAttribute("aria-label", "Select a line");
    sidebar.append(node("h4", "", "Explore the network"), lineNav);
    const lineButtons = new Map(), routeElements = [], markers = [], labelElements = [];
    const inspector = node("section", "atlas-inspector"); inspector.setAttribute("aria-live", "polite");
    const stationLabel = node("label", "atlas-station-picker", "Inspect a station"), stationSelect = node("select"); stationSelect.setAttribute("aria-label", "Station on the selected line"); stationLabel.append(stationSelect);
    sidebar.append(stationLabel, inspector); layout.append(mapColumn, sidebar); root.append(layout);
    function activation(element, callback) {
      element.addEventListener("click", event => { if (!dragMoved) callback(event); });
      element.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); callback(event); } });
    }
    function stopRows(line) {
      const rows = line.station_complexes?.length ? line.station_complexes : line.operational_stops || [];
      return rows.map((stop, index) => ({ ...stop, _key: String(first(stop.id, stop.operational_stop_id, stop.complex_id, stop.stop_id, index)), _position: position(stop) }));
    }
    function marker(point, line, stop, original) {
      if (!point) return;
      const [x, y] = project(point), circle = svgNode("circle", { cx: x, cy: y, r: original ? 3 : 4.3, fill: original ? "#f6f4ee" : "#fff", stroke: original ? "#65726c" : line.colour, "stroke-width": original ? 1.1 : 2, "vector-effect": "non-scaling-stroke" });
      if (original) { circle.classList.add("atlas-original-marker"); originalsGroup.append(circle); }
      else {
        circle.classList.add("atlas-station"); circle.setAttribute("tabindex", "0"); circle.setAttribute("role", "button"); circle.setAttribute("aria-label", `${line.line_id}: ${first(stop.name, stopId(stop))}`);
        activation(circle, () => selectLine(line.line_id, stop._key)); stationsGroup.append(circle);
      }
      const title = svgNode("title"); title.textContent = `${original ? "Original / access: " : "Operational platform: "}${first(stop.name, stopId(stop))}`; circle.append(title);
      markers.push({ element: circle, radius: original ? 3 : 4.3, line: line.line_id, stop: stop._key, original });
      if (!original) {
        const label = svgNode("text", { x: x + 8, y: y - 7 }); label.textContent = first(stop.name, stopId(stop)); label.classList.add("atlas-station-label"); labelsGroup.append(label); labelElements.push({ element: label, x, y });
      }
    }
    for (const line of lines) {
      const lineButton = button("", () => selectLine(line.line_id), "atlas-line-button"), swatch = node("span", "atlas-swatch"); swatch.style.background = line.colour;
      const text = node("span"); text.append(node("strong", "", line.name || line.line_id), node("small", "", `${human(line.shape || "line")} · ${unit(first(line.metrics?.headway_s, line.requirements?.headway_s), "s")}`));
      lineButton.append(swatch, text); lineNav.append(lineButton); lineButtons.set(line.line_id, lineButton);
      let coordinates = line.coordinates;
      if (!Array.isArray(coordinates)) coordinates = (geometry?.features || []).find(feature => feature.geometry?.type === "LineString" && [feature.properties?.line_id, feature.properties?.name].includes(line.line_id))?.geometry.coordinates;
      if (Array.isArray(coordinates) && coordinates.length > 1 && coordinates.every(validPosition)) {
        const d = "M" + coordinates.map(point => project(point).join(",")).join("L");
        const halo = svgNode("path", { d, fill: "none", stroke: "#fff", "stroke-width": 7, "vector-effect": "non-scaling-stroke", "aria-hidden": "true" });
        const path = svgNode("path", { d, fill: "none", stroke: line.colour, "stroke-width": 3.5, "vector-effect": "non-scaling-stroke", tabindex: "0", role: "button", "aria-label": `Inspect ${line.name || line.line_id}` });
        path.classList.add("atlas-route"); const title = svgNode("title"); title.textContent = line.name || line.line_id; path.append(title); activation(path, () => selectLine(line.line_id)); routesGroup.append(halo, path); routeElements.push({ element: path, halo, line: line.line_id });
      }
      for (const stop of line.original_stops || []) marker(position(stop), line, stop, true);
      for (const stop of stopRows(line)) {
        marker(stop._position, line, stop, false);
        for (const coordinates of stop.platform_coordinates || []) {
          if (!Array.isArray(coordinates) || coordinates.length < 2 || !coordinates.every(validPosition)) continue;
          const platform = svgNode("path", { d: "M" + coordinates.map(point => project(point).join(",")).join("L"), stroke: line.colour, fill: "none", "stroke-width": 7, "stroke-opacity": ".7", "vector-effect": "non-scaling-stroke" });
          const title = svgNode("title"); title.textContent = `Operational platform envelope: ${stopId(stop)}`; platform.append(title); connectorsGroup.append(platform);
        }
        for (const original of stop.original_markers || []) marker(position(original), line, original, true);
        for (const connector of stop.access_connectors || []) {
          const from = connector.from_coordinates, to = connector.to_coordinates;
          if (!validPosition(from) || !validPosition(to)) continue;
          const path = svgNode("path", { d: "M" + project(from).join(",") + "L" + project(to).join(","), fill: "none", stroke: line.colour, "stroke-width": 1.4, "stroke-dasharray": "4 3", "vector-effect": "non-scaling-stroke" });
          const title = svgNode("title"); title.textContent = `Access connector: ${unit(connector.along_route_connector_m, "m", 1)} along route; straight map link is illustrative`; path.append(title); connectorsGroup.append(path);
        }
      }
    }
    // Original routes remain context, never inherit selected-line service metrics.
    for (const feature of geometry?.features || []) {
      const kind = String(first(feature.properties?.kind, feature.properties?.alignment_kind, ""));
      if (feature.geometry?.type !== "LineString" || !/original/.test(kind)) continue;
      const paths = { lines: [], areas: [], points: [] }; featurePath(feature.geometry, project, paths);
      if (paths.lines.length) originalsGroup.prepend(svgNode("path", { d: paths.lines.join(""), stroke: "#78837e", fill: "none", "stroke-width": 1.7, "stroke-dasharray": "6 4", "vector-effect": "non-scaling-stroke" }));
    }
    const legend = node("p", "atlas-legend", "● Operational platform   ○ Original / access marker   ┄ Added walk link (illustrative)"); mapColumn.insertBefore(legend, layers);
    const serviceHeading = node("h4", "atlas-section-title", "Service by line"), serviceScroll = node("div", "atlas-table-scroll"), table = node("table", "atlas-service-table");
    const caption = node("caption", "", "One calculated candidate · demand and usable capacity in passengers / hour / direction"); table.append(caption);
    const thead = node("thead"), headerRow = node("tr");
    for (const text of ["Line", "Demand", "Usable / offered capacity", "Headway", "Journey", "Fleet", "Traction work / day"]) headerRow.append(node("th", "", text)); thead.append(headerRow); table.append(thead);
    const tbody = node("tbody");
    for (const line of lines) {
      const m = line.metrics || {}, tr = node("tr"), td = node("td"), pick = button(line.name || line.line_id, () => { selectLine(line.line_id); root.scrollIntoView({ behavior: "smooth", block: "start" }); }, "atlas-table-pick"); pick.style.color = line.colour; td.append(pick); tr.append(td);
      for (const value of [number(m.peak_demand_pphpd), `${number(m.planning_usable_capacity_pphpd)} / ${number(m.capacity_pphpd)}`, unit(m.headway_s, "s"), minutes(m.one_way_s), number(m.total_trainsets), unit(m.mechanical_traction_kwh_per_day, "kWh mechanical", 0)]) tr.append(node("td", "", value)); tbody.append(tr);
    }
    table.append(tbody); serviceScroll.append(table); root.append(serviceHeading, serviceScroll);
    root.append(node("p", "atlas-note", "Offered capacity is the nominal places calculation; usable capacity includes declared occupancy and availability assumptions. Traction work is mechanical energy, before electrical losses and auxiliary loads. Missing values remain unestablished. Shared project costs are not allocated to lines without a stated basis."));
    const lower = node("div", "atlas-lower"), costSection = node("section"), evidenceSection = node("section");
    costSection.append(node("h4", "", "Cost scope and uncertainty"));
    const costTable = node("table", "atlas-cost-table"), costHead = node("tr");
    for (const text of ["Whole-life scope", "Low", "Base", "High"]) costHead.append(node("th", "", text)); const costThead = node("thead"); costThead.append(costHead); costTable.append(costThead);
    const costBody = node("tbody"); for (const [scope, value] of Object.entries(costs.scope_totals_usd || {})) { const row = node("tr"); row.append(node("th", "", human(scope))); for (const key of ["low", "base", "high"]) row.append(node("td", "", money(value?.[key]))); costBody.append(row); } costTable.append(costBody);
    const costScroll = node("div", "atlas-table-scroll"); costScroll.append(costTable); costSection.append(costScroll);
    const reassessment = costs.capital_lines?.find(row => row.key === "revised-alignment-row-access-and-crossing-risk");
    if (reassessment) {
      const reserve = node("section", "atlas-disclosure-body"), quantities = reassessment.quantity || {}, facts = node("dl", "atlas-facts");
      reserve.append(node("h4", "", "Alignment reassessment reserve · already included"));
      fact(facts, "Reserve · low / base / high", ["low", "base", "high"].map(key => money(reassessment.costs_usd?.[key])).join(" / "));
      fact(facts, "Corridor under reassessment", unit(finite(quantities.changed_route_m) ? quantities.changed_route_m / 1000 : null, "km", 3));
      fact(facts, "Right-of-way area allowance", unit(quantities.additional_row_area_m2, "m²"));
      fact(facts, "Additional access walkway", unit(quantities.additional_access_walkway_m, "m", 1));
      fact(facts, "Unverified bridge-length hypothesis", unit(quantities.unverified_bridge_route_m_hypothesis, "m", 1));
      reserve.append(facts, node("p", "atlas-note", "The model marks an edited line's full length for site, right-of-way and crossing reassessment. These quantities and the reserve include earlier alignment assumptions. This allowance is already included in construction totals; the incremental cost of the geometry change remains unestablished pending site evidence."));
      expandable(reserve, "Reserve calculation and assumptions", reassessment); costSection.append(reserve);
    }
    evidenceSection.append(node("h4", "", "Evidence and next decisions"), node("p", "atlas-evidence-warning", "Calculated planning evidence. Hardware, operation and procurement release remain pending."));
    const idList = node("dl", "atlas-facts atlas-identities");
    for (const [label, value] of [["Physical research configuration", identity.research_configuration_id], ["Service evaluation", identity.service_evaluation_id], ["Cost evaluation", identity.cost_evaluation_id], ["Alignment identity", identity.selected_alignment_id], ["Selection identity", identity.selection_id]]) if (value) fact(idList, label, short(value)); evidenceSection.append(idList);
    expandable(evidenceSection, "Missing evidence and qualification work", packet.missing_evidence);
    expandable(evidenceSection, "Demand, site and pricing assumptions", packet.assumptions);
    expandable(evidenceSection, "Civil quantities and assumptions", packet.civil);
    expandable(evidenceSection, "Delivery resources", packet.resources);
    expandable(evidenceSection, "Source identities", { ...packet.sources, ...identity, map_context: options.contextSource || null });
    const finance = node("details", "atlas-disclosure atlas-finance"); finance.append(node("summary", "", "Explore a fare scenario"));
    const financeBody = node("div", "atlas-disclosure-body"); financeBody.append(node("p", "atlas-note", "Enter annual paid trips and the average fare received. Peak line demand does not establish network ridership. Values below are a user scenario, separate from the calculated candidate."));
    const financeForm = node("form", "atlas-finance-form"), tripsLabel = node("label", "", "Annual paid trips"), fareLabel = node("label", "", "Average fare received · US$");
    const trips = node("input"), fare = node("input");
    for (const input of [trips, fare]) { input.type = "number"; input.min = "0"; input.required = true; }
    trips.step = "1"; fare.step = ".01"; tripsLabel.append(trips); fareLabel.append(fare);
    const calc = node("button", "atlas-back", "Calculate fare and whole-life scenario"); calc.type = "submit";
    const financeResult = node("p", "atlas-note", "Annual paid trips and average fare are required to calculate revenue."); financeResult.setAttribute("aria-live", "polite");
    financeForm.append(tripsLabel, fareLabel, calc); financeBody.append(financeForm, financeResult); finance.append(financeBody); costSection.append(finance);
    financeForm.addEventListener("submit", event => { event.preventDefault(); const annual = Number(trips.value), received = Number(fare.value);
      if (!finite(annual) || !finite(received) || annual < 0 || received < 0 || !trips.value || !fare.value) return;
      const revenue = annual * received, policy = packet.assumptions?.policy || {};
      const years = policy.accounting_horizon_years, rate = policy.real_discount_rate;
      financeResult.textContent = `${money(revenue)} gross fare revenue / year. `;
      if (finite(years) && years > 0 && finite(rate) && rate >= 0 && finite(base(costs.whole_life_npv_usd))) {
        const factor = rate === 0 ? years : (1 - Math.pow(1 + rate, -years)) / rate;
        const balance = revenue * factor - base(costs.whole_life_npv_usd);
        financeResult.textContent += `${years} years at ${number(rate * 100, 2)}% real: ${money(balance)} discounted fare-only balance against the modelled whole-life costs. `;
        if (annual > 0) {
          const fares = ["low", "base", "high"].map(c => (costs.whole_life_npv_usd[c] / (annual * factor)).toLocaleString(undefined, {style:"currency",currency:"USD",maximumFractionDigits:2}));
          financeResult.textContent += `Whole-life cost-covering average fare: ${fares.join(" / ")} (low / base / high cost cases). `;
        }
        financeResult.textContent += "Assumes unchanged annual paid trips and real fare from the first operating year; funding timing, tax, debt, demand changes and non-fare benefits require their own scenario. These sensitivity cases are not confidence intervals.";
      } else financeResult.textContent += "A declared cost horizon and discount rate are required for a whole-life comparison.";
    });
    lower.append(costSection, evidenceSection); root.append(lower);
    function updateInspector() {
      inspector.replaceChildren(); const line = lines.find(item => item.line_id === selected); if (!line) return;
      const m = line.metrics || {}, stops = stopRows(line), stop = stops.find(item => item._key === selectedStop);
      inspector.append(node("p", "atlas-inspector-kicker", stop ? "Station and access" : "Selected line"), node("h4", "", stop ? first(stop.name, stopId(stop)) : line.name || line.line_id));
      const dl = node("dl", "atlas-facts");
      if (stop) {
        fact(dl, "Line", line.name || line.line_id); fact(dl, "Operational chainage", unit(first(stop.chainage_m, stop.platform_chainage_m), "m", 1));
        fact(dl, "Original stop references", (stop.original_stop_ids || stop.member_stop_ids || []).join(" · ") || "See access records");
        fact(dl, "Dwell", unit(first(stop.dwell_s, line.service?.stop_dwell_s?.[stops.indexOf(stop)]), "s"));
        if (stop._position) fact(dl, "Platform longitude / latitude", stop._position.map(value => value.toFixed(5)).join(", "));
        inspector.append(dl); expandable(inspector, "Access connectors and station requirements", stop);
        inspector.append(button("Back to line", () => selectLine(line.line_id), "atlas-back"));
      } else {
        for (const [label, value] of [["Route length", unit(line.route_m / 1000, "km", 2)], ["Demand", unit(m.peak_demand_pphpd, "pphpd")], ["Usable capacity", unit(m.planning_usable_capacity_pphpd, "pphpd")], ["Offered capacity", unit(m.capacity_pphpd, "places/h/direction")], ["Headway", unit(m.headway_s, "s")], [line.shape === "ring" ? "Circuit journey" : "One-way journey", minutes(m.one_way_s)], ["Round trip / cycle", minutes(m.round_trip_s)], ["Active + reserve fleet", `${number(m.active_trainsets)} + ${number(m.spare_trainsets)} trainsets`], ["Train distance / day", unit(m.train_km_per_day, "km")], ["Traction work / day", unit(m.mechanical_traction_kwh_per_day, "kWh mechanical")], ["Total electrical energy / day", unit(first(m.total_electrical_energy_kwh_per_day, m.energy_kwh_per_day, m.daily_energy_kwh), "kWh")]]) fact(dl, label, value);
        inspector.append(dl);
        const demand = m.peak_demand_pphpd, capacity = m.planning_usable_capacity_pphpd;
        if (finite(demand) && finite(capacity)) inspector.append(node("p", capacity >= demand ? "atlas-capacity-pass" : "atlas-capacity-hold", capacity >= demand ? `${number(capacity - demand)} pphpd calculated capacity margin` : `${number(demand - capacity)} pphpd demand exceeds usable capacity`));
        expandable(inspector, "Energy components and accounting limits", {
          mechanical_traction_kwh_per_day: m.mechanical_traction_kwh_per_day,
          auxiliary_load_kwh_per_day: m.auxiliary_load_kwh_per_day,
          auxiliary_grid_kwh_per_day: m.auxiliary_grid_kwh_per_day,
          total_electrical_energy_kwh_per_day: m.total_electrical_energy_kwh_per_day,
          interpretation: "Mechanical traction work is not grid electricity. A total electrical value requires a supported drive efficiency and all declared loads."
        });
        expandable(inspector, "Propulsion hypothesis", line.propulsion_hypothesis);
        expandable(inspector, "Service assumptions and design", { requirements: line.requirements, design: line.design });
      }
    }
    function selectLine(id, stop = null) {
      if (!lines.some(line => line.line_id === id)) return;
      selected = id; selectedStop = stop;
      for (const [key, element] of lineButtons) { element.classList.toggle("is-selected", key === id); element.setAttribute("aria-pressed", String(key === id)); }
      for (const item of routeElements) { item.element.classList.toggle("is-muted", item.line !== id); item.element.classList.toggle("is-selected", item.line === id); item.element.setAttribute("aria-pressed", String(item.line === id)); item.halo.style.opacity = item.line === id ? "1" : ".55"; }
      for (const item of markers) if (!item.original) item.element.classList.toggle("is-selected", item.line === id && item.stop === stop);
      stationSelect.replaceChildren(); const placeholder = node("option", "", "Choose a station…"); placeholder.value = ""; stationSelect.append(placeholder);
      for (const row of stopRows(lines.find(line => line.line_id === id))) { const option = node("option", "", first(row.name, stopId(row))); option.value = row._key; stationSelect.append(option); }
      stationSelect.value = stop || ""; updateInspector();
    }
    stationSelect.addEventListener("change", () => selectLine(selected, stationSelect.value || null));
    function updateView() {
      svg.setAttribute("viewBox", `${view.x} ${view.y} ${view.w} ${view.h}`);
      const ratio = view.w / 1000;
      for (const item of markers) item.element.setAttribute("r", item.radius * ratio);
      for (const item of labelElements) { item.element.setAttribute("font-size", 12 * ratio); item.element.setAttribute("x", item.x + 8 * ratio); item.element.setAttribute("y", item.y - 7 * ratio); }
      const rect = svg.getBoundingClientRect();
      const pixelsPerUnit = Math.max(.001, Math.min(rect.width / view.w, rect.height / view.h));
      const metresPerPixel = 1 / pixelsPerUnit / projectionScale;
      const desired = 100 * metresPerPixel, magnitude = 10 ** Math.floor(Math.log10(desired));
      const length = [5, 2, 1].map(value => value * magnitude).find(value => value <= desired) || magnitude / 2;
      scaleBar.style.width = `${length / metresPerPixel}px`; scaleLabel.textContent = length >= 1000 ? `${number(length / 1000, 1)} km` : `${number(length)} m`;
    }
    function fit() { view = { ...initialView }; updateView(); }
    function zoom(factor, cx = view.x + view.w / 2, cy = view.y + view.h / 2) {
      const width = Math.max(35, Math.min(6000, view.w * factor)), ratio = width / view.w;
      view = { x: cx - (cx - view.x) * ratio, y: cy - (cy - view.y) * ratio, w: width, h: view.h * ratio }; updateView();
    }
    let drag = null, dragMoved = false;
    svg.addEventListener("pointerdown", event => { if (event.button !== 0) return; dragMoved = false; drag = { x: event.clientX, y: event.clientY, view: { ...view } }; }, { signal });
    svg.addEventListener("pointermove", event => {
      if (!drag) return; const rect = svg.getBoundingClientRect(), dx = event.clientX - drag.x, dy = event.clientY - drag.y;
      if (Math.abs(dx) + Math.abs(dy) > 4) dragMoved = true;
      if (dragMoved) { const pixelsPerUnit = Math.max(.001, Math.min(rect.width / drag.view.w, rect.height / drag.view.h));
        svg.setPointerCapture?.(event.pointerId); view.x = drag.view.x - dx / pixelsPerUnit; view.y = drag.view.y - dy / pixelsPerUnit; updateView(); }
    }, { signal });
    svg.addEventListener("pointerup", () => { drag = null; }, { signal }); svg.addEventListener("pointercancel", () => { drag = null; }, { signal });
    svg.addEventListener("wheel", event => {
      if (!event.ctrlKey && !event.metaKey) return; event.preventDefault(); const rect = svg.getBoundingClientRect();
      const pixelsPerUnit = Math.max(.001, Math.min(rect.width / view.w, rect.height / view.h));
      const padX = (rect.width - view.w * pixelsPerUnit) / 2, padY = (rect.height - view.h * pixelsPerUnit) / 2;
      zoom(event.deltaY > 0 ? 1.15 : 1 / 1.15, view.x + (event.clientX - rect.left - padX) / pixelsPerUnit, view.y + (event.clientY - rect.top - padY) / pixelsPerUnit);
    }, { passive: false, signal });
    svg.addEventListener("keydown", event => {
      if (event.target !== svg) return;
      if (["+", "=", "-", "Home", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) event.preventDefault();
      if (event.key === "+" || event.key === "=") zoom(.7); else if (event.key === "-") zoom(1 / .7); else if (event.key === "Home") fit();
      else { if (event.key === "ArrowLeft") view.x -= view.w * .1; if (event.key === "ArrowRight") view.x += view.w * .1; if (event.key === "ArrowUp") view.y -= view.h * .1; if (event.key === "ArrowDown") view.y += view.h * .1; updateView(); }
    }, { signal });
    const resize = typeof ResizeObserver === "function" ? new ResizeObserver(updateView) : null; resize?.observe(mapFrame);
    const api = { fit, selectLine, destroy() { if (destroyed) return; destroyed = true; abort.abort(); resize?.disconnect(); if (root._cityAtlas === api) delete root._cityAtlas; } };
    root._cityAtlas = api; selectLine(selected); updateView(); return api;
  }
  window.OSRCityAtlas = Object.freeze({ render });
})();
