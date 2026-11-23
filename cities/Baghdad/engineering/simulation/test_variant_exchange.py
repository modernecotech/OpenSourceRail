"""Test the standard-library export through integrated three- and six-car cases."""
import csv
from io import StringIO
import json
import unittest

from cities.Baghdad.engineering.simulation import scenario, variant_exchange


class ScenarioExchange(unittest.TestCase):
    def test_parent_and_derivative(self):
        for config in ({},{"cars":3,"material":"hybrid","span_m":30,"headway_min":20,"topology":"paired6"}):
            result=scenario.run_case(config)
            files=variant_exchange.artifacts(result)
            meta=json.loads(files["candidate/exchange.json"])
            q=result["stages"]["production"]["quantities"]
            self.assertEqual(meta["counts"]["CarEnvelope"]*q["sets"], q["cars"])
            self.assertEqual(meta["counts"]["BearingDatum"],q["bearings"])
            self.assertEqual(meta["counts"]["TrackSpan"],q["beams"])
            self.assertEqual(meta["counts"]["PierFooting"],q["piers"])
            self.assertEqual(meta["counts"]["FeederChainage"],q["grid_sites"])
            self.assertEqual(meta["physical_id"],result["identity"]["physical_id"])
            lots=list(csv.DictReader(StringIO(files["candidate/procurement-lots.csv"].decode())))
            fleet=next(row for row in lots if row["lot"]=="fleet")
            self.assertEqual(fleet["planning_unit"],f"{result['inputs']['cars']}-car sets")
            self.assertEqual(fleet["evaluation_id"],result["identity"]["evaluation_id"])
            quantities=list(csv.DictReader(StringIO(files["candidate/planning-quantities.csv"].decode())))
            self.assertEqual(next(r["quantity"] for r in quantities if r["item"]=="rectifier_cabinets"),"")
            self.assertEqual(files["candidate/airport-layout.ifc"],variant_exchange.artifacts(result)["candidate/airport-layout.ifc"])
