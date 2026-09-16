import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "operating_readiness", ROOT / "tools/automation/operating-readiness.py"
)
READINESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(READINESS)


def test_city_without_checked_in_bundle_uses_all_tracked_evidence():
    city = READINESS.audit_city("edea")
    assert city["evidence"]["assets"] == 52
    assert city["compiled"]["erp_profile"] == "valid"
    assert city["compiled"]["components"]["instances"] == 1
    assert city["compiled"]["supervision"]["equipment"] > 0
    assert city["compiled"]["erp_full_plan"]["status"] == "generate-on-demand"
