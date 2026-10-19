"""WP00/01 compatibility contracts on the existing assembly geometry authority.

These definitions freeze a reproducible *provisional* prototype, not an adopted
railway requirement. Unknown supplier/licensed/site inputs remain typed holds.
"""
from copy import deepcopy
from datetime import date
from hashlib import sha256
import math
import re
import tomllib

from engineering.twin_workflow import core
from engineering.assembly_design import baseline
from engineering.design_consistency import contracts as geometry

ARCHITECTURE = 'baghdad-six-car'
OUTPUTS = ('cad', 'analysis', 'harness', 'schedule', 'cost', 'tests', 'qa')
INTERFACE_TYPES = {'structural-mount', 'bearing', 'electrical-connector', 'fluid-port', 'air-port', 'software-signal'}
DOFS = {'tx', 'ty', 'tz', 'rx', 'ry', 'rz'}
UNITS = {'m', 'mm', 'kg', 'kg/m3', 'kg*m2', 'N', 'N*m', 'Pa', 'MPa', 'K', 'degC', 'V', 'A', 'W', 'kWh', 'm3/s', 's', 'Hz', 'bool', 'count', 'm/s', 'ohm'}


def finite(value):
    """Reject nonfinite numbers recursively before hashing or solver dispatch."""
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('nonfinite contract value')
    if isinstance(value, dict):
        for item in value.values(): finite(item)
    if isinstance(value, (list, tuple)):
        for item in value: finite(item)
    return value


def _identity(value):
    if not isinstance(value, str) or not value.strip(): raise ValueError('nonempty identity required')
    return value


def _hash(value, *, nullable=False):
    if nullable and value is None: return
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('SHA256 required')


def quantity(value, unit, *, status='provisional', uncertainty=None):
    if unit not in UNITS: raise ValueError('unsupported explicit unit')
    finite(value); finite(uncertainty)
    return dict(value=value, unit=unit, status=status, uncertainty=uncertainty)


def prototype_configuration():
    """Freeze existing metro-6car planning data; do not borrow LM3 floor geometry."""
    paths = ['lib/templates/rolling-stock.toml', 'lib/templates/track-geometry.toml',
             'engineering/data/baghdad-reference-parts.json',
             'design/component-catalogue/src/osr_mech/rolling_stock/trainset.py',
             'engineering/assembly_design/data/baseline.json']
    profile = tomllib.loads((core.ROOT / paths[0]).read_text())['profiles']['metro-6car']
    track = tomllib.loads((core.ROOT / paths[1]).read_text())['presets']['standard-metro']
    facts = baseline.facts(core.read(baseline.DATA))
    values = dict(car_count=quantity(profile['cars'], 'count'),
        length=quantity(profile['length_m'], 'm'), car_length=quantity(profile['length_m']/profile['cars'], 'm'),
        nominal_passengers=quantity(profile['passenger_capacity'], 'count'), seats=quantity(profile['seat_count'], 'count'),
        crush_passengers=quantity(profile['crush_capacity'], 'count'), tare_mass=quantity(profile['tare_mass_t']*1000, 'kg'),
        gauge=quantity(track['gauge_mm'], 'mm'), speed_ceiling=quantity(profile['max_speed_mps'], 'm/s'),
        ambient=quantity(profile['hvac_design_ambient_c'], 'degC'),
        battery_nameplate=quantity(profile['onboard_battery_nameplate_kwh'], 'kWh'),
        battery_usable_allocation=quantity(profile['onboard_battery_kwh'], 'kWh'))
    value = dict(schema='osr-prototype-configuration/1', id='BAGHDAD-PROTOTYPE-6C-2026-10-19',
        architecture=ARCHITECTURE, family='metro-6car', status='frozen-provisional-software-baseline',
        values=values, bogie_arrangement=dict(powered_per_car=1, trailer_per_car=1, supplier_configuration=None),
        battery_chemistry=profile['battery_chemistry'],
        low_floor_layout=dict(value=None, state='hold', reason='No adopted six-car floor/door map; LM3 350/760 mm arrangement not transferred'),
        door_layout=dict(value=None, state='hold', reason='Six-car door positions, clear openings and platform match require definition'),
        charging=dict(concept='station/depot charging candidates', selected_configuration=None,
                      state='hold', reason='No adopted charger/concurrency/duty/thermal map'),
        route=dict(value=None, state='hold', reason='Surveyed route, gradient/speed histories and platform positions required'),
        emergency_states=['loss-of-traction', 'loss-of-cooling', 'fire-isolation', 'rescue-tow', 'loss-of-auxiliary-supply'],
        emergency_acceptance=dict(state='hold', criteria=None),
        sensitivities=dict(gross_mass_cases=quantity(facts['train.mass_cases'], 'kg'), roof_hot_case=quantity(85, 'degC')),
        conflicts=['Gross-mass planning cases are not reconciled to profile tare/passenger/axle maps; not interchangeable load definitions'],
        source_sha256={p: core.sha(core.ROOT/p) for p in paths}, **core.FLAGS)
    value['revision'] = core.digest(value)
    return value


FAMILIES = [
    ('interface', r'interface|\bICD\b|coupl|articulation', 'connection'),
    ('bearing-running-gear', r'bogie|wheelset|axle|wheel profile|suspension|brake', 'purchased-subsystem'),
    ('civil-primary', r'foundation|pile|pier|girder|precast|beam|cap|reinforcement', 'manufactured-structure'),
    ('structural-bay', r'underframe|load-bearing|carbody|car body|bolster|spine|door portal|roof structure|body structure', 'manufactured-structure'),
    ('panel-system', r'FRP|fiberglass|laminate|cladding|glazing|window|composite|coating', 'material-system'),
    ('thermal-fluid', r'HVAC|coolant|cooling|duct|filter|condensate|compressor|air supply|ventilation', 'service-module'),
    ('energy-power', r'battery|charger|charging|inverter|traction|motor|MPPT|\bPV\b|DC/DC|power conversion', 'purchased-subsystem'),
    ('electrical-harness', r'harness|connector|cable|wiring|earthing|grounding|bond|fuse|surge|terminal|distribution', 'service-module'),
    ('control-software', r'host|MCU|compute|network|sensor|radar|lidar|camera|controller|watchdog|radio|server|permission|SPI|CAN|\bI/O\b', 'control-subsystem'),
    ('track-system', r'rail|track|turnout|clip|fasten|plinth|slab|frog|points', 'track-module'),
    ('station-access', r'station|platform|stair|ramp|lift|canopy|ticket|gate|walkway|barrier|fenc', 'civil-module'),
    ('assembly-hardware', r'bolt|nut|washer|fastener|bracket|clamp|fixture|mount|lock|retention|seal', 'connection'),
    ('manufacturing-equipment', r'machine|tool|jig|mould|weld|cnc|press|lathe|laser|saw|bench|factory|crane', 'production-equipment'),
    ('passenger-fitout', r'door|seat|interior|lighting|grab|floor|PRM|fire|alarm|suppression', 'vehicle-module'),
]


def crosswalk(inventory=None):
    """Group source records by reusable function, retaining every source identity.

    Repeated catalogue IDs are duplicate *records*, never proven interchangeable
    hardware; family alternatives require explicit engineering applicability.
    """
    inventory = inventory or baseline.inventory(core.read(baseline.DATA))
    rows=[]; groups={}; duplicate_groups={}
    for item in inventory['items']:
        title=item['title']; catalogue=item['catalogue_id']
        family, kind = next(((name, kind) for name, pattern, kind in FAMILIES if re.search(pattern, title, re.I)), ('unclassified', 'unresolved-record'))
        if '-LC-' in catalogue or 'load case' in title.lower(): kind='requirement'
        elif '-ICD-' in catalogue: kind='interface'
        elif '-SA' in catalogue or 'complete ' in title.lower() or 'assembly' in title.lower(): kind='assembly'
        elif catalogue.startswith('OSR-TYPE-'): kind='alternative-type'
        group=item['architecture']+'/'+family
        row=dict(source_id=item['id'], catalogue_id=catalogue, title=title,
                 architecture=item['architecture'], family=family, record_type=kind,
                 source=item['source'], source_sha256=item['source_sha256'],
                 family_id=group, classification='provisional-rule-based; engineering reconciliation required',
                 alternative_group=group if kind=='alternative-type' else None)
        rows.append(row); groups.setdefault(group, []).append(item['id'])
        duplicate_groups.setdefault((item['architecture'], catalogue), []).append(item['id'])
    if len({r['source_id'] for r in rows}) != len(rows): raise ValueError('duplicate authoritative identity')
    duplicates=[dict(architecture=a,catalogue_id=c,source_ids=ids,status='duplicate-record-review; no quantity consolidation')
                for (a,c),ids in sorted(duplicate_groups.items()) if len(ids)>1]
    return dict(schema='osr-requirement-family-crosswalk/1', items=rows,
        families=[dict(id=k,source_ids=v,generator_status='allocation-only; evaluator qualification required') for k,v in sorted(groups.items())],
        duplicate_records=duplicates, source_record_count=len(rows), physical_part_count=None, **core.FLAGS)


def source_card(*, identity, publisher, exact_part, revision, url, locator, unit,
                retrieved, operating_envelope, uncertainty, document=None,
                document_sha256=None, licence='copyright; public metadata reference only',
                applicability=ARCHITECTURE, valid_until=None):
    if document is not None: document_sha256=sha256(document).hexdigest()
    value=dict(schema='osr-source-card/1', id=identity,publisher=publisher,exact_part=exact_part,
               revision=revision,url=url,document_sha256=document_sha256,locator=locator,
               unit=unit,licence=licence,retrieved=retrieved,valid_until=valid_until,
               operating_envelope=operating_envelope,uncertainty=uncertainty,applicability=applicability,
               evidence_state='hash-bound-reference' if document_sha256 else 'hold-document-not-retained',approved=False)
    validate_source(value)
    return value


def validate_source(card, *, architecture=ARCHITECTURE, observed_sha256=None, on_date=None):
    finite(card)
    for key in ('id','publisher','exact_part','revision','url','locator','unit','licence','retrieved','applicability'):
        _identity(card.get(key))
    if card['applicability'] not in (architecture,'reference-only'): raise ValueError('source architecture mismatch')
    if not card['url'].startswith(('https://','http://','repo:')): raise ValueError('explicit source URL required')
    if card.get('approved') is not False: raise ValueError('source metadata does not approve engineering use')
    _hash(card.get('document_sha256'), nullable=True)
    retrieved=date.fromisoformat(card['retrieved']); today=date.fromisoformat(on_date) if on_date else date.today()
    if retrieved>today: raise ValueError('future source retrieval')
    if card.get('valid_until') and date.fromisoformat(card['valid_until'])<today: raise ValueError('stale supplier source validity')
    if observed_sha256 is not None:
        _hash(observed_sha256)
        if observed_sha256!=card.get('document_sha256'): raise ValueError('stale supplier source revision/hash')
    if 'operating_envelope' not in card or 'uncertainty' not in card: raise ValueError('source applicability/uncertainty required')
    return card


def baseline_source_cards(policy=None):
    """Upgrade existing source entries without inventing retained document hashes.

    The 21 facts retain their own maxima/context applicability statements. These
    cards intentionally hold until exact document bytes/revisions are retained.
    """
    policy=policy or core.read(baseline.DATA)
    publishers={'british-steel':'British Steel','ekspan':'EKSPAN','freyssinet':'Freyssinet',
        'harwin-power':'Harwin','iraq-climate':'Iraq / UNFCCC','sci-bolts':'Steel Construction Institute',
        'software-standard':'BSI','vehicle-standard':'BSI'}
    result=[]
    for identity,source in sorted(policy['sources'].items()):
        facts=[dict(id=f['id'],value=f['value'],unit=f['unit'],applicability=f['applicability'],
                    status=f['status'],locator=f['locator']) for f in policy['facts'] if f['source']==identity]
        exact='M80-4000000F1-10-326-00-000' if identity=='harwin-power' else source['locator']
        result.append(source_card(identity=identity,publisher=publishers.get(identity,identity),
            exact_part=exact,revision='unconfirmed-document-revision',url=source['url'],locator=source['locator'],
            unit='mixed; each fact carries its unit',retrieved=source['retrieved'],
            operating_envelope=dict(scope=source['scope'],facts=facts),
            uncertainty='Published reference or family limit; derating, combined envelope and exact offered configuration not established',
            applicability='reference-only'))
    return result


def standards_register():
    """Official catalogue metadata only; normative texts/licensed adoption remain open."""
    return dict(schema='osr-standards-register/1', entries=[
        dict(id='IEC61373', edition='2026 edition 3.0', publication_date='2026-07-17',
             url='https://webstore.iec.ch/en/publication/68999', replaces='2010 edition 2.0',
             scope='Rolling-stock attached equipment shock/vibration; main vehicle structure and fixing bolts not evaluated',
             impact_review=['mounting category and operating environment', 'updated functional spectra and long-life acceleration method',
                            'fixture qualification and sequence', 'traction-motor/mechanical-only substructure exclusions',
                            'review old receipts before reuse; no automatic edition migration'],
             affected=['analysis','tests','qa','supplier-qualification']),
        dict(id='IEC62928', edition='2017 edition 1.0', publication_date='2017-12-07',
             url='https://webstore.iec.ch/en/publication/31101',
             scope='Onboard lithium-ion traction battery design, operation and tests',
             chemistry='lithium-ion', affected=['battery-duty','electrothermal','tests','qa']),
    ], licensed_text_available=False, jurisdiction='Iraq; project adoption not established',
        adopted=False, equipment_category=None, review_state='hold-licensed-text-category-and-authority',
        retrieved='2026-10-19', **core.FLAGS)


def standard_applicability(identity, *, chemistry=None, equipment_category=None, prior_edition=None):
    register=standards_register(); entry=next((r for r in register['entries'] if r['id']==identity),None)
    if entry is None: raise ValueError('unregistered standard')
    reason=[]
    if identity=='IEC62928' and chemistry not in {'lfp','nmc','nca','lto','lithium-ion'}:
        reason.append('chemistry not demonstrated within lithium-ion traction scope; explicit alternative test strategy required')
    if equipment_category is None: reason.append('equipment/mounting category not adopted')
    if identity=='IEC61373' and prior_edition and prior_edition!='2026':
        reason.append('2026 edition impact review required; old results not automatically reusable')
    reason.append('licensed normative text and project adoption required')
    return dict(state='hold',standard=entry,reasons=reason,applicable_approved=False)


def interface(identity, kind, endpoints, *, architecture=ARCHITECTURE, freedoms=(),
              quantities=None, tolerances=None, source_ids=(), uncertainty=None):
    value=dict(schema='osr-interface/1', id=identity,kind=kind,architecture=architecture,
               endpoints=list(endpoints),degrees_of_freedom=list(freedoms),quantities=quantities or {},
               tolerances=tolerances or {},source_ids=list(source_ids),uncertainty=uncertainty,
               invalidates=list(OUTPUTS),acceptance_state='open',**core.FLAGS)
    value['revision']=core.digest(value); validate_interface(value,architecture=architecture)
    return value


def validate_interface(value, *, architecture=ARCHITECTURE, component_ids=None):
    finite(value)
    if value.get('schema')!='osr-interface/1' or value.get('architecture')!=architecture: raise ValueError('interface architecture/schema mismatch')
    _identity(value.get('id'))
    if value.get('kind') not in INTERFACE_TYPES: raise ValueError('unknown interface type')
    endpoints=value.get('endpoints',[])
    if len(endpoints)!=2 or len(set(endpoints))!=2: raise ValueError('two distinct interface endpoints required')
    for endpoint in endpoints: _identity(endpoint)
    if component_ids is not None and not set(endpoints)<=set(component_ids): raise ValueError('missing interface endpoint')
    if not set(value.get('degrees_of_freedom',[]))<=DOFS: raise ValueError('unknown interface degree of freedom')
    for group in ('quantities','tolerances'):
        for q in value.get(group,{}).values():
            if q.get('unit') not in UNITS or 'value' not in q: raise ValueError('typed interface quantity required')
    copy=deepcopy(value); revision=copy.pop('revision',None)
    if revision!=core.digest(copy): raise ValueError('stale interface revision')
    if any(value.get(k) is not False for k in core.FLAGS): raise ValueError('provisional interface release forbidden')
    return value


def material_bundle(identity, *, material, process, density_kg_m3, properties=None, source_ids=(), operating_envelope=None):
    value=dict(id=identity,material=material,process=process,density=quantity(density_kg_m3,'kg/m3'),
        properties=properties or {},source_ids=list(source_ids),operating_envelope=operating_envelope,
        allowables_state='reference-only; batch/process/environment qualification open',qualified=False)
    value['revision']=core.digest(value); return validate_material(value)


def validate_material(value):
    finite(value)
    for key in ('id','material','process'): _identity(value.get(key))
    if value['density']['unit']!='kg/m3' or type(value['density']['value']) not in (int,float) or value['density']['value']<=0:
        raise ValueError('positive material density required')
    if value.get('qualified') is not False: raise ValueError('material qualification needs external authority')
    for q in value['properties'].values():
        if q.get('unit') not in UNITS: raise ValueError('typed material property required')
    copy=deepcopy(value); revision=copy.pop('revision',None)
    if revision!=core.digest(copy): raise ValueError('stale material bundle')
    return value


def component_bundle(contract, *, architecture=ARCHITECTURE, ownership, interfaces, material_bundles,
                     required_interfaces=(), source_cards=()):
    """Compatibility wrapper; existing editable geometry remains sole authority."""
    value=dict(schema='osr-component-contract/1',architecture=architecture,geometry=deepcopy(contract),
        ownership=deepcopy(ownership),interfaces=deepcopy(interfaces),material_bundles=deepcopy(material_bundles),
        required_interfaces=list(required_interfaces),source_cards=deepcopy(source_cards),**core.FLAGS)
    value['revision']=core.digest(value); return validate_component(value,architecture=architecture)


def validate_component(value, *, architecture=ARCHITECTURE):
    finite(value)
    if value['architecture']!=architecture: raise ValueError('component architecture mismatch (LM3/Baghdad cannot mix)')
    geometry.validate(value['geometry']); ids={r['id'] for r in value['geometry']['parts']}
    if set(value['ownership'])!=ids or any(o not in {'owned','purchased','provisional-envelope'} for o in value['ownership'].values()):
        raise ValueError('every represented part requires owned/purchased scope')
    interface_ids=set()
    for row in value['interfaces']:
        validate_interface(row,architecture=architecture)
        if row['id'] in interface_ids: raise ValueError('duplicate interface')
        interface_ids.add(row['id'])
        # External endpoints must be explicit, rather than absent silently.
        if not any(e in ids for e in row['endpoints']): raise ValueError('interface has no owned assembly endpoint')
        if any(e not in ids and not e.startswith('external:') for e in row['endpoints']): raise ValueError('missing interface endpoint; external endpoint must be declared external:')
    if not set(value['required_interfaces'])<=interface_ids: raise ValueError('missing mandatory interface')
    materials={row['id']:validate_material(row) for row in value['material_bundles']}
    if len(materials)!=len(value['material_bundles']) or not set(value['geometry']['materials'])<=set(materials): raise ValueError('missing/duplicate typed material bundle')
    for identity,material in value['geometry']['materials'].items():
        if not math.isclose(materials[identity]['density']['value'],material['density_kg_m3'],rel_tol=1e-12): raise ValueError('material/geometry density mismatch')
    for part in value['geometry']['parts']:
        if part.get('geometric_role')=='supplier-coordination-envelope' and value['ownership'][part['id']]=='owned':
            raise ValueError('supplier envelope cannot be declared owned manufactured solid')
    source_ids=set()
    for row in value['source_cards']:
        validate_source(row,architecture=architecture)
        if row['id'] in source_ids: raise ValueError('duplicate source card')
        source_ids.add(row['id'])
    if any(not set(row.get('source_ids',[]))<=source_ids for row in [*value['interfaces'],*value['material_bundles']]):
        raise ValueError('unbound interface/material source card')
    copy=deepcopy(value); revision=copy.pop('revision',None)
    if revision!=core.digest(copy): raise ValueError('stale component revision')
    if any(value.get(k) is not False for k in core.FLAGS): raise ValueError('provisional component release forbidden')
    return value


def dependency_manifest(inputs, dependencies=None):
    """Bind every derived representation to all mount/connector/material revisions.

    Caller can add precise edges, but the default deliberately invalidates every
    representation when a critical interface/material changes.
    """
    finite(inputs)
    revisions={key:core.digest(value) for key,value in sorted(inputs.items())}
    dependencies=deepcopy(dependencies) if dependencies is not None else {kind:sorted(revisions) for kind in OUTPUTS}
    graph={**{key:[] for key in revisions},**dependencies}
    if set(revisions)&set(dependencies): raise ValueError('input/output identities overlap')
    visited=set(); visiting=set()
    def visit(node):
        if node not in graph: raise ValueError('missing dependency '+node)
        if node in visiting: raise ValueError('cyclic representation dependency')
        if node in visited: return
        visiting.add(node)
        for parent in graph[node]: visit(parent)
        visiting.remove(node);visited.add(node)
    for node in graph: visit(node)
    return dict(schema='osr-revision-dependencies/1',inputs=revisions,dependencies=dependencies,
                revision=core.digest(dict(inputs=revisions,dependencies=dependencies)))


def invalidation_plan(previous, current):
    changed={key for key in previous['inputs'].keys()|current['inputs'].keys() if previous['inputs'].get(key)!=current['inputs'].get(key)}
    impacted=set(changed)
    for key in previous['dependencies'].keys()|current['dependencies'].keys():
        if previous['dependencies'].get(key)!=current['dependencies'].get(key): impacted.add(key)
    while True:
        added={key for key,deps in current['dependencies'].items() if set(deps)&impacted}
        if added<=impacted: break
        impacted|=added
    return dict(changed_inputs=sorted(changed),invalidated=sorted(impacted&current['dependencies'].keys()),
                removed_outputs=sorted(previous['dependencies'].keys()-current['dependencies'].keys()),
                previous_revision=previous['revision'],current_revision=current['revision'],acceptance_state='re-evaluation-required')


def regenerate(previous, current, builders, *, retained=None):
    """Execute affected adapter callbacks in DAG order; tests/QA request new checks.

    A callback success means regeneration only. No callback may confer acceptance.
    """
    plan=invalidation_plan(previous,current); pending=set(plan['invalidated']); outputs=deepcopy(retained or {})
    records=[]
    while pending:
        ready=sorted(key for key in pending if not (set(current['dependencies'][key])&pending))
        if not ready: raise ValueError('cyclic regeneration graph')
        for key in ready:
            if key not in builders: raise ValueError('missing representation adapter: '+key)
            result=builders[key](dict(input_revisions=current['inputs'],artifacts=deepcopy(outputs)))
            finite(result); outputs[key]=result
            records.append(dict(representation=key,artifact_sha256=core.digest(result),
                context_revision=current['revision'],state='regenerated; verification pending',accepted=False))
            pending.remove(key)
    return dict(plan=plan,artifacts=outputs,receipts=records,**core.FLAGS)
