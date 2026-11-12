"""Comparison contracts use sealed fixtures; root integration runs real studies."""
from copy import deepcopy
from pathlib import Path

import pytest

from engineering.outline import corridor_revision as revision
from engineering.station_rail.common import identity


def seal(value, key='evaluation_id'):
    value[key] = identity({k: v for k, v in value.items() if k != key})
    return value


@pytest.fixture
def scenario():
    a, b = revision.RAW_STOP_IDS
    refs = dict(candidate_id='a' * 64, body_candidate_id='b' * 64,
                support_component_id='c' * 64, propulsion_component_id='d' * 64)
    raw = [dict(id=a, chainage_m=10., lon=.001, lat=0., dwell_s=35.),
           dict(id=b, chainage_m=90., lon=.009, lat=0., dwell_s=35.),
           dict(id='far', chainage_m=500., lon=.05, lat=0., dwell_s=35.)]
    operational = [dict(raw[0], id='complex-pair'), deepcopy(raw[-1])]
    seed = dict(city_slug='samawah', seed_id='1' * 64, selected_city_input_id='2' * 64,
                reference_candidate_ids=refs, source_sha256={'vehicle.py': '3' * 64})
    base = dict(city='samawah', selection_id='4' * 64, revision_sha256='5' * 64,
        source_outline_evaluation_id='6' * 64,
        lines=[dict(id='line-1', coordinates=[[0., 0.], [.05, 0.]], shape='radial',
                    design_speed_cap_m_s=20., stops=operational)],
        outline_context=dict(city_input_template=dict(lines=[dict(line_id='line-1', stops=raw, route_m=500.)]),
            baseline_line_services=[dict(line_id='line-1', operational_stops=operational,
                station_repair=dict(complexes=[dict(operational_stop_id='complex-pair', original_stop_ids=[a, b])]))]))
    detail=dict(planning_seed=seed, evaluation_id='6' * 64)
    proposal = revision._build_proposal(detail, base, 'Fixture planner', revision._LOADED_SHA)
    return proposal, base


def result(proposal, revised=False, *, candidate=None, headway=200., bad_cost=False,
           moved_route=False, aliases=True, source=None, accepted=False):
    refs = deepcopy(candidate or proposal['reference_candidate_ids'])
    source = source or {'vehicle.py': '3' * 64}
    pair = revision.RAW_STOP_IDS
    raw = ([dict(id=revision.NEW_STOP_ID, chainage_m=50., lon=.005, lat=0., dwell_s=35.)]
           if revised else [dict(id=pair[0], chainage_m=10., lon=.001, lat=0., dwell_s=35.),
                            dict(id=pair[1], chainage_m=90., lon=.009, lat=0., dwell_s=35.)])
    raw.append(dict(id='far', chainage_m=500., lon=.05, lat=0., dwell_s=35.))
    line = dict(line_id='line-1', stops=raw, coordinates=[[0., 0.], [.05 + (.001 if moved_route else 0.), 0.]],
                shape='radial', route_m=500., planning_access_aliases={k: revision.NEW_STOP_ID for k in pair} if aliases else {})
    geometry = seal(dict(schema='osr-city-outline-input/1', reference_candidate_ids=refs, lines=[line]), 'input_id')
    duty = dict(line_id='line-1', requirements=dict(headway_s=headway, peak_demand_pphpd=4000.),
        design=dict(speed_m_s=20.), propulsion_hypothesis=dict(kind='station-cable-capstan'),
        operational_stops=[dict(id='near'), dict(id='far')],
        service=dict(total_trainsets=8, active_trainsets=7, spare_trainsets=1,
                     one_way_s=99. if revised else 100., round_trip_s=250., planning_usable_capacity_pphpd=4200.))
    service = seal(dict(city_input_id=geometry['input_id'], line_services=[duty]))
    scopes = {k: dict(low=1., base=1., high=1.) for k in revision.SCOPES}
    if revised:scopes['stations-power'] = dict(low=2., base=2., high=2.)
    cap = 11. if revised else 10.; npv = 15. if revised else 14.
    cost = seal(dict(city_input_id=geometry['input_id'], scope_totals_usd=scopes,
        installed_capital_usd=dict(low=cap + int(bad_cost), base=cap + int(bad_cost), high=cap + int(bad_cost)),
        whole_life_npv_usd=dict(low=npv, base=npv, high=npv),
        civil=dict(quantities=dict(route_m=500., rail_m=2000., unknown_ground_m=None,
                                  quantity_id=('7' if revised else '8') * 64)),
        resources=dict(original_map_stop_records=len(raw), line_stop_records=2,
                       boarding_edges=4, total_trainsets=8, unknown_quantity=None),
        assumptions=dict(local_rates_verified=False, pricing_basis='fixture Class C transfer'),
        capital_lines=[dict(key='station', costs_usd=dict(low=cap, base=cap, high=cap))],
        lifecycle_lines=[dict(key='maintenance', costs_usd=dict(low=4., base=4., high=4.))]))
    city = seal(dict(reference_candidate_ids=refs, selection_id=proposal['selection_id'], input_id=geometry['input_id'],
        geometry_and_service=geometry, service_evaluation=service, cost=cost,
        research_configuration_id=('9' if revised else 'a') * 64,
        planning_revision_id=('b' if revised else 'c') * 64,
        qualification_requirements=['Survey and physical validation unresolved'],
        policy=dict(peak_demand_pphpd=4000., pricing_basis='project-make-buy'), **revision.FLAGS))
    delivery = seal(dict(city_input_id=city['input_id'], city_record_evaluation_id=city['evaluation_id'],
        cost_evaluation_id=cost['evaluation_id'], research_configuration_id=city['research_configuration_id']), 'plan_id')
    business = seal(dict(source_plan_id=delivery['plan_id']), 'draft_id')
    value = seal(dict(schema='osr-mapped-city-workflow/1', request=deepcopy(proposal['revised_request' if revised else 'baseline_request']),
        source_outline_evaluation_id=proposal['source_outline_evaluation_id'], planning_seed_id=proposal['seed_id'],
        city_outline=city, delivery_plan=delivery, business_drafts=business, source_sha256=source, **revision.FLAGS))
    if accepted:
        value['physical_accepted'] = True; seal(value)
    manifest = seal(dict(schema='osr-mapped-city-workflow-publication/1', evaluation_id=value['evaluation_id'],
        source_sha256=source, files_sha256={'result.json.gz': 'e' * 64}, **revision.FLAGS), 'manifest_id')
    return value, manifest


def test_proposal_uses_existing_raw_consolidation_edit_and_keeps_base_unchanged(scenario):
    proposed, base = scenario; original = deepcopy(base)
    assert proposed['baseline_request']['edit_bundle']['edits'] == []
    edit = proposed['revised_request']['edit_bundle']['edits'][0]
    assert edit['kind'] == 'replace-line-geometry'
    assert edit['coordinates'] == base['lines'][0]['coordinates']
    assert edit['shape'] == base['lines'][0]['shape']
    assert edit['stops'] == [dict(id=revision.NEW_STOP_ID, chainage_m=50., dwell_s=35.),
                            dict(id='far', chainage_m=500., dwell_s=35.)]
    assert all(set(s) == {'id', 'chainage_m', 'dwell_s'} for s in edit['stops'])
    assert proposed['edit']['separation_m'] == 80.
    assert proposed['published_context']['raw_marker_count'] == 3
    assert proposed['published_context']['operational_stop_count'] == 2
    assert base == original


def test_public_proposal_requires_its_loaded_source_bytes(tmp_path):
    path = tmp_path / revision.PRODUCER; path.parent.mkdir(parents=True)
    path.write_text('source changed')
    with pytest.raises(ValueError, match='helper changed'):
        revision.proposal(tmp_path)


def test_comparison_separates_raw_and_operational_counts_and_preserves_unknowns(scenario):
    p, _ = scenario; before, bm = result(p); after, am = result(p, True)
    report = revision.compare(p, before, after, bm, am)
    metrics = {m['key']: m for m in report['metrics']}
    assert metrics['raw_marker_count']['delta'] == -1
    assert metrics['operational_stop_count']['delta'] == 0
    assert metrics['route_m']['delta'] == 0
    assert metrics['installed_capital_usd']['delta'] == 1.
    assert len(report['cost_scopes']) == 14
    assert report['quantities']['civil.unknown_ground_m']['delta'] is None
    assert report['quantities']['resources.unknown_quantity']['after'] is None
    assert report['reuse']['vehicle_definition_unchanged'] is True
    assert report['reuse']['execution_cache_reuse_verified'] is False
    assert report['performance'] is None
    assert report['identities']['before']['reference_candidate_ids'] == report['identities']['after']['reference_candidate_ids']
    assert all(report[k] is False for k in revision.FLAGS)
    assert report['comparison_id'] == identity({k: v for k, v in report.items() if k != 'comparison_id'})


def test_resealed_mixed_candidate_is_rejected(scenario):
    p, _ = scenario; before, bm = result(p); other = dict(p['reference_candidate_ids'], body_candidate_id='f' * 64)
    after, am = result(p, True, candidate=other)
    with pytest.raises(ValueError, match='Mixed physical candidate'):
        revision.compare(p, before, after, bm, am)


def test_tampered_result_and_retargeted_request_are_rejected(scenario):
    p, _ = scenario; before, bm = result(p); after, am = result(p, True)
    after['city_outline']['cost']['installed_capital_usd']['base'] += 1
    with pytest.raises(ValueError, match='Sealed city workflow'):
        revision.compare(p, before, after, bm, am)
    after, am = result(p, True)
    after['request']['service']['operating_hours_per_day'] = 24.
    seal(after); am['evaluation_id'] = after['evaluation_id']; seal(am, 'manifest_id')
    with pytest.raises(ValueError, match='exact corridor request'):
        revision.compare(p, before, after, bm, am)


@pytest.mark.parametrize('override,match', [
    ({'moved_route': True}, 'preserve route geometry'),
    ({'aliases': False}, 'access aliases'),
    ({'headway': 180.}, 'fixed service assumption'),
    ({'bad_cost': True}, 'capital/lifecycle ledger'),
    ({'source': {'vehicle.py': 'f' * 64}}, 'different source epochs'),
    ({'accepted': True}, 'cannot grant'),
])
def test_incompatible_or_overstated_comparisons_fail(scenario, override, match):
    p, _ = scenario; before, bm = result(p); after, am = result(p, True, **override)
    with pytest.raises(ValueError, match=match):
        revision.compare(p, before, after, bm, am)


def test_numeric_delta_does_not_turn_missing_or_boolean_quantities_into_zero():
    assert revision._delta(None, 7.) is None
    assert revision._delta(True, 7.) is None
    assert revision._delta({'a': 2., 'unknown': None}, {'a': 5., 'unknown': None}) == {'a': 3., 'unknown': None}
    with pytest.raises(ValueError, match='Finite'):
        revision._delta(1., float('inf'))
