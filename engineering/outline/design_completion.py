"""Current bounded price coverage for published railway and component designs.

Historical geometry/evaluation packets remain immutable. This adapter prices
actual candidate stock under a new explicit rate hypothesis, retaining unmatched
scope reserves rather than transplanting the selected vehicle or claiming safety.
"""
from collections import defaultdict
from math import fsum, isfinite
from pathlib import Path
import gzip
import json
import time

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from . import vehicle_supply

PRODUCER='engineering/outline/design_completion.py'
CASES=('low','base','high')
BASE='docs/design-engine/'
VEHICLE_RATE_SOURCE=BASE+'current/exports/selected-vehicle-cost.json'
PACKETS=('coupled-railway','breadth-first-shape-portfolio','civil-shape-portfolio')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,selected_reference_changed=False,procurement_approved=False)


def _seal(value,key='evaluation_id'):
    value[key]=identity(value);return value


def _checked(value,key):
    if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):
        raise ValueError('Source record identity differs: '+key)
    return value


def _array(path):
    """Stream top-level gzip JSON arrays; do not expand the690MB campaign at once."""
    dec=json.JSONDecoder()
    with gzip.open(path,'rt',encoding='utf8') as handle:
        buffer=handle.read(1<<20).lstrip()
        if not buffer.startswith('['):raise ValueError('Source array required')
        buffer=buffer[1:];first=True
        while True:
            buffer=buffer.lstrip()
            while not buffer:
                buffer=handle.read(8<<20).lstrip()
                if not buffer:raise ValueError('Truncated source array')
            if buffer.startswith(']'):
                if (buffer[1:]+handle.read()).strip():raise ValueError('Trailing JSON bytes')
                return
            if not first:
                if buffer.startswith(','):buffer=buffer[1:].lstrip()
                elif buffer:raise ValueError('Source array separator differs')
            while True:
                try:row,end=dec.raw_decode(buffer);break
                except json.JSONDecodeError:
                    more=handle.read(8<<20)
                    if not more:raise ValueError('Truncated or invalid source array')
                    buffer+=more
            yield row
            buffer=buffer[end:];first=False


def _packet(root,name,files):
    folder=root/BASE/name
    manifest=_checked(json.loads((folder/'manifest.json').read_bytes()),'manifest_id')
    for file in files:
        if digest(folder/file)!=manifest['files_sha256'].get(file):
            raise ValueError('Published packet bytes differ: '+name+'/'+file)
    return manifest


def policy(root=ROOT):
    root=Path(root);data,observations=vehicle_supply._dataset(root)
    raw,landed=vehicle_supply._rates(data,observations)
    source=json.loads((root/VEHICLE_RATE_SOURCE).read_bytes())
    _checked(source,'cost_estimate_id')
    import tomllib
    fx=tomllib.loads((root/vehicle_supply.FX_SPEC).read_text())['currency']['iqd_per_usd']
    value=dict(schema='osr-design-completion-pricing-policy/1',currency='IQD',iqd_per_usd=fx,
        china_dataset_id=data['dataset_id'],material_iqd_per_kg={f:[x*fx for x in v] for f,v in landed.items()},
        rebar_iqd_per_kg=[(observations['cn-nbs-20261021-31-hrb400e-rebar']['advertised_price']['low']/1000/
            data['fx_reference']['quote_per_base']+x)*(1+y)*fx for x,y in zip((.15,.3,.55),(0.,.05,.12))],
        productive_labour_iqd_per_h=[x/.75 for x in source['assumption_values']['loaded_two_shift_skilled_wage_iqd_per_h']],
        paid_idle_factor=1/.75,productive_utilisation=.75,production_shifts=2,hours_per_shift=8,
        purchase_yield=[.96,.90,.82],labour_h_per_kg=[.10,.30,1.],setup_h_per_part=[.02,.08,.25],
        machine_h_per_kg=[.02,.08,.25],machine_cash_iqd_per_h=[3*fx,6*fx,12*fx],
        consumables_iqd_per_kg=[.12*fx,.30*fx,.75*fx],qa_iqd_per_kg=[.20*fx,.55*fx,1.5*fx],
        overhead_fraction=[.10,.20,.30],extra_bulk_discount=False,
        generic_material_recipe={'aluminium':.4,'steel':.2,'composite':.25,'misc':.15},
        body_allowances=dict(
            connector_hardware_kg_per_location=[.4,1.2,3.],fasteners_per_location=[2,4,8],
            fastener_assembly_kg_each=[.04,.08,.16],connector_usd_per_kg=[4.,8.,18.],
            fastener_usd_each=[.5,1.5,4.],adhesive_kg_per_boundary_m=[.04,.08,.16],
            adhesive_usd_per_kg=[6.,12.,25.],joint_fit_h_per_location=[.15,.5,1.5],
            fastener_fit_h_each=[.02,.05,.12],bond_prepare_h_per_m=[.03,.08,.2],
            handling_h_per_part=[.03,.08,.2],handling_h_per_tonne=[.5,1.,2.],
            handling_equipment_hours=[1.,3.,8.],handling_equipment_usd_per_h=[40.,80.,160.],
            body_inspection_h_per_location=[.05,.15,.4],body_inspection_h_per_part=[.02,.05,.12],
            body_inspection_global_h=[8.,16.,40.],inspection_consumables_usd_per_location=[1.,3.,8.],
            fixture_usd_per_envelope_m2=[250.,650.,1800.],fixture_usd_per_location=[30.,80.,200.],
            tool_usd_per_manufacturing_group=[20.,60.,160.],setup_h_per_group=[.5,1.5,4.],
            global_setup_h=[40.,120.,400.],
            basis='Explicit Class C interface/handling/inspection and one-time fixture/setup assumptions; no qualified connection, adhesive, jig or released process implied.'),
        process_basis='Candidate declared stock/process where available; otherwise explicit material-family provisional fabrication route.',
        boundary='Factory-gate stock price; unmatched installed equipment, civil and lifecycle reserves remain explicit at their source amounts. No claim of supplier quotation or physical completion.')
    value['material_iqd_per_kg']['generic']=[fsum(landed[f][i]*v for f,v in value['generic_material_recipe'].items())*fx for i in range(3)]
    return _seal(value,'policy_id')


def _family(name):
    name=str(name).lower()
    if any(s in name for s in ('aluminium','aluminum','6082','6061')):return 'aluminium'
    if any(s in name for s in ('gfrp','glass','composite','foam','core')):return 'composite'
    if any(s in name for s in ('steel','iron')):return 'steel'
    return 'generic'


def _stock(parts,p,*,fleet=1):
    totals=[0.,0.,0.];materials=defaultdict(float);hours=[0.,0.,0.]
    processes=set()
    for part in parts:
        mass=float(part['mass_kg']);family=_family(part.get('material_id'))
        if not isfinite(mass) or mass<=0:raise ValueError('Positive candidate stock mass required')
        materials[family]+=mass
        for i,c in enumerate(CASES):
            h=(part.get('process_hours') or {}).get(c)
            if h is None:h=mass*p['labour_h_per_kg'][i]+p['setup_h_per_part'][i]
            if not isfinite(h) or h<0:raise ValueError('Bounded process hours required')
            direct=(mass/p['purchase_yield'][i]*p['material_iqd_per_kg'][family][i]
                +h*p['productive_labour_iqd_per_h'][i]
                +mass*p['machine_h_per_kg'][i]*p['machine_cash_iqd_per_h'][i]
                +mass*(p['consumables_iqd_per_kg'][i]+p['qa_iqd_per_kg'][i]))
            totals[i]+=direct*(1+p['overhead_fraction'][i])*fleet;hours[i]+=h*fleet
        processes.add(part.get('process') or {'aluminium':'cut/form/machine/join/inspect',
            'steel':'cut/weld/machine/protect/inspect','composite':'mould/lay-up/cure/trim/bond/inspect',
            'generic':'bounded mixed-material fabrication/fit/inspect'}[family])
    return dict(cost_iqd=totals,net_stock_kg=sum(materials.values()),material_mass_kg=dict(sorted(materials.items())),
        process_hours=hours,processes=sorted(processes),part_count=len(parts),fleet_multiplier=fleet)


def _row(kind,candidate,source_id,scope,quantity,prices,p,**extra):
    value=dict(kind=kind,physical_candidate_id=candidate,source_evaluation_id=source_id,
        scope=scope,quantity=quantity,prices_iqd={key:dict(zip(CASES,[round(x,2) for x in amounts])) for key,amounts in prices.items()},
        pricing_policy_id=p['policy_id'],design_stage_cost_complete=True,estimate_class='C',
        completion_basis='All declared scope inputs are explicit calculated quantities or named bounded assumptions; this is not physical qualification.',
        outstanding_detail=['Installed connections/material qualification/QA and manufacturing detail',
            'Structural, braking, electrical, thermal and safety validation appropriate to this scope',
            'Surveyed site/procurement and independent release requirements'],**extra,**FLAGS)
    return _seal(value)


def _railway(source,p):
    cost=_checked(source['economics']['model_cost'],'evaluation_id');cid=source['candidate_id']
    if cost['candidate_id']!=cid or not cost['model_cost_complete_for_declared_case'] or cost['model_cost_missing_scopes']:
        raise ValueError('Complete same-candidate14-scope source estimate required')
    plan=cost['provisional_manufacturing_plan'];routes={r['cost_line_id']:r for r in plan['routes']}
    old=[0.,0.,0.];parts=[];retained=0;other_deltas=[0.,0.,0.];adjustments=[]
    for line in cost['cost_line_items']:
        if line['candidate_id']!=cid:raise ValueError('Mixed railway line candidate')
        if line['line_key'].startswith('vehicle-stock/'):
            route=routes.get(line['line_id'])
            if route is None or route['candidate_id']!=cid:raise ValueError('Missing same-candidate stock process route')
            mass=route['nominal_mass_kg_per_car']
            if abs(mass-line['quantity']['per_car_mass_kg'])>1e-8:raise ValueError('Stock and route masses differ')
            parts.append(dict(mass_kg=mass,material_id=route['material_id'],process_hours=route['labor_hours_per_car'],process=route['provisional_process']))
            for i,c in enumerate(CASES):old[i]+=line['scenario_iqd'][c]
        elif line['line_key']=='precast-reinforcement':
            kg=line['quantity']['reinforcement_kg']
            if not isfinite(kg) or kg<=0:raise ValueError('Positive same-candidate reinforcement quantity required')
            revised=[kg*p['rebar_iqd_per_kg'][i] for i in range(3)]
            delta=[revised[i]-line['scenario_iqd'][c] for i,c in enumerate(CASES)]
            other_deltas=[other_deltas[i]+delta[i] for i in range(3)]
            adjustments.append(dict(source_line_id=line['line_id'],line_key=line['line_key'],scope='guideway',
                quantity_kg=kg,original_iqd=line['scenario_iqd'],revised_iqd=dict(zip(CASES,revised))))
        else:retained+=1
    stock=_stock(parts,p,fleet=cost['corridor_basis']['fleet_cars']);delta=[stock['cost_iqd'][i]-old[i] for i in range(3)]
    cap=[cost['model_based_installed_CAPEX_iqd'][i]+delta[i]+other_deltas[i] for i in range(3)]
    life=[cost['model_based_whole_life_NPV_iqd'][i]+delta[i]+other_deltas[i] for i in range(3)]
    scope_totals={k:list(v) for k,v in cost['scope_totals_iqd'].items()}
    scope_totals['rolling-stock']=[scope_totals['rolling-stock'][i]+delta[i] for i in range(3)]
    if adjustments:scope_totals['guideway']=[scope_totals['guideway'][i]+other_deltas[i] for i in range(3)]
    if len(scope_totals)!=14 or any(min(v)<=0 for v in scope_totals.values()):raise ValueError('Positive fourteen-scope coverage required')
    return _row('railway-bundle',cid,cost['evaluation_id'],'Source-declared synthetic corridor, same nominal formation/service; no city extrapolation',
        dict(corridor=cost['corridor_basis'],body_candidate_id=source['body_candidate_id'],stock=stock),
        dict(installed_capital=cap,whole_life_npv=life),p,
        scope_totals_iqd=scope_totals,other_quantified_price_adjustments=adjustments,replaced_stock_line_count=len(parts),retained_bounded_line_count=retained,
        retained_cost_policy='All non-stock scopes/reserves, renewal, maintenance and disposal work remain at source bounded amounts. Only changed initial factory-stock and quantified reinforcement subtotals propagate into CAPEX and total NPV; cheaper initial supply does not imply cheaper future maintenance.',
        comparison_context_id=identity(dict(corridor=cost['corridor_basis'],policy_id=p['policy_id'])),
        source_assumption_id=cost['assumption_id'])



def _body_outline(body,stock,p):
    """Close the bounded body-production account without inventing located CAD."""
    a=p['body_allowances'];fx=p['iqd_per_usd'];parts=body['parts']
    ids={part['id'] for part in parts};joins=body.get('joins',[]);connections=body.get('connections',[])
    joint_ids={j['id'] for j in joins}
    declared_unknown={c['occurrence_id'] for c in body.get('components',[])
        if c.get('inventory_status')!='located'}-joint_ids
    covered={pid for j in joins for pid in j.get('part_ids',[]) if pid in ids}
    for connection in connections:
        for name in ('from','to'):
            endpoint=connection.get(name,[])
            if endpoint and endpoint[0] in ids:covered.add(endpoint[0])
    # Parts without an explicit connection get a named one-interface reserve,
    # rather than being presumed attached for free. Counts are pricing hypotheses.
    unresolved=sorted(ids-covered)
    locations=len(joint_ids)+len(declared_unknown)+len(unresolved)
    locations=max(1,locations)
    panels={};groups=set()
    for part in parts:
        group=part.get('manufacturing_occurrence_id') or part['id'];groups.add(group)
        if part.get('kind')=='box' and part.get('size_m'):
            dimensions=sorted(float(x) for x in part['size_m'])
            if len(dimensions)!=3 or min(dimensions)<=0:raise ValueError('Positive panel dimensions required')
            # Use the two large face dimensions. Shared skin/core manufacturing
            # groups own one perimeter, avoiding duplicated sandwich seams.
            panels[group]=max(panels.get(group,0.),2*(dimensions[-1]+dimensions[-2]))
    boundary=sum(panels.values())
    boundary_basis='Sum of maximum large-face perimeter per actual panel manufacturing group; provisional attachment/bond boundary, not a developed joint drawing.'
    if not panels:
        boundary=2*(body['parameters']['length_m']+body['parameters']['width_m'])
        boundary_basis='Named envelope perimeter reserve because no explicit panel-group boundary is available; not a zero adhesive/attachment scope.'
    envelope=body['parameters']['length_m']*body['parameters']['width_m']
    qty=dict(explicit_joint_locations=len(joint_ids),additional_declared_unknown_interfaces=len(declared_unknown),
        unrepresented_part_attachment_reserve_count=len(unresolved),unrepresented_part_ids=unresolved,
        priced_joint_locations=locations,graph_connection_count=len(connections),part_count=len(parts),
        panel_manufacturing_group_count=len(panels),manufacturing_group_count=len(groups),
        attachment_boundary_m=boundary,attachment_boundary_basis=boundary_basis,envelope_plan_m2=envelope,
        fastener_units={},connector_hardware_mass_reserve_kg={},adhesive_mass_reserve_kg={},
        total_added_hardware_mass_reserve_kg={},repeat_productive_hours={},one_time_setup_hours={})
    component={name:[] for name in ('connector_hardware','fasteners','adhesive',
        'joint_and_bond_assembly','handling_and_equipment','body_level_inspection','additional_production_overhead')}
    repeat=[];fixed=[];first=[]
    for i,case in enumerate(CASES):
        connectors=locations*a['connector_hardware_kg_per_location'][i]
        bolts=locations*a['fasteners_per_location'][i]
        glue=boundary*a['adhesive_kg_per_boundary_m'][i]
        join_h=locations*a['joint_fit_h_per_location'][i]+bolts*a['fastener_fit_h_each'][i]+boundary*a['bond_prepare_h_per_m'][i]
        handle_h=len(parts)*a['handling_h_per_part'][i]+stock['net_stock_kg']/1000*a['handling_h_per_tonne'][i]
        inspect_h=locations*a['body_inspection_h_per_location'][i]+len(parts)*a['body_inspection_h_per_part'][i]+a['body_inspection_global_h'][i]
        wage=p['productive_labour_iqd_per_h'][i]
        values=dict(connector_hardware=connectors*a['connector_usd_per_kg'][i]*fx,
            fasteners=bolts*a['fastener_usd_each'][i]*fx,adhesive=glue*a['adhesive_usd_per_kg'][i]*fx,
            joint_and_bond_assembly=join_h*wage,
            handling_and_equipment=handle_h*wage+a['handling_equipment_hours'][i]*a['handling_equipment_usd_per_h'][i]*fx,
            body_level_inspection=inspect_h*wage+locations*a['inspection_consumables_usd_per_location'][i]*fx)
        values['additional_production_overhead']=sum(values.values())*p['overhead_fraction'][i]
        for name in component:component[name].append(values[name])
        total=stock['cost_iqd'][i]+sum(values.values());repeat.append(total)
        setup_h=len(groups)*a['setup_h_per_group'][i]+a['global_setup_h'][i]
        tooling=(envelope*a['fixture_usd_per_envelope_m2'][i]+locations*a['fixture_usd_per_location'][i]
            +len(groups)*a['tool_usd_per_manufacturing_group'][i])*fx+setup_h*wage
        fixed.append(tooling);first.append(total+tooling)
        qty['fastener_units'][case]=bolts
        qty['connector_hardware_mass_reserve_kg'][case]=connectors
        qty['adhesive_mass_reserve_kg'][case]=glue
        qty['total_added_hardware_mass_reserve_kg'][case]=connectors+bolts*a['fastener_assembly_kg_each'][i]+glue
        qty['repeat_productive_hours'][case]=stock['process_hours'][i]+join_h+handle_h+inspect_h
        qty['one_time_setup_hours'][case]=setup_h
    return dict(quantity=qty,repeat_factory_gate_iqd=repeat,one_time_tooling_setup_iqd=fixed,
        first_body_total_iqd=first,additional_repeat_components_iqd=component,
        scope='Complete provisional body-production outline: stock plus connection hardware/fasteners/adhesive, interface joining, handling, body-level inspection and one-time fixtures/setup. Purchased vehicle fitout is outside this body scope.',
        added_mass_basis='Evaluation-only hardware/adhesive reserves; no new located CAD, material assignment or physical candidate change.',
        joining_boundary='Additional interface fit/torque/bond and body assembly beyond nominal part fabrication; no second charge for part cutting/machining or part-level stock QA.',
        tooling_policy='One complete fixture/tool/setup account per design, not amortised into repeat-body prices or speculative future production.',
        shop_equipment_basis='Generic shop processing uses cash/hired machine and handling-hour rates; acquisition of an entire shared factory/building remains a project-level account.',
        installed_mass_qualified=False,body_outline_cost_complete=True)


def _source_inputs(root):
    root=Path(root)
    required=('coupled-railway/comparison.json.gz','breadth-first-shape-portfolio/result.json',
        'breadth-first-shape-portfolio/candidates.json.gz','civil-shape-portfolio/result.json','civil-shape-portfolio/candidates.json.gz')
    result={PRODUCER:digest(root/PRODUCER),vehicle_supply.PRODUCER:digest(root/vehicle_supply.PRODUCER),
        vehicle_supply.DATA:digest(root/vehicle_supply.DATA),vehicle_supply.FX_SPEC:digest(root/vehicle_supply.FX_SPEC),
        'engineering/station_rail/common.py':digest(root/'engineering/station_rail/common.py'),
        'engineering/outline/make_buy.py':digest(root/'engineering/outline/make_buy.py'),VEHICLE_RATE_SOURCE:digest(root/VEHICLE_RATE_SOURCE)}
    manifests={}
    for name in PACKETS:
        files=[s.split('/',1)[1] for s in required if s.startswith(name+'/')]
        m=_packet(root,name,files);manifests[name]=m['manifest_id']
        result[BASE+name+'/manifest.json']=digest(root/BASE/name/'manifest.json')
        for file in files:result[BASE+name+'/'+file]=m['files_sha256'][file]
    return result,manifests


def sources(root=ROOT):
    """Cheap exact request dependency map, including all source price packets."""
    return _source_inputs(root)[0]


def validate(value,root=ROOT):
    """Validate a resumed compact design result without repeating calculations."""
    _checked(value,'evaluation_id');_checked(value['pricing_policy'],'policy_id')
    current_sources,current_manifests=_source_inputs(root)
    if (value.get('schema')!='osr-design-price-coverage/1' or value['source_sha256']!=current_sources
            or value.get('source_manifest_ids')!=current_manifests):
        raise ValueError('Design completion source epoch differs')
    rows=value['rows'];counts={kind:sum(r['kind']==kind for r in rows)
        for kind in ('railway-bundle','vehicle-body','civil-span')}
    if (counts!={'railway-bundle':112,'vehicle-body':54,'civil-span':18} or value['counts']!=counts or len(rows)!=184
            or value.get('declared_design_count')!=184 or value.get('all_declared_designs_priced') is not True):
        raise ValueError('Exact184-design coverage required')
    if len({(r['kind'],r['physical_candidate_id']) for r in rows})!=184:
        raise ValueError('Unique physical design coverage required')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Cost completion cannot qualify designs')
    for row in rows:
        _checked(row,'evaluation_id')
        if row.get('design_stage_cost_complete') is not True or any(row.get(k) is not False for k in FLAGS):
            raise ValueError('Positive design-outline completion with separate qualification required')
        if row['pricing_policy_id']!=value['pricing_policy']['policy_id']:
            raise ValueError('Mixed design pricing policy')
        if any(not isfinite(x) or x<=0 for prices in row['prices_iqd'].values() for x in prices.values()):
            raise ValueError('Positive finite outline prices required')
        if row['kind']=='vehicle-body' and not row.get('body_outline',{}).get('body_outline_cost_complete'):
            raise ValueError('Complete provisional body-production scope required')
    return dict(verified=True,evaluation_id=value['evaluation_id'],counts=counts,**FLAGS)

def evaluate(root=ROOT,policy=None):
    started=time.perf_counter();root=Path(root)
    p=globals()['policy'](root) if policy is None else _checked(policy,'policy_id')
    for key in ('purchase_yield','productive_labour_iqd_per_h','labour_h_per_kg','machine_cash_iqd_per_h','rebar_iqd_per_kg'):
        if len(p[key])!=3 or any(type(x) not in (int,float) or not isfinite(x) or x<=0 for x in p[key]):
            raise ValueError('Explicit positive three-case pricing policy required: '+key)
    if p.get('extra_bulk_discount') is not False:raise ValueError('No second bulk discount permitted')
    sources,manifests=_source_inputs(root)
    rows=[]
    for record in _array(root/BASE/'coupled-railway/comparison.json.gz'):rows.append(_railway(record,p))
    body_results=_checked(json.loads((root/BASE/'breadth-first-shape-portfolio/result.json').read_bytes()),'portfolio_id')
    by_body={r['candidate_id']:r for r in body_results['evaluations']}
    for body in _array(root/BASE/'breadth-first-shape-portfolio/candidates.json.gz'):
        _checked(body,'definition_id')
        if body['candidate_id']!=identity(body['physical']):raise ValueError('Body physical identity differs')
        old=by_body.pop(body['candidate_id']);stock=_stock(body['parts'],p)
        if old['definition_id']!=body['definition_id']:raise ValueError('Body definition differs across packet')
        outline=_body_outline(body,stock,p)
        rows.append(_row('vehicle-body',body['candidate_id'],identity(old),outline['scope'],
            stock,dict(factory_gate_stock=stock['cost_iqd'],factory_gate=stock['cost_iqd'],
                repeat_body_factory_gate=outline['repeat_factory_gate_iqd'],
                one_time_tooling_setup=outline['one_time_tooling_setup_iqd'],first_body_total=outline['first_body_total_iqd']),
            p,body_definition_id=body['definition_id'],body_outline=outline,
            excluded_scope='Purchased vehicle fitout/equipment, whole-vehicle final assembly/delivery, shared factory premises, city/railway infrastructure and lifecycle costs legitimately remain outside this body-production component scope.'))
    if by_body:raise ValueError('Body candidate coverage differs')
    civil_results=_checked(json.loads((root/BASE/'civil-shape-portfolio/result.json').read_bytes()),'portfolio_id')
    geometries={r['candidate_id']:r for r in _array(root/BASE/'civil-shape-portfolio/candidates.json.gz')}
    for old in civil_results['evaluations']:
        _checked(old,'evaluation_id');geometry=geometries.pop(old['candidate_id']);q=old['quantities'];cost=old['cost_estimate']
        _checked(geometry,'candidate_id');_checked(q,'evaluation_id')
        if q['candidate_id']!=geometry['candidate_id'] or cost['candidate_id']!=geometry['candidate_id']:
            raise ValueError('Civil geometry, quantity and price identities differ')
        steel=q['by_material'].get('structural_steel',{}).get('mass_kg',0.);new_prices={k:[] for k in ('factory_gate','delivered','scoped_installed','scoped_whole_life_npv')}
        for i,c in enumerate(CASES):
            lines=cost['line_items_iqd'];original=cost['cases'][i]
            metal=steel*p['material_iqd_per_kg']['steel'][i]+original['preliminary_reinforcement_kg']*p['rebar_iqd_per_kg'][i]
            labour=original['factory_person_hours']*p['productive_labour_iqd_per_h'][i]
            machine=original['factory_person_hours']*.5*p['machine_cash_iqd_per_h'][i]
            old_changed=sum(lines[k][c] for k in ('steel_and_reinforcement','factory_labour','machine','factory_overhead'))
            retained_direct=original['factory_gate_iqd']-old_changed
            overhead=(retained_direct+metal+labour+machine)*p['overhead_fraction'][i]
            delta=metal+labour+machine+overhead-old_changed
            for key,source_key in (('factory_gate','factory_gate_iqd'),('delivered','delivered_iqd'),
                    ('scoped_installed','scoped_installed_iqd'),('scoped_whole_life_npv','scoped_lifecycle_npv_iqd')):
                new_prices[key].append(original[source_key]+delta)
        rows.append(_row('civil-span',old['candidate_id'],old['evaluation_id'],'One20m span with source bounded reinforcement/prestress/supports, delivery and erection; not a whole city',
            q,new_prices,p,geometry_identity=identity(geometry),
            retained_cost_policy='Retain concrete, prestress, tooling, rail/fastening interface, foundations/bearings, transport, erection, services, maintenance/renewal/disposal reserves. Reprice quantified steel/rebar, factory labour and cash machine work; rebuild factory overhead.'))
    if geometries:raise ValueError('Civil candidate coverage differs')
    counts={k:sum(r['kind']==k for r in rows) for k in ('railway-bundle','vehicle-body','civil-span')}
    if counts!={'railway-bundle':112,'vehicle-body':54,'civil-span':18}:raise ValueError('Published bounded design inventory differs; declare a revised coverage policy')
    if len({(r['kind'],r['physical_candidate_id']) for r in rows})!=len(rows):raise ValueError('Duplicate priced candidate')
    for row in rows:
        for amounts in row['prices_iqd'].values():
            if any(not isfinite(x) or x<=0 for x in amounts.values()):raise ValueError('Positive finite component-scope estimate required')
    if any(digest(root/n)!=sha for n,sha in sources.items()):raise ValueError('Source changed during price completion')
    value=_seal(dict(schema='osr-design-price-coverage/1',pricing_policy=p,counts=counts,
        all_declared_designs_priced=True,declared_design_count=len(rows),rows=rows,
        source_manifest_ids=manifests,source_sha256=sources,
        identity_policy='Historical packet byte integrity and same-candidate evaluation identities verified; no historical solver reexecution or current native evidence admission claimed.',
        scope_policy='112 whole synthetic-corridor scenarios,54 complete provisional body-production outlines with separate stock/repeat/tooling prices, and18 civil-span components; component cost completion does not mean full railway completion.',
        all_cities_priced=False,global_optimum_established=False,**FLAGS))
    return value,dict(elapsed_s=time.perf_counter()-started,native_solver_jobs=0,CAD_jobs=0,
        streamed_railway_records=counts['railway-bundle'])
