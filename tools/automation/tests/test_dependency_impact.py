import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('dependency_impact',ROOT/'tools/automation/dependency-impact.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)


def test_changed_shared_source_identifies_owner_without_modifying_evidence(tmp_path):
    source=tmp_path/'shared.py';source.write_text('old')
    artifact=next(iter(m.OWNERS));path=tmp_path/artifact;path.parent.mkdir(parents=True);record=dict(source_sha256={'shared.py':hashlib.sha256(source.read_bytes()).hexdigest()})
    path.write_text(json.dumps(record));before=path.read_bytes()
    assert m.impact([artifact],tmp_path)['invalidated']==[]
    source.write_text('new');result=m.impact([artifact],tmp_path)
    assert result['current_regeneration_required']==[artifact]
    assert result['invalidated'][0]['regenerate_command']
    assert path.read_bytes()==before and not result['source_hashes_rewritten']


def test_nested_maps_and_missing_dependencies_are_reported(tmp_path):
    p=tmp_path/'old.json';p.write_text(json.dumps(dict(review=dict(sources_sha256={'missing.py':'a'*64}))))
    result=m.impact(['old.json'],tmp_path)
    assert result['invalidated'][0]['state']=='scope-review-required'
    assert result['invalidated'][0]['changed_sources'][0]['current_sha256'] is None


def test_current_publication_detects_changed_output_locks_without_rewriting(tmp_path):
    artifact='cities/catalogue/west-asia/Iraq/Baghdad/publication-manifest.json'
    source=tmp_path/'coupled/manifest.json';source.parent.mkdir();source.write_text('old')
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(sources_sha256={},
        outputs_sha256={'coupled/manifest.json':hashlib.sha256(source.read_bytes()).hexdigest()},
        # Context-free body hashes intentionally differ from full file bytes.
        reference_bodies_sha256={'coupled/manifest.json':'a'*64})))
    before=path.read_bytes()
    assert m.impact([artifact],tmp_path)['invalidated']==[]
    source.write_text('new')
    report=m.impact([artifact],tmp_path)
    assert report['current_regeneration_required']==[artifact]
    assert report['invalidated'][0]['changed_sources'][0]['source']=='coupled/manifest.json'
    assert report['invalidated'][0]['regenerate_command']==[
        'tools/automation/osr-python','tools/automation/publish-city-summary.py']
    assert path.read_bytes()==before


@pytest.mark.parametrize('defect',['changed','missing'])
def test_plural_operations_source_hashes_reopen_current_review_without_retagging(tmp_path,defect):
    artifact='engineering/operations/pilot-review.json'
    source=tmp_path/'tools/automation/workbench-server.py';source.parent.mkdir(parents=True)
    source.write_bytes(b'original workbench producer')
    relative=source.relative_to(tmp_path).as_posix()
    original_digest=hashlib.sha256(source.read_bytes()).hexdigest()
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(source_sha256s={relative:original_digest},
                                   passed=True,movement_authority=False)))
    before=path.read_bytes()
    assert m.impact([artifact],tmp_path)['invalidated']==[]
    if defect=='changed':source.write_bytes(b'changed workbench producer')
    else:source.unlink()
    result=m.impact([artifact],tmp_path)
    assert result['current_regeneration_required']==[artifact]
    row=result['invalidated'][0]
    assert row['state']=='stale-current'
    assert row['regenerate_command']==[
        'tools/automation/osr-python','tools/automation/operations-pilot.py','--review']
    assert row['changed_sources']==[dict(source=relative,recorded_sha256=original_digest,
        current_sha256=hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None)]
    assert path.read_bytes()==before
    assert not result['acceptance_changed'] and not result['source_hashes_rewritten']


def test_tracked_operations_pilot_review_is_current():
    completed=subprocess.run([sys.executable,str(ROOT/'tools/automation/operations-pilot.py'),'--check'],
                             cwd=ROOT,capture_output=True,text=True,check=False)
    assert completed.returncode==0,completed.stdout+completed.stderr


@pytest.mark.parametrize('key',['dependency_hashes','evidence_hashes','input_hashes'])
@pytest.mark.parametrize('defect',['changed','missing'])
def test_digital_owner_input_maps_reopen_on_actual_root_input_changes(tmp_path,key,defect):
    artifact='docs/certification/digital-assurance-report.json'
    source=tmp_path/'docs/certification/software-soak-report.md';source.parent.mkdir(parents=True)
    source.write_bytes(b'original source evidence')
    relative=source.relative_to(tmp_path).as_posix()
    original_digest=hashlib.sha256(source.read_bytes()).hexdigest()
    path=tmp_path/artifact
    path.write_text(json.dumps(dict(schema='osr-digital-standards-thread/2',
        nested=[{key:{relative:original_digest}}],conformity_state='not-assessed')))
    before=path.read_bytes()
    assert m.impact([artifact],tmp_path)['invalidated']==[]
    if defect=='changed':source.write_bytes(b'changed source evidence')
    else:source.unlink()
    report=m.impact([artifact],tmp_path)
    assert report['current_regeneration_required']==[artifact]
    row=report['invalidated'][0]
    assert row['regenerate_command']==['python3','tools/automation/digital-assurance.py']
    assert row['changed_sources']==[dict(source=relative,recorded_sha256=original_digest,
        current_sha256=hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None)]
    assert path.read_bytes()==before
    assert not report['acceptance_changed'] and not report['source_hashes_rewritten']


@pytest.mark.parametrize('artifact,schema',[
    ('elsewhere/retained.json','osr-digital-standards-thread/2'),
    ('docs/certification/digital-assurance-report.json','some-other-report/1'),
])
def test_digital_input_key_meaning_requires_exact_owner_and_schema(tmp_path,artifact,schema):
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(schema=schema,dependency_hashes={'relative/input.json':'a'*64},
        evidence_hashes={'relative/evidence.json':'b'*64},input_hashes={'relative/model.json':'c'*64})))
    assert m.impact([artifact],tmp_path)['invalidated']==[]


def test_digital_owner_does_not_treat_output_or_context_free_body_hashes_as_root_inputs(tmp_path):
    artifact='docs/certification/digital-assurance-report.json'
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(schema='osr-digital-standards-thread/2',
        output_sha256={'cad/generated.step':'a'*64},outputs_sha256={'cad/generated.step':'b'*64},
        files_sha256={'artifact-relative.json':'c'*64},reference_bodies_sha256={'context.json':'d'*64})))
    assert m.impact([artifact],tmp_path)['invalidated']==[]


def test_tracked_digital_report_declared_root_inputs_are_current():
    artifact='docs/certification/digital-assurance-report.json'
    record=json.loads((ROOT/artifact).read_text())
    schema,keys=m.OWNER_INPUT_MAPS[artifact]
    assert record['schema']==schema
    inputs=set(m.dependency_maps(record,extra_keys=keys))
    assert ('docs/certification/software-soak-report.md',
            hashlib.sha256((ROOT/'docs/certification/software-soak-report.md').read_bytes()).hexdigest()) in inputs
    assert inputs
    for source,expected in inputs:
        path=(ROOT/source).resolve()
        assert path.is_relative_to(ROOT.resolve()),source
        assert path.is_file(),source
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,source
    assert m.impact([artifact],ROOT)['invalidated']==[]


def test_unfingerprinted_soak_has_real_native_owner_without_claiming_hash_freshness(tmp_path):
    artifact='docs/certification/software-soak-report.json'
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(schema='osr-software-soak/1',passed=True,profiles=[])))
    assert m.OWNERS[artifact]==['cargo','run','--quiet','--release','-p','osr-sim','--bin','osr-soak-evidence']
    # A hash scan cannot validate numerical evidence without declared source hashes.
    assert list(m.dependency_maps(json.loads(path.read_text())))==[]


@pytest.mark.parametrize('field,relative',[
    ('inventory_hashes','design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json'),
    ('evidence_hashes','docs/rfcs/0023-door-system-reference-design.md'),
    ('source_sha256','lib/templates/component-rfc-packages.toml'),
])
@pytest.mark.parametrize('defect',['changed','missing'])
def test_rfc_owner_proven_input_semantics_detect_actual_input_changes(tmp_path,field,relative,defect):
    artifact='docs/component-rfc-readiness.json'
    source=tmp_path/relative;source.parent.mkdir(parents=True);source.write_bytes(b'original input')
    expected=hashlib.sha256(source.read_bytes()).hexdigest()
    record={'schema':'osr-component-rfc-packages/1',field:expected if field=='source_sha256' else {relative:expected}}
    path=tmp_path/artifact;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(record))
    before=path.read_bytes()
    assert m.impact([artifact],tmp_path)['invalidated']==[]
    if defect=='changed':source.write_bytes(b'changed input')
    else:source.unlink()
    result=m.impact([artifact],tmp_path)
    assert result['current_regeneration_required']==[artifact]
    assert result['invalidated'][0]['changed_sources'][0]['source']==relative
    assert result['invalidated'][0]['regenerate_command']==[
        'tools/automation/osr-python','tools/automation/component_rfc_readiness.py']
    assert path.read_bytes()==before and not result['source_hashes_rewritten']


@pytest.mark.parametrize('artifact,schema',[
    ('docs/component-rfc-readiness.json','unrelated-schema/1'),
    ('elsewhere/report.json','osr-component-rfc-packages/1'),
    ('docs/operating/readiness.json','osr-operating-readiness/2'),
])
def test_scalar_digest_only_has_file_semantics_for_exact_proven_rfc_owner(tmp_path,artifact,schema):
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(schema=schema,source_sha256='a'*64,
        inventory_hashes={'relative/output.json':'b'*64},evidence_hashes={'relative/evidence.json':'c'*64})))
    assert m.impact([artifact],tmp_path)['invalidated']==[]


def test_tracked_rfc_report_declared_root_inputs_are_current():
    artifact='docs/component-rfc-readiness.json'
    record=json.loads((ROOT/artifact).read_text())
    schema,keys=m.OWNER_INPUT_MAPS[artifact]
    assert record['schema']==schema
    inputs=set(m.dependency_maps(record,extra_keys=keys))
    scalar_schema,scalars=m.OWNER_SCALAR_INPUTS[artifact]
    assert scalar_schema==schema
    inputs.update((source,record[key]) for key,source in scalars.items())
    assert inputs
    for source,expected in inputs:
        path=(ROOT/source).resolve()
        assert path.is_relative_to(ROOT.resolve()),source
        assert path.is_file(),source
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,source
    assert m.impact([artifact],ROOT)['invalidated']==[]


@pytest.mark.parametrize('artifact,schema',[
    ('docs/certification/software-soak-report.json','osr-software-soak/1'),
    ('docs/operating/readiness.json','osr-operating-readiness/2'),
])
def test_hash_scan_explicitly_requires_actual_unfingerprinted_or_aggregate_owner_check(tmp_path,artifact,schema):
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(schema=schema,passed=True,source_sha256='a'*64)))
    before=path.read_bytes()
    report=m.impact([artifact],tmp_path)
    assert report['current_regeneration_required']==[]
    assert report['hash_scan_only'] and report['canonical_owner_checks_executed'] is False
    check=report['canonical_owner_checks_required']
    assert len(check)==1 and check[0]['artifact']==artifact
    assert check[0]['command']==m.OWNER_CHECK_REQUIREMENTS[artifact]['command']
    assert check[0]['command'][-1]=='--check' and check[0]['reason']
    assert check[0]['executed'] is False and check[0]['freshness']=='not-assessed-by-hash-scan'
    assert path.read_bytes()==before
    path.write_text(json.dumps(dict(schema='unrelated-schema/1',source_sha256='a'*64)))
    assert m.impact([artifact],tmp_path)['canonical_owner_checks_required']==[]


def test_owner_check_requirement_is_not_inferred_for_an_unrelated_path(tmp_path):
    path=tmp_path/'elsewhere.json'
    path.write_text(json.dumps(dict(schema='osr-software-soak/1',passed=True)))
    assert m.impact(['elsewhere.json'],tmp_path)['canonical_owner_checks_required']==[]



def test_cli_prints_owner_check_limits_even_when_declared_file_hashes_are_current(tmp_path,monkeypatch,capsys):
    artifact='docs/certification/software-soak-report.json'
    path=tmp_path/artifact;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(schema='osr-software-soak/1',passed=True)))
    report=m.impact([artifact],tmp_path)
    monkeypatch.setattr(m,'impact',lambda:report)
    monkeypatch.setattr(sys,'argv',['dependency-impact.py','--check-current'])
    m.main()
    summary=json.loads(capsys.readouterr().out)
    assert summary['current_regeneration_required']==[]
    assert summary['canonical_owner_checks_required']==report['canonical_owner_checks_required']
    assert summary['hash_scan_only'] is True and summary['canonical_owner_checks_executed'] is False
