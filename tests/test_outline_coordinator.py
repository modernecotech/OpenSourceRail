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
