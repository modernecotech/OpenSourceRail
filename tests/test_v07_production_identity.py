"""Production edits must change the handoff evaluation, not its physical selection."""

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "docs/reference-v07/digital/production/generate.py"


def _generator():
    spec = importlib.util.spec_from_file_location("v07_production_generate", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_routing_revision_changes_only_production_evaluation(tmp_path, monkeypatch):
    module = _generator()
    original = module.compile_handoff()
    for source in module.SOURCES.values():
        target = tmp_path / source
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(ROOT / source)
    route = tmp_path / module.SOURCES["routing"]
    route.unlink()
    route.write_text((ROOT / module.SOURCES["routing"]).read_text().replace(
        "body-traveller", "body-traveller-revision", 1))
    monkeypatch.setattr(module, "ROOT", tmp_path)
    revised = module.compile_handoff()
    assert revised["source_sha256"]["routing"] != original["source_sha256"]["routing"]
    assert revised["evaluation_id"] != original["evaluation_id"]
    assert revised["source_selection_evaluation_id"] == original["source_selection_evaluation_id"]
    assert revised["physical_candidate_id"] == original["physical_candidate_id"]
    assert revised["selection_id"] == original["selection_id"]
