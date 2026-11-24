from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import PurePosixPath
import posixpath
import re
from unittest.mock import patch
from zipfile import ZipFile

import pytest

from cities.Baghdad.engineering.prototype import enquiries
from engineering.outline.baghdad_system import _id


class AnchorLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.targets.append(dict(attrs)["href"])


def test_published_issue_matches_erp_drawings_and_all_local_links():
    members = enquiries.contents()
    with ZipFile(enquiries.ISSUE) as z:
        assert {p: z.read(p) for p in z.namelist()} == members
    result = json.loads(members["manifest.json"])
    assert _id({k: v for k, v in result.items() if k != "issue_id"}) == result["issue_id"]
    assert {k: sha256(v).hexdigest() for k, v in members.items() if k != "manifest.json"} == result["sha256"]
    assert result["fabrication_released"] is False and result["operating_authorisation"] is False
    assert result["current_enquiry"] is False and result["route_scope"] == "12 km schematic"
    assert b"corrected 17.46 km horizontal study" in members["START.html"]
    tender = json.loads(members["sourcing-estimate.json"])
    assert result["estimate_evaluation_id"] == tender["evaluation_id"]
    costs = json.loads(members["shop-costs.json"])
    cam = json.loads(members["cam/cam-manifest.json"])
    assert result["cam_evaluation_id"] == cam["evaluation_id"]
    assert result["shop_cost_evaluation_id"] == costs["evaluation_id"]
    assert members["machine-offer.csv"] == enquiries.shop_offers.template(costs)
    assert all(members["cam/" + p] and sha256(members["cam/" + p]).hexdigest() == digest
               for p, digest in cam["artifact_sha256"].items())
    assert members["cam/input/stock.toml"] == enquiries.cam.STOCK.read_bytes()
    lots = {r["lot_id"] for r in tender["lots"]}
    assert len(result["package_lots"]) == 6
    for package in result["package_lots"]:
        assert package["lot_id"] in lots and package["schedule"] in members
    for name, content in members.items():
        if name.endswith(".html"):
            links = AnchorLinks()
            links.feed(content.decode())
            targets = links.targets
        elif name.endswith(".md") and not name.endswith("LICENSE.md"):
            targets = re.findall(r"\]\(([^)\s]+)\)", content.decode())
        else:
            continue
        for target in targets:
            path = target.split("#", 1)[0]
            if path and not path.startswith(("https://", "http://", "mailto:")):
                assert posixpath.normpath(str(PurePosixPath(name).parent / path)) in members, (name, path)


def test_issue_refuses_a_different_erp_estimate():
    with patch.object(enquiries.sourcing_estimates, "estimate_lots", return_value={"candidate_id": "other"}):
        with pytest.raises(ValueError, match="buyer estimate"):
            enquiries.contents()
