import hashlib
import json

import pytest

from engineering.outline.workforce_plan import (
    ERECTION, MODES, NETWORKS, OPERATING, QUANTITIES, ROOT, TRAINING, VEHICLE, YARD, build_plan,
)


DELIVERY = json.loads((ROOT / QUANTITIES).read_bytes())


@pytest.mark.parametrize("network", NETWORKS)
@pytest.mark.parametrize("mode", MODES)
def test_repeated_shifts_preserve_published_operating_hours_and_relief(network, mode):
    studies = {**DELIVERY["studies"], **DELIVERY["operating_options"]}
    published = studies[network]["workforce_scenarios"][mode]
    plan = build_plan(network, mode)
    assert plan["scope"]["operating_establishment_fte"] == published["total_fte"]
    rows = [row for row in plan["rows"] if row["phase"] == OPERATING]
    for role, hours in published["duty_hours_per_year"].items():
        role_rows = [row for row in rows if row["role"] == role]
        assert sum(row["required_minutes"] for row in role_rows) == hours * 60
        assert sum(row["paid_minutes"] for row in role_rows) == published["posts_fte"][role] * 2080 * 60

    def shifts_for(role):
        return [(row["start_minute"], row["minutes_per_shift"], row["assigned_posts"])
                for row in rows if row["role"] == role]

    depot = shifts_for("depot rolling-stock technicians")
    assert [row[:2] for row in depot] == [(360, 480), (840, 480), (1320, 480)]
    assert depot[0][2] == depot[1][2] == depot[2][2] * 2
    public = shifts_for("station duty and passenger assistance")
    assert [row[:2] for row in public] == [(360, 480), (840, 480), (1320, 120)]
    assert len({row["work_id"] for row in plan["rows"]}) == len(plan["rows"])


def test_costed_build_roles_and_training_keep_periods_separate():
    first = DELIVERY["studies"]["first"]
    plan = build_plan()
    def phase(wanted):
        return [row for row in plan["rows"] if row["phase"] == wanted]

    assert sum(row["assigned_posts"] for row in phase(VEHICLE)) == (
        first["vehicle"]["direct_posts_all_lines"] + first["vehicle"]["support_posts_all_lines"]
    )
    assert sum(row["assigned_posts"] for row in phase(YARD)) == first["civil"]["civil_yard_day_posts"]
    assert sum(row["assigned_posts"] for row in phase(ERECTION)) == first["civil"]["erection_day_posts"]
    trainees = first["initial_training_labour"]
    assert sum(row["paid_minutes"] for row in phase(TRAINING)) == 60 * (
        trainees["learner_hours"] + trainees["classroom_instructor_hours"] + trainees["field_mentor_hours"]
    )
    assert all(row["assigned_posts"] is None for row in phase(TRAINING))
    assert all(row["rates_cents_per_hour"][0] > 0 for row in plan["rows"])
    assert len({(row["phase"], row["cost_account"]) for row in plan["rows"]}) == 6


def test_cost_missing_for_unsited_reference_and_binding_changes_are_visible(tmp_path):
    reference = build_plan("core")
    assert all(row["rates_cents_per_hour"] is None for row in reference["rows"])
    assert all(row["paid_minutes"] is None for row in reference["rows"] if row["phase"] in {YARD, ERECTION, VEHICLE})
    assert reference["plan_id"] == build_plan("core")["plan_id"]
    prepared = tmp_path / QUANTITIES
    prepared.parent.mkdir(parents=True)
    prepared.write_text(json.dumps({"source_sha256": {"source.txt": hashlib.sha256(b"before").hexdigest()}}))
    (tmp_path / "source.txt").write_text("after")
    with pytest.raises(ValueError, match="Regenerate the published delivery quantities"):
        build_plan(root=tmp_path)
