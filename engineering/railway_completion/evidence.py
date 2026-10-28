"""Typed current evidence, authenticated outside the research design runner.

The external callback has the same responsibility as the existing qualification
workflow: verify the signature AND authorised role/scope against its own trust
store. Input files cannot install a verifier, trust key or approval policy.
Hashes identify bytes; they do not authenticate an article, limit or reviewer.
"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from math import isfinite
import json

from engineering.station_rail.common import identity, digest
from engineering.design_search import test_readiness
from engineering.design_search import railway_bundle
from . import FLAGS

PRODUCER='engineering/railway_completion/evidence.py'
MAX_FILE=16*1024**2
MAX_TOTAL=64*1024**2


def parse(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:
                raise ValueError('Duplicate JSON evidence key: '+key)
            result[key]=value
        return result
    def constant(value):
        raise ValueError('Nonfinite JSON evidence number: '+value)
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)


def read_owned(root,reference,*,maximum=MAX_FILE):
    if not isinstance(reference,dict) or set(reference)!={'path','sha256'}:
        raise ValueError('Explicit relative evidence path and SHA256 required')
    relative=PurePosixPath(reference['path'])
    if (relative.is_absolute() or not relative.parts or '..' in relative.parts
            or '\\' in reference['path'] or str(relative)!=reference['path']):
        raise ValueError('Ordinary relative evidence path required')
    parent=Path(root).resolve();path=parent
    for part in relative.parts:
        path=path/part
        if path.is_symlink():
            raise ValueError('Linked evidence refused')
    if not path.is_file() or not 0<path.stat().st_size<=maximum or digest(path)!=reference['sha256']:
        raise ValueError('Evidence file bytes or size differ')
    return path.read_bytes()


def timestamp(value):
    if not isinstance(value,str) or not value.endswith('Z'):
        raise ValueError('Explicit UTC evidence timestamp ending Z required')
    result=datetime.fromisoformat(value[:-1]+'+00:00')
    if result.tzinfo!=timezone.utc:
        raise ValueError('UTC timestamp required')
    return result


def number(value,name,*,nonnegative=False):
    if type(value) not in (int,float) or not isfinite(value) or nonnegative and value<0:
        raise ValueError('Finite '+name+' required')
    return float(value)


def binding(bundle):
    railway_bundle.validate(bundle)
    return dict(candidate_id=bundle['candidate_id'],bundle_definition_id=bundle['definition_id'],
        body_candidate_id=bundle['body_candidate_id'],requirement_revision=bundle['requirement_revision'],
        source_sha256=deepcopy(bundle['source_sha256']))


def _attest(attestation,claim,role,authenticator):
    if (not isinstance(attestation,dict) or attestation.get('role')!=role
            or attestation.get('payload_sha256')!=identity(claim)
            or not isinstance(attestation.get('signature'),str) or not attestation['signature']
            or not isinstance(attestation.get('subject_id'),str) or not attestation['subject_id']):
        return False
    # A callback is application configuration, never loaded from imported files.
    return authenticator is not None and authenticator(deepcopy(attestation),role) is True


def _claim(value):
    return {k:v for k,v in value.items() if k not in ('attestations','attestation')}


def _raw_samples(root,envelope,protocol):
    files=envelope.get('raw_files')
    if not isinstance(files,list) or not files:
        raise ValueError('Real raw measurement/source files required')
    if len(files)>32 or len({r.get('path') for r in files})!=len(files):
        raise ValueError('Unique bounded raw file inventory required')
    raw=[read_owned(root,r) for r in files]
    if sum(map(len,raw))>MAX_TOTAL:
        raise ValueError('Raw evidence package exceeds budget')
    if envelope['provenance_kind']!='physical-measurement':
        return [],files
    channels={r['name']:r['unit'] for r in protocol['measured_channels']}
    chunks=[];nested={}
    def source(reference):
        key=(reference['path'],reference['sha256'])
        if key not in nested:
            nested[key]=read_owned(root,reference)
            if len(nested)>256 or sum(map(len,nested.values()))>MAX_TOTAL:
                raise ValueError('Typed raw source budget exceeded')
    typed={'typed event','typed record','typed SI/each','currency','UTC timestamp'}
    for data in raw:
        packet=parse(data)
        if packet.get('schema')!='osr-wheel-LIM-measurements/1' or packet.get('channels')!=channels:
            raise ValueError('Measurement channels/units differ from the current protocol')
        if packet.get('binding')!=envelope['binding'] or packet.get('article')!=envelope.get('article'):
            raise ValueError('Raw article/candidate/source binding differs')
        rows=packet.get('samples')
        if not isinstance(rows,list) or not 2<=len(rows)<=100000:
            raise ValueError('Bounded synchronised measured samples required')
        duration=(timestamp(envelope['ended_at'])-timestamp(envelope['started_at'])).total_seconds()
        for row in rows:
            if set(row)!=set(channels):
                raise ValueError('Synchronous complete channel rows required')
            for name,value in row.items():
                unit=channels[name]
                if unit not in typed:
                    number(value,'measurement '+name)
                elif unit=='UTC timestamp':
                    if not timestamp(envelope['started_at'])<=timestamp(value)<=timestamp(envelope['ended_at']):
                        raise ValueError('UTC measurement outside declared execution time')
                else:
                    if not isinstance(value,dict) or not isinstance(value.get('source'),dict):
                        raise ValueError('Typed channel needs an actual source record: '+name)
                    source(value['source'])
                    if unit=='typed event' and (not isinstance(value.get('event_id'),str) or type(value.get('state')) not in (str,bool)):
                        raise ValueError('Typed event identity/state required')
                    if unit=='typed record' and not isinstance(value.get('record_id'),str):
                        raise ValueError('Typed record identity required')
                    if unit=='typed SI/each':
                        number(value.get('value'),'typed quantity',nonnegative=True)
                        if value.get('unit') not in ('m','m2','m3','kg','s','J','Wh','kWh','each'):
                            raise ValueError('Explicit SI/each quantity unit required')
                    if unit=='currency':
                        number(value.get('amount'),'quoted amount',nonnegative=True)
                        code=value.get('currency')
                        if not isinstance(code,str) or len(code)!=3 or not code.isalpha() or not code.isupper():
                            raise ValueError('Explicit three-letter quoted currency required')
            if 'time_s' in channels and not 0<=row['time_s']<=duration:
                raise ValueError('Relative measurement outside declared execution time')
        if 'time_s' in channels and any(b['time_s']<=a['time_s'] for a,b in zip(rows,rows[1:])):
            raise ValueError('Strictly increasing measurement times required')
        if 'event_time' in channels and any(timestamp(b['event_time'])<timestamp(a['event_time']) for a,b in zip(rows,rows[1:])):
            raise ValueError('Ordered UTC record times required')
        if not isinstance(packet.get('case_id'),str) or type(packet.get('repetition')) is not int or packet['repetition']<0:
            raise ValueError('Explicit physical case and repetition required')
        chunks.append(dict(case_id=packet['case_id'],repetition=packet['repetition'],samples=rows))
        if sum(len(c['samples']) for c in chunks)>100000:
            raise ValueError('Total measured sample budget exceeded')
    return chunks,files


def assess(root,envelope,bundle,*,authenticator=None):
    """Resolve and screen one record; supported records still grant no release."""
    if envelope.get('schema')!='osr-wheel-LIM-evidence-envelope/1':
        raise ValueError('Current wheel/LIM evidence envelope required')
    if envelope.get('binding')!=binding(bundle):
        raise ValueError('Evidence belongs to another exact candidate/source/interface')
    if envelope.get('provenance_kind') not in ('physical-measurement','supplier-record','site-survey','commercial-quote','numerical-validation'):
        raise ValueError('Synthetic, template and unknown provenance cannot enter production evidence')
    record=parse(read_owned(root,envelope['record']))
    if record.get('schema') not in ('osr-completion-domain-record/1','osr-wheel-operating-evidence/1','osr-completion-source-record/1'):
        raise ValueError('Typed current domain/operating/source record required')
    if record.get('record_id')!=identity({k:v for k,v in record.items() if k!='record_id'}):
        raise ValueError('Evidence record content identity differs')
    if any(record.get(k)!=v for k,v in binding(bundle).items()):
        raise ValueError('Evidence record binding differs')
    if any(record.get(k) is not False for k in FLAGS):
        raise ValueError('Imported evidence cannot grant automatic release')
    protocols={p['id']:p for p in test_readiness.definitions()['protocols']}
    protocol=protocols.get(envelope.get('protocol_id'))
    if protocol is None:
        raise ValueError('Current T01–T10 protocol required')
    start,end=timestamp(envelope['started_at']),timestamp(envelope['ended_at'])
    if end<start:
        raise ValueError('Evidence execution ends before it starts')
    chunks,files=_raw_samples(root,envelope,protocol)
    samples=[sample for chunk in chunks for sample in chunk['samples']]
    holds=[];failures=[];metrics=[]
    attest=envelope.get('attestations',{})
    claim=_claim(envelope)
    producer,reviewer=attest.get('producer'),attest.get('reviewer')
    if not _attest(producer,claim,'record-producer',authenticator):
        holds.append('Record producer signature/scope not externally authenticated')
    if (not _attest(reviewer,claim,'independent-reviewer',authenticator)
            or producer and reviewer and producer.get('subject_id')==reviewer.get('subject_id')):
        holds.append('Independent reviewer signature/scope or independence missing')
    procedure=envelope.get('procedure',{})
    procedure_data=None
    if (not procedure.get('revision') or not procedure.get('source')
            or timestamp(procedure.get('approved_at'))>start):
        holds.append('Pre-execution procedure approval missing')
    else:
        procedure_data=parse(read_owned(root,procedure['source']))
        if (procedure_data.get('schema')!='osr-wheel-LIM-approved-procedure/1'
                or procedure_data.get('revision')!=procedure['revision']
                or procedure_data.get('protocol_id')!=protocol['id']):
            raise ValueError('Procedure bytes differ from approved revision/protocol')
        if procedure_data.get('binding')!=binding(bundle):
            holds.append('Approved procedure scope differs from the exact candidate')
        if not _attest(attest.get('procedure'),procedure,'procedure-approver',authenticator):
            holds.append('Procedure approval not externally authenticated')
    prerequisites=envelope.get('prerequisites')
    required_prerequisites=None if procedure_data is None else procedure_data.get('required_prerequisites')
    if (not isinstance(required_prerequisites,list) or not required_prerequisites
            or any(not isinstance(item,str) or not item for item in required_prerequisites)
            or len(required_prerequisites)!=len(set(required_prerequisites))):
        holds.append('Approved named prerequisite set missing')
    if not isinstance(prerequisites,list) or not prerequisites:
        holds.append('Approved prerequisite/NCR disposition missing')
    else:
        names=[r['id'] for r in prerequisites]
        if len(set(names))!=len(names):
            raise ValueError('Duplicate prerequisite')
        if set(names)!=set(required_prerequisites or []):
            holds.append('Prerequisite coverage differs from approved procedure')
        for prerequisite in prerequisites:
            if prerequisite.get('binding')!=binding(bundle) or prerequisite.get('protocol_id')!=protocol['id']:
                raise ValueError('Prerequisite candidate/protocol binding differs')
            read_owned(root,prerequisite.get('source'))
            if not _attest(prerequisite.get('attestation'),_claim(prerequisite),'independent-assessor',authenticator):
                holds.append('Prerequisite not authenticated: '+prerequisite['id'])
            elif prerequisite.get('state')=='failed':
                failures.append('Failed prerequisite: '+prerequisite['id'])
            elif prerequisite.get('state')!='passed':
                holds.append('Open prerequisite: '+prerequisite['id'])
    if envelope.get('deviations')!=[]:
        holds.append('Deviations require approved procedure revision/retest and independent disposition')
    if envelope['provenance_kind']=='physical-measurement':
        article=envelope.get('article',{})
        for field in ('serials','material_batches'):
            identities=article.get(field)
            if (not isinstance(identities,list) or not identities
                    or any(not isinstance(value,str) or not value.strip() for value in identities)
                    or len(identities)!=len(set(identities))):
                raise ValueError('Unique nonempty article serial/batch identities required')
        if (article.get('as_built_candidate_id')!=bundle['candidate_id'] or not article.get('serials') or not article.get('material_batches')):
            holds.append('Exact as-built serial/batch article binding missing')
        if not envelope.get('cases') or len(set(envelope['cases']))!=len(envelope['cases']):
            holds.append('Complete distinct execution case inventory missing')
        required=None if procedure_data is None else procedure_data.get('required_cases')
        if (not isinstance(required,dict) or not required
                or any(not isinstance(k,str) or type(v) is not int or v<1 for k,v in required.items())):
            holds.append('Approved case/repetition matrix missing')
        else:
            expected={(case,rep) for case,count in required.items() for rep in range(count)}
            actual=[(chunk['case_id'],chunk['repetition']) for chunk in chunks]
            if set(actual)!=expected or len(actual)!=len(expected) or set(envelope.get('cases',[]))!=set(required):
                holds.append('Executed case/repetition matrix differs from pre-approved programme')
        calibration_rows=envelope.get('calibrations',[])
        calibrations={r['channel']:r for r in calibration_rows}
        if len(calibrations)!=len(calibration_rows):
            raise ValueError('Duplicate channel calibration')
        typed={'typed event','typed record','typed SI/each','currency','UTC timestamp'}
        channels={r['name']:r['unit'] for r in protocol['measured_channels'] if r['name']!='time_s' and r['unit'] not in typed}
        for channel,unit in channels.items():
            c=calibrations.get(channel)
            if c is None:
                holds.append('Calibration missing: '+channel);continue
            uncertainty=number(c.get('expanded_uncertainty'), 'expanded calibration uncertainty',nonnegative=True)
            if (not c.get('instrument_serial') or c['instrument_serial']!=envelope.get('channel_instruments',{}).get(channel)
                    or number(c.get('coverage_factor'),'uncertainty coverage factor')<1):
                holds.append('Calibrated instrument/uncertainty basis missing: '+channel)
            read_owned(root,c['certificate'])
            if c.get('unit')!=unit or timestamp(c['valid_from'])>start or timestamp(c['valid_until'])<end:
                holds.append('Calibration unit/validity differs: '+channel)
            if not _attest(c.get('attestation'),_claim(c),'calibration-authority',authenticator):
                holds.append('Calibration not externally authenticated: '+channel)
            lo,hi=c['range']
            if any(not number(lo,'calibration minimum')<=row[channel]<=number(hi,'calibration maximum') for row in samples):
                failures.append('Measurement outside calibrated range: '+channel)
        limits=envelope.get('approved_limits',[])
        expected_observables={r['observable'] for r in protocol['acceptance_criteria']}
        observable_units={r['observable']:r['unit'] for r in protocol['acceptance_criteria']}
        criterion_channels=None if procedure_data is None else procedure_data.get('criterion_channels')
        derived=[] if procedure_data is None else procedure_data.get('derived_observables',[])
        if (not isinstance(criterion_channels,dict) or not isinstance(derived,list)
                or len(derived)!=len(set(derived)) or set(criterion_channels)&set(derived)
                or set(criterion_channels)|set(derived)!=expected_observables
                or any(not isinstance(v,list) or not v or not set(v)<=set(channels) for v in criterion_channels.values())):
            holds.append('Approved scalar/derived mapping of every protocol observable missing')
        else:
            if any(channels[channel]!=observable_units[observable] for observable,names in criterion_channels.items() for channel in names):
                holds.append('Compound/typed observables need independently reviewed derived assessments')
            expected_limits={(observable,channel) for observable,names in criterion_channels.items() for channel in names}
            actual_limits=[(limit.get('observable'),limit.get('channel')) for limit in limits]
            if set(actual_limits)!=expected_limits or len(actual_limits)!=len(set(actual_limits)):
                holds.append('Guarded limit coverage differs from every approved protocol observable/channel')
        for limit in limits:
            channel=limit['channel'];unit=channels.get(channel)
            if unit is None or limit.get('unit')!=unit or limit.get('comparison') not in ('le','ge') or limit.get('statistic') not in ('min','max','absmax','mean','last'):
                raise ValueError('Typed approved limit channel/unit/statistic/comparison differs')
            if (limit.get('binding')!=binding(bundle) or limit.get('protocol_id')!=protocol['id']
                    or not limit.get('derivation') or timestamp(limit['approved_at'])>start
                    or not _attest(limit.get('attestation'),_claim(limit),'limit-approver',authenticator)):
                holds.append('Limit not authenticated before execution: '+channel);continue
            read_owned(root,limit['derivation_source'])
            c=calibrations.get(channel)
            if c is None:
                continue
            bound=number(limit['value'],'approved limit')
            uncertainty=number(c['expanded_uncertainty'],'expanded uncertainty',nonnegative=True)
            for chunk in chunks:
                values=[r[channel] for r in chunk['samples']]
                observed={'min':min(values),'max':max(values),'absmax':max(map(abs,values)),'mean':sum(values)/len(values),'last':values[-1]}[limit['statistic']]
                guarded=observed+uncertainty if limit['comparison']=='le' else observed-uncertainty
                passed=guarded<=bound if limit['comparison']=='le' else guarded>=bound
                metrics.append(dict(channel=channel,observable=limit.get('observable'),case_id=chunk['case_id'],repetition=chunk['repetition'],observed=observed,guarded=guarded,limit=bound,unit=unit,passed=passed))
                if not passed:
                    failures.append('Guard-banded criterion failed: '+channel+'/'+chunk['case_id'])
        derived_records={}
        for reference in envelope.get('derived_criteria',[]):
            item=parse(read_owned(root,reference));observable=item.get('observable')
            if observable in derived_records:
                raise ValueError('Duplicate derived criterion')
            derived_records[observable]=item
            if (item.get('schema')!='osr-wheel-LIM-derived-criterion/1'
                    or item.get('binding')!=binding(bundle) or item.get('article')!=envelope.get('article')
                    or item.get('unit')!=observable_units.get(observable)
                    or item.get('procedure_sha256')!=procedure.get('source',{}).get('sha256')
                    or item.get('raw_files')!=files or timestamp(item.get('reviewed_at'))<end):
                raise ValueError('Derived criterion article/raw/procedure/unit binding differs')
            if not _attest(item.get('attestation'),_claim(item),'independent-assessor',authenticator):
                holds.append('Derived criterion not independently authenticated: '+str(observable))
            elif item.get('conclusion')=='failed':
                failures.append('Derived criterion failed: '+str(observable))
            elif item.get('conclusion')!='passed':
                holds.append('Derived criterion unresolved: '+str(observable))
        if set(derived_records)!=set(derived):
            holds.append('Independent derived assessment coverage incomplete')
    ready=not holds and not failures
    value=dict(schema='osr-wheel-LIM-evidence-assessment/1',record_id=record['record_id'],
        candidate_id=bundle['candidate_id'],protocol_id=envelope['protocol_id'],
        state='failed' if failures else 'authenticated-for-declared-scope' if ready else 'hold',
        provenance_kind=envelope['provenance_kind'],
        authenticated=ready,holds=sorted(set(holds)),failures=failures,metrics=metrics,
        physical_protocol_screen_passed=ready and envelope['provenance_kind']=='physical-measurement',
        record=record,raw_files=files,external_authentication_required=True,
        scope='Current record authentication and numeric screening only; independent system disposition remains external',**FLAGS)
    value['assessment_id']=identity(value)
    return value


def load(root,manifest,bundle,*,authenticator=None):
    if manifest.get('schema')!='osr-wheel-LIM-input-manifest/1' or manifest.get('binding')!=binding(bundle):
        raise ValueError('Exact current input manifest binding required')
    references=manifest.get('envelopes')
    if not isinstance(references,list) or len(references)>32 or len({r['path'] for r in references})!=len(references):
        raise ValueError('Unique bounded evidence envelopes required')
    results=[assess(root,parse(read_owned(root,r)),bundle,authenticator=authenticator) for r in references]
    ids=[r['record_id'] for r in results]
    if len(ids)!=len(set(ids)):
        raise ValueError('Duplicate evidence record identity')
    return dict(records=[r['record'] for r in results],assessments=results,
        authenticated_ids=sorted({value for r in results if r['authenticated'] for value in
            [r['record_id'],*[f['sha256'] for f in r['raw_files']]]}),
        manifest_id=identity(manifest),physical_accepted=False)
