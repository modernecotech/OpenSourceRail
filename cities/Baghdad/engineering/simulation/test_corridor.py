import csv
import io
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from cities.Baghdad.engineering.simulation import corridor


class AirportCorridor(unittest.TestCase):
    def test_source_reconciliation(self):
        opening, *_ = corridor.sources()
        for name,source in opening["iraq_operations"]["cases"].items():
            run=corridor.evaluate({"demand":name})
            self.assertEqual(len(run["hourly_od"]),24)
            self.assertAlmostEqual(run["annual_od_balance_journeys"],0.,6)
            self.assertAlmostEqual(run["mean_trip_km"],source["mean_trip_km"])
            self.assertEqual(run["annual_paid_journeys"],source["paid_journeys"])
            self.assertGreater(run["annual_all_journeys"],run["annual_paid_journeys"])
            self.assertTrue(all(row[i]==0 for h in run["hourly_od"] for i,row in enumerate(h)))

    def test_hypotheses_and_geometry(self):
        base=corridor.evaluate()
        alt=corridor.evaluate(dict(headway_min=30,cars=3,grade_pct=2))
        self.assertEqual(base["hourly_od"],alt["hourly_od"])
        self.assertAlmostEqual(base["busiest_departure_load"]*2,alt["busiest_departure_load"])
        self.assertAlmostEqual(base["platform_queue"]*2,alt["platform_queue"])
        self.assertEqual(alt["stops"][-1]["elevation_relative_to_origin_m"],240)
        self.assertIsNone(alt["stops"][4]["longitude_latitude"])
        self.assertGreater(alt["mapped_centroid_order_straight_segments_km"],12)
        self.assertNotEqual(base["candidate_id"],alt["candidate_id"])
        self.assertEqual(base["candidate_id"],corridor.evaluate({"demand":"upside"})["candidate_id"])
        with self.assertRaises(ValueError):
            corridor.evaluate({"grade_pct":3})

    def test_gtfs_mapped_subset_and_full_return(self):
        with tempfile.TemporaryDirectory() as folder:
            for minutes in (15,20,30):
                path=Path(folder)/f"airport-{minutes}.zip"
                run=corridor.evaluate({"headway_min":minutes})
                receipt=corridor.gtfs(run,path)
                self.assertEqual(receipt["held_stop_ids"],["Airport-04"])
                self.assertEqual(receipt["trips"],2*18*60//minutes)
                self.assertEqual(len(receipt["full_six_stop_times"]),6*receipt["trips"])
                with ZipFile(path) as z:
                    read=lambda name: list(csv.DictReader(io.StringIO(z.read(name).decode())))
                    stops=read("stops.txt")
                    self.assertEqual(len(stops),5)
                    events=read("stop_times.txt")
                    self.assertEqual(len(events),5*receipt["trips"])
                    self.assertEqual({s["stop_id"] for s in stops},{s["stop_id"] for s in events})
                    self.assertEqual(read("calendar_dates.txt")[0]["date"],"20261123")
