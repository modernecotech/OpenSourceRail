"""Contract/publication regressions. Stubbed forces test bookkeeping only."""
from copy import deepcopy
import json

import pytest

from engineering.design_search.contracts import identity, make_evaluation_request, mass_properties
from engineering.passive_suspension import campaign, geometry, publication


def test_physical_grade_and_coil_connection_hypotheses_are_separate():
    value=geometry.candidate('B')
    first=campaign.common_candidate(value,'requirements')
    different=deepcopy(value)
    different['materials']['ferrite']['id']='another-physical-grade'
    different['physical_geometry_sha256']=identity(geometry.physical_definition(different))
    # geometry uses its own canonical byte convention including trailing newline.
    different.pop('geometry_sha256')
    different['geometry_sha256']=identity(different)
    other=campaign.common_candidate(different,'requirements')
    assert first['candidate_id']!=other['candidate_id']
    a=make_evaluation_request(first,evaluator_id='field',evaluator_sources={'field.py':'a'*64},hypothesis={'steel_mu':1000})
    b=make_evaluation_request(first,evaluator_id='field',evaluator_sources={'field.py':'a'*64},hypothesis={'steel_mu':500})
    assert a['candidate_id']==b['candidate_id'] and a['evaluation_id']!=b['evaluation_id']


def test_repeated_stock_is_not_complete_installed_mass_or_distribution():
    value=geometry.candidate('B')
    candidate=campaign.common_candidate(value,'requirements')
    mass=mass_properties(candidate)
    assert mass['known_mass_subtotal_kg']==pytest.approx(value['stock']['train_known_mass_kg_per_car'])
    assert mass['total_mass_kg'] is None and mass['cg_m'] is None
    assert mass_properties(candidate,'guideway-per-span')['known_mass_subtotal_kg']==pytest.approx(value['stock']['guideway_facing_kg_per_beam_span'])
    assert all(q['permanent_magnets']=='train-only' for q in candidate['interfaces'] if q['id']=='ordinary-guideway')


@pytest.fixture
def bookkeeping_run(tmp_path,monkeypatch):
    calls=[]
    def solve(value,**kwargs):
        calls.append((value['label'],kwargs))
        return dict(interpolation_usable=True,numerical_status='converged',F_z_N=1000.,F_y_N=0.,
                    scope='BOOKKEEPING TEST FIXTURE; NOT AN ENGINEERING RESULT')
    monkeypatch.setattr(campaign.fields,'solve',solve)
    monkeypatch.setattr(campaign.fields,'benchmarks',lambda:dict(source_sha256=campaign.fields.sources(),
        numerical_method_benchmark_pass=True,scope='BOOKKEEPING TEST FIXTURE; NOT METHOD VALIDATION'))
    monkeypatch.setattr(campaign.geometry,'bounded_variants',lambda:[geometry.candidate('A')|{'sample_id':'A/test'}])
    out=tmp_path/'run'
    result=campaign.run(out,run_map=False)
    return out,result,calls


def test_exact_restart_reuses_results_and_integrated_gate_stays_closed(bookkeeping_run):
    out,first,calls=bookkeeping_run
    count=len(calls)
    assert count==8
    assert campaign.run(out,run_map=False)==first
    assert len(calls)==count
    assert first['integrated_selection']['selected_candidate_id'] is None
    assert campaign.verify(out)['verified']


def test_missing_retained_evaluation_is_rejected(bookkeeping_run):
    out,result,_=bookkeeping_run
    (out/'registry/evaluation'/(result['evaluation_ids'][0]+'.json')).unlink()
    with pytest.raises(FileNotFoundError):campaign.verify(out)


def test_rehashed_summary_cannot_change_selection(bookkeeping_run):
    out,summary,_=bookkeeping_run
    summary['next_experiment']['selected_candidate_id']='f'*64
    summary['result_sha256']=identity({k:v for k,v in summary.items() if k!='result_sha256'})
    (out/'summary.json').write_text(json.dumps(summary))
    with pytest.raises(ValueError,match='Selection'):campaign.verify(out)


def test_rehashed_summary_cannot_promote_physical_acceptance(bookkeeping_run):
    out,summary,_=bookkeeping_run
    summary['physical_accepted']=True
    summary['result_sha256']=identity({k:v for k,v in summary.items() if k!='result_sha256'})
    (out/'summary.json').write_text(json.dumps(summary))
    with pytest.raises(ValueError,match='acceptance'):campaign.verify(out)


def test_nonnative_publication_has_no_fabricated_cad_and_rejects_bom_tampering(bookkeeping_run,tmp_path):
    out,result,_=bookkeeping_run
    target=tmp_path/'publication'
    assert publication.publish(out,target,export_native=False)['verified']
    assert not (target/'native/model.step').exists()
    assert json.loads((target/'native-execution.json').read_text())['execution_status']=='not-run'
    (target/'bom.json').write_text('{}')
    with pytest.raises(ValueError,match='artifact differs'):publication.verify(target)


def test_replacement_mass_sources_include_each_actual_canonical_input():
    sources=campaign.sources()
    assert set(campaign.canonical.sources()).issubset(sources)
    assert 'engineering/ferrite_maglev/data/candidate-parent-94ad.json' in sources
