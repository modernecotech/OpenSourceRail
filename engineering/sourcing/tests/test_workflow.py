from pathlib import Path
import pytest
from engineering.sourcing.model import record,validate_record
from engineering.sourcing.database import Store
from engineering.sourcing.workflow import evaluate


def setup_records(store, scopes=("study/panel/glass",), unknown_order=False):
    s=record("source",publisher="synthetic test catalogue",url="https://example.test/glass",retrieved_at="2026-10-29",
        access="test-fixture",source_kind="manufacturer_catalogue")
    p=record("product",product_key="synthetic-glass",manufacturer="synthetic",part_number="GLASS",category="raw-glass-fabric",
        description="glass reinforcement",source_ids=[s["record_id"]],supply_scope="raw-material",specifications={})
    o=record("offer",product_id=p["record_id"],source_id=s["record_id"],price_date="2026-10-29",currency="GBP",quantity_unit="m",
        minimum_order_quantity=None if unknown_order else "1",order_multiple=None if unknown_order else "1",source_class="B",tax_basis="excluded",tax_rate=None,valid_until=None,
        tiers=[dict(minimum_quantity="0",maximum_quantity=None,unit_price="4.05")])
    store.insert_many([o,p,s])
    reqs=[record("requirement",candidate_id="a"*64,input_id="b"*64,namespace="manufacturing-study",requirement_key="glass-"+str(i),
        description="glass",category="body-materials",priority=3,quantity="1",quantity_unit="m",occurrence_ids=[],physical_scopes=[scope],
        procurement_scope="raw-material",identifiers={},constraints=[]) for i,scope in enumerate(scopes)]
    bindings=[dict(candidate_id="a"*64,requirement_id=r["record_id"],product_id=p["record_id"]) for r in reqs]
    return reqs,bindings


def test_real_workflow_price_overlay_and_exact_replay(tmp_path):
    with Store(tmp_path/"records.sqlite") as store:
        reqs,bindings=setup_records(store)
        r=evaluate(store,reqs,bindings=bindings,as_of="2026-10-29",target_currency="GBP")
        assert r["summary"]["known_catalogue_subtotal"]=="4.05"
        assert r["summary"]["priced_requirement_count"]==1
        assert r["candidate_id"]==reqs[0]["candidate_id"]
        overlay=store.get(r["overlay_id"],"overlay")
        assert overlay["complete_installed_total"] is None and overlay["mass_or_geometry_mutated"] is False
        assert evaluate(store,reqs,bindings=bindings,as_of="2026-10-29",target_currency="GBP")==r
        validate_record(r,"run")


def test_family_lead_does_not_become_priced_or_selected(tmp_path):
    with Store(tmp_path/"records.sqlite") as store:
        reqs,bindings=setup_records(store)
        r=evaluate(store,reqs,as_of="2026-10-29",target_currency="GBP")
        assert r["summary"]["known_catalogue_subtotal"] is None
        assert r["summary"]["RFQ_drafts"]==1 and r["integrated_winner"] is None
        assert r["summary"]["redesign_tasks"]==1
        rfq=store.get(r["rfq_ids"][0],"rfq")
        assert rfq["send_supplier_emails"] is False and rfq["submission_allowed"] is False


def test_parent_child_cost_scope_overlap_rejected(tmp_path):
    with Store(tmp_path/"records.sqlite") as store:
        reqs,bindings=setup_records(store,("study/panel","study/panel/glass"))
        with pytest.raises(ValueError,match="parent/child"):evaluate(store,reqs,bindings=bindings,as_of="2026-10-29",target_currency="GBP")


def test_partial_lifecycle_never_complete(tmp_path):
    with Store(tmp_path/"records.sqlite") as store:
        reqs,bindings=setup_records(store)
        # Same currency avoids fabricating an FX rate for this synthetic contract.
        r=evaluate(store,reqs,as_of="2026-10-29",target_currency="USD",
            service_context=dict(cars=6,car_length_m=17.,normal_places_per_car=46,headway_s=120.,station_spacing_m=2000.,fleet_trainsets=3,estimate_date="2026-10-29"))
        assert r["lifecycle"]["complete_installed_whole_life_cost_usd"] is None
        assert len(r["lifecycle"]["missing_whole_life_scopes"])==12


def test_unknown_moq_listing_coverage_is_not_order_coverage(tmp_path):
    with Store(tmp_path/"records.sqlite") as store:
        reqs,bindings=setup_records(store,unknown_order=True)
        r=evaluate(store,reqs,bindings=bindings,as_of="2026-10-29",target_currency="GBP")
        assert r["summary"]["known_catalogue_subtotal"] is None
        assert r["summary"]["known_listed_extension_subtotal"]=="4.05"
        assert r["summary"]["order_price_requirement_count"]==0
        assert r["summary"]["listed_price_requirement_count"]==1
        assert r["summary"]["RFQ_drafts"]==1
        overlay=store.get(r["overlay_id"],"overlay")
        assert overlay["listed_extension_is_cost_bound"] is False


def test_requirement_order_does_not_change_run_identity(tmp_path):
    with Store(tmp_path/"records.sqlite") as store:
        reqs,bindings=setup_records(store,("study/a","study/b"))
        a=evaluate(store,reqs,bindings=bindings,as_of="2026-10-29",target_currency="GBP")
        b=evaluate(store,list(reversed(reqs)),bindings=list(reversed(bindings)),as_of="2026-10-29",target_currency="GBP")
        assert a==b
