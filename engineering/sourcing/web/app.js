"use strict";

const PAGE_SIZE = 25;
const state = {
  runsOffset: 0,
  recordsOffset: 0,
  recordsKind: "requirement",
  selectedRun: null,
  detailSection: "requirements",
  detailOffset: 0
};

const $ = (id) => document.getElementById(id);
const text = (node, value) => { node.textContent = value === null || value === undefined || value === "" ? "—" : String(value); };
const shortId = (value) => typeof value === "string" ? value.slice(0, 12) + "…" : "—";
const fmt = (value) => typeof value === "number" ? value.toLocaleString() : value === null || value === undefined ? "Unknown" : String(value);
const detailText = (value) => value === null || value === undefined ? "—" : typeof value === "object" ? JSON.stringify(value) : String(value);

async function getJson(path) {
  const response = await fetch(path, { method: "GET", credentials: "same-origin", cache: "no-store" });
  if (!response.ok) throw new Error("Local review endpoint returned " + response.status);
  return response.json();
}

function cell(row, value, className) {
  const node = document.createElement("td");
  if (className) node.className = className;
  text(node, value);
  row.appendChild(node);
  return node;
}

function setHeaders(tableId, labels) {
  const head = $(tableId);
  head.replaceChildren();
  const row = document.createElement("tr");
  labels.forEach((label) => {
    const th = document.createElement("th");
    text(th, label);
    row.appendChild(th);
  });
  head.appendChild(row);
}

function setEmpty(bodyId, message, span) {
  const body = $(bodyId);
  body.replaceChildren();
  const row = document.createElement("tr");
  const td = document.createElement("td");
  td.className = "empty";
  td.colSpan = span;
  text(td, message);
  row.appendChild(td);
  body.appendChild(row);
}

function metric(label, value, unknown) {
  const card = document.createElement("div");
  card.className = "metric";
  const name = document.createElement("span");
  name.className = "metric-label";
  text(name, label);
  const number = document.createElement("span");
  number.className = "metric-value" + (unknown ? " unknown" : "");
  text(number, value);
  card.append(name, number);
  return card;
}

async function loadStatus() {
  const status = await getJson("/api/status");
  text($("connection-state"), status.database_available ? "Database available · read only" : "Database not initialized");
  const cards = $("summary-cards");
  cards.replaceChildren();
  const counts = status.counts || {};
  const latest = status.recent_runs && status.recent_runs.length ? status.recent_runs[0] : null;
  const latestSummary = latest ? latest.summary : null;
  const coverage = latestSummary || {};
  cards.append(
    metric("Evaluation runs", counts.run || 0, false),
    metric("Supplied requirements", coverage.requirement_count ?? "No run", false),
    metric("Priced requirement groups", coverage.priced_requirement_count ?? "Unknown", !latest),
    metric("Unknown quantity", coverage.unknown_quantity_requirements ?? "Unknown", !latest),
    metric("Complete installed cost", "Unknown", true)
  );
  text($("scope-note"), status.note || "Complete installed and whole-life costs remain unknown.");
}

function runValues(run) {
  const summary = run.summary || {};
  return {
    date: run.estimate_date,
    candidate: shortId(run.candidate_id),
    count: summary.requirement_count,
    priced: summary.priced_requirement_count,
    unknown: summary.unknown_quantity_requirements,
    subtotal: summary.known_catalogue_subtotal === null ? "Unknown" : String(summary.known_catalogue_subtotal) + " " + run.currency
  };
}

async function loadRuns() {
  const body = $("runs-body");
  const page = await getJson("/api/runs?limit=" + PAGE_SIZE + "&offset=" + state.runsOffset);
  body.replaceChildren();
  if (!page.items.length) {
    setEmpty("runs-body", "No evaluation runs yet.", 7);
  } else {
    page.items.forEach((run) => {
      const values = runValues(run);
      const row = document.createElement("tr");
      cell(row, values.date);
      cell(row, values.candidate, "mono");
      cell(row, fmt(values.count));
      cell(row, fmt(values.priced));
      cell(row, fmt(values.unknown));
      cell(row, values.subtotal, "mono");
      const action = document.createElement("td");
      const button = document.createElement("button");
      button.type = "button";
      text(button, "View evidence");
      button.addEventListener("click", () => {
        state.selectedRun = run.run_id;
        state.detailOffset = 0;
        text($("detail-title"), "Evidence · " + shortId(run.run_id));
        $("run-detail").hidden = false;
        loadDetails();
        $("run-detail").scrollIntoView({ behavior: "smooth", block: "start" });
      });
      action.appendChild(button);
      row.appendChild(action);
      body.appendChild(row);
    });
  }
  const start = page.total ? page.offset + 1 : 0;
  const end = Math.min(page.offset + page.items.length, page.total);
  text($("runs-page-label"), start + "–" + end + " of " + page.total);
  $("runs-prev").disabled = page.offset === 0;
  $("runs-next").disabled = page.next_offset === null;
}

const recordColumns = {
  requirement: ["Requirement", "Namespace", "Description", "Quantity", "Category"],
  product: ["Product", "Manufacturer", "Part number", "Description", "Supply scope", "Specification facts"],
  offer: ["Product ID", "Price date", "Currency", "Class", "Quantity unit", "Packaging", "Order constraints", "Price tiers"],
  source: ["Publisher", "Source kind", "Retrieved", "Access"],
  assessment: ["Requirement ID", "Product", "Status", "Holds"],
  rfq: ["Category", "Candidate", "Items", "Enabled", "Supplier email"],
  benchmark: ["Benchmark", "Date", "Unit", "Value"],
  process: ["Process", "Material family", "Sources"]
};

function recordRow(kind, item) {
  const row = document.createElement("tr");
  if (kind === "requirement") {
    cell(row, item.requirement_key);
    cell(row, item.namespace);
    cell(row, item.description);
    cell(row, item.quantity === null ? "Unknown" : String(item.quantity) + " " + (item.quantity_unit || ""));
    cell(row, item.category);
  } else if (kind === "product") {
    cell(row, item.product_key);
    cell(row, item.manufacturer);
    cell(row, item.part_number);
    cell(row, item.description);
    cell(row, item.supply_scope);
    cell(row, detailText(item.specifications));
  } else if (kind === "offer") {
    cell(row, shortId(item.product_id), "mono");
    cell(row, item.price_date);
    cell(row, item.currency);
    cell(row, item.source_class);
    cell(row, item.quantity_unit);
    cell(row, detailText(item.packaging));
    cell(row, "MOQ " + fmt(item.minimum_order_quantity) + " · multiple " + fmt(item.order_multiple));
    cell(row, detailText(item.tiers));
  } else if (kind === "source") {
    cell(row, item.publisher);
    cell(row, item.source_kind);
    cell(row, item.retrieved_at);
    cell(row, item.access);
  } else if (kind === "assessment") {
    cell(row, shortId(item.requirement_id), "mono");
    cell(row, item.product_key || shortId(item.product_id));
    cell(row, item.status);
    cell(row, Array.isArray(item.holds) ? item.holds.join("; ") : "None");
  } else if (kind === "rfq") {
    cell(row, item.category);
    cell(row, shortId(item.candidate_id), "mono");
    cell(row, item.requested_item_count ?? item.requirement_count);
    cell(row, "Disabled");
    cell(row, "No");
  } else if (kind === "benchmark") {
    cell(row, item.benchmark_key);
    cell(row, item.observation_date);
    cell(row, item.quantity_unit);
    cell(row, item.unit_price);
  } else {
    cell(row, item.process_key || item.process_name);
    cell(row, item.material_family);
    cell(row, Array.isArray(item.source_ids) ? item.source_ids.length : 0);
  }
  return row;
}

async function loadRecords() {
  const kind = state.recordsKind;
  setHeaders("records-head", recordColumns[kind]);
  const page = await getJson("/api/records?kind=" + encodeURIComponent(kind) + "&limit=" + PAGE_SIZE + "&offset=" + state.recordsOffset);
  const body = $("records-body");
  body.replaceChildren();
  if (!page.items.length) setEmpty("records-body", "No " + kind + " records on this page.", recordColumns[kind].length);
  else page.items.forEach((item) => body.appendChild(recordRow(kind, item)));
  const start = page.total ? page.offset + 1 : 0;
  const end = Math.min(page.offset + page.items.length, page.total);
  text($("records-page-label"), start + "–" + end + " of " + page.total);
  $("records-prev").disabled = page.offset === 0;
  $("records-next").disabled = page.next_offset === null;
  $("record-rfq-note").hidden = kind !== "rfq";
}

const detailColumns = {
  requirements: ["Requirement", "Namespace", "Description", "Quantity", "Category"],
  technical_assessments: ["Product", "Status", "Holds", "Scope"],
  price_assessments: ["Price date", "Currency", "Status", "Holds"],
  RFQ_drafts: ["Category", "Requirement groups", "Requested items", "Enabled", "Email"],
  redesign_tasks: ["Requirement", "Product", "Status", "Reason"]
};

function detailRow(section, item) {
  const row = document.createElement("tr");
  if (section === "requirements") {
    cell(row, item.requirement_key);
    cell(row, item.namespace);
    cell(row, item.description);
    cell(row, item.quantity === null ? "Unknown" : String(item.quantity) + " " + (item.quantity_unit || ""));
    cell(row, item.category);
  } else if (section === "technical_assessments") {
    cell(row, item.product_key || shortId(item.product_id));
    cell(row, item.status);
    cell(row, Array.isArray(item.holds) ? item.holds.join("; ") : "None");
    cell(row, item.suitability_scope);
  } else if (section === "price_assessments") {
    cell(row, item.estimate_date || item.source_price_date);
    cell(row, item.target_currency || item.listed_currency);
    cell(row, item.status);
    cell(row, Array.isArray(item.holds) ? item.holds.join("; ") : "None");
  } else if (section === "RFQ_drafts") {
    cell(row, item.category);
    cell(row, item.requirement_count);
    cell(row, item.requested_item_count);
    cell(row, "Disabled");
    cell(row, "No");
  } else {
    cell(row, shortId(item.requirement_id));
    cell(row, item.product_id ? shortId(item.product_id) : "—");
    cell(row, item.status);
    cell(row, item.reason || item.task_type || "Review required");
  }
  return row;
}

async function loadDetails() {
  if (!state.selectedRun) return;
  const section = state.detailSection;
  setHeaders("detail-head", detailColumns[section]);
  $("rfq-disabled").hidden = section !== "RFQ_drafts";
  const query = new URLSearchParams({ section, limit: String(PAGE_SIZE), offset: String(state.detailOffset) });
  const page = await getJson("/api/runs/" + encodeURIComponent(state.selectedRun) + "/items?" + query);
  const body = $("detail-body");
  body.replaceChildren();
  if (!page.items.length) setEmpty("detail-body", "No evidence in this section.", detailColumns[section].length);
  else page.items.forEach((item) => body.appendChild(detailRow(section, item)));
  const start = page.total ? page.offset + 1 : 0;
  const end = Math.min(page.offset + page.items.length, page.total);
  text($("detail-page-label"), start + "–" + end + " of " + page.total);
  $("detail-prev").disabled = page.offset === 0;
  $("detail-next").disabled = page.next_offset === null;
}

function bind() {
  $("runs-prev").addEventListener("click", () => { state.runsOffset = Math.max(0, state.runsOffset - PAGE_SIZE); loadRuns(); });
  $("runs-next").addEventListener("click", () => { state.runsOffset += PAGE_SIZE; loadRuns(); });
  $("records-prev").addEventListener("click", () => { state.recordsOffset = Math.max(0, state.recordsOffset - PAGE_SIZE); loadRecords(); });
  $("records-next").addEventListener("click", () => { state.recordsOffset += PAGE_SIZE; loadRecords(); });
  $("record-kind").addEventListener("change", (event) => { state.recordsKind = event.target.value; state.recordsOffset = 0; loadRecords(); });
  $("detail-section").addEventListener("change", (event) => { state.detailSection = event.target.value; state.detailOffset = 0; loadDetails(); });
  $("detail-prev").addEventListener("click", () => { state.detailOffset = Math.max(0, state.detailOffset - PAGE_SIZE); loadDetails(); });
  $("detail-next").addEventListener("click", () => { state.detailOffset += PAGE_SIZE; loadDetails(); });
}

async function start() {
  bind();
  try {
    await loadStatus();
    await Promise.all([loadRuns(), loadRecords()]);
  } catch (error) {
    text($("connection-state"), "Local database unavailable");
    text($("scope-note"), error.message);
    setEmpty("runs-body", "The local review service could not load runs.", 7);
    setEmpty("records-body", "The local review service could not load records.", 5);
  }
}

document.addEventListener("DOMContentLoaded", start);
