"""Evidence scope is an exact match, including unknown optional dimensions."""

import hashlib
from copy import deepcopy

import pytest

from engineering.design_engine.contracts import canonical
from engineering.design_engine.economics import REQUIRED_SCOPES, installed_objectives
from engineering.design_engine.review import (
    ReviewStore,
    normalize_record_scope,
    record_applicability,
)
from engineering.design_engine.store import Store


def design_identity(**changes):
    value = dict(
        schema="osr-design-identity/1",
        city="samawah",
        project="scope-test-project",
        environment="simulation",
        configuration_revision="revision-1",
        baseline_sha256="a" * 64,
        run_id="scope-test-run",
        asset_id="test-car",
        part_id="test-panel",
    )
    return {**value, **changes}


def evidence_scope(**changes):
    return {
        "candidate_id": "test-candidate",
        "physical_part_id": "test-panel",
        "material_batch": "test-batch",
        "definition_sha256": "b" * 64,
        **changes,
    }


def evidence(tmp_path):
    root = tmp_path / "evidence"
    root.mkdir(exist_ok=True)
    document = root / "fixture.txt"
    document.write_text(
        "Test fixture only: retained source, never engineering acceptance"
    )
    return root, dict(
        path=document.name, sha256=hashlib.sha256(document.read_bytes()).hexdigest()
    )


def verified_quote(
    tmp_path, *, quote_scope="materials", identity=None, applicability=None
):
    identity = identity or design_identity()
    applicability = applicability or evidence_scope()
    root, reference = evidence(tmp_path)
    reviews = ReviewStore(Store(tmp_path / "store"))
    row = reviews.submit(
        identity["city"],
        identity["environment"],
        "quotation",
        dict(
            supplier="Test fixture supplier",
            place="Iraq",
            date="2026-10-13",
            currency="USD",
            scope=quote_scope,
            line_items=[
                dict(description="Test fixture", quantity=2, unit="ea", unit_price=100)
            ],
            source_reference=reference,
        ),
        "fixture-author",
        "scope-test-key-" + quote_scope,
        identity=identity,
        applicability=applicability,
    )
    verification = reviews.verify(
        row["id"],
        row["revision"],
        dict(username="fixture-reviewer", roles=["approver"], city_scopes=["samawah"]),
        city=identity["city"],
        environment=identity["environment"],
        evidence_root=root,
        identity=identity,
        applicability=applicability,
    )
    row = next(r for r in reviews.list("samawah", "simulation") if r["id"] == row["id"])
    return reviews, row, verification


def objectives(rows, **changes):
    arguments = dict(
        place="Iraq",
        currency="USD",
        as_of="2026-10-13",
        identity=design_identity(),
        applicability=evidence_scope(),
    )
    arguments.update(changes)
    return installed_objectives(rows, **arguments)


def test_full_identity_and_applicability_survive_submission_and_separate_verification(
    tmp_path,
):
    _, row, verification = verified_quote(tmp_path)
    assert row["identity"] == design_identity()
    _, expected = normalize_record_scope(design_identity(), evidence_scope())
    assert row["applicability"] == expected == verification["applicability"]
    assert verification["identity"] == row["identity"]
    assert record_applicability(row, design_identity(), evidence_scope())["eligible"]
    assert objectives([row])["known_scope_subtotal"] == 200
    assert objectives([row])["scope_complete_total"] is None
    assert verification["technical_applicability_accepted"] is False
    assert verification["independent_acceptance"] is False
    assert verification["physical_release"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("project", "another-project"),
        ("configuration_revision", "revision-2"),
        ("baseline_sha256", "c" * 64),
        ("run_id", "another-run"),
        ("asset_id", "another-car"),
        ("part_id", "another-panel"),
        ("environment", "physical"),
        ("city", "mosul"),
    ],
)
def test_other_identity_cannot_contribute_to_candidate_cost(tmp_path, field, value):
    _, row, _ = verified_quote(tmp_path)
    target = design_identity(**{field: value})
    target_app = evidence_scope()
    if field == "part_id":
        target_app["physical_part_id"] = value
    result = objectives([row], identity=target, applicability=target_app)
    assert result["known_scope_subtotal"] is None
    assert result["priced_scopes"] == {}
    assert result["rejected_records"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("candidate_id", "another-candidate"),
        ("physical_part_id", "another-panel"),
        ("material_batch", "another-batch"),
        ("definition_sha256", "c" * 64),
        ("candidate_id", None),
        ("material_batch", None),
        ("definition_sha256", None),
    ],
)
def test_other_candidate_part_batch_or_definition_is_not_an_applicable_quote(
    tmp_path, field, value
):
    _, row, _ = verified_quote(tmp_path)
    identity = (
        design_identity(part_id=None)
        if field == "physical_part_id"
        else design_identity()
    )
    result = objectives(
        [row], identity=identity, applicability=evidence_scope(**{field: value})
    )
    assert result["known_scope_subtotal"] is None
    assert result["rejected_records"]


def test_null_candidate_is_unknown_and_cannot_act_as_a_wildcard(tmp_path):
    _, row, _ = verified_quote(
        tmp_path, applicability=evidence_scope(candidate_id=None)
    )
    assert objectives([row])["known_scope_subtotal"] is None
    assert (
        objectives([row], applicability=evidence_scope(candidate_id=None))[
            "known_scope_subtotal"
        ]
        == 200
    )


def test_quotation_appraisal_without_explicit_identity_is_unknown_even_with_verified_quotes(
    tmp_path,
):
    _, row, _ = verified_quote(tmp_path)
    result = objectives(
        [row], identity=None, applicability=None, complete_installed_inventory=True
    )
    assert result["applicability_state"] == "unknown"
    assert result["known_scope_subtotal"] is None
    assert result["scope_complete_total"] is None


def test_complete_scoped_cost_still_needs_complete_installed_inventory(tmp_path):
    rows = [verified_quote(tmp_path, quote_scope=s)[1] for s in sorted(REQUIRED_SCOPES)]
    assert objectives(rows)["scope_complete_total"] is None
    assert (
        objectives(rows, complete_installed_inventory=True)["scope_complete_total"]
        == 2000
    )
    with pytest.raises(ValueError, match="duplicate"):
        objectives([*rows, rows[0]])


def test_city_only_or_changed_scope_cannot_verify_a_scoped_record(tmp_path):
    root, reference = evidence(tmp_path)
    reviews = ReviewStore(Store(tmp_path / "store"))
    row = reviews.submit(
        "samawah",
        "simulation",
        "material",
        dict(
            supplier="Fixture",
            grade="Fixture",
            batch="test-batch",
            conditions="Fixture",
            properties={"test": 1},
            source_reference=reference,
        ),
        "fixture-author",
        "scope-material-key",
        identity=design_identity(),
        applicability=evidence_scope(),
    )
    arguments = dict(city="samawah", environment="simulation", evidence_root=root)
    reviewer = dict(
        username="fixture-reviewer", roles=["approver"], city_scopes=["samawah"]
    )
    with pytest.raises(ValueError, match="exact retained"):
        reviews.verify(row["id"], row["revision"], reviewer, **arguments)
    with pytest.raises(ValueError, match="outside"):
        reviews.verify(
            row["id"],
            row["revision"],
            reviewer,
            **arguments,
            identity=design_identity(configuration_revision="revision-2"),
            applicability=evidence_scope()
        )
    with pytest.raises(ValueError, match="outside"):
        reviews.verify(
            row["id"],
            row["revision"],
            reviewer,
            **arguments,
            identity=design_identity(),
            applicability=evidence_scope(material_batch="different")
        )


def test_idempotency_and_record_revision_cover_full_identity_and_applicability(
    tmp_path,
):
    root, reference = evidence(tmp_path)
    reviews = ReviewStore(Store(tmp_path / "store"))
    payload = dict(
        supplier="Fixture",
        grade="Fixture",
        batch="test-batch",
        conditions="Fixture",
        properties={"test": 1},
        source_reference=reference,
    )
    arguments = (
        "samawah",
        "simulation",
        "material",
        payload,
        "fixture-author",
        "scope-material-key",
    )
    first = reviews.submit(
        *arguments, identity=design_identity(), applicability=evidence_scope()
    )
    assert (
        reviews.submit(
            *arguments, identity=design_identity(), applicability=evidence_scope()
        )["id"]
        == first["id"]
    )
    with pytest.raises(ValueError, match="idempotency"):
        reviews.submit(
            *arguments,
            identity=design_identity(project="another-project"),
            applicability=evidence_scope()
        )
    with pytest.raises(ValueError, match="idempotency"):
        reviews.submit(
            *arguments,
            identity=design_identity(),
            applicability=evidence_scope(candidate_id="another-candidate")
        )
    second = reviews.submit(
        *arguments[:-1],
        "scope-material-key-2",
        identity=design_identity(),
        applicability=evidence_scope(candidate_id="another-candidate")
    )
    assert second["revision"] != first["revision"]


def test_additive_migration_preserves_legacy_bytes_and_never_backfills_scope(tmp_path):
    store = Store(tmp_path / "store")
    payload = canonical(
        dict(
            place="Iraq",
            currency="USD",
            date="2026-10-13",
            scope="materials",
            line_items=[dict(quantity=2, unit_price=100)],
            source_reference={},
        )
    ).decode()
    with store.connect() as connection:
        connection.execute("""CREATE TABLE review_records(
            id TEXT PRIMARY KEY,city TEXT NOT NULL,environment TEXT NOT NULL,kind TEXT NOT NULL,
            creator TEXT NOT NULL,created TEXT NOT NULL,revision TEXT NOT NULL,payload TEXT NOT NULL,
            state TEXT NOT NULL,verifier TEXT,verification TEXT)""")
        connection.execute(
            "INSERT INTO review_records VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                "legacy-record",
                "samawah",
                "simulation",
                "quotation",
                "fixture-author",
                "old-created",
                "old-revision",
                payload,
                "verified-record",
                "fixture-reviewer",
                canonical(
                    dict(scope=dict(city="samawah", environment="simulation"))
                ).decode(),
            ),
        )
    reviews = ReviewStore(store)
    rows = reviews.list("samawah", "simulation")
    assert len(rows) == 1
    assert rows[0]["scope_state"] == "legacy-unscoped"
    assert rows[0]["identity"] is None and rows[0]["applicability"] is None
    assert rows[0]["revision"] == "old-revision"
    assert rows[0]["state"] == "verified-record"
    assert objectives(rows)["known_scope_subtotal"] is None
    with store.connect() as connection:
        assert (
            connection.execute("SELECT payload FROM review_records").fetchone()[0]
            == payload
        )
    assert not record_applicability(rows[0], design_identity(), evidence_scope())[
        "eligible"
    ]


def test_verification_of_another_scope_cannot_be_attached_to_a_record(tmp_path):
    _, row, _ = verified_quote(tmp_path)
    altered = deepcopy(row)
    altered["verification"]["identity"]["project"] = "another-project"
    assert objectives([altered])["known_scope_subtotal"] is None
    altered = deepcopy(row)
    altered["verification"]["applicability"]["candidate_id"] = "another-candidate"
    assert objectives([altered])["known_scope_subtotal"] is None


def test_changed_record_content_cannot_reuse_a_verified_revision(tmp_path):
    _, row, _ = verified_quote(tmp_path)
    row["payload"]["line_items"][0]["unit_price"] = 999999
    result = objectives([row])
    assert result["known_scope_subtotal"] is None
    assert "scoped revision" in result["rejected_records"][0]["reason"]


def test_conflicting_identity_or_batch_and_unknown_fields_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="differs"):
        normalize_record_scope(design_identity(), {"project": "another-project"})
    with pytest.raises(ValueError, match="fields"):
        normalize_record_scope(design_identity(), {"physical_release": True})
    with pytest.raises(ValueError, match="digest"):
        normalize_record_scope(design_identity(), {"definition_sha256": "not-a-digest"})
    root, reference = evidence(tmp_path)
    reviews = ReviewStore(Store(tmp_path / "store"))
    with pytest.raises(ValueError, match="material_batch"):
        reviews.submit(
            "samawah",
            "simulation",
            "material",
            dict(
                supplier="Fixture",
                grade="Fixture",
                batch="another-batch",
                conditions="Fixture",
                properties={"test": 1},
                source_reference=reference,
            ),
            "fixture-author",
            "scope-material-key",
            identity=design_identity(),
            applicability=evidence_scope(),
        )
