"""A routine regeneration must not replace controlled network intent."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("city_package_refresh", ROOT / "tools/automation/generate-city-packages-fast.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_existing_ring_layout_is_retained_unless_resynthesis_is_explicit(tmp_path, monkeypatch):
    city = tmp_path / "city"
    city.mkdir()
    design = city / "design.toml"
    original = '[city]\nslug="test"\n[[lines]]\nname="line-6"\nshape="ring"\n'
    design.write_text(original)
    raster = tmp_path / "rasters"
    raster.mkdir()
    (raster / "test.grid.json").write_text('{}')
    (city / "corridors.json").write_text('{}')  # deliberately unrelated cache
    monkeypatch.setattr(module, "RASTER_CACHE", raster)
    monkeypatch.setattr(module, "LOG_ROOT", tmp_path / "logs")
    monkeypatch.setattr(module, "source_artifacts", lambda *args: [design])
    commands = []
    monkeypatch.setattr(module, "run_logged", lambda command, *args, **kwargs: commands.append(command) or 0)
    result = module.prepare_city("test", design, {"country": "IQ"}, False, False)
    assert result["passed"]
    assert design.read_text() == original
    assert any("refresh-city-design-costs.py" in " ".join(cmd) for cmd in commands)
    assert not any(Path(cmd[0]).name == "osr-design" for cmd in commands)
    commands.clear()
    module.prepare_city("test", design, {"country": "IQ"}, False, False, True)
    assert any(Path(cmd[0]).name == "osr-design" for cmd in commands)


def _prepared_city(tmp_path, monkeypatch, slug, *, existing=True, policy=False):
    city = tmp_path / slug
    city.mkdir()
    design = city / "design.toml"
    if existing:
        design.write_text(f'[city]\nslug="{slug}"\n[[lines]]\nname="retained-ring"\nshape="ring"\n')
    if policy:
        (city / "alignment-policy.toml").write_text("[core]\n")
    raster = tmp_path / "rasters"
    raster.mkdir()
    (raster / f"{slug}.grid.json").write_text('{}')
    (city / "corridors.json").write_text('{}')
    monkeypatch.setattr(module, "RASTER_CACHE", raster)
    monkeypatch.setattr(module, "LOG_ROOT", tmp_path / "logs")
    monkeypatch.setattr(module, "source_artifacts", lambda *args: [design])
    commands = []

    def run(command, *args, **kwargs):
        commands.append(command)
        if Path(command[0]).name == "osr-design" and not design.exists():
            design.write_text(f'[city]\nslug="{slug}"\n')
        return 0

    monkeypatch.setattr(module, "run_logged", run)
    return design, commands


def test_default_refresh_preserves_baghdad_and_adopted_policy_layouts(tmp_path, monkeypatch):
    for slug in ("baghdad", "other-city"):
        case = tmp_path / slug
        case.mkdir()
        design, commands = _prepared_city(case, monkeypatch, slug, policy=True)
        original = design.read_bytes()
        result = module.prepare_city(slug, design, {"country": "IQ"}, False, False)
        assert result["passed"]
        assert result["layout_action"] == "retained-controlled-layout"
        assert design.read_bytes() == original
        assert not any("rework-" in " ".join(command) for command in commands)
        assert not any(Path(command[0]).name == "osr-design" for command in commands)


def test_new_city_bootstraps_its_own_current_planner_by_default(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, "new-city", existing=False)
    result = module.prepare_city("new-city", design, {"country": "FR"}, False, False)
    assert result["passed"]
    assert result["design_approach"] == "current-source-controlled-layout-v1"
    native = [i for i, command in enumerate(commands) if Path(command[0]).name == "osr-design"]
    current = [i for i, command in enumerate(commands) if "rework-city-alignment.py" in " ".join(command)]
    assert len(native) == 2
    assert native[0] < current[0] < current[-1] < native[1]
    assert "--design-only" not in commands[native[0]]
    assert "--design-only" in commands[native[1]]
    assert not any("rework-baghdad-alignment.py" in " ".join(command) for command in commands)
    assert all(str(design) in command for command in (commands[i] for i in current))


def test_retained_layout_refresh_does_not_download_deleted_raster_cache(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, 'retained')
    (module.RASTER_CACHE / 'retained.grid.json').unlink()
    assert module.prepare_city('retained', design, {'country': 'IQ'}, False, False)['passed']
    assert not any('osr_osm.cli' in command or 'osr_geo.cli' in command for command in commands)
    assert not any(Path(command[0]).name == 'osr-design' for command in commands)


def test_explicit_baghdad_resynthesis_retains_its_controlled_planner(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, "baghdad", policy=True)
    result = module.prepare_city("baghdad", design, {"country": "IQ"}, False, False, True)
    assert result["passed"]
    assert result["layout_action"] == "resynthesised"
    assert any("rework-baghdad-alignment.py" in " ".join(command) for command in commands)
    assert not any("rework-city-alignment.py" in " ".join(command) for command in commands)


def test_full_refresh_generates_design_status_before_package_manifest(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, "test")
    result = module.finish_city("test", design, 1)
    assert result["passed"]
    status = next(i for i, command in enumerate(commands) if "generate-city-design-status.py" in " ".join(command))
    federation = next(i for i, command in enumerate(commands) if "generate-city-federation.py" in " ".join(command))
    manifest = next(i for i, command in enumerate(commands) if "generate-city-package-manifest.py" in " ".join(command))
    assert federation < status < manifest


def test_baghdad_proposal_is_rebuilt_after_final_package_manifest(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, "baghdad")
    result = module.finish_city("baghdad", design, 1)
    assert result["passed"]
    manifest = next(i for i, command in enumerate(commands) if "generate-city-package-manifest.py" in " ".join(command))
    proposal = next(i for i, command in enumerate(commands) if "build-baghdad-proposal.py" in " ".join(command))
    assert manifest < proposal == len(commands) - 1
    commands.clear()
    assert module.finish_city("baghdad", design, 1, publish_proposal=False)["passed"]
    assert not any("build-baghdad-proposal.py" in " ".join(command) for command in commands)


def test_full_refresh_rechecks_retained_clearance_without_deleted_osm_cache(tmp_path, monkeypatch):
    design, commands = _prepared_city(tmp_path, monkeypatch, 'retained')
    folder = design.parent/'engineering/clearance'
    folder.mkdir(parents=True)
    for name in ('building-footprints.json.gz','building-source.json','terrain-elevation.f32.gz','terrain-source.json'):
        (folder/name).write_bytes(b'retained')
    assert module.finish_city('retained', design, 1)['passed']
    command = next(c for c in commands if 'audit-viaduct-clearance.py' in ' '.join(c))
    assert '--retain-inputs' not in command and '--fetch-terrain' not in command
    commands.clear()
    (folder/'terrain-source.json').unlink()
    assert module.finish_city('retained', design, 1)['passed']
    command = next(c for c in commands if 'audit-viaduct-clearance.py' in ' '.join(c))
    assert '--retain-inputs' in command and '--fetch-terrain' in command
