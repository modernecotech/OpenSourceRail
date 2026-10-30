"""Evidence-gated cost/weight sensitivity ranking for unresolved requirements.

The controller ranks only declared impact ranges. Missing cost or mass bounds
remain unranked; the declared system priority is retained as the fallback queue.
Cost and mass are separate axes, with Pareto fronts rather than an invented
exchange rate between IQD/USD and kilograms.
"""
from decimal import Decimal

from .model import decimal, decimal_text, identity, is_id, text


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


_SCOPE_ACTIONS = {
    ("civil/concrete", "concrete-hypothesis"): {
        "alternatives_to_evaluate": ["supplier-quoted precast member at an existing Iraqi plant",
                                     "locally cast member using a shared mould at an existing plant",
                                     "dedicated precast line with a defined utilisation and payback case"],
        "likely_reruns": ["guideway section and load-transfer analysis if recipe or member mass changes",
                          "pier and foundation reactions if span geometry or mass changes",
                          "transport and lifting envelope if production location or finished member changes"],
        "evidence_requests": ["approved concrete mix and batch certificates",
                              "reinforcement and prestressing takeoff with yield and tendons",
                              "precast factory quotation covering moulds, labour, QA, handling and delivery",
                              "foundation and erection rates for the defined span and support candidate"],
    },
    ("vehicle/body", "aluminium_reference"): {
        "alternatives_to_evaluate": ["aluminium frame with revised deep side-sills and bonded/load-transfer joints",
                                     "GFRP sandwich panels on a locally repairable aluminium primary frame",
                                     "GFRP monocoque or sandwich body with a separate qualified bogie load path"],
        "likely_reruns": ["body structural and joint analysis for each alloy, section and process change",
                          "installed mass, centre-of-gravity and axle-load reconciliation",
                          "vehicle dynamics and propulsion energy if installed mass changes"],
        "evidence_requests": ["candidate-specific profile, sheet and plate quantities by alloy and temper",
                              "supplier product certificates, usable lengths, price breaks and delivery terms",
                              "forming, joining, finishing, scrap-yield and QA shop route with timed labour"],
    },
    ("vehicle/passive-secondary", "6082-T6-proposed"): {
        "alternatives_to_evaluate": ["continuous aluminium secondary plate with qualified thickness and attachment spacing",
                                     "segmented aluminium plates with verified electrical, thermal and mechanical joints",
                                     "alternative aluminium alloy/product form sized from measured force and temperature limits"],
        "likely_reruns": ["secondary geometry and attachment stress analysis",
                          "LIM force, air-gap, current and thermal evaluation for each conductor plate change",
                          "vehicle installed mass and axle-load reconciliation"],
        "evidence_requests": ["6082-T6 stock certificate and product-form availability",
                              "machining, joining and inspection route with material yield",
                              "candidate-specific supplier quotation and thermal/electrical properties"],
    },
    ("wayside/primary", "copper-conductor"): {
        "alternatives_to_evaluate": ["five 20 m active banks (100 m total) as a separate station-drive candidate",
                                     "approximately 900 m shared winding per station and direction as the retained reference arrangement",
                                     "staged bank length and converter sizing matched to a verified force-speed envelope"],
        "likely_reruns": ["station LIM force map over voltage, current, speed and air-gap envelope",
                          "winding loss, cooling and repeated-headway thermal duty",
                          "converter sizing, feeder protection and station peak-demand analysis"],
        "evidence_requests": ["winding-grade copper specification and winding geometry takeoff",
                              "local or imported winding-wire quotation with insulation system and order yield",
                              "winding, impregnation, test, cooling and replacement process estimates"],
    },
}

_UNRANKED_EVIDENCE = {
    ("civil/rails", "60E1-mass-equivalent"): [
        "compatible rail-section supplier quotation and product certificate",
        "rail fastening, weld, installation and replacement quantities with local rates",
        "confirm mass-equivalent geometry against the selected rail profile and track design",
    ],
    ("vehicle/body", "gfrp_skin_research"): [
        "candidate-specific laminate schedule, core, adhesive and fire/smoke qualified materials",
        "locally available compatible fabric, resin and core prices with batch certificates",
        "mould, cure, trimming, joining, QA and repair labour route with measured hours",
    ],
    ("vehicle/passive-bogie-pair", "steel-reference"): [
        "complete passive bogie RFQ with wheels, axles, bearings, suspension, brakes and interfaces",
        "locally fabricated frame alternative with qualified material, process, NDT and assembly quote",
        "reconciled installed mass and brake / wheelset maintenance scope",
    ],
    ("wayside/primary", "linear-steel-hypothesis"): [
        "electrical-steel grade and laminated-stack supplier quotation with core-loss data",
        "cutting, punching, stacking, insulation and assembly process with yield and timed labour",
        "station LIM force and thermal model bound to the specified core material and geometry",
    ],
}

_UNRANKED_ALTERNATIVES = {
    ("civil/rails", "60E1-mass-equivalent"): [
        "compare supported rail profiles only after wheel/rail load, fatigue, wear and fastening checks",
        "compare directly fastened and resilient-pad systems on the same concrete support candidate",
    ],
    ("vehicle/body", "gfrp_skin_research"): [
        "solid laminate, structural sandwich and hybrid panel/frame families on equal passenger and load requirements",
        "local infusion versus imported finished panels with tooling, cure-cycle, QA and repair costs",
    ],
    ("vehicle/passive-bogie-pair", "steel-reference"): [
        "imported complete passive bogie versus locally fabricated frame with imported qualified wheelsets and brakes",
        "two-stage local manufacture after supplier and independent brake interfaces are defined",
    ],
    ("wayside/primary", "linear-steel-hypothesis"): [
        "electrical-steel laminated stack versus a separately modelled segmented core construction",
        "joint and cooling layouts matched to the same force/current/temperature envelope",
    ],
}


def candidate_sourcing_sensitivity(procurement_packet):
    """Summarize exact candidate-bound partial cost scenarios for design review.

    Scenario spread ranks only the width between currently declared alternative
    input cases. It is not an uncertainty interval, expected cost, value of
    information, preference margin, or complete installed-cost comparison.
    Stock mass is carried as context only and is never treated as an impact bound.
    """
    if not isinstance(procurement_packet, dict):
        raise ValueError("Candidate-bound procurement packet required")
    packet = procurement_packet
    for key in ("packet_id", "candidate_id", "evaluation_id", "source_input_id"):
        if not is_id(packet.get(key)):
            raise ValueError("Procurement packet requires exact " + key)
    if packet["packet_id"] != identity({key: value for key, value in packet.items() if key != "packet_id"}):
        raise ValueError("Procurement packet identity does not match its contents")
    lines = packet.get("material_purchasing_lines")
    packages = packet.get("packages")
    if not isinstance(lines, list) or not isinstance(packages, list):
        raise ValueError("Procurement packet material lines and packages are required")

    def _line_key(line):
        return line.get("system"), line.get("material")

    line_by_key = {}
    for line in lines:
        if not isinstance(line, dict) or not is_id(line.get("material_line_id")):
            raise ValueError("Every procurement material line must have an exact identity")
        key = _line_key(line)
        if key in line_by_key:
            raise ValueError("Candidate sensitivity requires unique system/material lines")
        line_by_key[key] = line

    def _base_scope(line):
        mass = decimal(line.get("modeled_gross_stock_mass_kg"), "modeled gross stock mass")
        if mass < 0:
            raise ValueError("Modeled gross stock mass cannot be negative")
        leads = line.get("domestic_fabrication_lead_sources", [])
        if not isinstance(leads, list):
            raise ValueError("Domestic source leads must be a list")
        return {
            "material_line_id": line["material_line_id"],
            "system": line["system"], "material": line["material"],
            "stock_scope": line.get("stock_scope"),
            "engineering_group_count": line.get("engineering_group_count"),
            "engineering_occurrence_count": line.get("engineering_occurrence_count"),
            "modeled_gross_stock_mass_kg_reference_only": decimal_text(mass),
            "source_lead_keys": sorted({lead["source_key"] for lead in leads if lead.get("source_key")}),
            "source_lead_count": len(leads),
            "complete_installed_cost": line.get("complete_installed_cost"),
            "commercial_order_quantity": line.get("commercial_order_quantity"),
        }

    def _scenario_totals(rows, *, expected_count, where, require_currency=True):
        if not isinstance(rows, list) or len(rows) != expected_count:
            raise ValueError(where + " has an unexpected scenario count")
        results = []
        seen = set()
        for row in rows:
            if (not isinstance(row, dict)
                    or (require_currency and row.get("currency") != "IQD")):
                raise ValueError(where + " scenario requires IQD currency")
            total = decimal(row.get("estimated_total_iqd"), where + " total")
            if total < 0:
                raise ValueError(where + " scenario total cannot be negative")
            results.append((row, total))
        return results

    ranked = []
    # Concrete package scenarios are aggregated only after checking each exact
    # package belongs to this one candidate and each region/hour cell covers all
    # 81 package identities exactly once.
    concrete_line = line_by_key.get(("civil/concrete", "concrete-hypothesis"))
    if concrete_line is not None:
        concrete_packages = [row for row in packages
                             if row.get("package_family") == "civil-concrete-stock-package"]
        expected_ids = concrete_line.get("related_package_ids")
        if (not isinstance(expected_ids, list) or len(expected_ids) != 81
                or sorted(expected_ids) != sorted(row.get("package_id") for row in concrete_packages)
                or len(concrete_packages) != 81):
            raise ValueError("Concrete sensitivity packages do not match the exact material line")
        cells = {}
        for package in concrete_packages:
            if (package.get("candidate_id") != packet["candidate_id"]
                    or package.get("evaluation_id") != packet["evaluation_id"]
                    or package.get("source_input_id") != packet["source_input_id"]
                    or package.get("package_id") != identity({key: value for key, value in package.items()
                                                               if key != "package_id"})):
                raise ValueError("Concrete package candidate identity or contents differ")
            for row in package.get("domestic_cost_estimate_scenarios", []):
                if (row.get("currency") != "IQD" or row.get("uplift_fraction") != "0.2"
                        or row.get("supplier_quote") is not False
                        or row.get("complete_process_cost") is not None
                        or row.get("complete_installed_cost") is not None):
                    raise ValueError("Concrete package scenario exceeds its partial-estimate boundary")
                cell = (row.get("region"), str(row.get("labour_hours_per_nominal_m3")))
                if not cell[0] or cell[1] not in {"2", "4", "8"}:
                    raise ValueError("Concrete package scenario has an unsupported region/hour alternative")
                cells.setdefault(cell, []).append((package["package_id"], row))
        if set(cells) != {(region, hours) for region in ("Baghdad", "Al-Muthanna")
                          for hours in ("2", "4", "8")}:
            raise ValueError("Concrete package scenarios do not cover the declared region/hour matrix")
        concrete_scenarios = []
        for (region, hours), members in sorted(cells.items()):
            if len(members) != 81 or len({package_id for package_id, _ in members}) != 81:
                raise ValueError("Concrete candidate total must aggregate exactly 81 package scopes")
            summed = {key: sum((decimal(row.get(key), "concrete " + key) for _, row in members), Decimal(0))
                      for key in ("direct_material_cost", "direct_labor_cost", "estimated_total_iqd")}
            if abs(summed["estimated_total_iqd"] -
                   (summed["direct_material_cost"] + summed["direct_labor_cost"]) * Decimal("1.20")) > Decimal("0.02"):
                raise ValueError("Aggregated concrete material/labour/20% arithmetic does not reconcile")
            concrete_scenarios.append({
                "currency": "IQD",
                "region": region, "labour_hours_per_nominal_m3": hours,
                "package_count": len(members),
                "source_estimate_packet_ids": sorted({row["source_estimate_packet_id"]
                                                       for _, row in members if row.get("source_estimate_packet_id")}),
                "direct_material_cost_iqd": decimal_text(summed["direct_material_cost"]),
                "direct_labour_cost_iqd": decimal_text(summed["direct_labor_cost"]),
                "uplift_fraction": "0.20",
                "estimated_partial_total_iqd": decimal_text(summed["estimated_total_iqd"]),
                "complete_process_cost": None, "complete_installed_cost": None,
            })
        scope = _base_scope(concrete_line)
        ranked.append({**scope, "scenario_method": "sum of per-package material + assumed labour + 20% cases",
                       "scenario_count": len(concrete_scenarios), "scenarios": concrete_scenarios})

    # Candidate-bound raw stock screens use the same predeclared line takeoff;
    # neither a material form nor its assumed hours is selected here.
    for key in (("vehicle/body", "aluminium_reference"),
                ("vehicle/passive-secondary", "6082-T6-proposed")):
        line = line_by_key.get(key)
        if line is None:
            continue
        rows = line.get("domestic_raw_stock_sensitivity_scenarios", [])
        validated = _scenario_totals(rows, expected_count=21, where="aluminium raw-stock sensitivity")
        scenarios, seen, takeoff_ids = [], set(), set()
        for row, total in validated:
            alt = (row.get("material_form"), str(row.get("labour_hours_per_stock_tonne")))
            if (not alt[0] or alt[1] not in {"8", "16", "32"} or alt in seen
                    or not is_id(row.get("source_takeoff_id"))
                    or row.get("supplier_quote") is not False
                    or row.get("uplift_fraction") != "0.2"
                    or row.get("complete_process_cost") is not None
                    or row.get("complete_installed_cost") is not None):
                raise ValueError("Aluminium raw-stock scenario is duplicated, unbound, or outside its partial scope")
            seen.add(alt)
            takeoff_ids.add(row["source_takeoff_id"])
            scenarios.append({
                "currency": "IQD",
                "material_form": alt[0], "labour_hours_per_stock_tonne": alt[1],
                "estimated_partial_total_iqd": decimal_text(total),
                "direct_material_cost_iqd": row.get("direct_material_cost"),
                "direct_labour_cost_iqd": row.get("direct_labour_cost"),
                "uplift_fraction": "0.20", "source_takeoff_id": row["source_takeoff_id"],
                "source_process_record_id": row.get("source_process_record_id"),
                "complete_process_cost": None, "complete_installed_cost": None,
            })
        if (len(seen) != 21 or len(takeoff_ids) != 1 or len({form for form, _ in seen}) != 7
                or any({hours for candidate_form, hours in seen if candidate_form == form}
                       != {"8", "16", "32"} for form in {form for form, _ in seen})):
            raise ValueError("Aluminium raw-stock scenarios do not cover 7 forms × 3 labour cases")
        ranked.append({**_base_scope(line),
                       "scenario_method": "candidate gross stock × listed raw-stock form plus assumed labour + 20%",
                       "scenario_count": len(scenarios), "scenarios": scenarios})

    copper_key = ("wayside/primary", "copper-conductor")
    copper_line = line_by_key.get(copper_key)
    if copper_line is not None:
        rows = copper_line.get("copper_imported_raw_stock_sensitivity_scenarios", [])
        validated = _scenario_totals(rows, expected_count=3, where="copper imported raw-stock sensitivity",
                                     require_currency=False)
        scenarios = []
        for row, total in validated:
            hours = str(row.get("labour_hours_per_gross_stock_tonne"))
            if (hours not in {"8", "16", "32"} or row.get("candidate_id") != packet["candidate_id"]
                    or row.get("source_input_id") != packet["source_input_id"]
                    or row.get("supplier_quote") is not False
                    or row.get("compatible_product_match") is not False
                    or row.get("uplift_fraction") != "0.20"
                    or row.get("complete_process_cost") is not None
                    or row.get("complete_installed_cost") is not None):
                raise ValueError("Copper raw-stock scenario candidate or partial-cost boundary differs")
            scenarios.append({
                "labour_hours_per_gross_stock_tonne": hours,
                "currency": "IQD",
                "estimated_partial_total_iqd": decimal_text(total),
                "direct_material_cost_iqd": row.get("direct_material_cost_iqd"),
                "direct_labour_cost_iqd": row.get("direct_labour_cost_iqd"),
                "uplift_fraction": "0.20", "scenario_id": row.get("scenario_id"),
                "candidate_takeoff_id": row.get("candidate_takeoff_id"),
                "material_benchmark_source_id": row.get("material_benchmark_source_id"),
                "wage_benchmark_source_id": row.get("wage_benchmark_source_id"),
                "complete_process_cost": None, "complete_installed_cost": None,
            })
        if {row["labour_hours_per_gross_stock_tonne"] for row in scenarios} != {"8", "16", "32"}:
            raise ValueError("Copper raw-stock scenarios do not cover the three declared labour cases")
        ranked.append({**_base_scope(copper_line),
                       "scenario_method": "import unit-value raw-stock proxy + assumed winding labour + 20%",
                       "scenario_count": len(scenarios), "scenarios": scenarios})

    for scope in ranked:
        totals = [decimal(row["estimated_partial_total_iqd"]) for row in scope["scenarios"]]
        low, high = min(totals), max(totals)
        scope.update({
            "currency": "IQD", "scenario_min_iqd": decimal_text(low),
            "scenario_max_iqd": decimal_text(high),
            "scenario_spread_iqd": decimal_text(high - low),
            "scenario_spread_meaning": "spread across the enumerated input cases only; not a confidence interval or cost bound",
            "rank_status": "partial-scenario-exposure-only",
            "selection_margin_iqd": None, "could_change_preferred": None,
            "expected_value_of_information_iqd": None,
            "design_alternatives_researched": [],
            "design_alternatives_to_evaluate": _SCOPE_ACTIONS.get(
                (scope["system"], scope["material"]), {}).get("alternatives_to_evaluate", []),
            "alternative_candidate_ids": [],
            "alternative_status": "proposal-only; each option needs its own candidate/configuration and no result transfers",
            "likely_reruns": _SCOPE_ACTIONS.get((scope["system"], scope["material"]), {}).get("likely_reruns", []),
            "evidence_requests": _SCOPE_ACTIONS.get((scope["system"], scope["material"]), {}).get("evidence_requests", []),
            "unknown_is_zero": False,
        })
    ranked.sort(key=lambda row: (-decimal(row["scenario_spread_iqd"]),
                                 row["system"], row["material"], row["material_line_id"]))
    for rank, row in enumerate(ranked, 1):
        row["scenario_spread_rank"] = rank

    unranked = []
    for key, line in sorted(line_by_key.items()):
        if any(row["material_line_id"] == line["material_line_id"] for row in ranked):
            continue
        raw = line.get("domestic_raw_stock_sensitivity_scenarios", [])
        copper = line.get("copper_imported_raw_stock_sensitivity_scenarios", [])
        direct = line.get("domestic_fabrication_estimate_scenarios", [])
        if raw or copper or direct:
            # Unaggregated or incomplete line-level scenarios do not become
            # numeric ranks. Keep the obligation visible with a concrete gap.
            reason = "line scenarios are incomplete or do not form a candidate-total priced case"
        else:
            reason = "no candidate-bound partial price scenario is available"
        scope = _base_scope(line)
        actions = _SCOPE_ACTIONS.get(key, {})
        unranked.append({**scope, "rank_status": "unranked-economic-impact-not-bounded",
                         "unranked_reason": reason,
                         "scenario_count": 0,
                         "selection_margin_iqd": None, "could_change_preferred": None,
                         "expected_value_of_information_iqd": None,
                         "design_alternatives_to_evaluate": actions.get(
                             "alternatives_to_evaluate", _UNRANKED_ALTERNATIVES.get(key, [])),
                         "alternative_candidate_ids": [],
                         "alternative_status": "proposal-only; each option needs its own candidate/configuration and no result transfers",
                         "likely_reruns": actions.get("likely_reruns", []),
                         "evidence_requests": actions.get("evidence_requests",
                             _UNRANKED_EVIDENCE.get(key, [
                                 "define the candidate-specific purchasing unit and exact technical specification",
                                 "obtain compatible local material/product rates and a documented manufacturing route",
                                 "record quantity, yield, lead time, delivery, QA and installed scope"])),
                         "unknown_is_zero": False})

    payload = {
        "schema": "osr-candidate-sourcing-sensitivity/1",
        "procurement_packet_id": packet["packet_id"],
        "candidate_id": packet["candidate_id"],
        "evaluation_id": packet["evaluation_id"],
        "source_input_id": packet["source_input_id"],
        "method": "rank the spread between explicit candidate-bound partial cost scenarios in one currency; use modeled gross stock mass as reference only; keep unpriced scopes outside economic ranking",
        "rank_meaning": "relative spread among declared cases only; not probability, confidence bound, expected value of information, complete cost or candidate preference",
        "currency": "IQD",
        "scenario_spread_ranks_are_not_value_of_information": True,
        "mass_and_cost_are_not_combined": True,
        "ranked_partial_scenario_exposures": ranked,
        "unranked_scopes": unranked,
        "summary": {
            "ranked_partial_scenario_exposure_count": len(ranked),
            "unranked_scope_count": len(unranked),
            "candidate_material_line_count": len(lines),
            "partial_scenario_count": sum(row["scenario_count"] for row in ranked),
            "known_candidate_priced_supplier_matches": 0,
            "complete_installed_cost": packet.get("complete_installed_cost"),
            "physical_qualification": packet.get("physical_qualification"),
            "selection_margin": None,
            "could_change_preferred": None,
            "expected_value_of_information": None,
            "mass_sensitivity_status": "not-ranked; no explicit mass-impact bounds or uncertainty fractions are available",
            "mass_sensitivity_ranked_scope_count": 0,
            "gross_stock_mass_is_reference_only": True,
            "unknown_is_zero": False,
        },
    }
    payload["sensitivity_id"] = identity(payload)
    return payload
