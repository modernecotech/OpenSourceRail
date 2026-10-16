// Execution progress and validated comparisons remain separate evidence.
import { element as el, table, evidenceBadge } from "./components.js";
import { language } from "../workbench/i18n.js";

export const refinementLabels = {
  heading: ["Independent passage refinement", "تنقيح مستقل لعبور القطار"],
  scope: [
    "Separate time, deck, rail and modal comparisons. Passing the provisional numerical screen does not establish physical validation or the complete operating envelope.",
    "مقارنات منفصلة للزمن والجسر والسكة والأنماط. اجتياز الفحص العددي الأولي لا يثبت التحقق الفيزيائي أو كامل نطاق التشغيل.",
  ],
  scenario: ["Scenario", "السيناريو"],
  planned: ["Cases planned", "الحالات المخططة"],
  executed: ["Cases executed", "الحالات المنفذة"],
  validated: ["Axis comparisons passed", "مقارنات المحاور المجتازة"],
  case: ["Case", "الحالة"],
  execution: ["Execution", "التنفيذ"],
  coverage: ["Complete passage", "العبور الكامل"],
  provenance: ["Verified provenance", "مصدر الأدلة المتحقق منه"],
  comparison: ["Numerical comparison", "المقارنة العددية"],
  issues: ["Provenance issues", "مشكلات مصدر الأدلة"],
  baseline: ["Baseline", "الحالة المرجعية"],
};
const text = (key) => refinementLabels[key][language() === "ar" ? 1 : 0];

export function refinementRows(candidate) {
  return Object.entries(
    candidate.definition?.independent_refinement_campaigns || {},
  ).flatMap(([scenario, campaign]) =>
    Object.entries(campaign.cases || {}).map(([id, result]) => {
      const comparison = campaign.comparison?.cases?.find(
        (row) => row.id === id,
      );
      const baseline = id === "baseline";
      return {
        scenario,
        id,
        execution: result.state || "not-run",
        coverage: result.full_passage_coverage === true,
        provenance: baseline
          ? campaign.comparison?.baseline_provenance_verified === true
          : comparison?.provenance_verified === true,
        comparison: baseline ? null : comparison?.state || "unknown",
        issues: baseline
          ? campaign.comparison?.baseline_provenance_issues || []
          : comparison?.provenance_issues || [],
      };
    }),
  );
}

export function refinementCampaigns(root, candidate) {
  const campaigns = candidate.definition?.independent_refinement_campaigns;
  if (!campaigns) return;
  const section = el("section", "", { "data-refinement-campaign": "" });
  section.append(el("h3", text("heading")), el("p", text("scope")));
  section.append(
    table(
      [text("scenario"), text("planned"), text("executed"), text("validated")],
      Object.entries(campaigns).map(([name, campaign]) => [
        name,
        campaign.planned,
        campaign.executed,
        campaign.validated,
      ]),
    ),
  );
  const wrapper = el("div", "", {
    class: "comparison-scroll",
    tabindex: "0",
    "aria-label": text("heading"),
  });
  wrapper.append(
    table(
      [
        text("scenario"),
        text("case"),
        text("execution"),
        text("coverage"),
        text("provenance"),
        text("comparison"),
        text("issues"),
      ],
      refinementRows(candidate).map((row) => [
        row.scenario,
        row.id,
        row.execution,
        evidenceBadge(row.coverage ? "passed" : "unknown"),
        evidenceBadge(row.provenance ? "passed" : "unknown"),
        row.comparison === null
          ? text("baseline")
          : evidenceBadge(row.comparison),
        row.issues.join("; "),
      ]),
    ),
  );
  section.append(wrapper);
  root.append(section);
}
