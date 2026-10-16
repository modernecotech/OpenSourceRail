import {
  element as el,
  table,
  evidenceBadge,
  quantityText,
} from "./components.js";
import { translate as t, applyLanguage, language } from "../workbench/i18n.js";
import { guidedManufacturing } from "./engineering-inputs.js";
import { refinementCampaigns } from "./refinement-campaign.js";
import {
  assemblyInspector,
  comparisonReasons,
  checkComparison,
  physicalParts,
} from "./assembly-inspector.js";
import {
  researchScope,
  applicabilityFields,
  exactResearchScope as scopeMatches,
} from "./scope-controls.js";
import { inputRevisionPanel } from "./input-revisions.js";
import {
  operationReadiness,
  operationMessage,
  operationText,
  recursiveTuning,
} from "./operation-preflight.js";
applyLanguage();
document
  .querySelectorAll("[data-view],#run,#refresh,#recordForm>button")
  .forEach((node) => (node.textContent = t(node.textContent)));
const params = new URLSearchParams(location.search);
let context = {
  city: params.get("city") || "samawah",
  project: params.get("project") || params.get("city") || "samawah",
  environment: params.get("environment") || "simulation",
  revision: params.get("revision") || "unselected",
  baseline_sha256: params.get("baseline_sha256") || null,
  run_id: params.get("run_id") || null,
  selected_asset: params.get("selected_asset") || null,
  selected_part: params.get("selected_part") || null,
};
let actor = null;
let preflights = {};
let operationPreflights = {};
let problems = [];
let schemas = {};
let activeView = params.get("view") || "design";
let selectionEpoch = 0;
let inspectedCandidate = null;
let inspectedPart = null;
let currentJob = null;
let comparisonSource = "unknown";
let sourceRecords = [];
const status = document.querySelector("#status");
function scope() {
  return {
    schema: "osr-design-identity/1",
    city: context.city,
    project: context.project || context.city,
    environment: context.environment,
    configuration_revision: context.revision || "unselected",
    baseline_sha256: context.baseline_sha256 || null,
    run_id: context.run_id || null,
    asset_id: context.selected_asset || null,
    part_id: context.selected_part || null,
  };
}
function query() {
  return new URLSearchParams({
    city: context.city,
    project: context.project || context.city,
    environment: context.environment,
    revision: context.revision,
    baseline_sha256: context.baseline_sha256 || "",
    run_id: context.run_id || "",
    asset_id: context.selected_asset || "",
    part_id: context.selected_part || "",
  });
}
async function api(path, body) {
  const epoch = selectionEpoch;
  const response = await fetch(
    "/api/design/" +
      path +
      (body ? "" : (path.includes("?") ? "&" : "?") + query()),
    body
      ? {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": actor?.csrf || "",
          },
          body: JSON.stringify({ ...body, identity: scope() }),
        }
      : {},
  );
  const result = await response.json();
  if (epoch !== selectionEpoch)
    throw Error("Scope changed; older response discarded.");
  if (!response.ok) throw Error(result.error || "Local service unavailable");
  return result;
}
function show(view) {
  activeView = view;
  document
    .querySelectorAll("[data-panel]")
    .forEach((p) => (p.hidden = p.dataset.panel !== view));
  document
    .querySelectorAll("[data-view]")
    .forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.view === view)),
    );
}
document.querySelectorAll("[data-view]").forEach(
  (b) =>
    (b.onclick = () => {
      show(b.dataset.view);
      if (activeView === "jobs") loadJobs();
      if (activeView === "evidence") loadRecords();
      if (activeView === "parts" && inspectedCandidate?.definition?.contract) {
        loadQualification();
        renderInputRevisions();
      }
    }),
);
function draftKey() {
  return "osr:design-draft:" + JSON.stringify(scope());
}
function recordApplicability() {
  return Object.fromEntries(
    [...document.querySelectorAll("[data-applicability-field]")].map((node) => [
      node.dataset.applicabilityField,
      node.value.trim() || null,
    ]),
  );
}
function recordValue() {
  if (document.querySelector("#kind").value !== "appointment")
    return JSON.parse(document.querySelector("#recordPayload").value);
  const value = {};
  document.querySelectorAll("[data-appointment-field]").forEach((node) => {
    value[node.dataset.appointmentField] = node.value || null;
  });
  value.identity_reference = null;
  return value;
}
function saveDraft() {
  try {
    localStorage.setItem(
      draftKey(),
      JSON.stringify({
        problem: document.querySelector("#problem").value,
        values: values(),
        search: document.querySelector("#search").checked,
        refine: document.querySelector("#refine").checked,
        iterate: document.querySelector("#iterate").checked,
        recordKind: document.querySelector("#kind").value,
        recordPayload: document.querySelector("#recordPayload").value,
        productionInput: document.querySelector("#productionInput").value,
        applicability: recordApplicability(),
        appointment: Object.fromEntries(
          [...document.querySelectorAll("[data-appointment-field]")].map(
            (n) => [n.dataset.appointmentField, n.value],
          ),
        ),
      }),
    );
  } catch (error) {
    status.textContent = "Draft could not be retained: " + error.message;
  }
}
function selectedProblem() {
  return problems.find(
    (p) => p.id === document.querySelector("#problem").value,
  );
}
function values() {
  const p = selectedProblem();
  if (!p) return {};
  return Object.fromEntries(
    Object.entries(p.variables).map(([key, spec]) => {
      const node = document.querySelector('[data-variable="' + key + '"]');
      return [
        key,
        spec.kind === "choice" ? JSON.parse(node.value) : Number(node.value),
      ];
    }),
  );
}
function renderProblem(saved) {
  const p = selectedProblem();
  if (!p) return;
  document.querySelector("#function").textContent = p.applicability.function;
  document.querySelector("#charter").textContent = JSON.stringify(
    p.applicability,
    null,
    2,
  );
  document.querySelector("#budget").value = document.querySelector("#iterate")
    .checked
    ? 32
    : p.budget.evaluations;
  const fields = document.querySelector("#variables");
  fields.replaceChildren();
  for (const [key, spec] of Object.entries(p.variables)) {
    const label = el("label", key + " [" + spec.unit + "]");
    let node;
    if (spec.kind === "choice") {
      node = el("select");
      for (const value of spec.choices)
        node.append(new Option(String(value), JSON.stringify(value)));
    } else {
      node = el("input", "", {
        type: "number",
        min: spec.bounds[0],
        max: spec.bounds[1],
        step: spec.kind === "integer" ? 1 : "any",
      });
      node.value = spec.bounds[0];
    }
    node.dataset.variable = key;
    if (saved && key in saved)
      node.value =
        spec.kind === "choice" ? JSON.stringify(saved[key]) : saved[key];
    node.onchange = saveDraft;
    label.append(node);
    fields.append(label);
  }
  renderPreflight();
}
function renderPreflight() {
  const p = selectedProblem();
  if (!p) return;
  const readiness = operationReadiness(
    operationPreflights[p.id],
    preflights[p.id],
    {
      search: document.querySelector("#search").checked,
      refine: document.querySelector("#refine").checked,
      iterate: document.querySelector("#iterate").checked,
    },
  );
  document.querySelector("#preflight").textContent =
    readiness.rows.map(operationMessage).join(" · ") +
    " " +
    operationText("domain");
  document.querySelector("#run").disabled = !readiness.available;
}
function updateExperiment(changed) {
  const iterate = document.querySelector("#iterate");
  const search = document.querySelector("#search");
  const refine = document.querySelector("#refine");
  if (changed === "iterate" && iterate.checked) {
    search.checked = false;
    refine.checked = false;
    document.querySelector("#budget").value = 32;
  }
  if (changed === "search" && search.checked) iterate.checked = false;
  refine.disabled = iterate.checked;
  document.querySelector("#budget").min = iterate.checked ? 32 : 1;
  renderPreflight();
  saveDraft();
}
document.querySelector("#iterateLabel").textContent =
  operationText("iterateLabel");
document.querySelector("#iterateHelp").textContent =
  operationText("iterateHelp");
for (const name of ["refine", "search", "iterate"])
  document.querySelector("#" + name).onchange = () => updateExperiment(name);
document.querySelector("#cadPreflight").textContent =
  operationText("cadButton");
document.querySelector("#cadPreflight").onclick = async () => {
  const button = document.querySelector("#cadPreflight");
  button.disabled = true;
  try {
    const result = await api(
      "preflight?problem=" +
        encodeURIComponent(selectedProblem().id) +
        "&operation=cad-export",
    );
    document.querySelector("#cadPreflightStatus").textContent =
      operationMessage(result);
  } catch (error) {
    document.querySelector("#cadPreflightStatus").textContent = error.message;
  } finally {
    button.disabled = false;
  }
};
document.querySelector("#problem").onchange = () => {
  renderProblem();
  saveDraft();
};
document.querySelector("#designForm").onsubmit = async (event) => {
  event.preventDefault();
  saveDraft();
  const button = document.querySelector("#run");
  button.disabled = true;
  try {
    const iterate = document.querySelector("#iterate").checked;
    const result = await api("jobs", {
      problem: selectedProblem().id,
      candidates: [values()],
      refine: iterate || document.querySelector("#refine").checked,
      search:
        !iterate && document.querySelector("#search").checked
          ? { seeds: [11, 29, 47], evaluations: 16 }
          : null,
      recursive: iterate ? recursiveTuning(selectedProblem()) : null,
      budget: { evaluations: Number(document.querySelector("#budget").value) },
    });
    status.textContent = "Local job queued: " + result.id;
    show("jobs");
    await loadJobs();
  } catch (error) {
    status.textContent = error.message;
  } finally {
    renderPreflight();
  }
};
async function loadJobs() {
  const epoch = selectionEpoch;
  try {
    const payload = await api("jobs");
    if (epoch !== selectionEpoch) return;
    const root = document.querySelector("#jobs");
    root.replaceChildren();
    const queue = await api("work-queue");
    document.querySelector("#workQueue").replaceChildren(
      table(
        ["Work", "Owner", "State"],
        queue.entries.map((e) => [e.title, e.owner, e.state]),
      ),
    );
    if (!payload.jobs.length) {
      root.append(el("p", "No design jobs in this city and environment."));
      return;
    }
    for (const job of payload.jobs) {
      if (!scopeMatches(job, scope())) continue;
      const section = el("section", "", { "data-job": job.id });
      section.append(
        el("h3", job.id + " · " + job.request.problem.id),
        el(
          "p",
          "Execution " +
            job.status +
            " · " +
            job.phase +
            " · " +
            Number(job.progress).toFixed(0) +
            "% · source " +
            job.source_state,
        ),
        el("p", job.error || "No execution error"),
      );
      const actions = el("div", "", { class: "actions" });
      for (const [label, action, enabled] of [
        ["Inspect results", "comparison", job.status === "completed"],
        ["Inspect logs and artifacts", "artifacts", true],
        [
          "Cancel",
          "cancel",
          ["queued", "running", "resuming"].includes(job.status),
        ],
        [
          "Resume",
          "resume",
          [
            "failed",
            "cancelled",
            "timeout",
            "budget-exceeded",
            "interrupted",
            "unavailable",
          ].includes(job.status) && job.source_state === "current",
        ],
        [
          "Export review package",
          "export",
          job.status === "completed" && job.source_state === "current",
        ],
      ]) {
        const b = el("button", label, { type: "button" });
        b.disabled = !enabled;
        b.onclick = async () => {
          try {
            if (action === "comparison") {
              currentJob = job.id;
              renderComparison(await api("jobs/" + job.id + "/comparison"));
            } else if (action === "artifacts") {
              const result = await api("jobs/" + job.id + "/artifacts");
              const list = el("div");
              list.append(
                el(
                  "p",
                  "Attempt artifacts and logs · execution " +
                    result.execution_state +
                    " · partial files do not establish a sealed result.",
                ),
              );
              for (const row of result.artifacts) {
                const q = query();
                q.set("file", row.name);
                list.append(
                  el("a", row.name + " · " + row.bytes + " bytes", {
                    href: "/api/design/jobs/" + job.id + "/artifact?" + q,
                    download: "",
                  }),
                  el("br"),
                );
              }
              document.querySelector("#comparison").replaceChildren(list);
            } else {
              const result = await api("jobs/" + job.id + "/" + action, {});
              status.textContent = result.local_output
                ? "Review package written locally: " + result.local_output
                : job.id + " " + action + " requested";
              await loadJobs();
              if (result.download) {
                const downloads = el("div");
                downloads.append(
                  el(
                    "p",
                    result.download.restore +
                      " Archive SHA256: " +
                      result.download.archive_sha256,
                  ),
                );
                for (const row of result.download.chunks) {
                  const q = query();
                  q.set("export", result.download.export_id);
                  q.set("file", row.name);
                  downloads.append(
                    el("a", row.name + " · SHA256 " + row.sha256, {
                      href: "/api/design/jobs/" + job.id + "/download?" + q,
                      download: "",
                    }),
                    el("br"),
                  );
                }
                document
                  .querySelector("#comparison")
                  .replaceChildren(downloads);
              }
            }
          } catch (error) {
            status.textContent = error.message;
          }
        };
        actions.append(b);
      }
      section.append(actions);
      root.append(section);
    }
  } catch (error) {
    status.textContent = error.message;
  }
}
function renderComparison(report) {
  if (!scopeMatches(report, scope())) {
    status.textContent =
      "Result belongs to a different city, environment or revision.";
    return;
  }
  const root = document.querySelector("#comparison");
  root.replaceChildren(
    el(
      "h2",
      "Candidate comparison · " +
        (report.source_state || "historical source scope"),
    ),
  );
  comparisonSource = report.source_state || "unknown";
  document.querySelector("#qualificationDraft").hidden = true;
  document.querySelector("#qualificationOutput").textContent = "";
  if (report.recursive_search) renderRecursive(root, report.recursive_search);
  root.append(checkComparison(report.candidates));
  for (const candidate of report.candidates) {
    const section = el("section");
    section.append(
      el("h3", candidate.id),
      evidenceBadge(candidate.evidence_state || "unknown"),
    );
    section.append(
      table(
        ["Quantity", "Value"],
        [
          [
            "Defined component mass",
            quantityText(candidate.metrics.defined_mass_kg, "kg"),
          ],
          [
            "Complete installed mass",
            quantityText(candidate.complete_installed_mass_kg, "kg"),
          ],
          ["Installed cost", quantityText(candidate.installed_cost)],
          [
            "Detailed deflection",
            quantityText(candidate.metrics.detailed_deflection_m, "m"),
          ],
          [
            "Combined pressure/fault deflection",
            quantityText(candidate.metrics.combined_holdout_deflection_m, "m"),
          ],
        ],
      ),
    );
    section.append(
      table(
        ["Mandatory check", "Evidence state", "Basis"],
        Object.entries(candidate.checks).map(([name, row]) => [
          name,
          evidenceBadge(row.state),
          row.basis,
        ]),
      ),
    );
    section.append(comparisonReasons(candidate));
    refinementCampaigns(section, candidate);
    const inspect = el("button", "Inspect physical parts", { type: "button" });
    inspect.onclick = () => {
      inspectCandidate(candidate);
      show("parts");
    };
    section.append(inspect);
    root.append(section);
  }
}
function renderRecursive(root, report) {
  const section = el("section", "", { "data-recursive-results": "" });
  section.append(
    el("h3", operationText("recursiveResults")),
    table(
      [operationText("outcome"), operationText("verificationScope")],
      [
        [
          operationText("incumbent"),
          report.incumbent_id || operationText("noIncumbent"),
        ],
        [
          operationText("termination"),
          report.termination_reason || operationText("unknown"),
        ],
        [
          operationText("conditionalBest"),
          report.best_verified_in_tested_domain_claimed === true
            ? operationText("established")
            : operationText("unestablished"),
        ],
        [
          operationText("verificationScope"),
          report.best_verified_claim_scope || operationText("noDomainClaim"),
        ],
      ],
    ),
    el("p", operationText("researchOnly")),
  );
  const details = el("details");
  details.append(el("summary", operationText("lineage")));
  const scroll = el("div", "", {
    class: "comparison-scroll",
    tabindex: "0",
    role: "region",
    "aria-label": operationText("lineage"),
  });
  scroll.append(
    table(
      [
        "#",
        operationText("phase"),
        operationText("parent"),
        operationText("candidate"),
        operationText("variables"),
        operationText("outcome"),
      ],
      (report.lineage || []).map((row) => [
        row.index,
        row.phase,
        row.parent_id || "—",
        row.candidate_id || "—",
        JSON.stringify(row.variables || {}),
        row.error
          ? `${row.error.type}: ${row.error.message}`
          : row.outcome?.numerically_verified === true
            ? "numerically-verified"
            : JSON.stringify(row.outcome || { state: "unknown" }),
      ]),
    ),
  );
  details.append(scroll);
  section.append(details);
  root.append(section);
}
function inspectCandidate(candidate) {
  inspectedCandidate = candidate;
  document.querySelector("#definitionReview").hidden =
    !candidate.definition?.contract;
  const root = document.querySelector("#inspector");
  root.replaceChildren(el("h2", "Physical definition " + candidate.id));
  if (candidate.definition?.contract && currentJob) {
    const q = query();
    q.set("candidate", candidate.id);
    root.append(
      el("a", "Download manufactured definition JSON", {
        href: "/api/design/jobs/" + currentJob + "/definition?" + q,
        download: "manufactured-definition.json",
      }),
    );
  }
  const data = candidate.definition || {};
  const parts = physicalParts(candidate);
  refinementCampaigns(root, candidate);
  renderQualification(candidate);
  if (!parts.length) {
    root.append(
      el(
        "p",
        "No complete physical inventory is available for this candidate.",
      ),
    );
    return;
  }
  assemblyInspector(root, candidate, {
    onPart: (part) => {
      inspectedPart = part;
    },
  });
  for (const [en, ar, report] of [
    [
      "Dimensional manufacturing checks",
      "فحوص أبعاد التصنيع",
      data.installed_register?.dimensional_manufacturing,
    ],
    [
      "Subsystem installation and electrical demands",
      "متطلبات تركيب الأنظمة والكهرباء",
      data.installation,
    ],
  ])
    if (report) {
      const disclosure = el("details");
      disclosure.append(
        el("summary", qt(en, ar)),
        el("pre", JSON.stringify(report, null, 2)),
      );
      root.append(disclosure);
    }
}
const qt = (en, ar) => (language() === "ar" ? ar : en);
function qualificationKey(
  kind = document.querySelector("#qualificationKind").value,
) {
  return (
    "osr:qualification-draft:" +
    JSON.stringify({
      identity: scope(),
      job: currentJob,
      candidate: inspectedCandidate?.id,
      contract:
        inspectedCandidate?.definition?.installed_register
          ?.physical_definition_sha256,
      kind,
    })
  );
}
function renderInputRevisions() {
  const root = document.querySelector("#inputRevisions");
  if (!inspectedCandidate?.definition?.contract || !currentJob) {
    root.replaceChildren();
    return;
  }
  const drafts = [];
  for (const kind of ["manufacturing", "site", "prestress", "foundation"]) {
    try {
      const sha = localStorage.getItem(qualificationKey(kind) + ":checked");
      if (sha && /^[a-f0-9]{64}$/.test(sha)) drafts.push({ kind, sha });
    } catch {
      /* Missing receipts stay unavailable. */
    }
  }
  inputRevisionPanel(root, {
    identity: scope(),
    candidate: inspectedCandidate,
    job: currentJob,
    sourceState: comparisonSource,
    records: sourceRecords,
    drafts,
    api,
    actor,
    accountsConfigured: schemas.accounts_configured,
  });
}
function saveQualification() {
  try {
    localStorage.setItem(
      qualificationKey(),
      document.querySelector("#qualificationInput").value,
    );
    document.querySelector("#qualificationStatus").textContent = qt(
      "Draft retained on this device in this candidate and project scope.",
      "تم حفظ المسودة على هذا الجهاز ضمن نطاق المرشح والمشروع.",
    );
  } catch (error) {
    document.querySelector("#qualificationStatus").textContent = error.message;
  }
}
function manufacturingTemplate(contract) {
  const id = contract.parts[0].id;
  return {
    schema: "osr-manufacturing-plan/1",
    part_rules: [
      {
        physical_id: id,
        stock_bounds_m: [null, null, null],
        minimum_wall_m: null,
        basis_reference: null,
      },
    ],
    tool_envelopes: [
      {
        physical_id: id,
        bounds_m: [
          [null, null, null],
          [null, null, null],
        ],
        keepout_part_ids: [],
        basis_reference: null,
      },
    ],
    removal_paths: [
      {
        physical_id: id,
        bounds_m: [
          [null, null, null],
          [null, null, null],
        ],
        translation_m: [null, null, null],
        keepout_part_ids: [],
        basis_reference: null,
      },
    ],
    tolerance_stacks: [
      {
        physical_id: id,
        nominal_clearance_m: null,
        required_clearance_m: null,
        contributors: [{ physical_id: id, plus_minus_m: null }],
        basis_reference: null,
      },
    ],
    tooling: [
      {
        id: null,
        kind: null,
        count: null,
        physical_part_ids: [id],
        basis_reference: null,
      },
    ],
  };
}
function loadQualification() {
  const kind = document.querySelector("#qualificationKind").value;
  const data = inspectedCandidate.definition;
  const template =
    kind === "manufacturing"
      ? manufacturingTemplate(data.contract)
      : data.civil_input_templates[kind + "_input"];
  try {
    document.querySelector("#qualificationInput").value =
      localStorage.getItem(qualificationKey()) ||
      JSON.stringify(template, null, 2);
  } catch {
    document.querySelector("#qualificationInput").value = JSON.stringify(
      template,
      null,
      2,
    );
  }
  document.querySelector("#qualificationOutput").textContent = "";
  document.querySelector("#qualificationStatus").textContent = qt(
    "Blank facts remain unknown. Source hashes are checked for syntax; retained files require evidence review.",
    "البيانات الفارغة تبقى غير معروفة. يتم فحص صيغة البصمات؛ الملفات المحفوظة تتطلب مراجعة الأدلة.",
  );
  const guided = document.querySelector("#guidedManufacturing");
  guided.hidden = kind !== "manufacturing";
  if (kind === "manufacturing")
    guidedManufacturing(guided, {
      parts: data.contract.parts,
      records: sourceRecords.filter(
        (record) =>
          record.applicability?.candidate_id === inspectedCandidate.id &&
          record.applicability?.definition_sha256 ===
            data.installed_register?.physical_definition_sha256,
      ),
      read: () =>
        JSON.parse(document.querySelector("#qualificationInput").value),
      write: (plan) => {
        document.querySelector("#qualificationInput").value = JSON.stringify(
          plan,
          null,
          2,
        );
        saveQualification();
      },
    });
}
function renderQualification(candidate) {
  const data = candidate.definition || {};
  const form = document.querySelector("#qualificationDraft");
  form.hidden = !data.contract?.parts?.length;
  if (form.hidden) return;
  document.querySelector("#qualificationHeading").textContent = qt(
    "Engineering input draft for this physical candidate",
    "مسودة المدخلات الهندسية لهذا المرشح",
  );
  document.querySelector("#qualificationInstructions").textContent = qt(
    "Fill sourced SI facts when available. Validate site, prestress or manufacturing demands against this exact candidate. The baseline and acceptance gates remain unchanged. Observation rows use id, description and position_m; manufacturing rules refer to actual physical IDs.",
    "أدخل بيانات موثقة بوحدات النظام الدولي عند توفرها. تحقق من الموقع أو الإجهاد المسبق أو التصنيع لهذا المرشح. يبقى التصميم المعتمد وبوابات القبول دون تغيير. سجلات الرصد تستخدم id وdescription وposition_m؛ قواعد التصنيع تستخدم معرفات الأجزاء الفعلية.",
  );
  document.querySelector("#qualificationKindLabel>span").textContent = qt(
    "Input kind",
    "نوع المدخلات",
  );
  document.querySelector("#qualificationInputLabel>span").textContent = qt(
    "Scoped engineering JSON draft",
    "مسودة JSON هندسية ضمن النطاق",
  );
  const chooser = document.querySelector("#qualificationKind");
  chooser.replaceChildren(
    new Option(
      qt("Manufacturing constraints", "قيود التصنيع"),
      "manufacturing",
    ),
  );
  if (data.civil_input_templates) {
    chooser.append(
      new Option(
        qt("Site and foundation records", "سجلات الموقع والأساسات"),
        "site",
      ),
      new Option(
        qt("Prestress and loss inputs", "مدخلات الإجهاد المسبق والفواقد"),
        "prestress",
      ),
    );
    chooser.value = "site";
  }
  if (data.civil_input_templates?.foundation_input)
    chooser.append(
      new Option(
        qt("Foundation resistance and settlement", "مقاومة الأساسات والهبوط"),
        "foundation",
      ),
    );
  document.querySelector("#qualificationReferencesLabel").textContent = qt(
    "Reference sources and actual investigation extent",
    "المراجع ونطاق التحقيق الفعلي",
  );
  document.querySelector("#qualificationReferences").textContent =
    JSON.stringify(
      data.civil_input_templates
        ? {
            references: data.civil_input_templates.references,
            foundation_geometry: data.civil_input_templates.foundation_geometry,
          }
        : data.installed_register?.dimensional_manufacturing || {},
      null,
      2,
    );
  const button = document.querySelector("#qualificationValidate");
  button.textContent = qt(
    "Retain and check numerical draft",
    "حفظ المسودة وفحصها عددياً",
  );
  button.disabled = comparisonSource !== "current";
  loadQualification();
  renderInputRevisions();
}
document.querySelector("#qualificationKind").onchange = loadQualification;
document.querySelector("#qualificationInput").oninput = saveQualification;
document.querySelector("#qualificationDraft").onsubmit = async (event) => {
  event.preventDefault();
  saveQualification();
  const button = document.querySelector("#qualificationValidate");
  button.disabled = true;
  try {
    const input_json = document.querySelector("#qualificationInput").value;
    if (new TextEncoder().encode(input_json).length > 200 * 1024)
      throw Error(
        qt(
          "Engineering input draft must be smaller than 200 KiB.",
          "يجب أن تكون المسودة أصغر من ٢٠٠ كيبي بايت.",
        ),
      );
    const result = await api("jobs/" + currentJob + "/qualification-draft", {
      candidate: inspectedCandidate.id,
      contract_sha256:
        inspectedCandidate.definition.installed_register
          .physical_definition_sha256,
      kind: document.querySelector("#qualificationKind").value,
      input_json,
    });
    document.querySelector("#qualificationOutput").textContent = JSON.stringify(
      result,
      null,
      2,
    );
    document.querySelector("#qualificationStatus").textContent = qt(
      "Draft retained and checked. Missing facts stay open; no baseline or physical acceptance changed.",
      "تم حفظ المسودة وفحصها. تبقى البيانات الناقصة مفتوحة؛ لم يتغير التصميم المعتمد أو القبول المادي.",
    );
    if (result.draft_sha256) {
      localStorage.setItem(
        qualificationKey() + ":checked",
        result.draft_sha256,
      );
      renderInputRevisions();
    }
  } catch (error) {
    document.querySelector("#qualificationStatus").textContent = error.message;
  } finally {
    button.disabled = comparisonSource !== "current";
  }
};
document.querySelector("#definitionReview").onsubmit = async (event) => {
  event.preventDefault();
  try {
    const file = document.querySelector("#revisedDefinition").files[0];
    if (!file || file.size > 4 * 1024 * 1024)
      throw Error("Choose a bounded revised physical definition JSON file.");
    const proposed_json = await file.text();
    JSON.parse(proposed_json);
    const result = await api("definition-diff", {
      job: currentJob,
      candidate: inspectedCandidate.id,
      proposed_json,
    });
    document.querySelector("#definitionDiff").textContent = JSON.stringify(
      { ...result, candidate_draft: undefined },
      null,
      2,
    );
    status.textContent =
      "Definition diff prepared; dependent evidence is invalidated and the adopted baseline remains separate.";
  } catch (error) {
    status.textContent = error.message;
  }
};
async function loadParts() {
  try {
    const payload = await api("parts");
    const root = document.querySelector("#parts");
    root.replaceChildren();
    for (const part of payload.parts) {
      const source = payload.sources[part.source_id];
      const details = el("details");
      details.append(el("summary", part.name + " · " + part.category));
      details.append(
        el(
          "p",
          "Public potential component. Price, availability, rights and project qualification: unknown.",
        ),
        el("pre", JSON.stringify(part.properties, null, 2)),
      );
      for (const limit of part.applicability_limits)
        details.append(el("p", limit));
      const link = el("a", source.publisher + " source · " + source.version, {
        href: source.url,
        target: "_blank",
        rel: "noopener noreferrer",
      });
      details.append(link);
      root.append(details);
    }
  } catch (error) {
    status.textContent = error.message;
  }
}
function renderRecordFields() {
  const kind = document.querySelector("#kind").value;
  const fields = schemas.kinds?.[kind] || [];
  document.querySelector("#recordFields").textContent =
    "Required fields: " + fields.join(", ");
  document.querySelector("#recordPayload").value = JSON.stringify(
    Object.fromEntries(fields.map((k) => [k, null])),
    null,
    2,
  );
  const root = document.querySelector("#appointmentFields");
  root.replaceChildren();
  root.hidden = kind !== "appointment";
  document.querySelector("#structuredFields").hidden = kind === "appointment";
  if (kind === "appointment")
    for (const [key, label] of [
      ["person_name", "Person name"],
      ["organization", "Organization"],
      ["role", "Appointed role"],
      ["appointment_scope", "Project, responsibility and limits"],
      ["valid_until", "Appointment valid until"],
    ]) {
      const field = el("label", t(label));
      const input = el(
        key === "appointment_scope" ? "textarea" : "input",
        "",
        key === "valid_until" ? { type: "date" } : {},
      );
      input.dataset.appointmentField = key;
      input.oninput = saveDraft;
      field.append(input);
      root.append(field);
    }
}
document.querySelector("#kind").onchange = () => {
  renderRecordFields();
  saveDraft();
};
document.querySelector("#recordPayload").oninput = saveDraft;
document.querySelector("#recordForm").onsubmit = async (event) => {
  event.preventDefault();
  saveDraft();
  const epoch = selectionEpoch;
  try {
    let payload = recordValue();
    const file = document.querySelector("#evidenceFile").files[0];
    if (file) {
      const response = await fetch(
        "/api/ops-core/" + context.city + "/evidence",
        {
          method: "POST",
          headers: {
            "X-CSRF-Token": actor?.csrf || "",
            "X-OSR-Filename": encodeURIComponent(file.name),
            "X-OSR-Mime": file.type || "application/octet-stream",
          },
          body: file,
        },
      );
      const data = await response.json();
      if (!response.ok) throw Error(data.error);
      const e = data.evidence;
      payload[
        document.querySelector("#kind").value === "appointment"
          ? "identity_reference"
          : "source_reference"
      ] = {
        path:
          context.city +
          "/" +
          e.sha256.slice(0, 2) +
          "/" +
          e.sha256 +
          "-" +
          e.file_name,
        sha256: e.sha256,
      };
    }
    if (epoch !== selectionEpoch)
      throw Error(
        "Scope changed; original draft and uploaded evidence remain in their original scope.",
      );
    const applicability = recordApplicability();
    const keyName = draftKey() + ":submission";
    const submitted = JSON.stringify({
      kind: document.querySelector("#kind").value,
      payload,
      applicability,
    });
    let previous;
    try {
      previous = JSON.parse(localStorage.getItem(keyName) || "null");
    } catch {}
    const key =
      previous?.submitted === submitted ? previous.key : crypto.randomUUID();
    localStorage.setItem(keyName, JSON.stringify({ key, submitted }));
    const result = await api("records", {
      kind: document.querySelector("#kind").value,
      payload,
      applicability,
      idempotency_key: key,
    });
    localStorage.removeItem(keyName);
    status.textContent = "Draft record retained: " + result.id;
    await loadRecords();
  } catch (error) {
    status.textContent = "Draft remains available: " + error.message;
  }
};
async function loadRecords() {
  try {
    const payload = await api("records");
    sourceRecords = payload.records;
    const costs = await api("cost-objectives");
    document.querySelector("#costObjectives").textContent = JSON.stringify(
      costs,
      null,
      2,
    );
    const root = document.querySelector("#records");
    root.replaceChildren();
    if (!payload.records.length)
      root.append(el("p", "No named appointments or evidence records yet."));
    for (const record of payload.records) {
      const section = el("section");
      section.append(
        el("h3", record.kind + " · " + record.id),
        el("p", "Record " + record.state + " · authored by " + record.creator),
        el("pre", JSON.stringify(record.payload, null, 2)),
      );
      const b = el("button", "Verify exact record and evidence", {
        type: "button",
      });
      b.disabled = record.state !== "draft" || !schemas.accounts_configured;
      b.onclick = async () => {
        try {
          const result = await api("records/verify", {
            record: record.id,
            revision: record.revision,
          });
          status.textContent =
            "Record verified by " +
            result.reviewer +
            "; technical applicability and physical release remain separate.";
          await loadRecords();
        } catch (error) {
          status.textContent = error.message;
        }
      };
      section.append(b);
      root.append(section);
    }
  } catch (error) {
    status.textContent = error.message;
  }
}
document.querySelector("#login").onsubmit = async (event) => {
  event.preventDefault();
  try {
    const form = new FormData(event.target);
    const response = await fetch("/api/ops-auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: form.get("username"),
        password: form.get("password"),
      }),
    });
    const result = await response.json();
    if (!response.ok) throw Error(result.error);
    event.target.reset();
    actor = result.actor;
    await initialize();
  } catch (error) {
    status.textContent = error.message;
  }
};
document.querySelector("#productionInput").oninput = saveDraft;
document.querySelector("#productionPlan").onsubmit = async (event) => {
  event.preventDefault();
  try {
    const data = JSON.parse(document.querySelector("#productionInput").value);
    document.querySelector("#productionOutput").textContent = JSON.stringify(
      await api("production-plan", data),
      null,
      2,
    );
  } catch (error) {
    status.textContent = error.message;
  }
};
document.querySelector("#refresh").onclick = loadJobs;
function changeContext(next) {
  const changed =
    next.city !== context.city ||
    (next.project || next.city) !== (context.project || context.city) ||
    next.environment !== context.environment ||
    (next.revision || "unselected") !== context.revision ||
    (next.baseline_sha256 || null) !== (context.baseline_sha256 || null) ||
    (next.run_id || null) !== (context.run_id || null) ||
    (next.selected_asset || null) !== (context.selected_asset || null) ||
    (next.selected_part || null) !== (context.selected_part || null);
  if (changed) {
    saveDraft();
    selectionEpoch++;
    sourceRecords = [];
    currentJob = null;
    inspectedCandidate = null;
    document.querySelector("#definitionReview").hidden = true;
    document.querySelector("#definitionDiff").textContent = "";
    document.querySelector("#qualificationDraft").hidden = true;
    document.querySelector("#qualificationInput").value = "";
    document.querySelector("#qualificationOutput").textContent = "";
    document.querySelector("#productionInput").value =
      '{"tasks":[],"resources":[]}';
    document.querySelector("#productionOutput").textContent = "";
    for (const id of ["comparison", "inspector", "jobs", "records"])
      document.querySelector("#" + id).replaceChildren();
  }
  context = {
    ...next,
    project: next.project || next.city,
    revision: next.revision || "unselected",
  };
  if (changed) {
    inspectedPart = null;
    document.querySelector("#inputRevisions").replaceChildren();
    initialize();
  }
}
window.addEventListener("message", (event) => {
  if (
    event.origin !== location.origin ||
    event.source !== parent ||
    event.data?.type !== "osr:context"
  )
    return;
  changeContext(event.data.context);
});
async function initialize() {
  const epoch = selectionEpoch;
  try {
    const session = await fetch("/api/ops-auth/session").then((r) => r.json());
    actor = session.actor || null;
    document.querySelector("#context").textContent =
      context.city +
      " · " +
      (context.project || context.city) +
      " · " +
      context.environment +
      " · " +
      (context.revision || "unselected");
    document.querySelector("#account").textContent = actor
      ? "Account: " + actor.display_name
      : "No authenticated account";
    researchScope(document.querySelector("#researchScopeControls"), {
      identity: scope(),
      change: (value) => {
        const next = {
          ...context,
          project: value.project,
          revision: value.configuration_revision,
          baseline_sha256: value.baseline_sha256,
        };
        const url = new URL(location.href);
        for (const [key, value] of Object.entries({
          project: next.project,
          revision: next.revision,
          baseline_sha256: next.baseline_sha256 || "",
        }))
          url.searchParams.set(key, value);
        history.replaceState(null, "", url);
        changeContext(next);
      },
    });
    applicabilityFields(document.querySelector("#recordApplicability"), {
      candidate: () => ({ candidate: inspectedCandidate, part: inspectedPart }),
      save: saveDraft,
      status: (text) => {
        status.textContent = text;
      },
    });
    const [p, s] = await Promise.all([api("problems"), api("review-schema")]);
    if (epoch !== selectionEpoch) return;
    problems = p.problems;
    preflights = p.preflight;
    operationPreflights = p.operations || {};
    schemas = s;
    const chooser = document.querySelector("#problem");
    chooser.replaceChildren(...problems.map((p) => new Option(p.id, p.id)));
    const kind = document.querySelector("#kind");
    kind.replaceChildren(...Object.keys(s.kinds).map((k) => new Option(k, k)));
    const saved = JSON.parse(localStorage.getItem(draftKey()) || "null");
    if (saved) {
      chooser.value = saved.problem;
      kind.value = saved.recordKind || "appointment";
    }
    document.querySelector("#iterate").checked = saved?.iterate === true;
    document.querySelector("#search").checked =
      saved?.search === true && !saved?.iterate;
    document.querySelector("#refine").checked =
      saved?.refine === true && !saved?.iterate;
    document.querySelector("#refine").disabled = saved?.iterate === true;
    document.querySelector("#budget").min = saved?.iterate === true ? 32 : 1;
    renderProblem(saved?.values);
    if (saved?.iterate) document.querySelector("#budget").value = 32;
    renderRecordFields();
    document.querySelector("#productionInput").value =
      saved?.productionInput || '{"tasks":[],"resources":[]}';
    if (saved?.recordPayload)
      document.querySelector("#recordPayload").value = saved.recordPayload;
    for (const node of document.querySelectorAll("[data-applicability-field]"))
      node.value =
        saved?.applicability?.[node.dataset.applicabilityField] || "";
    if (saved?.appointment)
      for (const node of document.querySelectorAll("[data-appointment-field]"))
        node.value = saved.appointment[node.dataset.appointmentField] || "";
    status.textContent =
      "Local design tools ready. Missing supplier, site and physical data remain explicit.";
    show(activeView);
    await loadParts();
    if (activeView === "jobs") await loadJobs();
    if (activeView === "evidence") await loadRecords();
    if (activeView !== "evidence") {
      try {
        const retained = await api("records");
        if (epoch === selectionEpoch) sourceRecords = retained.records || [];
      } catch {
        /* Unavailable records never become inferred sources. */
      }
    }
    if (activeView === "parts" && inspectedCandidate?.definition?.contract)
      renderInputRevisions();
  } catch (error) {
    if (epoch === selectionEpoch) status.textContent = error.message;
  }
}
show(activeView);
await initialize();
