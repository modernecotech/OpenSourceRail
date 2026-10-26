"""Equal-service research comparison, with explicit incompatible/unknown evidence."""
from . import ROOT,FLAGS
from .common import identity,source_map
from .families import describe,Family
from .operations import profile

def evaluate(record,root=ROOT):
    wheel=record['vehicle'];old=describe(Family.PM_MAGLEV,root)['vehicle'];rows=[]
    assumptions=[('v0.6 wheel/LIM',wheel['mass']['accounted_tare_kg_per_car'],.0025,50.,'New 17m comfort candidate; counted/reference/allowance mass, incomplete installation'),
       ('v0.5 PM maglev',old['mass']['accounted_tare_kg_per_car'],0.,1000.,'Retained 17m comfort candidate; original assumed constant drag, no stable hover demonstrated'),
       ('v0.4 station-launch mass proxy',23680.,.0025,50.,'26,250kg/car controlled budget less2,570kg traction/battery categories; assumes replacing shared auxiliaries is free, so optimistic. Original16.5m LM3 requires redesign for17m comfort service.')]
    for name,tare,rr,bearing,scope in assumptions:
        loaded=tare+46*75
        rot=(record['service']['rotating_stock']['equivalent_inertial_mass_kg_per_car'] if name=='v0.6 wheel/LIM' else 0.)
        cases=[profile(d,loaded,rolling_coefficient=rr,bearing_drag_N_per_car=bearing,loading='46 people/car',rotating_equivalent_mass_kg_per_car=rot) for d in (1500.,2000.)]
        rows.append(dict(name=name,accounted_tare_kg_per_car=tare,comparison_normal_loaded_kg_per_car=loaded,
            passengers_per_car=46,people_per_train=276,headway_s=120.,capacity_pphpd=8280.,
            launch_cap_m_s=20.,acceleration_m_s2=.4,service_deceleration_m_s2=.6,dwell_s=35.,
            scope=scope,profiles=cases,rotating_inertial_mass_kg_per_car=rot,rotating_stock_coverage='counted current wheel stock' if name=='v0.6 wheel/LIM' else 'zero for maglev; unresolved in v0.4 mass proxy',actual_vehicle_price_USD=None,installed_guideway_USD_per_directional_km=None,
            station_equipment_price_USD=None,annual_OPEX_USD=None,whole_life_cost_USD=None,
            prices_and_service_reliability_comparable=False,physical_accepted=False))
    civil=record['civil'];rate=civil['reference_rates_per_directional_km'];selected=civil['selected_reference'];ref=next(r for r in civil['alternatives'] if r['family']=='box-beam' and r['span_m']==25.)
    value=dict(schema='osr-v06-equal-service-comparison/1',selection_id=record['selection_id'],candidate_id=record['candidate_id'],
        purpose='Compare declared necessary quantities and point-mass requirements, not economic or physical acceptance',
        alternatives=rows,
        mass_change_from_v05_kg_per_car=rows[0]['accounted_tare_kg_per_car']-rows[1]['accounted_tare_kg_per_car'],
        mass_change_from_v04_stripped_arithmetic_kg_per_car=rows[0]['accounted_tare_kg_per_car']-rows[2]['accounted_tare_kg_per_car'],
        selected_civil_reference={key:selected[key] for key in ('span_m','load_case','prestress_strands','concrete_m3','running_rail_kg','direct_fastener_sets','counted_steel_kg','total_counted_span_mass_kg')},
        civil_comparison=dict(v05_structural_interface_steel_kg_per_25m=21627.329,
            v05_preliminary_concrete_m3_per_25m=17.,
            v06_running_rails_and_fasteners_kg_per_25m=ref['running_rail_kg']+ref['direct_fastener_kg'],
            v06_all_counted_steel_including_rebar_prestress_and_anchors_kg_per_25m=ref['counted_steel_kg'],
            v06_concrete_m3_per_25m=ref['concrete_m3'],
            v06_rails_kg_per_directional_km=rate['running_rail_kg'],
            boundaries='Old structural/interface steel excludes reinforcement and prestress. New all-counted steel includes preliminary reinforcement, prestress and fastener accounts. Neither includes complete bearings, piers, foundations, walkways, containment or station motors. Material reduction is not installed cost reduction.'),
        selection_decision='Select v0.6 for reference/prototype investigation by user direction: remove unresolved levitation and continuous magnetic facing assemblies. Retain v0.5 evidence and LSM comparison. Vehicle account is heavier than v0.5; lower whole-life cost is unknown.',
        economics_acceptance='unknown',numerical_city_regeneration='held',
        cost_coverage=dict(vehicle_quotes=False,civil_installed_quotes=False,station_power_quotes=False,
            maintenance_and_renewals=False,availability_and_staffing=False,energy_tariffs=False,financing=False),
        source_sha256=source_map(root,('engineering/station_rail/comparison.py','engineering/station_rail/families.py','engineering/station_rail/history.py')),**FLAGS)
    value['evaluation_id']=identity(value);return value
