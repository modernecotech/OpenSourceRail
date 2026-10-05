from collections import Counter
from copy import deepcopy
from pathlib import Path
import tomllib

import pytest

from osr_scenario.stabling import distributed_candidate
from osr_scenario.stabling_hybrid import station_and_depot_allocation

ROOT = Path(__file__).resolve().parents[3]


def inputs():
    folder = ROOT / 'cities/catalogue/west-asia/Iraq/Samawah'
    design = tomllib.loads((folder / 'design.toml').read_text())
    candidate, _ = distributed_candidate((folder / 'samawah.toml').read_text(), design['fleets'])
    profiles = tomllib.loads((ROOT / 'lib/templates/rolling-stock.toml').read_text())['profiles']
    return tomllib.loads(candidate), design, profiles


def test_samawah_station_launch_stock_and_depot_remainder():
    doc, design, profiles = inputs()
    report = station_and_depot_allocation(doc, design, profiles)
    assert report['allocation_passed']
    assert report['fleet_trainsets']==sum(f['trainset_count'] for f in design['fleets'])
    assert report['station_trainsets']+report['depot_trainsets']==report['fleet_trainsets']
    assert set(report['station_trainsets_by_location'].values()) == {2}
    station = [r for r in report['allocations'] if r['location_type'] == 'station']
    assert all(r['service_role'] == 'revenue' for r in station)
    assert sum(r['stabling_positions_required'] for r in report['depot_requirements'])==report['depot_trainsets']
    roles = Counter()
    for depot in report['depot_requirements']:
        roles.update(depot['service_roles'])
        assert depot['verified_stabling_positions'] is None
        assert len(depot['lines']) == 1
    assert roles['spare']==sum(f.get('spare_count',0) for f in doc['fleets'])
    assert roles['cold_reserve']==sum(f.get('cold_reserve_count',0) for f in doc['fleets'])
    assert roles['revenue']+report['station_trainsets']==sum(f['trainset_count']-f.get('spare_count',0)-f.get('cold_reserve_count',0) for f in doc['fleets'])
    assert sum(r['usable_stabling_length_required_m'] for r in report['depot_requirements'])==report['depot_trainsets']*(profiles[design['lines'][0]['rolling_stock']]['length_m']+10)
    assert sum(r['workshop_bays'] for r in report['depot_requirements'])==sum(r['fleet_stalls'] for r in design['depots'])
    assert not report['physical_release_ready']
    assert report['depot_access_requirements'] == []
    lines = {l['id']: {s['id'] for s in l['stations']} for l in doc['lines']}
    assert all(r['station'] in lines[r['line']] for r in report['allocations'])


def test_stock_is_conserved_per_line_and_role():
    doc, design, profiles = inputs()
    report = station_and_depot_allocation(doc, design, profiles)
    assigned = Counter()
    for row in report['allocations']:
        assigned[row['line'], row['service_role']] += row['trainset_count']
    for fleet in doc['fleets']:
        assert assigned[fleet['line'], 'spare'] == fleet['spare_count']
        assert assigned[fleet['line'], 'cold_reserve'] == fleet['cold_reserve_count']
        assert sum(n for (line, _), n in assigned.items() if line == fleet['line']) == fleet['trainset_count']


def test_missing_depot_cannot_be_silently_invented():
    doc, design, profiles = inputs()
    design['depots'] = []
    with pytest.raises(ValueError, match='declared depot'):
        station_and_depot_allocation(doc, design, profiles)


def test_revenue_shortage_retains_inventory_and_reports_missing_directions():
    doc, design, profiles = inputs()
    doc = deepcopy(doc)
    doc['fleets'][0]['trainset_count'] = doc['fleets'][0]['spare_count'] + doc['fleets'][0]['cold_reserve_count'] + 1
    report = station_and_depot_allocation(doc, design, profiles)
    assert report['capacity']['inventory_complete']
    assert report['missing_morning_directions']
    assert not report['allocation_passed']


def test_samawah_native_candidate_uses_local_storage_without_new_line_connections():
    from osr_scenario.stabling_hybrid import native_hybrid_candidate
    doc, design, profiles = inputs()
    path = ROOT / 'cities/catalogue/west-asia/Iraq/Samawah/samawah.toml'
    source, _ = distributed_candidate(path.read_text(), design['fleets'])
    allocation = station_and_depot_allocation(doc, design, profiles)
    result = tomllib.loads(native_hybrid_candidate(source, allocation))
    assert result['lines'] == doc['lines']
    assert result['sites'] == doc['sites']
    assert sum(s.get('depot_stabling_positions', 0) for s in result['stations']) == allocation['depot_trainsets']
    assert sum(s.get('is_depot', False) for s in result['stations']) == 3


def test_connected_native_candidate_preserves_service_energy_and_inventory():
    from osr_scenario.stabling_hybrid import native_hybrid_candidate
    path = next(ROOT.glob('cities/catalogue/*/*/*/uige.toml'))
    design = tomllib.loads(path.with_name('design.toml').read_text())
    source, _ = distributed_candidate(path.read_text(), design['fleets'])
    doc = tomllib.loads(source)
    profiles = inputs()[2]
    allocation = station_and_depot_allocation(doc, design, profiles)
    result = tomllib.loads(native_hybrid_candidate(source, allocation))
    assert {k: v for k, v in result.items() if k not in ('fleets', 'stations')} == {
        k: v for k, v in doc.items() if k not in ('fleets', 'stations')}
    for old, new in zip(doc['fleets'], result['fleets']):
        assert {k: v for k, v in new.items() if k != 'overnight_allocations'} == old
        assert sum(r['trainset_count'] for r in new['overnight_allocations']) == old['trainset_count']
    for old, new in zip(doc['stations'], result['stations']):
        assert {k: v for k, v in new.items() if k != 'depot_stabling_positions'} == old
    assert sum(s.get('depot_stabling_positions', 0) for s in result['stations']) == allocation['depot_trainsets']
