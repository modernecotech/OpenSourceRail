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
                   decision_basis=dict(declared_duty="completes simulated duty", failed_service_targets=[]),
                   cash_start_year=4, discount=.04, price=250., annual=8., pv=350.,
                   booked_trips=144, trips=144, places_per_hour=1400, served=10000., eligible=True)
        changed = {**row, "price": 190., "pv": 300., "annual": 7.}
        delta = dc.differential(row, changed)
        self.assertTrue(delta["selection_comparable"])
        inquiry = dc.differential(row, {**changed, "eligible": False})
        self.assertTrue(inquiry["matched_simulated_service_for_cost_enquiry"])
        self.assertFalse(inquiry["selection_comparable"])
        for rejected in (dict(declared_duty="numerically unresolved", failed_service_targets=[]),
                         dict(declared_duty="completes simulated duty", failed_service_targets=["capacity_screen"])):
            self.assertFalse(dc.differential(row, {**changed, "decision_basis": rejected})["matched_simulated_service_for_cost_enquiry"])
        annual_extra = delta["equivalent_extra_annual_cost"]
        self.assertAlmostEqual(sum(annual_extra / 1.04 ** year for year in range(4, 34)), 50)
        for change in ({"eligible": False}, {"served": 9992.}, {"places_per_hour": 700},
                       {"trips": 100}, {"booked_trips": 108}):
            self.assertFalse(dc.differential(row, {**changed, **change})["selection_comparable"])
        for change in ({"od_id": "other"}, {"cash_start_year": 5}):
            with self.assertRaises(ValueError):
                dc.differential(row, {**changed, **change})

    def test_duty_failure_and_open_evidence_have_different_consequences(self):
        result = dc.scenario.run_case(dict(condition="combined", topology="radial30", span_m=20))
        basis = dc.decision_basis(result)
        self.assertEqual(basis["declared_duty"], "misses simulated duty")
        self.assertIn("all_workings_complete", basis["failed_simulated_obligations"])
        self.assertIn("electrical_isolation_screen", basis["failed_simulated_obligations"])
        self.assertNotIn("protection_approved", basis["failed_simulated_obligations"])
        self.assertIn("protection_approved", basis["open_electrical_approvals"])
        self.assertIn("parent_cage_30pct_loss_kn", basis["breached_trial_controls"])
        self.assertIn("stock_lift_60t_t", basis["breached_trial_controls"])
        self.assertEqual(basis["supported_hard_screen"], "unknown")
        self.assertIsNone(basis["complete_installed_price_usd"])
        self.assertFalse(basis["comparable_for_adoption"])

    def test_completed_workings_do_not_imply_satisfied_service_targets(self):
        result = dc.scenario.run_case(dict(cars=3, headway_min=30, topology="paired6", ambient_c=48, demand="upside"))
        basis = dc.decision_basis(result)
        self.assertEqual(basis["declared_duty"], "completes simulated duty")
        self.assertIn("capacity_screen", basis["failed_service_targets"])
        self.assertIn("trial_cooling_kw", basis["breached_trial_controls"])
        self.assertFalse(basis["comparable_for_adoption"])
        result["stages"]["motion"]["gates"]["unreviewed_gate"] = True
        with self.assertRaisesRegex(ValueError, "changed motion gates"):
            dc.decision_basis(result)


if __name__ == "__main__":
    unittest.main()
