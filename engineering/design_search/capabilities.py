"""Fail-closed architecture capability contracts; declarations are not validation.

Module presence, software tests, numerical convergence, measured correlation and
physical qualification are separate facts. This registry never promotes the
selected development configuration and never invents unknown stock or prices.
Evidence admission checks identity and provenance, not the authenticity of a
reviewer's signature; authenticated physical evidence remains the responsibility
of the existing qualification workflow. No function here issues an operating or
manufacturing release.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,re
from typing import Literal,TypedDict

Domain=Literal['body','runninggear','propulsion','secondary','guideway','station','HVAC','manufacturing']
DOMAINS=('body','runninggear','propulsion','secondary','guideway','station','HVAC','manufacturing')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False)
SCHEMA='osr-capability-composition/1'


class Capability(TypedDict):
    id:str
    domain:Domain
    physical_family_id:str
    interface_revision:str
    generator:dict
    necessary_screens:list[str]
    native_evaluator:dict|None
    independent_benchmarks:list[dict]
    manufacturing_representation:dict
    installation_representation:dict
    validity_domain:dict
    maturity:str
    evidence_ids:list[str]
    required_source_paths:list[str]


def identity(value):return sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()


def _sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def _cap(name,domain,physical,revision,generator,*,native=None,benchmarks=(),scope='definition only',representation='incomplete-known-stock',families=None):
    sources=[] if generator is None else [generator.split(':')[0].replace('.','/')+'.py']
    sources+={'wheel-body':['engineering/station_rail/vehicle.py','engineering/station_rail/body_frame.py',
            'engineering/station_rail/body_floor_fit.py','engineering/station_rail/body_solid_frame.py'],
        'wheel-motor':['engineering/station_rail/station_motor.py','engineering/station_rail/long_motor.py']}.get(native,[])
    return dict(id=name,domain=domain,physical_family_id=physical,interface_revision=revision,
        architecture_families=list(families or ('P1','P2','P3','P4','P5','P6','P7')),
        generator=dict(reference=generator,status='declared-source-adapter' if generator else 'not-implemented',validated=False,
            role='definition-or-known-stock-only'),required_source_paths=sources,
        necessary_screens={'body':['complete mass/CG/inertia','support/aperture load paths','crowd loads','all-axis stability and fire'],
          'runninggear':['wheel/rail loads','adhesion and independent braking','curve/derailment/swept clearance','recovery'],
          'propulsion':['finite thrust/normal forces','current/voltage/temperature','overlap/entry/exit','fault stopping and route energy'],
          'secondary':['material and mounting stock','primary gap and motion','normal-force load path','heating/retention'],
          'guideway':['moving loads and torsion','track alignment and braking reactions','foundations/site/access','installation'],
          'station':['safe berth/route protection','accessible boarding and egress','doors/platform interfaces','power/charging and protected headway'],
          'HVAC':['actual ambient capacity','air quality and redundancy','stationary thermal duty','complete installed power/mass'],
          'manufacturing':['same-candidate BOM/CAD','all hardware and processes','assembly/removal paths','inspection and sourcing']}[domain],
        native_evaluator=None if native is None else dict(id=native,scope=scope,status='implemented-research-only',validated=False),
        independent_benchmarks=[dict(id=b,required_independence=i) for b,i in benchmarks],
        manufacturing_representation=dict(status=representation,complete=False),
        installation_representation=dict(status='installation-interfaces-and-clearance-unqualified',complete=False),
        validity_domain=dict(scope=scope,physical_family_id=physical,parameter_extension_requires_review=True,
            old_results_reusable_without_new_request=False),maturity='concept',evidence_ids=[],
        complete_installed_mass_kg=None,complete_installed_price_USD=None,**FLAGS)


def catalogue():
    records=[
      _cap('body.v06-frame','body','counted-aluminium-box-frame/1','body-stock-loadport/1','engineering.design_search.wheel_body:materialize',
        native='wheel-body',benchmarks=(('body-independent-box-and-offset/1','independent-analytical'),('body-all-axis-refinement/1','same-model')),
        scope='Current counted frame family only; no new monocoque, joint or laminate qualification'),
      _cap('body.new-topology','body','new-structural-topology/1','body-stock-loadport/1','engineering.design_search.structural_families:generate',scope='Definition proposals; topology-specific native body adapter absent',representation='component-local-stock-only'),
      _cap('runninggear.passive','runninggear','passive-two-axle-bogie/1','wheel-support-brake-port/1','engineering.station_rail.vehicle:running_gear',families=('P1','P2','P3','P5','P7'),scope='Counted stock and reduced longitudinal bounds; full wheel-contact model absent'),
      _cap('runninggear.creep','runninggear','bogie-with-recovery-drive/1','wheel-support-brake-port/1',None,families=('P4',)),
      _cap('runninggear.traction','runninggear','powered-wheel-bogie/1','wheel-support-brake-port/1',None,families=('P6',)),
      _cap('secondary.al-fin','secondary','single-passive-aluminium-fin/1','linear-primary-secondary-port/1','engineering.design_search.wheel_motor:stock',families=('P1','P2','P3','P4','P5'),scope='Single counted passive fin and mounts; thermal/swept fit unqualified'),
      _cap('secondary.none-wheel-drive','secondary','wheel-contact-drive-no-linear-secondary/1','wheel-traction-interface/1',None,families=('P6',),scope='Explicit not-applicable linear secondary; wheel traction interface still required'),
      _cap('secondary.alternative','secondary','new-passive-secondary-topology/1','new-primary-secondary-port/1','engineering.design_search.propulsion_families:expanded_plan',families=('P7',),scope='Definition only; new material/fin/rack topology cannot reuse the single-fin solver'),
      _cap('guideway.rail-box','guideway','concrete-box-conventional-rail/1','rail-reaction-alignment-port/1','engineering.station_rail.civil:alternative',scope='Analytical longitudinal moving-load screens; complete civil/native/site model absent'),
      _cap('station.compact','station','centre-platform-fixed-line/1','station-boarding-protection-port/1','engineering.station_rail.operations:station_zone',scope='Finite-zone requirement bounds; complete station geometry/control qualification absent'),
      _cap('HVAC.modular','HVAC','modular-rail-HVAC/1','hotel-thermal-services-port/1','engineering.design_search.joining_catalogue:catalogue',scope='Supplier module leads only; actual50C duty/ducts/condensate/controls absent',representation='supplier-lead-no-installed-assembly'),
      _cap('manufacturing.known-stock','manufacturing','candidate-known-stock-twin/1','engineering-occurrence-bom-port/1','engineering.design_search.wheel_twin:compile',
        native='wheel-known-stock-export',benchmarks=(('native-stock-volumes-and-identities/1','independent-geometry'),),
        scope='Known stock export/reopen only; never full assembly or physical evidence'),
    ]
    family_data={
      'P1':('Current station LIM', 'Station launch/coast/receive; passive wheels and aluminium fin', 'current-reference-research-family'),
      'P2':('Lower-speed station LIM','Explicit speed/spacing/acceleration alternatives with new requirement identity','revised-service-hypothesis'),
      'P3':('Sparse wayside boosters','Station drive plus explicitly located intermediate motor/power/protection zones','new-route-power-architecture'),
      'P4':('Creep/recovery drive','Station launch with a separately sized onboard recovery drive and energy supply','new-onboard-recovery-interface'),
      'P5':('Distributed wayside propulsion','Additional wayside propulsion along route; count supply, sections and maintenance','new-distributed-power-architecture'),
      'P6':('Onboard wheel traction','Wheel traction with separately declared battery/conductor supply variants','new-powered-bogie-and-energy-architecture'),
      'P7':('Alternative passive secondary','Different fin/material/topology or passive reluctance; new field/circuit adapter required','new-electromagnetic-topology'),
    }
    for family in family_data:
        same=family in ('P1','P2','P3')
        records.append(_cap('propulsion.'+family,'propulsion',
            'single-fin-copper-double-sided-LIM/1' if same else 'propulsion-'+family+'/1',
            'linear-primary-secondary-port/1' if family not in ('P6','P7') else 'wheel-traction-interface/1' if family=='P6' else 'new-primary-secondary-port/1',
            'engineering.design_search.wheel_motor:definition' if same else 'engineering.design_search.propulsion_families:expanded_plan' if family=='P7' else None,
            native='wheel-motor' if same else None,
            benchmarks=(('LIM-independent-force-and-power/1','independent-domain'),('LIM-field-boundary-refinement/1','same-model')) if same else (),
            scope='Single-fin finite2D component only; no full route/branch/thermal/3D map' if same else 'Definition only; dedicated native architecture adapter absent',families=(family,)))
    caps={r['id']:r for r in records};families={}
    for family,(label,description,kind) in family_data.items():
        defaults=dict(body='body.v06-frame',runninggear='runninggear.creep' if family=='P4' else 'runninggear.traction' if family=='P6' else 'runninggear.passive',
            propulsion='propulsion.'+family,secondary='secondary.none-wheel-drive' if family=='P6' else 'secondary.alternative' if family=='P7' else 'secondary.al-fin',
            guideway='guideway.rail-box',station='station.compact',HVAC='HVAC.modular',manufacturing='manufacturing.known-stock')
        families[family]=dict(id=family,label=label,description=description,research_kind=kind,capabilities=defaults,
            interface_revisions={d:caps[c]['interface_revision'] for d,c in defaults.items()},
            requirement_change_required=family!='P1',default_changed=False,
            energy_variants=['battery','conductor-supply'] if family=='P6' else [],**FLAGS)
    value=dict(schema='osr-design-capability-registry/1',revision='ARCHITECTURE-CAPABILITIES-1',
        source_sha256={'engineering/design_search/capabilities.py':sha256(Path(__file__).read_bytes()).hexdigest()},
        domains=list(DOMAINS),capabilities=caps,families=families,
        constraints=dict(mandatory_safety=['structural-and-crowd-loads','independent-braking-and-parking','overspeed-localisation-integrity','fire-electrical-thermal','recovery-and-evacuation'],
            mandatory_accessibility=['wheelchair-places-and-routes','boarding-gap-and-step','door-clearance-and-egress'],
            mandatory_functional=['explicit-route-load-climate','passenger-admission-and-crowd-control','protected-receiving-and-fault-state'],
            preferences=['whole-life-affordability','simplicity-and-few-parts','local-manufacture-repair','open-design'],
            revisable_hypotheses=['speed-and-station-spacing','acceleration-and-dwell','headway-target','powered-zone-layout','formation-with-platform-fleet-effects','onboard-energy-preference-for-research-alternatives']),
        assembly_requirements=['complete occurrence geometry and installed BOM','joints/fasteners/bearings/wiring/cooling/protection','derived complete mass CG inertia','load/thermal/electrical/clearance interfaces','assembly tolerances tools inspections removal','supplier/origin/cost coverage and maintenance'],
        measurement_plans=dict(M1=dict(scope='Measured component, joint and brake correlation',required=['specimen/lot/geometry identities','instrument calibration and raw data','load/current/gap/temperature conditions','uncertainty and model correlation','independent review'],completion='unknown'),
            M2=dict(scope='Repeated one passive carriage launch/coast/safe stop/faults',required=['equipped mass and interfaces','repeated hot duty and braking','fault stopping/capture/recovery','model-versus-measurement correlation'],completion='unknown'),
            M3=dict(scope='Full-sized station-to-station pilot and recovery',required=['protected route and accessible stations','formation and operating/fault scenarios','evacuation and recovery','independent qualification disposition'],completion='unknown')),
        maturity_levels=['concept','analytical','numerically_converged','cross_solver_confirmed','prototype_correlated','physically_qualified','manufacturing_released'],
        selected_development_default='engineering/development-baseline.toml',
        selected_development_default_changed=False,unknown_is_zero=False,**FLAGS)
    value['registry_id']=identity(value);return value


def composition(family_id,candidate_id,requirement_revision,*,capabilities=None,component_definition_ids=None):
    data=catalogue();family=data['families'].get(family_id)
    if family is None:raise ValueError('Registered research architecture family required')
    chosen=deepcopy(family['capabilities']);chosen.update(capabilities or {})
    value=dict(schema=SCHEMA,candidate_id=candidate_id,requirement_revision=requirement_revision,family_id=family_id,
        capabilities=chosen,interface_revisions={d:data['capabilities'][c]['interface_revision'] for d,c in chosen.items() if c in data['capabilities']},
        component_definition_ids=deepcopy(component_definition_ids or {}),**FLAGS)
    return validate_composition(value)


def validate_composition(value):
    data=catalogue()
    if value.get('schema')!=SCHEMA or not _sha(value.get('candidate_id')) or not isinstance(value.get('requirement_revision'),str) or not value['requirement_revision']:raise ValueError('Physical candidate identity and separate requirement revision required')
    if value.get('family_id') not in data['families']:raise ValueError('Registered architecture family required')
    if any(n in value for n in ('evaluation_id','selection_id','solver_settings')):raise ValueError('Evaluation/selection identity belongs outside physical composition')
    if any(value.get(n) is not False for n in FLAGS):raise ValueError('Composition cannot assert release')
    if set(value.get('capabilities',{}))!=set(DOMAINS) or set(value.get('interface_revisions',{}))!=set(DOMAINS):raise ValueError('Every required design domain must be explicit')
    for domain,name in value['capabilities'].items():
        r=data['capabilities'].get(name)
        if r is None or r['domain']!=domain or value['family_id'] not in r['architecture_families']:raise ValueError('Capability domain/architecture mismatch: '+domain)
        if value['interface_revisions'][domain]!=r['interface_revision']:raise ValueError('Interface revision mismatch: '+domain)
    if value['interface_revisions']['propulsion']!=value['interface_revisions']['secondary']:raise ValueError('Primary/secondary topology interface mismatch')
    definitions=value.get('component_definition_ids',{})
    if set(definitions)-set(DOMAINS) or any(not _sha(v) for v in definitions.values()):raise ValueError('Component physical definition IDs required when declared')
    json.dumps(value,allow_nan=False);return deepcopy(value)


def _admissible_evidence(row,capability,composition,current_sources):
    if not isinstance(row,dict) or not _sha(row.get('evidence_id')):return False
    if row['evidence_id']!=identity({n:v for n,v in row.items() if n!='evidence_id'}):return False
    definition_id=composition.get('component_definition_ids',{}).get(capability['domain'])
    if not _sha(definition_id):return False
    required=dict(candidate_id=composition['candidate_id'],component_definition_id=definition_id,
        capability_id=capability['id'],interface_revision=capability['interface_revision'],physical_family_id=capability['physical_family_id'],
        evaluator_id=capability['native_evaluator']['id'],
        evidence_kind='numerical-benchmark',execution='completed',numerical_validity='converged',screen_status='pass',review_disposition='accepted-for-declared-model-domain')
    if any(row.get(n)!=v for n,v in required.items()):return False
    domain=row.get('validation_domain')
    if not isinstance(domain,dict) or domain.get('physical_family_id')!=capability['physical_family_id'] or not domain.get('limits'):return False
    if not _sha(row.get('review_record_id')) or not _sha(row.get('artifact_id')) or any(row.get(n) is not False for n in FLAGS):return False
    sources=row.get('source_sha256')
    return (isinstance(sources,dict) and set(capability['required_source_paths'])<=set(sources)
        and all(_sha(h) and current_sources.get(n)==h for n,h in sources.items()))


def eligible_evaluators(value,evidence=(),*,current_source_sha256=None):
    """Return only source-bound, reviewed numerical capabilities for this stock.

    An empty result does not forbid a declared unvalidated research experiment;
    it forbids presenting that experiment as using an already validated model.
    Exact operating limits still belong to each evaluation request. Numerical
    benchmark evidence never authorises physical operation.
    """
    value=validate_composition(value);data=catalogue();sources=current_source_sha256 or {};eligible=[]
    for domain,name in value['capabilities'].items():
        cap=data['capabilities'][name]
        if cap['native_evaluator'] is None:continue
        valid=[r for r in evidence if _admissible_evidence(r,cap,value,sources)]
        matched=[];domains=[]
        for benchmark in cap['independent_benchmarks']:
            found=[r for r in valid if r.get('benchmark_id')==benchmark['id'] and r.get('independence')==benchmark['required_independence']]
            if not found:break
            matched.extend(r['evidence_id'] for r in found)
            domains.extend(dict(benchmark_id=r['benchmark_id'],validation_domain=r['validation_domain']) for r in found)
        else:
            if cap['independent_benchmarks']:eligible.append(dict(domain=domain,capability_id=name,evaluator_id=cap['native_evaluator']['id'],evidence_ids=matched,
                validation_scope=cap['validity_domain'],validated_domains=domains,
                request_domain_check_required=True,automatic_dispatch_eligible=False,
                execution_purpose='numerical-research-only',**FLAGS))
    return eligible


def admission_check(value,*,evidence=(),current_source_sha256=None,constraint_states=None,assembly_states=None,measurement_plans=None,purpose='next-experiment'):
    value=validate_composition(value);data=catalogue();constraints=constraint_states or {};assembly=assembly_states or {};plans=measurement_plans or {};holds=[]
    if purpose not in ('next-experiment','native-research','integrated-review'):raise ValueError('Explicit research/review purpose required')
    mandatory=sum((data['constraints'][n] for n in ('mandatory_safety','mandatory_accessibility','mandatory_functional')),[])
    for name in mandatory:
        state=constraints.get(name,'unknown')
        if state not in ('pass','fail','unknown','not-assessed'):raise ValueError('Typed constraint state required')
        if state!='pass':holds.append(dict(kind='mandatory-constraint',id=name,state=state))
    for name in data['assembly_requirements']:
        if assembly.get(name)!='complete':holds.append(dict(kind='assembly-evidence',id=name,state='unknown'))
    for name in ('M1','M2','M3'):
        plan=plans.get(name)
        if not isinstance(plan,dict) or not plan.get('plan_id') or plan.get('scope')!=data['measurement_plans'][name]['scope'] or not set(data['measurement_plans'][name]['required'])<=set(plan.get('required',[])):
            holds.append(dict(kind='measurement-plan',id=name,state='unknown'))
    eligible=eligible_evaluators(value,evidence,current_source_sha256=current_source_sha256)
    readiness='definition-research-only'
    if purpose=='native-research':
        readiness='native-research-eligible' if eligible else 'held-no-validated-native-capability'
    elif purpose=='integrated-review':
        # A plan and a declaration of complete bookkeeping are not measurements.
        # This registry has no authenticated measurement/qualification importer.
        holds.extend(dict(kind='physical-measurement-evidence',id=name,state='unknown') for name in ('M1','M2','M3'))
        holds.extend(dict(kind='complete-installed-quantity',id=name,state='unknown') for name in ('mass-CG-inertia','whole-life-price'))
        eligible_domains={r['domain'] for r in eligible}
        holds.extend(dict(kind='validated-domain-model',id=d,state='unknown') for d in DOMAINS if d not in eligible_domains)
        readiness='held-for-evidence'
    result=dict(schema='osr-capability-admission/1',candidate_id=value['candidate_id'],requirement_revision=value['requirement_revision'],family_id=value['family_id'],purpose=purpose,
        registry_id=data['registry_id'],composition_check_id=identity(value),readiness=readiness,holds=holds,eligible_evaluators=eligible,
        measurement_plan_is_measurement=False,measurement_evidence_accepted=False,complete_installed_mass_kg=None,complete_installed_price_USD=None,
        selected_development_default_changed=False,**FLAGS)
    result['admission_id']=identity(result);return result
