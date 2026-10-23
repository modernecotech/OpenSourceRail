"""Connected digital pilot delivery index; engineering failures stay visible."""
from hashlib import sha256
import importlib
import json
import os
from pathlib import Path

from . import model, pilot_limits

ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/pilot-delivery'
SCHEMA='osr-maglev-pilot-delivery/1'
COMPONENTS=(
    ('controlled-product','pilot_product','Counted equipment, allowance substitution, physical kit identities and bay access'),
    ('coupled-actuators','pilot_actuators','Voltage/current/force/beam/sensing dynamics and adverse cases'),
    ('launch-options','launch_optimisation','Independent energised sections, conductor and voltage lifetime-cost comparisons'),
    ('pilot-corridor','pilot_corridor','Baghdad pilot access, provisional demand, full-line service and funding'),
    ('candidate-finance','pilot_variants','Exact counted actuator alternative, actual powered sections, full-line energy and funding sensitivities'),
    ('resource-delivery','delivery_schedule','Resource-constrained1km erection, procurement and pooled factory accounting'),
    ('native-lifecycle','pilot_lifecycle','Serial-specific simulated receiving, inspection, repair, replacement and handback'),
    ('assurance-profiles','pilot_assurance','Separate executed engineering, delivery and formal control profiles'),
    ('capability-migration','capability_migration','Actual v0.4 capability dispositions and three-product boundary'),
)


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


def source_paths():
    return [Path(__file__),Path(pilot_limits.__file__),ROOT/'engineering/analysis/tests/test_ferrite_maglev_pilot_release.py']


def sources():
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}


def read_components():
    values=[]
    for identity,name,scope in COMPONENTS:
        module=importlib.import_module('.'+name,__package__)
        summary=module.read_summary()
        path=module.OUTPUT/'manifest.json'
        values.append(dict(id=identity,module=name,scope=scope,packet=module.OUTPUT.relative_to(ROOT).as_posix(),
                           manifest_sha256=sha256(path.read_bytes()).hexdigest(),digital_packet_verified=True,
                           summary=summary,engineering_accepted=False,physical_release=False))
    check_configurations(values)
    return values


def check_configurations(values):
    """A different exact product cannot enter this pilot through a passing file."""
    by_id={r['id']:r['summary'] for r in values}
    base=by_id['controlled-product']['configuration_sha256']
    for identity in ('pilot-corridor','native-lifecycle'):
        if by_id[identity]['configuration_sha256']!=base:
            raise ValueError('pilot child uses a different exact product configuration: '+identity)
    actuator=by_id['coupled-actuators']
    if actuator.get('base_configuration_sha256',actuator.get('configuration_sha256'))!=base:
        raise ValueError('actuator ancestry differs from controlled pilot product')
    recommended=by_id['launch-options'].get('research_recommendation')
    if recommended and recommended['configuration_sha256']!=base:
        raise ValueError('launch recommendation uses a different exact product')
    variant=by_id.get('candidate-finance')
    if variant:
        if variant['base_configuration_sha256']!=base:
            raise ValueError('candidate finance ancestry differs from controlled pilot product')
        if variant['configuration_sha256']!=actuator.get('qualified_configuration_sha256'):
            raise ValueError('candidate finance differs from exact executed actuator alternative')


def study():
    values=read_components();by_id={r['id']:r['summary'] for r in values}
    product=by_id['controlled-product']
    profiles=by_id['assurance-profiles']
    migration=by_id['capability-migration']
    mass_closed=product.get('mass_targets_closed',0)==product.get('configurations',2)
    actuator=by_id.get('coupled-actuators',{})
    candidate=next((r for r in actuator.get('repair_candidates',[])
                    if r['configuration_sha256']==actuator.get('qualified_configuration_sha256')), {})
    force=pilot_limits.actual_module_force(candidate)
    coupled_pass=(actuator.get('any_full_candidate_feasible',False)
                  and actuator.get('all_negative_controls_held') is True
                  and actuator.get('control_configuration_sha256')==actuator.get('qualified_configuration_sha256')
                  and actuator.get('qualified_configuration_sha256') is not None
                  and force['passed'])
    return dict(schema=SCHEMA,city='baghdad',components=values,source_sha256=sources(),
                qualification_progress=digital_progress(values),
                digital_packets_verified=len(values),digital_profiles_executed=profiles['all_profiles_executed'],
                mass_targets_closed=mass_closed,
                coupled_model_feasible=coupled_pass,
                coupled_actual_module_force=force,
                missing_legacy_capabilities=[r['id'] for r in migration['capabilities'] if r['state']=='missing'],
                development_deliverables=[
                    dict(id='migration-register',state='delivered',evidence=['capability-migration']),
                    dict(id='controlled-configuration',state='delivered-with-mass-hold' if not mass_closed else 'delivered',evidence=['controlled-product']),
                    dict(id='three-pilot-kits',state='provisional-definitions-delivered',evidence=['controlled-product','native-lifecycle']),
                    dict(id='coupled-actuator-and-launch-search',state='model-pass-provisional' if coupled_pass else 'model-infeasible',evidence=['coupled-actuators','launch-options']),
                    dict(id='baghdad-pilot-delivery-and-finance',state='provisional-pilot-delivered',evidence=['pilot-corridor','resource-delivery','candidate-finance']),
                    dict(id='lifecycle-and-assurance',state='executed-current' if profiles['all_profiles_executed'] else 'execution-hold',evidence=['native-lifecycle','assurance-profiles']),
                ],
                scope='Connected provisional digital pilot. Packet integrity, implemented design resolution, physical verification and independent acceptance are separate states.',
                physical_gate_state='open',manufacturing_gate_state='open',
                external_inputs=['qualified force/loss and material maps','measured mass/CG/inertia',
                                 'observed OD and boarding counts','surveyed land/utility/ground conditions',
                                 'supplier configurations and quotations','fire/accessibility/evacuation acceptance',
                                 'lender and authority decisions','independent physical first-article tests'], **model.FLAGS)


def digital_progress(values):
    """Attach scoped digital work without completing broader physical tasks."""
    from . import qualification
    current=qualification.study()
    groups={
        'controlled-product':['body-joints-hardpoints','magnetic-circuit'],
        'coupled-actuators':['magnetic-circuit','energy-services','control-protection'],
        'launch-options':['station-motor-interfaces','energy-services'],
        'pilot-corridor':['station-egress','energy-services','industrial-recovery-assurance'],
        'candidate-finance':['energy-services','industrial-recovery-assurance'],
        'resource-delivery':['civil-strength-stages','industrial-recovery-assurance'],
        'native-lifecycle':['industrial-recovery-assurance'],
        'assurance-profiles':['control-protection','industrial-recovery-assurance'],
        'capability-migration':['industrial-recovery-assurance'],
    }
    digital=[]
    for row in values:
        if not row.get('digital_packet_verified'):
            continue
        # Completing a packet's exact declared digital work is not completing
        # all design obligations in the broader qualification parent task.
        state='completed-digital-packet'
        if row['id']=='assurance-profiles' and not row['summary']['all_profiles_executed']:
            state='execution-hold'
        if row['id']=='native-lifecycle' and row['summary']['native']['state']!='executed-current':
            state='execution-hold'
        digital.append(dict(id='pilot/'+row['id'],state=state,scope=row['scope'],
                            parent_task_ids=['group/'+g+'/design' for g in groups[row['id']]],
                            manifest_sha256=row['manifest_sha256'],physical_acceptance=False))
    parent={}
    for row in digital:
        for identity in row['parent_task_ids']:
            parent.setdefault(identity,[]).append(row['id'])
    tasks=[dict(id=t['id'],digital_state='scoped-subtasks-available' if t['id'] in parent else t['digital_state'],
                digital_subtasks=parent.get(t['id'],[]),physical_state=t['physical_state'],accepted=False) for t in current['tasks']]
    return dict(qualification_binding_sha256=current['binding_sha256'],tasks=tasks,digital_subtasks=digital,
                completed_scoped_digital_subtasks=sum(r['state']=='completed-digital-packet' for r in digital),
                full_qualification_tasks_completed=0,physical_tasks_accepted=0,
                scope='Only each named packet scope is completed. Broader qualification tasks retain unexecuted physical evidence and independent review gates.')


def readme(value,output):
    def link(name):return Path(os.path.relpath(ROOT/name,output)).as_posix()
    lines=['# Baghdad connected digital pilot delivery','',value['scope'],'',
           f"Verified digital packets: **{value['digital_packets_verified']}**. All three development profiles executed against current sources: **{value['digital_profiles_executed']}**. Physical releases: **0**.",'',
           '| Deliverable | Digital state |', '|---|---|']
    lines += [f"| {r['id']} | {r['state']} |" for r in value['development_deliverables']]
    lines += ['','## Inspect the connected evidence','']
    lines += [f"- [{r['id']}]({link(r['packet']+'/README.md')}): {r['scope']}." for r in value['components']]
    progress=value['qualification_progress']
    lines += ['',f"Digital completion is recorded separately: {progress['completed_scoped_digital_subtasks']} scoped digital subtasks completed; {len(progress['tasks'])} broader qualification tasks tracked; {progress['full_qualification_tasks_completed']} full qualification tasks completed and 0 physical acceptances. The structured study links every subtask to its qualification parents and exact packet receipt.",'']
    force=value['coupled_actual_module_force']
    lines += [f"Actual module-force screen: {force['state']}; observed peak {force['observed_peak_n']}N against the declared {force['limit_n']:g}N study bound. A controller's requested-force clamp does not bound actual magnetic-force overshoot. This screen does not qualify the physical attachments.",'']
    lines += ['Retained rejected experiment: ['
              '120-turn coupled run and its exact sources]('+link('docs/design-engine/ferrite-maglev/pilot-actuators-rejected-120turn/README.md')+'). Its ['
              'matched failed-candidate financial sensitivity]('+link('docs/design-engine/ferrite-maglev/pilot-variant-failures/50faefb04c5f2872c05e342a0e1a65c1fbe56fc01b5b7392085f0b488c7ea999-failed/README.md')+') remains separately archived. A later candidate does not overwrite these failures.','']
    lines += ['','The component-accounted product is separate from historical14.2/14.4t tare targets. Defined equipment replaces the same scope allowance; target overruns, rejected assembly paths and unselected redesigns remain visible. Passing file integrity cannot close a failed design screen.','',
              'The counted steel/higher-copper actuator alternative has its own financial sensitivity. Its exact winding, cooling, mass and powered-section configuration are priced together. The lower-cost reference case and independent launch search cannot supply an economic advantage for a different executed candidate.','',
              'The pilot demand calculation is a declared open-data/proxy experiment, not an observed patronage forecast. Fare revenue, DSCR and funding gaps are sensitivities, not a funding commitment. The comparison-only steel-wheel option has its own quantity bill and does not replace the primary maglev architecture.','',
              'The native business campaign records simulation assets only. Receiving, inspection and handback in that campaign establish software workflow behavior; no hardware is accepted or authorised.','',
              'Missing v0.4 functions remain named: '+', '.join(value['missing_legacy_capabilities'])+'. They are not silently retired or marked restored.','',
              'External closure inputs: '+', '.join(value['external_inputs'])+'.','',
              'Reproduce: `./osr design pilot-delivery`. Heavy evidence: `./osr assurance run engineering`, `./osr assurance run delivery-lifecycle`, `./osr assurance run control-formal`.','']
    return '\n'.join(lines)


def publish(output=OUTPUT):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);value=study()
    files={'study.json':encoded(value),'README.md':readme(value,OUTPUT).encode()}
    for name,data in files.items():(output/name).write_bytes(data)
    result=dict(schema=SCHEMA,source_sha256=value['source_sha256'],files_sha256={n:sha256(d).hexdigest() for n,d in files.items()},**model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(result));return result


def verify(output=OUTPUT):
    output=Path(output);r=json.loads((output/'manifest.json').read_bytes())
    current=study()
    if (output.is_symlink() or r['schema']!=SCHEMA or any(r.get(k) is not False for k in model.FLAGS)
            or set(p.name for p in output.iterdir())!={'README.md','study.json','manifest.json'}
            or any(p.is_symlink() for p in output.iterdir())
            or r['files_sha256']!={n:sha256((output/n).read_bytes()).hexdigest() for n in ('README.md','study.json')}
            or r.get('source_sha256')!=sources()
            or json.loads((output/'study.json').read_bytes())!=current
            or (output/'README.md').read_text()!=readme(current,OUTPUT)):
        raise ValueError('stale or altered connected pilot evidence')
    return r


def read_summary(output=OUTPUT):
    verify(output)
    value=json.loads((Path(output)/'study.json').read_bytes())
    return {k:v for k,v in value.items() if k!='components'}
