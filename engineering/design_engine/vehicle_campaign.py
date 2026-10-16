"""Worker-budgeted independent full-passage campaigns with retained progress."""

from copy import deepcopy
from pathlib import Path

from .contracts import canonical
from .passage import case
from .vehicle_confirmation import (
    assembly_diagnostics,
    passage_plan,
    independent_refinement_plan,
    compare_independent_refinements,
    complete_coverage,
)


def run(data, folder, charge, *, remaining_seconds=None):
    from engineering.civil_exploration.spatial_demo import scenarios

    folder = Path(folder)
    model = data["model"]
    charge(2, "actual-modal-and-equipment-mass-reconciliation")
    diagnostics = [assembly_diagnostics(data, mode_count=count) for count in (2, 4)]
    data["assembly_diagnostics"] = diagnostics
    campaigns = data["independent_refinement_campaigns"] = {}
    results = data["coupled_cases"] = {}
    jobs = []
    for name, config in scenarios(model).items():
        config = deepcopy(config)
        config["equipment_mounts"] = diagnostics[0]["equipment_mount_laws"]
        config["flexible_vehicle"] = diagnostics[0]["flexible_vehicle_parameters"]
        whole = passage_plan(model, config)
        destination = folder / name
        destination.mkdir()
        campaign = campaigns[name] = dict(
            schema="osr-independent-passage-campaign/1",
            plan=None,
            planned=0,
            executed=0,
            validated=0,
            state="planned",
            cases={},
            comparison=None,
            physical_validation=False,
        )
        if not whole["within_adapter_domain"]:
            campaign.update(state="outside-domain", passage_plan=whole)
            continue
        plan = independent_refinement_plan(model, config)
        campaign["plan"] = plan
        (destination / "refinement-plan.json").write_bytes(canonical(plan) + b"\n")
        definitions = [
            dict(
                id="baseline",
                parameters=plan["baseline_parameters"],
                expected_steps=plan["passage"]["steps"],
            ),
            *plan["cases"],
        ]
        for definition in definitions:
            identifier = definition["id"]
            row = dict(state="not-run", requested_parameters=definition["parameters"])
            campaign["cases"][identifier] = row
            results[name + "/" + identifier] = row
            jobs.append((name, definition))
        campaign["planned"] = len(definitions)

    def retain():
        for name, campaign in campaigns.items():
            plan = campaign["plan"]
            if plan is None:
                continue
            cases = campaign["cases"]
            report = compare_independent_refinements(
                model, plan, cases["baseline"], cases, artifact_root=folder / name
            )
            campaign["comparison"] = report
            campaign["validated"] = sum(
                row["state"] == "passed" for row in report["cases"]
            )
            campaign["state"] = (
                "validated"
                if report["state"] == "passed"
                else (
                    "failed"
                    if report["state"] == "failed"
                    or any(
                        row["state"] in {"failed", "outside-domain", "stale"}
                        for row in cases.values()
                    )
                    else "executed" if campaign["executed"] else "planned"
                )
            )
            target = folder / name / "comparison.json"
            temporary = target.with_suffix(".pending.json")
            temporary.write_bytes(canonical(campaign) + b"\n")
            temporary.replace(target)
        target = folder / "passage-progress.json"
        temporary = target.with_suffix(".pending.json")
        temporary.write_bytes(
            canonical(dict(campaigns=campaigns, cases=results, physical_release=False))
            + b"\n"
        )
        temporary.replace(target)

    # Retain every plan before launching a native case. Baselines precede all
    # axis refinements so a short budget is not monopolised by one scenario.
    order = {
        name: i for i, name in enumerate(("baseline", "time", "deck", "rail", "modal"))
    }
    jobs.sort(key=lambda job: order[job[1]["id"]])
    retain()
    try:
        for index, (name, definition) in enumerate(jobs):
            # Native timeouts do not cover hashing, progress publication or the
            # common worker's final attempt seal. Leave that time available.
            remaining = None if remaining_seconds is None else remaining_seconds()
            reserve = 10.0
            if remaining is not None and remaining <= reserve:
                break
            identifier = definition["id"]
            charge(1, "vehicle-" + name + "-" + identifier)
            plan = campaigns[name]["plan"]
            configuration = definition.get("configuration", plan["configuration"])
            timeout = (
                45 if remaining is None else (remaining - reserve) / (len(jobs) - index)
            )
            native = case(
                model,
                configuration,
                definition["parameters"],
                folder / name / identifier,
                timeout=timeout,
            )
            native["allocated_wall_seconds"] = timeout
            coverage = {**plan["passage"], "steps": definition["expected_steps"]}
            native["full_passage_coverage"] = complete_coverage(
                model, configuration, coverage, native
            )
            campaigns[name]["cases"][identifier] = native
            results[name + "/" + identifier] = native
            campaigns[name]["executed"] += 1
            retain()
    finally:
        # Budget/cancellation exceptions retain planned and completed cases.
        retain()
    return campaigns
