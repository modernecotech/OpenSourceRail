"""Capacity is physical; release-share control is an evaluation hypothesis."""
from copy import deepcopy
from math import isfinite
from pathlib import Path
from engineering.station_cycle import design
from engineering.station_rail.common import identity,digest
from . import ROOT


def sources(root=ROOT):
    return {**design.sources(root),'engineering/recovery_search/configuration.py':digest(Path(root)/'engineering/recovery_search/configuration.py')}


def prepare(root=ROOT):
    root=Path(root).resolve();before=sources(root)
    values=design.variants(root)[3]
    parents={'none':next(d for d in values if d['variant']['family']=='powered-wheel' and d['technology'] is None),
             'steel':next(d for d in values if d['variant']['family']=='powered-wheel' and d['technology']=='steel' and d['capacity_j']==4e6),
             'hydraulic':next(d for d in values if d['variant']['family']=='powered-wheel' and d['technology']=='hydraulic' and d['capacity_j']==4e6)}
    value=dict(root=str(root),sources=before,parents=parents,policy=design.policy(root))
    if sources(root)!=before:raise ValueError('Recovery source changed during preparation')
    value['context_id']=identity(value);return value


def build(technology,capacity_j,*,root=ROOT,prepared=None):
    context=prepare(root) if prepared is None else prepared
    if (context['context_id']!=identity({k:v for k,v in context.items() if k!='context_id'})
        or context['sources']!=sources(root) or context['root']!=str(Path(root).resolve())):
        raise ValueError('Prepared recovery context changed')
    if technology not in (None,'steel','hydraulic'):raise ValueError('Explicit supported store technology required')
    if type(capacity_j) not in (int,float) or not isfinite(capacity_j):raise ValueError('Finite capacity required')
    # This bounded adapter extends the existing <=8MJ sizing experiment; it is
    # not a declaration that other physical capacities are impossible.
    if (technology is None and capacity_j!=0) or (technology is not None and not 0<capacity_j<=8e6):
        raise ValueError('Capacity outside this declared sizing experiment')
    d=deepcopy(context['parents'][technology or 'none']);v=d['variant'];parent=v['candidate_id']
    if technology is not None:
        s=design.size_store(technology,capacity_j,context['policy'])
        module=v['physical_definition']['station_energy_module']
        module.update(nominal_capacity_j=float(capacity_j),active_stock_kg_per_station=s['active_mass_kg'],
                      fluid_stock_kg_per_station=s['fluid_mass_kg'],envelope_reserve_m3_per_station=s['reserve_envelope_m3'])
        d.update(capacity_j=float(capacity_j),sizing=s)
        v['name']=f'Powered wheel 12 axles + {technology} {capacity_j/1e6:g} MJ'
    v['parent_candidate_id']=parent;v['candidate_id']=identity(v['physical_definition'])
    v['source_sha256'].update(context['sources'])
    d.update(schema='osr-configured-recovery-design/1',configuration=dict(technology=technology,capacity_j=float(capacity_j)),
             source_sha256=context['sources'],configuration_purpose='Bounded common-hardware economics; no new force/duty evidence or installed admission')
    d.pop('evaluation_id',None);d['evaluation_id']=identity(d);return d


def validate(value,*,root=ROOT):
    if not isinstance(value,dict) or value.get('evaluation_id')!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):
        raise ValueError('Sealed configured recovery design required')
    c=value['configuration'];expected=build(c['technology'],c['capacity_j'],root=root)
    if value!=expected:raise ValueError('Configured recovery hardware or source differs')
    return True


def release_control(share):
    if type(share) not in (int,float) or not isfinite(share) or not 0<share<=.8:
        raise ValueError('Release share outside the bounded control experiment')
    return dict(mode='grid-substitution-slew/2',force_slew_n_s=10000.,maximum_traction_share=float(share),reserve_factor=2.)


def validate_release_control(value):
    if not isinstance(value,dict) or value!=release_control(value.get('maximum_traction_share')):
        raise ValueError('Release control changes fixed reserve or slew obligations')
    return deepcopy(value)
