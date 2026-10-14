// Reviewed source use creates a new immutable numerical study, with fresh checks.
import { element as el, table } from "./components.js";
import { language } from "../workbench/i18n.js";

export const revisionLabels = {
  heading: ["Reviewed input revision", "مراجعة المدخلات بعد التحقق"],
  scope: [
    "Retain checked drafts and exact applicable source records, obtain independent permission for numerical use, then run a new revision. Existing results and the adopted baseline remain separate.",
    "احفظ المسودات المفحوصة وسجلات المصادر المنطبقة بدقة، واحصل على إذن مستقل للاستخدام العددي، ثم نفذ مراجعة جديدة. تبقى النتائج السابقة وخط الأساس المعتمد منفصلة.",
  ],
  unknown: [
    "A known research baseline and named configuration revision are required. Enter that scope and rerun the parent candidate before binding reviewed inputs.",
    "يلزم خط أساس بحثي معروف ومراجعة تكوين مسماة. أدخل ذلك النطاق وأعد تنفيذ المرشح الأصلي قبل ربط المدخلات المراجعة.",
  ],
  drafts: ["Checked draft sources", "مصادر المسودات المفحوصة"],
  noDraft: [
    "Retain and check an engineering draft to select its exact SHA256.",
    "احفظ مسودة هندسية وافحصها لاختيار بصمتها الدقيقة SHA256.",
  ],
  records: [
    "Verified records for this candidate and definition",
    "السجلات المتحقق منها لهذا المرشح والتعريف",
  ],
  noRecords: [
    "No independently verified applicable source records are available.",
    "لا توجد سجلات مصادر منطبقة متحقق منها بصورة مستقلة.",
  ],
  revision: ["New configuration revision", "مراجعة التكوين الجديدة"],
  rationale: ["Input-change rationale", "مبررات تغيير المدخلات"],
  policy: ["Input applicability policy", "سياسة انطباق المدخلات"],
  exact: ["Exact physical definition", "التعريف الفعلي المطابق"],
  ids: [
    "Retained physical IDs for manufacturing alternatives",
    "معرفات الأجزاء المحتفظ بها لبدائل التصنيع",
  ],
  propose: ["Create immutable input proposal", "إنشاء مقترح مدخلات ثابت"],
  choose: [
    "Select at least one checked draft and one verified applicable source record.",
    "اختر مسودة مفحوصة واحدة على الأقل وسجل مصدر منطبقاً متحققاً منه.",
  ],
  retained: [
    "Input proposal retained; independent review is required before numerical use.",
    "تم حفظ مقترح المدخلات؛ تلزم مراجعة مستقلة قبل الاستخدام العددي.",
  ],
  refresh: ["Refresh input proposals", "تحديث مقترحات المدخلات"],
  reviewRationale: [
    "Independent numerical-use rationale",
    "مبررات الإذن المستقل بالاستخدام العددي",
  ],
  review: [
    "Review exact proposal for numerical use",
    "مراجعة المقترح المطابق للاستخدام العددي",
  ],
  reviewed: [
    "Numerical-use review retained. This grants no physical acceptance.",
    "تم حفظ مراجعة الاستخدام العددي. لا تمنح قبولاً مادياً.",
  ],
  author: ["Author", "المؤلف"],
  state: ["State", "الحالة"],
  target: ["Target configuration revision", "مراجعة التكوين المستهدفة"],
  invalidated: [
    "Results invalidated in the new revision",
    "النتائج الملغاة في المراجعة الجديدة",
  ],
  refine: [
    "Run detailed confirmation and holdouts",
    "تنفيذ التأكيد التفصيلي وحالات التحقق المستقلة",
  ],
  search: [
    "Rerun seeded optimisation and equal-budget controls",
    "إعادة التحسين ببذور محددة وضوابط متساوية الميزانية",
  ],
  budget: ["Evaluation budget", "ميزانية التقييمات"],
  run: [
    "Run new revision with fresh checks",
    "تنفيذ المراجعة الجديدة بفحوص جديدة",
  ],
  queued: [
    "New numerical revision queued",
    "تمت إضافة المراجعة العددية الجديدة إلى قائمة التنفيذ",
  ],
  open: ["Open the new revision and job", "فتح المراجعة والمهمة الجديدتين"],
  noProposals: [
    "No retained input proposals for this parent candidate.",
    "لا توجد مقترحات مدخلات محفوظة لهذا المرشح الأصلي.",
  ],
};
const text = (key) => revisionLabels[key][language() === "ar" ? 1 : 0];

export function eligibleRevisionRecords(records, candidate) {
  const hash =
    candidate.definition?.installed_register?.physical_definition_sha256;
  return records.filter(
    (record) =>
      record.state === "verified" &&
      record.applicability?.candidate_id === candidate.id &&
      record.applicability?.definition_sha256 === hash,
  );
}
export function revisionLink(identity, job, base = location.href) {
  const url = new URL(base);
  for (const [key, value] of Object.entries({
    city: identity.city,
    project: identity.project,
    environment: identity.environment,
    revision: identity.configuration_revision,
    baseline_sha256: identity.baseline_sha256 || "",
    run_id: identity.run_id || "",
    selected_asset: identity.asset_id || "",
    selected_part: identity.part_id || "",
    view: "jobs",
  }))
    url.searchParams.set(key, value);
  url.searchParams.set("job", job.id);
  return url.href;
}
export function inputRevisionPanel(
  root,
  {
    identity,
    candidate,
    job,
    sourceState,
    records,
    drafts,
    api,
    actor,
    accountsConfigured,
  },
) {
  root.replaceChildren(el("h3", text("heading")), el("p", text("scope")));
  const known = Boolean(
    identity.baseline_sha256 &&
    identity.configuration_revision !== "unselected",
  );
  if (!known) root.append(el("p", text("unknown")));
  const form = el("form", "", { id: "inputRevisionForm" });
  const draftField = el("fieldset");
  draftField.append(el("legend", text("drafts")));
  if (!drafts.length) draftField.append(el("p", text("noDraft")));
  for (const draft of drafts) {
    const label = el("label", `${draft.kind} · ${draft.sha}`);
    const input = el("input", "", {
      type: "checkbox",
      "data-revision-draft": draft.sha,
    });
    input.checked = true;
    label.prepend(input);
    draftField.append(label);
  }
  const applicable = eligibleRevisionRecords(records, candidate);
  const recordField = el("fieldset");
  recordField.append(el("legend", text("records")));
  if (!applicable.length) recordField.append(el("p", text("noRecords")));
  for (const record of applicable) {
    const label = el(
      "label",
      `${record.kind} · ${record.id} · ${record.revision}`,
    );
    const input = el("input", "", {
      type: "checkbox",
      "data-revision-record": record.id,
    });
    label.prepend(input);
    recordField.append(label);
  }
  const revision = el("input", "", {
    type: "text",
    required: "",
    maxlength: "160",
    "data-input-revision-name": "",
  });
  const revisionLabel = el("label", text("revision"));
  revisionLabel.append(revision);
  const rationale = el("textarea", "", {
    rows: "3",
    required: "",
    maxlength: "8000",
    "data-input-revision-rationale": "",
  });
  const rationaleLabel = el("label", text("rationale"));
  rationaleLabel.append(rationale);
  const policy = el("select", "", { "data-input-revision-policy": "" });
  policy.append(
    new Option(text("exact"), "exact-definition"),
    new Option(text("ids"), "retained-physical-ids"),
  );
  const policyLabel = el("label", text("policy"));
  policyLabel.append(policy);
  const submit = el("button", text("propose"));
  submit.disabled = !known || sourceState !== "current";
  const status = el("p", "", { role: "status", "aria-live": "polite" });
  form.append(
    draftField,
    recordField,
    revisionLabel,
    rationaleLabel,
    policyLabel,
    submit,
    status,
  );
  root.append(form);
  const retained = el("div", "", { "data-input-proposals": "" });
  const refresh = el("button", text("refresh"), { type: "button" });
  root.append(refresh, retained);
  async function load() {
    try {
      const payload = await api("input-revisions");
      const proposals = (payload.revisions || []).filter(
        (row) =>
          row.parent_job === job &&
          row.proposal?.parent_candidate === candidate.id,
      );
      retained.replaceChildren();
      if (!proposals.length) retained.append(el("p", text("noProposals")));
      for (const row of proposals) {
        const section = el("section", "", { "data-input-proposal": row.id });
        section.append(
          el("h4", row.id),
          table(
            [text("state"), text("author"), text("target")],
            [
              [
                row.state,
                row.creator,
                row.target_identity?.configuration_revision ||
                  row.proposal?.target_identity?.configuration_revision,
              ],
            ],
          ),
        );
        const invalidated = el("details");
        invalidated.append(
          el("summary", text("invalidated")),
          el("pre", JSON.stringify(row.proposal.invalidated || [], null, 2)),
        );
        section.append(invalidated);
        const reviewLabel = el("label", text("reviewRationale"));
        const reviewRationale = el("textarea", "", {
          rows: "2",
          maxlength: "8000",
          "data-input-review-rationale": "",
        });
        reviewLabel.append(reviewRationale);
        const review = el("button", text("review"), { type: "button" });
        review.disabled =
          row.state !== "proposed" ||
          !accountsConfigured ||
          actor?.username === row.creator ||
          !actor?.roles?.some((role) => ["admin", "approver"].includes(role));
        review.onclick = async () => {
          try {
            await api(`input-revisions/${row.id}/review`, {
              revision: row.proposal_sha256,
              rationale: reviewRationale.value,
            });
            status.textContent = text("reviewed");
            await load();
          } catch (error) {
            status.textContent = error.message;
          }
        };
        const runForm = el("div");
        const refine = el("input", "", { type: "checkbox" });
        const refineLabel = el("label", text("refine"));
        refineLabel.prepend(refine);
        const search = el("input", "", { type: "checkbox" });
        const searchLabel = el("label", text("search"));
        searchLabel.prepend(search);
        const budget = el("input", "", {
          type: "number",
          min: "1",
          max: "1024",
          value: "256",
        });
        const budgetLabel = el("label", text("budget"));
        budgetLabel.append(budget);
        const canRun = actor?.roles?.some((role) =>
          ["admin", "planner"].includes(role),
        );
        const run = el("button", text("run"), { type: "button" });
        run.disabled =
          row.state !== "reviewed-input" ||
          sourceState !== "current" ||
          !canRun;
        run.onclick = async () => {
          run.disabled = true;
          try {
            const value = Number(budget.value);
            if (!Number.isInteger(value) || value < 1 || value > 1024)
              throw Error(text("budget"));
            const result = await api(`input-revisions/${row.id}/run`, {
              search: search.checked
                ? { seeds: [11, 29, 47], evaluations: 16 }
                : null,
              refine: refine.checked,
              budget: { evaluations: value },
            });
            status.replaceChildren(
              document.createTextNode(
                text("queued") + " · " + result.job.id + " ",
              ),
              el("a", text("open"), {
                href: revisionLink(result.child_identity, result.job),
                target: "_blank",
                rel: "noopener",
              }),
            );
          } catch (error) {
            status.textContent = error.message;
          } finally {
            run.disabled =
              row.state !== "reviewed-input" ||
              sourceState !== "current" ||
              !canRun;
          }
        };
        runForm.append(refineLabel, searchLabel, budgetLabel, run);
        section.append(reviewLabel, review, runForm);
        retained.append(section);
      }
    } catch (error) {
      status.textContent = error.message;
    }
  }
  refresh.onclick = load;
  form.onsubmit = async (event) => {
    event.preventDefault();
    submit.disabled = true;
    try {
      const chosenDrafts = [
        ...form.querySelectorAll("[data-revision-draft]:checked"),
      ].map((node) => node.dataset.revisionDraft);
      const chosenIds = [
        ...form.querySelectorAll("[data-revision-record]:checked"),
      ].map((node) => node.dataset.revisionRecord);
      if (!chosenDrafts.length || !chosenIds.length)
        throw Error(text("choose"));
      await api(`jobs/${job}/input-revisions`, {
        candidate: candidate.id,
        drafts: chosenDrafts,
        records: applicable
          .filter((row) => chosenIds.includes(row.id))
          .map((row) => ({
            id: row.id,
            revision: row.revision,
            applicability: row.applicability,
          })),
        configuration_revision: revision.value,
        rationale: rationale.value,
        policy: policy.value,
      });
      status.textContent = text("retained");
      await load();
    } catch (error) {
      status.textContent = error.message;
    } finally {
      submit.disabled = !known || sourceState !== "current";
    }
  };
  load();
}
