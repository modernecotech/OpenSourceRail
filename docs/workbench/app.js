const MODES = new Set(["design", "simulation", "training", "live"]);
const ROLES = new Set(["designer", "dispatcher", "maintainer", "reviewer"]);
const registry = await fetch("/workbench/modules.json").then(r => r.json());
const MODULES = new Set(registry.modules.map(m => m.id));
const services = await fetch("/api/workbench/services").then(r => r.json());
const buttons = document.getElementById("moduleButtons");
for (const group of [...new Set(registry.modules.map(m => m.group))]) {
  const section = document.createElement("div"); section.className = "module-group";
  const label = document.createElement("small"); label.textContent = group; section.append(label);
  for (const module of registry.modules.filter(m => m.group === group)) {
    const button = document.createElement("button"); button.dataset.module = module.id;
    button.textContent = module.label; section.append(button);
  }
  buttons.append(section);
}
const params = new URLSearchParams(location.search);
const bootstrap = await fetch("/api/workbench").then((response) => response.json());

const context = {
  schema_version: 1,
  city: valid(params.get("city"), /^[a-z0-9][a-z0-9-]{0,63}$/) || bootstrap.city,
  environment: params.get("environment") === "physical" ? "physical" : "simulation",
  mode: MODES.has(params.get("mode")) ? params.get("mode") : "design",
  role: ROLES.has(params.get("role")) ? params.get("role") : "designer",
  actor: valid(params.get("actor"), /^[A-Za-z0-9][A-Za-z0-9 ._@-]{1,119}$/) || "local-user",
};
setOptional("revision", params.get("revision"), /^osr-[a-f0-9]{16}$/);
setOptional("baseline_sha256", params.get("baseline_sha256"), /^[a-f0-9]{64}$/);
setOptional("run_id", params.get("run_id"), /^run-[a-f0-9]{16}$/);
setOptional("selected_asset", params.get("selected_asset"), /^.{1,160}$/);
if (context.mode === "live" && !context.baseline_sha256) context.mode = "training";

let activeModule = MODULES.has(params.get("module")) ? params.get("module") : "overview";
const frame = document.getElementById("moduleFrame");
let operationsOverride = sessionStorage.getItem(`osr:twin:${context.city}`) || "";
let twinJob = null;
let catalogue = [];
let detailPath = "";
let navigationId = 0;
document.getElementById("reloadModule").onclick = () => navigate(activeModule, detailPath);
document.getElementById("citySelector").onchange = event => {
  updateContext({ city: event.target.value });
  // Do not leave another city's native records visible if resolving the new scope fails.
  frame.src = "about:blank";
  document.getElementById("openNative").removeAttribute("href");
  enforceAccess();
};

document.getElementById("role").value = context.role;
document.getElementById("mode").value = context.mode;
document.getElementById("actor").value = context.actor;
document.getElementById("actor").addEventListener("change", (event) => {
  updateContext({ actor: event.target.value });
});
document.getElementById("role").addEventListener("change", (event) => {
  updateContext({ role: event.target.value });
  enforceAccess();
});
document.getElementById("mode").addEventListener("change", (event) => {
  if (event.target.value === "live" && !context.baseline_sha256) {
    event.target.value = context.mode;
    return;
  }
  updateContext({ mode: event.target.value, environment: event.target.value === "live" ? "physical" : "simulation" });
  enforceAccess();
});
document.querySelectorAll("[data-module]").forEach((button) => {
  button.addEventListener("click", () => navigate(button.dataset.module));
});
document.getElementById("occHandoff").addEventListener("click", () => {
  updateContext({ mode: "training", role: context.role === "designer" ? "reviewer" : context.role });
  navigate("occ");
});
document.getElementById("generateTwin").addEventListener("click", generateTwin);
document.getElementById("openTwin").addEventListener("click", openGeneratedTwin);

window.addEventListener("message", (event) => {
  const expectedOrigin = new URL(frame.src, location.href).origin;
  if (event.origin !== expectedOrigin || event.source !== frame.contentWindow) return;
  // Native business apps may navigate to a linked asset but cannot grant railway authority.
  if (event.origin !== location.origin) {
    if (event.data?.type === "osr:navigate" && event.data.module === "lifecycle") {
      updateContext({city:event.data.context?.city, selected_asset:event.data.context?.selected_asset,environment:event.data.context?.environment});
      navigate("lifecycle");
    }
    return;
  }
  if (event.data?.type === "osr:open-link") { openToolLink(event.data.url); return; }
  if (event.data?.type === "osr:context") updateContext(event.data.context || {});
  if (event.data?.type === "osr:navigate" && MODULES.has(event.data.module)) {
    updateContext(event.data.context || {});
    navigate(event.data.module);
  }
});
frame.addEventListener("load", () => {
  if (new URL(frame.src || location.href).origin === location.origin) frame.contentWindow?.postMessage({ type: "osr:context", context: { ...context } }, location.origin);
});

async function navigate(module, path = "") {
  if (!isAllowed(module)) {
    document.getElementById("moduleScope").textContent = `This view is unavailable for ${context.city}, ${context.mode} and ${context.role}. Railway controls belong to ${bootstrap.city}.`;
    return;
  }
  const requestId = ++navigationId;
  const selectedCity = context.city;
  const spec = registry.modules.find(m => m.id === module);
  let cityStatus;
  if (!path && ["erp", "fuxa"].includes(spec.service)) {
    document.getElementById("moduleScope").textContent = "Resolving city workspace…";
    try {
      const response = await fetch('/api/workbench/city?' + new URLSearchParams({city:context.city,environment:context.environment}));
      if (!response.ok) throw new Error('City deployment status unavailable');
      cityStatus = await response.json();
    } catch (error) {
      if(requestId === navigationId) document.getElementById("moduleScope").textContent = error.message;
      return;
    }
    if (requestId !== navigationId || selectedCity !== context.city) return;
    if (spec.service === "erp") {
      path = cityStatus.erp.routes[module] || "";
      if (["tasks","procurement","receipts","manufacturing","stock","issues","finance"].includes(module) && !path) {
        document.getElementById("moduleScope").textContent = `No unambiguous ERP project for ${context.city}. Open City execution or Projects to configure it.`;
        return;
      }
    }
    if (spec.service === "fuxa") {
      const site = cityStatus.supervision.sites.find(site => context.selected_asset === site || context.selected_asset?.startsWith(site + ':')) || cityStatus.supervision.preferred_site;
      if (!site) {
        document.getElementById("moduleScope").textContent = `No supervision package for ${context.city} / ${context.environment}.`;
        return;
      }
      path = '/home/?' + new URLSearchParams({viewName:`${context.city} · ${site} · ${context.environment}`});
    }
  }
  activeModule = module;
  detailPath = path;
  const query = contextQuery();
  const routes = {
    studio: `/studio/?${query}`,
    simulator: `/simulator/?${query}`,
    occ: `/occ/?${query}`,
    operations: `/operations/?data=${encodeURIComponent(operationsData())}&${query}#core`,
  };
  const environment = context.environment;
  routes.lifecycle = `/docs/lifecycle/?${new URLSearchParams({city:context.city,asset:context.selected_asset || "",environment})}`;
  routes.operating = `/docs/operating/?${query}`;
  routes['engineering-change'] = `/engineering/changes/?${query}`;
  routes.overview = `/workbench/hub/?${query}`;
  const base = spec.service === "local" ? location.origin : services[spec.service];
  frame.src = routes[module] || new URL(path || spec.path, base).href;
  document.getElementById("openNative").href = frame.src;
  document.getElementById("moduleTitle").textContent = spec.label;
  document.getElementById("moduleScope").textContent = spec.service === "erp"
    ? (cityStatus?.erp.routes[module] ? `${context.city} · ERP project ${cityStatus.erp.project || "not yet linked"}${cityStatus.erp.stale ? " · feedback unavailable or over one hour old" : ""} · native ERP permissions` : "Native ERP permissions · organisation-wide records; City execution provides project-linked actuals.")
    : spec.service === "fuxa" ? `${context.city} · ${context.environment} · verify the named display in FUXA; package preparation does not prove import or connectivity.`
    : "Shared city and asset context";
  history.replaceState(null, "", `/?module=${activeModule}&${contextQuery()}${path ? '&tool_path='+encodeURIComponent(path) : ''}`);
  render();
}

function updateContext(patch) {
  if (valid(patch.city, /^[a-z0-9][a-z0-9-]{0,63}$/) && patch.city !== context.city) {
    navigationId++;
    context.city = patch.city;
    for (const key of ["revision", "baseline_sha256", "run_id", "selected_asset"]) delete context[key];
    if (context.mode === "live") context.mode = "training";
    operationsOverride = sessionStorage.getItem(`osr:twin:${context.city}`) || "";
  }
  // Approval and simulation context belongs to the selected design revision.
  if (valid(patch.revision, /^osr-[a-f0-9]{16}$/) && patch.revision !== context.revision) {
    delete context.baseline_sha256;
    delete context.run_id;
  }
  if (valid(patch.baseline_sha256, /^[a-f0-9]{64}$/) && patch.baseline_sha256 !== context.baseline_sha256) {
    delete context.run_id;
  }
  if (["simulation", "physical"].includes(patch.environment)) context.environment = patch.environment;
  if (MODES.has(patch.mode)) context.mode = patch.mode;
  if (ROLES.has(patch.role)) context.role = patch.role;
  if (valid(patch.actor, /^[A-Za-z0-9][A-Za-z0-9 ._@-]{1,119}$/)) context.actor = patch.actor;
  assignOptional("revision", patch.revision, /^osr-[a-f0-9]{16}$/);
  assignOptional("baseline_sha256", patch.baseline_sha256, /^[a-f0-9]{64}$/);
  assignOptional("run_id", patch.run_id, /^run-[a-f0-9]{16}$/);
  assignOptional("selected_asset", patch.selected_asset, /^.{1,160}$/);
  if (context.mode === "live" && !context.baseline_sha256) context.mode = "training";
  document.getElementById("role").value = context.role;
  document.getElementById("mode").value = context.mode;
  document.getElementById("actor").value = context.actor;
  history.replaceState(null, "", `/?module=${activeModule}&${contextQuery()}`);
  render();
  if (new URL(frame.src || location.href).origin === location.origin) frame.contentWindow?.postMessage({ type: "osr:context", context: { ...context } }, location.origin);
}

async function enforceAccess() {
  if (!isAllowed(activeModule)) {
    activeModule = context.mode === "live" && isAllowed("occ") ? "occ" : "operations";
  }
  await navigate(activeModule);
}

function isAllowed(module) {
  if (!["studio", "simulator", "occ"].includes(module)) return MODULES.has(module);
  if (context.city !== bootstrap.city) return false;
  if (module === "studio") return ["designer", "reviewer"].includes(context.role) && ["design", "simulation"].includes(context.mode);
  if (module === "simulator") return ["designer", "dispatcher", "reviewer"].includes(context.role) && context.mode !== "live";
  if (module === "occ") {
    const modeAllowed = ["simulation", "training", "live"].includes(context.mode);
    const liveBaselineReady = context.mode !== "live" || Boolean(context.baseline_sha256);
    return ["dispatcher", "maintainer", "reviewer"].includes(context.role) && modeAllowed && liveBaselineReady;
  }
  return false;
}

function render() {
  document.getElementById("citySelector").value = context.city;
  document.getElementById("contextCity").textContent = context.city;
  document.getElementById("contextEnvironment").textContent = context.environment;
  document.getElementById("contextRevision").textContent = context.revision || "not selected";
  document.getElementById("contextBaseline").textContent = context.baseline_sha256?.slice(0, 16) || "not approved";
  document.getElementById("contextRun").textContent = context.run_id || "not run";
  document.getElementById("contextAsset").textContent = context.selected_asset || "none";
  document.querySelectorAll("[data-module]").forEach((button) => {
    button.disabled = !isAllowed(button.dataset.module);
    button.title = ["studio", "simulator", "occ"].includes(button.dataset.module) && context.city !== bootstrap.city
      ? `This Workbench control workspace is bound to ${bootstrap.city}. Start a Workbench with --project for the required city.` : "";
    button.classList.toggle("active", button.dataset.module === activeModule);
  });
  const banner = document.getElementById("safetyBanner");
  banner.classList.toggle("live", context.mode === "live");
  banner.textContent = context.mode === "live"
    ? "LIVE CONTROL — OCC commands require an approved baseline, authenticated role and signed audit path."
    : context.mode === "training"
      ? "TRAINING — deterministic replay only; no command reaches a live railway."
      : "PLANNING — design and simulation cannot issue movement authorities or live OCC commands.";
  document.getElementById("occHandoff").hidden = !context.run_id || !isAllowedWith("occ", "training", context.role === "designer" ? "reviewer" : context.role);
}

function isAllowedWith(module, mode, role) {
  const before = { mode: context.mode, role: context.role };
  context.mode = mode;
  context.role = role;
  const allowed = isAllowed(module);
  Object.assign(context, before);
  return allowed;
}

function contextQuery() {
  const output = new URLSearchParams();
  Object.entries(context).forEach(([key, value]) => output.set(key, String(value)));
  return output.toString();
}

function operationsData() {
  const city = catalogue.find(c => c.slug === context.city);
  return operationsOverride || city?.operations_data || (context.city === bootstrap.city ? bootstrap.operations_data : "");
}

async function loadTwinCatalogue() {
  try {
    const payload = await fetch("/api/twins/catalogue").then(checkedJson);
    catalogue = payload.cities;
    const globalSelector = document.getElementById("citySelector");
    globalSelector.replaceChildren(...catalogue.map(city => new Option(`${city.country} · ${city.name}`, city.slug)));
    globalSelector.value = context.city;
    const selector = document.getElementById("twinCity");
    selector.innerHTML = payload.cities.map((city) =>
      `<option value="${escapeHtml(city.slug)}">${escapeHtml(city.country)} · ${escapeHtml(city.name)} · ${escapeHtml(city.rolling_stock_family)}</option>`
    ).join("");
    if (payload.cities.some((city) => city.slug === context.city)) selector.value = context.city;
    document.getElementById("twinStatus").textContent = `${payload.cities.length} cities ready`;
  } catch (error) {
    document.getElementById("twinStatus").textContent = error.message;
    document.getElementById("generateTwin").disabled = true;
  }
}

async function loadPortfolio() {
  try {
    const payload = await fetch("/api/portfolio").then(checkedJson);
    const osr = payload.open_source_rail;
    const cases = payload.foreign_turnkey_comparator.cases;
    document.getElementById("portfolioHeadline").textContent =
      `${percent(osr.local_domestic_share)} domestic value · ${money(osr.imported_external_capital_usd)} external capital`;
    document.getElementById("portfolioScope").textContent =
      `${payload.scope.city_count} cities in ${payload.scope.country_count} countries. Read-only planning evidence; expand to compare controlled sensitivities.`;
    document.getElementById("portfolioTotal").textContent = money(osr.total_capex_usd);
    document.getElementById("portfolioLocal").textContent =
      `${money(osr.local_domestic_value_usd)} · ${percent(osr.local_domestic_share)}`;
    document.getElementById("portfolioExternal").textContent =
      `${money(osr.imported_external_capital_usd)} · ${percent(osr.imported_external_share)}`;
    document.getElementById("portfolioCases").innerHTML = ["low", "default", "high"].map((caseName) => {
      const row = cases[caseName];
      return `<tr><td>${escapeHtml(caseName[0].toUpperCase() + caseName.slice(1))} · ${row.price_multiplier.toFixed(1)}×</td><td>${money(row.turnkey_total_usd)}</td><td>${money(row.turnkey_external_capital_usd)}</td><td>${money(row.external_capital_avoided_usd)} · ${percent(row.external_capital_reduction)}</td><td>${money(row.external_capital_plus_interest_avoided_usd)}</td></tr>`;
    }).join("");
    document.getElementById("portfolioCaveat").textContent = payload.caveats.join(" ");
  } catch (error) {
    document.getElementById("portfolioHeadline").textContent = error.message;
  }
}

async function generateTwin() {
  const slug = document.getElementById("twinCity").value;
  const button = document.getElementById("generateTwin");
  button.disabled = true;
  document.getElementById("openTwin").hidden = true;
  try {
    twinJob = await fetch(`/api/twins/generate/${encodeURIComponent(slug)}`, { method: "POST" }).then(checkedJson);
    renderTwinJob();
    pollTwinJob();
  } catch (error) {
    twinJob = { status: "failed", progress_percent: 100, error: error.message };
    renderTwinJob();
    button.disabled = false;
  }
}

async function pollTwinJob() {
  if (!twinJob || !["queued", "running"].includes(twinJob.status)) return;
  await new Promise((resolve) => window.setTimeout(resolve, 500));
  try {
    twinJob = await fetch(`/api/twins/jobs/${encodeURIComponent(twinJob.id)}`).then(checkedJson);
    renderTwinJob();
    if (["queued", "running"].includes(twinJob.status)) pollTwinJob();
  } catch (error) {
    twinJob = { ...twinJob, status: "failed", progress_percent: 100, error: error.message };
    renderTwinJob();
  }
}

function renderTwinJob() {
  if (!twinJob) return;
  const progress = Number(twinJob.progress_percent || 0);
  document.getElementById("twinProgress").style.width = `${Math.max(0, Math.min(100, progress))}%`;
  const totals = twinJob.summary?.totals;
  document.getElementById("twinStatus").textContent = twinJob.error
    || (totals
      ? `${twinJob.phase} · ${totals.work_packages.toLocaleString()} work packages · $${Math.round(totals.planned_capex_usd).toLocaleString()} planned CAPEX`
      : `${twinJob.phase} · ${progress}%`);
  document.getElementById("generateTwin").disabled = ["queued", "running"].includes(twinJob.status);
  document.getElementById("openTwin").hidden = twinJob.status !== "completed";
}

function openGeneratedTwin() {
  if (!twinJob?.operations_data) return;
  operationsOverride = twinJob.operations_data;
  sessionStorage.setItem(`osr:twin:${twinJob.city}`, operationsOverride);
  updateContext({ city: twinJob.city });
  navigate("operations");
}

async function checkedJson(response) {
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[character]);
}

function money(value) {
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(Number(value));
}

function percent(value) {
  return new Intl.NumberFormat("en", {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(Number(value));
}

function setOptional(key, value, pattern) {
  const checked = valid(value, pattern);
  if (checked) context[key] = checked;
}

function assignOptional(key, value, pattern) {
  if (value === undefined) return;
  const checked = valid(String(value), pattern);
  if (checked) context[key] = checked;
}

function valid(value, pattern) {
  return value && pattern.test(value) ? value : "";
}

await loadTwinCatalogue();
loadPortfolio();
await enforceAccess();
const savedPath = params.get("tool_path");
if (savedPath && registry.modules.find(m=>m.id===activeModule)?.service !== "local") {
  const spec = registry.modules.find(m=>m.id===activeModule);
  const url = new URL(savedPath, services[spec.service]);
  if (url.origin === new URL(services[spec.service]).origin) openToolLink(url.href);
}

function openToolLink(href) {
  let url; try { url = new URL(href, location.origin); } catch { return; }
  if (url.origin === location.origin) {
    if (url.pathname.startsWith("/docs/operating/")) return navigate("operating");
    if (url.pathname.startsWith("/docs/operations-portal/")) return navigate("operations");
    return;
  }
  for (const service of ["erp", "fuxa"]) {
    if (url.origin !== new URL(services[service]).origin || url.username || url.password) continue;
    const module = registry.modules.find(m => m.service === service && url.pathname.startsWith(m.path));
    if (service === "erp" && !url.pathname.startsWith("/app/")) return;
    navigate(module?.id || (service === "erp" ? "erp" : "fuxa"), url.pathname + url.search + url.hash);
  }
}
