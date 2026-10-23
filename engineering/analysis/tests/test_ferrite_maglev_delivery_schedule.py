"""Independent delivery precedence, resources, quantities and cash controls."""
from copy import deepcopy
import gzip
import json
import math

import pytest
from engineering.ferrite_maglev import delivery_schedule as d


def test_shift_and_elapsed_cure_are_different_calendars():
    assert d.work_window(7.,3.,shift=8.)==(7.,26.)
    assert d.work_window(7.,168.,continuous=True)==(7.,175.)


def test_finite_resource_slots_and_dependency_cycle_negative():
    tasks=[dict(id=k,hours=8.,depends=[],resource='crane') for k in ('a','b','c')]
    rows=d.schedule(tasks,{'crane':1});assert [r['start_h'] for r in rows]==[0.,24.,48.]
    bad=deepcopy(rows);bad[1]['start_h']=1.
    with pytest.raises(ValueError,match='overlapping'):d.verify_schedule(bad,{'crane':1})
    tasks[0]['depends']=['c'];tasks[2]['depends']=['a']
    with pytest.raises(ValueError,match='cyclic'):d.schedule(tasks,{'crane':1})


def test_complete_one_km_has_no_duplicate_support_or_beam_serial():
    value=d.construction();q=value['quantities'];rows=value['tasks'];ids={r['id']:r for r in rows}
    assert (q['bays'],q['beams'],q['supports'])==(40,80,41)
    assert len([r for r in rows if r['id'].endswith('/foundation')])==41
    assert len({r['serial'] for r in rows if r['id'].endswith('/cast')})==80
    for i in range(80):
        uid=f'beam-{i:04d}'
        assert ids[uid+'/qa']['start_h']>=ids[uid+'/cast']['end_h']+168
        assert ids[uid+'/erect']['start_h']>=ids[f'bay-{i//2+1:04d}/foundation']['end_h']
    assert not value['actual_qa_or_construction_executed'] and not value['release']


def test_full_line_counts_separate_loop_supports_and_closing_units():
    from engineering.ferrite_maglev import pilot_corridor as p
    line=p.city_line();q=d.topology_quantities(line);supports={r['id']:r for r in q['support_units']}
    assert (q['beams'],q['supports'],q['curved_beam_count'],q['closing_beam_count'])==(546,302,60,8)
    assert len(supports)==302 and len({b['id'] for b in q['beam_units']})==546
    assert sum(c['beams'] for c in q['components'] if c['curved'])==60
    assert all(len(s['terminal_loop_endpoint_bearings'])==2 for s in supports.values() if 'terminal_loop_endpoint_bearings' in s)
    assert sum('terminal_loop_endpoint_bearings' in s for s in supports.values())==2
    assert q['priced_stock_length_m']==546*25 and q['closing_stock_surplus_m']>100
    for b in q['beam_units']:assert all(s in supports for s in b['support_ids'])
    assert not q['shared_support_acceptance'] and all(not b['manufacturing_geometry_qualified'] for b in q['beam_units'])
    bad=deepcopy(line);bad['operating_plan']['terminal_loops'][1]['id']=bad['operating_plan']['terminal_loops'][0]['id']
    with pytest.raises(ValueError,match='unique'):d.topology_quantities(bad)


def test_topology_schedule_erects_each_beam_on_its_actual_two_supports():
    from engineering.ferrite_maglev import pilot_corridor as p
    q=d.topology_quantities(p.city_line());v=d.construction(quantity_plan=q);tasks={r['id']:r for r in v['tasks']}
    assert sum(r['id'].endswith('/foundation') for r in v['tasks'])==302
    assert sum(r['id'].endswith('/cast') for r in v['tasks'])==546
    for b in q['beam_units']:
        erection=tasks[b['id']+'/erect']
        for support in b['support_ids']:
            uid=support+'/foundation';assert uid in erection['depends'] and tasks[uid]['end_h']<=erection['start_h']


def test_crane_capacity_is_at_radius_and_does_not_create_acceptance():
    a=d.load();q=d.quantities(1000,a)
    assert q['crane_radius_m']==25 and not q['crane_chart_verified']
    expected=(q['beam_concrete_m3']*2500+d.geometry.guideway_quantities()['magnetic_rail_mass_kg'])/1000
    assert q['maximum_lift_t']==pytest.approx((expected+4)*1.1)
    a['assumed_chart_capacity_t_at_radius']=1.
    assert not d.construction(a=a)['planning_readiness']


def test_shared_factory_is_allocated_once_with_separate_origin_and_training():
    a=d.load();shares=[d.factory_allocation(k,a) for k in (6.,24.,70.)]
    assert sum(r['allocated_factory_usd'] for r in shares)==pytest.approx(a['shared_factory_capital_usd'])
    for r in shares:
        assert sum(r[k] for k in ('imported_finished_usd','imported_inputs_usd','local_process_usd'))==pytest.approx(r['allocated_factory_usd'])
        assert r['verified_domestic_value_added_fraction'] is None and not r['training_executed']
    with pytest.raises(ValueError):d.factory_allocation(101.)


def test_rework_retains_same_serial_retest_and_actual_cost():
    value=d.construction(scenario='rework');rows={r['id']:r for r in value['tasks']}
    for i in range(0,80,10):
        uid=f'beam-{i:04d}';assert rows[uid+'/transport']['depends']==[uid+'/retest']
        assert rows[uid+'/rework']['serial']==rows[uid+'/cast']['serial']
    assert sum(r['task_cost_usd'] for r in value['monthly_task_cash'])==pytest.approx(sum(r['cost_usd'] for r in rows.values()))


def test_published_receipt_recalculates_schedule_and_rejects_rehashed_claim(tmp_path,monkeypatch):
    d.publish(tmp_path);value=d.study();original=d.study;calls=[]
    def counted():calls.append(True);return original()
    monkeypatch.setattr(d,'study',counted);summary=d.read_summary(tmp_path)
    assert len(calls)==1 and len(summary['scenarios'])==len(value['cases'])
    value['cases'][0]['actual_qa_or_construction_executed']=True
    (tmp_path/'study.json.gz').write_bytes(gzip.compress(d.encoded(value),mtime=0))
    m=json.loads((tmp_path/'manifest.json').read_bytes());m['files_sha256']['study.json.gz']=d.digest(tmp_path/'study.json.gz');(tmp_path/'manifest.json').write_bytes(d.encoded(m))
    with pytest.raises(ValueError,match='recalculation'):d.verify(tmp_path)
