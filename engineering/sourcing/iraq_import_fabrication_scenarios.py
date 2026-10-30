"""Build first-pass Iraqi conversion-cost sensitivities from CSO import rows.

These are generic one-tonne material screens, not candidate prices or quotes.
The imported HS-group unit values are combined with explicit local labour-hour
assumptions and an unallocated 20% uplift. Product form, grade and shop route
remain unresolved.
"""
from argparse import ArgumentParser
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path

from .catalogue import load_catalogue
from .model import identity


SCHEMA = "osr-iraq-import-fabrication-sensitivity/1"
LABOUR_HOURS_PER_TONNE = (8, 16, 32)
UPLIFT = Decimal("0.20")
MATERIAL_KEYS = (
    "cso-import-2025:hs76042100:iqd-per-kg",
    "cso-import-2025:hs76042900:iqd-per-kg",
    "cso-import-2025:hs76069100:iqd-per-kg",
    "cso-import-2025:hs76069200:iqd-per-kg",
)
WAGE_KEY = "iq-cso-2026-09:baghdad:wage:skilled:hour-8h-day"
DEFAULT_OUTPUT = Path(
    "docs/design-engine/sourcing/domestic-fabrication/"
    "cso-imported-aluminium-fabrication-sensitivity-2025-2026.json"
)


def _money(value):
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")


def build_packet(records):
    benchmarks = {
        row["benchmark_key"]: row
        for row in records
        if row["kind"] == "benchmark"
    }
    materials = [benchmarks[key] for key in MATERIAL_KEYS]
    wage = benchmarks[WAGE_KEY]
    if wage["currency"] != "IQD" or wage["quantity_unit"] != "h":
        raise ValueError("Baghdad skilled-wage benchmark must be IQD/hour")
    wage_per_hour = Decimal(wage["unit_price"])
    if wage_per_hour <= 0:
        raise ValueError("Positive explicit Baghdad wage required")

    scenarios = []
    for material in materials:
        material_per_tonne = Decimal(material["unit_price"]) * Decimal("1000")
        for hours in LABOUR_HOURS_PER_TONNE:
            labour = wage_per_hour * Decimal(hours)
            direct = material_per_tonne + labour
            uplift = direct * UPLIFT
            row = {
                "hs_code": material["hs_code"],
                "material_description": material["material_description"],
                "material_benchmark_key": material["benchmark_key"],
                "material_benchmark_id": material["record_id"],
                "gross_input_quantity": "1",
                "gross_input_unit": "t",
                "reported_import_unit_value_iqd_per_kg": material["unit_price"],
                "material_cost_iqd_per_tonne": _money(material_per_tonne),
                "assumed_direct_labour_hours_per_tonne": hours,
                "wage_benchmark_key": wage["benchmark_key"],
                "wage_benchmark_id": wage["record_id"],
                "wage_iqd_per_hour": wage["unit_price"],
                "direct_labour_cost_iqd_per_tonne": _money(labour),
                "direct_material_plus_labour_iqd_per_tonne": _money(direct),
                "unallocated_uplift_fraction": format(UPLIFT, "f"),
                "unallocated_uplift_iqd_per_tonne": _money(uplift),
                "screened_rate_iqd_per_tonne": _money(direct + uplift),
                "estimate_status": "illustrative imported-stock plus Iraqi labour sensitivity",
                "candidate_bom_match": False,
                "supplier_quote": False,
            }
            row["scenario_id"] = identity(row)
            scenarios.append(row)

    payload = {
        "schema": SCHEMA,
        "estimate_date": "2026-10-30",
        "source_document_sha256": next(
            row["document_sha256"]
            for row in records
            if row["kind"] == "source"
            and row["source_key"] == "iraq.cosit.import-report-2025"
        ),
        "source_method": "CSO 2025 Table 10 national import value / reported weight (kg), using IQD totals; HS-group grade and product form remain unresolved.",
        "labour_method": "September 2026 Baghdad CSO skilled construction-worker base-wage observation used as an explicit local labour proxy; 8, 16 and 32 assumed hours per gross input tonne.",
        "formula": "(2025 import CIF unit value per gross input tonne + assumed hours × September 2026 Baghdad base wage per hour) × 1.20",
        "candidate_binding": {
            "candidate_id": None,
            "input_id": None,
            "reason": "The candidate material takeoff does not resolve profile versus sheet quantities, alloy/temper, order yield or exact product form; no candidate cost extension is admitted.",
        },
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "scope_limits": [
            "CSO values are aggregate national CIF import unit values, not supplier quotations or domestic raw-stock prices.",
            "The wage is a construction-worker base-wage proxy, not a measured factory pay rate or employer-loaded shop rate.",
            "Labour hours are planning sensitivities, not timed manufacturing routes.",
            "The 20% is an unallocated uplift on direct material and base-wage labour; it is not evidence of overhead, profit, tax or contingency.",
            "No alloy/temper, product geometry, yield/scrap, tooling, energy, consumables, QA, finishing, duty, inland delivery, packaging or installation is included.",
            "These generic per-tonne rates are not compatible BOM matches and do not establish installed vehicle or railway cost.",
        ],
        "release_boundary": {
            "supplier_contacts_sent": 0,
            "supplier_quotes": 0,
            "engineering_approved": False,
            "procurement_approved": False,
            "candidate_bom_cost_changed": False,
            "physical_acceptance": False,
        },
    }
    payload["packet_id"] = identity(payload)
    return payload


def write_packet(path=DEFAULT_OUTPUT):
    path = Path(path)
    packet = build_packet(load_catalogue())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n")
    return packet


def main(argv=None):
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    packet = write_packet(args.output)
    print(json.dumps({
        "packet_id": packet["packet_id"],
        "scenario_count": packet["scenario_count"],
        "output": str(args.output),
        "candidate_bom_cost_changed": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
