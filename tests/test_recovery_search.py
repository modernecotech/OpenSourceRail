from copy import deepcopy
from math import fsum
import pytest
from engineering.station_rail.common import identity
from engineering.recovery_search import configuration as c
from engineering.recovery_search.search import specifications,pareto,assessment
from engineering.railway_closure import coordinator,installed,bundle,service,motion,fleet
from engineering.vehicle_installation import underframe
from engineering.pilot_civil import design as civil


@pytest.fixture(scope='module')
def prepared():return c.prepare()


def test_capacity_is_physical_but_dispatch_control_is_evaluation(prepared):
    small=c.build('hydraulic',250000.,prepared=prepared)
    large=c.build('hydraulic',4e6,prepared=prepared)
    steel=c.build('steel',250000.,prepared=prepared)
    assert len({d['variant']['candidate_id'] for d in (small,large,steel)})==3
    assert small['sizing']['active_mass_kg']<large['sizing']['active_mass_kg']
    assert c.release_control(.2)!=c.release_control(.8)
    assert c.build('hydraulic',250000.,prepared=prepared)==small
    module=small['variant']['physical_definition']['station_energy_module']
    big=large['variant']['physical_definition']['station_energy_module']
    for k in module.keys()-{'nominal_capacity_j','active_stock_kg_per_station','fluid_stock_kg_per_station','envelope_reserve_m3_per_station'}:
        assert module[k]==big[k]


def test_hardware_and_fixed_control_cannot_be_silently_cheapened(prepared):
    value=c.build('hydraulic',250000.,prepared=prepared)
    value['variant']['physical_definition']['station_energy_module']['nominal_capacity_j']=1.
    value.pop('evaluation_id');value['evaluation_id']=identity(value)
    with pytest.raises(ValueError):c.validate(value)
    for field,x in [('reserve_factor',1.),('force_slew_n_s',1e8),('mode','free-energy')]:
        q=c.release_control(.2);q[field]=x
        with pytest.raises(ValueError):c.validate_release_control(q)
    for x in (0.,float('nan'),True,1.):
        with pytest.raises(ValueError):c.release_control(x)


@pytest.fixture(scope='module')
def common(prepared):
    body=underframe.build(underframe.load_parent(c.ROOT/coordinator.PARENT),family_id='steel-650x650x10')
    d=c.build('hydraulic',250000.,prepared=prepared)
    i=installed.integrate(body,recovery_design=d)
    axles=installed.axle_packet(i)
    cv=civil.evaluate(axles,family='folded_plate',revision='thick-web',soil_case='base')
    canonical=bundle.combine(i,cv)
    s=service.plan(canonical['candidate_id'],dict(A=190.,B=190.),service.brief(),headway_s=200.,phase_b_s=90.,active_trainsets=3)
    return body,i,canonical,s


def test_exact_mass_and_same_hardware_control_binding(common,prepared):
    body,i,b,s=common
    big=installed.integrate(body,recovery_design=c.build('hydraulic',4e6,prepared=prepared))
    no=installed.integrate(body,with_recovery=False,recovery_design=c.build(None,0.,prepared=prepared))
    for a,z,n in zip(i['load_cases'],big['load_cases'],no['load_cases']):
        assert a['train_mass_kg']==z['train_mass_kg']
        assert a['train_mass_kg']-n['train_mass_kg']==a['added_capture_interface_kg']>0
        assert abs(fsum(x['vertical_force_N'] for x in a['axles'])-a['train_mass_kg']*installed.G)<1e-6
    context=motion.prepare()
    low=fleet.request(i,b,s,prepared=context,release_control=c.release_control(.2))
    high=fleet.request(i,b,s,prepared=context,release_control=c.release_control(.8))
    assert low['candidate_id']==high['candidate_id'] and low['id']!=high['id']
    assert len(low['trains'])==4 and len(low['departures'])==16
    assert all(x['initial_energy_j']==0 and len(x['capture_stages'])==5 for x in low['stations'])
    assert s['planning_capacity_pphpd']==pytest.approx(4222.8)
    assert s['planned_service_complete']
    assert i['packaging_screen'].startswith('hold:')
    with pytest.raises(ValueError):installed.integrate(body,with_recovery=False,recovery_design=c.build('hydraulic',250000.,prepared=prepared))


def test_bounded_cases_and_economic_frontier_excludes_incomplete_service():
    specs=specifications();assert len(specs)==32
    assert len({(x['technology'],x['capacity_j']) for x in specs})==11
    rows=[dict(key='base',model_screen=True,installed_capital_usd_base=10.,whole_life_NPV_usd_base=30.,annual_grid_kwh_base=100.),
          dict(key='store',model_screen=True,installed_capital_usd_base=12.,whole_life_NPV_usd_base=35.,annual_grid_kwh_base=110.),
          dict(key='failed-cheap',model_screen=False,installed_capital_usd_base=1.,whole_life_NPV_usd_base=None,annual_grid_kwh_base=None),
          dict(key='energy-alternative',model_screen=True,installed_capital_usd_base=15.,whole_life_NPV_usd_base=36.,annual_grid_kwh_base=90.)]
    assert pareto(rows)==['base','energy-alternative']
