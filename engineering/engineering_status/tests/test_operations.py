import pytest
from engineering.engineering_status import operations as o


def test_equal_service_requires_180_seconds_and_slow_walk_has_its_own_time_bound():
    assert o.capacity(180)==14400 and o.capacity(300)==8640
    assert o.transfer(300,1.)['comparison_screen_pass'] is True
    assert o.transfer(300,.6)['comparison_screen_pass'] is False
    assert o.transfer(180,.6)['comparison_screen_pass'] is True
    assert o.transfer(965.82892602,1.)['comparison_screen_pass'] is False
    assert o.transfer(180,.6)['accessible_route_qualified'] is False


@pytest.mark.parametrize('h',[0,-1,True,float('nan')])
def test_invalid_headways_cannot_generate_infinite_or_plausible_capacity(h):
    with pytest.raises(ValueError):o.capacity(h)
