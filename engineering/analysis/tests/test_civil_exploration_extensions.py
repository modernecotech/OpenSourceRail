"""Independent mechanics, complete quantities, safe retrieval and workflow gates."""
from copy import deepcopy
from pathlib import Path
import math
import json
import tempfile

import numpy as np
import pytest

from osr_mech.civil.exploration import geometry,deck_section,foundation_geometry,assembly_cad,rectangle
from engineering.civil_exploration.contracts import HERE,ROOT,load,encoded,sha,validate_study
from engineering.civil_exploration.workflow import candidate
from engineering.civil_exploration.model import takeoff,System
from engineering.civil_exploration import materials,commercial,storage,search,validation,nonlinear,orthotropic,detailed,connections,vehicle


def reference():
    study=load(HERE/'config/reference.json')
    return study,candidate(study['candidates'][1],study)


@pytest.mark.parametrize('family',['conventional-I','U-girder','ribbed-deck','uhpc-ribbed','hybrid-shell','segmental-box'])
def test_registered_family_geometry_has_disjoint_materials_and_positive_inertia(family):
    s,c=reference();definition=deepcopy(c['definition']);definition['deck']['family']=family
    g=geometry(definition)
    assert g['deck'][1]['inertia_y_m4']>0
    assert len(g['deck'][1]['regions'])==len(g['deck'][1]['material_roles'])
    assert len(g['deck'])==3 and g['deck'][0]['area_m2']>g['deck'][1]['area_m2']


def test_family_rejects_ignored_parameters_and_missing_material_records():
    s,c=reference();c['definition']['deck']['family']='U-girder';c['definition']['deck']['parameters']['top_m']=.2
    with pytest.raises(ValueError,match='ignored'):geometry(c['definition'])
    s['candidates'][0]['deck']['family']='hybrid-shell'
    with pytest.raises(ValueError,match='material record'):validate_study(s)


def test_foundation_and_complete_cad_quantity_matches_independent_takeoff():
    s,c=reference();f=foundation_geometry(c['foundation'])
    expected=4*math.pi*.5**2*15+4*4*1.5
    assert f['pile_concrete_m3']+f['cap_concrete_m3']==pytest.approx(expected)
    assert assembly_cad(c['definition'],c['foundation'],100.).volume/1e9==pytest.approx(takeoff(c,s)['concrete_m3'])
    bad=deepcopy(c['foundation']);bad['cap_width_m']=.5
    with pytest.raises(ValueError,match='fit'):foundation_geometry(bad)


def test_transformed_composite_section_matches_independent_parallel_axis_sum():
    section=dict(regions=[rectangle(1.,.1,z=.05),rectangle(1.,.1,z=.15)],material_roles=['concrete','frp'],
                 area_m2=.2,shear_area_m2=.15)
    records=dict(concrete=dict(youngs_modulus_pa=30e9,poisson_ratio=.2,density_kg_m3=2500.,basis='fixture',measured=False),
                 frp=dict(youngs_modulus_pa=10e9,poisson_ratio=.25,density_kg_m3=1800.,basis='fixture',measured=False))
    r=materials.elastic_matrix(section,records,30e9)
    centre=(30*.05+10*.15)/40
    expected=30e9*(.1**3/12+.1*(.05-centre)**2)+10e9*(.1**3/12+.1*(.15-centre)**2)
    assert r['neutral_axis_z_m']==pytest.approx(centre)
    assert r['effective_EI_nm2']==pytest.approx(expected)
    assert r['mass_kg_m']==pytest.approx(430.)
    with pytest.raises(ValueError,match='missing material'):materials.elastic_matrix(section,{'concrete':records['concrete']},30e9)


def test_hybrid_quantity_does_not_count_frp_as_concrete():
    from engineering.civil_exploration.programme import families
    pytest.importorskip('openseespy.opensees')
    s,c=reference();_,rows,_=families(s)
    hybrid=next(r for r in rows if r['family']=='hybrid-shell')
    q=hybrid['quantities'];assert q['deck_material_volumes_m3']['frp']>0
    assert q['deck_concrete_m3']==pytest.approx(q['deck_material_volumes_m3']['concrete'])
    assert commercial.bill(hybrid['candidate'],s)['frp_material_and_fabrication']['quantity']==q['deck_material_volumes_m3']['frp']


def test_native_nonlinear_sections_and_piles_reproduce_registered_checks():
    pytest.importorskip('openseespy.opensees')
    p=load(HERE/'config/components.json')
    r=nonlinear.moment_curvature([rectangle(2.,1.5,z=.75)],p['concrete'],p['steel'],steps=30)
    assert r['observed_initial_EI_nm2']==pytest.approx(r['initial_EI_nm2'],rel=.001)
    assert r['peak_moment_nm'] < r['initial_EI_nm2']*.006
    assert r['physical_release'] is False
    pile=nonlinear.pile(p['pile']);assert pile['curve'][-1]['load_factor']==pytest.approx(1.)
    assert sum(row['pult_n'] for row in pile['springs'])==pytest.approx(p['pile']['pult_n_m']*15*.7)
    r=nonlinear.pier_pdelta(8.,3.,.5625,30e9,100e6,1e5)
    assert r['amplification']>1. and r['analytical_relative_error']<.002


def test_native_friction_cycle_has_mechanical_limit_and_hysteresis():
    pytest.importorskip('openseespy.opensees')
    r=connections.friction_cycle()
    assert r['benchmark_passed'] and r['peak_shear_n']==pytest.approx(300000.)
    assert r['curve'][-1]['shear_n']!=0 and r['curve'][-1]['slip_m']==0


def test_genuine_continuity_changes_bearings_while_link_slab_does_not():
    pytest.importorskip('openseespy.opensees')
    s,c=reference();s['connection_scheme']='link-slab';link=takeoff(c,s)
    s['connection_scheme']='continuous';continuous=takeoff(c,s)
    assert link['bearing_count']==32 and continuous['bearing_count']==20
    model=System(c,s,s['ground_scenarios'][0],8)
    assert any(r['type']=='structural-continuity' for r in model.assembly()['rigid_links'])
    cold=model.thermal(0.,1e-5)
    assert cold['peak_bearing_movement_m']==pytest.approx(0.,abs=1e-10)
    assert cold['peak_corrected_axial_force_n']==pytest.approx(0.,abs=.01)


def test_real_section_mesh_volume_and_load_cover_the_source():
    s,c=reference()
    for family in ('pi','hollow-box','U-girder'):
        d=deepcopy(c['definition']);d['deck']['family']=family
        m=detailed.mesh(d,1.)
        assert m['concrete_or_matrix_volume_m3']==pytest.approx(sum((x['end_m']-x['start_m'])*x['area_m2'] for x in geometry(d)['deck']))
        assert sum(m['top_face_weights_m2'].values())==pytest.approx(25*2.9)
        assert all(len(set(e['nodes']))==20 for e in m['elements'])


def test_native_solid_exchange_and_stress_allocations(tmp_path):
    if not __import__('shutil').which('ccx'):pytest.skip('CalculiX unavailable')
    s,c=reference();c['definition']['deck']['span_m']=20.
    r=detailed.run(c,s,1.,tmp_path/'solid')
    assert r['midspan_displacement_m']>0 and r['peak_von_mises_pa']>0
    fields=load(tmp_path/'solid/stress-fields.json')
    assert len({(r['element_id'],r['integration_point']) for r in fields})==len(fields)
    assert (tmp_path/'solid/native-exchange.csv').is_file()


def test_orthotropic_native_coupon_and_invalid_energy_matrix(tmp_path):
    m=dict(ex_pa=25e9,ey_pa=8e9,ez_pa=8e9,nu_xy=.25,nu_xz=.25,nu_yz=.3,gxy_pa=3e9,gxz_pa=3e9,gyz_pa=3e9)
    assert min(np.linalg.eigvalsh(orthotropic.validate(m)))>0
    bad=deepcopy(m);bad['nu_yz']=5.
    with pytest.raises(ValueError,match='positive definite'):orthotropic.validate(bad)
    if not __import__('shutil').which('ccx'):pytest.skip('CalculiX unavailable')
    assert orthotropic.coupon(m,tmp_path/'coupon')['passed']


def test_coupled_vehicle_matches_small_mass_limit_and_symmetric_matrices():
    v=dict(sprung_mass_kg=50.,unsprung_mass_kg=5.,suspension_n_m=1e7,suspension_ns_m=0.,contact_n_m=1e9,
           bridge_damping_ratio=0.,irregularity_amplitude_m=0.,irregularity_wavelength_m=10.,basis='verification')
    M,C,K,_=vehicle.matrices(5.4e9,3000.,20.,8,v,[10.])
    assert np.allclose(K,K.T) and np.allclose(C,C.T) and min(np.linalg.eigvalsh(M))>0
    r=vehicle.run(5.4e9,3000.,20.,[0.],v,speed=10.,dt=.001)
    from engineering.analysis.benchmarks.civil.exploration import moving_point_analytical
    expected=max(abs(moving_point_analytical(float(t),20.,10.,55*9.81,5.4e9,3000.,0.)) for t in np.arange(.001,2.001,.001))
    assert r['peak_displacement_m']==pytest.approx(expected,rel=.01)


def test_unknown_costs_and_unit_mismatches_cannot_make_a_cheapest_claim():
    s,c=reference();inputs=load(HERE/'config/commercial.json')
    r=commercial.price(c,s,inputs)
    assert r['installed_cost_usd'] is None and r['whole_life_cost_usd'] is None
    assert set(r['unpriced_scope'])==set(commercial.bill(c,s))
    inputs['rates']['deck_concrete']=dict(unit='kg',rate=10.,currency='USD',source='',source_sha256='',classification='assumption',expiry_date=None)
    with pytest.raises(ValueError,match='unit'):commercial.price(c,s,inputs)


def test_conditional_lifecycle_cost_matches_independent_discount_arithmetic():
    s,c=reference();inputs=load(HERE/'config/commercial.json')
    inputs['rates']={key:dict(unit=row['unit'],rate=1.,currency='USD',source='synthetic fixture',source_sha256='',classification='assumption',expiry_date=None) for key,row in commercial.bill(c,s).items()}
    inputs['life_years']=2;inputs['real_discount_rate']=.1;inputs['maintenance_annual']=100.
    inputs['replacement_events']=[dict(year=2,cost_usd=500.,basis='synthetic replacement scenario')]
    r=commercial.price(c,s,inputs)
    assert r['whole_life_cost_usd']==pytest.approx(r['installed_cost_usd']+100/1.1+600/1.1**2)
    assert r['classification']=='conditional-priced-scenario' and not r['physical_release']


def test_archives_roundtrip_and_reject_tampered_parts(tmp_path):
    source=tmp_path/'source';source.mkdir();(source/'nested').mkdir();(source/'nested/data.json').write_bytes(encoded({'a':list(range(1000))}))
    (source/'random.bin').write_bytes(__import__('os').urandom(8000))
    index=storage.pack(source,tmp_path/'store',maximum=1024)
    assert len(index['parts'])>1 and max(p['bytes'] for p in index['parts'])<=1024
    restored=storage.restore(tmp_path/'store',tmp_path/'restored')
    assert restored['integrity_verified'] and sha(source/'random.bin')==sha(tmp_path/'restored/random.bin')
    first=tmp_path/'store'/index['parts'][0]['name'];first.write_bytes(b'changed')
    with pytest.raises(ValueError,match='integrity'):storage.restore(tmp_path/'store',tmp_path/'bad')
    assert not (tmp_path/'bad').exists()


def test_archive_traversal_and_symlinks_are_rejected(tmp_path):
    with pytest.raises(ValueError,match='escapes'):storage.safe(tmp_path,'../outside')
    source=tmp_path/'source';source.mkdir();(source/'link').symlink_to('/etc/passwd')
    with pytest.raises(ValueError,match='symlink'):storage.pack(source,tmp_path/'store')


def test_calibration_holdout_separation_and_empty_physical_protocols():
    # Repository source is a controlled synthetic fixture, never a lab result.
    source='engineering/civil_exploration/config/components.json'
    dataset=dict(schema='osr-civil-validation-data/1',property='youngs_modulus',unit='Pa',specimen_batch='synthetic',source=source,
                 source_sha256=sha(ROOT/source),measurement_uncertainty=0.,
                 calibration=[dict(specimen_id=f'c{i}',strain=x,stress_pa=30e9*x) for i,x in enumerate((.00001,.00002))],
                 holdout=[dict(specimen_id=f'h{i}',strain=x,stress_pa=30e9*x) for i,x in enumerate((.000015,.000025))])
    r=validation.fit_and_holdout(dataset)
    assert r['fitted_modulus_pa']==pytest.approx(30e9) and r['physical_acceptance'] is False
    dataset['holdout'][0]['specimen_id']='c0'
    with pytest.raises(ValueError,match='leakage'):validation.fit_and_holdout(dataset)


def test_search_equal_budget_resume_and_checkpoint_integrity(tmp_path):
    pytest.importorskip('openseespy.opensees')
    s,c=reference()
    report=search.run(s,tmp_path/'search',seeds=[11],evaluations=16,population=4)
    assert [r['completed_evaluations'] for r in report['methods']]==[16,16]
    assert report['qualified_feasible_pareto_set']==[] and report['physical_release'] is False
    hashes={p:sha(p) for p in (tmp_path/'search/results').glob('*.json')}
    resumed=search.run(s,tmp_path/'search',seeds=[11],evaluations=16,population=4,resume=True)
    assert report['shortlist']==resumed['shortlist'] and {p:sha(p) for p in hashes}==hashes
    path=next(iter(hashes));path.write_text('{}')
    with pytest.raises(ValueError,match='checkpoint'):search.run(s,tmp_path/'search',seeds=[11],evaluations=16,population=4,resume=True)


def test_ifc_geometry_has_stable_identifiers_and_source_volumes(tmp_path):
    ifc=pytest.importorskip('ifcopenshell')
    from engineering.civil_exploration.bim import export
    s,c=reference();first=export(c,s,tmp_path/'one.ifc');second=export(c,s,tmp_path/'two.ifc')
    assert first['source_volume_m3']==pytest.approx(takeoff(c,s)['concrete_m3'])
    assert first['ifc_sha256']==second['ifc_sha256']
    native=ifc.open(str(tmp_path/'one.ifc'))
    assert len(native.by_type('IfcPile'))==20 and len({p.GlobalId for p in native.by_type('IfcElement')})==len(native.by_type('IfcElement'))


def test_measured_claims_need_controlled_evidence_and_preserve_source_binding():
    s,c=reference();s['foundation']['site_verified']=True
    with pytest.raises(ValueError,match='controlled evidence'):validate_study(s)
    # Synthetic source binding checks the software contract only, not a site.
    path='engineering/civil_exploration/config/components.json'
    s['evidence_refs']={'foundation':dict(source=path,sha256=sha(ROOT/path),basis='synthetic binding fixture')}
    validate_study(s)
    s['evidence_refs']['foundation']['sha256']='0'*64
    with pytest.raises(ValueError,match='missing/stale'):validate_study(s)


def test_unrelated_accepted_gate_cannot_promote_unresolved_research(tmp_path,monkeypatch):
    s,c=reference();bundle=tmp_path/'bundle';(bundle/'case').mkdir(parents=True)
    (bundle/'study.json').write_bytes(encoded(s));(bundle/'manifest.json').write_bytes(encoded({'synthetic':True}))
    (bundle/'case/record.json').write_bytes(encoded(dict(status='completed')))
    (bundle/'case/result.json').write_bytes(encoded(dict(engineering_feasibility='unresolved',physical_validation=False)))
    manifest=dict(complete=True,cases=[dict(candidate_id=c['id'])],study_sha256=sha(bundle/'study.json'),
                  evaluations=[dict(path='case/record.json',sha256=sha(bundle/'case/record.json'))])
    monkeypatch.setattr(validation,'verify',lambda _:manifest)
    monkeypatch.setattr(validation.structural_release,'build_report',lambda *a,**k:dict(authority_accepted=True,missing_technical_roles=[]))
    proposal=validation.promotion(bundle,tmp_path/'proposal',design=tmp_path/'design',receipt_manifest=tmp_path/'receipt',evidence_root=tmp_path/'evidence')
    assert proposal['status']=='blocked-awaiting-physical-and-independent-evidence'
    assert proposal['candidate_specific_qualification'] is False and proposal['physical_release'] is False
    assert load(tmp_path/'proposal/seal.json')['accepted'] is False
