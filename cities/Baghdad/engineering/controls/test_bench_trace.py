"""Synthetic recorder fixtures for the offline intake only."""
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from bench_trace import CHANNELS, assess, templates
from engineering.station_rail.common import identity


def fixture():
    docs = templates()
    manifest = docs["manifest"]
    manifest.update(article_serial="fixture-1", started_at="2026-11-01T12:00:00Z", trial_id="test",
                    as_tested_build="0"*64, wiring_revision="fixture-wiring",
                    direction_sign=1, clock_error_ms=0.1, provenance="synthetic-fixture")
    docs["limits"].update(approved_at="2026-01-01T00:00:00Z", procedure_revision="software-test-only",
        thresholds=dict(maximum_sample_gap_ms=2, maximum_clock_error_ms=0.2, minimum_hold_kn=5,
                        released_hold_max_kn=1, maximum_inhibited_effort_kn=1, minimum_start_effort_kn=3,
                        maximum_rollback_mm=1, maximum_stationary_travel_mm=1, dispatch_to_effort_ms=20))
    docs["witness"].update(trial_id="test", article_serial="fixture-1", observer="fixture",
                           load_and_gradient="synthetic level", observations="simulated")
    docs["calibration"].update(trial_id="test", valid_until="2027-01-01T00:00:00Z",
                               maximum_clock_error_ms=0.1, clock_alignment_method="synthetic shared axis")
    raw = docs["raw"]
    raw.update(article_serial="fixture-1", trial_id="test")
    for index, name in enumerate(CHANNELS):
        channel = raw["channels"][name]
        channel["input_id"] = "fixture-" + name
        docs["calibration"]["channels"][name].update(input_id=channel["input_id"], certificate="test-only")
        for t in range(100):
            v = {"door_locked": int(t < 10 or t >= 20), "parking_applied": int(t < 64),
                 "hold_force": 6 if t < 68 else 0, "inverter_inhibited": int(t < 34),
                 "traction_effort": 5 if t >= 40 else 0, "wheel_position": max(0, t-75),
                 "dispatch_request": int(30 <= t < 32), "release_request": int(54 <= t < 56)}
            channel["samples"].append([t + index/100, v[name]])
    return docs


def analyze(docs, verifier=None, opening=None):
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        for key, ref in docs["manifest"]["files"].items():
            raw = json.dumps(docs[key]).encode()
            (root / ref["path"]).write_bytes(raw)
            ref["sha256"] = sha256(raw).hexdigest()
        return assess(root, docs["manifest"], authenticator=verifier, opening=opening)


class HandoverTest(unittest.TestCase):
    def test_recorded_opening_must_match_the_prepared_rig(self):
        from cities.Baghdad.airport_assembly import FRAME
        from cities.Baghdad.airport_opening import calculate, opening_inputs
        from cities.Baghdad.airport_service import build_service

        cfg, report, selected = opening_inputs()
        service = build_service(cfg, report["networks"]["first"]["groups"]["Airport"])
        case = calculate(inputs=(cfg, report, selected), service=service,
                         vehicle_revision=json.loads(FRAME.read_bytes())["braced_revision_id"])
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "opening.json"
            path.write_text(json.dumps(case))
            records = fixture()
            opening_basis = templates(path)["manifest"]["binding"]
            for key in ("manifest", "raw", "limits"):
                records[key]["binding"] = opening_basis
            self.assertEqual(analyze(records, opening=path)["disposition"], "held")
            with self.assertRaisesRegex(ValueError, "candidate"):
                analyze(records)
            case["controls"]["door_controllers"] -= 1
            path.write_text(json.dumps(case))
            with self.assertRaisesRegex(ValueError, "controller inventory"):
                analyze(records, opening=path)

    def test_normal_fixture_and_unwitnessed_physical_claim_stay_held(self):
        docs = fixture()
        r = analyze(docs)
        self.assertEqual(r["observed_faults"], [])
        self.assertEqual(set(r["events_ms"]), {"unlock","relock","dispatch","effort","release_request","hold_break","released","motion"})
        self.assertAlmostEqual(r["dispatch_to_effort_observed_ms"], 9.98)
        self.assertEqual(len(r["holds"]), 2)
        docs["manifest"]["provenance"] = "physical-measurement"
        r = analyze(docs)
        self.assertFalse(any(r["authenticated_roles"].values()))
        self.assertEqual(r["disposition"], "held")
        self.assertFalse(r["physical_accepted"])

    def test_force_during_boarding_and_rollback(self):
        docs = fixture()
        docs["raw"]["channels"]["traction_effort"]["samples"][15][1] = 2
        docs["raw"]["channels"]["wheel_position"]["samples"][55][1] = -4
        r = analyze(docs)
        self.assertIn("Effort measured while inverter inhibited", r["observed_faults"])
        self.assertIn("Rollback exceeds the limit", r["observed_faults"])
        self.assertEqual(r["maximum_rollback_mm"], 4)

    def test_release_before_effort(self):
        docs = fixture()
        docs["raw"]["channels"]["parking_applied"]["samples"][37][1] = 0
        self.assertIn("Physical hold fell before release request", analyze(docs)["observed_faults"])

    def test_sampling_and_late_limit_hold(self):
        docs = fixture()
        del docs["raw"]["channels"]["hold_force"]["samples"][64:68]
        docs["limits"]["approved_at"] = "2026-11-02T00:00:00Z"
        holds = analyze(docs)["holds"]
        self.assertIn("Recorder interval exceeds the limit", holds)
        self.assertIn("Recorded limits postdate the trial", holds)

    def test_stale_candidate_and_clock_faults(self):
        docs = fixture()
        docs["manifest"]["binding"] = {"selected_candidate": "unrelated"}
        with self.assertRaisesRegex(ValueError, "candidate"):
            analyze(docs)
        docs = fixture()
        docs["raw"]["channels"]["hold_force"]["samples"][15][0] = 0
        with self.assertRaisesRegex(ValueError, "time order"):
            analyze(docs)

    def test_role_coverage_independence_and_synthetic_boundary(self):
        docs = fixture()
        analyze(docs)  # Bind exact source bytes in the manifest.
        m = docs["manifest"]
        def attach():
            claim = {k: v for k, v in m.items() if k != "attestations"}
            for role, payload in {"record-producer": claim, "independent-reviewer": claim,
                                  "limit-approver": docs["limits"],
                                  "calibration-authority": docs["calibration"]}.items():
                m["attestations"][role] = {"role": role, "subject_id": role, "signature": "unit-test-only",
                                           "payload_sha256": identity(payload)}
        def mock_verifier(attestation, role):
            return attestation["signature"] == "unit-test-only" and attestation["role"] == role
        attach()
        self.assertEqual(analyze(docs, mock_verifier)["disposition"], "held")
        m["provenance"] = "physical-measurement"
        attach()
        r = analyze(docs, mock_verifier)
        self.assertEqual(r["disposition"], "ready for qualification review")
        self.assertFalse(r["physical_accepted"])
        m["attestations"]["independent-reviewer"]["subject_id"] = "record-producer"
        self.assertIn("Reviewer must be independent of producer", analyze(docs, mock_verifier)["holds"])

    def test_berth_creep_in_either_direction_before_dispatch(self):
        for t in (15, 26):  # During boarding and after relock.
            for displacement in (-1.01, -1, 1, 1.01):
                with self.subTest(t=t, displacement=displacement):
                    docs = fixture()
                    docs["limits"]["thresholds"]["maximum_rollback_mm"] = 10
                    docs["raw"]["channels"]["wheel_position"]["samples"][t][1] = displacement
                    r = analyze(docs)
                    self.assertEqual(r["maximum_held_berth_displacement_mm"], abs(displacement))
                    self.assertEqual("Displacement from secured berth exceeds the stationary limit"
                                     in r["observed_faults"], abs(displacement) > 1)
                    self.assertGreater(r["events_ms"]["motion"], 75)

    def test_lock_and_effort_supervised_until_first_motion(self):
        for channel, t, expected in (
                ("door_locked", 60, "Door unlocked through brake handover"),
                ("traction_effort", 70, "Starting effort lost through brake handover"),
                ("traction_effort", 77, "Starting effort lost through brake handover")):
            with self.subTest(channel=channel, t=t):
                docs = fixture()
                docs["raw"]["channels"][channel]["samples"][t][1] = 0
                self.assertIn(expected, analyze(docs)["observed_faults"])
