import pytest
from osr_scenario.service_acceptance import line_service_screen, configured_passenger_capacity


def inputs():
    design={'lines':[{'name':'a','length_m':10000},{'name':'b','length_m':10000}]}
    scenario={'lines':[{'id':'a','name':'Alpha'},{'id':'b','name':'Beta'}],
              'consist':{'passenger_capacity':360},
              'fleets':[{'line':line,'schedule':[{'from':'23:00','to':'01:00','headway_min':6}]} for line in ['a','b']]}
    return design,scenario


def test_surplus_on_one_line_cannot_mask_an_unserved_line():
    design,scenario=inputs()
    result=line_service_screen(design,scenario,[['Alpha',800],['Beta',0]])
    assert sum(r['observed_train_km'] for r in result['lines']) == sum(r['scheduled_train_km'] for r in result['lines'])
    assert not result['passed'] and not result['lines'][1]['passed']


@pytest.mark.parametrize('observations', [[],[['Alpha',400]], [['Alpha',400],['Alpha',400]],
    [['Alpha',400],['Beta',float('nan')]], [['Alpha',400],['Beta',-1]],
    [['Alpha',400],['Beta',400],['Unknown',1]]])
def test_missing_ambiguous_or_invalid_line_evidence_fails(observations):
    assert not line_service_screen(*inputs(),observations)['passed']


def test_midnight_windows_threshold_and_changed_headway():
    design,scenario=inputs()
    assert line_service_screen(design,scenario,[['Alpha',360],['Beta',360]])['passed']
    assert not line_service_screen(design,scenario,[['Alpha',360],['Beta',359]])['passed']
    scenario['fleets'][1]['schedule'][0]['headway_min']=3
    result=line_service_screen(design,scenario,[['Alpha',400],['Beta',400]])
    assert result['lines'][1]['scheduled_train_km']==800 and not result['passed']


def test_capacity_changes_are_effective_but_do_not_grant_acceptance():
    _,scenario=inputs();result=configured_passenger_capacity(scenario)
    assert result['windows'][0]['configured_passengers_per_hour_per_direction']==3600
    scenario['consist']['passenger_capacity']=180
    scenario['fleets'][0]['schedule'][0]['headway_min']=12
    result=configured_passenger_capacity(scenario)
    assert result['windows'][0]['configured_passengers_per_hour_per_direction']==900
    assert not result['accepted'] and result['status']=='open'
    scenario['consist']['passenger_capacity']=None
    assert not configured_passenger_capacity(scenario)['configured_inputs_valid']
