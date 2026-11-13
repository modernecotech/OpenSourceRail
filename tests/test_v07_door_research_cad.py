"""One native visual control cannot promote a held door child."""
from copy import deepcopy
import json
from math import pi,prod

import pytest

from engineering.station_rail.common import identity
from engineering.vehicle_parts import door_research_cad as cad,door_research_child


@pytest.fixture(scope='module')
def child():
    return door_research_child.evaluate_radius(.03)


def test_scene_is_bound_to_exact_child_and_has_only_four_envelopes(child):
    case=cad.scene_case(child)
    assert case['candidate_id']==cad.CHILD
    assert case['source_evaluation_id']==child['evaluation_id']
    assert case['source_selection_id'] is None
    assert case['component_geometry_id']==identity(dict(candidate_id=cad.CHILD,
        entities=case['entities'],visual_scope='gross envelopes, no belt solid or mated assembly'))
    assert len(case['entities'])==4
    assert {e['shape'] for e in case['entities']}=={'box','cylinder'}
    guide=next(e for e in case['entities'] if e['id']=='guide-rail/nominal-bounding-box')
    assert guide['size_m']==[2.9,.05,.035]
    assert len(case['belt_route_polyline_m'])>30
    assert all('belt' not in e['id'] for e in case['entities'])
    assert case['physical_accepted'] is case['engineering_accepted'] is False


def test_other_candidate_or_adopted_child_refused(child):
    wrong=deepcopy(child)
    wrong['physical_candidate_id']='0'*64
    with pytest.raises(ValueError,match='Exact unselected'):
        cad.scene_case(wrong)
    wrong=deepcopy(child)
    wrong['candidate_adopted']=True
    wrong['evaluation_id']=identity({k:v for k,v in wrong.items() if k!='evaluation_id'})
    with pytest.raises(ValueError,match='Exact unselected'):
        cad.scene_case(wrong)


def synthetic_results(case):
    bodies=[]
    for e in case['entities']:
        if e['shape']=='box':volume=prod(e['size_m'])
        else:volume=pi*e['radius_m']**2*e['length_m']
        bodies.append(dict(name=e['id'],closed=True,volume_mm3=volume*1e9,
            area_mm2=1.,center_of_mass=[0.,0.,0.],
            bbox=dict(min=[0.,0.,0.],max=[1.,1.,1.])))
    return dict(bodies=bodies,body_count=4,total=dict(volume_mm3=sum(b['volume_mm3'] for b in bodies)))


def test_native_measurements_remain_envelope_diagnostics(child):
    case=cad.scene_case(child)
    measured,comparisons=cad._measure(case,synthetic_results(case))
    assert len(measured['bodies'])==4
    assert all(x['relative_difference']<1e-12 for x in comparisons.values())
    assert all(x['exact_material_volume_verified'] is False for x in comparisons.values())
    bad=synthetic_results(case);bad['bodies'].pop();bad['body_count']=3
    with pytest.raises(ValueError,match='Four exact'):
        cad._measure(case,bad)


def test_resource_refusal_retains_failure_packet_without_native_run(tmp_path,monkeypatch):
    monkeypatch.setattr(cad,'_git',lambda root,*args:'clean-revision' if args[0]=='rev-parse' else '')
    monkeypatch.setattr(cad,'disk_admission',lambda *args,**kwargs:dict(admitted=False))
    monkeypatch.setattr(cad.native,'run',lambda *args,**kwargs:pytest.fail('native run must not start'))
    output=tmp_path/'held'
    with pytest.raises(ValueError,match='scratch unavailable'):
        cad.run(output)
    failure=json.loads((output/'failure.json').read_bytes())
    manifest=json.loads((output/'manifest.json').read_bytes())
    assert failure['physical_candidate_id']==cad.CHILD
    assert failure['phase']=='admission' and manifest['status']=='held-admission'
    assert manifest['manifest_id']==identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    assert manifest['files_sha256']['failure.json']==cad.digest(output/'failure.json')
