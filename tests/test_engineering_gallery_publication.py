"""Exercise the published native evidence and reject resealed identity drift."""
import shutil
import pytest
from tools.engineering_gallery import cad, publication as p


def test_public_gallery_reopens_complete_native_field():
    result=p.verify(p.ROOT/p.DEST)
    assert result['current'] and result['cards']==6
    assert result['native_nodes']==43340 and result['native_cells']==22680
    assert not result['physical_accepted']


@pytest.mark.parametrize('fault',['mislabelled-view','failed-render','accepted-render','fem-request','producer-omission','held-relabelled','resource-understatement'])
def test_resealed_packets_cannot_hide_wrong_view_or_failed_evidence(tmp_path,fault):
    packet=tmp_path/'gallery';shutil.copytree(p.ROOT/p.DEST,packet)
    manifest=cad.read(packet/'manifest.json')
    if fault=='mislabelled-view':
        a=packet/'evidence'/'bogie-cradle';b=packet/'evidence'/'vehicle-car0'
        shutil.rmtree(b);shutil.copytree(a,b)
    elif fault in ('failed-render','accepted-render'):
        path=packet/'evidence'/'launch-assembly'/'result.json';result=cad.read(path)
        if fault=='failed-render':result['execution']='held';result['exit_code']=1
        else:result['physical_accepted']=True
        p.dump(path,p.sealed({k:v for k,v in result.items() if k!='evaluation_id'}))
    elif fault=='held-relabelled':
        path=packet/'evidence'/'vehicle-car0'/'image-record.json';result=cad.read(path);result['execution']='completed'
        p.dump(path,p.sealed({k:v for k,v in result.items() if k!='evaluation_id'}))
    elif fault=='resource-understatement':
        manifest['cards']['vehicle-car0']['observed_usage']['peak_rss_kib']=1
    elif fault=='fem-request':
        path=packet/'evidence'/'civil-fem'/'figure.json';figure=cad.read(path);figure['request_id']='0'*64
        p.dump(path,p.sealed({k:v for k,v in figure.items() if k!='evaluation_id'}))
    else:manifest['source_sha256'].pop(next(iter(manifest['source_sha256'])))
    manifest['files']=p.inventory(packet)
    p.dump(packet/'manifest.json',p.sealed({k:v for k,v in manifest.items() if k!='evaluation_id'}))
    with pytest.raises(ValueError):p.verify(packet)
