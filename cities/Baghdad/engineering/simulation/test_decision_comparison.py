import unittest
from itertools import product

from cities.Baghdad.engineering.simulation import decision_comparison as dc


class ComparisonTest(unittest.TestCase):
    def test_crossed_service_power_and_civil_cases(self):
        cases = list(dc.campaign())
        self.assertEqual(len(cases), len({tuple(sorted(case.items())) for _, case in cases}))
        crossed = [case for group, case in cases if group == "crossed"]
        self.assertEqual({(c["cars"], c["headway_min"], c["topology"], c["span_m"]) for c in crossed},
                         set(product((3, 6), (15, 20, 30), ("radial30", "paired6"), (10, 20, 25))))

    def test_cash_break_even_and_service_gate(self):
        row = dict(od_id="same", inputs=dict(grade_pct=0, ambient_c=40, condition="normal"),
                   cash_start_year=4, discount=.04, price=250., annual=8., pv=350.,
                   booked_trips=144, trips=144, places_per_hour=1400, served=10000., eligible=True)
        changed = {**row, "price": 190., "pv": 300., "annual": 7.}
        delta = dc.differential(row, changed)
        self.assertTrue(delta["selection_comparable"])
        annual_extra = delta["equivalent_extra_annual_cost"]
        self.assertAlmostEqual(sum(annual_extra / 1.04 ** year for year in range(4, 34)), 50)
        for change in ({"eligible": False}, {"served": 9992.}, {"places_per_hour": 700},
                       {"trips": 100}, {"booked_trips": 108}):
            self.assertFalse(dc.differential(row, {**changed, **change})["selection_comparable"])
        for change in ({"od_id": "other"}, {"cash_start_year": 5}):
            with self.assertRaises(ValueError):
                dc.differential(row, {**changed, **change})


if __name__ == "__main__":
    unittest.main()
