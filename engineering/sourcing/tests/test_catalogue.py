from copy import deepcopy
import json
from pathlib import Path

import pytest

from engineering.sourcing.catalogue import load_catalogue, seed
from engineering.sourcing.database import Store
from engineering.sourcing.model import FLAGS, validate_record

SUPPLIERS = Path(__file__).resolve().parents[1] / "data/supplier-catalogue.json"


def raw_seed():
    return dict(schema="osr-sourcing-seed/1", sources={"test.source":dict(publisher="Test manufacturer",url="https://example.com/product",retrieved_at="2026-10-29",access="Test fixture, not physical evidence",source_kind="manufacturer_catalogue")},
        products=[dict(product_key="TEST-1",manufacturer="Test manufacturer",part_number="A1",category="test",supply_scope="raw-material",description="Unit fixture",specifications={},source_keys=["test.source"])],
        offers=[dict(product_key="TEST-1",source_key="test.source",price_date="2026-10-29",currency="GBP",quantity_unit="kg",source_class="B",minimum_order_quantity=None,order_multiple=None,tax_basis="excluded",tax_rate=None,valid_until=None,tiers=[dict(minimum_quantity="0",maximum_quantity=None,unit_price="2.50")])])


def write_seed(path, data):
    path.write_text(json.dumps(data));return path


def test_actual_catalogue_scopes_prices_and_half_open_breaks():
    values=load_catalogue([SUPPLIERS]);products={v['product_key']:v for v in values if v['kind']=='product'}
    assert len(products)==14
    assert sum(v['kind']=='source' for v in values)==15
    offers={v['product_id']:v for v in values if v['kind']=='offer'}
    assert len(offers)==5
    cloth=offers[products['EC-GF-BA-440-127']['record_id']]
    assert [t['minimum_quantity'] for t in cloth['tiers']]==['0','5','10','101']
    assert [t['maximum_quantity'] for t in cloth['tiers']]==['5','10','101',None]
    assert cloth['tiers'][0]['unit_price']=='4.05' and cloth['tiers'][-1]['unit_price']=='3.1'
    assert cloth['minimum_order_quantity'] is None and cloth['order_multiple'] is None
    assert cloth['quantity_unit']=='m' and cloth['tax_basis']=='excluded'
    assert products['EC-GF-BA-440-127']['specifications']['fabric_width_m']['value']=='1.27'
    assert products['EC-VP-EC20-1']['specifications']['mass_kg']['value'] is None
    assert products['EC-VP-EC20-1']['specifications']['shipping_gross_mass_kg']['scope']=='shipping-gross'
    assert products['WABTEC-ESP4C-1300']['specifications']['mass_kg']['scope']=='mechanism-and-hanger-only'
    assert products['THERMOKING-LRV8T']['specifications']['hot_55C_performance'] is None
    assert products['LONGI-LR7-60HVHL-560M']['supply_scope']=='solar-module'
    for value in values:
        validate_record(value)
        assert all(value[key] is flag for key,flag in FLAGS.items())


def test_seed_references_are_atomic_and_repeatable(tmp_path):
    with Store(tmp_path/'sourcing.db') as store:
        first=seed(store,[SUPPLIERS]);second=seed(store,[SUPPLIERS])
        assert first['added_count']==first['record_count']==34
        assert second['added_count']==0
        assert first['record_ids']==second['record_ids']
        for offer in store.all('offer'):
            product=store.get(offer['product_id'],'product')
            assert offer['source_id'] in product['source_ids']


def test_load_returns_copies(tmp_path):
    path=write_seed(tmp_path/'seed.json',raw_seed());a=load_catalogue([path]);a[0]['publisher']='mutated'
    assert load_catalogue([path])!=a


def test_identical_aliases_and_products_coalesce(tmp_path):
    a=write_seed(tmp_path/'a.json',raw_seed());b=write_seed(tmp_path/'b.json',raw_seed())
    assert len(load_catalogue([a,b]))==3


@pytest.mark.parametrize('mutator,match',[
    (lambda s:s['sources']['test.source'].update(publisher='Different'), 'Conflicting source'),
    (lambda s:s['products'][0].update(part_number='OTHER'), 'Conflicting product'),
])
def test_conflicting_source_or_product_keys_rejected(tmp_path,mutator,match):
    one=raw_seed();two=deepcopy(one);mutator(two)
    paths=[write_seed(tmp_path/'a.json',one),write_seed(tmp_path/'b.json',two)]
    with pytest.raises(ValueError,match=match):load_catalogue(paths)


@pytest.mark.parametrize('mutator,match',[
    (lambda s:s['products'][0].update(source_keys=['absent']), 'Unknown catalogue source'),
    (lambda s:s['offers'][0].update(product_key='absent'), 'Unknown offer product'),
    (lambda s:s['offers'][0].update(part_number='OTHER'), 'identity mismatch'),
    (lambda s:s['sources']['test.source'].update(source_kind='commodity_benchmark'), 'benchmarks cannot'),
    (lambda s:s['sources']['test.source'].update(physical_accepted=True), 'acceptance'),
    (lambda s:s['products'][0].update(source_ids=['a'*64]), 'declared aliases'),
    (lambda s:s['products'][0].update(kind='offer'), 'computed'),
    (lambda s:s.update(offres=[]), 'Unknown catalogue seed collection'),
])
def test_invalid_seed_is_not_a_partial_import(tmp_path,mutator,match):
    data=raw_seed();mutator(data);path=write_seed(tmp_path/'bad.json',data)
    with Store(tmp_path/'empty.db') as store:
        with pytest.raises(ValueError,match=match):seed(store,[path])
        assert store.all()==[]


def test_offer_cannot_point_to_an_unrelated_page(tmp_path):
    data=raw_seed();data['sources']['other']=dict(data['sources']['test.source'],url='https://example.com/unrelated')
    data['offers'][0]['source_key']='other'
    with pytest.raises(ValueError,match='exact product'):load_catalogue([write_seed(tmp_path/'bad.json',data)])


def test_fx_and_process_aliases_resolve_and_source_type_is_checked(tmp_path):
    data=raw_seed();data['sources']['rates']=dict(data['sources']['test.source'],source_kind='exchange_rate')
    data['fx']=[dict(source_key='rates',rate_date='2026-10-28',base_currency='EUR',quote_currency='GBP',rate='0.88')]
    data['processes']=[dict(source_keys=['test.source'],process_key='test-process',complete_output_units=None)]
    values=load_catalogue([write_seed(tmp_path/'valid.json',data)])
    assert any(v['kind']=='fx' for v in values) and any(v['kind']=='process' for v in values)
    data['fx'][0]['source_key']='test.source'
    with pytest.raises(ValueError,match='exchange-rate'):load_catalogue([write_seed(tmp_path/'invalid.json',data)])
