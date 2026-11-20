"""Independent equilibrium, pricing and parent checks for the four span envelopes."""

import json
import unittest

from compare_spans import DIR, PARENT, evaluate, monthly_yard_demand, price_yard_return, render, yard_return_form


class SpanComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = evaluate()
        cls.parent = json.loads((PARENT / "schedule.json").read_text())

    def test_published_result_and_candidate_ancestry(self):
        self.assertEqual(render(self.result), (DIR / "SPAN-COMPARISON.md").read_text())
        rows = self.result["rows"]
        parent = json.loads((DIR / "section-results.json").read_bytes())
        self.assertEqual(rows[0]["physical_id"], parent["physical_id"])
        self.assertEqual(rows[0]["actions"], parent["track"])
        self.assertEqual([r["length_m"] for r in rows], [10, 20, 25, 30])
        self.assertEqual(len({r["physical_id"] for r in rows}), 4)
        for row in rows:
            margin_usd = (rows[0]["direct_elevated_usd_m"] - row["direct_elevated_usd_m"]) * 1e6
            self.assertAlmostEqual(row["redesign_headroom_usd_each"] * row["placements"], margin_usd)
            self.assertEqual(row["stock_only_chart_balance_t"] > 0, row["length_m"] == 10)

    def test_reported_moving_moment_from_influence_line(self):
        train = self.parent["train"]
        axles = [c + a for c in train["car_centres_m"] for a in train["body_axle_x_m"]]
        load = self.result["crowd_train_t"] * 9.80665 / len(axles)
        for row in self.result["rows"]:
            case = row["sampled_live"]
            span = row["actions"]["bearing_span_m"]
            x = case["moment_location_m_from_left_support"]
            shift = case["moment_pose_train_centre_m_from_left_support"]
            positions = [a + shift for a in axles if -0.2500001 <= a + shift <= span + 0.2500001]
            moment = sum(p * (1 - x / span) if p <= x else x * (1 - p / span) for p in positions) * load
            self.assertAlmostEqual(moment, case["max_live_moment_knm_sampled"], places=2)

    def test_yard_stock_and_last_release(self):
        months = [{"year": 2028, "month": i+1, "beams_cast": cast, "beams_erected": lifts,
                   "cast_beams_awaiting_release": wip, "released_beams_awaiting_erection": finished}
                  for i, (cast, lifts, wip, finished) in enumerate(
                      [(0, 0, 0, 0), (10, 0, 10, 0), (8, 6, 8, 4), (0, 12, 0, 0), (0, 0, 0, 0)])]
        result = monthly_yard_demand({"factory_yards_needed_at_declared_rate": 2,
                                      "erection_fronts_needed_at_declared_rate": 3,
                                      "monthly_delivery": {"months": months}}, 30)
        self.assertEqual(result["yard_months"], 6)
        self.assertEqual(result["front_months"], 6)
        self.assertEqual(result["peak_month_end_stock_t"], 360)
        self.assertEqual(result["peak_month"], "2028-03")

    def test_yard_price_uses_only_matched_residual(self):
        form = yard_return_form(self.result)
        with self.assertRaises(ValueError):
            price_yard_return(self.result, form)
        form["scope_and_allowance_review"] = "Unit test fixture"
        rates = form["rates_2026_usd"]
        for row in rates.values():
            row.update(cash_price=5000, included_allowance=5000)
        rates["hold_one_yard_month"]["cash_price"] += 3000
        self.assertEqual(price_yard_return(self.result, form)["net_direct_change_usd"],
                         3000 * self.result["reference_delivery"]["yard_months"])
        rates["hold_one_yard_month"]["included_allowance"] = 1e14
        with self.assertRaisesRegex(ValueError, "exceed"):
            price_yard_return(self.result, form)
        form["candidate"] = "different"
        with self.assertRaisesRegex(ValueError, "current candidate"):
            price_yard_return(self.result, form)
