import pytest
from engineering.station_rail.motor_review import parallel_winding_options

def full():
    return dict(schema='osr-native-full-station-LIM-2D/1',physical_accepted=False,
        configuration=dict(coils_per_phase_both_sides=50),case=dict(current_RMS_A=100.),
        phase_terminal_requirements=[dict(all_series_phase_voltage_RMS_V=2000.) for _ in range(3)],primary_copper_W=44000.)

def test_parallel_groups_keep_loss_and_expose_unknown_local_flux():
    rows=parallel_winding_options(full());a,b=rows[0],next(r for r in rows if r['parallel_paths_per_phase']==10)
    assert a['arithmetic_voltage_screen']=='fail'
    assert b['arithmetic_voltage_screen']=='pass'
    assert b['series_coils_per_path']==5
    assert b['total_converter_phase_current_RMS_A']==1000
    assert b['primary_copper_loss_W']==a['primary_copper_loss_W']
    assert b['actual_current_sharing_screen']=='unknown'
    assert b['actual_maximum_branch_voltage_RMS_V'] is None

def test_parallel_reconnection_cannot_qualify_equipment():
    r=full();r['physical_accepted']=True
    with pytest.raises(ValueError):parallel_winding_options(r)
