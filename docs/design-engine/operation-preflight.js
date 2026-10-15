import { language } from "../workbench/i18n.js";

export const operationLabels = {
  screen: ["Screening", "الفحص الأولي"],
  optimise: ["Optimisation", "التحسين"],
  confirm: ["Detailed confirmation", "التأكيد التفصيلي"],
  iterate: ["Recursive native iteration", "التكرار الأصلي المتتابع"],
  iterateLabel: [
    "Iterate designs using actual native test feedback",
    "تكرار التصاميم باستخدام نتائج الاختبارات الأصلية الفعلية",
  ],
  iterateHelp: [
    "Uses bounded design changes and native confirmation. Paired search is a separate experiment. Physical qualification remains open.",
    "يستخدم تغييرات تصميم محدودة وتأكيداً أصلياً. البحث المقارن تجربة منفصلة. يبقى التأهيل المادي مفتوحاً.",
  ],
  recursiveResults: ["Recursive iteration results", "نتائج التكرار المتتابع"],
  incumbent: ["Verified numerical incumbent", "المرشح العددي المتحقق الحالي"],
  termination: ["Termination reason", "سبب التوقف"],
  verificationScope: ["Verification scope", "نطاق التحقق"],
  conditionalBest: [
    "Best in the declared finite domain",
    "الأفضل ضمن المجال المحدود المعلن",
  ],
  established: [
    "Established for the declared numerical checks only",
    "مثبت للفحوص العددية المعلنة فقط",
  ],
  unestablished: ["Not established", "غير مثبت"],
  noIncumbent: [
    "No numerically verified candidate",
    "لا يوجد مرشح متحقق عددياً",
  ],
  noDomainClaim: [
    "No exhaustive finite-domain claim",
    "لا يوجد ادعاء باستنفاد المجال المحدود",
  ],
  researchOnly: [
    "No global optimum or physical release is established.",
    "لم يتم إثبات حل أمثل عالمي أو منح تصريح مادي.",
  ],
  lineage: [
    "Iteration lineage and adverse outcomes",
    "تسلسل التكرارات والنتائج السلبية",
  ],
  attempt: ["Attempt", "المحاولة"],
  phase: ["Phase", "المرحلة"],
  parent: ["Parent candidate", "المرشح الأصل"],
  candidate: ["Candidate", "المرشح"],
  variables: ["Variables", "المتغيرات"],
  outcome: ["Outcome", "النتيجة"],
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
export function requestedOperations({
  search = false,
  refine = false,
  iterate = false,
} = {}) {
  if (iterate) return ["screen", "iterate"];
  return [
    "screen",
    ...(search ? ["optimise"] : []),
    ...(refine ? ["confirm"] : []),
  ];
}
export function recursiveTuning(problem) {
  return {
    evaluations: 32,
    iterations: 32,
    confirmations: 12,
    finite_exhaustive: ["mechanical-cleat", "civil-steel-beam"].includes(
      problem.adapter || problem.id,
    ),
  };
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
