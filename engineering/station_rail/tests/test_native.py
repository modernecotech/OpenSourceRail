from engineering.station_rail import native,vehicle


def test_native_fixture_is_current_hollow_section_and_current_force():
    v=vehicle.build();deck,n,e=native._ccx_deck(v,.2)
    assert 'TYPE=C3D8' in deck
    assert ',0.508' in deck or ',0.508\n' in deck
    assert n>1000 and e>500
    total=sum(float(line.split(',')[2]) for line in deck.split('*CLOAD\n')[1].split('*NODE PRINT')[0].splitlines() if line)
    expected=-v['mass']['accounted_cap_loaded_kg_per_car']*9.80665/2
    assert abs(total-expected)<1e-5
