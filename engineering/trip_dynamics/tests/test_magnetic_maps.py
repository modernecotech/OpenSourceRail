from copy import deepcopy
from itertools import product
import os
from pathlib import Path

import pytest

from engineering.trip_dynamics import magnetic_maps as m


def reseal(value):
    result=deepcopy(value);result.pop('map_id',None);result['map_id']=m.identity(result);return result


def fixture():
    axes={key:[0.] for key in m.REQUIRED_AXES}
    axes.update(gap_m=[.008,.012],lateral_m=[-.001,.001],temperature_C=[20.],current_A=[0.,10.])
    ident={key:str(i+1)*64 for i,key in enumerate(m.IDENTITY_KEYS)}
    rows=[]
    for values in product(*axes.values()):
        q=dict(zip(axes,values));g,y,i=q['gap_m'],q['lateral_m'],q['current_A']
        rows.append(dict(identity=ident,coordinates=q,numerical_status='converged',
            force_N=[2*i,-1000*y,10000-100000*g+10*i],moment_Nm=[5*y,.1*i,g],
            field_energy_J=2+i*i,losses_W=.2*i*i,flux_linkage_Wb_turn={'lift':.002*i}))
    value=dict(schema=m.SCHEMA,identity=ident,frame=deepcopy(m.FRAME),units=deepcopy(m.UNITS),
        axes=axes,current_axes={'lift':'current_A'},rows=rows,source_sha256={'fixture.py':'a'*64},
        execution_status='executed',numerical_status='converged',evidence_kind='synthetic-test',
        physics=dict(spatial_dimension=3,nonlinear_material_solve=True,velocity_dependent=False),
        validation=dict(mesh=dict(state='pass',reason='manufactured mesh test'),domain=dict(state='pass',reason='manufactured domain'),
            material_model=dict(state='pass',reason='manufactured constitutive domain'),
            force=dict(state='pass',reason='signed component comparison',component_absolute_error_N=[.1]*3,component_tolerance_N=[1.]*3),
            moment=dict(state='pass',reason='all moments checked',component_absolute_error_Nm=[.001]*3,component_tolerance_Nm=[.01]*3)),
        ports=dict(field_energy_J='available',flux_linkage_Wb_turn='available',losses_W='available'),physical_accepted=False)
    return m.seal_force_map(value)


def query():
    q={key:0. for key in m.REQUIRED_AXES};q.update(gap_m=.01,temperature_C=20.,current_A=5.);return q


def test_vector_interpolation_all_components_and_ports():
    value=fixture();model=m.ForceMap(value,expected_identity={'candidate_id':'1'*64});r=model.sample(query())
    assert r['force_N']==pytest.approx([10.,0.,9050.])
    assert r['moment_Nm']==pytest.approx([0.,.5,.01])
    assert r['flux_linkage_Wb_turn']['lift']==pytest.approx(.01)
    assert r['losses_W']==pytest.approx(10.)  # interpolation of sampled losses
    assert not r['physical_accepted']


@pytest.mark.parametrize('key,value',[('gap_m',.0120000000001),('lateral_m',.002),('v_m_s',1.),('temperature_C',50.)])
def test_no_extrapolation_even_on_singleton_axes(key,value):
    model=m.ForceMap(fixture());q=query();q[key]=value
    with pytest.raises(m.MapDomainError):model.sample(q)


def test_missing_dimensions_and_missing_vector_components_are_refused():
    value=fixture();value['axes'].pop('yaw_rad')
    with pytest.raises(m.MapError,match='dimensions'):m.validate_force_map(reseal(value))
    value=fixture();value['rows'][0]['moment_Nm']=None
    with pytest.raises(m.MapError,match='three explicit'):m.validate_force_map(reseal(value))
    q=query();q.pop('current_A')
    with pytest.raises(m.MapDomainError):m.ForceMap(fixture()).sample(q)


def test_mixed_candidate_geometry_material_or_evaluation_identity_refused():
    for key in m.IDENTITY_KEYS:
        value=fixture();value['rows'][0]['identity']=dict(value['identity'],**{key:'f'*64})
        with pytest.raises(m.MapError,match='mixed'):m.validate_force_map(reseal(value))
        with pytest.raises(m.MapError,match='identity mismatch'):m.validate_force_map(fixture(),expected_identity={key:'f'*64})


def test_content_corruption_nonconvergence_and_two_dimensions_refused():
    value=fixture();value['rows'][0]['force_N'][0]+=1
    with pytest.raises(m.MapError,match='digest'):m.validate_force_map(value)
    value=fixture();value['numerical_status']='nonconverged'
    with pytest.raises(m.MapError,match='converged'):m.validate_force_map(reseal(value))
    value=fixture();value['physics']['spatial_dimension']=2
    with pytest.raises(m.MapError,match='nonlinear3D'):m.validate_force_map(reseal(value))
    value=fixture();value['rows'][0]['numerical_status']='nonconverged'
    with pytest.raises(m.MapError,match='nonconverged row'):m.validate_force_map(reseal(value))


def test_cartesian_coverage_duplicates_and_off_grid_rows_refused():
    value=fixture();value['rows'].pop()
    with pytest.raises(m.MapError,match='Cartesian'):m.validate_force_map(reseal(value))
    value=fixture();value['rows'][0]=deepcopy(value['rows'][1])
    with pytest.raises(m.MapError,match='duplicate'):m.validate_force_map(reseal(value))


def test_unknown_energy_flux_and_loss_stay_unknown():
    value=fixture();value['ports']={key:'unknown' for key in value['ports']}
    for r in value['rows']:
        for key in value['ports']:r[key]=None
    r=m.ForceMap(reseal(value)).sample(query())
    assert r['losses_W'] is None and r['field_energy_J'] is None and r['flux_linkage_Wb_turn'] is None
    value['rows'][0]['losses_W']=0.
    with pytest.raises(m.MapError,match='silently become zero'):m.validate_force_map(reseal(value))


def test_static_map_cannot_claim_velocity_dependent_forces():
    value=fixture();value['axes']['v_m_s']=[1.]
    for row in value['rows']:row['coordinates']['v_m_s']=1.
    with pytest.raises(m.MapError,match='velocity-dependent'):m.validate_force_map(reseal(value))


def test_force_and_moment_confidence_checks_and_material_domain_required():
    for key,error in [('force','component_absolute_error_N'),('moment','component_absolute_error_Nm')]:
        value=fixture();value['validation'][key][error][1]=100.
        with pytest.raises(m.MapError,match='uncertainty'):m.validate_force_map(reseal(value))
    value=fixture();value['validation']['material_model']['state']='unknown'
    with pytest.raises(m.MapError,match='constitutive'):m.validate_force_map(reseal(value))


def test_frame_units_sources_and_physical_flags_are_strict():
    for mutate in [lambda v:v['frame']['axes'].__setitem__('z','down'),
                   lambda v:v['units'].__setitem__('force','kN'),
                   lambda v:v.__setitem__('source_sha256',{'../solver.py':'a'*64}),
                   lambda v:v.__setitem__('physical_accepted',True)]:
        value=fixture();mutate(value)
        with pytest.raises(m.MapError):m.validate_force_map(reseal(value))


def test_callers_cannot_poison_internal_interpolation():
    value=fixture();model=m.ForceMap(value);expected=model.sample(query())
    value['rows'][0]['force_N'][2]=0.;metadata=model.metadata;metadata['frame']['axes']['z']='down'
    assert model.sample(query())==expected


EVIDENCE_ROOT=Path(os.environ.get('OSR_EVIDENCE_ROOT',str(Path(__file__).resolve().parents[3])))
HAS_EVIDENCE=(EVIDENCE_ROOT/'docs/design-engine/vehicle-optimisation/manifest.json').is_file()


@pytest.mark.skipif(not HAS_EVIDENCE,reason='Explicit retained publication root not present in sparse checkout')
def test_real_publications_preserve_distinct_candidates_and_never_create_3d_maps():
    evidence=m.current_magnetic_evidence(EVIDENCE_ROOT)
    assert not evidence['errors'] and not evidence['force_maps']
    canonical=next(r for r in evidence['records'] if r['family']=='canonical-ferrite')
    assert canonical['points'][0]['force_z_N']==pytest.approx(3064.0009882082604)
    assert canonical['mass_aw3_kg_band']==pytest.approx([37618.5915003343]*2)
    vehicle=dict(candidate_id=canonical['candidate_id'],comparison_aw3_kg_per_car=canonical['mass_aw3_kg_band'][0],mass_ledger_id=canonical['mass_ledger_id'])
    gates=m.assess_magnetic_readiness(evidence,vehicle,dict(candidate_id=canonical['candidate_id'],load_case='AW3',temperature_C=20.))
    assert next(g for g in gates if g['id']=='published-canonical-support-screen')['state']=='unknown'
    at_reference=m.assess_magnetic_readiness(evidence,vehicle,dict(candidate_id=canonical['candidate_id'],load_case='AW3',temperature_C=40.))
    assert next(g for g in at_reference if g['id']=='published-canonical-support-screen')['state']=='fail'
    assert next(g for g in gates if g['id']=='magnetic-nonlinear3d-map')['state']=='unknown'
    assert next(g for g in gates if g['id']=='magnetic-moving-losses')['state']=='unknown'
    assert next(g for g in gates if g['id']=='magnetic-thermal-duty')['state']=='unknown'


@pytest.mark.skipif(not HAS_EVIDENCE,reason='Explicit retained publication root required')
def test_no_cross_candidate_mass_or_hot_temperature_borrowing():
    evidence=m.current_magnetic_evidence(EVIDENCE_ROOT)
    passive=next(r for r in evidence['records'] if r['label']=='B/revised-area-and-ferrite')
    bad=m.assess_magnetic_readiness(evidence,dict(candidate_id=passive['candidate_id'],comparison_aw3_kg_per_car=37618.5915003343),
                                  dict(candidate_id=passive['candidate_id'],load_case='AW3',temperature_C=20.))
    assert next(g for g in bad if g['id']=='magnetic-mass-ledger')['state']=='unknown'
    nd=next(r for r in evidence['records'] if r['label']=='N35-H8-half-no-yoke / lighter-services-two')
    gates=m.assess_magnetic_readiness(evidence,dict(candidate_id=nd['candidate_id'],comparison_aw3_kg_per_car=nd['mass_aw3_kg_band'][-1]),
        dict(candidate_id=nd['candidate_id'],load_case='AW3',temperature_C=20.))
    assert next(g for g in gates if g['id']=='magnetic-load-support')['state']=='unknown'
    assert next(g for g in gates if g['id']=='magnetic-winding-fill')['state']=='fail'


def test_scenario_id_is_distinct_from_candidate_binding():
    evidence=dict(records=[],force_maps=[])
    gates=m.assess_magnetic_readiness(evidence,dict(candidate_id='a'*64),dict(candidate_id='b'*64,scenario_id='a'*64))
    assert next(g for g in gates if g['id']=='magnetic-scenario-binding')['state']=='fail'
