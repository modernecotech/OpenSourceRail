import { element as el } from "./components.js";
import { language } from "../workbench/i18n.js";

export const scopeLabels = {
  heading: [
    "Research scope and evidence applicability",
    "نطاق البحث وانطباق الأدلة",
  ],
  project: ["Project identifier", "معرف المشروع"],
  revision: ["Configuration revision", "مراجعة التكوين"],
  baseline: [
    "Baseline SHA256 (blank means unknown)",
    "بصمة خط الأساس SHA256 (الفراغ يعني غير معروف)",
  ],
  apply: ["Use this research scope", "استخدام نطاق البحث هذا"],
  note: [
    "Enter a known research baseline to bind future reviewed inputs. This selection grants no baseline adoption or physical release.",
    "أدخل خط أساس بحثي معروفاً لربط المدخلات التي ستراجع لاحقاً. لا يمنح هذا الاختيار اعتماد خط الأساس أو الإذن المادي.",
  ],
  candidate: [
    "Applicable candidate ID (optional)",
    "معرف المرشح المنطبق (اختياري)",
  ],
  part: [
    "Applicable physical part ID (optional)",
    "معرف الجزء الفعلي المنطبق (اختياري)",
  ],
  batch: [
    "Applicable material batch (optional)",
    "دفعة المادة المنطبقة (اختياري)",
  ],
  definition: [
    "Applicable definition SHA256 (optional)",
    "بصمة التعريف المنطبق SHA256 (اختياري)",
  ],
  copy: [
    "Use inspected candidate and part",
    "استخدام المرشح والجزء الجاري فحصهما",
  ],
  none: [
    "Inspect a candidate before copying its applicability.",
    "افحص مرشحاً قبل نسخ نطاق انطباقه.",
  ],
  exact: [
    "Records retain the project, revision and baseline shown above. Optional fields further restrict applicability; they cannot broaden it.",
    "تحتفظ السجلات بالمشروع والمراجعة وخط الأساس المبين أعلاه. الحقول الاختيارية تضيق نطاق الانطباق ولا توسعه.",
  ],
};
const text = (key) => scopeLabels[key][language() === "ar" ? 1 : 0];

export function exactResearchScope(record, identity) {
  const actual = record.identity || record.request?.identity;
  if (!actual) return false;
  return [
    "city",
    "project",
    "environment",
    "configuration_revision",
    "baseline_sha256",
    "run_id",
    "asset_id",
    "part_id",
  ].every((key) => (actual[key] ?? null) === (identity[key] ?? null));
}

export function researchScope(root, { identity, change }) {
  root.replaceChildren();
  const disclosure = el("details");
  disclosure.append(el("summary", text("heading")), el("p", text("note")));
  const form = el("form", "", { id: "researchScope" });
  const fields = el("div", "", { class: "engineering-fields" });
  const controls = {};
  for (const [key, label] of [
    ["project", "project"],
    ["configuration_revision", "revision"],
    ["baseline_sha256", "baseline"],
  ]) {
    const input = el("input", "", {
      type: "text",
      "data-research-scope": key,
      maxlength: key === "baseline_sha256" ? "64" : "128",
    });
    if (key === "baseline_sha256") input.pattern = "[a-f0-9]{64}";
    else input.required = true;
    input.value = identity[key] || "";
    const wrapper = el("label", text(label));
    wrapper.append(input);
    fields.append(wrapper);
    controls[key] = input;
  }
  form.append(fields, el("button", text("apply")));
  form.onsubmit = (event) => {
    event.preventDefault();
    change(
      Object.fromEntries(
        Object.entries(controls).map(([key, node]) => [
          key,
          node.value.trim() || null,
        ]),
      ),
    );
  };
  disclosure.append(form);
  root.append(disclosure);
}

export function applicabilityFields(root, { candidate, save, status }) {
  root.replaceChildren(el("p", text("exact")));
  const fields = el("div", "", { class: "engineering-fields" });
  for (const [key, label] of [
    ["candidate_id", "candidate"],
    ["physical_part_id", "part"],
    ["material_batch", "batch"],
    ["definition_sha256", "definition"],
  ]) {
    const wrapper = el("label", text(label));
    const input = el("input", "", {
      type: "text",
      "data-applicability-field": key,
      maxlength: key === "definition_sha256" ? "64" : "192",
    });
    if (key === "definition_sha256") input.pattern = "[a-f0-9]{64}";
    input.oninput = save;
    wrapper.append(input);
    fields.append(wrapper);
  }
  const copy = el("button", text("copy"), { type: "button" });
  copy.onclick = () => {
    const selected = candidate();
    if (!selected.candidate) {
      status(text("none"));
      return;
    }
    const values = {
      candidate_id: selected.candidate.id,
      physical_part_id: selected.part?.id || null,
      definition_sha256:
        selected.candidate.definition?.installed_register
          ?.physical_definition_sha256 || null,
    };
    for (const [key, value] of Object.entries(values))
      root.querySelector(`[data-applicability-field="${key}"]`).value =
        value || "";
    save();
  };
  root.append(fields, copy);
}
