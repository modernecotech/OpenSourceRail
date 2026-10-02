"""A changed bundle must not silently retain the fixture's old physical model."""
import copy,json
import pytest
from tools.automation.tacs_reference import BASE,validate_reference_model

def test_supported_bundle_and_rejected_geometry_braking_and_conflict_changes():
    model=json.loads((BASE/'railway-model.json').read_text());validate_reference_model(model)
    changes=(('geometry',),('braking',),('conflicts',))
    for (change,) in changes:
        m=copy.deepcopy(model)
        if change=='geometry':m['routes'][0]['segments'][0]['end_mm']+=1000
        elif change=='braking':m['trains'][0]['config']['minimum_deceleration_mmps2']+=100
        else:m['resources'][2]['conflicts']=[2]
        with pytest.raises(ValueError,match='unsupported'):validate_reference_model(m)
