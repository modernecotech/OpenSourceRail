from copy import deepcopy
import json
import pytest
from engineering.design_search import contracts as k,wheel_twin as t


def fixture():
    p=dict(id='known-floor',kind='box-with-rectangular-cutouts',at_m=[0.,0.,0.],size_m=[1.,1.,.1],
           rectangular_cutouts=[dict(at_m=[.1,.1,0.],size_m=[.1,.1,.1])],
           volume_m3=.099,mass_kg=99.,density_kg_m3=1000.,material='fixture',cg_m=[.5,.5,.05])
    c=k.make_candidate(requirement_revision='wheel-twin-fixture-r1',architecture=dict(family='wheel_rail_station_lim'),
      frames=[dict(id='car',parent_id=None,origin_m=[0.,0.,0.],rotation_matrix=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])],
      materials=[dict(id='fixture',density_kg_m3=1000.,basis='Fixture')],
      geometry=[dict(id='floor',kind='native-stock-region',frame_id='car',material_id='fixture',native_part=p),
                dict(id='budget',kind='unlocated-mass-budget',frame_id='car',material_id='fixture')],interfaces=[],
      installed_inventory=[dict(id='floor',geometry_id='floor',quantity=1,status='known',scope='vehicle-per-car',frame_id='car',basis='Known stock',unit_mass_kg=99.,cg_m=p['cg_m'],inertia_kg_m2=None),
                           dict(id='unlocated',geometry_id='budget',quantity=1,status='known',scope='vehicle-per-car',frame_id='car',basis='Unlocated account',unit_mass_kg=15.,cg_m=None,inertia_kg_m2=None),
                           dict(id='unknown-services',geometry_id=None,quantity=1,status='unknown',scope='vehicle-per-car',frame_id='car',basis='Unknown equipment',unit_mass_kg=None)])
    return c,dict(candidate_id=c['candidate_id'],geometry_parts=[p],wayside_parts=[])


def test_export_omits_unknown_and_unlocated_stock_without_placeholder(tmp_path,monkeypatch):
    c,m=fixture();monkeypatch.setattr(t,'_materialize',lambda _:deepcopy(m))
    r=t.compile(c,[],output=tmp_path/'twin',export_native=False)
    assert r['verified'] and not r['complete_installed_twin']
    s=r['summary'];assert s['known_geometric_occurrences']==1
    assert s['omitted_unlocated_inventory_ids']==['unlocated']
    assert s['omitted_unknown_inventory_ids']==['unknown-services']
    assert not (tmp_path/'twin'/'wheel-stock.ifc').exists()
    assert not (tmp_path/'twin'/'wheel-stock.step').exists()
    assert s['native']['execution']=='not-run'
    with pytest.raises(k.UnknownInstalledStock):t.compile(c,[],output=tmp_path/'complete',export_native=False,allow_incomplete=False)


def test_mixed_candidate_result_or_geometry_is_rejected(tmp_path,monkeypatch):
    c,m=fixture();other=deepcopy(c);other['architecture']['alternative']='other'
    other=k.make_candidate(requirement_revision=c['requirement_revision'],**{key:other[key] for key in k.PHYSICAL_KEYS})
    req=k.make_evaluation_request(other,evaluator_id='fixture',evaluator_sources={'fixture.py':'a'*64})
    r=k.make_result(req,execution_status='executed',numerical_status='converged',screen_status='fail')
    monkeypatch.setattr(t,'_materialize',lambda _:deepcopy(m))
    with pytest.raises(ValueError,match='Mixed candidate'):t.compile(c,[r],output=tmp_path/'mixed',export_native=False)
    m['geometry_parts'][0]['size_m'][0]=2.
    with pytest.raises(ValueError,match='native stock differs'):t.compile(c,[],output=tmp_path/'geometry',export_native=False)


def test_retained_twin_payload_changes_are_detected(tmp_path,monkeypatch):
    c,m=fixture();monkeypatch.setattr(t,'_materialize',lambda _:deepcopy(m));out=tmp_path/'twin'
    t.compile(c,[],output=out,export_native=False)
    (out/'procurement.json').write_text('{}')
    with pytest.raises(ValueError,match='payload'):t.verify(out)
