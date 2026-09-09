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
    assert (report['station_trainsets'], report['depot_trainsets'], report['fleet_trainsets']) == (40, 68, 108)
    assert set(report['station_trainsets_by_location'].values()) == {2}
    station = [r for r in report['allocations'] if r['location_type'] == 'station']
    assert len(station) == 34
    assert all(r['service_role'] == 'revenue' for r in station)
    depot, = report['depot_requirements']
    assert depot['service_roles'] == {'revenue': 57, 'spare': 8, 'cold_reserve': 3}
    assert depot['stabling_positions_required'] == 68
    assert depot['usable_stabling_length_required_m'] == 4046
    assert depot['workshop_bays'] == 17
    assert depot['verified_stabling_positions'] is None
    assert not report['physical_release_ready']
    assert [(r['line'], r['trainsets']) for r in report['depot_access_requirements']] == [('line-2', 16), ('line-3', 15)]


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


def test_native_candidate_rejects_samawah_missing_interline_access():
    from osr_scenario.stabling_hybrid import native_hybrid_candidate
    doc, design, profiles = inputs()
    allocation = station_and_depot_allocation(doc, design, profiles)
    with pytest.raises(ValueError, match='interline depot access'):
        native_hybrid_candidate('', allocation)


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
