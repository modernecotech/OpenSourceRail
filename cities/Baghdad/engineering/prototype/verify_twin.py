"""Inspect the exported quotation packet with independent IFC4 geometry and schema readers."""

from argparse import ArgumentParser
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
from zipfile import ZipFile

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.validate


class ModelPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_model = False
        self.data = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "a":
            self.links.append(attr["href"])
        if tag == "script":
            self.in_model = attr.get("id") == "model-data"

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_model = False

    def handle_data(self, text):
        if self.in_model:
            self.data = json.loads(text)


def inspect(path):
    result = {}
    with ZipFile(path) as z:
        manifest = json.loads(z.read("manifest.json"))
        names = z.namelist()
        assert len(set(names)) == len(names) and set(manifest["sha256"]) == set(names) - {"manifest.json"}
        for name, checksum in manifest["sha256"].items():
            assert sha256(z.read(name)).hexdigest() == checksum, name
        for name in names:
            if name.endswith(".md") and name != "LICENSE.md":
                for ref in re.findall(r"\]\(([^)]+)\)", z.read(name).decode()):
                    link = ref.split("#")[0]
                    if link and not link.startswith(("https://", "http://")):
                        assert posixpath.normpath(posixpath.join(posixpath.dirname(name), link)) in names, (
                            name,
                            link,
                        )
        opening = json.loads(z.read("opening.json"))
        candidate = opening["candidate_id"]
        assert (
            candidate
            == manifest["candidate_id"]
            == json.loads(z.read("decision-register.json"))["airport_candidate_id"]
        )
        assert (
            candidate
            == json.loads(z.read("returns/finance.json"))["candidate_id"]
            == json.loads(z.read("returns/weights.json"))["basis"]["candidate_id"]
        )
        h = sha256(z.read("opening.json")).hexdigest()
        for name in names:
            if name.endswith("-logger.json"):
                capture = json.loads(z.read(name))["binding"]
                assert capture["opening_sha256"] == h and capture["opening_candidate"] == candidate
            elif name.endswith(("-feeder.json", "-hot-test.json")):
                assert json.loads(z.read(name))["binding"]["opening_candidate_id"] == candidate
        page = ModelPage()
        page.feed(z.read("START.html").decode())
        assert all(href.startswith("#") or href in names for href in page.links)
        for selection, entries in page.data["geometry"].items():
            file = "car-and-bogies" if selection == "car" else selection
            model = ifcopenshell.file.from_string(z.read(file + ".ifc").decode())
            logger = ifcopenshell.validate.json_logger()
            ifcopenshell.validate.validate(model, logger)
            assert not logger.statements, logger.statements[:1]
            mesh = {}
            for line in z.read(file + ".obj").decode().splitlines():
                fields = line.split()
                if not fields:
                    continue
                if fields[0] == "o":
                    points = []
                    mesh[fields[1]] = points
                elif fields[0] == "v":
                    points.append(tuple(map(float, fields[1:])))
            products = {p.Tag: p for p in model.by_type("IfcBuildingElementProxy")}
            assert set(products) == set(mesh) == {p["id"] for p in entries}
            settings = ifcopenshell.geom.settings()
            for entry in entries:
                product = products[entry["id"]]
                # OpenCascade triangulation includes transform and IFC metre conversion.
                shape = ifcopenshell.geom.create_shape(settings, product)
                coords = list(shape.geometry.verts)
                assert len(coords) >= 9 and len(coords) % 3 == 0
                cloud = list(zip(coords[::3], coords[1::3], coords[2::3]))
                for k in range(3):
                    for func, name in ((min, "lower_m"), (max, "upper_m")):
                        bound = func(pt[k] for pt in cloud)
                        assert abs(bound - entry[name][k]) < 2e-6, (entry["id"], bound, entry[name][k])
                        assert abs(bound - func(pt[k] for pt in mesh[entry["id"]])) < 2e-6
                assert (
                    len(product.Decomposes) == 1
                    and product.Decomposes[0].RelatingObject.Name == entry["assembly"]
                )
            result[selection] = len(products)
    return result


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    print(json.dumps(inspect(parser.parse_args().packet)))
