"""Independent identities, physical quantities, constraint failures and solver evidence."""
from pathlib import Path
from copy import deepcopy
import hashlib,importlib.util,json,math,sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.design_consistency import demonstrators as d
from engineering.design_consistency.contracts import validate,summary
from engineering.design_consistency.analysis import mandatory_status,bolt_screen,interface_modes,civil_stages
from engineering.design_consistency.search import evaluate,pareto
from osr_mech.section_contract import rhs,geometry,reconcile
from osr_mech.automated_geometry import primitive_volume,aggregate
from osr_mech.rolling_stock.composite_panels import coupled_core,support_network
CONFIG=json.loads((ROOT/'engineering/composite_panels/config/development.json').read_text())
OUT=ROOT/'engineering/design_consistency/examples'


def test_section_area_inertia_and_native_wall_quantities_are_independently_consistent():
    sec=rhs(.16,.28,.008,density_kg_m3=7850);r=reconcile(sec,2,geometry(sec,2))
    assert r['analysis_mass_kg']==pytest.approx((.16*.28-.144*.264)*2*7850)
    assert sec['iy_m4']==pytest.approx((.16*.28**3-.144*.264**3)/12)
    assert sec['j_torsion_m4']!=pytest.approx(sec['polar_area_moment_m4'])
    broken=geometry(sec,2);broken['primitives'][0]['dimensions_m'][2]*=2
    with pytest.raises(ValueError):reconcile(sec,2,broken)


@pytest.mark.parametrize('wall',[0,.08,.1,math.nan])
def test_closed_invalid_section_never_enters_search(wall):
    with pytest.raises(ValueError):rhs(.16,.28,wall,density_kg_m3=7850)


def test_grade_changes_density_and_stiffness_together_and_keeps_temperature_limit():
    a=coupled_core(CONFIG,60);b=coupled_core(CONFIG,100)
    assert a['density_kg_m3']<b['density_kg_m3']and a['shear_pa']<b['shear_pa']and a['compressive_strength_pa']<b['compressive_strength_pa']
    assert a['continuous_max_temperature_c']<85
    with pytest.raises(ValueError):coupled_core(CONFIG,75)


def test_reducing_span_generates_and_charges_for_additional_physical_supports():
    a=support_network(CONFIG,.994,3.45,1);b=support_network(CONFIG,.994,3.45,.5)
    assert b['rail_count']>a['rail_count']and b['bracket_count']>a['bracket_count']and b['mass_kg']>a['mass_kg']
    assert len(b['panel_attachment_sites_m'])==b['panel_attachment_count']
    c=support_network(CONFIG,.994,3.45,1,holes=[(.28,1.1,.71,2.25)])
    assert not c['nominal_span_realised']and len(c['panel_attachment_sites_m'])==c['panel_attachment_count']
    for x,y in c['panel_attachment_sites_m']:assert not(.28<x<.71 and 1.1<y<2.25)


def test_panel_variation_updates_physical_layers_materials_supports_and_response():
    a=d.panel_bay(CONFIG);b=d.panel_bay(CONFIG,skin=.002,core=.03,grade_density=100,span=.5)
    assert summary(b)['mass_kg']>summary(a)['mass_kg']
    assert b['support_network']['rail_count']>a['support_network']['rail_count']
    assert b['materials']['foam']['shear_pa']>a['materials']['foam']['shear_pa']
    assert b['response']['total_deflection_m']<a['response']['total_deflection_m']
    plies=[p for p in b['parts']if 'laminate_ply'in p]
    assert all(p['laminate_ply']['thickness_m']==pytest.approx(.002/8)for p in plies)
    assert {p['laminate_ply']['angle_deg']for p in plies}=={0,45,-45,90}


def test_asymmetric_drilling_moves_cg_without_inventing_mass():
    primitive=dict(id='coupon',kind='perforated-plate',centre_m=[0,0,0],dimensions_m=[1,1,.01],holes_xy_m=[[.2,0]],hole_radius_m=.1)
    prop=aggregate([primitive],[primitive_volume(primitive)*7850])
    assert prop['cg_m'][0]==pytest.approx(-math.pi*.1**2*.2/(1-math.pi*.1**2))
    assert np.linalg.eigvalsh(prop['inertia_tensor_kg_m2']).min()>0


def test_contract_rejects_stale_mass_datum_inertia_and_claimed_release():
    source=d.interface()
    for path,value in [('mass_kg',0),('cg_m',[0,0,5]),('inertia_tensor_kg_m2',np.eye(3).tolist())]:
        broken=deepcopy(source);broken['parts'][0]['analysis'][path]=value
        with pytest.raises(ValueError):validate(broken)
    broken=deepcopy(source);broken['production_released']=True
    with pytest.raises(ValueError):validate(broken)


def test_unknown_mandatory_gate_stays_unknown_and_failure_cannot_be_scored_away():
    assert mandatory_status({'strength':'passed','fire':'unknown'})=='unknown'
    assert mandatory_status({'strength':'failed','cost':'passed'})=='blocked'
    candidate=evaluate(CONFIG,dict(core_m=.03,supports=8,grade=100,curved=True))
    assert candidate['checks']['thermal']=='failed'and candidate['status']=='blocked'and not pareto([candidate])
    assert candidate['installed_cost_usd']is None and not candidate['qualified']


def test_joint_separation_and_slip_are_explicit_not_assumed_passes():
    joint=d.interface()['assembly_joints'][0];a=bolt_screen(joint);b=bolt_screen(joint,separating_force_n=1e6,shear_force_n=1e6)
    assert a['status']=='unknown'and a['fatigue_cycles_to_failure']is None
    assert b['checks']['contact_compression']=='failed'and b['checks']['friction_slip']=='failed'and b['status']=='blocked'


def test_assembled_modal_transfer_preserves_rigid_kinetic_mass_and_inertia():
    model=d.interface();r=interface_modes(model)
    assert r['rigid_mass_inertia_relative_error']<1e-10 and r['mass_orthogonality_error']<1e-8
    assert len(r['physical_part_distribution'])==len(model['parts'])
    assert all(v>0 for v in r['frequencies_hz'])and not r['whole_vehicle_transfer_accepted']
    assert sum(p['mass_kg']for p in r['physical_part_distribution'])==pytest.approx(summary(model)['mass_kg'])


def test_front_carries_real_reinforcement_mass_and_has_no_resource_overlaps():
    model=d.viaduct();r=d.front(model);assert r['schedule_status']=='blocked'
    assert any(not l['transport_eligible']for l in r['lifts'])and r['quoted_installed_cost_usd']is None
    assert len(r['lifts'][0]['physical_part_ids'])>1
    tasks=r['resource_schedule']
    for i,t in enumerate(tasks):
        for s in tasks[i+1:]:
            if set(t['resources'])&set(s['resources']):assert max(t['start_day'],s['start_day'])>=min(t['end_day'],s['end_day'])


def test_full_axle_envelope_and_erection_stages_keep_resistance_unknown():
    trace=json.loads((ROOT/'engineering/industrialisation/vehicle-civil-load-trace.json').read_text());r=civil_stages(d.viaduct(),trace)
    assert r['service']['train_axle_count']==len(trace['reference']['axle_pattern'])and r['service']['simultaneous_tracks']==2
    assert r['service']['complete_axle_sweep']and r['lifting']['dynamic_factor']==1.3
    assert r['checks']['ground_calibration']=='unknown'and not r['production_released']


def test_retained_native_ifc_solver_and_search_evidence_is_current_and_scoped():
    spec=importlib.util.spec_from_file_location('study',ROOT/'tools/automation/design-consistency-study.py');study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)
    for relative in ('manifest.json','cad/verification.json','ifc-verification.json','solver/verification.json'):
        value=json.loads((OUT/relative).read_text());assert value['source_sha256']==study.sources()
        for path,digest in value['output_sha256'].items():assert hashlib.sha256((OUT/path).read_bytes()).hexdigest()==digest
    native=json.loads((OUT/'cad/verification.json').read_text());assert len(native['records'])==4
    assert all(r['native_reopened']and not r['material_intersections']and r['step_reimport_volume_reconciled']for r in native['records'])
    solver=json.loads((OUT/'solver/verification.json').read_text());assert solver['bending_agreement_screen_passed']and solver['refinement_relative_difference']<.01
    search=json.loads((OUT/'mixed-search.json').read_text());assert len(search['trials'])==3 and search['verified_pareto']==[]
    assert all(t['holdout_pressure_pa']==3500 and len(t['random_benchmark'])==t['evaluation_count']for t in search['trials'])
