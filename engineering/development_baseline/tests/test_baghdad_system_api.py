"""One live Workbench edit must carry one candidate through the Baghdad system."""
import json
import shutil
import threading
import urllib.error
import urllib.request

from engineering.development_baseline.server import make_server
from engineering.outline.baghdad_system import ROOT, load


def test_baghdad_workbench_joined_edit():
    server = make_server(root=ROOT, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with urllib.request.urlopen(base + "/api/v07/baghdad-system") as response:
            summary = json.load(response)
        assert summary["networks"]["first"]["digital_cost_leader"] == "protected_conductor"

        def edit(supply, span=10, candidate=None):
            body = json.dumps({
                "expected_candidate_id": candidate or load(ROOT)["candidate_id"],
                "network": "first", "supply": supply, "span_m": span,
                "common_pier": False,
            }).encode()
            request = urllib.request.Request(base + "/api/v07/baghdad-system", body,
                                             {"Content-Type": "application/json", "Origin": base},
                                             method="POST")
            with urllib.request.urlopen(request) as response:
                return json.load(response)

        conductor = edit("protected_conductor")
        battery = edit("station_battery")
        longer_span = edit("protected_conductor", 20)
        assert conductor["service"]["route_km"] == battery["service"]["route_km"]
        assert conductor["vehicle"]["mass_t"] < battery["vehicle"]["mass_t"]
        assert conductor["civil"]["quantities"]["beam_count"] == battery["civil"]["quantities"]["beam_count"]
        assert conductor["civil"]["physical_screen"]["candidate_crowd_train_t"] != battery["civil"]["physical_screen"]["candidate_crowd_train_t"]
        assert conductor["capital_usd_m"]["installed"] != battery["capital_usd_m"]["installed"]
        assert longer_span["civil"]["quantities"]["beam_count"] < conductor["civil"]["quantities"]["beam_count"]
        assert longer_span["physical_candidate_id"] != conductor["physical_candidate_id"]
        metro_body = json.dumps({
            "expected_candidate_id": load(ROOT)["candidate_id"],
            "network": "metropolitan", "supply": "protected_conductor",
            "span_m": 10, "common_pier": False,
        }).encode()
        metro_request = urllib.request.Request(base + "/api/v07/baghdad-system", metro_body,
                                               {"Content-Type": "application/json", "Origin": base},
                                               method="POST")
        with urllib.request.urlopen(metro_request) as response:
            metro = json.load(response)
        assert metro["service"]["route_km"] == 605.652
        assert metro["service"]["line_count"] == 14
        assert metro["local_delivery"]["planning_local_contract_usd_m"] > 12000
        try:
            edit("protected_conductor", candidate="stale-candidate")
            assert False, "stale candidate was accepted"
        except urllib.error.HTTPError as error:
            assert error.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_citywide_post_does_not_require_first_plan_map(tmp_path):
    cfg = load()
    target = tmp_path / "cities/Baghdad/system.toml"
    target.parent.mkdir(parents=True)
    target.write_text((ROOT / "cities/Baghdad/system.toml").read_text().replace(
        cfg["map_sources"]["first_sha256"], "first-map-not-present"))
    source_map = ROOT / cfg["map_sources"]["metropolitan_path"]
    dest_map = tmp_path / cfg["map_sources"]["metropolitan_path"]
    dest_map.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_map, dest_map)
    for name in ("baghdad_power.py", "baghdad_viaduct.py"):
        source = ROOT / "engineering/outline" / name
        dest = tmp_path / "engineering/outline" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    server = make_server(root=tmp_path, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        body = json.dumps({"expected_candidate_id": cfg["candidate_id"],
                           "network": "metropolitan", "supply": "protected_conductor",
                           "span_m": 10, "common_pier": False}).encode()
        request = urllib.request.Request(base + "/api/v07/baghdad-system", body,
                                         {"Content-Type": "application/json", "Origin": base},
                                         method="POST")
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
        assert result["service"]["route_km"] == 605.652
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
