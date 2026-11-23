"""Exercise procurement, service, feeder and cost propagation together."""

from hashlib import sha256
from io import BytesIO
from zipfile import ZIP_STORED, ZipFile
import json
import pytest
from cities.Baghdad import airport_finance, airport_integration as integration


@pytest.fixture(scope="module")
def opening():
    return integration.build()


def test_packet_connects_planning_finance_and_sources(opening):
    case, finance = opening["opening"], opening["finance"]
    assert opening["selection"]["planning_configuration"] and not opening["selection"]["physical_accepted"]
    assert case["controls"]["grid_protection_gateways"] == case["bundle"]["grid_sites"]
    assert (
        case["controls"]["section_control_gateways"]
        == case["section_power"]["procurement"]["dc_outgoing_breaker_circuits"]
    )
    for name, row in finance["market_scenarios"].items():
        other = opening["reference_finance"]["market_scenarios"][name]
        assert row["passenger_km_year"] == other["passenger_km_year"]
        assert row["paid_journeys_day"] == other["paid_journeys_day"]
    for path, digest in case["sources"].items():
        if "#" not in path:
            assert sha256((integration.ROOT / path).read_bytes()).hexdigest() == digest
    rows = finance["phased_cash"]["annual"]
    assert sum(r["capital"] for r in rows) == pytest.approx(finance["priced_capital_usd_m"]["base"])
    assert sum(r["borrowing"] - r["principal"] for r in rows) == pytest.approx(0)
    assert sum(r["operations"] for r in rows) == pytest.approx(
        30 * finance["market_scenarios"]["central"]["annual_opex_usd_m"]
    )
    packet = integration.make_packet(opening)
    assert integration.make_packet(opening) == packet
    with ZipFile(BytesIO(packet)) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["candidate_id"] == case["candidate_id"]
        assert all(sha256(archive.read(k)).hexdigest() == v for k, v in manifest["sha256"].items())


def test_packet_verification_accepts_alternative_compression_and_detects_changed_members(opening):
    original = BytesIO(integration.make_packet(opening))
    with ZipFile(original) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}

    def repack(items):
        output = BytesIO()
        with ZipFile(output, "w", compression=ZIP_STORED) as archive:
            for name, value in reversed(items.items()):
                archive.writestr(name, value)
        return output

    assert integration.same_packet(original, repack(members))
    members["bom.csv"] = bytes(len(members["bom.csv"]))
    assert not integration.same_packet(original, repack(members))
    del members["bom.csv"]
    assert not integration.same_packet(original, repack(members))


def test_price_return_changes_life_cost_and_cash(opening):
    case = opening["opening"]
    f = airport_finance.quote_form(case)
    f["lots"]["trainsets"] = {
        "direct_price_usd_m": case["scopes_usd_m"]["Fleet, including spare sets"] + 1,
        "annual_maintenance_change_usd_m": 0.25,
        "renewal_changes_usd_m": {"25": -0.5},
        "review_reference": "synthetic exact-scope regression",
    }
    revised = integration.build(quote=f)
    a, b = [data["finance"]["market_scenarios"]["central"] for data in (opening, revised)]
    assert revised["selection"]["physical_candidate_id"] == opening["selection"]["physical_candidate_id"]
    assert b["capital_usd_m"] - a["capital_usd_m"] == pytest.approx(1.326)
    assert b["annual_support_usd_m"] - a["annual_support_usd_m"] == pytest.approx(0.25)
    assert b["priced_whole_life_30y_usd_m"] - a["priced_whole_life_30y_usd_m"] == pytest.approx(
        1.326 + sum(0.25 / (1.04**y) for y in range(1, 31)) - 0.5 / 1.04**25
    )
    f["opening_candidate_id"] = "unrelated"
    with pytest.raises(ValueError, match="match the opening"):
        integration.build(quote=f)


def test_complete_weight_return_recalculates_train_and_civil(opening):
    mass = json.loads(json.dumps(opening["assembly"]["mass_account"]["weight_return"]))
    for key, kg in zip(
        mass["train_mass_groups"], [35000, 22000, 25000, 28000, 12000, 9000, 72000], strict=True
    ):
        mass["train_mass_groups"][key] = {"kg": kg, "evidence": "synthetic test only"}
    revised = integration.build(mass_form=mass)["opening"]
    base = opening["opening"]
    assert revised["power"]["vehicle"]["mass_t"] == pytest.approx(203)
    assert revised["candidate_id"] != base["candidate_id"]
    assert revised["power"]["traction"]["required_force_kn"] > base["power"]["traction"]["required_force_kn"]
    assert revised["power"]["energy"]["annual_grid_gwh"] > base["power"]["energy"]["annual_grid_gwh"]
    assert revised["civil_load"]["candidate_crowd_train_t"] == 203
    assert (
        revised["scopes_usd_m"]["Viaduct, piers and foundations"]
        > base["scopes_usd_m"]["Viaduct, piers and foundations"]
    )
    assert (
        revised["section_power"]["braking_reception"]["kinetic_kwh"]
        > base["section_power"]["braking_reception"]["kinetic_kwh"]
    )
