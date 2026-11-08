"""Bounded synthetic controls; no source body materialization or native CAD."""
from copy import deepcopy
from math import isclose
import pytest

from engineering import finished_fitout as f


def fixture():
    parts = []
    for name, qty, n, length, mass, price in (
        ('body/chair-frame',264,1,2.4,1.4,24),
        ('body/terminal-end-seal',2,1,7.,1.8,35),
        ('body/passage-end-seal',10,1,7.,1.8,35)):
        parts.append(dict(id=name, quantity_per_train=qty, quantity_per_assembly=n,
            stock=dict(length_m=length), component_definition_id=f.identity(name),
            mass_each_kg=dict.fromkeys(f.CASES,mass),direct_cost_each_usd=dict.fromkeys(f.CASES,price)))
    for name,(n,_) in f.HARDWARE.items():
        qty=264 if name.startswith('body/chair') else 2
        parts.append(dict(id=name,quantity_per_train=n*qty,quantity_per_assembly=n,
            component_definition_id=f.identity(name),mass_each_kg=dict.fromkeys(f.CASES,.01),
            direct_cost_each_usd=dict.fromkeys(f.CASES,.1)))
    patterns=[]
    for name,n,z in (('body/chair-frame',264,1.6),('body/terminal-end-seal',2,2.25),('body/passage-end-seal',10,2.25)):
        for i in range(n):
            patterns.append(dict(part_id=name,id=name+str(i),count=1,assembly_occurrence_id='synthetic/'+str(i),
                positions_m=[[i*1.,0.,z]],rotation=deepcopy(f.I),uncertainty_m=[.25,.25,.25]))
    body=dict(candidate_id=f.BODY_ID,evaluation_id=f.BODY_EVAL,parts=parts,patterns=patterns,
        policy=dict(layout=dict(floor_top_m=1.15,seat_pan_z_m=1.45),rates=dict(
            aluminium_usd_kg=[2.5,4.,6.5],labour_usd_h=[6,10,16],overhead_fraction=[.1,.2,.3])))
    own=dict(body_candidate_id=f.BODY_ID,body_evaluation_id=f.BODY_EVAL,evaluation_id=f.OWNERSHIP_ID,
        parts=[dict(part_id=p['id'],component_definition_id=p['component_definition_id']) for p in parts[:2]])
    return body,own


def evaluate():
    return f.evaluate(*fixture(),input_sha256={'synthetic':'0'*64},source_sha256={'synthetic':'1'*64})


def test_geometry_stock_and_material_conservation():
    r=evaluate();chair,seal=r['physical_definition']['parts']
    assert isclose(chair['net_tube_length_m'],3.384)
    assert isclose(chair['stock_summary']['gross_procurement_length_m'],3.557)
    assert isclose(seal['stock_summary']['gross_procurement_length_m'],9.048)
    assert isclose(sum(f._volume(e) for e in seal['entities']),8.9*.012*.018)
    assert all(p['stock_summary']['source_stock_shortfall_m']>0 for p in (chair,seal))
    assert all(f._volume(e)>0 for p in (chair,seal) for e in p['entities'])
    # Holes remove material; sleeves and plates cannot become massless hardware.
    expected=3.384*.000184-8*2*3.141592653589793*(.0065/2)**2*.002
    walls=sum(f._volume(e) for e in chair['entities'] if '/wall-' in e['id'])
    assert isclose(walls,expected,abs_tol=1e-14)
    assert chair['hardware_counts']['new_fastener_pieces']==16
    assert chair['welds']['joints']==18
    assert all(s['trim_and_drill_scrap_volume_m3']>0 for s in chair['ancillary_cut_stock'])
    assert chair['new_fastener_procurement']['ordered_bolts']==1078
    assert seal['hardware_counts']['stops'] is None


def test_actual_transform_not_policy_lift_and_finite_sweep():
    r=evaluate();p=r['physical_definition']['parts'][0]
    b=r['physical_definition']['installed_bindings'][0]
    assert b['translation_m'][2]==1.6
    assert isclose(b['finished_nominal_bounds_m'][0][2],1.31996)
    assert r['source_datums']['added_lift_m']==0
    assert p['removal_swept_local_bounds_m'][1][0]>.8
    # Independent signed rotation control: all8corners must remain in AABB.
    R=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]
    assert f._bounds([[-1,-2,-3],[1,2,3]],R,[4,5,6])==[[2.,4.,3.],[6.,6.,9.]]


def test_identity_once_only_hardware_and_no_acceptance():
    r=evaluate()
    assert r['candidate_id']==f.identity(r['physical_definition'])
    assert r['evaluation_id']==f.identity({k:v for k,v in r.items() if k!='evaluation_id'})
    assert all(r[k] is False for k in f.FLAGS)
    assert r['retained_passage_gaskets']['quantity']==10
    assert not r['retained_passage_gaskets']['removed']
    assert len({h['source_part_id'] for h in r['retained_hardware']})==len(f.HARDWARE)
    assert all(h['added_again_mass_kg']==h['added_again_cost_usd']==0 for h in r['retained_hardware'])
    assert all(x['proposed_component_mass_each_kg']['base']>0 for x in r['changes'])
    assert r['physical_definition']['parts'][1]['tolerance']['compression_screen_passed'] is False


def test_commands_compile_material_holes_and_profile_without_native():
    r=evaluate()
    for p in r['physical_definition']['parts']:
        commands=f.solidcraft.script_for(f.cad_case(r,p))['commands']
        assert commands[0]['command']=='document.units'
        assert commands[-1]['command']=='inspect.measure'
    chair_commands=f.solidcraft.script_for(f.cad_case(r,r['physical_definition']['parts'][0]))['commands']
    assert sum(c['command']=='solid.cylinder' and c['params']['operation']=='cut' for c in chair_commands)==36


@pytest.mark.parametrize('mutate',[
    lambda b,o:b.update(candidate_id='f'*64),
    lambda b,o:o.update(evaluation_id='f'*64),
    lambda b,o:b['parts'][2].update(quantity_per_train=9),
    lambda b,o:b['parts'][3].update(quantity_per_train=1),
    lambda b,o:b['patterns'][0].update(count=2),
    lambda b,o:b['patterns'][0].update(rotation=[[2,0,0],[0,1,0],[0,0,1]]),
    lambda b,o:b['patterns'][0].update(rotation=[[-1,0,0],[0,1,0],[0,0,1]]),
])
def test_reject_mixed_candidate_ownership_and_counts(mutate):
    b,o=fixture();mutate(b,o)
    with pytest.raises(ValueError):f.evaluate(b,o,input_sha256={},source_sha256={})
