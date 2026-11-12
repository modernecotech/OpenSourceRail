"""Runner edit controls, independent of GIS/native calculation execution."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).resolve().parents[1]/'tools/automation/tests/verify-v07-native-gis.py'
spec=importlib.util.spec_from_file_location('native_gis_runner',PATH)
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


def fixture():
    fields=['id','chainage_m','lon','lat','dwell_s']
    native={'maps':[{'layers':[{'name':'stations','dataset':{'fields':[{'name':x} for x in fields],
        'features':[{'geometry':{'Point':{'x':.01,'y':0.}},
                     'attrs':[{'Text':'midpoint'},{'Float':10.},{'Float':.01},{'Float':0.},{'Float':35.}]}]}}]}]}
    base={'lines':[{'id':'line-1','coordinates':[[0.,0.],[.1,0.]],
                   'stops':[{'id':'midpoint','chainage_m':10.,'dwell_s':35.}]}]}
    return native,base


def test_real_geometry_and_proxy_change_remain_one_station():
    native,base=fixture();old=deepcopy(native)
    edited,change=runner.edit_station(native,base,'midpoint','station-move',lambda coords,at:[at/1000.,0.])
    assert native==old
    feature=edited['maps'][0]['layers'][0]['dataset']['features'][0]
    assert feature['geometry']=={'Point':{'x':.011,'y':0.}}
    assert feature['attrs'][1:]==[{'Float':11.},{'Float':.011},{'Float':0.},{'Float':35.}]
    request={'edit_bundle':{'edits':[{'kind':'replace-line-geometry','coordinates':base['lines'][0]['coordinates'],
                                    'stops':[{'id':'midpoint','chainage_m':11.,'dwell_s':35.}]}]}}
    runner.validate_edit(request,base,'midpoint','station-move',change)
    request['edit_bundle']['edits'][0]['stops'][0]['dwell_s']=36.
    with pytest.raises(ValueError,match='Only'):runner.validate_edit(request,base,'midpoint','station-move',change)


def test_dwell_change_does_not_move_geometry_and_duplicate_stop_is_refused():
    native,base=fixture();edited,change=runner.edit_station(native,base,'midpoint','dwell',None)
    feature=edited['maps'][0]['layers'][0]['dataset']['features'][0]
    assert feature['geometry']==native['maps'][0]['layers'][0]['dataset']['features'][0]['geometry']
    assert feature['attrs'][-1]=={'Float':36.}
    native['maps'][0]['layers'][0]['dataset']['features']*=2
    with pytest.raises(ValueError,match='once'):runner.edit_station(native,base,'midpoint','dwell',None)


def test_generic_corridor_selection_uses_its_own_interior_station():
    native,base=fixture()
    base['lines'][0]['id']='baghdad-corridor'
    base['lines'][0]['stops']=[{'id':'start','chainage_m':0.,'dwell_s':35.},
        {'id':'midpoint','chainage_m':10.,'dwell_s':35.},{'id':'end','chainage_m':20.,'dwell_s':35.}]
    assert runner.select_station(base,'baghdad','baghdad-corridor')=='midpoint'
    edited,change=runner.edit_station(native,base,'midpoint','dwell',None,'baghdad-corridor')
    stops=deepcopy(base['lines'][0]['stops']);stops[1]['dwell_s']=36.
    request={'edit_bundle':{'edits':[{'kind':'replace-line-geometry','line':'baghdad-corridor',
        'coordinates':base['lines'][0]['coordinates'],'stops':stops}]}}
    runner.validate_edit(request,base,'midpoint','dwell',change,'baghdad-corridor')
    request['edit_bundle']['edits'][0]['line']='unrelated-line'
    with pytest.raises(ValueError,match='alignment'):runner.validate_edit(request,base,'midpoint','dwell',change,'baghdad-corridor')
    with pytest.raises(ValueError,match='corridor'):runner.select_station(base,'baghdad','wrong-line')
    with pytest.raises(ValueError,match='station'):runner.select_station(base,'baghdad','baghdad-corridor','wrong-stop')
