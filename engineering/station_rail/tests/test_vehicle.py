from engineering.station_rail import vehicle


def test_motors_and_maglev_stock_removed_but_services_kept():
    v=vehicle.build()
    d=v['physical_definition']
    assert d['vehicle']['onboard_traction_motors']==0
    assert d['vehicle']['onboard_traction_battery_kWh']==0
    assert d['vehicle']['onboard_permanent_magnets']==0
    assert next(r for r in v['inventory'] if r['id']=='service-battery')['mass_kg']>=1345
    assert not any(r['system'] in ('magnetics','propulsion','protection','hardpoints') for r in v['inventory'])
    assert not any('lower-stringer' in p['id'] for p in v['geometry_parts'])
    assert v['mass']['installed_tare_kg_per_car'] is None
    assert v['mass']['accounted_cap_loaded_kg_per_car']-v['mass']['accounted_tare_kg_per_car']==3450


def test_axles_clear_station_stator_and_secondary_ends():
    v=vehicle.build();c=v['clearance']
    assert c['fin_to_nearest_axle_x_m']>.8
    assert c['axle_bottom_above_station_primary_top_m']>.1
    assert c['floor_underside_m']>.93
    assert not c['swept_curves_suspension_travel_wheel_wear_and_turnouts_qualified']
    assert v['support_counts']['wheels_per_train']==48
    assert v['propulsion']['secondary_aluminium_mass_kg']>3*v['propulsion']['active_fin_aluminium_mass_kg']


def test_vehicle_mass_closes_account_not_installed_design():
    v=vehicle.build()
    assert abs(sum(r['mass_kg'] for r in v['inventory'])-v['mass']['accounted_tare_kg_per_car'])<1e-7
    assert v['mass']['unlocated_or_reference_account_kg']>9000
    assert all(v[k] is False for k in ('engineering_accepted','physical_accepted','installed_mass_complete','manufacturing_release','operating_release'))
    assert v['underframe_screens']['normal']['deflection_screen']=='fail'


def test_cassette_material_connections_and_floating_negative_control():
    v=vehicle.build();parts=v['geometry_parts']
    assert vehicle.cassette_connectivity(parts)['engineering_screen']=='pass'
    assert v['clearance']['heat_sink_lowest_point_above_primary_top_m']>.08
    floating=[p for p in parts if p['id']!='station-secondary/upper-neck']
    assert vehicle.cassette_connectivity(floating)['engineering_screen']=='fail'
    short_hangers=[]
    for p in parts:
        p=dict(p)
        if p['id'].startswith('station-secondary/hanger/'):
            p['size_m']=[*p['size_m'][:2],.2]
        short_hangers.append(p)
    assert vehicle.cassette_connectivity(short_hangers)['engineering_screen']=='fail'


def test_new_underframe_does_not_interpenetrate_retained_shell():
    parts=vehicle.build()['geometry_parts']
    frame=[p for p in parts if p.get('system')=='underframe']
    shell=[p for p in parts if p['id'].startswith('comfort-shell/') and p['kind']=='box']
    collisions=[]
    for a in frame:
        for b in shell:
            depths=[min(a['at_m'][i]+a['size_m'][i],b['at_m'][i]+b['size_m'][i])-max(a['at_m'][i],b['at_m'][i]) for i in range(3)]
            if min(depths)>1e-7:collisions.append((a['id'],b['id']))
    assert not collisions
