"""Planning price refresh cannot rewrite the evidence of previous execution."""
import importlib.util
import re
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("capex_refresh", ROOT / "tools/automation/recalculate-city-capex.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_outdated_fleet_price_is_corrected_without_rebinding_solver_evidence(tmp_path):
    city = ROOT / "cities/catalogue/west-asia/Iraq/Samawah"
    path = tmp_path / "design.toml"
    original = (city / "design.toml").read_text()
    path.write_text(re.sub(r"(?m)^rolling_stock_usd\s*=.*$", "rolling_stock_usd = 1", original))
    (tmp_path / "samawah.toml").write_bytes((city / "samawah.toml").read_bytes())
    evidence = tmp_path / "engineering/simulation/validation-summary.json"
    evidence.parent.mkdir(parents=True)
    historical = b'{"design_sha256":"retained-original-input","passed":true}\n'
    evidence.write_bytes(historical)
    before = tomllib.loads(path.read_text())
    assert module.recalculate(path)
    after = tomllib.loads(path.read_text())
    expected = sum(f["trainset_count"] for f in after["fleets"]) * module.CAPEX["trainset_unit_usd"]["light-metro-3car"]
    assert after["costs"]["rolling_stock_usd"] == expected
    before.pop("costs"); after.pop("costs")
    assert before == after
    assert evidence.read_bytes() == historical
