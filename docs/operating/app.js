const modules = [
  ["Projects & delivery", "Projects, tasks, timesheets, costs and accountable delivery.", "project"],
  ["Purchasing & suppliers", "Requests, quotations, purchase orders and receipt of materials.", "purchase-order"],
  ["Stock & manufacturing", "Warehouses, bills of materials, production orders and job cards.", "work-order"],
  ["Assets & maintenance", "Asset ownership, service schedules, repairs and maintenance costs.", "asset-maintenance"],
  ["Finance & accounting", "Invoices, payments, budgets, cost centres and accounting reports.", "purchase-invoice"],
  ["People & payroll", "Employees, recruitment, attendance, leave, expenses and payroll in Frappe HR.", "employee"],
];
let erpBase = "";
let twins = [];

try {
  const response = await fetch("/api/operating");
  if (!response.ok) throw new Error("Operating platform configuration is unavailable.");
  const config = await response.json();
  const base = new URL(config.url);
  if (!["http:", "https:"].includes(base.protocol) || base.username || base.password) throw new Error("Invalid operating platform address.");
  erpBase = base.href.replace(/\/$/, "");
  const workspace = document.getElementById("workspace");
  workspace.href = `${base.href.replace(/\/$/, "")}/app/opensourcerail`;
  workspace.hidden = false;
  document.getElementById("connection").textContent = `ERPNext at ${base.origin}. Sign in with your ERPNext account.`;
  for (const [title, summary, route] of modules) {
    const card = document.createElement("article");
    card.className = "module";
    const heading = document.createElement("h2");
    heading.textContent = title;
    const description = document.createElement("p");
    description.textContent = summary;
    const link = document.createElement("a");
    link.textContent = "Open in ERPNext ↗";
    link.href = `${base.href.replace(/\/$/, "")}/app/${route}`;
    link.target = "_blank";
    link.rel = "noopener";
    card.append(heading, description, link);
    document.getElementById("modules").append(card);
  }
} catch (error) {
  document.getElementById("connection").textContent = `${error.message} Start the OSR Workbench to use this page.`;
}

document.getElementById("refreshTwins").addEventListener("click", loadTwins);
document.getElementById("twinSelector").addEventListener("change", renderTwin);
await loadTwins();

async function loadTwins() {
  const status = document.getElementById("twinStatus");
  const selector = document.getElementById("twinSelector");
  const selectedProject = twins[Number(selector.value)]?.project;
  try {
    const response = await fetch("/api/operating/twins");
    if (!response.ok) throw new Error("City feedback is unavailable on this server.");
    const payload = await response.json();
    twins = payload.snapshots || [];
    selector.replaceChildren();
    if (!twins.length) throw new Error("No city feedback has been exported yet. The city deployment guide explains how to connect a baseline.");
    twins.forEach((twin, index) => {
      const option = document.createElement("option");
      option.value = index;
      option.textContent = `${twin.city} · ${twin.company} · ${twin.engineering_revision} · release ${twin.operating_release}`;
      selector.append(option);
    });
    const wanted = new URLSearchParams(location.search).get("city");
    const chosen = twins.findIndex(t => selectedProject ? t.project === selectedProject : t.city === wanted);
    selector.value = chosen >= 0 ? chosen : 0;
    selector.disabled = false;
    renderTwin();
  } catch (error) {
    selector.disabled = true;
    status.textContent = error.message;
    document.getElementById("twinSummary").replaceChildren();
    document.getElementById("twinCategories").replaceChildren();
    document.getElementById("twinReadiness").replaceChildren();
    document.getElementById("businessFlow").hidden = true;
    document.getElementById("componentsFlow").hidden = true;
    document.getElementById("assetWork").hidden = true;
  }
}

function renderTwin() {
  const twin = twins[Number(document.getElementById("twinSelector").value)];
  if (!twin) return;
  const age = Date.now() - new Date(twin.observed_at).getTime();
  document.getElementById("twinStatus").textContent =
    `Snapshot ${twin.observed_at}${age > 3600000 ? " · more than one hour old" : ""}. Refresh view reads the latest exported ERP snapshot.`;
  const container = document.getElementById("twinSummary");
  container.replaceChildren();
  const metrics = document.createElement("div");
  metrics.className = "twin-metrics";
  for (const [label, value] of [["Tasks", twin.task_count], ["Completed", twin.task_status.Completed || 0],
    ["Recorded hours", twin.actual_hours], ["Task cost", `${twin.task_cost} ${twin.currency}`]]) {
    const item = document.createElement("div");
    const number = document.createElement("strong");
    number.textContent = value;
    item.append(number, document.createTextNode(label));
    metrics.append(item);
  }
  container.append(metrics);
  if (erpBase) {
    const link = document.createElement("a");
    link.href = `${erpBase}/app/project/${encodeURIComponent(twin.project)}`;
    link.textContent = "Open this project in ERPNext ↗";
    link.target = "_blank";
    link.rel = "noopener";
    container.append(link);
  }
  renderStatusTable("twinCategories", "Work category", twin.categories);
  const readiness = document.getElementById("twinReadiness");
  readiness.replaceChildren();
  if (twin.readiness) {
    const text = document.createElement("p");
    text.textContent = `Work needing attention: ${twin.readiness.overdue} overdue · ${twin.readiness.undated} without due dates · ${twin.readiness.unassigned} unassigned. Counts can overlap and exclude completed or cancelled tasks.`;
    readiness.append(text);
  }
  const business = Object.fromEntries(Object.entries(twin.business_documents || {}).map(([name, values]) =>
    [name, values.available ? {Draft: values.draft, Submitted: values.submitted, Cancelled: values.cancelled} : {Unavailable: "access or project link"}]));
  renderStatusTable("businessFlowRows", "Native ERP document", business);
  document.getElementById("businessFlow").hidden = !Object.keys(business).length;
  const components = Object.fromEntries(Object.entries(twin.components || {}).map(([name, entry]) =>
    [name, entry.available ? (Object.keys(entry.states).length ? entry.states : {Records: 0}) : {Unavailable: 'access restricted'}]));
  renderStatusTable('componentsFlowRows', 'Operating component', components);
  document.getElementById('componentsFlow').hidden = !Object.keys(components).length;
  renderStatusTable("assetWorkRows", "Railway asset", twin.asset_work);
  document.getElementById("assetWork").hidden = !Object.keys(twin.asset_work).length;
}

function renderStatusTable(id, title, groups) {
  const table = document.createElement("table");
  const header = table.createTHead().insertRow();
  for (const text of [title, "Visible ERP task status"]) {
    const cell = document.createElement("th");
    cell.textContent = text;
    header.append(cell);
  }
  const body = table.createTBody();
  for (const [name, counts] of Object.entries(groups)) {
    const row = body.insertRow();
    row.insertCell().textContent = name;
    row.insertCell().textContent = Object.entries(counts).map(([status, count]) => `${status}: ${count}`).join(" · ");
  }
  document.getElementById(id).replaceChildren(table);
}
