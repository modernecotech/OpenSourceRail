"""Selected logical boundaries stay candidate-bound and non-authoritative at the UI edge."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "osr_v07_interface_schedule", ROOT / "control-electronics/interface_schedule.py")
schedule = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(schedule)


def _copy_inputs(tmp_path: Path) -> None:
    for source in (schedule.SELECTED, schedule.EQUIPMENT):
        target = tmp_path / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)


def test_published_schedule_is_current_and_separates_authority():
    value = json.loads((ROOT / schedule.OUTPUT).read_text())
    schedule.validate(value)
    assert value["physical_candidate_id"] == "osr-v07-joined-civil-518dad57a3af5046f40c8f4f"
    assert value["source_selection_evaluation_id"] == "osr-v07-digital-interface-20261117"
    assert value["evaluation_id"] != value["source_selection_evaluation_id"]
    assert value["safety_qualification"] is value["live_control_enabled"] is False
    assert value["passenger_display_equipment_quantity"] is None
    assert value["passenger_display_price_usd_m"] is None
    assert value["physical_connector_pinout"] is None
    assert value["installed_software_versions"] is None
    rows = {row["id"]: row for row in value["interfaces"]}
    assert rows["authority-to-atp"]["role"] == "safety_authority"
    assert rows["station-dispatch-request"]["role"] == "safety_request"
    assert rows["atp-to-independent-brake"]["role"] == "safety_command"
    assert all(row["role"] in {"observation", "business_record", "passenger_information"}
               for row in rows.values() if row["sink"] in {"fuxa-gateway", "erpnext", "passenger-information"})


def test_mixed_candidate_and_missing_counted_equipment_rejected(tmp_path: Path):
    _copy_inputs(tmp_path)
    source = tmp_path / schedule.EQUIPMENT
    source.write_text(source.read_text().replace(
        'selected_physical_candidate_id = "osr-v07-joined-civil-518dad57a3af5046f40c8f4f"',
        'selected_physical_candidate_id = "another-vehicle"'))
    with pytest.raises(ValueError, match="physical candidate differ"):
        schedule.build(tmp_path)
    shutil.copyfile(ROOT / schedule.EQUIPMENT, source)
    source.write_text(re.sub(r"\[items\.atp-channel\].*?(?=\[items\.)", "",
                             source.read_text(), count=1, flags=re.S))
    with pytest.raises(ValueError, match="Required control equipment is missing"):
        schedule.build(tmp_path)


def test_missing_interface_and_observation_escalation_rejected():
    original = schedule.build()
    missing = deepcopy(original)
    missing["interfaces"] = [row for row in missing["interfaces"]
                             if row["id"] != "atp-to-independent-brake"]
    with pytest.raises(ValueError, match="Required logical interface"):
        schedule.validate(missing)
    promoted = deepcopy(original)
    next(row for row in promoted["interfaces"] if row["id"] == "train-status-to-fuxa")["role"] = "safety_authority"
    with pytest.raises(ValueError, match="Logical interface or source evaluation differs"):
        schedule.validate(promoted)


def test_input_price_revision_changes_evaluation_not_physical_candidate(tmp_path: Path):
    _copy_inputs(tmp_path)
    before = schedule.build(tmp_path)
    source = tmp_path / schedule.EQUIPMENT
    source.write_text(source.read_text().replace("price_usd_m_each = 0.020",
                                                 "price_usd_m_each = 0.021", 1))
    after = schedule.build(tmp_path)
    assert after["physical_candidate_id"] == before["physical_candidate_id"]
    assert after["selection_id"] == before["selection_id"]
    assert after["evaluation_id"] != before["evaluation_id"]
    with pytest.raises(ValueError, match="Logical interface or source evaluation differs"):
        schedule.validate(before, tmp_path)
