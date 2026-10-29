"""Saved public Easy Composites pages; no script execution or protected crawling."""
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlsplit

from ..model import UNITS, decimal_text, record
from ._source import checked_source
from .tenders import _text


class _NextData(HTMLParser):
    def __init__(self):
        super().__init__();self.active=False;self.scripts=[];self.parts=[];self.visible=[];self.in_script=False
    def handle_starttag(self,tag,attrs):
        if tag=='script':
            self.in_script=True;self.active=dict(attrs).get('id')=='__NEXT_DATA__';self.parts=[]
    def handle_data(self,data):
        if self.active:self.parts.append(data)
        elif not self.in_script:self.visible.append(data)
    def handle_endtag(self,tag):
        if tag=='script':
            if self.active:self.scripts.append(''.join(self.parts))
            self.active=False;self.in_script=False


def parse_easy_composites_html(raw,source,*,expected_part_number,currency='GBP',quantity_unit=None):
    """Use the exact selected SKU and its actual half-open Pricing rows.

    BasePricing is an advertised cheapest tier and is never used. Blank MOQ,
    order increment and installed mass remain unknown. ``quantity_unit`` may
    explicitly annotate a missing displayed unit; it cannot override a known one.
    """
    if source.get('source_kind') not in {'manufacturer_catalogue','distributor_catalogue','factory_catalogue'}:
        raise ValueError('Catalogue source required')
    checked_source(source,source['source_kind'],raw)
    if urlsplit(source['url']).hostname!='www.easycomposites.co.uk':
        raise ValueError('Explicit UK catalogue source required')
    parser=_NextData();parser.feed(_text(raw))
    if len(parser.scripts)!=1:raise ValueError('One public NEXT_DATA document required')
    data=json.loads(parser.scripts[0])
    try:
        state=data['props']['initialState'];product=state['page']['product'];session=state['session']
    except (KeyError,TypeError):raise ValueError('Unsupported public catalogue page schema') from None
    if not expected_part_number or product.get('Name')!=expected_part_number:
        raise ValueError('Selected SKU differs from requested variant')
    if session.get('currency',{}).get('text')!=currency:
        raise ValueError('Selected catalogue currency differs')
    sale=product.get('WebsiteSaleUnit',{}).get('text') or product.get('SaleUnit',{}).get('text')
    units={'Linear Metre':'m','Linear Meter':'m','Each':'each','EACH':'each','Pack':'each','Kit':'each'}
    actual_unit=units.get(sale)
    if quantity_unit is not None and quantity_unit not in UNITS:raise ValueError('Supported explicit sale unit required')
    if actual_unit and quantity_unit and actual_unit!=quantity_unit:raise ValueError('Sale unit annotation conflicts with catalogue')
    unit=actual_unit or quantity_unit
    visible=' '.join(parser.visible)
    tax='excluded' if session.get('includeVat') is False and re.search(r'ex\.?\s*VAT',visible,re.I) else 'unknown'
    if session.get('includeVat') is True and re.search(r'inc\.?\s*VAT',visible,re.I):tax='included'
    holds=['order-multiple-unreported']
    moq=product.get('MOQ')
    if moq in (None,'','0',0):moq=None;holds.append('minimum-order-quantity-unreported')
    else:moq=decimal_text(moq,'MOQ',positive=True)
    if unit is None:holds.append('sale-unit-unreported')
    pack={name:product.get(name,{}).get('text') or None for name in ('Pack Size','Kit Size','Speed','Version','Width','Length')}
    lead=record('product',product_key='EasyComposites:'+expected_part_number,
        manufacturer='Easy Composites (catalogue seller; OEM identity unverified)',
        part_number=expected_part_number,category='composite-material-or-factory-equipment',
        description=product.get('DisplayName') or product.get('PageTitle') or expected_part_number,
        source_ids=[source['record_id']],specifications=dict(selected_catalogue_sku=expected_part_number,
            catalogue_product_type=product.get('Type'),sale_unit_display=sale,quantity_unit=unit,
            pack_variant=pack,alternative_unit=product.get('AltDisplayUnit',{}).get('text') or None,
            alternative_unit_conversion_factor=product.get('AltUnitConversionFactor') or None,
            shipping_gross_weight_raw=product.get('GrossWeight'),installed_mass_kg=None,
            country_of_origin=None,technical_compatibility='pending',material_allowables=None,
            sourcing_holds=holds,price_basis='selected-SKU-Pricing-rows; advertised BasePricing ignored'))
    tiers=[]
    pricing=product.get('Pricing',[])
    if not isinstance(pricing,list) or len(pricing)>10000:raise ValueError('Bounded catalogue price rows required')
    for row in pricing:
        if row.get('Currency',{}).get('text')!=currency:continue
        if row.get('PriceLevel',{}).get('text')!='Base Price':continue
        tiers.append(dict(minimum_quantity=decimal_text(row.get('MinimumQuantity')),
            maximum_quantity=None if row.get('MaximumQuantity') in ('',None) else decimal_text(row['MaximumQuantity']),
            unit_price=decimal_text(row.get('UnitPrice'),'unit price')))
    tiers.sort(key=lambda r:__import__('decimal').Decimal(r['minimum_quantity']))
    if not tiers or unit is None:return [lead]
    offer=record('offer',product_id=lead['record_id'],source_id=source['record_id'],
        price_date=source['retrieved_at'][:10],valid_until=None,currency=currency,quantity_unit=unit,
        source_class='B',tax_basis=tax,tax_rate=None,minimum_order_quantity=moq,order_multiple=None,
        tiers=tiers,pack_variant=pack,sourcing_holds=holds,purchase_cost_admission='held',
        price_kind='base-catalogue',freight_cost=None,incoterm=None,country_of_origin=None,
        installed_cost_complete=False)
    return [lead,offer]
