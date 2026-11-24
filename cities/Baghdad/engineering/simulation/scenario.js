"use strict";

const form = document.querySelector("#scenario");
const viewButtons = [...document.querySelectorAll("[data-view]")];
const numeric = new Set([
  "headway_min",
  "cars",
  "span_m",
  "ambient_c",
  "grade_pct",
]);
const live = ["http:", "https:"].includes(location.protocol);
const baseOptions = Object.fromEntries(new FormData(form));
const number = new Intl.NumberFormat("en", { maximumFractionDigits: 1 });
const metricDefinitions = [
  ["capital_usd", "Opening capital", (value) => dollars(value, "m")],
  [
    "annual_opex_usd",
    "Annual operations",
    (value) => dollars(value, "m") + "/yr",
  ],
  ["annual_train_km", "Annual train distance", (value) => n(value) + " km"],
  [
    "minimum_voltage_v",
    "Minimum collector voltage",
    (value) => n(value) + " V",
  ],
  ["peak_power_mw", "Peak wayside power", (value) => n(value) + " MW"],
];
const savedData = window.AIRPORT_SIMULATION?.cases;
const cases = (Array.isArray(savedData) ? savedData : []).filter(
  (data) => data?.inputs && data?.decision,
);
const auditLink = document.querySelector("#audit-link");
if (auditLink && cases.length > 1) auditLink.hidden = false;
const selectedCases = [];
let current;
let running = false;

function byId(id) {
  return document.getElementById(id);
}
function node(tag, text) {
  const result = document.createElement(tag);
  if (text != null) result.textContent = String(text);
  return result;
}
function n(value) {
  return number.format(value);
}
function dollars(value, suffix) {
  return (
    "USD " +
    n(suffix === "m" ? value / 1e6 : value) +
    (suffix ? " " + suffix : "")
  );
}
function valueOf(value, format = n) {
  return typeof value === "number" && Number.isFinite(value)
    ? format(value)
    : "Open";
}
function config(inputs) {
  return Object.fromEntries(
    Object.keys(baseOptions).map((key) => {
      const value = inputs[key] ?? baseOptions[key];
      return [key, numeric.has(key) ? Number(value) : String(value)];
    }),
  );
}
function keyOf(inputs) {
  return JSON.stringify(config(inputs));
}
function identityOf(data) {
  return data.identity?.evaluation_id || keyOf(data.inputs);
}
function selectedLabel(key, value) {
  const input = form.elements.namedItem(key);
  return (
    [...input.options].find((option) => option.value === String(value))
      ?.textContent || String(value)
  );
}
function description(inputs) {
  const i = config(inputs);
  return [
    selectedLabel("headway_min", i.headway_min),
    selectedLabel("cars", i.cars),
    selectedLabel("material", i.material),
    selectedLabel("span_m", i.span_m),
    selectedLabel("topology", i.topology),
    selectedLabel("demand", i.demand),
    selectedLabel("ambient_c", i.ambient_c),
    selectedLabel("grade_pct", i.grade_pct),
    selectedLabel("condition", i.condition),
  ].join(" · ");
}
function setStatus(message, error = false) {
  const text = byId("status");
  text.textContent = message;
  text.classList.toggle("error", error);
}
function setControls(inputs) {
  for (const [key, value] of Object.entries(config(inputs)))
    form.elements.namedItem(key).value = value;
}
function refreshSaved() {
  const select = byId("saved");
  select.replaceChildren(node("option", "Choose a scenario"));
  select.firstChild.value = "";
  for (const [index, data] of cases.entries()) {
    const option = node("option", data.label || description(data.inputs));
    option.value = String(index);
    select.append(option);
  }
  const index = cases.indexOf(current);
  if (index >= 0) select.value = String(index);
}
function definition(label, value) {
  const pair = node("div");
  pair.append(node("dt", label), node("dd", value));
  return pair;
}

function routeSchematic() {
  const canvas = byId("route");
  const c = canvas.getContext("2d");
  c.strokeStyle = "#608490";
  c.lineWidth = 1;
  for (let i = 15; i <= 410; i += 19) {
    c.beginPath();
    c.moveTo(i, 25);
    c.lineTo(i, 110);
    c.stroke();
  }
  c.fillStyle = "#193d48";
  c.fillRect(15, 44, 390, 48);
  c.strokeStyle = "#74d0c8";
  c.lineWidth = 3;
  c.beginPath();
  c.moveTo(32, 68);
  c.lineTo(388, 68);
  c.stroke();
  for (let i = 0; i < 6; i++) {
    c.beginPath();
    c.arc(32 + i * 71.2, 68, i % 5 === 0 ? 7 : 4.5, 0, Math.PI * 2);
    c.fillStyle = i % 5 === 0 ? "#fec685" : "#adede6";
    c.fill();
  }
  c.font = "13px system-ui";
  c.fillStyle = "#dae9ee";
  c.fillText("Airport", 17, 130);
  c.textAlign = "center";
  c.fillText("12 km · 6 stations", 210, 130);
  c.textAlign = "right";
  c.fillText("Urban terminal", 407, 130);
}

function renderTrace(motion) {
  const points = (motion?.trace || []).filter(
    (row) => Number.isFinite(row.time_s) && Number.isFinite(row.source_mw),
  );
  byId("plot-section").hidden = points.length < 2;
  if (points.length < 2) return;
  const positions = points.flatMap((row) =>
    (row.trains || [])
      .filter(
        (train) => Number.isFinite(train.chainage_m) && train.chainage_m >= 0,
      )
      .map((train) => ({ value: train.chainage_m / 1000, time: row.time_s })),
  );
  byId("trace-picker").hidden = positions.length === 0;
  const distance =
    positions.length > 0 && byId("trace-mode").value === "distance";
  const unit = distance ? " km" : " MW";
  byId("trace-title").textContent = distance
    ? "Train positions over the operating day"
    : "Power over the operating day";
  byId("trace-description").textContent = distance
    ? "Sampled corridor chainage by local time."
    : "Sampled wayside supply power by local time.";
  const canvas = byId("trace");
  canvas.setAttribute(
    "aria-label",
    distance
      ? "Scatter chart of sampled train positions by time"
      : "Line chart of sampled wayside supply power by time",
  );
  const ctx = canvas.getContext("2d");
  const { width, height } = canvas;
  const [left, right, top, bottom] = [50, width - 12, 18, height - 32];
  const first = Math.min(...points.map((row) => row.time_s));
  const last = Math.max(...points.map((row) => row.time_s));
  const peak = Math.max(0, ...points.map((row) => row.source_mw));
  const maximum = distance
    ? Math.max(12, Math.ceil(Math.max(...positions.map((p) => p.value))))
    : Math.max(1, Math.ceil(peak));
  const x = (time) =>
    left + ((time - first) / Math.max(1, last - first)) * (right - left);
  const y = (power) => bottom - (power / maximum) * (bottom - top);
  ctx.clearRect(0, 0, width, height);
  ctx.font = "13px system-ui";
  ctx.fillStyle = "#465e68";
  ctx.strokeStyle = "#d5dfe2";
  ctx.lineWidth = 1;
  for (let i = 0; i < 5; i++) {
    const power = (i * maximum) / 4;
    ctx.beginPath();
    ctx.moveTo(left, y(power));
    ctx.lineTo(right, y(power));
    ctx.stroke();
    ctx.fillText(n(power) + unit, 0, y(power) + 4);
  }
  const clockLabel = (seconds) => {
    const hour = Math.floor(seconds / 3600) % 24;
    const minute = Math.floor(seconds / 60) % 60;
    return (
      String(hour).padStart(2, "0") + ":" + String(minute).padStart(2, "0")
    );
  };
  for (let i = 0; i < 5; i++) {
    const time = first + ((last - first) * i) / 4;
    ctx.fillText(clockLabel(time), x(time) - (i === 4 ? 35 : 14), height - 8);
  }
  if (distance) {
    ctx.fillStyle = "#08726c";
    for (const point of positions)
      ctx.fillRect(x(point.time) - 1.5, y(point.value) - 1.5, 3, 3);
  } else {
    ctx.beginPath();
    for (const [i, point] of points.entries())
      ctx[i ? "lineTo" : "moveTo"](x(point.time_s), y(point.source_mw));
    ctx.strokeStyle = "#08726c";
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  const sampling = clockLabel(first) + "–" + clockLabel(last);
  byId("trace-summary").textContent = distance
    ? positions.length + " train positions sampled between " + sampling + "."
    : points.length +
      " samples, " +
      sampling +
      ". Highest sampled value " +
      n(peak) +
      " MW.";
}

function renderEngineering(data) {
  const stages = data.stages || data.engineering || {};
  const vehicle = stages.vehicle || {};
  const motion = stages.motion || {};
  const civil = vehicle.selected_span || {};
  const passengers = stages.passengers || {};
  const production = stages.production || {};
  const corridor = stages.corridor || {};
  const groups = [
    [
      "Corridor service",
      [
        [
          "Route length",
          valueOf(
            corridor.route_km ?? corridor.distance_km ?? 12,
            (v) => n(v) + " km",
          ),
        ],
        [
          "Completed passenger workings",
          valueOf(motion.metrics?.completed_passenger_trips),
        ],
        [
          "Denied boarding attempts",
          valueOf(motion.metrics?.denied_boarding_attempts),
        ],
        [
          "Delivered energy intensity",
          valueOf(
            motion.energy_kwh_per_train_km,
            (v) => n(v) + " kWh/train-km",
          ),
        ],
      ],
    ],
    [
      "Vehicle and civil works",
      [
        [
          "Loaded train mass",
          valueOf(vehicle.loaded_train_kg, (v) => n(v / 1000) + " t"),
        ],
        [
          "Tare mass",
          valueOf(vehicle.tare_train_kg, (v) => n(v / 1000) + " t"),
        ],
        [
          "Opening beams",
          valueOf(production.quantities?.beams ?? civil.beams_1p8km),
        ],
        [
          "Service power margin",
          valueOf(vehicle.interfaces?.battery_margin_kwh, (v) => n(v) + " kWh"),
        ],
      ],
    ],
    [
      "Passenger movement and climate",
      [
        [
          "Full-train auxiliary demand",
          valueOf(passengers.auxiliary_kw, (v) => n(v) + " kW"),
        ],
        [
          "Thermal cooling requirement",
          valueOf(
            passengers.hvac?.required_cooling_kw_thermal,
            (v) => n(v) + " kW",
          ),
        ],
        [
          "Assisted transfer dwell",
          valueOf(
            passengers.door_exchange?.total_dwell_with_one_assisted_transfer_s,
            (v) => n(v) + " s",
          ),
        ],
        [
          "Waiting density",
          valueOf(
            passengers.station_movement?.waiting_density_people_m2,
            (v) => n(v) + " people/m²",
          ),
        ],
      ],
    ],
    [
      "Production and whole-life cost",
      [
        [
          "Modelled completion",
          valueOf(
            production.decision_summary
              ?.normal_last_modelled_completion_workday,
            (v) => n(v) + " workdays",
          ),
        ],
        [
          "Reduced-capacity completion",
          valueOf(
            production.scenarios?.["reduced-capacity"]?.last_completion_workday,
            (v) => n(v) + " workdays",
          ),
        ],
        [
          "Operating support per paid journey",
          valueOf(
            production.decision_summary
              ?.annual_subsidy_per_paid_journey_base_usd,
            (v) => dollars(v),
          ),
        ],
        [
          "Priced 30-year present value",
          valueOf(production.decision_summary?.priced_30y_pv_base_usd, (v) =>
            dollars(v, "m"),
          ),
        ],
      ],
    ],
  ];
  const container = byId("engineering-results");
  container.replaceChildren();
  for (const [title, rows] of groups) {
    const card = node("section");
    card.className = "card subsection";
    const fields = node("dl");
    fields.append(...rows.map(([label, value]) => definition(label, value)));
    card.append(node("h3", title), fields);
    container.append(card);
  }
  renderTrace(motion);
}

function compare() {
  const host = byId("comparison");
  const added =
    current &&
    selectedCases.some((data) => identityOf(data) === identityOf(current));
  byId("pin").disabled = added || selectedCases.length >= 4;
  byId("pin").textContent = added
    ? "Current case added"
    : selectedCases.length >= 4
      ? "Comparison is full"
      : "Add current case";
  byId("clear").hidden = !selectedCases.length;
  byId("compare-empty").hidden = Boolean(selectedCases.length);
  host.hidden = !selectedCases.length;
  if (!selectedCases.length) {
    host.replaceChildren();
    return;
  }
  const table = node("table");
  const head = node("thead");
  const headings = node("tr");
  headings.append(node("th", "Measure"));
  for (const data of selectedCases) {
    const heading = node("th", data.label || description(data.inputs));
    heading.scope = "col";
    headings.append(heading);
  }
  head.append(headings);
  const body = node("tbody");
  for (const [field, label, fmt] of metricDefinitions) {
    const row = node("tr");
    const header = node("th", label);
    header.scope = "row";
    row.append(
      header,
      ...selectedCases.map((data) =>
        node("td", valueOf(data.decision[field], fmt)),
      ),
    );
    body.append(row);
  }
  table.append(head, body);
  host.replaceChildren(table);
}

function render(data, message) {
  current = data;
  const decision = data.decision;
  const identity = data.identity || {};
  setControls(data.inputs);
  byId("result-content").hidden = false;
  byId("selected-summary").textContent = description(data.inputs);
  const eligibility = byId("eligibility");
  eligibility.textContent = decision.eligible
    ? "Eligible for comparison"
    : "Selection held";
  eligibility.classList.toggle("ready", Boolean(decision.eligible));
  byId("metrics").replaceChildren(
    ...metricDefinitions.map(([field, label, fmt]) =>
      definition(label, valueOf(decision[field], fmt)),
    ),
  );
  const holds = Array.isArray(decision.holds) ? decision.holds : [];
  const humanReadable = (item) => {
    const text = String(item);
    return /^[a-z0-9]+(?:_[a-z0-9]+)+$/.test(text)
      ? (text[0].toUpperCase() + text.slice(1))
          .replaceAll("_", " ")
          .replace(/^Dc /, "DC ")
      : text;
  };
  byId("holds").replaceChildren(
    ...(holds.length ? holds : ["No open items supplied in this case."]).map(
      (item) => node("li", humanReadable(item)),
    ),
  );
  byId("identity").replaceChildren(
    definition("Physical candidate", identity.physical_id || "Open"),
    definition("Evaluation", identity.evaluation_id || "Open"),
    definition("Parent candidate", identity.parent_candidate_id || "Open"),
  );
  const evidence =
    data.provenance ??
    Object.fromEntries(
      Object.entries(data.stages || data.engineering || {})
        .filter(([, stage]) => stage && typeof stage === "object")
        .map(([name, stage]) => [
          name,
          {
            evaluation_id: stage.evaluation_id,
            source_sha256: stage.source_sha256,
          },
        ]),
    );
  byId("provenance").textContent = JSON.stringify(evidence, null, 2);
  renderEngineering(data);
  compare();
  refreshSaved();
  setStatus(message);
}

async function request(body) {
  const response = await fetch("/api/airport-simulation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const type = response.headers.get("Content-Type") || "";
    const error = type.includes("json") ? await response.json() : null;
    const message =
      error?.error?.message || error?.error || error?.message || error?.reason;
    throw new Error(
      typeof message === "string"
        ? message
        : "Local API returned " +
            response.status +
            ". Start the workbench to evaluate new cases.",
    );
  }
  return response;
}

function busy(active) {
  running = active;
  for (const control of form.elements) control.disabled = active;
  byId("saved").disabled = active;
  byId("export").disabled = active || !live;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (running) return;
  const input = config(Object.fromEntries(new FormData(form)));
  const cached = cases.find((data) => keyOf(data.inputs) === keyOf(input));
  if (!live) {
    if (cached) render(cached, "Showing a saved scenario.");
    else {
      byId("saved").value = "";
      setStatus(
        "No saved scenario matches these inputs. Choose a saved scenario or start the local workbench. The results below still show the previous case.",
        true,
      );
    }
    return;
  }
  busy(true);
  setStatus("Evaluating the requested configuration…");
  try {
    const data = await (await request({ inputs: input })).json();
    if (!data?.inputs || !data?.decision)
      throw new Error("The API response has no scenario decision.");
    if (!cases.some((old) => identityOf(old) === identityOf(data)))
      cases.push(data);
    render(data, "Scenario evaluated by the local workbench.");
  } catch (error) {
    if (cached)
      render(
        cached,
        "Showing the matching saved scenario because the local evaluation failed.",
      );
    else
      setStatus(
        error.message +
          (current ? " The results below still show the previous case." : ""),
        true,
      );
  } finally {
    busy(false);
  }
});
form.addEventListener("change", () => {
  if (!current) return;
  if (keyOf(Object.fromEntries(new FormData(form))) === keyOf(current.inputs)) {
    refreshSaved();
    setStatus("Inputs match the displayed results.");
    return;
  }
  byId("saved").value = "";
  setStatus("Inputs changed. Evaluate to update the displayed results.");
});
byId("saved").addEventListener("change", ({ target }) => {
  if (target.value !== "")
    render(cases[Number(target.value)], "Showing a saved scenario.");
});
for (const active of viewButtons)
  active.addEventListener("click", () => {
    for (const button of viewButtons) {
      button.setAttribute("aria-pressed", String(button === active));
      byId(button.dataset.view).hidden = button !== active;
    }
  });
byId("pin").addEventListener("click", () => {
  if (
    current &&
    selectedCases.length < 4 &&
    !selectedCases.some((data) => identityOf(data) === identityOf(current))
  ) {
    selectedCases.push(current);
    compare();
  }
});
byId("clear").addEventListener("click", () => {
  selectedCases.length = 0;
  compare();
});
byId("export").addEventListener("click", async () => {
  if (!current || running || !live) return;
  busy(true);
  setStatus("Preparing the dossier for the displayed result…");
  try {
    const response = await request({
      inputs: config(current.inputs),
      export: true,
    });
    const file = await response.blob();
    const url = URL.createObjectURL(file);
    const anchor = node("a");
    anchor.href = url;
    anchor.download =
      "airport-simulation-" +
      identityOf(current)
        .slice(0, 12)
        .replace(/[^a-zA-Z0-9-]/g, "") +
      ".zip";
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setStatus("Dossier ZIP downloaded.");
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    busy(false);
  }
});
byId("trace-mode").addEventListener("change", () => {
  if (current) renderTrace((current.stages || current.engineering)?.motion);
});
byId("offline-help").hidden = live;
byId("mode").textContent = live
  ? "Local evaluation and saved cases"
  : "Offline saved cases";
byId("export").disabled = !live;
if (!live)
  byId("export").title = "Start the local workbench to export a dossier.";
routeSchematic();
if (cases.length) render(cases[0], "Showing the first published scenario.");
else
  setStatus(
    live
      ? "Set the inputs and evaluate a scenario."
      : "No saved scenario data was found beside this page.",
    !live,
  );
