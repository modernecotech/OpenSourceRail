"""Delivery arithmetic must expose missing scope and preserve existing funding."""
from copy import deepcopy
import csv
import hashlib
import json
from pathlib import Path
import sys
import tomllib
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from baghdad_delivery_baseline import dispatch_energy, hourly_duty, validate, correlated_risk
OUT=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/delivery-baseline'

def read(name):return json.loads((OUT/(name+'.json')).read_text())

def test_qualification_packages_reconcile_without_claiming_new_funding():
    family=read('six-car')
    assert sum(r['reference_budget_usd'] for r in family['qualification_work_packages'])==pytest.approx(12000000)
    assert len(family['qualification_work_packages'])==len(family['interfaces'])==10
    assert family['qualification_incremental_cost_usd'] is None
    assert not any(r['accepted'] for r in family['qualification_work_packages'])

def test_rental_allocation_preserves_physical_cost_and_separates_tenant_credit():
    options=read('rental-delivery-options')
    npvs=[]
    for name,case in options['cases'].items():
        assert case['landlord_fitout_usd']+case['partner_fitout_usd']==pytest.approx(case['total_physical_fitout_usd'])
        assert case['landlord_before_tax_npv_usd']+case['partner_before_tax_value_npv_usd']==pytest.approx(case['combined_before_tax_value_npv_usd'])
        assert case['maintenance_interruption_rent_loss_usd']>0
        with (OUT/case['monthly_file']).open() as handle:
            for row in csv.DictReader(handle):
                assert float(row['landlord_before_tax_cash_usd'])+float(row['partner_before_tax_cash_or_avoided_rent_usd'])==pytest.approx(float(row['combined_before_tax_value_usd']))
        npvs.append(case['combined_before_tax_value_npv_usd'])
    assert max(npvs)-min(npvs)<.001
    assert npvs[0]<options['original_before_tax_npv_usd']
    assert options['cases']['tenant_funded_shell']['partner_value_is_avoided_rent']
    assert options['actual_local_enquiries'] is None and options['inspection_work_cost_usd'] is None
@pytest.fixture(scope='module')
def config():return tomllib.loads((ROOT/'lib/templates/baghdad-delivery-baseline.toml').read_text())

def test_complete_scope_is_not_inferred_from_base_and_replacement_scenarios():
    s=read('scope-register');programme=json.loads((OUT.parent.parent.parent/'finance/baghdad-programme.json').read_text())
    assert sum(r['base_estimate_usd'] or 0 for r in s['rows'])==pytest.approx(programme['total_capex_usd'],abs=.02)
    assert s['base_programme_usd']==pytest.approx(7880493587.215033,abs=.02)
    assert not s['complete_delivery_budget'] and s['unpriced_scope_count']==12
    for r in s['rows']:
        assert r['named_estimator'] is None and r['price_date'] is None and r['quotation'] is None
        if r['quantity'] is not None:assert r['quantity']*r['reference_rate_usd']==pytest.approx(r['base_estimate_usd'])
        else:assert r['base_estimate_usd'] is None
    for r in s['alternatives'].values():
        assert r['provisional_reference_total_if_replacement_usd']==pytest.approx(s['base_programme_usd']-8e6+r['depot_gross_reference_usd'])
        assert not r['adopted'] and not r['complete_delivery_budget']
    assert all(r['allocated_cost_usd'] is None for r in s['epc_obligations'])

def test_line_local_storage_and_workshops_reconcile_without_double_equipment_delta(config):
    s=read('depot-package')
    assert s['station_trainsets']+s['depot_trainsets']==s['fleet_trainsets']==831
    assert not s['original_allocation_passed'] and s['missing_morning_directions']
    design=tomllib.loads((OUT.parent.parent/'design.toml').read_text())
    fleets={r['line']:r['trainset_count'] for r in design['fleets']}
    c=config['depot']
    for variant,v in s['alternatives'].items():
        assert len(v['sites'])==9 and sum(r['stabling_positions'] for r in v['sites'])==533
        assert v['gross_reference_cost_usd']==pytest.approx(sum(r['quantity']*r['reference_rate_usd'] for r in v['items']))
        for r in v['sites']:
            assert r['storage_usable_track_m']==r['stabling_positions']*121
            assert r['storage_tracks']*3>=r['stabling_positions']
            assert r['turnouts']==r['storage_tracks']+2 and not r['layout_accepted']
            if variant=='workload_bays':assert r['workshop_bays']*260*16*.7>=fleets[r['line']]*400
        assert sum(r['reference_cost_usd'] for r in v['items'] if r['scope'].startswith('depot-'))==6500000
        assert not v['allowance_overlap_accepted'] and not v['actual_layout_released']
    assert sum(r['workshop_bays'] for r in s['alternatives']['retained_declared_bays']['sites'])==125

def test_six_car_price_mass_counts_and_factory_payroll_boundary():
    s=read('six-car')
    assert s['trainsets']==831 and s['vehicle_modules']==4986
    assert sum(r['cost_allocation_per_consist_usd'] for r in s['bom'])==1680000
    assert sum(r['planning_mass_kg_per_consist'] for r in s['bom'])+s['unallocated_mass_reserve_kg']==204000
    assert s['doors_per_consist']==24 and s['windows_per_consist']==36
    assert s['full_load_axle_load_average_t']==pytest.approx((204000+960*75)/24000)
    assert s['controlled_profile']['onboard_battery_nameplate_kwh']==1350
    assert s['controlled_profile']['onboard_battery_kwh']==1080
    assert s['qualification_incremental_cost_usd'] is None and not s['engineering_release']
    assert all(not r['lm3_credit_accepted'] and r['mass_evidence'] is None for r in s['bom'])
    assert all(r['network_person_hours']==r['reference_person_hours_per_consist']*831 and r['labour_in_train_procurement'] and r['measured_cycle_days'] is None for r in s['labour_routes'])

def test_editable_price_and_fx_reconcile_in_fleet_bom_and_payroll(monkeypatch,config):
    import baghdad_delivery_baseline as baseline
    design=tomllib.loads((OUT.parent.parent/'design.toml').read_text());scenario=tomllib.loads((OUT.parent.parent/'baghdad.toml').read_text())
    risk=json.loads((OUT.parent/'delivery-risk/summary.json').read_text());detail=json.loads((OUT.parent/'detail/register.json').read_text())
    factory=json.loads((OUT.parent/'factory/summary.json').read_text());finance=json.loads((OUT.parent/'finance/summary.json').read_text())
    monkeypatch.setattr(baseline,'trainset_reference_cost',lambda:2000000)
    phased=baseline.phase_fleet(design,scenario,risk,config)
    assert phased['deferred_train_capital_usd']==phased['deferred_fleet']*2000000
    assert baseline.family_baseline(design,scenario,detail,factory,config)['cost_allocations_reconcile_usd']==pytest.approx(2000000)
    altered=deepcopy(config);altered['model']['iqd_per_usd_reference']=1500
    wages=baseline.workforce(design,scenario,finance,risk,factory,altered)
    assert wages['reference_annual_loaded_payroll_usd']==pytest.approx(wages['reference_annual_loaded_payroll_iqd']/1500)

def test_hourly_losses_limits_energy_conservation_and_no_free_storage(config):
    rows=dispatch_energy([100.,0.],[0.,100.],storage_kwh=100,power_kw=100,grid_kw=100,config=config['energy'])
    assert rows[0]['opening_soc_kwh']==10 and rows[0]['storage_discharge_kwh']==0
    assert rows[0]['closing_soc_kwh']==100 and rows[1]['closing_soc_kwh']==pytest.approx(10)
    assert rows[1]['storage_discharge_kwh']==pytest.approx(85.5) and rows[1]['grid_import_kwh']==pytest.approx(14.5)
    assert all(abs(r['energy_residual_kwh'])<1e-6 for r in rows)
    no_grid=dispatch_energy([0.],[100.],storage_kwh=100,power_kw=50,grid_kw=30,config=config['energy'])
    assert no_grid[0]['unserved_kwh']==70 and no_grid[0]['grid_import_kwh']==30

@pytest.mark.parametrize('generation,load', [([float('nan')],[1.]),([-1.],[1.]),([1.,2.],[1.])])
def test_invalid_energy_data_rejected(config,generation,load):
    with pytest.raises(ValueError):dispatch_energy(generation,load,storage_kwh=100,power_kw=10,grid_kw=10,config=config['energy'])

def test_all_chronological_cases_reconcile_and_unserved_service_is_unaccepted(config):
    s=read('chronological-energy')
    assert len(s['cases'])==9 and s['aggregate_pooling_unestablished']
    demand=None
    for name,c in s['cases'].items():
        with (OUT/c['hourly_file']).open() as f:rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
        assert len(rows)==8760
        assert sum(r['grid_import_kwh'] for r in rows)==pytest.approx(c['grid_import_kwh'])
        assert sum(r['unserved_kwh'] for r in rows)==pytest.approx(c['unserved_kwh'])
        assert sum(r['demand_kwh'] for r in rows)==pytest.approx(c['charging_bus_demand_kwh'])
        assert c['electricity_purchase_usd']==pytest.approx(c['grid_import_kwh']*.10)
        assert c['annual_energy_cost_usd']==pytest.approx(sum(c[k] for k in ['electricity_purchase_usd','wheeling_usd','balancing_usd','connection_usd','solar_ppa_usd','owned_solar_maintenance_usd']))
        if demand is None:demand=c['traction_demand_kwh']
        assert c['traction_demand_kwh']==demand and not c['service_accepted']
        for r in rows:
            assert r['grid_import_kwh']<=s['aggregate_import_limit_kw']+.01
            assert abs(r['generation_kwh']+r['grid_import_kwh']+r['opening_soc_kwh']-r['demand_kwh']+r['unserved_kwh']-r['curtailed_kwh']-r['conversion_loss_kwh']-r['closing_soc_kwh'])<1e-6
    owned=s['cases']['synthetic_reference:owned_solar'];hybrid=s['cases']['synthetic_reference:hybrid_storage']
    assert owned['grid_import_kwh']>0 and owned['unserved_kwh']>0
    assert hybrid['grid_import_kwh']<owned['grid_import_kwh'] and hybrid['additional_hybrid_equipment_usd']==180e6
    assert s['ten_percent_purchase_sensitivity_usd']==pytest.approx(s['annual_traction_demand_kwh']*.01)

def test_midnight_hourly_schedule_conserves_daily_duty():
    d=dict(lines=[dict(name='L',length_m=1000)])
    s=dict(fleets=[dict(line='L',schedule=[{'from':'23:30','to':'02:00','headway_min':10}])])
    duty=hourly_duty(d,s,365000)
    assert sum(duty)==pytest.approx(1000) and sum(duty[2:23])==0
    assert duty[0]==pytest.approx(duty[1]) and duty[0]==pytest.approx(2*duty[23])

def test_fleet_phasing_net_purchase_and_service_supply_reconcile():
    s=read('first-phase')
    assert s['baseline_fleet']-s['deferred_fleet']+s['additional_fleet']==s['opening_fleet']
    assert s['additional_fleet']==1 # Round 10% spares up on the already 6-minute line 9.
    for r in s['lines']:
        assert r['baseline_trainsets']-r['deferred_trainsets']+r['additional_trainsets']==r['opening_trainsets']
        assert r['opening_trainsets']==r['opening_peak_count']+r['opening_spares']+r['opening_cold_reserves']
        assert r['opening_daily_train_km']<=r['baseline_daily_train_km']
        assert r['od_demand'] is None and r['commercial_corridor_rank'] is None and not r['adopted']
    assert not s['unchanged_fares_claimed'] and not s['factory_resize_accepted']

def test_workload_grade_cost_unit_cover_recruitment_and_separate_commissioning(config):
    s=read('workforce');c=config['workforce']
    assert s['productive_hours_per_fte']==1520 and len(s['roles'])==21
    assert s['reference_required_fte']==sum(r['required_fte'] for r in s['roles'])
    assert s['reference_annual_loaded_payroll_iqd']==pytest.approx(sum(r['annual_loaded_payroll_iqd'] for r in s['roles']))
    for r in s['roles']:
        units=[u for u in s['units'] if u['unit'].startswith(r['role_id']+':')]
        assert sum(u['required_fte'] for u in units)==r['required_fte']
        assert sum(u['annual_workload_person_hours'] for u in units)==pytest.approx(r['annual_workload_person_hours'])
        assert all(u['required_fte']*1520>=u['annual_workload_person_hours'] for u in units)
        assert r['annual_loaded_payroll_iqd']==pytest.approx(r['required_fte']*r['monthly_base_iqd']*12*1.35)
        assert sum(p['target_authorised_staff'] for p in s['recruitment_cohorts'] if p['role_id']==r['role_id'])==r['required_fte']
    for p in s['recruitment_cohorts']:
        assert p['expected_authorised']>=p['target_authorised_staff']
        assert p['requisition_month']<p['join_month']<p['training_complete_month']<p['first_assessment_month']<p['repeated_assessment_month']<p['authorised_available_month']
        assert p['authorised_available_month']==p['required_line_opening_month'] and not p['available']
        assert p['additional_commissioning_payroll_iqd']==0 # Supervised operating trainees already paid.
    assert len(s['temporary_commissioning_cohorts'])==9
    assert s['temporary_commissioning_payroll_iqd']==pytest.approx(9*12*1950000*1.35*3)
    assert not s['factory_payroll_added_to_operating_payroll'] and s['construction_staff_separate']
    assert s['named_workers']==0 and all(r['worker_id'] is None and not r['eligible'] for r in s['pilot_roster'])
    assert sum(r['paid_duration_hours'] for r in s['pilot_roster'])==7*20.5

def test_curricula_governance_and_budgeted_evidence_do_not_approve_anything():
    s=read('workforce')
    assert len(s['curricula'])==7 and all(not r['accepted'] and not r['attendance_is_competence'] and not r['competence_is_task_authorisation'] for r in s['curricula'])
    assert all(r['assessment_criteria'] and r['equipment'] and r['retraining_triggers'] for r in s['curricula'])
    m=read('mobilisation');assert m['project']['project_id']=='BAGHDAD-DELIVERY'
    assert m['summary']['roles_ready']==m['summary']['gates_accepted']==m['summary']['management_systems_ready']==0
    assert not m['reference_template_windows_adopted']
    w=read('90-day-work-programme');assert len(w['work_packages'])==6
    assert sum(r['reference_closure_budget_usd'] for r in w['work_packages'])==w['reference_total_closure_budget_usd']
    assert all(r['named_owner'] is None and r['evidence'] is None and not r['budget_committed'] for r in w['work_packages'])

def test_correlated_risk_is_reproducible_uncalibrated_and_keeps_missing_costs_null(config):
    source=read('scope-register');r=correlated_risk(source,config)
    assert r==read('cost-schedule-risk') and r['p80_known_scope_usd']>=r['p50_known_scope_usd']>source['base_programme_usd']
    assert not r['unpriced_scope_included'] and r['approved_contingency_usd'] is None

def test_all_sources_outputs_and_current_review_match():
    s=read('summary')
    for base,key in [(ROOT,'sources_sha256'),(OUT,'outputs_sha256'),(ROOT,'external_outputs_sha256')]:
        for path,sha in s[key].items():assert hashlib.sha256((base/path).read_bytes()).hexdigest()==sha,path
    root=(ROOT/'README.md').read_text();old=(ROOT/'docs/codebase-and-iraq-review-2026-10-03.md').read_text()
    assert 'docs/baghdad-ci-controls-review-2026-10-04.md' in root and 'superseded' in old[:1000]
    assert not s['complete_delivery_budget'] and not s['operational_release']

def test_invalid_workforce_hours_fail_closed(config):
    c=deepcopy(config);c['workforce']['leave_hours']=3000
    with pytest.raises(ValueError):validate(c)

@pytest.mark.parametrize('section,key',[('depot','positions_per_track'),('workforce','trainer_learners_per_group'),('fleet','opening_peak_headway_minutes'),('rental_delivery','inspection_closure_interval_months')])
def test_zero_divisors_and_service_intervals_rejected(config,section,key):
    c=deepcopy(config);c[section][key]=0
    with pytest.raises(ValueError):validate(c)

def test_current_front_door_headlines_follow_physical_and_finance_sources():
    city=OUT.parent.parent;design=tomllib.loads((city/'design.toml').read_text())
    scope=read('scope-register');family=read('six-car')
    programme=json.loads((city.parent/'finance/baghdad-programme.json').read_text())
    text=(ROOT/'docs/baghdad-delivery-review-2026-10-04.md').read_text()
    assert f"{len(design['lines'])} lines, {sum(r['length_m'] for r in design['lines'])/1000:.4f} km, {len(design['stations'])} stations and {family['trainsets']} six-car trains" in text
    assert f"USD {scope['base_programme_usd']/1e9:.6f}bn" in text
    assert f"capital table has {sum(r['capex_usd']>0 for r in programme['monthly'])} periods" in text
