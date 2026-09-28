from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "deployment/erpnext/apps/osr_erpnext"))

from osr_erpnext.lifecycle_governance import (  # noqa: E402
    identity_record,
    make_city_package,
    qr_payload,
    validate_city_package,
    validate_resolver_base,
    validate_template,
)


def template() -> dict:
    return json.loads(
        (ROOT / "deployment/erpnext/config/lifecycle-governance.json").read_text()
    )


def test_template_and_cross_language_identity_fixture_are_exact():
    clean = validate_template(template())
    fixture = json.loads((ROOT / "tests/fixtures/asset-identity.json").read_text())
    assert identity_record("samawah", "SAM-ST-001", "rev:abc123") == fixture
    assert qr_payload(fixture, "https://assets.operator.example") == (
        "https://assets.operator.example/id/osr/samawah/asset/SAM-ST-001"
    )
    assert clean["qr_identity"]["resolver_base"] is None


def test_city_package_is_deterministic_non_personal_and_fail_closed():
    clean = validate_template(template())
    first = make_city_package(
        clean,
        city="samawah",
        project="samawah-pilot",
        revision="rev:abc123",
        asset_ids=["SAM-ST-001", "SAM-VH-001"],
    )
    second = make_city_package(
        clean,
        city="samawah",
        project="samawah-pilot",
        revision="rev:abc123",
        asset_ids=["SAM-ST-001", "SAM-VH-001"],
    )
    assert first == second
    assert first["asset_identity_inventory"] == {
        "count": 2,
        "sha256": first["asset_identity_inventory"]["sha256"],
        "printable_labels": 0,
        "state": "blocked-until-operator-https-resolver-and-physical-binding",
        "resolver_base": None,
        "optional_gs1_mapping": "unassigned",
    }
    validate_city_package(first)


@pytest.mark.parametrize(
    "value",
    [
        "http://assets.example",
        "https://user@assets.example",
        "https://assets.example/path",
        "https://assets.example?token=x",
        "https://assets.example/#fragment",
    ],
)
def test_resolver_rejects_non_origins_and_secrets(value):
    with pytest.raises(ValueError):
        validate_resolver_base(value)


def test_template_rejects_authority_drift_duplicate_roles_and_deployed_resolver():
    changed = template()
    changed["qr_identity"]["authority"] = "work-authority"
    with pytest.raises(ValueError):
        validate_template(changed)

    changed = template()
    changed["role_templates"].append(deepcopy(changed["role_templates"][0]))
    with pytest.raises(ValueError):
        validate_template(changed)

    changed = template()
    changed["qr_identity"]["resolver_base"] = "https://assets.example"
    with pytest.raises(ValueError):
        validate_template(changed)


def test_identity_and_package_reject_unknown_fields_tampering_and_duplicates():
    fixture = json.loads((ROOT / "tests/fixtures/asset-identity.json").read_text())
    fixture["command"] = "open"
    with pytest.raises(ValueError):
        qr_payload(fixture, "https://assets.example")

    package = make_city_package(
        template(), city="samawah", project="pilot", revision="r1", asset_ids=["A-1"]
    )
    package["asset_identity_inventory"]["printable_labels"] = 1
    with pytest.raises(ValueError):
        validate_city_package(package)

    with pytest.raises(ValueError):
        make_city_package(
            template(),
            city="samawah",
            project="pilot",
            revision="r1",
            asset_ids=["A-1", "A-1"],
        )
