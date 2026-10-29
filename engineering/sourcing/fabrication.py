"""Source-linked domestic fabrication cost screens.

The calculation is deliberately limited to declared raw-material quantities,
direct labour hours, and a user-specified uplift. It is not an installed price,
supplier offer, or validated production route.
"""
from decimal import Decimal, localcontext
import re

from .model import UNITS, decimal, decimal_text, is_id, record, text, validate_record


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
