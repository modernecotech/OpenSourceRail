"""Paid journey counts and revenue cannot be manufactured by transfers."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from baghdad_demand_bridge import account_journeys


def network():
    return dict(lines=[dict(name='A'),dict(name='B'),dict(name='C')],
        interchanges=[dict(lines=['A','B'])],stations=[])


def test_integrated_journey_has_two_boardings_and_one_fare():
    cohort=[dict(journey_id='observed-od-1',line_path=['A','B'],annual_journeys=100,fare_iqd=1500)]
    result=account_journeys(network(),cohort)
    assert result['annual_unique_paid_journeys']==100
    assert result['annual_train_boardings']==200
    assert result['annual_fare_receipts_iqd']==150000
    assert result['line_boardings']=={'A':100,'B':100,'C':0}
    assert not result['forecast_accepted']
    charged=account_journeys(network(),cohort,tariff='charged-per-boarding')
    assert charged['annual_fare_receipts_iqd']==300000
    assert charged['annual_unique_paid_journeys']==100


def test_disconnected_od_duplicate_cohorts_and_invalid_values_are_rejected():
    row=dict(journey_id='x',line_path=['A','C'],annual_journeys=100,fare_iqd=1500)
    with pytest.raises(ValueError,match='undeclared'):account_journeys(network(),[row])
    row['line_path']=['A']
    with pytest.raises(ValueError,match='Duplicate'):account_journeys(network(),[row,row])
    row['annual_journeys']=float('nan')
    with pytest.raises(ValueError,match='Invalid'):account_journeys(network(),[row])
    with pytest.raises(ValueError,match='tariff'):account_journeys(network(),[],tariff='implied')
