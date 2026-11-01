"""Breadth-first combinations of currently executable body productions.

This registry composes the existing frame, shell and rib productions. It does
not claim curved shells, cellular lattices, organic topology or new material
physics; those require distinct geometry and evaluator adapters.
"""
from itertools import product
import tomllib
from pathlib import Path

from engineering.station_rail.common import digest
from engineering.station_rail import ROOT
from . import design_grammar, material_database, model_cost

PRODUCER = "engineering/design_search/shape_families.py"
CAMPAIGN = "campaigns/breadth-first-shape-portfolio.toml"


def load(root=ROOT):
    root = Path(root)
    value = tomllib.loads((root / CAMPAIGN).read_text())
    if (value.get("schema") != "osr-breadth-first-shape-portfolio/1"
            or value.get("purpose") != "next-experiment"
            or value.get("reference_changes_allowed") is not False
            or value.get("native_dispatch") is not False
            or value.get("integrated_selection") is not False):
        raise ValueError("A bounded non-promoting research portfolio is required")
    axes = value.get("design_axes", {})
    profiles = value.get("profiles", [])
    expected = (len(axes.get("frames", [])) * len(axes.get("shells", []))
        * len(axes.get("rib_layouts", [])) * len(profiles))
    if (len(axes.get("frames", [])) != 2 or len(axes.get("shells", [])) != 3
            or len(axes.get("rib_layouts", [])) != 3 or len(profiles) != 3
            or value.get("maximum_candidates") != expected):
        raise ValueError("Explicit finite composition axes and candidate budget required")
    if len({row.get("id") for row in profiles}) != len(profiles):
        raise ValueError("Unique named shape profiles required")
    for profile in profiles:
        if set(profile) != {"id", "bay_pitch_m", "frame_depth_m", "chord_width_m",
                "chord_height_m", "chord_wall_m", "braced", "integrated_roof",
                "modular_length_m", "skin_thickness_m", "core_thickness_m"}:
            raise ValueError("Complete explicit profile parameter set required")
    return value


def registry(root=ROOT):
    """Return all 18 compatible compositions, retaining existing family names."""
    spec = load(root)
    registry = design_grammar.recipe_registry()
    reverse = {tuple(sorted(row.items())): name for name, row in registry.items()}
    for frame, shell, ribs in product(spec["design_axes"]["frames"],
            spec["design_axes"]["shells"], spec["design_axes"]["rib_layouts"]):
        production = dict(frame=frame, shell=shell, ribs=ribs)
        if tuple(sorted(production.items())) in reverse:
            continue
        name = "composition__" + "__".join((frame, shell, ribs))
        registry = design_grammar.register_recipe(name, production, registry)
        reverse[tuple(sorted(production.items()))] = name
    if len(registry) != 18:
        raise ValueError("The declared morphology matrix must contain 18 distinct productions")
    return registry


def generate(root=ROOT):
    """Generate each frame/shell/rib composition under three shape profiles."""
    root = Path(root)
    spec = load(root)
    baseline = tomllib.loads((root / "engineering/development-baseline.toml").read_text())
    recipes = registry(root)
    original = design_grammar.recipe_registry()
    rows = []
    for family, production in sorted(recipes.items()):
        for profile in spec["profiles"]:
            parameters = design_grammar.parameters()
            parameters["family"] = family
            parameters["length_m"] = float(baseline["vehicle"]["body_length_m"])
            parameters["cars"] = int(baseline["vehicle"]["cars"])
            parameters["width_m"] = float(spec["vehicle_envelope"]["width_m"])
            parameters.update({key: value for key, value in profile.items() if key != "id"})
            candidate = design_grammar.build(parameters, recipes=recipes,
                reason="Breadth-first shape-family and profile comparison")
            if candidate["recipe_registry"][family] != production:
                raise ValueError("Candidate composition differs from its morphology cell")
            if (candidate["parameters"]["length_m"] != float(baseline["vehicle"]["body_length_m"])
                    or candidate["parameters"]["cars"] != int(baseline["vehicle"]["cars"])):
                raise ValueError("Shape portfolio must retain the development envelope and formation")
            rows.append(dict(family=family, profile_id=profile["id"],
                descriptor=dict(frame=production["frame"], shell=production["shell"],
                    ribs=production["ribs"]), candidate=candidate))
    if (len(rows) != spec["maximum_candidates"]
            or len({r["candidate"]["candidate_id"] for r in rows}) != len(rows)):
        raise ValueError("Candidate budget or physical candidate uniqueness differs")
    # Preserve the existing five-name menu; the full matrix is a separate study.
    if design_grammar.recipe_registry() != original:
        raise ValueError("The breadth-first study must not alter the default recipe registry")
    return rows


def sources(root=ROOT):
    root = Path(root)
    names = ("design_grammar", "grammar_geometry", "dfma", "model_cost", "remit",
        "requirement_policy",
        "material_database", "structural_families", "joining_catalogue", "interface_graph",
        "shape_families", "quality_diversity", "design_portfolio")
    result = {"campaigns/breadth-first-shape-portfolio.toml": digest(root / CAMPAIGN)}
    result["engineering/development-baseline.toml"] = digest(root / "engineering/development-baseline.toml")
    result["engineering/station_rail/common.py"] = digest(root / "engineering/station_rail/common.py")
    result.update({f"engineering/design_search/{name}.py": digest(
        root / "engineering/design_search" / f"{name}.py") for name in names})
    result.update(design_grammar._reference_equipment()[2])
    result.update(model_cost.sources(root))
    result.update(material_database.source_map())
    return result
