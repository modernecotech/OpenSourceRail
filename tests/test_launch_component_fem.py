from copy import deepcopy
from math import pi,sqrt
from pathlib import Path
import json
import pytest
from engineering.design_search.craft_backends import launch_component_fem as f


@pytest.fixture
def spec():
    return dict(candidate_id='a'*64,component_geometry_id='b'*64,units='m-kg-s-N-Pa',
        length_m=.16,height_m=.12,thickness_m=.025,bore_diameter_m=.04,bore_x_m=.12,bore_z_m=.06,
        y_base_m=-.055,force_per_ear_N=80000.,pin_force_N=160000.,young_Pa=210e9,poisson=.3,density_kg_m3=7850.)


def test_actual_component_nominal_stresses_are_not_one_metre_controls(spec):
    r=f.analytical(spec)
    assert r['net_section_nominal_Pa']==pytest.approx(40e6)
    assert r['bearing_nominal_Pa']==pytest.approx(80e6)
    assert r['forward_edge_shear_nominal_Pa']==pytest.approx(80e6)
    assert r['pin_double_shear_nominal_Pa']==pytest.approx(160000/(2*pi*.04**2/4))
    assert r['single_ear_material_mass_kg']==pytest.approx((.16*.12*.025-pi*.02**2*.025)*7850)
    assert not r['material_strength_qualified'] and not r['physical_accepted']


@pytest.mark.parametrize('level,elements',[('coarse',256),('fine',1024)])
def test_mesh_follows_rectangle_and_bore_with_distributed_bearing_equilibrium(spec,level,elements):
    original=deepcopy(spec);m=f.mesh(spec,level)
    assert spec==original and len(m['elements'])==elements
    assert all(len(e)==20 and len(set(e))==20 for e in m['elements'].values())
    assert m['applied_N']==pytest.approx([80000,0,0],abs=1e-8)
    assert len(m['nodal_load_N'])>50
    for n in m['bore_nodes']:
        x,y,z=m['nodes'][str(n)]
        assert sqrt((x-.12)**2+(z-.06)**2)==pytest.approx(.02,abs=1e-12)
        assert -.055-1e-12<=y<=-.03+1e-12
    assert all(abs(m['nodes'][str(n)][0])<1e-10 for n in m['root_nodes'])
    assert len(m['probe_nodes'])==16
    assert all(m['nodes'][str(n)]==pytest.approx(p) for n,p in zip(m['probe_nodes'],m['probe_xyz_m']))


def test_coarse_fine_compare_identical_physical_interfaces_and_different_meshes(spec):
    a,b=f.mesh(spec,'coarse'),f.mesh(spec,'fine')
    assert a['candidate_id']==b['candidate_id'] and a['component_geometry_id']==b['component_geometry_id']
    assert a['mesh_id']!=b['mesh_id'] and a['probe_xyz_m']==b['probe_xyz_m']
    assert len(b['nodes'])>len(a['nodes'])


@pytest.mark.parametrize('change',[dict(units='mm'),dict(force_per_ear_N=160000),dict(bore_x_m=.15),dict(poisson=.5),dict(physical_accepted=True),dict(candidate_id='invalid')])
def test_invalid_units_geometry_load_split_and_acceptance_refused(spec,change):
    spec.update(change)
    with pytest.raises(ValueError):f.mesh(spec)


def test_native_admission_refuses_unbound_geometry(spec,tmp_path):
    with pytest.raises(ValueError,match='authenticated CAD'):f.run(spec,tmp_path/'run')


def test_component_deck_uses_full_solid_elements_distributed_loads_and_readonly_source(spec):
    m=f.mesh(spec);text=f.deck(spec,m)
    assert '*ELEMENT,TYPE=C3D20' in text and '*CLOAD' in text and '*EL PRINT' in text
    assert 'ROOT,1,3' in text and 'T3D2' not in text
    commands=f.commands(spec,m)
    assert commands[0]['params']['system']=='m-kg-s-N-Pa'
    assert sum(c['command']=='model.load.create' for c in commands)==len(m['nodal_load_N'])
    assert all('set' in c['params']['target'] and 'nodes' not in c['params']['target'] for c in commands if c['command']=='model.load.create')


def assembly_fixture(spec):
    parts=[dict(id='clevis/ear/'+str(i),shape='box',size_m=[.16,.025,.12],at_m=[.1,y,.24],
        holes=[dict(axis='y',diameter_m=.04,x_m=.12,z_m=.06)]) for i,y in enumerate((-.055,.03))]
    physical=dict(parts=deepcopy(parts));candidate=f.identity(physical)
    component=dict(parts=parts,component_frame=dict(rotation_matrix=[[1,0,0],[0,1,0],[0,0,1]],translation_to_station_m=[.1,0,.24]))
    cid=f.identity(component)
    interface=dict(candidate_id=candidate,component_geometry_id=cid,force_direction=[1,0,0],force_per_ear_N=80000.,total_force_N=160000.,
        units=dict(force='N',length='m',stress='Pa'),
        dimensions=dict(ear_length_m=.16,ear_height_m=.12,ear_thickness_m=.025,bore_diameter_m=.04,bore_center_local_xz_m=[.12,.06],
            ear_local_y_m=[-.055,.03],ear_parent_translation_m=[.1,0,.24],pin_diameter_m=.04,clear_gap_m=.06),
        material_hypothesis=dict(young_Pa=210e9,poisson=.3,density_kg_m3=7850.,nominal_yield_Pa=355e6),**f.FLAGS)
    a=dict(physical_definition=physical,candidate_id=candidate,component_geometry=component,component_geometry_id=cid,
        fem_interface=interface,**f.FLAGS)
    a['assembly_definition_id']=f.identity(a)
    return a


def test_assembly_ids_units_and_actual_holes_are_preserved_readonly(spec):
    a=assembly_fixture(spec);original=deepcopy(a);s=f.from_assembly(a)
    assert a==original and s['candidate_id']==a['candidate_id'] and s['component_geometry_id']==a['component_geometry_id']
    assert s['installed_translation_m']==[.1,0,.24] and s['force_per_ear_N']==80000
    assert f.analytical(s)['bearing_nominal_Pa']==80e6


@pytest.mark.parametrize('attack',['mixed-candidate','mixed-component','dimensions','rotation','material','release'])
def test_resealed_inconsistent_cad_fem_contract_is_refused(spec,attack):
    a=assembly_fixture(spec)
    if attack=='mixed-candidate':a['fem_interface']['candidate_id']='c'*64
    if attack=='mixed-component':a['fem_interface']['component_geometry_id']='d'*64
    if attack=='dimensions':a['fem_interface']['dimensions']['bore_diameter_m']=.05
    if attack=='rotation':a['component_geometry']['component_frame']['rotation_matrix']=[[0,1,0],[1,0,0],[0,0,1]]
    if attack=='material':a['fem_interface']['material_hypothesis']['young_Pa']=0
    if attack=='release':a['fem_interface']['engineering_accepted']=True
    a['assembly_definition_id']=f.identity({k:v for k,v in a.items() if k!='assembly_definition_id'})
    with pytest.raises(ValueError):f.from_assembly(a)


def test_changed_load_is_evaluation_change_not_new_physical_geometry(spec):
    a=assembly_fixture(spec);b=deepcopy(a)
    b['fem_interface'].update(force_per_ear_N=40000,total_force_N=80000)
    b['assembly_definition_id']=f.identity({k:v for k,v in b.items() if k!='assembly_definition_id'})
    x,y=f.from_assembly(a),f.from_assembly(b)
    assert x['candidate_id']==y['candidate_id'] and x['component_geometry_id']==y['component_geometry_id']
    assert f.identity(x)!=f.identity(y) and f.mesh(x)['mesh_id']!=f.mesh(y)['mesh_id']


def test_pin_bending_is_not_hidden_by_double_shear_screen(spec):
    spec.update(pin_diameter_m=.04,ear_center_span_m=.085,central_eye_contact_width_bound_m=[0.,.06])
    r=f.analytical(spec);pin=r['pin_bending']
    assert pin['maximum_moment_bound_Nm']==pytest.approx([2200,3400])
    assert pin['outer_fibre_bending_nominal_bound_Pa']==pytest.approx([32*2200/(pi*.04**3),32*3400/(pi*.04**3)])
    assert max(pin['outer_fibre_bending_nominal_bound_Pa'])>500e6
    assert r['pin_double_shear_nominal_Pa']<65e6 and not pin['strength_qualification']


def test_resealed_component_not_in_physical_assembly_is_refused(spec):
    a=assembly_fixture(spec);a['physical_definition']['parts'][0]['at_m'][0]=.2
    a['candidate_id']=f.identity(a['physical_definition']);a['fem_interface']['candidate_id']=a['candidate_id']
    a['assembly_definition_id']=f.identity({k:v for k,v in a.items() if k!='assembly_definition_id'})
    with pytest.raises(ValueError,match='same physical assembly'):f.from_assembly(a)


def held_evidence(folder,assembly):
    s=f.from_assembly(assembly);folder.mkdir()
    f.native.write(folder/'input.json',s)
    (folder/'evaluator-source.py').write_bytes(Path(f.__file__).read_bytes())
    request=dict(candidate_id=s['candidate_id'],component_geometry_id=s['component_geometry_id'],
        input_sha256=f.identity(s),source_sha256=f.sources())
    request['evaluation_id']=f.identity(request);f.native.write(folder/'request.json',request)
    result=dict(candidate_id=s['candidate_id'],component_geometry_id=s['component_geometry_id'],evaluation_id=request['evaluation_id'],
        levels={n:dict(state='held',reason='No native evidence') for n in ('coarse','fine')},refinement=None,analytical=f.analytical(s),
        artifact_sha256={p.name:f.native.digest(p) for p in folder.iterdir() if p.is_file()},**f.FLAGS)
    result['result_id']=f.identity(result);f.native.write(folder/'result.json',result)
    return result


def test_integrity_of_a_hold_does_not_establish_physical_or_numerical_acceptance(spec,tmp_path):
    a=assembly_fixture(spec);out=tmp_path/'held';held_evidence(out,a)
    verified=f.verify(out,a)
    assert verified['integrity_verified'] and verified['fresh_native_solve'] is False
    assert all(verified[k] is False for k in f.FLAGS)


@pytest.mark.parametrize('attack',['candidate','component','evaluation','release','source','artifact'])
def test_resealed_false_candidate_release_or_changed_native_evidence_is_refused(spec,tmp_path,attack):
    a=assembly_fixture(spec);out=tmp_path/'held';r=held_evidence(out,a)
    if attack=='candidate':r['candidate_id']='c'*64
    if attack=='component':r['component_geometry_id']='d'*64
    if attack=='evaluation':r['evaluation_id']='e'*64
    if attack=='release':r['physical_accepted']=True
    if attack=='source':(out/'evaluator-source.py').write_text('changed evaluator')
    if attack=='artifact':(out/'unexpected.log').write_text('unbound execution')
    r['result_id']=f.identity({k:v for k,v in r.items() if k!='result_id'})
    (out/'result.json').write_text(json.dumps(r))
    with pytest.raises(ValueError):f.verify(out,a)
