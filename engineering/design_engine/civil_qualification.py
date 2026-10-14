"""Bounded civil evidence and elastic prestress checks, without site release.

The FHWA examples establish the equations, not applicable project properties or
an adopted railway design standard. Every future parameter keeps its source.
"""

from __future__ import annotations

from datetime import date
import math
import re

from .contracts import fingerprint, identity, number

REFERENCES = {
    "prestress_losses": "https://www.fhwa.dot.gov/bridge/concrete/hif15016.pdf",
    "elastic_shortening": "https://www.fhwa.dot.gov/bridge/lrfd/pscus054.cfm",
    "anchorage_and_friction": "https://www.fhwa.dot.gov/bridge/prefab/if09010/appa.cfm",
    "site_characterization": "https://www.fhwa.dot.gov/engineering/geotech/pubs/nhi16072.pdf",
}
SOURCE_BASES = {"project-measured", "project-design", "published-example", "research-assumption"}


def source(value):
    if not isinstance(value, dict) or set(value) != {"reference", "sha256", "basis"}:
        raise ValueError("source reference, retained SHA-256 and explicit basis required")
    if not isinstance(value["reference"], str) or not value["reference"].strip():
        raise ValueError("nonempty source reference required")
    if not isinstance(value["sha256"], str) or not re.fullmatch("[a-f0-9]{64}", value["sha256"]):
        raise ValueError("controlled source SHA-256 required")
    if value["basis"] not in SOURCE_BASES:
        raise ValueError("explicit project or research source basis required")
    return value


def scalar(row, unit, name, *, minimum=0):
    if not isinstance(row, dict) or set(row) != {"value", "unit", "source"}:
        raise ValueError("source-qualified scalar required for " + name)
    if row["unit"] != unit:
        raise ValueError("explicit SI unit required for " + name)
    source(row["source"])
    return number(row["value"], name, minimum=minimum)


def _scope(bundle, context, schema):
    if bundle.get("schema") != schema:
        raise ValueError("versioned " + schema + " input required")
    actual = identity(bundle["identity"])
    expected = identity(context)
    # Inputs may come from a prior run; all engineering scope must match.
    for key in expected:
        if key != "run_id" and actual[key] != expected[key]:
            raise ValueError("civil evidence scope mismatch: " + key)


def elastic_shortening(groups, *, area_m2, inertia_m4, concrete_modulus_pa, self_weight_moment_nm):
    """Simultaneous straight pretension transfer, compression-positive stress.

    SI groups specify metallic area, pretransfer stress, modulus and signed
    eccentricity. No design allowables or material defaults enter this solve.
    """
    import numpy as np

    area = number(area_m2, "gross area", minimum=1e-12)
    inertia = number(inertia_m4, "gross inertia", minimum=1e-15)
    eci = number(concrete_modulus_pa, "concrete modulus", minimum=1)
    moment = number(self_weight_moment_nm, "self-weight moment", minimum=0)
    if not 1 <= len(groups) <= 128:
        raise ValueError("bounded nonempty simultaneous tendon groups required")
    for row in groups:
        for name in ("metallic_area_m2", "pretransfer_stress_pa", "steel_modulus_pa"):
            number(row[name], name, minimum=1e-12)
        number(row["eccentricity_m"], "eccentricity")
    n = len(groups)
    matrix, rhs = np.eye(n), np.zeros(n)
    for i, pi in enumerate(groups):
        ratio = pi["steel_modulus_pa"] / eci
        for j, pj in enumerate(groups):
            coupling = ratio * pj["metallic_area_m2"] * (1 / area + pi["eccentricity_m"] * pj["eccentricity_m"] / inertia)
            matrix[i, j] += coupling
            rhs[i] += coupling * pj["pretransfer_stress_pa"]
        rhs[i] -= ratio * moment * pi["eccentricity_m"] / inertia
    losses = np.linalg.solve(matrix, rhs)
    if not np.isfinite(losses).all():
        raise ValueError("nonfinite elastic transfer result")
    return losses.tolist()


def foundation_geometry(contract):
    """Investigation extent from actual matrix pile solids, excluding rebar."""
    piles = []
    for part in contract["parts"]:
        if not part["id"].startswith("pile-") or "-rebar-" in part["id"]:
            continue
        primitives = part["manufacturing"]["primitives"]
        if len(primitives) != 1 or primitives[0]["kind"] != "perforated-cylinder" or primitives[0]["axis"] != "z":
            raise ValueError("actual vertical cylindrical matrix pile required")
        primitive = primitives[0]
        x, y, z = part["properties"]["cg_m"]
        radius, length = primitive["radius_m"], primitive["length_m"]
        piles.append(dict(physical_part_id=part["id"], centre_m=[x, y, z], radius_m=radius,
                          length_m=length, toe_below_design_origin_m=-z + length / 2))
    if not piles:
        raise ValueError("foundation assessment requires actual defined piles")
    bounds = [min(p["centre_m"][0] - p["radius_m"] for p in piles),
              min(p["centre_m"][1] - p["radius_m"] for p in piles),
              max(p["centre_m"][0] + p["radius_m"] for p in piles),
              max(p["centre_m"][1] + p["radius_m"] for p in piles)]
    return dict(contract_sha256=fingerprint(contract), piles=piles, footprint_bounds_m=bounds,
                minimum_investigation_depth_m=max(p["toe_below_design_origin_m"] for p in piles),
                datum_basis="candidate local design origin; a sourced survey transform/vertical datum must bind this to the site")


def input_templates(contract, context):
    """Editable JSON records with blank evidence; no simulated measurements."""
    context = identity(context)
    blank_source = dict(reference=None, sha256=None, basis=None)
    def blank(unit):
        return dict(value=None, unit=unit, source=dict(blank_source))
    geometry = foundation_geometry(contract)
    site = dict(schema="osr-civil-site-input/1", identity=context,
                contract_sha256=fingerprint(contract),
                survey=dict(crs=None, vertical_datum=None, date=None, source=dict(blank_source),
                            horizontal_uncertainty=blank("m"), vertical_uncertainty=blank("m"),
                            coverage_bounds_m=None, design_origin_in_crs_m=None, design_axes_in_crs=None),
                layers=[dict(top=blank("m"), bottom=blank("m"), description=None, source=dict(blank_source))],
                groundwater=dict(source=dict(blank_source), observations=[]),
                utilities=dict(source=dict(blank_source), observations=[]),
                calibration=dict(source=dict(blank_source), training_records=[], holdout_records=[],
                                 model_domain=None, uncertainty=blank("1")),
                route_station_constraints=[])
    prestress = dict(schema="osr-civil-prestress-input/1", identity=context,
                     contract_sha256=fingerprint(contract), mode="pretensioned-straight",
                     transfer_age=blank("s"), service_age=blank("s"),
                     concrete_transfer_modulus=blank("Pa"),
                     transfer_compression_limit=blank("Pa"), transfer_tension_limit=blank("Pa"),
                     service_compression_limit=blank("Pa"), service_tension_limit=blank("Pa"),
                     tendons=[dict(physical_part_id=p["id"], metallic_area=blank("m2"),
                                   pretransfer_stress=blank("Pa"), steel_modulus=blank("Pa"),
                                   creep_loss=None, shrinkage_loss=None, relaxation_loss=None)
                              for p in contract["parts"] if p["id"].startswith("tendon-")])
    return dict(schema="osr-civil-evidence-templates/1", foundation_geometry=geometry,
                site_input=site, prestress_input=prestress,
                references=REFERENCES,
                instructions="Fill sourced SI values and exact scope; blank templates are not valid measured inputs. Source SHA syntax alone does not verify retained evidence. Independent appointments/review remain in evidence intake UI.",
                physical_release=False)


def prestress_assessment(contract, trace, inputs=None, *, context=None):
    """Straight pretensioned tendon elastic shortening and timed loss ledger.

    The actual reservations are solid CAD envelopes, not qualified strand areas.
    A supplied metallic area must fit each reservation. This model excludes
    post-tensioning sequence, friction, curved tendons, nonlinear cracking and
    anchorage resistance. Those cases cannot silently use pretension equations.
    """
    from engineering.design_consistency.analysis import civil_stages

    gross = civil_stages(contract, trace, prestress_n=0)
    deck = next(p for p in contract["parts"] if p["id"] == "deck")
    sec = deck["analysis"]["section"]
    length = max(p["dimensions_m"][2] for p in deck["manufacturing"]["primitives"])
    tendons = {p["id"]: p for p in contract["parts"] if p["id"].startswith("tendon-")}
    result = dict(
        schema="osr-civil-prestress-assessment/1",
        contract_sha256=fingerprint(contract),
        references=REFERENCES,
        gross_demands=gross,
        tendon_reservations=list(tendons),
        prestress_model="straight pretensioned, linear gross concrete, simultaneous transfer",
        checks={key: "unknown" for key in (
            "transfer", "loss_history", "service_cracking", "anchorage",
            "reinforcement_shear_torsion_ultimate", "physical_correlation",
        )},
        physical_release=False,
        site_qualified=False,
        complete_installed_inventory=False,
    )
    if inputs is None:
        result["basis"] = "No controlled tendon force, metallic area, age-dependent properties or stress limits; no seed prestress is credited."
        return result
    if context is None:
        raise ValueError("engineering identity required for entered prestress evidence")
    _scope(inputs, context, "osr-civil-prestress-input/1")
    if inputs.get("mode") != "pretensioned-straight":
        raise ValueError("outside domain: only simultaneous straight pretensioned transfer is supported")
    if inputs.get("contract_sha256") != fingerprint(contract):
        raise ValueError("prestress evidence refers to a different physical contract")
    transfer_age = scalar(inputs["transfer_age"], "s", "concrete age at transfer", minimum=1)
    service_age = scalar(inputs["service_age"], "s", "service assessment age", minimum=1)
    if service_age <= transfer_age:
        raise ValueError("service assessment age must follow transfer")
    rows = inputs.get("tendons", [])
    if len(rows) != len(tendons) or {r.get("physical_part_id") for r in rows} != set(tendons):
        raise ValueError("exactly one controlled record per actual tendon reservation required")
    eci = scalar(inputs["concrete_transfer_modulus"], "Pa", "transfer concrete modulus", minimum=1)
    transfer_compression = scalar(inputs["transfer_compression_limit"], "Pa", "transfer compression limit", minimum=1)
    transfer_tension = scalar(inputs["transfer_tension_limit"], "Pa", "transfer tension limit")
    service_compression = scalar(inputs["service_compression_limit"], "Pa", "service compression limit", minimum=1)
    service_tension = scalar(inputs["service_tension_limit"], "Pa", "service tension limit")
    # Compute self-weight moment from the same defined deck/bar/tendon mass.
    mass = gross["service"]["installed_deck_assembly_mass_kg"]
    self_moment = mass * 9.80665 * length / 8
    area, inertia, half_depth = sec["area_m2"], sec["iy_m4"], sec["height_m"] / 2
    parsed = []
    for row in rows:
        part = tendons[row["physical_part_id"]]
        ap = scalar(row["metallic_area"], "m2", "metallic strand area", minimum=1e-12)
        envelope = sum(math.pi * p["radius_m"] ** 2 for p in part["manufacturing"]["primitives"])
        if ap > envelope:
            raise ValueError("metallic area exceeds the physical tendon reservation")
        stress = scalar(row["pretransfer_stress"], "Pa", "pretransfer strand stress", minimum=1)
        ep = scalar(row["steel_modulus"], "Pa", "prestressing steel modulus", minimum=1)
        # Positive eccentricity means below gross deck centroid.
        eccentricity = deck["properties"]["cg_m"][2] - part["properties"]["cg_m"][2]
        if abs(eccentricity) >= half_depth:
            raise ValueError("tendon centroid lies outside the gross section")
        losses = {}
        for name in ("creep_loss", "shrinkage_loss", "relaxation_loss"):
            losses[name] = scalar(row[name], "Pa", name) if row.get(name) is not None else None
        parsed.append(dict(physical_part_id=row["physical_part_id"], metallic_area_m2=ap,
                           pretransfer_stress_pa=stress, steel_modulus_pa=ep,
                           eccentricity_m=eccentricity, long_term_losses_pa=losses))
    # Solve simultaneous elastic shortening analytically as a coupled linear
    # system: dfi = Epi/Eci * (sum Pj/A + ei*sum Pj*ej/I - Mg*ei/I).
    # This reduces to the independent FHWA closed-form equation for one group.
    shortening = elastic_shortening(parsed, area_m2=area, inertia_m4=inertia,
                                   concrete_modulus_pa=eci, self_weight_moment_nm=self_moment)
    for row, loss in zip(parsed, shortening):
        if loss < 0 or loss >= row["pretransfer_stress_pa"]:
            raise ValueError("outside domain: transfer predicts stress gain or nonpositive tendon force")
        row["elastic_shortening_loss_pa"] = float(loss)
        row["transfer_force_n"] = row["metallic_area_m2"] * (row["pretransfer_stress_pa"] - float(loss))
        values = list(row["long_term_losses_pa"].values())
        row["service_force_n"] = None if any(v is None for v in values) else row["transfer_force_n"] - row["metallic_area_m2"] * sum(values)
        if row["service_force_n"] is not None and row["service_force_n"] <= 0:
            raise ValueError("loss history consumes the full prestress force")
    def fibres(key, moment):
        if any(row[key] is None for row in parsed):
            return None
        force = sum(row[key] for row in parsed)
        pm = sum(row[key] * row["eccentricity_m"] for row in parsed)
        # Compression positive; sagging external moment compresses the top.
        endpoints = [force / area - pm * half_depth / inertia,
                     force / area + pm * half_depth / inertia]
        midspan = [force / area + (moment - pm) * half_depth / inertia,
                   force / area - (moment - pm) * half_depth / inertia]
        return dict(minimum_top_compression_pa=min(endpoints[0], midspan[0]),
                    maximum_top_compression_pa=max(endpoints[0], midspan[0]),
                    minimum_bottom_compression_pa=min(endpoints[1], midspan[1]),
                    maximum_bottom_compression_pa=max(endpoints[1], midspan[1]))
    transfer = fibres("transfer_force_n", self_moment)
    service = fibres("service_force_n", gross["service"]["maximum_bending_moment_nm"])
    def check(values, compression_limit, tension_limit):
        if values is None:
            return "unknown"
        return "passed" if all(-tension_limit <= v <= compression_limit for v in values.values()) else "failed"
    result["checks"]["transfer"] = check(transfer, transfer_compression, transfer_tension)
    result["checks"]["service_cracking"] = check(service, service_compression, service_tension)
    result["checks"]["loss_history"] = "unknown" if service is None else "passed"
    result.update(tendons=parsed, transfer_fibre_stress=transfer, service_envelope_fibre_stress=service,
                  loss_history_basis="Entered creep/shrinkage/relaxation stress losses at service age; no hidden empirical age law",
                  transfer_age_s=transfer_age, service_age_s=service_age,
                  input_sha256=fingerprint(inputs), input_sources=inputs,
                  basis="Conditional numerical checks against explicitly entered limits, not adopted standard or physical qualification.",
                  omitted_effects=["transfer development length and bond", "nonlinear cracked stiffness", "anchorage bursting",
                                   "shear and torsion", "ultimate resistance", "time-resolved creep interaction", "duct/anchor/grout inventory"])
    return result


def assess_site(inputs, *, context, required_depth_m, contract=None):
    """Validate source/scoped survey, layered ground and holdout coverage.

    Report numerical/metadata checks independently. A source hash, a calibrated
    research stiffness or a named reviewer cannot establish site resistance.
    """
    required_depth_m = number(required_depth_m, "foundation investigation depth", minimum=1e-9)
    result = dict(schema="osr-civil-site-assessment/1", references=REFERENCES,
                  checks={k: "unknown" for k in ("survey", "ground_depth_coverage", "groundwater", "utilities", "calibration", "route_station_constraints")},
                  site_qualified=False, physical_release=False, independent_acceptance="unknown",
                  source_files_verified=False,
                  source_check_basis="SHA syntax and scope only; retained file verification belongs to the evidence intake workflow")
    geometry = None
    if contract is not None:
        geometry = foundation_geometry(contract)
        required_depth_m = max(required_depth_m, geometry["minimum_investigation_depth_m"])
        result["foundation_geometry"] = geometry
        result["checks"]["foundation_survey_footprint"] = "unknown"
    result["required_investigation_depth_m"] = required_depth_m
    if inputs is None:
        result["basis"] = "No project survey, boreholes, groundwater, utilities or independent calibration records supplied."
        return result
    _scope(inputs, context, "osr-civil-site-input/1")
    if contract is not None and inputs.get("contract_sha256") != fingerprint(contract):
        raise ValueError("site evidence refers to a different physical foundation contract")
    survey = inputs.get("survey")
    if survey is not None:
        source(survey["source"])
        if not isinstance(survey.get("crs"), str) or not survey["crs"].strip():
            raise ValueError("explicit survey CRS including vertical datum required")
        if not isinstance(survey.get("vertical_datum"), str) or not survey["vertical_datum"].strip():
            raise ValueError("explicit survey vertical datum required")
        if date.fromisoformat(survey["date"]) > date.today():
            raise ValueError("future survey date cannot be an observed survey")
        scalar(survey["horizontal_uncertainty"], "m", "survey horizontal uncertainty")
        scalar(survey["vertical_uncertainty"], "m", "survey vertical uncertainty")
        result["checks"]["survey"] = "passed"
        if geometry is not None:
            bounds = survey.get("coverage_bounds_m")
            origin = survey.get("design_origin_in_crs_m")
            axes = survey.get("design_axes_in_crs")
            if not isinstance(bounds, list) or len(bounds) != 4:
                raise ValueError("four survey coverage bounds in local design metres required")
            if not isinstance(origin, list) or len(origin) != 3:
                raise ValueError("sourced local design origin in survey CRS required")
            for value in bounds + origin:
                number(value, "survey bounding/origin coordinate")
            if not isinstance(axes, list) or len(axes) != 3 or any(not isinstance(row, list) or len(row) != 3 for row in axes):
                raise ValueError("three sourced orthonormal local design axes in survey CRS required")
            for row in axes:
                for value in row:
                    number(value, "survey design axis")
            import numpy as np
            rotation = np.asarray(axes, dtype=float)
            if not np.allclose(rotation @ rotation.T, np.eye(3), atol=1e-9, rtol=0) or not math.isclose(float(np.linalg.det(rotation)), 1, abs_tol=1e-9):
                raise ValueError("survey transform axes must be orthonormal and right handed")
            if bounds[2] <= bounds[0] or bounds[3] <= bounds[1]:
                raise ValueError("nonempty survey coverage bounds required")
            # Coverage shrinks by horizontal uncertainty before testing against
            # actual pile footprints. Datum transform provenance is retained.
            uncertainty = survey["horizontal_uncertainty"]["value"]
            pile_bounds = geometry["footprint_bounds_m"]
            covered = (bounds[0] + uncertainty <= pile_bounds[0] and bounds[1] + uncertainty <= pile_bounds[1]
                       and bounds[2] - uncertainty >= pile_bounds[2] and bounds[3] - uncertainty >= pile_bounds[3])
            result["checks"]["foundation_survey_footprint"] = "passed" if covered else "failed"
    layers = inputs.get("layers")
    if layers is not None:
        if not isinstance(layers, list) or not 1 <= len(layers) <= 256:
            raise ValueError("bounded nonempty ordered ground layers required")
        depth = 0
        for layer in layers:
            source(layer["source"])
            top = scalar(layer["top"], "m", "layer top")
            bottom = scalar(layer["bottom"], "m", "layer bottom")
            if top != depth or bottom <= top:
                raise ValueError("contiguous nonoverlapping ground layer depths required")
            if not isinstance(layer.get("description"), str) or not layer["description"].strip():
                raise ValueError("ground stratum description required")
            depth = bottom
        result["investigated_depth_m"] = depth
        result["checks"]["ground_depth_coverage"] = "passed" if depth >= required_depth_m else "failed"
    for name in ("groundwater", "utilities"):
        if inputs.get(name) is not None:
            row = inputs[name]
            source(row["source"])
            if not isinstance(row.get("observations"), list) or not row["observations"]:
                raise ValueError(name + " requires actual observations; missing is not none-present")
            result["checks"][name] = "passed"
    calibration = inputs.get("calibration")
    if calibration is not None:
        source(calibration["source"])
        training, holdout = calibration.get("training_records"), calibration.get("holdout_records")
        for records in (training, holdout):
            if not isinstance(records, list) or not records or any(not isinstance(r, str) or not r.strip() for r in records) or len(set(records)) != len(records):
                raise ValueError("nonempty distinct calibration record identities required")
        if set(training) & set(holdout):
            raise ValueError("calibration and holdout observations must be independent")
        if not isinstance(calibration.get("model_domain"), str) or not calibration["model_domain"].strip():
            raise ValueError("site calibration model domain required")
        scalar(calibration["uncertainty"], "1", "calibration relative uncertainty")
        result["checks"]["calibration"] = "passed"
    constraints = inputs.get("route_station_constraints")
    if constraints is not None:
        if not isinstance(constraints, list) or not 1 <= len(constraints) <= 512:
            raise ValueError("bounded nonempty route/station constraints required")
        ids = set()
        states = []
        for row in constraints:
            if not isinstance(row.get("id"), str) or not row["id"] or row["id"] in ids:
                raise ValueError("unique route/station constraint identity required")
            ids.add(row["id"])
            source(row["source"])
            if row.get("kind") not in {"route_clearance", "station_access", "junction_clearance", "utility_separation"}:
                raise ValueError("explicit supported route/station constraint kind required")
            measured = scalar(row["available"], "m", "available surveyed clearance")
            required = scalar(row["required"], "m", "entered clearance requirement", minimum=1e-9)
            uncertainty = scalar(row["uncertainty"], "m", "clearance uncertainty")
            states.append("passed" if measured - uncertainty >= required else "failed")
        result["checks"]["route_station_constraints"] = "failed" if "failed" in states else "passed"
        result["constraint_checks"] = dict(zip([r["id"] for r in constraints], states))
    result.update(input_sha256=fingerprint(inputs), input_sources=inputs,
                  basis="Input completeness, depth and clearance checks only; measured resistance, group/settlement/cyclic model correlation and independent review remain open.")
    return result
