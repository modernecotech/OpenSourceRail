from copy import deepcopy
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
