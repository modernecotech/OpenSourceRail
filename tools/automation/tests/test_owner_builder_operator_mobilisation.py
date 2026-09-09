from __future__ import annotations

import json
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools/automation/validate-owner-builder-operator-mobilisation.py"


def test_blank_mobilisation_baseline_is_complete_and_fail_closed() -> None:
    module = runpy.run_path(str(SCRIPT))
    status = module["build_status"]()
    assert status["summary"] == {
        "roles_ready": 0,
        "roles_total": 13,
        "independent_parties_ready": 0,
        "independent_parties_total": 3,
        "gates_accepted": 0,
        "gates_total": 8,
        "work_packages_complete": 0,
        "work_packages_total": 18,
        "management_systems_ready": 0,
        "management_systems_total": 11,
        "default_programme_start_month": 0,
        "default_programme_end_month": 60,
        "mobilisation_ready": False,
    }
    assert all(status["validation"].values())
    assert {row["id"] for row in status["gates"]} == {f"G{number}" for number in range(8)}
    assert {row["id"] for row in status["work_packages"]} == {
        f"MOB-{number:03d}" for number in range(10, 181, 10)
    }
    assert all(row["status"] == "not-started" and not row["complete"] for row in status["work_packages"])
    assert {row["id"] for row in status["management_systems"]} == {
        "MS-GOV", "MS-ENG", "MS-SAF", "MS-COMP", "MS-COM", "MS-PC",
        "MS-QUA", "MS-ASSET", "MS-ENV", "MS-FIN", "MS-DIG",
    }
    assert all(row["status"] == "not-established" and not row["ready"] for row in status["management_systems"])


def test_tracked_mobilisation_outputs_match_source() -> None:
    module = runpy.run_path(str(SCRIPT))
    status = module["build_status"]()
    assert json.loads((ROOT / "docs/owner-builder-operator-mobilisation-status.json").read_text()) == status
    assert (ROOT / "docs/owner-builder-operator-mobilisation-status.md").read_text() == module["render_status"](status)


def test_small_workshop_scope_uses_its_own_roles_and_evidence(tmp_path):
    module = runpy.run_path(str(SCRIPT))
    source = tmp_path / 'workshop.toml'
    source.write_text('''
deployment_scope = "Existing workshop adopting non-safety inspection records"
[entity_model]
required_fields = []
[[role]]
id = "WORKSHOP"
title = "Workshop responsible engineer"
accountable_for = ["inspection records"]
status = "vacant"
[[gate]]
id = "PILOT"
accountable_role_ids = ["WORKSHOP"]
required_evidence = ["record integrity demonstration"]
decision = "open"
[[work_package]]
id = "RECORDS"
accountable_role_id = "WORKSHOP"
gate_id = "PILOT"
start_month = 0
end_month = 0.5
fte_min = 0.25
fte_max = 0.5
deliverables = ["tested local installation"]
status = "not-started"
''')
    report = module['build_status'](source)
    assert 'Existing workshop' in module['render_status'](report)
    assert report['summary']['roles_total'] == 1
    assert report['summary']['gates_total'] == 1
    assert report['summary']['management_systems_total'] == 0
    assert report['work_packages'][0]['duration_months'] == 0.5
    assert report['summary']['mobilisation_ready'] is False
    source.write_text(source.read_text().replace('decision = "open"', 'decision = "accepted"\ndecided_by = "owner"\ndecided_at = "2026-09-09"\nevidence_refs = [""]'))
    assert module['build_status'](source)['gates'][0]['accepted'] is False
    import pytest
    source.write_text(source.read_text().replace('gate_id = "PILOT"', 'gate_id = "UNKNOWN"'))
    with pytest.raises(ValueError, match='unresolved role or gate'):
        module['build_status'](source)
