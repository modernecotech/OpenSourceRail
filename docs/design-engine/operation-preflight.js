import { language } from "../workbench/i18n.js";

export const operationLabels = {
  screen: ["Screening", "الفحص الأولي"],
  optimise: ["Optimisation", "التحسين"],
  confirm: ["Detailed confirmation", "التأكيد التفصيلي"],
  "cad-export": ["Native CAD export", "تصدير CAD الأصلي"],
  available: ["Local prerequisites available", "متطلبات التنفيذ المحلي متوفرة"],
  missing: ["Missing prerequisites", "متطلبات مفقودة"],
  unknown: ["Operation preflight unavailable", "فحص متطلبات العملية غير متاح"],
  cadButton: ["Check native CAD export setup", "فحص متطلبات تصدير CAD الأصلي"],
  domain: [
    "Model domains and physical acceptance gates still apply.",
    "تبقى مجالات النماذج وبوابات القبول المادي سارية.",
  ],
};
export const operationText = (key) =>
  operationLabels[key][language() === "ar" ? 1 : 0];
export function requestedOperations({ search = false, refine = false } = {}) {
  return [
    "screen",
    ...(search ? ["optimise"] : []),
    ...(refine ? ["confirm"] : []),
  ];
}
export function operationReadiness(operations, screen, selection) {
  const rows = requestedOperations(selection).map((operation) => ({
    operation,
    ...(operations?.[operation] ||
      (operation === "screen" ? screen : null) || {
        available: false,
        missing: [operationText("unknown")],
      }),
  }));
  return { available: rows.every((row) => row.available === true), rows };
}
export function operationMessage(result) {
  return `${operationText(result.operation)}: ${result.available === true ? operationText("available") : operationText("missing") + " · " + (result.missing || [operationText("unknown")]).join(", ")}`;
}
