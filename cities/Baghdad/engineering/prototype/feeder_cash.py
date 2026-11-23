"""Compare two Airport feeder offers on the opening's annual financing schedule."""
import argparse
import json
from hashlib import sha256
from pathlib import Path

from cities.Baghdad import airport_integration, airport_opening, financing
from cities.Baghdad.engineering.commissioning import feeder
from cities.Baghdad.engineering.prototype import car, commercial


OFFSITE = "Offsite distribution feeders and tie-ins"


def scope_form(radial, alternative):
    """Bind optional custody and boundary evidence to the contents of both bids."""
    return {
        "return_ids": [car.identity(f) for f in (radial, alternative)],
        "documents": {},
        "bid_document": {"radial": None, "alternative": None},
        "scope_review_document": None,
        "offsite_boundary": None,
        "separate_installed_offsite_usd": None,
    }


def _boundary(radial, alternative, review, directory):
    if review is None:
        return {"boundary": "unconfirmed", "additional_direct_usd": 0, "documents": {}}
    template = scope_form(radial, alternative)
    if not isinstance(review, dict) or review.keys() != template.keys() or review["return_ids"] != template["return_ids"]:
        raise ValueError("Scope review must identify the exact two returned offers")
    docs = commercial.evidence(review["documents"], directory)
    references = review["bid_document"]
    if (not isinstance(references, dict) or references.keys() != template["bid_document"].keys()
            or not all(commercial.has_document(ref, docs) for ref in [*references.values(), review["scope_review_document"]])):
        raise ValueError("Supply the two bid references and the documented offsite boundary decision")
    boundary, costs = review["offsite_boundary"], review["separate_installed_offsite_usd"]
    if boundary == "included in both bids" and costs is None:
        extra = 0.0
    elif boundary == "excluded from both bids" and isinstance(costs, dict) and costs.keys() == references.keys():
        extra = (commercial.number(costs["alternative"], "six-site offsite price")
                 - commercial.number(costs["radial"], "radial offsite price"))
    else:
        raise ValueError("Specify matching offsite boundaries; separate offsite cost may be counted only once")
    return {"boundary": boundary, "additional_direct_usd": extra, "documents": docs,
            "bid_document": references, "scope_review_document": review["scope_review_document"],
            "separate_installed_offsite_usd": costs}


def compare(opening, service, cfg, radial, alternative, scope_review=None, directory=None, finance_return=None):
    base = commercial.assess(opening, service, cfg, finance_return, directory)
    if "line_power" in base["matched_supplier_lots"] or OFFSITE in base["site_replacements"]:
        raise ValueError("Exclude parallel commercial line-power or offsite prices from this comparison")
    forms = (radial, alternative)
    records = []
    for index, form in enumerate(forms):
        option = form.get("scope", {}).get("option") if isinstance(form, dict) and isinstance(form.get("scope"), dict) else None
        if option not in (("priced_radial",) if index == 0 else feeder.OPTIONS[1:]):
            raise ValueError("Supply the priced radial form first and one six-site option second")
        record = feeder.evaluate(opening, form, service=service)["return"]
        records.append(record)
    boundary = _boundary(radial, alternative, scope_review, directory)
    result = {
        "schema": "baghdad-feeder-cash/1", "opening_candidate_id": opening["candidate_id"],
        "opening_evaluation_id": opening["evaluation_id"], "commercial_evaluation_id": base["evaluation_id"],
        "service_evaluation_id": service["evaluation_id"], "source_sha256": {
            Path(m.__file__).name: sha256(Path(m.__file__).read_bytes()).hexdigest()
            for m in (feeder, financing, commercial)
        }, "compiler_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "returns": [{k: r[k] for k in ("return_id", "scope", "record_kind", "coverage", "document_revision", "price")}
                    for r in records],
        "offsite_review": boundary, "basis": "Six-site bid minus radial bid; millions of constant 2026 USD.",
        "status": "awaiting matched prices", "annual_cash_difference_usd_m": None,
        "absolute_repriced_opening_capital_usd_m": None,
        "radial_planning_reference": {"capital_usd_m": base["priced_capital_usd_m"],
                                     "annual_opex_usd_m": base["annual_operating_cost_usd_m"]},
        "limits": [
            "Matching installed scope, utility boundary, site connections, protection, commissioning, taxes, recurring service and renewal coverage require buyer and utility review.",
            "Both bids use the same draw shares, borrowing terms, operating fractions, fares and service. Owner overhead, contingency, energy losses, additional factory capacity and unquoted works are held constant.",
            "The radial budget includes modelled allowances that can differ from the radial bid. The cash difference alone cannot establish a revised absolute opening budget.",
        ],
        "selection": None, "authorised_for_procurement": False, "physical_accepted": False,
    }
    if any(r["price"]["priced_scope_pv_30y_usd"] is None for r in records):
        result["evaluation_id"] = car.identity(result)
        return result
    first, second = (r["price"] for r in records)
    direct = {k: (alternative["price_2026_usd"]["installed_direct"][k]
                  - radial["price_2026_usd"]["installed_direct"][k]) / 1e6 for k in feeder.PRICE_ITEMS}
    capex = sum(direct.values()) + boundary["additional_direct_usd"] / 1e6
    upkeep = (second["annual_upkeep_usd"] - first["annual_upkeep_usd"]) / 1e6
    renewals = {
        y: (second["renewals_by_year_usd"].get(y, 0) - first["renewals_by_year_usd"].get(y, 0)) / 1e6
        for y in sorted(first["renewals_by_year_usd"].keys() | second["renewals_by_year_usd"].keys())
    }
    schedule = base["annual_cash"]
    draws = [{"year": r["year"], "capital_usd_m": capex*r["capital"]/base["priced_capital_usd_m"]}
             for r in schedule if r["capital"] > 0]
    delta = financing.cash_schedule({
        "selected_construction_cashflow": {"annual_capital_draw": draws, "full_service_start_year_assumption": draws[-1]["year"]+1},
        "selected_annual_opex_usd_m": {"total": upkeep},
        "selected_renewals_usd_m": [{"year": y, "usd_m": v} for y, v in renewals.items()],
    }, *financing.CASES["mixed_debt"])
    for row, original in zip(delta["annual"], schedule, strict=True):
        if row["year"] != original["year"]:
            raise ValueError("Financing years differ from Airport cash schedule")
        row["service_fraction"] = original["service_fraction"]
        row["operations"] = row["service_fraction"] * upkeep
        row["net_fares"] = 0.0
        row["buyer_cash"] = (row["capital"] - row["borrowing"] + row["interest"] + row["principal"]
                             + row["operations"] + row["renewals"])
        row["public_cash_after_fares"] = row["buyer_cash"]
    result.update(status="conditional bid-difference sensitivity", installed_scope_difference_usd_m=direct,
                  installed_difference_usd_m=capex, annual_upkeep_difference_usd_m=upkeep,
                  renewal_difference_by_operating_year_usd_m=renewals, annual_cash_difference_usd_m=delta["annual"],
                  financing_terms={k:v for k,v in delta.items() if k != "annual"},
                  whole_life_difference_30y_at_4pct_usd_m=(
                      second["priced_scope_pv_30y_usd"] - first["priced_scope_pv_30y_usd"]
                      + boundary["additional_direct_usd"]) / 1e6)
    result["evaluation_id"] = car.identity(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radial", type=Path, required=True)
    parser.add_argument("--alternative", type=Path, required=True)
    parser.add_argument("--scope-template", action="store_true")
    parser.add_argument("--scope-review", type=Path)
    parser.add_argument("--finance-return", type=Path)
    parser.add_argument("--documents", type=Path)
    args = parser.parse_args()
    def read(path):
        return json.loads(path.read_bytes()) if path is not None else None
    try:
        radial, alternative = read(args.radial), read(args.alternative)
        if args.scope_template:
            result = scope_form(radial, alternative)
        else:
            parent = airport_integration.build()
            opening = car.build(parent)["opening"]
            result = compare(opening, parent["service"], airport_opening.opening_inputs()[0], radial,
                             alternative, read(args.scope_review), args.documents, read(args.finance_return))
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        parser.exit(2, f"Invalid Airport feeder comparison: {exc}\n")


if __name__ == "__main__":
    main()
