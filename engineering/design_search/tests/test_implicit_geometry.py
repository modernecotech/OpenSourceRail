"""Independent checks for bounded 3D implicit sampling, never qualification."""
from copy import deepcopy
from hashlib import sha256
from math import cos, pi, sin

import pytest

from engineering.design_search import implicit_geometry as implicit
from engineering.station_rail.common import identity


def candidate(**changes):
    args=dict(envelope_m=[.4,.4,.4],period_m=.2,threshold=.45,material_family='research_steel')
    args.update(changes)
    return implicit.generate(**args)


def sample(c=None,n=16,**changes):
    args=dict(density_kg_m3=7850.,minimum_feature_m=.08)
    args.update(changes)
    return implicit.sample(c or candidate(),[n,n,n],**args)


def reseal(value,key):
    value[key]=identity({k:v for k,v in value.items() if k!=key})


def test_sample_contains_real_gyroid_cells_in_portable_x_fastest_vtk():
    c=candidate(phase_rad=(.1,.2,.3));result,vtk=sample(c)
    marker=b'LOOKUP_TABLE default\n';head,raw=vtk.split(marker,1)
    assert b'DATASET STRUCTURED_POINTS\n' in head
    assert b'DIMENSIONS 17 17 17\n' in head and b'CELL_DATA 4096\n' in head
    assert len(raw)==4097 and raw[-1:]==b'\n'
    bits=raw[:-1];spacing=.4/16;count=0
    for iz in range(16):
        for iy in range(16):
            for ix in range(16):
                x,y,z=[2*pi*(j+.5)*spacing/.2+phase for j,phase in zip((ix,iy,iz),(.1,.2,.3))]
                expected=abs(sin(x)*cos(y)+sin(y)*cos(z)+sin(z)*cos(x))<=.45
                assert bool(bits[ix+16*iy+256*iz]) is expected
                count+=expected
    g=result['geometry']
    assert count==g['occupied_voxel_count']
    assert g['sampled_solid_volume_m3']==pytest.approx(count*spacing**3)
    assert g['sampled_solid_mass_kg']==pytest.approx(count*spacing**3*7850)
    assert g['occupancy_sha256']==sha256(bits).hexdigest() and g['vtk_sha256']==sha256(vtk).hexdigest()
    assert implicit.verify(c,result,vtk,expected_evaluation_id=result['evaluation_id'])['verified'] is True


def test_sampled_grid_identity_changes_but_physical_identity_does_not():
    c=candidate();rough,_=sample(c,16);fine,_=sample(c,32)
    heavy,_=sample(c,16,density_kg_m3=8000.)
    assert rough['candidate_id']==fine['candidate_id']==heavy['candidate_id']==c['candidate_id']
    assert len({rough['evaluation_id'],fine['evaluation_id'],heavy['evaluation_id']})==3
    assert heavy['geometry']['sampled_solid_volume_m3']==rough['geometry']['sampled_solid_volume_m3']
    assert heavy['geometry']['sampled_solid_mass_kg']>rough['geometry']['sampled_solid_mass_kg']


def test_ancestry_does_not_create_fake_physical_geometry():
    first=candidate();revision=candidate(parent_candidate_id='a'*64)
    assert first['candidate_id']==revision['candidate_id']
    assert first['definition_id']!=revision['definition_id']
    changed=candidate(threshold=.5,parent_candidate_id=first['candidate_id'])
    assert changed['candidate_id']!=first['candidate_id']
    assert changed['parent_candidate_id']==first['candidate_id']


def test_one_reproducible_refinement_example_and_explicit_ideal_bounds():
    coarse,_=sample(n=32);middle,_=sample(n=64);fine,_=sample(n=96)
    volume=lambda r:r['geometry']['sampled_solid_volume_m3']
    assert abs(volume(fine)-volume(middle))<abs(volume(middle)-volume(coarse))
    for r in (coarse,middle,fine):
        lo,hi=r['geometry']['ideal_arithmetic_implicit_volume_interval_m3']
        assert 0<=lo<=volume(r)<=hi<=r['geometry']['envelope_volume_m3']+1e-14
    assert fine['geometry']['ideal_arithmetic_implicit_volume_interval_m3'][1] < coarse['geometry']['ideal_arithmetic_implicit_volume_interval_m3'][1]
    assert fine['geometry']['continuous_surface_qualified'] is False
    assert fine['geometry']['floating_point_roundoff_guaranteed'] is False
    assert 'exact arithmetic only' in fine['geometry']['implicit_volume_interval_scope']


def test_full_threshold_produces_all_cells_and_exact_envelope_volume():
    result,vtk=sample(candidate(threshold=3.))
    assert result['geometry']['occupied_voxel_count']==16**3
    assert result['geometry']['sampled_solid_volume_m3']==pytest.approx(.4**3)
    assert set(vtk.split(b'LOOKUP_TABLE default\n',1)[1][:-1])=={1}


def test_binary_vtk_reopens_when_reader_available(tmp_path):
    vtk=pytest.importorskip('vtk')
    c=candidate();record,data=sample(c);path=tmp_path/'occupancy.vtk';path.write_bytes(data)
    reader=vtk.vtkStructuredPointsReader();reader.SetFileName(str(path));reader.Update()
    image=reader.GetOutput();cells=image.GetCellData().GetScalars('solid')
    assert reader.GetErrorCode()==0 and image.GetDimensions()==(17,17,17)
    assert image.GetNumberOfCells()==4096 and cells.GetNumberOfTuples()==4096
    assert sum(int(cells.GetTuple1(i)) for i in range(4096))==record['geometry']['occupied_voxel_count']


def test_allowances_stay_separate_and_unknown_never_becomes_zero():
    c=candidate();r,_=sample(c)
    assert r['allowance_mass_kg']=={name:None for name in implicit.ALLOWANCES}
    assert r['complete_installed_mass_kg'] is None and r['complete_installed_cost'] is None
    allowance=dict(skin=[1.,2.],interfaces_and_attachments=None,installation_and_protection=[3.,9.])
    bounded,_=sample(c,allowance_mass_kg=allowance)
    assert bounded['allowance_mass_kg']==allowance
    assert bounded['geometry']['sampled_solid_mass_kg']==r['geometry']['sampled_solid_mass_kg']
    assert bounded['complete_installed_mass_kg'] is None
    for flag in implicit.FLAGS:assert bounded[flag] is False
    assert not bounded['sampling']['requested_feature_physically_proved']
    assert bounded['engineering_screen']=='unknown'


@pytest.mark.parametrize('arg,value',[
    ('envelope_m',[0,.4,.4]),('envelope_m',[.4,float('nan'),.4]),('envelope_m',[.4,.4]),
    ('period_m',0),('period_m',float('inf')),('period_m',3),('threshold',0),('threshold',float('nan')),
    ('threshold',3.1),('phase_rad',[0,0,float('inf')]),('material_family',''),('material_family','steel/../../x'),
    ('parent_candidate_id','x'*64),('parent_candidate_id','a'*63),
])
def test_invalid_physical_definitions_rejected(arg,value):
    with pytest.raises(ValueError):candidate(**{arg:value})


@pytest.mark.parametrize('dims',[[0,16,16],[16,16,16.],[257,16,16],[256,256,256],[True,16,16],[16,16]])
def test_invalid_or_oversized_grids_rejected_before_allocation(dims,monkeypatch):
    monkeypatch.setattr(implicit.np,'meshgrid',lambda *_a,**_k:pytest.fail('Grid allocated before validation'))
    with pytest.raises(ValueError):implicit.sample(candidate(),dims,density_kg_m3=7850.,minimum_feature_m=.08)


def test_declared_sampling_and_feature_resolution_are_checked_before_allocation(monkeypatch):
    monkeypatch.setattr(implicit.np,'meshgrid',lambda *_a,**_k:pytest.fail('Grid allocated before validation'))
    with pytest.raises(ValueError,match='eight voxel'):implicit.sample(candidate(),[8]*3,density_kg_m3=7850.,minimum_feature_m=.3)
    with pytest.raises(ValueError,match='three voxel'):implicit.sample(candidate(),[16]*3,density_kg_m3=7850.,minimum_feature_m=.01)


@pytest.mark.parametrize('bad',[0,-1,float('inf'),float('nan'),True])
def test_density_rejected_when_not_positive_finite(bad):
    with pytest.raises(ValueError):sample(density_kg_m3=bad)


@pytest.mark.parametrize('allowance',[
    {}, {'skin':[0,1], 'interfaces_and_attachments':None,'installation_and_protection':None},
    {'skin':[2,1], 'interfaces_and_attachments':None,'installation_and_protection':None},
    {'skin':[1,float('nan')], 'interfaces_and_attachments':None,'installation_and_protection':None},
])
def test_bad_allowances_cannot_be_silent(allowance):
    with pytest.raises(ValueError):sample(allowance_mass_kg=allowance)


@pytest.mark.parametrize('damage',['candidate','physical-reseal','promotion','result','result-reseal','vtk','other-candidate'])
def test_tampering_and_cross_candidate_rejected(damage):
    c=candidate();result,vtk=sample(c);expected=result['evaluation_id']
    if damage=='candidate':c['candidate_id']='0'*64
    elif damage=='physical-reseal':
        c['physical_definition']['period_m']=.25;reseal(c,'definition_id')
    elif damage=='promotion':
        c['physical_accepted']=True;reseal(c,'definition_id')
    elif damage=='result':result['geometry']['occupied_voxel_count']+=1
    elif damage=='result-reseal':
        result['geometry']['sampled_solid_mass_kg']=0;reseal(result,'evaluation_id')
    elif damage=='vtk':vtk=vtk[:-2]+bytes([vtk[-2]^1])+b'\n'
    else:c=candidate(threshold=.51)
    with pytest.raises(ValueError):implicit.verify(c,result,vtk,expected_evaluation_id=expected)


def test_other_observed_python_environment_keeps_original_id_and_requires_identical_voxels(monkeypatch):
    c=candidate();record,vtk=sample(c);original=deepcopy(record);expected=record['evaluation_id']
    observed=deepcopy(record['numerical_environment']);observed['python']='3.12.99'
    monkeypatch.setattr(implicit,'_environment',lambda:deepcopy(observed))
    replay=implicit.verify(c,record,vtk,expected_evaluation_id=expected)
    assert replay['evaluation_id']==expected and replay['replay_evaluation_id']!=expected
    assert replay['recorded_environment']==original['numerical_environment'] and replay['replay_environment']==observed
    assert replay['environments_identical'] is False and replay['recorded_environment_independently_attested'] is False
    assert replay['native_evaluator_reuse'] is False and record==original
    with pytest.raises(ValueError):implicit.verify(c,record,vtk[:-2]+bytes([vtk[-2]^1])+b'\n',expected_evaluation_id=expected)


@pytest.mark.parametrize('damage',['version','missing','extra','machine','arithmetic','scope'])
def test_malformed_recorded_environment_fails_even_after_reseal(damage):
    c=candidate();record,vtk=sample(c);env=record['numerical_environment']
    if damage=='version':env['python']='3.bad'
    elif damage=='missing':del env['numpy']
    elif damage=='extra':env['unknown']='x'
    elif damage=='machine':env['machine']='not a valid machine'
    elif damage=='arithmetic':env['arithmetic']='integer'
    else:env['scope']='manufacturing accepted'
    reseal(record,'evaluation_id')
    with pytest.raises(ValueError):implicit.verify(c,record,vtk,expected_evaluation_id=record['evaluation_id'])


def test_resealing_a_forged_runtime_cannot_change_externally_pinned_identity():
    c=candidate();record,vtk=sample(c);expected=record['evaluation_id']
    record['numerical_environment']['python']='3.12.99';reseal(record,'evaluation_id')
    assert record['evaluation_id']!=expected
    with pytest.raises(ValueError,match='expected evaluation identity'):
        implicit.verify(c,record,vtk,expected_evaluation_id=expected)


@pytest.mark.parametrize('damage',['source','density','mass','candidate','interval'])
def test_resealed_content_and_occupancy_cannot_bypass_independent_replay(damage):
    c=candidate();record,vtk=sample(c)
    if damage=='source':record['source_sha256'][implicit.PRODUCER]='0'*64
    elif damage=='density':record['material']['density_kg_m3']+=1
    elif damage=='mass':record['geometry']['sampled_solid_mass_kg']+=1
    elif damage=='candidate':record['candidate_id']='0'*64
    else:record['geometry']['ideal_arithmetic_implicit_volume_interval_m3'][1]=0
    reseal(record,'evaluation_id')
    with pytest.raises(ValueError):implicit.verify(c,record,vtk,expected_evaluation_id=record['evaluation_id'])


def test_changed_but_valid_assumption_requires_a_new_external_identity():
    c=candidate();record,vtk=sample(c);original_id=record['evaluation_id']
    record['allowance_mass_kg']['skin']=[10.,20.];reseal(record,'evaluation_id')
    with pytest.raises(ValueError,match='expected evaluation identity'):
        implicit.verify(c,record,vtk,expected_evaluation_id=original_id)


@pytest.mark.parametrize('expected',[None,'','x'*64,'0'*64,True])
def test_replay_requires_a_matching_externally_expected_identity(expected):
    c=candidate();record,vtk=sample(c)
    with pytest.raises(ValueError,match='expected evaluation identity'):
        implicit.verify(c,record,vtk,expected_evaluation_id=expected)
