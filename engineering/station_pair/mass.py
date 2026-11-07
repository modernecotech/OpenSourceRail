"""Count-preserving mass/layout sensitivity for one immutable parts proposal.

Only standard-library arithmetic. No CAD, FEM, full fastener expansion, parent
allowance inheritance, invented trim, or inferred wheel inertia.
"""
from copy import deepcopy
from hashlib import sha256
from math import fsum,isfinite
from pathlib import Path
import gzip,json

ROOT=Path(__file__).resolve().parents[2]
PRODUCER='engineering/station_pair/mass.py'
POLICY='engineering/station_pair/mass-policy.json'
INPUT='docs/design-engine/vehicle-parts/manufacturing-bundle.json.gz'
CANDIDATE_ID='907da3680bcbd01ffe1223652443e4e34a9f581e201385917a99edf4150bd90a'
BUNDLE_ID='bc43edc029e8d4acf44df281dcdb640c71dccdb8a0f244f9de82644672aef6f1'
SOURCE_EVALUATION_ID='1edaf7cc668deb7e488e32e84b76dd53dc3e04e39f7735dfc6ba963f4c9e0d0e'
INPUT_SHA256='678959424e25119d699c96a087ed8343efcaf775337be6aca61ca2de666ba448'
CASES=('low','base','high')
FLAGS=dict(installed_mass_complete=False,physical_accepted=False,engineering_accepted=False,
           manufacturing_release=False,operating_release=False,selected_reference_changed=False)

def _encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def _identity(v):return sha256(_encoded(v)).hexdigest()
def _digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def _number(v):
    if type(v) not in (int,float) or not isfinite(v):raise ValueError('Finite numeric value required; booleans are not quantities')
    return float(v)
def _interval(v):
    if not isinstance(v,dict) or set(v)!=set(CASES):raise ValueError('Explicit low/base/high reserve required')
    a=[_number(v[k]) for k in CASES]
    if min(a)<0 or a!=sorted(a):raise ValueError('Ordered nonnegative mass scenarios required')
    return dict(zip(CASES,a))
def _box(v):
    if not isinstance(v,list) or len(v)!=3:raise ValueError('Three centroid intervals required')
    out=[]
    for axis in v:
        if not isinstance(axis,list) or len(axis)!=2:raise ValueError('Two ordered centroid endpoints required')
        lo,hi=map(_number,axis)
        if lo>hi:raise ValueError('Ordered centroid bounds required')
        out.append([lo,hi])
    return out

def _check_flags(value):
    if isinstance(value,dict):
        for k,v in value.items():
            if k in FLAGS and v is not False:raise ValueError('No installed completeness or release claim permitted')
            _check_flags(v)
    elif isinstance(value,list):
        for v in value:_check_flags(v)

def _validate(bundle,root):
    if not isinstance(bundle,dict) or (bundle.get('candidate_id'),bundle.get('bundle_id'),bundle.get('evaluation_id'))!=(CANDIDATE_ID,BUNDLE_ID,SOURCE_EVALUATION_ID):
        raise ValueError('Exact candidate, bundle and source evaluation required')
    for flag in FLAGS:
        if bundle.get(flag) is not False:raise ValueError('No installed completeness or release claim permitted')
    path=root/INPUT
    if _digest(path)!=INPUT_SHA256:raise ValueError('Externally pinned parts input bytes differ')
    canonical=json.loads(gzip.decompress(path.read_bytes()))
    if bundle!=canonical:raise ValueError('Parts payload differs from authenticated canonical bundle')
    policy=json.loads((root/POLICY).read_bytes());_check_flags(policy)
    if policy.get('schema')!='osr-station-pair-mass-policy/1':raise ValueError('Mass policy schema differs')
    for key in ('actual_installed_positions_known','centroid_boxes_are_guaranteed_physical_bounds','shared_load_transfer_verified','reserve_covers_all_remaining_unknowns','gross_stock_trim_deductions_allowed'):
        if policy.get(key) is not False:raise ValueError('Policy cannot promote layout/reserve/trim assumptions')
    if policy['reserve_allocation']!='equal-share-six-cars' or policy['shared_intercar_allocation']!='half-to-each-adjacent-car':raise ValueError('Unsupported mass allocation hypothesis')
    if type(policy['maximum_group_rows']) is not int or not 1<=policy['maximum_group_rows']<=5000:raise ValueError('Bounded group budget required')
    _box(policy['default_centroid_box_m']);_box(policy['shared_centroid_box_relative_to_connection_m'])
    for b in policy['assembly_centroid_boxes_m'].values():_box(b)
    if _number(policy['gravity_m_s2'])<=0:raise ValueError('Positive gravity required')
    return policy

def _outer_bounds(rows,supports,gravity):
    """Conservative fractional CG bounds; mass/centroid correlations retained
    for reaction extrema. Each row has a positive mass interval and xyz box.
    Independent mass choices are a sensitivity domain, not a measured bound.
    """
    lo=fsum(r['mass_kg']['low'] for r in rows);hi=fsum(r['mass_kg']['high'] for r in rows)
    if lo<=0:raise ValueError('Positive accounted mass lower bound required')
    cg=[]
    for axis in range(3):
        qlo=qhi=0.
        for r in rows:
            m=r['mass_kg'];x=r['centroid_box_m'][axis]
            corners=[a*b for a in (m['low'],m['high']) for b in x]
            qlo+=min(corners);qhi+=max(corners)
        values=[q/m for q in (qlo,qhi) for m in (lo,hi)]
        cg.append([min(values),max(values)])
    left,right=supports;span=right-left
    if span<=0:raise ValueError('Ordered support positions required')
    reactions=[]
    for which in ('left','right'):
        lower=[];upper=[]
        for r in rows:
            m=r['mass_kg'];x=r['centroid_box_m'][0]
            corners=[gravity*a*((right-b) if which=='left' else (b-left))/span for a in (m['low'],m['high']) for b in x]
            lower.append(min(corners));upper.append(max(corners))
        reactions.append([fsum(lower),fsum(upper)])
    return dict(mass_interval_kg=[lo,hi],CG_outer_box_m=cg,left_support_force_outer_N=reactions[0],right_support_force_outer_N=reactions[1],
                possible_negative_support_force=min(reactions[0][0],reactions[1][0])<0,
                bounds_scope='Conservative outer intervals for independent declared mass/centroid hypotheses; different endpoints need not coexist. Not guaranteed physical bounds.')

def _fixed_scenario(rows,case,supports,gravity):
    mass=fsum(r['mass_kg'][case] for r in rows)
    first=[[fsum(r['mass_kg'][case]*r['centroid_box_m'][a][side] for r in rows) for side in (0,1)] for a in range(3)]
    left,right=supports;span=right-left
    endpoints=[]
    for moment in first[0]:
        rr=gravity*(moment-left*mass)/span;ll=gravity*mass-rr
        endpoints.append(dict(x_CG_m=moment/mass,left_support_force_N=ll,right_support_force_N=rr,
                              force_residual_N=ll+rr-gravity*mass,moment_residual_Nm=rr*span-gravity*(moment-left*mass)))
    return dict(case=case,mass_kg=mass,CG_outer_box_m=[[q/mass for q in interval] for interval in first],support_endpoints=endpoints,
                support_scope='Rigid whole-car accounting at two vertical point supports, including running-gear mass; not actual suspension, bogie or individual axle/wheel loads.')

def reconcile(bundle,*,unknown_mass_kg_per_train,root=ROOT):
    """Authenticate the fixed proposal and evaluate explicit residual scenarios.

    The required reserve is never inferred from a parent allocation. Zero is
    permitted only as an explicit study assumption and does not close unknowns.
    Gross procurement stock and existing direct costs are preserved unchanged.
    """
    root=Path(root);reserve=_interval(unknown_mass_kg_per_train);policy=_validate(bundle,root)
    if _digest(Path(__file__))!=_digest(root/PRODUCER):raise ValueError('Executing and declared producer differ')
    source_paths=(PRODUCER,POLICY,INPUT,'engineering/vehicle_parts/catalogue.py','engineering/vehicle_parts/policy.json',
                  'engineering/vehicle_parts/data/body.json','engineering/vehicle_parts/data/running_gear.json','engineering/vehicle_parts/data/services.json')
    epoch={p:_digest(root/p) for p in source_paths}
    for p in source_paths[3:]:
        if bundle['source_sha256'].get(p)!=epoch[p]:raise ValueError('Current parts source differs from authenticated bundle epoch')
    form=bundle['integration_policy']['formation'];ref=bundle['physical_definition']['reference_interfaces']
    if (form['cars'],form['body_length_m'],form['proposed_intercar_gap_m'],form['body_and_intercar_gap_length_m'])!=(6,17.,.65,105.25):raise ValueError('Fixed six-car650mm-gap formation required')
    supports=[float(x) for x in ref['bogie_centres_x_m']]
    if supports!=[-6.4,6.4] or ref['bogie_wheelbase_m']!=2.1:raise ValueError('Fixed support and wheel station interface required')
    pitch=form['body_length_m']+form['proposed_intercar_gap_m'];centres=[(i-2.5)*pitch for i in range(6)]
    assemblies={a['id']:a for a in bundle['assemblies']};groups=[];car_rows=[[] for _ in range(6)]
    for part in bundle['parts']:
        aid=part['assembly_id'];a=assemblies[aid];n=a['quantity_per_train'];per=part['quantity_per_assembly']
        if type(n) is not int or type(per) is not int or per<1:raise ValueError('Positive integral multiplicities required')
        mass=_interval(part['mass_each_kg'])
        if aid in policy['shared_assembly_ids']:
            if n!=5:raise ValueError('Exactly five intercar connections required')
            allocations=[('connection-'+str(i+1),per,[(i,.5),(i+1,.5)],(centres[i]+centres[i+1])/2) for i in range(5)]
        else:
            counts=([1,0,0,0,0,1] if aid in policy['terminal_assembly_ids'] else ([1,2,2,2,2,1] if aid==policy['passage_end_assembly_id'] else [n//6]*6))
            if sum(counts)!=n:raise ValueError('Assembly needs explicit nonuniform car allocation')
            allocations=[('car-'+str(i+1),per*count,[(i,1.)],centres[i]) for i,count in enumerate(counts) if count]
        if sum(count for _,count,_,_ in allocations)!=part['quantity_per_train']:raise ValueError('Grouped counts differ from exact source multiplicity')
        for suffix,count,shares,origin in allocations:
            shared=suffix.startswith('connection-');box=_box(policy['shared_centroid_box_relative_to_connection_m'] if shared else policy['assembly_centroid_boxes_m'].get(aid,policy['default_centroid_box_m']))
            global_box=deepcopy(box);global_box[0]=[x+origin for x in box[0]]
            row=dict(group_id=part['id']+'/'+suffix,source_part_id=part['id'],component_definition_id=part['component_definition_id'],assembly_id=aid,
                leaf_multiplicity=count,source_quantity_per_train=part['quantity_per_train'],mass_basis=deepcopy(part['mass_basis']),
                source_stock=deepcopy(part['stock']),mass_kg={c:mass[c]*count for c in CASES},centroid_box_train_m=global_box,
                position_evidence='explicit evaluation assumption; no installed occurrence transform',actual_installed_transform=None,
                owner='shared-intercar' if shared else suffix,car_shares=[dict(car=i+1,fraction=f) for i,f in shares],
                gross_stock_trim_deduction_kg=0.,trim_state='No deductions authorized; gross stock retained, finished allowances not re-trimmed',
                replaces_parent_account_ids=[],overlap_state='unresolved; no exact installed geometry/interference check')
            groups.append(row)
            for i,f in shares:
                b=deepcopy(global_box);b[0]=[x-centres[i] for x in global_box[0]]
                car_rows[i].append(dict(group_id=row['group_id'],fraction=f,mass_kg={c:row['mass_kg'][c]*f for c in CASES},centroid_box_m=b))
    if len(groups)>policy['maximum_group_rows']:raise ValueError('Grouped row budget exceeded')
    for i in range(6):
        car_rows[i].append(dict(group_id='explicit-unlisted-reserve/car-'+str(i+1),fraction=1/6,mass_kg={c:reserve[c]/6 for c in CASES},centroid_box_m=_box(policy['default_centroid_box_m'])))
    cars=[];g=policy['gravity_m_s2']
    for i,rows in enumerate(car_rows):
        cars.append(dict(car=i+1,body_centre_train_m=[centres[i],0.,0.],allocation_rows=rows,
            mass_scenarios=[_fixed_scenario(rows,c,supports,g) for c in CASES],outer_bounds=_outer_bounds(rows,supports,g)))
    subtotal={c:fsum(r['mass_kg'][c] for r in groups) for c in CASES}
    for c in CASES:
        expected=bundle['nominal_mass_kg']['known_leaf_subtotal'][c]
        if abs(subtotal[c]-expected)>1e-7:raise ValueError('No parent, assembly or leaf mass may be added twice')
    train_rows=[]
    for i,rows in enumerate(car_rows):
        for r in rows:
            b=deepcopy(r['centroid_box_m']);b[0]=[x+centres[i] for x in b[0]]
            train_rows.append({**r,'centroid_box_m':b})
    scenarios=[]
    for c in CASES:
        total=subtotal[c]+reserve[c];car_total=fsum(x['mass_scenarios'][CASES.index(c)]['mass_kg'] for x in cars)
        if abs(total-car_total)>1e-7:raise ValueError('Car/shared/reserve mass closure failed')
        scenarios.append(dict(case=c,catalogued_gross_stock_and_finished_allowance_kg=subtotal[c],explicit_uncatalogued_reserve_kg=reserve[c],
            conditional_accounted_train_mass_kg=total,per_car_mass_kg=[x['mass_scenarios'][CASES.index(c)]['mass_kg'] for x in cars],mass_allocation_residual_kg=car_total-total))
    train_bounds=_outer_bounds(train_rows,[-6.4+centres[0],6.4+centres[-1]],g)
    train_cg={k:train_bounds[k] for k in ('mass_interval_kg','CG_outer_box_m','bounds_scope')}
    result=dict(schema='osr-station-pair-mass-reconciliation/1',candidate_id=CANDIDATE_ID,source_bundle_id=BUNDLE_ID,source_evaluation_id=SOURCE_EVALUATION_ID,
        source_sha256=epoch,input_authentication='Exact externally pinned gzip bytes and equality of supplied payload; executing/declared source checked',policy_id=_identity(policy),
        formation=dict(cars=6,body_length_m=17.,intercar_gap_m=.65,body_and_gap_length_m=105.25,car_centres_train_x_m=centres,
            bogie_centres_car_x_m=supports,wheelset_centres_car_x_m=[x+d for x in supports for d in (-1.05,1.05)],
            complete_overall_train_length_m=None,minimum_usable_platform_length_m=None),
        grouped_occurrences=groups,group_count=len(groups),counted_leaf_multiplicity=sum(r['leaf_multiplicity'] for r in groups),cars=cars,mass_scenarios=scenarios,
        shared_intercar_mass_kg={c:fsum(r['mass_kg'][c] for r in groups if r['owner']=='shared-intercar') for c in CASES},
        train_outer_bounds=train_cg,
        procurement=dict(direct_parts_process_usd=deepcopy(bundle['direct_parts_process_usd']),gross_stock_costs_preserved=True,trim_scrap_credit_usd=None,
            scope='Source direct part/process subtotals unchanged; no net-trim discount or parent assembly cost. Final assembly, overhead, capital, qualification and installation remain outside source scope.'),
        reserve=dict(mass_kg_per_train=reserve,allocation='equal share to six cars, declared evaluation assumption',covers_all_unknowns=False,
            scope='Illustrative unlisted installation/redesign allowance, additional to counted leaves only; not a parent residual or supplier-internal duplicate'),
        actual_installed_positions_known=False,centroid_boxes_are_guaranteed_physical_bounds=False,installed_CG_m=None,installed_inertia_kg_m2=None,
        individual_axle_loads_N=None,individual_wheel_loads_N=None,rotating_inertia_kg_m2=None,rotating_equivalent_mass_kg=None,rotational_energy_J=None,
        rotating_scenario_required=True,physical_journey_evidence_inherited=False,
        unresolved=['Gross stock still needs unique net cuts/overlap reconciliation; procurement and installed mass differ',
            'Numeric centroid boxes are declared sensitivity assumptions, not feasible placements or guaranteed physical bounds',
            'Unlisted mass beyond the chosen reserve remains open; all catalogued bounded leaves do not establish completeness',
            'Car support reactions are whole-car rigid point-support accounting, not suspension/axle/wheel distribution',
            'No scalar force map, brake plant, reference rotating inertia or physical journey evidence transfers',
            'Adopting actual placements/cuts requires a descendant physical candidate; this evaluation keeps the source proposal fixed'],**FLAGS)
    if epoch!={p:_digest(root/p) for p in source_paths}:raise ValueError('Source changed during reconciliation')
    result['evaluation_id']=_identity(result);return result
