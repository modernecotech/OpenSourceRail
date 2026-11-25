"""Estimate Airport support and site allowances from corridor GIS samples."""

from bisect import bisect_left
from collections import Counter
from hashlib import sha256
from math import ceil, isclose, isfinite, pi
from pathlib import Path
import tomllib

from cities.Baghdad.engineering.mechanical.civil import family_comparison
from cities.Baghdad.engineering.simulation import airport_alignment
from engineering.outline.baghdad_system import _id

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[1]
ROOT = CITY.parents[1]
AIRPORT_RATES = CITY / "airport-works.toml"
CIVIL_RATES = CITY / "iraq-capital.toml"
MARKET = CITY / "iraq-market.toml"
CIVIL_CONCEPT = family_comparison.HERE / "concept.toml"
CASES = family_comparison.CASES
SCHEMA = "osr-baghdad-airport-site-costs/1"
# Classification for placing an allowance. No mapped quantity sets a bearing limit.
REPEATED_WATER_PCT = 10.0


def number(value, description):
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"Expected a finite {description}")
    return value


def optional_pct(row, key):
    value = row.get(key)
    if value is not None and not 0 <= number(value, key) <= 100:
        raise ValueError(f"{key} outside the 0–100 percent range")
    return value


def read_rates(path):
    return tomllib.loads(path.read_text(encoding="utf-8"))


def support_samples(profile, girder, cap_depth_m):
    """Carry the civil row's standard chainages plus its one end closure."""
    route_m = number(profile["route_m"], "route length in metres")
    if route_m <= 0 or not isclose(route_m, girder["route_km"] * 1000, rel_tol=0, abs_tol=1e-5):
        raise ValueError("Site profile and civil quantities cover different route lengths")
    samples = profile["samples"]
    points = [number(row["chainage_m"], "sample chainage in metres") for row in samples]
    if (not points or points[0] != 0 or not isclose(points[-1], route_m, rel_tol=0, abs_tol=1e-5)
            or any(a >= b for a, b in zip(points, points[1:]))):
        raise ValueError("Site samples must span the entire route in strictly increasing chainage order")
    levels = [number(row["soffit_height_m"], "railway soffit height") for row in samples]
    expected_bays = girder["full_standard_bays"]
    standard = [i * girder["span_m"] for i in range(expected_bays + 1)]
    potential_closure = girder["closure_bay_m"] or 0
    if not isclose(standard[-1] + potential_closure, route_m, rel_tol=0, abs_tol=1e-5):
        raise ValueError("Site support chainages do not match the civil stock and closure quantities")
    locations = [(point, False) for point in standard]
    if potential_closure:
        locations.append((route_m, True))
    multiplicity = 1 if girder["shared_pier"] else 2
    if len(locations) * multiplicity != girder["supports"]:
        raise ValueError("Site support population differs from the civil estimate")

    supports = []
    for chainage, closure_support in locations:
        right = min(bisect_left(points, chainage), len(points) - 1)
        left = max(right - 1, 0)
        if points[right] == chainage or left == right:
            soffit = levels[right]
            nearest = right
        else:
            frac = (chainage - points[left]) / (points[right] - points[left])
            soffit = levels[left] + frac * (levels[right] - levels[left])
            nearest = left if frac < .5 else right
        # Clear column above sampled ground to underside of cap. Bedding and
        # bearing stack adjustments await a dimensional support arrangement.
        column_height = soffit - cap_depth_m
        if column_height <= 0:
            raise ValueError("Site profile leaves no above-ground column below the cap")
        row = samples[nearest]
        supports.append(dict(
            chainage_m=chainage, count=multiplicity, closure_end_support=closure_support,
            trial_column_height_m=column_height, soffit_height_m=soffit,
            source_sample_chainage_m=points[nearest],
            clay_pct=optional_pct(row, "clay_pct"),
            water_occurrence_pct=optional_pct(row, "water_occurrence_pct"),
            water_occurrence_100m_max_pct=optional_pct(row, "water_occurrence_100m_max_pct"),
        ))
    return supports


def priority(row):
    water = row["water_occurrence_pct"]
    nearby = row["water_occurrence_100m_max_pct"]
    clay = row["clay_pct"]
    return (
        water is not None and water >= REPEATED_WATER_PCT,
        water is not None and water > 0,
        water is None,
        water if water is not None else 0,
        nearby is not None and nearby >= REPEATED_WATER_PCT,
        nearby if nearby is not None else 0,
        clay if clay is not None else -1,
        -row["chainage_m"],
    )


def footing_trials(girder, supports, config, piles_by_case):
    """Keep the issued stock screen and independently resize pads for each trial."""
    width = girder["support"]["footing_width_m"]
    if width is None:
        return None
    depth = girder["support"]["footing_depth_m"]
    baseline_pad_volume = width**2 * depth
    profile = sorted(config["pier"]["soil_pressures_kpa"], reverse=True)
    actions = girder["load_case_actions"][girder["governing_bent_load"]]
    counts = dict.fromkeys(str(pressure) for pressure in profile)
    sized = {}
    for name, pressure in zip(CASES, profile, strict=True):
        pile_supports = Counter(piles_by_case[name])
        failures = 0
        unresolved = 0
        added_concrete = 0.
        changed = 0
        maximum_width = width
        for row in supports:
            trial = {**config, "pier": {**config["pier"], "column_height_m": row["trial_column_height_m"]}}
            fixed = family_comparison.support(actions, girder["shared_pier"], pressure, trial,
                                              fixed_footing_width_m=width)
            if fixed["foundation_hold"] is None:
                continue
            failures += row["count"]
            shallow_count = row["count"] - pile_supports[row["chainage_m"]]
            if shallow_count == 0:
                continue
            resized = family_comparison.support(actions, girder["shared_pier"], pressure, trial)
            if resized["foundation_hold"] or resized["independent_footings_clear"] is False:
                unresolved += shallow_count
                continue
            changed += shallow_count
            new_width = resized["footing_width_m"]
            new_volume = new_width**2 * resized["footing_depth_m"]
            added_concrete += shallow_count * max(new_volume - baseline_pad_volume, 0)
            maximum_width = max(maximum_width, new_width)
        counts[str(pressure)] = failures
        sized[name] = dict(assumed_bearing_kpa=pressure, supports_enlarged=changed,
                           supports_with_pile_allowance=len(piles_by_case[name]),
                           maximum_trial_footing_width_m=maximum_width,
                           extra_pad_concrete_m3=added_concrete,
                           unresolved_supports=unresolved)
    return dict(
        failed_support_count_by_assumed_bearing_kpa=counts,
        fixed_footing_width_m=width,
        resized_footings=sized,
        scope="Independent shallow bearing sensitivities at the governing bent load and DEM-profile height. "
              "Failed fixed pads are resized at the supports without a shaft allowance. Trial bearing pressures are "
              "separate inputs and do not come from mapped clay or water.",
    )


def closure_unit_prices(girder):
    if not girder["closure_bay_m"]:
        return dict.fromkeys(CASES, 0)
    standard = girder["standard_only_cost_cases"]
    bays = girder["full_standard_bays"]
    rates = {}
    for name in CASES:
        if not standard or not bays or standard[name]["installed_usd"] is None:
            rates[name] = None
        else:
            parts = standard[name]["installed_breakdown_usd"]
            rates[name] = sum(value for key, value in parts.items()
                              if key not in {"forms", "common_elevated_scope"}) / bays
    return rates


def evaluate(profile, girder):
    """Price conditional incremental site work for the scaled civil stock order."""
    profile_body = {key: value for key, value in profile.items()
                    if key not in {"site_profile_id", "alignment_input"}}
    if profile.get("site_profile_id") != airport_alignment.identity(profile_body):
        raise ValueError("Site profile identity does not match its inputs")
    config = read_rates(CIVIL_CONCEPT)
    civil = read_rates(CIVIL_RATES)["civil"]
    works = read_rates(AIRPORT_RATES)
    exchange = read_rates(MARKET)["currency"]["iqd_per_usd"]
    ground, material = works["ground"], works["materials"]
    supports = support_samples(profile, girder, girder["support"]["cap_depth_m"])
    counts = girder["supports"]
    reference_height = config["pier"]["column_height_m"]
    # These widths are the same as those used by family_comparison.support().
    column_width = 1.4 if girder["shared_pier"] else config["pier"]["column_width_m"]
    taller = sum(max(row["trial_column_height_m"] - reference_height, 0) * row["count"]
                 for row in supports) * column_width**2
    reduce = sum(max(reference_height - row["trial_column_height_m"], 0) * row["count"]
                 for row in supports) * column_width**2
    baseline_volume = girder["support"]["concrete_m3"]

    water = sum(row["count"] for row in supports
                if row["water_occurrence_pct"] is not None and row["water_occurrence_pct"] >= REPEATED_WATER_PCT)
    any_water = sum(row["count"] for row in supports
                    if row["water_occurrence_pct"] is not None and row["water_occurrence_pct"] > 0)
    adjacent_water = sum(row["count"] for row in supports
                         if row["water_occurrence_100m_max_pct"] is not None
                         and row["water_occurrence_100m_max_pct"] >= REPEATED_WATER_PCT)
    any_adjacent_water = sum(row["count"] for row in supports
                             if row["water_occurrence_100m_max_pct"] is not None
                             and row["water_occurrence_100m_max_pct"] > 0)
    soil_missing = sum(row["count"] for row in supports if row["clay_pct"] is None)
    water_missing = sum(row["count"] for row in supports if row["water_occurrence_pct"] is None)
    ranked = [row["chainage_m"] for row in sorted(supports, key=priority, reverse=True)
              for _ in range(row["count"])]
    # Geographic screening can enlarge the reserve. The percentage floors,
    # shaft diameters/lengths and unit prices remain explicit planning inputs.
    piles_by_case = {
        name: ranked[:max(ceil(counts * ground["affected_support_share"][i]), (0, water, any_water)[i])]
        for i, name in enumerate(CASES)
    }
    footing = footing_trials(girder, supports, config, piles_by_case)
    concrete_material = (civil["cement_t_per_m3"] * material["resistant_cement_iqd_t"]
                         + civil["sand_m3_per_m3"] * material["sand_iqd_m3"]
                         + civil["gravel_m3_per_m3"] * material["crushed_gravel_iqd_m3"]) / exchange
    shaft_material = (ground["cement_t_per_m3"] * material["resistant_cement_iqd_t"]
                      + ground["sand_m3_per_m3"] * material["sand_iqd_m3"]
                      + ground["gravel_m3_per_m3"] * material["crushed_gravel_iqd_m3"]
                      + ground["rebar_t_per_m3"] * material["reinforcing_steel_iqd_t"]) / exchange
    closure_prices = closure_unit_prices(girder)
    cases = {}
    for i, name in enumerate(CASES):
        affected = len(piles_by_case[name])
        shafts = affected * ground["piles_per_affected_support"]
        shaft_volume = shafts * pi * ground["diameter_m"]**2 / 4 * ground["bored_length_m"][i]
        shaft_usd_per_m3 = shaft_material * ground["installed_to_material_factor"][i]
        labour = civil["support_works_usd_each"][i] * (1.25 if girder["shared_pier"] else 1.)
        taller_rate = (None if baseline_volume is None else
                       concrete_material * family_comparison.TRIALS["material_delivery_multiplier"][i]
                       + civil["rebar_t_per_m3"][i] * material["reinforcing_steel_iqd_t"] / exchange
                       + labour / baseline_volume)
        pad_volume = footing["resized_footings"][name]["extra_pad_concrete_m3"] if footing else None
        pad_amount = (None if footing is None or footing["resized_footings"][name]["unresolved_supports"]
                      else pad_volume * taller_rate)
        cases[name] = dict(
            trial_shaft_support_count=affected, trial_shaft_count=shafts,
            trial_shaft_length_m=ground["bored_length_m"][i], trial_shaft_concrete_m3=shaft_volume,
            trial_shaft_concrete_installed_usd_per_m3=shaft_usd_per_m3,
            trial_shaft_support_chainages_m=piles_by_case[name],
            extra_column_rebar_t=taller * civil["rebar_t_per_m3"][i],
            extra_column_installed_usd_per_m3=taller_rate,
            pier_height_usd=None if taller_rate is None else taller * taller_rate,
            extra_shallow_footing_concrete_m3=pad_volume,
            shallow_footing_usd=pad_amount,
            foundation_allowance_usd=shaft_volume * shaft_usd_per_m3,
            closure_allowance_usd=closure_prices[name],
        )

    def lot(quantity, unit, field, basis):
        return dict(quantity=quantity, unit=unit, usd={name: case[field] for name, case in cases.items()}, basis=basis)

    pad_unit = "base scenario additional pad m³"
    pad_quantity = cases["base"]["extra_shallow_footing_concrete_m3"]
    if pad_quantity == 0:
        pad_quantity = max(case["extra_shallow_footing_concrete_m3"] for case in cases.values())
        pad_unit = "maximum scenario additional pad m³"
    lots = {
        "gis-pier-height": lot(taller, "additional column m³", "pier_height_usd",
            "Extra column concrete and bar above the standard 6 m stock datum, with the existing support works "
            "allowance prorated by concrete volume. Retain the standard price where columns are shorter."),
        "gis-shallow-footing": lot(pad_quantity, pad_unit, "shallow_footing_usd",
            "Enlarged pad volume above the standard footing, including steel and existing excavation and "
            "installation rates prorated by concrete volume. Uses independent 250/200/150 kPa shallow trial "
            "assumptions for low/base/high cost. Pile-allowance positions retain the stock pad as a trial cap."),
        "gis-foundation-allowance": lot(cases["base"]["trial_shaft_concrete_m3"], "base scenario shaft m³",
            "foundation_allowance_usd", "Trial shafts below the stock pad retained as a cap. Uses the Airport "
            "ground scenarios and GIS exposure to allocate candidate positions in place of enlarged pads."),
    }
    if girder["closure_bay_m"]:
        lots["gis-end-closure-allowance"] = lot(1, "double-track end closure", "closure_allowance_usd",
            "One comparable standard bay as a cost allowance for the exceptional end closure. Uses the "
            "same stock, installed rates and cost bands, with existing form and common elevated costs excluded.")

    for name, case in cases.items():
        amounts = [entry["usd"][name] for entry in lots.values()]
        case["opening_site_known_subtotal_usd"] = sum(amount for amount in amounts if amount is not None)
        case["opening_site_unpriced_lots"] = [key for key, entry in lots.items() if entry["usd"][name] is None]

    sources = (Path(__file__).resolve(), Path(family_comparison.__file__), CIVIL_CONCEPT,
               AIRPORT_RATES, CIVIL_RATES, MARKET)
    result = dict(
        schema=SCHEMA, alignment_id=profile["alignment_id"], site_profile_id=profile["site_profile_id"],
        civil_physical_id=girder["physical_id"], currency="constant 2026 USD", material_price_basis="2026-10",
        sources={path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in sources},
        support_profile=supports, footing_sensitivity=footing,
        quantities=dict(
            support_locations=len(supports), physical_supports=counts,
            standard_supports=girder["quantities"]["standard_supports"],
            reference_column_height_m=reference_height,
            trial_column_height_min_m=min(row["trial_column_height_m"] for row in supports),
            trial_column_height_max_m=max(row["trial_column_height_m"] for row in supports),
            extra_column_concrete_m3=taller, potential_uncredited_short_column_concrete_m3=reduce,
            supports_with_repeated_historical_water=water, supports_with_any_historical_water=any_water,
            supports_with_repeated_water_within_100m=adjacent_water,
            supports_with_any_historical_water_within_100m=any_adjacent_water,
            supports_without_clay_value=soil_missing, supports_without_water_value=water_missing,
            historical_water_priority_threshold_pct=REPEATED_WATER_PCT,
            closure_route_m=girder["closure_bay_m"]),
        cases=cases, lots=lots,
        excluded_scope=[
            "Ordinary drainage, elevated works, standard support works, bearing upkeep and renewals remain in existing civil lots.",
            "Water occurrence shows historical surface water in sampled pixels. Groundwater, flood depth, drainage design and scour remain outside these additions.",
            "Clay percentage is a shallow regional proxy. Stratigraphy, compressibility, seismic response, pile design and foundation acceptance require their own evidence.",
            "The closure allowance leaves permanent geometry, its construction sequence, exceptional crossings and route utilities open.",
            "Site-specific upkeep, renewals, delivery delay and owner risk remain outside the site increments.",
        ],
    )
    result["evaluation_id"] = _id(result)
    return result
