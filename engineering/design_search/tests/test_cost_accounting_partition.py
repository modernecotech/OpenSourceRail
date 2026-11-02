"""Independent asset partition arithmetic and a small complete cost ledger."""
from copy import deepcopy
from math import fsum, nextafter

import pytest

from engineering.design_search import model_cost as m
from engineering.development_baseline import system_cost


CID = "a"*64


def _seal_assumptions(value):
    value["assumption_id"] = m.identity({k:v for k,v in value.items() if k!="assumption_id"})
    return value


def _assumptions(**changes):
    value = m.assumptions()
    value.update(changes)
    return _seal_assumptions(value)


def _line(key, values=(100.,100.,100.), scope="stations-power", components=None, **extra):
    rows = []
    m._line(rows,candidate_id=CID,scope=scope,key=key,quantity={},unit="fixture",
        totals=list(values),stage="factory-gate",basis="Independent accounting fixture",
        source_ids=["b"*64],components=components)
    row = rows[0]
    row.update(extra)
    row["line_id"] = m.identity({k:v for k,v in row.items() if k!="line_id"})
    return row


def _group(plan, name):
    return next(g for g in plan["asset_groups"] if g["asset_group"]==name)


def _station(values=(60.,60.,60.)):
    return _line("stations-platform-access-protection-control",values,
        components=dict(platform=[20.]*3,accessible_access_and_protection=[10.]*3,
            controls=[25.]*3,station_installation=[5.]*3))


def test_disjoint_groups_use_their_own_capital_and_independent_event_npvs():
    a = _assumptions()
    rows = [_line("station-lim-primary-stock",[100.]*3),
        _line("traction-converter-capacity",[200.]*3), _station(),
        _line("vehicle-stock/passive-secondary",[40.]*3,scope="rolling-stock"),
        _line("rail-fastener-sets",[50.]*3,scope="guideway")]
    original = deepcopy(rows)
    plan = m.renewal_plan(rows,a)
    capital = dict(rolling_stock=40.,motor_primary=100.,power_electronics=225.,guideway=50.,stations=35.)
    assert plan["conservation"]["source_initial_CAPEX_iqd"] == dict.fromkeys(m.CASES,450.)
    assert plan["conservation"]["allocated_initial_CAPEX_iqd"] == dict.fromkeys(m.CASES,450.)
    for group, amount in capital.items():
        result = _group(plan,group)
        assert result["allocated_initial_CAPEX_iqd"] == dict.fromkeys(m.CASES,amount)
        for i,case in enumerate(m.CASES):
            life = a["assumptions"]["asset_life_years"][group][i]*18/a["operating_hours_per_day_cases"][i]
            years = [life*n for n in range(1,10) if life*n < 30]
            expected = fsum(amount/1.04**year for year in years)
            assert result["cases"][i]["renewal_NPV_iqd"] == pytest.approx(expected)
            assert [e["year"] for e in result["cases"][i]["events"]] == pytest.approx(years)
    for i,case in enumerate(m.CASES):
        expected = fsum(_group(plan,g)["cases"][i]["renewal_NPV_iqd"] for g in capital)
        assert plan["renewal_NPV_iqd"][i] == round(expected,2)
    assert len(plan["source_line_allocations"])==8  # Four explicit station components, four other lines.
    assert rows==original
    assert plan["plan_id"]==m.identity({k:v for k,v in plan.items() if k!="plan_id"})


def test_same_year_different_disjoint_assets_are_not_deduplicated():
    a = _assumptions(operating_hours_per_day_cases=[18]*3)
    a["assumptions"]["asset_life_years"] = {g:[10]*3 for g in m.RENEWAL_GROUPS}
    _seal_assumptions(a)
    plan = m.renewal_plan([_line("station-lim-primary-stock",[100]*3),
        _line("traction-converter-capacity",[200]*3)],a)
    expected = 300/1.04**10+300/1.04**20
    assert plan["renewal_NPV_iqd"]==[round(expected,2)]*3
    assert [e["year"] for e in _group(plan,"motor_primary")["cases"][1]["events"]]==[10,20]
    assert [e["year"] for e in _group(plan,"power_electronics")["cases"][1]["events"]]==[10,20]


@pytest.mark.parametrize("key", sorted(m._PRIMARY_RENEWAL_KEYS))
def test_each_primary_fallback_supply_and_support_package_has_one_group(key):
    plan = m.renewal_plan([_line(key)],_assumptions())
    assert {x["asset_group"] for x in plan["source_line_allocations"]}=={"motor_primary"}
    assert plan["conservation"]["allocated_initial_CAPEX_iqd"]==dict.fromkeys(m.CASES,100.)


@pytest.mark.parametrize("key", sorted(m._ELECTRONICS_RENEWAL_KEYS))
def test_converter_and_charger_rows_are_not_also_primary_or_station_capital(key):
    plan = m.renewal_plan([_line(key)],_assumptions())
    assert {x["asset_group"] for x in plan["source_line_allocations"]}=={"power_electronics"}


def test_every_source_component_is_allocated_once_with_bounded_rounding():
    row = _line("station-lim-primary-stock",[1.]*3,
        components={"material":[.334]*3,"labour":[.334]*3,"overhead":[.334]*3})
    original = deepcopy(row)
    plan = m.renewal_plan([row],_assumptions())
    allocations = plan["source_line_allocations"]
    assert {x["component"] for x in allocations}=={"material","labour","overhead"}
    assert len({(x["source_line_id"],x["component"]) for x in allocations})==3
    assert fsum(x["allocated_initial_CAPEX_iqd"]["base"] for x in allocations)==1.
    assert fsum(x["rounding_adjustment_iqd"]["base"] for x in allocations)==pytest.approx(.01)
    assert row==original


def test_unknown_new_keys_require_explicit_reviewed_group():
    row = _line("new-protection-cabinet")
    with pytest.raises(ValueError,match="explicit renewal group"):
        m.renewal_plan([row],_assumptions())
    row = _line("new-protection-cabinet",renewal_asset_group="power_electronics")
    assert m.renewal_plan([row],_assumptions())["source_line_allocations"][0]["asset_group"]=="power_electronics"
    row = _line("topology-web-material",scope="guideway",renewal_asset_group="guideway")
    assert m.renewal_plan([row],_assumptions())["source_line_allocations"][0]["asset_group"]=="guideway"


def test_explicit_new_component_partition_covers_each_component_once():
    row=_line("new-mixed-equipment",[30.]*3,
        components=dict(fan=[10.]*3,converter=[20.]*3),
        renewal_component_groups=dict(fan="motor_primary",converter="power_electronics"))
    plan=m.renewal_plan([row],_assumptions())
    assert _group(plan,"motor_primary")["allocated_initial_CAPEX_iqd"]==dict.fromkeys(m.CASES,10.)
    assert _group(plan,"power_electronics")["allocated_initial_CAPEX_iqd"]==dict.fromkeys(m.CASES,20.)
    assert len(plan["source_line_allocations"])==2


@pytest.mark.parametrize("mutation,match", [
    (lambda r:r.update(components_iqd=None),"every explicit"),
    (lambda r:r["components_iqd"].pop("controls"),"every explicit"),
    (lambda r:r["components_iqd"].update(platform=[100]*3),"conserve"),
    (lambda r:r.update(renewal_asset_group="motor_primary"),"cannot share"),
    (lambda r:r["components_iqd"].update(unknown=[0]*3),"component renewal group"),
    (lambda r:r.update(renewal_component_groups={"controls":"power_electronics"}),"exactly one"),
])
def test_missing_incompatible_or_unallocated_station_components_fail(mutation,match):
    row = _station();mutation(row)
    row["line_id"] = m.identity({k:v for k,v in row.items() if k!="line_id"})
    with pytest.raises(ValueError,match=match):m.renewal_plan([row],_assumptions())


def test_invalid_source_identity_duplicate_and_cross_candidate_fail():
    row = _line("station-lim-primary-stock")
    with pytest.raises(ValueError,match="Duplicate"):m.renewal_plan([row,row],_assumptions())
    wrong = deepcopy(row);wrong["scenario_iqd"]["base"]+=1
    with pytest.raises(ValueError,match="Sealed canonical"):m.renewal_plan([wrong],_assumptions())
    other = _line("traction-converter-capacity",candidate_id="c"*64)
    with pytest.raises(ValueError,match="Mixed candidate"):m.renewal_plan([row,other],_assumptions())
    with pytest.raises(ValueError,match="contradicts"):
        m.renewal_plan([_line("station-lim-primary-stock",renewal_asset_group="power_electronics")],_assumptions())


def _cost_fixture(monkeypatch, *, sets=70, hardware=560.):
    # Isolate cost accounting from physical bundle admission. This is a small
    # synthetic ledger fixture, never an accepted or generated railway candidate.
    monkeypatch.setattr(m.railway_bundle,"validate",lambda value:None)
    def record(**fields):
        value=dict(candidate_id=CID,**fields);value["evaluation_id"]=m.identity(value);return value
    bundle=dict(candidate_id=CID,definition_id="d"*64,body_candidate_id="e"*64,
        propulsion_component_id="f"*64,family_id="P1",cars=6,car_length_m=17.,
        mass=dict(accounted_tare_kg_per_car=20000.),
        requirements=dict(target_headway_s=120.,dwell_s=35.,speed_cap_m_s=20.),
        architecture_case=dict(physical_definition=dict(route=dict(directional_ring_length_m=6000.,station_spacing_m=2000.,stations=3),
            guideway=dict(family="box-beam",span_m=20.))))
    inventory=record(engineering_BOM=[dict(id="fixture-services",scope="retained-unlocated-reference-account",
        accounted_mass_kg=1000.,component_definition_id="b"*64)],manufacturing_BOM=[],
        assembly_operation_graph=dict(operations=[]),geometry_coverage=dict(unknown_joint_ids=[]),unweighed_architecture_equipment=[])
    architecture=record(quantity_coefficients=dict(normal_service_trainsets=6,spare_trainsets=2,
        directional_route_m=6000.,stations=3,platform_train_length_m=106.5,
        offered_people_per_hour_direction=8280.,linear_motor_track_m=2839.5),
        trajectory=dict(runtime_s=150.,peak_required_power_W_train=2664670.7783586776,
            traction_mechanical_energy_J_train=1000000.))
    propulsion=record(bare_primary_kg_per_m=228.1856)
    motion=record()
    beam=dict(family="box-beam",load_case="crowd_control",concrete_m3=22.2816,
        reinforcement_kg=2673.792,prestress_kg=571.48,prestress_anchorage_kg=234.,
        running_rail_kg=2408.4,direct_fastener_kg=hardware,direct_fastener_sets=sets,
        total_counted_span_mass_kg=62151.672)
    civil=record(alternatives=[beam])
    return m.evaluate(bundle,inventory,architecture,propulsion,motion,civil)


def test_complete_set_cost_and_overhead_charged_once_with_mass_retained(monkeypatch):
    result = _cost_fixture(monkeypatch)
    rows={r["line_key"]:r for r in result["cost_line_items"]}
    assert "precast-direct-fasteners" not in rows
    fasteners=rows["rail-fastener-sets"]
    assert fasteners["quantity"]==dict(sets=42000,counted_hardware_mass_kg=336000.)
    assert list(fasteners["scenario_iqd"].values())==[4200000000.,16800000000.,63000000000.]
    overhead=rows["beam-factory-machine-QA-overhead"]["components_iqd"]
    for i,case in enumerate(m.CASES):
        direct=fsum(r["scenario_iqd"][case] for r in rows.values()
            if r["scope"]=="guideway" and r["line_key"]!="beam-factory-machine-QA-overhead")
        direct+=overhead["equipment"][i]+overhead["QA"][i]
        assert overhead["factory_overhead"][i]==pytest.approx(round(direct*[.1,.2,.3][i],2),abs=.02)
    assert rows["beam-heavy-haul-to-site"]["quantity"]["counted_span_mass_t"]==pytest.approx(62.151672)
    assert rows["beam-heavy-haul-to-site"]["quantity"]["tonne_km"]==pytest.approx(1864550.16)
    # Independent overlap removed from the former raw steel charge plus overhead.
    assert [336000*rate*(1+over) for rate,over in zip((2500,10000,35000),(.1,.2,.3))]==pytest.approx([924000000.,4032000000.,15288000000.])
    assert set(result["scope_totals_iqd"])==set(m.SCOPES)
    plan=rows["bounded-asset-replacements"]["quantity"]["renewal_plan"]
    assert plan["conservation"]["every_source_component_allocated_once"] is True
    assert result["renewal_plan_id"]==plan["plan_id"]
    assert result["production_plan"]["production_shifts_per_day"]==2
    assert result["production_plan"]["civil_shifts_per_day"]==2
    assert result["production_plan"]["operations_shifts_per_day_cases"]==[2,2,3]
    assert result["physical_mass_complete"] is result["physical_or_safety_accepted"] is False


@pytest.mark.parametrize("sets,hardware",[(0,560.),(70,0.),(70.5,560.),(-1,560.)])
def test_incompatible_fastener_count_and_nonzero_mass_fail(monkeypatch,sets,hardware):
    with pytest.raises(ValueError,match="fastener hardware mass"):
        _cost_fixture(monkeypatch,sets=sets,hardware=hardware)


def test_empty_foreign_currency_and_non_string_groups_fail():
    with pytest.raises(ValueError,match="At least one"):
        m.renewal_plan([],_assumptions())
    for extra in (dict(currency="USD"),dict(source_ids=[]),dict(source_ids=[None])):
        with pytest.raises(ValueError,match="Sealed canonical"):
            m.renewal_plan([_line("station-lim-primary-stock",**extra)],_assumptions())
    with pytest.raises(ValueError,match="contradicts"):
        m.renewal_plan([_line("new-item",renewal_asset_group=[])],_assumptions())
    with pytest.raises(ValueError,match="Mixed candidate"):
        m.renewal_plan([_line("station-lim-primary-stock",candidate_id="unknown")],_assumptions())


def test_tiny_asset_life_stops_at_an_explicit_computational_budget():
    a=_assumptions();a["assumptions"]["asset_life_years"]["motor_primary"]=[.000001]*3;_seal_assumptions(a)
    with pytest.raises(ValueError,match="computational accounting budget"):
        m.renewal_plan([_line("station-lim-primary-stock")],a)


def test_stale_or_incomplete_life_assumptions_fail():
    a=_assumptions();a["real_discount_rate"] = .05
    with pytest.raises(ValueError,match="Sealed renewal"):
        m.renewal_plan([_line("station-lim-primary-stock")],a)
    a=_assumptions();a["assumptions"]["asset_life_years"].pop("stations");_seal_assumptions(a)
    with pytest.raises(ValueError,match="asset life"):
        m.renewal_plan([_line("station-lim-primary-stock")],a)


@pytest.mark.parametrize("life,times",[(29.5,[29.5]),(30.,[]),(15.,[15.])])
def test_exact_strict_horizon_for_shared_helper_and_renewal_plan(life,times):
    assert m.replacement_event_times(30,life)==times
    a=_assumptions(operating_hours_per_day_cases=[18]*3)
    a["assumptions"]["asset_life_years"]["motor_primary"]=[life]*3;_seal_assumptions(a)
    plan=m.renewal_plan([_line("station-lim-primary-stock")],a)
    for case in _group(plan,"motor_primary")["cases"]:
        assert [e["year"] for e in case["events"]]==times
        assert case["replacement_count"]==len(times)
        assert case["renewal_NPV_iqd"]==pytest.approx(fsum(100/1.04**y for y in times))


def test_fractional_duty_adjustment_produces_event_between_29_and_30():
    a=_assumptions(operating_hours_per_day_cases=[24]*3)
    a["assumptions"]["asset_life_years"]["motor_primary"]=[118/3]*3;_seal_assumptions(a)
    plan=m.renewal_plan([_line("station-lim-primary-stock")],a)
    assert _group(plan,"motor_primary")["cases"][1]["events"][0]["year"]==29.5


@pytest.mark.parametrize("pack_life,vehicle_life,times,covered",[
    (29.5,30.,[29.5],[False]),(30.,15.,[],[]),
    (15.,15.,[15.],[True]),(15.,30.,[15.],[False]),
    (29.5,29.5,[29.5],[True]),
])
def test_service_pack_uses_shared_horizon_and_preserves_vehicle_overlap(pack_life,vehicle_life,times,covered):
    a=_assumptions(operating_hours_per_day_cases=[18]*3)
    a["assumptions"]["service_pack_life_years"]=[pack_life]*3
    a["assumptions"]["asset_life_years"]["rolling_stock"]=[vehicle_life]*3;_seal_assumptions(a)
    source=_line("retained-equipment/selected-service-battery-and-services",scope="rolling-stock")
    line,schedules=system_cost._account_renewal(CID,dict(cost_line_items=[source]),a)
    expected=round(fsum(100/1.04**year for year,is_covered in zip(times,covered) if not is_covered),2)
    assert line["scenario_iqd"]==dict.fromkeys(m.CASES,expected)
    for case in schedules:
        assert [e["year"] for e in case["events"]]==times
        assert [e["covered_by_complete_vehicle_replacement"] for e in case["events"]]==covered


def test_default_service_pack_schedule_resets_after_complete_vehicle_replacement():
    source=_line("retained-equipment/selected-service-battery-and-services",scope="rolling-stock")
    line,schedules=system_cost._account_renewal(CID,dict(cost_line_items=[source]),_assumptions())
    assert [[e["year"] for e in c["events"]] for c in schedules]==[
        [11.25,22.5],[8.,16.,28.],[4.5,9.,15.75,20.25,27.]]
    assert [r['year'] for r in schedules[0]['age_resets']]==[28.125]
    assert [r['year'] for r in schedules[1]['age_resets']]==[20.]
    assert [r['year'] for r in schedules[2]['age_resets']]==[11.25,22.5]
    assert not any(e['covered_by_complete_vehicle_replacement'] for e in schedules[2]['events'])
    expected_times=[[11.25,22.5],[8.,16.,28.],[4.5,9.,15.75,20.25,27.]]
    assert [line['scenario_iqd'][c] for c in m.CASES]==[
        round(fsum(100./1.04**year for year in times),2) for times in expected_times]


def test_near_horizon_event_retains_strict_unrounded_time():
    life=nextafter(30.,0.)
    assert m.replacement_event_times(30.,life)==[life]
    a=_assumptions(operating_hours_per_day_cases=[18]*3)
    a["assumptions"]["service_pack_life_years"]=[life]*3
    a["assumptions"]["asset_life_years"]["rolling_stock"]=[30.]*3;_seal_assumptions(a)
    source=_line("retained-equipment/selected-service-battery-and-services",scope="rolling-stock")
    _,schedules=system_cost._account_renewal(CID,dict(cost_line_items=[source]),a)
    assert all(c["events"][0]["year"]<30 for c in schedules)


@pytest.mark.parametrize("horizon,life",[(10**500,1.),(1e200,1e200),(30.,1e-300)])
def test_astronomical_horizons_or_event_counts_fail_before_allocation(horizon,life):
    with pytest.raises(ValueError,match="horizon|computational accounting budget"):
        m.replacement_event_times(horizon,life)


def test_plan_checks_astronomical_horizon_before_reading_line_iterable():
    class UnreadableLines(list):
        def __iter__(self):raise AssertionError("Cost lines must not be iterated")
    a=_assumptions(design_life_years=10**12)
    with pytest.raises(ValueError,match="horizon"):
        m.renewal_plan(UnreadableLines(),a)


@pytest.mark.parametrize("years,pack_life",[(10**12,10.),(30,1e-300)])
def test_service_pack_rejects_astronomical_schedule_before_event_generation(years,pack_life):
    a=_assumptions(design_life_years=years)
    a["assumptions"]["service_pack_life_years"]=[pack_life]*3;_seal_assumptions(a)
    source=_line("retained-equipment/selected-service-battery-and-services",scope="rolling-stock")
    with pytest.raises(ValueError,match="horizon|computational accounting budget"):
        system_cost._account_renewal(CID,dict(cost_line_items=[source]),a)
