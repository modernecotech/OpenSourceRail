from hashlib import sha256
import io,tarfile
from pathlib import Path
import json,shutil
import pytest
from engineering.station_rail import ROOT
from engineering.design_search import design_grammar as grammar,grammar_coupling,failure_diagnosis,generative_campaign as campaign,generative_publication as publication


def test_generative_campaign_tracks_transitive_requirement_and_vehicle_sources():
    sources=campaign.sources()
    for path in ('engineering/design_search/requirement_policy.py',
                 'engineering/design_search/architecture_demand.py',
                 'engineering/design_search/structural_families.py',
                 'engineering/design_search/joining_catalogue.py',
                 'engineering/station_rail/vehicle.py',
                 'engineering/station_rail/braking.py',
                 'engineering/station_rail/civil.py',
                 'engineering/station_rail/common.py',
                 'engineering/station_rail/brief.toml',
                 'engineering/station_rail/electrical.py',
                 'engineering/station_rail/__init__.py',
                 'docs/design-engine/ferrite-maglev/comfort-design/design.json.gz',
                 'docs/design-engine/ferrite-maglev/comfort-design/manifest.json'):
        assert sources[path]==publication.digest(ROOT/path)


def test_generated_mass_propagates_to_native_load_and_required_motion_without_inventing_available_force():
    parent=grammar.build(grammar.parameters());child=grammar.rewrite(parent,'triangulate-underfloor',reason='Load-path redesign')
    a,b=grammar_coupling.evaluate(parent),grammar_coupling.evaluate(child)
    delta=child['known_structure_stock_kg']-parent['known_structure_stock_kg']
    assert b['accounted_tare_hypothesis_kg_per_car']-a['accounted_tare_hypothesis_kg_per_car']==pytest.approx(delta)
    load=-sum(n['force_N'][2] for n in child['structure']['loads'])/9.80665
    assert load==pytest.approx(b['normal_sprung_load_mass_kg'])
    assert b['candidate_id']==child['candidate_id'] and b['actual_motor_map'] is None
    assert b['force_motion_thermal_braking_journey_completed'] is False and b['whole_life_cost_USD'] is None
    assert a['required_motion']!=b['required_motion'] and b['complete_installed_mass_kg'] is None


def test_invalid_model_prompts_evaluator_work_without_provisional_body_rejection():
    c=grammar.build(grammar.parameters());d=failure_diagnosis.diagnose(c,native={'numerical_validity':'outside_linear_domain'})
    assert d['findings'][0]['kind']=='model-domain-or-numerical'
    assert any(a['operator'] is None and a['kind']=='evaluator-development' for a in d['actions'])
    assert not d['provisional_target_rejection'] and d['integrated_suitability']=='unknown'


def test_retained_generative_evidence_verifies_without_executing_native_tools():
    r=publication.verify()
    assert r['candidate_count']==8 and r['native_design_case_count']==2 and r['CAD_case_count']==6
    assert r['physical_accepted'] is False


def test_publication_refuses_tampered_summary(tmp_path):
    source=ROOT/publication.OUTPUT;out=tmp_path/'packet';shutil.copytree(source,out)
    p=out/'summary.json';s=json.loads(p.read_bytes());s['integrated_selection']='invented-winner';p.write_text(json.dumps(s))
    with pytest.raises(ValueError,match='payload changed'):publication.verify(output=out)


def test_current_publication_reuses_evidence_without_requiring_local_native_run_folders(monkeypatch):
    def refused(*args,**kwargs):raise AssertionError('Publishing current evidence must not execute or require new local solves')
    monkeypatch.setattr(publication,'read_campaign',refused)
    assert publication.build()['candidate_count']==8


def test_failed_method_archives_carry_forward_when_ignored_solver_files_are_absent(tmp_path):
    previous=tmp_path/'previous';previous.mkdir()
    out=tmp_path/'new';out.mkdir()
    source=b'pinned historical method source\n';source_id=sha256(source).hexdigest()
    source_artifact=f'historical-sources/{source_id}';(previous/source_artifact).parent.mkdir()
    (previous/source_artifact).write_bytes(source)
    source_epochs={source_id:dict(repository_path='engineering/design_search/grammar_structure.py',artifact=source_artifact)}
    (previous/'source-epochs.json').write_bytes(publication.encoded(source_epochs))
    rows=[]
    for i,name in enumerate(('axial-s1','axial-s2','tripod-s1','tripod-s2')):
        result=dict(source_sha256={'engineering/design_search/grammar_structure.py':source_id},execution='failed-method-epoch')
        result_raw=publication.encoded(result);result_hash=sha256(result_raw).hexdigest()
        omitted={'graph.frd':sha256(f'omitted-{i}'.encode()).hexdigest()}
        raw_manifest=dict(schema='fixture',source_sha256=result['source_sha256'],files_sha256={'result.json':result_hash,**omitted})
        raw_manifest['manifest_id']=publication.identity(raw_manifest)
        archive_index=dict(retained_sha256={'result.json':result_hash},omitted_sha256=omitted)
        buf=io.BytesIO()
        with tarfile.open(fileobj=buf,mode='w:gz') as tar:
            for filename,raw in [('result.json',result_raw),('manifest.json',publication.encoded(raw_manifest)),('archive-index.json',publication.encoded(archive_index))]:
                info=tarfile.TarInfo(filename);info.size=len(raw);info.mtime=0;tar.addfile(info,io.BytesIO(raw))
        archive_raw=buf.getvalue();archive_rel=f'native/{i}.tar.gz'
        (previous/archive_rel).parent.mkdir(exist_ok=True)
        (previous/archive_rel).write_bytes(archive_raw)
        rows.append(dict(name=f'fixtures-r1/{name}',kind='failed-method-epoch',archive=archive_rel,
            raw_manifest=raw_manifest,raw_result=result))
    index_raw=publication.encoded(rows);(previous/'native-index.json').write_bytes(index_raw)
    files={p.relative_to(previous).as_posix():publication.digest(p) for p in previous.rglob('*') if p.is_file()}
    manifest=dict(schema='fixture-publication',files_sha256=files)
    manifest['manifest_id']=publication.identity(manifest)
    (previous/'manifest.json').write_bytes(publication.encoded(manifest))
    copied,epochs=publication.carry_failed_method_epoch(previous,out,root=tmp_path)
    assert [row['name'] for row in copied]==[row['name'] for row in rows]
    for i,row in enumerate(rows):
        assert (out/copied[i]['archive']).read_bytes()==(previous/row['archive']).read_bytes()
        assert copied[i]['raw_manifest']==row['raw_manifest'] and copied[i]['raw_result']==row['raw_result']
    assert epochs==source_epochs
    assert sha256((out/source_artifact).read_bytes()).hexdigest()==source_id
