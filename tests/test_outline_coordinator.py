"""Integration checks for useful outlines without physical release authority."""
from copy import deepcopy
from http.server import ThreadingHTTPServer
from pathlib import Path
from functools import partial
import json
import threading
import urllib.error
import urllib.request

import pytest

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity
from engineering.outline import coordinator, interactive
from engineering.development_baseline.server import Handler


@pytest.fixture(scope='module')
def study():
    return coordinator.evaluate()


def test_complete_demand_study_retains_all_cost_scopes_and_source_identity(study):
    value,measurement=study
    assert value['evaluation_id']==identity({k:v for k,v in value.items() if k!='evaluation_id'})
    assert len(value['outlines'])==3 and len(value['cost_index'])>=30
    assert measurement['elapsed_s']>0 and measurement['native_solver_calls']==0
    assert measurement['source_loads']==1
    assert value['approach_policy']['examples_are_exhaustive'] is False
    assert value['global_optimum_established'] is False
    assert len(value['unassessed_approaches'])>=6
    assert all(row['comparison_admitted'] is False and row['cost'] is None for row in value['unassessed_approaches'])
    for row in value['outlines']:
        assert len(row['cost']['scope_totals_iqd'])==14
        assert all(x['base']>0 for x in row['cost']['scope_totals_iqd'].values())
        assert row['maturity']['outline_acceptance']=='accepted'
        assert row['maturity']['manufacturing_release'] is False
        assert row['maturity']['available_force_map_admitted'] is False
        assert row['physical_candidate_id'] is None
        assert row['requirements']['headway_s']==200
        assert row['service']['total_trainsets'] <52
        assert len(row['outline_input']['manufacturing_routes'])>=2
        assert row['outline_input']['bounded_mass_kg']['low']>0
        draft=row['delivery_draft']
        assert draft['outline_id']==row['outline_id']
        assert draft['ERPNext']['production_orders']==[]
        assert all(item['disabled']==1 for item in draft['provisional_account_BOM'])
        assert draft['workforce']['production_shifts']==2
        assert len(draft['construction_precedence'])==6


def test_recommendation_uses_common_brief_whole_life_cost_not_hardware_selection(study):
    value,_=study
    selected=next(o for o in value['outlines'] if o['outline_id']==value['recommended_outline_id'])
    assert selected['cost']['whole_life_npv_usd']['base']==min(o['cost']['whole_life_npv_usd']['base'] for o in value['outlines'])
    assert value['selection_is_physical_adoption'] is False
    assert value['requirements_id']!=coordinator.budget.active_baseline(ROOT)['requirements_id']
    assert all(value[k] is False for k in coordinator.FLAGS)
    assert value['reference_library']['rea_executed'] is False
    assert value['reference_library']['physical_plant_observed'] is False


def test_frozen_reference_and_sources_are_unchanged(study):
    value,_=study
    assert coordinator.budget.specification(ROOT)['requirements']['headway_s']==120
    sources=value['source_sha256']
    assert coordinator.PRODUCER in sources
    assert 'engineering/outline/maturity.py' in sources
    assert 'engineering/railway_completion/evidence.py' in sources
    for k in ('engineering/outline/reference_library.py','engineering/outline/rea_adapter.py'):
        assert k in sources


def test_conflicting_dependency_epochs_are_rejected():
    with pytest.raises(ValueError,match='Mixed source epochs'):
        coordinator.merge_sources({'common.py':'old'},{'common.py':'new'})


def test_live_worker_refuses_a_changed_loaded_source_epoch(monkeypatch):
    monkeypatch.setitem(coordinator._LOADED,coordinator.PRODUCER,'0'*64)
    with pytest.raises(ValueError,match='restart the calculation worker'):
        coordinator.prepare()


def test_immutable_run_detects_tampering_and_replays(tmp_path):
    domain=deepcopy(coordinator.DEFAULT_VARIABLES)
    domain.update(headways_s=[180.],speeds_kmh=[72.],accelerations_m_s2=[1.])
    out=tmp_path/'study';coordinator.run(out,variables=domain)
    assert coordinator.verify(out)['manifest_id']
    with pytest.raises(ValueError,match='fresh immutable'):
        coordinator.run(out,variables=domain)
    data=json.loads((out/'result.json').read_bytes()); data['outlines'][0]['cost']['installed_capital_usd']['base']=1
    (out/'result.json').write_bytes(encoded(data))
    with pytest.raises(ValueError,match='payload differs'):coordinator.verify(out)


def test_compact_publication_reproduces_summary(tmp_path):
    variables=deepcopy(coordinator.DEFAULT_VARIABLES)
    variables.update(headways_s=[200.],speeds_kmh=[72.],accelerations_m_s2=[.8])
    state=tmp_path/'run';output=tmp_path/'publication'
    coordinator.run(state,variables=variables)
    manifest=coordinator.publish(state,output)
    assert {p.name for p in output.iterdir()}=={'inputs.json','summary.json','manifest.json'}
    assert manifest['canonical_result_sha256']
    assert sum(p.stat().st_size for p in output.iterdir())<200_000
    assert coordinator.verify_compact(output)['manifest_id']==manifest['manifest_id']


def test_http_requires_same_origin_bounds_and_refuses_arbitrary_artifacts(tmp_path,monkeypatch):
    policy=tmp_path/'engineering/outline/supply-policy.toml'
    policy.parent.mkdir(parents=True)
    policy.write_bytes((Path(ROOT)/'engineering/outline/supply-policy.toml').read_bytes())
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,root=tmp_path))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base='http://127.0.0.1:'+str(server.server_port)
    try:
        assert json.load(urllib.request.urlopen(base+'/api/outline-study'))['brief']['peak_demand_pphpd']==4000
        def post(raw,origin):
            return urllib.request.urlopen(urllib.request.Request(base+'/api/outline-study',data=raw,
                headers={'Content-Type':'application/json','Origin':origin}))
        with pytest.raises(urllib.error.HTTPError) as caught:post(b'{}','https://other.example')
        assert caught.value.code==403
        with pytest.raises(urllib.error.HTTPError) as caught:post(b'{"brief":{},"brief":{}}',base)
        assert caught.value.code==400
        assert not (tmp_path/'build/outline-workbench').exists()
        with pytest.raises(urllib.error.HTTPError) as caught:urllib.request.urlopen(base+'/api/outline-study/../../etc/passwd')
        assert caught.value.code==400
        with pytest.raises(urllib.error.HTTPError) as caught:post(b'{}'*(interactive.MAX_REQUEST_BYTES),base)
        assert caught.value.code==400
    finally:server.shutdown();server.server_close();thread.join(timeout=2)


def test_all_three_outline_installations_reconcile_exact_cost_quantities_and_braking(study):
    value,_=study
    for row in value['outlines']:
        installation=row['propulsion_installation'];mode=row['mechanism']
        assert installation['cost_quantities_reconciled'] is True
        assert installation['receiving_propulsion_selected'] is False
        assert installation['independent_onboard_braking_required'] is True
        assert installation['available_force_N'] is None
        assert installation['actual_installed_mass_kg'] is None
        assert installation['electrical_thermal_qualified'] is False
        assert row['delivery_draft']['physical_installation_id']==installation['physical_installation_id']
        assert row['delivery_draft']['source_propulsion_installation_evaluation_id']==installation['evaluation_id']
        assert installation['departure_sites']==22
        totals=installation['corridor_quantities']
        if mode=='compact-launch-LIM':
            costline=next(z for z in row['cost']['capital_lines'] if z['key']=='LIM-primary-installed')
            assert installation['cost_quantity_line_id']==costline['line_id']
            q=costline['quantity'];layout=installation['geometry']['layout']
            assert layout['physical_definition']['directions']==1
            assert totals['installed_length_m']==q['metres']==22*q['installed_length_m_per_site']
            assert totals['full_modules']==22*q['modules_per_site']
            assert totals['stator_face_module_joints']==22*q['stator_face_module_joints_per_site']
            assert totals['bare_primary_stock_kg']==totals['installed_length_m']*q['stock_proxy_kg_per_m']
            assert all(s['role']=='launch' for s in layout['sections'])
        else:
            q=next(z['quantity'] for z in row['cost']['capital_lines'] if z['key']=='launch-contact-and-return-hardware')
            if mode=='cable-capstan':
                assert totals['rope_length_m']==22*q['rope_m_per_site']
                assert installation['geometry']['continuous_coupling'] is True
            else:
                assert totals['roller_contacts']==22*q['contacts_per_site']
                assert totals['installed_common_drive_bank_m']==22*q['bank_m_per_site']
                assert installation['geometry']['motor_per_roller_assumed'] is False


def test_priced_outline_geometry_is_compact_source_bound_and_not_complete_native_CAD(study):
    value,_=study
    for row in value['outlines']:
        geometry=row['outline_geometry'];vehicle=geometry['vehicle'];guideway=geometry['guideway'];station=geometry['stations']
        assert geometry['route_length_m']==30000 and geometry['world_crs'] is None
        assert geometry['detailed_CAD_generated'] is False and geometry['native_solver_jobs']==0
        assert vehicle['cars_per_train']==6 and vehicle['length_m']==104.5
        assert vehicle['car_module']['source_body_candidate_id']
        assert vehicle['car_module']['complete_installed_height_m'] is None
        assert guideway['priced_span_count']==3000 and guideway['repeat_pattern']['count_per_track']==1500
        assert guideway['module']['span_m']==20
        assert guideway['module']['section_dimensions']==dict(outer_width_m=2.,depth_m=1.4,wall_m=.18,flange_m=.18)
        assert guideway['foundation_dimensions'] is None and guideway['relative_track_centres_m'] is None
        assert station['chainages_m'][0]==0 and station['chainages_m'][-1]==30000
        assert station['priced_boarding_edges']==24 and station['priced_platform_area_m2']==24*120*4
        assert station['platform_module']['height_above_rail_m'] is None
        assert row['delivery_draft']['outline_geometry_id']==geometry['geometry_id']
        assert geometry['geometry_id']==identity({k:v for k,v in geometry.items() if k!='geometry_id'})
        assert len(encoded(geometry))<20000


def test_mixed_cost_sites_or_unrounded_LIM_metres_cannot_masquerade_as_geometry(study):
    value,_=study;row=next(z for z in value['outlines'] if z['mechanism']=='compact-launch-LIM')
    case=next(c for c in value['service_screen']['cases'] if c['case_id']==row['service_case_id'])
    context=dict(vehicle=coordinator.selection.load()['vehicle'],spec=coordinator.budget.specification(),root=Path(ROOT))
    for key in ('metres','sites'):
        cost=deepcopy(row['cost']);line=next(z for z in cost['capital_lines'] if z['key']=='LIM-primary-installed')
        line['quantity'][key]*=2
        line.pop('line_id');line['line_id']=identity(line)
        cost.pop('evaluation_id');cost['evaluation_id']=identity(cost)
        with pytest.raises(ValueError,match='quantit'):
            coordinator._installation(case,cost,context)
    cost=deepcopy(row['cost']);cost['service_evaluation_id']='f'*64
    cost.pop('evaluation_id');cost['evaluation_id']=identity(cost)
    with pytest.raises(ValueError,match='Mixed service'):
        coordinator._installation(case,cost,context)


def test_installation_producer_changes_are_captured_before_costing(monkeypatch):
    for name in (coordinator.propulsion_layout.PRODUCER,coordinator.station_motor.PRODUCER):
        with monkeypatch.context() as patch:
            patch.setitem(coordinator._LOADED,name,'0'*64)
            with pytest.raises(ValueError,match='restart the calculation worker'):coordinator.prepare()
