import copy
import unittest

from cities.Baghdad.engineering.simulation import airport_alignment, site_layers


class SiteLayerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.alignment = airport_alignment.evaluate()
        cls.record = site_layers.load_site_layers(alignment=cls.alignment)

    def test_public_data_cover_supports_and_named_stops(self):
        rows = self.record["samples"]
        self.assertEqual(len(rows), 879)
        self.assertEqual(rows[0]["chainage_m"], 0)
        self.assertEqual(rows[-1]["chainage_m"], self.record["route_m"])
        self.assertTrue({round(km * 1000, 6) for km in self.alignment["chainages_km"]}
                        <= {row["chainage_m"] for row in rows})
        self.assertTrue(all(0 < right["chainage_m"] - left["chainage_m"] <= 20
                            for left, right in zip(rows, rows[1:])))
        for name in ("ground_elevation_m", "clay_pct", "clay_0_5cm_pct"):
            self.assertGreater(len({row[name] for row in rows if row[name] is not None}), 1)
        self.assertTrue(any(row["water_occurrence_100m_max_pct"] > row["water_occurrence_pct"]
                            for row in rows if row["water_occurrence_pct"] is not None))

    def test_reject_shifted_chainage_even_if_fingerprint_is_recomputed(self):
        changed = copy.deepcopy(self.record)
        changed["samples"][1]["chainage_m"] += 0.1
        del changed["record_id"]
        changed["record_id"] = airport_alignment.identity(changed)
        with self.assertRaisesRegex(ValueError, "chainage or coordinate"):
            site_layers.validate(changed, self.alignment)

    def test_reject_unsealed_edit_to_soil_or_water(self):
        changed = copy.deepcopy(self.record)
        changed["samples"][0]["clay_pct"] = 0
        with self.assertRaisesRegex(ValueError, "record identity"):
            site_layers.validate(changed, self.alignment)

    def test_zero_occurrence_is_distinct_from_no_data(self):
        changed = copy.deepcopy(self.record)
        changed["samples"][0]["water_occurrence_pct"] = None
        changed["samples"][0]["water_occurrence_100m_max_pct"] = None
        del changed["record_id"]
        changed["record_id"] = airport_alignment.identity(changed)
        self.assertIsNone(site_layers.validate(changed, self.alignment)["samples"][0]["water_occurrence_pct"])
        self.assertTrue(any(row["water_occurrence_pct"] == 0 for row in self.record["samples"]))
