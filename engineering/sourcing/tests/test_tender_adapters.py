"""Constructed tender/quotation documents cannot self-approve commercial data."""
import json
import pytest
from engineering.sourcing.model import record
from engineering.sourcing.adapters import parse_boq_csv,parse_caltrans_html,parse_caltrans_csv,parse_quotation_json,parse_quotation_csv


def source(kind):
    return record("source",publisher="Synthetic test document",url="https://www.ungm.org/test-only",
        retrieved_at="2026-10-29",access="constructed-test-fixture",source_kind=kind,document_sha256=None,licence=None)


def html(award=True,total="200.00",unit="CY"):
    cells=['','510051 - SYNTHETIC CONCRETE ITEM',unit,'04','100','$2.00','$1.90','$'+total,'01-01-2025','04-TEST','1','M','TRO']
    return ('<table><tr>'+''.join('<td>'+c+'</td>' for c in cells)+'</tr></table><p>Bidders='+('Awarded Only' if award else 'All')+'</p>').encode()


def test_awarded_original_and_adjusted_values_are_distinct():
    row=parse_caltrans_html(html(),source('awarded_bid'))[0]
    assert row['unit_price']=='2' and row['adjusted_unit_price']=='1.9'
    assert row['reference_quantity']=='100' and row['quantity_unit']=='CY'
    assert not row['target_Iraq_unit_rate'] and not row['is_manufactured_product_price']


@pytest.mark.parametrize('raw',[html(False),html(total='300.00'),html(unit='LS')])
def test_all_bidders_total_mismatch_and_lump_sum_are_rejected(raw):
    with pytest.raises(ValueError):parse_caltrans_html(raw,source('awarded_bid'))


def test_awarded_csv_requires_award_and_unit_scope():
    raw='item_code,contract,bid_open_date,quantity,quantity_unit,unit_price,currency,awarded\n510051,TEST,2025-01-01,10,CY,20,USD,true\n'
    assert parse_caltrans_csv(raw,source('awarded_bid'))[0]['unit_price']=='20'
    with pytest.raises(ValueError):parse_caltrans_csv(raw.replace(',true',',false'),source('awarded_bid'))


def test_unpriced_boq_stays_unknown_not_zero():
    raw='description,quantity,quantity_unit,unit_price,currency\nConcrete,10,m3,,\n'
    row=parse_boq_csv(raw,source('tender_notice'))[0]
    assert row['kind']=='run' and row['rows'][0]['observed_unit_price'] is None
    assert row['price_offers_created']==0 and row['rows'][0]['currency'] is None


def test_filled_boq_price_is_not_an_awarded_rate():
    raw='description,quantity,quantity_unit,unit_price,currency\nConcrete,10,m3,50,USD\n'
    row=parse_boq_csv(raw,source('tender_notice'))[0]
    assert row['rows'][0]['rate_state']=='unverified-document-value' and not row['rows'][0]['pricing_admitted']


def quotation():
    return dict(product_key='TEST-ITEM',manufacturer='Test-only manufacturer',part_number='TEST-001',category='test',description='Constructed quote fixture',unit_price='100',quantity='10',currency='USD',quantity_unit='each',source_class='A',authenticated=True,procurement_approved=True)


def test_a_quotation_cannot_authenticate_its_own_class_a_claim():
    result=parse_quotation_json(json.dumps({'items':[quotation()]}),source('supplier_quotation'))
    assert [x['kind'] for x in result]==['product','run']
    assert all(not x['procurement_approved'] for x in result)
    assert result[-1]['claims'][0]['claimed_source_class']=='A' and result[-1]['price_offers_created']==0


def test_quotation_csv_is_also_held():
    row=quotation();keys=list(row)
    raw=','.join(keys)+'\n'+','.join(str(row[k]) for k in keys)+'\n'
    assert parse_quotation_csv(raw,source('supplier_quotation'))[-1]['status']=='held'
