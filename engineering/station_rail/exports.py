"""Same-candidate research delivery records; unpriced/unqualified work stays open."""
from pathlib import Path
import gzip,json,math
from . import ROOT,FLAGS
from .common import encoded,identity,digest,source_map
from .evaluation import IDS

CASES=('low','base','high')

def _ordered_hours(values,label):
    if not isinstance(values,list) or len(values)!=len(CASES):
        raise ValueError(label+' requires low/base/high hours')
    result={}
    for case,value in zip(CASES,values):
        if isinstance(value,bool) or not isinstance(value,(int,float)):
            raise ValueError(label+' must be finite nonnegative hours')
        value=float(value)
        if not math.isfinite(value) or value<0:
            raise ValueError(label+' must be finite nonnegative hours')
        result[case]=value
    if not result['low']<=result['base']<=result['high']:
        raise ValueError(label+' low/base/high order differs')
    return result

def _process_hour_schedule(cost,record):
    """Expose cost-ledger process hours without guessing broad-operation allocation."""
    for key in IDS:
        if cost.get(key)!=record.get(key):
            raise ValueError('process-hour cost record uses a different '+key)
    if cost.get('evaluation_id')!=record.get('evaluation_id'):
        raise ValueError('process-hour cost record uses a different evaluation')
    if (cost.get('schema')!='osr-v06-selected-vehicle-class-c-cost/1'
            or cost.get('development_default') is not True or cost.get('estimate_class')!='C'
            or cost.get('currency')!='IQD'):
        raise ValueError('selected candidate Class C cost record required for process hours')
    estimate_id=cost.get('cost_estimate_id')
    if not isinstance(estimate_id,str) or identity({k:v for k,v in cost.items() if k!='cost_estimate_id'})!=estimate_id:
        raise ValueError('process-hour cost estimate identity differs')
    cars=cost.get('vehicle_account',{}).get('cars_per_train')
    if isinstance(cars,bool) or not isinstance(cars,int) or cars!=6:
        raise ValueError('six-car process-hour cost basis required')
    shift=cost.get('shifts',{}).get('production_per_day',{})
    utilisation=cost.get('assumption_values',{}).get('productive_utilisation')
    if (shift.get('shifts')!=2 or shift.get('hours_per_shift')!=8
            or isinstance(utilisation,bool) or not isinstance(utilisation,(int,float))
            or not 0<float(utilisation)<=1
            or abs(float(shift.get('productive_hours_per_day',-1))-16*float(utilisation))>1e-8):
        raise ValueError('two × eight-hour production shift basis required')
    lines=cost.get('lines')
    if not isinstance(lines,list):
        raise ValueError('selected cost ledger lines required for process hours')
    work=[];excluded=[]
    stage_order={'factory-gate':0,'factory-gate-equipment-allowance':1,'final-assembly':2}
    for line in lines:
        if not isinstance(line,dict):
            raise ValueError('invalid selected vehicle cost line')
        stage=line.get('stage')
        if stage=='reference-delivery':
            excluded.append(dict(line_id=line.get('line_id'),line_key=line.get('line_key'),
                reason='Delivery is outside the factory process-hour schedule'))
            continue
        if stage not in stage_order:
            raise ValueError('unsupported selected vehicle factory cost stage: '+str(stage))
        if line.get('candidate_id')!=record['candidate_id'] or line.get('estimate_class')!='C':
            raise ValueError('process-hour line uses a different candidate or estimate class')
        line_id=line.get('line_id')
        if not isinstance(line_id,str) or identity({k:v for k,v in line.items() if k!='line_id'})!=line_id:
            raise ValueError('selected vehicle cost line identity differs')
        quantity=line.get('quantity')
        if not isinstance(quantity,dict):
            raise ValueError('process-hour cost line has no quantity record')
        if stage=='factory-gate':
            per_car=_ordered_hours(quantity.get('process_hours_per_car'),'Per-car process hours')
            hours={case:per_car[case]*cars for case in CASES}
            basis='Per-car provisional process hours × selected six-car formation'
        elif stage=='factory-gate-equipment-allowance':
            hours=_ordered_hours(quantity.get('process_hours_per_train'),'Equipment allowance process hours')
            basis='Per-train provisional process-hour allowance for unlocated equipment'
        else:
            per_car=_ordered_hours(quantity.get('labour_hours_per_car'),'Per-car final assembly labour hours')
            hours={case:per_car[case]*cars for case in CASES}
            basis='Per-car provisional final assembly labour hours × selected six-car formation'
        work.append(dict(sequence=0,stage=stage,line_id=line_id,line_key=line.get('line_key'),
            process_template=line.get('process_template'),quantity=quantity,
            process_hours_per_train={case:round(hours[case],6) for case in CASES},
            hours_basis=basis,calculation_basis=line.get('calculation_basis'),
            source_ids=line.get('source_ids',[]),occurrence_ids=line.get('occurrence_ids',[]),
            estimate_class='C',rate_evidence_class=line.get('rate_evidence_class'),
            engineering_process_qualified=False))
    work.sort(key=lambda row:(stage_order[row['stage']],str(row['line_key']),row['line_id']))
    for number,row in enumerate(work,1):row['sequence']=number
    if not work:
        raise ValueError('selected cost ledger has no factory process-hour lines')
    totals={case:round(sum(row['process_hours_per_train'][case] for row in work),6) for case in CASES}
    factory={case:round(sum(row['process_hours_per_train'][case] for row in work
        if row['stage']!='final-assembly'),6) for case in CASES}
    assembly={case:round(sum(row['process_hours_per_train'][case] for row in work
        if row['stage']=='final-assembly'),6) for case in CASES}
    value=dict(schema='osr-v06-line-linked-process-hours/1',**{key:record[key] for key in IDS},
        evaluation_id=record['evaluation_id'],cost_estimate_id=estimate_id,
        cost_assumptions_id=cost.get('assumptions_id'),cars_per_train=cars,hours_unit='process-hour',estimate_class='C',
        production_shift_basis=dict(shift),productive_utilisation=float(utilisation),
        work_package_hours_per_train=totals,factory_process_hours_per_train=factory,
        final_assembly_labour_hours_per_train=assembly,work_packages=work,excluded_cost_lines=excluded,
        macro_operation_allocation='unallocated; cost lines do not map one-to-one to broad generic operations',
        assumptions=('Hours are model-derived Class C process/labour scenarios, not timed work instructions, crew-hours, qualified cycle times or capacity evidence.',
            'Generic manufacturing and construction operations remain unallocated unless a source-bound mapping is available.'),
        source_sha256=cost.get('source_sha256',{}),engineering_process_qualified=False)
    value['schedule_id']=identity(value)
    return value

def compile(record,root=ROOT,city_index=None):
    if city_index is not None and any(city_index.get(k)!=record[k] for k in IDS):raise ValueError('city index belongs to another physical candidate')
    stamp=dict(**{k:record[k] for k in IDS},evaluation_id=record['evaluation_id'],development_default=True,purpose='research and requests for evidence',**FLAGS)
    common=lambda schema,**value:dict(schema=schema,**stamp,**value)
    from engineering.development_baseline import factory_draft, system_cost, vehicle_cost
    selected_vehicle_cost=vehicle_cost.evaluate(record,root)
    selected_system_cost=system_cost.evaluate(record,root,selected_vehicle_cost)
    process_hour_schedule=_process_hour_schedule(selected_vehicle_cost,record)
    resource_envelope=factory_draft.resource_envelope(process_hour_schedule['work_packages'],record,
        selected_vehicle_cost['cost_estimate_id'],process_hour_schedule['productive_utilisation'])
    car=record['vehicle'];s=record['service'];z=s['selected_station'];battery=s['electrical']['battery']
    bom=common('osr-v06-engineering-bom/1',mass=car['mass'],stock_inventory_per_car=car['inventory'],
        formation=dict(cars=6,bogies=12,axles=24,wheels=48),onboard_traction_motors=0,onboard_traction_battery_kWh=0.,
        service_battery=battery,complete_installed_BOM=False,retained_component_ancestry=car['retained_component_ancestry'],residual_overlap_unresolved=car['residual_overlap_unresolved'])
    manufacturing=common('osr-v06-manufacturing/1',production_labour_hours_per_car=None,
        line_linked_process_hour_schedule=process_hour_schedule,tooling_cost_USD=None,
        provisional_resource_envelope=resource_envelope,
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
        vehicle_process_hour_schedule=process_hour_schedule,
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
    return dict(bom=bom,manufacturing=manufacturing,procurement=procurement,assembly=assembly,civil=civil,controls=controls,
        selected_vehicle_cost=selected_vehicle_cost,selected_system_cost=selected_system_cost)

def write(output,record,root=ROOT,city_index=None,native=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);values=compile(record,root,city_index)
    for key,value in values.items():
        name='engineering-bom' if key=='bom' else 'selected-vehicle-cost' if key=='selected_vehicle_cost' else 'selected-system-cost' if key=='selected_system_cost' else key
        raw=encoded(value);(output/(name+'.json.gz' if key in ('bom','procurement') else name+'.json')).write_bytes(gzip.compress(raw,mtime=0) if key in ('bom','procurement') else raw)
    cad=dict(schema='osr-v06-cad-reference/1',**{k:record[k] for k in IDS},development_default=True,
        execution='not-run' if native is None else native.get('execution','completed'),
        native=native,complete_installed_geometry=False,**FLAGS)
    (output/'cad.json').write_bytes(encoded(cad))
    from . import bim
    (output/'bim.json').write_bytes(encoded(bim.write(output,record)))
    from engineering.development_baseline import system_cost, vehicle_cost
    m=dict(schema='osr-v06-delivery-manifest/1',**{k:record[k] for k in IDS},evaluation_id=record['evaluation_id'],
        development_default=True,source_sha256=source_map(root,('engineering/station_rail/exports.py','engineering/station_rail/bim.py',
            'engineering/development_baseline/factory_draft.py',*vehicle_cost.sources(root).keys(),
            *system_cost.sources(root).keys())),
        files_sha256={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file() and p.name!='manifest.json'},**FLAGS)
    m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m));return m

def verify(output,record,root=ROOT,city_index=None):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if any(m.get(k)!=record[k] for k in (*IDS,'evaluation_id')):raise ValueError('delivery candidate differs')
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('delivery manifest identity differs')
    from engineering.development_baseline import system_cost, vehicle_cost
    if m['source_sha256']!=source_map(root,('engineering/station_rail/exports.py','engineering/station_rail/bim.py',
        'engineering/development_baseline/factory_draft.py',*vehicle_cost.sources(root).keys(),*system_cost.sources(root).keys())):raise ValueError('delivery source differs')
    if {p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('delivery payload differs')
    for key,value in compile(record,root,city_index).items():
        name='engineering-bom' if key=='bom' else 'selected-vehicle-cost' if key=='selected_vehicle_cost' else 'selected-system-cost' if key=='selected_system_cost' else key;compressed=key in ('bom','procurement')
        raw=(output/(name+'.json.gz' if compressed else name+'.json')).read_bytes()
        if (gzip.decompress(raw) if compressed else raw)!=encoded(value):raise ValueError('delivery calculation differs')
    from . import bim
    receipt=json.loads((output/'bim.json').read_bytes())
    if receipt['execution']=='completed':bim.verify(output/'selected-interface.ifc',record,receipt)
    return dict(current=True,manifest_id=m['manifest_id'],complete_installed_BOM=False,**FLAGS)
