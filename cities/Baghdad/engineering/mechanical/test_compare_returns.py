import unittest
from cities.Baghdad.engineering.mechanical.compare_returns import compare, estimate, return_form


class MatchedBuyerReturns(unittest.TestCase):
    def setUp(self):
        self.basis, self.quantities, self.units, self.scopes, self.rates = estimate()
        self.form = return_form(self.basis, self.units)

    def result(self):
        return compare(self.form, self.basis, self.units, self.scopes, self.rates)

    def test_partial_article_does_not_set_a_price_or_mass(self):
        self.assertAlmostEqual(self.result()["change_usd_m"], 0)
        self.assertAlmostEqual(self.quantities["trial_cut_stock_kg_per_train"], 31177.086)
        self.assertEqual(self.quantities["bogie_frames"], 2904)
        self.assertIsNone(self.quantities["complete_installed_train_tare_kg"])

    def test_one_complete_station_and_two_sets(self):
        self.form["lots"]["stations_access"].update(matched_units=1, cash_total_usd_m=14,
                                                     scope_review_reference="matched station example")
        unit_price = self.scopes["vehicles"] / self.units["vehicles"]
        self.form["lots"]["vehicles"].update(matched_units=2, cash_total_usd_m=2*unit_price-3,
                                              scope_review_reference="two complete sets example")
        result = self.result()
        self.assertAlmostEqual(result["matched_returns"]["stations_access"]["displaced_allowance_usd_m"], 13)
        self.assertAlmostEqual(result["change_usd_m"], -2 * 1.105 * 1.2)
        self.assertAlmostEqual(self.scopes["stations_access"], 832)

    def test_scope_and_candidate_checks(self):
        for fields in [dict(matched_units=65), dict(cash_total_usd_m=0),
                       dict(matched_units=1, cash_total_usd_m=12),
                       dict(matched_units=True), dict(cash_total_usd_m=float("nan"))]:
            with self.subTest(fields=fields):
                self.form = return_form(self.basis, self.units)
                self.form["lots"]["stations_access"].update(fields)
                with self.assertRaises(ValueError):
                    self.result()
        self.form["basis"] = dict(self.basis, network="metropolitan")
        with self.assertRaises(ValueError):
            self.result()
