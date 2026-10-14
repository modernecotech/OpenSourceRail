import pytest
from engineering.design_engine.economics import (
    installed_objectives,
    schedule,
    REQUIRED_SCOPES,
)
from engineering.design_engine.review import ReviewStore
from engineering.design_engine.store import Store
import hashlib


@pytest.fixture
def quotations(tmp_path):
    identity = dict(
        schema="osr-design-identity/1",
        city="samawah",
        project="economics-fixture",
        environment="simulation",
        configuration_revision="fixture-revision",
        baseline_sha256="a" * 64,
        run_id=None,
        asset_id=None,
        part_id=None,
    )
    applicability = dict(
        candidate_id="fixture-candidate",
        physical_part_id=None,
        material_batch=None,
        definition_sha256="b" * 64,
    )
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    source = evidence / "fixture-quotation.txt"
    source.write_text(
        "Test fixture supplier quotation: quantity 2, unit price 100 USD. No binding procurement."
    )
    reference = dict(
        path=source.name, sha256=hashlib.sha256(source.read_bytes()).hexdigest()
    )
    reviews = ReviewStore(Store(tmp_path / "store"))

    def quote(scope):
        payload = dict(
            supplier="Test fixture supplier",
            place="Iraq",
            currency="USD",
            date="2026-10-13",
            scope=scope,
            line_items=[
                dict(description="Fixture item", quantity=2, unit="ea", unit_price=100)
            ],
            source_reference=reference,
        )
        row = reviews.submit(
            "samawah",
            "simulation",
            "quotation",
            payload,
            "fixture-author",
            "economics-fixture-" + scope,
            identity=identity,
            applicability=applicability,
        )
        reviews.verify(
            row["id"],
            row["revision"],
            dict(
                username="fixture-reviewer", roles=["approver"], city_scopes=["samawah"]
            ),
            city="samawah",
            environment="simulation",
            evidence_root=evidence,
            identity=identity,
            applicability=applicability,
        )
        return next(
            value
            for value in reviews.list("samawah", "simulation")
            if value["id"] == row["id"]
        )

    return quote, dict(
        place="Iraq",
        currency="USD",
        as_of="2026-10-13",
        identity=identity,
        applicability=applicability,
    )


def test_partial_quotes_never_close_missing_hardware_qa_or_lifecycle_cost(quotations):
    quote, arguments = quotations
    result = installed_objectives([quote("materials")], **arguments)
    assert (
        result["known_scope_subtotal"] == 200 and result["scope_complete_total"] is None
    )
    assert "joints-supports-retention-seals" in result["missing_scopes"]
    assert result["global_finance_adopted"] is False


def test_complete_cost_still_requires_complete_physical_inventory(quotations):
    quote, arguments = quotations
    rows = [quote(s) for s in REQUIRED_SCOPES]
    assert installed_objectives(rows, **arguments)["scope_complete_total"] is None
    assert (
        installed_objectives(rows, **arguments, complete_installed_inventory=True)[
            "scope_complete_total"
        ]
        == 2000
    )
    with pytest.raises(ValueError):
        installed_objectives([*rows, rows[0]], **arguments)


def test_one_crane_cannot_be_used_by_two_fronts_at_once():
    tasks = [
        dict(
            id=name,
            duration_hours=3,
            predecessors=[],
            resources={"crane": 1},
            productivity_source="explicit test planning input",
        )
        for name in ("A", "B")
    ]
    result = schedule(tasks, [dict(id="crane", capacity=1)])
    assert result["makespan_hours"] == 6
    assert result["tasks"][0]["end_hour"] <= result["tasks"][1]["start_hour"]
    assert schedule(tasks, [dict(id="crane", capacity=2)])["makespan_hours"] == 3


def test_cycles_missing_productivity_and_free_equipment_are_rejected():
    task = dict(
        id="A",
        duration_hours=3,
        predecessors=[],
        resources={"crane": 1},
        productivity_source="source",
    )
    for bad in [
        {**task, "predecessors": ["A"]},
        {**task, "productivity_source": None},
        {**task, "resources": {"unpriced-unavailable-crane": 1}},
    ]:
        with pytest.raises(ValueError):
            schedule([bad], [dict(id="crane", capacity=1)])


def test_closures_procurement_and_crane_availability_bound_actual_schedule():
    task = dict(
        id="lift",
        duration_hours=3,
        release_hour=4,
        closure_windows=[[0, 6], [10, 16]],
        predecessors=[],
        resources={"crane": 1, "crew": 1},
        productivity_source="explicit planning fixture",
    )
    resources = [
        dict(id="crane", capacity=1, available_windows=[[11, 15]]),
        dict(id="crew", capacity=1),
    ]
    result = schedule([task], resources)
    assert (
        result["tasks"][0]["start_hour"] == 11 and result["tasks"][0]["end_hour"] == 14
    )
    with pytest.raises(ValueError):
        schedule([{**task, "duration_hours": 5}], resources)
    with pytest.raises(ValueError):
        schedule([], resources)
