"""Authenticated synthetic topology projections; no engineering jobs are run."""
from copy import deepcopy
from hashlib import sha256
import json
import subprocess
import sys
from types import SimpleNamespace

import pytest

from engineering.development_baseline import portfolio_view as view
from engineering.station_rail.common import encoded, identity

ELIGIBLE='a'*64
REJECTED='b'*64
SCOPES=('rolling-stock','guideway','stations-power','factory-tooling','construction',
    'land-utilities-depot','fleet','energy','operations','maintenance','renewals','recovery','reliability','disposal')


def seal(value,key):
    value[key]=identity({k:v for k,v in value.items() if k!=key})
    return value


def synthetic_baseline():
    return dict(selection_id='1'*64,vehicle=dict(candidate_id='2'*64,evaluation_id='3'*64))


def topology_record(baseline=None):
    """Small fixture follows the published schema; all prices are synthetic IQD."""
    baseline=synthetic_baseline() if baseline is None else baseline
    production=dict(production_shifts_per_day=2,civil_shifts_per_day=2,
        operations_shifts_per_day_cases=[2,2,3],precedence_and_resource_conflicts_resolved=False)
    whole=dict(evaluation_id='c'*64,comparison_to_corrected_canonical_baseline={},cases={
        mass:dict(factory_gate_cost_iqd=[1000.,2000.,4000.],delivered_cost_iqd=[1100.,2200.,4400.],
            model_based_installed_CAPEX_iqd=[3000.,6000.,12000.],
            model_based_whole_life_NPV_iqd=[10000.,20000.,40000.],
            scope_totals_iqd={scope:[100.,200.,400.] for scope in SCOPES},production_plan=deepcopy(production))
        for mass in ('low','base','high')})
    eligible=dict(candidate_id=ELIGIBLE,evaluation_id='4'*64,quantity_evaluation_id='5'*64,
        composition_candidate_id='6'*64,binary_replay_admitted_to_archive=True,
        binary_replay='completed',refinement_status='two-mesh-comparison-within-declared-target',
        nominal_stock_mass_kg=23000.,maximum_crowd_high_accounted_mass_model_displacement_m=.004,
        span_installed_cost_iqd=dict(low=10.,base=20.,high=40.),factory_person_hours=dict(low=2.,base=4.,high=8.),
        trial=dict(kind='optimized-density',initial_field='uniform',volume_fraction=.35),
        system_cost=whole,**view.FLAGS)
    rejected=deepcopy(eligible)
    rejected.update(candidate_id=REJECTED,evaluation_id='7'*64,quantity_evaluation_id='8'*64,
        composition_candidate_id='9'*64,binary_replay_admitted_to_archive=False,binary_replay='not-run',
        refinement_status='mesh-unresolved',maximum_crowd_high_accounted_mass_model_displacement_m=None,
        system_cost=None)
    duplicate=deepcopy(eligible)
    duplicate.update(evaluation_id='d'*64,trial=dict(kind='optimized-density',initial_field='longitudinal-wave',volume_fraction=.50))
    failed=dict(candidate_id=None,execution='wall-timeout',**view.FLAGS)
    descriptor=dict(material='steel-concrete',manufacture='cut-plate-and-precast-deck',solid_fraction_band=1)
    archive=seal(dict(schema='osr-quality-diversity-archive/1',
        objectives=['nominal_stock_mass_kg','base_whole_life_npv_iqd','crowd_high_model_displacement_m'],
        descriptor_keys=list(descriptor),cell_count=1,cells=[dict(cell_id=identity(descriptor),descriptor=descriptor,
            candidate_ids=[ELIGIBLE],retained_pareto_candidate_ids=[ELIGIBLE],excluded=[])],
        retained_candidate_ids=[ELIGIBLE],cross_cell_partial_quantity_pareto_candidate_ids=[ELIGIBLE],
        global_optimum_proven=False,integrated_selection=None),'archive_id')
    return seal(dict(schema='osr-civil-topology-portfolio/1',
        selection_id=baseline['selection_id'],selected_vehicle_candidate_id=baseline['vehicle']['candidate_id'],
        vehicle_evaluation_id=baseline['vehicle']['evaluation_id'],load_context_id='e'*64,baseline_id='f'*64,
        unique_realized_candidate_count=2,numerically_replayed_candidate_count=1,
        attempts=[eligible,rejected,duplicate,failed],archive=archive,
        ranking_scope='Next-experiment plane-model comparison; no integrated baseline ranking',
        physical_qualification_pending=['buckling and fatigue','bearing contact and unequal web sharing'],
        integrated_selection=None,**view.FLAGS),'portfolio_id')


def test_realizations_deduplicate_without_promoting_rejected_or_unknown_evidence():
    baseline=synthetic_baseline();record=topology_record(baseline);before=deepcopy(record)
    result=view._topology(record,baseline);rows={row['candidate_id']:row for row in result['rows']}
    assert record==before
    assert set(rows)=={ELIGIBLE,REJECTED}
    assert rows[ELIGIBLE]['mechanics_evaluation_id']=='d'*64
    assert rows[ELIGIBLE]['mechanics_retained'] is True
    assert rows[REJECTED]['mechanics_retained'] is None
    assert rows[REJECTED]['model_deflection_upper_m'] is None
    assert rows[REJECTED]['assumptions']['whole_system_cost'] is None
    assert result['mechanics_retained_count']==1
    assert result['quantity_archive_id'] is result['quantity_retained_count'] is None
    assert all(row['quantity_retained'] is None and row['quantity_dominated_by']==[] for row in rows.values())
    assert all(row['complete_installed_mass_kg'] is None and row['next_tasks'] for row in rows.values())
    assert all(row[key] is False for row in rows.values() for key in view.FLAGS)
    assert result['assumptions']['failed_attempt_count']==1


def test_span_prices_remain_separate_from_full_corridor_assumptions_and_shifts():
    record=topology_record();result=view._topology(record,synthetic_baseline())
    row=next(row for row in result['rows'] if row['candidate_id']==ELIGIBLE)
    assert row['cost_iqd']==dict(low=10.,base=20.,high=40.)
    assert row['process_hours']==dict(low=2.,base=4.,high=8.)
    whole=row['assumptions']['whole_system_cost']['cases']['base']
    assert whole['model_based_whole_life_NPV_iqd']==[10000.,20000.,40000.]
    assert set(whole['scope_totals_iqd'])==set(SCOPES)
    assert whole['production_plan']['production_shifts_per_day']==2
    assert whole['production_plan']['civil_shifts_per_day']==2
    assert whole['production_plan']['operations_shifts_per_day_cases']==[2,2,3]
    assert 'exclude rails, foundations' in row['assumptions']['scope']
    assert 'Representative' in row['assumptions']['deflection_scope']
    assert 'no integrated baseline ranking' in result['assumptions']['ranking_scope']


@pytest.mark.parametrize('field',('selected_vehicle_candidate_id','vehicle_evaluation_id','selection_id'))
def test_resealed_candidate_load_evaluation_and_selection_mismatch_is_rejected(field):
    baseline=synthetic_baseline();record=topology_record(baseline);record[field]='0'*64
    seal(record,'portfolio_id')
    with pytest.raises(view.CurrentUnavailable,match='selected vehicle/load context'):
        view._topology(record,baseline)


@pytest.mark.parametrize('target',('record','eligible','rejected'))
def test_resealed_acceptance_promotion_is_rejected_at_each_visible_level(target):
    record=topology_record()
    destination=record if target=='record' else record['attempts'][0 if target=='eligible' else 1]
    destination['physical_accepted']=True;seal(record,'portfolio_id')
    with pytest.raises(view.CurrentUnavailable,match='acceptance or selection'):
        view._topology(record,synthetic_baseline())


@pytest.mark.parametrize('mutation',('missing-member','rejected-admitted','foreign-member','wrong-count','archive-selection'))
def test_resealed_archive_coverage_and_selection_fail_closed(mutation):
    record=topology_record();archive=record['archive']
    if mutation=='missing-member':archive['cells'][0]['candidate_ids']=[]
    elif mutation=='rejected-admitted':record['attempts'][1]['binary_replay_admitted_to_archive']=True
    elif mutation=='foreign-member':archive['cells'][0]['candidate_ids'].append('0'*64)
    elif mutation=='wrong-count':record['unique_realized_candidate_count']+=1
    else:archive['integrated_selection']=ELIGIBLE
    seal(archive,'archive_id');seal(record,'portfolio_id')
    with pytest.raises(view.CurrentUnavailable):view._topology(record,synthetic_baseline())


def test_source_binding_checks_exact_fixture_bytes_and_record_seal(tmp_path):
    relative='docs/design-engine/civil-topology/result.json';target=tmp_path/relative
    target.parent.mkdir(parents=True);record=topology_record();raw=encoded(record);target.write_bytes(raw)
    publication=dict(source_sha256={relative:sha256(raw).hexdigest()})
    assert view._read(tmp_path,publication,'civil-topology','result.json',record['schema'],'portfolio_id')==record
    target.write_bytes(raw+b' ')
    with pytest.raises(view.CurrentUnavailable,match='current source binding'):
        view._read(tmp_path,publication,'civil-topology','result.json',record['schema'],'portfolio_id')
    record['ranking_scope']='mutated without resealing';raw=encoded(record);target.write_bytes(raw)
    publication['source_sha256'][relative]=sha256(raw).hexdigest()
    with pytest.raises(view.CurrentUnavailable,match='record identity'):
        view._read(tmp_path,publication,'civil-topology','result.json',record['schema'],'portfolio_id')


def test_projection_never_spawns_numerical_work_and_returns_independent_records(monkeypatch):
    from engineering import design_search
    def forbidden(*_args,**_kwargs):pytest.fail('Read-only portfolio cannot dispatch work')
    monkeypatch.setattr(subprocess,'run',forbidden);monkeypatch.setattr(subprocess,'Popen',forbidden)
    for name,methods in {'civil_topology':('evaluate_trial','run','plan'),
            'topology_optimisation':('mesh','solve','solve_binary','optimise'),
            'topology_system_cost':('make_baseline','compose','compare')}.items():
        stub=SimpleNamespace(**dict.fromkeys(methods,forbidden))
        monkeypatch.setitem(sys.modules,'engineering.design_search.'+name,stub)
        monkeypatch.setattr(design_search,name,stub,raising=False)
    record=topology_record();result=view._topology(record,synthetic_baseline())
    selected=next(row for row in result['rows'] if row['candidate_id']==ELIGIBLE)
    selected['cost_iqd']['base']=0
    selected['assumptions']['whole_system_cost']['cases']['base']['model_based_whole_life_NPV_iqd'][1]=0
    assert record['attempts'][2]['span_installed_cost_iqd']['base']==20.
    assert record['attempts'][2]['system_cost']['cases']['base']['model_based_whole_life_NPV_iqd'][1]==20000.
