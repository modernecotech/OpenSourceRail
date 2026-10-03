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
