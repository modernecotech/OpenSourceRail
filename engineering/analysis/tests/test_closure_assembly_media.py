"""Native identity, dependency and retained video controls for assembly media."""
from copy import deepcopy
import pytest
from engineering.assembly_design import assembly_media as media
from engineering.twin_workflow import core


def example():
    return dict(kind='controlled-fixture', revision='fixture-revision',
        contract=dict(parts=[dict(id='base'), dict(id='upper')]),
        metadata=dict(assembly_sequence=[
            dict(id='base-stage', title='Locate base', part_ids=['base'], requires=[]),
            dict(id='upper-stage', title='Fit upper part', part_ids=['upper'], requires=['base-stage'])]))


@pytest.mark.parametrize('defect', ('omission', 'duplicate', 'unknown-part', 'future-stage', 'duplicate-stage'))
def test_stages_cannot_hide_parts_or_invent_a_build_order(defect):
    c = example()
    if defect == 'omission': c['metadata']['assembly_sequence'].pop()
    elif defect == 'duplicate': c['metadata']['assembly_sequence'][1]['part_ids'].append('base')
    elif defect == 'unknown-part': c['metadata']['assembly_sequence'][1]['part_ids'] = ['other']
    elif defect == 'future-stage': c['metadata']['assembly_sequence'][0]['requires'] = ['upper-stage']
    else: c['metadata']['assembly_sequence'][1]['id'] = 'base-stage'
    with pytest.raises(ValueError): media.stages(c)


def test_encoded_native_stage_video_retains_geometry_identity_and_decodes(tmp_path):
    c = example()
    mesh = dict(parts=[dict(id=name,
        vertices=[[0., 0., z], [1., 0., z], [0., 1., z]], faces=[[0, 1, 2]])
        for name, z in (('base', 0.), ('upper', 1.))])
    source = tmp_path/'native-mesh.json'
    core.write(source, mesh)
    result = media.build(c, source, tmp_path)
    assert result['state'] == 'executed'
    assert result['frames'] == 12 and result['decoded_video']['codec_name'] == 'h264'
    assert not result['physical_validation'] and not result['design_complete']
    assert media.verify(c, source, tmp_path, result) == result
    changed = deepcopy(result)
    changed['decoded_video']['nb_frames'] = '999'
    with pytest.raises(ValueError, match='stream'): media.verify(c, source, tmp_path, changed)
    changed = deepcopy(c)
    changed['metadata']['assembly_sequence'][1]['title'] = 'Falsified installed acceptance'
    with pytest.raises(ValueError, match='stages'): media.verify(changed, source, tmp_path, result)
    (tmp_path/'assembly-stages.png').write_bytes(b'forged')
    with pytest.raises(ValueError, match='bytes'): media.verify(c, source, tmp_path, result)


def test_missing_mesh_identity_cannot_be_relabelled_as_a_video(tmp_path):
    source = tmp_path/'mesh.json'
    core.write(source, dict(parts=[dict(id='base')]))
    with pytest.raises(ValueError, match='identities'): media.build(example(), source, tmp_path)
