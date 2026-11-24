"""Check exact feeder bindings and conditional equipment-return margins."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cities.Baghdad.engineering.simulation import audit_power_return as power


class FeederReturnTests(unittest.TestCase):
    @staticmethod
    def day(layout, evaluation_id, *, conductor_factor=1., condition="normal", branch_peak=1.25,
            source_peak=1.6, numerical_valid=True, near=150., remote=52.):
        sites = (0., 3000., 6000.)
        motion = {"physical": {"alignment_id": "mapped route", "feeder": {
            "name": layout, "sites": sites, "trunk_factor": conductor_factor,
        }}}
        return dict(
            power.binding(motion), topology=layout, evaluation_id=evaluation_id, condition=condition,
            site_chainages_m=sites, rms_branch_ka=.35, site_rms_ka=.55, peak_site_ka=source_peak,
            numerical_valid=numerical_valid, equipment_enquiry=dict(
                observed_healthy_branch_peak_ka_no_sharing_credit=branch_peak,
                upper_daily_branch_rms_ka_no_sharing_credit=.35,
                ideal_bolted_near_bus_ka=near, ideal_bolted_remote_single_path_ka=remote,
            ),
        )

    @staticmethod
    def document(directory, key):
        path = Path(directory) / "ratings.txt"
        path.write_text("Example return: static numerical fixture")
        return dict(schema=power.SCHEMA, documents={path.name: {
            "sha256": sha256(path.read_bytes()).hexdigest(), "issuer": "Test maker", "date": "2026-11-24",
        }}, layouts={key: dict(
            equipment_revision="maker-rev-04", document=path.name, ratings=dict(
                branch_peak_ka=2., branch_rms_ka=.4, source_peak_ka=2.5, source_rms_ka=.6,
            ), protection=dict(
                maximum_healthy_current_ka=2.5, pickup_min_ka=3., pickup_max_ka=4.,
                minimum_sustained_fault_ka=10., maximum_prospective_fault_ka=100., rated_breaking_ka=110.,
                required_grading_ms=20., maximum_cable_i2t_ka2s=1500., maximum_system_time_constant_ms=30.,
                rated_time_constant_ms=40., maximum_recovery_voltage_kv=1.6, rated_dc_voltage_kv=1.8,
                bands=[dict(from_ka=10., through_ka=100., primary_max_clear_ms=20.,
                            backup_min_trip_ms=50., backup_max_clear_ms=100.)],
            ),
        )})

    def test_inventory_groups_only_exact_layout_and_keeps_unknowns(self):
        normal = self.day("paired6", "normal")
        stress = self.day("paired6", "stress", condition="combined", branch_peak=1.9, near=140., remote=45.)
        different = self.day("paired6", "revised", conductor_factor=.75)
        data = power.assess([normal], [stress, different])
        self.assertEqual(len(data["layouts"]), 2)
        row = data["layouts"][normal["feeder_physical_id"]]
        self.assertEqual(row["envelope"]["branch_peak_ka"]["governing_evaluation_id"], "stress")
        self.assertEqual(row["envelope"]["near_bus_bolted_fault_ka"]["value"], 150.)
        self.assertEqual(row["envelope"]["remote_single_path_bolted_fault_ka"]["value"], 45.)
        self.assertEqual(row["equipment_return_screen"], "unknown")
        self.assertFalse(row["production_ranking_eligible"])
        self.assertFalse(data["physical_acceptance"])

    def test_sourced_ratings_keep_declared_capabilities_and_ideal_indicators_separate(self):
        normal = self.day("paired6", "normal")
        stress = self.day("paired6", "stress", branch_peak=2.1, source_peak=2.2)
        key = normal["feeder_physical_id"]
        with TemporaryDirectory() as directory:
            document = self.document(directory, key)
            data = power.assess([normal], [stress], document, evidence_directory=directory)
            result = data["layouts"][key]
            self.assertEqual(result["equipment_revision"], "maker-rev-04")
            self.assertEqual(result["declared_protection"]["status"], "pass")
            self.assertEqual(result["ideal_static_fault_comparison"]["near_bus_breaking_margin"]["margin"], -40.)
            self.assertEqual(result["current_rating_screen"]["branch_peak_ka"]["screen"], "fail")
            self.assertEqual(result["equipment_return_screen"], "fail")
            self.assertFalse(data["production_ranking_eligible"])
            document["layouts"][key]["ratings"]["branch_peak_ka"] = 3.
            passed = power.assess([normal], [stress], document, evidence_directory=directory)["layouts"][key]
            self.assertEqual(passed["equipment_return_screen"], "pass")
            self.assertFalse(passed["production_ranking_eligible"])
            missing = deepcopy(stress)
            missing["numerical_valid"] = False
            unknown = power.assess([normal], [missing], document, evidence_directory=directory)["layouts"][key]
            self.assertEqual(unknown["equipment_return_screen"], "unknown")
            self.assertFalse(unknown["envelope"]["source_rms_ka"]["complete"])

    def test_refuses_wrong_physical_identity_and_changed_attachments(self):
        duty = self.day("paired6", "normal")
        key = duty["feeder_physical_id"]
        changed = deepcopy(duty)
        changed["feeder_physical"]["feeder"]["trunk_factor"] = .75
        with self.assertRaisesRegex(ValueError, "matching physical layout"):
            power.assess([changed], [])
        with self.assertRaisesRegex(ValueError, "appears more than once"):
            power.assess([duty], [duty])
        with TemporaryDirectory() as directory:
            document = self.document(directory, key)
            moved = self.day("paired6", "revised", conductor_factor=.75)
            with self.assertRaisesRegex(ValueError, "exact studied physical IDs"):
                power.assess([moved], [], document, evidence_directory=directory)
            (Path(directory) / "ratings.txt").write_text("changed after hash")
            with self.assertRaisesRegex(ValueError, "Missing or changed attachment"):
                power.assess([duty], [], document, evidence_directory=directory)


if __name__ == "__main__":
    unittest.main()
