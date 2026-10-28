"""Owned engineering inputs and externally authenticated records for continuing cells.

The calling application owns trust/replay providers. Input JSON never loads code,
trust keys or an approval switch. Existing evidence contracts remain authoritative.
"""
from pathlib import Path
from copy import deepcopy
from engineering.railway_completion import evidence
from engineering.reference_cell import manufacturing,economics
from . import identity,FLAGS

KINDS={'force-map','coupled-models','fault-maps','quote','lifecycle-charge','site-input','component-record'}


def template(bundle):
    return dict(schema='osr-continuing-cell-inputs/1',binding=evidence.binding(bundle),
        evidence_manifest=dict(schema='osr-wheel-LIM-input-manifest/1',binding=evidence.binding(bundle),envelopes=[]),
        inputs=[],service_context=None,years=30,discount_rate=.04)


def load(root,manifest,bundle,*,authenticator=None,authentication_context_id=None):
    if (manifest.get('schema')!='osr-continuing-cell-inputs/1' or manifest.get('binding')!=evidence.binding(bundle)
        or not isinstance(manifest.get('inputs'),list) or len(manifest['inputs'])>128):
        raise ValueError('Exact candidate-bound continuing input manifest required')
    if authenticator is not None and (not isinstance(authentication_context_id,str) or len(authentication_context_id)!=64
        or any(c not in '0123456789abcdef' for c in authentication_context_id)):
        raise ValueError('Trusted external authentication context identity required')
    loaded=evidence.load(root,manifest['evidence_manifest'],bundle,authenticator=authenticator)
    inputs=[];seen=set();total=0
    for row in manifest['inputs']:
        if set(row)!={'kind','context','file'} or row['kind'] not in KINDS or not isinstance(row['context'],str):
            raise ValueError('Typed named owned input required')
        key=(row['kind'],row['context'])
        if key in seen:raise ValueError('Select one input per context explicitly')
        seen.add(key);raw=evidence.read_owned(root,row['file']);total+=len(raw)
        if total>evidence.MAX_TOTAL:raise ValueError('Continuing input budget exceeded')
        value=evidence.parse(raw)
        if value.get('candidate_id')!=bundle['candidate_id']:raise ValueError('Imported engineering input uses another candidate')
        inputs.append(dict(kind=row['kind'],context=row['context'],value=value,reference=deepcopy(row['file'])))
    result=dict(manifest=deepcopy(manifest),inputs=inputs,assessments=loaded['assessments'],
        records=loaded['records'],authenticated_ids=loaded['authenticated_ids'],authentication_context_id=authentication_context_id,
        source_kind='owned-inputs-with-external-authentication',**FLAGS)
    result['input_evaluation_id']=identity(result);return result


def for_context(loaded,kind,context):
    rows=[r['value'] for r in loaded['inputs'] if r['kind']==kind and r['context']==context]
    if len(rows)>1:raise ValueError('Ambiguous input context')
    return None if not rows else deepcopy(rows[0])


def commercial(vehicle,civil,bundle,loaded,*,authenticator=None):
    _authentication(loaded,authenticator)
    quotes=[r['value'] for r in loaded['inputs'] if r['kind']=='quote']
    result=manufacturing.compile(vehicle,civil,bundle=bundle,quotes=quotes,authenticator=authenticator)
    result['authentication_context_id']=loaded['authentication_context_id']
    result.pop('evaluation_id',None);result['evaluation_id']=identity(result)
    return result


def _authentication(loaded,authenticator):
    if authenticator is not None and (not callable(authenticator) or not isinstance(loaded.get('authentication_context_id'),str)
        or len(loaded['authentication_context_id'])!=64 or any(c not in '0123456789abcdef' for c in loaded['authentication_context_id'])):
        raise ValueError('Trusted external authentication context identity required')


def lifecycle(bundle,loaded,*,authenticator=None):
    _authentication(loaded,authenticator)
    m=loaded['manifest'];records=[r['value'] for r in loaded['inputs'] if r['kind']=='lifecycle-charge'];context=m.get('service_context')
    if context is None:
        return dict(candidate_id=bundle['candidate_id'],execution='held',reason='Actual service/fleet/cashflow context missing',
                    whole_life_cost_usd=None,required_scopes=list(economics.SCOPES),**FLAGS)
    physical=bundle['architecture_case']['physical_definition']
    expected=dict(cars=bundle['cars'],car_length_m=bundle['car_length_m'],
        normal_places_per_car=bundle['requirements']['passengers_per_car'],
        station_spacing_m=physical['route']['station_spacing_m'])
    if any(context.get(k)!=v for k,v in expected.items()):
        raise ValueError('Service context must match candidate formation, capacity and station spacing')
    if any(context.get(k) is True for k in ('protected_service_qualified','engineering_evidence_qualified')):
        raise ValueError('Input service booleans cannot establish physical or protected-service qualification')
    return economics.evaluate(bundle['candidate_id'],records,m['years'],m['discount_rate'],context,
        authenticator=authenticator,authentication_context_id=loaded['authentication_context_id'])
