"""Each candidate admits only its exact load/source civil experiment."""
from pathlib import Path
import json
import pytest
from engineering.railway_closure import ROOT,civil_reference as proof,civil_package
from engineering.station_rail.common import encoded,identity


def registry(folder,names):
    folder.mkdir(parents=True,exist_ok=True)
    value={'schema':'osr-civil-proof-registry/1','manifests':names}
    value['index_id']=identity(value);(folder/proof.INDEX).write_bytes(encoded(value))


def test_civil_proof_compaction_keeps_results_and_records_recoverable_scratch(tmp_path):
    assert civil_package._omission_reason('case-1/fieldcraft/rolling-1.fieldcraft')
    assert civil_package._omission_reason('case-1/fieldcraft/rolling-1.fieldcraft.bak')
    assert civil_package._omission_reason('case-1/mesh-native/imported.msh')
    assert civil_package._omission_reason('case-1/input.step')
    assert civil_package._omission_reason('case-1/result.json') is None
    assert civil_package._omission_reason('case-1/mesh.json') is None
    source=tmp_path/'input.json';source.write_text('{"same":true}\n')
    first=tmp_path/'first.tar.gz';second=tmp_path/'second.tar.gz'
    civil_package._stable_tar(first,{'proof/input.json':source})
    civil_package._stable_tar(second,{'proof/input.json':source})
    assert first.read_bytes()==second.read_bytes()


def test_current_archive_matches_only_exact_evaluation():
    out=ROOT/'docs/design-engine/reconciled-pilot'
    civil=json.loads((out/'civil.json').read_bytes());axles=json.loads((out/'axle-loads.json').read_bytes())
    result=proof.applicable(civil,axles)
    assert result['applicable']
    assert result['manifest_file']==json.loads((out/'summary.json').read_bytes())['civil']['native_reference']['manifest_file']
    registered=json.loads((ROOT/proof.FOLDER/result['manifest_file']).read_bytes())
    assert registered['civil_evaluation_id']==civil['evaluation_id']
    assert registered['input_load_evaluation_id']==axles['evaluation_id']
    assert result['physical_accepted'] is False
    changed=dict(axles,evaluation_id='0'*64)
    assert proof.applicable(civil,changed)['applicable'] is False


@pytest.mark.parametrize('names',[['../outside.json'],['one.json','one.json'],[],['/absolute.json']])
def test_registry_rejects_ambiguous_or_escaping_configuration(tmp_path,names):
    registry(tmp_path,names)
    with pytest.raises(ValueError):proof.manifest_names(tmp_path)


def test_matching_proofs_are_not_chosen_by_filename_or_registration_order(tmp_path):
    folder=tmp_path/proof.FOLDER;registry(folder,['first.json','second.json'])
    value={'schema':'osr-pilot-civil-native-proof/1','civil_evaluation_id':'c'*64,'input_load_evaluation_id':'a'*64}
    value['evaluation_id']=identity(value)
    for name in ('first.json','second.json'):(folder/name).write_bytes(encoded(value))
    with pytest.raises(ValueError,match='Ambiguous exact-load'):
        proof.applicable({'evaluation_id':'c'*64},{'evaluation_id':'a'*64},root=tmp_path)


def test_other_loads_remain_held_without_running_a_solver(tmp_path,monkeypatch):
    folder=tmp_path/proof.FOLDER;registry(folder,['different-load.json'])
    value={'schema':'osr-pilot-civil-native-proof/1','civil_evaluation_id':'c'*64,'input_load_evaluation_id':'a'*64}
    value['evaluation_id']=identity(value);(folder/'different-load.json').write_bytes(encoded(value))
    def forbidden(*args,**kwargs):raise AssertionError('A mismatched load must not inherit native evidence')
    monkeypatch.setattr(proof,'verify',forbidden)
    result=proof.applicable({'evaluation_id':'d'*64},{'evaluation_id':'b'*64},root=tmp_path)
    assert result['applicable'] is False and result['physical_accepted'] is False
