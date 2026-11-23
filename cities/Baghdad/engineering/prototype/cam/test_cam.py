"""Check the buyer input boundary and opening quantities without a CAD install."""
import csv
import importlib.util
import io
import json
import unittest
import zipfile
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("airport_cam", HERE/"build.py")
cam = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cam)


class CamTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = cam.artifacts()

    def rows(self, file):
        return list(csv.DictReader(io.StringIO(self.out[file].decode())))

    def test_rebuild_published_members_and_reject_mixed_inputs(self):
        with zipfile.ZipFile(cam.PACKET) as packet:
            members = {name: packet.read(name) for name in packet.namelist()}
        self.assertEqual(cam.artifacts(members), self.out)
        for name, data in self.out.items():
            self.assertEqual((HERE/name).read_bytes(), data, name)
        members["revised-cuts.csv"] += b"\n"
        with self.assertRaisesRegex(ValueError, "differs from its manifest"):
            cam.artifacts(members)

    def test_streams_and_raw_stock(self):
        stock = {r["pattern"]:r for r in self.rows("saw-stock.csv")}
        saw = Counter()
        previous_end = {key:10 for key in stock}
        for row in self.rows("saw-cuts.csv"):
            key = row["pattern"]
            self.assertAlmostEqual(previous_end[key], float(row["start_mm"]))
            length = float(row["near_blade_face_mm"])-float(row["start_mm"])
            self.assertAlmostEqual(length, float(row["length_mm"]))
            previous_end[key] = float(row["near_blade_face_mm"]) + float(row["blade_kerf_mm"])
            saw[row["part"]] += int(stock[key]["bars"])
            if length >= 12000:
                self.assertGreater(int(stock[key]["raw_length_mm"]), 12000)
        for key, row in stock.items():
            self.assertAlmostEqual(int(row["raw_length_mm"])-previous_end[key], float(row["remaining_tail_mm"]))
            self.assertGreaterEqual(float(row["remaining_tail_mm"]), int(row["min_tail_grip_mm"]))
        self.assertEqual((sum(saw.values()), saw["jamb_liner"]), (3168, 576))
        plated = Counter()
        sheet_copies = {}
        for row in self.rows("sheet-schedule.csv"):
            sheet_copies[row["layout"]] = int(row["sheets"])
            plated[row["part"]] += int(row["blanks_per_sheet"]) * int(row["sheets"])
        self.assertEqual(plated, {"gusset":1440,"primary_underside":288,"secondary_top":144,"secondary_body":144})
        self.assertEqual(sum(sheet_copies.values()), 44)

    def test_sealed_native_replay(self):
        receipt = json.loads((HERE/"training/freecad-receipt.json").read_bytes())
        manifest = json.loads(self.out["cam-manifest.json"])
        self.assertEqual(receipt["input_cam_evaluation_id"], manifest["evaluation_id"])
        self.assertEqual(receipt["verifier_sha256"], cam.sha((HERE/"verify_freecad.py").read_bytes()))
        self.assertEqual(receipt["practice"]["posted_nc_sha256"], cam.sha(self.out["training/practice.nc"]))
        self.assertEqual(receipt["practice"]["minimum_remaining_floor_mm"], 7)


if __name__ == "__main__":
    unittest.main()
