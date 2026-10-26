from pathlib import Path
from copy import deepcopy
import os
import pytest
from engineering.design_search import structural_families as s
from engineering.station_rail import vehicle
ROOT=Path(os.environ.get('OSR_EVIDENCE_ROOT',str(vehicle.ROOT)))

@pytest.fixture(scope='module')
def base():return vehicle.build(ROOT)

def test_primary_catalogue_has_units_axes_minima_and_unknown_prices():
    c=s.material_catalogue();a=c['cores']['al_5052_criii_31'];p=c['cores']['pet_t92_80'];v=c['cores']['pvc_h80']
    assert a['density_kg_m3']==pytest.approx(3.1*16.01846337396)
    assert a['shear_modulus_LT_Pa']==pytest.approx(45000*6894.757293168)
    assert a['shear_modulus_LT_Pa']>a['shear_modulus_WT_Pa']
    assert p['density_kg_m3']==85. and p['compression_modulus_T_Pa']==75e6
    assert v['continuous_temperature_claim_C']==70. and v['heat_distortion_temperature_C']==125.
    assert all(m['price_USD_per_kg'] is None and m['rail_fire_acceptance']=='unknown' for m in c['cores'].values())
    assert all(len(src['sha256'])==64 and src['url'].startswith('https://') for src in c['sources'].values())

def test_stock_generator_preserves_apertures_counts_local_parts_and_never_adopts(base):
    for p in s.initial_parameters():
        c=s.generate(base,p);parts=c['replacement_stock']
        assert len(c['panels'])==80 and all(q['aperture_preserved'] for q in c['panels'])
        assert sum(q['mass_kg'] for q in parts)==pytest.approx(c['counted_new_material_kg'])
        assert len({q['id'] for q in parts})==len(parts)
        assert any(q['frame_id'].startswith('hardpoint-stock') for q in parts)
        assert c['installed_tare_kg_per_car'] is None and not c['full_body_ranking_eligible'] and not c['physical_accepted']

def test_core_cell_orientation_is_physical_and_swaps_directional_shear(base):
    p=s.default_parameters();p['core_id']='al_5052_criii_31';a=s.generate(base,p)
    q={**p,'cell_L_axis':'transverse'};b=s.generate(base,q)
    assert a['candidate_id']!=b['candidate_id']
    assert s.panel_bound(p['core_id'],direction='W')['shear_deflection_m']>s.panel_bound(p['core_id'],direction='L')['shear_deflection_m']
    assert s.necessary_bounds(a)['candidate_id']==a['candidate_id']
    assert not s.necessary_bounds(a)['dispatch_native_full_body']

def test_current_two_point_joint_has_a_missing_rotation():
    two=s.rigid_pad_rank([[-.02,0,0],[.02,0,0]])
    four=s.rigid_pad_rank([[-.02,0,-.02],[.02,0,-.02],[-.02,0,.02],[.02,0,.02]])
    assert two['rank']==5 and two['unconstrained_dofs']==1
    assert four['rank']==6

def test_temperature_and_unknown_hot_properties_are_not_erased(base):
    p=s.default_parameters();p['core_id']='pvc_h80';r=s.necessary_bounds(s.generate(base,p),maximum_core_temperature_C=80.)
    assert r['necessary_screens']['supplier_continuous_temperature']=='fail'
    assert r['necessary_screens']['hot_mechanical_properties']=='unknown'
    assert r['price_USD_per_kg'] is None

def test_coupon_inputs_are_full_integration_dense_and_independently_defined():
    for name,n in [('shear_L',2),('shear_W',2),('bending',20),('bending',40)]:
        raw,d=s.coupon_deck(name,n);nodes,elements,eq,bc=s._read_deck(raw)
        assert len(elements)==d['solid_elements'] and max(e[0] for e in elements)==len(elements)
        assert '*ELEMENT,TYPE=C3D20,' in raw and 'TYPE=C3D20R' not in raw
        assert not eq
    a=s.coupon_deck('shear_L',2)[1]['analytical']['expected_top_shear_force_N']
    b=s.coupon_deck('shear_W',2)[1]['analytical']['expected_top_shear_force_N']
    assert a/b==pytest.approx(45/22)


def test_model_diagnosis_locates_native_node_and_does_not_confuse_graph_with_stability(tmp_path):
    raw,d=s.coupon_deck('bending',20);nodes=d['nodes'];tip=max(nodes,key=lambda n:nodes[n][0])
    (tmp_path/'body.inp').write_text(raw)
    (tmp_path/'body.dat').write_text(f'displacements\n1 0 0 0\n{tip} 0 .254 0\nforces\n')
    q=dict(id='diagnostic-panel',kind='box',at_m=[0,0,-.001],size_m=[1,.1,.1])
    import json
    (tmp_path/'candidate.json').write_text(json.dumps(dict(candidate_id='test-only',geometry_parts=[q],wheel_body=dict(pads=[dict(post_id='post',end=0,bolt_axes=[[-.02,0],[.02,0]])]))))
    r=s.diagnose_native(tmp_path)
    assert r['maxima']['lateral']['node_id']==tip
    assert r['maxima']['lateral']['source_stock_envelope_matches']==['diagnostic-panel']
    assert r['graph']['physical_components']==1 and r['ideal_pad_rank_histogram']=={'5':1}
    assert not r['causal_diagnosis_complete'] and not r['full_body_ranking_eligible']

def test_concept_leads_do_not_invent_corrugated_properties_or_native_support():
    leads=s.concept_leads()
    assert len(leads)==2
    assert all(v['core_moduli_Pa'] is None and not v['native_adapter_available'] for v in leads)
    assert all(v['url'].startswith('https://') and len(v['archived_html_sha256'])==64 for v in leads)


def test_unsupported_layup_generates_a_model_job_without_inheriting_balanced_stiffness(base):
    p=s.default_parameters();p['face_ply_angles_deg']=[0,45]
    c=s.generate(base,p);r=s.necessary_bounds(c)
    assert r['panel_estimate'] is None
    assert any('ABD' in job for job in r['next_jobs'])
    assert not r['dispatch_native_full_body']
    a=s.necessary_bounds(c,maximum_core_temperature_C=23.)
    assert r['candidate_id']==a['candidate_id'] and r['evaluation_id']!=a['evaluation_id']


def test_shear_prescribed_values_fit_calculix_numeric_fields_and_retain_affine_field():
    for kind in ('shear_L','shear_W'):
        raw,d=s.coupon_deck(kind,2);nodes,_,_,boundary=s._read_deck(raw)
        specified=[row for row in boundary if row[1:3]==['1','1']]
        assert specified
        for row in specified:
            # CalculiX accepts at most20 characters per numeric data field.
            assert all(len(field)<=20 for field in row)
            assert float(row[3])==pytest.approx(d['analytical']['imposed_gamma']*nodes[int(row[0])][2],abs=1e-18)
