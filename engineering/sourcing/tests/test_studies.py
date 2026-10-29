from engineering.sourcing.catalogue import seed
from engineering.sourcing.database import Store
from engineering.sourcing.model import identity, record
from engineering.sourcing.requirements import validate_requirements
from engineering.sourcing.studies import laminate_study_requirements
from engineering.sourcing.matching import match_products
from engineering.sourcing.publication import execute, publish, verify
import pytest


def test_source_linked_laminate_studies_keep_unknown_items_and_same_basis(tmp_path):
    with Store(tmp_path / "source.sqlite") as store:
        seed(store)
        studies = laminate_study_requirements(
            store, parent_candidate_id="a" * 64, source_input_id="b" * 64)
        assert len(studies) == 3
        assert len({study["candidate_id"] for study in studies}) == 3
        assert len({study["proposal"]["parent_candidate_id"] for study in studies}) == 1
        assert len({study["process"]["functional_basis_id"] for study in studies}) == 1
        for study in studies:
            validate_requirements(study["requirements"])
            assert study["complete_installed_mass_kg"] is None
            assert study["complete_installed_cost"] is None
            assert "adhesive:areal-quantity" in study["process"]["unknown_additional_quantities"]
            matches = match_products(study["requirements"], store.all("product"))
            cloth = [item for item in matches if item["product_key"] == "EC-GF-BA-600-127" and item["exact_product_identifier"]]
            resin = [item for item in matches if item["product_key"] == "EC-EP-IN2-S-1" and item["exact_product_identifier"]]
            assert len(cloth) == len(resin) == 1
            assert cloth[0]["status"] == "compatible"
            assert resin[0]["status"] == "compatible"
            if study["proposal"]["core"].get("product_key"):
                foam = [item for item in matches if item["product_key"] == "GURIT-CORECELL-M80"
                        and item["exact_product_identifier"]]
                assert len(foam) == 1 and foam[0]["status"] == "compatible"
                assert len(foam[0]["checks"]) == 4
                assert "rail allowables" in " ".join(study["limitations"])
                assert study["process"]["conditional_known_net_material_bounds_kg"] == {
                    "lower": "40.2" if study["proposal"]["recipe"] == "sandwich-600gsm" else "36.2",
                    "nominal": study["process"]["conditional_known_net_material_kg"],
                    "upper": "41.8" if study["proposal"]["recipe"] == "sandwich-600gsm" else "37.8",
                    "basis": "Finite identified material inputs only; declared source ranges applied where present",
                }
            else:
                assert not [item for item in matches if item["product_key"] == "GURIT-CORECELL-M80"]
        assert [study["process"]["conditional_known_net_material_kg"] for study in studies] == ["48", "41", "37"]
        assert identity(studies[0]["proposal"]) != identity(studies[1]["proposal"])
        study = studies[0]
        twin_input = {"schema": "osr-sourcing-twin-input/1", "payload": study,
                      "payload_id": identity(study), "origin": {"research_proposal": True}}
        request = {"as_of": "2026-10-29", "target_currency": "GBP",
                   "max_requirements_by_category": {"body-materials": 2}}
        result = execute(store, twin_input, request)
        assert twin_input["payload_id"] == identity(twin_input["payload"])
        assert result["evaluated_requirement_count"] == 2
        assert len(result["pending_requirement_ids"]) == len(study["requirements"]) - 2
        output = tmp_path / "packet"
        publish(store, result, twin_input, request, output)
        assert verify(output)["semantic_replay_executed"] is True


def test_laminate_study_rejects_nonhex_identity_and_duplicate_product_revision(tmp_path):
    with Store(tmp_path / "source.sqlite") as store:
        seed(store)
        with pytest.raises(ValueError, match="parent physical candidate"):
            laminate_study_requirements(store, parent_candidate_id="z" * 64, source_input_id="b" * 64)
        with pytest.raises(ValueError, match="digital-twin input identity"):
            laminate_study_requirements(store, parent_candidate_id="a" * 64, source_input_id="z" * 64)
        source = next(item for item in store.all("product") if item["product_key"] == "GURIT-CORECELL-M80")
        duplicate = {key: value for key, value in source.items() if key not in {"schema", "kind", "record_id"}}
        duplicate["part_number"] = "Conflicting Corecell M80 publication"
        store.put(record("product", **duplicate))
        with pytest.raises(ValueError, match="Unique immutable supplier product observation"):
            laminate_study_requirements(store, parent_candidate_id="a" * 64, source_input_id="b" * 64)


def test_material_evidence_revision_changes_evaluation_not_physical_candidate(tmp_path):
    with Store(tmp_path / "source.sqlite") as store:
        seed(store)
        original = laminate_study_requirements(
            store, parent_candidate_id="a" * 64, source_input_id="b" * 64)[1]
        source = next(item for item in store.all("product") if item["product_key"] == "GURIT-CORECELL-M80")
        duplicate = {key: value for key, value in source.items() if key not in {"schema", "kind", "record_id"}}
        duplicate["specifications"]["density_range_kg_m3"]["values"] = ["80", "90"]
        duplicate["specifications"]["density_min_kg_m3"]["value"] = "80"
        duplicate["specifications"]["density_max_kg_m3"]["value"] = "90"
        updated = record("product", **duplicate)
        store.put(updated)
        revised = laminate_study_requirements(
            store, parent_candidate_id="a" * 64, source_input_id="b" * 64,
            product_observations={"GURIT-CORECELL-M80": updated["record_id"]})[1]
        assert original["candidate_id"] == revised["candidate_id"]
        assert original["process"]["input_id"] != revised["process"]["input_id"]
        assert original["process"]["conditional_known_net_material_kg"] == "41"
        assert revised["process"]["conditional_known_net_material_kg"] == "41"
        assert revised["process"]["conditional_known_net_material_bounds_kg"]["lower"] == "40"
        assert revised["process"]["conditional_known_net_material_bounds_kg"]["upper"] == "42"
        matches = match_products(revised["requirements"], store.all("product"))
        core = [item for item in matches if item["product_key"] == "GURIT-CORECELL-M80"]
        assert len(core) == 1 and core[0]["product_id"] == updated["record_id"]
