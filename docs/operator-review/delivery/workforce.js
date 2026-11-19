"use strict";
const byId = id => document.getElementById(id);
const number = new Intl.NumberFormat("en-US");
const usd = value => "$" + number.format(Math.round(value));
const millions = value => "$" + value.toLocaleString("en-US", {minimumFractionDigits:3, maximumFractionDigits:3}) + "m";
const commonRoles = ["station duty and passenger assistance", "station security and cleaning",
  "OCC control, traction, incidents and information", "depot rolling-stock technicians",
  "civil, track and power response", "planning, payroll, stores and trainers"];
const roleRows = new Map();
const creditInputs = new Map();
const railway = () => workforceStudy.studies[byId("railway").value];
const scenario = () => railway().workforce_scenarios[byId("mode").value];
function amountField(label, positive, step) {
  const input = document.createElement("input");
  input.type = "number";
  input.min = positive ? "0.01" : "0";
  input.step = step;
  input.setAttribute("aria-label", label);
  input.addEventListener("input", render);
  return input;
}
function buildRows(keepCommonRates = false) {
  const previous = new Map();
  if (keepCommonRates) for (const [role, row] of roleRows) previous.set(role, row.rate.value);
  const body = byId("roles");
  body.replaceChildren();
  roleRows.clear();
  for (const name of [scenario().onboard_role, ...commonRoles]) {
    const tr = body.insertRow();
    tr.insertCell().textContent = name[0].toUpperCase() + name.slice(1);
    const duty = tr.insertCell(), reference = tr.insertCell(), count = tr.insertCell();
    const rate = amountField(name + " loaded annual pay in USD", true, "0.01");
    rate.placeholder = "Common";
    rate.value = previous.get(name) || "";
    rate.disabled = scenario().posts_fte[name] === 0;
    tr.insertCell().append(rate);
    roleRows.set(name, {duty, reference, count, rate});
  }
}
function buildCredits() {
  const target = byId("credits");
  target.replaceChildren();
  creditInputs.clear();
  for (const [name, allowance] of Object.entries(railway().opex.eligible_envelopes_usd_m_year)) {
    const line = document.createElement("div"), label = document.createElement("label");
    line.className = "credit";
    const input = amountField(name + " embedded annual payroll in USD millions", false, "any");
    input.id = "credit-" + creditInputs.size;
    input.max = String(allowance);
    input.placeholder = "Unknown";
    label.htmlFor = input.id;
    label.textContent = name + " · " + millions(allowance) + " available";
    line.append(label, input);
    target.append(line);
    creditInputs.set(name, input);
  }
}
function reconcile(payroll) {
  let credit = 0, allKnown = true, valid = true;
  for (const field of creditInputs.values()) {
    allKnown &&= Number.isFinite(field.valueAsNumber);
    valid &&= field.validity.valid;
    credit += Number.isFinite(field.valueAsNumber) ? field.valueAsNumber : 0;
  }
  const baseline = railway().opex.baseline_usd_m_year;
  const priced = Number.isFinite(payroll);
  byId("baseline-cost").textContent = millions(baseline);
  byId("credited-cost").textContent = allKnown && valid ? millions(credit) : "Unconfirmed";
  byId("payroll-cost").textContent = priced ? millions(payroll / 1e6) : "Unpriced";
  const ready = allKnown && valid && priced;
  const annual = ready ? baseline - credit + payroll / 1e6 : null;
  byId("revised-cost").textContent = ready ? millions(annual) : "Pending";
  const transfer = byId("transfer");
  const commissioning = byId("mode").value === "supervised";
  transfer.hidden = !ready || commissioning;
  if (!transfer.hidden) transfer.href = "../finance/index.html?" + new URLSearchParams({network:byId("railway").value, opex:annual});
  else transfer.removeAttribute("href");
  byId("cost-status").textContent = !valid ? "Enter an included payroll between zero and its full contract allowance." :
    !allKnown || !priced ? "Confirm the included payroll in every allowance and price every staffed role." :
    commissioning ? "Annualised commissioning comparison only. Agree trial dates and charge the actual period to commissioning before using it in project finance." :
    "Annual scenario in 2026 USD. Procurement needs itemised payroll, non-labour scope and local pay evidence.";
}
function render() {
  const hoursInput = byId("hours"), common = byId("salary"), selected = scenario();
  const hoursValid = hoursInput.validity.valid, commonPay = common.valueAsNumber;
  let hours = 0, staff = 0, pay = 0, payKnown = true, ratesValid = common.validity.valid;
  for (const [role, fields] of roleRows) {
    const duty = selected.duty_hours_per_year[role];
    const fte = hoursValid ? Math.ceil(duty / hoursInput.valueAsNumber) : 0;
    const rate = fields.rate.value === "" ? commonPay : fields.rate.valueAsNumber;
    fields.duty.textContent = number.format(duty);
    fields.reference.textContent = number.format(selected.posts_fte[role]);
    fields.count.textContent = hoursValid ? number.format(fte) : "—";
    hours += duty;
    staff += fte;
    if (!fte) continue;
    ratesValid &&= fields.rate.validity.valid;
    if (Number.isFinite(rate)) pay += rate * fte;
    else payKnown = false;
  }
  const total = hoursValid ? number.format(staff) : "—";
  const footer = byId("roster-total");
  footer.replaceChildren();
  const row = footer.insertRow();
  for (const value of ["Total",number.format(hours),number.format(selected.total_fte),total,""]) row.insertCell().textContent = value;
  byId("error").textContent = !hoursValid ? "Enter 1 to 2,080 whole rosterable hours." :
      !ratesValid ? "Enter positive pay rates in USD." : "";
  byId("establishment").textContent = total;
  const payroll = payKnown && ratesValid && hoursValid && Number.isFinite(pay) ? pay : null;
  byId("pay").textContent = payroll === null ? "Unpriced" : usd(payroll);
  byId("learner-total").textContent = hoursValid ? number.format(staff * 160) : "—";
  const cohorts = Math.ceil(staff / 12);
  byId("cohorts").textContent = hoursValid ? number.format(cohorts) : "—";
  byId("instructors").textContent = hoursValid ? number.format(cohorts * 80) : "—";
  byId("mentored").textContent = hoursValid ? number.format(staff * 80) : "—";
  const explanations = {
    goa4:"No routine onboard post. Station assistance, control-room supervision and field response continue.",
    supervised:"One onboard commissioning supervisor per train-duty hour, shown as a full-year equivalent.",
    assisted:"Passenger assistance covers a quarter of train-duty hours. The operator must assign specific turns and reliefs."
  };
  byId("fleet-description").textContent = explanations[byId("mode").value] + " " + selected.train_duty_basis;
  byId("study").textContent = workforceStudy.study_evaluation_sha256.slice(0,12);
  reconcile(payroll);
}
byId("railway").addEventListener("change", () => {buildRows(); buildCredits(); render();});
byId("mode").addEventListener("change", () => {buildRows(true); render();});
for (const id of ["hours","salary"]) byId(id).addEventListener("input", render);
buildRows();
buildCredits();
render();
