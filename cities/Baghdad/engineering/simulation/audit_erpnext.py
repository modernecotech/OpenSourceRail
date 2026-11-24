"""Prepare and reconcile verified Airport budgetary enquiries with ERPNext."""

import argparse
from hashlib import file_digest
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

from deployment.erpnext.apps.osr_erpnext.osr_erpnext.sourcing_contract import (
    calendar_date, decimal_value, digest, exact_text,
)

from . import audit_offers, audit_packet, scenario

SCHEMA = "baghdad-airport-erpnext-estimate/1"
PERIODS = {"opening-direct": "one-time", "first-full-year-operations": "annual",
           "renewal-schedule": "scheduled"}


def issue_data(path, expected_issue_id):
    # Use the same bytes for verification and extraction.
    contents = Path(path).read_bytes()
    manifest = audit_packet.verify(BytesIO(contents), expected_issue_id=expected_issue_id)
    with ZipFile(BytesIO(contents)) as bundle:
        pricing = json.loads(bundle.read("pricing/production.json"))
    return manifest, pricing


def portal_estimate(path, estimate_date, *, expected_issue_id=None):
    """Return the payload accepted by ERPNext's existing buyer estimate upload."""
    issue, pricing = issue_data(path, expected_issue_id)
    return estimate_payload(issue, pricing, estimate_date)


def estimate_payload(issue, pricing, estimate_date):
    lots = []
    for row in pricing["pricings"]:
        if not row["quantity"]:
            continue
        if row["cost_evidence"] == "buyer-referenced offer input":
            raise ValueError("Use an issue with unchanged baseline pricing scopes")
        scope = row["supplier_scope"]
        title = row["lot_id"].replace("-", " ").capitalize()
        description = f"{title} for {issue['layout']}, full scope of {scope['quantity']} {scope['unit']}"
        if scope["operating_year"] is not None:
            description += f" in operating year {scope['operating_year']}"
        lots.append(dict(
            lot_id=row["lot_id"], description=description, quantity=1, unit="lot",
            inclusion_group=row["group"], price_period=PERIODS[row["group"]],
            price_basis=scope["currency"], design_id=row["scope_id"], operating_year=scope["operating_year"],
            published_scope=description, supplier_scope=scope,
            deliverables=f"Complete lot {row['lot_id']} in verified enquiry {issue['issue_id']}. "
                         f"Match engineering scope {row['scope_id']} and report any deviations.",
            design_documents=[f"Airport enquiry {issue['issue_id']}: pricing/production.json and engineering files"],
            **{f"{band}_usd": row["usd"][band] if row["usd"] is not None else None
               for band in ("low", "base", "high")},
        ))
    packet = dict(schema=SCHEMA, candidate_id=issue["candidate_id"], issue_id=issue["issue_id"],
                  parent_candidate_id=issue["parent_candidate_id"], audit_evaluation_id=issue["evaluation_id"],
                  estimate_date=calendar_date(estimate_date).isoformat(), lots=lots)
    packet["evaluation_id"] = digest(packet)
    return packet


def matching_quotation(rows, quotation):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Provide native ERPNext quotation records")
    matching = [row for row in rows if row.get("quotation") == quotation]
    if len(matching) != 1:
        raise ValueError("Use one uniquely attributable ERPNext quotation")
    return matching[0]


def quotation_digest(value):
    try:
        path = Path(value)
        if path.is_file():
            with path.open("rb") as document:
                if document.read(1):
                    document.seek(0)
                    return file_digest(document, "sha256").hexdigest()
    except (OSError, TypeError, ValueError) as exc:
        raise ValueError("Provide a readable, nonempty original quotation document") from exc
    raise ValueError("Provide a readable, nonempty original quotation document")


def reviewed_offers(path, estimate_date, export, reviews, *, expected_issue_id=None):
    """Map current, complete ERPNext quote amounts to buyer-reviewed audit offers."""
    manifest, pricing = issue_data(path, expected_issue_id)
    estimate = estimate_payload(manifest, pricing, estimate_date)
    if not isinstance(export, dict) or not isinstance(export.get("comparison"), dict) or not isinstance(reviews, list):
        raise ValueError("Provide a native ERPNext comparison and buyer review list")
    comparison = export["comparison"]
    rfq = exact_text(export.get("rfq"), "RFQ")
    project = exact_text(export.get("project"), "Project")
    lot_id = exact_text(export.get("lot_id"), "lot ID", 100)
    as_of = calendar_date(export.get("as_of"))
    lot = next((row for row in estimate["lots"] if row["lot_id"] == lot_id), None)
    if (lot is None or comparison.get("schema") != "osr-lot-quotation-comparison/1"
            or comparison.get("comparison_id") != digest({
                key: value for key, value in comparison.items() if key != "comparison_id"
            })
            or comparison.get("estimate_evaluation_id") != estimate["evaluation_id"]
            or comparison.get("candidate_id") != estimate["candidate_id"]
            or comparison.get("lot_id") != lot_id
            or comparison.get("price_period") != lot["price_period"]
            or comparison.get("currency_basis") != lot["price_basis"]
            or type(export.get("rfq_docstatus")) is not int
            or export["rfq_docstatus"] != 1):
        raise ValueError("ERPNext comparison must bind the issued candidate, estimate, lot, currency and submitted RFQ")
    layout = manifest["layout"]
    offers, awards = [], []
    for review in reviews:
        if not isinstance(review, dict):
            raise ValueError("Provide a buyer review for each quotation")
        quote = exact_text(review.get("quotation"), "quotation")
        row = matching_quotation(comparison.get("offers"), quote)
        trace = matching_quotation(export.get("suppliers"), quote)
        supplier = exact_text(row.get("supplier"), "supplier")
        if (trace.get("supplier") != supplier or trace.get("status") != "received"
                or trace.get("project") != project or trace.get("rfq") != rfq or trace.get("lot_id") != lot_id
                or not calendar_date(trace.get("recorded_on")) <= as_of <= calendar_date(trace.get("valid_until"))):
            raise ValueError("Use a current, attributable ERPNext quotation")
        if row["evidence_kind"] != "supplier-offer" or row["comparable_direct"] is not True or row["exclusions"] != []:
            raise ValueError("Use a buyer-reviewed quote covering the complete lot")
        amount = decimal_value(row.get("direct_usd"), "quoted amount for the period", places=2, positive=True)
        reference = exact_text(review.get("buyer_review_reference"), "buyer review reference", 500)
        origin = dict(project=project, rfq=rfq, lot_id=lot_id, quotation=quote, supplier=supplier,
                      as_of=as_of.isoformat(), recorded_on=trace["recorded_on"], valid_until=trace["valid_until"],
                      comparison_id=comparison["comparison_id"], comparison_receipt_sha256=digest(export))
        native_reference = json.dumps(origin, sort_keys=True)
        offers.append(dict(offer_id=quote, supplier=supplier, scope_id=lot["design_id"],
                           buyer_review_reference=f"{reference} | ERPNext {native_reference}",
                           offer_sha256=quotation_digest(review.get("quotation_document")),
                           price_usd=float(amount), claimed_domestic_value_usd=None))
        if "buyer_award_reference" in review:
            awards.append(dict(scope_id=lot["design_id"], offer_id=quote,
                               buyer_award_reference=review["buyer_award_reference"]))
    document = dict(schema=audit_offers.SCHEMA, layouts={layout: dict(offers=offers, awards=awards)})
    audit_offers.choices(document, layout, pricing["pricings"], pricing["inputs"])
    return document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("estimate_date", help="Buyer estimate edition date in YYYY-MM-DD")
    parser.add_argument("output", type=Path)
    parser.add_argument("--issue-id", help="Expected issue ID from a trusted source for a custom packet")
    parser.add_argument("--comparison", type=Path, help="JSON result of the ERPNext compare_rfq method")
    parser.add_argument("--reviews", type=Path, help="JSON list of explicit buyer reviews and original quote paths")
    args = parser.parse_args()
    if bool(args.comparison) != bool(args.reviews):
        parser.error("--comparison and --reviews must be supplied together")
    if args.comparison:
        output = reviewed_offers(args.packet, args.estimate_date, json.loads(args.comparison.read_bytes()),
                                 json.loads(args.reviews.read_bytes()), expected_issue_id=args.issue_id)
    else:
        output = portal_estimate(args.packet, args.estimate_date, expected_issue_id=args.issue_id)
    scenario.write_atomic(args.output, json.dumps(output, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n")


if __name__ == "__main__":
    main()
