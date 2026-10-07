from datetime import date
import hashlib
import pytest
from osr_mech.delivery_commercial import quote_register,partial_cashflow_sensitivity,procurement_requirements
from osr_mech.handling_assurance import gross_section,support_screen,beam_stage_assurance
from osr_mech.station_capacity import footprint_screen,station_capacity_screen


def quotation(**changes):
    row=dict(id='test-quote',supplier_id='test-supplier',source_record='test-only',source_sha256='a'*64,
        scope='launcher-purchase',status='firm',currency='USD',issued_on='2026-10-01',valid_until='2026-12-01',
        quantity=18,unit_price_usd=500000,review_accepted=True)
    return {**row,**changes}


def test_quote_expiry_review_and_contract_are_separate_from_plant_capacity(tmp_path):
    source=tmp_path/'quote.txt';source.write_text('test-only quotation')
    quote=quotation(source_record=source.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    row=quote_register([quote], '2026-10-07',evidence_root=tmp_path)[0]
    assert row['cash_usd']==9e6 and row['price_evidence_applicable_as_of']
    assert not row['purchase_committed'] and not row['factory_capacity_qualified_by_quote']
    assert not quote_register([quote], '2027-01-01',evidence_root=tmp_path)[0]['price_evidence_applicable_as_of']
    assert not quote_register([quote], '2026-10-07')[0]['price_evidence_applicable_as_of']
    source.write_text('altered')
    with pytest.raises(ValueError,match='receipt drift'):
        quote_register([quote],'2026-10-07',evidence_root=tmp_path)
    with pytest.raises(ValueError,match='FX'):quote_register([quotation(currency='IQD')],'2026-10-07')


def test_partial_interest_uses_each_payment_date_without_manufacturing_a_budget():
    payments=[dict(scope='one',date='2027-01-01',cash_usd=1000),dict(scope='two',date='2027-07-01',cash_usd=500)]
    row=partial_cashflow_sensitivity(payments,'2028-01-01',.08)
    assert row['interest_on_identified_cash_usd']==pytest.approx(80+500*.08*184/365)
    assert row['complete_financing_usd'] is None and row['claimed_net_saving_usd'] is None
    assert row['revenue_usd'] is None and not row['financing_committed']


def test_contracted_label_requires_a_separate_received_and_reviewed_contract(tmp_path):
    source=tmp_path/'quote.txt';source.write_text('test-only quotation')
    contract=tmp_path/'contract.txt';contract.write_text('test-only contract')
    quote=quotation(status='contracted',source_record=source.name,
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        contract_record=contract.name,contract_sha256=hashlib.sha256(contract.read_bytes()).hexdigest())
    assert not quote_register([quote],'2026-10-07',evidence_root=tmp_path)[0]['purchase_committed']
    reviewed={**quote,'contract_review_accepted':True}
    row=quote_register([reviewed],'2026-10-07',evidence_root=tmp_path)[0]
    assert row['purchase_committed'] and not row['factory_capacity_qualified_by_quote']
    contract.write_text('changed')
    with pytest.raises(ValueError,match='receipt drift'):
        quote_register([reviewed],'2026-10-07',evidence_root=tmp_path)


def test_statics_conserve_weight_and_resolve_the_known_uniform_beam_solution():
    row=support_screen(1000,10,(0,10))
    assert row['reaction_a_kn']+row['reaction_b_kn']==pytest.approx(9.81)
    assert row['maximum_positive_moment_knm']==pytest.approx(9.81*10/8)
    for span in (20.,25.):
        stages=beam_stage_assurance(span)
        assert stages['lifting_screen']['maximum_negative_moment_knm']<0
        assert stages['lifting_screen']['maximum_leg_tension_kn']>0
        assert not stages['construction_release'] and not stages['independently_checked']
    assert gross_section()['area_m2']==pytest.approx(1.199)


def test_overlapping_lift_shaft_footprints_are_counted_once():
    platform=dict(y_mm=0,width_mm=8000,level='platform',id='p')
    equipment=[dict(id=k,kind=kind,x_mm=0,y_mm=0,width_mm=2000,length_mm=2000,served_levels=['platform']) for k,kind in [('a','lift'),('b','shaft')]]
    area=footprint_screen(platform,10,equipment)
    assert area['equipment_union_area_m2']==4 and area['unoccupied_envelope_area_m2']==76
    assert area['narrowest_largest_contiguous_lane_m']==3
    station=dict(id='s',layout=dict(platforms=[platform],equipment=equipment),passenger_demand={})
    result=station_capacity_screen(station,10)
    assert result['one_lift_out_cases'][0]['remaining_station_lift_capacity_pax_hour'] is None
    assert not result['engineering_qualified'] and result['evacuation_seconds'] is None
