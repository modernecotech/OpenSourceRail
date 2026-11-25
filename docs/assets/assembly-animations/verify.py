"""Verify the paired assembly publication against its named geometry and current sources."""

import argparse
import csv
import gzip
import importlib
import json
from pathlib import Path
import subprocess

from ledger import FILMS, ROOT, digest, validate_dependencies
from PIL import Image, ImageChops

from render import LIMIT_BYTES, raster
from scene import load_obj

HERE = Path(__file__).resolve().parent


def read_json(path):
    return json.loads(path.read_bytes())


def verified_sources(sources):
    assert sources
    for source, checksum in sources.items():
        assert digest((ROOT / source).read_bytes()) == checksum, source


def verify_film(path, film, receipt, decode):
    mp4 = path / f"{film}.mp4"
    assert mp4.stat().st_size == receipt["bytes"] < LIMIT_BYTES, mp4
    assert digest(mp4.read_bytes()) == receipt["mp4_sha256"], mp4
    assert digest((path / f"{film}.webp").read_bytes()) == receipt["poster_sha256"]
    verified_sources(receipt["source_sha256"])
    if not decode:
        return
    details = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(mp4)]))
    stream, = details["streams"]
    assert (stream["codec_name"], stream["width"], stream["height"], stream["pix_fmt"]) == (
        "h264", receipt["width_px"], receipt["height_px"], "yuv420p")
    assert float(details["format"]["duration"]) == receipt["seconds"]
    assert int(stream["nb_frames"]) == receipt["fps"] * receipt["seconds"]
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(mp4), "-f", "null", "-"], check=True)


def verify(path, decode=False):
    ledger = read_json(path / "assembly-ledger.json")["candidates"]
    videos = read_json(path / "receipt.json")
    views = read_json(path / "views-receipt.json")
    assert set(FILMS) == set(ledger) == set(videos)
    verified_sources(views["sources"])
    assert {"train-exterior", "train-interior", "train-connector", "viaduct-placement",
            "viaduct-completed"}.issubset(views["views"])
    for name, record in views["views"].items():
        image = path / f"{name}.jpg"
        assert digest(image.read_bytes()) == record["render_sha256"], image
    for name, frame_times in (("train", (144,)), ("viaduct", (43, 57))):
        module = importlib.import_module(name)
        for seconds in frame_times:
            with Image.open(path / f"{name}-{seconds}.png") as screenshot:
                assert ImageChops.difference(screenshot.convert("RGB"), raster(module, seconds)).getbbox() is None
    with (path / "assembly-bom.csv").open(newline="") as bom:
        bom_rows = {(row["film"], row["key"]): row for row in csv.DictReader(bom)}

    schedule = read_json(path / "workplan/plan.json")
    assert (path / "assembly-plan.json").read_bytes() == (path / "workplan/plan.json").read_bytes()
    verified_sources(schedule["source_sha256"])
    work_rows = {row["work_id"]: row for row in schedule["rows"]}
    assert len(work_rows) == len(bom_rows) == sum(len(x["parts"]) for x in ledger.values())
    result = read_json(path / "workplan/summary.json")
    receipt = read_json(path / "workplan/run-receipt.json")
    verified_sources(receipt["evaluator_source_sha256"])
    assert receipt["input_sha256"] == result["input_sha256"] == digest((path / "assembly-plan.json").read_bytes())
    assert result["row_count"] == len(work_rows) and result["availability_bps"] == 9000
    for file, checksum in receipt["file_sha256"].items():
        assert digest((path / "workplan" / file).read_bytes()) == checksum, file

    for film, model in ledger.items():
        verified_sources(model["source_sha256"])
        validate_dependencies(model["parts"])
        assert schedule["scope"]["candidate_ids"][film] == model["candidate_id"]
        obj = gzip.decompress((path / model["part_file"]).read_bytes())
        assert digest(obj) == model["geometry_sha256"]
        mesh_names = {mesh for part in model["parts"] for mesh in part["geometry_objects"]}
        assert set(load_obj(obj.decode())) == mesh_names
        for part in model["parts"]:
            bom = bom_rows[film, part["key"]]
            row = work_rows[f"{film}-{part['key']}"]
            assert bom["candidate_id"] == model["candidate_id"]
            assert int(bom["quantity"]) == part["quantity"] and row["cost_account"] == part["account"]
            for metric in ("mass_kg", "price_usd"):
                bounds = part[f"unit_{metric}"]
                for index, case in enumerate(("low", "base", "high")):
                    exported = bom[f"extended_{metric}_{case}"]
                    assert (not exported if bounds is None
                            else abs(float(exported) - bounds[index] * part["quantity"]) <= .00000501), part["key"]
            required = part["unit_person_hours"] * part["quantity"] * 60
            assert required <= row["required_minutes"] < required + 1.00001
        verify_film(path, film, videos[film], decode)
        print(f"{film}: {len(model['parts'])} work packages, {len(mesh_names)} CAD objects, "
              f"{videos[film]['seconds']} seconds, {videos[film]['bytes']:,} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=HERE)
    parser.add_argument("--decode", action="store_true", help="Decode both complete videos")
    args = parser.parse_args()
    verify(args.path, args.decode)
