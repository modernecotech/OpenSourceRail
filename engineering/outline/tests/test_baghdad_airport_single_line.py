from copy import deepcopy
from xml.etree import ElementTree

import pytest

from cities.Baghdad.airport_opening import calculate, opening_inputs
from cities.Baghdad.airport_service import build_service
from cities.Baghdad.airport_single_line import single_line_svg


def test_drawing_follows_costed_source_breaker_and_tie_counts_for_each_load():
    inputs = opening_inputs()
    service = build_service(inputs[0], inputs[1]["networks"]["first"]["groups"]["Airport"])
    sizes = []
    for mass in (None, 190.0):
        opening = calculate(inputs=inputs, service=service, loaded_mass_t=mass, size_feeder=True)
        svg = single_line_svg(opening)
        root = ElementTree.fromstring(svg)
        n = opening["bundle"]["grid_sites"]
        assert len(root.findall('.//*[@data-device="breaker"]')) == 4*(n-1)
        assert len(root.findall('.//*[@data-device="tie"]')) == 2*(n-1)
        assert opening["candidate_id"] in svg and opening["bundle"]["feeder_design_id"] in svg
        assert f"S{n:02d}" in svg and "12.000 km" in svg and "negative return" in svg
        assert "backfeed" in svg and "earthing" in svg
        sizes.append(n)
    assert sizes[0] != sizes[1]
    mixed = deepcopy(opening)
    mixed["bundle"]["feeder_design_id"] = "wrong"
    with pytest.raises(ValueError, match="matching identities"):
        single_line_svg(mixed)
    with pytest.raises(ValueError, match="priced Airport radial feeder"):
        single_line_svg(calculate(inputs=inputs))
