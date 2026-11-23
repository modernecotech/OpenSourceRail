/* An offline exercise record contains only choices and numbers. */
(function () {
"use strict";

const identity = Object.freeze({
  edition: "baghdad-airport-factory-workshop/1",
  candidate_id: "b38d4bd348cc57d8f3fab9696df06e5b35ba51380670aa8e566b7f89d9c5da01",
  frame_revision: "5904e648c5de9b4b6ad5cf4c0c5ebfa93d5a35c2c746b3c12ae52eed49c929ae",
  opening_evaluation_id: "6a0580105823dbd30dadde4e44f7d9032aee7a4b210e229950d17673a7231e87",
  factory_evaluation_id: "be5bfe8fa5ff42de8792c720fafedd736a0cfee618ced81ba95dbd18944d891c",
  estimate_evaluation_id: "83de4f2c3023521a1b9a9b02c436b10ffa9c24a67763d700da624e53036ad095",
});
const lessons = [
  {
    id: "buy", role: "Buyer",
    situation: "The fleet lot covers six six-car sets, including spares. Its central allowance is USD 50,880,000. In this exercise, offer A prices all six at USD 9,000,000 per set on matching terms. Offer B prices only three at USD 8,000,000 each.",
    question: "What is the increase in direct fleet cost (USD) if the buyer models offer A?",
    expected: 3120000, calculation: "6 × 9,000,000 − 50,880,000 = USD 3,120,000. Credit the existing direct fleet allowance once.",
    actions: ["Rank B first on its lower total.", "Keep B outside the comparable set and invite a complete revised return in a new round.", "Add both quotations to the opening estimate."],
    correct: 1, rationale: "Supplier B omitted three sets. Preserve its receipt and scope exception. Give suppliers the same edition, quantity, expiry and delivery basis.",
    task: "Prepare a draft Request for Quotation for the fleet lot and mark offer B for clarification. Rehearse using the paper bid register in the instructor guide or an authorised ERPNext training project.",
  },
  {
    id: "cam", role: "CAD/CAM technician",
    situation: "The Airport cut register has 5,184 gross pieces. The section and liner saw takes 3,168 pieces. A subcontractor offers to nest all 5,184 as plate using a drawing from another frame revision.",
    question: "How many plate pieces belong on the subcontract nesting enquiry?",
    expected: 2016, calculation: "5,184 − 3,168 = 2,016 plate pieces. Gross cut quantity is distinct from a released toolpath.",
    actions: ["Accept the nest because the total piece count matches.", "Send the old drawing with a note for the machine operator.", "Reject the mixed issue, match the frame and cut list, then review a preview using the specified stock and units."],
    correct: 2, rationale: "Keep the saw route separate. Bind the plate preview to its source drawing and revision. The shop must approve the machine, controller post, fixture and first article before any production run.",
    task: "Use the CAM guide to locate a digital preview and its source. Record their identities, units, orientation, stock and operation. Write the review disposition for a mismatched drawing.",
  },
  {
    id: "vehicle", role: "Vehicle fabricator",
    situation: "A production plan offers one body build bed for 36 steel bodies. Each body occupies a bed for 60 h. Setup takes 48 h once. The window is 250 days, one 8 h shift per day and 80% availability.",
    question: "How many whole body beds does the planning load require?",
    expected: 2, calculation: "(36 × 60 + 48) ÷ (250 × 8 × 0.8) = 1.38. Round up to two beds.",
    actions: ["Return the one-bed plan and request a two-bed loading sequence, crew cover and post-unclamp datum check.", "Remove setup and inspection hours to fit the offered bed.", "Record one accepted bed and build while the other is surveyed."],
    correct: 0, rationale: "One bed offers 1,600 h against 2,208 h of demand. Two beds provide calendar capacity. The layout, crew cover and as-built geometry still need review.",
    task: "Mark the two beds on a work-centre loading sheet. Map three datum wear pads per bed to jig and position, then record who reviews the post-unclamp survey.",
  },
  {
    id: "precast", role: "Precast yard planner",
    situation: "The baseline uses eight beam positions at eight beams per day and 24 h mould occupancy. The contractor proposes a 48 h occupancy cycle and offers the same eight positions. Positions remain occupied overnight.",
    question: "How many independently usable positions sustain eight beams per day at 48 h occupancy?",
    expected: 16, calculation: "8 beams/day × 48 h/beam ÷ 24 h/day = 16 positions. At eight positions the revised rate is four beams per day.",
    actions: ["Strip early once the dispatch target is reached.", "Request sixteen positions or a revised programme, with transfer strength and independent release evidence.", "Count off-shift curing as free mould time."],
    correct: 1, rationale: "Occupancy continues through cure. Programme pressure cannot substitute for the approved strength at transfer or lifting.",
    task: "Draw two days of mould occupancy, identify the change in output, and give the inspector the pre-pour, batch, cure, strength and survey record references for a mock beam.",
  },
  {
    id: "electrical", role: "Electrical integrator",
    situation: "The wayside register allocates 30 grid protection gateways, 116 section control gateways and six station dispatch controllers. On a paper bench sheet, two different points report the same address. A contractor uses the total allocation as the rectifier cabinet count.",
    question: "How many allocated wayside control devices are in the bench workload?",
    expected: 152, calculation: "30 + 116 + 6 = 152 allocated control devices. The number of installed and tested rectifier cabinets remains open.",
    actions: ["Accept duplicate addressing because the device total agrees.", "Book all 152 devices as rectifier cabinets.", "Hold the affected serials, reconcile the terminal map and repeat the affected point checks against an independent list."],
    correct: 2, rationale: "Log each wrong address against the serial, point-list issue and bench adapter. Request actual rectifier panel drawings and quantities separately.",
    task: "Make a two-point paper I/O list. Inject the duplicate, mark the affected results failed and record the recheck. Use simulated contacts only for this exercise.",
  },
  {
    id: "quality", role: "Quality inspector and maintainer",
    situation: "The study reserves a 1,360 mm rough door opening with 25 mm allowed per edge, giving 1,310 mm nominal clear width. The requirement is 1,300 mm. A synthetic loaded-aperture reading after liner exchange is 1,298 mm.",
    question: "What is the signed clearance margin from the synthetic reading (mm)?",
    expected: -2, calculation: "1,298 − 1,300 = −2 mm. The design allowance of +10 mm cannot clear this measured shortfall in the exercise.",
    actions: ["Hold handback, log the serial and reading, and require corrective work, reinspection and authorised review.", "Release on the +10 mm drawing margin.", "Use the absolute difference as a positive margin."],
    correct: 0, rationale: "Capture the quality issue, method, calibration, installed and removed serials and limit revision. Keep the failed reading with any corrected reading.",
    task: "Create a mock Quality Inspection and repair handover. Simulate an approved adjustment followed by a 1,304 mm check. Record both readings and route the +4 mm result for independent review.",
  },
  {
    id: "instructor", role: "Instructor and shift planner",
    situation: "Four trainees attended the fixture induction. Two have current, independently reviewed authorisations for this exact fixture and task. One has expired authorisation. The fourth has only the completed online exercise.",
    question: "How many are eligible under this exercise's stated authorisation criterion?",
    expected: 2, calculation: "Two current in-scope authorisations qualify. The expired record requires reassessment and the attendance-only record requires task assessment.",
    actions: ["Assign all four on the strength of the attendance list.", "Check scope, expiry and restrictions before assignment and route the other two to supervised practice or reassessment.", "Extend the expired record using the online score."],
    correct: 1, rationale: "Frappe HR Training Event attendance and Training Result support the competence file. An accountable assessor issues the separate scope, restrictions and validity.",
    task: "Have a partner explain one failed shop case, reproduce the result, and identify the handover owner. Record the observation separately from the automatic arithmetic check.",
  },
];

function assess(id, answer, action) {
  const lesson = lessons.find(item => item.id === id);
  if (!lesson || !Number.isFinite(answer) || !Number.isInteger(action) ||
      action < 0 || action >= lesson.actions.length) throw new Error("Choose a listed case and action and enter a finite number.");
  return {id, answer, action, calculation_ok: answer === lesson.expected, disposition_ok: action === lesson.correct};
}
function replay(record) {
  if (!record || Object.keys(identity).some(key => record[key] !== identity[key])) {
    throw new Error("The saved exercise belongs to another edition, candidate, frame or evaluation. Open its matching workshop.");
  }
  if (record.evidence_class !== "offline_training_fixture") throw new Error("Choose an offline training record.");
  if (!Array.isArray(record.attempts)) throw new Error("The attempt list is missing.");
  return record.attempts.map(attempt => assess(attempt.id, attempt.answer, attempt.action));
}
function record(attempts) {
  return {...identity, evidence_class: "offline_training_fixture", attempts: attempts.map(a => assess(a.id, a.answer, a.action))};
}

function start() {
  const byId = id => document.getElementById(id);
  const picker = byId("case");
  let attempts = [];
  const status = byId("status");
  const history = byId("history");
  function updateHistory() {
    history.replaceChildren();
    attempts.forEach(a => {
      const li = document.createElement("li");
      const l = lessons.find(item => item.id === a.id);
      li.textContent = l.role + " · " + a.answer + " · " + l.actions[a.action] + " · " +
        (a.calculation_ok ? "Calculation correct" : "Recheck calculation") + " · " +
        (a.disposition_ok ? "Disposition correct" : "Recheck disposition");
      history.appendChild(li);
    });
    byId("save").disabled = !attempts.length;
  }
  function showCase() {
    const l = lessons.find(item => item.id === picker.value);
    byId("situation").textContent = l.situation;
    byId("quantity-label").textContent = l.question;
    byId("task").textContent = l.task;
    byId("quantity").value = "";
    const choices = byId("choices");
    choices.replaceChildren();
    l.actions.forEach((title, index) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "radio";
      input.name = "action";
      input.value = index;
      input.required = true;
      label.append(input, " " + title);
      choices.appendChild(label);
    });
    status.textContent = "";
  }
  lessons.forEach(l => picker.add(new Option(l.role, l.id)));
  picker.addEventListener("change", showCase);
  byId("exercise").addEventListener("submit", event => {
    event.preventDefault();
    const action = byId("exercise").elements.action.value;
    const result = assess(picker.value, byId("quantity").valueAsNumber, Number(action));
    const l = lessons.find(item => item.id === picker.value);
    attempts.push(result);
    status.textContent = (result.calculation_ok ? "Correct calculation. " : "Recheck the quantity. ") + l.calculation +
      (result.disposition_ok ? " Correct disposition. " : " Reconsider the disposition. ") + l.rationale;
    updateHistory();
  });
  byId("save").addEventListener("click", () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(record(attempts), null, 2)], {type: "application/json"}));
    const link = document.createElement("a");
    link.href = url;
    link.download = "airport-workshop-attempts.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  byId("restore").addEventListener("change", async event => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      const imported = replay(JSON.parse(await file.text()));
      attempts.push(...imported);
      updateHistory();
      byId("file-status").textContent = imported.length + (imported.length === 1 ? " attempt" : " attempts") + " replayed and added to this session.";
    } catch (error) {
      byId("file-status").textContent = "Import failed. " + error.message;
    }
    event.target.value = "";
  });
  showCase();
  updateHistory();
}
if (typeof module !== "undefined" && module.exports) module.exports = {identity, lessons, assess, replay, record};
if (typeof document !== "undefined") start();
})();
