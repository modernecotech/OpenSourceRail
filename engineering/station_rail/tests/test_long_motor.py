from engineering.station_rail import long_motor as m

def test_full_primary_and_actual_fin_are_separate_physical_lengths():
    g=m.configuration();c=m.case()
    assert g['primary_length_m']==12.5
    assert g['secondary_length_m']==9
    assert g['secondary_start_x_m']==1.75
    assert g['coils_per_phase_both_sides']==50
    assert c['gap_each_side_m']/c['plate_gap_mesh_m']>=3
    assert c['mesh_m']<=.5/16
    assert g['steel_kg']+g['copper_kg']>2800

def test_all_phase_terminal_integrals_are_in_generated_native_model():
    p=m.formulation(m.case(),m.short.definition())
    assert all(('phase'+phase+'.txt') in p for phase in 'ABC')
    assert 'PhaseA=Region[{100,103}]' in p
