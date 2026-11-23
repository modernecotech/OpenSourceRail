"""Check the standard-library quotation package through the same producer used by the CLI."""

from hashlib import sha256
from html.parser import HTMLParser
from io import BytesIO
import json
from zipfile import ZipFile

import pytest

from cities.Baghdad.engineering.prototype import mesh, review


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.paths.append(dict(attrs)["href"])


def test_twin_delivers_matching_drawings_costs_and_evidence_forms():
    files, public = review.construct()
    manifest = json.loads(files["manifest.json"])
    assert manifest["sha256"] == {k: sha256(v).hexdigest() for k, v in files.items() if k != "manifest.json"}
    budget = json.loads(files["cash.json"])
    opening = json.loads(files["opening.json"])
    assert budget["candidate_id"] == opening["candidate_id"] == manifest["candidate_id"]
    assert len(budget["annual_cash"]) == 33 and budget["opening_date"] is None
    article = json.loads(files["civil-article.json"])
    decisions = json.loads(files["decision-register.json"])
    assert article["physical_id"] == decisions["civil_cage_id"]
    assert article["candidate_id"] == decisions["airport_candidate_id"]
    assert not decisions["fabrication_released"] and not decisions["operating_authorisation"]
    orders = json.loads(files["draft-work-orders.json"])
    assert all(path in files for order in orders["draft_work_orders"] for path in order["documents"])
    trial = json.loads(files["material-comparison.json"])
    assert (
        trial["steel"]["candidate_id"]
        == manifest["candidate_id"]
        != trial["illustrative_hybrid"]["candidate_id"]
    )
    assert trial["steel"]["mass_t"] - trial["illustrative_hybrid"]["mass_t"] == pytest.approx(3)
    assert trial["hybrid_supplier_price_usd_m"] is None and not trial["hybrid_selected"]
    assert trial["illustrative_hybrid"]["traction_mw"] < trial["steel"]["traction_mw"]
    for content, offline in ((files["START.html"], True), (public, False)):
        links = Links()
        links.feed(content.decode())
        for path in links.paths:
            if path.startswith("#"):
                assert 'id="' + path[1:] + '"' in content.decode()
            elif offline:
                assert path in files
            else:
                assert (review.HERE / path).is_file()
    with ZipFile(BytesIO(review.archive(files))) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(files)


def test_mesh_rejects_unbound_occurrences_and_out_of_range_faces():
    sample = b"o bracket\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
    parts = mesh.read_obj(sample, assembly="bogie")
    assert len(parts) == 1 and parts[0]["id"] == "bracket"
    with pytest.raises(ValueError, match="identities"):
        mesh.read_obj(sample, [{**parts[0], "id": "bearing"}])
    with pytest.raises(ValueError, match="bounds"):
        mesh.read_obj(sample, [{**parts[0], "lower_m": [-1, 0, 0]}])
    with pytest.raises(ValueError, match="face"):
        mesh.read_obj(sample + b"f 1 2 44\n", assembly="bogie")
