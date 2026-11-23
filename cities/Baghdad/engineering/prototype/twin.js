"use strict";
const twin = JSON.parse(document.getElementById("model-data").textContent);
const get = (id) => document.getElementById(id);
const canvas = get("car");
const ctx = canvas.getContext("2d");
let parts = twin.geometry.car;
const model = get("model");
let angle = -0.58,
  tilt = 0.29,
  zoom = 1,
  dragging;
const group = get("group"),
  item = get("piece");
function filtered() {
  return parts.filter((p) => !group.value || p.assembly === group.value);
}
function setModel() {
  parts = twin.geometry[model.value];
  group.replaceChildren(
    new Option("All assemblies", ""),
    ...[...new Set(parts.map((p) => p.assembly))].map((n) => new Option(n, n)),
  );
  get("datum").textContent = twin.datums[model.value];
  get("detail").checked = false;
  zoom = 1;
  refresh();
}
model.onchange = setModel;
function draw() {
  const w = canvas.clientWidth,
    h = canvas.clientHeight,
    dp = Math.min(devicePixelRatio || 1, 2);
  canvas.width = Math.round(w * dp);
  canvas.height = Math.round(h * dp);
  ctx.setTransform(dp, 0, 0, dp, 0, 0);
  ctx.clearRect(0, 0, w, h);
  const selection = parts.find((p) => p.id === item.value);
  const shown = filtered();
  const mid = [0, 1, 2].map(
    (k) =>
      (Math.min(...shown.map((p) => p.lower_m[k])) +
        Math.max(...shown.map((p) => p.upper_m[k]))) /
      2,
  );
  const span = Math.max(
    ...[0, 1, 2].map(
      (k) =>
        Math.max(...shown.map((p) => p.upper_m[k])) -
        Math.min(...shown.map((p) => p.lower_m[k])),
    ),
  );
  const origin =
    selection && get("detail").checked
      ? selection.lower_m.map((v, k) => (v + selection.upper_m[k]) / 2)
      : mid;
  const width =
    selection && get("detail").checked
      ? Math.max(
          0.01,
          ...selection.lower_m.map((v, k) => selection.upper_m[k] - v),
        ) * 1.65
      : span * 1.12;
  const scale = Math.min(w / width, h / (width * 0.47)) * zoom;
  const ca = Math.cos(angle),
    sa = Math.sin(angle),
    ct = Math.cos(tilt),
    st = Math.sin(tilt);
  function project(v) {
    const [x, y, z] = v.map((n, k) => n - origin[k]);
    const vdepth = sa * x + ca * y;
    return [
      w / 2 + scale * (ca * x - sa * y),
      h / 2 - scale * (z * ct - vdepth * st),
      vdepth * ct + z * st,
    ];
  }
  const faces = [];
  for (const p of shown) {
    const points = p.vertices.map(project);
    for (const face of p.faces) {
      const verts = face.map((i) => points[i]);
      const depth = verts.reduce((a, v) => a + v[2], 0) / verts.length;
      faces.push({ verts, depth, p });
    }
  }
  faces.sort((a, b) => a.depth - b.depth);
  for (const { verts, p } of faces) {
    ctx.beginPath();
    ctx.moveTo(...verts[0].slice(0, 2));
    for (const v of verts.slice(1)) ctx.lineTo(v[0], v[1]);
    ctx.closePath();
    ctx.fillStyle =
      p === selection
        ? "#ebaa49"
        : p.part.includes("liner")
          ? "#299486"
          : p.assembly.startsWith("bogie")
            ? "#536878"
            : "#728b86";
    ctx.strokeStyle = p === selection ? "#703c0b" : "#395851";
    ctx.lineWidth = 0.55;
    ctx.fill();
    ctx.stroke();
  }
  get("dimensions").textContent = selection
    ? selection.lower_m
        .map((v, k) => Math.round((selection.upper_m[k] - v) * 1000))
        .join(" × ") + " mm"
    : "";
  get("selection").textContent = selection ? selection.id : "";
}
function refresh() {
  item.replaceChildren(...filtered().map((p) => new Option(p.id, p.id)));
  const jamb = filtered().find((p) => p.part === "jamb_liner");
  if (jamb) item.value = jamb.id;
  draw();
}
group.onchange = refresh;
item.onchange = draw;
get("detail").onchange = draw;
get("reset").onclick = () => {
  angle = -0.58;
  tilt = 0.29;
  zoom = 1;
  get("detail").checked = false;
  draw();
};
get("left").onclick = () => {
  angle -= 0.15;
  draw();
};
get("right").onclick = () => {
  angle += 0.15;
  draw();
};
canvas.onpointerdown = (e) => {
  dragging = [e.clientX, e.clientY];
  canvas.setPointerCapture(e.pointerId);
};
canvas.onpointermove = (e) => {
  if (!dragging) return;
  angle += (e.clientX - dragging[0]) * 0.008;
  tilt = Math.max(
    -1.32,
    Math.min(1.32, tilt + (e.clientY - dragging[1]) * 0.009),
  );
  dragging = [e.clientX, e.clientY];
  draw();
};
canvas.onpointerup = canvas.onpointercancel = () => {
  dragging = null;
};
canvas.onkeydown = (e) => {
  if (
    !["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "+", "-"].includes(
      e.key,
    )
  )
    return;
  e.preventDefault();
  if (e.key === "ArrowLeft") angle -= 0.1;
  if (e.key === "ArrowRight") angle += 0.1;
  if (e.key === "ArrowUp") tilt = Math.min(1.32, tilt + 0.1);
  if (e.key === "ArrowDown") tilt = Math.max(-1.32, tilt - 0.1);
  if (e.key === "+") zoom = Math.min(4, zoom * 1.2);
  if (e.key === "-") zoom = Math.max(0.4, zoom / 1.2);
  draw();
};
new ResizeObserver(draw).observe(canvas);
setModel();

const service = twin.service,
  clock = get("clock"),
  route = get("route");
const ns = "http://www.w3.org/2000/svg";
function svg(tag, attrs, text) {
  const el = document.createElementNS(ns, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  if (text) el.textContent = text;
  return el;
}
function chainage(legs, t) {
  for (const leg of legs) {
    if (t < leg.departure_s) return leg.start_km;
    if (t <= leg.arrival_s) {
      const time = t - leg.departure_s,
        a = leg.acceleration_s,
        c = leg.cruise_s,
        v = leg.cruise_m_s;
      const acc = leg.acceleration_m_s2,
        brake = leg.deceleration_m_s2,
        b = Math.max(0, time - a - c);
      const m =
        (acc * Math.min(time, a) ** 2) / 2 +
        v * Math.min(Math.max(time - a, 0), c) +
        v * b -
        (brake * b * b) / 2;
      return leg.start_km + (Math.sign(leg.end_km - leg.start_km) * m) / 1000;
    }
  }
  return legs.at(-1).end_km;
}
const trips = service.trips,
  names = [...new Set(trips.map((r) => r[0]))].sort();
const timeString = (t) =>
  [Math.floor(t / 3600) % 24, Math.floor(t / 60) % 60, t % 60]
    .map((x) => String(x).padStart(2, "0"))
    .join(":") + (t >= 86400 ? " (+1 day)" : "");
const x = (km) => 40 + (640 * km) / service.km;
const yard = service.yard_moves || [];
clock.min = Math.min(...trips.map((r) => r[2]), ...yard.map((m) => m.start_s));
clock.max = Math.max(...trips.map((r) => r[3]), ...yard.map((m) => m.end_s));
clock.value = service.first_departure;
function positions() {
  const t = Number(clock.value);
  get("when").textContent = timeString(t);
  route.replaceChildren(
    svg("title", {}, "Distance along the Airport line at " + timeString(t)),
  );
  route.append(
    svg("line", {
      x1: 40,
      y1: 46,
      x2: 680,
      y2: 46,
      stroke: "#516757",
      "stroke-width": 3,
    }),
  );
  service.stops.forEach((s, i) => {
    route.append(
      svg("circle", {
        cx: x(s.fraction * service.km),
        cy: 46,
        r: 4,
        fill: "#112f2b",
      }),
    );
    route.append(
      svg(
        "text",
        {
          x: x(s.fraction * service.km),
          y: 78,
          "text-anchor": "middle",
          "font-size": 14,
        },
        String(i + 1),
      ),
    );
  });
  const table = get("trains");
  table.replaceChildren();
  for (const name of names) {
    const list = trips.filter((r) => r[0] === name);
    const active = list.find((r) => r[2] <= t && t < r[3]);
    const previous = list
        .filter((r) => r[3] <= t)
        .sort((a, b) => b[3] - a[3])[0],
      next = list.find((r) => r[2] > t);
    let km, label;
    if (active) {
      km = chainage(service.legs[active[1]], t - active[2]);
      label =
        (active[4] ? "Empty to " : "In service to ") +
        (active[1] ? service.stops[0].label : service.stops.at(-1).label);
    } else {
      const moves = yard.filter((m) => m.train === name);
      const move = moves.find((m) => m.start_s <= t && t < m.end_s);
      const arrived = moves.find((m) => m.kind === "depot to platform");
      const removed = moves.find((m) => m.kind === "platform to depot");
      if (move) {
        label =
          move.kind === "depot to platform"
            ? "Depot to platform"
            : "Platform to depot";
      } else if (previous && next) {
        km = previous[1] ? 0 : service.km;
        label = "At terminus";
      } else if (
        (!previous && arrived && t >= arrived.end_s) ||
        (!next && removed && t < removed.start_s && previous)
      ) {
        km = 0;
        label = "At Airport platform";
      } else {
        label = "Off main line";
      }
    }
    if (km !== undefined) {
      const n = names.indexOf(name);
      route.append(
        svg("circle", {
          cx: x(km),
          cy: 16 + n * 9,
          r: 5,
          fill: ["#b74717", "#1b766d", "#445fb3"][n % 3],
        }),
      );
    }
    const row = table.insertRow();
    for (const v of [name, label, km === undefined ? "—" : km.toFixed(2)])
      row.insertCell().textContent = v;
  }
}
clock.oninput = positions;
positions();

function powerReplay(power) {
  const panel = get("power-replay");
  if (!panel || !power) return;
  const title = document.createElement("h3");
  title.textContent = "Scheduled duty after a source outage";
  panel.append(title);
  const controls = document.createElement("div");
  controls.className = "feeder-controls";
  panel.append(controls);
  function select(id, name) {
    const label = document.createElement("label");
    label.textContent = name;
    const field = document.createElement("select");
    field.id = id;
    label.append(field);
    controls.append(label);
    return field;
  }
  const layout = select("power-layout", "Circuit under review");
  layout.add(new Option("Priced radial · hot circuit", "radial"));
  layout.add(
    new Option("Six stations, paired paths · combined sensitivity", "paired"),
  );
  const isolation = select("power-isolation", "Isolated source");
  const result = document.createElement("p");
  result.id = "power-result";
  result.setAttribute("aria-live", "polite");
  panel.append(result);
  function drawResult() {
    const record = power[layout.value].outages[isolation.selectedIndex];
    const duty = record.worst;
    const site = "S" + String(duty.site + 1).padStart(2, "0");
    const voltage =
      duty.collector_kv === null
        ? "no stable operating voltage"
        : duty.collector_kv.toFixed(4) + " kV";
    result.textContent =
      `Lowest scheduled collector voltage ${voltage} at ${timeString(duty.first_local_s)}. ` +
      `Source ${site} feeds up to ${duty.furthest_fed_km.toFixed(3)} km in that case. ` +
      `Maximum daily source RMS current ${record.site_rms_ka_upper?.toFixed(3) ?? "unresolved"} kA.`;
  }
  function setLayout() {
    const config = power[layout.value];
    const sites =
      layout.value === "radial"
        ? config.site_chainage_km
        : config.scope.design.site_chainage_km;
    isolation.replaceChildren(
      ...config.outages.map((row) =>
        row.failed_site === null
          ? new Option("All sources available", "all")
          : new Option(
              `S${String(row.failed_site + 1).padStart(2, "0")} · ${sites[row.failed_site].toFixed(3)} km`,
              String(row.failed_site),
            ),
      ),
    );
    drawResult();
  }
  layout.onchange = setLayout;
  isolation.onchange = drawResult;
  setLayout();
}
powerReplay(twin.power);
