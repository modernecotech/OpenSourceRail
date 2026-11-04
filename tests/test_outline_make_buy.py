from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import pytest

from engineering.outline import make_buy
from engineering.station_rail.common import identity


@pytest.fixture
def spec():
    return dict(item_id="comparison-rail-bracket",unit="bracket",currency="USD",quantity=100,
        committed_volume=100,project_years=1,
        purchase=dict(unit="bracket",tiers=[dict(minimum_quantity=1,unit_price=20.,already_bulk=False,
            source_class="declared-planning-price",source="synthetic independent arithmetic fixture")],
            landed=dict(freight_per_unit=1.,insurance_fraction=.02,duty_fraction=.1,
                qa_per_unit=.5,local_delivery_per_unit=.3)),
        make=dict(unit="bracket",material=dict(unit="kg",net_quantity_per_unit=1.,unit_price=2.,
            yield_fraction=.8,scrap_credit_per_unit=None),
            operations=dict(cell_hours_per_unit=1.,labour_hours_per_unit=.2,machine_hours_per_unit=.3,
                setup_cell_hours_per_batch=1.,setup_labour_hours_per_batch=.5,setup_machine_hours_per_batch=.5,
                batch_quantity=50,labour_rate_per_hour=10.,machine_rate_per_hour=2.,
                energy_kwh_per_unit=.5,setup_energy_kwh_per_batch=1.,energy_rate_per_kwh=.2,
                consumables_per_unit=.2,qa_per_unit=.5,labour_rate_basis="productive-hour-loaded",
                machine_rate_basis="cash-operating-excluding-capital-recovery"),
            fixed=dict(equipment_per_cell=500.,tooling_per_cell=100.,building_shared=200.,commissioning_shared=100.),
            capacity=dict(shifts_per_day=2,hours_per_shift=8.,days_per_year=250.,utilisation=.75),
            learning=None))


def volume(spec,quantity):
    result=deepcopy(spec);result.update(quantity=quantity,committed_volume=quantity)
    return result


def test_independent_landed_and_factory_arithmetic(spec):
    result=make_buy.evaluate(spec);row=result["cases"]["base"]
    buy=(100*20+100*1)*1.02*1.1+100*(.5+.3)
    # Material at yield 80%, two batches with setup, and fixed factory once.
    make=100/0.8*2+(100*.2+2*.5)*10+(100*.3+2*.5)*2+(100*.5+2*1)*.2+100*(.2+.5)+900
    assert row["purchase"]["total"]==pytest.approx(buy)
    assert row["make"]["total"]==pytest.approx(make)
    assert row["make"]["required_cell_hours"]==102
    assert row["make"]["available_hours_per_cell_project"]==3000
    assert row["make"]["batches"]==2 and row["make"]["cell_count"]==1
    assert row["make"]["fixed_total"]==900
    assert row["make"]["fixed_cost_per_committed_unit"]==9
    assert result["evaluation_id"]==identity({k:v for k,v in result.items() if k!="evaluation_id"})
    assert all(result[key] is False for key in make_buy.FLAGS)


def test_portable_arithmetic_contract_does_not_encode_observed_runtime(spec):
    result=make_buy.evaluate(spec)
    assert "runtime" not in result
    assert result["runtime_contract"]["supported_python"]==["3.12","3.13"]
    assert "external execution receipt" in result["runtime_contract"]["observed_execution_runtime"]


def test_canonical_result_bytes_match_python312_and_python313(spec):
    interpreters=[os.environ.get("OSR_TEST_PYTHON312") or shutil.which("python3.12"),
        os.environ.get("OSR_TEST_PYTHON313") or shutil.which("python3.13")]
    if not all(interpreters):
        pytest.skip("Set OSR_TEST_PYTHON312/OSR_TEST_PYTHON313 to test both installed interpreters")
    program=("import json,sys; from engineering.outline.make_buy import evaluate; "
        "from engineering.station_rail.common import encoded; "
        "assert sys.version_info[:2]==tuple(map(int,sys.argv[1].split('.'))); "
        "sys.stdout.buffer.write(encoded(evaluate(json.load(sys.stdin))))")
    outputs=[subprocess.run([exe,"-c",program,version],input=json.dumps(spec).encode(),capture_output=True,
        check=True,timeout=10,cwd=Path(__file__).resolve().parents[1]).stdout
        for exe,version in zip(interpreters,("3.12","3.13"))]
    assert outputs[0]==outputs[1]


def test_bulk_tiers_are_final_not_a_second_country_or_bulk_discount(spec):
    spec["purchase"]["tiers"].append(dict(minimum_quantity=100,unit_price=12.,already_bulk=True,
        source_class="supplier-listing-not-firm-quote",source="declared Chinese EXW quantity offer"))
    result=make_buy.evaluate(spec)["cases"]["base"]["purchase"]
    assert result["selected_tier"]["unit_price"]==12
    assert result["components"]["goods"]==1200
    assert result["extra_bulk_discount_applied"] is False
    spec["purchase"]["tiers"][1]["already_bulk"]=False
    assert make_buy.evaluate(spec)["cases"]["base"]["purchase"]["total"]==result["total"]
    spec["purchase"]["bulk_discount_fraction"]=.2
    with pytest.raises(ValueError,match="second purchase discount"):
        make_buy.evaluate(spec)


def test_small_quantity_buys_large_quantity_makes_without_free_factory(spec):
    small=make_buy.evaluate(volume(spec,1))["cases"]["base"]
    large=make_buy.evaluate(volume(spec,1000))["cases"]["base"]
    assert small["preferred"]=="buy" and large["preferred"]=="make"
    assert small["make"]["fixed_total"]==large["make"]["fixed_total"]==900
    assert large["make"]["total"]==large["make"]["variable_total"]+900
    assert large["make"]["speculative_future_order_credit"]==0
    assert large["make"]["resale_credit"]==0


def test_capacity_steps_include_setup_and_full_parallel_cell_cost(spec):
    spec["make"]["capacity"].update(hours_per_shift=1,days_per_year=5,utilisation=1)
    spec["make"]["operations"].update(batch_quantity=10,setup_cell_hours_per_batch=2)
    a=make_buy.evaluate(volume(spec,8))["cases"]["base"]["make"]
    b=make_buy.evaluate(volume(spec,9))["cases"]["base"]["make"]
    assert a["required_cell_hours"]==10 and a["cell_count"]==1
    assert b["required_cell_hours"]==11 and b["cell_count"]==2
    assert b["fixed_total"]-a["fixed_total"]==600
    assert b["fixed_components"]["building"]==a["fixed_components"]["building"]==200
    assert b["available_project_cell_hours"]>=b["required_cell_hours"]


def test_unknown_inputs_remain_null_not_zero(spec):
    del spec["make"]["fixed"]["equipment_per_cell"]
    result=make_buy.evaluate(spec);row=result["cases"]["base"]
    assert row["purchase"] is not None and row["make"] is None
    assert row["preferred"] is None and row["make_minus_buy"] is None
    assert "make.fixed.equipment_per_cell" in result["unknowns"]
    assert result["base_choice"] is None and result["status"]=="incomplete"
    del spec["quantity"]
    result=make_buy.evaluate(spec)
    assert all(row["purchase"] is None and row["make"] is None for row in result["cases"].values())
    assert "quantity" in result["unknowns"]


def test_missing_case_rate_does_not_reuse_another_case(spec):
    spec["make"]["material"]["unit_price"]={"low":1,"base":2}
    result=make_buy.evaluate(spec)
    assert result["cases"]["base"]["make"] is not None
    assert result["cases"]["high"]["make"] is None
    assert "make.material.unit_price.high" in result["cases"]["high"]["unknowns"]


@pytest.mark.parametrize("branch",["purchase","make"])
def test_comparable_units_and_currency_are_required(spec,branch):
    spec[branch]["unit"]="metre"
    with pytest.raises(ValueError,match="unit mismatch"):
        make_buy.evaluate(spec)
    spec[branch]["unit"]="bracket";spec[branch]["currency"]="CNY"
    with pytest.raises(ValueError,match="currency mismatch"):
        make_buy.evaluate(spec)


def test_declared_commitment_cannot_hide_factory_in_future_orders(spec):
    spec["committed_volume"]=100000
    with pytest.raises(ValueError,match="committed volume"):
        make_buy.evaluate(spec)


def test_scrap_is_explicit_bounded_and_never_free_material(spec):
    baseline=make_buy.evaluate(spec)["cases"]["base"]["make"]
    spec["make"]["material"]["scrap_credit_per_unit"]=.2
    credited=make_buy.evaluate(spec)["cases"]["base"]["make"]
    assert baseline["material"]["purchased_quantity"]==credited["material"]["purchased_quantity"]==125
    assert baseline["total"]-credited["total"]==pytest.approx(20)
    spec["make"]["material"]["scrap_credit_per_unit"]=.51
    with pytest.raises(ValueError,match="Scrap credit exceeds"):
        make_buy.evaluate(spec)


def test_learning_only_changes_declared_hours_and_respects_floor(spec):
    spec=volume(spec,1000)
    baseline=make_buy.evaluate(spec)["cases"]["base"]["make"]
    spec["make"]["learning"]=dict(progress_ratio=.8,reference_quantity=10,floor_fraction=.6,
        applies_to=["cell_hours_per_unit","labour_hours_per_unit"])
    learned=make_buy.evaluate(spec)["cases"]["base"]["make"]
    assert learned["learning"]["average_hours_factor"]==.6
    assert learned["labour_hours"]==pytest.approx(1000*.2*.6+20*.5)
    assert learned["variable_components"]["material_gross"]==baseline["variable_components"]["material_gross"]
    assert learned["variable_components"]["QA"]==baseline["variable_components"]["QA"]
    assert learned["machine_hours"]==baseline["machine_hours"]
    spec["make"]["learning"]["applies_to"].append("qa_per_unit")
    with pytest.raises(ValueError,match="Learning may affect only"):
        make_buy.evaluate(spec)


def test_scenario_winners_are_separate_from_base_choice(spec):
    spec["purchase"]["tiers"][0]["unit_price"]={"low":1.,"base":20.,"high":40.}
    result=make_buy.evaluate(spec)
    assert result["base_choice"]=="make"
    assert result["cases"]["low"]["preferred"]=="buy"
    assert result["cases"]["low"]["preference_differs_from_base"] is True
    assert result["cases"]["low"]["cost_of_base_choice"]==result["cases"]["low"]["make"]["total"]


def test_paid_idle_labour_is_costed_once_and_separate_from_cell_utilisation(spec):
    # Equal cash cost whether the caller loads the productive hourly rate or
    # supplies paid hours explicitly. Capacity remains the same two-shift 75%.
    loaded=deepcopy(spec);paid=deepcopy(spec)
    loaded["make"]["operations"]["labour_rate_per_hour"]=10/.75
    paid["make"]["operations"].update(labour_rate_basis="paid-hour",paid_hours_per_productive_hour=1/.75)
    a=make_buy.evaluate(loaded)["cases"]["base"]["make"]
    b=make_buy.evaluate(paid)["cases"]["base"]["make"]
    assert a["variable_components"]["labour"]==pytest.approx(b["variable_components"]["labour"])
    assert b["charged_labour_hours"]==pytest.approx(b["labour_hours"]/.75)
    assert a["available_project_cell_hours"]==b["available_project_cell_hours"]==3000
    assert b["labour_utilisation_adjustment_inferred"] is False
    del paid["make"]["operations"]["paid_hours_per_productive_hour"]
    assert make_buy.evaluate(paid)["cases"]["base"]["make"] is None


def test_zero_building_requires_named_external_cost_and_full_hire_rate_is_rejected(spec):
    spec["make"]["fixed"]["building_shared"]=0
    held=make_buy.evaluate(spec)
    assert held["cases"]["base"]["make"] is None
    assert "make.fixed.building_cost_reference" in held["unknowns"]
    spec["make"]["fixed"].update(building_priced_elsewhere=True,building_cost_reference="project factory capital line")
    assert make_buy.evaluate(spec)["cases"]["base"]["make"]["building_cost_reference"]=="project factory capital line"
    spec["make"]["operations"]["machine_rate_basis"]="full-hire-including-capital"
    with pytest.raises(ValueError,match="cash operating cost"):
        make_buy.evaluate(spec)


def test_break_even_explicitly_retains_tier_changes(spec):
    spec["purchase"]["tiers"].append(dict(minimum_quantity=100,unit_price=1,already_bulk=True,
        source_class="declared-planning-price",source="synthetic high volume finished-goods offer"))
    spec["break_even"]=dict(minimum_quantity=98,maximum_quantity=101,max_evaluations=4)
    result=make_buy.evaluate(spec)["break_even"]
    assert [r["preferred"] for r in result["samples"]["base"]]==["make","make","buy","buy"]
    crossing=result["transitions"]["base"][0]
    assert crossing["lower_quantity"]==99 and crossing["upper_quantity"]==100
    assert crossing["same_fixed_cell_and_tier_segment"] is False
    assert crossing["exact_adjacent_integer_boundary"] is True


def test_no_country_preference_for_materials_or_finished_goods(spec):
    china=deepcopy(spec);local=deepcopy(spec)
    china["purchase"]["tiers"][0].update(unit_price=50,source="China freight-heavy synthetic fixture")
    local["purchase"]["tiers"][0].update(unit_price=10,source="Local synthetic fixture")
    assert make_buy.evaluate(china)["cases"]["base"]["purchase"]["total"]>make_buy.evaluate(local)["cases"]["base"]["purchase"]["total"]
    china["purchase"]["tiers"][0]["unit_price"]=10
    assert make_buy.evaluate(china)["cases"]["base"]["purchase"]["total"]==make_buy.evaluate(local)["cases"]["base"]["purchase"]["total"]


def test_break_even_retains_nonmonotonic_capacity_reversals(spec):
    spec["purchase"]["landed"]={key:0 for key in make_buy._LANDED}
    spec["purchase"]["tiers"][0]["unit_price"]=10
    spec["make"]["material"].update(net_quantity_per_unit=1,unit_price=0,yield_fraction=1)
    spec["make"]["operations"]={key:0 for key in make_buy._OPERATIONS}
    spec["make"]["operations"].update(cell_hours_per_unit=1,batch_quantity=100,
        labour_rate_basis="productive-hour-loaded",machine_rate_basis="cash-operating-excluding-capital-recovery")
    spec["make"]["fixed"].update(equipment_per_cell=15,tooling_per_cell=0,building_shared=0,commissioning_shared=0,
        building_priced_elsewhere=True,building_cost_reference="synthetic shared project building, counted separately")
    spec["make"]["capacity"].update(shifts_per_day=2,hours_per_shift=1,days_per_year=1,utilisation=1)
    spec["break_even"]=dict(minimum_quantity=1,maximum_quantity=8,max_evaluations=8)
    result=make_buy.evaluate(spec)["break_even"]
    assert result["complete_integer_domain"] is True
    assert [r["preferred"] for r in result["samples"]["base"]][:4]==["buy","make","tie","make"]
    # A larger fixed cell creates repeated make->buy->make reversals.
    spec["make"]["fixed"]["equipment_per_cell"]=35
    spec["make"]["capacity"]["days_per_year"]=2
    result=make_buy.evaluate(spec)["break_even"]
    assert [r["preferred"] for r in result["samples"]["base"]]==["buy","buy","buy","make","buy","buy","tie","make"]
    assert result["global_crossover_established"] is False
    assert result["untested_intervals"]==[]


def test_break_even_sampling_never_fills_untested_gaps(spec):
    spec["break_even"]=dict(minimum_quantity=1,maximum_quantity=100000,max_evaluations=16)
    result=make_buy.evaluate(spec)["break_even"]
    assert result["distinct_quantities_evaluated"]<=16
    assert result["complete_integer_domain"] is False
    assert result["untested_intervals"] and result["preferred_intervals"]["base"]==[]
    assert result["global_crossover_established"] is False


@pytest.mark.parametrize("path,value",[("quantity",float("nan")),("quantity",True),("project_years",0)])
def test_invalid_or_nonfinite_inputs_are_rejected(spec,path,value):
    spec[path]=value
    with pytest.raises(ValueError):
        make_buy.evaluate(spec)
