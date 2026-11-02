"""Component clocks restart when a complete replacement supplies a new one."""
from math import fsum, nextafter

import pytest

from engineering.development_baseline import system_cost as s
from engineering.design_search import model_cost as m


@pytest.mark.parametrize('horizon,life,parents,years,covered',[
    (30.,8.,[20.],[8.,16.,28.],[False]*3),
    (30.,4.5,[11.25,22.5],[4.5,9.,15.75,20.25,27.],[False]*5),
    (30.,10.,[20.],[10.,20.],[False,True]),
    (30.,15.,[15.],[15.],[True]),
    (30.,30.,[15.],[],[]),
    (30.,29.5,[],[29.5],[False]),
    (30.,30.,[],[],[]),
    (30.,3.,[7.,14.,21.,28.],[3.,6.,10.,13.,17.,20.,24.,27.],[False]*8),
    (30.,7.,[7.,14.,21.,28.],[7.,14.,21.,28.],[True]*4),
    (2.,.25,[.5,1.25],[.25,.5,.75,1.,1.25,1.5,1.75],[False,True,False,False,True,False,False]),
])
def test_independent_exact_age_reset_examples(horizon,life,parents,years,covered):
    result=s.component_renewal_schedule(horizon,life,parents)
    assert [e['year'] for e in result['events']]==years
    assert [e['covered_by_parent_replacement'] for e in result['events']]==covered
    assert [r['year'] for r in result['age_resets']]==parents
    assert all(r['component_supplied_by_parent_replacement'] and r['component_age_after_reset_years']==0 for r in result['age_resets'])
    assert all(0<e['year']<horizon for e in result['events'])
    assert result['evaluation_id']==m.identity({k:v for k,v in result.items() if k!='evaluation_id'})


def test_age_metadata_tracks_the_most_recent_component_and_parent_resets():
    result=s.component_renewal_schedule(30,8,[20.])
    assert [e['component_age_origin_year'] for e in result['events']]==[0.,8.,20.]
    assert [e['component_age_at_event_years'] for e in result['events']]==[8.,8.,8.]
    assert result['age_resets']==[dict(year=20.,component_supplied_by_parent_replacement=True,
        component_age_origin_year=16.,component_age_before_reset_years=4.,
        component_age_after_reset_years=0.,coincident_component_event_recorded=False)]


def test_reset_at_fractional_parent_changes_later_cashflow_without_new_rates():
    result=s.component_renewal_schedule(30.,4.,[9.5,19.,28.5])
    expected=[4.,8.,13.5,17.5,23.,27.]
    assert [e['year'] for e in result['events']]==expected
    assert fsum(100./1.04**e['year'] for e in result['events'])==pytest.approx(fsum(100./1.04**y for y in expected))


def test_exact_horizon_excluded_and_near_horizon_not_rounded_away():
    near=nextafter(30.,0.)
    assert [e['year'] for e in s.component_renewal_schedule(30.,near,[])['events']]==[near]
    assert s.component_renewal_schedule(30.,15.,[])['events'][-1]['year']==15.
    assert not s.component_renewal_schedule(30.,30.,[])['events']
    with pytest.raises(ValueError,match='inside the horizon'):s.component_renewal_schedule(30.,10.,[30.])


def test_valid_due_offset_after_reset_is_retained_if_addition_rounds_to_horizon():
    life=nextafter(10.,0.)
    assert 20.+life==30.  # The exact input offset is still less than ten.
    result=s.component_renewal_schedule(30.,life,[20.])
    last=result['events'][-1]
    assert last['year']==nextafter(30.,0.)
    assert last['nominal_due_year']==30.
    assert last['strict_horizon_float_roundoff_adjustment']
    assert not last['covered_by_parent_replacement']


@pytest.mark.parametrize('parents',[None,'20',(x for x in [20]),[0.],[-1.],[30.],[31.],
    [20.,10.],[20.,20.],[float('nan')],[float('inf')],[10**500],[True]])
def test_malformed_parent_sequences_are_rejected(parents):
    with pytest.raises(ValueError):s.component_renewal_schedule(30.,8.,parents)


@pytest.mark.parametrize('horizon,life',[(0.,8.),(-1.,8.),(30.,0.),(30.,-1.),
    (30.,float('nan')),(30.,float('inf')),(30.,10**500),(10**500,8.),
    (10**12,8.),(30.,1e-300),(True,8.),(30.,True)])
def test_unbounded_or_nonfinite_inputs_rejected_before_allocation(horizon,life):
    class UnreadableParents(list):
        def __iter__(self):raise AssertionError('Invalid timing must fail first')
    with pytest.raises(ValueError):s.component_renewal_schedule(horizon,life,UnreadableParents())


def test_parent_count_rejected_before_iteration():
    class UnreadableParents(list):
        def __iter__(self):raise AssertionError('Oversized timing must fail first')
    with pytest.raises(ValueError,match='Bounded explicit'):
        s.component_renewal_schedule(30.,8.,UnreadableParents([1.]*10001))


def test_tiny_valid_fractional_times_do_not_coalesce_multiple_events():
    result=s.component_renewal_schedule(1e-9,1e-12,[5e-10])
    years=[e['year'] for e in result['events']]
    assert years==sorted(set(years)) and all(0<y<1e-9 for y in years)
    assert sum(e['covered_by_parent_replacement'] for e in result['events'])==1
