"use strict";
const byId = (id) => document.getElementById(id);
const format = (n) => typeof n === "number" && Number.isFinite(n)
  ? n.toLocaleString("en-GB", { maximumFractionDigits: 2 }) : "Not defined";
const identityKeys = [
  "selection_id",
  "candidate_id",
  "body_candidate_id",
  "support_component_id",
  "propulsion_component_id",
];
const qualificationKeys = [
  "engineering_accepted",
  "physical_accepted",
  "installed_mass_complete",
  "manufacturing_release",
  "operating_release",
];
function validated(value, expected) {
  if (value.development_default !== true)
    throw Error("This record is not the selected development default.");
  for (const key of qualificationKeys)
    if (value[key] !== false)
      throw Error("Unexpected qualification disposition: " + key);
  for (const key of identityKeys) {
    if (!/^[a-f0-9]{64}$/.test(value[key] || ""))
      throw Error("Missing selected identity: " + key);
    if (expected && value[key] !== expected[key])
      throw Error("Mixed candidate identity: " + key);
  }
  return value;
}
async function request(url) {
  const response = await fetch(url, { cache: "no-store" });
  const value = await response.json();
  if (!response.ok) {
    const error = Error(value.reason || "Current record unavailable");
    error.record = value;
    throw error;
  }
  return value;
}
function fact(container, label, value) {
  const dt = document.createElement("dt"),
    dd = document.createElement("dd");
  dt.textContent = label;
  dd.textContent = value ?? "Unknown";
  container.append(dt, dd);
}
function readable(value) {
  if (value === null || value === undefined) return "Unknown";
  return typeof value === "object" ? JSON.stringify(value) : String(value);
}
function billions(value) {
  return (Number(value) / 1e9).toLocaleString("en-GB", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}
async function renderVehicleCost(expected) {
  const cost = validated(
    await request(
      "/docs/design-engine/current/exports/selected-vehicle-cost.json",
    ),
    expected,
  );
  if (
    cost.schema !== "osr-v06-selected-vehicle-class-c-cost/1" ||
    cost.evaluation_id !==
      (expected.publication?.evaluation_id || expected.evaluation_id) ||
    cost.whole_life_cost_iqd !== null ||
    cost.city_cost_iqd !== null
  )
    throw Error("Selected vehicle cost record or scope disposition differs.");
  const train = cost.total_vehicle_factory_delivery_assembly_iqd_per_train;
  const car = cost.unit_iqd_per_car;
  const tooling = cost.separate_unamortized_factory_tooling_capital_iqd;
  for (const scenarios of [train, car, tooling]) {
    const values = [scenarios.low, scenarios.base, scenarios.high];
    if (
      values.some((value) => !Number.isFinite(value) || value < 0) ||
      values[0] > values[1] ||
      values[1] > values[2]
    )
      throw Error("Cost scenarios must be finite and ordered low/base/high.");
  }
  byId("vehicle-cost-train").textContent = billions(train.base);
  byId("vehicle-cost-car").textContent = billions(car.base);
  byId("vehicle-tooling").textContent = billions(tooling.base);
  byId("vehicle-cost-status").textContent =
    `Class C provisional estimate · ${cost.currency} · ${cost.estimate_date} · assumptions ${cost.assumptions_id.slice(0, 12)}.`;
  const facts = byId("vehicle-cost-facts");
  fact(
    facts,
    "Per train, low / base / high",
    `${billions(train.low)} / ${billions(train.base)} / ${billions(train.high)} billion IQD`,
  );
  fact(
    facts,
    "Per car, low / base / high",
    `${billions(car.low)} / ${billions(car.base)} / ${billions(car.high)} billion IQD`,
  );
  fact(
    facts,
    "Accounted / located / residual mass per car",
    `${format(cost.vehicle_account.accounted_tare_kg_per_car / 1000)} / ${format(cost.vehicle_account.located_geometry_kg_per_car / 1000)} / ${format(cost.vehicle_account.residual_account_kg_per_car / 1000)} t`,
  );
  fact(
    facts,
    "Production and civil shifts",
    `${cost.shifts.production_per_day.shifts} × ${cost.shifts.production_per_day.hours_per_shift} h; ${cost.shifts.civil_per_day.shifts} × ${cost.shifts.civil_per_day.hours_per_shift} h`,
  );
  fact(
    facts,
    "Operating cases",
    cost.shifts.operations_cases
      .map((row) => `${row.hours_per_day} h/day (${row.shifts_per_day} shifts)`)
      .join(" · "),
  );
  fact(
    facts,
    "Reference delivery",
    `${format(cost.reference_delivery_distance_km)} km · ${billions(cost.reference_delivery_cost_iqd_per_train.base)} billion IQD/train base`,
  );
  const body = byId("vehicle-cost-lines");
  body.replaceChildren();
  for (const line of cost.lines) {
    const tr = document.createElement("tr");
    const label = document.createElement("td");
    label.textContent = line.line_key.replaceAll("/", " · ");
    tr.append(label);
    for (const scenario of ["low", "base", "high"]) {
      const cell = document.createElement("td");
      cell.textContent = format(line.cost_iqd[scenario]);
      tr.append(cell);
    }
    body.append(tr);
  }
}
function activePropulsionPolicy(record) {
  const value=record.active_propulsion_policy;
  if (!value || value.schema!=="osr-candidate-specific-propulsion-policy/1" ||
      !/^[a-f0-9]{64}$/.test(value.policy_id||"") ||
      value.policy?.selection_mode!=="candidate-specific" ||
      value.policy?.prescribed_powered_length!==false ||
      value.policy?.automatic_hardware_adoption!==false ||
      value.reference_vehicle_is_installed_drive_selection!==false ||
      value.kinematic_distance_is_powered_hardware_length!==false)
    throw Error("Candidate-specific active propulsion policy required.");
  if(value.reference_vehicle_candidate_id!==record.candidate_id || value.reference_passive_interface_id!==record.propulsion_component_id)
    throw Error("Active policy uses a mixed reference vehicle or passive interface.");
  for (const key of ["selected_installed_propulsion_id","selected_architecture",
      "selected_powered_length_m","selected_acceleration_m_s2","selected_braking_m_s2","selected_headway_s"])
    if(value[key]!==null)throw Error("The active baseline cannot prescribe an installed propulsion selection: "+key);
  for(const key of ["physical_accepted","engineering_accepted","manufacturing_release","operating_release","movement_authority"])
    if(value[key]!==false)throw Error("Propulsion policy cannot grant release: "+key);
  return value;
}
function showMaturity(complete,label) {
  byId("maturity-outline").textContent=complete ? "Outline complete · "+label : "Revision or further definition needed";
  byId("maturity-engineering").textContent="Verification pending";
  byId("maturity-prototype").textContent="Not validated";
  byId("maturity-release").textContent="Not approved";
}
async function sourceBoundOutlineSummary(expected) {
  const name="docs/design-engine/demand-outline/summary.json";
  const response=await fetch("/"+name,{cache:"no-store"});
  if(!response.ok)throw Error("Current outline comparison unavailable");
  const raw=await response.arrayBuffer();
  const actual=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",raw)),b=>b.toString(16).padStart(2,"0")).join("");
  const manifest=validated(await request("/docs/design-engine/current/manifest.json"),expected);
  if(manifest.source_sha256?.[name]!==actual)throw Error("Outline comparison lacks its current source binding");
  const value=JSON.parse(new TextDecoder().decode(raw));
  if(value.schema!=="osr-demand-outline-summary/1")throw Error("Current demand-led outline summary required");
  for(const key of [...qualificationKeys,"movement_authority","procurement_ready"])if(value[key]!==false)throw Error("Outline comparison cannot grant qualification or release");
  return value;
}
async function renderSystemCost(expected) {
  const cost=validated(await request("/docs/design-engine/current/exports/selected-system-cost.json"),expected);
  if(cost.schema!=="osr-selected-v06-whole-system-class-c-cost/1" ||
      cost.selection_role!=="retired-reference-control-comparison" ||
      cost.active_installed_propulsion_selected!==false ||
      cost.vehicle_evaluation_id!==(expected.publication?.evaluation_id||expected.evaluation_id))
    throw Error("Reference-control comparison must not become the active budget.");
  const value=await sourceBoundOutlineSummary(expected);
  renderOutlineRows(value,"../../design-engine/demand-outline/");
  byId("system-capex").textContent="Compare outlines";
  byId("system-whole-life").textContent="Candidate-specific";
  byId("system-cost-status").textContent="Current calculated corridor alternatives · no installed propulsion selected. Use the requirement form above to generate a new comparison.";
  const facts=byId("system-cost-facts");facts.replaceChildren();
  fact(facts,"Calculated example",`${value.brief.route_km} km · ${value.brief.stations} stations · ${format(value.brief.peak_demand_pphpd)} peak passengers/hour/direction`);
  fact(facts,"Compared approaches",value.outlines.map(row=>launchNames[row.mechanism]||row.mechanism).join(" · "));
  fact(facts,"Scope","Fourteen whole-life cost scopes per outline; assumptions remain inspectable. Engineering, prototype and release are separate.");
  outlineStatus.textContent=`${value.outlines.length} calculated outlines for the starting brief. Change the requirements above to generate and compare alternatives.`;
}

async function renderPortfolios(expected) {
  const view = await request("/api/portfolios/current");
  const researchFlags = [
    "physical_accepted",
    "engineering_accepted",
    "configuration_adopted",
    "selected_reference_changed",
    "manufacturing_release",
    "operating_release",
  ];
  const checkResearch = (record) => {
    if (researchFlags.some((key) => record[key] !== false))
      throw Error("Portfolio research dispositions differ.");
  };
  checkResearch(view);
  if (
    view.schema !== "osr-design-portfolio-view/1" ||
    view.integrated_selection !== null ||
    view.numerical_jobs_dispatched !== 0 ||
    view.selected_reference_context.selection_id !== expected.selection_id ||
    view.selected_reference_context.candidate_id !== expected.candidate_id ||
    view.portfolios.length !== 4 ||
    new Set(view.portfolios.map((portfolio) => portfolio.key)).size !== 4 ||
    !["body", "civil", "topology", "topology-revisions"].every((key) =>
      view.portfolios.some((portfolio) => portfolio.key === key),
    )
  )
    throw Error("Portfolio source or selected-reference context differs.");
  if (view.current_evaluator_admission !== false || view.numerical_reexecuted !== false ||
      view.reference_comparison?.selection_role !== "retired-reference-control-comparison" ||
      view.reference_comparison.current_evaluator_admission !== false ||
      view.reference_comparison.numerical_reexecuted !== false)
    throw Error("Retired component comparison cannot claim current evaluator admission.");
  for (const portfolio of view.portfolios) {
    const ids = new Set();
    for (const row of portfolio.rows) {
      checkResearch(row);
      const costs = [row.cost_iqd.low, row.cost_iqd.base, row.cost_iqd.high];
      if (
        !/^[a-f0-9]{64}$/.test(row.candidate_id) ||
        ids.has(row.candidate_id) ||
        !Number.isFinite(row.stock_mass_kg) ||
        row.stock_mass_kg < 0 ||
        costs.some((value) => !Number.isFinite(value) || value < 0) ||
        costs[0] > costs[1] ||
        costs[1] > costs[2] ||
        row.complete_installed_mass_kg !== null
      )
        throw Error(
          "Portfolio candidate identities, quantities or cost scenarios differ.",
        );
      ids.add(row.candidate_id);
    }
    if (
      ids.size !== portfolio.candidate_count ||
      (portfolio.quantity_retained_count !== null &&
        portfolio.rows.filter((row) => row.quantity_retained).length !==
          portfolio.quantity_retained_count) ||
      (portfolio.mechanics_retained_count !== null &&
        portfolio.rows.filter((row) => row.mechanics_retained).length !==
          portfolio.mechanics_retained_count)
    )
      throw Error("Portfolio archive coverage differs.");
  }
  const system = byId("portfolio-system"),
    family = byId("portfolio-family"),
    retention = byId("portfolio-retention");
  const familyName = (row) =>
    Object.entries(row.descriptor)
      .map(([key, value]) => `${key}: ${value}`)
      .join(" · ");
  const selected = () =>
    view.portfolios.find((portfolio) => portfolio.key === system.value);
  function inspect(row, portfolio) {
    byId("portfolio-detail").hidden = false;
    byId("portfolio-evidence").textContent =
      row.structural_status + ". Physical acceptance remains open.";
    const facts = byId("portfolio-facts");
    facts.replaceChildren();
    fact(facts, "Physical candidate", row.candidate_id);
    fact(
      facts,
      "Quantity evaluation",
      row.quantity_evaluation_id ??
        "No aggregate evaluation ID; exact record SHA-256 below",
    );
    fact(facts, "Quantity record SHA-256", row.quantity_record_sha256);
    fact(facts, "Mechanics evaluation", row.mechanics_evaluation_id);
    fact(
      facts,
      "Low / base / high scoped cost",
      ["low", "base", "high"]
        .map((key) => format(row.cost_iqd[key]))
        .join(" / ") + " IQD",
    );
    fact(
      facts,
      portfolio.process_hours_label + " · low / base / high",
      row.process_hours === null
        ? row.process_hours_status || "Unknown; not present in the published summary"
        : ["low", "base", "high"]
            .map((key) => format(row.process_hours[key]))
            .join(" / "),
    );
    fact(facts, "Complete installed mass", "Unknown");
    fact(
      facts,
      portfolio.deflection_label || "Crowd/high-mass model deflection bound",
      row.model_deflection_upper_m === null
        ? "Unknown; structural analysis not run"
        : `${format(row.model_deflection_upper_m * 1000)} mm · conditional elastic model only`,
    );
    if (row.quantity_dominated_by.length)
      fact(
        facts,
        "Quantity archive exclusion",
        "Dominated on partial quantity objectives by " +
          row.quantity_dominated_by.join(", ") +
          ". This does not determine engineering suitability.",
      );
    const tasks = byId("portfolio-tasks");
    tasks.replaceChildren();
    for (const task of row.next_tasks) {
      const li = document.createElement("li");
      li.textContent = task;
      tasks.append(li);
    }
    byId("portfolio-assumptions").textContent = JSON.stringify(
      {
        portfolio_id: portfolio.portfolio_id,
        quantity_archive_id: portfolio.quantity_archive_id,
        mechanics_archive_id: portfolio.mechanics_archive_id,
        study_assumptions: portfolio.assumptions,
        candidate_assumptions: row.assumptions,
      },
      null,
      2,
    );
    byId("portfolio-source").href = portfolio.evidence_path;
    byId("portfolio-geometry").href = portfolio.geometry_path;
    for (const button of byId("portfolio-rows").querySelectorAll("button"))
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.candidate === row.candidate_id),
      );
  }
  function filter() {
    const portfolio = selected();
    const rows = portfolio.rows.filter(
      (row) =>
        (family.value === "all" || familyName(row) === family.value) &&
        (retention.value === "all" ||
          (retention.value === "quantity"
            ? row.quantity_retained
            : row.mechanics_retained === true)),
    );
    byId("portfolio-count").textContent =
      `${rows.length} of ${portfolio.candidate_count} alternatives shown` +
      (portfolio.quantity_retained_count === null
        ? " · separate quantity ranking not run"
        : ` · quantity archive ${portfolio.quantity_retained_count}`) +
      (portfolio.mechanics_retained_count === null
        ? " · mechanics not evaluated"
        : ` · mechanics archive ${portfolio.mechanics_retained_count}`) +
      (portfolio.key === "topology-revisions"
        ? ` · ${portfolio.assumptions.terminal_attempt_count} terminal attempts · ${portfolio.assumptions.residual_gate_failed_attempt_count} numerical residual failures · ${portfolio.assumptions.mesh_unresolved_attempt_count} mesh unresolved; physical model and strength unqualified`
        : "");
    byId("portfolio-rows").replaceChildren();
    byId("portfolio-detail").hidden = true;
    for (const row of rows) {
      const tr = document.createElement("tr"),
        cell = document.createElement("td"),
        button = document.createElement("button");
      tr.dataset.candidate = row.candidate_id;
      button.type = "button";
      button.dataset.candidate = row.candidate_id;
      button.textContent = `${row.candidate_id.slice(0, 12)} · ${row.profile}`;
      button.title = row.candidate_id;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => inspect(row, portfolio));
      cell.append(button);
      tr.append(cell);
      for (const value of [
        familyName(row),
        format(row.stock_mass_kg / 1000),
        format(row.cost_iqd.base / 1e6),
        row.quantity_retained === null
          ? "Not ranked separately"
          : row.quantity_retained ? "Retained" : "Outside partial front",
        row.mechanics_retained === null
          ? "Unknown / not run"
          : row.mechanics_retained
            ? "Retained"
            : "Outside partial front",
      ]) {
        const td = document.createElement("td");
        td.textContent = value;
        tr.append(td);
      }
      byId("portfolio-rows").append(tr);
    }
    if (rows.length) inspect(rows[0], portfolio);
  }
  function changeSystem() {
    const portfolio = selected();
    family.replaceChildren(new Option("All families", "all"));
    for (const name of [...new Set(portfolio.rows.map(familyName))].sort())
      family.append(new Option(name, name));
    retention.value = "all";
    retention.querySelector('[value="mechanics"]').disabled =
      portfolio.mechanics_archive_id === null;
    retention.querySelector('[value="quantity"]').disabled =
      portfolio.quantity_archive_id === null;
    byId("portfolio-scope").textContent =
      `${portfolio.unit}. ${portfolio.cost_scope}`;
    filter();
  }
  system.replaceChildren(
    ...view.portfolios.map(
      (portfolio) => new Option(portfolio.label, portfolio.key),
    ),
  );
  system.addEventListener("change", changeSystem);
  family.addEventListener("change", filter);
  retention.addEventListener("change", filter);
  byId("portfolio-controls").hidden = false;
  byId("portfolio-status").textContent =
    "Retired component comparisons · original quantity and mechanics evidence · no current solver execution or integrated replacement selected.";
  changeSystem();
}
function renderGates(gates) {
  const rows = Array.isArray(gates)
    ? gates
    : Object.entries(gates || {}).map(([id, g]) =>
        typeof g === "object" ? { id, ...g } : { id, screen: g },
      );
  for (const gate of rows) {
    const tr = document.createElement("tr"),
      name = document.createElement("td"),
      screen = document.createElement("td"),
      detail = document.createElement("td"),
      badge = document.createElement("span");
    name.textContent =
      gate.title ||
      gate.gate ||
      gate.name ||
      gate.id ||
      gate.requirement ||
      "Engineering gate";
    const state = String(
      gate.engineering_screen ||
        gate.state ||
        gate.screen ||
        gate.status ||
        gate.disposition ||
        "unknown",
    ).toLowerCase();
    badge.textContent = state;
    badge.className =
      "screen " +
      (state === "pass" ? "pass" : state === "fail" ? "fail" : "unknown");
    screen.append(badge);
    detail.textContent = readable(
      gate.reason ||
        gate.basis ||
        gate.limitation ||
        gate.note ||
        gate.scope ||
        gate.evidence ||
        gate,
    );
    tr.append(name, screen, detail);
    byId("gates").append(tr);
  }
  if (!rows.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 3;
    td.textContent = "Unknown — no current readiness gates supplied.";
    tr.append(td);
    byId("gates").append(tr);
  }
}
let current;
let cityRecords = [];
async function showCity(slug) {
  byId("city-status").textContent = "Checking current city record…";
  byId("city-details").textContent = "";
  try {
    const city = validated(
      await request("/api/city/" + encodeURIComponent(slug)),
      current,
    );
    byId("city-status").textContent =
      (city.name || city.city?.name || city.city_name || slug) +
      " · selected-design analytical planning";
    byId("city-details").textContent = JSON.stringify(
      city.totals ||
        city.planning ||
        city.network ||
        city.service ||
        city.summary ||
        city,
      null,
      2,
    );
    const path =
      city.summary_path ||
      city.current_summary_path ||
      cityRecords.find((row) => row.slug === slug)?.summary_path;
    if (path) byId("city-link").href = "/" + path;
  } catch (error) {
    byId("city-status").textContent = "Outline available above. Engineering verification pending: " + error.message;
    const record = error.record;
    byId("city-link").hidden = !record?.geography?.map_context_available;
    if (record?.geography) {
      byId("city-details").textContent = JSON.stringify(
        { geography: record.geography },
        null,
        2,
      );
      byId("city-link").href =
        "/docs/workbench/planning/?city=" +
        encodeURIComponent(record.city.slug);
      byId("city-link").textContent = "Open city planning";
    }
  }
}
async function start() {
  try {
    current = validated(await request("/api/default-design"));
    if (current.publication_state !== "current")
      throw Error("The selected publication is not current.");
    if (current.family !== "wheel_rail_vehicle_reference")
      throw Error(
        "The current family is not the v0.6 vehicle reference.",
      );
    const packet = validated(current.publication, current),
      v = current.vehicle,
      s = current.service;
    const policy=activePropulsionPolicy(current),publishedPolicy=activePropulsionPolicy(packet);
    if(policy.policy_id!==publishedPolicy.policy_id || current.reference_service_values_are_active_requirements!==false)
      throw Error("Active policy and reference controls are mixed.");
    if(v.normal_passengers_per_car!==46 || v.standing_passengers_per_car!==0)
      throw Error("Reference vehicle passenger policy differs.");
    byId("speed").textContent="Variable";
    byId("headway").textContent="Optimised";
    byId("capacity").textContent="Demand-led";
    byId("active-propulsion-status").textContent="No installed propulsion architecture, powered length or operating headway is selected. Compare candidates against passenger needs, physics and complete cost.";
    try {
      await renderVehicleCost(current);
    } catch (error) {
      byId("vehicle-cost-status").textContent = "Held: " + error.message;
      byId("vehicle-cost-lines").replaceChildren();
    }
    try {
      await renderSystemCost(current);
    } catch (error) {
      byId("system-cost-status").textContent = "Held: " + error.message;
    }
    const vf = byId("vehicle-facts");
    fact(vf, "Formation", v.cars + " × " + v.body_length_m + " m");
    fact(
      vf,
      "Passengers",
      v.normal_passengers_per_car +
        " / car; " +
        v.cars * v.normal_passengers_per_car +
        " / train",
    );
    fact(vf, "Standing passengers", "0");
    fact(vf, "Support", "Passive wheel bogies; conventional rails");
    fact(vf, "Onboard traction motors / traction battery", "None");
    fact(
      vf,
      "Services battery",
      "Retained for HVAC, doors and essential systems",
    );
    fact(
      vf,
      "Passenger doors",
      v.passenger_doors_total_per_car + " / car, one side",
    );
    const mass = packet.mass || current.mass;
    fact(
      vf,
      "Accounted tare / car",
      readable(
        mass.accounted_tare_kg_per_car
          ? format(mass.accounted_tare_kg_per_car / 1000) + " t"
          : mass.accounted_empty_mass_kg
            ? format(mass.accounted_empty_mass_kg / 1000) + " t"
            : mass,
      ),
    );
    const nf = byId("network-facts");
    fact(nf, "Retained stop spacing", "Existing city stops retained");
    fact(nf,"Active propulsion","Not selected; candidate-specific architectures remain open");
    fact(nf,"Powered hardware length","Not prescribed; derive and count each candidate's actual sections");
    fact(nf,"Grid, branches and thermal duty","Counted for each candidate; independent engineering verification pending");
    fact(nf,"Reference controls only",`${format(typeof s.launch_speed_cap_m_s==="number"?s.launch_speed_cap_m_s*3.6:null)} km/h · ${format(s.headway_s)} s · ${format(s.normal_capacity_pphpd_arithmetic)} places/hour/direction; not active requirements`);
    fact(
      vf,
      "Accounted cap-loaded / car",
      mass.accounted_cap_loaded_kg_per_car
        ? format(mass.accounted_cap_loaded_kg_per_car / 1000) + " t"
        : "Unknown",
    );
    const cities = packet.cities || {};
    const baghdad = cities.Baghdad || cities.baghdad || {};
    fact(nf,"Baghdad","Priced outline available in the city workspace; engineering verification pending");
    renderGates(packet.gates || packet.readiness?.gates);
    try {
      await renderPortfolios(current);
    } catch (error) {
      byId("portfolio-status").textContent = "Held: " + error.message;
      byId("portfolio-controls").hidden = true;
      byId("portfolio-detail").hidden = true;
      byId("portfolio-rows").replaceChildren();
    }
    try {
      const campaign = await request("/api/campaigns/current");
      if (
        campaign.physical_accepted !== false ||
        campaign.configuration_adopted !== false
      )
        throw Error("Research dispositions differ");
      byId("campaign-status").textContent =
        `${campaign.generations} generations · ${campaign.candidates.length} candidates · integrated baseline: ${campaign.integrated_baseline.status}. Research selection; physical qualification remains open.`;
      byId("campaign-rows").replaceChildren();
      for (const candidate of campaign.candidates) {
        const tr = document.createElement("tr");
        for (const value of [
          `g${candidate.generation} / ${candidate.candidate_id.slice(0, 12)}`,
          `${format(candidate.mass_kg_per_car / 1000)} t/car`,
          `${candidate.body_engineering_screen} / ${candidate.body_numerical_validity}`,
          candidate.motor_numerical_status,
        ]) {
          const td = document.createElement("td");
          td.textContent = value;
          tr.append(td);
        }
        byId("campaign-rows").append(tr);
      }
    } catch (error) {
      byId("campaign-status").textContent =
        "No current source-bound campaign publication is available.";
    }
    try {
      const space = await request("/api/design-space/current");
      if (space.physical_accepted !== false || space.default_changed !== false)
        throw Error("Research dispositions differ");
      byId("design-space-status").textContent =
        `${space.structural_proposals} structural and ${space.propulsion_proposals} propulsion proposals, with sourced cores, joints, glazing and HVAC leads. Full-body models and whole-system selection remain held.`;
    } catch (error) {
      byId("design-space-status").textContent =
        "No current source-bound design-space publication is available.";
    }
    try {
      const architecture = await request("/api/architectures/current");
      if (
        architecture.physical_accepted !== false ||
        architecture.development_default_changed !== false
      )
        throw Error("Research dispositions differ");
      byId("architecture-status").textContent =
        `${architecture.evaluation_cases} analytical cases · ${architecture.physical_definitions} physical definitions · ${architecture.generations} generations. No qualified architecture selected.`;
      byId("architecture-rows").replaceChildren();
      for (const family of architecture.families) {
        const row = document.createElement("tr");
        for (const value of [
          `${family.family_id} — ${family.label}`,
          family.cases,
          family.target_reached_at_comparison_mass,
          family.physical_journeys,
        ]) {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.append(cell);
        }
        byId("architecture-rows").append(row);
      }
    } catch (error) {
      byId("architecture-status").textContent =
        "No current source-bound architecture publication is available.";
    }
    try {
      const adaptive = await request("/api/adaptive/current");
      if (
        adaptive.physical_accepted !== false ||
        adaptive.selected_reference_changed !== false
      )
        throw Error("Research dispositions differ");
      byId("adaptive-status").textContent =
        `${adaptive.variable_count} extensible variables · ${Object.keys(adaptive.domains).length} domains · ${adaptive.native_case_count} native cases. Search: ${adaptive.search_status}.`;
      byId("adaptive-rows").replaceChildren();
      for (const candidate of adaptive.rows) {
        const row = document.createElement("tr");
        for (const value of [
          candidate.section,
          `${format(candidate.accounted_tare_kg_per_car / 1000)} t`,
          candidate.normal_vertical_displacement_m === null
            ? "Unconfirmed"
            : `${format(candidate.normal_vertical_displacement_m * 1000)} mm`,
          candidate.integrated_suitability,
        ]) {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.append(cell);
        }
        byId("adaptive-rows").append(row);
      }
    } catch (error) {
      byId("adaptive-status").textContent =
        "No current source-bound adaptive publication is available.";
    }
    try {
      const generative = await request("/api/generative/current");
      if (
        generative.physical_accepted !== false ||
        generative.selected_reference_changed !== false ||
        generative.integrated_selection !== null
      )
        throw Error("Generative research dispositions differ");
      byId("generative-status").textContent =
        `${generative.candidate_count} generated designs · ${generative.initial_recipe_count} initial recipes · ${generative.rewrite_count} executed rewrites · ${generative.CAD_case_count} CAD cases · ${generative.native_design_case_count} native structural cases. No integrated design selected.`;
      byId("generative-rows").replaceChildren();
      for (const candidate of generative.rows) {
        const row = document.createElement("tr");
        for (const value of [
          `${candidate.label} / ${candidate.candidate_id.slice(0, 10)}`,
          candidate.gross_structure_stock_kg === null
            ? "Unknown"
            : `${format(candidate.gross_structure_stock_kg / 1000)} t`,
          candidate.mechanism_count === null
            ? "Unconfirmed"
            : candidate.mechanism_count,
          candidate.full_body_evaluator,
          candidate.integrated_suitability,
        ]) {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.append(cell);
        }
        byId("generative-rows").append(row);
      }
    } catch (error) {
      byId("generative-status").textContent =
        "No current source-bound generative publication is available.";
    }
    try {
      const railway = await request("/api/railway/current");
      if (
        railway.physical_accepted !== false ||
        railway.selected_reference_changed !== false ||
        railway.integrated_selection !== null
      )
        throw Error("Research dispositions differ");
      byId("railway-status").textContent =
        `${railway.body_count} body definitions · ${railway.evaluated_bundle_count} railway bundles · ${railway.downstream_stage_count} linked evaluations. No qualified journey selected.`;
      byId("railway-rows").replaceChildren();
      for (const candidate of railway.body_rows) {
        const row = document.createElement("tr");
        for (const value of [
          candidate.label,
          candidate.accounted_empty_mass_kg === null
            ? "Unknown"
            : `${format(candidate.accounted_empty_mass_kg / 1000)} t (partial account)`,
          candidate.structural_status,
          candidate.architecture_cases,
        ]) {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.append(cell);
        }
        byId("railway-rows").append(row);
      }
    } catch (error) {
      byId("railway-status").textContent =
        "No current source-bound coordinated publication is available.";
    }
    for (const key of identityKeys)
      fact(byId("identities"), key==="propulsion_component_id"?"reference passive interface ID":key.replaceAll("_", " "), current[key]);
    byId("native-scope").textContent =
      "Native evidence scope: " +
      readable(
        packet.native?.methodscope ||
          packet.native?.method_scope ||
          packet.native?.scope ||
          packet.native ||
          "See the current engineering report.",
      );
    byId("loading").hidden = true;
    byId("design").hidden = false;
    try {
      const catalogue = validated(await request("/api/cities"), current);
      const rows = Array.isArray(catalogue)
        ? catalogue
        : catalogue.cities || catalogue.entries || [];
      cityRecords = rows;
      byId("city").replaceChildren();
      for (const row of rows) {
        const option = document.createElement("option");
        option.value = row.slug;
        option.textContent =
          (row.name || row.slug) +
          (row.execution === "held"
            ? " · outline workspace available; engineering pending"
            : "");
        byId("city").append(option);
      }
      byId("city").value = "baghdad";
      byId("city").addEventListener("change", () =>
        showCity(byId("city").value),
      );
      await showCity("baghdad");
    } catch (error) {
      byId("city-status").textContent = "Outline available above. Engineering verification pending: " + error.message;
      byId("city-link").hidden = true;
    }
  } catch (error) {
    byId("loading").hidden = true;
    byId("design").hidden = true;
    byId("error").hidden = false;
    byId("error").textContent =
      "Current design held: " +
      error.message +
      " Rebuild and verify the selected publication; no historical fallback was loaded.";
  }
}
// Outline research is independent of the selected hardware publication above.
// The local server calculates immutable studies; the static site explains how
// to start it instead of substituting historical results.
const outlineForm = document.getElementById("outline-form");
const outlineStatus = document.getElementById("outline-status");
const launchNames = {"cable-capstan":"Cable / capstan", "common-drive-rollers":"Common-drive rollers", "compact-launch-LIM":"Compact LIM"};
const moneyMillions = value => `$${(value / 1e6).toFixed(1)}m`;
function outlineInspect(row,open=true) {
  const area = document.getElementById("outline-evidence");
  area.replaceChildren();
  const title = document.createElement("h3");
  title.textContent = `${launchNames[row.mechanism]||row.mechanism} · ${row.maturity === "accepted" ? "Outline accepted" : row.maturity}`;
  area.append(title);
  showMaturity(row.maturity==="accepted",launchNames[row.mechanism]||row.mechanism);
  for (const assumption of row.assumptions) {
    const paragraph = document.createElement("p");
    paragraph.textContent = `${assumption.id}: ${assumption.purpose} Bounds: ${JSON.stringify(assumption.bounds)}. Source: ${assumption.source}`;
    area.append(paragraph);
  }
  for (const task of row.tasks) {
    const paragraph = document.createElement("p");
    paragraph.textContent = task.explanation || task.reason || task.action || JSON.stringify(task);
    area.append(paragraph);
  }
  document.getElementById("outline-detail").open = open;
}
function renderOutlineRows(value,artifactBase) {
  if(!Array.isArray(value.outlines)||!value.outlines.length)throw Error("No calculated outline alternatives available");
  for(const row of value.outlines) {
    for(const field of ["headway_s","speed_kmh","acceleration_m_s2","journey_minutes","trainsets"])
      if(typeof row[field]!=="number"||!Number.isFinite(row[field])||row[field]<=0)throw Error("Finite outline service value required: "+field);
    for(const field of ["installed_capital_usd","whole_life_npv_usd","price_per_route_km_usd"]) {
      const prices=[row[field]?.low,row[field]?.base,row[field]?.high];
      if(prices.some(x=>typeof x!=="number"||!Number.isFinite(x)||x<=0)||prices[0]>prices[1]||prices[1]>prices[2])throw Error("Bounded ordered outline costs required");
    }
  }
    const body = document.getElementById("outline-rows");
    body.replaceChildren();
    for (const row of value.outlines) {
      const tr = document.createElement("tr");
      const values = [launchNames[row.mechanism]||row.mechanism,`${row.headway_s}s · ${row.speed_kmh.toFixed(0)} km/h · ${row.acceleration_m_s2} m/s²`,
        `${row.journey_minutes.toFixed(1)} min`,row.trainsets,
        moneyMillions(row.price_per_route_km_usd.base),moneyMillions(row.whole_life_npv_usd.base),
        row.maturity === "accepted" ? "Outline accepted" : row.maturity];
      for (const text of values) { const td=document.createElement("td"); td.textContent=text; tr.append(td); }
      const td=document.createElement("td"), inspect=document.createElement("button");
      inspect.textContent="Inspect outline"; inspect.addEventListener("click",()=>outlineInspect(row)); td.append(inspect); tr.append(td); body.append(tr);
    }
    const selected=value.outlines.find(row=>row.outline_id===value.recommended_outline_id);
    document.getElementById("outline-recommendation").textContent = selected
      ? `Lowest central whole-life estimate in this bounded search: ${launchNames[selected.mechanism]||selected.mechanism}. Installed range ${moneyMillions(selected.installed_capital_usd.low)}–${moneyMillions(selected.installed_capital_usd.high)}; these are sensitivity cases, not confidence limits.`
      : "No outline meets this brief within the current search budget. Inspect the complete study for failures, pending work and alternative requirements.";
    const links=document.getElementById("outline-artifacts"); links.replaceChildren();
    for (const [file,label] of [["result.json","Complete study and evidence"],["manifest.json","Source and artifact identities"],["performance.json","Execution measurements"]]) {
      const link=document.createElement("a"); link.href=artifactBase+file; link.textContent=label; links.append(link);
    }
    document.getElementById("outline-results").hidden=false;

  showMaturity(value.outlines.some(row=>row.maturity==="accepted"),`${value.brief.route_km} km example`);
  if(selected)outlineInspect(selected,false);
}
outlineForm.addEventListener("submit", async event => {
  event.preventDefault();
  const button = document.getElementById("outline-generate");
  button.disabled = true;
  outlineStatus.textContent = "Screening service choices and recalculating fleet, production and fourteen cost scopes…";
  document.getElementById("outline-results").hidden = true;
  try {
    const fields = new FormData(outlineForm);
    const brief = {
      route_km: Number(fields.get("route_km")), stations: Number(fields.get("stations")),
      peak_demand_pphpd: Number(fields.get("peak_demand_pphpd")),
      maximum_one_way_minutes: Number(fields.get("maximum_one_way_minutes")),
      maximum_headway_s: Number(fields.get("maximum_headway_s")),
      planning_occupancy: Number(fields.get("occupancy_percent")) / 100,
      operating_hours_per_day: Number(fields.get("operating_hours_per_day")),
      availability_target: .99, planning_availability_assumption: .99,
      demand_source: "User-entered planning brief; survey evidence not attached"
    };
    const response = await fetch("/api/outline-study", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({brief, pricing_scenario:fields.get("pricing_scenario")})});
    const value = await response.json();
    if (!response.ok) throw Error(value.error || "Outline calculation unavailable");
    renderOutlineRows(value,value.artifact_url);
    outlineStatus.textContent=`${value.costed_cases} complete cost cases · ${value.outlines.length} retained outlines · ${value.pricing_scenario} · requirements ${value.requirements_id.slice(0,12)}.`;
  } catch(error) {
    outlineStatus.textContent=`Unable to complete the outline: ${error.message}. For calculations, open the local Workbench with ./osr workbench.`;
  } finally {button.disabled=false;}
});

// Published completion is a separate outline scenario, never the selected
// hardware's physical-performance endpoint. Static hosting reads the same
// immutable publication as the loopback API.
let completionCatalogue;
const completionBase = "../../design-engine/outline-completion/";
async function completionRecord(file, api) {
  const local = ["127.0.0.1", "localhost", "[::1]"].includes(location.hostname);
  const response = await fetch(local ? api : completionBase + file, {cache:"no-store"});
  const value = !local && file.endsWith(".gz")
    ? await new Response(response.body.pipeThrough(new DecompressionStream("gzip"))).json()
    : await response.json();
  if (!response.ok) throw Error(value.error || "Published outline unavailable");
  for (const key of qualificationKeys)
    if (value[key] !== false) throw Error("Unexpected outline qualification: " + key);
  return value;
}
async function showCityOutline(slug) {
  const status = byId("city-outline-status");
  status.textContent = "Loading the city's calculated quantities, service and cost scopes…";
  try {
    const row = await completionRecord(`cities/${slug}.json.gz`, `/api/outline-completion/city/${slug}`);
    const facts = byId("city-outline-facts"); facts.replaceChildren();
    fact(facts, "Design stage", row.outline_complete ? "Outline complete · engineering verification pending" : row.outline_completion);
    showMaturity(row.outline_complete,row.city.name);
    fact(facts, "Mapped network", `${format(row.route_km)} route-km · ${row.lines} lines · ${row.stations} line-stop records`);
    fact(facts, "Joined operational stop complexes", row.operational_station_complexes);
    fact(facts, "Alignment retained for this outline", row.selected_alignment_kind);
    fact(facts, "Fleet including reserves", `${row.trainsets} trainsets`);
    fact(facts, "Installed capital · low / base / high", ["low","base","high"].map(c=>moneyMillions(row.installed_capital_usd[c])).join(" / "));
    fact(facts, "Central cost per route-km", moneyMillions(row.price_per_route_km_usd.base));
    fact(facts, "30-year whole-life NPV · base", moneyMillions(row.whole_life_npv_usd.base));
    fact(facts, "Demand basis", row.policy.demand_source);
    const body = byId("city-outline-costs"); body.replaceChildren();
    for (const [scope, costs] of Object.entries(row.scope_totals_usd)) {
      const tr = document.createElement("tr");
      for (const text of [scope,...["low","base","high"].map(c=>(costs[c]/1e6).toFixed(2))]) {
        const td = document.createElement("td"); td.textContent = text; tr.append(td);
      }
      body.append(tr);
    }
    const lines = byId("city-outline-lines"); lines.replaceChildren();
    for (const line of row.line_outlines) {
      const p = document.createElement("p");
      p.textContent = `${line.line_id}: ${line.shape} · ${line.headway_s}s headway · ${line.trainsets} trainsets · ${line.propulsion}. Retained station-reference issues: ${line.known_reference_failures.length}.`;
      lines.append(p);
    }
    byId("city-outline-detail").textContent = JSON.stringify({
      pricing_and_site_assumptions:row.assumptions,
      delivery:row.delivery_draft,
      later_verification:row.qualification_requirements
    },null,2);
    const alignments = byId("city-outline-alignments"); alignments.replaceChildren();
    for (const alternative of row.alignment_comparison) {
      const p = document.createElement("p");
      p.textContent = `${alternative.kind}: ${format(alternative.route_km)} km · ${moneyMillions(alternative.installed_capital_usd.base)} installed · ${moneyMillions(alternative.whole_life_npv_usd.base)} whole-life NPV · ${alternative.selection_eligibility.status}.`;
      alignments.append(p);
    }
    const geometry = await completionRecord(`maps/${slug}.geojson.gz`, `/api/outline-completion/map/${slug}`);
    drawOutlineMap(geometry);
    byId("city-outline-download").href = completionBase + `cities/${slug}.json.gz`;
    status.textContent = `${row.city.name}, ${row.city.country} · Class C estimates, not supplier offers. No hardware or operating approval. Outline ${row.evaluation_id.slice(0,12)}.`;
  } catch (error) {status.textContent = "City outline unavailable: " + error.message;}
}
byId("city-outline-load").addEventListener("click", async () => {
  const button = byId("city-outline-load"); button.disabled = true;
  try {
    completionCatalogue = await completionRecord("summary.json", "/api/outline-completion");
    const select = byId("city-outline-select"); select.replaceChildren();
    for (const row of completionCatalogue.cities) {
      const option = document.createElement("option"); option.value = row.city.slug;
      option.textContent = `${row.city.name} · ${row.city.country}`; select.append(option);
    }
    const requested = new URLSearchParams(location.search).get("outlineCity") || "baghdad";
    select.value = completionCatalogue.cities.some(r=>r.city.slug===requested) ? requested : completionCatalogue.cities[0].city.slug;
    byId("city-outline-results").hidden = false;
    renderDesignPrices();
    await showCityOutline(select.value);
  } catch (error) {byId("city-outline-status").textContent = "Published outlines unavailable: " + error.message;}
  finally {button.disabled = false;}
});
byId("city-outline-select").addEventListener("change", event=>showCityOutline(event.target.value));
byId("city-study-options").addEventListener("submit",async event=>{
  event.preventDefault();
  const button=byId("city-study-start"),status=byId("city-study-status");
  button.disabled=true;byId("city-study-result").hidden=true;
  try {
    const fields=new FormData(event.target),slug=byId("city-outline-select").value;
    const original=completionCatalogue.cities.find(row=>row.city.slug===slug);
    const payload={city_slug:slug,expected_outline_evaluation_id:original.evaluation_id,
      service:{peak_demand_pphpd:Number(fields.get("peak_demand_pphpd")),
        maximum_headway_s:Number(fields.get("maximum_headway_s")),operating_hours_per_day:Number(fields.get("operating_hours_per_day"))},
      alignment:{maximum_added_walk_m:Number(fields.get("maximum_added_walk_m"))},
      project:{pricing_scenario:fields.get("pricing_scenario")},selection:fields.get("selection")};
    status.textContent="Starting a bounded mapped-city calculation…";
    const response=await fetch("/api/city-studies",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    let job=await response.json();
    if (!response.ok) throw Error(job.error||"Another calculation is running; retry after it finishes");
    const deadline=Date.now()+150000;
    while(job.state==="running" && Date.now()<deadline) {
      status.textContent="Calculating mapped service, all cost scopes, factory/civil resources and draft delivery records…";
      await new Promise(resolve=>setTimeout(resolve,1000));
      job=await request("/api/city-studies/"+job.job_id);
    }
    if(job.state!=="completed")throw Error(job.error||"Calculation did not finish within its budget; artifacts were retained");
    const s=job.summary;
    byId("city-study-outcome").textContent=`${s.city.name}: ${s.outline_acceptance==="accepted"?"Outline accepted":"Priced proposal requires revision"}. `+
      `${s.trainsets} trainsets; ${moneyMillions(s.installed_capital_usd.base)} installed; ${moneyMillions(s.whole_life_npv_usd.base)} whole-life NPV. `+
      `${Math.ceil(s.delivery.cases.base.finish_workday)} provisional working days with the priced resources; `+
      (s.delivery.cases.base.target_met?"within the planning target. ":"the planning target needs revised resources, methods or dates. ")+
      "Production and civil works use two shifts. Actual calendar dates and physical releases remain subject to review.";
    const links=byId("city-study-links");links.replaceChildren();
    for(const [file,label] of [["planning.json","Editable planning base"],["delivery-plan.json","Production and construction schedule"],
      ["business-drafts.json","Disabled business-system drafts"],["manifest.json","Sources and artifact identities"]]) {
      const a=document.createElement("a");a.href=job.artifact_url+file;a.textContent=label;links.append(a);
    }
    const edit=document.createElement("a");edit.href=`../planning/?city=${encodeURIComponent(slug)}&pricedRun=${job.job_id}`;
    edit.textContent="Edit this outline and recalculate";links.prepend(edit);
    byId("city-study-result").hidden=false;
    showMaturity(s.outline_acceptance==="accepted",s.city.name);
    status.textContent=`${job.cache_hit?"Reused the identical verified calculation":"Calculation complete"} · ${s.service_lines.length} lines · ${s.research_configuration_id.slice(0,12)}. Physical approval remains separate.`;
  } catch(error) {status.textContent=`Unable to calculate this city: ${error.message}. Run the local Workbench with ./osr workbench.`;}
  finally {button.disabled=false;}
});
function renderDesignPrices() {
  if (!completionCatalogue) return;
  const kind=byId("design-price-kind").value;
  const prices=completionCatalogue.designs,fx=prices.pricing_policy.iqd_per_usd;
  const keys={"railway-bundle":["installed_capital","whole_life_npv"],"vehicle-body":["repeat_body_factory_gate","one_time_tooling_setup"],"civil-span":["scoped_installed","scoped_whole_life_npv"]}[kind];
  const body=byId("design-price-rows");body.replaceChildren();
  for (const row of prices.rows.filter(r=>r.kind===kind)) for (const key of keys) {
    const tr=document.createElement("tr");
    for (const text of [row.physical_candidate_id.slice(0,12),key.replaceAll("_"," "),(row.prices_iqd[key].base/fx).toLocaleString("en-GB",{maximumFractionDigits:0})]) {
      const td=document.createElement("td");td.textContent=text;tr.append(td);
    }
    const td=document.createElement("td"),button=document.createElement("button");button.textContent="Inspect";
    button.addEventListener("click",()=>{byId("design-price-detail").textContent=JSON.stringify(row,null,2);byId("design-price-inspection").open=true;});
    td.append(button);tr.append(td);body.append(tr);
  }
}
byId("design-price-kind").addEventListener("change",renderDesignPrices);
function drawOutlineMap(geometry) {
  const svg = byId("city-outline-map"); svg.replaceChildren();
  const lines = geometry.features.filter(f=>f.geometry?.type==="LineString");
  const points = lines.flatMap(f=>f.geometry.coordinates);
  if (!points.length) return;
  const latitude = points.reduce((s,p)=>s+p[1],0)/points.length;
  const longitudeScale = Math.cos(latitude*Math.PI/180);
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  for (const p of points) {minX=Math.min(minX,p[0]*longitudeScale);maxX=Math.max(maxX,p[0]*longitudeScale);minY=Math.min(minY,p[1]);maxY=Math.max(maxY,p[1]);}
  const scale=Math.min(860/Math.max(1e-9,maxX-minX),480/Math.max(1e-9,maxY-minY));
  const projected=p=>[20+(p[0]*longitudeScale-minX)*scale,500-(p[1]-minY)*scale];
  for (const feature of lines) {
    const path=document.createElementNS("http://www.w3.org/2000/svg","path");
    const kind=feature.properties.variant;
    path.setAttribute("d",feature.geometry.coordinates.map((p,i)=>`${i?"L":"M"}${projected(p).join(" ")}`).join(" "));
    path.setAttribute("fill","none");path.setAttribute("stroke",kind==="original"?"#83918d":kind.includes("ring")?"#bc6a18":"#08735a");
    path.setAttribute("stroke-width",kind==="original"?"4":"2");
    const title=document.createElementNS("http://www.w3.org/2000/svg","title");title.textContent=`${feature.properties.line_id||feature.properties.name||"Route"} · ${kind}`;
    path.append(title);svg.append(path);
  }
  for (const feature of geometry.features.filter(f=>f.geometry?.type==="Point")) {
    const circle=document.createElementNS("http://www.w3.org/2000/svg","circle");
    const point=projected(feature.geometry.coordinates),kind=feature.properties.variant;
    circle.setAttribute("cx",point[0]);circle.setAttribute("cy",point[1]);circle.setAttribute("r","2.5");
    circle.setAttribute("fill",kind==="original"?"#65736e":kind.includes("ring")?"#bc6a18":"#08735a");
    const title=document.createElementNS("http://www.w3.org/2000/svg","title");title.textContent=`${feature.properties.stop_id} · ${kind}`;
    circle.append(title);svg.append(circle);
  }
}
if (new URLSearchParams(location.search).has("outlineCity")) byId("city-outline-load").click();

start();
