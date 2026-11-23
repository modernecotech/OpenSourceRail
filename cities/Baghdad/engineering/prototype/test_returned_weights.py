from copy import deepcopy

import pytest

from cities.Baghdad import airport_integration
from cities.Baghdad.engineering.commissioning import feeder
from cities.Baghdad.engineering.prototype import car, commercial, returned_weights, weights


@pytest.fixture(scope="module")
def article_and_service():
    parent = airport_integration.build()
    return car.build(parent), parent["service"]


def test_partial_keeps_dependent_results_unknown(article_and_service):
    article, service = article_and_service
    form = weights.form(article)
    result = returned_weights.assess(article, form, service=service, financial_return={"old": 12})
    assert result["result"] == "partial return" and result["weights"]["missing"]
    assert result["dependent_input_ids"]["financial"] == car.identity({"old": 12})
    assert all(result[k] is None for k in ("candidate_id", "electrical", "commercial", "templates"))
    assert result["record_kind"] == "unclassified" and not result["physical_accepted"]
    with pytest.raises(ValueError, match="origin"):
        returned_weights.assess(article, {"record_kind": "accepted", "weights": form}, service=service)


def test_reweighted_opening_has_its_own_procurement_and_test_forms(article_and_service, tmp_path):
    article, service = article_and_service
    mass_folder = tmp_path / "weighing"
    quote_folder = tmp_path / "tender"
    mass_folder.mkdir()
    quote_folder.mkdir()
    form = weights.form(article)
    data = b"Software fixture for seven declared groups"
    (mass_folder / "mass.txt").write_bytes(data)
    form["documents"]["mass.txt"] = {"issuer": "test", "date": "2026-11-23", "sha256": car.sha(data)}
    for row, kg in zip(
        form["mass_groups"]["train_mass_groups"].values(),
        (35000, 22000, 25000, 28000, 12000, 9000, 72000),
        strict=True,
    ):
        row.update(kg=kg, evidence="mass.txt")
    wrapped = {"record_kind": "synthetic-fixture", "weights": form}

    def run(**kwargs):
        return returned_weights.assess(
            article, wrapped, directory=mass_folder, service=service, **kwargs
        )

    case = run()
    assert case["candidate_id"] != article["candidate_id"]
    assert case["weights"]["opening"]["power"]["vehicle"]["mass_t"] == 203
    assert case["electrical"]["binding"]["opening_candidate_id"] == case["candidate_id"]
    assert case["record_kind"] == "synthetic-fixture" and not case["physical_accepted"]
    forms = case["templates"]
    for typ in ("hot_test", "feeder"):
        assert set(forms[typ]) == set(feeder.OPTIONS)
        for option, f in forms[typ].items():
            assert f["scope"]["option"] == option and f["binding"] == case["electrical"]["binding"]
    money = deepcopy(forms["finance"])
    assert money["opening_evaluation_id"] == case["opening_evaluation_id"]
    attachment = b"Synthetic funding allocation"
    (quote_folder / "budget.txt").write_bytes(attachment)
    money["documents"]["budget.txt"] = {
        "issuer": "test",
        "date": "2026-11-23",
        "sha256": car.sha(attachment),
    }
    money["public_allocations_usd_m"]["3"] = {"document": "budget.txt", "amount": 10}
    revised = run(
        financial_return=money,
        financial_directory=quote_folder,
        feeder_return=forms["feeder"]["six_site_parallel"],
    )
    assert revised["commercial"]["annual_cash"][2]["documented_allocation_usd_m"] == 10
    assert revised["electrical"]["return"] != case["electrical"]["return"]
    assert revised["weights"]["evaluation_id"] == case["weights"]["evaluation_id"]
    assert revised["evaluation_id"] != case["evaluation_id"]
    assert not revised["authorised_for_purchase"] and not revised["energisation_authorised"]
    with pytest.raises(ValueError, match="another physical design"):
        run(financial_return=commercial.form(article["opening"]))
    with pytest.raises(ValueError):
        run(feeder_return=feeder.return_form(article["opening"]))

    scales = form["axle_weighing"]
    scales.update(
        tare_document="mass.txt",
        loaded_document="mass.txt",
        balance_limit_document="mass.txt",
        permitted_total_discrepancy_kg=0.1,
    )
    for i, row in enumerate(scales["readings"].values()):
        row.update(tare_kg=131000 / 24, loaded_kg=203000 / 24 + (500 if i % 2 else -500))
    distributed = run()
    assert distributed["candidate_id"] != case["candidate_id"]
    assert distributed["weights"]["axle_civil"]["measured_max_axle_kg"] == pytest.approx(
        203000 / 24 + 500
    )
    assert distributed["templates"]["finance"]["candidate_id"] == distributed["candidate_id"]
    assert distributed["electrical"]["binding"]["opening_candidate_id"] == distributed["candidate_id"]
    assert not distributed["physical_accepted"]

    form["axle_weighing"] = weights.form(article)["axle_weighing"]
    form["mass_groups"]["train_mass_groups"]["crowd_payload"]["kg"] = 1_000_000
    held = run()
    assert held["result"] == "feeder design held" and held["weights"]["engineering_hold"]
    assert held["electrical"] is None and held["commercial"] is None and held["templates"] is None
