import csv
import io
import unittest
from copy import deepcopy
from hashlib import sha256

from cities.Baghdad import airport_integration
from cities.Baghdad.engineering.prototype import car, manufacturing


class ManufacturingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = airport_integration.build()
        cls.article, cls.files = car.artifacts(cls.parent)
        cls.cuts = cls.files["revised-cuts.csv"]
        cls.orders, cls.bom = manufacturing.routing(cls.parent, cls.article, cls.cuts)
        cls.rows = list(csv.DictReader(io.StringIO(cls.bom.decode())))

    def row(self, item):
        rows = [r for r in self.rows if r["item"] == item]
        self.assertEqual(len(rows), 1)
        return rows[0]

    def test_frame_takeoff_matches_drawn_occurrences_and_mass(self):
        orders = self.orders
        profiles = orders["gross_stock_by_profile"]
        fleet_cars = orders["fleet_cars"]
        self.assertEqual(fleet_cars, 36)
        self.assertEqual(sum(r["pieces_opening"] for r in profiles), 144 * fleet_cars)
        self.assertEqual(sum(r["pieces_opening"] for r in profiles),
                         sum(int(r["opening_quantity"]) for r in self.rows if r["scope"] == "cut material"))
        self.assertAlmostEqual(sum(r["gross_cut_kg_opening"] for r in profiles),
                               self.article["mass"]["cut_kg_per_car"] * fleet_cars, places=2)
        self.assertIsNone(next(r["cut_m_opening"] for r in profiles if "triangle" in r["nominal_stock_mm"]))
        self.assertEqual(self.row("Wheelset")["opening_quantity"], "144")
        self.assertEqual(self.row("sliding leaves")["opening_quantity"], "576")
        self.assertEqual(self.row("Independent stopping and parking brake hardware")["opening_quantity"], "")
        self.assertEqual(orders["source_bindings"]["bom_sha256"], sha256(self.bom).hexdigest())
        self.assertEqual(orders["source_bindings"]["cuts_sha256"], sha256(self.cuts).hexdigest())

    def test_civil_power_and_pilot_series_quantities_have_distinct_scope(self):
        for item, quantity in {"beam_count": 2400, "pier_foundation_count": 2402,
                               "bearing_unit_allowance": 9600, "grid_sites": 30, "dc_source_groups": 30,
                               "dc_outgoing_breaker_circuits": 116, "normally_open_track_ties": 58,
                               "protected_track_km": 24, "section_control_gateways": 116,
                               "passenger station sites": 6, "open terminal platform faces (both ends)": 2,
                               "onboard_contact_sets": 24, "charger_ports": 0}.items():
            with self.subTest(item=item):
                self.assertEqual(float(self.row(item)["opening_quantity"]), quantity)
        self.assertEqual(self.row("installed and tested rectifier cabinets")["opening_quantity"], "")
        self.assertEqual(len(self.orders["draft_work_orders"]), 5)
        for order in self.orders["draft_work_orders"]:
            self.assertEqual((order["qty"], order["docstatus"], order["production_item"], order["bom_no"]),
                             (1, 0, None, None))
            self.assertEqual(order["candidate_id"], self.article["candidate_id"])
        self.assertAlmostEqual(self.orders["fleet_purchase_allowance_usd_m"], 50.88)
        self.assertIsNone(self.orders["revised_fleet_supplier_quote_usd_m"])

    def test_wrong_drawings_duties_or_assembly_rejected(self):
        with self.assertRaisesRegex(ValueError, "drawing"):
            manufacturing.routing(self.parent, self.article, self.cuts.replace(b"356.704", b"999.999"))
        for error, path in (("Power and finance", ("finance", "candidate_id")),
                            ("Power and finance", ("opening", "section_power", "power_evaluation_id"))):
            with self.subTest(path=path):
                bad = deepcopy(self.article)
                target = bad
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = "other"
                bad["evaluation_id"] = car.identity({k: v for k, v in bad.items() if k != "evaluation_id"})
                with self.assertRaisesRegex(ValueError, error):
                    manufacturing.routing(self.parent, bad, self.cuts)
        bad_parent = deepcopy(self.parent)
        bad_parent["assembly"]["parts"][0]["fleet_quantity"] = 2
        with self.assertRaisesRegex(ValueError, "parent assembly"):
            manufacturing.routing(bad_parent, self.article, self.cuts)


if __name__ == "__main__":
    unittest.main()
