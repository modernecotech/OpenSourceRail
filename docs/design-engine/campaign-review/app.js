import {
  filterCandidates,
  comparisonNotice,
  screenLabel,
  valueText,
  expandReview,
} from "./model.js";

const byId = (id) => document.getElementById(id);
const element = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};
const badge = (text, kind = "") => element("span", text, `badge ${kind}`);
const link = (text, href) => {
  const node = element("a", text);
  const url = new URL(href, location.href);
  if (
    url.origin !== location.origin ||
    !url.pathname.startsWith(new URL("../", location.href).pathname)
  )
    throw new Error("Invalid local evidence link");
  node.href = url.href;
  return node;
};
const list = (items) => {
  const node = element("ul");
  for (const item of items) node.append(element("li", item));
  return node;
};

async function start() {
  const response = await fetch("data.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`Review data: HTTP ${response.status}`);
  const data = expandReview(await response.json());
  if (
    data.schema !== "osr-campaign-review/1" ||
    data.manufacturing_release !== false ||
    data.physical_release !== false
  )
    throw new Error("Unreleased review data required");
  const cases = new Map(data.cases.map((row) => [row.id, row]));
  const packets = new Map(data.packets.map((row) => [row.id, row]));
  const candidates = new Map(data.candidates.map((row) => [row.id, row]));
  const selected = new Set();
  let page = 0;
  const pageSize = 50;
  const option = (select, value, text) => {
    const node = element("option", text);
    node.value = value;
    select.append(node);
  };
  option(
    byId("configuration-select"),
    "",
    "All configurations — keep applicability visible",
  );
  for (const row of data.cases)
    option(
      byId("configuration-select"),
      row.id,
      `${row.architecture} · ${row.label}`,
    );
  for (const row of data.packets)
    if (data.candidates.some((c) => c.packet === row.id))
      option(byId("packet"), row.id, `${row.label} · ${row.applicability}`);
  for (const value of [
    ...new Set(data.cases.map((row) => row.architecture)),
  ].sort())
    option(byId("architecture"), value, value);
  for (const value of [
    ...new Set(data.candidates.map((row) => row.family)),
  ].sort())
    option(byId("family"), value, value);

  function configurationDetail() {
    const container = byId("configuration-detail");
    container.replaceChildren();
    const row = cases.get(byId("configuration-select").value);
    if (!row) {
      container.append(
        element(
          "p",
          "Choose one configuration to review its geometry, load identity and open inputs. Comparisons across configurations remain conditional.",
        ),
      );
      return;
    }
    const packet = packets.get(row.packet);
    container.append(
      element("h3", row.label),
      badge(row.architecture),
      badge(
        packet.applicability,
        packet.applicability === "historical" ? "historical" : "unknown",
      ),
      badge("Inputs unaccepted", "unknown"),
    );
    if (row.train_mass_kg !== undefined)
      container.append(
        element(
          "p",
          `${valueText(row.train_mass_kg, 1000, " t known model mass")} · ${valueText(row.train_length_m, 1, " m train")} · ${row.axles} axles · ${valueText(row.platform_length_m, 1, " m full-module platform")}`,
        ),
      );
    container.append(
      element("p", `Geometry: ${row.geometry}`),
      element("p", `Connections: ${row.connections}`),
    );
    container.append(
      element(
        "p",
        "Definition remains incomplete: accepted materials, connections, loading, manufacturing and inspection evidence are required.",
      ),
    );
    if (row.required_gates) container.append(list(row.required_gates));
    container.append(link("Configuration evidence reference", row.source));
  }

  function comparison() {
    const rows = [...selected].map((id) => candidates.get(id)).filter(Boolean);
    byId("comparison-note").textContent = comparisonNotice(...rows);
    const container = byId("comparison-cards");
    container.replaceChildren();
    for (const row of rows) {
      const card = element("article", undefined, "card");
      const configuration = cases.get(row.case);
      const packet = packets.get(row.packet);
      card.append(
        element("h3", row.candidate_id),
        badge(screenLabel(row), row.screen),
        badge(
          packet.applicability,
          packet.applicability === "historical" ? "historical" : "unknown",
        ),
      );
      card.append(
        element(
          "p",
          `${configuration.architecture} · ${configuration.label} · ${row.family}`,
        ),
      );
      card.append(
        element("h4", "Geometry / declared variables"),
        element("pre", JSON.stringify(row.variables, null, 2)),
      );
      if (row.basis)
        card.append(
          element(
            "p",
            `Declared method / basis: ${typeof row.basis === "string" ? row.basis : JSON.stringify(row.basis)}`,
          ),
        );
      card.append(
        element(
          "p",
          "These variables do not define all joints, reinforcement, tolerances or manufacturing operations.",
        ),
      );
      card.append(
        element("h4", "Demand / local metrics [reported SI units]"),
        element("pre", JSON.stringify(row.metrics, null, 2)),
      );
      card.append(
        element("h4", "Known failed checks"),
        list(
          row.failed_checks.length
            ? row.failed_checks
            : [
                "No reported known check failed in this submodel. Complete design acceptance remains open.",
              ],
        ),
      );
      card.append(
        element("h4", "Unknown / required qualification"),
        list(
          row.unknown_gates.length
            ? row.unknown_gates
            : [
                "See configuration and work-package requirements; this submodel does not establish complete qualification.",
              ],
        ),
      );
      card.append(
        element(
          "p",
          `Materials: ${row.material_acceptance}. Connections: ${row.connection_acceptance}. Manufacturing release: false.`,
        ),
      );
      if (row.source_configuration_compatible === false)
        card.append(
          element(
            "p",
            "Source configuration conflict: this is a change proposal requiring adoption and interface rechecks.",
            "notice",
          ),
        );
      card.append(
        element("h4", "Next required action"),
        element("p", row.next_action),
        link("Immutable evidence reference", row.source),
      );
      container.append(card);
    }
  }

  function render() {
    const filtered = filterCandidates(data, {
      case: byId("configuration-select").value,
      query: byId("search").value,
      packet: byId("packet").value,
      architecture: byId("architecture").value,
      family: byId("family").value,
      screen: byId("screen").value,
      shortlisted: byId("shortlisted").checked,
    });
    const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pages - 1);
    byId("result-count").textContent =
      `${filtered.length.toLocaleString("en-GB")} of ${data.candidates.length.toLocaleString("en-GB")} local variation records. ${selected.size} selected for comparison. All manufacturing gates remain open.`;
    const body = byId("candidate-rows");
    body.replaceChildren();
    for (const row of filtered.slice(page * pageSize, (page + 1) * pageSize)) {
      const tr = element("tr");
      const choice = element("td");
      const checkbox = element("input");
      checkbox.type = "checkbox";
      checkbox.checked = selected.has(row.id);
      checkbox.disabled = selected.size === 2 && !checkbox.checked;
      checkbox.setAttribute(
        "aria-label",
        `Compare ${row.candidate_id} in ${row.case}`,
      );
      checkbox.addEventListener("change", () => {
        checkbox.checked ? selected.add(row.id) : selected.delete(row.id);
        render();
      });
      choice.append(checkbox);
      const identity = element("td");
      identity.append(
        element("strong", row.candidate_id),
        element("div", row.family),
        element("div", row.record_kind || "bounded-candidate"),
        badge(
          packets.get(row.packet).applicability,
          packets.get(row.packet).applicability === "historical"
            ? "historical"
            : "unknown",
        ),
      );
      if (row.selected_local) identity.append(badge("Local selection only"));
      if (row.proposed_configuration)
        identity.append(badge("Configuration proposal", "unknown"));
      const configuration = element(
        "td",
        `${cases.get(row.case).architecture} · ${cases.get(row.case).label}`,
      );
      const screen = element("td");
      screen.append(
        badge(screenLabel(row), row.screen),
        element(
          "div",
          row.source_configuration_compatible === false
            ? "Source envelope conflict"
            : row.source_configuration_compatible === true
              ? "Source fit predicate only"
              : "Source fit not established",
        ),
      );
      tr.append(
        choice,
        identity,
        configuration,
        screen,
        element(
          "td",
          valueText(row.metrics.minimum_service_compression_pa, 1e6, " MPa"),
        ),
        element(
          "td",
          `${valueText(row.metrics.initial_bed_force_n, 1e6, " MN")} / ${valueText(row.metrics.maximum_hook_equivalent_kg, 1000, " t")}`,
        ),
        element("td", row.next_action),
      );
      body.append(tr);
    }
    if (!filtered.length) {
      const tr = element("tr");
      const td = element(
        "td",
        "No records match these filters. Reset or choose another configuration.",
      );
      td.colSpan = 7;
      tr.append(td);
      body.append(tr);
    }
    byId("page-number").textContent = `Page ${page + 1} of ${pages}`;
    byId("previous").disabled = page === 0;
    byId("next").disabled = page >= pages - 1;
    comparison();
  }

  function packages() {
    const query = byId("package-search").value.toLowerCase().trim();
    const container = byId("package-list");
    container.replaceChildren();
    for (const row of data.packages.filter((p) =>
      JSON.stringify([p.id, p.title, p.owner, p.source_products])
        .toLowerCase()
        .includes(query),
    )) {
      const details = element("details");
      details.append(
        element("summary", `${row.id} · ${row.title} · Open`),
        element(
          "p",
          `${row.owner} · ${row.domain} · ${row.missing_artifacts} missing/unissued production artifacts`,
        ),
      );
      details.append(
        element(
          "p",
          `Dependencies: ${row.dependencies.join(", ") || "None declared"}`,
        ),
        element("pre", JSON.stringify(row.unresolved_gates, null, 2)),
        element("p", row.next_action),
        element("p", "Design complete: false. Manufacturing release: false."),
      );
      container.append(details);
    }
  }
  byId("filters").addEventListener("submit", (event) => event.preventDefault());
  byId("filters").addEventListener("input", () => {
    page = 0;
    render();
  });
  byId("filters").addEventListener("reset", () =>
    setTimeout(() => {
      page = 0;
      render();
    }, 0),
  );
  byId("configuration-select").addEventListener("change", () => {
    page = 0;
    configurationDetail();
    render();
  });
  byId("previous").addEventListener("click", () => {
    page--;
    render();
  });
  byId("next").addEventListener("click", () => {
    page++;
    render();
  });
  byId("clear-comparison").addEventListener("click", () => {
    selected.clear();
    render();
  });
  byId("package-search").addEventListener("input", packages);
  const audit = data.manufacturing_audit;
  byId("audit-summary").textContent =
    `${data.packages.length} packages remain open: ${audit.missing_or_unissued_production_artifacts} missing/unissued production artifacts, ${audit.inspection_characteristics} planned inspections, ${audit.actual_inspection_result_records} actual result records, ${audit.issued_drawing_references} issued drawing references.`;
  byId("applicability-rule").textContent =
    `${data.applicability_rule} ${data.counting_rule}`;
  for (const packet of data.packets) {
    const card = element("article", undefined, "history-entry");
    card.append(
      element("h3", packet.label),
      badge(
        packet.applicability,
        packet.applicability === "historical" ? "historical" : "unknown",
      ),
      element(
        "p",
        "Retained integrity verified. Review generation does not recompute physics; source applicability is separate.",
      ),
      link("Snapshot / archive reference", packet.source),
    );
    byId("history-list").append(card);
  }
  configurationDetail();
  render();
  packages();
  byId("load-status").textContent =
    `${data.cases.length} configuration contexts · ${data.candidates.length.toLocaleString("en-GB")} local records · manufacturing release: false. ${data.counting_rule}`;
}

start().catch((error) => {
  byId("load-status").textContent = `Review could not load: ${error.message}`;
  byId("load-status").className = "notice";
});
