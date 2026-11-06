/* Conditional journey inspection using only the currently displayed city packet. */
(function () {
  "use strict";
  const defaults = Object.freeze({ walking_speed_m_s: 1.2, transfer_detour_factor: 1.4, interchange_overhead_s: 120, wait_headway_fraction: .5 });
  const finite = value => typeof value === "number" && Number.isFinite(value);
  const first = (...values) => values.find(value => value !== null && value !== undefined);
  const key = (line, stop) => `${line}::${stop}`;
  function haversine(a, b) {
    if (![a?.lon, a?.lat, b?.lon, b?.lat].every(finite)) return null;
    const r = Math.PI / 180, lat = (b.lat - a.lat) * r, lon = (b.lon - a.lon) * r;
    const h = Math.sin(lat / 2) ** 2 + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(lon / 2) ** 2;
    return 6371008.8 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(Math.max(0, 1 - h)));
  }
  function model(packet) {
    if (packet?.schema !== "osr-city-atlas/1" || !Array.isArray(packet.lines)) throw Error("Current city atlas packet required");
    const stops = [], bySource = new Map(), byKey = new Map(), entries = [], lines = new Map();
    for (const line of packet.lines) {
      const row = { line, stops: [], legs: new Map() }; lines.set(line.line_id, row);
      for (const [index, stop] of (line.operational_stops || []).entries()) {
        const complex = (line.station_complexes || []).find(item => item.operational_stop_id === stop.id);
        const item = { key: key(line.line_id, stop.id), line_id: line.line_id, id: stop.id, stop, complex, index, row };
        stops.push(item); row.stops.push(item); byKey.set(item.key, item);
        for (const id of new Set([stop.id, ...(stop.source_stop_ids || []), ...(complex?.original_stop_ids || [])])) {
          const list = bySource.get(id) || []; list.push(item); bySource.set(id, list);
        }
        const sources = stop.source_stop_ids?.length ? stop.source_stop_ids : complex?.original_stop_ids?.length ? complex.original_stop_ids : [stop.id];
        for (const id of sources) {
          const original = (line.original_stops || []).find(source => source.id === id);
          const connector = (complex?.access_connectors || []).find(source => source.original_stop_id === id);
          entries.push({ key: key(line.line_id, id), line_id: line.line_id, stop_id: stop.id, original_stop_id: id,
            label: `${line.name || line.line_id} · ${original?.name || original?.label || id}`, access_m: connector ? connector.along_route_connector_m : id === stop.id ? 0 : null, item });
        }
      }
      for (const leg of line.legs || []) {
        if (!finite(leg.scheduled_runtime_s) || leg.scheduled_runtime_s < 0) continue;
        const from = row.stops.find(stop => stop.id === leg.from_stop), to = row.stops.find(stop => stop.id === leg.to_stop);
        if (!from || !to) continue;
        row.legs.set(key(from.id, to.id) + "::1", { from, to, leg, direction: 1 });
        row.legs.set(key(to.id, from.id) + "::-1", { from: to, to: from, leg, direction: -1 });
      }
    }
    const transfers = new Map(stops.map(stop => [stop.key, []]));
    for (const interchange of packet.interchanges || []) {
      const members = [...new Set((interchange.platforms || []).flatMap(id => (bySource.get(id) || []).filter(stop => !interchange.lines?.length || interchange.lines.includes(stop.line_id))))];
      for (const from of members) for (const to of members) {
        if (from.line_id === to.line_id || from.key === to.key) continue;
        const distance = haversine(from.stop, to.stop);
        if (!finite(distance)) continue; // Missing coordinates do not become zero walking distance.
        const add = id => (id.complex?.access_connectors || []).filter(connector => (interchange.platforms || []).includes(connector.original_stop_id));
        const accessA = add(from), accessB = add(to);
        const access = (list, stop) => list.length && list.every(item => finite(item.along_route_connector_m)) ? Math.min(...list.map(item => item.along_route_connector_m)) : (interchange.platforms || []).includes(stop.id) ? 0 : null;
        const fromAccess = access(accessA, from), toAccess = access(accessB, to);
        if (!finite(fromAccess) || !finite(toAccess)) continue;
        transfers.get(from.key).push({ to, interchange_id: interchange.id, distance_m: distance, access_m: fromAccess + toAccess });
      }
    }
    return { stops, entries, transfers, bySource, byKey };
  }
  function stations(packet) { return model(packet).entries.map(({ item, ...entry }) => entry); }
  function route(packet, originKey, destinationKey, assumptions = {}) {
    const a = { ...defaults, ...assumptions };
    if (!finite(a.walking_speed_m_s) || a.walking_speed_m_s <= 0 || !finite(a.transfer_detour_factor) || a.transfer_detour_factor < 1 || !finite(a.interchange_overhead_s) || a.interchange_overhead_s < 0 || !finite(a.wait_headway_fraction) || a.wait_headway_fraction < 0 || a.wait_headway_fraction > 1) throw Error("Bounded walking, detour, overhead and waiting assumptions required");
    const m = model(packet);
    function resolve(value) {
      const exact = m.entries.find(entry => entry.key === value);
      if (exact) return exact;
      const matches = m.entries.filter(entry => entry.original_stop_id === value || entry.stop_id === value);
      if (matches.length === 1) return matches[0];
      const item = m.byKey.get(value); return item ? { key: value, item, access_m: 0, label: item.id, line_id: item.line_id, stop_id: item.id } : null;
    }
    const origin = resolve(originKey), destination = resolve(destinationKey);
    if (!origin || !destination) throw Error("Station key is missing or ambiguous in this city packet");
    const resultBase = { schema: "osr-city-journey/1", packet_id: packet.packet_id, origin_key: origin.key, destination_key: destination.key, assumptions: a,
      evidence_stage: "Conditional analytical journey; not a qualified timetable", symmetric_return_hypothesis: true,
      timing_basis: "Actual scheduled_runtime_s leg values in both directions under a symmetric-return hypothesis; stop_dwell_s only at intermediate through stops. Waiting applies once per boarding. Transfers exist only at explicit interchange references.", physical_accepted: false };
    if (origin.key === destination.key) return { ...resultBase, status: "reachable", duration_s: 0, boardings: 0, steps: [], totals: { running_s: 0, dwell_s: 0, wait_s: 0, walking_s: 0, transfer_overhead_s: 0 } };
    if (!finite(origin.access_m) || !finite(destination.access_m)) return { ...resultBase, status: "unreachable", reason: "Endpoint access distance is not established", steps: [] };
    const step = (kind, duration_s, details = {}) => ({ kind, duration_s, ...details });
    const access = (entry, end) => entry.access_m > 0 ? [step("access", entry.access_m / a.walking_speed_m_s, { line_id: entry.line_id, stop_id: entry.stop_id, distance_m: entry.access_m, endpoint: end })] : [];
    const startSteps = access(origin, "origin"), initial = startSteps.reduce((sum, item) => sum + item.duration_s, 0);
    const distances = new Map([["start", initial]]), states = new Map([["start", { stop: origin.item, direction: 0 }]]), previous = new Map(), visited = new Set();
    const terminal = "destination";
    const relax = (from, id, state, steps) => {
      const duration = steps.reduce((sum, item) => sum + item.duration_s, 0), next = distances.get(from) + duration;
      if (!finite(next)) return;
      if (next < (distances.get(id) ?? Infinity)) { distances.set(id, next); states.set(id, state); previous.set(id, { from, steps }); }
    };
    function rides(fromId, at, direction, before, boarding) {
      const row = at.row, nextIndex = at.index + direction;
      const ring = row.line.shape === "ring", nextStop = row.stops[ring ? (nextIndex + row.stops.length) % row.stops.length : nextIndex];
      if (!nextStop || nextStop === at) return;
      const ride = row.legs.get(key(at.id, nextStop.id) + "::" + direction); if (!ride) return;
      const steps = [...before];
      if (boarding) {
        const headway = first(row.line.metrics?.headway_s, row.line.requirements?.headway_s);
        if (!finite(headway) || headway <= 0) return;
        steps.push(step("board", headway * a.wait_headway_fraction, { line_id: at.line_id, stop_id: at.id, headway_s: headway, wait_basis: "Editable fraction of headway, no timed connection claim" }));
      } else {
        const dwell = first(row.line.service?.stop_dwell_s?.[at.index], at.stop.dwell_s);
        if (!finite(dwell) || dwell < 0) return;
        if (dwell) steps.push(step("dwell", dwell, { line_id: at.line_id, stop_id: at.id }));
      }
      steps.push(step("ride", ride.leg.scheduled_runtime_s, { line_id: at.line_id, from_stop: at.id, to_stop: nextStop.id, leg_index: row.line.legs.indexOf(ride.leg), distance_m: ride.leg.distance_m, direction: direction === 1 ? "source direction" : "symmetric-return hypothesis", timing_field: "scheduled_runtime_s" }));
      relax(fromId, `${nextStop.key}::${direction}`, { stop: nextStop, direction }, steps);
    }
    while (true) {
      let current = null, distance = Infinity;
      for (const [id, value] of distances) if (!visited.has(id) && value < distance) { current = id; distance = value; }
      if (current === null || current === terminal) break;
      visited.add(current); const state = states.get(current), at = state.stop;
      if (at.key === destination.item.key) relax(current, terminal, null, access(destination, "destination"));
      if (current === "start") { rides(current, at, 1, [], true); rides(current, at, -1, [], true); }
      else rides(current, at, state.direction, [], false);
      for (const transfer of m.transfers.get(at.key) || []) {
        const walkingM = transfer.distance_m * a.transfer_detour_factor + transfer.access_m;
        const steps = [step("transfer", walkingM / a.walking_speed_m_s + a.interchange_overhead_s, { from_line_id: at.line_id, line_id: transfer.to.line_id, from_stop: at.id, to_stop: transfer.to.id, interchange_id: transfer.interchange_id, distance_m: walkingM, straight_line_distance_m: transfer.distance_m, walking_s: walkingM / a.walking_speed_m_s, overhead_s: a.interchange_overhead_s, geometry_basis: "Declared interchange only; coordinate separation × editable detour plus recorded access connectors; path not surveyed" })];
        if (transfer.to.key === destination.item.key) relax(current, terminal, null, [...steps, ...access(destination, "destination")]);
        rides(current, transfer.to, 1, steps, true); rides(current, transfer.to, -1, steps, true);
      }
    }
    if (!distances.has(terminal)) return { ...resultBase, status: "unreachable", reason: "No journey through timed legs and explicit interchanges under these assumptions", steps: [] };
    let id = terminal, groups = [];
    while (id !== "start") { const edge = previous.get(id); if (!edge) throw Error("Incomplete journey predecessor chain"); groups.push(edge.steps); id = edge.from; }
    const steps = [...startSteps, ...groups.reverse().flat()], totals = { running_s: 0, dwell_s: 0, wait_s: 0, walking_s: 0, transfer_overhead_s: 0 };
    for (const item of steps) {
      if (item.kind === "ride") totals.running_s += item.duration_s;
      if (item.kind === "dwell") totals.dwell_s += item.duration_s;
      if (item.kind === "board") totals.wait_s += item.duration_s;
      if (item.kind === "access") totals.walking_s += item.duration_s;
      if (item.kind === "transfer") { totals.walking_s += item.walking_s; totals.transfer_overhead_s += item.overhead_s; }
    }
    return { ...resultBase, status: "reachable", duration_s: distances.get(terminal), steps, totals, boardings: steps.filter(item => item.kind === "board").length };
  }
  function element(tag, cls, text) { const node = document.createElement(tag); if (cls) node.className = cls; if (text !== undefined) node.textContent = text; return node; }
  function mount(parent, packet) {
    if (typeof parent === "string") parent = document.querySelector(parent);
    if (!parent) throw Error("Journey planner parent is missing");
    const entries = stations(packet), root = element("section", "atlas-journeys"), heading = element("h4", "", "Inspect a station-to-station journey");
    root.append(heading, element("p", "atlas-note", "Uses this result’s timed legs and declared interchanges. Return travel uses the same leg times as a symmetric-return hypothesis. Walking routes and connections are planning assumptions; this is not a qualified timetable."));
    const form = element("form", "outline-inputs"), inputs = {};
    for (const [name, label] of [["origin", "From station"], ["destination", "To station"]]) {
      const wrapper = element("label", "", label), select = element("select"); select.required = true;
      for (const entry of entries) { const option = element("option", "", entry.label); option.value = entry.key; select.append(option); }
      if (name === "destination" && entries.length > 1) select.value = entries.at(-1).key;
      inputs[name] = select; wrapper.append(select); form.append(wrapper);
    }
    for (const [name, label, min, max, step] of [["walking_speed_m_s", "Walking speed · m/s", .1, 4, .1], ["transfer_detour_factor", "Transfer walking detour factor", 1, 10, .1], ["interchange_overhead_s", "Interchange overhead · seconds", 0, 3600, 10], ["wait_headway_fraction", "Expected wait · fraction of headway", 0, 1, .05]]) {
      const wrapper = element("label", "", label), input = element("input"); input.type = "number"; input.min = min; input.max = max; input.step = step; input.value = defaults[name]; input.required = true; inputs[name] = input; wrapper.append(input); form.append(wrapper);
    }
    const submit = element("button", "atlas-back", "Calculate conditional journey"); submit.type = "submit"; form.append(submit); root.append(form);
    const output = element("div", "atlas-disclosure-body"); output.setAttribute("aria-live", "polite"); root.append(output); parent.append(root);
    function calculate() {
      output.replaceChildren();
      try {
        const assumptions = Object.fromEntries(Object.keys(defaults).map(name => [name, Number(inputs[name].value)]));
        const result = route(packet, inputs.origin.value, inputs.destination.value, assumptions);
        if (result.status !== "reachable") { output.append(element("p", "atlas-capacity-hold", result.reason)); return result; }
        const min = seconds => (seconds / 60).toFixed(1) + " min";
        output.append(element("p", "atlas-capacity-pass", `${min(result.duration_s)} conditional total · ${result.boardings || 0} boardings`));
        output.append(element("p", "atlas-note", `Running ${min(result.totals.running_s)} · intermediate dwell ${min(result.totals.dwell_s)} · boarding wait ${min(result.totals.wait_s)} · walking ${min(result.totals.walking_s)} · interchange overhead ${min(result.totals.transfer_overhead_s)}`));
        const list = element("ol", "atlas-readable-list");
        for (const item of result.steps) {
          const descriptions = { access: `Walk ${item.endpoint || ""} access · ${Math.round(item.distance_m)} m`, board: `Board ${item.line_id} at ${item.stop_id} · expected wait`, dwell: `Remain on ${item.line_id} at ${item.stop_id} · intermediate dwell`, ride: `${item.line_id}: ${item.from_stop} → ${item.to_stop} · ${item.direction}`, transfer: `Transfer ${item.from_line_id} → ${item.line_id} at ${item.interchange_id} · ${Math.round(item.distance_m)} m assumed walk plus overhead` };
          list.append(element("li", "", `${descriptions[item.kind]} — ${min(item.duration_s)}`));
        }
        output.append(list); return result;
      } catch (error) { output.append(element("p", "atlas-capacity-hold", error.message)); return null; }
    }
    form.addEventListener("submit", event => { event.preventDefault(); calculate(); });
    return { calculate, destroy() { root.remove(); } };
  }
  window.OSRCityJourneys = Object.freeze({ mount, route, stations, defaults });
})();
