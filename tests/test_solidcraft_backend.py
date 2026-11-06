"""Recorded-command, units and identity boundaries, independent of native tools."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import math
import pytest

P = Path(__file__).resolve().parents[1]/'engineering/design_search/craft_backends/solidcraft.py'
spec = spec_from_file_location('osr_craft_solidcraft', P)
s = module_from_spec(spec)
spec.loader.exec_module(s)


def case(entities):
    return dict(case_id='asymmetric', candidate_id='a'*64, component_geometry_id='b'*64, entities=entities)


def box(name='source/asymmetric'):
    return dict(id=name, shape='box', at_m=[2.1, -3.2, .7], size_m=[.17, .043, .009], render_offset_m=[10, 0, 0], material='aluminium')


def test_asymmetric_si_box_keeps_installed_pose_and_identity():
    value=case([box()]);before=deepcopy(value);commands=s.script_for(value)['commands']
    native=next(c['params'] for c in commands if c['command']=='solid.box')
    assert native==dict(length=170.,width=43.,height=9.,corner=[2100.,-3200.,700.],operation='new',body_name='source/asymmetric')
    assert commands[0]==dict(command='document.units',params={'units':'mm'})
    metadata=commands[1]['params']['values']['org.opensourcerail.candidate']
    assert metadata['candidate_id']=='a'*64 and metadata['component_geometry_id']=='b'*64
    assert metadata['display_offsets_applied'] is False and value==before
    assert commands[-1]['command']=='inspect.measure'


def test_normalized_case_entity_keeps_geometry_and_original_source():
    original=box();normalized=dict(id=original['id'],shape='box',geometry={k:original[k] for k in ('at_m','size_m')},source_entity=original,material='aluminium')
    assert s.script_for(case([normalized]))==s.script_for(case([original]))


def test_individual_touching_stock_is_never_implicitly_fused():
    a=box('a');b=box('b');b['at_m']=[2.27,-3.2,.7]
    commands=s.script_for(case([b,a]))['commands']
    parts=[c['params'] for c in commands if c['command']=='solid.box']
    assert [p['body_name'] for p in parts]==['a','b']
    assert all(p['operation']=='new' for p in parts)
    assert not any(c['command']=='solid.combine' for c in commands)


def test_cylinder_rotates_about_source_base_without_display_offset():
    e=dict(id='wheel',shape='cylinder',at_m=[.111,.222,.333],axis=[1,0,0],radius_m=.02,length_m=.123)
    p=next(c['params'] for c in s.script_for(case([e]))['commands'] if c['command']=='solid.cylinder')
    assert p['base']==[111.,222.,333.] and p['axis']==[1.,0.,0.]
    assert p['radius']==20 and p['height']==123 and p['operation']=='new'


def test_tube_subtracts_only_its_own_bore_with_original_body_name():
    e=dict(id='tube',shape='tube',at_m=[.4,.5,.6],axis=[0,-1,0],radius_m=.04,inner_radius_m=.03,length_m=.08)
    rows=[c['params'] for c in s.script_for(case([e]))['commands'] if c['command']=='solid.cylinder']
    assert rows[0]['body_name']=='tube' and rows[0]['operation']=='new'
    assert rows[1]['targets']==['tube'] and rows[1]['operation']=='cut'
    assert rows[1]['axis']==[0.,-1.,0.] and rows[1]['base']==[400.,500.,600.]


def test_explicit_density_is_converted_and_assigned_without_strength_invention():
    v=case([box()]);v['materials']={'aluminium':{'density_kg_m3':2700.}}
    commands=s.script_for(v)['commands'];create=next(c for c in commands if c['command']=='material.create')
    assert create['params']==dict(name='OSR aluminium',density_g_cm3=2.7)
    assert next(c for c in commands if c['command']=='material.assign')['params']['bodies']==['source/asymmetric']
    assert 'physical_card' not in str(commands)


def test_unknown_density_is_not_turned_into_a_zero_or_default_mass():
    commands=s.script_for(case([box()]))['commands']
    assert not any(c['command'].startswith('material.') for c in commands)


@pytest.mark.parametrize('attack',['nan','axis','tube','pipe','duplicate','promotion','identity','hole'])
def test_invalid_or_unsupported_inputs_are_refused_before_native_execution(attack):
    e=box();v=case([e])
    if attack=='nan':e['size_m'][0]=math.nan
    if attack=='axis':e.update(shape='cylinder',axis=[2,0,0],radius_m=.1,length_m=.2)
    if attack=='tube':e.update(shape='tube',axis=[0,0,1],radius_m=.1,inner_radius_m=.1,length_m=.2)
    if attack=='pipe':e['shape']='pipe'
    if attack=='duplicate':v['entities'].append(deepcopy(e))
    if attack=='promotion':v['physical_accepted']=True
    if attack=='identity':v['candidate_id']='unknown'
    if attack=='hole':e['holes']=[dict(diameter_m=.01,x_m=0,y_m=.02)]
    with pytest.raises(ValueError):s.script_for(v)


def measured():
    return dict(bodies=[dict(name='source/asymmetric',closed=True,volume_mm3=65790.,area_mm2=18454.,
                center_of_mass=[2185.,-3178.5,704.5],bbox=dict(min=[2100,-3200,700],max=[2270,-3157,709]),mass_g=84.8691,material='Default')],
                body_count=1,total=dict(volume_mm3=65790.,open_bodies_skipped=0,mass_g=84.8691))


def test_native_units_are_explicit_and_default_cad_mass_is_ignored():
    v=s.parse_measurements([dict(created_bodies=['source/asymmetric']),measured()]);b=v['bodies'][0]
    assert b['volume_m3']==pytest.approx(.17*.043*.009)
    assert b['center_of_mass_m']==pytest.approx([2.185,-3.1785,.7045])
    assert b['bbox_m']['min']==pytest.approx([2.1,-3.2,.7])
    assert b['mass_kg'] is None and b['provider_mass_ignored']
    assert 'tessellation' in v['measurement_fidelity'] and not v['physical_accepted']


def test_open_surface_unknown_volume_does_not_become_zero():
    v=measured();v['bodies'][0].update(closed=False,volume_mm3=None,center_of_mass=None);v['total']={'open_bodies_skipped':1,'volume_mm3':0}
    r=s.parse_measurements(v);assert r['bodies'][0]['volume_m3'] is None and r['total_volume_m3'] is None


def test_profile_uses_source_yz_plane_normal_along_x():
    e=dict(id='section',shape='profile',at_m=[1,2,3],points_yz_m=[[0,0],[.1,0],[0,.2]],length_m=.3)
    c=s.script_for(case([e]))['commands'];sketch=next(x['params'] for x in c if x['command']=='sketch.create')
    assert sketch['plane']==dict(origin=[1000.,2000.,3000.],x_dir=[0,1,0],y_dir=[0,0,1])
    assert next(x['params'] for x in c if x['command']=='solid.extrude')['distance']==300.
