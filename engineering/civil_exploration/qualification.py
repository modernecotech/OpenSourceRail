"""Baghdad input readiness without inventing a six-car moving-load pattern."""
from __future__ import annotations
import math
from pathlib import Path
import tomllib

from .contracts import ROOT,HERE,load,encoded,sha,validate,validate_study

LOAD_MODEL='docs/civil/viaduct-load-model.toml'
ROLLING_STOCK='lib/templates/rolling-stock.toml'


def controlled(path):
    path=Path(path).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError('qualification source must be a retained repository file')
    return path


def build(train_record=None):
    target=load(HERE/'config/qualification-target.json')
    validate(target,load(HERE/'schemas/qualification-target.json'))
    if target['deployment']!='baghdad' or target['train_family']!='metro-6car':
        raise ValueError('qualification target does not describe Baghdad six-car stock')
    city=ROOT/target['city_path']
    paths=[ROOT/LOAD_MODEL,ROOT/ROLLING_STOCK,city/'design.toml',city/'engineering/soil/summary.json',
           city/'engineering/survey/structural-release-readiness.json',city/'engineering/survey/surveyed-alignment-readiness.json',
           HERE/'config/qualification-target.json']
    paths += [HERE/'qualification.py',ROOT/'tools/automation/civil-study.py',
              HERE/'schemas/supplier-train.json',HERE/'schemas/qualification-target.json']
    sources={p.relative_to(ROOT).as_posix():sha(controlled(p)) for p in paths}
    loads=tomllib.loads((ROOT/LOAD_MODEL).read_text());train=loads['deployment_trains']['metro-6car']
    stock=tomllib.loads((ROOT/ROLLING_STOCK).read_text())['profiles']['metro-6car']
    if train['cars']!=stock['cars'] or train['length_m']!=stock['length_m'] or train['tare_mass_t']!=stock['tare_mass_t']:
        raise ValueError('Baghdad load seed and controlled rolling-stock profile disagree')
    for field,capacity in (('aw2_mass_t','passenger_capacity'),('aw3_mass_t','crush_capacity')):
        if not math.isclose(train[field],stock['tare_mass_t']+stock[capacity]*train['passenger_mass_kg']/1000):
            raise ValueError('Baghdad passenger/load planning envelopes do not reconcile')
    design=tomllib.loads((city/'design.toml').read_text())
    if design['city']['slug']!='baghdad' or any(line['rolling_stock']!='metro-6car' for line in design['lines']):
        raise ValueError('Baghdad city lines and selected train family disagree')
    soil=load(city/'engineering/soil/summary.json')
    structural=load(city/'engineering/survey/structural-release-readiness.json')
    survey=load(city/'engineering/survey/surveyed-alignment-readiness.json')
    pattern=None
    selected=train_record or target['supplier_train_record']
    if selected:
        record_path=controlled(ROOT/selected if not Path(selected).is_absolute() else selected)
        record=load(record_path);validate(record,load(HERE/'schemas/supplier-train.json'))
        if record['deployment']!='baghdad' or record['family']!='metro-6car' or record['cars']!=6 or record['axle_count']!=24:
            raise ValueError('supplier record must describe Baghdad six-car, 24-axle stock')
        positions,forces=record['axle_positions_m'],record['axle_loads_kn']
        if len(positions)!=24 or len(forces)!=24 or positions!=sorted(set(positions)) or max(positions)>record['length_m']:
            raise ValueError('supplier axle geometry/count/length mismatch')
        if not math.isclose(sum(forces)*1000,record['loaded_mass_kg']*9.81,rel_tol=1e-5):
            raise ValueError('supplier axle loads do not balance the stated loaded mass')
        if Path(record['source']).is_absolute() or '..' in Path(record['source']).parts:
            raise ValueError('supplier source must be a controlled relative path')
        source=controlled(ROOT/record['source'])
        if sha(source)!=record['source_sha256']:raise ValueError('supplier drawing/load source is stale')
        sources[record_path.relative_to(ROOT).as_posix()]=sha(record_path)
        sources[source.relative_to(ROOT).as_posix()]=sha(source)
        pattern=dict(record=record,record_path=record_path.relative_to(ROOT).as_posix(),record_sha256=sha(record_path),
                     leading_axle_offset_m=positions[0],offsets_from_first_axle_m=[x-positions[0] for x in positions])
    missing=[dict(id='TRAIN-AXLE-POSITIONS',owner='rolling-stock supplier',blocks_moving_load=pattern is None,
                  status='open' if pattern is None else 'supplied-source-bound',required='six-car supplier drawing with all 24 axle positions'),
             dict(id='TRAIN-LOADED-DISTRIBUTION',owner='rolling-stock supplier/structural lead',blocks_moving_load=pattern is None,
                  status='open' if pattern is None else 'supplied-source-bound',required='case-specific loaded axle forces and balanced loaded mass')]
    missing += [dict(id=key,owner=owner,status='open',blocks_moving_load=False,required=description) for key,owner,description in [
        ('TRAIN-SUSPENSION','rolling-stock supplier','per-axle sprung/unsprung masses, suspension, contact and bogie/articulation relationships'),
        ('TRAIN-OTHER-CASES','supplier/structural lead','AW3, infrastructure, braking/rescue/maintenance, lateral and dynamic combinations'),
        ('GROUND-CALIBRATION','geotechnical lead','support-zone boreholes, calibrated axial/lateral/group/settlement parameters and pile tests'),
        ('MATERIAL-AND-TENDONS','materials/structural lead','actual concrete/composite batches, reinforcement, tendons, anchorage and losses'),
        ('CODES-AND-LIMITS','engineers of record','adopted Iraqi/project standards, load combinations and accepted limits'),
        ('SURVEY-AND-ERECTION','survey/construction leads','accepted alignment/support locations, temporary stages, actual rigging/routes and equipment charts'),
        ('QUOTATIONS','cost/manufacturing owner','Baghdad-local supplier quotations, productivity and maintenance/replacement inputs'),
        ('PHYSICAL-AND-INDEPENDENT','independent checker/authority','instrumented validation, independent review and existing controlled authority acceptance')]]
    report=dict(schema='osr-civil-deployment-readiness/1',deployment='baghdad',qualification_target=True,
                comparison_scope=dict(route_length_m=target['comparison_route_length_m'],tracks=2,basis='bounded comparison segment, not the complete city'),
                catalogue_context=dict(city=design['city']['slug'],lines=len(design['lines']),ground_status=soil['status'],
                                       missing_ground_profiles=soil.get('missing_profile_count'),structural_status=structural['status'],
                                       structural_authority_accepted=structural['authority_accepted'],survey_status=survey['status']),
                planning_train=dict(family=train['id'],cars=6,axles=24,length_m=train['length_m'],tare_mass_t=train['tare_mass_t'],
                                    aw2_mass_t=train['aw2_mass_t'],aw3_mass_t=train['aw3_mass_t'],
                                    infrastructure_full_train_allowance_t=train['infrastructure_full_train_allowance_t'],
                                    basis='planning envelopes; infrastructure allowance and averages do not define loaded axle forces'),
                supplier_pattern=pattern,missing_inputs=missing,moving_force_execution_ready=pattern is not None,
                coupled_programme_execution_ready=False,engineering_qualification_ready=False,physical_release=False,
                source_hashes=sources,status='blocked-missing-supplier-axle-inputs' if pattern is None else 'moving-force-inputs-supplied-other-qualification-gates-open',
                reference_results='Existing LM3 results remain reference-software evidence and are not Baghdad qualification results')
    return report


def moving_force_study(report,config=None):
    if not report['moving_force_execution_ready']:raise ValueError('Baghdad moving loads blocked: supplier axle positions and loaded distribution are missing')
    study=load(config or HERE/'config/reference.json');pattern=report['supplier_pattern'];record=pattern['record']
    study['name']='baghdad-six-car-civil-research';study['route_length_m']=report['comparison_scope']['route_length_m']
    study['train'].update(name='Baghdad-metro-6car-'+record['load_case'],axle_offsets_m=pattern['offsets_from_first_axle_m'],
                          axle_loads_kn=record['axle_loads_kn'],supplier_verified=True,
                          basis='Source-bound six-car supplier pattern; uncalibrated structure/rail-distribution assumptions and qualification gaps remain open')
    study['sources_sha256'].update(report['source_hashes'])
    study.setdefault('evidence_refs',{})['train']=dict(source=pattern['record_path'],sha256=pattern['record_sha256'],basis=record['basis'])
    validate_study(study)
    return study


def write(report,output,*,config=None,resume=False):
    profile=moving_force_study(report,config) if report['moving_force_execution_ready'] else None
    if output.exists():
        if not resume:raise ValueError('qualification output must be new; use --resume for matching inputs')
        if (output/'qualification.json').read_bytes()!=encoded(report):
            raise ValueError('qualification resume inputs changed')
        if profile is not None and (output/'solver-profile.json').read_bytes()!=encoded(profile):
            raise ValueError('qualification resume solver profile changed')
        return output
    output.mkdir(parents=True)
    (output/'qualification.json').write_bytes(encoded(report))
    if profile is not None:(output/'solver-profile.json').write_bytes(encoded(profile))
    train=report['planning_train']
    text=['# Baghdad civil qualification input readiness','',
          f"Target: **Baghdad**, six cars, **24 axles**, {train['length_m']:g} m retained planning length.",
          f"Planning masses: {train['tare_mass_t']:g} t tare, {train['aw2_mass_t']:g} t AW2 and {train['aw3_mass_t']:g} t AW3.",
          '', 'Supplier axle positions and loaded distribution are required before a Baghdad moving-load run. LM3 axle spacing is never repeated or relabelled.',
          '',f"Status: `{report['status']}`. Physical release and engineering qualification remain false.",
          '', '| Input | Owner | Status | Required evidence |','|---|---|---|---|']
    text += [f"| {r['id']} | {r['owner']} | {r['status']} | {r['required']} |" for r in report['missing_inputs']]
    text += ['', f"The {report['comparison_scope']['route_length_m']:g} m double-track comparison segment is separate from the complete city inventory. Desktop soil screens are not calibrated site resistance.",
             'Existing LM3 studies remain software verification references. The coupled programme requires supplier suspension/bogie data and a suitable per-axle adapter.', '']
    (output/'qualification.md').write_text('\n'.join(text))
    return output
