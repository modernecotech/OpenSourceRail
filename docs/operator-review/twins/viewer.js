"use strict";
const el = (id) => document.getElementById(id);
const canvas = el("canvas");
const ctx = canvas.getContext("2d");
const palette = {
  web: "#52717b",
  hub: "#63818a",
  disc: "#8e938b",
  stock: "#447975",
  brace: "#bb7e44",
  plate: "#b97344",
  bogiestock: "#3f5767",
  floor: "#4b6772",
  roof: "#d8e2da",
  sill: "#cdd9d0",
  glass: "#315c70",
  end: "#63818a",
  door: "#389e94",
  frame: "#465f68",
  wheel: "#304754",
  axle: "#809198",
  control: "#d16b38",
  motor: "#aa6846",
  brake: "#d8a84f",
  collection: "#bc7432",
  beam: "#9aaba8",
  pier: "#b0bdb3",
  rail: "#667d80",
  platform: "#c6ccba",
  edge: "#e1bc58",
};
const titles = {
  stock: "Fabricated stock",
  body: "Carbody",
  bogie: "Powered bogie",
  door: "Boarding interface",
  platform: "Island platform",
  beam: "Track and viaduct",
  power: "Traction supply",
  control: "Car control node",
};
const labels = {
  web: "Wheel web",
  hub: "Wheel hub",
  disc: "Brake disc",
  stock: "Body stock",
  brace: "Sidewall brace",
  plate: "Mounting plate",
  bogiestock: "Bogie stock",
  floor: "Floor envelope",
  roof: "Roof or post",
  sill: "Side sill",
  glass: "Glazing envelope",
  end: "End panel",
  door: "Door opening",
  frame: "Bogie frame",
  wheel: "Wheel",
  axle: "Axle",
  control: "Control allocation",
  motor: "Motor envelope",
  brake: "Rail brake shoe",
  collection: "Collection interface",
  beam: "Running beam",
  pier: "Support position",
  rail: "Running rail",
  platform: "Platform deck",
  edge: "Platform edge",
};
const views = {
  frame: {
    id: "sill_000",
    caption: "Braced quotation revision B · 128 actual cut-stock mesh objects",
  },
  station: {
    id: "ISL/deck",
    caption: "Station arrangement · 140 m display window",
  },
  car: { id: "C03/floor", caption: "Car 03 · body and roof equipment" },
  bogie: {
    id: "C03/B1/A1",
    caption: "Car 03 · leading bogie, carbody removed",
  },
  door: {
    id: "C03/side+1/D1",
    caption: "Car 03 · platform-side boarding interface",
  },
  civil: {
    id: "T1/span07",
    caption: "Straight running spans · independent track supports",
  },
  control: {
    id: "C03/node-zone",
    caption: "Car 03 · equipment allocation, carbody removed",
  },
};
let m,
  view,
  chosen,
  pieces,
  yaw,
  elevation,
  zoom,
  base,
  target,
  hits = [],
  activeId = "";
function readQuery() {
  const q = new URLSearchParams(location.hash.slice(1));
  return [
    ["baghdad", "frame"].includes(q.get("model")) ? q.get("model") : "core",
    Object.hasOwn(views, q.get("view")) ? q.get("view") : "station",
  ];
}
function useModel(key, v) {
  m = window.RAIL_MODELS[key];
  if (key === "frame") v = "frame";
  else if (v === "frame") v = "station";
  el("stock-study").hidden = key === "core";
  el("stock-study").textContent =
    key === "frame" ? "Return to first programme" : "Frame quotation ↗";
  el("stock-study").setAttribute("aria-pressed", key === "frame");
  document
    .querySelectorAll("[data-view]")
    .forEach((b) => (b.hidden = key === "frame"));
  el("scene-scope").hidden = key === "frame";
  document
    .querySelectorAll("[data-model]")
    .forEach((b) =>
      b.setAttribute(
        "aria-pressed",
        b.dataset.model === (key === "frame" ? "baghdad" : key),
      ),
    );
  el("subtitle").textContent = m.subtitle;
  el("title").textContent =
    m.key === "frame"
      ? "Baghdad carbody and bogie frames"
      : m.name + " station and train";
  el("scope").textContent = m.scope;
  const values =
    key === "frame"
      ? [
          ["17 m", "carbody length"],
          [m.parts.length, "cut-stock objects"],
          [(m.stockKg / 1000).toFixed(3) + " t", "cut-stock mass / car"],
          ["Quotation B", "design revision"],
        ]
      : [
          [m.length + " m", "train length"],
          [m.places.toLocaleString(), "normal places / train"],
          [
            m.carCount * m.doorX.length * m.doorSides.length,
            "door openings / train",
          ],
          [m.collection, "traction supply"],
        ];
  el("metrics").replaceChildren(
    ...values.map(([a, b]) => {
      const d = document.createElement("div");
      d.className = "metric";
      const n = document.createElement("b");
      n.textContent = a;
      d.append(n, document.createTextNode(b));
      return d;
    }),
  );
  el("download").textContent =
    key === "frame" ? "Download original OBJ mesh ↓" : "Download IFC4 model ↓";
  el("download").href =
    key === "frame"
      ? "../../../cities/Baghdad/engineering/mechanical/vehicle/braced-frame.obj"
      : key + ".ifc";
  el("identity").textContent =
    "Physical candidate " +
    m.candidate +
    " · Evaluation " +
    m.evaluation +
    " · Selection " +
    m.selection +
    ".";
  useView(v);
}
function useView(v) {
  view = v;
  zoom = 1;
  activeId = "";
  const t = -(m.spacing || 0) / 2,
    cx = -8.75,
    bx = cx + (m.bogieX?.[0] || 0);
  const config = {
    frame: [[0, 0, 1.65], 20, -0.44, 0.38],
    station: [[0, 0, -1.2], 148, -0.66, 0.47],
    car: [[cx, t, 1.8], 21, -0.41, 0.35],
    bogie: [[bx, t, 0.47], 4.4, -0.51, 0.42],
    door: [[cx + (m.doorX?.[0] || 0), t + 1.15, 1.3], 7, -0.56, 0.44],
    civil: [[-5, -0.5, -2.7], 37, -0.73, 0.39],
    control: [[cx, t, 0.54], 10, -0.48, 0.6],
  };
  [target, base, yaw, elevation] = config[v];
  function shows(r) {
    if (v === "station" || v === "frame") return true;
    if (v === "car") return r[1].startsWith("C03/");
    if (v === "bogie")
      return (
        r[1].startsWith("C03/") && r[0] === "bogie" && Math.abs(r[2] - bx) < 2.3
      );
    if (v === "control")
      return r[1].startsWith("C03/") && ["control", "bogie"].includes(r[0]);
    if (v === "door") return r[1].startsWith("C03/") || r[0] === "platform";
    return (
      ["beam", "power", "platform"].includes(r[0]) &&
      Math.abs(r[2] + 5) < r[5] / 2 + 14
    );
  }
  pieces = m.parts.filter(shows);
  const opts = pieces.map((r) => {
    const o = document.createElement("option");
    o.value = r[1];
    o.textContent = r[1] + " · " + labels[r[8]];
    return o;
  });
  el("occurrence").replaceChildren(...opts);
  inspect(views[v].id, false);
  el("caption").textContent = views[v].caption;
  document
    .querySelectorAll("[data-view]")
    .forEach((b) => b.setAttribute("aria-pressed", b.dataset.view === v));
  if (location.hash !== "#model=" + m.key + "&view=" + v)
    history.replaceState(null, "", "#model=" + m.key + "&view=" + v);
  draw();
}
function inspect(id, highlight = true) {
  chosen = pieces.find((r) => r[1] === id) || pieces[0];
  const [g, name, x, y, z, a, b, c, style] = chosen;
  el("occurrence").value = name;
  activeId = highlight ? name : "";
  el("inspection").textContent = titles[g];
  const texts = {
    stock:
      "The first-article mesh includes both hollow body-side frames, jambs and braces, bolsters, two bogie frames and the primary and secondary interface plates. The 5.196 t subtotal covers cut stock. Welds, joints, wheels, suspension, traction, fitout and installed mass require separate take-offs.",
    body: "Six individually supported 17 m carbodies on a 17.5 m pitch. The floor surface sits 1.0 m above rail. Review the ends, threshold load paths and equipment access in the linked vehicle design.",
    platform:
      "The 125 × 8 m island gives 10.25 m at each end of the centred 104.5 m train and a 75 mm nominal straight body-to-edge gap. The island requires its own frame and foundations.",
    door: m.hold,
    beam: m.quantity,
    control: m.control,
    power: m.powerText,
    bogie:
      m.key === "core"
        ? "Two bogies support each car. Each axle takes a 640 × 520 × 520 mm motor envelope. The two bogies carry 4.966 t of modelled steel per car before powered equipment and outstanding installations. Measure yaw, roll, hose travel and tool access."
        : "Two bogies support each car at ±6.4 m from its centre. The quotation rig places two axles on a 2.10 m wheelbase. Check the outer doorway over the bolster, joint loads and bogie withdrawal with a supported test car.",
  };
  el("note").textContent = texts[g];
  el("source").href = "../../../" + m.links[g];
  const coords = [x, y, z].map((n) => n.toFixed(2)).join(" / ");
  const rows = [
    ["Component", labels[style]],
    ["X / Y / Z (m)", coords],
    ["Envelope (m)", [a, b, c].map((n) => String(+n.toFixed(3))).join(" × ")],
  ];
  el("dimensions").replaceChildren(
    ...rows.map(([key, value]) => {
      const d = document.createElement("div"),
        n = document.createElement("b");
      n.textContent = value;
      d.append(document.createTextNode(key), n);
      return d;
    }),
  );
  if (highlight) draw();
}
function shade(hex, f) {
  const rgb = [1, 3, 5].map((i) =>
    Math.min(255, Math.round(parseInt(hex.slice(i, i + 2), 16) * f)),
  );
  return "rgb(" + rgb.join(",") + ")";
}
function draw() {
  const w = canvas.clientWidth,
    h = canvas.clientHeight;
  if (!w || !h || !m) return;
  const dpr = Math.min(devicePixelRatio || 1, 2);
  if (
    canvas.width !== Math.round(w * dpr) ||
    canvas.height !== Math.round(h * dpr)
  ) {
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
  }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const sky = ctx.createLinearGradient(0, 0, w * 0.15, h);
  sky.addColorStop(0, "#edf2e9");
  sky.addColorStop(1, "#dbe5d9");
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, w, h);
  const sy = Math.sin(yaw),
    cy = Math.cos(yaw),
    se = Math.sin(elevation),
    ce = Math.cos(elevation);
  const scale =
    Math.min(w / base, h / (base * (view === "station" ? 0.34 : 0.59))) * zoom;
  function project(x, y, z) {
    x -= target[0];
    y -= target[1];
    z -= target[2];
    const horiz = -sy * x + cy * y;
    return [
      w * 0.5 + scale * (cy * x + sy * y),
      h * 0.53 + scale * (se * horiz - ce * z),
      ce * horiz + se * z,
    ];
  }
  function line(p, q) {
    ctx.beginPath();
    ctx.moveTo(p[0], p[1]);
    ctx.lineTo(q[0], q[1]);
    ctx.stroke();
  }
  const grid =
    view === "station" ? 10 : view === "civil" ? 5 : view === "bogie" ? 0.5 : 2;
  const level = ["station", "civil"].includes(view) ? -7.65 : -0.12;
  const range = base * 2;
  ctx.strokeStyle = "#a8beaf66";
  ctx.lineWidth = 0.65;
  for (
    let i = Math.floor((target[0] - range) / grid);
    i <= Math.ceil((target[0] + range) / grid);
    i++
  )
    line(
      project(i * grid, target[1] - range, level),
      project(i * grid, target[1] + range, level),
    );
  for (
    let i = Math.floor((target[1] - range) / grid);
    i <= Math.ceil((target[1] + range) / grid);
    i++
  )
    line(
      project(target[0] - range, i * grid, level),
      project(target[0] + range, i * grid, level),
    );
  const faces = [];
  function face(poly, record, light) {
    if (
      poly.every((p) => p[0] < -2) ||
      poly.every((p) => p[0] > w + 2) ||
      poly.every((p) => p[1] < -2) ||
      poly.every((p) => p[1] > h + 2)
    )
      return;
    let area = 0;
    for (let j = 0; j < poly.length; j++) {
      let p = poly[j],
        q = poly[(j + 1) % poly.length];
      area += p[0] * q[1] - q[0] * p[1];
    }
    if (area <= 0) return;
    faces.push({
      poly,
      record,
      light,
      depth: poly.reduce((a, p) => a + p[2], 0) / poly.length,
    });
  }
  for (const r of pieces) {
    const [, name, x, y, z, a, b, c, style, shape] = r;
    if (shape === "mesh") {
      for (const polygon of m.faces[name]) {
        const world = polygon.map((i) => m.vertices[i]);
        const pts = world.map((p) => project(...p));
        const p = world[0],
          q = world[1],
          t = world[2];
        const a = q.map((v, i) => v - p[i]),
          b = t.map((v, i) => v - p[i]);
        const n = [
          a[1] * b[2] - a[2] * b[1],
          a[2] * b[0] - a[0] * b[2],
          a[0] * b[1] - a[1] * b[0],
        ];
        const light = 0.77 + (0.3 * Math.abs(n[2])) / (Math.hypot(...n) || 1);
        face(pts, r, light);
        face(pts.slice().reverse(), r, light);
      }
      continue;
    }
    if (shape === "cylinder") {
      const n = view === "station" ? 10 : 32,
        sides = [[], []],
        holes = [[], []];
      const inner = r[10] || 0;
      for (let k = 0; k < 2; k++)
        for (let j = 0; j < n; j++) {
          const ang = (j * 2 * Math.PI) / n;
          sides[k].push(
            project(
              x + a * 0.5 * Math.cos(ang),
              y + (k - 0.5) * b,
              z + c * 0.5 * Math.sin(ang),
            ),
          );
          if (inner)
            holes[k].push(
              project(
                x + inner * Math.cos(ang),
                y + (k - 0.5) * b,
                z + inner * Math.sin(ang),
              ),
            );
        }
      if (inner) {
        for (let j = 0; j < n; j++) {
          const k = (j + 1) % n;
          face([sides[0][j], sides[0][k], holes[0][k], holes[0][j]], r, 0.97);
          face([holes[1][j], holes[1][k], sides[1][k], sides[1][j]], r, 0.88);
          face([holes[0][j], holes[0][k], holes[1][k], holes[1][j]], r, 0.73);
        }
      } else {
        face(sides[0], r, 0.97);
        face(sides[1].slice().reverse(), r, 0.85);
      }
      for (let j = 0; j < n; j++) {
        const k = (j + 1) % n;
        face(
          [sides[0][k], sides[0][j], sides[1][j], sides[1][k]],
          r,
          0.87 + 0.14 * Math.sin((j * 2 * Math.PI) / n),
        );
      }
      continue;
    }
    const clip = view === "door" || view === "civil";
    const lo = Math.max(x - a / 2, clip ? target[0] - base * 0.51 : -Infinity),
      hi = Math.min(x + a / 2, clip ? target[0] + base * 0.51 : Infinity);
    if (lo >= hi) continue;
    const chunks = Math.ceil((hi - lo) / (view === "station" ? 2 : 1.5));
    // Tile wide surfaces as well, so near platform edges can occlude wheelsets.
    const rows = Math.max(1, Math.ceil(b / 2.1));
    for (let i = 0; i < chunks; i++)
      for (let j = 0; j < rows; j++) {
        const x0 = lo + ((hi - lo) * i) / chunks,
          x1 = lo + ((hi - lo) * (i + 1)) / chunks;
        const y0 = y - b * 0.5 + (b * j) / rows,
          y1 = y - b * 0.5 + (b * (j + 1)) / rows,
          z0 = z - c * 0.5,
          z1 = z + c * 0.5;
        const p = [
          [x0, y0, z0],
          [x1, y0, z0],
          [x1, y1, z0],
          [x0, y1, z0],
          [x0, y0, z1],
          [x1, y0, z1],
          [x1, y1, z1],
          [x0, y1, z1],
        ].map((k) => project(...k));
        const f = (idx, l) =>
          face(
            idx.map((k) => p[k]),
            r,
            l,
          );
        f([4, 5, 6, 7], 1.08);
        f([3, 2, 1, 0], 0.7);
        if (!j) f([0, 1, 5, 4], 0.82);
        if (j === rows - 1) f([2, 3, 7, 6], 0.9);
        if (!i) f([3, 0, 4, 7], 0.73);
        if (i === chunks - 1) f([1, 2, 6, 5], 0.95);
      }
  }
  faces.sort((a, b) => a.depth - b.depth);
  for (const f of faces) {
    const pts = f.poly;
    ctx.fillStyle = shade(
      f.record[1] === activeId ? "#e5aa3c" : palette[f.record[8]],
      f.light,
    );
    ctx.strokeStyle = ctx.fillStyle;
    ctx.lineWidth = 0.48;
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    pts.slice(1).forEach((p) => ctx.lineTo(p[0], p[1]));
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
  }
  hits = faces;
  const tick =
    view === "station" ? 10 : view === "civil" ? 5 : view === "bogie" ? 0.5 : 1;
  const x0 = 18,
    y0 = h - 55;
  ctx.strokeStyle = "#506d60";
  ctx.fillStyle = "#36564b";
  ctx.lineWidth = 1.25;
  line([x0, y0], [x0 + tick * scale, y0]);
  line([x0, y0 - 3], [x0, y0 + 3]);
  line([x0 + tick * scale, y0 - 3], [x0 + tick * scale, y0 + 3]);
  ctx.font = "11px Arial";
  ctx.fillText(tick + " m", x0, y0 - 6);
}
function contains(points, x, y) {
  let inside = false;
  for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
    const [a, b] = points[i],
      [c, d] = points[j];
    if (b > y !== d > y && x < ((c - a) * (y - b)) / (d - b) + a)
      inside = !inside;
  }
  return inside;
}
let press;
canvas.addEventListener("pointerdown", (e) => {
  press = { x: e.clientX, y: e.clientY, yaw, elevation };
  canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener("pointermove", (e) => {
  if (!press) return;
  yaw = press.yaw + (e.clientX - press.x) * 0.008;
  elevation = Math.max(
    0.04,
    Math.min(1.46, press.elevation + (e.clientY - press.y) * 0.006),
  );
  draw();
});
canvas.addEventListener("pointerup", (e) => {
  if (press && Math.hypot(e.clientX - press.x, e.clientY - press.y) < 4) {
    const b = canvas.getBoundingClientRect();
    for (let i = hits.length - 1; i >= 0; i--)
      if (contains(hits[i].poly, e.clientX - b.left, e.clientY - b.top)) {
        inspect(hits[i].record[1]);
        break;
      }
  }
  press = null;
});
canvas.addEventListener("pointercancel", () => {
  press = null;
});
function changeZoom(f) {
  zoom = Math.max(0.4, Math.min(6, zoom * f));
  draw();
}
canvas.addEventListener(
  "wheel",
  (e) => {
    e.preventDefault();
    changeZoom(e.deltaY < 0 ? 1.12 : 1 / 1.12);
  },
  { passive: false },
);
canvas.addEventListener("keydown", (e) => {
  if (
    ![
      "ArrowLeft",
      "ArrowRight",
      "ArrowUp",
      "ArrowDown",
      "+",
      "-",
      "=",
    ].includes(e.key)
  )
    return;
  e.preventDefault();
  if (e.key === "ArrowLeft") yaw -= 0.12;
  if (e.key === "ArrowRight") yaw += 0.12;
  if (e.key === "ArrowUp") elevation = Math.min(1.46, elevation + 0.09);
  if (e.key === "ArrowDown") elevation = Math.max(0.04, elevation - 0.09);
  if (e.key === "+" || e.key === "=") changeZoom(1.2);
  if (e.key === "-") changeZoom(1 / 1.2);
  draw();
});
el("stock-study").onclick = () =>
  useModel(
    m.key === "frame" ? "baghdad" : "frame",
    m.key === "frame" ? "car" : "frame",
  );
el("plus").onclick = () => changeZoom(1.2);
el("minus").onclick = () => changeZoom(1 / 1.2);
el("reset").onclick = () => useView(view);
el("occurrence").onchange = (e) => inspect(e.target.value);
document
  .querySelectorAll("[data-model]")
  .forEach((b) => (b.onclick = () => useModel(b.dataset.model, view)));
document
  .querySelectorAll("[data-view]")
  .forEach((b) => (b.onclick = () => useView(b.dataset.view)));
useModel(...readQuery());
new ResizeObserver(draw).observe(canvas);
window.addEventListener("hashchange", () => useModel(...readQuery()));
