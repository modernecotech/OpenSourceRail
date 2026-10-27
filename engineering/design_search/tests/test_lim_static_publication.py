"""Recorded native fields stay portable without inheriting native-verifier gaps."""
from contextlib import contextmanager
from pathlib import Path
import json,tarfile
import pytest
from engineering.design_search import lim_static_publication as p,lim_static_benchmark as s

PACKET=Path(__file__).resolve().parents[3]/p.OUTPUT


@pytest.fixture(scope='module')
def execution(tmp_path_factory):
    root=tmp_path_factory.mktemp('recorded-static-fields')
    with tarfile.open(PACKET/'native-runs.tar.gz') as tar:
        for m in tar:
            assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
            dest=root/m.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(tar.extractfile(m).read())
    return root/'execution'


@contextmanager
def changed_files(root,names):
    saved={name:(root/name).read_bytes() for name in (*names,'manifest.json')}
    try:yield
    finally:
        for name,data in saved.items():(root/name).write_bytes(data)


def reseal_inventory(root):
    m=s.read(root/'manifest.json');m['campaign_id']=s.read(root/'campaign.json')['campaign_id']
    m['files_sha256']={f.relative_to(root).as_posix():p.digest(f) for f in root.rglob('*') if f.is_file() and f!=root/'manifest.json'}
    m.pop('manifest_id');m['manifest_id']=p.identity(m);(root/'manifest.json').write_bytes(p.encoded(m))


def test_actual_packet_verifies_without_reading_original_tool(monkeypatch):
    report=s.read(PACKET/'assessment.json');original=p.digest
    def guarded(path):
        assert str(path)!=report['tool_record']['path'],'Portable verification must not require the original executable'
        return original(path)
    monkeypatch.setattr(p,'digest',guarded)
    monkeypatch.setattr(s,'tool',lambda *a,**k:pytest.fail('No native tool invocation permitted'))
    v=p.verify();assert v['static_cases']==4 and not v['physical_accepted'] and not v['operating_map_admitted']


def test_resealed_raw_case_input_cannot_diverge_from_root_plan(execution):
    name='zero/input.json'
    with changed_files(execution,[name]):
        value=s.read(execution/name);value['case']['path_currents_A'][0]=1.
        (execution/name).write_bytes(p.encoded(value));reseal_inventory(execution)
        with pytest.raises(ValueError,match='executed case binding'):p.collect(execution)


def test_resealed_row_evaluation_identity_is_checked(execution):
    names=['zero/result.json','campaign.json']
    with changed_files(execution,names):
        r=s.read(execution/names[0]);r['evaluation_id']='0'*64;(execution/names[0]).write_bytes(p.encoded(r))
        c=s.read(execution/'campaign.json');c['rows'][0]=r;c.pop('campaign_id');c['campaign_id']=p.identity(c)
        (execution/'campaign.json').write_bytes(p.encoded(c));reseal_inventory(execution)
        with pytest.raises(ValueError,match='identity differs: evaluation_id'):p.collect(execution)


def test_source_work_gate_survives_resealed_native_agreement_true(execution):
    names=['quarter-current/work.txt','quarter-current/result.json','quarter-current/worker-result.json','campaign.json']
    with changed_files(execution,names):
        (execution/names[0]).write_text('0 0\n')
        plan=s.read(execution/'plan.json');case=plan['cases'][1];data=s.mesh_data(plan['parent_request'])
        bad=s.analyze(execution/'quarter-current',plan['parent_request'],case['path_currents_A'],data)
        assert bad['numerical_subset_agreement'] and abs(bad['getdp_source_work_minus_twice_energy_J'])>.01
        r=s.read(execution/names[1]);r['analysis']=bad;r.pop('evaluation_id');r['evaluation_id']=p.identity(r)
        (execution/names[1]).write_bytes(p.encoded(r))
        worker=s.read(execution/names[2]);worker['analysis']=bad;(execution/names[2]).write_bytes(p.encoded(worker))
        c=s.read(execution/'campaign.json');c['rows'][1]=r;c.pop('campaign_id');c['campaign_id']=p.identity(c)
        (execution/'campaign.json').write_bytes(p.encoded(c));reseal_inventory(execution)
        with pytest.raises(ValueError,match='work/boundary/operator numerical screen'):p.collect(execution)


def test_numeric_verification_tolerance_never_accepts_nonfinite_or_engineering_claims():
    assert p._same(1.,1.+1e-9) and not p._same(float('nan'),float('nan'))
    assert not p._same({'physical_accepted':False},{'physical_accepted':True})
    assert p._diagnostics_same({'global_imposed_source_current_A':-5.7e-14,'x':1.},{'global_imposed_source_current_A':-7.9e-15,'x':1.})
    assert not p._diagnostics_same({'global_imposed_source_current_A':1e-6,'x':1.},{'global_imposed_source_current_A':0.,'x':1.})


@pytest.mark.parametrize('flag',['engineering_accepted','configuration_adopted','manufacturing_release','operating_release'])
def test_resealed_nested_case_cannot_claim_acceptance_or_release(execution,flag):
    names=['zero/result.json','campaign.json']
    with changed_files(execution,names):
        r=s.read(execution/names[0]);r[flag]=True;r.pop('evaluation_id');r['evaluation_id']=p.identity(r)
        (execution/names[0]).write_bytes(p.encoded(r))
        c=s.read(execution/'campaign.json');c['rows'][0]=r;c.pop('campaign_id');c['campaign_id']=p.identity(c)
        (execution/'campaign.json').write_bytes(p.encoded(c));reseal_inventory(execution)
        with pytest.raises(ValueError,match='qualification/release claim forbidden'):p.collect(execution)


def test_resealed_recorded_command_cannot_claim_another_tool(execution):
    name='zero/command.json'
    with changed_files(execution,[name]):
        cmd=s.read(execution/name);cmd['command'][0]='/bin/true';(execution/name).write_bytes(p.encoded(cmd));reseal_inventory(execution)
        with pytest.raises(ValueError,match='recorded native command differs'):p.collect(execution)


def test_resealed_parent_result_cannot_claim_another_request(execution):
    names=['parent/result.json','parent/manifest.json','plan.json','campaign.json']
    names += [f'{case}/{file}' for case in s.NAMES for file in ('input.json','result.json')]
    with changed_files(execution,names):
        parent=s.read(execution/'parent/result.json');parent['request_id']='0'*64
        parent.pop('evaluation_id');parent['evaluation_id']=p.identity(parent);(execution/'parent/result.json').write_bytes(p.encoded(parent))
        receipt=s.read(execution/'parent/manifest.json');receipt['evaluation_id']=parent['evaluation_id']
        receipt['files_sha256']['result.json']=p.digest(execution/'parent/result.json');receipt.pop('manifest_id');receipt['manifest_id']=p.identity(receipt)
        (execution/'parent/manifest.json').write_bytes(p.encoded(receipt))
        plan=s.read(execution/'plan.json');plan['parent_result_sha256']=p.digest(execution/'parent/result.json');plan['parent_evaluation_id']=parent['evaluation_id']
        plan.pop('plan_id');plan['plan_id']=p.identity(plan);(execution/'plan.json').write_bytes(p.encoded(plan))
        camp=s.read(execution/'campaign.json');camp['plan_id']=plan['plan_id']
        for case,row in zip(s.NAMES,camp['rows']):
            inp=s.read(execution/case/'input.json');inp['plan']=plan;(execution/case/'input.json').write_bytes(p.encoded(inp))
            row['plan_id']=plan['plan_id'];row.pop('evaluation_id');row['evaluation_id']=p.identity(row)
            (execution/case/'result.json').write_bytes(p.encoded(row))
        camp.pop('campaign_id');camp['campaign_id']=p.identity(camp);(execution/'campaign.json').write_bytes(p.encoded(camp))
        manifest=s.read(execution/'manifest.json');manifest['plan_id']=plan['plan_id'];(execution/'manifest.json').write_bytes(p.encoded(manifest));reseal_inventory(execution)
        with pytest.raises(ValueError,match='parent result context differs'):p.collect(execution)
