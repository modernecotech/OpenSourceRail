"""Semantic checks for independently projected Airport enquiry records."""

from copy import deepcopy
from functools import reduce
import json
from operator import getitem
from pathlib import Path
import unittest
from zipfile import ZipFile

from cities.Baghdad.engineering.simulation.audit_packet_evidence import check_evidence


class PacketEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with ZipFile(Path(__file__).with_name("audited-enquiry.zip")) as packet:
            cls.docs = {name: json.loads(packet.read(name)) for name in packet.namelist() if name.endswith(".json")}

    def test_semantic_relationships_reject_independent_projection_changes(self):
        check_evidence(self.docs, self.docs["manifest.json"])
        mutations = (
            ("station", ("engineering/station.json", "auxiliary_kw"), 0),
            ("forecast demand", ("engineering/service.json", "annual_paid_journeys"), 0),
            ("factory", ("factory/routing-basis.json", "prices_confirmed"), True),
            ("high-mass duty coverage", ("engineering/feeder.json", "high_mass"), []),
            ("duty candidate", ("engineering/feeder.json", "high_mass", 0, "candidate_id"), "other"),
            ("duty gate", ("engineering/feeder.json", "high_mass", 0, "gates", "protection_approved"), True),
            ("equipment duty inventory", ("engineering/feeder.json", "equipment", "duties"), []),
            ("operating decision", ("decision.json", "assessment", "operating_screen"), "failed"),
        )
        for expected, path, value in mutations:
            with self.subTest(scope=expected):
                changed = deepcopy(self.docs)
                reduce(getitem, path[:-1], changed)[path[-1]] = value
                with self.assertRaisesRegex(ValueError, expected):
                    check_evidence(changed, changed["manifest.json"])
