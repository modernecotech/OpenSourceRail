"""Trusted checks for bounded research recipes and pure-data native assemblies."""
from pathlib import Path

from .core import FLAGS, ROOT, validate, write


def evaluate(proposal, output):
    validate(proposal, proposal["baseline_sha256"])
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    kind, params = proposal["kind"], proposal["parameters"]
    if kind in ("mechanical-cleat", "civil-steel-beam"):
        from engineering.design_engine.generated_parts import compile_definition
        from engineering.design_engine.generated_parts_native import native_screen
        definition = compile_definition(kind, params)
        write(output / "definition.json", definition, exclusive=True)
        native = native_screen(definition, output / "native", ROOT, remaining_seconds=600)
        checks = native["checks"]
        study_pass = all(c["state"] == "passed" for k, c in checks.items()
                         if k not in ("physical_correlation", "independent_acceptance"))
        result = dict(study_pass=study_pass, checks=checks, metrics=native["metrics"],
            open_evidence=definition["unresolved"],
            scope="One ideal-clamped isotropic solid; displacement mesh study, not accepted strength/contact/fatigue")
    elif kind in ("vehicle-interface", "civil-bay", "controlled-assembly"):
        from engineering.design_consistency import demonstrators as d
        from engineering.design_consistency.contracts import summary
        from engineering.design_engine.native_cad import generate
        definition = (params["contract"] if kind == "controlled-assembly" else
                      d.interface() if kind == "vehicle-interface" else d.viaduct(**params))
        path = output / "definition.json"
        write(path, definition, exclusive=True)
        cad = generate(path, output / "cad", ROOT)
        checks = dict(native_reopened=cad["native_reopened"], part_identity=cad["physical_ids_preserved"],
            step_volume=cad["step_volume_reconciled"],
            inspection_projection=cad["inspection_projection_edges"] > 0)
        if kind == "civil-bay":
            from engineering.design_consistency.ifc import export
            from .ifc_checks import correct_analytical_representation
            receipt = export(definition, output / "civil.ifc")
            validation = correct_analytical_representation(output / "civil.ifc")
            write(output / "ifc-schema-issues.json", validation, exclusive=True)
            receipt["schema_issue_count"] = len(validation["after"])
            write(output / "ifc-correspondence.json", receipt, exclusive=True)
            checks["ifc_exact_part_volumes"] = receipt["maximum_tessellation_volume_relative_error"] <= 5e-4
            checks["ifc_schema"] = not validation["after"]
        result = dict(study_pass=all(checks.values()), checks=checks,
            correspondence=summary(definition),
            open_evidence=definition["mandatory_evidence"] + definition.get("unresolved_part_allocations", []),
            scope="Partial research assembly, simplified fasteners/reinforcement; drawing dimensions, tolerances and issue remain open")
    else:
        from engineering.generative_design.twin_software_factory import fault_suite, replay_precharge
        rows = []
        for case in fault_suite():
            replay = replay_precharge(case["frames"], params["policy"])
            actual = replay["rows"][-1]["request_main_close"]
            rows.append(dict(id=case["id"], expected=case["expected_request"], actual=actual,
                             passed=actual is case["expected_request"], replay=replay))
        write(output / "fault-replay.json", rows, exclusive=True)
        result = dict(study_pass=all(r["passed"] for r in rows),
            checks={r["id"]: r["passed"] for r in rows},
            metrics=dict(cases=len(rows), failed_cases=sum(not r["passed"] for r in rows)),
            open_evidence=["Complete executable control software", "independent target SIL/HIL and timing tests",
                           "installed hardware identities and calibrated observations", "independent safety acceptance"],
            scope="Existing precharge policy simulator; no source generation, target control or HIL")
    result.update(FLAGS)
    write(output / "result.json", result, exclusive=True)
    return result
