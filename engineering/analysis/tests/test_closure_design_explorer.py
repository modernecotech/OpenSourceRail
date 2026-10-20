"""Offline UI must preserve exact identities and expose missing/stale evidence."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import pytest
from engineering.assembly_design import design_explorer as explorer


def exhibit():
    parts = [dict(id='beam', revision='beam-r1', material='steel', process_route='cut and drill',
                  properties={'mass_kg': 12.5}, joints=['seat']),
             dict(id='seat', revision='seat-r3', material='steel', process_route='machine',
                  properties={'mass_kg': 2.})]
    return dict(path='civil assembly', candidate=dict(kind='civil-assembly', revision='candidate-r4',
        source_scope='Provisional concrete and reinforcement representation',
        contract=dict(name='Civil bay', parts=parts),
        metadata={'assembly_sequence':[
            dict(id='place-seat', title='Place seat', part_ids=['seat'], requires=[]),
            dict(id='place-beam', title='Place beam', part_ids=['beam'], requires=['place-seat'])]},
        open_requirements=['Supplier load table']),
        assessment=dict(candidate_revision='candidate-r4', failed_checks=[], held_checks=['soil bearing']),
        result=dict(candidate_revision='candidate-r4', native_state='passed'),
        mesh={'parts':[dict(id=part, vertices=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]], faces=[[0,1,2],[0,1,3]]) for part in ['beam','seat']]})


def read(output):
    return json.loads((output/'explorer-data.json').read_text())


def test_native_binding_stages_bom_assets_are_deterministic_and_portable(tmp_path):
    example=exhibit(); folder=tmp_path/'civil assembly';folder.mkdir()
    image=b'retained native preview bytes';(folder/'overview.png').write_bytes(image)
    first=explorer.build(tmp_path,[example]); html=(tmp_path/'index.html').read_bytes()
    second=explorer.build(tmp_path,[example]); assert first==second
    assert html==(tmp_path/'index.html').read_bytes()
    actual=read(tmp_path)['exhibits'][0]
    assert actual['represented_mass_kg']==14.5
    assert [r['id'] for r in actual['parts']]==['beam','seat']
    assert actual['parts'][0]['revision']=='beam-r1'
    assert actual['stages'][1]['requires']==['place-seat']
    assert actual['stages'][0]['part_ids']==['seat']
    assert actual['unassigned_part_ids']==[]
    assert {r['id'] for r in actual['projection']['parts']}=={'beam','seat'}
    assert len(actual['projection']['parts'][0]['envelope'])>=3
    assert actual['assets'][0]['sha256']==sha256(image).hexdigest()
    assert actual['assets'][0]['url']=='civil%20assembly/overview.png'
    assert actual['native_state']=='passed' and actual['design_complete'] is False
    assert actual['manufacturing_release'] is False and actual['physical_release'] is False
    assert 'STEP' in actual['unavailable_assets']
    assert b'fetch(' not in html and b'src="http' not in html
    assert b'rtl' in html and 'العربية'.encode() in html


def test_absent_geometry_and_unknown_mass_are_not_invented(tmp_path):
    example=exhibit();example.pop('mesh');example['candidate']['contract']['parts'][0]['properties']['mass_kg']=None
    example['candidate']['metadata']['assembly_sequence'][1]['part_ids']=[]
    explorer.build(tmp_path,[example]); row=read(tmp_path)['exhibits'][0]
    assert row['projection'] is None and row['represented_mass_kg'] is None
    assert row['assets']==[] and 'Native model' in row['unavailable_assets']
    assert row['unassigned_part_ids']==['beam']


def test_known_packaging_findings_are_visible_even_when_native_solids_pass(tmp_path):
    example=exhibit()
    finding=dict(instance_id='car-01/cooling-1',opening_id='door-left',state='datum-in-declared-door-circulation-prism')
    example['assessment']['measurements']=dict(equipment_packaging=dict(issues=[finding]))
    explorer.build(tmp_path,[example]);row=read(tmp_path)['exhibits'][0]
    assert row['native_state']=='passed' and row['design_complete'] is False
    assert any('car-01/cooling-1' in r and 'door-left' in r for r in row['open_requirements'])


def test_mesh_identity_mismatch_and_nonfinite_vertices_cannot_reach_ui(tmp_path):
    example=exhibit();example['mesh']['parts'][0]['id']='another beam'
    with pytest.raises(ValueError,match='identities'):explorer.build(tmp_path,[example])
    assert not (tmp_path/'index.html').exists()
    example=exhibit();example['mesh']['parts'][0]['vertices'][0][0]=float('nan')
    with pytest.raises(ValueError,match='non-finite'):explorer.build(tmp_path,[example])
    example=exhibit();example['mesh']['parts'].append(deepcopy(example['mesh']['parts'][0]))
    with pytest.raises(ValueError,match='identities'):explorer.build(tmp_path,[example])


@pytest.mark.parametrize('mutation',[
    lambda e:e['assessment'].update(candidate_revision='stale'),
    lambda e:e['result'].update(candidate_revision='stale'),
    lambda e:e['candidate']['metadata']['assembly_sequence'][0].update(part_ids=['unknown']),
    lambda e:e['candidate']['metadata']['assembly_sequence'][0].update(requires=['place-beam']),
    lambda e:e['candidate']['metadata']['assembly_sequence'][1].update(id='place-seat'),
    lambda e:e['candidate']['contract']['parts'].append(deepcopy(e['candidate']['contract']['parts'][0])),
])
def test_stale_results_unknown_parts_and_future_stage_dependencies_are_rejected(tmp_path,mutation):
    example=exhibit();mutation(example)
    with pytest.raises(ValueError):explorer.build(tmp_path,[example])
    assert not (tmp_path/'index.html').exists()


@pytest.mark.parametrize('path',['../escape','/tmp/elsewhere','a/../b','a//b','a\\b','a?b','a#b','a%2fb','https://remote.invalid/a','x\nfile'])
def test_unsafe_exhibit_paths_rejected(tmp_path,path):
    example=exhibit();example['path']=path
    with pytest.raises(ValueError,match='unsafe'):explorer.build(tmp_path,[example])
    assert not (tmp_path/'index.html').exists()


def test_symlinked_asset_cannot_link_outside_the_portable_package(tmp_path):
    output=tmp_path/'package';output.mkdir();outside=tmp_path/'outside';outside.mkdir()
    (outside/'overview.png').write_bytes(b'private file')
    (output/'civil assembly').symlink_to(outside,target_is_directory=True)
    with pytest.raises(ValueError,match='escapes'):explorer.build(output,[exhibit()])
    assert not (output/'index.html').exists()


def test_script_breakout_text_is_data_and_dom_never_uses_html_insertion(tmp_path):
    example=exhibit();attack='</script><img src=x onerror=alert(1)> & \u2028'
    example['candidate']['contract']['name']=attack
    example['candidate']['source_scope']=attack
    example['candidate']['contract']['parts'][0]['material']=attack
    explorer.build(tmp_path,[example]); page=(tmp_path/'index.html').read_text()
    assert attack not in page
    assert '\\u003c/script\\u003e' in page
    assert '.innerHTML' not in page and 'insertAdjacentHTML' not in page
    embedded=page.split('<script id="explorer-data" type="application/json">',1)[1].split('</script>',1)[0]
    assert json.loads(embedded)==read(tmp_path)
    assert read(tmp_path)['exhibits'][0]['title']==attack
    assert 'object-src' in page and "base-uri 'none'" in page


def test_projection_scales_with_exact_native_coordinates(tmp_path):
    example=exhibit();explorer.build(tmp_path,[example]);first=read(tmp_path)['exhibits'][0]['projection']['bounds_m']
    for part in example['mesh']['parts']:
        part['vertices']=[[2*x,2*y,2*z] for x,y,z in part['vertices']]
    explorer.build(tmp_path,[example]);second=read(tmp_path)['exhibits'][0]['projection']['bounds_m']
    assert second==pytest.approx([2*v for v in first],abs=1e-7)


def test_exhibit_and_data_budget_must_be_valid(tmp_path,monkeypatch):
    with pytest.raises(ValueError,match='at least one'):explorer.build(tmp_path,[])
    with pytest.raises(ValueError,match='uniquely'):explorer.build(tmp_path,[exhibit(),exhibit()])
    monkeypatch.setattr(explorer,'MAX_DATA_BYTES',10)
    with pytest.raises(ValueError,match='budget'):explorer.build(tmp_path,[exhibit()])
    assert not (tmp_path/'index.html').exists()


def test_verification_can_rebuild_elsewhere_without_changing_portable_paths(tmp_path):
    original=tmp_path/'original';original.mkdir()
    folder=original/'civil assembly';folder.mkdir()
    (folder/'overview.png').write_bytes(b'exact retained image')
    first=explorer.build(original,[exhibit()])
    verification=tmp_path/'verification'
    second=explorer.build(verification,[exhibit()],asset_root=original)
    assert first==second
    for name in ['index.html','explorer-data.json']:
        assert (original/name).read_bytes()==(verification/name).read_bytes()
        assert str(original).encode() not in (verification/name).read_bytes()
