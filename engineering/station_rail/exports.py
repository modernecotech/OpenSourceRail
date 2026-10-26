"""Same-candidate research delivery records; unpriced/unqualified work stays open."""
from pathlib import Path
import gzip,json
from . import ROOT,FLAGS
from .common import encoded,identity,digest,source_map
from .evaluation import IDS

def compile(record,root=ROOT,city_index=None):
    if city_index is not None and any(city_index.get(k)!=record[k] for k in IDS):raise ValueError('city index belongs to another physical candidate')
    stamp=dict(**{k:record[k] for k in IDS},evaluation_id=record['evaluation_id'],development_default=True,purpose='research and requests for evidence',**FLAGS)
    common=lambda schema,**value:dict(schema=schema,**stamp,**value)
    car=record['vehicle'];s=record['service'];z=s['selected_station'];battery=s['electrical']['battery']
    bom=common('osr-v06-engineering-bom/1',mass=car['mass'],stock_inventory_per_car=car['inventory'],
        formation=dict(cars=6,bogies=12,axles=24,wheels=48),onboard_traction_motors=0,onboard_traction_battery_kWh=0.,
        service_battery=battery,complete_installed_BOM=False,retained_component_ancestry=car['retained_component_ancestry'],residual_overlap_unresolved=car['residual_overlap_unresolved'])
    manufacturing=common('osr-v06-manufacturing/1',production_labour_hours_per_car=None,tooling_cost_USD=None,
        operations=[dict(operation_id='V06-M%02d'%i,operation=op,qualified_process=False,labour_hours=None,inspection_required=True)
          for i,op in enumerate(('Cut and fixture aluminium sills, bows and bogie hardpoints','Join frame and verify diagonal, twist and load-path datums',
            'Prepare, bond and retain GFRP panels and roof/floor sandwiches','Fit doors, glazing, seating, accessible zones and flush PV',
            'Manufacture or procure identical unpowered bogies; inspect wheelsets, bearings and welds','Install independent brakes, WSP, parking and odometry',
            'Fit passive LIM fin and hangers; verify hot and suspension-travel clearance','Install independently fused service/essential supply, HVAC and low-voltage equipment',
            'Weigh equipped car and measure CG/inertia; perform structural, insulation, brake and interface tests'),1)],
        structural_participation='Only demonstrated load paths may receive stiffness credit; panel/joint participation and hot strength remain open')
    procurement=common('osr-v06-procurement/1',stock_inventory_per_car=car['inventory'],total_price_USD=None,
        prices_current=False,supplier_rail_approvals_complete=False,delivery_dates=None,first_material_consumption_dates=None,
        material_availability_blocks_consumption=True,city_scope=dict(city_count=city_index['city_count'] if city_index else None,
            numerical_city_regeneration='held',whole_repository_city_delivery_complete=False))
    sequence=('Site survey and ground investigation','Foundation design and construction','Pier and headstock erection',
      'Install bearings and verify temporary stability','Lift precast span and secure temporary works','Fit conventional running rails and gauge-control fasteners',
      'Install separately supported station LIM sections and electrical equipment','Survey gauge, cant, alignment, joints and dynamic clearance',
      'Inspect, test and independently release completed railway')
    assembly=common('osr-v06-assembly/1',scheduled_start_dates=None,crew_and_crane_resources=None,
        construction_operations=[dict(id='V06-C%02d'%i,operation=op,predecessor=None if i==1 else 'V06-C%02d'%(i-1),
            material_release_required=True,structural_release_required=True,duration_h=None) for i,op in enumerate(sequence,1)],
        vehicle_assembly_sequence=manufacturing['operations'],production_release=False)
    civil=common('osr-v06-civil-export/1',alternatives=record['civil'],fully_installed_route_quantities=None,
        continuous_magnetic_facings=False,rails_per_track=2,station_primary_supports_and_maintenance_walkway_qualified=False)
    controls=common('osr-v06-controls-export/1',architecture='Existing station-led GoA4, independent onboard ATP and mechanical brakes',
        launch_speed_cap_m_s=20.,target_headway_s=120.,normal_capacity_pphpd=8280.,
        shared_station_winding_m=z['length_m'] if z else None,addressed_sections_per_direction=z['sections_per_direction'] if z else None,
        section_length_m=12.5,minimum_independent_train_phase_branches_per_direction=2,
        station_led_functions=['Reserve protected route and receiving berth','Prove configuration, doors, train integrity, service/brake reserve and receiver readiness',
            'Sequence launch sections and monitor continuous movement authority','Supervise coast; preserve independent onboard stopping',
            'Receive, stop, prove zero speed, apply holding brake and authorise platform access'],
        onboard_functions=['Independent ATP and mechanical service/emergency/parking braking','Wheel odometry and bounded localisation',
            'Integrity, communications and services monitoring','No autonomous off-zone propulsion'],
        mainline_switches=False,depot_switch_exceptions=True,
        station_converter_rating=None,qualified_braking_floor_m_s2=None,actual_physical_headway_s=None,
        wheel_suspension_independent_of_station_power=True,magnetic_suspension_inputs=False,
        contract_fixture='crates/osr-atp/examples/wheel_station_contract.rs',qualified_GoA4_product=False)
    return dict(bom=bom,manufacturing=manufacturing,procurement=procurement,assembly=assembly,civil=civil,controls=controls)

def write(output,record,root=ROOT,city_index=None,native=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);values=compile(record,root,city_index)
    for key,value in values.items():
        name='engineering-bom' if key=='bom' else key
        raw=encoded(value);(output/(name+'.json.gz' if key in ('bom','procurement') else name+'.json')).write_bytes(gzip.compress(raw,mtime=0) if key in ('bom','procurement') else raw)
    cad=dict(schema='osr-v06-cad-reference/1',**{k:record[k] for k in IDS},development_default=True,
        execution='not-run' if native is None else native.get('execution','completed'),
        native=native,complete_installed_geometry=False,**FLAGS)
    (output/'cad.json').write_bytes(encoded(cad))
    from . import bim
    (output/'bim.json').write_bytes(encoded(bim.write(output,record)))
    m=dict(schema='osr-v06-delivery-manifest/1',**{k:record[k] for k in IDS},evaluation_id=record['evaluation_id'],
        development_default=True,source_sha256=source_map(root,('engineering/station_rail/exports.py','engineering/station_rail/bim.py')),
        files_sha256={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file() and p.name!='manifest.json'},**FLAGS)
    m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m));return m

def verify(output,record,root=ROOT,city_index=None):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if any(m.get(k)!=record[k] for k in (*IDS,'evaluation_id')):raise ValueError('delivery candidate differs')
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('delivery manifest identity differs')
    if m['source_sha256']!=source_map(root,('engineering/station_rail/exports.py','engineering/station_rail/bim.py')):raise ValueError('delivery source differs')
    if {p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('delivery payload differs')
    for key,value in compile(record,root,city_index).items():
        name='engineering-bom' if key=='bom' else key;compressed=key in ('bom','procurement')
        raw=(output/(name+'.json.gz' if compressed else name+'.json')).read_bytes()
        if (gzip.decompress(raw) if compressed else raw)!=encoded(value):raise ValueError('delivery calculation differs')
    from . import bim
    receipt=json.loads((output/'bim.json').read_bytes())
    if receipt['execution']=='completed':bim.verify(output/'selected-interface.ifc',record,receipt)
    return dict(current=True,manifest_id=m['manifest_id'],complete_installed_BOM=False,**FLAGS)
