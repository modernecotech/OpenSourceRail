"""Evidence-gated cost/weight sensitivity ranking for unresolved requirements.

The controller ranks only declared impact ranges. Missing cost or mass bounds
remain unranked; the declared system priority is retained as the fallback queue.
Cost and mass are separate axes, with Pareto fronts rather than an invented
exchange rate between IQD/USD and kilograms.
"""
from decimal import Decimal

from .model import decimal, decimal_text, is_id, text


def _impact_range(value, key, *, currency=False):
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"lower", "upper"} | ({"currency"} if currency else set()):
        raise ValueError(key + " must declare exactly its lower and upper bounds")
    lower = decimal(value.get("lower"), key + " lower bound")
    upper = decimal(value.get("upper"), key + " upper bound")
    if upper < lower:
        raise ValueError(key + " upper bound precedes lower bound")
    result = {"lower": decimal_text(lower), "upper": decimal_text(upper)}
    if currency:
        code = value.get("currency")
        if not isinstance(code, str) or len(code) != 3 or not code.isalpha() or code.upper() != code:
            raise ValueError(key + " requires an ISO currency code")
        result["currency"] = code
    return result


def _labels(value, key):
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > 128:
        raise ValueError(key + " must be a bounded list")
    return [text(item, key + " item") for item in value]


def _decision(row):
    raw = row.get("decision_sensitivity")
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("Decision-sensitivity input must be an object")
    unknown = set(raw) - {"cost_impact_range", "mass_impact_range_kg", "uncertainty_fraction",
        "cost_impact_basis", "mass_impact_basis_kg", "uncertainty_basis",
        "dependent_decisions", "safety_or_design_blocker", "alternative_designs",
        "simulations_to_rerun", "evidence_requests", "selection_margin"}
    if unknown:
        raise ValueError("Unknown decision-sensitivity input fields: " + ", ".join(sorted(unknown)))
    cost = _impact_range(raw.get("cost_impact_range"), "cost impact range", currency=True)
    mass = _impact_range(raw.get("mass_impact_range_kg"), "mass impact range")
    uncertainty = None if raw.get("uncertainty_fraction") is None else decimal(
        raw["uncertainty_fraction"], "uncertainty fraction")
    if uncertainty is not None and not Decimal(0) <= uncertainty <= Decimal(1):
        raise ValueError("Uncertainty fraction must be in [0,1]")
    dependencies_declared = "dependent_decisions" in raw
    dependencies = _labels(raw.get("dependent_decisions"), "dependent decisions")
    if len(dependencies) != len(set(dependencies)):
        raise ValueError("Dependent decisions must be unique")
    blocker = raw.get("safety_or_design_blocker")
    if blocker is not None and type(blocker) is not bool:
        raise ValueError("Safety/design-blocker flag must be explicit Boolean")
    alternatives = raw.get("alternative_designs", [])
    if not isinstance(alternatives, list) or len(alternatives) > 128:
        raise ValueError("Alternative design list must be bounded")
    normalized_alternatives = []
    for alternative in alternatives:
        if not isinstance(alternative, dict) or set(alternative) - {"name", "physical_candidate_id", "change"}:
            raise ValueError("Alternative design must be a named, bounded proposal")
        alternative_candidate = alternative.get("physical_candidate_id")
        if alternative_candidate is not None and not is_id(alternative_candidate):
            raise ValueError("Alternative physical candidate identity must be exact")
        normalized_alternatives.append(dict(name=text(alternative.get("name"), "alternative name"),
            physical_candidate_id=alternative_candidate,
            change=text(alternative.get("change"), "alternative design change")))
    margin = raw.get("selection_margin")
    if margin is not None:
        if not isinstance(margin, dict) or set(margin) != {"amount", "currency"}:
            raise ValueError("Selection margin requires amount and currency")
        amount = decimal(margin["amount"], "selection margin")
        if amount < 0:
            raise ValueError("Selection margin must be non-negative")
        currency = margin["currency"]
        if not isinstance(currency, str) or len(currency) != 3 or not currency.isalpha() or currency.upper() != currency:
            raise ValueError("Selection margin requires an ISO currency code")
        margin = dict(amount=decimal_text(amount), currency=currency)

    missing = []
    if cost is None:
        missing.append("cost-impact-range-and-currency")
    cost_basis = raw.get("cost_impact_basis")
    if cost is not None and not isinstance(cost_basis, str):
        missing.append("cost-impact-range-source-or-model-basis")
    elif cost_basis is not None:
        cost_basis = text(cost_basis, "cost impact basis")
    if mass is None:
        missing.append("mass-impact-range-kg")
    mass_basis = raw.get("mass_impact_basis_kg")
    if mass is not None and not isinstance(mass_basis, str):
        missing.append("mass-impact-range-source-or-model-basis")
    elif mass_basis is not None:
        mass_basis = text(mass_basis, "mass impact basis")
    if uncertainty is None:
        missing.append("uncertainty-fraction-and-basis")
    uncertainty_basis = raw.get("uncertainty_basis")
    if uncertainty is not None and not isinstance(uncertainty_basis, str):
        missing.append("uncertainty-fraction-basis")
    elif uncertainty_basis is not None:
        uncertainty_basis = text(uncertainty_basis, "uncertainty basis")
    if not dependencies_declared:
        missing.append("downstream-decision-dependencies")
    if blocker is None:
        missing.append("safety-or-design-blocker-screen")
    if not alternatives:
        missing.append("alternative-geometry-material-or-process")
    reruns = _labels(raw.get("simulations_to_rerun"), "simulations to rerun")
    evidence = _labels(raw.get("evidence_requests"), "evidence requests")
    if not reruns:
        missing.append("affected-simulations")
    if not evidence:
        missing.append("catalogue-datasheet-or-supplier-evidence-request")

    factor = Decimal(1 + len(dependencies))
    cost_score = None
    if cost is not None and cost_basis is not None and uncertainty is not None and uncertainty_basis is not None and dependencies_declared:
        cost_score = (decimal(cost["upper"]) - decimal(cost["lower"])) * uncertainty * factor
    mass_score = None
    if mass is not None and mass_basis is not None and uncertainty is not None and uncertainty_basis is not None and dependencies_declared:
        mass_score = (decimal(mass["upper"]) - decimal(mass["lower"])) * uncertainty * factor
    could_change = None
    if margin is not None and cost is not None and cost_basis is not None and margin["currency"] == cost["currency"]:
        could_change = decimal(cost["upper"]) >= decimal(margin["amount"])
    return dict(cost_range=cost, cost_impact_basis=cost_basis,
        mass_range=mass, mass_impact_basis_kg=mass_basis,
        uncertainty=decimal_text(uncertainty) if uncertainty is not None else None,
        uncertainty_basis=uncertainty_basis,
        dependent_decisions=dependencies, safety_or_design_blocker=blocker,
        alternative_designs=normalized_alternatives, simulations_to_rerun=reruns,
        evidence_requests=evidence, selection_margin=margin,
        potential_cost_impact=decimal_text(decimal(cost["upper"])) if cost is not None else None,
        cost_sensitivity_score=decimal_text(cost_score) if cost_score is not None else None,
        cost_sensitivity_currency=cost["currency"] if cost is not None else None,
        mass_sensitivity_score_kg=decimal_text(mass_score) if mass_score is not None else None,
        could_change_preferred=could_change,
        rank_status="rankable" if cost_score is not None or mass_score is not None or blocker is True else "impact-inputs-required",
        missing_sensitivity_inputs=missing)


def rank_backlog(requirements):
    """Return safety blockers, explicit cost/weight ranks and fallback queue.

    The Pareto calculation only compares candidates with both numeric axes. A
    safety/design blocker is surfaced ahead of financial ranking. Cost scores
    may only be compared within one currency.
    """
    if not isinstance(requirements, list):
        raise ValueError("Unresolved requirement list required")
    rows = []
    currencies = set()
    for requirement in requirements:
        result = _decision(requirement)
        if result["cost_sensitivity_currency"]:
            currencies.add(result["cost_sensitivity_currency"])
        has_numeric_score = result["cost_sensitivity_score"] is not None or result["mass_sensitivity_score_kg"] is not None
        rank_method = ("explicit cost/mass sensitivity" if has_numeric_score else
                       "safety/design blocker review; no numeric impact evidence" if result["safety_or_design_blocker"] is True else
                       "declared system priority then stable identity; no numeric impact evidence")
        rows.append(dict(requirement_id=requirement["record_id"],
            requirement_key=requirement["requirement_key"],
            category=requirement.get("category", "other"), priority=requirement.get("priority", 15),
            expected_cost_impact=None, uncertainty="unresolved" if requirement.get("quantity") is None else "price-or-specification-evidence-needed",
            effect_on_other_decisions="; ".join(result["dependent_decisions"]) or "not declared",
            rank_method=rank_method,
            sensitivity=result))
    if len(currencies) > 1:
        raise ValueError("Cost sensitivity ranking requires one explicitly normalized currency")

    # The queue uses safety/design blockers first, then fully scored non-dominated
    # fronts. Cost-only and mass-only ranks remain separate; incomplete items
    # retain the existing system/category priority and never receive zero impact.
    paired = [r for r in rows if r["sensitivity"]["cost_sensitivity_score"] is not None and
              r["sensitivity"]["mass_sensitivity_score_kg"] is not None]
    for row in rows:
        row["sensitivity"]["pareto_front"] = None
    masses = sorted({decimal(r["sensitivity"]["mass_sensitivity_score_kg"]) for r in paired}, reverse=True)
    mass_indexes = {value:index + 1 for index, value in enumerate(masses)}
    tree = [0] * (len(masses) + 1)
    def query(index):
        result = 0
        while index:
            result = max(result, tree[index])
            index -= index & -index
        return result
    def update(index, value):
        while index < len(tree):
            tree[index] = max(tree[index], value)
            index += index & -index
    paired.sort(key=lambda r:(-decimal(r["sensitivity"]["cost_sensitivity_score"]),
                              -decimal(r["sensitivity"]["mass_sensitivity_score_kg"]),
                              r["requirement_id"]))
    cursor = 0
    while cursor < len(paired):
        first = paired[cursor]["sensitivity"]
        cost = decimal(first["cost_sensitivity_score"])
        mass = decimal(first["mass_sensitivity_score_kg"])
        end = cursor + 1
        while end < len(paired):
            item = paired[end]["sensitivity"]
            if (decimal(item["cost_sensitivity_score"]) != cost or
                    decimal(item["mass_sensitivity_score_kg"]) != mass):
                break
            end += 1
        # Reverse coordinate: the prefix covers mass scores greater than or
        # equal to this score. Equal score pairs are batched, so they do not
        # dominate one another.
        mass_index = mass_indexes[mass]
        pareto_front = query(mass_index) + 1
        for row in paired[cursor:end]:
            row["sensitivity"]["pareto_front"] = pareto_front
        update(mass_index, pareto_front)
        cursor = end

    # Exact currency-specific and mass-specific ranks are useful when one axis
    # is known and the other is still open.
    cost_sorted = sorted((r for r in rows if r["sensitivity"]["cost_sensitivity_score"] is not None),
        key=lambda r: (-decimal(r["sensitivity"]["cost_sensitivity_score"]), r["requirement_id"]))
    mass_sorted = sorted((r for r in rows if r["sensitivity"]["mass_sensitivity_score_kg"] is not None),
        key=lambda r: (-decimal(r["sensitivity"]["mass_sensitivity_score_kg"]), r["requirement_id"]))
    for rank, row in enumerate(cost_sorted, 1): row["sensitivity"]["cost_rank"] = rank
    for rank, row in enumerate(mass_sorted, 1): row["sensitivity"]["mass_rank"] = rank
    rows.sort(key=lambda r:(0 if r["sensitivity"]["safety_or_design_blocker"] is True else
                            1 if r["sensitivity"]["safety_or_design_blocker"] is None else 2,
        r["sensitivity"]["pareto_front"] is None,
        r["sensitivity"]["pareto_front"] or 10**9,
        r["priority"], r["requirement_id"]))
    return rows
