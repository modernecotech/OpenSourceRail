from copy import deepcopy
import pytest
from engineering.design_search import railway_delivery as delivery,railway_bundle,design_grammar as grammar,system_inventory
from engineering.station_rail.common import identity


def test_candidate_delivery_reconciles_stock_manufacturing_and_disabled_ERP_drafts():
    body=grammar.build(grammar.parameters());bundle=railway_bundle.materialize(body)
    inventory=system_inventory.evaluate(body,bundle_id=bundle['candidate_id']);r=delivery.compile(bundle,body,inventory)
    assert r['candidate_id']==bundle['candidate_id'] and r['body_candidate_id']==body['candidate_id']
    assert r['engineering_BOM']==inventory['engineering_BOM'] and r['manufacturing_BOM']==inventory['manufacturing_BOM']
    assert len(r['ERPNext']['items'])==len(inventory['manufacturing_BOM'])
    assert all(x['disabled']==1 and x['unit_price'] is None for x in r['ERPNext']['items'])
    assert r['ERPNext']['BOM']['docstatus']==0 and not r['ERPNext']['posted'] and not r['ERPNext']['ready_for_import']
    assert r['complete_installed_cost_USD'] is None and r['physical_accepted'] is False
    changed=deepcopy(inventory);changed['candidate_id']='f'*64
    with pytest.raises(ValueError,match='different bundle'):delivery.compile(bundle,body,changed)


def test_box_facets_preserve_actual_source_volume_with_outward_orientation():
    import numpy as np
    p=dict(id='stock',at_m=[1.,2.,3.],size_m=[.2,.3,.4]);r=delivery._box_mesh(p,.024);points=np.array(r['vertices_m'])
    volume=sum(np.dot(points[a],np.cross(points[b],points[c]))/6 for a,b,c in r['triangles'])
    assert volume==pytest.approx(.024,abs=1e-14)


def test_delivery_cache_is_bound_to_native_tool_and_exact_CAD(monkeypatch):
    body=grammar.build(grammar.parameters());bundle=railway_bundle.materialize(body)
    inventory=system_inventory.evaluate(body,bundle_id=bundle['candidate_id'])
    cad=dict(candidate_id=body['candidate_id'],occurrences=[])
    monkeypatch.setattr(delivery,'ifc_tool_identity',lambda:dict(version='first',native_binary_sha256={'library':'a'}))
    first=delivery.cache_context(bundle,body,inventory,cad)
    monkeypatch.setattr(delivery,'ifc_tool_identity',lambda:dict(version='second',native_binary_sha256={'library':'b'}))
    second=delivery.cache_context(bundle,body,inventory,cad)
    assert first['cache_context_id']!=second['cache_context_id']
    assert second['cache_context_id']==identity({k:v for k,v in second.items() if k!='cache_context_id'})
    changed=dict(cad,occurrences=[dict(id='different')])
    assert delivery.cache_context(bundle,body,inventory,changed)['cache_context_id']!=second['cache_context_id']
