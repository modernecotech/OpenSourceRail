"""Soil screening must retain units, uncertainty, coverage and receipt integrity."""
import json
import math
from pathlib import Path
import pytest
from engineering.analysis import city_soils as soils
from engineering.analysis import survey_package, route_station_fit, surveyed_alignment


def test_density_scale_is_converted_once_and_nodata_is_unknown():
    assert soils.decode(150, False, .01, 0, 'bd.core') == 1500
    assert soils.decode(72, False, .1, 0, 'ph.h2o') == 7.2
    assert soils.decode(32767, True, .01, 0, 'bd.core') is None
    with pytest.raises(ValueError): soils.decode(math.nan, False, 1, 0, 'clay')
    with pytest.raises(ValueError): soils.decode(101, False, 1, 0, 'sand')


def test_uncertainty_triggers_investigation_without_inventing_strength():
    values = {p+'_'+s: 10 for p in soils.PROPERTIES for s in soils.STATS}
    values.update(clay_mean=20, clay_p84=40, soc_p84=60)
    flags = soils.investigation_flags({'0..30cm':values})
    assert 'fine-soil-plasticity-and-shrink-swell-tests' in flags
    assert 'organic-content-and-compressibility-tests' in flags
    values['sand_p16'] = None
    assert 'coverage-gap' in soils.investigation_flags({'0..30cm':values})
    values['clay_p16'] = 45
    assert 'invalid-prediction-interval' in soils.investigation_flags({'0..30cm':values})


@pytest.mark.parametrize('writer', [
    lambda p: survey_package.write_manifest(p, []),
    lambda p: route_station_fit.write_placeholder_manifest(p, {'input':[]}),
    lambda p: surveyed_alignment.write_placeholder_manifest(p, [], {'global_input':[], 'line_input':[]}),
])
def test_regeneration_preserves_received_manifest(tmp_path, writer):
    path = tmp_path / 'received.csv'
    original = b'file_role,sha256,acceptance_status\nfield-survey,controlled-hash,accepted\n'
    path.write_bytes(original)
    writer(path)
    assert path.read_bytes() == original


def test_locations_cover_every_station_and_segment_with_bounded_spacing():
    city = soils.ROOT / 'cities/catalogue/west-asia/Iraq/Samawah'
    points = soils.sample_locations(city)
    segments = json.loads((city / 'engineering/gis/layers/civil_segments.geojson').read_text())['features']
    stations = json.loads((city / 'engineering/gis/layers/stations.geojson').read_text())['features']
    assert {p['scope_id'] for p in points if p['scope_type']=='station'} == {s['properties']['id'] for s in stations}
    for feature in segments:
        prop=feature['properties']; found=[p for p in points if p['scope_type']=='civil_segment' and p['scope_id']==prop['id']]
        chainages=sorted(p['chainage_m'] for p in found)
        assert len(found)>=3
        assert chainages[0]==pytest.approx(prop['from_chainage_m'],abs=.001)
        assert chainages[-1]==pytest.approx(prop['to_chainage_m'],abs=.001)
    assert len({p['sample_id'] for p in points}) == len(points)


def test_catalogue_samples_are_bound_to_current_routes_and_retain_unknowns():
    # Independent checks over the actual retained source data and derived scope.
    import csv
    for path in (soils.ROOT/'cities/catalogue').glob('*/*/*/engineering/soil/summary.json'):
        report=json.loads(path.read_text());folder=path.parent
        receipt=json.loads((folder/'source-receipt.json').read_text())
        assert report['samples_sha256']==receipt['samples_sha256']==soils.sha(folder/'samples.csv')
        assert receipt['input_sha256']['design']==soils.sha(folder.parents[1]/'design.toml')
        assert report['ground_design_validated'] is False
        assert report['deployment_release_ready'] is False
        plan=json.loads((folder/'civil-investigation-plan.json').read_text())
        assert all(s['allowable_bearing_kpa'] is None and s['groundwater_depth_m'] is None and s['foundation_type'] is None for s in plan['scopes'])
        with (folder/'samples.csv').open() as handle:rows=list(csv.DictReader(handle))
        assert len(rows)==3*report['sample_count']
        missing={r['sample_id'] for r in rows if any(r[p+'_'+s]=='' for p in soils.PROPERTIES for s in soils.STATS)}
        assert len(missing)==report['missing_profile_count']
