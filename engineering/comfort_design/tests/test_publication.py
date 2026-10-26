"""Cross-domain design, service and physical-release regression controls."""
from copy import deepcopy
import pytest
from engineering.comfort_design import ROOT
from engineering.comfort_design import publication as p


@pytest.fixture(scope='module')
def proposal():return p.assemble(ROOT)


def test_matched_vehicle_and_two_minute_capacity(proposal):
    car=proposal['vehicle'];ops=proposal['service'];s=p.summary(proposal)
    assert car['candidate_id']==ops['candidate_id']==proposal['interfaces']['candidate_id']
    assert s['capacity_pphpd']==6*46*3600/120==8280
    assert s['regular_service_average_wait_s']==60
    assert s['mass']['accounted_tare_kg_per_car']==pytest.approx(17356.683728076856)
    assert s['mass']['installed_tare_kg_per_car'] is None
    assert car['located_material_properties']['mass_kg'] < s['mass']['accounted_tare_kg_per_car']
    assert car['mass']['CG_m'] is None
    assert not proposal['complete_engineering_design']


def test_section_control_is_distinct_from_full_winding_lease(proposal):
    campaigns={(r['architecture'],r['delay_first_dwell_s']):r for r in proposal['service']['station_resource_campaign']}
    assert campaigns['section-addressed',15.]['screen']=='pass'
    assert campaigns['whole-zone-exclusive',15.]['screen']=='fail'
    assert campaigns['section-addressed',60.]['screen']=='fail'
    station=proposal['service']['selected_station']
    assert station['length_m']==450
    assert station['sections_per_direction']==36
    assert station['minimum_concurrent_train_phase_current_branches_per_direction']==2
    assert station['nominal_120_s_margin_s']==pytest.approx(35.242979451791015)


def test_real_coast_and_known_failed_hardware_cannot_become_qualified(proposal):
    profile=proposal['service']['selected_scenario']['profile']
    assert not profile['coast_powered'] and not profile['force_map_driven']
    assert profile['arrival_speed_before_braking_m_s'] < profile['peak_speed_m_s']
    assert profile['runtime_s']==pytest.approx(218.70656340727956)
    states={g.get('gate',g.get('name')):g['state'] for g in proposal['interfaces']['gates']}
    assert sum(v=='fail' for v in states.values())>=2
    assert not proposal['physical_accepted'] and not proposal['operating_release']
    assert proposal['native_evidence']['execution']=='not-run'


def test_mixed_service_configuration_rejected_before_publication(proposal,monkeypatch):
    wrong=deepcopy(proposal['service']);wrong['body_candidate_id']='f'*64
    monkeypatch.setattr(p.service,'evaluate',lambda *a,**kw:wrong)
    with pytest.raises(ValueError,match='mixed or missing body_candidate_id'):p.assemble(ROOT)


def test_dossier_does_not_hide_failed_controls_or_city_cost_scope(proposal):
    text=p.readme(proposal)
    assert '1206' in text.replace(',','') and '120' in text
    assert 'capture' in text.lower()
    assert '37.4' in text
    assert '8,280' in text and '14,400' in text
    assert 'operating' in text and 'unknown' in text
