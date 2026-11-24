"""Validation and canonical identity for the native sourcing workflow."""

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from hashlib import sha256
import json
import re


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def object_value(value):
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict):
        raise ValueError("Provide a JSON object")
    return value


def exact_text(value, label, limit=140):
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > limit:
        raise ValueError(f"Invalid {label}")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError(f"Invalid {label}")
    return value


def calendar_date(value):
    value = exact_text(value, "date", 10)
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Use a date in YYYY-MM-DD format")
    return parsed


def decimal_value(value, label, *, places=6, positive=False):
    if type(value) not in (int, float, str, Decimal) or len(str(value)) > 32:
        raise ValueError(f"Invalid {label}")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid {label}") from exc
    if not number.is_finite() or not 0 <= number <= 10**12 or (positive and not number):
        raise ValueError(f"Invalid {label}")
    if number != number.quantize(Decimal(1).scaleb(-places)):
        raise ValueError(f"{label} supports at most {places} decimal places")
    return number


def decimal_text(number):
    formatted = format(number.normalize(), "f")
    return "0" if not number else formatted


def amount_usd(rate, qty):
    return (rate * qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def one_lot(packet, lot_id):
    matches = [lot for lot in packet["lots"] if lot["lot_id"] == lot_id]
    if len(matches) != 1:
        raise ValueError("Choose a lot in the staged engineering estimate")
    return matches[0]


def corrected_enquiry_reference(packet, lot):
    """Return the public packet and physical lot pointers without the estimate."""
    if packet.get("schema") != "baghdad-airport-erpnext-estimate/1":
        return None
    scope = lot.get("supplier_scope")
    if not isinstance(scope, dict) or scope.get("lot_id") != lot["lot_id"]:
        raise ValueError("Corrected enquiry requires its physical lot scope")
    issue_id, scope_id = packet.get("issue_id"), lot.get("design_id")
    if (not isinstance(issue_id, str) or not re.fullmatch(r"[0-9a-f]{64}", issue_id)
            or scope_id != digest(scope)):
        raise ValueError("Corrected enquiry requires the exact issue and lot scope IDs")
    qty = scope.get("quantity")
    decimal_value(qty, "physical lot quantity", places=18, positive=True)
    return dict(issue_id=issue_id, scope_id=scope_id, lot_id=lot["lot_id"], quantity=qty,
                unit=exact_text(scope.get("unit"), "physical lot unit"))


def estimate_payload(value):
    packet = object_value(value)
    if not isinstance(packet.get("lots"), list) or not packet["lots"]:
        raise ValueError("Provide a sourcing estimate with lots")
    for key in ("candidate_id", "evaluation_id"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(packet.get(key, ""))):
            raise ValueError(f"Invalid estimate {key}")
    if digest({k: v for k, v in packet.items() if k != "evaluation_id"}) != packet["evaluation_id"]:
        raise ValueError("Sourcing estimate evaluation digest does not match the packet")
    ids = set()
    for lot in packet["lots"]:
        if not isinstance(lot, dict):
            raise ValueError("Invalid sourcing lot")
        lot_id = exact_text(lot.get("lot_id"), "lot ID", 100)
        if lot_id in ids:
            raise ValueError("Sourcing lot IDs must be unique")
        ids.add(lot_id)
        exact_text(lot.get("description"), "lot description", 2000)
        exact_text(lot.get("unit"), "lot unit", 140)
        decimal_value(lot.get("quantity"), "lot quantity", places=18, positive=True)
    return packet


def offer_payload(value, binding):
    posted = object_value(value)
    scope = binding["scope"]
    expected = {
        "candidate_id": scope["candidate_id"],
        "evaluation_id": scope["evaluation_id"],
        "lot_id": scope["lot_id"],
        "scope_sha256": digest(scope),
        "unit": scope["unit"],
        "currency": "USD",
    }
    required = {
        *expected,
        "quantity", "rate_usd", "supplier_reference", "valid_until", "lead_time_days",
        "annual_upkeep_usd", "renewals_usd", "exclusions", "warranty",
    }
    if posted.keys() != required or any(posted[key] != val for key, val in expected.items()):
        raise ValueError("Offer must match the RFQ design, evaluation, lot, unit, scope and USD basis")
    qty = decimal_value(posted["quantity"], "quantity", positive=True)
    if qty != decimal_value(scope["quantity"], "lot quantity", positive=True):
        raise ValueError("Offer quantity must match the complete RFQ lot")
    rate = decimal_value(posted["rate_usd"], "USD unit rate", positive=True)
    direct = amount_usd(rate, qty)
    if not 0 < direct <= 10**12:
        raise ValueError("Invalid extended USD price")
    lead = decimal_value(posted["lead_time_days"], "lead time in days", places=0, positive=True)
    if lead > 3650:
        raise ValueError("Use a delivery lead time of up to 3650 days")
    upkeep = posted["annual_upkeep_usd"]
    if upkeep is not None:
        upkeep = float(decimal_value(upkeep, "annual upkeep", places=2))
    renewals = posted["renewals_usd"]
    if renewals is not None:
        if not isinstance(renewals, dict) or any(str(year) not in {str(n) for n in range(1, 31)} for year in renewals):
            raise ValueError("Renewals must map service years 1–30 to USD costs")
        renewals = {str(year): float(decimal_value(cost, f"renewal year {year}", places=2))
                    for year, cost in renewals.items()}
    if scope["price_period"] == "annual" and upkeep not in (None, 0):
        raise ValueError("The annual service rate already includes annual upkeep")
    if scope["price_period"] == "scheduled" and (
        upkeep not in (None, 0)
        or renewals is not None and sum(Decimal(str(cost)) for cost in renewals.values()) != direct
    ):
        raise ValueError("Allocate the scheduled price across renewal years and avoid duplicate upkeep")
    operating_year = scope["technical_scope"].get("operating_year")
    if scope["price_period"] == "scheduled" and renewals is not None and operating_year is not None:
        if renewals != {str(operating_year): float(direct)}:
            raise ValueError("Allocate the scheduled price to the RFQ's stated operating year")
    exclusions = posted["exclusions"]
    if exclusions is not None:
        if not isinstance(exclusions, list) or len(exclusions) > 30:
            raise ValueError("Provide a list of exceptions or explicitly declare unknown coverage")
        exclusions = [exact_text(row, "exclusion", 500) for row in exclusions]

    return dict(
        expected,
        quantity=decimal_text(qty),
        rate_usd=decimal_text(rate),
        direct_usd=float(direct),
        supplier_reference=exact_text(posted["supplier_reference"], "supplier quotation reference"),
        valid_until=calendar_date(posted["valid_until"]).isoformat(),
        lead_time_days=int(lead),
        annual_upkeep_usd=upkeep,
        renewals_usd=renewals,
        exclusions=exclusions,
        warranty=exact_text(posted["warranty"], "warranty or explicit warranty status", 1000),
    )
