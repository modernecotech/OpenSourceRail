"""Disjoint material/allocation replacements in one unchanged service context."""
from copy import deepcopy
import math

from engineering.design_search.contracts import FLAGS, identity

SERVICE = dict(cars=6, body_length_m=17., passengers_normal_per_car=120,
               passengers_aw3_per_car=160, passenger_mass_kg=75.,
               doors_per_car=4, door_opening_m=[1.4,2.1],
               normal_pphpd=14400, headway_s=180.)


def number(value,name,positive=False):
    if type(value) not in (float,int) or not math.isfinite(value) or value<0 or positive and value<=0:
        raise ValueError('finite nonnegative '+name+' required')
    return float(value)


def compose(base_empty_kg,changes,*,payload_kg=12000.,unresolved=None):
    """A retained-allocation comparison is not a complete installed mass.

    Counted-stock removals name actual parts. Allowance removals name their
    inherited budget and provenance. Those two evidence classes never merge.
    Each item specifies exact replacement known stock and its missing hardware.
    """
    base=number(base_empty_kg,'base empty mass',True)
    payload=number(payload_kg,'payload')
    if payload!=SERVICE['passengers_aw3_per_car']*SERVICE['passenger_mass_kg']:
        raise ValueError('AW3 payload must match the explicit unchanged passenger service')
    ids=set();parts=set();allocations=set();removed=0.;added=0.;rows=[];unknown=list(unresolved or [])
    for source in changes:
        row=deepcopy(source)
        name=row.get('id')
        if not name or name in ids:raise ValueError('unique replacement identities required')
        ids.add(name)
        kind=row.get('removal_kind')
        if kind not in ('counted-stock','inherited-allocation'):raise ValueError('explicit replacement evidence class required')
        keys=row.get('removed_part_ids',[]) if kind=='counted-stock' else row.get('removed_allocation_ids',[])
        if not keys or len(set(keys))!=len(keys):raise ValueError('identified disjoint removal scope required')
        owned=parts if kind=='counted-stock' else allocations
        if owned.intersection(keys):raise ValueError('overlapping replacement removes the same physical stock or budget twice')
        owned.update(keys)
        if not row.get('source_bindings') or not row.get('basis'):raise ValueError('replacement provenance required')
        old=number(row['removed_kg_per_car'],'removed stock',True)
        new=number(row['added_known_kg_per_car'],'added known stock')
        if old>base:raise ValueError('individual removal exceeds baseline')
        removed+=old;added+=new
        unknown.extend(row.get('unknown_installed_inventory',[]))
        row.update(delta_known_comparison_kg=new-old,
                   saving_is_weighed=False,installed_replacement_mass_kg=None if row.get('unknown_installed_inventory') else new)
        rows.append(row)
    if removed>base:raise ValueError('combined removals exceed canonical empty mass')
    subtotal=base-removed+added
    value=dict(schema='osr-vehicle-component-replacement-ledger/1',
        base_empty_kg=base,payload_kg=payload,removed_kg_per_car=removed,
        retained_other_components_and_allocations_kg=base-removed,
        added_known_kg_per_car=added,comparison_empty_kg_per_car=subtotal,
        comparison_aw3_kg_per_car=subtotal+payload,comparison_train_aw3_kg=6*(subtotal+payload),
        changes=rows,unknown_installed_inventory=unknown,
        installed_empty_kg_per_car=None,installed_aw3_kg_per_car=None,
        cg_m=None,inertia_kg_m2=None,service=deepcopy(SERVICE),
        scope='Canonical retained-allocation/material comparison; all unmodified components remain, all new unresolved hardware remains unknown',**FLAGS)
    value['ledger_id']=identity(value)
    return value


def support_screen(force_N,ledger,*,units_per_car=24,reserve=1.3,quality_usable=False,numerical_variation_N=0.):
    """One module on one bank, with mass feedback; no complete-system pass."""
    force=number(force_N,'module force')
    variation=number(numerical_variation_N,'observed numerical force variation')
    if type(units_per_car) is not int or units_per_car<=0:raise ValueError('positive module count required')
    reserve=number(reserve,'reserve',True)
    if reserve<1:raise ValueError('reserve cannot reduce passenger support')
    required=ledger['comparison_aw3_kg_per_car']*9.80665*reserve/units_per_car
    lower=max(0.,force-variation);upper=force+variation
    state='unknown' if not quality_usable or lower<required<=upper else 'pass' if lower>=required else 'fail'
    return dict(force_N_per_module=force,force_minus_observed_variation_N=lower,
                observed_numerical_variation_N=variation,required_N_per_module=required,
                comparison_aw3_kg_per_car=ledger['comparison_aw3_kg_per_car'],
                reserve=reserve,modules_per_car=units_per_car,force_ratio=force/required,
                force_minus_variation_ratio=lower/required,
                variation_basis='Observed mesh/domain/air-contour spread only; not a certified physical uncertainty bound',
                conditional_necessary_pass=state=='pass',state=state,
                installed_mass_complete=False,coupled_control_and_thermal_pass=False,**FLAGS)
