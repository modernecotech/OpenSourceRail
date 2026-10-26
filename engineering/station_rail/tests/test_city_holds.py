"""City publication stops at preserved geography until physical gates exist."""
from copy import deepcopy
from hashlib import sha256
import json

import pytest

from engineering.station_rail import cities, FLAGS
from engineering.station_rail.common import identity


@pytest.fixture
def context(tmp_path,monkeypatch):
    from engineering.development_baseline import selection
    spec=dict(family='wheel_rail_station_lim')
    car=dict(candidate_id='a'*64,body_candidate_id='b'*64,support_component_id='c'*64,
             propulsion_component_id='d'*64,mass=dict(accounted_tare_kg_per_car=22000.))
    baseline=dict(selection_id=identity(spec),selection=spec,vehicle=car,source_sha256={},**FLAGS)
    monkeypatch.setattr(selection,'load',lambda root:baseline)
    city=tmp_path/'cities/catalogue/fixture/country/City';(city/'engineering/maglev').mkdir(parents=True)
    (city/'engineering/current').mkdir()
    (city/'city.json').write_text(json.dumps(dict(name='City',city=dict(slug='city',country='country'))))
    (city/'engineering/maglev/network.svg').write_text('<svg>Underlying streets and city detail</svg>')
    (city/'engineering/maglev/summary.json').write_text(json.dumps(dict(lines=[dict(line='line-1',stations=[dict(id='a',s_m=0.),dict(id='b',s_m=2500.)])])))
    (city/'engineering/current/summary.json').write_text('{"historical_fleet":906}')
    (city/'README.md').write_text('Historical city front page\n')
    for name in ('engineering/station_rail/brief.toml','engineering/station_rail/__init__.py',
                 'engineering/station_rail/common.py',cities.CODE,'engineering/development_baseline/cities.py'):
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('fixture source\n')
    return tmp_path,baseline,city


def test_city_returns_bound_hold_without_reusing_old_performance(context):
    root,baseline,city=context
    value=cities.evaluate_city('city',baseline,root=root)
    assert value['execution']=='held'
    assert value['performance_evaluated'] is False
    assert value['totals'] is None
    assert value['geography']['map_available'] is True
    assert value['geography']['underlying_city_details_preserved'] is True
    assert value['historical']['selected_for_v06'] is False
    assert value['support_component_id']==baseline['vehicle']['support_component_id']
    assert 'magnet_component_id' not in value
    assert value['physical_accepted'] is False


def test_publish_all_writes_global_register_and_preserves_city_bytes(context):
    root,baseline,city=context
    before={p.relative_to(city):sha256(p.read_bytes()).hexdigest() for p in city.rglob('*') if p.is_file()}
    index=cities.publish_all(root=root,baseline=baseline)
    assert index['city_count']==1
    assert index['summary']['cities_held']==1
    assert index['longest_gap']['distance_m']==2500.
    assert index['route_geography']['performance_models_executed']==0
    assert index['city_performance_packages_written']==0
    assert index['cities'][0]['summary_path'] is None
    assert index['cities'][0]['totals'] is None
    assert cities.verify_all(root=root)['verified'] is True
    assert before=={p.relative_to(city):sha256(p.read_bytes()).hexdigest() for p in city.rglob('*') if p.is_file()}
    value=cities.publish_city('city',root=root,update_readme=True)
    assert value['execution']=='held'
    assert before=={p.relative_to(city):sha256(p.read_bytes()).hexdigest() for p in city.rglob('*') if p.is_file()}


def test_catalogue_and_city_reject_identity_and_acceptance_tampering(context):
    root,baseline,_=context
    bad=deepcopy(baseline);bad['vehicle']['support_component_id']='0'*64
    with pytest.raises(ValueError,match='identity differs'):cities.evaluate_city('city',bad,root=root)
    cities.publish_all(root=root)
    path=root/cities.INDEX_MANIFEST;receipt=json.loads(path.read_bytes());receipt['physical_accepted']=True
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='qualification'):cities.verify_all(root=root)


def test_catalogue_never_falls_back_to_historical_city(context):
    root,_,_=context
    with pytest.raises(FileNotFoundError,match='has not been generated'):cities.read_catalogue(root)
