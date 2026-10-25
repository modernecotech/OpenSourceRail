from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from engineering.electropermanent import catalogue, pulse, publication, study


def test_rl_exact_solution_matches_independent_ode_and_energy_ports():
    R,L,V,T=2.,.03,12.,.02
    result=pulse.rl_pulse(R,L,V,T)
    ode=solve_ivp(lambda t,y:[(V-R*y[0])/L,V*y[0],R*y[0]**2],
                  (0,T),[0.,0.,0.],rtol=1e-11,atol=1e-12,method='DOP853')
    assert result['final_current_A']==pytest.approx(ode.y[0,-1],rel=1e-10)
    assert result['input_VI_J']==pytest.approx(ode.y[1,-1],rel=1e-10)
    assert result['resistor_I2R_J']==pytest.approx(ode.y[2,-1],rel=1e-10)
    assert abs(result['energy_residual_J'])<1e-12
    near_lossless=pulse.rl_pulse(1e-6,.01,5.,.001)
    assert near_lossless['final_current_A']==pytest.approx(.5,rel=1e-7)


@pytest.mark.parametrize('R',[.2,2.,8.])
def test_rlc_all_damping_regimes_against_independent_ode(R):
    L,C,V,T=.01,.01,24.,.02
    result=pulse.rlc_pulse(R,L,C,V,T)
    ode=solve_ivp(lambda t,y:[(y[1]-R*y[0])/L,-y[0]/C,R*y[0]**2,y[1]*y[0]],
                  (0,T),[0.,V,0.,0.],rtol=1e-11,atol=1e-12,method='DOP853')
    assert result['final_current_A']==pytest.approx(ode.y[0,-1],rel=1e-9)
    assert result['final_capacitor_voltage_V']==pytest.approx(ode.y[1,-1],rel=1e-9)
    assert result['resistor_I2R_J']==pytest.approx(ode.y[2,-1],rel=1e-9)
    assert result['capacitor_VI_delivered_J']==pytest.approx(ode.y[3,-1],rel=1e-9)
    assert abs(result['energy_residual_J'])<1e-8
    assert result['turnoff_clamp_qualified'] is False


def test_reverse_ringing_is_not_a_free_retained_programming_state():
    value=pulse.rlc_pulse(.1,.001,.001,48.,.004)
    assert value['capacitor_reversal_present']
    assert value['minimum_capacitor_voltage_V']<0
    assert value['switching_qualified'] is False
    assert value['hysteresis_and_eddy_energy_J'] is None


@pytest.mark.parametrize('bad',[0.,-1.,float('nan'),float('inf'),True])
def test_bad_and_out_of_domain_inputs_are_refused(bad):
    with pytest.raises(ValueError):pulse.rl_pulse(bad,.01,12.,.02)
    with pytest.raises(ValueError):pulse.rlc_pulse(1.,.01,bad,12.,.02)
    with pytest.raises(ValueError):pulse.rl_pulse(1.,.01,12.,2.)
    with pytest.raises(ValueError):pulse.rlc_pulse(1e-6,1e-8,1e-9,12.,1.)


def test_coupled_gap_loadline_and_bidirectional_mmf_identity():
    args=dict(gaps_m=[.012,.012],magnet_length_m=.05,pole_area_m2=.0012,
              nd_area_m2=.0008,alnico_area_m2=.0008)
    row=pulse.coupled_loadline(B_gap_T=.8,**args)
    assert row['common_H_A_per_m']==pytest.approx(-305577.490736439,rel=1e-10)
    assert row['retention_screen']=='fail-necessary-positive-state'
    assert row['actual_force_N'] is None and not row['remanent_state_known']
    contact=pulse.coupled_loadline(B_gap_T=.8,**dict(args,gaps_m=[.0002,.0002]))
    assert contact['retention_screen']=='unknown'  # belowHc never proves retention
    positive=pulse.energized_parallel_circuit(H_m_A_per_m=240000.,B_alnico_T=1.5,turns=380,**args)
    negative=pulse.energized_parallel_circuit(H_m_A_per_m=-240000.,B_alnico_T=-1.5,turns=380,**args)
    assert positive['required_NI_At']==pytest.approx(positive['magnet_MMF_At']+positive['gap_MMF_At'])
    assert abs(positive['required_current_A'])>abs(negative['required_current_A'])
    assert positive['required_current_A']>240000*.05/380
    Bnd=positive['nd_branch_B_T']
    assert args['pole_area_m2']*positive['prescribed_circuit_B_gap_T']==pytest.approx(args['nd_area_m2']*Bnd+args['alnico_area_m2']*1.5)
    bound=pulse.positive_branch_retention_bound(gaps_m=[.012,.012],magnet_length_m=.05,
        pole_area_m2=.0048,nd_area_m2=.0008)
    assert bound['status']=='fail-within-declared-no-leakage-circuit'
    assert bound['minimum_gap_B_from_positive_branches_T']>bound['maximum_gap_B_before_normal_Hc_T']
    assert bound['minimum_magnet_length_m']==pytest.approx(.06882,rel=.002)
    assert bound['actual_retention_qualified'] is False


def test_exact_stock_mass_turns_geometry_and_passive_rail():
    values=catalogue.candidates()
    assert len(values)==3 and len({v['candidate_id'] for v in values})==3
    assert {v['parent_magnet_id'] for v in values}=={'ff677ea60334a09828e70df8e89f8a9a8726e38da171cfc0f73c5f60221d2c0e'}
    for value in values:
        catalogue.validate(value)
        parts=value['stock_parts'];train=[p for p in parts if p['group']=='train']
        assert value['mass']['known_module_stock_kg']==pytest.approx(math.fsum(p['volume_m3']*p['density_kg_m3'] for p in train))
        assert value['mass']['installed_car_mass_kg'] is None
        assert all(p['material']=='steel' for p in parts if p['group']=='guideway')
        assert len([p for p in parts if p['role']=='EPM-pulse-conductor'])==4*value['winding']['turns']
        assert value['winding']['slot_fill']<=.55
        assert value['packing']['longitudinal_margin_m']>0
        assert value['parent_force_result_transferable'] is False
        assert value['magnetic_circuit']['ideal_zero_external_flux_Nd_shunt_B_T']==pytest.approx(1.17)
        assert value['magnetic_circuit']['off_force_N'] is None
        assert all(row['mass_kg'] is None for row in value['unknown_installed_inventory'])
        # Independent finite box intersection, including the parent winding and
        # added endcaps/copper: touching boundaries are not overlapping volumes.
        lo=np.array([p['at_m'] for p in train]);hi=lo+np.array([p['size_m'] for p in train])
        for start in range(0,len(train),128):
            overlap=np.all(np.minimum(hi[start:start+128,None,:],hi[None,:,:])-np.maximum(lo[start:start+128,None,:],lo[None,:,:])>1e-10,axis=2)
            for j in range(len(overlap)):overlap[j,start+j]=False
            assert not overlap.any()


def test_rehashed_geometry_material_or_mass_cannot_be_silently_ignored():
    value=catalogue.candidates()[0]
    for mutate in (lambda v:v['stock_parts'][0]['size_m'].__setitem__(0,.1),
                   lambda v:v['materials']['AlNiCo'].__setitem__('Br_T',2.),
                   lambda v:v['mass'].__setitem__('known_module_stock_kg',0.)):
        changed=deepcopy(value);mutate(changed)
        changed.pop('bundle_sha256');changed['bundle_sha256']=catalogue.identity(changed)
        with pytest.raises(ValueError,match='unsupported or modified'):catalogue.validate(changed)
    with pytest.raises(ValueError,match='no identified AlNiCo'):catalogue.field_geometry(value)


def test_study_optimisation_energy_identity_unknowns_and_recharge():
    result=study.study()
    assert result['counts']['architectures']==3
    assert result['counts']['pulse_cases']==18 and result['counts']['spatial_field_solves']==0
    assert result['counts']['electrical_bank_proposals']==27
    assert result['counts']['optimisation_RLC_evaluations']==162
    assert result['counts']['physical_survivors']==0
    assert result['retired_thin_bridge_counterexample']['ideal_zero_external_flux_bridge_B_T']==pytest.approx(4.68)
    assert len(result['electrical_optimisation']['selected_proposal_ids'])==3
    for row in result['pulse_cases']:
        assert abs(row['linear_RLC']['energy_residual_J'])<1e-7
        assert row['switching_screen']=='unknown' and row['core_eddy_hysteresis_J'] is None
        assert row['result_sha256']==catalogue.identity({k:v for k,v in row.items() if k!='result_sha256'})
    for summary in result['summary'][:2]:
        assert summary['conditional_pulse_budget_passes']==6
        timing=summary['timing']
        assert timing['two_polarity_reference_car_capacitor_reset_J']==pytest.approx(2*timing['one_polarity_reference_car_capacitor_reset_J'])
        assert timing['post_turnoff_clamp_recovery_heat_J'] is None
        assert timing['serial_program_plus_reset_s_assuming_no_overlap']>timing['minimum_program_slots_s']
    assert result['summary'][1]['capacitor_energy_per_car_J']==24*result['summary'][0]['capacitor_energy_per_car_J']


def test_immutable_packet_reconstruction_and_coherent_tamper_refusal(tmp_path):
    path=tmp_path/'packet';manifest=publication.run(path)
    assert publication.verify(path)['verified']
    assert manifest['source_sha256'] and manifest['physical_accepted'] is False
    with pytest.raises(ValueError,match='fresh/empty'):publication.run(path)
    data=json.loads((path/'pulse-cases.json').read_bytes());data[0]['linear_RLC']['peak_current_A']+=1
    raw=catalogue.encoded(data);(path/'pulse-cases.json').write_bytes(raw)
    manifest['files_sha256']['pulse-cases.json']=sha256(raw).hexdigest()
    manifest.pop('manifest_id');manifest['manifest_id']=catalogue.identity(manifest)
    (path/'manifest.json').write_bytes(catalogue.encoded(manifest))
    with pytest.raises(ValueError,match='retained/fresh'):publication.verify(path)


def test_source_drift_and_false_acceptance_cannot_reseal_packet(tmp_path,monkeypatch):
    path=tmp_path/'packet';manifest=publication.run(path)
    changed=deepcopy(manifest);changed['physical_accepted']=True;changed.pop('manifest_id');changed['manifest_id']=catalogue.identity(changed)
    (path/'manifest.json').write_bytes(catalogue.encoded(changed))
    with pytest.raises(ValueError,match='cannot assert'):publication.verify(path)
    original=publication.sources;counter=[0]
    def changing(root):
        value=original(root);counter[0]+=1
        if counter[0]>1:value['code_sha256']['changed.py']='f'*64
        return value
    monkeypatch.setattr(publication,'sources',changing)
    with pytest.raises(ValueError,match='source changed'):publication.run(tmp_path/'drifted')
    assert not (tmp_path/'drifted').exists()
