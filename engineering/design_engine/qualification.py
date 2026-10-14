"""Part/subsystem/assembly, measured correlation and exact formal-scope register."""

from __future__ import annotations
import importlib.util
from pathlib import Path
from .registry import ROOT, problems


def matrix():
    rows = []
    for identifier, charter in problems().items():
        level = (
            "part"
            if charter["adapter"] in {"panel", "roof"}
            else (
                "subsystem"
                if charter["adapter"] in {"battery", "interface", "twin"}
                else "assembly/site"
            )
        )
        for name in charter["applicability"]["mandatory_checks"]:
            physical = name in {
                "physical_correlation",
                "supplier_calibration",
                "independent_acceptance",
                "fire",
                "fatigue",
                "hot_wet_properties",
                "joint_strength",
            }
            rows.append(
                dict(
                    problem=identifier,
                    level=level,
                    check=name,
                    state="unknown" if physical else "not-run",
                    required_source=(
                        "measured/supplier/project-appointed evidence"
                        if physical
                        else "source-bound numerical/native execution"
                    ),
                    owner_role=(
                        "independent reviewer"
                        if physical
                        else "discipline verification engineer"
                    ),
                    appointed_person=None,
                    physically_accepted=False,
                )
            )
    spec = importlib.util.spec_from_file_location(
        "formal_scope_register", ROOT / "tools/automation/assurance-evidence.py"
    )
    formal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(formal)
    return dict(
        schema="osr-design-verification-matrix/1",
        checks=rows,
        formal_obligations=[
            dict(
                solution=r["solution"],
                path=r["path"],
                anchor=r["anchor"],
                scope="exact declared harness with recorded assumptions/unwind bounds",
                state="unknown; consult current controlled execution and independent acceptance records",
            )
            for r in formal.declared()
        ],
        selected_proof_success_closes_other_obligations=False,
        physical_data_available=False,
        physical_release=False,
    )


def correlate(model, dataset, parameters, predict, *, evidence_root, holdout_specimens):
    from engineering.civil_exploration.correlation import calibrate

    # Existing calibrator verifies retained data hashes, calibration identity,
    # specimen independence, domain/uncertainty and measured-versus-synthetic class.
    return calibrate(
        model,
        dataset,
        parameters,
        predict,
        root=Path(evidence_root),
        holdout_specimens=holdout_specimens,
    )
