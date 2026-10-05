"""Accounting regressions: multi-hop transfers, native counts and union access."""
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/automation'))
from city_access import EARTH_RADIUS_M, population_audit, transfer_audit


def test_three_line_chain_counts_indirect_reachability():
    design = dict(lines=[dict(id=name) for name in 'ABCD'],
                  interchanges=[dict(lines=['A', 'B'])],
                  stations=[dict(id='B1', line='B', junction_group=0),
                            dict(id='C1', line='C', junction_group=0)])
    graph = transfer_audit(design)
    assert graph['direct_transfer_fraction'] == pytest.approx(2/6)
    assert graph['reachable_line_pair_fraction'] == pytest.approx(3/6)
    assert graph['reachable_with_at_most_two_transfers_fraction'] == pytest.approx(3/6)
    assert graph['components'] == [['A', 'B', 'C'], ['D']]
    assert next(row for row in graph['pairs'] if row['lines'] == ['A', 'C'])['minimum_transfers'] == 2


def test_geometric_crossing_does_not_create_a_transfer():
    graph = transfer_audit(dict(lines=[dict(id='A'), dict(id='B')], stations=[]))
    assert graph['reachable_line_pair_fraction'] == 0
    assert transfer_audit(dict(lines=[]))['reachable_line_pair_fraction'] is None
    assert transfer_audit(dict(lines=[dict(id='A')]))['reachable_line_pair_fraction'] == 1


def test_population_is_counted_once_without_catalogue_scaling():
    design = dict(city=dict(population=999999), stations=[dict(lat=0., lon=0.), dict(lat=0., lon=.001)])
    # Native counts include a high-population far cell and a missing cell;
    # averaging the cells or multiplying by city population gives wrong answers.
    report = population_audit([0, 0, 0, 0], [0, .001, .02, .002],
                              [10, 20, 70, 900], [True, True, True, False], design, (500, 3000))
    assert report['bbox_population_2020'] == 100
    assert report['catchments'][0]['covered_population_2020'] == 30
    assert report['catchments'][0]['fraction_of_raster_population'] == .3
    assert report['catchments'][1]['covered_population_2020'] == 100
    assert report['missing_pixels'] == 1


def test_spherical_distance_and_no_stations_or_positive_population():
    design = dict(city=dict(population=100), stations=[dict(lat=70., lon=179.999)])
    result = population_audit([70.], [-179.999], [5.], [True], design, (100,))
    assert result['catchments'][0]['covered_population_2020'] == 5
    design['stations'] = []
    assert population_audit([0], [0], [5], [True], design)['catchments'][0]['covered_population_2020'] == 0
    assert population_audit([0], [0], [0], [True], design)['catchments'][0]['fraction_of_raster_population'] is None
    with pytest.raises(ValueError):
        population_audit([0], [0], [-1], [True], design)


def test_retained_native_window_preserves_pixel_counts(tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    spec = importlib.util.spec_from_file_location('access_audit_test', ROOT/'tools/automation/audit-city-access.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raster = tmp_path/'irq_ppp_2020_constrained.tif'
    with rasterio.open(raster, 'w', driver='GTiff', height=2, width=2, count=1,
                       dtype='float32', crs='EPSG:4326', transform=from_origin(0, 2, 1, 1), nodata=-999) as dst:
        dst.write(np.array([[10, 20], [30, -999]], dtype='float32'), 1)
    design = dict(city=dict(bbox=dict(west=0, south=0, east=2, north=2)))
    module.retain_population(design, tmp_path, raster)
    import gzip
    import io
    with np.load(io.BytesIO(gzip.decompress((tmp_path/'population-pixels.npz.gz').read_bytes()))) as values:
        assert values['counts'].sum() == 60
        assert values['valid'].sum() == 3


def test_disconnected_recovery_candidates_never_create_a_transfer():
    from city_access import transfer_audit,transfer_recovery_candidates
    design=dict(lines=[dict(name='a'),dict(name='b'),dict(name='c')],interchanges=[],stations=[
        dict(id='a1',line='a',lat=0,lon=0),dict(id='b1',line='b',lat=0,lon=.001),
        dict(id='c1',line='c',lat=0,lon=.002)])
    before=transfer_audit(design)
    candidates=transfer_recovery_candidates(design)
    assert len(candidates)==2
    assert all(100<r['straight_distance_m']<120 and not r['transfer_created'] for r in candidates)
    assert before==transfer_audit(design)
    assert before['reachable_line_pair_fraction']==0
