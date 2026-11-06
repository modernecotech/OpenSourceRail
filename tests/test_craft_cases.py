"""Independent SI/source/identity boundaries; no native CAD or physical acceptance."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import os
import shutil

import pytest

HERE=Path(__file__).resolve().parents[1]
REFERENCE=Path(os.environ.get('OSR_CRAFT_REFERENCE_ROOT',HERE))
spec=spec_from_file_location('osr_craft_case_fixtures',HERE/'engineering/design_search/craft_backends/cases.py')
c=module_from_spec(spec);spec.loader.exec_module(c)


@pytest.fixture(scope='module')
def records():
    return {v['case_id']:v for v in c.cases(REFERENCE)}


def reseal(value):
    value['case_definition_id']=c.identity({k:v for k,v in value.items() if k!='case_definition_id'})


def test_three_real_demonstrations_plus_asymmetric_unit_control_are_deterministic(records):
    assert [v['case_id'] for v in c.cases(REFERENCE)]==list(records)
    assert sum(v['expected']['part_count'] for v in records.values())==25
    for value in records.values():
        assert c.validate_case(value)==value
        assert all(value[k] is False for k in c.FLAGS)
        assert value['units']['length']=='m'


def test_selected_beam_is_six_source_solids_with_end_diaphragms(records):
    value=records['selected-beam20m']
    assert value['expected']['part_count']==6
    assert value['expected']['total_volume_m3']==pytest.approx(22.2816)
    assert value['expected']['total_material_mass_kg']==pytest.approx(55704.)
    assert value['expected']['bounds_m'][0]==pytest.approx([0.,-1.,-1.592])
    assert value['expected']['bounds_m'][1]==pytest.approx([20.,1.,-.192])
    assert len([e for e in value['entities'] if 'diaphragm' in e['id']])==2
    assert 'reinforcement' in value['scope'] and 'excluded, not zero' in value['scope']


def test_sill_retains_four_material_walls_and_actual_installed_frame(records):
    value=records['selected-side-sill']
    assert value['candidate_id']==records['selected-beam20m']['candidate_id']
    assert value['source_selection_id']==records['selected-beam20m']['source_selection_id']
    assert value['expected']['total_volume_m3']==pytest.approx(.139808)
    assert value['expected']['total_material_mass_kg']==pytest.approx(378.87968)
    assert value['expected']['bounds_m'][0]==pytest.approx([-8.5,1.01,.4445])
    assert all(e['geometry']['at_m']==e['source_entity']['source_at_m'] for e in value['entities'])
    assert all(e['presentation_offset_applied'] is False for e in value['entities'])


def test_shuttle_is_separate_layout_not_selected_train_and_unknowns_remain_unknown(records):
    value=records['research-launch-shuttle']
    assert value['candidate_id']!=records['selected-beam20m']['candidate_id']
    assert value['candidate_id']==value['component_geometry_id']
    assert value['source_selection_id'] is None and value['source_candidate_id'] is None
    assert value['source_study_id']=='76dcb35c33300628c60c97030c12eac2b1530bffef4ff1dff4b4ea396443d4a5'
    assert value['expected']['total_material_mass_kg'] is None
    assert value['expected']['known_material_mass_subtotal_kg']>0
    assert len([m for m in value['expected']['part_material_masses_kg'].values() if m is None])==2
    assert any('160000kg point mass' in a for a in value['assumptions'])
    cyl=next(e for e in value['entities'] if e['shape']=='cylinder')
    assert cyl['geometry']['axis']==[0,1,0]


def test_asymmetric_control_exposes_millimetre_and_translation_errors(records):
    value=records['asymmetric-si-control']
    assert value['expected']['total_volume_m3']==pytest.approx(.000196131)
    assert value['expected']['centroid_m']==pytest.approx([-2.1395,1.7235,.6065])
    assert value['entities'][0]['geometry']['size_m']==[.321,.047,.013]


def test_exploded_offsets_cannot_change_physical_geometry_or_placement(records):
    e=records['selected-side-sill']['entities'][0]['source_entity']
    changed=deepcopy(e);changed['render_offset_m']=[100.,-200.,300.]
    a=c.normalize_entity(e,'6082-T6-proposed');b=c.normalize_entity(changed,'6082-T6-proposed')
    assert c.geometry_identity([a])==c.geometry_identity([b])
    assert a['geometry']==b['geometry']


@pytest.mark.parametrize('attack',['candidate','selection','volume','centroid','bounds','coverage','subtotal','unknown-mass','physical'])
def test_resealed_but_inconsistent_case_is_refused(records,attack):
    value=deepcopy(records['research-launch-shuttle' if attack in ('selection','unknown-mass') else 'selected-beam20m'])
    if attack=='candidate':value['candidate_id']='a'*64
    if attack=='selection':value['source_selection_id']='b'*64
    if attack=='volume':value['expected']['total_volume_m3']*=1000
    if attack=='centroid':value['expected']['centroid_m'][0]+=1
    if attack=='bounds':value['expected']['bounds_m'][0][0]+=1
    if attack=='coverage':value['expected']['part_count']+=1
    if attack=='subtotal':value['expected']['known_material_mass_subtotal_kg']=0
    if attack=='unknown-mass':value['expected']['total_material_mass_kg']=value['expected']['known_material_mass_subtotal_kg']
    if attack=='physical':value['physical_accepted']=True
    reseal(value)
    with pytest.raises(ValueError):c.validate_case(value)


@pytest.mark.parametrize('shape',['pipe','profile','mesh','unknown'])
def test_unsupported_or_unquantified_shapes_do_not_become_zero_material(shape):
    with pytest.raises(ValueError,match='Unsupported or unquantified'):
        c.normalize_entity(dict(id='unknown',shape=shape,at_m=[0,0,0],material='unknown',source='unresolved',basis='proposed-envelope'))


def test_changed_source_producer_is_refused_without_rebinding_publication(records,tmp_path):
    names=set()
    for value in records.values():names.update(value['source_sha256'])
    names.update((c.CURRENT+'/manifest.json',c.GALLERY+'/manifest.json'))
    for name in names:
        src=Path(c.__file__) if name==c.PRODUCER else REFERENCE/name
        dst=tmp_path/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    p=tmp_path/'engineering/visual_models/station.py';p.write_bytes(p.read_bytes()+b'\n# changed producer\n')
    with pytest.raises(ValueError,match='source changed'):
        c.cases(tmp_path)
