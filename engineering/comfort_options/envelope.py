"""Floor/roof component comparisons, never automatic whole-car mass credits.

New tiled assemblies count skins, foam displaced by edge walls/inserts, edge
closures, bond stock and panel-to-frame fasteners. Skin/core material coupons
and one-metre strip models do not qualify a carbody. Existing primary frames,
magnetic hardpoints and fixed 40/70 kN reactions are preserved as interfaces.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path

from engineering.halbach_scaling import vehicles
from engineering.vehicle_optimisation import equipment
from engineering.ferrite_maglev import candidate_magnetics

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "osr.comfort-envelope-components/v1"
PARENT_REVISION = "bf5ce225683fe4d3eb048fa5d96cb2e0dd2041b6"
STOCK_PATH = "engineering/ferrite_maglev/data/candidate-retained-body-stock.json"
G = 9.80665
LENGTH_M, WIDTH_M = 17.0, 2.65
AREA_M2 = LENGTH_M * WIDTH_M
PANELS_LONG, PANELS_WIDE = 8, 3
PANEL_COUNT = PANELS_LONG * PANELS_WIDE
PANEL_L, PANEL_W = LENGTH_M / PANELS_LONG, WIDTH_M / PANELS_WIDE
FLAGS = dict(configuration_adopted=False, engineering_accepted=False,
             physical_accepted=False, installed_mass_complete=False,
             manufacturing_release=False, global_body_qualified=False)

SOURCES = {
    "diab-core": {
        "url": "https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-may-2026-rev26-si.pdf",
        "sha256": "d4a108dd3be35da9fef378037ddbe92133a7e24b991f5098a3ed0a2882c6e4a4",
        "document": "Divinycell H rev 26 SI, May 2026, pages 1-2",
        "basis": "23 C minimum shear properties; density nominal/range and 20 C conductivity",
        "scope": "Coupon properties; no complete panel, hot-loaded or railway fire qualification",
    },
    "hippe-glass-epoxy": {
        "url": "https://www.hippe.de/en/products/detail/product/ep-gc-202-as",
        "document": "EP GC 202 AS producer sheet/board product data, retrieved 2026-10-26",
        "basis": "Bending modulus minimum 22 GPa; density range 1800-2000 kg/m3",
        "scope": "A named glass-epoxy plate comparator; not properties of an untested infused laminate",
    },
    "hydro-aluminium": {
        "url": equipment.HYDRO_6082,
        "document": "Hydro EN AW-6082 producer data as retained in halbach_scaling/vehicles.py",
        "basis": "Nominal E 70 GPa and density 2710 kg/m3; conservative 69 GPa screen",
        "scope": "No extrusion proof-strength or weld limit is transferred to thin panel skins",
    },
}
CORES = {
    60: dict(id="Divinycell-H60", density_kg_m3=60.0, density_range_kg_m3=[48.0, 67.0],
             shear_modulus_min_Pa=16e6, shear_strength_min_Pa=0.63e6,
             compression_strength_min_Pa=0.7e6, conductivity_W_mK=0.029),
    80: dict(id="Divinycell-H80", density_kg_m3=80.0, density_range_kg_m3=[67.0, 87.0],
             shear_modulus_min_Pa=23e6, shear_strength_min_Pa=0.95e6,
             compression_strength_min_Pa=1.15e6, conductivity_W_mK=0.031),
    100: dict(id="Divinycell-H100", density_kg_m3=100.0, density_range_kg_m3=[90.0, 115.0],
              shear_modulus_min_Pa=28e6, shear_strength_min_Pa=1.4e6,
              compression_strength_min_Pa=1.65e6, conductivity_W_mK=0.033),
}
ROLES = {
    "floor": dict(source_role="panel-floor", skin_m=0.00225, core_m=0.060,
                  core_density=100, bond_m_total=0.001, counted_reference_kg=700.5275,
                  pressures_Pa=[2000.0, 5000.0], nominal_support_span_m=1.0),
    "roof": dict(source_role="panel-roof", skin_m=0.002, core_m=0.040,
                 core_density=80, bond_m_total=0.0007, counted_reference_kg=518.075,
                 pressures_Pa=[750.0, 1500.0], nominal_support_span_m=2.125),
}


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return float(value)


def _stock(part_id, volume, density, quantity=1, **geometry):
    if volume < 0 or not math.isfinite(volume):
        raise ValueError("nonnegative finite stock volume required")
    return dict(id=part_id, volume_m3_each=volume, density_kg_m3=density, quantity=quantity,
                total_mass_kg=volume * density * quantity, **geometry)


def source_inputs(root=ROOT):
    """Bind the data and actual imported evaluators, refusing mixed source trees."""
    root = Path(root).resolve()
    result = {STOCK_PATH: hashlib.sha256((root / STOCK_PATH).read_bytes()).hexdigest()}
    for module in (vehicles, equipment, candidate_magnetics):
        path = Path(module.__file__).resolve()
        name = path.relative_to(path.parents[2]).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError("executing and retained envelope dependency differ: " + name)
        result[name] = digest
    result["engineering/comfort_options/envelope.py"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


def _retained(root, role):
    raw = json.loads((Path(root) / STOCK_PATH).read_text())
    parts = [p for p in raw["parts"] if p["role"] == ROLES[role]["source_role"]]
    if len(parts) != 4 or any(p["kind"] != "box" or p.get("holes") for p in parts):
        raise ValueError("audit changed retained panel topology before comparing")
    mass = math.fsum(math.prod(p["size_m"]) * p["density_assumption_kg_m3"] for p in parts)
    r = ROLES[role]
    expected = [(r["skin_m"], 1900.0), (r["core_m"], float(r["core_density"])),
                (r["skin_m"], 1900.0), (r["bond_m_total"], 1000.0)]
    for p, (t, density) in zip(parts, expected):
        if p["size_m"] != [LENGTH_M, WIDTH_M, t] or p["density_assumption_kg_m3"] != density:
            raise ValueError("retained panel dimensions/material account changed")
    if not math.isclose(mass, r["counted_reference_kg"], abs_tol=1e-7):
        raise ValueError("retained panel mass account changed")
    return parts, mass


def sandwich_strip(skin_m, core_m, face_E_Pa, core_G_Pa, span_m, pressure_Pa):
    """One-metre-wide simply-supported beam, with bending and core shear.

    Faces carry bending; ignoring core bending is conservative in this fixture.
    Core shear is uniform with area b*c and correction 1. Face wrinkling, bond,
    indentation, orthotropy and joint continuity are separate unresolved checks.
    """
    t, c, E, Gc, L, p = (_positive(v, n) for v, n in zip(
        (skin_m, core_m, face_E_Pa, core_G_Pa, span_m, pressure_Pa),
        ("skin", "core", "face E", "core G", "span", "pressure")))
    width = 1.0
    I = 2 * width * (t**3 / 12 + t * ((c + t) / 2)**2)
    EI = E * I
    q = p * width
    moment, shear = q * L**2 / 8, q * L / 2
    bending = 5 * q * L**4 / (384 * EI)
    shear_deflection = q * L**2 / (8 * Gc * width * c)
    displacement = bending + shear_deflection
    domain = displacement / (c + 2 * t) <= 0.5 and displacement / L <= 0.02
    return dict(span_m=L, total_pressure_Pa=p, one_metre_width=True,
                face_second_moment_m4=I, EI_Nm2=EI, face_EA_N=2 * E * t * width,
                face_peak_bending_stress_Pa=moment * (c / 2 + t) / I,
                core_peak_shear_Pa=shear / (width * c), bending_deflection_m=bending,
                shear_deflection_m=shear_deflection, total_deflection_m=displacement,
                numerical_validity="valid_linear_fixture" if domain else "outside_small_deflection_domain",
                declared_L_over_300_target_m=L / 300,
                deflection_necessary_screen=("pass" if displacement <= L / 300 else "fail") if domain else "unknown",
                actual_face_strength_Pa=None, face_strength_screen="unknown",
                face_wrinkling_bond_point_load_and_fixing_screen="unknown")


def _new_stock(role, skin_kind, t, core_density):
    r = ROLES[role]
    c = r["core_m"]
    face_density = 1900.0 if skin_kind == "glass-epoxy" else 2710.0
    # Four inserts in each panel are for panel-to-frame attachment, not seats or magnets.
    insert_count = PANEL_COUNT * 4
    wall_t, lap, insert_outer, insert_inner = 0.0015, 0.020, 0.020, 0.008
    inner_area = (PANEL_L - 2 * wall_t) * (PANEL_W - 2 * wall_t)
    edge_wall_area = PANEL_L * PANEL_W - inner_area
    flange_area = PANEL_L * PANEL_W - (PANEL_L - 2 * lap) * (PANEL_W - 2 * lap)
    foam_each = inner_area * c - 4 * math.pi * insert_outer**2 / 4 * c
    if foam_each <= 0:
        raise ValueError("edge/insert detail leaves no foam")
    parts = [
        _stock("skin/top", PANEL_L * PANEL_W * t, face_density, PANEL_COUNT,
               size_m=[PANEL_L, PANEL_W, t], material=skin_kind),
        _stock("skin/bottom", PANEL_L * PANEL_W * t, face_density, PANEL_COUNT,
               size_m=[PANEL_L, PANEL_W, t], material=skin_kind),
        _stock("core/trimmed-foam", foam_each, float(core_density), PANEL_COUNT,
               core_thickness_m=c, displaced_edge_wall_volume_m3_each=edge_wall_area * c,
               displaced_insert_volume_m3_each=4 * math.pi * insert_outer**2 / 4 * c),
        _stock("bond/skin-core-total", AREA_M2 * r["bond_m_total"], 1000.0,
               total_bond_thickness_m=r["bond_m_total"], basis="Retained gross bond-film stock; exact distribution unqualified"),
        _stock("edge/GFRP-vertical-ring", edge_wall_area * c, 1900.0, PANEL_COUNT,
               wall_m=wall_t, core_thickness_m=c),
        _stock("edge/GFRP-lap-rings", flange_area * wall_t, 1900.0, 2 * PANEL_COUNT,
               lap_width_m=lap, thickness_m=wall_t, basis="External face laps; local thickness growth requires fit check"),
        _stock("bond/edge-lap", flange_area * 0.0002, 1200.0, 2 * PANEL_COUNT, thickness_m=0.0002),
        _stock("attachment/aluminium-sleeve", math.pi * (insert_outer**2 - insert_inner**2) / 4 * (c + 2 * t),
               2710.0, insert_count, outer_diameter_m=insert_outer, inner_diameter_m=insert_inner, length_m=c + 2 * t),
        _stock("attachment/steel-load-spreader", math.pi * (0.030**2 - 0.009**2) / 4 * 0.002,
               7850.0, 2 * insert_count, thickness_m=0.002),
        _stock("attachment/M6-shank", math.pi * 0.006**2 / 4 * (c + 2 * t + 0.012), 7850.0, insert_count,
               diameter_m=0.006, length_m=c + 2 * t + 0.012),
        _stock("attachment/M6-head-nut-envelope", math.pi * 0.011**2 / 4 * 0.009, 7850.0, insert_count,
               basis="Machining stock envelope; holes not credited, fastener grade unqualified"),
    ]
    return parts


def _frame_context(root, source_parts):
    rows = []
    for name, force in (("6082-six-cell-deep-40kn", 40000.0), ("6082-six-cell-deep-70kn", 70000.0)):
        frame = vehicles._frame(name, Path(root))
        if frame["design_force_N_per_module"] != force:
            raise ValueError("fixed magnetic frame load changed")
        rows.append(dict(id=name, frame_id=frame["frame_id"],
                         counted_material_mass_kg=frame["counted_material_mass_kg"],
                         ancestor_frame_counted_kg=frame["removed_counted_frame_kg"],
                         ancestor_part_ids=frame["removed_stock_ids"],
                         generated_stock_ids=[p["id"] for p in frame["stock_parts"]],
                         generated_stock_sha256=_hash(frame["stock_parts"]),
                         engineering_member_count=frame["engineering_member_count"],
                         fixed_magnetic_force_N_per_module=force,
                         scope="Existing independent frame alternative; no panel/frame saving credited here",
                         global_body_qualified=False, actual_bracing_qualified=False,
                         installed_mass_kg=None))
    return dict(aluminium_frame_comparisons=rows,
                preserved_magnetic_roles=["magnetic-load-path", "hardpoints", "fasteners"],
                retained_body_source_part_ids_sha256=_hash(sorted(p["id"] for p in source_parts)),
                lower_passenger_count_reduces_fixed_magnetic_design_load=False,
                explanation="Aluminium density alone is insufficient: match stiffness, local reactions, joints and bracing. Current 40 kN stock is about 3.19 kg below the ancestor frame; the 70 kN stock is heavier. Neither is a released whole body.")


def _evaluate(role, t, core_density, face_E, mass, reference):
    r = ROLES[role]
    core = CORES[core_density]
    dead = mass * G / AREA_M2
    rows = []
    for span in (0.5, 1.0, 2.125):
        for imposed in r["pressures_Pa"]:
            f = sandwich_strip(t, r["core_m"], face_E, core["shear_modulus_min_Pa"], span, imposed + dead)
            allowable = core["shear_strength_min_Pa"] / 2
            f.update(imposed_pressure_Pa=imposed, counted_stock_dead_pressure_Pa=dead,
                     core_shear_comparison_allowable_Pa=allowable,
                     core_shear_factor_hypothesis=2.0,
                     core_shear_necessary_screen="pass" if f["core_peak_shear_Pa"] <= allowable else "fail")
            rows.append(f)
    section = sandwich_strip(t, r["core_m"], face_E, core["shear_modulus_min_Pa"], 1, 1)
    old = sandwich_strip(r["skin_m"], r["core_m"], 20e9,
                         CORES[r["core_density"]]["shear_modulus_min_Pa"], 1, 1)
    global_strip = sandwich_strip(t, r["core_m"], face_E, core["shear_modulus_min_Pa"],
                                  17.0, max(r["pressures_Pa"]) + dead)
    return dict(execution="completed", evidence_maturity="analytical_component_fixture",
                engineering_screen="unknown", physical_acceptance="unqualified",
                local_fixtures=rows,
                nominal_existing_support_span_m=r["nominal_support_span_m"],
                nominal_support_span_is_qualified=False,
                global_stiffness_comparison=dict(
                    face_EA_ratio_to_retained=section["face_EA_N"] / old["face_EA_N"],
                    local_EI_ratio_to_retained=section["EI_Nm2"] / old["EI_Nm2"],
                    continuous_section_stiffness_necessary_screen="pass" if (
                        section["face_EA_N"] >= old["face_EA_N"] and section["EI_Nm2"] >= old["EI_Nm2"]) else "fail",
                    joint_continuity_qualified=False, whole_body_shear_torsion_buckling_fatigue_screen="unknown",
                    panel_alone_17m_strip=global_strip,
                    basis="Same core depth; reference GFRP E=20 GPa hypothesis. Component stiffness continuity is necessary for direct substitution, not proof of body behaviour."),
                thermal=dict(core_only_R_m2K_W=r["core_m"] / core["conductivity_W_mK"],
                             complete_assembly_U_W_m2K=None, solar_absorptance=None,
                             material_continuous_core_temperature_limit_C=70.0,
                             actual_core_temperature_C=None, hot_loaded_property_map=None,
                             declared_80C_core_case="outside manufacturer continuous temperature range",
                             thermal_bridge_and_HVAC_coupling="unknown"),
                reference_fixture=reference,
                limitations=["Uniform imposed floor/roof pressures and L/300 are declared research cases, not approval limits",
                             "No seat-leg, wheelchair, HVAC, solar, magnet, maintenance or impact point-load qualification",
                             "Skin wrinkling, bond peel, corrosion, fire and actual fixings remain unknown",
                             "Tiled-panel continuity and global carbody modal/coupler/crash load paths require a new compatible body model"])


@lru_cache(maxsize=4)
def _options(root_name, source_key):
    root = Path(root_name)
    inputs = json.loads(source_key)
    raw = json.loads((root / STOCK_PATH).read_text())
    context = _frame_context(root, raw["parts"])
    records = []
    for role, r in ROLES.items():
        retained, reference_mass = _retained(root, role)
        variants = [("retained", r["skin_m"], r["core_density"])]
        core_choices = (80, 100) if role == "floor" else (60, 80)
        variants += [(kind, t, density) for kind, ts in (("glass-epoxy", (0.001, 0.0015)),
                                                      ("aluminium", (0.0006, 0.0009)))
                     for t in ts for density in core_choices]
        for kind, t, density in variants:
            is_reference = kind == "retained"
            parts = ([_stock(p["id"], math.prod(p["size_m"]), p["density_assumption_kg_m3"],
                             size_m=p["size_m"], at_m=p["at_m"], material=p["material"]) for p in retained]
                     if is_reference else _new_stock(role, kind, t, density))
            mass = math.fsum(p["total_mass_kg"] for p in parts)
            face_E = 20e9 if is_reference else 22e9 if kind == "glass-epoxy" else 69e9
            definition = dict(role=role, skin_kind=kind, skin_m=t, core_m=r["core_m"],
                              core_grade_intent="generic retained core" if is_reference else CORES[density]["id"],
                              nominal_core_density_kg_m3=density, gross_area_m2=AREA_M2,
                              panel_count=1 if is_reference else PANEL_COUNT,
                              panel_size_m=[LENGTH_M, WIDTH_M] if is_reference else [PANEL_L, PANEL_W],
                              stock_parts=parts, ancestor_part_ids=[p["id"] for p in retained],
                              retained_body_stock_sha256=inputs[STOCK_PATH])
            physical_id = _hash(definition)
            evaluation = _evaluate(role, t, density, face_E, mass, is_reference)
            nominal = [f for f in evaluation["local_fixtures"]
                       if f["span_m"] == r["nominal_support_span_m"]]
            screens = [evaluation["global_stiffness_comparison"]["continuous_section_stiffness_necessary_screen"]]
            screens += [f[k] for f in nominal for k in ("deflection_necessary_screen", "core_shear_necessary_screen")]
            necessary = "fail" if "fail" in screens else "unknown" if "unknown" in screens else "pass"
            evaluation_id = _hash(dict(physical_definition_id=physical_id, source_inputs=inputs,
                                       material_sources=SOURCES, face_E_hypothesis_Pa=face_E, result=evaluation))
            records.append(dict(
                schema=SCHEMA, id=f"{role}/{kind}/{t * 1000:g}mm/core-{density}",
                role=role, component=role,
                name=f"{role.title()}: {kind}, {t * 1000:g} mm faces, core {density}",
                envelope_id=physical_id, physical_definition_id=physical_id,
                evaluation_id=evaluation_id, selection_id=None,
                source_root=str(root), source_inputs=inputs, sources=deepcopy(SOURCES),
                parent_revision=PARENT_REVISION, physical_definition=definition,
                replacement_scope_part_ids=[p["id"] for p in retained],
                stock_parts=parts, counted_material_mass_kg=mass, counted_mass_kg=mass,
                mass_basis=f"per car {role} assembly",
                necessary_screen=necessary,
                necessary_screen_scope="Nominal-span strip deflection/core shear and continuous-section EA/EI only; point loads, joints and complete body unknown",
                retained_panel_counted_material_mass_kg=reference_mass,
                conditional_counted_stock_saving_kg=reference_mass - mass,
                compatible_complete_body_record_id=None, applied_to_current_parent=False,
                mass_saving_credited_to_current_parent=False,
                installed_mass_kg=None, installed_cost=None, installed_CG_m=None, installed_inertia_kg_m2=None,
                face_modulus_hypothesis_Pa=face_E,
                face_modulus_basis="Retained hypothesis" if is_reference else "Producer glass-epoxy bending proxy" if kind == "glass-epoxy" else "Conservative producer alloy proxy; thin-skin product unqualified",
                core_properties=deepcopy(CORES[density]),
                core_properties_are_proven_retained_material=False,
                frame_context=deepcopy(context), evaluation=evaluation,
                unknown_installed_inventory=[
                    dict(id="remaining-edge-joints-and-frame-interface-hardware", mass_kg=None),
                    dict(id="qualified-seating-HVAC-and-magnetic-point-load-reinforcement", mass_kg=None),
                    dict(id="fire-smoke-thermal-finish-corrosion-and-wear-layers", mass_kg=None),
                    dict(id="global-continuity-bracing-impact-fatigue-and-repair-details", mass_kg=None)],
                component_only=True, **FLAGS))
    if source_inputs(root) != inputs:
        raise ValueError("envelope sources changed during bounded execution")
    return records


def options(root=ROOT):
    """Eighteen source-bound component alternatives; no current parent mutation."""
    root = Path(root).resolve()
    key = json.dumps(source_inputs(root), sort_keys=True)
    return deepcopy(_options(str(root), key))


def validate(record, root=None):
    """Reproduce a component record, refusing changed quantities or mass credits."""
    if not isinstance(record, dict):
        raise ValueError("generated envelope component required")
    try:
        root = Path(record["source_root"] if root is None else root).resolve()
        inputs = source_inputs(root)
        expected = next(r for r in _options(str(root), json.dumps(inputs, sort_keys=True))
                        if r["physical_definition_id"] == record["physical_definition_id"])
    except (KeyError, StopIteration, TypeError, OSError) as exc:
        raise ValueError("unknown envelope component or missing source") from exc
    if record != expected:
        raise ValueError("envelope identity, quantities, source or component-only scope changed")
    return deepcopy(expected)
