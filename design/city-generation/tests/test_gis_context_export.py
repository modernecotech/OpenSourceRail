import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_gis_context_export_is_deterministic_and_georeferenced(tmp_path: Path) -> None:
    source = tmp_path / "city.json"
    source.write_text(
        json.dumps(
            {
                "bbox": {"south": 1, "west": 2, "north": 3, "east": 4},
                "slug": "fixture",
                "fetched_at": 1_700_000_000,
                "arterials": [
                    {
                        "id": 7,
                        "class": "primary",
                        "name": "Test Road",
                        "nodes": [[1.1, 2.2], [1.2, 2.3]],
                    }
                ],
                "buildings": [],
                "water": [],
                "protected": [],
                "rail_existing": [],
            }
        ),
        encoding="utf-8",
    )
    first = tmp_path / "first"
    second = tmp_path / "second"
    lock_path = tmp_path / "sources.lock.json"
    lock_path.write_text('{"schema_version":1,"sources":[]}\n', encoding="utf-8")
    command = [sys.executable, str(ROOT / "tools/automation/export-gis-context.py"), str(source)]
    subprocess.run([*command, str(first)], check=True, capture_output=True, text=True)
    subprocess.run([*command, str(second)], check=True, capture_output=True, text=True)

    assert {path.name: path.read_bytes() for path in first.iterdir()} == {
        path.name: path.read_bytes() for path in second.iterdir()
    }
    roads = json.loads((first / "context-roads.geojson").read_text(encoding="utf-8"))
    assert roads["metadata"]["coordinate_reference_system"] == "EPSG:4326"
    assert roads["metadata"]["license"] == "ODbL 1.0"
    assert roads["features"][0]["geometry"]["coordinates"] == [[2.2, 1.1], [2.3, 1.2]]
    assert roads["features"][0]["properties"]["osm_id"] == 7
    locks = json.loads(lock_path.read_text(encoding="utf-8"))["sources"]
    assert {entry["id"] for entry in locks} == {
        "context-buildings",
        "context-existing-rail",
        "context-protected",
        "context-roads",
        "context-water",
    }
    assert all(len(entry["sha256"]) == 64 for entry in locks)
