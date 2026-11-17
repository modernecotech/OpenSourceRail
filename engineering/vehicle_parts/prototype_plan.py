"""Selected-car prototype planning view from the existing research parts child."""
from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
from engineering.station_rail.common import encoded
from . import ROOT, publication

INPUTS = (
    'docs/design-engine/current/manifest.json',
    'docs/design-engine/current/evaluation.json.gz',
    'docs/design-engine/current/exports/assembly.json',
    'docs/design-engine/current/exports/manifest.json',
    'docs/design-engine/mass-reconciliation/current/summary.json',
    'docs/design-engine/mass-reconciliation/current/manifest.json',
    'docs/design-engine/v07-execution/door-interface-handoff.json',
    'docs/design-engine/v07-execution/door-pack-preflight.json',
    'docs/design-engine/vehicle-parts/manifest.json',
    'docs/design-engine/vehicle-parts/manufacturing-bundle.json.gz',
)
SCOPES = ('body/underframe','body/sideframe','body/roof','body/floor',
          'running/bogie-frame','running/wheelset','running/axlebox')
FLAGS = dict(complete_installed_BOM=False, installed_mass_complete=False,
             engineering_accepted=False, manufacturing_release=False,
             operating_release=False, physical_accepted=False,
             selected_reference_changed=False)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(root, name):
    path = root/name
    with (gzip.open(path,'rt') if name.endswith('.gz') else path.open()) as stream:
        return json.load(stream)


def compose(selected, mass, assembly, door, child):
    cid, eid, sid = (selected[k] for k in ('candidate_id','evaluation_id','selection_id'))
    if any(x['candidate_id'] != cid for x in (mass,assembly)):
        raise ValueError('Mixed selected physical candidate')
    if mass['selected_evaluation_id'] != eid or assembly['evaluation_id'] != eid:
        raise ValueError('Mixed selected evaluation')
    if mass['selection_id'] != sid or assembly['selection_id'] != sid:
        raise ValueError('Mixed selected selection')
    if child['parent_candidate_id'] != cid or child['parent_selection_id'] != sid:
        raise ValueError('Research child lacks selected ancestry')
    if child['candidate_id'] == cid or door['physical_candidate_id'] != child['candidate_id']:
        raise ValueError('Research child and selected candidate identities mixed')
    if door['installed_candidate_id'] == cid or door['installed_geometry_verified']:
        raise ValueError('Unverified door cannot enter selected geometry')
    if selected['installed_mass_complete'] or selected['physical_accepted']:
        raise ValueError('Expected development-only selected reference')
    tare = mass['accounted_tare_kg_per_car']
    located = mass['located_geometry_mass_kg']
    residual = mass['residual_reference_or_unlocated_mass_kg']
    if abs(tare-located-residual)>1e-6 or residual<=0:
        raise ValueError('Residual mass account does not reconcile')
    if mass['complete_installed_mass_kg'] is not None or mass['complete_installed_CG_m'] is not None:
        raise ValueError('Installed mass or CG changed; this view needs revision')

    vehicle=selected['vehicle'];seats=vehicle['seating_layout']
    if seats['door_centres_x_m'] != [-4.5,4.5] or seats['boarding_side'] != '+y':
        raise ValueError('Door positions or boarding side changed')
    axles=sorted({round(p['at_m'][0],6) for p in vehicle['geometry_parts']
                  if p['id'] in ('bogie/0/axle/0','bogie/0/axle/1','bogie/1/axle/0','bogie/1/axle/1')})
    if len(axles)!=4 or vehicle['support_counts']['bogies_per_car']!=2:
        raise ValueError('Running-gear geometry changed')
    centres=[(axles[0]+axles[1])/2,(axles[2]+axles[3])/2]
    ref=child['physical_definition']['reference_interfaces']
    if (ref['body_length_m']!=17.0 or ref['bogie_centres_x_m']!=centres
            or ref['fixed_seats_per_car']!=seats['seats_total']
            or ref['wheelchair_places_per_car']!=seats['wheelchair_places']
            or ref['passenger_door_openings_per_car']!=seats['doors_total']
            or seats['standing_passengers']!=0):
        raise ValueError('Research child reference interfaces differ from selected car')
    opening=door['opening_frame']
    guide=[p for p in door['parts'] if p['part_id']=='body/door-guide-rail']
    if len(guide)!=1 or opening['clear_width_m']!=seats['door_width_m']:
        raise ValueError('Door aperture or guide changed')
    guide_m=guide[0]['stock']['length_m'];travel_m=opening['proposed_slide_m']
    end_stock_m=(guide_m-opening['clear_width_m']-2*travel_m)/2
    if end_stock_m<0 or opening['accepted_installation_datum'] is not None:
        raise ValueError('Door guide or installation datum cannot be adopted')

    summaries={a['id']:a for a in child['assembly_summaries']}
    details={a['id']:a for a in child['assemblies']}
    scopes=[]
    for ident in SCOPES:
        s,a=summaries[ident],details[ident]
        q,pieces=s['quantity_per_train'],s['counted_leaf_pieces']
        leaf=[p for p in child['parts'] if p['assembly_id']==ident]
        if q%6 or pieces%6 or a['quantity_per_train']!=q or len(leaf)!=s['unique_leaf_types']:
            raise ValueError('Child assembly quantity or leaf coverage changed')
        if any(p['quantity_per_train']%6 for p in leaf):
            raise ValueError('Child leaf cannot be allocated to one representative car')
        mass_sum=sum(p['quantity_per_train']*p['mass_each_kg']['base'] for p in leaf)
        cost_sum=sum(p['quantity_per_train']*p['direct_cost_each_usd']['base'] for p in leaf)
        if (abs(mass_sum-s['nominal_mass_kg']['known_leaf_subtotal']['base'])>1e-6
                or abs(cost_sum-s['direct_parts_process_usd']['known_leaf_subtotal']['base'])>1e-6):
            raise ValueError('Child leaf quantities do not reconcile with assembly subtotal')
        leaf_rows=[dict(part_id=p['id'],quantity_per_car=p['quantity_per_train']//6,
            material_id=p['material_id'],make_buy=p['make_buy'],stock=p['stock'],
            provisional_mass_each_kg=p['mass_each_kg']['base'],
            provisional_direct_cost_each_usd=p['direct_cost_each_usd']['base'],
            mass_basis=p['mass_basis']['kind'],joining=p['joining'],
            tolerance_and_fits=p['tolerance_and_fits'],inspection=p['inspection'],
            open_tasks=p['open_tasks']) for p in leaf]
        scopes.append(dict(assembly_id=ident, instances_per_car=q//6,
            counted_leaf_pieces_per_car=pieces//6, leaf_quote_rows=leaf_rows,
            make_buy_by_leaf_type={k:sum(p['make_buy']==k for p in leaf)
                                   for k in sorted({p['make_buy'] for p in leaf})},
            child_gross_stock_and_bought_mass_kg_per_car=s['nominal_mass_kg']['known_leaf_subtotal']['base']/6,
            child_direct_part_process_allowance_usd_per_car=s['direct_parts_process_usd']['known_leaf_subtotal']['base']/6,
            process_steps=a['assembly_steps'], removal_method=a['maintenance_removal'],
            selection_status='research child; mass and price not additive to selected car'))
    doors=[]
    for x in seats['door_centres_x_m']:
        half=opening['clear_width_m']/2
        doors.append(dict(centre_x_m=x,boarding_side='+y',aperture_x_m=[x-half,x+half],
            nominal_leaf_x_sweep_m=[x-half-travel_m,x+half+travel_m],guide_length_m=guide_m,
            ideal_guide_end_stock_m=end_stock_m,proposed_tool_radius_m=opening['proposed_tool_radius_m'],
            swept_y_z_clearance_verified=False))
    return dict(schema='osr-v07-representative-car-prototype-plan/1',
        candidate_id=cid,evaluation_id=eid,selection_id=sid,
        body_candidate_id=selected['body_candidate_id'],
        research_child_candidate_id=child['candidate_id'],research_child_bundle_id=child['bundle_id'],
        research_door_installed_candidate_id=door['installed_candidate_id'],
        coordinate_frame='car local: x forward, y left, z up; rail running surface z=0',
        formation=dict(cars=ref['cars'],car_body_length_m=ref['body_length_m'],
                       fixed_seats_per_car=seats['seats_total'],
                       wheelchair_places_per_car=seats['wheelchair_places'],
                       planned_standing=seats['standing_passengers'],
                       bogies_per_car=2,axles_per_car=4,doors_per_car=2,boarding_side='+y'),
        mass_account=dict(accounted_tare_kg_per_car=tare,located_geometry_kg_per_car=located,
            residual_reference_or_unlocated_kg_per_car=residual,
            complete_installed_tare_kg_per_car=None,complete_installed_CG_m=None,
            complete_installed_inertia_kg_m2=None,axle_reactions_N=None,
            research_child_scopes_additive_to_selected_mass=False),
        structural_and_running_gear_quote_scopes=scopes,
        nominal_geometry=dict(axle_x_m=axles,bogie_centre_x_m=centres,door_openings=doors),
        interface_register=[
            dict(id='carbody-bogie',known_nominal=dict(bogie_centres_x_m=centres,
                axle_x_m=axles),required_loads='gross, crowd, braking, curve, fatigue, rescue',
                controlled_datum=None,approved_tolerance=None,finite_motion_verified=False),
            dict(id='door-platform',known_nominal=dict(side='+y',door_centres_x_m=seats['door_centres_x_m'],
                clear_width_m=seats['door_width_m'],clear_height_m=seats['door_height_m']),
                required_loads='leaf retention, obstruction, emergency release, platform gap',
                controlled_datum=None,approved_tolerance=None,finite_motion_verified=False),
            dict(id='door-header-guide',known_nominal=dict(guide_length_m=guide_m,
                leaf_travel_m=travel_m,ideal_end_stock_m=end_stock_m),
                required_loads='belt force, end stop, vibration, manual release',
                controlled_datum=None,approved_tolerance=None,finite_motion_verified=False),
            dict(id='roof-hvac-and-service',known_nominal=None,
                required_loads='equipment gravity, vibration, condensate, thermal and electrical duty',
                controlled_datum=None,approved_tolerance=None,finite_motion_verified=False),
            dict(id='body-secondary-and-brake',known_nominal=None,
                required_loads='station propulsion force, hot clearance, independent stop, tow and brake reaction',
                controlled_datum=None,approved_tolerance=None,finite_motion_verified=False)
        ],
        release_holds=[
            'Measure bogie/body mating datums, force transfer, fasteners, suspension sweep and lifting access.',
            'Measure both door apertures and control guide, pulley, belt, stop, retention, release, interlock and wiring interfaces.',
            'Verify full 3D door motion and 150 mm proposed tool sweep; 30 mm ideal guide-end stock is not a tolerance budget.',
            'Locate and weigh 10,090.2 kg/car residual account, resolve service-pack overlap and measure whole-car mass, CG and inertia.',
            'Fit HVAC, battery, brake, wiring, cooling, coupling and repair access on one physical candidate.',
            'Approve material/process specifications, joint allowables, QA limits and supplier drawings before prototype fabrication.'
        ],selected_assembly_operations=assembly['vehicle_assembly_sequence'],**FLAGS)


def build(root=ROOT):
    root=Path(root)
    v=publication.verify(root,root/'docs/design-engine/vehicle-parts')
    if not v['verified'] or v['physical_accepted']:
        raise ValueError('Research child publication is not verified unreleased evidence')
    manifest=read(root,INPUTS[0])
    if digest(root/INPUTS[1])!=manifest['files_sha256']['evaluation.json.gz']:
        raise ValueError('Selected evaluation differs from current manifest')
    if digest(root/'docs/design-engine/current/exports/assembly.json')!=manifest['files_sha256']['exports/assembly.json']:
        raise ValueError('Selected assembly differs from current manifest')
    mass_manifest=read(root,'docs/design-engine/mass-reconciliation/current/manifest.json')
    if digest(root/'docs/design-engine/mass-reconciliation/current/summary.json')!=mass_manifest['files_sha256']['summary.json']:
        raise ValueError('Selected mass summary differs from its manifest')
    preflight=read(root,'docs/design-engine/v07-execution/door-pack-preflight.json')
    if digest(root/'docs/design-engine/v07-execution/door-interface-handoff.json')!=preflight['source_handoff_sha256']:
        raise ValueError('Door handoff differs from its preflight receipt')
    selected=read(root,INPUTS[1])
    if any(selected[k]!=manifest[k] for k in ('candidate_id','evaluation_id','selection_id')):
        raise ValueError('Current selected identities differ')
    result=compose(selected,read(root,'docs/design-engine/mass-reconciliation/current/summary.json'),
                   read(root,'docs/design-engine/current/exports/assembly.json'),
                   read(root,'docs/design-engine/v07-execution/door-interface-handoff.json'),
                   read(root,'docs/design-engine/vehicle-parts/manufacturing-bundle.json.gz'))
    result['source_sha256']={name:digest(root/name) for name in INPUTS}
    result['source_sha256']['engineering/vehicle_parts/prototype_plan.py']=digest(Path(__file__))
    result['plan_id']=sha256(encoded(result)).hexdigest()
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('build','verify'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    payload=encoded(build())
    if args.action=='build':
        if args.output.exists():raise ValueError('Fresh output path required')
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(payload)
    elif args.output.read_bytes()!=payload:
        raise ValueError('Prototype plan differs from current sources')
    print(json.dumps(dict(verified=True,plan_id=json.loads(payload)['plan_id'],physical_accepted=False),sort_keys=True))
    return 0


if __name__=='__main__':raise SystemExit(main())
