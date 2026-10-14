// A schematic of represented locations and explicit joint links, never a CAD claim.
import {
  element as el,
  table,
  evidenceBadge,
  quantityText,
} from "./components.js";
import { language } from "../workbench/i18n.js";

export const assemblyLabels = {
  heading: [
    "Assembly locations and correspondence",
    "مواقع التجميع وترابط الأجزاء",
  ],
  scope: [
    "Schematic of represented part centres. Unmodelled inventory and capacity remain unresolved.",
    "مخطط لمراكز الأجزاء الممثلة. تبقى الأجزاء غير الممثلة وقدراتها دون حسم.",
  ],
  part: ["Physical part", "الجزء الفعلي"],
  property: ["Property", "الخاصية"],
  value: ["Value", "القيمة"],
  partId: ["Catalogue part ID", "معرف جزء الكتالوج"],
  revision: ["Revision", "المراجعة"],
  quantity: ["Represented quantity", "الكمية الممثلة"],
  material: ["Material", "المادة"],
  mass: ["Defined mass [kg]", "الكتلة المعرفة [kg]"],
  missing: ["Unresolved installed allocations", "تخصيصات التركيب غير المحسومة"],
  joints: [
    "Explicit joints involving this part",
    "الوصلات الصريحة المرتبطة بهذا الجزء",
  ],
  none: [
    "No explicit part-level joint correspondence is declared.",
    "لم يحدد ترابط صريح للوصلات على مستوى هذا الجزء.",
  ],
  checks: ["Checks associated with this part", "الفحوص المرتبطة بهذا الجزء"],
  unlocated: [
    "Candidate-level checks have no declared part localization.",
    "فحوص المرشح لا تحدد موقعاً على مستوى الجزء.",
  ],
  check: ["Check", "الفحص"],
  state: ["Evidence state", "حالة الأدلة"],
  basis: ["Basis", "الأساس"],
  details: ["Native part definition", "تعريف الجزء الأصلي"],
  why: [
    "Recorded reasons and limiting observables",
    "الأسباب المسجلة والقيم الحاكمة",
  ],
  limit: ["Limit", "الحد"],
  observed: ["Observed", "القيمة المرصودة"],
  noObservable: [
    "No scalar limit is recorded; inspect the retained check details.",
    "لا يوجد حد عددي مسجل؛ راجع تفاصيل الفحص المحفوظة.",
  ],
  variables: ["Candidate variables", "متغيرات المرشح"],
  matrix: ["Check comparison across candidates", "مقارنة الفحوص بين المرشحين"],
};
export const assemblyText = (key) =>
  assemblyLabels[key][language() === "ar" ? 1 : 0];

export function physicalParts(candidate) {
  const data = candidate.definition || {};
  return data.contract?.parts || data.model?.instances || [];
}
function locations(candidate) {
  const data = candidate.definition || {};
  const instanceModel = Boolean(data.model?.instances);
  return physicalParts(candidate).map((part) => {
    const properties = part.properties?.design || part.properties || {};
    let cg = properties.cg_m;
    if (!Array.isArray(cg) || cg.length !== 3 || !cg.every(Number.isFinite))
      return { id: part.id, point: null };
    if (instanceModel) {
      const transform = part.transform;
      if (!transform?.rotation || !transform?.translation_m)
        return { id: part.id, point: null };
      cg = transform.rotation.map((row, i) =>
        row.reduce(
          (sum, value, j) => sum + value * cg[j],
          transform.translation_m[i],
        ),
      );
    }
    return { id: part.id, point: cg };
  });
}
export function partReferences(value, physicalIds) {
  const ids = new Set(physicalIds);
  const result = new Set();
  const visit = (item) => {
    if (typeof item === "string" && ids.has(item)) result.add(item);
    else if (Array.isArray(item)) item.forEach(visit);
    else if (item && typeof item === "object")
      Object.values(item).forEach(visit);
  };
  visit(value);
  return [...result];
}
export function failedObservables(candidate) {
  return Object.entries(candidate.checks || {})
    .filter(
      ([, row]) =>
        row.state === "failed" ||
        row.state === "outside-domain" ||
        row.state === "budget-exceeded",
    )
    .map(([name, row]) => ({
      name,
      state: row.state,
      basis: row.basis,
      value:
        typeof row.value === "number" && Number.isFinite(row.value)
          ? row.value
          : null,
      limit:
        typeof row.limit === "number" && Number.isFinite(row.limit)
          ? row.limit
          : null,
      unit: row.unit || "",
    }));
}
export function comparisonReasons(candidate) {
  const root = el("div", "", { class: "candidate-reasons" });
  root.append(el("h4", assemblyText("why")));
  for (const row of failedObservables(candidate)) {
    const item = el("p");
    item.append(
      el("strong", row.name + " · "),
      evidenceBadge(row.state),
      document.createTextNode(" " + (row.basis || "")),
    );
    item.append(
      el("br"),
      document.createTextNode(
        row.value !== null && row.limit !== null
          ? `${assemblyText("observed")}: ${row.value} ${row.unit}; ${assemblyText("limit")}: ${row.limit} ${row.unit}`
          : assemblyText("noObservable"),
      ),
    );
    root.append(item);
  }
  const details = el("details");
  details.append(
    el("summary", assemblyText("variables")),
    table(
      [assemblyText("property"), assemblyText("value")],
      Object.entries(candidate.variables || {}),
    ),
  );
  root.append(details);
  return root;
}
export function checkComparison(candidates) {
  const names = [
    ...new Set(
      candidates.flatMap((candidate) => Object.keys(candidate.checks || {})),
    ),
  ];
  const wrapper = el("div", "", {
    class: "comparison-scroll",
    tabindex: "0",
    "aria-label": assemblyText("matrix"),
  });
  wrapper.append(
    el("h3", assemblyText("matrix")),
    table(
      [assemblyText("check"), ...candidates.map((row) => row.id)],
      names.map((name) => [
        name,
        ...candidates.map((row) =>
          evidenceBadge(row.checks?.[name]?.state || "unknown"),
        ),
      ]),
    ),
  );
  return wrapper;
}

export function assemblyInspector(root, candidate, { onPart = () => {} } = {}) {
  const parts = physicalParts(candidate);
  const data = candidate.definition || {};
  const register = data.installed_register || {};
  root.append(
    el("h3", assemblyText("heading")),
    el("p", assemblyText("scope")),
  );
  const label = el("label", assemblyText("part"));
  const select = el("select", "", { "aria-label": assemblyText("part") });
  for (const part of parts) select.append(new Option(part.id, part.id));
  label.append(select);
  root.append(label);
  const coordinates = locations(candidate).filter((row) => row.point !== null);
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 800 260");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", assemblyText("heading"));
  svg.classList.add("assembly-schematic");
  const detail = el("div", "", { "data-assembly-detail": "" });
  root.append(svg, detail);
  const dimensions = [0, 1, 2]
    .map((axis) => ({
      axis,
      span: coordinates.length
        ? Math.max(...coordinates.map((row) => row.point[axis])) -
          Math.min(...coordinates.map((row) => row.point[axis]))
        : 0,
    }))
    .sort((a, b) => b.span - a.span);
  const project = (point, index) => {
    if (!point)
      return [20 + (index % 30) * 25, 20 + Math.floor(index / 30) * 15];
    return dimensions.slice(0, 2).map(({ axis, span }, index) => {
      const low = Math.min(...coordinates.map((row) => row.point[axis]));
      return (
        20 +
        (span ? (point[axis] - low) / span : 0.5) * (index === 0 ? 760 : 220)
      );
    });
  };
  const positions = new Map(
    locations(candidate).map((row, index) => [
      row.id,
      project(row.point, index),
    ]),
  );
  const ids = parts.map((part) => part.id);
  const joints =
    register.joints ||
    data.contract?.assembly_joints ||
    data.model?.joints ||
    [];
  const circles = new Map();
  for (const part of parts) {
    const circle = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "circle",
    );
    const [x, y] = positions.get(part.id);
    circle.setAttribute("cx", x);
    circle.setAttribute("cy", y);
    circle.setAttribute("r", "3");
    circle.dataset.physicalId = part.id;
    const title = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "title",
    );
    title.textContent = part.id;
    circle.append(title);
    circle.onclick = () => {
      select.value = part.id;
      select.onchange();
    };
    svg.append(circle);
    circles.set(part.id, circle);
  }
  select.onchange = () => {
    const part = parts.find((row) => row.id === select.value);
    if (!part) return;
    for (const [id, circle] of circles) {
      circle.classList.toggle("selected", id === part.id);
      circle.setAttribute("r", id === part.id ? "7" : "3");
    }
    const installed = (register.parts || []).find(
      (row) => row.physical_id === part.id,
    );
    const prop = part.properties?.design || part.properties || {};
    detail.replaceChildren(
      table(
        [assemblyText("property"), assemblyText("value")],
        [
          [
            assemblyText("partId"),
            installed?.part_id ?? part.part_id ?? part.id,
          ],
          [assemblyText("revision"), part.revision ?? quantityText(null)],
          [
            assemblyText("quantity"),
            quantityText(installed?.quantity, installed?.unit || ""),
          ],
          [assemblyText("material"), installed?.material ?? quantityText(null)],
          [
            assemblyText("mass"),
            quantityText(installed?.defined_mass_kg ?? prop.mass_kg, "kg"),
          ],
        ],
      ),
      el("h4", assemblyText("joints")),
    );
    const connected = joints.filter((joint) =>
      partReferences(joint, ids).includes(part.id),
    );
    if (!connected.length) detail.append(el("p", assemblyText("none")));
    for (const joint of connected) {
      const entry = el("details");
      entry.append(el("summary", joint.id || quantityText(null)));
      const links = el("div", "", { class: "actions" });
      for (const id of partReferences(joint, ids)) {
        const button = el("button", id, { type: "button" });
        button.onclick = () => {
          select.value = id;
          select.onchange();
        };
        links.append(button);
      }
      entry.append(links, el("pre", JSON.stringify(joint, null, 2)));
      detail.append(entry);
    }
    const localChecks = [
      ...(register.dimensional_manufacturing?.checks || []),
      ...Object.entries(candidate.checks || {}).map(([id, row]) => ({
        id,
        ...row,
      })),
    ].filter(
      (row) =>
        row.physical_id === part.id ||
        (row.physical_part_ids || []).includes(part.id),
    );
    detail.append(el("h4", assemblyText("checks")));
    if (localChecks.length)
      detail.append(
        table(
          [assemblyText("check"), assemblyText("state"), assemblyText("basis")],
          localChecks.map((row) => [
            row.id,
            evidenceBadge(row.state),
            row.basis || row.basis_reference || "",
          ]),
        ),
      );
    else detail.append(el("p", assemblyText("unlocated")));
    const original = el("details");
    original.append(
      el("summary", assemblyText("details")),
      el("pre", JSON.stringify(part, null, 2)),
    );
    detail.append(original);
    onPart(part);
  };
  select.onchange();
  const missing = el("details");
  missing.append(
    el("summary", assemblyText("missing")),
    el("pre", JSON.stringify(register.unresolved_allocations ?? null, null, 2)),
  );
  root.append(missing);
  return select;
}
