"""Parametric stock changes and explicit drive mass ownership, in SI.

The outer drive boxes are necessary-space hypotheses. They never become a
supplier shape, a negative clash result, or qualified manufacturing geometry.
"""
from copy import deepcopy
from itertools import product
from math import fsum, prod, pi, sqrt, sin, cos
from pathlib import Path
import json

from engineering.station_rail.common import identity, digest
from engineering.vehicle_installation import model, underframe
from . import ROOT, FLAGS

POLICY = 'engineering/powered_bogie/policy.json'
PARENT = 'c89556f453e39448a8f3e9bf2d0d4d008f97cd20d252ac417284e40965e261b3'
REPLACED = ('running/frame-side-rhs', 'running/frame-transom-rhs',
            'running/frame-end-tie', 'running/frame-weld-metal')


def policy(root=ROOT):
    p = json.loads((Path(root) / POLICY).read_bytes())
    if p['schema'] != 'osr-powered-bogie-policy/1' or p['parent_candidate_id'] != PARENT:
        raise ValueError('Explicit powered-bogie parent and policy required')
    if p['coordinate_frame']['inner_face_gauge_m'] != 1.435:
        raise ValueError('Fixed inner-face gauge changed')
    return p


def sources(root=ROOT):
    root = Path(root)
    names = set(model.sources(root)) | {POLICY, policy(root)['source_catalogue'],
        'engineering/railway_closure/data/frozen-installed-parent.json.gz',
        'engineering/station_pair/profiles.py'}
    names |= {p.relative_to(root).as_posix() for p in (root/'engineering/powered_bogie').glob('*.py')}
    return {n: digest(root/n) for n in sorted(names)}


def validate_parent(body):
    if (body.get('candidate_id') != PARENT
            or identity(body['physical_definition']) != PARENT
            or body['evaluation_id'] != identity({k:v for k,v in body.items() if k != 'evaluation_id'})):
        raise ValueError('Exact sealed counted-body parent required')
    return body


def parent(root=ROOT):
    return underframe.build(underframe.load_parent(Path(root)/
        'engineering/railway_closure/data/frozen-installed-parent.json.gz'),
        family_id='steel-650x650x10')


def _volume(stock):
    if stock['kind'] == 'box':
        return prod(stock['size_m'])
    if stock['kind'] == 'rhs':
        L,b,h,t = (stock[k] for k in ('length_m','width_m','depth_m','wall_m'))
        if not 0 < 2*t < min(b,h):
            raise ValueError('Positive RHS walls and open void required')
        return L*(b*h-(b-2*t)*(h-2*t))
    raise ValueError('Only explicit box or RHS volume is admitted')


def definitions(body, p):
    """One-bogie definitions, expanded into exactly twelve private anchors."""
    template = body['parts'][0]
    parts, placements = [], {}
    def add(name, positions, stock, *, mass=None, material='running/steel-s355',
            rotation=model.I, partition=False, labour_h=0., holes=0, process=None):
        r = deepcopy(template); quantity = len(positions)
        if mass is None:
            value = _volume(stock)*7850.
            masses = {c:value for c in model.CASES}
        else:
            masses = dict(zip(model.CASES, mass if isinstance(mass,list) else [mass]*3))
        r.update(id='powered-bogie/'+name, name=name, source_part_id=None,
            assembly_id='research/powered-bogie', quantity_per_assembly=quantity,
            quantity_per_train=quantity*12, stock=stock, material_id=material,
            mass_each_kg=masses, make_buy='make' if mass is None else 'bounded-purchased-or-processed',
            BOP_partition=partition)
        r['component_definition_id'] = identity({k:r[k] for k in
            ('id','stock','quantity_per_train','material_id','mass_each_kg')})
        # Retain positive purchase/process estimates. These are calculated
        # allowance rates, never fabricated supplier quotations.
        rates = body['policy']['rates']
        costs = model._price(masses, material, body['policy'])
        r['direct_cost_each_usd'] = {c:costs[c]+labour_h*rates['labour_usd_h'][i]*
            (1+rates['overhead_fraction'][i]) for i,c in enumerate(model.CASES)}
        r['mass_basis'] = dict(kind='calculated-gross-stock' if mass is None else
            'explicit-bounded-component-mass', description='Blank mass; holes and profiling not deducted' if mass is None else
            'Separate positive allowance; actual finished component mass and material remain unverified')
        r['cost_basis'] = 'Existing declared low/base/high material, yield, process-hour/kg, machine/QA and overhead rates plus explicit drilling/join labour; excludes drive procurement, final integration, testing, tax and release'
        r['process_quantities'] = dict(extra_labour_h_each=labour_h, drilled_holes_each=holes,
            gross_volume_m3_each=_volume(stock) if stock['kind'] in ('box','rhs') else None,
            allowances_are_not_quotations=True)
        r['manufacturing'] = process or ['Cut stock and retain heat identity',
            'Fixture on wheelset/secondary-interface datums; drill or ream stated mating holes',
            'Join with qualified distortion-controlled process; inspect accessible seams before closing',
            'Survey, protect from corrosion and record measured finished mass']
        r['joining'] = 'Counted proposed weld/retained fixing interfaces; no weld, bolt or bearing strength accepted'
        r['maintenance_removal'] = 'Support body and bogie on rated fixtures, isolate power, open guards, support drive on drop table, release retained mounts; swept paths and supplier lifting eyes remain held'
        parts.append(r); placements[r['id']] = (deepcopy(positions), deepcopy(rotation))
    f=p['frame']
    add('side-rhs', [[0.,s*f['side_y_m'],f['side_z_m']] for s in (-1,1)],
        dict(kind='rhs',length_m=f['side_length_m'],width_m=f['side_width_m'],
             depth_m=f['side_depth_m'],wall_m=f['side_wall_m']),labour_h=1.5)
    add('transom-rhs', [[x,0.,.41] for x in f['crossmember_x_m']],
        dict(kind='rhs',length_m=f['crossmember_length_m'],width_m=f['crossmember_width_m'],
             depth_m=f['crossmember_depth_m'],wall_m=f['crossmember_wall_m']),
        rotation=model.RZ90,labour_h=1.)
    add('end-tie', [[x,0.,.41] for x in f['end_tie_x_m']],
        dict(kind='box',size_m=[1.65,.16,.016]), rotation=model.RZ90,labour_h=.5)
    # Lower removable cradle plates and outboard arms make the proposed load
    # path visible. Intersections with the unknown gear remain failures.
    add('motor-cradle-plate', [[-.48,y,.095] for y in (-.40,.20)],
        dict(kind='box',size_m=[.58,.12,.025]),partition=True,labour_h=.8,holes=4)
    add('motor-vertical-cheek', [[-.48,y,.25] for y in (-.63,.63)],
        dict(kind='box',size_m=[.50,.020,.30]),partition=True,labour_h=.6,holes=2)
    add('motor-outrigger-rhs', [[-.48,s*.82,.25] for s in (-1,1)],
        dict(kind='rhs',length_m=.43,width_m=.18,depth_m=.12,wall_m=.010),
        rotation=model.RZ90,partition=True,labour_h=.8)
    add('torque-arm-plate', [[-.99,.73,.40],[-.51,.73,.40]],
        dict(kind='box',size_m=[.24,.016,.12]),partition=True,labour_h=.7,holes=2)
    add('torque-arm-bush', [[-.99,.73,.40],[-.51,.73,.40]],
        dict(kind='envelope',size_m=[.07,.07,.07]),mass=[.9,1.2,1.8],partition=True)
    add('retention-strap', [[-.48,y,.115] for y in (-.54,.34)],
        dict(kind='box',size_m=[.65,.040,.008]),partition=True,labour_h=.6,holes=2)
    add('retention-stop', [[-.78,-.12,.13],[-.18,-.12,.13]],
        dict(kind='envelope',size_m=[.06,.08,.04]),mass=[.15,.3,.5],partition=True)
    bolt_positions=[[-.48+dx,y,.11] for dx in (-.19,.19) for y in (-.44,-.36,.16,.24)]
    torque_positions=[[x,.73,z] for x in (-.99,-.51) for z in (.365,.435)]
    all_bolts=bolt_positions+torque_positions
    add('M20-retained-bolt',all_bolts,dict(kind='envelope',size_m=[.034,.034,.10]),
        mass=[.30,.35,.42],partition=True,labour_h=.10)
    add('M20-locknut',[[x,y,z+.065] for x,y,z in all_bolts],
        dict(kind='envelope',size_m=[.034,.034,.020]),mass=[.06,.075,.09],partition=True)
    add('M20-washer',[[x,y,z+dz] for x,y,z in all_bolts for dz in (-.052,.052)],
        dict(kind='envelope',size_m=[.040,.040,.003]),mass=[.02,.025,.03],partition=True)
    add('retention-M12-fixing',[[x,y,.14] for x in (-.76,-.20) for y in (-.54,.34)],
        dict(kind='envelope',size_m=[.022,.022,.065]),mass=[.06,.08,.11],partition=True,
        process=['Finished bolt, locking nut and two washers per item; four retained fixing sets per bogie, no loose uncounted hardware'])
    # Weld metal is counted by seam length and triangular throat geometry.
    seam_length=4*2*(.18+.22)+4*(.18+.26)+4*.30+4*.50
    weld_mass=seam_length*.008**2/2*7850.
    add('frame-weld-deposit',[[0.,0.,.41]],
        dict(kind='envelope',size_m=[3.24,2.10,.26]),mass=weld_mass,labour_h=seam_length*.12,
        process=[f'{seam_length:.3f}m declared 8mm equal-leg fillet equivalent; explicit research seam map, no strength or HAZ acceptance',
                 'Real groove preparation, penetrations, weld access, distortion and NDT plan remain open'])
    mount_seam=4*.30+4*.50
    add('mount-weld-deposit',[[-.48,0.,.25]],dict(kind='envelope',size_m=[.70,1.8,.40]),
        mass=mount_seam*.006**2/2*7850.,partition=True,labour_h=mount_seam*.15)
    s=p['services']
    cable_mass=s['power_cable_length_m']*s['power_cable_copper_area_m2']*8960.+.38
    add('flexible-power-cable',[[-.3,-.32+.04*i,.55] for i in range(3)],
        dict(kind='envelope',size_m=[.9,.02,.30]),mass=[cable_mass*.9,cable_mass,cable_mass*1.25],
        material='services/copper',partition=True,labour_h=.25)
    add('power-connector',[[-.48,-.58,.48] for _ in range(3)],
        dict(kind='envelope',size_m=[.09,.045,.05]),mass=[.16,.25,.4],partition=True)
    add('bonding-braid',[[-.48,y,.4] for y in (-.65,.65)],
        dict(kind='envelope',size_m=[.7,.025,.08]),mass=s['bonding_length_m']*
            s['bonding_copper_area_m2']*8960.,material='services/copper',partition=True)
    add('flexible-air-duct',[[-.25,-.48,.58]],
        dict(kind='envelope',size_m=[.9,.12,.28]),mass=[.7,1.2,2.],partition=True,labour_h=.5)
    add('service-clamp',[[-.4+i*.1,-.62,.49] for i in range(8)],
        dict(kind='envelope',size_m=[.035,.03,.025]),mass=[.03,.05,.08],partition=True)
    add('clamp-M6-fixing-set',[[-.4+i*.1,-.62,.51] for i in range(8)],
        dict(kind='envelope',size_m=[.012,.012,.025]),mass=[.007,.012,.02],partition=True)
    return parts,placements


def _anchors(body):
    l=body['policy']['layout']
    return [dict(id=f'research/powered-bogie/{car}/{j}',
                 at_m=[8.5+car*17.65+dx,0.,0.],
                 car_allocation=[[car,1.]],bogie_index=2*car+j)
            for car in range(6) for j,dx in enumerate(l['bogie_centres_local_x_m'])]


def external_drive_placements(body, p):
    out=[]
    for anchor in _anchors(body):
        for name in ('motor','gear_including_couplings'):
            e=p['drive_envelopes'][name];centre=[anchor['at_m'][i]+e['centre_m'][i] for i in range(3)]
            out.append(dict(id=name+'@'+anchor['id'],hardware=name,
                driven_axle_index=anchor['bogie_index']*2,bogie_index=anchor['bogie_index'],
                car_allocation=anchor['car_allocation'],mass_kg={c:e['mass_kg'] for c in model.CASES},
                centroid_m=centre,positions_m=[centre],rotation=model.I,size_m=e['size_m'],
                position_uncertainty_m=e['position_uncertainty_m'],frame=e['frame'],
                mass_owner=e['mass_owner'],body_BOM_contains_mass=False,
                gear_support='Driven axle bearing bore plus proposed frame torque reaction' if name!='motor' else
                    'Proposed retained lower cradle, foot interface unknown',supplier_fit_verified=False))
    if fsum(r['mass_kg']['base'] for r in out)!=12*796.:
        raise ValueError('Known drive catalogue mass was lost or counted twice')
    return out


def build(body, *, variant_id='extended-cradle-3240', root=ROOT):
    validate_parent(body);p=policy(root);before=sources(root)
    if variant_id not in p['variant_ids']:
        raise ValueError('Variant outside declared two-proposal budget')
    rows,placements=definitions(body,p) if variant_id!='retained-frame-control' else ([],{})
    removed=set(REPLACED) if rows else set()
    parts=[deepcopy(r) for r in body['parts'] if r['id'] not in removed]+rows
    patterns=[deepcopy(r) for r in body['patterns'] if r['part_id'] not in removed]
    anchors=_anchors(body)
    for r in rows:
        positions,R=placements[r['id']]
        for a in anchors:
            world=[[a['at_m'][i]+v[i] for i in range(3)] for v in positions]
            patterns.append(model._moments_for_pattern(r,a,world,R,model.geometry(r),body['policy']))
    for part in parts:
        if sum(r['count'] for r in patterns if r['part_id']==part['id'])!=part['quantity_per_train']:
            raise ValueError('Revised occurrence coverage differs: '+part['id'])
    drives=external_drive_placements(body,p)
    partition={c:fsum(r['quantity_per_train']*r['mass_each_kg'][c] for r in rows if r['BOP_partition']) for c in model.CASES}
    reserve=underframe.ADDITIONS['drive_BOP_train_kg']
    if any(partition[c]>=reserve[c] for c in model.CASES):
        raise ValueError('Explicit BOP parts exhaust unknown drive reserve')
    physical=dict(schema='osr-powered-bogie-body-physical/1',parent_candidate_id=body['candidate_id'],
        variant_id=variant_id,coordinate_frame=deepcopy(p['coordinate_frame']),
        track_interface=deepcopy(body['physical_definition']['track_interface']),
        layout=deepcopy(body['policy']['layout']),proposal=p,
        removed_parts=sorted(removed),
        proposed_components=[{k:r[k] for k in ('id','component_definition_id','quantity_per_train','material_id','stock','mass_each_kg','BOP_partition')} for r in rows],
        occurrence_patterns=[{k:r[k] for k in ('id','part_id','count','positions_m','rotation','geometry','car_allocation','bogie_index')} for r in patterns],
        external_drive_geometry=drives, external_drive_mass_in_body_BOM=False)
    result=deepcopy(body)
    result.update(candidate_id=identity(physical),physical_definition=physical,
        parent_candidate_id=body['candidate_id'],parent_evaluation_id=body['evaluation_id'],
        parts=parts,patterns=patterns,proposed_component_types=len(parts),
        total_occurrences=sum(r['count'] for r in patterns),source_sha256=before,
        mass_scenarios=[underframe._scenario(patterns,body['policy'],kind,c)
            for kind in ('tare','normal','crowd-control') for c in model.CASES],
        nominal_part_mass_kg={c:fsum(r['quantity_per_train']*r['mass_each_kg'][c] for r in parts) for c in model.CASES},
        direct_parts_process_usd={c:fsum(r['quantity_per_train']*r['direct_cost_each_usd'][c] for r in parts) for c in model.CASES},
        exact_stock_types=sum(model.geometry(r)['exact_stock'] for r in parts),
        unknown_finished_geometry_types=sum(not model.geometry(r)['exact_stock'] for r in parts),
        external_drive_placements=drives,
        BOP_partition=dict(explicit_parts_already_in_body_kg=partition,
            previous_external_reserve_kg=deepcopy(reserve),
            remaining_unknown_external_reserve_kg={c:reserve[c]-partition[c] for c in model.CASES},
            instruction='Replace the external796kg-per-driven-axle point by exactly one486kg motor and one310kg gear/coupling item per bogie at these centres. Subtract only the explicit BOP partition already included in this body from the previous BOP reserve, and retain the strictly positive remainder. No external drive mass belongs to this body BOM.'),
        change_set=dict(removed_part_ids=sorted(removed),added_part_ids=[r['id'] for r in rows],
            mass_delta_kg={c:fsum(r['quantity_per_train']*r['mass_each_kg'][c] for r in rows)-
                fsum(r['quantity_per_train']*r['mass_each_kg'][c] for r in body['parts'] if r['id'] in removed) for c in model.CASES},
            cost_delta_usd={c:fsum(r['quantity_per_train']*r['direct_cost_each_usd'][c] for r in rows)-
                fsum(r['quantity_per_train']*r['direct_cost_each_usd'][c] for r in body['parts'] if r['id'] in removed) for c in model.CASES}),
        **FLAGS)
    result['assembly_occurrences']['research/powered-bogie']=anchors
    result['revisions']=deepcopy(body.get('revisions',[]))+[dict(old_part_id=r,
        reason='Powered-bogie child replaces frame stock around declared drive envelope; static support interfaces unchanged') for r in sorted(removed)]
    result['removed_parts']=deepcopy(body.get('removed_parts',[]))+[
        dict(part_id=r['id'],source_part_id=r['source_part_id'],
             reason='Original running-frame stock explicitly removed in this research child; replacement stock counted under powered-bogie IDs')
        for r in body['parts'] if r['id'] in removed]
    origins={r['source_part_id'] for r in parts if r['source_part_id']}
    removed_origins={r['source_part_id'] for r in result['removed_parts'] if r.get('source_part_id')}
    expected={r['source_part_id'] for r in body['parts'] if r['source_part_id']}|{
        r['source_part_id'] for r in body.get('removed_parts',[]) if r.get('source_part_id')}
    if origins&removed_origins or origins|removed_origins!=expected:
        raise ValueError('Source origins must be retained or explicitly removed exactly once')
    result['source_origins_explicitly_removed']=len(removed_origins)
    result['assembly_plans']['powered_bogie_revision']=dict(
        operations=['Keep existing wheelbase, spring seats, axlebox and secondary-support datums in a survey jig',
            'Cut longer side RHS, fit crossmembers and end plates; inspect accessible seams and preserve open RHS access',
            'Fabricate removable cradle, torque-reaction plates, bushes and retained stop/strap fixings',
            'Trial-fit supplier drive only after receiving housing/shaft/foot drawings and resolving current brake/body conflicts',
            'Install flexible power/bond/ventilation routes with counted clamps, bend radii, insulation and retention checks',
            'Measure complete bogie mass, CG, interface coordinates and removal/tool paths before any prototype admission'],
        controls=['Stock/heat traceability, weld coupons and NDT',
            'Datum survey, dimensional fit and interference record',
            'Recorded torque, locking, bore/bearing/shaft retention',
            'Bond/insulation, rotation, brake and service-flexibility checks'],
        blockers=['Unknown supplier interfaces','Body/brake/mount envelope conflicts',
            'Unverified frame/mount fatigue and suspension dynamics'],
        tool_access_verified=False,manufacturing_release=False)
    result['mass_uncertainty']=dict(status='Superseded parent CG/inertia intervals; positive source mass intervals and position uncertainty retained in every pattern; no new verified installed bounds',
        conservative_rebound_required=True)
    result['structural_comparison']=dict(status='Parent body analysis retained only as ancestry; altered running-frame load path has not been stress/fatigue evaluated',
        parent_evaluation_id=body['evaluation_id'],strength_verified=False)
    result['interface_screens']['powered_bogie']=dict(status='Unresolved; inspect dedicated bogie evaluation',supplier_fit_verified=False)
    result['evaluation_id']=identity({k:v for k,v in result.items() if k!='evaluation_id'})
    if before!=sources(root):raise ValueError('Source drift during powered bogie revision')
    return result
