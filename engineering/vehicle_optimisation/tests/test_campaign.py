from copy import deepcopy
import json
import pytest
from engineering.design_search.contracts import identity
from engineering.passive_suspension import fields
from engineering.passive_suspension.tests.test_fields import fixture
from engineering.vehicle_optimisation import campaign, magnets


def test_actual_checked_primitive_cannot_be_relabelled_as_hot_or_smaller_gap():
    geometry=fixture()
    raw=fields.solve(geometry,gap_m=.03,temperature_C=20.,settings=campaign.FIELD_SETTINGS)
    campaign.check_field(raw,geometry,gap_m=.03,temperature_C=20.)
    with pytest.raises(ValueError,match='operating point'):
        campaign.check_field(raw,geometry,gap_m=.03,temperature_C=80.)
    with pytest.raises(ValueError,match='operating point'):
        campaign.check_field(raw,geometry,gap_m=.008,temperature_C=20.)
    with pytest.raises(ValueError,match='operating point'):
        campaign.check_field(raw,geometry,gap_m=.03,temperature_C=20.,currents_A={'lift':20.})


def test_resealed_worker_with_missing_schedule_is_not_admitted(tmp_path):
    payload=dict(candidates=magnets.candidates(),source_sha256=magnets.sources(),rows=[])
    payload['study_id']=identity(payload)
    path=tmp_path/'study.json';path.write_text(json.dumps(payload))
    with pytest.raises(ValueError,match='schedule'):
        campaign.load_workers(path,tmp_path/'missing-refinement.json',tmp_path/'missing-nonlinear.json')


def test_steel_to_aluminium_analysis_hypotheses_do_not_change_physical_identity():
    magnet=magnets.candidates()[0]
    member=dict(id='frame/member',width_m=.1,depth_m=.2,wall_m=.003,length_m=2.,
                section={'area_m2':.001},reference_EI_N_m2=[1.,2.],proposed_EI_N_m2=[3.,4.],stiffness_necessary_pass=False)
    chassis=dict(id='prototype',material=dict(alloy='6082',temper='T6',density_kg_m3=2710.),
                 members=[member],stock_parts=[])
    mode=dict(chassis=chassis,fitout=None,climate=None)
    before=identity(campaign.physical_descriptor(magnet,mode))
    member.update(reference_EI_N_m2=[100.,200.],proposed_EI_N_m2=[300.,400.],stiffness_necessary_pass=True)
    assert identity(campaign.physical_descriptor(magnet,mode))==before
    member['wall_m']=.004
    assert identity(campaign.physical_descriptor(magnet,mode))!=before


def test_reduced_halbach_retains_actual_winding_packing_failure():
    value=magnets._build(tuple(campaign.REFINEMENT_RECIPES[0]))
    rows=campaign.winding_screen(value)
    assert rows[0]['bare_copper_fill']>.55
    assert rows[0]['pass_screen'] is False
