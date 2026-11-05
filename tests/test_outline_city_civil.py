from copy import deepcopy
from math import ceil
import pytest
from engineering.outline import city_civil
from engineering.station_rail.common import identity


def city(shape='radial'):
    return dict(input_id='synthetic-city-input',city=dict(slug='fixture',country='XX'),
        lines=[dict(line_id='A',shape=shape,route_m=6000.,stops=[dict(id='a',chainage_m=0.),dict(id='b',chainage_m=3000.),dict(id='c',chainage_m=6000.)])],
        civil_segments=[dict(line_id='A',**{'class':'elevated'},from_m=0.,to_m=6000.)],interchanges=[],source_sha256={})


def test_fragmentation_does_not_round_a_span_per_tiny_mapped_piece():
    c=city();whole=city_civil.quantities(c)
    c['civil_segments']=[dict(line_id='A',**{'class':'elevated'},from_m=i,to_m=i+1.) for i in range(6000)]
    split=city_civil.quantities(c)
    assert split==whole
    assert split['span_count']==600 and split['independent_supports']==602


def test_ring_has_no_two_invented_terminal_supports_and_joins_wrap_class():
    c=city('ring');assert city_civil.quantities(c)['independent_supports']==600
    c['civil_segments']=[dict(line_id='A',**{'class':k},from_m=a,to_m=b) for k,a,b in [('elevated',0,100),('at-grade',100,5900),('elevated',5900,6000)]]
    q=city_civil.quantities(c)
    assert len(q['runs'])==2 and q['span_count']==20 and q['class_route_m']['elevated']==200


def test_mixed_alignment_quantities_reconcile_and_keep_all_rails():
    c=city();c['civil_segments']=[dict(line_id='A',**{'class':k},from_m=a,to_m=b) for k,a,b in [('at-grade',0,2000),('bridge',2000,4000),('tunnel',4000,6000)]]
    q=city_civil.quantities(c)
    assert q['span_count']==200 and q['rail_kg']==pytest.approx(4*6000*60.21)
    assert q['tunnel_portals']==2 and q['bridge_runs']==1
    assert sum(q['class_route_m'].values())==q['route_m']


@pytest.mark.parametrize('segments',[
    [dict(line_id='A',**{'class':'elevated'},from_m=1,to_m=6000)],
    [dict(line_id='A',**{'class':'elevated'},from_m=0,to_m=6001)],
    [dict(line_id='Z',**{'class':'elevated'},from_m=0,to_m=6000)],
    [dict(line_id='A',**{'class':'free-bridge'},from_m=0,to_m=6000)]])
def test_incoherent_or_unpriced_civil_class_not_silently_zero(segments):
    c=city();c['civil_segments']=segments
    with pytest.raises(ValueError):city_civil.quantities(c)


def test_missing_alignment_gets_named_elevated_assumption():
    c=city();c['civil_segments']=[];q=city_civil.quantities(c)
    assert q['runs'][0]['assumed'] is True and q['span_count']>0


def test_unknown_policy_and_nan_rejected():
    with pytest.raises(ValueError):city_civil.quantities(city(),{'civil':{'free_factory':True}})
    with pytest.raises(ValueError):city_civil.quantities(city(),{'civil':{'at_grade_formation_m3_per_route_m':float('nan')}})
