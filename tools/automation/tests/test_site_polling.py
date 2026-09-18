"""Grouped FUXA transport preserves individual identities, quality and alarms."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import threading
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'services/integration'))
from osr_integration.config import build_package,digest,validate_package
from osr_integration.fuxa import project,deployment_manifest,deployment_review
from osr_integration.server import GatewayHTTPServer,FuxaReadHandler
from osr_integration.store import Store


@pytest.fixture
def package():
    generic=json.loads((ROOT/'deployment/supervision/config/generic.json').read_text())
    return build_package(generic,{'city':'mosul','fuxa_polling_scope':'site'},[
        dict(asset_type='station',asset_id='MOS-ST-001',name='Station'),
        dict(asset_type='station',asset_id='MOS-ST-002',name='Other station')],'revision')


def test_grouped_project_retains_every_tag_and_uses_valid_transport_sources(package):
    grouped=project([package]);original=copy.deepcopy(package)
    original['fuxa_polling_scope']='asset';original['sha256']=digest({k:v for k,v in original.items() if k!='sha256'})
    individual=project([original])
    flatten=lambda p:{key:value for d in p['devices'].values() for key,value in d['tags'].items()}
    assert flatten(grouped)==flatten(individual)
    assert len(grouped['devices'])==2 and len(individual['devices'])==10
    for view in grouped['hmi']['views']:
        for variable in view['variables'].values():
            if variable['source']=='0':continue
            assert variable['id'] in grouped['devices'][variable['source']]['tags']
    assert all(t['memaddress'] in grouped['devices'] for t in grouped['server']['tags'].values())
    assert len(grouped['server']['tags'])==len(grouped['devices'])
    manifest=deployment_manifest([package]);assert manifest['packages'][0]['devices']==sorted(grouped['devices'])
    review=deployment_review(individual,[package]);assert review['destructive_changes']
    assert len(review['devices']['removed'])==10 and len(review['devices']['added'])==2


def test_site_api_matches_individual_reads_and_excludes_retired_assets(tmp_path,package):
    store=Store(tmp_path/'db');store.apply(package,'engineer')
    active=[a for a in package['equipment'] if a['site_id']=='MOS-ST-001']
    # Exercise every asset's disconnected quality and one active alarm.
    with store.connect() as db:
        a=next(a for a in active if a['alarms']);scope=store.scope('mosul','simulation',a['asset_id'])
        db.execute('INSERT INTO alarms(key,scope,rule,active) VALUES(?,?,?,1)',(scope+'|test',scope,a['alarms'][0]['id']))
    expected=[tag for a in active for tag in FuxaReadHandler.tags(store.device('mosul','simulation',a['asset_id']))]
    actual=[tag for a in store.site_devices('mosul','simulation','MOS-ST-001') for tag in FuxaReadHandler.tags(a)]
    assert sorted(actual,key=lambda t:t['id'])==sorted(expected,key=lambda t:t['id'])
    server=GatewayHTTPServer(('127.0.0.1',0),FuxaReadHandler);server.store=store
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        base=f'http://127.0.0.1:{server.server_port}/site-tags/'
        with urlopen(base+'mosul/simulation/MOS-ST-001') as response:
            assert sorted(json.load(response),key=lambda t:t['id'])==sorted(expected,key=lambda t:t['id'])
        for path in ['samawah/simulation/MOS-ST-001','mosul/physical/MOS-ST-001','mosul/simulation/missing']:
            with pytest.raises(HTTPError) as error:urlopen(base+path)
            assert error.value.code==404
        retired=active[0]
        with store.connect() as db:db.execute("UPDATE assets SET configuration_status='retired' WHERE asset_id=?",(retired['asset_id'],))
        tags=[tag for a in store.site_devices('mosul','simulation','MOS-ST-001') for tag in FuxaReadHandler.tags(a)]
        assert not any(t['id'].startswith(retired['fuxa_device_id']+'__') for t in tags)
    finally:server.shutdown();server.server_close();thread.join()


def test_scope_is_validated_and_part_of_package_change_review(tmp_path,package):
    store=Store(tmp_path/'db');store.apply(package,'engineer')
    changed=copy.deepcopy(package);changed['fuxa_polling_scope']='asset';changed['sha256']=digest({k:v for k,v in changed.items() if k!='sha256'})
    review=store.package_review(changed)
    assert any(r['path']=='fuxa_polling_scope' for r in review['package_changes'])
    for value in ['city','',None,True]:
        invalid=copy.deepcopy(package);invalid['fuxa_polling_scope']=value;invalid['sha256']=digest({k:v for k,v in invalid.items() if k!='sha256'})
        with pytest.raises(ValueError):validate_package(invalid)
