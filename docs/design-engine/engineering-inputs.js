// Guided inputs retain explicit SI units and source scope; they grant no acceptance.
import { element as el } from "./components.js";
import { language } from "../workbench/i18n.js";

export const inputLabels = {
  heading: ["Guided manufacturing rule", "قاعدة تصنيع موجهة"],
  kind: ["Rule type", "نوع القاعدة"],
  part: ["Manufacturing component", "جزء التصنيع"],
  source: ["Rule source record", "سجل مصدر القاعدة"],
  other: [
    "Other reference, awaiting evidence review",
    "مرجع آخر بانتظار مراجعة الأدلة",
  ],
  reference: [
    "Source reference and applicability limits",
    "مرجع المصدر وحدود انطباقه",
  ],
  add: ["Add rule to engineering draft", "إضافة القاعدة إلى المسودة الهندسية"],
  saved: [
    "Rule added. Retain and check the draft before creating a reviewed input revision.",
    "تمت إضافة القاعدة. احفظ المسودة وافحصها قبل إنشاء مراجعة مدخلات معتمدة.",
  ],
  missing: [
    "Complete the indicated fields with finite values and a source reference.",
    "أكمل الحقول المحددة بقيم عددية محدودة ومرجع مصدر.",
  ],
  noParts: [
    "This candidate has no physical parts for a manufacturing rule.",
    "لا يحتوي هذا المرشح على أجزاء فعلية لقاعدة تصنيع.",
  ],
  keepouts: [
    "Keepout parts (select all relevant parts)",
    "أجزاء العوائق (اختر كل الأجزاء ذات الصلة)",
  ],
  contributor: ["Tolerance contributor part", "الجزء المساهم في تفاوت الأبعاد"],
  stock: ["Stock envelope and minimum wall", "حدود المادة الخام وأقل سماكة"],
  tool: ["Tool access envelope", "حدود حيز وصول الأداة"],
  removal: ["Replacement removal path", "مسار الإزالة للاستبدال"],
  tolerance: ["Worst-case tolerance stack", "تراكم التفاوت في أسوأ حالة"],
  tooling: ["Mould or fixture allocation", "تخصيص القالب أو المثبت"],
  fixture: ["Fixture", "مثبت"],
  mould: ["Mould", "قالب"],
  toolKind: ["Tooling kind", "نوع تجهيز التصنيع"],
  toolId: ["Tooling identifier", "معرف تجهيز التصنيع"],
  count: ["Tooling count [ea]", "عدد تجهيزات التصنيع [قطعة]"],
  stockX: ["Stock X [m]", "طول المادة الخام X [m]"],
  stockY: ["Stock Y [m]", "عرض المادة الخام Y [m]"],
  stockZ: ["Stock Z [m]", "ارتفاع المادة الخام Z [m]"],
  wall: ["Minimum wall [m]", "أقل سماكة [m]"],
  lowX: ["Envelope minimum X [m]", "أصغر حد للحيز X [m]"],
  lowY: ["Envelope minimum Y [m]", "أصغر حد للحيز Y [m]"],
  lowZ: ["Envelope minimum Z [m]", "أصغر حد للحيز Z [m]"],
  highX: ["Envelope maximum X [m]", "أكبر حد للحيز X [m]"],
  highY: ["Envelope maximum Y [m]", "أكبر حد للحيز Y [m]"],
  highZ: ["Envelope maximum Z [m]", "أكبر حد للحيز Z [m]"],
  shiftX: ["Removal translation X [m]", "إزاحة الإزالة X [m]"],
  shiftY: ["Removal translation Y [m]", "إزاحة الإزالة Y [m]"],
  shiftZ: ["Removal translation Z [m]", "إزاحة الإزالة Z [m]"],
  nominal: ["Nominal clearance [m]", "الخلوص الاسمي [m]"],
  required: ["Required clearance [m]", "الخلوص المطلوب [m]"],
  plusMinus: ["Contributor ± tolerance [m]", "تفاوت الجزء ± [m]"],
};
export const inputText = (key) => inputLabels[key][language() === "ar" ? 1 : 0];
const TYPES = {
  part_rules: "stock",
  tool_envelopes: "tool",
  removal_paths: "removal",
  tolerance_stacks: "tolerance",
  tooling: "tooling",
};

function finite(value, label, minimum = -Infinity) {
  if (
    value === "" ||
    value === null ||
    value === undefined ||
    typeof value === "boolean"
  )
    throw Error(label);
  const number = Number(value);
  if (!Number.isFinite(number) || number < minimum) throw Error(label);
  return number;
}
export function manufacturingRule(kind, values, physicalIds) {
  if (!(kind in TYPES) || !physicalIds.includes(values.physical_id))
    throw Error(inputText("part"));
  const basis = String(values.basis_reference || "").trim();
  if (!basis) throw Error(inputText("reference"));
  const row = { physical_id: values.physical_id, basis_reference: basis };
  const number = (key, min) => finite(values[key], inputText(key), min);
  if (kind === "part_rules")
    return {
      ...row,
      stock_bounds_m: ["stockX", "stockY", "stockZ"].map((key) =>
        number(key, Number.MIN_VALUE),
      ),
      minimum_wall_m: number("wall", Number.MIN_VALUE),
    };
  if (kind === "tool_envelopes" || kind === "removal_paths") {
    const lows = ["lowX", "lowY", "lowZ"].map((key) => number(key));
    const highs = ["highX", "highY", "highZ"].map((key) => number(key));
    if (lows.some((value, i) => value >= highs[i]))
      throw Error(inputText("tool"));
    const ids = values.keepout_part_ids || [];
    if (
      !ids.length ||
      new Set(ids).size !== ids.length ||
      ids.some((id) => !physicalIds.includes(id) || id === values.physical_id)
    )
      throw Error(inputText("keepouts"));
    const result = { ...row, bounds_m: [lows, highs], keepout_part_ids: ids };
    if (kind === "removal_paths") {
      result.translation_m = ["shiftX", "shiftY", "shiftZ"].map((key) =>
        number(key),
      );
      if (!result.translation_m.some((value) => value !== 0))
        throw Error(inputText("removal"));
    }
    return result;
  }
  if (kind === "tolerance_stacks") {
    if (!physicalIds.includes(values.contributor))
      throw Error(inputText("contributor"));
    return {
      ...row,
      nominal_clearance_m: number("nominal", 0),
      required_clearance_m: number("required", 0),
      contributors: [
        {
          physical_id: values.contributor,
          plus_minus_m: number("plusMinus", 0),
        },
      ],
    };
  }
  const count = number("count", 1);
  if (
    !Number.isInteger(count) ||
    count > 1024 ||
    !String(values.toolId || "").trim() ||
    !["mould", "fixture"].includes(values.toolKind)
  )
    throw Error(inputText("tooling"));
  return {
    id: values.toolId.trim(),
    kind: values.toolKind,
    count,
    physical_part_ids: [values.physical_id],
    basis_reference: basis,
  };
}

function enteredFact(value, key = "") {
  if (["physical_id", "physical_part_ids"].includes(key)) return false;
  if (value === null || value === undefined || value === "") return false;
  if (Array.isArray(value)) return value.some((item) => enteredFact(item));
  if (typeof value === "object")
    return Object.entries(value).some(([name, item]) =>
      enteredFact(item, name),
    );
  return true;
}
export function appendManufacturingRule(existing, kind, row) {
  if (existing.schema !== "osr-manufacturing-plan/1")
    throw Error("osr-manufacturing-plan/1");
  const result = structuredClone(existing);
  for (const key of Object.keys(TYPES)) {
    if (!Array.isArray(result[key] || [])) throw Error(key);
    result[key] = (result[key] || []).filter(enteredFact);
  }
  result[kind].push(row);
  return result;
}

export function guidedManufacturing(
  root,
  { parts, records = [], read, write },
) {
  root.replaceChildren();
  root.append(el("h4", inputText("heading")));
  if (!parts.length) {
    root.append(el("p", inputText("noParts")));
    return;
  }
  const fields = el("div", "", { class: "engineering-fields" });
  const note = el("p", "", { role: "status", "aria-live": "polite" });
  const controls = {};
  const field = (key, node) => {
    const label = el("label", inputText(key));
    label.append(node);
    fields.append(label);
    return node;
  };
  const chooser = field("kind", el("select", "", { "data-guided-kind": "" }));
  for (const [key, label] of Object.entries(TYPES))
    chooser.append(new Option(inputText(label), key));
  const part = field("part", el("select", "", { "data-guided-part": "" }));
  for (const row of parts) part.append(new Option(row.id, row.id));
  const source = field(
    "source",
    el("select", "", { "data-guided-source": "" }),
  );
  source.append(new Option(inputText("other"), ""));
  const populateSources = () => {
    source.replaceChildren(new Option(inputText("other"), ""));
    for (const record of records.filter(
      (row) =>
        row.state === "verified" &&
        (!row.applicability?.physical_part_id ||
          row.applicability.physical_part_id === part.value),
    ))
      source.append(
        new Option(
          `${record.kind} · ${record.id} · ${record.revision}`,
          record.id,
        ),
      );
  };
  populateSources();
  const reference = field(
    "reference",
    el("input", "", { type: "text", "data-guided-reference": "" }),
  );
  const varying = el("div", "", { class: "engineering-fields" });
  const add = el("button", inputText("add"), {
    type: "button",
    "data-guided-add": "",
  });
  root.append(fields, varying, add, note);
  source.onchange = () => {
    reference.disabled = Boolean(source.value);
    reference.value = source.value;
  };
  const draw = () => {
    varying.replaceChildren();
    for (const key of Object.keys(controls)) delete controls[key];
    const make = (key, node) => {
      const label = el("label", inputText(key));
      label.append(node);
      varying.append(label);
      controls[key] = node;
      return node;
    };
    const numeric = (key) =>
      make(
        key,
        el("input", "", {
          type: "number",
          step: "any",
          "data-guided-field": key,
        }),
      );
    const kind = chooser.value;
    let numericKeys = [];
    if (kind === "part_rules")
      numericKeys = ["stockX", "stockY", "stockZ", "wall"];
    if (["tool_envelopes", "removal_paths"].includes(kind)) {
      numericKeys = ["lowX", "lowY", "lowZ", "highX", "highY", "highZ"];
      if (kind === "removal_paths")
        numericKeys.push("shiftX", "shiftY", "shiftZ");
      const keepouts = make(
        "keepouts",
        el("select", "", { multiple: "", size: "4" }),
      );
      for (const row of parts.filter((row) => row.id !== part.value))
        keepouts.append(new Option(row.id, row.id));
    }
    if (kind === "tolerance_stacks") {
      numericKeys = ["nominal", "required", "plusMinus"];
      const contributor = make("contributor", el("select"));
      for (const row of parts) contributor.append(new Option(row.id, row.id));
    }
    if (kind === "tooling") {
      make("toolId", el("input", "", { type: "text" }));
      const toolKind = make("toolKind", el("select"));
      for (const key of ["fixture", "mould"])
        toolKind.append(new Option(inputText(key), key));
      numericKeys = ["count"];
    }
    for (const key of numericKeys) numeric(key);
  };
  chooser.onchange = draw;
  part.onchange = () => {
    draw();
    populateSources();
    source.onchange();
  };
  draw();
  add.onclick = () => {
    for (const node of [reference, ...Object.values(controls)])
      node.removeAttribute("aria-invalid");
    try {
      const values = {
        physical_id: part.value,
        basis_reference: source.value || reference.value,
      };
      for (const [key, node] of Object.entries(controls))
        values[key] =
          key === "keepouts"
            ? [...node.selectedOptions].map((option) => option.value)
            : node.value;
      values.keepout_part_ids = values.keepouts;
      const row = manufacturingRule(
        chooser.value,
        values,
        parts.map((row) => row.id),
      );
      write(appendManufacturingRule(read(), chooser.value, row));
      note.textContent = inputText("saved");
    } catch (error) {
      note.textContent = inputText("missing") + " " + error.message;
      const key = Object.keys(inputLabels).find(
        (key) => inputText(key) === error.message,
      );
      const node = key === "reference" ? reference : controls[key];
      if (node) {
        node.setAttribute("aria-invalid", "true");
        node.focus();
      }
    }
  };
}
