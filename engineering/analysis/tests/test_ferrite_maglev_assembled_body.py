"""Joined-material native candidate tests; no physical or production acceptance."""
from engineering.ferrite_maglev import assembled_body as a


def test_defined_primary_stock_and_all_release_holds():
    d=a.definition();r=a.study()
    assert d['source_primary_stock_count']==63
    assert d['installed_primary_member_count']==65
    assert r['complete_equipped_vehicle'] is False
    assert all(r[k] is False for k in a.FLAGS)
    assert r['hardpoint_screen']['analytical_screen_pass']
    assert not r['hardpoint_screen']['rejected_four_bolt_120x80']['screen_pass']

from copy import deepcopy
from hashlib import sha256
import gzip
import json
import math
import shutil
from pathlib import Path

import pytest
from engineering.factory_examples import models


def test_hardpoint_centres_all_have_real_wall_holes_spacers_and_access():
    d=a.definition();ps={p['id']:p for p in d['parts']};h=a.load()['hardpoint']
    assert len(d['interfaces'])==24
    assert sum(p['id'].endswith('/shank') and p['id'].startswith('hardpoint/') for p in ps.values())==len(d['interfaces'])*h['bolts']
    for interface in d['interfaces']:
        assert interface['bolt_count']==h['bolts'] and len(interface['bolt_centres_m'])==h['bolts']
        uid=interface['id'];flange=ps[uid+'/carrier-flange'];patch=ps[uid+'/laminate']
        assert len(flange['holes'])==len(patch['holes'])==h['bolts']
        for k in range(h['bolts']):
            spacer=ps[uid+f'/bolt-{k}/crush-spacer']
            assert spacer['cylinder_axis']=='y' and spacer['size_m'][2]==pytest.approx(.116)
            assert spacer['holes'][0]['length_m']==pytest.approx(.116)
            assert spacer['holes'][0]['diameter_m']==pytest.approx(.013)
    screen=a.hardpoint_screen(d)
    force=26400*9.81*1.3*1.5/23
    assert screen['maximum_interface_force_n']==pytest.approx(force)
    assert screen['tension_per_bolt_n']==pytest.approx(force*(1.2+h['carrier_flange_m']-.88)*1.5/((max(h['rows_z_m'])-min(h['rows_z_m']))*len(h['columns_x_m'])))
    assert screen['socket_clearance_m']==pytest.approx(.001) and screen['minimum_centre_edge_m']>.024
    assert screen['projection_beyond_nut_m']>=2*.00175
    path=a.carrier_load_path_screen();assert path['analytical_screen_pass']
    assert not path['rejected_thin_100x80x6_arm']['screen_pass'] and not path['rejected_12mm_flange']['screen_pass']
    assert screen['spacer_compression_pa']<150e6 and screen['checks']['positive_net_section']
    assert screen['tension_per_bolt_n']<screen['inboard_tube_wall_pullthrough_capacity_n']
    svg=a.sections_svg(d)
    assert f'carrier flange{h["carrier_flange_m"]*1000:g}mm' in svg
    assert f'{h["bolts"]}×M12 bolts' in svg and 'carrier flange12mm' not in svg


def test_tube_material_regions_and_hole_integrals_are_exclusive():
    d=a.definition()
    for p in d['parts']:
        V,c,I=a._primitive_properties(p)
        assert V==pytest.approx(models.volume(p),rel=1e-9)
        assert V>0 and all(math.isfinite(x) for x in c)
        assert all(I[i][i]>0 for i in range(3))
        for i in range(3):
            for j in range(3):assert I[i][j]==pytest.approx(I[j][i])
    for member in d['members']:
        assert len(member['part_ids'])==4
        assert member['size_m'][member['axis']]>0


def test_cut_stock_coverage_and_gangway_are_actual_geometric_changes():
    d=a.definition();source={p['id'] for p in a.closure.primary_frame_definition()['parts']}
    fitted=[m for m in d['members'] if m['source_member_id']]
    assert {m['source_member_id'] for m in fitted}==source
    assert len(fitted)==len(source)+2
    for m in fitted:
        if '-cross-0/segment-' in m['id']:
            lo=m['at_m'][1];hi=lo+m['size_m'][1]
            assert hi<=-.65+1e-10 or lo>=.65-1e-10
    assert all('lower-crosshead' not in p['id'] for p in d['parts'])
    assert any('cantilever-' in p['id'] for p in d['parts'])


def test_structural_axial_compliance_reduces_coupler_only_plant_assumption():
    r=a.axial_screen();area=.14*.22-(.14-.024)*(.22-.024)
    k=2*20e9*area/17
    assert r['gross_body_axial_stiffness_n_m']==pytest.approx(k)
    assert r['body_and_coupler_series_stiffness_n_m']==pytest.approx(1/(1/k+1/100e6))
    assert 0<r['drilled_body_axial_stiffness_n_m']<k
    assert 0<r['drilled_body_and_coupler_series_stiffness_n_m']<r['body_and_coupler_series_stiffness_n_m']<100e6
    assert not r['plant_stiffness_promoted'] and not r['physical_validation']


def test_legacy_control_is_exact_immutable_old_topology_not_current_inference():
    r=a.study()['legacy_negative_control'];old=json.loads(a.LEGACY.read_text())
    assert r['definition_sha256']==old['historical_native_manifest']['files_sha256']['interface/definition.json']
    assert r['historical_native_manifest_sha256']==sha256(a.encoded(old['historical_native_manifest'])).hexdigest()
    assert r['eligible_for_assembled_adoption'] is False
    assert len(r['part_ids'])==2
    assert r['exact_configuration_revision']=='V052-FIXED-LINE-URBAN-SUBURBAN-3'


def test_translated_independent_box_and_annular_cylinder_integrals():
    p=dict(kind='box',size_m=[1.,2.,3.],at_m=[4.,5.,6.])
    V,c,I=a._primitive_properties(p)
    assert V==6 and c==[4.5,6.,7.5]
    assert I[0][0]==pytest.approx(6*(2**2+3**2)/12)
    p=dict(kind='cylinder',cylinder_axis='y',size_m=[.025,.025,.116],at_m=[1.,2.,3.],holes=[dict(axis='y',x_m=.0125,z_m=.0125,diameter_m=.013,length_m=.116)])
    V,c,I=a._primitive_properties(p)
    assert V==pytest.approx(math.pi*(.025**2-.013**2)/4*.116)
    assert c==pytest.approx([1.0125,2.058,3.0125])
    assert I[1][1]==pytest.approx(V*((.025/2)**2+(.013/2)**2)/2)


@pytest.mark.parametrize('field,value',[('material_properties_qualified',True),('complete_equipped_vehicle',True),('adopt_mass_or_stiffness_in_city_defaults',True)])
def test_no_source_flag_can_self_qualify_geometry(tmp_path,monkeypatch,field,value):
    raw=a.INPUT.read_text().replace(field+' = false',field+' = true');path=tmp_path/'input.toml';path.write_text(raw);monkeypatch.setattr(a,'INPUT',path)
    with pytest.raises(ValueError):a.load()


@pytest.fixture(scope='session')
def verified_native_baseline(tmp_path_factory):
    if not (a.OUTPUT/'manifest.json').exists():pytest.skip('Publish actual reopened native assembled packet first')
    # One owned immutable snapshot avoids rechecking the same native geometry
    # before every corruption case; each mutated copy still calls full verify.
    out=tmp_path_factory.mktemp('verified-assembled-body')/'canonical'
    shutil.copytree(a.OUTPUT,out);a.verify(out);return out


@pytest.fixture
def packet(tmp_path,verified_native_baseline):
    out=tmp_path/'assembled';shutil.copytree(verified_native_baseline,out);return out


def reseal(packet,name,value):
    raw=a.encoded(value)
    if name.endswith('.gz'):raw=gzip.compress(raw,mtime=0)
    (packet/name).write_bytes(raw)
    m=json.loads((packet/'manifest.json').read_text());m['files_sha256'][name]=sha256(raw).hexdigest();(packet/'manifest.json').write_bytes(a.encoded(m))


def test_actual_native_packet_geometry_masses_and_control_are_bound(packet):
    m=a.verify(packet);summary=a.read_summary(packet)
    assert m['all_defined_material_pairs_native_checked'] and m['unintended_intersection_count']==0
    assert summary['defined_vehicle_material_mass_kg']>0 and summary['complete_equipped_vehicle'] is False
    legacy=json.loads((packet/'legacy-collision-control.json').read_text())
    assert legacy['expected_failure_observed'] and legacy['total_common_volume_mm3']>0
    assert len(legacy['collisions'])>=4
    assert not legacy['eligible_for_assembled_adoption']


@pytest.mark.parametrize('mutation',['inertia','centroid','density','context','repetition'])
def test_rehashed_mass_receipts_cannot_fake_native_geometry_properties(packet,mutation):
    r=json.loads((packet/'mass-properties.json').read_text())
    p=next(p for p in r['regions'] if p['included_in_defined_vehicle_material_mass'])
    if mutation=='inertia':p['inertia_at_region_centroid_kg_m2'][0][0]*=1.1
    if mutation=='centroid':p['centre_of_volume_m'][0]+=.001
    if mutation=='density':p['density_assumption_kg_m3']*=2
    if mutation=='context':next(p for p in r['regions'] if p['role']=='guideway-context')['mass_kg']=1.
    if mutation=='repetition':r['six_car_repetition']['instanced_inertia_kg_m2'][1][1]*=1.1
    reseal(packet,'mass-properties.json',r)
    with pytest.raises(ValueError):a.verify(packet)


def test_rehashed_native_receipt_cannot_omit_context_from_collision_checks(packet):
    r=json.loads((packet/'native-cad.json').read_text());r['checked_interference_roles'].remove('guideway-context');reseal(packet,'native-cad.json',r)
    with pytest.raises(ValueError,match='all-pair'):a.verify(packet)


def test_legacy_failure_cannot_be_relabelled_accepted_after_rehash(packet):
    r=json.loads((packet/'legacy-collision-control.json').read_text());r['eligible_for_assembled_adoption']=True;reseal(packet,'legacy-collision-control.json',r)
    with pytest.raises(ValueError,match='legacy'):a.verify(packet)


def cube_mesh(offset=(0.,0.,0.)):
    vertices=[[x+offset[0],y+offset[1],z+offset[2]] for z in (0.,1.) for y in (0.,1.) for x in (0.,1.)]
    return dict(vertices_m=vertices,triangles=[[0,2,3],[0,3,1],[4,5,7],[4,7,6],[0,1,5],[0,5,4],[2,6,7],[2,7,3],[0,4,6],[0,6,2],[1,3,7],[1,7,5]])


def test_mesh_oracle_reproduces_translated_box_and_cylinder_control():
    cube=a.mesh_properties(cube_mesh((101.,-50.,20.)))
    assert cube['signed_volume_m3']==pytest.approx(1.) and cube['euler_characteristic']==2
    assert cube['bounds_m']==[101.,-50.,20.,102.,-49.,21.]
    control=a.mesh_control()['control']
    assert control['passed'] and control['relative_circle_volume_error']==pytest.approx(1-16*math.sin(2*math.pi/16)/2/math.pi)
    assert control['signed_mesh_volume_m3']==pytest.approx(control['analytical_polygon_volume_m3'])


@pytest.mark.parametrize('mutation',['missing-face','reversed','orphan','disconnected','bad-index'])
def test_closed_mesh_oracle_rejects_material_representation_corruption(mutation):
    cube=cube_mesh()
    if mutation=='missing-face':cube['triangles'].pop()
    elif mutation=='reversed':cube['triangles']=[t[::-1] for t in cube['triangles']]
    elif mutation=='orphan':cube['vertices_m'].append([5.,5.,5.])
    elif mutation=='disconnected':
        other=cube_mesh((3.,0.,0.));cube['vertices_m']+=other['vertices_m'];cube['triangles']+=[[i+8 for i in t] for t in other['triangles']]
    elif mutation=='bad-index':cube['triangles'][0][0]=True
    with pytest.raises(ValueError):a.mesh_properties(cube)


def test_exact_eight_bolt_failure_is_retained_and_current_sixteen_bolt_screen_is_fresh():
    rejected=json.loads(a.REJECTED.read_text());now=a.study();screen=now['hardpoint_screen']
    assert sha256(a.encoded(rejected['definition'])).hexdigest()==rejected['definition_sha256']
    assert rejected['configuration']['hardpoint']['bolts']==8
    assert rejected['tension_per_bolt_n']>rejected['inboard_wall_pullthrough_capacity_n']
    assert now['rejected_eight_bolt_candidate']['fixture_sha256']==a.digest(a.REJECTED)
    assert screen['bolt_count']==16 and screen['tension_per_bolt_n']<screen['inboard_tube_wall_pullthrough_capacity_n']
    assert now['revision']!=rejected['configuration']['revision']


def test_rehashed_native_part_validity_cannot_claim_invalid_solid(packet):
    r=json.loads((packet/'native-cad.json').read_text());r['parts'][0]['valid']=False;reseal(packet,'native-cad.json',r)
    with pytest.raises(ValueError,match='validity'):a.verify(packet)


@pytest.mark.parametrize('mutation',['missing-triangle','reversed-shell','inset-extrema'])
def test_rehashed_mesh_cannot_hide_incomplete_or_shifted_material_shell(packet,mutation):
    mesh=json.loads(gzip.decompress((packet/'native-mesh.json.gz').read_bytes()));part=mesh['parts'][0]
    if mutation=='missing-triangle':part['triangles'].pop()
    elif mutation=='reversed-shell':part['triangles']=[t[::-1] for t in part['triangles']]
    else:
        centre=[sum(v[i] for v in part['vertices_m'])/len(part['vertices_m']) for i in range(3)]
        part['vertices_m']=[[centre[i]+(v[i]-centre[i])*.999 for i in range(3)] for v in part['vertices_m']]
    reseal(packet,'native-mesh.json.gz',mesh)
    digest=sha256((packet/'native-mesh.json.gz').read_bytes()).hexdigest()
    cad=json.loads((packet/'native-cad.json').read_text());cad['files_sha256']['native-mesh.json.gz']=digest;reseal(packet,'native-cad.json',cad)
    visual=json.loads((packet/'visual-receipt.json').read_text());visual['mesh_sha256']=digest;reseal(packet,'visual-receipt.json',visual)
    with pytest.raises(ValueError,match='mesh'):a.verify(packet)


def test_native_packet_counts_all_current_socket_paths_and_hardware(packet):
    d=json.loads((packet/'definition.json').read_text());h=a.load()['hardpoint'];access=json.loads((packet/'tool-access.json').read_text())
    assert access['path_count']==len(d['interfaces'])*h['bolts']*2==768
    assert len(access['paths'])==access['path_count'] and access['failures']==[]


def test_rehashed_truncated_centroid_cannot_bypass_property_check(packet):
    mass=json.loads((packet/'mass-properties.json').read_text());mass['regions'][0]['centre_of_volume_m'].pop();reseal(packet,'mass-properties.json',mass)
    with pytest.raises(ValueError):a.verify(packet)


@pytest.mark.parametrize('mutation',['duplicate','shift'])
def test_rehashed_socket_paths_cannot_claim_duplicate_or_shifted_coverage(packet,mutation):
    access=json.loads((packet/'tool-access.json').read_text())
    if mutation=='duplicate':access['paths'][1]=deepcopy(access['paths'][0])
    else:access['paths'][0]['start_m'][0]+=.01
    reseal(packet,'tool-access.json',access)
    with pytest.raises(ValueError,match='socket path'):a.verify(packet)


def test_socket_specs_cover_unique_declared_bolts_and_mirrored_actual_centres():
    d=a.definition();h=a.load()['hardpoint'];specs=a.socket_paths(d)
    assert len(specs)==len(d['interfaces'])*h['bolts']*2==768
    assert len({(p['interface'],p['bolt_index'],p['direction']) for p in specs})==len(specs)
    interfaces={p['id']:p for p in d['interfaces']}
    for p in specs:
        c=interfaces[p['interface']]['bolt_centres_m'][p['bolt_index']]
        assert p['start_m'][0]==c[0] and p['start_m'][2]==c[2]
        assert p['start_m'][1]==p['start_y_m']
        assert p['outer_diameter_m']==h['socket_outer_diameter_m'] and p['length_m']>0
        assert (p['start_y_m']>0)==(int(p['interface'].split('/')[1])>0)



def test_loaded_flange_face_cut_rejects_exact_twelve_bolt_candidate():
    rejected=json.loads(a.REJECTED_FLANGE.read_text());old=rejected['configuration']['hardpoint'];r=a.study();h=r['hardpoint_screen'];path=r['carrier_load_path_screen']
    assert sha256(a.encoded(rejected['definition'])).hexdigest()==rejected['definition_sha256']
    force=26400*9.81*1.3*1.5/23
    correct_tension=force*(1.2+old['carrier_flange_m']-.88)*old['prying_multiplier']/((max(old['rows_z_m'])-min(old['rows_z_m']))*len(old['columns_x_m']))
    assert rejected['tension_per_bolt_n']==pytest.approx(correct_tension)
    assert rejected['prior_wrong_stringer_centre_tension_n']<rejected['inboard_wall_pullthrough_capacity_n']<correct_tension
    assert r['rejected_twelve_bolt_candidate']['fixture_sha256']==a.digest(a.REJECTED_FLANGE)
    d=a.definition();flange=next(p for p in d['parts'] if p['id']=='hardpoint/1/00/carrier-flange')
    assert h['joint_geometry']['loaded_flange_face_y_m']==flange['at_m'][1]+flange['size_m'][1]
    assert h['geometric_force_offset_m']==pytest.approx(.352)
    assert h['tension_per_bolt_n']==pytest.approx(force*.352*1.5/(.17*8))
    assert h['tension_per_bolt_n']<h['inboard_tube_wall_pullthrough_capacity_n']
    assert path['lower_cantilever_moment_nm']==pytest.approx(path['body_joint_couple_nm']+force*path['upper_arm_m'])
    assert path['upper_arm_m']==pytest.approx(1.44-1.232)
    assert path['moment_equilibrium_residual_nm']==pytest.approx(0.,abs=1e-8)


def test_native_verify_load_calls_are_bounded_for_the_actual_packet(packet,monkeypatch):
    original=a.load;calls=[]
    def observed_load():
        calls.append(None)
        return original()
    monkeypatch.setattr(a,"load",observed_load)
    a.verify(packet)
    assert len(calls)<=24, "Configuration validation must stay bounded independently of all4,040material regions"



def test_display_envelopes_are_explicitly_separate_from_native_geometry():
    d=a.definition();before=sha256(a.encoded(d)).hexdigest();visible=[p for p in d['parts'] if p['role']!='guideway-context']
    triangles=0
    for p in visible:
        view=a.display_surface(p);props=a.mesh_properties(view);size=models.global_size(p)
        assert props['bounds_m']==pytest.approx(p['at_m']+[p['at_m'][i]+size[i] for i in range(3)])
        assert view['id']==p['id'] and view['material']==p['material']
        assert 'volume_m3' not in view and 'holes' not in view
        triangles+=len(view['triangles'])
    assert triangles<150000
    assert sha256(a.encoded(d)).hexdigest()==before
    assert 'display-only' in a.display_surface.__doc__.lower() or 'display envelope only' in a.display_surface.__doc__.lower()


@pytest.mark.parametrize('mutation',['acceptance','count'])
def test_rehashed_visual_lod_cannot_claim_native_acceptance_or_omit_regions(packet,mutation):
    visual=json.loads((packet/'visual-receipt.json').read_text())
    if mutation=='acceptance':visual['display_lod']['display_mesh_is_acceptance_evidence']=True
    else:visual['display_lod']['represented_material_region_count']-=1
    reseal(packet,'visual-receipt.json',visual)
    with pytest.raises(ValueError,match='visual scope'):a.verify(packet)



def cylinder_test_part():return dict(id='control',kind='cylinder',cylinder_axis='y',size_m=[.012,.012,.23],at_m=[0.,0.,0.],material='steel')


def test_cylinder_radial_extrema_use_geometric_chord_sagitta_only():
    p=cylinder_test_part();mesh=a.display_surface(p,segments=26);props=a.mesh_properties(mesh);tol=a.mesh_bounds_tolerances(p,mesh)
    assert tol[1]==1e-8 and 1e-8<tol[0]<.00005 and tol[0]==tol[2]
    exact=p['at_m']+[p['at_m'][i]+models.global_size(p)[i] for i in range(3)]
    assert any(abs(x-y)>1e-8 for x,y in zip(props['bounds_m'],exact))
    assert all(abs(x-y)<=t for x,y,t in zip(props['bounds_m'],exact,tol*2))


@pytest.mark.parametrize('mutation',['inset-radius','shift-radius','coarse-gap','missing-end-ring','off-radius-side'])
def test_cylinder_chord_bound_cannot_hide_geometry_shift_or_missing_coverage(mutation):
    p=cylinder_test_part();mesh=a.display_surface(p,segments=26)
    if mutation=='inset-radius':
        for v in mesh['vertices_m']:
            for axis in (0,2):v[axis]=.006+(v[axis]-.006)*.999
    elif mutation=='shift-radius':
        for v in mesh['vertices_m']:v[0]+=.000001
    elif mutation=='coarse-gap':mesh=a.display_surface(p,segments=6)
    elif mutation=='missing-end-ring':
        for v in mesh['vertices_m']:
            if v[1]==.23:v[1]=.229
    else:mesh['vertices_m'].append([.006,.115,.007])
    with pytest.raises(ValueError):a.mesh_bounds_tolerances(p,mesh)



def test_cap_vertex_insertion_cannot_hide_outside_native_circle():
    p=cylinder_test_part();mesh=a.display_surface(p,segments=26);before=a.mesh_properties(mesh);n=len(mesh['vertices_m']);mesh['vertices_m'].append([0.,0.,0.])
    i,j,k=mesh['triangles'].pop(0);mesh['triangles']+= [[i,j,n],[j,k,n],[k,i,n]]
    after=a.mesh_properties(mesh)
    assert after['euler_characteristic']==2 and after['signed_volume_m3']==pytest.approx(before['signed_volume_m3'])
    with pytest.raises(ValueError,match='radius'):a.mesh_bounds_tolerances(p,mesh)


def annular_cylinder_mesh(p,segments=26):
    outer=a.display_surface(p,segments=segments);vertices=outer['vertices_m'];axis='xyz'.index(p['cylinder_axis']);uv=[i for i in range(3) if i!=axis]
    centre=[p['at_m'][i]+models.global_size(p)[i]/2 for i in range(3)];ratio=p['holes'][0]['diameter_m']/p['size_m'][0]
    vertices=vertices+[[v[i] if i==axis else centre[i]+(v[i]-centre[i])*ratio for i in range(3)] for v in vertices];faces=[];n=segments
    for i in range(n):
        j=(i+1)%n
        faces.extend([[i,j,n+j],[i,n+j,n+i],[2*n+i,3*n+j,2*n+j],[2*n+i,3*n+i,3*n+j],
                      [n+i,n+j,3*n+j],[n+i,3*n+j,3*n+i],[i,2*n+j,j],[i,2*n+i,2*n+j]])
    return dict(vertices_m=vertices,triangles=faces)


def test_enlarged_bore_cannot_hide_inside_volume_tolerance():
    p=dict(id='spacer-control',kind='cylinder',cylinder_axis='y',size_m=[.025,.025,.116],at_m=[0.,0.,0.],material='steel',holes=[dict(axis='y',x_m=.0125,z_m=.0125,diameter_m=.013,length_m=.116)])
    mesh=annular_cylinder_mesh(p);a.mesh_bounds_tolerances(p,mesh)
    for v in mesh['vertices_m'][52:]:
        for i in (0,2):v[i]=.0125+(v[i]-.0125)*1.01
    props=a.mesh_properties(mesh)
    assert props['euler_characteristic']==0
    assert abs(props['signed_volume_m3']/models.volume(p)-1)<.03
    with pytest.raises(ValueError,match='radius'):a.mesh_bounds_tolerances(p,mesh)
