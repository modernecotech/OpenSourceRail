"""Regression checks for the Baghdad construction work packages."""

import unittest

from cities.Baghdad.engineering.mechanical.civil import network_delivery as delivery


class NetworkDeliveryTests(unittest.TestCase):
    def test_ring_and_access_are_not_treated_as_two_ended_open_lines(self):
        config = delivery.system.load()
        for network, deck_sections in (("first", 7), ("metropolitan", 13)):
            lengths, _, _ = delivery.system._lines(delivery.ROOT, config, network)
            rows = delivery.sections(network, config, lengths)
            self.assertEqual(len({name for name, _, _, _ in rows}), len(lengths))
            self.assertAlmostEqual(sum(km for _, km, _, _ in rows),
                                   config["networks"][network]["route_km"])
            self.assertEqual(sum(method == "deck" for _, _, method, _ in rows), deck_sections)
        self.assertIn(("road", "ring: two access sites needed"),
                      [(method, purpose) for _, _, method, purpose in rows])

    def test_reused_launchers_wait_and_separate_road_work_still_counts(self):
        orders = [
            dict(section="A", launcher_sets=2, calendar_days=90),
            dict(section="B", launcher_sets=2, calendar_days=70),
            dict(section="C", launcher_sets=2, calendar_days=60),
            dict(section="Ring", launcher_sets=0, calendar_days=150),
        ]
        serial = delivery.slots(orders, 1)
        parallel = delivery.slots(orders, 2)
        self.assertEqual(serial["last_standard_deck_day"], 220)
        self.assertEqual(parallel["last_standard_deck_day"], 150)
        self.assertEqual(parallel["paired_line_programmes"][-1]["start_day"], 70)
        self.assertEqual(delivery.slots([orders[-1]], 2)["last_standard_deck_day"], 150)

    def test_published_capital_replaces_direct_scope_once(self):
        import json

        report = json.loads((delivery.OUTPUT / "network-delivery.json").read_text())
        for programme in report["networks"].values():
            ledger = programme["civil_replacement_costs"]["base"]
            self.assertAlmostEqual(ledger["elevated_direct_usd_m"],
                                   sum(row["civil_scope_usd"]["base"] for row in programme["orders"]) / 1e6)
            self.assertAlmostEqual(ledger["installed_planning_usd_m"], sum(ledger[name] for name in (
                "elevated_direct_usd_m", "inherited_other_direct_usd_m", "design_usd_m", "test_usd_m",
                "allowance_usd_m")))
            self.assertAlmostEqual(ledger["construction_cash_assumption"]["total_capital_usd_m"],
                                   ledger["installed_planning_usd_m"])


if __name__ == "__main__":
    unittest.main()
