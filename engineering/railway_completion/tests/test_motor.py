"""Configured winding/circuit, legacy correspondence and immutable failure tests."""
from copy import deepcopy
from types import SimpleNamespace
import json
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

from engineering.design_search import moving_lim as legacy, railway_bundle, design_grammar
from engineering.railway_twin import model
from engineering.railway_completion import motor as m


@pytest.fixture(scope='module')
def reference():
    return railway_bundle.materialize(design_grammar.initial_candidates()[0])


@pytest.fixture(scope='module')
def short():
    return model.materialize()['bundle']


def reseal(value):
    value['request_id']=m.identity({k:v for k,v in value.items() if k!='request_id'})
    return value


def test_25period_mesh_and_resistance_match_unchanged_legacy_exactly(reference):
    args=dict(start_m=-8.95,speed_m_s=.5,mesh_m=.08,steps=2)
    old=legacy.request(reference,**args);new=m.request(reference,**args)
    for actual,expected in zip(m.mesh(new),legacy.mesh(old)):
        assert np.array_equal(actual,expected)
    assert new['wiring']['coils_per_path']==5
    p,d=new['physical_geometry'],new['motor_definition']
    rho=d['copper_resistivity_20C_ohm_m_hypothesis']*(1+d['copper_temperature_coefficient_K_inv_hypothesis']*60)
    assert np.array_equal(m.path_resistance(new),np.full(30,5*rho*d['wire_length_m_per_coil']/p['conductor_area_m2']))
    assert np.array_equal(m.phase_commands(new,.004),np.repeat(2*np.cos(2*np.pi*30*.004-np.arange(3)*2*np.pi/3),10))


def test_40period_winding_has_eight_series_coils_and_four_each_face(short):
    request=m.request(short)
    points,tri,regions,boundary,branch,sign=m.mesh(request)
    area,_=m.transient_lim.geometry(points,tri)
    centres=points[tri].mean(axis=1)
    assert request['wiring']['coils_per_path']==8
    assert request['wiring']['coil_count']==240
    assert request['wiring']['opposite_face_coil_offset']==40
    slot_area=.04*.055
    for path in range(30):
        for face in (-1,1):
            for polarity in (-1,1):
                active=(branch==path)&(centres[:,1]*face>0)&(sign==polarity)
                assert area[active].sum()/slot_area==pytest.approx(4.,abs=1e-10)
    assert m.estimate(request)['mesh_nodes_within_budget']
    assert m.estimate(request)['Peclet_max']==0


def test_phase_sequence_reversal_is_evaluation_only_not_global_voltage_negation(short):
    forward=m.request(short,phase_direction=1)
    reverse=m.request(short,phase_direction=-1)
    assert forward['motor_component_id']==reverse['motor_component_id']
    assert forward['evaluated_component_definition_id']==reverse['evaluated_component_definition_id']
    assert forward['request_id']!=reverse['request_id']
    a=m.phase_commands(forward,.003)[::10];b=m.phase_commands(reverse,.003)[::10]
    assert b==pytest.approx(a[[0,2,1]])
    assert not np.allclose(b,-a)


@pytest.mark.parametrize('change',[
    {'maximum_nodes':180001},{'maximum_seconds':180.},{'memory_bytes':4*1024**3},
    {'phase_direction':0},{'external_leakage_H_hypothesis':-.001},
    {'available_operating_map':{'approved':True}},{'native_evaluator_admission':True},
])
def test_resealing_cannot_relax_resource_or_evidence_contract(short,change):
    request=m.request(short);request.update(change);reseal(request)
    with pytest.raises(ValueError):m.validate(request)


def test_resealing_cannot_change_actual_40period_series_count(short):
    request=m.request(short);request['wiring']['coils_per_path']=5
    request['wiring']['wiring_hypothesis_id']=m.identity({k:v for k,v in request['wiring'].items() if k!='wiring_hypothesis_id'})
    request['evaluated_component_definition_id']=m.identity(dict(motor_geometry_id=request['motor_component_id'],wiring_hypothesis=request['wiring']))
    with pytest.raises(ValueError):m.validate(reseal(request))


def test_highspeed_unstabilized_request_is_a_preflight_hold(short):
    value=m.estimate(m.request(short,speed_m_s=20.))
    assert value['Peclet_max']>1 and not value['unstabilized_domain_supported']


def test_bound_failure_retains_exact_inputs_and_verifies_without_a_solve(short,tmp_path,monkeypatch):
    request=m.request(short,maximum_nodes=1)
    def forbidden(*args,**kwargs):raise AssertionError('A preflight failure must not dispatch a worker')
    monkeypatch.setattr(m.subprocess,'run',forbidden)
    result=m.run(request,tmp_path/'held')
    assert result['execution']=='held-preflight'
    assert m.verify(tmp_path/'held')['verified']
    replay=m.verify(tmp_path/'held',replay=True)
    assert replay['independent_execution_attempted'] is True
    assert replay['numerical_replay_executed'] is False
    assert (m.Path(replay['replay_package'])/'manifest.json').is_file()
    assert (tmp_path/'held'/'input-sources.tar.gz').is_file()
    assert (tmp_path/'held'/'stdout.log').read_bytes()==b''
    with pytest.raises(ValueError,match='Fresh immutable'):m.run(request,tmp_path/'held')


def test_forged_map_cannot_promote_a_resealed_held_package(short,tmp_path):
    folder=tmp_path/'held';m.run(m.request(short,maximum_nodes=1),folder)
    result=json.loads((folder/'result.json').read_bytes())
    result['available_operating_map']={'passed':True}
    result['evaluation_id']=m.identity({k:v for k,v in result.items() if k!='evaluation_id'})
    (folder/'result.json').write_bytes(m.encoded(result))
    manifest=json.loads((folder/'manifest.json').read_bytes())
    manifest['evaluation_id']=result['evaluation_id']
    manifest['files_sha256']['result.json']=m.digest(folder/'result.json')
    manifest['manifest_id']=m.identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    (folder/'manifest.json').write_bytes(m.encoded(manifest))
    with pytest.raises(ValueError,match='operating evidence'):m.verify(folder)


def test_field_flux_plus_external_leakage_matches_independent_RL_limit():
    # Two opposite branch currents yield field inductance2h per branch.
    R,V,h,L,T=3.,5.,.4,.2,1.;errors=[]
    exact=V/R*(1-np.exp(-R*T/(2*h+L)))
    for steps in (20,40,80):
        dt=T/steps;A=I=0.
        matrix=m.circuit_jacobian(csr_matrix([[1.]]),np.zeros(1),np.zeros(1),1.,
            csr_matrix([[1.,-1.]]),np.full(2,R+L/dt),dt,h)
        for _ in range(steps):
            result=spsolve(matrix,[0.,0.,V+h*A/dt+L*I/dt,-V-h*A/dt-L*I/dt,0.])
            A,u,I,other,neutral=result
            assert A==pytest.approx(2*I) and other==pytest.approx(-I)
        errors.append(abs(I-exact))
    assert errors[2]<errors[1]<errors[0]
    assert errors[0]/errors[1]>1.8 and errors[1]/errors[2]>1.8


def zero_worker_fixture(short,folder,monkeypatch,tool_changes=None):
    """Synthetic tool-receipt fixture; no numerical/native job is executed."""
    request=m.request(short,steps=1,voltage_peak_V=0.)
    p=request['physical_geometry'];area=p['secondary_length_m']*p['secondary_thickness_m']
    row=dict(time_s=request['dt_s'],secondary_start_m=request['start_m'],
        secondary_end_m=request['start_m']+p['secondary_length_m'],conductor_area_m2=area,
        conductor_first_moment_x_m3=area*(request['start_m']+p['secondary_length_m']/2),
        path_currents_A=[0.]*30,phase_currents_A=[0.]*3,phase_voltage_commands_V=[0.]*3,
        primary_copper_W=0.,net_terminal_current_A=0.,external_leakage_energy_J=0.,
        external_leakage_work_W=0.,external_leakage_BE_dissipation_W=0.,thrust_N=0.,
        mechanical_W=0.,magnetic_energy_J=0.,backward_Euler_dissipation_W=0.,
        terminal_W=0.,secondary_Joule_W=0.,stabilization_work_W=0.,discrete_power_residual_W=0.)
    tool=m._tool(request)
    tool.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
        enforced_address_space_limit_bytes=request['memory_bytes'],requested_address_space_limit_bytes=request['memory_bytes'])
    tool.update(tool_changes or {})
    worker=dict(execution='completed',state='synthetic-tool-receipt-fixture',test_fixture_only=True,
        trace=[row],tool=tool,available_operating_map=None,installed_force_available_N=None,
        repeated_thermal_duty_verified=False,converter_current_control_verified=False,**m.FLAGS)
    def fake_worker(*args,**kwargs):
        (folder/'worker-result.json').write_bytes(m.encoded(worker))
        return SimpleNamespace(returncode=0,stdout=b'Synthetic test fixture; no numerical job\n',stderr=b'')
    monkeypatch.setattr(m.subprocess,'run',fake_worker)
    m.run(request,folder)
    return request,tool


def test_recorded_tool_archive_mode_preserves_foreign_tool_identity_and_forbids_exact_reuse(short,tmp_path,monkeypatch):
    folder=tmp_path/'foreign';_,tool=zero_worker_fixture(short,folder,monkeypatch,
        dict(python_sha256='f'*64,numpy='different-recorded-numpy',scipy='different-recorded-scipy'))
    result=m.verify(folder,require_current_tool=False)
    assert result['verified'] and result['recorded_tool_identity']['python_sha256']==tool['python_sha256']
    assert result['current_tool_identity']['python_sha256']!=tool['python_sha256']
    assert not result['toolchain_matches_current'] and not result['native_reuse_eligible']
    assert result['require_current_tool'] is False and result['numerical_replay_executed'] is False
    with pytest.raises(ValueError,match='Numerical tool identity differs'):m.verify(folder)
    def forbidden(*args,**kwargs):raise AssertionError('Mismatched tools cannot dispatch an exact replay')
    monkeypatch.setattr(m,'run',forbidden)
    with pytest.raises(ValueError,match='Numerical tool identity differs'):
        m.verify(folder,require_current_tool=False,replay=True)


def test_matching_recorded_and_current_tool_is_explicitly_eligible_for_exact_native_reuse(short,tmp_path,monkeypatch):
    folder=tmp_path/'matching';zero_worker_fixture(short,folder,monkeypatch)
    result=m.verify(folder)
    assert result['recorded_tool_identity']==result['current_tool_identity']
    assert result['toolchain_matches_current'] and result['native_reuse_eligible']
    assert result['physical_accepted'] is False and result['native_evaluator_admission'] is False


@pytest.mark.parametrize('changes',[
    {'python_sha256':'not-a-digest'}, {'superlu_sha256':'A'*64},
    {'enforced_address_space_limit_bytes':0}, {'OMP_NUM_THREADS':'2'}, {'numpy':''},
])
def test_recorded_mode_cannot_skip_tool_schema_resource_or_thread_contract(short,tmp_path,monkeypatch,changes):
    folder=tmp_path/'invalid';zero_worker_fixture(short,folder,monkeypatch,changes)
    with pytest.raises(ValueError):m.verify(folder,require_current_tool=False)


def test_backiron_rewrite_is_new_bound_physical_candidate_with_actual_wayside_stock(short):
    original=deepcopy(short);changed=m.variant(short,.1)
    assert short==original
    assert changed['candidate_id']!=short['candidate_id']
    assert changed['propulsion_component_id']!=short['propulsion_component_id']
    assert changed['parent_bundle_id']==short['candidate_id']
    assert changed['body_candidate_id']==short['body_candidate_id']
    assert changed['mass']==short['mass']
    assert changed['physical_definition']['vehicle']['onboard_traction_motors']==0
    assert changed['motor_parameters']['physical']['backiron_m']==.1
    for key in ('secondary_length_m','secondary_thickness_m','active_height_m','gap_each_side_m','turns_per_coil'):
        assert changed['motor_parameters']['physical'][key]==short['motor_parameters']['physical'][key]
    assert changed['brake_definition']['candidate_id']==changed['candidate_id']
    assert changed['brake_definition']['propulsion_component_id']==changed['propulsion_component_id']
    assert changed['architecture_case']['physical_definition']['propulsion_definition_id']==changed['propulsion_component_id']
    assert changed['physical_definition']['propulsion']['physical_geometry']==changed['motor_parameters']['physical']
    assert changed['complete_installed_mass_kg'] is None
    old_stock=[s for s in m.wheel_motor.stock(short['motor_parameters']) if s['installation']=='wayside']
    new_stock=[s for s in m.wheel_motor.stock(changed['motor_parameters']) if s['installation']=='wayside']
    expected=2*(.1-.025)*.16*20*7850
    assert sum(s['mass_kg'] for s in new_stock)-sum(s['mass_kg'] for s in old_stock)==pytest.approx(expected)
    assert m.request(changed)['motor_component_id']==changed['propulsion_component_id']


@pytest.mark.parametrize('thickness',[.024,.151,float('nan'),True])
def test_backiron_rewrite_rejects_outside_explicit_construction_domain(short,thickness):
    with pytest.raises(ValueError):m.variant(short,thickness)


def test_reference25_geometry_cannot_be_silently_rewritten_or_relabelled(reference,short):
    with pytest.raises(ValueError,match='only.*20m'):m.variant(reference,.1)
    with pytest.raises(ValueError,match='actually change'):m.variant(short,.025)


def test_rewound_family_changes_real_stock_and_ids_with_same_current_density_obligation(short):
    original=deepcopy(short);rewound=m.rewound_variant(short);r=m.request(rewound)
    p=rewound['motor_parameters']['physical'];d=rewound['motor_definition']
    assert short==original and rewound['candidate_id']!=short['candidate_id']
    assert rewound['propulsion_component_id']!=short['propulsion_component_id']
    assert rewound['mass']==short['mass']
    assert p['backiron_m']==.1 and p['slot_depth_m']==.08 and p['conductor_area_m2']==45e-6
    assert p['turns_per_coil']==40 and p['secondary_length_m']==9 and p['gap_each_side_m']==.015
    assert rewound['motor_parameters']['evaluation']['wire_density_limit_RMS_A_mm2']==4.
    assert d['slot_fill_fraction']==pytest.approx(.5625)
    assert r['current_limit_A']==230 and r['current_density_limit_RMS_A_mm2']==4.
    assert 230/np.sqrt(2)/45<4
    assert m.path_resistance(r)[0]/m.path_resistance(m.request(short))[0]==pytest.approx(25/45)
    base=[p for p in m.wheel_motor.stock(short['motor_parameters']) if p['installation']=='wayside']
    revised=[p for p in m.wheel_motor.stock(rewound['motor_parameters']) if p['installation']=='wayside']
    copper=lambda rows:sum(p['mass_kg'] for p in rows if p['role']=='copper-stock')
    assert copper(revised)/copper(base)==pytest.approx(45/25)
    assert rewound['brake_definition']['propulsion_component_id']==rewound['propulsion_component_id']
    assert rewound['physical_definition']['vehicle']['onboard_traction_motors']==0
    assert rewound['complete_installed_mass_kg'] is None and r['available_operating_map'] is None


def test_rewound_electrical_ceiling_is_only_conditional_headroom_not_available_force(short):
    from engineering.design_search.launch_options import bounds
    rewound=m.rewound_variant(short);r=m.request(rewound)
    required=bounds(6*short['mass']['accounted_cap_loaded_kg_per_car'],
        6*short['rotating_equivalent_kg_per_car'],20.,.4)['required_mechanical_power_W']
    # Balanced three-phase apparent ceiling3*V_rms*I_rms*parallel_paths.
    old_ceiling=1.5*375*140*10;new_ceiling=1.5*375*230*10
    assert old_ceiling<required<new_ceiling
    assert not r['native_evaluator_admission'] and r['actual_converter_loss_W'] is None


@pytest.mark.parametrize('current',[230.01,255.])
def test_rewound_current_bound_cannot_exceed_declared_or_density_envelope(short,current):
    with pytest.raises(ValueError,match='domain exceeded'):
        m.request(m.rewound_variant(short),current_limit_A=current)


def test_old_family_cannot_inherit_rewound_current_or_other_partial_geometry(short):
    with pytest.raises(ValueError,match='domain exceeded'):m.request(short,current_limit_A=230.)
    rewound=m.rewound_variant(short)
    with pytest.raises(ValueError,match='actually change'):m.rewound_variant(rewound)
    with pytest.raises(ValueError,match='physical geometry'):m.variant(rewound,.09)
