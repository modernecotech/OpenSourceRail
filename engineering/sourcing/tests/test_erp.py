from copy import deepcopy
import pytest
from engineering.sourcing.model import record
from engineering.sourcing.erp import delivery_drafts,build_rfq_drafts


def requirement(quantity=None):
    return record("requirement",candidate_id="a"*64,input_id="b"*64,namespace="station-account",requirement_key="doors-account",
        description="retained door account",category="doors-glazing",quantity=quantity,quantity_unit="each" if quantity else None,
        occurrence_ids=[],physical_scopes=["account/doors"],procurement_scope="mixed-subtotal-account-per-car")


def test_disabled_exports_preserve_unknown_counts_and_active_orders():
    order={"order_id":"WO-EXISTING","candidate_id":"c"*64,"docstatus":1,"items":[{"qty":99}]}
    saved=deepcopy(order)
    r=delivery_drafts([requirement()],existing_orders=[order])
    assert order==saved and r["active_order_mutations"]==0
    assert r["items"][0]["disabled"]==1 and r["BOM"]["items"]==[]
    assert r["BOM"]["total_cost"] is None and r["send_supplier_emails"] is False
    assert r["RFQs"][0]["requested_items"][0]["quantity"] is None
    assert r["existing_order_reviews"][0]["mutation_allowed"] is False


def test_mixed_candidate_assessment_rejected():
    a=record("assessment",candidate_id="c"*64,requirement_id=requirement()["record_id"],product_id="d"*64)
    with pytest.raises(ValueError,match="candidate"):build_rfq_drafts([requirement()],[a])
