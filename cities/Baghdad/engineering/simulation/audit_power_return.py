"""Match feeder ratings and fault evidence to the exact corrected Airport layout."""

from cities.Baghdad.engineering.commissioning import feeder as commissioning
from cities.Baghdad.engineering.prototype import commercial
from engineering.outline.baghdad_system import _id

SCHEMA = "baghdad-airport-feeder-equipment-return/1"
CURRENT_FIELDS = ("branch_peak_ka", "branch_rms_ka", "source_peak_ka", "source_rms_ka")
FAULT_FIELDS = ("near_bus_bolted_fault_ka", "remote_single_path_bolted_fault_ka")


def binding(motion):
    """Identify the source/branch circuit independently of train and operating duty."""
    physical = motion["physical"]
    scope = dict(alignment_id=physical["alignment_id"], feeder=physical["feeder"])
    return dict(feeder_physical=scope, feeder_physical_id=_id(scope))


def _current(value, label):
    return None if value is None else commercial.number(value, label)


def _margin(capacity, demand, *, strict=False, unit="kA"):
    difference = None if capacity is None or demand is None else capacity - demand
    passed = None if difference is None else (difference > 0 if strict else difference >= 0)
    return dict(capacity=capacity, demand=demand, margin=difference, unit=unit,
                screen="unknown" if passed is None else "pass" if passed else "fail")


def _inventory(power_days, high_mass_power):
    layouts = {}
    seen = set()
    for category, days in (("matched service", power_days), ("high-mass stress", high_mass_power)):
        for row in days:
            physical = row.get("feeder_physical")
            key = row.get("feeder_physical_id")
            if (not isinstance(physical, dict) or physical.keys() != {"alignment_id", "feeder"}
                    or key != _id(physical) or physical["feeder"]["name"] != row["topology"]
                    or list(physical["feeder"]["sites"]) != list(row["site_chainages_m"])):
                raise ValueError("Feeder duty needs the matching physical layout and ID")
            evaluation = row["evaluation_id"]
            if evaluation in seen:
                raise ValueError("Feeder duty evaluation appears more than once")
            seen.add(evaluation)
            enquiry = row["equipment_enquiry"]
            values = dict(
                branch_peak_ka=enquiry.get("observed_healthy_branch_peak_ka_no_sharing_credit"),
                branch_rms_ka=enquiry.get("upper_daily_branch_rms_ka_no_sharing_credit"),
                source_peak_ka=row.get("peak_site_ka"), source_rms_ka=row.get("site_rms_ka"),
                near_bus_bolted_fault_ka=enquiry.get("ideal_bolted_near_bus_ka"),
                remote_single_path_bolted_fault_ka=enquiry.get("ideal_bolted_remote_single_path_ka"),
            )
            if (row.get("rms_branch_ka") is not None and values["branch_rms_ka"] is not None
                    and row["rms_branch_ka"] != values["branch_rms_ka"]):
                raise ValueError("Feeder duty has conflicting branch RMS values")
            layout = layouts.setdefault(key, dict(feeder_physical=physical, topology=row["topology"], duties=[]))
            if type(row["numerical_valid"]) is not bool:
                raise ValueError("Feeder duty must declare numerical validity")
            layout["duties"].append(dict(
                category=category, condition=row["condition"], evaluation_id=evaluation,
                numerical_valid=row["numerical_valid"], failure=row.get("failure"),
                current_ka={name: _current(value, name) for name, value in values.items()},
            ))
    return layouts


def _supplier_returns(document, layouts, evidence_directory):
    if document is None:
        return {}, {}
    if (not isinstance(document, dict) or document.keys() != {"schema", "layouts", "documents"}
            or document["schema"] != SCHEMA or not isinstance(document["layouts"], dict)
            or document["layouts"].keys() - layouts.keys()):
        raise ValueError("Use the feeder equipment return schema and exact studied physical IDs")
    docs = commercial.evidence(document["documents"], evidence_directory)
    for reply in document["layouts"].values():
        if (not isinstance(reply, dict) or reply.keys() != {"equipment_revision", "document", "ratings", "protection"}
                or not isinstance(reply["equipment_revision"], str) or not reply["equipment_revision"].strip()
                or not commercial.has_document(reply["document"], docs)
                or not isinstance(reply["ratings"], dict) or set(reply["ratings"]) != set(CURRENT_FIELDS)
                or reply["protection"] is not None and not isinstance(reply["protection"], dict)):
            raise ValueError("Match a sourced equipment revision, complete current-rating fields and optional protection")
        for name, value in reply["ratings"].items():
            if value is not None:
                commercial.number(value, name, positive=True)
    return document["layouts"], docs


def _envelope(duties):
    result = {}
    for name in (*CURRENT_FIELDS, *FAULT_FIELDS):
        valid = [d for d in duties if d["numerical_valid"] and d["current_ka"][name] is not None]
        choose = min if name == "remote_single_path_bolted_fault_ka" else max
        governing = choose(valid, key=lambda d: d["current_ka"][name]) if valid else None
        result[name] = dict(
            value=governing["current_ka"][name] if governing else None, unit="kA",
            governing_evaluation_id=governing["evaluation_id"] if governing else None,
            governing_condition=governing["condition"] if governing else None,
            complete=len(valid) == len(duties),
        )
    return result


def _duty_value(envelope, field):
    row = envelope[field]
    return row["value"] if row["complete"] else None


def _current_margins(envelope, ratings):
    margins = {}
    for field in CURRENT_FIELDS:
        row = envelope[field]
        margin = _margin(ratings.get(field), row["value"])
        if not row["complete"] and margin["screen"] != "fail":
            margin["screen"] = "unknown"
        margin["duty_complete"] = row["complete"]
        margins[field] = margin
    return margins


def _declared_protection_margins(values):
    return dict(
        healthy_current_below_pickup=_margin(values["pickup_min_ka"], values["maximum_healthy_current_ka"], strict=True),
        least_sustained_fault_above_pickup=_margin(values["minimum_sustained_fault_ka"], values["pickup_max_ka"], strict=True),
        maximum_prospective_fault_breaking=_margin(values["rated_breaking_ka"], values["maximum_prospective_fault_ka"]),
        system_time_constant_within_rating=_margin(values["rated_time_constant_ms"],
                                                  values["maximum_system_time_constant_ms"], unit="ms"),
        recovery_voltage_within_rating=_margin(values["rated_dc_voltage_kv"],
                                              values["maximum_recovery_voltage_kv"], unit="kV"),
    )


def assess(power_days, high_mass_power, document=None, *, evidence_directory=None):
    """Return equipment enquiry and conditional matching margins for each physical layout."""
    layouts = _inventory(power_days, high_mass_power)
    submitted, documents = _supplier_returns(document, layouts, evidence_directory)
    for key, layout in layouts.items():
        reply = submitted.get(key) or {}
        ratings = reply.get("ratings", {})
        protection = reply.get("protection")
        envelope = _envelope(layout["duties"])
        # Feed the submitted protection screen the larger of source and branch peak
        # demand. The returned protection scope covers each active path/site.
        peak_fields = ("source_peak_ka", "branch_peak_ka")
        healthy = max(envelope[field]["value"] for field in peak_fields) if all(
            envelope[field]["complete"] for field in peak_fields) else None
        protection_result = (commissioning.protection_screen(protection, healthy) if protection is not None else None)
        protection_status = "unknown"
        if protection_result and not protection_result["missing"]:
            checks = protection_result["checks"]
            independent_fail = any(not passed for name, passed in checks.items()
                                   if name != "healthy_envelope_covers_declared_duty")
            if independent_fail or healthy is not None and not checks["healthy_envelope_covers_declared_duty"]:
                protection_status = "fail"
            elif healthy is not None:
                protection_status = "pass"
        values = protection or dict.fromkeys(commissioning.PROTECTION)
        current_margins = _current_margins(envelope, ratings)
        screens = {row["screen"] for row in current_margins.values()} | {protection_status}
        equipment_status = "fail" if "fail" in screens else "unknown" if "unknown" in screens else "pass"
        layout.update(
            envelope=envelope, equipment_revision=reply.get("equipment_revision"), supplier_return_id=_id(reply) if reply else None,
            supplier_document=reply.get("document"), current_rating_screen=current_margins,
            declared_protection=dict(status=protection_status, checks=protection_result, margins=_declared_protection_margins(values)),
            ideal_static_fault_comparison=dict(
                near_bus_breaking_margin=_margin(values["rated_breaking_ka"], _duty_value(envelope, "near_bus_bolted_fault_ka")),
                remote_pickup_margin=_margin(_duty_value(envelope, "remote_single_path_bolted_fault_ka"),
                                             values["pickup_max_ka"], strict=True),
                scope="Ideal bolted DC indicators. Actual fault limits depend on utility supply, source controls, and arc, return and conductor conditions.",
            ),
            equipment_return_screen=equipment_status, production_ranking_eligible=False,
        )
    result = dict(
        schema="baghdad-airport-feeder-equipment-assessment/1", layouts=layouts, supplier_documents=documents,
        source_return_id=_id(document) if document is not None else None,
        holds=[
            "Verify conductor and return temperatures, converter and breaker duty, local ambient/installation and peak duration at the actual installation.",
            "Replay a controlled current-limited moving train with the exact equipment curves. The present replay estimates steady resistive DC duty.",
            "Obtain authenticated fault study, backup clearing, safe isolation and restoration, touch potentials and evacuation evidence.",
            "Obtain the approved utility connection, physical equipment and witnessed integrated tests with independent review.",
        ],
        production_ranking_eligible=False, physical_acceptance=False,
    )
    return {**result, "assessment_id": _id(result)}
