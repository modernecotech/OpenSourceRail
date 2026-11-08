"""Replay-backed import and revision of calculated city planning hypotheses.

The selected physical reference and original map files remain untouched. An
editable planning base is a proposal, never a transfer of engineering approval.
"""
from copy import deepcopy
from math import fsum
from pathlib import Path
import gzip
import json
import re

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,digest,identity
from engineering.development_baseline import planning
from . import planning_geometry as geometry

PRODUCER='engineering/outline/planning_adapter.py'
SEED_SCHEMA='osr-priced-planning-seed/1'
EDIT_SCHEMA='osr-priced-planning-edits/1'
PUBLICATION='docs/design-engine/outline-completion'
FLAGS={**planning.DISPOSITIONS,'selected_reference_changed':False,'procurement_approved':False}
_LOADED={PRODUCER:digest(__file__),geometry.PRODUCER:digest(geometry.__file__)}
CHAINAGE_EPSILON_M=1e-7


def _endpoint(value,length):
    if -CHAINAGE_EPSILON_M<=value<0:return 0.
    if length<value<=length+CHAINAGE_EPSILON_M:return length
    return value


def merge_sources(*maps):
    value={}
    for mapping in maps:
        for n,h in mapping.items():
            if n in value and value[n]!=h:raise planning.PlanningError('Mixed planning source epochs: '+n)
            value[n]=h
    return value


def _sources(root,mapping):
    for n,h in mapping.items():
        if not re.fullmatch('[0-9a-f]{64}',str(h)):raise planning.PlanningError('Invalid source digest')
        if digest(planning._safe_file(root,n))!=h:raise planning.PlanningError('Planning source changed: '+n)


def _published_seed(root,slug):
    if not isinstance(slug,str) or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',slug):
        raise planning.PlanningError('Bounded known city slug required')
    folder=Path(root)/PUBLICATION
    manifest=json.loads(planning._safe_file(root,PUBLICATION+'/manifest.json').read_bytes())
    if manifest.get('schema')!='osr-outline-completion-publication/2' or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):
        raise planning.PlanningError('Published outline manifest identity differs')
    name='cities/'+slug+'.json.gz';path=planning._safe_file(root,PUBLICATION+'/'+name)
    if manifest.get('files_sha256',{}).get(name)!=digest(path):raise planning.PlanningError('Published city payload differs')
    value=planning._read_gzip_json(path)
    if value.get('city',{}).get('slug')!=slug or 'planning_seed' not in value:
        raise planning.PlanningError('Published city lacks a replay planning seed')
    if any(value.get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','selected_reference_changed')):
        raise planning.PlanningError('Calculated planning import cannot grant release')
    seed=value['planning_seed']
    for field,key in (('selected_alignment_id','selected_alignment_id'),('source_outline_evaluation_id','evaluation_id'),
            ('research_configuration_id','research_configuration_id'),('source_result_sha256','full_result_sha256')):
        if seed.get(field)!=value.get(key):raise planning.PlanningError('Published planning seed differs: '+field)
    return seed


def validate_seed(seed,root=ROOT):
    if not isinstance(seed,dict) or seed.get('schema')!=SEED_SCHEMA or seed.get('seed_id')!=identity({k:v for k,v in seed.items() if k!='seed_id'}):
        raise planning.PlanningError('Sealed priced planning seed required')
    required={'city_slug','rules','selected_alignment_id','selected_alignment_kind','selected_city_input_id',
        'selected_service_evaluation_id','source_outline_evaluation_id','source_cost_evaluation_id',
        'research_configuration_id','reference_candidate_ids','source_sha256','source_result_sha256'}
    if not required<=set(seed):raise planning.PlanningError('Incomplete priced planning seed')
    for name in required-{'city_slug','rules','selected_alignment_kind','reference_candidate_ids','source_sha256'}:
        if not re.fullmatch('[0-9a-f]{64}',str(seed[name])):raise planning.PlanningError('Invalid seed identity: '+name)
    if encoded(seed)!=encoded(_published_seed(root,seed.get('city_slug'))):
        raise planning.PlanningError('Seed is not the currently published city planning seed')
    _sources(root,seed['source_sha256'])
    if any(seed.get(k) not in (None,False) for k in FLAGS):raise planning.PlanningError('Planning seed cannot grant release')
    return seed


def _reconstruct(seed,root,context=None,verify_cost=False):
    from . import city_inputs,city_alignment,city_service,coordinator
    engineering=(context or {}).get('engineering',context) if context else coordinator.prepare(root)
    geography=(context or {}).get('geography') or city_inputs.prepare(root)
    original=city_inputs.load(seed['city_slug'],root=root,context=geography)
    portfolio=city_alignment.propose(original,root=root,policy=seed['rules'])
    matching=[v for v in portfolio['variants'] if v['alignment_id']==seed['selected_alignment_id']]
    if len(matching)!=1 or matching[0]['kind']!=seed['selected_alignment_kind']:
        raise planning.PlanningError('Selected outline alignment does not replay')
    city=matching[0]['city_input']
    if city['input_id']!=seed['selected_city_input_id'] or city['reference_candidate_ids']!=seed['reference_candidate_ids']:
        raise planning.PlanningError('Selected city or physical reference does not replay')
    services=city_service.evaluate(city,seed['rules'],engineering['spec']['design'],engineering['vehicle'],root=root)
    if services['evaluation_id']!=seed['selected_service_evaluation_id']:
        raise planning.PlanningError('Selected city service does not replay')
    if verify_cost:
        from . import city_project_cost
        cost=city_project_cost.evaluate_city_cost(city,services['line_services'],engineering,policy=seed['rules'],root=root)
        if cost['evaluation_id']!=seed['source_cost_evaluation_id']:raise planning.PlanningError('Selected city cost does not replay')
    return city,services


def export_plan(seed,root=ROOT,*,context=None,verify_cost=False):
    validate_seed(seed,root);city,services=_reconstruct(seed,root,context,verify_cost)
    return _build_plan(seed,city,services,verify_cost=verify_cost)


def _build_plan(seed,city,services,*,verify_cost=False,origin=None,design=None):
    by={x['line_id']:x for x in services['line_services']};lines=[];mapping={};normalizations=[];route_normalizations=[]
    for line in city['lines']:
        duty=by[line['line_id']];stops=deepcopy(duty['operational_stops'])
        editable_length=geometry.route(line['coordinates'],line['shape'])[-1]
        if abs(editable_length-line['route_m'])>CHAINAGE_EPSILON_M:
            raise planning.PlanningError('Source route length differs beyond endpoint numerical epsilon')
        if editable_length!=line['route_m']:
            route_normalizations.append(dict(line_id=line['line_id'],source_route_m=line['route_m'],
                editable_route_m=editable_length,delta_m=editable_length-line['route_m'],
                scope='Binary64 chain accumulation only; no route rescaling or physical coordinate change'))
        for stop,dwell in zip(stops,duty['service']['stop_dwell_s']):stop['dwell_s']=dwell
        for stop in stops:
            at=stop['chainage_m'];normalized=_endpoint(at,editable_length)
            if at!=normalized:
                normalizations.append(dict(line_id=line['line_id'],stop_id=stop['id'],source_chainage_m=at,
                    editable_chainage_m=normalized,delta_m=normalized-at,
                    scope='Binary64 endpoint representation only; source geometry and physical position unchanged'))
                stop['chainage_m']=normalized
        for c in duty['station_repair']['complexes']:
            for old in c['original_stop_ids']:mapping[old]=c['operational_stop_id']
        lines.append(dict(id=line['line_id'],shape=line['shape'],coordinates=deepcopy(line['coordinates']),
            length_m=editable_length,headway_s=duty['requirements']['headway_s'],
            design_speed_cap_m_s=duty['design']['speed_m_s'],stops=stops))
    # Existing records use an empty OD list. Preserve any future original rows
    # separately: an import never fabricates demand or discards their provenance.
    od=[]
    for row in city.get('od',[]):
        r=deepcopy(row);r['origin']=mapping.get(r['origin'],r['origin']);r['destination']=mapping.get(r['destination'],r['destination'])
        if r['origin']!=r['destination']:od.append(r)
    provenance=origin or seed
    plan=dict(schema=planning.BASE_SCHEMA,environment='planning',city=seed['city_slug'],revision=0,
        source_outline_evaluation_id=provenance['source_outline_evaluation_id'],
        source_service_evaluation_id=provenance.get('source_service_evaluation_id',seed['selected_service_evaluation_id']),
        source_cost_evaluation_id=provenance['source_cost_evaluation_id'],
        research_configuration_id=provenance['research_configuration_id'],
        source_alignment_id=provenance.get('selected_alignment_id'),official_seed_id=seed['seed_id'],
        selection_id=city['selection_id'],source_sha256=merge_sources(seed['source_sha256'],city.get('source_sha256',{}),services.get('source_sha256',{}),_LOADED),
        lines=lines,interchanges=deepcopy(city.get('interchanges',[])),od=od,
        outline_context=dict(seed=deepcopy(seed),city_input_template=deepcopy(city),
            baseline_line_services=deepcopy(services['line_services']),original_OD=deepcopy(city.get('od',[])),
            study_rules=deepcopy(origin['rules'] if origin else seed['rules']),
            source_study=deepcopy(origin),requested_design=deepcopy(design),
            verification_metadata_policy='Observed import/cost verification belongs in the external execution receipt',
            endpoint_chainage_normalizations=normalizations,route_length_normalizations=route_normalizations,
            original_geography_modified=False),
        **{key:False for key in planning.PLAN_DISPOSITIONS})
    contexts=[n for n in seed['source_sha256'] if n.startswith('cities/catalogue/') and n.endswith('/map-context.json.gz')]
    if len(contexts)==1:
        plan['map_context']=dict(path=contexts[0],sha256=seed['source_sha256'][contexts[0]],
            role='Geographic context only; not survey, route-clearance, demand, engineering or operating evidence')
    plan['revision_sha256']=planning.digest_json(plan)
    return planning._validate_plan(plan,seed['city_slug'])


def plan_from_record(seed,city_record,root=ROOT,*,trusted_record_sha256,design=None):
    """Rebase on an exact immutable calculation verified by the server caller.

    The expected hash must come from the caller's verified run manifest, never
    from an untrusted upload. This function does not authenticate that manifest.
    """
    validate_seed(seed,root)
    if not re.fullmatch('[0-9a-f]{64}',str(trusted_record_sha256)) or planning.digest_bytes(encoded(city_record))!=trusted_record_sha256:
        raise planning.PlanningError('Server-verified study artifact hash differs')
    if city_record.get('evaluation_id')!=identity({k:v for k,v in city_record.items() if k!='evaluation_id'}):
        raise planning.PlanningError('Source study record identity differs')
    _sources(root,city_record['source_sha256'])
    if any(city_record.get(k) not in (None,False) for k in FLAGS):raise planning.PlanningError('Source study cannot grant release')
    city=city_record['geometry_and_service'];services=city_record['service_evaluation'];cost=city_record['cost']
    for value,key in ((city,'input_id'),(services,'evaluation_id'),(cost,'evaluation_id')):
        if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):
            raise planning.PlanningError('Source study subrecord identity differs: '+key)
    if (city['city']['slug']!=seed['city_slug'] or city['reference_candidate_ids']!=seed['reference_candidate_ids']
            or city_record['reference_candidate_ids']!=seed['reference_candidate_ids']
            or services['city_input_id']!=city['input_id'] or cost['city_input_id']!=city['input_id']):
        raise planning.PlanningError('Mixed study city, service, cost or physical reference')
    origin=dict(kind='server-verified-calculated-study',source_study_sha256=trusted_record_sha256,
        source_outline_evaluation_id=city_record['evaluation_id'],source_city_input_id=city['input_id'],
        source_service_evaluation_id=services['evaluation_id'],source_cost_evaluation_id=cost['evaluation_id'],
        research_configuration_id=city_record['research_configuration_id'],
        selected_alignment_id=city_record.get('selected_alignment_id'),selected_alignment_kind=city_record.get('selected_alignment_kind'),
        rules=deepcopy(city_record['policy']),official_seed_id=seed['seed_id'])
    return _build_plan(seed,city,services,origin=origin,design=design)


def verify_base(base,root=ROOT,*,trusted_base_sha256=None):
    planning._validate_plan(base,base.get('city'));validate_seed(base['outline_context']['seed'],root)
    _sources(root,base['source_sha256'])
    if trusted_base_sha256 is not None:
        if not re.fullmatch('[0-9a-f]{64}',str(trusted_base_sha256)) or planning.digest_bytes(encoded(base))!=trusted_base_sha256:
            raise planning.PlanningError('Server-verified planning base artifact hash differs')
    else:
        expected=export_plan(base['outline_context']['seed'],root)
        if encoded(base)!=encoded(expected):raise planning.PlanningError('Rebased planning revisions require a server-verified immutable base artifact')
    return base


def _line_input(original,current,baseline_duty):
    """Expand edited complexes back into their original raw member offsets."""
    output=deepcopy(original);same_geometry=current['coordinates']==original['coordinates'] and current['shape']==original['shape']
    editable_length=geometry.route(current['coordinates'],current['shape'])[-1]
    chain=deepcopy(original.get('coordinate_chainages_m')) if same_geometry else None
    if chain is None:chain=geometry.route(current['coordinates'],current['shape'])
    length=original['route_m'] if same_geometry else chain[-1]
    oldops={s['id']:deepcopy(s) for s in baseline_duty['operational_stops']}
    for stop,dwell in zip(baseline_duty['operational_stops'],baseline_duty['service']['stop_dwell_s']):oldops[stop['id']]['dwell_s']=dwell
    repairs={c['operational_stop_id']:c for c in baseline_duty['station_repair']['complexes']}
    raw={s['id']:s for s in original['stops']};stops=[];walk=0.;maximum=0.;aliases={}
    ring=current['shape']=='ring';oldring=original['shape']=='ring'
    remaining={s['id']:s for s in current['stops']}
    for sid,old in oldops.items():
        if sid in remaining:target=remaining[sid]
        else:target=min(current['stops'],key=lambda s:planning._distance([old['lon'],old['lat']],[s['lon'],s['lat']]))
        relocation=planning._distance([old['lon'],old['lat']],[target['lon'],target['lat']])*1.25
        oldrepair=repairs[sid];walk+=relocation*len(oldrepair['original_stop_ids'])
        maximum=max(maximum,oldrepair['maximum_added_walk_m']+relocation)
        representative=repairs[target['id']]['original_stop_ids'][0] if target['id'] in repairs else target['id']
        aliases.update({member:representative for member in oldrepair['original_stop_ids']})
    for stop in current['stops']:
        sid=stop['id'];old=oldops.get(sid)
        members=repairs[sid]['original_stop_ids'] if sid in repairs else [sid]
        for member in members:
            unchanged_position=(old is not None and same_geometry and
                stop['chainage_m']==_endpoint(old['chainage_m'],editable_length) and
                stop['lon']==old['lon'] and stop['lat']==old['lat'])
            if unchanged_position and member in raw:
                item=deepcopy(raw[member])
                if stop['dwell_s']!=old['dwell_s']:item['dwell_s']=stop['dwell_s']
                stops.append(item);continue
            offset=raw[member]['chainage_m']-old['chainage_m'] if old is not None else 0.
            if oldring and offset>original['route_m']/2:offset-=original['route_m']
            if oldring and offset<-original['route_m']/2:offset+=original['route_m']
            at=stop['chainage_m']+offset
            if ring:at%=length
            else:
                # Raw and operational endpoint chainages can differ by binary64
                # accumulation. Preserve the existing representation-only rule
                # after re-expansion as well as when constructing the base.
                at=_endpoint(at,length)
                if not 0<=at<=length:raise planning.PlanningError('Relocated station complex exceeds the route envelope')
            item=deepcopy(raw.get(member,stop));item.update(id=member,chainage_m=at)
            # Preserve raw dwell defaults for exact no-edit replay; only a
            # changed visible dwell deliberately revises the underlying request.
            if old is None or stop['dwell_s']!=old.get('dwell_s'):item['dwell_s']=stop['dwell_s']
            item['lon'],item['lat']=geometry.point(current['coordinates'],chain,at)
            stops.append(item)
    stops.sort(key=lambda s:s['chainage_m'])
    if any(b['chainage_m']<=a['chainage_m'] for a,b in zip(stops,stops[1:])):
        raise planning.PlanningError('Edited complex member envelopes overlap; revise explicit stop positions')
    legs=[dict(from_stop=a['id'],to_stop=b['id'],distance_m=b['chainage_m']-a['chainage_m'],closing_leg=False) for a,b in zip(stops,stops[1:])]
    if ring:legs.append(dict(from_stop=stops[-1]['id'],to_stop=stops[0]['id'],distance_m=length-stops[-1]['chainage_m']+stops[0]['chainage_m'],closing_leg=True))
    output.update(shape=current['shape'],coordinates=deepcopy(current['coordinates']),coordinate_chainages_m=chain,
        route_m=length,operational_route_m=fsum(x['distance_m'] for x in legs),stops=stops,legs=legs,
        design_speed_cap_m_s=current['design_speed_cap_m_s'],planning_access_aliases=aliases)
    return output,walk,maximum


def apply_edits(base,bundle,root=ROOT,*,trusted_base_sha256=None):
    verify_base(base,root,trusted_base_sha256=trusted_base_sha256);seed=base['outline_context']['seed']
    expected={'schema','city','base_revision_sha256','seed_id','source_outline_evaluation_id','actor','edits'}
    if not isinstance(bundle,dict) or set(bundle)!=expected or bundle.get('schema')!=EDIT_SCHEMA:
        raise planning.PlanningError('Typed priced planning edit bundle required')
    if (bundle['city']!=base['city'] or bundle['base_revision_sha256']!=base['revision_sha256']
            or bundle['seed_id']!=seed['seed_id'] or bundle['source_outline_evaluation_id']!=base['source_outline_evaluation_id']):
        raise planning.PlanningError('Stale or incompatible priced planning base')
    plan=geometry.apply_edits(base,bundle['edits'],bundle['actor']);template=deepcopy(base['outline_context']['city_input_template'])
    by={l['line_id']:l for l in template['lines']};duties={l['line_id']:l for l in base['outline_context']['baseline_line_services']}
    if {l['id'] for l in plan['lines']}!=set(by):raise planning.PlanningError('Planning line identities differ')
    lines=[];segments=[];extra_walk=0.;maximum=0.;changed=0.;requests={};aliases={};active_raw=set()
    for current in plan['lines']:
        old=by[current['id']];new,walk,peak=_line_input(old,current,duties[current['id']]);lines.append(new)
        aliases.update(new['planning_access_aliases']);active_raw.update(s['id'] for s in new['stops'])
        extra_walk+=walk;maximum=max(maximum,peak)
        geometry_changed=current['coordinates']!=old['coordinates'] or current['shape']!=old['shape']
        if geometry_changed:changed+=new['route_m']
        scale=new['route_m']/old['route_m']
        for row in template.get('civil_segments',[]):
            if row['line_id']==current['id']:
                item=deepcopy(row);item.update(from_m=row['from_m']*scale,to_m=row['to_m']*scale)
                if geometry_changed:item.update(assumed=True,reassessment='Explicit proportional civil-class planning allocation; crossing/soil locations require reassessment')
                segments.append(item)
        requests[current['id']]=dict(headway_s=current['headway_s'],dwell_s=min(s['dwell_s'] for s in current['stops']))
    for interchange in template.get('interchanges',[]):
        prior=interchange.get('platforms',[])
        if any(x not in active_raw for x in prior):
            interchange['source_platform_ids']=deepcopy(prior)
            interchange['platforms']=[aliases.get(x,x) for x in prior]
            interchange['access_reassessment_required']=True
    parent_input_id=template.pop('input_id');template.update(lines=lines,civil_segments=segments,
        od=deepcopy(plan['od']),proposed_OD_reference_scope='Edited operational stop proposals; not surveyed or forecast demand',
        source_sha256=merge_sources(template['source_sha256'],_LOADED),
        ancestry=dict(parent_input_id=parent_input_id,revision_operator='priced-planning-edits',
            planning_revision_sha256=plan['revision_sha256'],seed_id=seed['seed_id']),**{k:False for k in city_flag_names()})
    if changed or extra_walk:
        hypothesis=deepcopy(template.get('alignment_hypothesis',{}));risk=hypothesis.setdefault('risk_quantities',{})
        risk['additional_access_walkway_m']=risk.get('additional_access_walkway_m',0.)+extra_walk
        risk['changed_route_m']=risk.get('changed_route_m',0.)+changed
        risk['additional_row_area_m2']=risk.get('additional_row_area_m2',0.)+changed*20.
        risk['unverified_bridge_route_m_hypothesis']=risk.get('unverified_bridge_route_m_hypothesis',0.)+changed*.05
        hypothesis.update(kind='edited-priced-planning-research',parent_input_id=parent_input_id,
            route_clearance_unknown=True,site_and_row_verified=False,
            revision_assumptions=dict(walking_detour_factor=1.25,new_ROW_width_m=20.,unverified_bridge_route_fraction=.05,
                civil_class_allocation='Existing class intervals rescaled as an explicit hypothesis; actual crossing locations not inherited'))
        template['alignment_hypothesis']=hypothesis
    template['input_id']=identity(template)
    rules=base['outline_context']['study_rules']
    maximum_allowed=rules.get('alignment',{}).get('maximum_added_walk_m',500.)
    result=dict(schema='osr-priced-planning-revision/1',plan=plan,city_input=template,
        requirements=deepcopy(rules),service_requests=requests,requested_design=deepcopy(base['outline_context'].get('requested_design')),
        base_revision_sha256=base['revision_sha256'],seed_id=seed['seed_id'],edit_bundle_id=identity(bundle),
        source_outline_evaluation_id=base['source_outline_evaluation_id'],official_source_outline_evaluation_id=seed['source_outline_evaluation_id'],
        research_configuration_parent_id=base['research_configuration_id'],
        access_screen=dict(status='pass' if maximum<=maximum_allowed else 'fail',maximum_added_walk_m=maximum,
            maximum_allowed_walk_m=maximum_allowed,additional_access_walkway_m=extra_walk,actual_walk_network_verified=False),
        planning_revision_id=planning.digest_json(dict(plan_revision=plan['revision_sha256'],seed_id=seed['seed_id'],edit_bundle=bundle)),
        source_sha256=deepcopy(template['source_sha256']),original_geography_modified=False,**FLAGS)
    result['evaluation_id']=identity(result);return result


def city_flag_names():
    return ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','selected_reference_changed','movement_authority')
