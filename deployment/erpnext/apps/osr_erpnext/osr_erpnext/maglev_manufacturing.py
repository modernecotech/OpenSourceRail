"""Pure, bounded draft quantities for the explicit native simulation runner."""
import math
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING


def stock_lines(product):
    quantified=product.get('manufacturing_mode')=='quantified-candidate';rows=[]
    for line in product['bom']:
        if not quantified:
            rows.append(dict(id=line['id'],uom='Nos',quantity=1.,rate=1.,purchase_quantity=4.,source_sha256=line['source_sha256']));continue
        value=line['source'];quantity=value['purchase_quantity'];rate=value['unit_rate_usd'];net=value['net_quantity'];waste=value['waste_fraction']
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in (quantity,rate,net,waste)) or quantity<=0 or rate<0 or not 0<=waste<1:raise ValueError('finite positive quantified manufacturing input required')
        if not math.isclose(net,quantity*(1-waste),rel_tol=1e-9) or not math.isclose(value['extended_cost_usd'],quantity*rate,rel_tol=1e-9):raise ValueError('manufacturing material/valuation balance differs')
        if value['supplier_quote'] is not None or value['purchase_release'] is not False:raise ValueError('simulation cannot invent quote or procurement release')
        if value['uom'] not in {'Kg','Nos','Cubic Meter','Meter'}:raise ValueError('explicit stock UOM required')
        native_quantity=float(Decimal(str(quantity)).quantize(Decimal('.001'),rounding=ROUND_CEILING))
        native_rate=float(Decimal(str(rate)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
        rows.append(dict(id=line['id'],uom=value['uom'],quantity=native_quantity,net_quantity=net,waste_fraction=waste,rate=native_rate,purchase_quantity=4*native_quantity,source_sha256=line['source_sha256'],
            engineering_quantity_exact=quantity,engineering_unit_rate_usd=rate,
            native_quantity_increment=native_quantity-quantity,quantity_resolution=.001,currency_resolution_usd=.01,
            rounding_basis='Gross consumption rounded UP to0.001stockunit; unquoted rate rounded half-up toUSD0.01 for native business precision. Engineering cut schedule remains exact.'))
    return rows
