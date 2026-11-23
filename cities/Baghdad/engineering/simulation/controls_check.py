"""Replay the issued six-car station visit with the locked Rust adapter."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from cities.Baghdad.engineering.simulation.scenario import HERE, ROOT, PACKET


def replay():
    with ZipFile(PACKET) as z:
        raw = z.read("opening.json")
        bound = json.loads(z.read("returns/handover-logger.json"))["binding"]
    sources = bound["control_source_sha256"]
    if any(sha256((ROOT / path).read_bytes()).hexdigest() != h for path, h in sources.items()):
        raise ValueError("Reissue the station interface records against this control build")
    with TemporaryDirectory() as temp:
        path = Path(temp) / "opening.json"
        path.write_bytes(raw)
        command = ["cargo", "run", "--quiet", "--locked", "--manifest-path",
                   "cities/Baghdad/engineering/controls/Cargo.toml", "--", "--opening", str(path)]
        lines = subprocess.check_output(command, cwd=ROOT, text=True).splitlines()
    opening = json.loads(raw)
    if lines[:2] != ["physical " + opening["candidate_id"], "system evaluation " + opening["evaluation_id"]]:
        raise ValueError("Rust replay did not select the Airport issue")
    return dict(physical=opening["candidate_id"], opening=opening["evaluation_id"], formation_cars=6,
                replay_id=lines[2].split()[-1], source_sha256=sources,
                observations=lines[3:], evidence_class="simulated inputs; six-car secured station visit",
                measured_hardware_response=None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = replay()
    target = HERE / "controls-replay.json"
    if args.write:
        target.write_text(json.dumps(result, indent=2) + "\n")
    elif json.loads(target.read_bytes()) != result:
        raise SystemExit("Reissued Rust replay differs")
    print(result["replay_id"])
