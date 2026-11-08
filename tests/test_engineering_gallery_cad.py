"""Display recipes preserve candidate/source boundaries and never grant release."""
from copy import deepcopy
import pytest
from tools.engineering_gallery import cad


def test_gallery_covers_exact_native_and_located_assembly_sources():
    recipes=list(cad.recipes())
    assert [r['kind'] for r in recipes]==['native','native','native','vehicle','civil']
    assert len({r['recipe_id'] for r in recipes})==5
    assert recipes[0]['candidate_id']==recipes[1]['candidate_id']
    assert recipes[2]['candidate_id']!=recipes[0]['candidate_id']
    assert all(cad.validate(r) for r in recipes)
    assert all(r['render_size']==[3000,1900] for r in recipes)


@pytest.mark.parametrize('change',['candidate','approval','source','camera'])
def test_changed_or_resealed_mixed_candidate_is_refused(change):
    r=deepcopy(next(cad.recipes()))
    if change=='candidate':r['candidate_id']='0'*64
    if change=='approval':r['physical_accepted']=True
    if change=='source':r['source_sha256'][r['input_file']]='0'*64
    if change=='camera':
        r['camera']={'view':'front'}
        with pytest.raises(ValueError,match='seal'):cad.validate(r)
        return
    r['recipe_id']=cad.identity({k:v for k,v in r.items() if k!='recipe_id'})
    with pytest.raises(ValueError):cad.validate(r)


def test_private_prepare_copies_exact_input_and_refuses_overwrite(tmp_path):
    r=next(cad.recipes());out=tmp_path/'run'
    cad.prepare(r,cad.ROOT,out,preview=True)
    scene=cad.read(out/'scene.json')
    assert scene['width']==1500 and scene['height']==950
    assert scene['candidate_id']==r['candidate_id']
    assert cad.digest(scene['input_path'])==r['source_sha256'][r['native_file']]
    assert scene['maximum_triangles']==1000000 and scene['maximum_mesh_groups']==668
    with pytest.raises(FileExistsError):cad.prepare(r,cad.ROOT,out)
