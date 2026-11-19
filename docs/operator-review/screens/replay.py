"""Write the local review fixture using the selected controls and gateway rules."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from services.integration.osr_integration.store import Store
from services.integration.osr_integration.v07_supervision import simulation_package

ASSETS = ("station-01", "section-01", "grid-01")
START = datetime(2026, 11, 19, 8, 0, tzinfo=timezone.utc).timestamp()


def utc(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).strftime("%H:%M:%S")


def build():
    package = simulation_package(ROOT)
    assert package["environment"] == "simulation"
    config = {item["site_id"]: item for item in package["equipment"]}
    frames = []
    with TemporaryDirectory() as scratch:
        store = Store(Path(scratch) / "review.sqlite3")
        store.apply(package, "review-fixture")
        for seq, (label, elapsed, section) in enumerate((
            ("Normal readings", 0, 0), ("Section trips", 5, 1),
            ("Section signal stale", 38, None), ("Signal restored and trip cleared", 40, 0)
        )):
            now = START + elapsed
            rows = []
            for name in ASSETS:
                if name != "section-01" or section is not None:
                    store.ingest(dict(city=package["city"], environment="simulation",
                                      asset_id=config[name]["asset_id"], source_id="simulator", measurement="protection_trip",
                                      quality="valid", sequence=seq, source_timestamp=datetime.fromtimestamp(now, timezone.utc).isoformat(), unit="state",
                                      value=section if name == "section-01" else 0), "simulator", now)
                asset = store.device(package["city"], "simulation", config[name]["asset_id"], now)
                reading = asset["readings"]["protection_trip"]
                rule = config[name]["alarms"][0]
                alarm = next(item for item in asset["alarms"] if item["rule"] == rule["id"])
                rows.append(dict(asset=name, role=asset["equipment_type"], quality=reading["quality"],
                                 value=reading["value"] if reading["quality"]=="valid" else None,
                                 source_time=utc(reading["source_time"]), active=bool(alarm["active"]),
                                 occurrences=alarm["occurrences"], response=rule["response"]))
            frames.append(dict(name=label, time=utc(now), rows=rows))
    assert [frame["rows"][1]["active"] for frame in frames] == [False, True, True, False]
    assert frames[2]["rows"][1]["quality"] == "stale"
    return dict(candidate=package["physical_candidate_id"], package=package["sha256"],
                evaluation=package["control_interface_evaluation_id"], frames=frames)


if __name__ == "__main__":
    content = json.dumps(build(), sort_keys=True, indent=2)
    path = Path(__file__).with_name("replay-data.js")
    path.write_text("const supervisionReplay = " + content + ";\n")
    print(path.name, sha256(path.read_bytes()).hexdigest())
