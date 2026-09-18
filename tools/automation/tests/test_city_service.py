import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('city_service',ROOT/'tools/automation/validate-city-service.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)


@pytest.mark.parametrize('failure',[None,'software','short','missing-line','degraded-line'])
def test_qualification_preserves_software_checks_and_adds_line_gates(failure):
    design={'lines':[{'name':'a','length_m':10000}]}
    scenario={'lines':[{'id':'a','name':'A'}], 'consist':{'passenger_capacity':360},
        'fleets':[{'line':'a','schedule':[{'from':'07:00','to':'09:00','headway_min':6}]}]}
    report=dict(passed=failure!='software',model=dict(minimum_service_completion_ratio=.9,service_completion_numerical_tolerance=.002),
        runs=[dict(duration_s=60 if failure=='short' else 90000,per_line_km=[] if failure=='missing-line' else [['A',400]])],
        resilience_required=True,resilience_passed=True,
        resilience_cases=[dict(passed=True,per_line_km=[['A',300 if failure=='degraded-line' else 400]],minimum_service_completion_ratio=.9)])
    result=s.qualify(report,design,scenario)
    assert result['passed'] is (failure is None)
    assert not result['operating_release'] and not result['passenger_capacity']['accepted']
    if failure=='degraded-line':
        assert result['aggregate_software_passed'] and not result['resilience_passed']
