export function expandReview(data) {
  if (data.schema === "osr-campaign-review/1") return data;
  if (data.schema !== "osr-campaign-review-compact/1")
    throw new Error("Unsupported review data schema");
  const result = { ...data, schema: "osr-campaign-review/1" };
  const reference = (table, index) => {
    if (
      !Number.isInteger(index) ||
      index < 0 ||
      index >= data.tables[table].length
    )
      throw new Error("Invalid compact review reference");
    return data.tables[table][index];
  };
  result.candidates = data.records.map((values) => {
    if (values.length !== data.columns.length)
      throw new Error("Incomplete compact review row");
    const row = Object.fromEntries(
      data.columns.map((key, index) => [key, values[index]]),
    );
    const keys = reference("metric_keys", row.metric_keys_ref);
    if (keys.length !== row.metric_values.length)
      throw new Error("Incomplete compact metric values");
    return {
      ...row,
      id: `${row.packet}:${row.case}:${row.family}:${row.candidate_id}`,
      variables: reference("variables", row.variables_ref),
      unknown_gates: reference("gates", row.gates_ref),
      failed_checks: reference("failures", row.failures_ref),
      next_action: reference("actions", row.action_ref),
      source: reference("sources", row.source_ref),
      metrics: Object.fromEntries(
        keys.map((key, index) => [key, row.metric_values[index]]),
      ),
      material_acceptance: "unaccepted",
      connection_acceptance: "unqualified",
      manufacturing_release: false,
    };
  });
  return result;
}

export function filterCandidates(data, filters = {}) {
  const cases = new Map(data.cases.map((row) => [row.id, row]));
  const query = (filters.query || "").trim().toLowerCase();
  return data.candidates.filter((row) => {
    const configuration = cases.get(row.case);
    return (
      (!filters.case || row.case === filters.case) &&
      (!filters.packet || row.packet === filters.packet) &&
      (!filters.architecture ||
        configuration?.architecture === filters.architecture) &&
      (!filters.family || row.family === filters.family) &&
      (!filters.screen || row.screen === filters.screen) &&
      (!filters.shortlisted ||
        row.selected_local ||
        row.proposed_configuration) &&
      (!query ||
        JSON.stringify([
          row.candidate_id,
          row.variables,
          row.packages,
          row.failed_checks,
          row.unknown_gates,
          configuration?.label,
        ])
          .toLowerCase()
          .includes(query))
    );
  });
}

export function comparisonNotice(left, right) {
  if (!left) return "Choose records in the table.";
  if (!right) return "One record selected. Choose a second to compare.";
  if (
    left.source_configuration_compatible === false ||
    right.source_configuration_compatible === false ||
    left.proposed_configuration ||
    right.proposed_configuration
  )
    return "At least one record changes the source configuration. Reconcile its geometry and interfaces before comparing suitability; local demands do not establish adoption.";
  if (
    left.case !== right.case ||
    left.family !== right.family ||
    left.packet !== right.packet
  )
    return "Different configurations or functions: compare demands within their own applicability. These values do not establish a design ranking.";
  return "Same declared load case and submodel. Compare failed and unknown requirements alongside numerical demands; no manufacturing release is established.";
}

export function screenLabel(row) {
  if (row.screen === "failed") return "Failed known check";
  if (row.screen === "local-pass") return "Local screen passed only";
  return "Screen unknown";
}

export function valueText(value, scale = 1, suffix = "") {
  return typeof value === "number" && Number.isFinite(value)
    ? `${(value / scale).toLocaleString("en-GB", { maximumFractionDigits: 3 })}${suffix}`
    : "Not evaluated / unknown";
}
