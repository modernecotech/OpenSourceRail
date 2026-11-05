"""Independent arithmetic and identity controls for explicit station layouts."""
from copy import deepcopy
from pathlib import Path

import pytest

from engineering.station_rail import station_motor as motor,propulsion_layout as p
from engineering.station_rail.common import digest,identity


def args(length=203.,**changes):
    value=dict(candidate_id='a'*64,body_candidate_id='b'*64,passive_interface_id='c'*64,
        sections=[dict(section_id='departure',start_m=0.,length_m=length,role='launch')],
        module_length_m=12.5,module_policy='whole-modules',directions=2,
        independent_branches_per_direction=2,magnetic_period_m=.5,faces_per_track=2)
    value.update(changes);return value


def test_finite_unit_has_no_selected_deployment_and_intentionally_new_identity():
    d=motor.definition()
    wire=40*(2*(.16+.25)+.05);copper=wire*25e-6*8960*(2*3/.5)
    steel=2*(.025+.055*(1-.04/(.5/6)))*.16*7850
    assert d['schema']=='osr-station-LIM-primary-definition/2'
    assert d['deployment_length_m'] is None and d['native_evidence_admitted'] is False
    assert 'bare_900m_stock_kg_per_direction' not in d
    assert 'bare_12_5m_module_stock_kg_both_sides' not in d
    assert d['copper_kg_per_m']==copper and d['primary_steel_kg_per_m']==steel
    assert d['motor_component_id']!= '82edcd61383e44ccbc5dfd327eefcad769fa245ba8653b56aab502c956e9b293'
    assert d['motor_component_id']==identity({k:v for k,v in d.items() if k!='motor_component_id'})


def test_203m_counts_seventeen_whole_modules_and_both_faces_once():
    x=p.layout(**args());q=p.quantities(x)
    assert x['per_direction']['full_modules']==17
    assert x['per_direction']['installed_length_m']==212.5
    assert x['per_direction']['excess_stock_length_m']==9.5
    assert x['totals']['installed_length_m']==425
    assert x['totals']['stator_face_module_joints']==2*16*2
    assert x['totals']['independently_terminated_bank_ends']==4
    assert q['stock']['copper_kg']==pytest.approx(425*93.5424)
    assert q['stock']['steel_kg']==pytest.approx(425*134.6432)
    assert q['stock']['bare_primary_stock_kg']==pytest.approx(425*228.1856)
    assert q['installed_total_mass_kg'] is None and q['faces_already_counted']==2
    assert all(r['installed_mass_kg'] is None and r['cost'] is None and r['required'] for r in q['additional_installation_accounts'])
    assert all(q[k] is False for k in p.FLAGS)
    assert q['actual_available_force_N'] is None and q['current_to_thrust_map_id'] is None
    assert q['thermal_equilibrium_C'] is None and q['stock_scaling_is_force_evidence'] is False


def test_explicit_tail_policy_counts_piece_period_rounding_and_excess():
    x=p.layout(**args(module_policy='whole-period-tail'))
    row=x['sections'][0]
    assert (row['full_modules'],row['tail_modules'],row['tail_length_m'],row['installed_length_m'])==(16,1,3.,203.)
    y=p.layout(**args(203.1,module_policy='whole-period-tail'))
    assert y['sections'][0]['tail_length_m']==3.5
    assert y['per_direction']['installed_length_m']==203.5
    assert y['per_direction']['excess_stock_length_m']==pytest.approx(.4)


def test_same_installed_geometry_different_requirements_keep_physical_identity():
    a=p.layout(**args(203.));b=p.layout(**args(204.))
    assert a['physical_layout_id']==b['physical_layout_id'] and a['layout_id']!=b['layout_id']
    qa,qb=p.quantities(a),p.quantities(b)
    assert qa['installed_primary_candidate_id']==qb['installed_primary_candidate_id']
    assert qa['evaluation_id']!=qb['evaluation_id'] and qa['stock']==qb['stock']
    c=p.layout(**args(213.));assert c['physical_layout_id']!=a['physical_layout_id']


def test_section_names_and_duty_roles_are_not_new_physical_geometry():
    aa=args();bb=deepcopy(aa);bb['sections'][0].update(section_id='arrival',role='receiving')
    a,b=p.layout(**aa),p.layout(**bb)
    assert a['physical_layout_id']==b['physical_layout_id'] and a['layout_id']!=b['layout_id']


def test_electrical_branches_are_counted_without_duplicating_primary_stock():
    a=p.layout(**args());b=p.layout(**args(independent_branches_per_direction=3))
    assert b['electrical_resources']['total_independent_branches']==6
    assert b['electrical_resources']['branch_count_duplicates_primary_stock'] is False
    assert b['electrical_resources']['electrical_coil_termination_count'] is None
    assert p.quantities(a)['stock']==p.quantities(b)['stock']
    assert a['physical_layout_id']!=b['physical_layout_id']


def test_separate_banks_count_interfaces_and_ends_and_do_not_merge_their_stock():
    sections=[dict(section_id='arrival',start_m=-200.,length_m=100.,role='receiving'),
              dict(section_id='departure',start_m=0.,length_m=100.,role='launch')]
    x=p.layout(**args(sections=sections));q=p.quantities(x)
    assert x['totals']['full_modules']==32
    assert x['totals']['installed_length_m']==400
    assert x['totals']['independently_terminated_bank_ends']==8
    assert x['totals']['stator_face_module_joints']==56
    assert q['installed_length_m']==400
    assert 'engineering/station_rail/brief.toml' not in x['source_sha256']


def test_nonoverlap_is_checked_after_physical_module_rounding():
    sections=args()['sections']+[dict(section_id='arrival',start_m=205.,length_m=10.,role='receiving')]
    with pytest.raises(ValueError,match='overlap'):p.layout(**args(sections=sections))


def test_resealed_derived_quantities_cannot_override_the_physical_request():
    x=p.layout(**args());x['totals']['installed_length_m']=0.
    x.pop('layout_id');x['layout_id']=identity(x)
    with pytest.raises(ValueError,match='reproduce'):p.quantities(x)
    x=p.layout(**args());x['candidate_id']='d'*64
    with pytest.raises(ValueError,match='Sealed'):p.quantities(x)


def test_mixed_primary_definition_or_period_is_rejected():
    d=motor.definition();d['motor_component_id']='f'*64
    with pytest.raises(ValueError,match='source-bound'):p.quantities(p.layout(**args()),d)
    x=p.layout(**args(module_length_m=12.,magnetic_period_m=1.))
    with pytest.raises(ValueError,match='periods differ'):p.quantities(x)


def test_inputs_are_not_mutated_or_returned_by_reference():
    request=args();before=deepcopy(request);x=p.layout(**request)
    assert request==before
    d=motor.definition();before=deepcopy(d);q=p.quantities(x,d)
    assert d==before
    x['request']['sections'][0]['length_m']=1.
    assert request==args() and q['installed_length_m']==425


@pytest.mark.parametrize('bad',[0.,-1.,True,float('nan'),float('inf')])
def test_invalid_length_has_no_fallback(bad):
    with pytest.raises(ValueError):p.layout(**args(bad))


@pytest.mark.parametrize('name,bad',[
    ('module_length_m',False),('module_length_m',float('inf')),('magnetic_period_m',0.),
    ('module_length_m',12.6),('directions',True),('directions',0),
    ('independent_branches_per_direction',1.5),('independent_branches_per_direction',0),
    ('candidate_id','no-id'),('module_policy','assume-cheapest'),('sections',[]),
])
def test_explicit_invalid_deployment_contract_is_rejected(name,bad):
    with pytest.raises(ValueError):p.layout(**args(**{name:bad}))


def test_missing_explicit_deployment_arguments_raise_instead_of_selecting_a_length():
    with pytest.raises(TypeError):p.layout(candidate_id='a'*64)
    request=args();request['sections'][0]['start_m']=float('nan')
    with pytest.raises(ValueError):p.layout(**request)
    request=args();request['sections']*=2
    with pytest.raises(ValueError,match='Unique'):p.layout(**request)


def test_changed_source_context_invalidates_even_resealed_cached_layout(tmp_path):
    x=p.layout(**args())
    for name in x['source_sha256']:
        target=tmp_path/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((Path(p.ROOT)/name).read_bytes())
    assert p.layout(**args(),root=tmp_path)==x
    (tmp_path/p.PRODUCER).write_bytes((tmp_path/p.PRODUCER).read_bytes()+b'\n')
    with pytest.raises(ValueError,match='producer differs'):p.layout(**args(),root=tmp_path)


@pytest.mark.parametrize('faces',[1,4,6])
def test_other_face_counts_get_exact_geometry_without_inheriting_two_face_stock(faces):
    x=p.layout(**args(faces_per_track=faces))
    assert x['physical_definition']['faces_per_track']==faces
    assert x['totals']['stator_face_module_joints']==faces*16*2
    assert x['physical_layout_id']!=p.layout(**args())['physical_layout_id']
    with pytest.raises(ValueError,match='exactly two'):p.quantities(x)


def test_installed_physical_identity_uses_geometry_not_evaluator_source_identity():
    x=p.layout(**args());d=motor.definition();q=p.quantities(x)
    expected=identity(dict(candidate_id=x['candidate_id'],body_candidate_id=x['body_candidate_id'],
        passive_interface_id=x['passive_interface_id'],physical_layout_id=x['physical_layout_id'],
        repeating_cell_physical_id=d['repeating_cell_physical_id']))
    assert q['installed_primary_candidate_id']==expected
    assert q['primary_unit_definition_id']==d['motor_component_id']
    assert q['repeating_cell_physical_id']==d['repeating_cell_physical_id']
