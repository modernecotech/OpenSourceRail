"""Independent executable timetable controls, separate from magnetic dynamics."""
import math
import xml.etree.ElementTree as ET
import pytest
from engineering.ferrite_maglev import operations_crosscheck as o


def line():
    return dict(id='test-fixed',length_m=4000.,headway_s=240.,stops=[dict(id=f's{i}',chainage_m=float(i*2000)) for i in range(3)])


def test_closed_form_independent_trapezoid_and_triangle():
    assert math.isclose(o.free_running_time(2000),2000/20+20/.7)
    assert math.isclose(o.free_running_time(10),2*math.sqrt(10/.7))
    with pytest.raises(ValueError):o.free_running_time(-1)


def test_counted_train_and_explicit_named_negative_cases():
    files,expected=o.input_files(line(),train_mass_kg=210000.,services=2)
    root=ET.fromstring(files['services.rou.xml']);train=root.find('vType')
    assert float(train.get('mass'))==210000. and float(train.get('length'))==104.5
    assert len(root.findall('vehicle'))==4 and len(expected)==8
    with pytest.raises(ValueError):o.input_files(line(),train_mass_kg=210000.,scenario='invented')


@pytest.mark.parametrize('scenario',['nominal','variable-dwell','receiver-failure','capacity-negative-control'])
def test_actual_independent_sumo_retains_outputs_and_detects_overbooking(tmp_path,scenario):
    result=o.execute(tmp_path/scenario,line=line(),configuration_sha256='a'*64,train_mass_kg=210000.,scenario=scenario,services=3)
    assert result['study_pass'],result['screens']
    assert result['tool_version'].startswith('Eclipse SUMO')
    assert all(c['exit_code']==0 for c in result['commands'])
    assert (tmp_path/scenario/'stop-output.xml').is_file()
    assert result['physical_release'] is False
