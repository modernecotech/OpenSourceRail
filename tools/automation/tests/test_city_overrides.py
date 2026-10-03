import importlib.util
from pathlib import Path
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("city_overrides", ROOT / "tools/automation/apply-city-overrides.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_controlled_policy_survives_synthesis_without_altering_geometry(tmp_path):
    path = tmp_path / "design.toml"
    generated = '[city]\nslug="test"\n[operations.energy]\nenabled=true\n[[lines]]\nname="line-1"\n'
    path.write_text(generated)
    (tmp_path / "design-overrides.toml").write_text('[operations.habd]\nenabled=true\napproach_distance_m=500\n')
    assert module.apply(path)
    first = path.read_bytes()
    data = tomllib.loads(first.decode())
    assert data["lines"] == [{"name": "line-1"}]
    assert data["operations"]["habd"]["enabled"]
    assert not module.apply(path)
    assert path.read_bytes() == first
    path.write_text(generated)  # next synthesis replaces the generated file
    assert module.apply(path)
    assert path.read_bytes() == first


def test_uncontrolled_scope_is_rejected(tmp_path):
    path = tmp_path / "design.toml"
    path.write_text('[[lines]]\nname="line-1"\n')
    (tmp_path / "design-overrides.toml").write_text('[costs]\ntotal_usd=1\n')
    with pytest.raises(ValueError, match="geometry and budgets"):
        module.apply(path)
