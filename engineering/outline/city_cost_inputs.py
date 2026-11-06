"""Versioned local operating inputs with explicit transferred-reference fallbacks."""
from copy import deepcopy
from math import isfinite
from pathlib import Path
import tomllib
from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,identity

PRODUCER='engineering/outline/city_cost_inputs.py'
POLICY='engineering/outline/city-cost-inputs.toml'
FIELDS=('electricity_usd_per_kwh','operations_loaded_paid_wage_usd_h')


def _triple(value,name):
    if (not isinstance(value,list) or len(value)!=3 or any(type(x) not in (int,float) or not isfinite(x) or x<=0 for x in value)
            or value!=sorted(value)):
        raise ValueError('Ordered positive low/base/high local cost inputs required: '+name)
    return value


def sources(root=ROOT):return {n:digest(Path(root)/n) for n in (PRODUCER,POLICY)}


def resolve(city,defaults,policy=None,root=ROOT):
    config=tomllib.loads((Path(root)/POLICY).read_text())
    if (config.get('schema')!='osr-city-local-cost-inputs/1' or config.get('physical_reference_changed') is not False
            or config.get('local_rates_verified') is not False):raise ValueError('Non-promoting local cost policy required')
    value={k:list(_triple(defaults[k],k)) for k in FIELDS};records=[];overridden=set()
    levels=[('country',config.get('countries',{}).get(city.get('country'),{})),
            ('city',config.get('cities',{}).get(city.get('slug'),{})),
            ('request',(policy or {}).get('local_costs',{}))]
    for level,profile in levels:
        if not profile:continue
        if (not isinstance(profile,dict) or set(profile)-set(FIELDS)-{'basis','sources'}
                or not isinstance(profile.get('basis'),str) or not profile['basis'].strip()
                or not isinstance(profile.get('sources',[]),list)
                or any(not isinstance(s,str) or not s.strip() for s in profile.get('sources',[]))):
            raise ValueError('Explicit scoped local cost estimate basis required')
        used=[]
        for key in FIELDS:
            if key in profile:value[key]=list(_triple(profile[key],key));overridden.add(key);used.append(key)
        records.append(dict(level=level,fields=used,basis=profile['basis'],sources=deepcopy(profile.get('sources',[]))))
    result=dict(schema=config['schema'],revision=config['revision'],city=deepcopy(city),values=value,
        fields_overridden=sorted(overridden),overrides=records,reference_origin=config['reference_origin'],
        status='scoped-operating-estimates' if overridden else 'transferred-reference-estimates',
        scope='Electricity tariff and operating paid-hour wage only; does not validate civil, manufacturing, land, taxes or supplier prices',
        source_sha256=sources(root),local_rates_verified=False,physical_reference_changed=False)
    result['inputs_id']=identity(result);return result
