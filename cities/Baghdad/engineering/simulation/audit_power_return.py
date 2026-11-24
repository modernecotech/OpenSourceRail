"""Match feeder ratings and fault evidence to the exact corrected Airport layout."""

from math import isfinite

from cities.Baghdad.engineering.commissioning import feeder as commissioning
from cities.Baghdad.engineering.prototype import commercial
from engineering.outline.baghdad_system import _id

SCHEMA = "baghdad-airport-feeder-equipment-return/1"
CURRENT_FIELDS = ("branch_peak_ka", "branch_rms_ka", "source_peak_ka", "source_rms_ka")
FAULT_FIELDS = ("near_bus_bolted_fault_ka", "remote_single_path_bolted_fault_ka")
THERMAL_FIELDS = ("hot_resistance_ohm", "thermal_resistance_k_per_w", "heat_capacity_j_per_k",
                  "ambient_c", "initial_temperature_c", "maximum_temperature_c")


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


def _inventory(power_days, high_mass_power, traction_fault_power=()):
    layouts = {}
    seen = set()
    for category, days in (("matched service", power_days), ("high-mass stress", high_mass_power),
                           ("one-driven-axle-out", traction_fault_power)):
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
            duration = _current(row.get("service_day_current_basis_seconds"), "service_day_current_basis_seconds")
            if duration is not None and duration <= 0:
                raise ValueError("Feeder current duty duration must be positive")
            layout["duties"].append(dict(
                category=category, condition=row["condition"], evaluation_id=evaluation,
                numerical_valid=row["numerical_valid"], failure=row.get("failure"),
                duration_s=duration,
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
        if (not isinstance(reply, dict) or not {"equipment_revision", "document", "ratings", "protection"} <= reply.keys()
                or reply.keys() - {"equipment_revision", "document", "ratings", "protection", "thermal"}
                or not isinstance(reply["equipment_revision"], str) or not reply["equipment_revision"].strip()
                or not commercial.has_document(reply["document"], docs)
                or not isinstance(reply["ratings"], dict) or set(reply["ratings"]) != set(CURRENT_FIELDS)
                or reply["protection"] is not None and not isinstance(reply["protection"], dict)):
            raise ValueError("Match a sourced equipment revision, complete current-rating fields and optional protection")
        for name, value in reply["ratings"].items():
            if value is not None:
                commercial.number(value, name, positive=True)
        thermal = reply.get("thermal")
        if thermal is not None:
            if not isinstance(thermal, dict) or thermal.keys() != {"branch", "source"}:
                raise ValueError("Thermal return requires branch and source component scopes")
            for component, parameters in thermal.items():
                if parameters is None:
                    continue
                if not isinstance(parameters, dict) or parameters.keys() != set(THERMAL_FIELDS):
                    raise ValueError(f"Thermal {component} requires a complete sourced RC and temperature envelope")
                for field in THERMAL_FIELDS[:3]:
                    commercial.number(parameters[field], field, positive=True)
                for field in THERMAL_FIELDS[3:]:
                    value = parameters[field]
                    if type(value) not in (float, int) or not isfinite(value):
                        raise ValueError(f"Invalid {field}")
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


def _thermal_screen(duties, thermal):
    """Bound each component temperature for every possible waveform under the replay bounds.

    An RMS upper bound limits integral I²dt over the replay. The peak bounds
    instantaneous heating. A first-order passive RC with hot resistance then
    has a temperature rise no larger than either its peak steady limit or the
    adiabatic whole-day limit. Exceeding either bound proves nothing about the
    actual waveform; only a bound below the limit can pass this screen.
    """
    result = {}
    for component, field_prefix in (("branch", "branch"), ("source", "source")):
        parameters = None if thermal is None else thermal[component]
        rows = []
        for duty in duties:
            peak = duty["current_ka"][f"{field_prefix}_peak_ka"]
            rms = duty["current_ka"][f"{field_prefix}_rms_ka"]
            duration = duty["duration_s"]
            energy = None if rms is None or duration is None else (rms * 1000)**2 * duration
            upper = None
            if parameters is not None and peak is not None:
                resistance = parameters["hot_resistance_ohm"]
                capacity = parameters["heat_capacity_j_per_k"]
                thermal_r = parameters["thermal_resistance_k_per_w"]
                # This remains conservative when the stated initial temperature
                # exceeds ambient, since its cooling is not credited.
                base = max(parameters["ambient_c"], parameters["initial_temperature_c"])
                peak_rise = (peak * 1000)**2 * resistance * thermal_r
                adiabatic_rise = None if energy is None else energy * resistance / capacity
                upper = base + min(peak_rise, adiabatic_rise) if adiabatic_rise is not None else base + peak_rise
            status = "unknown"
            if parameters is not None and parameters["initial_temperature_c"] > parameters["maximum_temperature_c"]:
                status = "fail"
            elif duty["numerical_valid"] and upper is not None and upper <= parameters["maximum_temperature_c"]:
                status = "pass"
            rows.append(dict(evaluation_id=duty["evaluation_id"], category=duty["category"], condition=duty["condition"],
                             numerical_valid=duty["numerical_valid"], duration_s=duration,
                             current_peak_ka=peak, current_rms_upper_ka=rms,
                             current_i2t_upper_a2s=energy, maximum_temperature_upper_c=upper,
                             temperature_limit_c=None if parameters is None else parameters["maximum_temperature_c"],
                             screen=status))
        statuses = {row["screen"] for row in rows}
        status = "fail" if "fail" in statuses else "unknown" if "unknown" in statuses else "pass"
        result[component] = dict(status=status, parameters=parameters, duties=rows,
                                 scope="One declared component per active path/site; worst-branch and worst-site daily RMS are upper bounds. Hot resistance and RC parameters require installed-equipment evidence.")
    return result


def assess(power_days, high_mass_power, document=None, *, evidence_directory=None, traction_fault_power=()):
    """Return equipment enquiry and conditional matching margins for each physical layout."""
    layouts = _inventory(power_days, high_mass_power, traction_fault_power)
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
        margins = _declared_protection_margins(values)
        # Any valid observed peak is a lower bound on the full duty, even if
        # another duty was incomplete. Missing curve bands cannot cure overload.
        observed = max((envelope[f]["value"] for f in peak_fields if envelope[f]["value"] is not None), default=None)
        load_margin = _margin(values["maximum_healthy_current_ka"], observed)
        if healthy is None and load_margin["screen"] != "fail":
            load_margin["screen"] = "unknown"
        margins["declared_healthy_envelope_covers_duty"] = load_margin
        if any(row["screen"] == "fail" for row in margins.values()):
            protection_status = "fail"
        current_margins = _current_margins(envelope, ratings)
        thermal_result = _thermal_screen(layout["duties"], reply.get("thermal"))
        screens = {row["screen"] for row in current_margins.values()} | {protection_status}
        equipment_status = "fail" if "fail" in screens else "unknown" if "unknown" in screens else "pass"
        complete_screens = screens | {row["status"] for row in thermal_result.values()}
        complete_status = ("fail" if "fail" in complete_screens else
                           "unknown" if "unknown" in complete_screens else "pass")
        layout.update(
            envelope=envelope, equipment_revision=reply.get("equipment_revision"), supplier_return_id=_id(reply) if reply else None,
            supplier_document=reply.get("document"), current_rating_screen=current_margins,
            declared_thermal=thermal_result,
            declared_protection=dict(status=protection_status, checks=protection_result, margins=margins),
            ideal_static_fault_comparison=dict(
                near_bus_breaking_margin=_margin(values["rated_breaking_ka"], _duty_value(envelope, "near_bus_bolted_fault_ka")),
                remote_pickup_margin=_margin(_duty_value(envelope, "remote_single_path_bolted_fault_ka"),
                                             values["pickup_max_ka"], strict=True),
                scope="Ideal bolted DC indicators. Actual fault limits depend on utility supply, source controls, and arc, return and conductor conditions.",
            ),
            equipment_return_screen=equipment_status,
            complete_equipment_duty_screen=complete_status, production_ranking_eligible=False,
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
