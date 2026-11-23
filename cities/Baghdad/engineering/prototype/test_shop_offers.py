import csv
from io import StringIO
import json
import pytest

from cities.Baghdad.engineering.prototype import shop_offers


def response(costs, supplier, updates=None):
    rows = list(csv.DictReader(StringIO(shop_offers.template(costs).decode())))
    row = rows[0]
    row.update(supplier=supplier, erp_supplier_quotation="Q-" + supplier, unit_rate_usd="123.45",
               scope_response="matches", delivery_terms_and_exclusions="Quoted to yard, taxes itemised",
               price_evidence_ref="signed offer, line 1")
    row.update(updates or {})
    output = StringIO()
    writer = csv.DictWriter(output, shop_offers.FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return supplier, output.getvalue()


def test_prices_compare_only_within_issued_scope_and_edition():
    costs = json.loads((shop_offers.HERE / "shop-costs.json").read_bytes())
    a = response(costs, "A")
    b = response(costs, "B", {"scope_response": "deviation"})
    offers = shop_offers.compare(costs, [a, b])["responses"]
    assert offers[0]["unit_variance_from_planning_usd"] is not None
    assert offers[1]["unit_variance_from_planning_usd"] is None
    with pytest.raises(ValueError, match="duplicate"):
        shop_offers.compare(costs, [a, a])
    altered = json.loads(json.dumps(costs))
    altered["resources"][0]["unit_rate_usd"]["base"] += 1
    with pytest.raises(ValueError, match="content differs"):
        shop_offers.compare(altered, [a])
    for changes in ({"shop_cost_evaluation_id": "old"}, {"pricing_unit": "wrong"}, {"unit_rate_usd": "NaN"},
                    {"unit_rate_usd": "-2"}, {"price_evidence_ref": ""}):
        with pytest.raises(ValueError):
            shop_offers.compare(costs, [response(costs, "A", changes)])
