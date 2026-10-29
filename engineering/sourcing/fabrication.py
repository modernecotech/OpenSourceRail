"""Source-linked domestic fabrication cost screens.

The calculation is deliberately limited to declared raw-material quantities,
direct labour hours, and a user-specified uplift. It is not an installed price,
supplier offer, or validated production route.
"""
from decimal import Decimal, localcontext
import re

from .model import UNITS, decimal, decimal_text, identity, is_id, record, text, validate_record


def _benchmark(value, expected_unit, currency):
    validate_record(value, "benchmark")
    if value.get("is_manufactured_product_price") is not False:
        raise ValueError("Fabrication inputs must cite material/wage benchmarks, not product offers")
    if value.get("quantity_unit") != expected_unit:
        raise ValueError("Benchmark unit differs from the explicit recipe line")
    if value.get("currency") != currency:
        raise ValueError("Mixed currencies require an explicit, source-bound conversion")
    return value


def domestic_fabrication_estimate(*, estimate_key, candidate_id, input_id,
                                  output_quantity, output_unit, currency,
                                  material_lines, labour_lines, benchmarks,
                                  uplift_fraction="0.20"):
    """Price an explicit domestic process recipe against immutable benchmarks.

    ``candidate_id`` and ``input_id`` bind the estimate to a twin evaluation
    context. The returned record states separately if the recipe is only a
    generic unit-rate reference and has not been mapped to candidate takeoff.
    Material and labour line units must match their exact benchmark units.
    """
    text(estimate_key, "fabrication estimate key")
    if not is_id(candidate_id) or not is_id(input_id):
        raise ValueError("Exact digital-twin candidate and input identities required")
    if output_unit not in UNITS:
        raise ValueError("Explicit output unit required")
    if not isinstance(currency, str) or re.fullmatch(r"[A-Z]{3}", currency) is None:
        raise ValueError("ISO estimate currency required")
    output = decimal(output_quantity, "output quantity", positive=True)
    uplift = decimal(uplift_fraction, "uplift fraction")
    if not Decimal(0) <= uplift <= Decimal(1):
        raise ValueError("Uplift fraction must be from zero through one")
    if not isinstance(benchmarks, dict):
        raise ValueError("Exact immutable benchmark lookup required")
    if not isinstance(material_lines, list) or not material_lines:
        raise ValueError("At least one explicit material line required")
    if not isinstance(labour_lines, list) or not labour_lines:
        raise ValueError("At least one explicit labour-hours line required")

    used_benchmarks = {}
    source_ids = set()
    materials, labour = [], []
    with localcontext() as context:
        context.prec = 28
        material_total = Decimal(0)
        labour_total = Decimal(0)

        for row in material_lines:
            if not isinstance(row, dict):
                raise ValueError("Material line object required")
            name = text(row.get("material_key"), "material key")
            unit = row.get("quantity_unit")
            if unit not in UNITS:
                raise ValueError("Canonical material quantity unit required")
            quantity = decimal(row.get("quantity"), "material quantity", positive=True)
            benchmark_id = row.get("benchmark_id")
            if not is_id(benchmark_id) or benchmark_id not in benchmarks:
                raise ValueError("Exact material benchmark identity required")
            benchmark = _benchmark(benchmarks[benchmark_id], unit, currency)
            rate = decimal(benchmark.get("unit_price"), "material benchmark rate")
            extension = quantity * rate
            material_total += extension
            source_ids.add(benchmark["source_id"])
            used_benchmarks[benchmark_id] = benchmark
            materials.append(dict(material_key=name, quantity=decimal_text(quantity),
                                  quantity_unit=unit, benchmark_id=benchmark_id,
                                  unit_rate=decimal_text(rate), currency=currency,
                                  extended_cost=decimal_text(extension),
                                  evidence_scope=benchmark.get("cost_scope")))

        for row in labour_lines:
            if not isinstance(row, dict):
                raise ValueError("Labour line object required")
            name = text(row.get("labour_category"), "labour category")
            hours = decimal(row.get("person_hours"), "person-hours", positive=True)
            benchmark_id = row.get("benchmark_id")
            if not is_id(benchmark_id) or benchmark_id not in benchmarks:
                raise ValueError("Exact labour benchmark identity required")
            benchmark = _benchmark(benchmarks[benchmark_id], "h", currency)
            rate = decimal(benchmark.get("unit_price"), "hourly wage benchmark")
            extension = hours * rate
            labour_total += extension
            source_ids.add(benchmark["source_id"])
            used_benchmarks[benchmark_id] = benchmark
            labour.append(dict(labour_category=name, person_hours=decimal_text(hours),
                               quantity_unit="h", benchmark_id=benchmark_id,
                               unit_rate=decimal_text(rate), currency=currency,
                               extended_cost=decimal_text(extension),
                               wage_basis=benchmark.get("normalization_basis"),
                               evidence_scope=benchmark.get("cost_scope")))

        direct = material_total + labour_total
        uplift_amount = direct * uplift
        estimated_total = direct + uplift_amount
        unit_total = estimated_total / output

    return record("process", process_key="domestic-fabrication-cost-screen",
        estimate_key=estimate_key, candidate_id=candidate_id, input_id=input_id,
        application_scope="digital-twin evaluation context; generic unit-rate recipe not mapped to candidate takeoff",
        output_quantity=decimal_text(output), output_unit=output_unit,
        currency=currency, material_lines=materials, labour_lines=labour,
        benchmark_ids=sorted(used_benchmarks), source_ids=sorted(source_ids),
        direct_material_cost=decimal_text(material_total),
        direct_labor_cost=decimal_text(labour_total),
        direct_cost=decimal_text(direct), uplift_fraction=decimal_text(uplift),
        uplift_amount=decimal_text(uplift_amount),
        uplift_basis="direct material plus direct labour",
        estimated_total=decimal_text(estimated_total),
        estimated_unit_cost=decimal_text(unit_total),
        complete_process_cost=None, complete_installed_cost=None,
        whole_life_cost=None, candidate_takeoff_mapped=False,
        known_inputs_only=True, unknown_is_zero=False,
        excluded_cost_categories=["material waste and yield", "consumables", "tooling and moulds",
            "factory occupancy and utilities", "equipment depreciation", "quality inspection and testing",
            "packaging", "transport and delivery", "taxes and duty", "erection and installation",
            "rework, warranty and lifecycle maintenance"],
        limitations=["Wage benchmark is an annual 2025 daily average normalized by the recipe's explicit 8-hour day assumption",
            "Material benchmark is a public statistical/market observation, not a supplier quotation for the exact grade or delivery scope",
            "Labour hours are recipe assumptions until measured on a defined work route",
            "The requested uplift is a planning allowance and is not validated as overhead, profit, contingency, or tax"])


def domestic_fabrication_takeoff_estimate(*, estimate_key, takeoff, target_rollup,
                                          recipe_output_quantity, currency, material_lines, labour_lines,
                                          benchmarks, uplift_fraction="0.20"):
    """Apply a declared unit recipe to one exact, fully quantified takeoff roll-up.

    The output is a candidate-bound budget scenario. It preserves every source
    manufacturing-group and engineering-occurrence identity, but does not turn
    gross geometry into a qualified product, a purchase order, or installed cost.
    """
    if (not isinstance(takeoff, dict) or
            takeoff.get("schema") != "osr-engineering-material-takeoff/1" or
            not is_id(takeoff.get("takeoff_id")) or
            takeoff["takeoff_id"] != identity({key: value for key, value in takeoff.items()
                                                if key != "takeoff_id"})):
        raise ValueError("Exact sealed material-takeoff packet required")
    candidate_id = takeoff.get("candidate_id")
    source_input_id = takeoff.get("source_input_id")
    if not is_id(candidate_id) or not is_id(source_input_id):
        raise ValueError("Exact takeoff candidate and source-input identities required")
    if not isinstance(target_rollup, dict) or set(target_rollup) != {"system", "material", "stock_scope"}:
        raise ValueError("Exact roll-up system, material and stock scope required")
    selector = {key: text(target_rollup[key], "takeoff " + key) for key in target_rollup}
    matches = [row for row in takeoff.get("material_rollups", [])
               if all(row.get(key) == value for key, value in selector.items())]
    if len(matches) != 1:
        raise ValueError("Target material takeoff must match one exact roll-up")
    rollup = matches[0]
    if rollup.get("missing_nominal_stock_volume_group_count") != 0:
        raise ValueError("Every manufacturing group in the target roll-up needs a nominal volume")
    volume = decimal(rollup.get("nominal_stock_volume_m3"),
                     "takeoff nominal stock volume", positive=True)
    group_count = rollup.get("manufacturing_group_count")
    occurrence_count = rollup.get("engineering_occurrence_count")
    if type(group_count) is not int or group_count <= 0 or type(occurrence_count) is not int or occurrence_count <= 0:
        raise ValueError("Positive exact group and occurrence counts required")

    scoped_groups = [row for row in takeoff.get("manufacturing_groups", [])
                     if all(row.get(key) == value for key, value in selector.items())]
    if len(scoped_groups) != group_count:
        raise ValueError("Target roll-up group identities are incomplete")
    group_volume = Decimal(0)
    occurrence_ids = set()
    group_refs = []
    for group in scoped_groups:
        if group.get("nominal_stock_volume_m3") is None:
            raise ValueError("A target manufacturing group has unknown volume")
        member_ids = group.get("engineering_occurrence_ids")
        if not isinstance(member_ids, list) or not member_ids or len(member_ids) != len(set(member_ids)):
            raise ValueError("Exact engineering occurrence membership is required")
        if occurrence_ids.intersection(member_ids):
            raise ValueError("Takeoff groups overlap engineering occurrences")
        occurrence_ids.update(member_ids)
        group_volume += decimal(group["nominal_stock_volume_m3"], "group nominal volume", nonnegative=True)
        group_refs.append({
            "manufacturing_group_id": group.get("manufacturing_group_id"),
            "engineering_group_key": group.get("engineering_group_key"),
            "nominal_stock_volume_m3": group["nominal_stock_volume_m3"],
            "known_gross_stock_mass_kg": group.get("known_gross_stock_mass_kg"),
            "engineering_occurrence_ids": sorted(member_ids),
            "component_definition_ids": group.get("component_definition_ids", []),
            "geometry_ids": group.get("geometry_ids", []),
        })
    if len(occurrence_ids) != occurrence_count or group_volume != volume:
        raise ValueError("Takeoff roll-up quantity or occurrence reconciliation differs")

    output_quantity = decimal(recipe_output_quantity, "recipe output quantity", positive=True)
    scaled_materials = []
    for row in material_lines:
        if not isinstance(row, dict):
            raise ValueError("Material recipe line required")
        scaled_materials.append(dict(row, quantity=decimal_text(
            decimal(row.get("quantity"), "recipe material quantity", positive=True) * volume / output_quantity)))
    scaled_labour = []
    for row in labour_lines:
        if not isinstance(row, dict):
            raise ValueError("Labour recipe line required")
        scaled_labour.append(dict(row, person_hours=decimal_text(
            decimal(row.get("person_hours"), "recipe person-hours", positive=True) * volume / output_quantity)))

    unit_process = domestic_fabrication_estimate(
        estimate_key=estimate_key, candidate_id=candidate_id, input_id=source_input_id,
        output_quantity=volume, output_unit="m3", currency=currency,
        material_lines=scaled_materials, labour_lines=scaled_labour,
        benchmarks=benchmarks, uplift_fraction=uplift_fraction)
    fields = {key: value for key, value in unit_process.items()
              if key not in {"schema", "kind", "record_id"}}
    fields.update(
        application_scope="candidate-bound gross material takeoff roll-up; recipe quantities and labour hours are explicit scenarios, not measured production data",
        candidate_takeoff_id=takeoff["takeoff_id"],
        candidate_takeoff_scope=selector,
        candidate_takeoff_group_count=group_count,
        candidate_takeoff_occurrence_count=occurrence_count,
        candidate_takeoff_mapped=True,
        candidate_takeoff_quantity_basis="nominal stock geometry volume; not a mix design, purchased quantity, finished beam quantity, installed quantity or accepted component",
        candidate_takeoff_group_refs=sorted(group_refs, key=lambda row: (row["engineering_group_key"], row["manufacturing_group_id"])),
        complete_process_cost=None,
        complete_installed_cost=None,
        whole_life_cost=None,
        unknown_is_zero=False,
    )
    return record("process", **fields)
