"""Conditional longitudinal EI models for exact nominal civil section cells.

These are gross linear-elastic beam hypotheses, not section resistance models.
Concrete cracking, shear deformation, bond, local stability and actual installed
load transfer are not established by calculating a transformed section.
"""
from math import fsum, isfinite
from pathlib import Path

from engineering.station_rail.common import digest, identity

from . import civil_shape_geometry as geometry

PRODUCER = "engineering/design_search/civil_section_model.py"
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False,
    configuration_adopted=False, selected_reference_changed=False)


def _sources():
    root = Path(__file__).resolve().parents[2]
    paths = (PRODUCER, "engineering/design_search/civil_shape_geometry.py",
        "engineering/station_rail/common.py")
    return {path: digest(root/path) for path in paths}


def _positive_modulus(value):
    if type(value) not in (int, float):
        return False
    try:
        return isfinite(value) and value > 0
    except OverflowError:
        return False


def models(candidate, moduli_Pa):
    """Return source-bound gross-section hypotheses for the same physical stock.

    Moduli must cover exactly the candidate's declared material registry, even
    when a material has no stock in a particular family. No missing modulus is
    silently replaced by zero. The steel-only hybrid model deliberately omits
    concrete *longitudinal stiffness*, while retaining its complete nominal
    geometric mass. Neither hybrid hypothesis brackets physical performance.
    """
    geometry.validate(candidate)
    quantities = geometry.quantities(candidate)
    if (not isinstance(moduli_Pa, dict)
            or set(moduli_Pa) != set(candidate["materials"])
            or any(not _positive_modulus(value) for value in moduli_Pa.values())):
        raise ValueError("Finite positive moduli with exact declared material coverage required")
    moduli = {key: float(moduli_Pa[key]) for key in sorted(moduli_Pa)}
    source = _sources()
    full_name = ("perfect-bond-uncracked" if candidate["family"] == "hybrid_steel_concrete"
        else "full-section-uncracked")
    hypotheses = [(full_name, None,
        "All nominal section materials share plane sections and perfect longitudinal bond, "
        "with uncracked linear elasticity. Shear deformation, cracking, slip, local stability "
        "and installed load transfer remain unqualified; no resistance or prestress is credited.")]
    if candidate["family"] == "hybrid_steel_concrete":
        hypotheses.insert(0, ("steel-only-longitudinal", {"structural_steel"},
            "Nominal steel plates form longitudinal girders with common vertical curvature. "
            "The concrete deck transfers gravity without credited longitudinal composite action. "
            "Plate continuity, deck load transfer, lateral distribution, shear deformation and "
            "local/lateral stability remain unqualified. All nominal concrete dead mass is retained."))
    result = []
    for name, active_materials, hypothesis in hypotheses:
        cells = []
        for cell in candidate["cells"]:
            sections = []
            mass_per_length = []
            for section in cell["sections"]:
                material = section["material"]
                props = geometry._properties(section["polygon_yz_m"])
                area = props["area_m2"]
                mass_per_length.append(area*candidate["materials"][material]["density_kg_m3"])
                if active_materials is None or material in active_materials:
                    sections.append((section, props, moduli[material]))
            if not sections:
                raise ValueError("A longitudinal stiffness model needs explicit active section stock")
            ea_terms = [modulus*props["area_m2"] for _, props, modulus in sections]
            if any(not isfinite(value) or value <= 0 for value in ea_terms):
                raise ValueError("Finite positive transformed-section axial stiffness required")
            total_ea = fsum(ea_terms)
            neutral = fsum(ea*props["centroid_yz_m"][1]
                for ea, (_, props, _) in zip(ea_terms, sections))/total_ea
            ei = fsum(modulus*(props["I_y_m4"]
                + props["area_m2"]*(props["centroid_yz_m"][1]-neutral)**2)
                for _, props, modulus in sections)
            mass = fsum(mass_per_length)
            if not isfinite(ei) or ei <= 0 or not isfinite(mass) or mass <= 0:
                raise ValueError("Finite positive nominal beam stiffness and mass required")
            fibers = [dict(section_id=section["id"], material=section["material"],
                modulus_Pa=modulus,
                z_min_m=min(point[1] for point in section["polygon_yz_m"]),
                z_max_m=max(point[1] for point in section["polygon_yz_m"]),
                neutral_axis_z_m=neutral) for section, _, modulus in sections]
            cells.append(dict(x_start_m=cell["x_start_m"], x_end_m=cell["x_end_m"],
                EI_Nm2=ei, mass_per_length_kg_m=mass, section_fibers=fibers,
                hypothesis=hypothesis))
        value = dict(schema="osr-civil-longitudinal-section-model/1", name=name,
            candidate_id=candidate["candidate_id"],
            source_quantity_evaluation_id=quantities["evaluation_id"],
            source_sha256=source, moduli_Pa=dict(moduli), cells=cells,
            hypothesis=hypothesis,
            mass_scope="All nominal geometric materials; unresolved installed stock remains unknown",
            resistance_scope="No tensile, compressive, prestress, fatigue or dynamic acceptance",
            complete_installed_mass_kg=None, **FLAGS)
        value["evaluation_id"] = identity(value)
        result.append(value)
    return result
