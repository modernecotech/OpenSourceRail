"""Source/geometry, factory-scope and selected-evidence publication contracts."""
from copy import deepcopy
from pathlib import Path
import json,shutil
import pytest
from engineering.design_search.craft_backends import launch_detail_publication as p
from engineering.design_search.craft_backends import launch_assembly as a
from engineering.design_search.craft_backends.cases import identity

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def source():return json.loads((ROOT/p.DATA).read_bytes())


def test_fixed_fixture_is_amortized_once_without_second_wholesale_discount(source):
    one=p.costing(a.build(),source,1);many=p.costing(a.build(),source,100)
    assert one['nominal_component_count']==120 and one['nominal_material_region_count']==122
    assert one['no_additional_bulk_discount'] and one['fixed_fixture_counted_once']
    assert one['source_dataset_id']==source['dataset_id']
    for i,case in enumerate(p.CASES):
        x,y=one['cases'][case],many['cases'][case]
        assert x['steel_stock_usd']==y['steel_stock_usd'] and x['bronze_proxy_stock_usd']==y['bronze_proxy_stock_usd']
        assert x['factory_usd_per_shuttle']-y['factory_usd_per_shuttle']==pytest.approx(one['assumptions']['one_batch_fixture_tooling_usd'][i]*.99)
        assert y['committed_batch_factory_usd']==pytest.approx(y['factory_usd_per_shuttle']*100)
    assert one['cases']['low']['factory_usd_per_shuttle']<one['cases']['base']['factory_usd_per_shuttle']<one['cases']['high']['factory_usd_per_shuttle']
    assert one['procurement_approved'] is False


def test_grade_bronze_form_and_landing_are_explicit_additions_not_material_equivalence(source):
    c=p.costing(a.build(),source)
    assert all(x>0 for x in c['assumptions']['steel_grade_form_premium_usd_per_kg'])
    assert all(x>0 for x in c['assumptions']['bronze_tin_alloy_stock_conversion_premium_usd_per_kg'])
    assert c['source_observation_ids']['bronze_proxy'].endswith('copper-1')
    assert 'not a supplier quote' in c['estimate_class']
    assert any('Actuator and storage' in s for s in c['exclusions'])
    assert [c['cases'][s]['labour_hours'] for s in p.CASES]==[12.,24.,48.]


@pytest.mark.parametrize('quantity',[0,-1,1.5,True,100001])
def test_uncommitted_or_invalid_volume_does_not_trigger_speculative_discount(source,quantity):
    with pytest.raises(ValueError):p.costing(a.build(),source,quantity)


def test_only_the_authenticated_advisory_label_difference_is_allowed():
    current=a.build();old=deepcopy(current)
    old['necessary_screens'].pop('screening_factor_basis')
    old['assembly_definition_id']=identity({k:v for k,v in old.items() if k!='assembly_definition_id'})
    r=p.reconcile(current,old)
    assert r['physical_geometry_identical'] and r['load_interface_identical'] and not r['source_records_rewritten']
    old['necessary_screens']['proof_factor']=.1
    old['assembly_definition_id']=identity({k:v for k,v in old.items() if k!='assembly_definition_id'})
    with pytest.raises(ValueError,match='Undeclared'):p.reconcile(current,old)


@pytest.mark.parametrize('attack',['geometry','force-interface','seal'])
def test_source_context_difference_cannot_hide_different_physical_or_load_inputs(attack):
    current=a.build();other=deepcopy(current)
    if attack=='geometry':other['physical_definition']['parts'][0]['size_m'][0]+=.1
    if attack=='force-interface':other['fem_interface']['total_force_N']=1.
    if attack!='seal':other['assembly_definition_id']=identity({k:v for k,v in other.items() if k!='assembly_definition_id'})
    else:other['assembly_definition_id']='0'*64
    with pytest.raises(ValueError):p.reconcile(current,other)


def test_published_package_is_reviewable_and_verifies_without_private_solvers():
    result=p.verify(root=ROOT)
    assert result['verified'] and result['selected_package_only'] and not result['fresh_native_solve']
    folder=ROOT/p.OUTPUT
    assert (folder/'assembly.sc').stat().st_size>100000 and (folder/'assembly.step').stat().st_size>100000
    assert (folder/'assembly.png').read_bytes().startswith(b'\x89PNG')
    assert (folder/'clevis-bore-stress.png').read_bytes().startswith(b'\x89PNG')
    text=(folder/'README.md').read_text()
    assert 'previous 40 mm pin' in text and 'one ear with 80 kN' in text and '18% opacity' in text
    assert sum(f.stat().st_size for f in folder.iterdir())<5*1024**2


def _reseal_file_and_inventory(folder,name,value,key=None):
    if key:value[key]=identity({k:v for k,v in value.items() if k!=key})
    path=folder/name;path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    m=json.loads((folder/'manifest.json').read_bytes());sha=p.native.digest(path)
    m['files_sha256'][name]=sha
    if name in m['selected_asset_source_sha256']:m['selected_asset_source_sha256'][name]=sha
    m['manifest_id']=identity({k:v for k,v in m.items() if k!='manifest_id'})
    (folder/'manifest.json').write_text(json.dumps(m))


@pytest.mark.parametrize('attack',['free-cost','wrong-candidate','release'])
def test_resealed_publication_still_checks_numerical_scope_and_candidate(tmp_path,attack):
    folder=tmp_path/'package';shutil.copytree(ROOT/p.OUTPUT,folder)
    if attack=='free-cost':
        v=json.loads((folder/'factory-cost.json').read_bytes());v['cases']['base']['factory_usd_per_shuttle']=0
        _reseal_file_and_inventory(folder,'factory-cost.json',v,'cost_estimate_id')
    else:
        v=json.loads((folder/'fem-evidence.json').read_bytes())
        if attack=='wrong-candidate':v['candidate_id']='d'*64
        else:v['physical_accepted']=True
        _reseal_file_and_inventory(folder,'fem-evidence.json',v,'result_id')
    with pytest.raises(ValueError):p.verify(folder,root=ROOT)
