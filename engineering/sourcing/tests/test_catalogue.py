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
    assert len(products)==16
    assert sum(v['kind']=='source' for v in values)==56
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
    assert products['WABTEC-ESP4C-1300']['specifications']['mass_kg']['scope']=='door-mechanism'
    assert products['WABTEC-ESP4C-1300']['specifications']['mass_kg']['scope_detail']=='mechanism-and-hanger-only'
    assert products['THERMOKING-LRV8T']['specifications']['hot_55C_performance'] is None
    assert products['LONGI-LR7-60HVHL-560M']['supply_scope']=='solar-module'
    foam=products['GURIT-CORECELL-M80']
    assert foam['specifications']['density_min_kg_m3']['value']=='81'
    assert foam['specifications']['density_max_kg_m3']['value']=='89'
    assert foam['specifications']['published_observations']['thickness_range_mm']==['3','53']
    assert not [v for v in values if v['kind']=='offer' and v['product_id']==foam['record_id']]
    for value in values:
        validate_record(value)
        assert all(value[key] is flag for key,flag in FLAGS.items())


def test_seed_references_are_atomic_and_repeatable(tmp_path):
    with Store(tmp_path/'sourcing.db') as store:
        first=seed(store,[SUPPLIERS]);second=seed(store,[SUPPLIERS])
        assert first['added_count']==first['record_count']==281
        assert second['added_count']==0
        assert first['record_ids']==second['record_ids']
        for offer in store.all('offer'):
            product=store.get(offer['product_id'],'product')
            assert offer['source_id'] in product['source_ids']


def test_iraqi_2024_private_building_material_ratios_retain_method_and_table_totals():
    values=load_catalogue([SUPPLIERS])
    sources={value['source_key']:value for value in values if value['kind']=='source'}
    benchmarks={value['benchmark_key']:value for value in values if value['kind']=='benchmark'}
    source=sources['iraq.cso.private-construction-estimates-2024']
    assert source['document_sha256']=='d7bba757619b67a1cb05939a51a30cb08f292df0db6c2b9953ebf8b8ee354770'
    assert '2012 private-building survey' in source['methodology']
    assert 'Kurdistan Region is excluded' in source['access']
    expected={
        'baghdad:cement-ordinary':('115000','t','24427840','212416'),
        'baghdad:cement-resistant':('140000','t','9108540','65061'),
        'baghdad:grit-normal':('20000','m3','6059900','302995'),
        'baghdad:grit-broken':('22000','m3','3214508','146114'),
        'baghdad:sand-red':('22000','m3','13552','616'),
        'baghdad:sand-black':('20000','m3','10960','548'),
        'iraq-total:cement-ordinary':('114672.74','t','74711351','651518'),
        'iraq-total:sand-red':('18504.52','m3','34770','1879'),
    }
    assert len([key for key in benchmarks if key.startswith('iq-cso-2024-private-building-estimate:')])==14
    for suffix,(rate,unit,cost,quantity) in expected.items():
        row=benchmarks['iq-cso-2024-private-building-estimate:'+suffix]
        assert row['unit_price']==rate
        assert row['quantity_unit']==unit
        assert row['source_table_estimated_cost_thousand_iqd']==cost
        assert row['source_table_estimated_quantity']==quantity
        assert row['supplier_quote'] is False
        assert row['target_installed_rate'] is False
        assert 'not a transaction' in row['cost_scope']
    assert not [row for row in values if row['kind']=='offer' and
                row.get('source_id')==sources['iraq.cso.private-construction-estimates-2024']['record_id']]


def test_additional_iraqi_aluminium_sources_are_leads_not_offers():
    values=load_catalogue([SUPPLIERS])
    sources={value['source_key']:value for value in values if value['kind']=='source'}
    products={value['product_key']:value for value in values if value['kind']=='product'}
    offers=[value for value in values if value['kind']=='offer']
    keys={'iraq.asia-aluminium','iraq.alko-aluminium','iraq.baxi-siwail-aluminium','iraq.ii-alco-aluminium'}
    assert keys <= sources.keys()
    new_source_ids={sources[key]['record_id'] for key in keys}
    assert not any(source_id in product['source_ids'] for source_id in new_source_ids for product in products.values())
    assert not any(offer['source_id'] in new_source_ids for offer in offers)
    for key in keys:
        source=sources[key]
        assert source['source_kind']=='factory_catalogue'
        assert 'price' in source['access'].lower()
        assert 'qualification' in source['access'].lower()


def test_additional_iraqi_industry_sources_are_discovery_leads_not_products_or_offers():
    values=load_catalogue([SUPPLIERS])
    sources={value['source_key']:value for value in values if value['kind']=='source'}
    products={value['product_key']:value for value in values if value['kind']=='product'}
    offers=[value for value in values if value['kind']=='offer']
    keys={
        'iraq.mim-industrial-platform',
        'iraq.duraid-al-sudani-metal-fabrication',
        'iraq.ms-cable-busbar',
        'iraq.diyala-transformers',
        'iraq.qaiwan-steel-rebar',
    }
    assert keys <= sources.keys()
    source_ids={sources[key]['record_id'] for key in keys}
    assert not any(source_id in product['source_ids'] for source_id in source_ids for product in products.values())
    assert not any(offer['source_id'] in source_ids for offer in offers)
    assert sources['iraq.mim-industrial-platform']['source_kind']=='industrial_directory'
    assert all(sources[key]['source_kind'] in {'factory_catalogue','manufacturer_catalogue'}
               for key in keys-{'iraq.mim-industrial-platform'})
    for key in keys:
        assert any(term in sources[key]['access'].lower()
                   for term in ('unverified','unconfirmed','confirm'))


def test_new_iraqi_concrete_and_factory_payroll_sources_keep_their_limits():
    values=load_catalogue([SUPPLIERS])
    sources={value['source_key']:value for value in values if value['kind']=='source'}
    offers=[value for value in values if value['kind']=='offer']
    benchmarks={value['benchmark_key']:value for value in values if value['kind']=='benchmark'}
    ready_mix=sources['iraq.sc-dpi-ready-mix']
    assert ready_mix['source_kind']=='factory_catalogue'
    assert '60-120 m3/h' in ready_mix['access']
    assert 'does not represent a precast beam' in ready_mix['access']
    assert not any(value['source_id']==ready_mix['record_id'] for value in offers)
    assert sources['iraq.cosit.import-report-2025']['source_kind']=='national_statistic'
    assert 'contributes no unit-value observations' in sources['iraq.cosit.import-report-2025']['access']
    assert sources['iraq.moch.price-analysis-bulletin-preparation-2026-09']['source_kind']=='national_statistic'
    annual_large=benchmarks['iq-cso-industrial-2024:large-establishment-average-annual-pay']
    annual_medium=benchmarks['iq-cso-industrial-2024:medium-establishment-average-annual-pay']
    assert (annual_large['unit_price'],annual_large['quantity_unit'])==('12500000','person-year')
    assert (annual_medium['unit_price'],annual_medium['quantity_unit'])==('6300000','person-year')
    assert 'not an hourly fabrication wage' in annual_large['cost_scope']
    assert 'not an hourly fabrication wage' in annual_medium['cost_scope']


def test_domestic_cable_composite_and_copper_leads_are_not_products_or_prices():
    values=load_catalogue()
    sources={value['source_key']:value for value in values if value['kind']=='source'}
    products={value['product_key']:value for value in values if value['kind']=='product'}
    offers=[value for value in values if value['kind']=='offer']
    keys={'iraq.alrowad-cables','iraq-nubin-grp-facade','iraq.dici-copper-wire-line'}
    assert keys <= sources.keys()
    source_ids={sources[key]['record_id'] for key in keys}
    assert not any(source_id in product['source_ids'] for source_id in source_ids for product in products.values())
    assert not any(offer['source_id'] in source_ids for offer in offers)
    assert 'southern Baghdad' in sources['iraq.alrowad-cables']['access']
    assert 'rail-body capability' in sources['iraq-nubin-grp-facade']['access']
    assert 'not verified commissioning' in sources['iraq.dici-copper-wire-line']['access']
    assert sources['iraq.dici-copper-wire-line']['source_kind']=='industrial_directory'


def test_iraq_july_2026_material_origins_and_governorate_wages_are_statistical_inputs():
    values=load_catalogue()
    sources={value['source_key']:value for value in values if value['kind']=='source'}
    benchmarks={value['benchmark_key']:value for value in values if value['kind']=='benchmark'}
    source=sources['iraq.cso.regional-materials-wages-2026-07']
    assert source['source_kind']=='national_statistic'
    assert source['observation_period']=='2026-07'
    assert len([key for key in benchmarks if key.startswith('iq-cso-2026-07:')])==106
    expected_materials={
        'iq-cso-2026-07:iraq-origin:material:cement-ordinary':('105000','t'),
        'iq-cso-2026-07:iraq-origin:material:sand-red':('20000','m3'),
        'iq-cso-2026-07:iraq-origin:material:gravel-crushed':('22000','m3'),
        'iq-cso-2026-07:iraq-origin:material:rebar':('965000','t'),
        'iq-cso-2026-07:arab-origin:material:rebar':('1020000','t'),
        'iq-cso-2026-07:foreign-origin:material:rebar':('1056000','t'),
        'iq-cso-2026-07:iraq-origin:material:steel-i-beam':('17000','m'),
    }
    for key,(price,unit) in expected_materials.items():
        row=benchmarks[key]
        assert (row['unit_price'],row['quantity_unit'])==(price,unit)
        assert row['source_id']==source['record_id']
        assert row['supplier_quote'] is False
        assert row['target_installed_rate'] is False
    wage_keys=[key for key in benchmarks if key.startswith('iq-cso-2026-07:') and ':wage:' in key]
    assert len(wage_keys)==90
    assert benchmarks['iq-cso-2026-07:baghdad:wage:skilled:hour-8h-day']['unit_price']=='9375'
    assert benchmarks['iq-cso-2026-07:al-muthanna:wage:skilled:hour-8h-day']['unit_price']=='7500'
    assert benchmarks['iq-cso-2026-07:salah-al-din:wage:skilled:hour-8h-day']['unit_price']=='5000'
    assert all(benchmarks[key]['employer_burden_included'] is False for key in wage_keys)
    assert sources['iraq.scosi-extrusion-press-components-2026-03']['source_kind']=='factory_catalogue'
    assert sources['iraq.icsc-samawa-cement-plant']['source_kind']=='manufacturer_catalogue'
    assert not [row for row in values if row['kind']=='offer'
                and row['source_id'] in {sources['iraq.scosi-extrusion-press-components-2026-03']['record_id'],
                                         sources['iraq.icsc-samawa-cement-plant']['record_id']}]


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
