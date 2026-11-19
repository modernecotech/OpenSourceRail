"use strict";
const study = workforceStudy;
const byId = id => document.getElementById(id);
const format = new Intl.NumberFormat("en-US");
const roleOrder = ["train operators", "station duty and passenger assistance", "station security and cleaning",
    "OCC control, traction, incidents and information", "depot rolling-stock technicians",
    "civil, track and power response", "planning, payroll, stores and trainers"];
function row(parent, values) {
  const tr = parent.insertRow();
  for (const value of values) tr.insertCell().textContent = value;
}
function render() {
  const railway = study.studies[byId("railway").value];
  const hoursInput = byId("hours");
  const payInput = byId("salary");
  const validHours = hoursInput.validity.valid;
  const validSalary = payInput.validity.valid;
  const roster = railway.roster;
  let hours = 0, staff = 0;
  byId("error").textContent = !validHours ? "Enter 1 to 2,080 whole rosterable hours." :
      (!validSalary ? "Enter a positive annual USD rate or leave it blank." : "");
  const body = byId("roles"), totals = byId("roster-total");
  body.replaceChildren();
  totals.replaceChildren();
  for (const role of roleOrder) {
    const duty = roster.duty_hours_per_year[role];
    const proposed = validHours ? Math.ceil(duty / hoursInput.valueAsNumber) : 0;
    hours += duty;
    staff += proposed;
    row(body, [role[0].toUpperCase() + role.slice(1), format.format(duty),
      format.format(roster.posts_fte[role]), validHours ? format.format(proposed) : "—"]);
  }
  const validTotal = validHours ? format.format(staff) : "—";
  row(totals, ["Total",format.format(hours),format.format(roster.total_fte),validTotal]);
  byId("establishment").textContent = validTotal;
  byId("pay").textContent = Number.isFinite(payInput.valueAsNumber) && validSalary && validHours
    ? "$" + format.format(Math.round(staff * payInput.valueAsNumber)) : "Unpriced";
  byId("learner-total").textContent = validHours ? format.format(staff * 160) : "—";
  const cohorts = Math.ceil(staff / 12);
  byId("cohorts").textContent = validHours ? format.format(cohorts) : "—";
  byId("instructors").textContent = validHours ? format.format(cohorts * 80) : "—";
  byId("mentored").textContent = validHours ? format.format(staff * 80) : "—";
  byId("fleet-description").textContent = (railway.vehicle.cars / 6) + " six-car trains in the fleet · " +
    format.format(roster.train_operator_hours_per_day) + " train operator duty-hours per day";
  byId("study").textContent = study.study_evaluation_sha256.slice(0,12);
}
for (const id of ["railway","hours","salary"]) byId(id).addEventListener("input", render);
render();
