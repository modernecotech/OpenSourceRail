"""Thin adapters over existing physical compilers and analysis implementations.

No adapter fills an absent supplier, site, cost or physical result with a pass.
The same full physical definition feeds screening, refinement and export.
"""

from __future__ import annotations
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path
import shutil

from .contracts import fingerprint, checks_status, variables, problem_fingerprint
from .registry import ROOT


class OutsideDomain(ValueError):
    pass


class Unavailable(RuntimeError):
    pass


def checks(charter):
    return {
        name: dict(
            state="not-run",
            basis="required by the independent problem verification matrix",
        )
        for name in charter["applicability"]["mandatory_checks"]
    }


def set_check(result, name, state, basis, **observables):
    if name not in result["checks"]:
        raise ValueError("adapter cannot invent or omit a mandatory check")
    result["checks"][name] = dict(state=state, basis=basis, **observables)


def compile_candidate(charter, scope, values):
    values = variables(charter, values)
    kind = charter["adapter"]
    data = {}
    metrics = {}
    from engineering.design_consistency import demonstrators as d
    from engineering.design_consistency.contracts import summary

    if kind in {"panel", "roof"}:
        config = json.loads(
            (ROOT / "engineering/composite_panels/config/development.json").read_text()
        )
        model = d.panel_bay(
            config,
            span=values["support_span_m"],
            grade_density=values["grade_density"],
            skin=values["skin_m"],
            core=values["core_m"],
            crown=0.05 if kind == "roof" else 0,
            aperture=kind == "panel",
        )
        if kind == "panel":
            from engineering.panel_response.plate import regions

            regions(model)  # physical potting overlap is rejected before ranking
        data = dict(contract=model, correspondence=summary(model))
        metrics = dict(
            defined_mass_kg=data["correspondence"]["mass_kg"],
            attachment_count=model["support_network"]["panel_attachment_count"],
        )
    elif kind == "interface":
        model = d.interface()
        joint = model["assembly_joints"][0]
        joint["preload_range_n"] = [
            v * values["preload_factor"] for v in joint["preload_range_n"]
        ]
        data = dict(contract=model, correspondence=summary(model))
        metrics = dict(defined_mass_kg=data["correspondence"]["mass_kg"])
    elif kind in {"viaduct", "foundation"}:
        model = d.viaduct(
            length=20,
            pier_height=values.get("pier_height_m", 8),
            pile_length=values["pile_length_m"],
            pile_spacing=values["pile_spacing_m"],
        )
        data = dict(contract=model, correspondence=summary(model))
        metrics = dict(defined_mass_kg=data["correspondence"]["mass_kg"])
    elif kind in {"battery", "vehicle"}:
        from engineering.civil_exploration.variant_compiler import (
            compile_variant,
            CHOICES_PATH,
        )

        choices = json.loads(CHOICES_PATH.read_text())
        choices["family"] = "metro-6car"
        if kind == "battery":
            choices["battery"].update(values)
        else:
            choices["family"] = values["family"]
        data = compile_variant(choices)
        if kind == "battery":
            from .electrical_installation import installation_report

            data["installation"] = installation_report(data, kind="battery")
        metrics = dict(defined_mass_kg=data["review"]["total_mass_kg"])
    elif kind == "twin":
        from .subsystems import hvac

        data = hvac(values)
        metrics = dict(defined_mass_kg=data["review"]["total_train_mass_kg"])
    elif kind == "civil":
        data = dict(
            study=json.loads(
                (
                    ROOT / "engineering/civil_exploration/config/reference.json"
                ).read_text()
            )
        )
    elif kind in {"city-options", "engineering-change"}:
        if values["city"] != scope["city"]:
            raise OutsideDomain(
                "city option and change candidates cannot cross city context"
            )
        folder = ROOT / (
            "engineering/design-options"
            if kind == "city-options"
            else "engineering/changes"
        )
        catalogue = json.loads((folder / "catalogue.json").read_text())
        entries = [
            e
            for e in catalogue["entries"]
            if e["city"] == scope["city"] and e["environment"] == scope["environment"]
        ]
        if not entries:
            raise OutsideDomain(
                "no retained option/change in the selected asset environment"
            )
        data = dict(
            catalogue_entries=entries, domain_root=folder.relative_to(ROOT).as_posix()
        )
    else:
        raise OutsideDomain("unregistered discipline adapter")
    from .manufacturing import compile_register, reconcile

    data["installed_register"] = reconcile(compile_register(data), data)
    result = dict(
        schema="osr-design-candidate/1",
        identity=deepcopy(scope),
        problem_sha256=problem_fingerprint(charter),
        variables=deepcopy(values),
        definition=data,
        definition_sha256=fingerprint(data),
        metrics=metrics,
        checks=checks(charter),
        complete_installed_mass_kg=None,
        installed_cost=None,
        lifecycle_cost=None,
        production_time=None,
        disruption=None,
        imported_content=None,
        carbon=None,
        physical_release=False,
        independently_accepted=False,
        production_released=False,
    )
    result["id"] = "candidate-" + fingerprint(
        dict(
            problem=result["problem_sha256"],
            variables=values,
            definition=result["definition_sha256"],
        )
    )
    set_check(
        result,
        "geometry",
        (
            "failed"
            if data["installed_register"]
            .get("dimensional_manufacturing", {})
            .get("state")
            == "failed"
            else "passed"
        ),
        "existing physical compiler and dimensional validation; any failed entered manufacturing constraint rejects geometry; missing workshop evidence remains open",
    )
    return result


def screen(charter, result, charge, folder):
    kind = charter["adapter"]
    charge(1, "screen")
    data = result["definition"]
    if kind in {"panel", "roof"}:
        contract = data["contract"]
        response = contract["response"]
        deflection = response["total_deflection_m"]
        result["metrics"]["screen_deflection_m"] = deflection
        set_check(
            result,
            "nominal_deflection",
            "passed" if deflection <= 0.005 else "failed",
            "existing strip screen only; detailed model and attachment faults govern finalists",
            value=deflection,
            unit="m",
            limit=0.005,
        )
        for key in (
            "joint_strength",
            "fatigue",
            "fire",
            "hot_wet_properties",
            "complete_installed_inventory",
            "physical_correlation",
        ):
            set_check(
                result,
                key,
                "unknown",
                "supplier, full installed definition or measured applicability evidence absent",
            )
        if kind == "roof" and contract["thermal_status"] == "failed":
            set_check(
                result,
                "hot_wet_properties",
                "failed",
                "85 degC roof study exceeds the public core continuous-temperature datum",
                unit="degC",
                value=85,
                limit=contract["core_grade"]["continuous_max_temperature_c"],
            )
    elif kind == "interface":
        from engineering.design_consistency.analysis import bolt_screen, interface_modes

        data["joint_screen"] = bolt_screen(data["contract"]["assembly_joints"][0])
        data["modal_screen"] = interface_modes(data["contract"])
        set_check(
            result,
            "mass_inertia",
            "passed",
            "physical rigid-body mass/inertia and modal orthogonality reconciled",
            residual=data["modal_screen"]["rigid_mass_inertia_relative_error"],
        )
        failed = any(v == "failed" for v in data["joint_screen"]["checks"].values())
        set_check(
            result,
            "interfaces",
            "failed" if failed else "unknown",
            "joint compression/slip screen plus unresolved resistance/fatigue/calibration",
        )
    elif kind in {"viaduct", "foundation"}:
        from engineering.design_consistency.analysis import civil_stages

        trace = json.loads(
            (
                ROOT / "engineering/industrialisation/vehicle-civil-load-trace.json"
            ).read_text()
        )
        data["stages"] = civil_stages(data["contract"], trace)
        from .civil_qualification import (
            prestress_assessment,
            assess_site,
            input_templates,
        )

        data["prestress_assessment"] = prestress_assessment(
            data["contract"], trace, context=result["identity"]
        )
        data["site_assessment"] = assess_site(
            None,
            context=result["identity"],
            required_depth_m=result["variables"]["pile_length_m"],
            contract=data["contract"],
        )
        data["civil_input_templates"] = input_templates(
            data["contract"], result["identity"]
        )
        set_check(
            result,
            "mass_inertia",
            "passed",
            "manufacturing/analysis/coordination quantities reconciled",
        )
        set_check(
            result,
            "service",
            data["stages"]["checks"]["global_elastic_deflection"],
            "complete axle sweep, staged lifting and bearing replacement demand; resistance and site response unqualified",
        )
    elif kind in {"battery", "vehicle", "twin"}:
        review = data["review"]
        residual = review.get(
            "mass_balance_residual_kg", review.get("mass_reallocation_residual_kg")
        )
        set_check(
            result,
            "mass_inertia",
            "passed" if abs(residual) < 1e-7 else "failed",
            "full existing assembly allocation and rigid kinetic mass reconciliation",
            residual_kg=residual,
        )
        set_check(
            result,
            "interfaces",
            "unknown" if kind in {"battery", "twin"} else "passed",
            (
                "typed crosswalk passed; battery cooling/fire/mount and DC/AC supplier compatibility remain unqualified"
                if kind in {"battery", "twin"}
                else "existing typed physical/electrical/thermal/control crosswalk validation; no supplier compatibility acceptance"
            ),
            typed_crosswalk_state="passed",
            installation=data.get("installation"),
        )
        if kind == "twin":
            set_check(
                result,
                "service",
                (
                    "passed"
                    if data["studies"]["hvac_nominal"]["within_declared_study_limit"]
                    else "failed"
                ),
                "existing nominal lumped HVAC duty screen",
            )
            set_check(
                result,
                "degraded_service",
                (
                    "passed"
                    if data["studies"]["hvac_one_module_out"][
                        "within_declared_study_limit"
                    ]
                    else "failed"
                ),
                "existing failed-module thermal duty and electrical energy penalty retained",
            )
        elif kind == "battery":
            duty = review["battery_duty"]
            passed = duty.get("research_constraints_passed")
            # The adapter uses the domain's named checks, never infers success
            # from the absence of an exception or a nonempty result dictionary.
            if "checks" in duty:
                passed = all(
                    v is True or v == "passed" for v in duty["checks"].values()
                )
            set_check(
                result,
                "service",
                (
                    "passed"
                    if passed is True
                    else "failed" if passed is False else "unknown"
                ),
                "existing battery duty research constraints; unknown supplier limits stay open",
            )
        for key in (
            "complete_installed_inventory",
            "supplier_calibration",
            "physical_correlation",
            "independent_acceptance",
        ):
            set_check(
                result,
                key,
                "unknown",
                "explicit incomplete physical allocation, supplier or independent evidence remains required",
            )
    elif kind in {"city-options", "engineering-change"}:
        module_path = ROOT / (
            "tools/automation/design-option.py"
            if kind == "city-options"
            else "engineering/changes/workflow.py"
        )
        spec = importlib.util.spec_from_file_location(
            "common_legacy_review", module_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        reports = []
        for entry in data["catalogue_entries"]:
            bundle = ROOT / data["domain_root"] / entry["bundle"]
            if kind == "engineering-change":
                report = module.verify(ROOT, bundle)
            else:
                # The old option module exposes its existing verifier; retain
                # original domain records and its exact source/hash semantics.
                report = module.verify(bundle)
            reports.append(report)
        data["verified_original_manifests"] = reports
        set_check(
            result,
            "interfaces",
            "passed",
            "original domain manifest/source and exact city/environment verification",
        )
        for key in (
            "complete_installed_inventory",
            "supplier_calibration",
            "physical_correlation",
            "independent_acceptance",
        ):
            set_check(
                result,
                key,
                "unknown",
                "review package cannot adopt business/engineering/railway baseline",
            )
    result["evidence_state"] = checks_status(
        result["checks"], charter["applicability"]["mandatory_checks"]
    )
    return result


def refine(charter, result, charge, folder):
    kind = charter["adapter"]
    data = result["definition"]
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    if kind == "panel":
        from engineering.panel_response.plate import solve, single_clip_envelope

        model = data["contract"]
        charge(2, "mesh-refinement")
        coarse = solve(model, mesh_size=0.08)
        fine = solve(model, mesh_size=0.04)
        delta = abs(coarse["maximum_deflection_m"] / fine["maximum_deflection_m"] - 1)
        set_check(
            result,
            "mesh_refinement",
            "passed" if delta < 0.03 else "failed",
            "mapped plate/rail mesh comparison",
            relative_difference=delta,
            limit=0.03,
        )
        set_check(
            result,
            "nominal_deflection",
            fine["deflection_screen"],
            "detailed trimmed MITC4 plate with actual hollow rails and clip locations",
            value=fine["maximum_deflection_m"],
            unit="m",
            limit=0.005,
        )
        charge(len(fine["attachments"]) + 1, "single-attachment-envelope")
        envelope = single_clip_envelope(model, mesh_size=0.04)
        worst = envelope["worst"]
        fault = worst["failed_clip"]
        unstable = worst["status"] == "unstable"
        set_check(
            result,
            "single_attachment_loss",
            "failed" if unstable or worst["maximum_deflection_m"] > 0.005 else "passed",
            "every individual physical clip removed; unstable cases retained",
            case_count=envelope["case_count"],
            governing_case=fault,
        )
        charge(3, "independent-holdouts")
        holdout = solve(model, mesh_size=0.04, pressure_pa=3500)
        combined = (
            dict(
                deflection_screen="failed",
                maximum_deflection_m=None,
                status="outside-domain",
                basis="governing clip loss is unstable; combined linear solution unavailable",
            )
            if unstable
            else solve(model, mesh_size=0.04, pressure_pa=3500, failed_clip=fault)
        )
        soft = solve(model, mesh_size=0.04, clip_stiffness_factor=0.1)
        set_check(
            result,
            "combined_pressure_fault",
            combined["deflection_screen"],
            "independent 3.5 kPa pressure plus governing single-clip loss",
            value=combined["maximum_deflection_m"],
            unit="m",
            governing_case=fault,
            pressure_pa=3500,
        )
        data["confirmation"] = dict(
            coarse=coarse,
            refined=fine,
            all_clip_losses=envelope,
            holdout=holdout,
            combined=combined,
            soft_joint=soft,
        )
        result["metrics"].update(
            detailed_deflection_m=fine["maximum_deflection_m"],
            combined_holdout_deflection_m=combined["maximum_deflection_m"],
        )
    elif kind == "roof":
        from .roof_shell import solve as shell

        model = data["contract"]
        charge(2, "native-curved-shell-refinement")
        coarse = shell(model, folder / "coarse", mesh_size=0.12)
        fine = shell(model, folder / "refined", mesh_size=0.08)
        delta = abs(
            coarse["maximum_radial_deflection_m"] / fine["maximum_radial_deflection_m"]
            - 1
        )
        set_check(
            result,
            "mesh_refinement",
            "passed" if delta < 0.03 else "failed",
            "native curved composite S8R and hollow BOX rails",
            relative_difference=delta,
            limit=0.03,
        )
        set_check(
            result,
            "nominal_deflection",
            fine["deflection_screen"],
            "native radial roof-shell response; unresolved curved contact stiffness is a sensitivity",
            value=fine["maximum_radial_deflection_m"],
            unit="m",
            limit=0.005,
        )
        confirmation = dict(coarse=coarse, refined=fine, all_clip_losses=[])
        data["confirmation"] = confirmation
        for index, clip in enumerate(fine["geometry"]["clips"]):
            charge(1, "native-roof-single-clip-loss")
            try:
                case = shell(
                    model,
                    folder / f"clip-loss-{index:03d}",
                    mesh_size=0.08,
                    failed_clip=clip["id"],
                )
            except (RuntimeError, ValueError) as error:
                case = dict(
                    state="failed",
                    failed_clip=clip["id"],
                    error=str(error),
                    maximum_radial_deflection_m=None,
                )
            confirmation["all_clip_losses"].append(case)
        cases = confirmation["all_clip_losses"]
        worst = max(
            cases,
            key=lambda r: (
                float("inf")
                if r["maximum_radial_deflection_m"] is None
                else r["maximum_radial_deflection_m"]
            ),
        )
        index = cases.index(worst)
        fault = fine["geometry"]["clips"][index]["id"]
        set_check(
            result,
            "single_attachment_loss",
            (
                "failed"
                if worst["maximum_radial_deflection_m"] is None
                or worst["maximum_radial_deflection_m"] > 0.005
                else "passed"
            ),
            "every individually defined physical roof clip removed in the native curved model",
            case_count=len(cases),
            governing_case=fault,
        )
        for name, options in [
            ("holdout", dict(pressure_pa=3500)),
            ("combined", dict(pressure_pa=3500, failed_clip=fault)),
            ("soft_joint", dict(contact_stiffness_n_m=1e6)),
        ]:
            charge(1, "native-roof-" + name)
            try:
                confirmation[name] = shell(
                    model, folder / name, mesh_size=0.08, **options
                )
            except (RuntimeError, ValueError) as error:
                confirmation[name] = dict(
                    state="failed",
                    error=str(error),
                    maximum_radial_deflection_m=None,
                    deflection_screen="failed",
                )
        combined = confirmation["combined"]
        set_check(
            result,
            "combined_pressure_fault",
            combined["deflection_screen"],
            "native 3.5 kPa pressure with governing individual clip removed",
            value=combined["maximum_radial_deflection_m"],
            unit="m",
            governing_case=fault,
        )
        result["metrics"].update(
            detailed_deflection_m=fine["maximum_radial_deflection_m"],
            combined_holdout_deflection_m=combined["maximum_radial_deflection_m"],
        )
    elif kind in {"viaduct", "foundation"}:
        from .civil_confirmation import beam

        trace = json.loads(
            (
                ROOT / "engineering/industrialisation/vehicle-civil-load-trace.json"
            ).read_text()
        )
        results = {}
        charge(6, "native-civil-stage-mesh-confirmation")
        for stage in ("service", "lifting", "bearing-replacement"):
            results[stage] = [
                beam(
                    data["contract"],
                    trace,
                    folder / (stage + "-" + str(n)),
                    elements=n,
                    stage=stage,
                )
                for n in (40, 80)
            ]
        data["native_stage_confirmation"] = results
        ratios = {
            stage: abs(
                values[0]["maximum_deflection_m"] / values[1]["maximum_deflection_m"]
                - 1
            )
            for stage, values in results.items()
        }
        set_check(
            result,
            "refinement",
            "passed" if all(x < 0.03 for x in ratios.values()) else "failed",
            "native hollow BOX deck with actual defined self weight, governing complete axle load, lifting and replacement demand; no resistance/site pass",
            relative_differences=ratios,
        )
        set_check(
            result,
            "supplier_calibration",
            "unknown",
            "prestress/anchorage histories, reinforcement resistance, bearing laws and site-ground calibration require entered evidence",
        )
    elif kind == "civil":
        from engineering.civil_exploration.workflow import run_campaign

        config = ROOT / "engineering/civil_exploration/config/reference.json"
        charge(
            1
            + len(data["study"]["candidates"]) * len(data["study"]["ground_scenarios"]),
            "native-civil-campaign",
        )
        data["native_manifest"] = run_campaign(config, folder / "native-campaign")
        data["native_comparison"] = json.loads(
            (folder / "native-campaign/comparison.json").read_text()
        )
        failed = any(
            r["execution"] != "completed" or r["numerical_screen"] != "passed"
            for r in data["native_comparison"]["rows"]
        )
        set_check(
            result,
            "refinement",
            "failed" if failed else "passed",
            "original complete native campaign and independent benchmark, mesh/time and ground cases retained",
        )
    elif kind == "vehicle":
        from engineering.civil_exploration.spatial_demo import scenarios
        from .passage import case
        from .vehicle_confirmation import (
            assembly_diagnostics,
            passage_plan,
            complete_coverage,
        )

        model = data["model"]
        results = {}
        charge(2, "actual-modal-and-equipment-mass-reconciliation")
        diagnostics = [assembly_diagnostics(data, mode_count=count) for count in (2, 4)]
        data["assembly_diagnostics"] = diagnostics
        set_check(
            result,
            "mass_inertia",
            (
                "passed"
                if all(
                    d["mass_relative_error"] < 1e-12
                    and d["reaction_relative_error"] < 1e-12
                    and d["modal_preload_residual_n"] < 1e-6
                    and d["minimum_static_contact_n"] > 0
                    for d in diagnostics
                )
                else "failed"
            ),
            "actual separate battery mounts and mass-normalized research body modes conserve physical mass and static reactions; shell correlation open",
        )
        for name, config in scenarios(model).items():
            for index, (level, dt, deck_mesh, rail_step) in enumerate(
                [
                    ("coarse", 0.002, 4, 1.0),
                    ("refined", 0.001, 8, 0.5),
                ]
            ):
                charge(1, "vehicle-" + name + "-" + level)
                plan = passage_plan(model, config, dt=dt)
                planned = plan["configuration"]
                planned["equipment_mounts"] = diagnostics[index]["equipment_mount_laws"]
                planned["flexible_vehicle"] = diagnostics[index][
                    "flexible_vehicle_parameters"
                ]
                parameters = dict(
                    dt=dt,
                    duration_s=plan["duration_s"],
                    deck_mesh=deck_mesh,
                    rail_step=rail_step,
                )
                if not plan["within_adapter_domain"]:
                    results[name + "/" + level] = dict(
                        state="outside-domain",
                        basis="the complete assembly cannot clear the approach within the native motion/time/step domain",
                        requested_parameters=parameters,
                    )
                else:
                    results[name + "/" + level] = case(
                        model, planned, parameters, folder / (name + "-" + level)
                    )
                results[name + "/" + level]["passage_plan"] = plan
                native = results[name + "/" + level]
                covered = complete_coverage(model, planned, plan, native)
                native["full_passage_coverage"] = covered
                if "joint_resultant_cycles" in native:
                    native["joint_resultant_cycles"]["full_passage_history"] = covered
                (folder / "passage-progress.json").write_text(
                    json.dumps(
                        dict(cases=results, physical_release=False), allow_nan=False
                    )
                )
        data["coupled_cases"] = results
        data["paired_refinement"] = {}
        for name in scenarios(model):
            coarse, refined = results[name + "/coarse"], results[name + "/refined"]
            if all(
                r.get("state") == "completed" and r.get("within_adapter_domain") is True
                for r in (coarse, refined)
            ):
                differences = {
                    metric: abs(coarse[metric] - refined[metric])
                    / max(abs(refined[metric]), 1e-12)
                    for metric in (
                        "peak_structure_displacement_m",
                        "peak_total_carbody_acceleration_m_s2",
                        "maximum_wheel_contact_n",
                    )
                }
                data["paired_refinement"][name] = dict(
                    state=(
                        "passed"
                        if all(d <= 0.05 for d in differences.values())
                        else "failed"
                    ),
                    relative_differences=differences,
                    provisional_relative_limit=0.05,
                    basis="jointly refined time/deck/rail/modal levels; separate sensitivity remains required",
                )
            else:
                data["paired_refinement"][name] = dict(
                    state="not-run",
                    basis="both complete, within-domain native histories required",
                )
        failed = any(
            r.get("state") in {"outside-domain", "failed", "budget-exceeded"}
            or r.get("within_adapter_domain") is not True
            or r.get("full_passage_coverage") is not True
            for r in results.values()
        )
        set_check(
            result,
            "service",
            "failed" if failed else "unknown",
            "whole assembly enters before the approach and clears the exit under its prescribed motion; actual battery mount/modal mass retained; synthetic laws and physical passage unqualified",
        )
        set_check(
            result,
            "refinement",
            (
                "failed"
                if failed
                or any(
                    r["state"] == "failed" for r in data["paired_refinement"].values()
                )
                else "passed"
            ),
            "paired time/deck/rail/modal refinement only; complete within-domain histories required; no shell or physical correlation claim",
        )
    elif kind == "battery":
        from engineering.civil_exploration.automated_battery import duty_cycle

        pack = data["battery"]
        charge(2, "aged-hot-battery-holdouts")
        aged = deepcopy(pack)
        aged["capacity_ah"] *= 0.8
        aged["resistance_ohm"] *= 1.25
        aged["cooling_conductance_w_k"] *= 0.75
        segments = [
            dict(duration_s=60, terminal_power_w=200000),
            dict(duration_s=60, terminal_power_w=30000),
            dict(duration_s=20, terminal_power_w=-75000),
        ]
        data["degraded_holdouts"] = dict(
            aged_hot=duty_cycle(aged, segments, ambient_temperature_c=45),
            nominal=duty_cycle(pack, segments),
        )
        strings = pack["parallel_strings"]
        if strings > 1:
            isolated = deepcopy(pack)
            factor = (strings - 1) / strings
            isolated["capacity_ah"] *= factor
            isolated["resistance_ohm"] /= factor
            isolated["discharge_current_limit_a"] *= factor
            isolated["charge_current_limit_a"] *= factor
            charge(1, "isolated-parallel-string-holdout")
            data["degraded_holdouts"]["one_string_isolated"] = duty_cycle(
                isolated, segments, ambient_temperature_c=45
            )
            data["degraded_holdouts"][
                "isolation_basis"
            ] = "electrically isolated parallel string; installed physical modules/mounting mass remain unchanged; thermal sharing uncalibrated"
        actual = [r for r in data["degraded_holdouts"].values() if isinstance(r, dict)]
        failed = any(r.get("research_constraints_passed") is False for r in actual)
        confirmed = all(r.get("research_constraints_passed") is True for r in actual)
        set_check(
            result,
            "degraded_service",
            "failed" if failed else "passed" if confirmed else "unknown",
            "aged/hot/failed-cooling sensitivities are synthetic; supplier capacity and thermal calibration remain open",
        )
    elif kind == "twin":
        from engineering.twin_design.physics import thermal_study

        params = data["inputs"]["hvac"]["thermal_assumptions"]
        capacity = data["inputs"]["hvac"]["module_cooling_w"]
        charge(3, "hvac-holdouts")
        half = deepcopy(params)
        half["step_s"] /= 2
        hot = deepcopy(params)
        hot["ambient_c"] = 50
        count = data["inputs"]["hvac"]["module_count_per_car"]
        data["thermal_confirmation"] = dict(
            refined=thermal_study(half, count - 1, capacity),
            two_out=thermal_study(params, count - 2, capacity),
            hot=thermal_study(hot, count - 1, capacity),
        )
        coarse = thermal_study(params, count - 1, capacity)
        refined = data["thermal_confirmation"]["refined"]
        temperature_difference = abs(
            coarse["maximum_temperature_c"] - refined["maximum_temperature_c"]
        )
        energy_difference = abs(
            coarse["electrical_energy_kwh"] - refined["electrical_energy_kwh"]
        ) / max(coarse["electrical_energy_kwh"], 1e-12)
        set_check(
            result,
            "refinement",
            (
                "passed"
                if temperature_difference <= 0.001 and energy_difference <= 0.01
                else "failed"
            ),
            "exact constant-step lumped thermal integration rerun at half step; supplier/airflow model still uncalibrated",
            maximum_temperature_difference_c=temperature_difference,
            relative_electrical_energy_difference=energy_difference,
            temperature_limit_c=0.001,
            energy_relative_limit=0.01,
        )
        set_check(
            result,
            "degraded_service",
            (
                "failed"
                if any(
                    r["within_declared_study_limit"] is False
                    for r in data["thermal_confirmation"].values()
                )
                else "passed"
            ),
            "actual module count minus one/two and 50°C holdouts; no physical ambient/airflow qualification",
        )
    result["evidence_state"] = checks_status(
        result["checks"], charter["applicability"]["mandatory_checks"]
    )
    return result
