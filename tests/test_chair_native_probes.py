"""Invented primitives and mock membership; no actual plan/export/FreeCAD call."""
import ast
from copy import deepcopy
import hashlib
import json
from math import pi, prod
from pathlib import Path
import subprocess

import pytest

from engineering import chair_native_probes as p


@pytest.fixture(autouse=True)
def prohibit_native(monkeypatch):
    def forbidden(*a,**k):raise AssertionError('Actual/native application forbidden')
    monkeypatch.setattr(subprocess,'Popen',forbidden)


def box(*,swap=False):
    cuts=[dict(axis=2,base_m=[-.12,0.,-.05 if swap else .025],radius_m=.025,length_m=.025),
          dict(axis=2,base_m=[.12,0.,.025 if swap else -.05],radius_m=.025,length_m=.025)]
    return dict(id='invented/plate',material='invented/al',shape='box',corner_m=[-.3,-.2,-.05],size_m=[.6,.4,.1],cuts=cuts)


def cylinder(axis=0,inner=.007):
    return dict(id='invented/round',material='invented/steel',shape='cylinder',axis=axis,
                start_m=[-.21,.31,-.41],length_m=.03,radius_m=.01,inner_radius_m=inner)


def fixture(solids=None):
    solids=deepcopy([box()] if solids is None else solids)
    case=dict(schema='osr-local-chair-native-geometry/1',units='m',frame='coupon-local',entities=solids)
    case['component_geometry_id']=p.identity(case)
    case.update(source_physical_definition_id='a'*64,source_execution_id='b'*64,
        physical_accepted=False,engineering_accepted=False,native_evaluator_admitted=False,
        installed_mass_complete=False,manufacturing_release=False,operating_release=False,
        selected_reference_changed=False,movement_authority=False)
    expected={}
    for s in solids:
        if s['shape']=='box':
            lo=s['corner_m'];hi=[a+b for a,b in zip(lo,s['size_m'])];gross=prod(s['size_m']);center=[(a+b)/2 for a,b in zip(lo,hi)]
            removal=[(pi*c['radius_m']**2*c['length_m'],[c['base_m'][k]+(c['length_m']/2 if k==c['axis'] else 0.) for k in range(3)]) for c in s['cuts']]
            v=gross-sum(x[0] for x in removal);cc=[(gross*center[k]-sum(vv*q[k] for vv,q in removal))/v for k in range(3)]
        else:
            a=s['axis'];st=s['start_m'];v=pi*(s['radius_m']**2-s['inner_radius_m']**2)*s['length_m']
            lo=[st[k] if k==a else st[k]-s['radius_m'] for k in range(3)]
            hi=[st[k]+s['length_m'] if k==a else st[k]+s['radius_m'] for k in range(3)]
            cc=[st[k]+(s['length_m']/2 if k==a else 0.) for k in range(3)]
        expected[s['id']]=dict(volume_m3=v,center_of_mass_m=cc,bbox_m=dict(min=lo,max=hi),source_material=s['material'],complete_installed=False)
    return case,expected


def bodies(expected):
    return [dict(deepcopy(e),id=k,native_name='native/'+k,valid=True,closed=True,all_solids_closed_valid=True,solid_count=1) for k,e in expected.items()]


def evaluate(case,expected,*,actual=None,rows=None):
    plan=p.compile_probe_plan(case,expected);actual=case['entities'] if actual is None else actual
    geometry={'native/'+s['id']:s for s in actual}
    result=p.evaluate_probes(plan,bodies(expected) if rows is None else rows,lambda name,point:p.nominal_state(geometry[name],point)[0])
    return plan,result


def base_worker():
    f=Path(__file__).resolve().parents[1]/'engineering/design_search/craft_backends/freecad_reference.py'
    assert hashlib.sha256(f.read_bytes()).hexdigest()==p.BASE_MODULE_SHA256
    tree=ast.parse(f.read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='WORKER' for t in n.targets))


def test_swapped_equal_blind_ends_evade_metrics_but_fail_points():
    case,oracle=fixture();swapped,other=fixture([box(swap=True)])
    assert oracle.keys()==other.keys()
    for k in oracle:
        assert oracle[k]['volume_m3']==pytest.approx(other[k]['volume_m3'],abs=1e-16)
        assert oracle[k]['center_of_mass_m']==pytest.approx(other[k]['center_of_mass_m'],abs=1e-14)
        assert oracle[k]['bbox_m']==other[k]['bbox_m']
    plan,good=evaluate(case,oracle);_,bad=evaluate(case,oracle,actual=swapped['entities'])
    assert good['geometry_verification']=='passed' and not good['mismatches']
    assert bad['geometry_verification']=='held' and bad['mismatches']
    assert not bad['mapping_issues'] and bad['execution']=='completed'
    assert any('/void/' in x['probe_id'] for x in bad['mismatches'])
    assert any('blind-end-material' in x['id'] for x in plan['records'][0]['probes'])


@pytest.mark.parametrize('axis',[0,1,2])
@pytest.mark.parametrize('inner',[0.,.007])
def test_all_round_axes_annular_void_and_material_are_strict(axis,inner):
    case,oracle=fixture([cylinder(axis,inner)]);plan,result=evaluate(case,oracle)
    assert result['geometry_verification']=='passed'
    probes=plan['records'][0]['probes']
    assert all(x['clearance_m']>=p.MIN_CLEARANCE_M for x in probes)
    assert any(x['id']=='round/annular-void' for x in probes)==bool(inner)
    assert all(p.nominal_state(case['entities'][0],x['point_m'])[0] is x['inside'] for x in probes)


@pytest.mark.parametrize('axis',[0,1,2])
def test_through_box_bore_all_axes(axis):
    s=box();base=[0.,0.,0.];base[axis]=s['corner_m'][axis]
    s['cuts']=[dict(axis=axis,base_m=base,radius_m=.005,length_m=s['size_m'][axis])]
    plan,r=evaluate(*fixture([s]))
    assert r['geometry_verification']=='passed'
    assert any('/void/' in x['id'] for x in plan['records'][0]['probes'])
    assert not any('blind-end-material' in x['id'] for x in plan['records'][0]['probes'])


def test_wrong_scale_and_datum_are_not_silently_applied():
    case,oracle=fixture();plan=p.compile_probe_plan(case,oracle);s=case['entities'][0]
    for transform in [lambda x:[v*1000 for v in x],lambda x:[x[0],x[1],x[2]+.150]]:
        r=p.evaluate_probes(plan,bodies(oracle),lambda _,x:p.nominal_state(s,transform(x))[0])
        assert r['execution']=='completed' and r['geometry_verification']=='held' and r['mismatches']
    assert plan['native_point_scale_mm_per_m']==1000. and plan['on_boundary_argument'] is True


def test_missing_ambiguous_and_invalid_native_mapping_remain_held():
    case,oracle=fixture();plan=p.compile_probe_plan(case,oracle);rows=bodies(oracle)
    for bad in [[],rows+[dict(rows[0],native_name='duplicate',id='duplicate')],[dict(rows[0],closed=False)]]:
        r=p.evaluate_probes(plan,bad,lambda _,x:True)
        assert r['execution']=='completed' and r['geometry_verification']=='held' and r['mapping_issues']
    r=p.evaluate_probes(plan,rows,lambda _,x:1)
    assert r['geometry_verification']=='held' and all('not boolean' in x['error'] for x in r['mismatches'])


def test_native_renaming_is_a_separate_retained_failure():
    case,oracle=fixture();rows=bodies(oracle);rows[0]['id']='ImportedName'
    _,r=evaluate(case,oracle,rows=rows)
    assert r['geometry_verification']=='passed' and r['strict_native_name_identity']=='failed'
    assert r['strict_name_failure']=='STEP source occurrence identity/count differs'
    assert r['physical_accepted'] is False


@pytest.mark.parametrize('mutate',[
    lambda c,e:c.update(units='mm'),
    lambda c,e:c.update(frame='world'),
    lambda c,e:c.update(source_physical_definition_id='unknown'),
    lambda c,e:c.update(source_execution_id=True),
    lambda c,e:c.update(component_geometry_id='0'*64),
    lambda c,e:c.update(physical_accepted=True),
    lambda c,e:e.clear(),
    lambda c,e:e['invented/plate'].update(volume_m3=True),
    lambda c,e:e['invented/plate'].update(center_of_mass_m=[0.,0.,float('nan')]),
    lambda c,e:e['invented/plate'].update(volume_m3=100.),
    lambda c,e:e['invented/plate'].update(source_material='other'),
])
def test_units_identity_oracle_and_status_refusal(mutate):
    case,oracle=fixture();mutate(case,oracle)
    with pytest.raises(ValueError):p.compile_probe_plan(case,oracle)


@pytest.mark.parametrize('mutate',[
    lambda s:s.update(shape='unknown'),
    lambda s:s['size_m'].__setitem__(0,True),
    lambda s:s['corner_m'].__setitem__(0,float('nan')),
    lambda s:s['cuts'][0].update(axis=True),
    lambda s:s['cuts'][0].update(radius_m=-1.),
    lambda s:s['cuts'][0].update(length_m=.2),
    lambda s:s['cuts'].append(deepcopy(s['cuts'][0])),
    lambda s:s.update(unresolved_feature=True),
])
def test_resealed_invalid_cut_domain_refused(mutate):
    case,oracle=fixture();mutate(case['entities'][0])
    with pytest.raises(ValueError):
        case['component_geometry_id']=p.identity({k:case[k] for k in ('schema','units','frame','entities')})
        p.compile_probe_plan(case,oracle)


def test_boundary_and_unresolvably_thin_features_refused():
    s=box();point=[-.3,0.,0.];assert p.nominal_state(s,point)[1]==0.
    small=dict(id='invented/thin',material='invented/al',shape='box',corner_m=[0.,0.,0.],size_m=[1e-7,.01,.01],cuts=[])
    with pytest.raises(ValueError):p.compile_probe_plan(*fixture([small]))


def test_duplicate_case_entities_refused():
    case,oracle=fixture();case['entities'].append(deepcopy(case['entities'][0]));case['component_geometry_id']=p.identity({k:case[k] for k in ('schema','units','frame','entities')})
    with pytest.raises(ValueError):p.compile_probe_plan(case,oracle)


def test_instrumentation_keeps_base_capture_and_binds_changed_worker():
    case,oracle=fixture();plan=p.compile_probe_plan(case,oracle);base=base_worker();r=p.instrument_freecad_worker(base,plan)
    assert r['base_worker_sha256']==hashlib.sha256(base.encode()).hexdigest()
    assert r['worker_sha256']==hashlib.sha256(r['worker'].encode()).hexdigest()!=r['base_worker_sha256']
    assert r['probe_plan_id']==plan['plan_id'] and r['actual_native_calls']==0
    tree=ast.parse(r['worker']);compile(tree,'invented-instrumented-worker','exec')
    assert "result['point_probes']" in r['worker'] and 'v*1000.0 for v in point_m' in r['worker']
    assert 'shape.isInside(point, 0.00001, True)' in r['worker']
    assert 'actual_worker_sha256=' in r['worker'] and "'measurement.json'" in r['worker']
    assert r['worker'].count('Import.insert(')==base.count('Import.insert(')==1
    assert "resource.setrlimit(resource.RLIMIT_CPU, (120, 120))" in r['worker']
    assert '(2147483648, 2147483648)' in r['worker']
    assert all(r[k] is False for k in p.FLAGS)


@pytest.mark.parametrize('mutation',[
    lambda plan:plan.update(native_point_scale_mm_per_m=1.),
    lambda plan:plan.update(inside_tolerance_mm=10.),
    lambda plan:plan['records'][0]['probes'][0]['point_m'].__setitem__(2,.150),
    lambda plan:plan['records'][0]['probes'].pop(),
    lambda plan:plan['bindings'].update(source_execution_id='c'*64),
    lambda plan:plan.update(matching=dict(volume_relative=1.)),
])
def test_resealed_plan_cannot_change_features_or_method_contract(mutation):
    plan=p.compile_probe_plan(*fixture());mutation(plan);plan['plan_id']=p.identity({k:v for k,v in plan.items() if k!='plan_id'})
    with pytest.raises(ValueError):p.instrument_freecad_worker(base_worker(),plan)


def test_wrong_base_worker_refused_without_application_import():
    plan=p.compile_probe_plan(*fixture())
    with pytest.raises(ValueError):p.instrument_freecad_worker(base_worker()+'\n',plan)
