"""Issue and verify one corrected Airport layout for a budgetary supplier enquiry."""
import argparse
from io import BytesIO
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from cities.Baghdad.engineering.mechanical.civil import family_comparison

from . import airport_alignment, audit_offers, audit_power_return, motion_power, scenario

PUBLISHED_RECEIPT = scenario.HERE / "audited-enquiry.receipt.json"
RECEIPT_KEYS = ("issue_id", "evaluation_id", "candidate_id", "layout")
SCHEMA = "baghdad-airport-budgetary-enquiry/1"
PURPOSE = dict(purpose="budgetary enquiry", physical_acceptance=False, fabrication_release=False,
               investment_selection=None, operating_authorisation=False)
MEMBERS = {
    "README.md", "engineering/alignment.json", "engineering/route.geojson", "engineering/vehicle.json",
    "engineering/station.json", "engineering/service.json", "engineering/feeder.json", "engineering/civil.json",
    "factory/routing-basis.json", "pricing/production.json", "pricing/supplier-comparisons.json",
    "returns/buyer-offers.json", "returns/vehicle.json", "returns/feeder.json", "decision.json",
}


def without(record, key):
    return {name: value for name, value in record.items() if name != key}


def reject_buyer_returns(present):
    if present:
        raise ValueError("Supplier enquiries require the audit before buyer offers, awards or equipment returns. "
                         "Keep the returned evidence in the buyer's audit.")


def issue(result, layout, path):
    if result["evaluation_id"] != scenario._id(without(result, "evaluation_id")):
        raise ValueError("Recalculate the audit before issuing a changed evaluation")
    if layout not in ("radial30", "paired6") or layout not in result["production"]:
        raise ValueError("Choose a layout with a civil and production quotation scope")
    reject_buyer_returns(any(result["supplier_comparisons"].values()) or result["civil"]["erection_offers"]
                         or result["feeder_equipment"]["source_return_id"] is not None)
    price = result["production"][layout]
    route = result["alignment"]
    train = result["vehicle"]
    decision = result["decision"]["candidates"][layout]
    duties = [r for r in result["power_days"] if r["topology"] == layout]
    feeder_id = duties[0]["feeder_physical_id"]
    factory = json.loads((scenario.PROTO / "factory-routes.json").read_bytes())
    docs = {
        "engineering/alignment.json": route, "engineering/route.geojson": airport_alignment.geojson(route),
        "engineering/vehicle.json": train, "engineering/station.json": result["climate"],
        "engineering/service.json": result["demand"],
        "engineering/civil.json": result["civil_quotation"],
        "engineering/feeder.json": dict(equipment=result["feeder_equipment"]["layouts"][feeder_id], duties=duties,
            high_mass=[r for r in result["high_mass_power"] if r["topology"] == layout],
            planning_price_sensitivity=result["feeder_price_sensitivities"][layout]),
        "factory/routing-basis.json": factory, "pricing/production.json": price,
        "pricing/supplier-comparisons.json": result["supplier_comparisons"].get(layout, []),
        "returns/buyer-offers.json": dict(schema=audit_offers.SCHEMA, layouts={layout: dict(offers=[], awards=[])}),
        "returns/vehicle.json": train["return_template"],
        "returns/feeder.json": dict(schema=audit_power_return.SCHEMA, layouts={}, documents={}),
        "decision.json": dict(layout=layout, assessment=decision, evidence_needed=result["decision"]["evidence_holds"],
                              audit_evaluation_id=result["evaluation_id"], **PURPOSE),
    }
    members = {name: json.dumps(data, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n"
               for name, data in docs.items()}
    members["README.md"] = guide(route, train, price, layout, decision, feeder_id).encode()
    manifest = dict(schema=SCHEMA, layout=layout, candidate_id=decision["physical_candidate_id"],
                    parent_candidate_id=route["parent_candidate_id"], evaluation_id=result["evaluation_id"],
                    assemblies=decision["assemblies"], production_evaluation_id=price["evaluation_id"],
                    feeder_physical_id=feeder_id, members_sha256={k: scenario.sha(v) for k,v in members.items()},
                    **PURPOSE)
    manifest["issue_id"] = scenario._id(manifest)
    members["manifest.json"] = scenario.encode(manifest)
    raw = scenario.archive(members)
    verify(BytesIO(raw), expected_issue_id=manifest["issue_id"])
    scenario.write_atomic(Path(path), raw)
    return manifest


def guide(route, train, price, layout, decision, feeder_id):
    q = price["quantities"]
    return f"""# Airport budgetary enquiry

Please quote the {route['route_km']:.3f} km working alignment, {train['physical']['formation_cars']}-car
{train['physical']['material']} formation and {layout} supply layout identified in manifest.json.
The operating screen for this configuration is **{decision['operating_screen']}**. Consult
decision.json for failures by duty and the evidence needed before selecting equipment or releasing drawings.

| Enquiry | Quantity basis | Return requested |
| --- | --- | --- |
| Representative car | {q['cars']} cars in {q['sets']} sets. Vehicle file contains installed allocations, drawing basis, cut stock and loaded cases. | Fitted BOM, mass and centre of gravity, joining details, access envelopes, door deflection and aged battery performance. |
| Powered bogie | {q['bogies']} bogies. Vehicle file gives static axle reactions, traction and degraded stopping demand. | Suspension stroke, mounting loads, removal clearance, brake response, thermal rating and failed-module performance. |
| Viaduct | {q['beams']} standard beams, {q['piers']} standard support positions and {q['bearings']} bearings. See [the civil takeoff](engineering/civil.json) for span, section and end closures. | Price stock, prestress, foundations, bearing replacement, haulage and erection at working radius. Identify closure design, ground data and temporary works separately. |
| Station | {q['station_sites']} sites. See the [route](engineering/route.geojson), [service](engineering/service.json) and [station calculations](engineering/station.json) for locations, passenger exchanges and summer duty. | Site layout, accessible boarding, clearances, evacuation and platform equipment. Identify allowances for unconfirmed sites. |
| Power and controls | {q['grid_sites']} supply sites. The [feeder study](engineering/feeder.json) lists chainages, failed cases, peak and RMS envelopes. | Rate continuous and transient loads, protection, return paths and safe isolation for feeder {feeder_id}. Use the rail-side rate sensitivity to compare scope. Quote utility terms, installation, validation and scheduled renewals separately. |
| Local production | The [production study](pricing/production.json) gives the planned quantities, equipment counts by resource and disruption schedules. The [routing basis](factory/routing-basis.json) identifies inherited process and fixture assumptions. | Return machine/crew hours, tool and fixture quantities, workcell capacity, yield, inspection holds, training, logistics and origin evidence. |

## Return an offer

1. Open pricing/production.json. In `pricings`, choose a lot and copy its `scope_id`, quantity, unit and year into your quotation. Identify exclusions, price basis, delivery, quote validity and renewal assumptions. Each price covers the complete lot in constant 2026 USD.
2. The buyer records each independent supplier in a copy of returns/buyer-offers.json under `offers`. Supply `offer_id`, `supplier`, `scope_id`, `price_usd`, `buyer_review_reference`, the quotation document's `offer_sha256` and `claimed_domestic_value_usd` (null when unknown). Retain the original documents and ERPNext Supplier Quotation references. Use `awards` for explicit awards with `offer_id`, `scope_id` and `buyer_award_reference`.
3. Run the original audit with its original service and engineering inputs plus `--offers buyer-offers.json --json`. Review the competing prices, revised cash flows and open items. Vehicle or feeder evidence uses the respective template and adjacent source documents with `--vehicle-return` or `--supply-return`.

The factory basis and released steel cut list describe the parent prototype. Confirm compatibility with this issue before pricing any change of material, girder, formation or tooling. Prices with unknown quantities, unpriced closures and unverified capabilities remain visible in the ledger. Use the source repository's prototype training workshop for supervised practice. Fabrication requires reviewed drawings, confirmed interfaces and inspection instructions.
"""


def verify(path, expected_issue_id=None):
    """Check an archive against the original issuer reference held separately by the buyer."""
    try:
        pin = (json.loads(PUBLISHED_RECEIPT.read_bytes()) if expected_issue_id is None
               else {"issue_id": expected_issue_id})
        if expected_issue_id is None and (not isinstance(pin, dict) or set(pin) != set(RECEIPT_KEYS)):
            raise ValueError("The published enquiry receipt requires the issue, evaluation, candidate and layout pins")
        with ZipFile(path) as bundle:
            names = bundle.namelist()
            if len(set(names)) != len(names) or set(names) != MEMBERS | {"manifest.json"}:
                raise ValueError("Enquiry members are missing, unexpected or duplicated")
            m = json.loads(bundle.read("manifest.json"))
            if (m["schema"] != SCHEMA or m["issue_id"] != scenario._id(without(m, "issue_id"))
                    or scenario.encode({k: m[k] for k in PURPOSE}) != scenario.encode(PURPOSE)):
                raise ValueError("Invalid budgetary enquiry manifest or release status")
            if m["issue_id"] != pin["issue_id"]:
                raise ValueError("Enquiry differs from the trusted issue ID. Use the original issuer reference for a custom case.")
            if any(m[key] != value for key, value in pin.items()):
                raise ValueError("Enquiry differs from the published evaluation, candidate or layout pin")
            raw = {k: bundle.read(k) for k in MEMBERS}
            if {k: scenario.sha(v) for k,v in raw.items()} != m["members_sha256"]:
                raise ValueError("Enquiry member digest differs from the issued scope")
            docs = {k: json.loads(v) for k,v in raw.items() if k.endswith((".json", ".geojson"))}
        check_scope(m, docs)
        from .audit_packet_evidence import check_evidence
        check_evidence(docs, m)
        return m
    except (KeyError, IndexError, TypeError, BadZipFile) as exc:
        raise ValueError("Incomplete budgetary enquiry or candidate scope") from exc


def check_scope(m, docs):
    route = airport_alignment.validate(docs["engineering/alignment.json"])
    train = docs["engineering/vehicle.json"]
    price = docs["pricing/production.json"]
    civil = docs["engineering/civil.json"]
    feeder = docs["engineering/feeder.json"]
    decision = docs["decision.json"]
    demand = docs["engineering/service.json"]
    factory = docs["factory/routing-basis.json"]
    vehicle_return = train["return_assessment"]
    equipment = feeder["equipment"]
    reject_buyer_returns(docs["pricing/supplier-comparisons.json"] != []
                         or price["localisation"]["buyer_referenced_offers"] != []
                         or any(vehicle_return[key] for key in ("submission_id", "claim", "documents", "submitted"))
                         or any(equipment[key] is not None for key in ("supplier_return_id", "supplier_document", "equipment_revision"))
                         or any(case["offer_id"] is not None for case in civil["priced_cases"].values()))
    layout = m["layout"]
    ctx = price["inputs"]
    assemblies = dict(alignment=route["alignment_id"], train=train["candidate_id"],
                      civil=civil["physical_id"], feeder=ctx["motion_candidate_id"])
    ids = price["child_ids"]
    normal, = (d for d in feeder["duties"] if d["condition"] == "normal")
    circuit = dict(alignment_id=assemblies["alignment"], feeder=ctx["feeder"])
    def require_equal(label, *values):
        if any(value != values[0] for value in values[1:]):
            raise ValueError(f"Enquiry records identify different {label}")

    if layout not in ("radial30", "paired6"):
        raise ValueError("Unknown budgetary layout")
    require_equal("layout", layout, ctx["feeder"]["name"], decision["layout"])
    require_equal("assemblies", assemblies, m["assemblies"], decision["assessment"]["assemblies"])
    require_equal("integrated candidate", scenario._id(assemblies), m["candidate_id"], decision["assessment"]["physical_candidate_id"])
    require_equal("release status", scenario.encode(PURPOSE), scenario.encode({k: decision[k] for k in PURPOSE}))
    require_equal("audit evaluation", m["evaluation_id"], decision["audit_evaluation_id"])
    require_equal("parent", m["parent_candidate_id"], route["parent_candidate_id"], train["physical"]["parent_candidate_id"],
                  factory["candidate_id"], civil["source_train_candidate_id"])
    require_equal("workshop routing", factory["evaluation_id"], ids["factory_evaluation_id"])
    require_equal("production evaluation", price["evaluation_id"], m["production_evaluation_id"],
                  scenario._id(without(price, "evaluation_id")))
    require_equal("vehicle evaluation", ids["vehicle_evaluation_id"], train["evaluation_id"],
                  scenario._id(without(train, "evaluation_id")))
    require_equal("vehicle duty", ctx["vehicle_duty_id"], train["duty_id"])
    require_equal("vehicle candidate", ctx["vehicle_candidate_id"], assemblies["train"], scenario._id(train["physical"]))
    require_equal("vehicle return", docs["returns/vehicle.json"], train["return_template"])
    require_equal("civil geometry", ctx["civil_physical_id"], assemblies["civil"])
    require_equal("civil pricing basis", ids["civil_row_id"], civil["audit_row_id"],
                  family_comparison.digest(without(civil, "audit_row_id")))
    require_equal("alignment", ctx["alignment_id"], assemblies["alignment"], demand["alignment_id"])
    require_equal("alignment record", ids["alignment_record_id"], route["record_id"], demand["alignment_record_id"])
    require_equal("geometry export", docs["engineering/route.geojson"], airport_alignment.geojson(route))
    require_equal("demand evaluation", ctx["demand_evaluation_id"], demand["evaluation_id"])
    require_equal("working day", ctx["motion_evaluation_id"], normal["evaluation_id"])
    require_equal("buyer return", docs["returns/buyer-offers.json"],
                  dict(schema=audit_offers.SCHEMA, layouts={layout: dict(offers=[], awards=[])}))
    require_equal("feeder return", docs["returns/feeder.json"],
                  dict(schema=audit_power_return.SCHEMA, layouts={}, documents={}))
    require_equal("feeder equipment", m["feeder_physical_id"], scenario._id(circuit))
    require_equal("equipment scope", feeder["equipment"]["feeder_physical"], circuit)
    require_equal("feeder duties", sorted(d["condition"] for d in feeder["duties"]), sorted(motion_power.CONDITIONS))
    for d in feeder["duties"]:
        require_equal("working candidate", d["candidate_id"], assemblies["feeder"])
    for d in feeder["duties"] + feeder["high_mass"]:
        require_equal("feeder scope", d["feeder_physical"], circuit)
        require_equal("feeder configuration", d["feeder_physical_id"], m["feeder_physical_id"])
    for row in price["pricings"]:
        if row["supplier_scope"]["context"] != ctx or scenario._id(row["supplier_scope"]) != row["scope_id"]:
            raise ValueError("Price lot differs from its issued scope")



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--issue-id", help="Original issue ID recorded by the buyer for a custom enquiry")
    args = parser.parse_args()
    try:
        print(verify(args.packet, args.issue_id)["issue_id"])
    except (ValueError, OSError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    main()
