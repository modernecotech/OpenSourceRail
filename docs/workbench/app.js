const MODES = new Set(["design", "simulation", "training", "live"]);
const ROLES = new Set(["designer", "dispatcher", "maintainer", "reviewer"]);
const MODULES = new Set(["studio", "simulator", "occ", "operations"]);
const params = new URLSearchParams(location.search);
const bootstrap = await fetch("/api/workbench").then((response) => response.json());

const context = {
  schema_version: 1,
  city: valid(params.get("city"), /^[a-z0-9][a-z0-9-]{0,63}$/) || bootstrap.city,
  mode: MODES.has(params.get("mode")) ? params.get("mode") : "design",
  role: ROLES.has(params.get("role")) ? params.get("role") : "designer",
  actor: valid(params.get("actor"), /^[A-Za-z0-9][A-Za-z0-9 ._@-]{1,119}$/) || "local-user",
};
setOptional("revision", params.get("revision"), /^osr-[a-f0-9]{16}$/);
setOptional("baseline_sha256", params.get("baseline_sha256"), /^[a-f0-9]{64}$/);
setOptional("run_id", params.get("run_id"), /^run-[a-f0-9]{16}$/);
setOptional("selected_asset", params.get("selected_asset"), /^.{1,160}$/);
if (context.mode === "live" && !context.baseline_sha256) context.mode = "training";

let activeModule = MODULES.has(params.get("module")) ? params.get("module") : "studio";
const frame = document.getElementById("moduleFrame");

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
  updateContext({ mode: event.target.value });
  enforceAccess();
});
document.querySelectorAll("[data-module]").forEach((button) => {
  button.addEventListener("click", () => navigate(button.dataset.module));
});
document.getElementById("occHandoff").addEventListener("click", () => {
  updateContext({ mode: "training", role: context.role === "designer" ? "reviewer" : context.role });
  navigate("occ");
});

window.addEventListener("message", (event) => {
  if (event.origin !== location.origin || event.source !== frame.contentWindow) return;
  if (event.data?.type === "osr:context") updateContext(event.data.context || {});
  if (event.data?.type === "osr:navigate" && MODULES.has(event.data.module)) {
    updateContext(event.data.context || {});
    navigate(event.data.module);
  }
});
frame.addEventListener("load", () => {
  frame.contentWindow?.postMessage({ type: "osr:context", context: { ...context } }, location.origin);
});

function navigate(module) {
  if (!isAllowed(module)) return;
  activeModule = module;
  const query = contextQuery();
  const routes = {
    studio: `/studio/?${query}`,
    simulator: `/simulator/?${query}`,
    occ: `/occ/?${query}`,
    operations: `/operations/?data=${encodeURIComponent(operationsData())}&${query}#core`,
  };
  frame.src = routes[module];
  render();
}

function updateContext(patch) {
  if (valid(patch.city, /^[a-z0-9][a-z0-9-]{0,63}$/)) context.city = patch.city;
  if (MODES.has(patch.mode)) context.mode = patch.mode;
  if (ROLES.has(patch.role)) context.role = patch.role;
  if (valid(patch.actor, /^[A-Za-z0-9][A-Za-z0-9 ._@-]{1,119}$/)) context.actor = patch.actor;
  assignOptional("revision", patch.revision, /^osr-[a-f0-9]{16}$/);
  assignOptional("baseline_sha256", patch.baseline_sha256, /^[a-f0-9]{64}$/);
  assignOptional("run_id", patch.run_id, /^run-[a-f0-9]{16}$/);
  assignOptional("selected_asset", patch.selected_asset, /^.{1,160}$/);
  document.getElementById("role").value = context.role;
  document.getElementById("mode").value = context.mode;
  document.getElementById("actor").value = context.actor;
  history.replaceState(null, "", `/?module=${activeModule}&${contextQuery()}`);
  render();
  frame.contentWindow?.postMessage({ type: "osr:context", context: { ...context } }, location.origin);
}

function enforceAccess() {
  if (!isAllowed(activeModule)) {
    activeModule = context.mode === "live" ? "occ" : "operations";
  }
  navigate(activeModule);
}

function isAllowed(module) {
  if (module === "operations") return true;
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
  document.getElementById("contextCity").textContent = context.city;
  document.getElementById("contextRevision").textContent = context.revision || "not selected";
  document.getElementById("contextBaseline").textContent = context.baseline_sha256?.slice(0, 16) || "not approved";
  document.getElementById("contextRun").textContent = context.run_id || "not run";
  document.getElementById("contextAsset").textContent = context.selected_asset || "none";
  document.querySelectorAll("[data-module]").forEach((button) => {
    button.disabled = !isAllowed(button.dataset.module);
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
  return bootstrap.operations_data;
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

enforceAccess();
