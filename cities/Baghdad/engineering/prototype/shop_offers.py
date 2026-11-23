"""Generate machine-level price returns and compare suppliers within one issued estimate."""

import argparse
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
IDENTITY = ("candidate_id", "shop_cost_evaluation_id", "lot_id", "id", "pricing_unit", "period")
FIELDS = (*IDENTITY, "priced_quantity", "supplier", "erp_supplier_quotation", "unit_rate_usd",
          "scope_response", "delivery_terms_and_exclusions", "price_evidence_ref")


def basis(costs, row):
    return dict(candidate_id=costs["candidate_id"], shop_cost_evaluation_id=costs["evaluation_id"],
                **{key: row[key] for key in ("lot_id", "id", "pricing_unit", "period")},
                priced_quantity="" if row["priced_quantity"] is None else str(row["priced_quantity"]))


def template(costs):
    output = StringIO(newline="")
    writer = csv.DictWriter(output, FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(basis(costs, r) for r in costs["resources"])
    return output.getvalue().encode()


def compare(costs, documents):
    payload = {key: value for key, value in costs.items() if key != "evaluation_id"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if sha256(canonical).hexdigest() != costs["evaluation_id"]:
        raise ValueError("Workshop estimate content differs from its evaluation ID")
    resources = {r["id"]: r for r in costs["resources"]}
    seen = set()
    comparison = []
    for name, content in documents:
        reader = csv.DictReader(StringIO(content))
        if reader.fieldnames != list(FIELDS):
            raise ValueError(f"{name}: columns differ from the issued return")
        count = 0
        identity = None
        for i, row in enumerate(reader, 2):
            where = f"{name} line {i}"
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f"{where}: wrong number of columns")
            resource = resources.get(row["id"])
            if resource is None or any(row[k] != v for k, v in basis(costs, resource).items()):
                raise ValueError(f"{where}: unknown resource or changed estimate, quantity, unit or period")
            response = {k: row[k].strip() for k in FIELDS[len(IDENTITY) + 1:]}
            if not any(response.values()):
                continue
            if not all(response.values()) or response["scope_response"] not in ("matches", "deviation"):
                raise ValueError(f"{where}: incomplete price or scope return")
            owner = (response["supplier"], response["erp_supplier_quotation"])
            if identity is None:
                identity = owner
            if identity != owner:
                raise ValueError(f"{where}: use a separate file for each supplier quotation")
            key = (owner[0].casefold(), row["id"])
            if key in seen:
                raise ValueError(f"{where}: duplicate supplier/resource. Select one quote revision")
            seen.add(key)
            try:
                rate = Decimal(response["unit_rate_usd"])
            except InvalidOperation as exc:
                raise ValueError(f"{where}: invalid unit rate") from exc
            if not rate.is_finite() or rate <= 0 or rate > Decimal("1e12") or rate.as_tuple().exponent < -6:
                raise ValueError(f"{where}: enter a positive USD unit rate, up to six decimals")
            quantity = resource["priced_quantity"]
            comparable = response["scope_response"] == "matches"
            amount = None if quantity is None else str((rate * Decimal(str(quantity))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            delta = rate - Decimal(str(resource["unit_rate_usd"]["base"])) if comparable else None
            comparison.append(dict(**basis(costs, resource), **response, extended_usd=amount,
                                   quantity_status=resource["quantity_status"],
                                   unit_variance_from_planning_usd=None if delta is None else str(delta)))
            count += 1
        if not count:
            raise ValueError(f"{name}: no priced lines")
    return dict(candidate_id=costs["candidate_id"], shop_cost_evaluation_id=costs["evaluation_id"],
                currency="USD", responses=sorted(comparison, key=lambda r: (r["id"], r["supplier"])),
                commercial_use="Quotation attachment; confirm scope, parent credits and technical review in ERPNext.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("returns", nargs="+", type=Path, help="one issued CSV per supplier quotation")
    parser.add_argument("--costs", type=Path, default=HERE / "shop-costs.json")
    args = parser.parse_args()
    try:
        result = compare(json.loads(args.costs.read_bytes()), [(p.name, p.read_text(encoding="utf-8-sig")) for p in args.returns])
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
