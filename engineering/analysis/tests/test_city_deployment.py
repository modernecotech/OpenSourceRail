"""Deployment status must follow evidence, including stale replay and nodata limits."""
import json
from engineering.analysis import city_deployment as deployment


def setup_city(tmp_path):
    (tmp_path/'design.toml').write_text('[city]\nslug="test-city"\n')
    return tmp_path


def put(city, relative, value):
    p=city/'engineering'/relative;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value))


def statuses(report):return {g['id']:g['status'] for g in report['gates']}


def test_desktop_soils_and_timing_do_not_release_a_city(tmp_path):
    city=setup_city(tmp_path)
    put(city,'soil/summary.json',{'desktop_screen_generated':True,'missing_profile_count':0})
    put(city,'simulation/operations-crosscheck.json',{'automatic_crosscheck_passed':True,'full_service_evidence_current':False})
    report=deployment.generate(city)
    state=statuses(report)
    assert state['soil-desktop-inputs']=='closed'
    assert state['model-timing-comparison']=='closed'
    assert state['full-service-validation']=='open'
    assert state['drainage-ground']=='open'
    assert not report['deployment_release_ready']


def test_accepted_local_ground_evidence_can_resolve_regional_nodata(tmp_path):
    city=setup_city(tmp_path)
    put(city,'soil/summary.json',{'desktop_screen_generated':True,'missing_profile_count':2})
    assert statuses(deployment.generate(city))['soil-coverage']=='open'
    put(city,'survey/drainage-ground-readiness.json',{'authority_accepted':True})
    assert statuses(deployment.generate(city))['soil-coverage']=='closed'


def test_current_but_failed_replay_does_not_close_service_gate(tmp_path):
    city=setup_city(tmp_path)
    put(city,'simulation/operations-crosscheck.json',{'full_service_evidence_current':True,'full_service_evidence_passed':False})
    assert statuses(deployment.generate(city))['full-service-validation']=='open'
