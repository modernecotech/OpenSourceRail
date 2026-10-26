import pytest
from engineering.station_rail.native_drive import exact_slab,conditional_map


def test_secondary_diffusion_energy_force_identity_and_field_scaling():
    a=exact_slab(field_peak_T=.1)
    b=exact_slab(field_peak_T=.2)
    assert b['conditional_longitudinal_force_N']==pytest.approx(4*a['conditional_longitudinal_force_N'])
    assert b['conditional_secondary_Joule_W']/b['conditional_longitudinal_force_N']==pytest.approx(b['slip_frequency_Hz']*b['wavelength_m_hypothesis'])
    assert b['useful_force_is_available'] is False


def test_conditional_boundary_field_never_becomes_available_motor_force():
    result=conditional_map(10000)
    assert len(result['cases'])==15
    assert result['available_force_N_per_car'] is None
    assert all(c['actual_current_to_force_map'] is None for c in result['cases'])
    assert result['engineering_accepted'] is False
