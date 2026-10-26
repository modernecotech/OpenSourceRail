"""Counted glazing alternatives; no window assembly is released by these screens.

The retained glass reference is 6 mm *total* glass with 0.76 mm PVB, not
two 6 mm sheets. Door panes belong to this ledger, never to door leaf stock.
Plate calculations are uniform-pressure, simply-supported, small-deflection
research fixtures. They exclude nonlinear membrane action, frames, joints,
creep and impact. An out-of-domain linear answer is not a physical failure or
an approved window. All records preserve the outstanding installed inventory.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path


SCHEMA = "osr.comfort-glazing/v1"
EVALUATOR_VERSION = "navier-laminate-bounds-v1"
PARENT_REVISION = "bf5ce225683fe4d3eb048fa5d96cb2e0dd2041b6"
PRESSURES_PA = (500.0, 1500.0)
PC_DENSITY_KG_M3 = 1200.0
PC_E_PA = 340_000.0 * 6894.757293168
PC_NU = 0.38
PC_EXPANSION_PER_K = 3.75e-5 * 1.8
GLASS_E_PA = 70e9  # Declared reference hypothesis, not a laminate certificate.
GLASS_NU = 0.22
AL_E_PA = 69e9  # Declared stock hypothesis; alloy/temper certificates outstanding.
AL_EXPANSION_PER_K = 23e-6

SOURCES = {
    "plaskolite-tuffak-tg": {
        "url": "https://plaskolite.com/docs/default-source/pds/pds183_tuf_tg.pdf",
        "sha256": "8d88a7a65aeca3677096f0803caec499daf152261db29da0692d1a4100bee15f",
        "retrieved_utc_date": "2026-10-26",
        "manufacturer_document": "PDS183_TUF_TG, 012023, pages 1-2",
        "role": "Named hard-coated rail polycarbonate, typical material properties",
        "scope": (
            "Manufacturer lists 0.236/0.250 inch sheets in dual-glazed systems "
            "and 0.460 inch monolithic rail glazing. Those system claims do not "
            "qualify this proposed 6/8/12 mm assembly or an Iraqi installation. "
            "Published properties are typical, explicitly not specifications."
        ),
    },
    "sabic-rail-product-family": {
        "url": "https://ff.sabic.eu/uploads/resources/1345453513-13350349-SABIC-SFS-692_Solid-Sheet-Brochure-English.pdf",
        "manufacturer_document": "SABIC SFS-692 Solid Sheet brochure, page 12",
        "role": "Alternative coated rail grade family; not the calculated material",
        "scope": (
            "LEXAN FRA460 is described for single-glazed rail applications; "
            "FRA25C/FRA236C for dual-glazed component systems. No density, "
            "modulus, solar factor or certification is transferred between grades."
        ),
    },
    "retained-glass-takeoff": {
        "repository_revision": PARENT_REVISION,
        "path": "engineering/vehicle_optimisation/equipment.py::_glazing",
        "role": "Exact retained glass/PVB, retention, seal and bond quantities",
        "scope": "Counted stock, not a certified complete installed window",
    },
}


def _hash(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


MATERIAL_DATA_ID = _hash({
    "sources": SOURCES,
    "PC_density_kg_m3": PC_DENSITY_KG_M3,
    "PC_E_Pa": PC_E_PA,
    "PC_nu": PC_NU,
    "PC_expansion_per_K": PC_EXPANSION_PER_K,
    "reference_hypotheses": {"glass_E_Pa": GLASS_E_PA, "glass_nu": GLASS_NU,
                             "aluminium_E_Pa": AL_E_PA},
})


def _positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return float(value)


def _doors(value):
    if isinstance(value, bool) or not isinstance(value, int) or value not in (2, 3, 4):
        raise ValueError("doors_total must be the explicit total 2, 3 or 4 per car")
    return value


def _stock(stock_id, volume_m3_each, density_kg_m3, quantity=1, **geometry):
    return {
        "id": stock_id, "volume_m3_each": volume_m3_each,
        "density_kg_m3": density_kg_m3, "quantity": quantity,
        "total_mass_kg": volume_m3_each * density_kg_m3 * quantity,
        **geometry,
    }


def plate_center(a_m, b_m, pressure_Pa, rigidity_Nm, poisson_ratio=PC_NU, odd_terms=31):
    """Navier sum for a uniformly loaded, simply supported rectangular plate.

    Expanding q in odd double-sine terms gives Wmn = 16 q /
    (pi**6 D m n [(m/a)**2 + (n/b)**2]**2). Derivatives provide
    centre moments per unit width. The moments are not local peak stresses.
    """
    a = _positive(a_m, "a_m")
    b = _positive(b_m, "b_m")
    q = _positive(pressure_Pa, "pressure_Pa")
    D = _positive(rigidity_Nm, "rigidity_Nm")
    if not math.isfinite(poisson_ratio) or not -1 < poisson_ratio < 0.5:
        raise ValueError("poisson_ratio outside isotropic elastic domain")
    if isinstance(odd_terms, bool) or not isinstance(odd_terms, int) or not 1 <= odd_terms <= 101:
        raise ValueError("odd_terms must be an integer from 1 to 101")
    displacements, moments_x, moments_y = [], [], []
    for mi in range(odd_terms):
        m = 2 * mi + 1
        for ni in range(odd_terms):
            n = 2 * ni + 1
            sign = -1.0 if (mi + ni) % 2 else 1.0
            ax, by = (m / a) ** 2, (n / b) ** 2
            term = sign / (m * n * (ax + by) ** 2)
            displacements.append(term)
            moments_x.append(term * (ax + poisson_ratio * by))
            moments_y.append(term * (by + poisson_ratio * ax))
    return {
        "centre_deflection_m": 16 * q * math.fsum(displacements) / (math.pi**6 * D),
        "centre_moment_x_Nm_per_m": 16 * q * math.fsum(moments_x) / math.pi**4,
        "centre_moment_y_Nm_per_m": 16 * q * math.fsum(moments_y) / math.pi**4,
        "odd_terms_each_direction": odd_terms,
    }


def laminate_rigidity_bounds():
    """Glass-only limits for two 3 mm skins, with no PVB stiffness credit.

    Uncoupled skins share deflection but transfer no interlayer shear. The
    fully coupled upper rigidity assumes perfect shear transfer. Actual PVB
    time/temperature/shear behaviour and edge fixity are not established.
    """
    t, gap = 0.003, 0.00076
    z = (t + gap) / 2
    uncoupled_I = 2 * t**3 / 12
    coupled_I = 2 * (t**3 / 12 + t * z**2)
    return {
        "uncoupled_Nm": GLASS_E_PA * uncoupled_I / (1 - GLASS_NU**2),
        "fully_coupled_Nm": GLASS_E_PA * coupled_I / (1 - GLASS_NU**2),
        "basis": "Two 3 mm glass skins; 0.76 mm PVB; declared E=70 GPa, nu=0.22",
        "actual_laminate_rigidity_Nm": None,
    }


def equal_stiffness_pc_thickness_bounds_m():
    bounds = laminate_rigidity_bounds()
    return {
        "uncoupled_glass_equivalent": (12 * (1 - PC_NU**2) * bounds["uncoupled_Nm"] / PC_E_PA) ** (1 / 3),
        "fully_coupled_glass_equivalent": (12 * (1 - PC_NU**2) * bounds["fully_coupled_Nm"] / PC_E_PA) ** (1 / 3),
        "basis": "Equal panel span and boundary conditions; typical room-temperature PC E only",
    }


def _sheet_screen(a, b, pressure, D, nu, thickness):
    fine = plate_center(a, b, pressure, D, nu, 31)
    coarse = plate_center(a, b, pressure, D, nu, 15)
    w = fine["centre_deflection_m"]
    domain = w / thickness <= 0.5
    fine.update({
        "panel_size_m": [a, b], "pressure_Pa": pressure,
        "rigidity_Nm": D, "w_over_thickness": w / thickness,
        "series_deflection_relative_change": abs(w - coarse["centre_deflection_m"]) / abs(w),
        "small_deflection_domain": domain,
        "numerical_validity": "valid_linear_fixture" if domain else "outside_small_deflection_domain",
        "declared_target_5mm_screen": ("pass" if w <= 0.005 else "fail") if domain else "unknown",
        "declared_target_25mm_screen": ("pass" if w <= 0.025 else "fail") if domain else "unknown",
        "centre_stress_Pa_if_monolithic": 6 * max(abs(fine["centre_moment_x_Nm_per_m"]),
                                                abs(fine["centre_moment_y_Nm_per_m"])) / thickness**2,
        "strength_allowable_Pa": None,
        "strength_screen": "unknown",
    })
    return fine


def _mullion_definition(partition):
    # 80 mm depth normal to window; 40 mm face; 3 mm wall. No frame strength credit.
    section = {"depth_m": 0.08, "width_m": 0.04, "wall_m": 0.003}
    members = []
    if partition in ("halves", "quarters", "sixths"):
        members.append({"axis": "vertical", "length_m": 1.5, "quantity": 8,
                        "tributary_width_m": 1.0})
    if partition in ("quarters", "sixths"):
        rows = 2 if partition == "quarters" else 3
        members.append({"axis": "horizontal", "length_m": 1.0, "quantity": 16 * (rows - 1),
                        "tributary_width_m": 1.5 / rows})
    return {"section": section, "members": members,
            "connections_qualified": False, "installed_frame_capacity_N": None}


def _mullion_screen(definition, pressure):
    s = definition["section"]
    d, b, t = s["depth_m"], s["width_m"], s["wall_m"]
    I = (b * d**3 - (b - 2 * t) * (d - 2 * t)**3) / 12
    rows = []
    for member in definition["members"]:
        L = member["length_m"]
        q = pressure * member["tributary_width_m"]
        moment = q * L**2 / 8
        rows.append({
            **member, "pressure_Pa": pressure, "line_load_N_m": q,
            "I_normal_m4": I,
            "simply_supported_deflection_m": 5 * q * L**4 / (384 * AL_E_PA * I),
            "maximum_bending_stress_Pa": moment * d / (2 * I),
            "joint_capacity_N": None, "assembled_grid_screen": "unknown",
        })
    return rows


def _evaluate_definition(definition, pressures=PRESSURES_PA):
    material = definition["material"]
    a, b = definition["fixed_window_size_m"]
    bounds = laminate_rigidity_bounds()
    rows = []
    if material == "laminated-glass":
        rigidities = [("uncoupled", bounds["uncoupled_Nm"]),
                      ("fully_coupled", bounds["fully_coupled_Nm"])]
        nu, thickness = GLASS_NU, 0.00676
    else:
        thickness = definition["sheet_thickness_m"]
        rigidities = [("typical_PC_room_temperature", PC_E_PA * thickness**3 / (12 * (1 - PC_NU**2)))]
        nu = PC_NU
    for pressure in pressures:
        _positive(pressure, "pressure_Pa")
        for model, D in rigidities:
            fixed = _sheet_screen(a, b, pressure, D, nu, thickness)
            door = _sheet_screen(0.5, 1.0, pressure, D, nu, thickness)
            if material == "laminated-glass":
                fixed["centre_stress_Pa_if_monolithic"] = None
                door["centre_stress_Pa_if_monolithic"] = None
            rows.append({"model": model, "pressure_Pa": pressure,
                         "fixed_panel": fixed, "door_panel": door,
                         "mullions": _mullion_screen(definition["mullions"], pressure)})
    expansion = None
    if material != "laminated-glass":
        expansion = {
            "declared_temperature_change_K": 60.0,
            "fixed_panel_free_expansion_m": [L * PC_EXPANSION_PER_K * 60 for L in (a, b)],
            "relative_to_aluminium_m": [L * (PC_EXPANSION_PER_K - AL_EXPANSION_PER_K) * 60 for L in (a, b)],
            "actual_retention_travel_m": None, "retention_screen": "unknown",
        }
    return {
        "execution": "completed", "evidence_maturity": "analytical_research_fixture",
        "engineering_screen": "unknown", "physical_acceptance": "unqualified",
        "pressures_Pa": list(pressures), "fixtures": rows,
        "thermal_expansion": expansion,
        "equal_stiffness_pc_thickness_bounds_m": equal_stiffness_pc_thickness_bounds_m(),
        "laminated_glass_rigidity_bounds": bounds,
        "limitations": [
            "500/1500 Pa and 5/25 mm targets are declared comparisons, not code requirements",
            "Simply supported linear plates; no nonlinear membrane, impact, frame or local edge analysis",
            "PC modulus versus temperature, sustained creep and actual grade tolerance remain unknown",
            "Mullion fixtures do not establish assembled grid, attachment or body opening capacity",
            "Centre sheet deflection and frame deflection are separate; no combined assembly clearance pass",
        ],
    }


def _definition(doors_total, material, partition, thickness):
    columns, rows = {"full": (1, 1), "halves": (2, 1), "quarters": (2, 2), "sixths": (2, 3)}[partition]
    a, b = 2 / columns, 1.5 / rows
    return {
        "material": material,
        "manufacturer_grade_intent": ("PLASKOLITE TUFFAK TG hard-coated polycarbonate"
                                      if material != "laminated-glass" else "retained glass/PVB reference"),
        "doors_total": doors_total,
        "fixed_gross_area_m2": 24.0,
        "fixed_window_count": 8 * columns * rows,
        "fixed_window_size_m": [a, b],
        "door_window_count": 2 * doors_total,
        "door_window_size_m": [0.5, 1.0],
        "partition": partition, "sheet_thickness_m": thickness,
        "glass_layers_m": [0.003, 0.00076, 0.003] if material == "laminated-glass" else None,
        "mullions": _mullion_definition(partition),
        "retention_stock_cross_section_m2": 0.02 * 0.003,
        "seal_stock_cross_section_m2": 0.00008,
        "bond_stock_cross_section_m2": 0.012 * 0.003,
        "support_intent": "Mullions behind pane boundaries, not substituted for extra transparent area",
    }


def _evaluation_id(glazing_id, source_digest, result):
    return _hash({"physical_definition_id": glazing_id, "material_data_id": MATERIAL_DATA_ID,
                  "evaluator_version": EVALUATOR_VERSION, "source_sha256": source_digest,
                  "evaluation": result})


@lru_cache(maxsize=33)
def _build(doors_total, material, partition, thickness):
    d = _definition(doors_total, material, partition, thickness)
    area, door_area = 24.0 + doors_total, float(doors_total)
    a, b = d["fixed_window_size_m"]
    perimeter = d["fixed_window_count"] * 2 * (a + b) + 2 * doors_total * 3
    if material == "laminated-glass":
        stock = [_stock("glazing/glass", area * 0.006, 2500.0, area_m2=area, thickness_m=0.006),
                 _stock("glazing/PVB", area * 0.00076, 1070.0, area_m2=area, thickness_m=0.00076)]
        slug = "glass-6mm-pvb-0.76mm/full"
    else:
        stock = [_stock("glazing/polycarbonate-sheet", area * thickness, PC_DENSITY_KG_M3,
                        area_m2=area, thickness_m=thickness)]
        slug = f"tuffak-tg-proposal-{thickness * 1000:g}mm/{partition}"
    sheet_mass = math.fsum(p["total_mass_kg"] for p in stock)
    stock.extend([
        _stock("glazing/retention-aluminium", perimeter * 0.020 * 0.003, 2700.0, length_m=perimeter),
        _stock("glazing/EPDM-seal", perimeter * 0.00008, 1200.0, length_m=perimeter),
        _stock("glazing/bond", perimeter * 0.012 * 0.003, 1200.0, length_m=perimeter),
    ])
    s = d["mullions"]["section"]
    section_area = s["depth_m"] * s["width_m"] - (s["depth_m"] - 2 * s["wall_m"]) * (s["width_m"] - 2 * s["wall_m"])
    for member in d["mullions"]["members"]:
        stock.append(_stock("glazing/mullion-" + member["axis"], section_area * member["length_m"],
                            2700.0, member["quantity"], length_m_each=member["length_m"],
                            section_m=s))
    physical = {"schema": SCHEMA, "definition": d, "stock_parts": stock,
                "ancestry": {"revision": PARENT_REVISION, "role": "exact glazing replacement only"}}
    glazing_id = _hash(physical)
    evaluation = _evaluate_definition(d)
    source_digest = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    evaluation_id = _evaluation_id(glazing_id, source_digest, evaluation)
    unknown = [
        {"id": "complete-certified-perimeter-frame-and-corner-joints", "mass_kg": None},
        {"id": "fasteners-clips-tolerances-and-body-attachments", "mass_kg": None},
        {"id": "qualified-pane-emergency-release-and-ventilation-hardware", "mass_kg": None},
        {"id": "actual-solar-control-treatment-and-coating-allowance", "mass_kg": None},
    ]
    if partition != "full":
        unknown.append({"id": "mullion-intersections-and-end-retention", "mass_kg": None})
    baseline_perimeter = 56 + 6 * doors_total
    baseline_mass = area * (0.006 * 2500 + 0.00076 * 1070) + baseline_perimeter * (0.020 * 0.003 * 2700 + 0.00008 * 1200 + 0.012 * 0.003 * 1200)
    counted_mass = math.fsum(p["total_mass_kg"] for p in stock)
    return {
        "schema": SCHEMA, "id": f"{slug}/{doors_total}-doors",
        "name": ("Retained laminated glass" if material == "laminated-glass" else f"Coated rail-PC {thickness * 1000:g} mm, {partition}"),
        "glazing_id": glazing_id, "physical_definition_id": glazing_id,
        "evaluation_id": evaluation_id, "selection_id": None,
        "material_data_id": MATERIAL_DATA_ID, "evaluator_source_sha256": source_digest,
        "evaluator_version": EVALUATOR_VERSION, "sources": deepcopy(SOURCES),
        "physical_definition": physical,
        "doors_total": doors_total, "fixed_area_m2": 24.0, "door_area_m2": door_area,
        "total_area_m2": area, "fixed_window_count": d["fixed_window_count"],
        "fixed_window_size_m": d["fixed_window_size_m"],
        "door_window_count": 2 * doors_total, "door_window_size_m": [0.5, 1.0],
        "retention_perimeter_m": perimeter, "partition": partition,
        "material": material, "sheet_thickness_m": thickness,
        "stock_parts": stock, "known_sheet_mass_kg": sheet_mass,
        "counted_material_mass_kg": counted_mass,
        "same_door_count_glass_reference_kg": baseline_mass,
        "counted_stock_saving_vs_same_door_count_glass_kg": baseline_mass - counted_mass,
        "installed_mass_kg": None, "installed_cost": None, "installed_cg_m": None,
        "unknown_installed_inventory": unknown,
        "actual_solar_factor_g": None, "actual_U_W_m2K": None,
        "solar_factor_g": None, "U_W_m2K": None,
        "thermal_sensitivities": [
            {"id": "hypothetical-strong-solar-control", "solar_factor_g": 0.35, "U_W_m2K": 5.7},
            {"id": "retained-glass-comparison-only", "solar_factor_g": 0.55, "U_W_m2K": 5.7},
            {"id": "hypothetical-weak-solar-control", "solar_factor_g": 0.75, "U_W_m2K": 5.7},
        ],
        "thermal_basis": (
            "Declared sensitivity values, not product properties; no glass solar factor "
            "or U-value is assigned to PC. Tint/light transmission is not solar g."
        ),
        "manufacturer_evidence": {
            "named_rail_product": material != "laminated-glass",
            "PC_typical_density_kg_m3": PC_DENSITY_KG_M3,
            "PC_typical_E_Pa": PC_E_PA, "PC_typical_nu": PC_NU,
            "PC_typical_expansion_per_K": PC_EXPANSION_PER_K,
            "hard_coating_documented": material != "laminated-glass",
            "abrasion_and_weathering_evidence": "Manufacturer typical tests; assembly qualification outstanding",
            "supplier_listed_nominal_thicknesses_m": [0.0059944, 0.00635, 0.011684],
            "exact_proposed_thickness_and_tolerance_confirmed": False,
            "published_test_claim_transferred_to_this_assembly": False,
        },
        "evaluation": evaluation,
        "opening_windows": False,
        "structural_participation": "No carbody stiffness credit; window and local support loads only",
        "assembly_function": "Separately retained panes; replacement and emergency release paths require design",
        "egress_basis": "Hard-to-break PC cannot inherit hammer-breakable glass evacuation provisions",
        "qualification_holds": [
            "Exact grade, thickness, coating, solar/UV exposure and cleaning lifecycle",
            "Fire, smoke, toxicity and impact for the complete selected assembly",
            "Retention, local body attachment, seal movement and pressure fatigue",
            "Emergency release, accessible evacuation and stationary ventilation",
            "Hot-weather modulus, creep, acoustic performance and thermal comfort",
        ],
        "configuration_adopted": False, "engineering_accepted": False,
        "physical_accepted": False, "installed_mass_complete": False,
        "comfort_qualified": False, "manufacturing_release": False,
    }


def options(doors_total=2):
    """Eleven physical families for an explicit 2/3/4-door car, as fresh records."""
    doors_total = _doors(doors_total)
    rows = [_build(doors_total, "laminated-glass", "full", 0.00676)]
    rows.extend(_build(doors_total, "coated-polycarbonate", partition, thickness)
                for thickness in (0.006, 0.008, 0.012)
                for partition in ("full", "halves", "quarters"))
    rows.append(_build(doors_total, "coated-polycarbonate", "sixths", 0.012))
    return deepcopy(rows)


def validate(option, doors_total=None):
    """Reject edited takeoffs, mixed door counts and transplanted evaluation data."""
    if not isinstance(option, dict):
        raise ValueError("glazing option must be a generated record")
    try:
        n = _doors(option["doors_total"])
        if doors_total is not None and n != _doors(doors_total):
            raise ValueError("glazing and layout doors_total differ")
        expected = next(c for c in options(n) if c["glazing_id"] == option["glazing_id"])
    except (KeyError, StopIteration, TypeError) as exc:
        raise ValueError("unknown glazing physical definition") from exc
    if option != expected:
        raise ValueError("glazing quantities, physical definition or evaluation identity changed")
    return deepcopy(expected)


def evaluate(option, pressures_Pa=PRESSURES_PA):
    """Re-evaluate a validated physical record; pressure changes only evaluation ID."""
    record = validate(option)
    if not isinstance(pressures_Pa, (list, tuple)) or not 1 <= len(pressures_Pa) <= 8:
        raise ValueError("one to eight positive declared pressures required")
    pressures = tuple(_positive(p, "pressure_Pa") for p in pressures_Pa)
    result = _evaluate_definition(record["physical_definition"]["definition"], pressures)
    return {
        "physical_definition_id": record["physical_definition_id"],
        "glazing_id": record["glazing_id"],
        "evaluation_id": _evaluation_id(record["glazing_id"], record["evaluator_source_sha256"], result),
        "result": result,
    }
