import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import compare


class RapidManufactureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = compare.build()

    def test_cam_coverage_keeps_heavy_and_flat_stock_on_saw(self):
        result = self.result
        eligible = [row for row in result["stock_profile_screen"] if row["automatic_tube_eligible"]]
        fallback = [row for row in result["stock_profile_screen"] if not row["automatic_tube_eligible"]]
        self.assertEqual(sum(row["blank_pieces"] for row in eligible), 2232)
        self.assertEqual(sum(row["blank_pieces"] for row in fallback), 936)
        self.assertTrue(any("weight_kg" in row["screen"] for row in fallback))
        self.assertEqual(result["gross_blanks_per_car"], 144)

    def test_base_cost_and_schedule_tradeoffs(self):
        small = self.result["orders"]["36"]
        self.assertLess(small["shared_cnc"]["last_coated_frame_set_shift_days"],
                        small["saw_fixture"]["last_coated_frame_set_shift_days"])
        self.assertGreater(small["shared_cnc"]["price_cases"]["base"]["total_usd"],
                           small["saw_fixture"]["price_cases"]["base"]["total_usd"])
        large = self.result["orders"]["180"]
        self.assertLess(large["shared_cnc"]["price_cases"]["base"]["total_usd"],
                        large["saw_fixture"]["price_cases"]["base"]["total_usd"])
        self.assertGreaterEqual(large["dedicated"]["robot_pairs"] * 2,
                                large["dedicated"]["machine_counts"]["body"] +
                                large["dedicated"]["machine_counts"]["bogies"])
        delayed = self.result["double_rework_180_cars"]["shared_cnc"]
        self.assertGreater(delayed["last_coated_frame_set_shift_days"],
                           large["shared_cnc"]["last_coated_frame_set_shift_days"])
        self.assertFalse(self.result["production_release"])

    def test_changed_frame_is_rejected(self):
        with TemporaryDirectory() as temp:
            folder = Path(temp)
            for name in compare.SOURCE_FILES:
                dst = folder / name
                dst.parent.mkdir(exist_ok=True, parents=True)
                dst.symlink_to(compare.PROTOTYPE / name)
            manifest = folder / "cam/cam-manifest.json"
            data = json.loads(manifest.read_text())
            manifest.unlink()
            data["frame_revision"] = f"{data['frame_revision']}-incompatible"
            manifest.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "one physical frame"):
                compare.read_source(folder)
