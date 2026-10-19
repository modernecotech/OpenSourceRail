"""City system reports preserve architecture and distinguish files from acceptance."""
import importlib.util
import gzip
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("city_design_status", ROOT / "tools/automation/generate-city-design-status.py")
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)


def city(root, slug="test-city", family="tram-small"):
    folder = root / "cities" / slug
    folder.mkdir(parents=True)
    design = folder / "design.toml"
    design.write_text(f'[city]\nslug="{slug}"\ncountry="XX"\npopulation=120000\n[climate]\npreset="temperate"\n[[lines]]\nname="a"\nlength_m=1234\nrolling_stock="{family}"\n')
    engineering = folder / "engineering"
    engineering.mkdir()
    return design, engineering


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(status.encoded(value))


def test_other_city_uses_own_family_and_missing_inputs_remain_open(tmp_path):
    design, _ = city(tmp_path)
    report = status.build(design, tmp_path)
    assert report["city"] == "test-city"
    assert report["configuration"]["rolling_stock_families"] == ["tram-small"]
    assert report["configuration"]["route_length_m"] == 1234
    assert report["counts"]["system_domains"] == 12
    assert all(system["state"] == "missing-evidence" for system in report["systems"])
    assert "baghdad-six-car" not in json.dumps(report)
    assert not report["design_complete"] and not report["manufacturing_release"]


def test_receipt_failure_cannot_be_overridden_by_passed_or_release_claim(tmp_path):
    design, engineering = city(tmp_path)
    write(engineering / "energy/summary.json", {"design_sha256": "0" * 64, "passed": True, "engineering_release": True})
    report = status.build(design, tmp_path)
    electrical = next(s for s in report["systems"] if s["id"] == "electrical")
    assert electrical["state"] == "stale-evidence"
    assert not electrical["engineering_complete"]
    assert not report["engineering_release"]


def test_registered_parts_and_software_are_retained_without_promoting_completion(tmp_path):
    design, engineering = city(tmp_path)
    source = tmp_path / "definition.txt"
    source.write_text("source v1")
    write(engineering / "detail/register.json", {
        "sources_sha256": {str(design.relative_to(tmp_path)): status.digest(design), "definition.txt": status.digest(source)},
        "parts": [{"id": "PART-001", "title": "Frame", "quantity_network_reference": 3,
                   "acceptance": "Independent load and manufacturing verification", "supplier_part_number": None}],
        "software_allocations": [{"name": "control", "hosts": ["ecu"]}],
        "engineering_release": True,
    })
    report = status.build(design, tmp_path)
    assert report["part_register_receipt"]["state"] == "design-bound"
    assert report["parts"][0]["state"] == "provisional-reference"
    assert report["counts"]["registered_parts"] == 1
    assert report["counts"]["software_allocations"] == 1
    source.write_text("changed")
    report = status.build(design, tmp_path)
    assert report["parts"][0]["state"] == "stale-reference"
    assert report["part_register_receipt"]["mismatches"] == ["definition.txt"]


def test_visuals_are_actual_files_and_report_does_not_inventory_itself(tmp_path):
    design, engineering = city(tmp_path)
    for name in ("new-adapter/test.FCStd", "new-adapter/export.step.gz", "new-adapter/assembly.mp4"):
        p = engineering / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"retained artifact")
    report = status.generate(design, tmp_path)
    assert len(report["artifacts"]) == 3
    assert not any("design-system/" in p for p in report["sources_sha256"])
    assert status.generate(design, tmp_path, verify=True) == report
    assert "motion, collision or physical validation" in (engineering / "design-system/index.html").read_text()


def test_verification_detects_input_drift_added_artifacts_and_edited_html(tmp_path):
    design, engineering = city(tmp_path)
    status.generate(design, tmp_path)
    design.write_text(design.read_text().replace("1234", "5678"))
    with pytest.raises(ValueError, match="stale city design system"):
        status.generate(design, tmp_path, verify=True)
    status.generate(design, tmp_path)
    (engineering / "new.ifc").write_text("geometry")
    with pytest.raises(ValueError, match="stale city design system"):
        status.generate(design, tmp_path, verify=True)
    status.generate(design, tmp_path)
    (engineering / "design-system/index.html").write_text("edited")
    with pytest.raises(ValueError, match="stale city design system"):
        status.generate(design, tmp_path, verify=True)


def test_unbound_json_is_not_labelled_fresh_or_accepted(tmp_path):
    design, engineering = city(tmp_path)
    write(engineering / "factory/summary.json", {"passed": True})
    report = status.build(design, tmp_path)
    artifact = next(a for a in report["artifacts"] if a["path"].endswith("factory/summary.json"))
    assert artifact["receipt"]["state"] == "unbound"
    assert report["counts"]["accepted_complete_systems"] == 0


def test_unsafe_receipt_path_is_held_and_links_escape_markup(tmp_path):
    design, engineering = city(tmp_path)
    write(engineering / "energy/summary.json", {"sources_sha256": {"../private": "0" * 64}})
    report = status.build(design, tmp_path)
    assert next(a for a in report["artifacts"] if a["path"].endswith("energy/summary.json"))["receipt"]["state"] == "stale"
    name = 'drawing<script>.svg'
    (engineering / name).write_text("svg")
    text = status.render(status.build(design, tmp_path), engineering / "design-system", tmp_path)
    assert "drawing<script>" not in text
    assert "drawing%3Cscript%3E.svg" in text


def test_non_repository_design_is_rejected(tmp_path):
    design, _ = city(tmp_path / "outside")
    with pytest.raises(ValueError, match="within the repository"):
        status.build(design, tmp_path / "other")


def test_local_output_receipts_disambiguate_root_readme_and_station_geometry(tmp_path):
    design, engineering = city(tmp_path)
    (tmp_path / "README.md").write_text("repository front door")
    folder = engineering / "connected-build/cad"
    folder.mkdir(parents=True)
    local = folder / "README.md"
    local.write_text("station geometry")
    (folder / "station.FCStd").write_bytes(b"station only")
    write(folder / "manifest.json", {"outputs_sha256": {"README.md": status.digest(local)}})
    report = status.build(design, tmp_path)
    manifest = next(a for a in report["artifacts"] if a["path"].endswith("cad/manifest.json"))
    assert manifest["receipt"]["state"] == "receipt-consistent"
    stations = next(s for s in report["systems"] if s["id"] == "stations")
    mechanical = next(s for s in report["systems"] if s["id"] == "mechanical")
    assert any(name.endswith("station.FCStd") for name in stations["artifacts"])
    assert not any(name.endswith("station.FCStd") for name in mechanical["artifacts"])
    local.write_text("altered station geometry")
    assert status.receipt_status(folder / "manifest.json", design, tmp_path)["state"] == "stale"


def research_fixture(root):
    folder = root / "docs/design-engine/assembly-design"
    folder.mkdir(parents=True)
    source = root / "source.txt"
    source.write_text("frozen source")
    hashes = {"source.txt": status.digest(source)}
    flags = dict(design_complete=False, manufacturing_release=False, physical_release=False, physical_validation=False)
    prototype = dict(id="BAGHDAD-PROTOTYPE-6C-2026-10-19", architecture="baghdad-six-car", family="metro-6car", **flags)
    baseline = dict(prototype=prototype, policy={"architecture": "baghdad-six-car"}, source_sha256=hashes, **flags)
    epoch = status.sha256(status.encoded(baseline)).hexdigest()
    progress = dict(epoch=epoch, source_sha256=hashes, counts={"completed_trials": 50}, selected=[],
                    diagnostics=[{"key": "cassette-key", "kind": "service-cassette"}], **flags)
    qualification = dict(passed=True, returncode=0, sources=hashes, **flags)
    for name, data in (("prototype.json", prototype), ("progress.json", progress), ("qualification.json", qualification),
                       ("diagnostics/service-cassette/result.json", {"failed_checks": ["known-fit-failure"], "held_checks": ["physical"]}),
                       ("diagnostics/service-cassette/native-result.json", {"child": "cassette-key", "state": "passed"})):
        write(folder / name, data)
    (folder / "baseline.json.gz").write_bytes(gzip.compress(status.encoded(baseline)))
    (folder / "diagnostics/service-cassette/model.FCStd").write_bytes(b"native geometry")
    files = {p.relative_to(folder).as_posix(): status.digest(p) for p in folder.rglob("*") if p.is_file()}
    write(folder / "manifest.json", dict(epoch=epoch, files_sha256=files, progress_digest=status.sha256(status.encoded(progress)).hexdigest(), **flags))
    return folder, source


def test_baghdad_research_requires_exact_context_and_never_transfers_to_other_city(tmp_path):
    folder, source = research_fixture(tmp_path)
    context, used = status.research_context("other-city", {"metro-6car"}, tmp_path)
    assert context is None and used == set()
    context, _ = status.research_context("baghdad", {"tram-small"}, tmp_path)
    assert context["state"] == "inapplicable-prototype"
    context, used = status.research_context("baghdad", {"metro-6car"}, tmp_path)
    assert context["state"] == "source-current-provisional-research"
    assert context["completed_variants"] == 50
    assert context["native_exhibits"] == 1
    assert context["pilots"][0]["state"] == "excluded-diagnostic"
    assert context["pilots"][0]["failed_checks"] == ["known-fit-failure"]
    assert not context["manufacturing_release"]
    assert not any(p.name in {"evidence.tar.gz", "model.FCStd"} for p in used)
    source.write_text("changed qualified input")
    context, _ = status.research_context("baghdad", {"metro-6car"}, tmp_path)
    assert context["state"] == "stale-source-context"
    assert context["source_mismatches"] == ["source.txt"]


def test_research_metadata_tampering_cannot_be_relabelled_current(tmp_path):
    folder, _ = research_fixture(tmp_path)
    progress = json.loads((folder / "progress.json").read_text())
    progress["counts"]["completed_trials"] = 5000
    write(folder / "progress.json", progress)
    context, _ = status.research_context("baghdad", {"metro-6car"}, tmp_path)
    assert context["state"] == "invalid-research-context"
    assert "seal differs" in context["reason"]


def test_logical_source_aliases_check_actual_design_scenario_and_generator(tmp_path):
    design, engineering = city(tmp_path)
    scenario = design.with_name("test-city.toml")
    scenario.write_text("city-specific simulation")
    generator = tmp_path / "tools/generator.py"
    generator.parent.mkdir(parents=True)
    generator.write_text("current generator")
    paths = {"design": str(design.relative_to(tmp_path)), "scenario": str(scenario.relative_to(tmp_path)),
             "generator": str(generator.relative_to(tmp_path))}
    receipt = engineering / "stabling/summary.json"
    write(receipt, {"source_paths": paths, "source_sha256": {name: status.digest(tmp_path / path) for name, path in paths.items()}})
    result = status.receipt_status(receipt, design, tmp_path)
    assert result == {"state": "design-bound", "checked": 3, "mismatches": []}
    generator.write_text("generator changed")
    result = status.receipt_status(receipt, design, tmp_path)
    assert result["state"] == "stale" and result["mismatches"] == ["generator"]
    value = json.loads(receipt.read_text())
    value["source_paths"]["generator"] = "../outside"
    write(receipt, value)
    assert "unsafe receipt path" in status.receipt_status(receipt, design, tmp_path)["mismatches"][0]
