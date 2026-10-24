"""Append-only JSON registry and exact-context cache for candidate design work."""
from pathlib import Path
import json
import re

from .contracts import FLAGS, PHYSICAL_KEYS, UNITS, encoded, identity, validate_candidate, validate_request, validate_result
from .storage import ImmutableConflict, atomic_immutable


class IdentityCollision(ValueError):
    pass


class ImmutableRegistry:
    KEYS={'candidate':'candidate_id','evaluation-request':'evaluation_id',
          'evaluation':'evaluation_id','selection':'selection_id','coupling':'coupling_id','candidate-context':'candidate_context_id'}

    def __init__(self,root):
        self.root=Path(root)

    def _path(self,kind,identity):
        if kind not in self.KEYS or not isinstance(identity,str) or not re.fullmatch('[0-9a-f]{64}',identity):
            raise ValueError('registered record kind and SHA256 identity required')
        return self.root/kind/(identity+'.json')

    def store(self,kind,value):
        if kind not in self.KEYS:raise ValueError('unknown registry record kind')
        if kind=='candidate':
            validate_candidate(value)
            context=dict(schema='osr-candidate-context/1',candidate_context_id=identity(value),candidate_id=value['candidate_id'],bundle=value)
            self.store('candidate-context',context)
            value=dict(schema='osr-design-physical-candidate/1',candidate_id=value['candidate_id'],units=UNITS,
                **{key:value[key] for key in PHYSICAL_KEYS},**FLAGS)
        elif kind=='evaluation-request':validate_request(value)
        elif kind=='evaluation':validate_result(value)
        elif kind in ('selection','coupling'):
            key=self.KEYS[kind]
            if value[key]!=identity({name:item for name,item in value.items() if name!=key}):raise IdentityCollision('record payload digest differs')
        path=self._path(kind,value[self.KEYS[kind]]);payload=encoded(value)
        try:
            atomic_immutable(path,payload)
        except ImmutableConflict as error:
            raise IdentityCollision('immutable '+kind+' record differs: '+value[self.KEYS[kind]]) from error
        return path

    def read(self,kind,record_id):
        path=self._path(kind,record_id);value=json.loads(path.read_bytes())
        if value.get(self.KEYS[kind])!=record_id:raise IdentityCollision('registry filename/content identity differs')
        if kind=='candidate':
            if value.get('schema')!='osr-design-physical-candidate/1' or value['candidate_id']!=identity(dict(units=UNITS,**{key:value[key] for key in PHYSICAL_KEYS})):
                raise IdentityCollision('physical registry record differs')
        elif kind=='evaluation-request':validate_request(value)
        elif kind=='evaluation':validate_result(value)
        elif kind in ('selection','coupling'):
            key=self.KEYS[kind]
            if value[key]!=identity({name:item for name,item in value.items() if name!=key}):raise IdentityCollision('record payload digest differs')
        return value

    def read_context(self,context_id):
        value=self.read('candidate-context',context_id)
        validate_candidate(value['bundle'])
        if identity(value['bundle'])!=context_id:raise IdentityCollision('candidate context digest differs')
        return value['bundle']

    def cached(self,request):
        """Reuse only an identical source/settings/scenario/environment request."""
        validate_request(request)
        try:value=self.read('evaluation',request['evaluation_id'])
        except FileNotFoundError:return None
        if value['request']!=request:raise IdentityCollision('evaluation context differs')
        return value

    def entries(self,kind):
        if kind not in self.KEYS:raise ValueError('unknown registry record kind')
        return [self.read(kind,path.stem) for path in sorted((self.root/kind).glob('*.json'))]


Registry=ImmutableRegistry
