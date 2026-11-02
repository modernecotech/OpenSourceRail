"""Operation-local cost reuse retains independent export replay and source checks."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from engineering.development_baseline import system_cost, vehicle_cost
from engineering.station_rail import bim, exports, publication
from engineering.station_rail.common import encoded, identity
from engineering.station_rail.evaluation import IDS


@pytest.fixture
def context(tmp_path, monkeypatch):
    record={key:key+'-fixture' for key in (*IDS,'evaluation_id')}
    rates=tmp_path/'rates';rates.write_text('original')
    sources=lambda root:{'rates':(Path(root)/'rates').read_text()}
    monkeypatch.setattr(vehicle_cost,'sources',sources)
    monkeypatch.setattr(system_cost,'sources',sources)
    calls=[]
    def vehicle(record,root):
        calls.append('vehicle')
        value=dict(record,source_sha256=sources(root),scopes=[1,2,3])
        value['cost_estimate_id']=identity(value)
        return value
    def system(record,root,vehicle):
        calls.append('system')
        value=dict(record,source_sha256=sources(root),vehicle_cost_estimate_id=vehicle['cost_estimate_id'],scopes=list(range(14)))
        value['vehicle_evaluation_id']=value.pop('evaluation_id')
        value['cost_estimate_id']=identity(value)
        return value
    monkeypatch.setattr(vehicle_cost,'evaluate',vehicle)
    monkeypatch.setattr(system_cost,'evaluate',system)
    return record,calls,rates


def test_reuse_equals_original_calculation_without_repeating_builders(context,tmp_path):
    record,calls,_=context
    original=publication._selected_cost_records(tmp_path,record)
    compiled=dict(zip(('selected_vehicle_cost','selected_system_cost'),original))
    before=encoded(compiled)
    assert encoded(publication._selected_cost_records(tmp_path,record,compiled))==encoded(original)
    assert calls==['vehicle','system']
    assert encoded(compiled)==before
    # A separate operation remains a fresh calculation, not a candidate-ID cache.
    assert encoded(publication._selected_cost_records(tmp_path,record))==encoded(original)
    assert calls==['vehicle','system','vehicle','system']


@pytest.mark.parametrize('damage',('seal','candidate','evaluation','link','source'))
def test_reuse_rejects_damaged_or_wrong_context_records(context,tmp_path,damage):
    record,_,rates=context
    vehicle,system=publication._selected_cost_records(tmp_path,record)
    compiled={'selected_vehicle_cost':deepcopy(vehicle),'selected_system_cost':deepcopy(system)}
    item=compiled['selected_system_cost']
    if damage=='seal':item['scopes'].append(99)
    elif damage=='source':rates.write_text('changed')
    else:
        item[{'candidate':'candidate_id','evaluation':'vehicle_evaluation_id','link':'vehicle_cost_estimate_id'}[damage]]='different'
        item['cost_estimate_id']=identity({k:v for k,v in item.items() if k!='cost_estimate_id'})
    with pytest.raises(ValueError,match='Reused selected cost|Reused system cost'):
        publication._selected_cost_records(tmp_path,record,compiled)


def test_export_return_is_opt_in_and_verify_always_recalculates_before_exposing(context,tmp_path,monkeypatch):
    record,calls,rates=context
    def compile(record,root,city_index):
        vehicle=vehicle_cost.evaluate(record,root)
        system=system_cost.evaluate(record,root,vehicle)
        return dict(selected_vehicle_cost=vehicle,selected_system_cost=system,bom={'all':'bytes'},procurement={'unknown':None})
    monkeypatch.setattr(exports,'compile',compile)
    monkeypatch.setattr(exports,'source_map',lambda root,names:{'rates':rates.read_text()})
    monkeypatch.setattr(bim,'write',lambda *_:{'execution':'not-run'})
    output=tmp_path/'exports'
    manifest,compiled=exports.write(output,record,tmp_path,return_compiled=True)
    assert calls==['vehicle','system']
    assert manifest==exports.write(output,record,tmp_path)
    calls.clear()
    result,fresh=exports.verify(output,record,tmp_path,return_compiled=True)
    assert calls==['vehicle','system']
    assert fresh is not compiled and encoded(fresh)==encoded(compiled)
    assert result==exports.verify(output,record,tmp_path)
    # Resealing a changed payload does not bypass complete calculated-byte replay.
    path=output/'selected-system-cost.json'
    altered=json.loads(path.read_bytes());altered['scopes'].append(99);path.write_bytes(encoded(altered))
    from engineering.station_rail.common import digest
    manifest['files_sha256'][path.name]=digest(path)
    manifest['manifest_id']=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    (output/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises(ValueError,match='delivery calculation differs'):
        exports.verify(output,record,tmp_path,return_compiled=True)
    rates.write_text('changed')
    calls.clear()
    with pytest.raises(ValueError,match='delivery source differs'):
        exports.verify(output,record,tmp_path,return_compiled=True)
    assert calls==[]
