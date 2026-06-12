const DATA_URL = "data/samawah-operations.json";
const CORE_STATUSES = ["open", "assigned", "in_progress", "ready_to_close", "hold", "closed"];
const DAILY_TASK_IDS = new Set(["rs-daily", "station-daily", "energy-daily", "systems-daily"]);
const WEEKLY_TASK_IDS = new Set([
  "rs-daily",
  "station-daily",
  "energy-daily",
  "systems-daily",
  "rs-weekly",
  "station-weekly",
  "track-weekly",
]);
const CORE_RECORD_KEYS = ["workOrders", "inspections", "defects", "audit"];

const state = {
  data: null,
  core: null,
  coreStore: {
    mode: "loading",
    label: "Storage: loading",
    apiUrl: "",
  },
  coreSave: {
    pending: "",
    inFlight: false,
  },
  activeTab: "dashboard",
  qaVisible: [],
  tasksVisible: [],
  assetsVisible: [],
  workOrdersVisible: [],
  selectedWorkOrderId: null,
};

document.addEventListener("DOMContentLoaded", async () => {
  bindTabs();
  bindFilters();
  bindExports();
  bindCoreActions();
  state.data = await loadData();
  state.core = await loadCoreState();
  setDefaultDates();
  renderAll();
});

async function loadData() {
  const response = await fetch(DATA_URL);
  if (!response.ok) {
    throw new Error(`Failed to load ${DATA_URL}`);
  }
  return response.json();
}

function bindTabs() {
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      activateTab(button.dataset.tab);
      history.replaceState(null, "", `#${button.dataset.tab}`);
    });
  });
  const initialTab = location.hash.replace("#", "");
  if (document.getElementById(initialTab)) {
    activateTab(initialTab);
    requestAnimationFrame(() => window.scrollTo(0, 0));
  }
}

function activateTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll(".tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === state.activeTab);
  });
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === state.activeTab);
  });
}

function bindFilters() {
  [
    "qaSearch",
    "qaDomain",
    "taskSearch",
    "taskType",
    "taskOwner",
    "assetSearch",
    "assetType",
    "assetLine",
    "coreSearch",
    "coreStatus",
  ].forEach((id) => {
    document.getElementById(id)?.addEventListener("input", renderTables);
  });
}

function bindExports() {
  document.querySelectorAll("[data-export]").forEach((button) => {
    button.addEventListener("click", () => {
      const kind = button.dataset.export;
      if (kind === "maintenance") return downloadCsv("maintenance-schedule.csv", state.data.maintenance_tasks);
      if (kind === "qa") return downloadCsv("qa-register.csv", state.data.qa_actions);
      if (kind === "qa-visible") return downloadCsv("qa-visible.csv", state.qaVisible);
      if (kind === "maintenance-visible") return downloadCsv("maintenance-visible.csv", state.tasksVisible);
      if (kind === "assets-visible") return downloadCsv("assets-visible.csv", state.assetsVisible);
      if (kind === "core-workorders") return downloadCsv("work-orders.csv", state.core.workOrders);
      if (kind === "core-defects") return downloadCsv("defects-ncr.csv", state.core.defects);
      if (kind === "core-audit") return downloadCsv("audit-trail.csv", state.core.audit);
    });
  });
}

function bindCoreActions() {
  document.getElementById("workOrderForm")?.addEventListener("submit", (event) => {
    event.preventDefault();
    createQuickWorkOrder();
  });
  document.getElementById("inspectionForm")?.addEventListener("submit", (event) => {
    event.preventDefault();
    saveInspection();
  });
  document.getElementById("seedCorePlan")?.addEventListener("click", generateDueWork);
  document.getElementById("refreshReconcile")?.addEventListener("click", renderReconciliation);
  document.getElementById("mergeLocalToSqlite")?.addEventListener("click", mergeLocalToSqlite);
  document.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    if (button.dataset.createTask) createWorkOrderFromTask(button.dataset.createTask);
    if (button.dataset.createQa) createWorkOrderFromQa(button.dataset.createQa);
    if (button.dataset.selectWo) selectWorkOrder(button.dataset.selectWo);
    if (button.dataset.advanceWo) advanceWorkOrder(button.dataset.advanceWo);
    if (button.dataset.holdWo) holdWorkOrder(button.dataset.holdWo);
    if (button.dataset.resolveDefect) resolveDefect(button.dataset.resolveDefect);
  });
}

function renderAll() {
  const { meta } = state.data;
  document.getElementById("cityName").textContent = meta.city_name;
  document.getElementById("cityCountry").textContent = meta.country;
  renderMetrics();
  renderFilters();
  renderTables();
  renderCharts();
  renderCore();
  renderApps();
}

function renderMetrics() {
  const totals = state.data.totals;
  const metrics = [
    ["Assets", totals.assets],
    ["Maintenance Tasks", totals.maintenance_tasks],
    ["QA Actions", totals.qa_actions],
    ["Trainsets", totals.trainsets],
    ["Stations", totals.stations],
  ];
  document.getElementById("metrics").innerHTML = metrics.map(([label, value]) => (
    `<article class="metric"><span>${escapeHtml(label)}</span><strong>${formatNumber(value)}</strong></article>`
  )).join("");
}

function renderFilters() {
  fillSelect("qaDomain", ["All domains", ...unique(state.data.qa_actions.map((r) => r.domain))]);
  fillSelect("taskType", ["All asset types", ...unique(state.data.maintenance_tasks.map((r) => r.asset_type))]);
  fillSelect("taskOwner", ["All owners", ...unique(state.data.maintenance_tasks.map((r) => r.owner))]);
  fillSelect("assetType", ["All asset types", ...unique(state.data.assets.map((r) => r.asset_type))]);
  fillSelect("assetLine", ["All lines", ...unique(state.data.assets.map((r) => r.line).filter(Boolean))]);
  fillSelect("coreStatus", ["All statuses", ...CORE_STATUSES]);
  document.querySelectorAll("#coreStatus option").forEach((option) => {
    if (option.value) option.textContent = statusLabel(option.value);
  });
  fillSelect("coreOwner", ["Owner", ...coreOwners()]);
  document.getElementById("coreAssetOptions").innerHTML = state.data.assets.map((asset) => (
    `<option value="${escapeAttr(asset.asset_id)}">${escapeHtml(asset.name)}</option>`
  )).join("");
}

function fillSelect(id, values) {
  const select = document.getElementById(id);
  if (!select || select.options.length) return;
  select.innerHTML = values.map((value, index) => (
    `<option value="${index === 0 ? "" : escapeAttr(value)}">${escapeHtml(value)}</option>`
  )).join("");
}

function renderTables() {
  renderQaTable();
  renderTaskTable();
  renderAssetTable();
  renderCoreTables();
}

function renderQaTable() {
  const search = norm(document.getElementById("qaSearch").value);
  const domain = document.getElementById("qaDomain").value;
  state.qaVisible = state.data.qa_actions.filter((row) => {
    if (domain && row.domain !== domain) return false;
    return matches(row, search, ["gate_id", "domain", "asset_id", "asset_name", "asset_type", "stage", "evidence_required"]);
  }).slice(0, 500);
  document.getElementById("qaTable").innerHTML = state.qaVisible.map((row) => (
    `<tr>
      <td><code>${escapeHtml(row.gate_id)}</code><br>${escapeHtml(row.asset_id)}</td>
      <td>${escapeHtml(row.domain)}</td>
      <td>${escapeHtml(row.asset_type)}<br>${escapeHtml(row.asset_name)}</td>
      <td>${escapeHtml(row.stage)}</td>
      <td>${escapeHtml(row.evidence_required)}</td>
      <td>${escapeHtml(row.release_authority)}<br>${statusTag(row.status)}</td>
      <td><button class="mini-button" type="button" data-create-qa="${escapeAttr(row.qa_uid)}">Open WO</button></td>
    </tr>`
  )).join("");
}

function renderTaskTable() {
  const search = norm(document.getElementById("taskSearch").value);
  const type = document.getElementById("taskType").value;
  const owner = document.getElementById("taskOwner").value;
  state.tasksVisible = state.data.maintenance_tasks.filter((row) => {
    if (type && row.asset_type !== type) return false;
    if (owner && row.owner !== owner) return false;
    return matches(row, search, ["asset_id", "asset_name", "asset_type", "line", "task_id", "scope", "owner", "next_due_basis"]);
  }).slice(0, 700);
  document.getElementById("taskTable").innerHTML = state.tasksVisible.map((row) => (
    `<tr>
      <td><code>${escapeHtml(row.asset_id)}</code><br>${escapeHtml(row.asset_name)}</td>
      <td>${escapeHtml(row.asset_type)}</td>
      <td><code>${escapeHtml(row.task_id)}</code><br>${escapeHtml(row.scope)}</td>
      <td>${escapeHtml(row.cadence)}<br>${escapeHtml(row.trigger)}</td>
      <td>${escapeHtml(row.owner)}</td>
      <td>${escapeHtml(row.next_due_basis)}</td>
      <td>${statusTag(row.severity)}</td>
      <td><button class="mini-button" type="button" data-create-task="${escapeAttr(row.task_uid)}">Open WO</button></td>
    </tr>`
  )).join("");
}

function renderAssetTable() {
  const search = norm(document.getElementById("assetSearch").value);
  const type = document.getElementById("assetType").value;
  const line = document.getElementById("assetLine").value;
  state.assetsVisible = state.data.assets.filter((row) => {
    if (type && row.asset_type !== type) return false;
    if (line && row.line !== line) return false;
    return matches(row, search, ["asset_id", "source_id", "asset_type", "subtype", "name", "line", "station", "location"]);
  }).slice(0, 700);
  document.getElementById("assetTable").innerHTML = state.assetsVisible.map((row) => (
    `<tr>
      <td><code>${escapeHtml(row.asset_id)}</code><br>${escapeHtml(row.source_id)}</td>
      <td>${escapeHtml(row.asset_type)}<br>${escapeHtml(row.subtype)}</td>
      <td>${escapeHtml(row.name)}</td>
      <td>${escapeHtml(row.line || "-")}</td>
      <td>${escapeHtml(chainage(row))}</td>
      <td>${escapeHtml(row.location)}</td>
    </tr>`
  )).join("");
}

function renderCharts() {
  renderBarList("maintenanceChart", countBy(state.data.maintenance_tasks, "asset_type"));
  renderBarList("qaChart", countBy(state.data.qa_actions, "domain"));
}

function renderBarList(id, counts) {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const max = Math.max(...entries.map(([, value]) => value), 1);
  document.getElementById(id).innerHTML = entries.map(([label, value]) => {
    const width = Math.max(3, Math.round((value / max) * 100));
    return `<div class="bar-row">
      <span>${escapeHtml(label)}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
      <strong>${formatNumber(value)}</strong>
    </div>`;
  }).join("");
}

function renderCore() {
  renderCoreMetrics();
  renderCoreTables();
  renderSelectedWorkOrder();
  renderAuditTrail();
  renderReconciliation();
}

function renderCoreMetrics() {
  const workOrders = state.core.workOrders;
  const defects = state.core.defects;
  const today = todayString();
  const open = workOrders.filter((row) => row.status !== "closed").length;
  const due = workOrders.filter((row) => row.status !== "closed" && row.due_date <= today).length;
  const hold = workOrders.filter((row) => row.status === "hold").length;
  const openDefects = defects.filter((row) => row.status !== "resolved").length;
  const inspections = state.core.inspections.length;
  const metrics = [
    ["Open Work", open],
    ["Due Now", due],
    ["On Hold", hold],
    ["Open Defects", openDefects],
    ["Evidence Records", inspections],
  ];
  document.getElementById("coreMetrics").innerHTML = metrics.map(([label, value]) => (
    `<article class="metric"><span>${escapeHtml(label)}</span><strong>${formatNumber(value)}</strong></article>`
  )).join("");
  document.getElementById("coreStorageStatus").textContent = state.coreStore.label;
}

function renderCoreTables() {
  renderWorkOrders();
  renderDefects();
  renderSelectedWorkOrder();
  renderAuditTrail();
}

function renderWorkOrders() {
  const search = norm(document.getElementById("coreSearch").value);
  const status = document.getElementById("coreStatus").value;
  const rows = state.core.workOrders
    .filter((row) => {
      if (status && row.status !== status) return false;
      return matches(row, search, ["id", "asset_id", "asset_name", "asset_type", "title", "owner", "status", "priority"]);
    })
    .sort(compareWorkOrders)
    .slice(0, 700);
  state.workOrdersVisible = rows;
  if (!rows.length) {
    document.getElementById("coreWorkTable").innerHTML = emptyRow(7, "No work orders");
    return;
  }
  document.getElementById("coreWorkTable").innerHTML = rows.map((row) => {
    const selected = row.id === state.selectedWorkOrderId ? " selected-row" : "";
    return `<tr class="${selected}">
      <td><code>${escapeHtml(row.id)}</code><br>${escapeHtml(row.source_type)}</td>
      <td><code>${escapeHtml(row.asset_id)}</code><br>${escapeHtml(row.asset_name)}</td>
      <td>${escapeHtml(row.title)}<br>${statusTag(row.priority)}</td>
      <td>${escapeHtml(row.owner)}</td>
      <td>${escapeHtml(row.due_date || "-")}</td>
      <td>${statusTag(row.status)}</td>
      <td class="action-cell">
        <button class="mini-button" type="button" data-select-wo="${escapeAttr(row.id)}">View</button>
        <button class="mini-button" type="button" data-advance-wo="${escapeAttr(row.id)}">${escapeHtml(nextActionLabel(row.status))}</button>
        <button class="mini-button danger-button" type="button" data-hold-wo="${escapeAttr(row.id)}">Hold</button>
      </td>
    </tr>`;
  }).join("");
}

function renderDefects() {
  const rows = state.core.defects
    .slice()
    .sort((a, b) => String(a.status).localeCompare(String(b.status)) || String(b.created_at).localeCompare(String(a.created_at)))
    .slice(0, 200);
  if (!rows.length) {
    document.getElementById("defectTable").innerHTML = emptyRow(5, "No defects");
    return;
  }
  document.getElementById("defectTable").innerHTML = rows.map((row) => (
    `<tr>
      <td><code>${escapeHtml(row.id)}</code><br>${statusTag(row.severity)}</td>
      <td><code>${escapeHtml(row.asset_id)}</code><br>${escapeHtml(row.asset_name)}</td>
      <td>${escapeHtml(row.finding)}<br><span class="muted-text">${escapeHtml(row.owner)}</span></td>
      <td>${statusTag(row.status)}<br><span class="muted-text">Due ${escapeHtml(row.due_date)}</span></td>
      <td>${row.status === "resolved" ? "" : `<button class="mini-button" type="button" data-resolve-defect="${escapeAttr(row.id)}">Resolve</button>`}</td>
    </tr>`
  )).join("");
}

function renderSelectedWorkOrder() {
  const wo = currentWorkOrder();
  const panel = document.getElementById("selectedWorkOrder");
  const form = document.getElementById("inspectionForm");
  if (!wo) {
    panel.innerHTML = `<p class="empty-state">No work order selected</p>`;
    setFormDisabled(form, true);
    return;
  }
  setFormDisabled(form, false);
  const recent = state.core.inspections.find((row) => row.wo_id === wo.id);
  panel.innerHTML = `<dl class="summary-list">
    <div><dt>Work</dt><dd><code>${escapeHtml(wo.id)}</code> ${escapeHtml(wo.title)}</dd></div>
    <div><dt>Asset</dt><dd><code>${escapeHtml(wo.asset_id)}</code> ${escapeHtml(wo.asset_name)}</dd></div>
    <div><dt>Owner</dt><dd>${escapeHtml(wo.owner)}</dd></div>
    <div><dt>Status</dt><dd>${statusTag(wo.status)}</dd></div>
    <div><dt>Latest</dt><dd>${recent ? `${escapeHtml(recent.result)} - ${escapeHtml(recent.note || recent.reading || recent.evidence_ref || "recorded")}` : "No evidence yet"}</dd></div>
  </dl>`;
}

function renderAuditTrail() {
  const rows = state.core.audit.slice(-30).reverse();
  if (!rows.length) {
    document.getElementById("auditTrail").innerHTML = `<p class="empty-state">No audit events</p>`;
    return;
  }
  document.getElementById("auditTrail").innerHTML = rows.map((row) => (
    `<div class="audit-row">
      <time>${escapeHtml(row.at)}</time>
      <strong>${escapeHtml(row.action)}</strong>
      <code>${escapeHtml(row.ref)}</code>
      <span>${escapeHtml(row.detail)}</span>
    </div>`
  )).join("");
}

function renderReconciliation() {
  const summary = reconciliationSummary();
  const mergeButton = document.getElementById("mergeLocalToSqlite");
  mergeButton.disabled = state.coreStore.mode !== "sqlite" || summary.localRecords === 0 || summary.localOnly === 0 && summary.conflicts === 0;
  const message = state.coreStore.mode === "sqlite"
    ? "Merge imports browser-local fallback records into SQLite and keeps the newest copy on id conflicts."
    : "Serve with scripts/ops-core-server.py to reconcile browser-local records into SQLite.";
  const items = [
    ["SQLite", summary.sqliteRecords],
    ["Browser Local", summary.localRecords],
    ["Local Only", summary.localOnly],
    ["SQLite Only", summary.sqliteOnly],
    ["Conflicts", summary.conflicts],
    ["Status", state.coreStore.mode === "sqlite" ? "ready" : "local"],
  ];
  document.getElementById("reconcileSummary").innerHTML = [
    ...items.map(([label, value]) => (
      `<div class="reconcile-item"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`
    )),
    `<p class="reconcile-message">${escapeHtml(message)}</p>`,
  ].join("");
}

function createQuickWorkOrder() {
  const asset = findAsset(document.getElementById("coreAssetInput").value);
  if (!asset) return;
  const title = document.getElementById("coreTitle").value.trim();
  if (!title) return;
  const wo = createWorkOrder({
    source_type: "manual",
    source_uid: "",
    asset_id: asset.asset_id,
    asset_name: asset.name,
    asset_type: asset.asset_type,
    title,
    owner: document.getElementById("coreOwner").value || "operations control",
    priority: document.getElementById("corePriority").value,
    due_date: document.getElementById("coreDueDate").value || todayString(),
  });
  state.selectedWorkOrderId = wo.id;
  document.getElementById("coreTitle").value = "";
  saveCoreState();
  renderCore();
}

function createWorkOrderFromTask(uid) {
  const task = state.data.maintenance_tasks.find((row) => row.task_uid === uid);
  if (!task) return;
  const wo = createWorkOrder(workOrderFromTask(task, document.getElementById("coreDueDate").value || todayString()));
  state.selectedWorkOrderId = wo.id;
  saveCoreState();
  renderCore();
}

function createWorkOrderFromQa(uid) {
  const qa = state.data.qa_actions.find((row) => row.qa_uid === uid);
  if (!qa) return;
  const wo = createWorkOrder(workOrderFromQa(qa, document.getElementById("coreDueDate").value || todayString()));
  state.selectedWorkOrderId = wo.id;
  saveCoreState();
  renderCore();
}

function generateDueWork() {
  const scope = document.getElementById("corePlanScope").value;
  const dueDate = document.getElementById("corePlanDate").value || todayString();
  const rows = state.data.maintenance_tasks.filter((row) => {
    if (scope === "all") return true;
    if (scope === "weekly") return WEEKLY_TASK_IDS.has(row.task_id);
    return DAILY_TASK_IDS.has(row.task_id);
  });
  let created = 0;
  rows.forEach((task) => {
    const before = state.core.workOrders.length;
    createWorkOrder(workOrderFromTask(task, dueDate), { audit: false, save: false });
    if (state.core.workOrders.length > before) created += 1;
  });
  logAudit("generated", "due-work", `${created} work orders for ${dueDate}`);
  saveCoreState();
  renderCore();
}

function createWorkOrder(payload, options = {}) {
  const existing = payload.source_uid ? state.core.workOrders.find((row) => (
    row.source_type === payload.source_type &&
    row.source_uid === payload.source_uid &&
    row.due_date === payload.due_date
  )) : null;
  if (existing) return existing;
  const now = timestamp();
  const wo = {
    id: nextCoreId("workOrder"),
    city: state.data.meta.city_slug,
    status: "open",
    created_at: now,
    updated_at: now,
    closed_at: "",
    source_type: payload.source_type,
    source_uid: payload.source_uid || "",
    asset_id: payload.asset_id,
    asset_name: payload.asset_name,
    asset_type: payload.asset_type,
    title: payload.title,
    owner: payload.owner || "operations control",
    priority: payload.priority || "routine",
    due_date: payload.due_date || todayString(),
  };
  state.core.workOrders.unshift(wo);
  if (options.audit !== false) logAudit("created", wo.id, `${wo.asset_id} ${wo.title}`);
  if (options.save !== false) saveCoreState();
  return wo;
}

function workOrderFromTask(task, dueDate) {
  return {
    source_type: "maintenance",
    source_uid: task.task_uid,
    asset_id: task.asset_id,
    asset_name: task.asset_name,
    asset_type: task.asset_type,
    title: task.scope,
    owner: task.owner,
    priority: task.severity === "routine" ? "routine" : "attention",
    due_date: dueDate,
  };
}

function workOrderFromQa(qa, dueDate) {
  return {
    source_type: "qa",
    source_uid: qa.qa_uid,
    asset_id: qa.asset_id,
    asset_name: qa.asset_name,
    asset_type: qa.asset_type,
    title: `${qa.gate_id}: ${qa.hold_point}`,
    owner: qa.release_authority,
    priority: "safety",
    due_date: dueDate,
  };
}

function selectWorkOrder(id) {
  state.selectedWorkOrderId = id;
  renderCore();
}

function advanceWorkOrder(id) {
  const wo = state.core.workOrders.find((row) => row.id === id);
  if (!wo) return;
  const next = nextStatus(wo.status);
  wo.status = next;
  wo.updated_at = timestamp();
  if (next === "closed") wo.closed_at = wo.updated_at;
  state.selectedWorkOrderId = id;
  logAudit("status", id, statusLabel(next));
  saveCoreState();
  renderCore();
}

function holdWorkOrder(id) {
  const wo = state.core.workOrders.find((row) => row.id === id);
  if (!wo) return;
  wo.status = "hold";
  wo.updated_at = timestamp();
  state.selectedWorkOrderId = id;
  logAudit("hold", id, "work stopped pending defect/authority");
  saveCoreState();
  renderCore();
}

function saveInspection() {
  const wo = currentWorkOrder();
  if (!wo) return;
  const now = timestamp();
  const result = document.getElementById("inspectionResult").value;
  const severity = document.getElementById("inspectionSeverity").value;
  const inspection = {
    id: nextCoreId("inspection"),
    wo_id: wo.id,
    asset_id: wo.asset_id,
    asset_name: wo.asset_name,
    result,
    severity,
    reading: document.getElementById("inspectionReading").value.trim(),
    evidence_ref: document.getElementById("inspectionEvidence").value.trim(),
    note: document.getElementById("inspectionNote").value.trim(),
    recorded_at: now,
  };
  state.core.inspections.unshift(inspection);
  if (result === "pass") {
    wo.status = "ready_to_close";
  } else if (result === "watch") {
    wo.status = wo.status === "open" ? "in_progress" : wo.status;
  } else {
    wo.status = "hold";
    createDefectFromInspection(wo, inspection);
  }
  wo.updated_at = now;
  logAudit("evidence", wo.id, result);
  saveCoreState();
  clearInspectionForm();
  renderCore();
}

function createDefectFromInspection(wo, inspection) {
  const defect = {
    id: nextCoreId("defect"),
    wo_id: wo.id,
    inspection_id: inspection.id,
    asset_id: wo.asset_id,
    asset_name: wo.asset_name,
    severity: inspection.severity,
    finding: inspection.note || inspection.reading || wo.title,
    owner: wo.owner,
    status: "open",
    created_at: inspection.recorded_at,
    due_date: defectDueDate(inspection.severity),
    resolved_at: "",
  };
  state.core.defects.unshift(defect);
  logAudit("defect", defect.id, `${defect.severity} finding on ${defect.asset_id}`);
}

function resolveDefect(id) {
  const defect = state.core.defects.find((row) => row.id === id);
  if (!defect) return;
  defect.status = "resolved";
  defect.resolved_at = timestamp();
  logAudit("resolved", id, defect.asset_id);
  saveCoreState();
  renderCore();
}

function reconciliationSummary() {
  const local = loadLocalCoreState();
  const summary = {
    sqliteRecords: totalCoreRecords(state.core),
    localRecords: totalCoreRecords(local),
    localOnly: 0,
    sqliteOnly: 0,
    conflicts: 0,
  };
  CORE_RECORD_KEYS.forEach((key) => {
    const sqliteRows = byRecordId(state.core[key]);
    const localRows = byRecordId(local[key]);
    localRows.forEach((localRow, id) => {
      const sqliteRow = sqliteRows.get(id);
      if (!sqliteRow) {
        summary.localOnly += 1;
      } else if (stableJson(sqliteRow) !== stableJson(localRow)) {
        summary.conflicts += 1;
      }
    });
    sqliteRows.forEach((_, id) => {
      if (!localRows.has(id)) summary.sqliteOnly += 1;
    });
  });
  return summary;
}

function mergeLocalToSqlite() {
  if (state.coreStore.mode !== "sqlite") return;
  const local = loadLocalCoreState();
  const before = reconciliationSummary();
  if (!before.localRecords) return;
  const merged = emptyCoreState();
  CORE_RECORD_KEYS.forEach((key) => {
    merged[key] = mergeRecordRows(state.core[key], local[key]);
  });
  merged.counters = reconcileCounters(state.core, local, merged);
  state.core = merged;
  logAudit("reconciled", "browser-local", `${before.localOnly} local-only, ${before.conflicts} conflicts`);
  saveCoreState();
  try {
    localStorage.setItem(coreStorageKey(), JSON.stringify(state.core));
  } catch {
    return;
  }
  renderCore();
}

function mergeRecordRows(sqliteRows, localRows) {
  const rows = [...sqliteRows];
  const indexById = new Map(rows.map((row, index) => [row.id, index]).filter(([id]) => id));
  localRows.forEach((localRow) => {
    if (!localRow.id) return;
    const index = indexById.get(localRow.id);
    if (index === undefined) {
      indexById.set(localRow.id, rows.length);
      rows.push(localRow);
      return;
    }
    const sqliteRow = rows[index];
    if (recordTimestamp(localRow) > recordTimestamp(sqliteRow)) {
      rows[index] = localRow;
    }
  });
  return rows.sort(compareCoreRecords);
}

function reconcileCounters(sqliteState, localState, mergedState) {
  const counters = { ...emptyCoreState().counters };
  Object.keys(counters).forEach((kind) => {
    counters[kind] = Math.max(sqliteState.counters[kind] || 1, localState.counters[kind] || 1, nextCounterFromRows(kind, mergedState));
  });
  return counters;
}

function nextCounterFromRows(kind, core) {
  const config = {
    workOrder: ["workOrders", "WO"],
    inspection: ["inspections", "INSP"],
    defect: ["defects", "NCR"],
    audit: ["audit", "AUD"],
  }[kind];
  if (!config) return 1;
  const [key, prefix] = config;
  const maxId = core[key].reduce((max, row) => {
    const match = String(row.id || "").match(new RegExp(`^${prefix}-(\\d+)$`));
    return match ? Math.max(max, Number(match[1])) : max;
  }, 0);
  return maxId + 1;
}

function loadLocalCoreState() {
  try {
    const raw = localStorage.getItem(coreStorageKey());
    return raw ? normalizeCoreState(JSON.parse(raw)) : emptyCoreState();
  } catch {
    return emptyCoreState();
  }
}

function totalCoreRecords(core) {
  return CORE_RECORD_KEYS.reduce((sum, key) => sum + core[key].length, 0);
}

function byRecordId(rows) {
  return new Map(rows.filter((row) => row.id).map((row) => [row.id, row]));
}

function compareCoreRecords(a, b) {
  return recordTimestamp(a).localeCompare(recordTimestamp(b)) || String(a.id).localeCompare(String(b.id));
}

function recordTimestamp(row) {
  return String(row.updated_at || row.recorded_at || row.created_at || row.resolved_at || row.at || "");
}

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function renderApps() {
  const apps = state.data.applications;
  const byId = Object.fromEntries(apps.map((app) => [app.id, app]));
  document.getElementById("occApp").innerHTML = renderAppCard(byId.occ);
  document.getElementById("simApp").innerHTML = renderAppCard(byId.simulator);
  document.getElementById("backofficeApps").innerHTML = apps
    .filter((app) => ["cbm", "afc", "historian", "qa-maintenance"].includes(app.id))
    .map(renderAppCard)
    .join("");
}

function renderAppCard(app) {
  const web = app.web_command ? `<div class="web-row"><dt>Web</dt><dd><code>${escapeHtml(app.web_command)}</code></dd></div>` : "";
  return `<article class="app-card">
    <div>
      <p class="eyebrow">${escapeHtml(app.category)}</p>
      <h2>${escapeHtml(app.name)}</h2>
      <p class="app-summary">${escapeHtml(app.summary)}</p>
    </div>
    <dl>
      <div><dt>Status</dt><dd>${statusTag(app.status)}</dd></div>
      <div><dt>Native</dt><dd><code>${escapeHtml(app.native_command)}</code></dd></div>
      ${web}
    </dl>
    <a class="text-button" href="../../${escapeAttr(app.docs)}">Docs</a>
  </article>`;
}

async function loadCoreState() {
  const fallback = emptyCoreState();
  const apiUrl = coreApiUrl();
  try {
    const response = await fetch(apiUrl, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (response.ok) {
      const payload = await response.json();
      state.coreStore = {
        mode: "sqlite",
        label: "Storage: SQLite",
        apiUrl,
      };
      return normalizeCoreState(payload.state || payload);
    }
  } catch {
    // The static server has no API; local fallback keeps the portal usable.
  }

  state.coreStore = {
    mode: "local",
    label: "Storage: browser local",
    apiUrl: "",
  };
  try {
    const raw = localStorage.getItem(coreStorageKey());
    if (!raw) return fallback;
    return normalizeCoreState(JSON.parse(raw));
  } catch {
    return fallback;
  }
}

function saveCoreState() {
  if (state.coreStore.mode === "sqlite" && state.coreStore.apiUrl) {
    state.coreSave.pending = JSON.stringify(state.core);
    flushCoreSave();
    return;
  }
  try {
    localStorage.setItem(coreStorageKey(), JSON.stringify(state.core));
  } catch {
    return;
  }
}

async function flushCoreSave() {
  if (state.coreSave.inFlight || !state.coreSave.pending) return;
  state.coreSave.inFlight = true;
  const body = state.coreSave.pending;
  state.coreSave.pending = "";
  try {
    const response = await fetch(state.coreStore.apiUrl, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body,
    });
    if (!response.ok) throw new Error(`SQLite save failed: ${response.status}`);
    state.coreStore.label = "Storage: SQLite";
    renderCoreMetrics();
  } catch {
    state.coreStore = {
      mode: "local",
      label: "Storage: browser local fallback",
      apiUrl: "",
    };
    try {
      localStorage.setItem(coreStorageKey(), JSON.stringify(state.core));
    } catch {
      return;
    }
    renderCoreMetrics();
  } finally {
    state.coreSave.inFlight = false;
    if (state.coreStore.mode === "sqlite" && state.coreSave.pending) {
      flushCoreSave();
    }
  }
}

function emptyCoreState() {
  return {
    workOrders: [],
    inspections: [],
    defects: [],
    audit: [],
    counters: {
      workOrder: 1,
      inspection: 1,
      defect: 1,
      audit: 1,
    },
  };
}

function normalizeCoreState(value) {
  const core = emptyCoreState();
  if (!value || typeof value !== "object") return core;
  core.workOrders = Array.isArray(value.workOrders) ? value.workOrders : [];
  core.inspections = Array.isArray(value.inspections) ? value.inspections : [];
  core.defects = Array.isArray(value.defects) ? value.defects : [];
  core.audit = Array.isArray(value.audit) ? value.audit : [];
  core.counters = { ...core.counters, ...(value.counters || {}) };
  return core;
}

function coreStorageKey() {
  return `osr.ops-core.${state.data.meta.city_slug}`;
}

function coreApiUrl() {
  return `/api/ops-core/${encodeURIComponent(state.data.meta.city_slug)}`;
}

function nextCoreId(kind) {
  const prefixes = {
    workOrder: "WO",
    inspection: "INSP",
    defect: "NCR",
    audit: "AUD",
  };
  const next = state.core.counters[kind] || 1;
  state.core.counters[kind] = next + 1;
  return `${prefixes[kind]}-${String(next).padStart(5, "0")}`;
}

function logAudit(action, ref, detail) {
  state.core.audit.push({
    id: nextCoreId("audit"),
    at: timestamp(),
    action,
    ref,
    detail,
  });
}

function setDefaultDates() {
  const today = todayString();
  ["corePlanDate", "coreDueDate"].forEach((id) => {
    const input = document.getElementById(id);
    if (input && !input.value) input.value = today;
  });
}

function todayString(offsetDays = 0) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}

function timestamp() {
  return new Date().toISOString();
}

function defectDueDate(severity) {
  if (severity === "safety") return todayString();
  if (severity === "service") return todayString(2);
  return todayString(7);
}

function currentWorkOrder() {
  if (!state.selectedWorkOrderId) {
    const first = state.core.workOrders.find((row) => row.status !== "closed") || state.core.workOrders[0];
    state.selectedWorkOrderId = first ? first.id : null;
  }
  return state.core.workOrders.find((row) => row.id === state.selectedWorkOrderId) || null;
}

function findAsset(value) {
  const search = norm(value).trim();
  if (!search) return null;
  return state.data.assets.find((asset) => norm(asset.asset_id) === search || norm(asset.source_id) === search) ||
    state.data.assets.find((asset) => norm(asset.name).includes(search) || norm(asset.asset_id).includes(search));
}

function coreOwners() {
  return unique([
    ...state.data.maintenance_tasks.map((row) => row.owner),
    ...state.data.qa_actions.map((row) => row.release_authority),
    "operations control",
    "owner engineer",
  ]);
}

function nextStatus(status) {
  if (status === "open") return "assigned";
  if (status === "assigned") return "in_progress";
  if (status === "in_progress") return "ready_to_close";
  if (status === "ready_to_close") return "closed";
  if (status === "hold") return "assigned";
  return "closed";
}

function nextActionLabel(status) {
  if (status === "closed") return "Closed";
  return status === "hold" ? "Release" : "Next";
}

function statusLabel(status) {
  return String(status || "").replace(/_/g, " ");
}

function compareWorkOrders(a, b) {
  if (a.status === "closed" && b.status !== "closed") return 1;
  if (b.status === "closed" && a.status !== "closed") return -1;
  return String(a.due_date).localeCompare(String(b.due_date)) || String(b.created_at).localeCompare(String(a.created_at));
}

function setFormDisabled(form, disabled) {
  if (!form) return;
  [...form.elements].forEach((element) => {
    element.disabled = disabled;
  });
}

function clearInspectionForm() {
  ["inspectionReading", "inspectionEvidence", "inspectionNote"].forEach((id) => {
    document.getElementById(id).value = "";
  });
  document.getElementById("inspectionResult").value = "pass";
  document.getElementById("inspectionSeverity").value = "minor";
}

function emptyRow(colspan, text) {
  return `<tr><td colspan="${colspan}" class="empty-cell">${escapeHtml(text)}</td></tr>`;
}

function downloadCsv(filename, rows) {
  if (!rows || !rows.length) return;
  const headers = Object.keys(rows[0]);
  const body = [
    headers.join(","),
    ...rows.map((row) => headers.map((h) => csvCell(row[h])).join(",")),
  ].join("\n");
  const blob = new Blob([body + "\n"], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function csvCell(value) {
  const text = String(value ?? "");
  if (!/[",\n]/.test(text)) return text;
  return `"${text.replace(/"/g, '""')}"`;
}

function statusTag(status) {
  const cssClass = String(status ?? "").toLowerCase().replace(/[^a-z0-9_-]+/g, "-");
  return `<span class="tag ${escapeAttr(cssClass)}">${escapeHtml(statusLabel(status))}</span>`;
}

function countBy(rows, key) {
  return rows.reduce((acc, row) => {
    const value = row[key] || "unknown";
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function matches(row, search, keys) {
  if (!search) return true;
  return keys.some((key) => norm(row[key]).includes(search));
}

function chainage(row) {
  if (!row.km_start && !row.km_end) return "-";
  if (row.km_start === row.km_end) return `${row.km_start} km`;
  return `${row.km_start}-${row.km_end} km`;
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => String(a).localeCompare(String(b)));
}

function formatNumber(value) {
  return Number(value).toLocaleString("en-US");
}

function norm(value) {
  return String(value ?? "").toLowerCase();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/'/g, "&#39;");
}
