"""Independent arithmetic, missing-data and budget-conservation checks."""
import math
import pytest
from engineering.analysis.city_delivery import allocate, construction_workload, refinement
from engineering.analysis.detail_checks import (thermal_movement_mm, seal_compression_range,
                                               preload_range_n, cleaning_labour_hours)


def test_movement_units_and_direction():
    assert thermal_movement_mm(100,10,30)==30
    assert thermal_movement_mm(100,10,-30)==-30
    with pytest.raises(ValueError): thermal_movement_mm(100,math.nan,30)


def test_seal_tolerance_bounds_include_loss_of_contact():
    low,high=seal_compression_range(10,1,8,1)
    assert low==0
    assert high==pytest.approx(4/11)
    assert seal_compression_range(10,1,10,1)[0]<0
    with pytest.raises(ValueError): seal_compression_range(1,1,1,0)


def test_torque_variation_widens_preload_not_a_fixed_torque_recommendation():
    low,high=preload_range_n(100,10,.1,.2,.1)
    assert low==pytest.approx(45000)
    assert high==pytest.approx(110000)
    with pytest.raises(ValueError): preload_range_n(100,10,.2,.1,0)


def test_cleaning_counts_setup_per_cycle_and_person_hours():
    assert cleaning_labour_hours(120,60,3,20)==7
    with pytest.raises(ValueError): cleaning_labour_hours(100,0,1,0)


def test_allocation_preserves_budget_and_stable_ties():
    roles=[dict(id=k,weight=1,minimum_fte=1) for k in ['b','a','c']]
    assert allocate(8,roles)=={'a':3,'b':3,'c':2}
    assert allocate(8,list(reversed(roles)))==allocate(8,roles)
    with pytest.raises(ValueError): allocate(2,roles)


def test_workload_counts_inclusive_finish_and_keeps_unsized_crews_unknown():
    def task(start,end,count):
        return dict(work_center='civil',planned_start_day=start,planned_finish_day=end,
                    resource_count=count,staff_roles='lead; fitter',package_id='test')
    result=construction_workload([task(0,1,2),task(1,2,1)])[0]
    assert result['peak_concurrent_resources']==3
    assert result['resource_days']==6
    assert result['peak_day']==1
    result=construction_workload([task(0,1,'')])[0]
    assert result['peak_concurrent_resources'] is None
    assert result['resource_days'] is None
    assert result['worker_headcount'] is None


def test_separate_elevated_fragments_and_missing_cold_extreme():
    design={'climate':{'preset':'test'},'civil_segments':[
        dict(line='a',from_station_m=0,to_station_m=25,**{'class':'elevated'}),
        dict(line='a',from_station_m=100,to_station_m=125,**{'class':'elevated'})]}
    result=refinement(design,{},dict(ambient_c_average=20,ambient_c_design=50),
                      dict(investigation_flag_counts={},missing_profile_count=1))
    assert len(result['elevated_segments'])==2
    assert sum(s['plan']['bearings'] for s in result['elevated_segments'])==16
    assert all(s['hot_movement_sensitivity_mm']['10']==7.5 for s in result['elevated_segments'])
    assert all(s['cold_movement_sensitivity_mm'] is None for s in result['elevated_segments'])
    alternative=refinement(design,{},dict(ambient_c_average=20,ambient_c_design=50),
                            dict(investigation_flag_counts={},missing_profile_count=1),span_m=20,unit_spans=5)
    assert all(s['plan']['span_m']==20 and s['plan']['unit_spans']==5 for s in alternative['elevated_segments'])
    assert all(s['hot_movement_sensitivity_mm']['10']==12 for s in alternative['elevated_segments'])


def test_catalogue_role_budgets_and_new_maintenance_have_real_asset_targets():
    import json
    from engineering.analysis.city_delivery import ROOT
    paths=sorted((ROOT/'cities/catalogue').glob('*/*/*/engineering/delivery/summary.json'))
    assert len(paths)==266
    for path in paths:
        report=json.loads(path.read_text())
        # Compact review must work without the ignored full operations bundle.
        assert not any(source.endswith('.gz') for source in report['input_sha256'])
        assert any(source.endswith('-operations-manifest.json') for source in report['input_sha256'])
        org=report['organisation']; roles=org['roles']; funded=org['finance_basis']
        assert sum(r['fte'] for r in roles)==funded['total_fte']
        for group,total in funded['groups_fte'].items():
            assert sum(r['fte'] for r in roles if r['group']==group)==total
        assert next(r for r in roles if r['id']=='city-director')['fte']==1
        assert all('train-operator'!=r['id'] for r in roles)
        assert not org['roster_validated']
        counts=report['maintenance_task_counts']
        assert counts['rs-finish-seal-joint']==counts['rs-controlled-wash']>0
        assert counts['civil-joint-drain-finish']>0
        assert counts['energy-soiling-cleaning']>0
