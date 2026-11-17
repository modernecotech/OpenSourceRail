"""One live Workbench edit must carry one candidate through the Baghdad system."""
import json
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
        try:
            edit("protected_conductor", candidate="stale-candidate")
            assert False, "stale candidate was accepted"
        except urllib.error.HTTPError as error:
            assert error.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
