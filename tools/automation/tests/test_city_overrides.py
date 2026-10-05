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
    with pytest.raises(ValueError, match="support operations.habd"):
        module.apply(path)


def test_charging_recovery_prices_repeated_equipment_without_changing_fleet(tmp_path):
    source = ROOT / "cities/catalogue/west-asia/Egypt/Asyut/design.toml"
    path = tmp_path / "design.toml"
    path.write_bytes(source.read_bytes())
    baseline = tomllib.loads(path.read_text())
    old = baseline["costs"]["technology_basis"]["station_charging_cabinet_count"]
    (tmp_path / "design-overrides.toml").write_text(
        f'[charging]\nstation_cabinet_count={old + 1}\nbasis="Degraded-case recovery test"\n'
    )
    assert module.apply(path)
    current = tomllib.loads(path.read_text())
    assert current["lines"] == baseline["lines"]
    assert current["fleets"] == baseline["fleets"]
    assert current["depots"] == baseline["depots"]
    assert current["costs"]["charging_microgrid_usd"] == round(baseline["costs"]["charging_microgrid_usd"] * (old + 1) / old)
    assert current["costs"]["total_usd"] - baseline["costs"]["total_usd"] == (
        current["costs"]["charging_microgrid_usd"] - baseline["costs"]["charging_microgrid_usd"]
        + current["costs"]["epc_overhead_usd"] - baseline["costs"]["epc_overhead_usd"]
    )
    first = path.read_bytes()
    assert not module.apply(path)
    assert path.read_bytes() == first


@pytest.mark.parametrize("count", [0, 9, True, 1.5])
def test_unbounded_or_noninteger_charging_recovery_is_rejected(tmp_path, count):
    path = tmp_path / "design.toml"
    path.write_text('[[lines]]\nname="line-1"\n')
    import json
    (tmp_path / "design-overrides.toml").write_text(
        f'[charging]\nstation_cabinet_count={json.dumps(count)}\nbasis="Test"\n'
    )
    with pytest.raises(ValueError, match="1–8"):
        module.apply(path)
