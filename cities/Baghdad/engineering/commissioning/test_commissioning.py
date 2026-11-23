from hashlib import sha256
from io import StringIO
import csv
import json

import pytest

from cities.Baghdad import airport_integration
from cities.Baghdad.engineering.commissioning import feeder, measurements, recorder


@pytest.fixture(scope="module")
def opening():
    return airport_integration.build()["opening"]


def test_voltage_inverse_and_new_topology(opening):
    study = feeder.evaluate(opening)
    s = study["priced_radial"]
    assert s["published_hot_margin_v"] == pytest.approx(0.9254063)
    row = s["cases"]["published hot circuit"]
    floor = study["floor_kv"]
    assert feeder.voltage(
        row["source_kv"] - s["source_dip_to_floor_v"] / 1000, row["loop_ohm"], row["collector_load_mw"], floor
    )["collector_kv"] == pytest.approx(floor)
    pilot = study["parallel_quotation"]
    assert pilot["minimum_combined_collector_kv"] == pytest.approx(1.3689378113)
    assert pilot["single_path_lost_with_site_out_combined"]["collector_kv"] < floor
    assert pilot["replayed_pulses"] == 736 and len(pilot["outages"]) == 7
    assert len({feeder.return_form(opening, option)["scope"]["design_id"] for option in feeder.OPTIONS}) == 3
    assert study["return"]["protection"]["status"] == "awaiting protection return"
    assert pilot["installed_direct_2026_usd"] is None


def test_graded_curve_and_tamper(opening):
    form = feeder.return_form(opening, "six_site_parallel")
    form.update(
        record_kind="engineering-sensitivity", document_revision="fixture only", coverage="test envelope"
    )
    # Numeric bands exercise the predicate, with no issued field settings.
    form["path"] = dict(zip(feeder.PATH, [1.5, 0.005, 0.001, 0.001, 0.001, 13.0], strict=True))
    form["protection"] = dict(
        zip(feeder.PROTECTION, [11, 12, 13, 15, 25, 30, 5, 100, 8, 10, 2, 2.1], strict=True)
    )
    form["protection"]["bands"] = [
        dict(zip(feeder.BAND, [15, 20, 10, 18, 30], strict=True)),
        dict(zip(feeder.BAND, [20, 25, 10, 20, 30], strict=True)),
    ]
    report = feeder.evaluate(opening, form)["return"]
    assert report["protection"]["status"] == "returned envelope passes" and not report["authenticated"]
    form["protection"]["bands"][1]["backup_min_trip_ms"] = 12
    assert not feeder.evaluate(opening, form)["return"]["protection"]["checks"]["all_bands_selective"]
    form["protection"]["bands"][1]["from_ka"] = 21
    with pytest.raises(ValueError, match="adjoin"):
        feeder.evaluate(opening, form)
    form["scope"]["rectifier_sites"] = 30
    with pytest.raises(ValueError, match="circuit"):
        feeder.evaluate(opening, form)
    parent, alt = [feeder.return_form(opening, k) for k in ("priced_radial", "six_site_parallel")]
    assert (
        feeder.compare_returns(opening, parent, alt)["six_site_minus_priced_radial"]["installed_direct_usd"]
        is None
    )
    for i, f in enumerate([parent, alt]):
        f.update(record_kind="engineering-sensitivity", document_revision="fixture", coverage="all zones")
        f["price_2026_usd"].update(
            installed_direct={k: (i + 1) * 10000 for k in feeder.PRICE_ITEMS},
            annual_upkeep=100 * i,
            renewals_by_year={},
        )
    d = feeder.compare_returns(opening, parent, alt)["six_site_minus_priced_radial"]
    assert d["installed_direct_usd"] == 40000
    assert d["priced_scope_pv_30y_usd"] == pytest.approx(40000 + sum(100 / 1.04**n for n in range(1, 31)))


def test_hot_measurement_uncertainty_and_binding(opening):
    raw = (
        "time_s,window,source_ka,branch_ka,bus_kv,collector_kv,conductor_c\n"
        "0,low,1,1,1.49,1.48,75\n1,low,1,1,1.49,1.48,75\n"
        "2,high,8,8,1.42,1.38,75\n3,high,8,8,1.42,1.38,75\n"
    ).encode()
    form = measurements.template(opening)
    form.update(
        trial_id="fixture",
        calibration_record="fixture",
        serial_and_wiring_record="fixture",
        record_kind="synthetic-fixture",
        live_site_index=0,
        failed_site_index=1,
        track="outward",
        collector_chainage_km=0.3,
        minimum_test_temperature_c=75,
        raw_csv_sha256=sha256(raw).hexdigest(),
    )
    form["uncertainty"] = dict.fromkeys(measurements.UNCERTAINTY, 0)
    r = measurements.assess(opening, form, raw)
    assert r["maximum_two_point_source_slope_ohm"] == pytest.approx(0.01)
    assert r["maximum_high_window_bus_to_shoe_loop_ohm"] == pytest.approx(0.005)
    assert r["measured_window_above_floor"] and not r["covers_stated_load"]
    form["uncertainty"].update(voltage_abs_kv=0.002, temperature_abs_c=1)
    r = measurements.assess(opening, form, raw)
    assert r["maximum_two_point_source_slope_ohm"] > 0.01 and not r["covers_test_temperature"]
    with pytest.raises(ValueError, match="SHA256"):
        measurements.assess(opening, form, raw + b"\n")


def capture_fixture(path, mode, mutation=None, *, schema=recorder.SCHEMA):
    form = recorder.template(path, mode, schema=schema)
    form.update(
        trial_id="fixture",
        article_serial="synthetic-car",
        wiring_revision="fixture",
        record_kind="synthetic-fixture",
        as_tested_build_sha256="0" * 64,
    )
    if schema == recorder.SCHEMA:
        form["visit"].update(dict.fromkeys(recorder.VISIT, "fixture"))
        form["visit"].update(
            platform_side="left", physical_door_slot=0, direction_sign=1, controller_boot_id="0"
        )
    for key, item in form["inputs"].items():
        if schema == recorder.SCHEMA:
            item.update(device_serial="fixture", device_terminal=key)
        item.update(input_id="pin_" + key)
    if mode != "handover":
        form.update(
            limit_document_revision="fixture", witness_record_sha256="0" * 64, stimulus_record_sha256="1" * 64
        )
        form["limits"].update(
            clock_error_ms=0.05,
            maximum_gap_ms=2,
            response_deadline_ms=4,
            minimum_hold_observation_ms=5,
            maximum_effort_kn=1,
            minimum_holding_force_kn=5,
            maximum_displacement_mm=1,
        )
        if mode == "stale_command":
            form["limits"]["maximum_command_age_ms"] = 10
    out = StringIO(newline="")
    keys = list(form["inputs"])
    writer = csv.writer(out)
    writer.writerow(["time_ms", *("pin_" + k for k in keys)])
    for i in range(24):
        row = dict.fromkeys(keys, 0)
        row.update(
            stimulus=int(i >= 4),
            drive_inhibited=1,
            parking_contact=1,
            holding_force=10,
            independent_brake_request=int(i >= 5),
            brake_feedback_ok=int(i < 4),
            wrong_side_command=int(i >= 4),
            local_handle=int(i >= 4),
            emergency_brake_output=int(i >= 5),
            command_received=1,
            command_sent_ms=100 + i - (20 if i >= 4 else 0),
            command_age=20 if i >= 4 else 0,
            egress_authorised=int(mode == "evacuation_authorised"),
            exit_open=int(mode == "evacuation_authorised" and i >= 7),
            supply_healthy=int(i < 4 or i >= 11),
            boot_epoch=int(i >= 11),
            reset_key=int(i >= 6),
        )
        if mutation:
            mutation(i, row)
        writer.writerow([100 + i, *(row[k] for k in keys)])
    data = out.getvalue().encode()
    form["raw_csv_sha256"] = sha256(data).hexdigest()
    return form, data


@pytest.mark.parametrize("mode", list(recorder.FAULTS) + ["handover"])
def test_station_capture_and_fault_replay(opening, tmp_path, mode):
    path = tmp_path / "opening.json"
    path.write_text(json.dumps(opening))
    form, data = capture_fixture(path, mode)
    r = recorder.convert(path, form, data)
    if mode == "handover":
        assert len(r["channels"]["door_locked"]["samples"]) == 24
        return
    assert r["disposition"] == "observations within supplied limits" and not r["physical_accepted"]
    form, data = capture_fixture(path, mode, lambda i, row: row.update(opposite_door_open=int(i == 15)))
    assert "unpermitted door opening" in recorder.convert(path, form, data)["observed_faults"]


def test_original_logger_cannot_change_provenance_in_bench_manifest(opening, tmp_path):
    path = tmp_path / "opening.json"
    path.write_text(json.dumps(opening))
    form, data = capture_fixture(path, "handover")
    manifest = recorder.bench_trace.templates(path)["manifest"]
    manifest.update(
        provenance="physical-measurement",
        trial_id=form["trial_id"],
        article_serial=form["article_serial"],
        as_tested_build=form["as_tested_build_sha256"],
        wiring_revision=form["wiring_revision"],
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="provenance"):
        recorder.assess_handover(path, form, data, manifest_path)


@pytest.mark.parametrize(
    "mode,mutation,field,message",
    [
        (
            "brake_feedback_loss",
            lambda i, r: r.update(position=100 if i == 2 else 0),
            "sampling_and_protocol_holds",
            "stationary pre-stimulus",
        ),
        (
            "wrong_side_request",
            lambda i, r: r.update(emergency_brake_output=0),
            "observed_faults",
            "no protective response",
        ),
        (
            "stale_command",
            lambda i, r: r.update(command_sent_ms=100 + i),
            "sampling_and_protocol_holds",
            "corroborate",
        ),
        (
            "stale_command",
            lambda i, r: r.update(command_received=0),
            "sampling_and_protocol_holds",
            "Packet receipt",
        ),
        (
            "evacuation_authorised",
            lambda i, r: r.update(local_handle=0),
            "sampling_and_protocol_holds",
            "local handle edge",
        ),
        (
            "evacuation_authorised",
            lambda i, r: r.update(other_same_side_exit_open=int(i == 10)),
            "observed_faults",
            "Another exit",
        ),
        (
            "power_restart",
            lambda i, r: r.update(boot_epoch=int(i >= 11) + int(i >= 17)),
            "sampling_and_protocol_holds",
            "boot identity changed",
        ),
    ],
)
def test_hardware_fault_proof(opening, tmp_path, mode, mutation, field, message):
    path = tmp_path / "opening.json"
    path.write_text(json.dumps(opening))
    form, data = capture_fixture(path, mode, mutation)
    result = recorder.convert(path, form, data)
    assert any(message in issue for issue in result[field])


def test_device_binding_and_old_records(opening, tmp_path):
    path = tmp_path / "opening.json"
    path.write_text(json.dumps(opening))
    form, data = capture_fixture(path, "stale_command", schema=recorder.LEGACY_SCHEMA)
    assert recorder.convert(path, form, data)["disposition"] == "incomplete observations"
    form, data = capture_fixture(path, "brake_feedback_loss")
    form["visit"]["physical_door_slot"] = 4
    with pytest.raises(ValueError, match="platform-side"):
        recorder.convert(path, form, data)
    form["visit"]["platform_side"] = "right"
    form["inputs"]["holding_force"]["device_terminal"] = "traction_effort"
    with pytest.raises(ValueError, match="same device terminal"):
        recorder.convert(path, form, data)


def test_handover_direction_bound_to_physical_visit(opening, tmp_path):
    path = tmp_path / "opening.json"
    path.write_text(json.dumps(opening))
    form, data = capture_fixture(path, "handover")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "provenance": form["record_kind"],
                "article_serial": form["article_serial"],
                "trial_id": form["trial_id"],
                "as_tested_build": form["as_tested_build_sha256"],
                "wiring_revision": form["wiring_revision"],
                "direction_sign": -1,
            }
        )
    )
    with pytest.raises(ValueError, match="departure direction"):
        recorder.assess_handover(path, form, data, manifest_path)


def test_paired_outage_counts_footprints_on_a_restored_source_boundary():
    sites = [0.0, 2.4000000000000004, 4.800000000000001]
    # Site 1 is isolated. The eastern healthy source serves back to the break.
    # A footprint ending at the break and an eastern train both load its bound.
    windows = {((2.0, 2.4), (4.0, 4.2)): {"seconds": 1, "first_s": 7}}
    results = feeder._paired_replay(sites, windows, 1.5, 1.35, 0.005, 0.003, 3.0, 1.0)
    failed = next(row for row in results if row["failed_site"] == 1)["worst"]
    assert failed["site"] == 2
    assert failed["simultaneous_pulses"] == 2
    assert failed["furthest_fed_km"] == pytest.approx(2.4)
    assert failed["loop_ohm_bound"] == pytest.approx(0.005 + 2.4 * 0.003)
    assert failed["collector_load_bound_mw"] == 7
