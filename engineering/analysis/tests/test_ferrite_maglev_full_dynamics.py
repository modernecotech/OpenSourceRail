"""Independent conservation/refusal controls for continued physical states."""
import ctypes as C
from hashlib import sha256
import math
import subprocess
from types import SimpleNamespace

import numpy as np
import pytest

from engineering.ferrite_maglev import full_dynamics as d


@pytest.fixture(scope='module')
def kernel():
    target=d.ROOT/'build/full-dynamics-test-kernel'
    command=['cargo','build','--locked','--release','--manifest-path',str(d.KERNEL/'Cargo.toml'),'--target-dir',str(target)]
    result=subprocess.run(command,cwd=d.ROOT,capture_output=True,text=True,timeout=300)
    assert result.returncode==0,result.stderr
    return target/'release/libosr_full_dynamics_kernel.so'


def current_fixture(kernel):
    a=d.load();plant=d.RustPlant(kernel,a,'a'*64)
    channels=dict(resistance=np.full((144,2),.1),inductance=np.broadcast_to([[.02,.003],[.003,.04]],(144,2,2)).copy(),
        emf=np.zeros((144,2)),targets=np.tile([20.,-5.],(144,1)),reserve_targets=np.tile([20.,-5.],(144,1)),
        current=np.tile([20.,-5.],(144,1)),temperature=np.full((144,2),40.),copper_mass=np.full((144,2),5.),
        cooling=np.zeros((144,2)),faults=np.zeros(144,dtype='u4'),reserve_energy=np.full(6,100000.),reserve_aux=np.full(6,120.))
    return plant,channels


def advance(plant,c):
    output,current,temp=plant.current_step(**c)
    c.update(current=current,temperature=temp,reserve_energy=np.array(output.reserve_remaining_j))
    return output


def test_no_capture_negative_is_declared_and_all_cases_unique():
    a=d.load();assert len(a['cases'])==14
    assert len({r['id'] for r in a['cases']})==14
    assert any(r['fault']=='no-capture' for r in a['cases'])
    assert next(r for r in a['cases'] if r['id']=='asymmetric-load')['fault']=='none'
    for row in a['cases']:assert d.validate_case(row)==row
    with pytest.raises(ValueError,match='named fault'):d.validate_case(dict(a['cases'][0],fault='unimplemented'))


def test_protection_contact_revision_counts_every_hanger_tie_and_strip():
    value,rows=d.protection()
    assert sum(r['unit_mass_kg']*r['quantity_per_car'] for r in rows.values())==pytest.approx(405.1243056)
    assert rows['protection/capture-hanger-kit']['unit_mass_kg']==pytest.approx(10.22)
    assert value['guideway_rows'][0]['mass_kg_per_track_m']==pytest.approx(2*.012*.2*7850)
    assert not rows['protection/capture-shoe']['contact_interface']['fit_verified']
    assert not rows['protection/independent-guideway-brake']['contact_interface']['qualified']
    assert all(value[k] is False for k in d.FLAGS)
    assert rows['protection/independent-reserve-battery']['ratings']['gross_energy_kwh']==1.5


def test_parallel_axis_offcentre_equipment_changes_all_inertias():
    regions=[dict(mass_kg=10.,position_m=[-1.,0.,0.],bounds_m=[.2,.2,.2]),dict(mass_kg=10.,position_m=[1.,0.,0.],bounds_m=[.2,.2,.2])]
    r=d.mass_properties(regions)
    assert r['mass_kg']==20 and r['cg_m']==[0.,0.,0.]
    assert r['inertia_kg_m2'][1][1]==pytest.approx(20+20*.08/12)
    assert r['inertia_kg_m2'][0][0]==pytest.approx(20*.08/12)
    assert r['measured'] is False


def test_unilateral_capture_has_no_tension_and_compression_only_dissipation():
    force,energy,loss=d.contact_force(np.array([-.01,0.,.002,.002]),np.array([1.,1.,1.,-1.]),1e7,2e4)
    assert np.all(force[:2]==0) and np.all(energy[:2]==0) and np.all(loss[:2]==0)
    assert force[2]==pytest.approx(40000.) and force[3]==pytest.approx(20000.)
    assert loss[2]==20000 and loss[3]==0


def test_modal_midpoint_work_damping_energy_closes_independently():
    q=np.array([.02,-.01]);v=np.array([.2,.1]);mass=np.array([15.,25.]);k=np.array([1e4,2e4]);c=np.array([25.,20.]);f=np.array([35.,-20.])
    q1,v1,loss=d.modal_step(q,v,f,mass,k,c,.001)
    change=np.sum((mass*(v1*v1-v*v)+k*(q1*q1-q*q))/2)
    assert change==pytest.approx(np.sum(f*(q1-q))-loss.sum(),abs=1e-12)


def test_rigid_band_terminal_curve_has_real_chord_offset():
    offset=d.curve_offsets([-5.5,0,5.5],50.)
    assert offset[0]==pytest.approx(50-math.sqrt(2500-5.5**2))
    assert offset[0]>.3 and offset[1]==0 and offset[0]==offset[2]


def test_actual_rust_current_refusal_keeps_rl_current_and_then_uses_reserve(kernel):
    plant,c=current_fixture(kernel)
    normal=advance(plant,c);assert normal.primary_fault_channels==0
    old=c['current'].copy();c['faults'][:]=1|512
    delayed=advance(plant,c)
    assert delayed.primary_fault_channels>0 and delayed.reserve_used_channels==0
    assert np.all(np.abs(c['current'])>0) and np.max(np.abs(c['current']-old))<1
    c['faults'][:]=1
    fallback=advance(plant,c)
    assert fallback.reserve_used_channels>0 and fallback.reserve_draw_j>0
    assert fallback.physical_output_authorised==0
    assert fallback.maximum_rl_residual_j<1e-10
    assert np.sum(c['reserve_energy'])<600000.


def test_empty_reserve_does_not_instantly_remove_current_or_invent_energy(kernel):
    plant,c=current_fixture(kernel);c['faults'][:]=1|128;c['reserve_energy'][:]=0.
    initial=c['current'].copy();out=advance(plant,c)
    assert out.reserve_draw_j==0 and out.reserve_used_channels==0
    assert np.linalg.norm(c['current'])<np.linalg.norm(initial)
    assert np.linalg.norm(c['current'])>.9*np.linalg.norm(initial)
    assert out.maximum_rl_residual_j<1e-10


def test_reserve_brownout_is_latched_without_overdraw(kernel):
    plant,c=current_fixture(kernel);c['faults'][:]=1;c['reserve_energy'][:]=1e-8
    out=advance(plant,c)
    assert out.reserve_depleted_cars==63
    assert np.all(c['reserve_energy']>=0)
    assert out.reserve_draw_j<=6e-8


def test_primary_disagreement_and_watchdog_use_real_rust_refusal(kernel):
    for flags,expected in [(4,4),(16,3)]:
        plant,c=current_fixture(kernel);c['faults'][:]=flags
        out=advance(plant,c)
        assert out.primary_fault_channels>0
        assert out.modules[0].primary[0].fault==expected
        assert out.reserve_used_channels>0


def test_actual_receiver_authority_loss_continues_current_decay_and_energy(kernel):
    a=d.load();rust=d.RustPlant(kernel,a,'a'*64);receiver=d.ReceiverPlant(rust.lib,a,'a'*64)
    r,force=receiver.tick(np.full(6,12.),np.full(6,5000.),False)
    assert np.all(force<0) and r.maximum_residual_j<1e-8
    before=np.array([list(x.current_dq_a) for x in r.receivers])
    bad,force=receiver.tick(np.full(6,12.),np.full(6,5000.),False,gates={})
    assert bad.refused_microsteps>0 and bad.maximum_residual_j<1e-8
    assert np.any(np.asarray([list(x.current_dq_a) for x in bad.receivers])!=0)
    assert bad.receivers[0].state.fault==8
    assert bad.physical_output_authorised==0


def test_authority_requires_exact_config_freshness_and_actual_protocol():
    event=dict(schema='osr-full-dynamics-authority/1',configuration_sha256='a'*64,actual_rust_protocol=True,
        physical_output_authorised=False,protected=True,committed=True,receiver_ready=True,resistor_ready=True,
        issued_s=1.,expires_s=1.1,sequence=1,source_receipt_sha256='b'*64)
    assert d.authority_at([event],1.05,'a'*64)['permitted']
    assert not d.authority_at([event],1.11,'a'*64)['permitted']
    assert not d.authority_at([event],1.05,'c'*64)['permitted']
    assert not d.authority_at([],1.,'a'*64)['permitted']
    with pytest.raises(ValueError,match='sequence/time'):d.authority_at([event,event],1.05,'a'*64)
    with pytest.raises(ValueError,match='sequence/time'):d.authority_at([dict(event,expires_s=2.)],1.05,'a'*64)


def test_interface_is_offline_and_target_timing_is_not_host_timing():
    v=d.io_design()
    assert not v['sbc']['target_timing_measured'] and not v['local_mcu']['target_build_and_timing_measured']
    assert v['topology']['current_circuits_per_module']==2
    assert v['output_packet']['hardware_addresses']==[] and not v['output_packet']['physical_outputs_enabled']
    assert all(x[k] is False for x in [v] for k in d.FLAGS)


def test_actual_rust_preferred_allocation_preserves_wrench_and_is_not_uniform(kernel):
    a=d.load();plant=d.RustPlant(kernel,a,'a'*64)
    positions=np.array([[x,y,-.5] for y in (-.88,.88) for x in np.arange(-5.5,6.,1.)])
    weights=np.tile([1,1,2,2,2,2,2,2,2,2,1,1],2).astype(float);weights*=10000*a['gravity_m_s2']/weights.sum()
    plant.preferred=weights;plant.previous_forces[:,:,0]=weights
    forces,status=plant.allocation(a,positions,10000.,np.zeros((6,5)),np.zeros((6,5)),np.zeros(6))
    assert status==[0]*6
    assert np.ptp(forces[0,:,0])>1000
    for f in forces:
        assert f[:,0].sum()==pytest.approx(98100.,abs=20.)
        assert np.sum(positions[:,1]*f[:,0]-positions[:,2]*f[:,1])==pytest.approx(0.,abs=50.)
        assert np.sum(-positions[:,0]*f[:,0])==pytest.approx(0.,abs=50.)
        assert f[:,1].sum()==pytest.approx(0.,abs=20.)
    plant.preferred=None
    uniform,status=plant.allocation(a,positions,10000.,np.zeros((6,5)),np.zeros((6,5)),np.zeros(6))
    assert status==[0]*6 and np.ptp(uniform[0,:,0])<1e-6


def test_real_group_voltage_kernel_conserves_energy_and_refuses_authority(kernel):
    plant=d.GroupPlant(C.CDLL(str(kernel)),'a'*64,2)
    args=dict(resistance=np.array([.1,.2]),inductance=np.array([.02,.03]),phase=np.array([.2,-.7]),omega=np.array([10.,12.]),flux=np.array([.1,.2]),
        targets=np.array([20.,30.]),emf=np.array([[.1,.2],[.2,.3]]),copper_mass=np.array([10.,15.]),current_limit=1350.,bus=2400.,mode=0,gates=15)
    good,current=plant.tick(**args)
    assert np.linalg.norm(current)>0 and good.maximum_residual_j<1e-10
    assert good.maximum_voltage_v>0 and good.physical_output_authorised==0
    before=plant.view['current_ab_a'].copy();args['gates']=0
    bad,current=plant.tick(**args)
    assert bad.refused_microsteps==40 and bad.maximum_residual_j<1e-10
    assert np.any(current!=0) and np.any(plant.view['current_ab_a']!=before)
    assert bad.dc_j==0 and bad.dump_heat_j>0
    assert bad.groups[0].state.fault==8


def test_capture_drop_energy_cannot_fit_old_400kn_capacity():
    mass=37600.;g=9.81;drop=.005;stroke=.008
    # Independent energy lower bound, even before impact damping/unequal pads.
    minimum_average_reaction=mass*g*(1+drop/stroke)
    assert minimum_average_reaction>8*50000.
    assert minimum_average_reaction*stroke==pytest.approx(mass*g*(drop+stroke))


def test_actual_rust_allocator_enforces_residual_pm_lift_floor(kernel):
    a=d.load();plant=d.RustPlant(kernel,a,'a'*64)
    positions=np.array([[x,y,-.5] for y in (-.88,.88) for x in np.arange(-5.5,6.,1.)])
    weights=np.tile([0,0,1,1,1,1,1,1,1,1,0,0],2).astype(float);weights*=98100/weights.sum()
    plant.preferred=weights;plant.previous_forces[:,:,0]=98100/24
    plant.physical_limits=np.broadcast_to([2000.,20000.],(6,24,2)).copy()
    force,status=plant.allocation(a,positions,10000.,np.zeros((6,5)),np.zeros((6,5)),np.zeros(6))
    assert status==[0]*6
    assert force[:,:,0].min()>=2000-1e-9
    assert np.all(abs(force[:,:,0].sum(axis=1)-98100)<20)


def guideway_fixture():
    return d.Guideway(dict(span_m=25.,distributed_mass_kg_m=2000.,polar_mass_per_length_kg_m=1000.,young_pa=34e9,
        vertical_inertia_m4=.5,lateral_inertia_m4=.03,shear_pa=14e9,torsion_constant_m4=.1,damping_fraction=.03,
        beam_centroid_z_m=-2.,gravity_m_s2=9.81),1)


def test_guideway_torsion_uses_actual_section_centroid():
    guide=guideway_fixture();guide.q[0,2]=.01
    pose,_=guide.pose(np.array([12.5]),np.array([.4]),np.array([1.]))
    assert pose[0,0]==pytest.approx(.004) and pose[0,1]==pytest.approx(-.03)
    guide.q[:]=0.
    result=guide.advance(np.array([12.5]),np.array([.4]),np.array([1.]),np.array([0.]),np.array([100.]),np.array([0.]),.0001)
    assert result['peak_torsion_nm']==pytest.approx(300.)
    assert abs(result['mechanical_energy_residual_j'])<1e-10


def test_longitudinal_braking_eccentricity_reaches_bearing_reactions():
    guide=guideway_fixture()
    result=guide.advance(np.array([12.5]),np.array([.4]),np.array([1.]),np.array([0.]),np.array([0.]),np.array([0.]),.0001,vehicle_longitudinal=np.array([-1000.]))
    assert result['applied_pitch_moments_nm']==pytest.approx([3000.])
    assert result['live_reactions_n']==pytest.approx([-120.,120.],abs=1e-8)
    assert result['lateral_reactions_n']==pytest.approx([-16.,16.],abs=1e-8)
    assert sum(result['dead_reactions_n'])==pytest.approx(2000*25*9.81)


def test_new_mandatory_map_failure_disqualifies_a_converged_inverse():
    # Explicit synthetic refusal fixture, not physical evidence: the numerical
    # target converges, but an applicable stationary-rail/material check fails.
    model=d.MagneticPlant.__new__(d.MagneticPlant);model.inverse_flux={}
    model.module=SimpleNamespace(inverse_current=lambda **kw:dict(current_a=np.zeros((144,2)),converged=np.ones(144,dtype=bool),
        valid=np.zeros(144,dtype=bool),force_residual_n=np.zeros((144,2)),flux_state_wb=np.zeros((144,4))))
    _,valid,_=model.inverse(np.zeros((144,2)),np.full((144,4),.008),np.full((144,2),40.),np.zeros((144,2)))
    assert not valid.any()
