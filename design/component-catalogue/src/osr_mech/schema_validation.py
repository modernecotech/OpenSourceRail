"""Portable bounded JSON Schema validation for engineering and native CAD runtimes."""
import json
import math
import re


def validate(value, schema, location='$', *, root=None):
    root=schema if root is None else root
    if '$ref' in schema:
        reference=schema['$ref']
        if not reference.startswith('#/'):
            raise ValueError(location+': only local schema references are supported')
        target=root
        for token in reference[2:].split('/'):
            target=target[token.replace('~1','/').replace('~0','~')]
        return validate(value,target,location,root=root)
    if 'anyOf' in schema:
        for branch in schema['anyOf']:
            try:validate(value,branch,location,root=root)
            except ValueError:continue
            else:break
        else:raise ValueError(location+': no allowed schema alternative')
    types=schema.get('type',[]);types=[types] if isinstance(types,str) else types
    matches={'object':type(value) is dict,'array':type(value) is list,'string':type(value) is str,
             'number':type(value) in (int,float),'integer':type(value) is int,'boolean':type(value) is bool,'null':value is None}
    if types and not any(matches[t] for t in types):raise ValueError(location+': wrong type')
    allowed=schema.get('enum',[schema['const']] if 'const' in schema else None)
    if allowed is not None and not any(value==v and (type(value) is bool)==(type(v) is bool) for v in allowed):
        raise ValueError(location+': unregistered value')
    if type(value) in (int,float):
        if not math.isfinite(value):raise ValueError(location+': nonfinite number')
        if value<schema.get('minimum',-math.inf) or value>schema.get('maximum',math.inf) or value<=schema.get('exclusiveMinimum',-math.inf):
            raise ValueError(location+': numeric bound')
    if type(value) is str:
        if len(value)<schema.get('minLength',0):raise ValueError(location+': empty string')
        if 'pattern' in schema and not re.search(schema['pattern'],value):raise ValueError(location+': pattern mismatch')
    if type(value) is dict:
        properties=schema.get('properties',{})
        if set(schema.get('required',[]))-value.keys():raise ValueError(location+': missing required fields')
        if schema.get('additionalProperties') is False and value.keys()-properties.keys():raise ValueError(location+': unknown fields')
        for key,item in value.items():
            if key in properties:validate(item,properties[key],location+'.'+key,root=root)
            elif isinstance(schema.get('additionalProperties'),dict):validate(item,schema['additionalProperties'],location+'.'+key,root=root)
    if type(value) is list:
        if not schema.get('minItems',0)<=len(value)<=schema.get('maxItems',math.inf):raise ValueError(location+': invalid array length')
        if schema.get('uniqueItems'):
            identities={json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False) for v in value}
            if len(identities)!=len(value):raise ValueError(location+': duplicate array entries')
        for i,item in enumerate(value):validate(item,schema.get('items',{}),location+f'[{i}]',root=root)
