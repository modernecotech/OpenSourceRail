"use strict";
const byId = (id) => document.getElementById(id);
const format = (n) =>
  Number(n).toLocaleString("en-GB", { maximumFractionDigits: 2 });
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
    byId("city-status").textContent = "Held: " + error.message;
    const record = error.record;
    byId("city-link").hidden = !record?.geography?.map_available;
    if (record?.geography) {
      byId("city-details").textContent = JSON.stringify(
        { geography: record.geography, historical: record.historical },
        null,
        2,
      );
      byId("city-link").href = "/" + record.geography.map_path;
      byId("city-link").textContent =
        "Preserved city map · historical engineering labels";
    }
  }
}
async function start() {
  try {
    current = validated(await request("/api/default-design"));
    if (current.publication_state !== "current")
      throw Error("The selected publication is not current.");
    if (current.family !== "wheel_rail_station_lim")
      throw Error(
        "The selected family is not v0.6 station-launched wheel rail.",
      );
    const packet = validated(current.publication, current),
      v = current.vehicle,
      s = current.service;
    const speed = s.launch_speed_cap_m_s * 3.6,
      capacity = (v.cars * v.normal_passengers_per_car * 3600) / s.headway_s;
    if (
      speed !== 72 ||
      s.headway_s !== 120 ||
      capacity !== 8280 ||
      v.normal_passengers_per_car !== 46 ||
      v.standing_passengers_per_car !== 0
    )
      throw Error("Selected service specification differs.");
    byId("speed").textContent = format(speed);
    byId("headway").textContent = format(s.headway_s);
    byId("capacity").textContent = format(capacity);
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
    fact(
      nf,
      "2 km station example",
      readable(
        packet.service?.shared_winding_m ?? s.prototype_shared_winding_m,
      ) + " m shared winding",
    );
    fact(
      nf,
      "Sections / direction",
      (packet.service?.shared_winding_m ?? s.prototype_shared_winding_m) /
        (s.station_section_m ?? s.station_section_length_m),
    );
    fact(
      nf,
      "Independent branches",
      "At least " +
        (s.minimum_phase_branches_per_direction ??
          s.minimum_independent_train_phase_branches_per_direction ??
          2) +
        " / direction",
    );
    fact(
      vf,
      "Accounted cap-loaded / car",
      mass.accounted_cap_loaded_kg_per_car
        ? format(mass.accounted_cap_loaded_kg_per_car / 1000) + " t"
        : "Unknown",
    );
    const cities = packet.cities || {};
    const baghdad = cities.Baghdad || cities.baghdad || {};
    fact(
      nf,
      "Baghdad fleet",
      readable(
        baghdad.total_trainsets ||
          baghdad.fleet ||
          baghdad.trainsets ||
          "Held pending v0.6 physical evaluation",
      ),
    );
    renderGates(packet.gates || packet.readiness?.gates);
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
      fact(byId("identities"), key.replaceAll("_", " "), current[key]);
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
            ? " · geography available, evaluation held"
            : "");
        byId("city").append(option);
      }
      byId("city").value = "baghdad";
      byId("city").addEventListener("change", () =>
        showCity(byId("city").value),
      );
      await showCity("baghdad");
    } catch (error) {
      byId("city-status").textContent = "Held: " + error.message;
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
start();
