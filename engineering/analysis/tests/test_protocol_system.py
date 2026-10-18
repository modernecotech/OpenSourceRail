"""Executable interface composition, independent vetoes and negative controls."""
import json
from pathlib import Path

import pytest

from engineering.continuous_design import capabilities, evidence, ledger, planning, protocol_receiver, protocol_system, research, service, tasks, worker
from engineering.twin_workflow import core
from engineering.analysis.tests.test_continuous_planning import complete,real_children


def executable_receiver(parameters):
    namespace={}
    exec(compile(protocol_receiver.source(parameters),'<generated-receiver>','exec'),namespace)
    return namespace['Receiver']


def guard(**facts):
    return all(facts.values())


def test_receiver_faults_and_each_local_guard_propagate_through_the_actual_link():
    receiver=executable_receiver(dict(decoder='bytes',history_capacity=4,sequence_policy='modular',reset_policy='standstill'))
    rows=protocol_system.replay(receiver,guard)
    assert len(rows)>1000 and all(row['passed'] for row in rows)
    assert sum(row['id'].startswith('local-') for row in rows)==len(tasks.FACTS)


def test_bridge_that_ignores_receiver_faults_fails_composed_negative_controls():
    class BrokenLink(protocol_system.Link):
        def receive(self,packet,receipt,local):
            return self.policy(**local)
    receiver=executable_receiver(dict(decoder='struct',history_capacity=1,sequence_policy='modular',reset_policy='standstill'))
    failures=[row for row in protocol_system.replay(receiver,guard,link_class=BrokenLink) if not row['passed']]
    assert any(row['id']=='crc-fault-persists' for row in failures)
    assert any(row['id']=='duplicate-packet' for row in failures)


def test_matching_four_child_integration_runs_receipt_bound_executables_and_is_admitted_automatically(tmp_path,monkeypatch):
    monkeypatch.setattr(capabilities,'registered',lambda *_:True)
    store=service.Store(tmp_path);baseline='a'*64;deps=real_children(store,baseline)
    value=protocol_receiver.seeds()[0]
    result=worker.evaluate(dict(task=value,key=tasks.identity(value,baseline)),tmp_path/'receiver-evaluate')
    receiver=complete(store,value,baseline,result)
    deps.append(receiver)
    # Retain the actual generated executable bytes, just as production receipts do.
    import shutil
    for child,source in [(deps[2],tmp_path/'evaluate-2/generated-controller.py'),(receiver,tmp_path/'receiver-evaluate/generated-receiver.py')]:
        folder=Path(child['folder']);(folder/'output').mkdir()
        destination=folder/'output'/source.name;shutil.copyfile(source,destination)
        receipt=core.read(folder/'receipt.json');receipt['files_sha256']['output/'+source.name]=core.sha(destination)
        (folder/'receipt.json').write_text(json.dumps(receipt))
        child['receipt_sha256']=core.sha(folder/'receipt.json')
        with store.db:store.db.execute('UPDATE jobs SET receipt_sha=? WHERE key=?',(child['receipt_sha256'],child['key']))
    for child in deps:
        with ledger.transaction(store.db):research.observe(store,child['key'])
    assert planning.integration_frontier(store,baseline)>=2
    row=store.db.execute("SELECT * FROM jobs WHERE json_extract(task,'$.kind')='integration-protocol'").fetchone()
    assert row
    result=worker.evaluate(dict(task=json.loads(row['task']),key=row['key'],baseline_sha256=baseline,
        dependencies=deps,evidence_workspace=str(tmp_path)),tmp_path/'composed')
    assert result['study_pass'] and result['protocol_link']['cases']>1000
    assert len(result['protocol_link']['executable_children'])==2
    assert all(result[key] is False for key in core.FLAGS)
    # Correspondence includes the linked code: changing it invalidates the receipt.
    target=Path(receiver['folder'])/'output/generated-receiver.py';target.write_text('changed')
    with pytest.raises(ValueError,match='child artifact changed'):
        worker.integration(dict(baseline_sha256=baseline,dependencies=deps))
