"""Explicit station-primary layouts and bare stock, without force-map admission.

The finite primary is a research unit. Required run-up or stopping distances do
not automatically become installed motor lengths. A caller must supply physical
sections, their tiling policy and independently addressed electrical resources.
"""
from copy import deepcopy
from math import ceil, floor, isfinite
from pathlib import Path
import re

from . import ROOT, FLAGS, station_motor
from .common import digest, identity

PRODUCER='engineering/station_rail/propulsion_layout.py'
_LOADED_SHA=digest(__file__)
_UNIT_LOADED_SHA=digest(station_motor.__file__)
POLICIES=('whole-modules','whole-period-tail')
ROLES=('launch','receiving','shared','boost','research')
MAX_SECTIONS=2048


def _number(value,name,*,positive=True):
    if type(value) not in (int,float) or not isfinite(value) or (positive and value<=0):
        raise ValueError('Finite '+('positive ' if positive else '')+name+' required')
    return float(value)


def _count(value,name,maximum):
    if type(value) is not int or not 1<=value<=maximum:
        raise ValueError('Bounded positive integer '+name+' required')
    return value


def _reference(value,name):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):
        raise ValueError('Explicit '+name+' identity required')
    return value


def _sources(root):
    if digest(Path(root)/PRODUCER)!=_LOADED_SHA:
        raise ValueError('Loaded propulsion layout producer differs from source root')
    return {n:digest(Path(root)/n) for n in (PRODUCER,'engineering/station_rail/common.py','engineering/station_rail/__init__.py')}


def layout(*,candidate_id,body_candidate_id,passive_interface_id,sections,
           module_length_m,module_policy,directions,
           independent_branches_per_direction,magnetic_period_m,faces_per_track,root=ROOT):
    """Describe one track's sections and count explicitly replicated directions.

    Each section is an independently terminated bank. Both stator faces are
    counted once by the unit stock model. Adjoining banks retain separate ends;
    no electrical phase topology or common end termination is inferred.
    """
    refs={k:_reference(v,k) for k,v in dict(candidate_id=candidate_id,
        body_candidate_id=body_candidate_id,passive_interface_id=passive_interface_id).items()}
    module=_number(module_length_m,'module length');period=_number(magnetic_period_m,'magnetic period')
    ratio=module/period
    if not isfinite(ratio) or abs(ratio-round(ratio))>1e-9 or round(ratio)<1:
        raise ValueError('Physical module must contain complete magnetic periods')
    if module_policy not in POLICIES:raise ValueError('Explicit supported module policy required')
    faces=_count(faces_per_track,'stator faces per track',64)
    directions=_count(directions,'directions',64)
    branches=_count(independent_branches_per_direction,'independent branches per direction',10000)
    if not isinstance(sections,list) or not 1<=len(sections)<=MAX_SECTIONS:
        raise ValueError('One to 2048 explicit physical sections required')
    rows=[];ids=set()
    for section in sections:
        if not isinstance(section,dict) or set(section)!={'section_id','start_m','length_m','role'}:
            raise ValueError('Explicit section ID, position, length and role required')
        sid=section['section_id']
        if not isinstance(sid,str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}',sid) or sid in ids:
            raise ValueError('Unique bounded section ID required')
        ids.add(sid)
        if section['role'] not in ROLES:raise ValueError('Named section role required')
        start=_number(section['start_m'],'section start',positive=False)
        length=_number(section['length_m'],'section length')
        if module_policy=='whole-modules':
            full=ceil(length/module);tail=0.
        else:
            full=floor(length/module);remaining=length-full*module
            tail=ceil(remaining/period)*period if remaining>0 else 0.
            if tail>=module:
                full+=1;tail=0.
        installed=full*module+tail;end=start+installed
        if not isfinite(end) or not isfinite(installed) or installed<=0:
            raise ValueError('Physical section arithmetic exceeds finite quantity domain')
        pieces=full+(tail>0)
        rows.append(dict(section_id=sid,role=section['role'],start_m=start,
            requested_length_m=length,installed_length_m=installed,
            installed_end_m=end,full_modules=full,tail_modules=int(tail>0),
            tail_length_m=tail,module_pieces=pieces,
            excess_stock_length_m=max(0.,installed-length),
            longitudinal_module_interfaces=max(0,pieces-1),
            stator_face_module_joints=faces*max(0,pieces-1),
            independently_terminated_bank_ends=2))
    rows.sort(key=lambda r:(r['start_m'],r['section_id']))
    if any(a['installed_end_m']>b['start_m'] for a,b in zip(rows,rows[1:])):
        raise ValueError('Installed sections overlap; shared hardware requires one explicit shared section')
    physical=dict(module_length_m=module,magnetic_period_m=period,directions=directions,
        independent_branches_per_direction=branches,
        sections=[{k:r[k] for k in ('start_m','installed_length_m','full_modules','tail_length_m')} for r in rows],
        faces_per_track=faces,bank_boundaries='Each declared section independently terminated')
    keys=('requested_length_m','installed_length_m','excess_stock_length_m','full_modules',
          'tail_modules','module_pieces','longitudinal_module_interfaces',
          'stator_face_module_joints','independently_terminated_bank_ends')
    one={k:sum(r[k] for r in rows) for k in keys};totals={k:v*directions for k,v in one.items()}
    value=dict(schema='osr-candidate-propulsion-layout/1',**refs,
        physical_layout_id=identity(physical),physical_definition=physical,
        request=dict(module_policy=module_policy,sections=deepcopy(sections)),
        sections=rows,per_direction=one,totals=totals,
        electrical_resources=dict(independent_branches_per_direction=branches,
            total_independent_branches=branches*directions,
            electrical_coil_termination_count=None,converter_installed_capacity_W=None,
            branch_count_duplicates_primary_stock=False),
        references_authenticated=False,complete_installed_quantities=False,
        actual_available_force_N=None,thermal_equilibrium_C=None,
        source_sha256=_sources(root),**FLAGS)
    value['layout_id']=identity(value);return value


def _validate_layout(value,root):
    if (value.get('schema')!='osr-candidate-propulsion-layout/1'
            or value.get('layout_id')!=identity({k:v for k,v in value.items() if k!='layout_id'})):
        raise ValueError('Sealed candidate propulsion layout required')
    p=value['physical_definition'];request=value['request']
    expected=layout(**{k:value[k] for k in ('candidate_id','body_candidate_id','passive_interface_id')},
        sections=request['sections'],module_policy=request['module_policy'],
        module_length_m=p['module_length_m'],magnetic_period_m=p['magnetic_period_m'],faces_per_track=p['faces_per_track'],
        directions=p['directions'],independent_branches_per_direction=p['independent_branches_per_direction'],root=root)
    if value!=expected:raise ValueError('Propulsion layout does not reproduce from its physical request')


def quantities(candidate_layout,primary_definition=None,*,root=ROOT):
    """Calculate bare Cu/steel stock for a sealed explicit layout.

    This adapter supports the current uniform double-sided research unit only.
    A different material or geometry needs its own counted unit-stock adapter;
    an unknown installed assembly never becomes the bare stock subtotal.
    """
    _validate_layout(candidate_layout,root)
    unit=station_motor.definition() if primary_definition is None else deepcopy(primary_definition)
    expected=station_motor.definition()
    if unit!=expected:
        raise ValueError('Supported source-bound finite primary definition required')
    if unit['deployment_length_m'] is not None or unit['native_evidence_admitted'] is not False:
        raise ValueError('Finite primary cannot select deployment or admit native evidence')
    if candidate_layout['physical_definition']['faces_per_track']!=2:
        raise ValueError('Finite unit stock adapter supports exactly two stator faces per track')
    if abs(unit['wavelength_m']-candidate_layout['physical_definition']['magnetic_period_m'])>1e-12:
        raise ValueError('Layout and finite unit magnetic periods differ')
    # Both faces and coil end-turn stock are already included in these rates.
    metres=candidate_layout['totals']['installed_length_m']
    stock={k:metres*unit[field] for k,field in (
        ('copper_kg','copper_kg_per_m'),('steel_kg','primary_steel_kg_per_m'),
        ('bare_primary_stock_kg','bare_primary_stock_kg_per_m'))}
    if any(not isfinite(v) or v<=0 for v in stock.values()):
        raise ValueError('Bare stock arithmetic exceeds finite quantity domain')
    sources={**candidate_layout['source_sha256'],station_motor.PRODUCER:digest(Path(root)/station_motor.PRODUCER)}
    if sources[station_motor.PRODUCER]!=_UNIT_LOADED_SHA:
        raise ValueError('Loaded finite primary differs from source root')
    refs={k:candidate_layout[k] for k in ('candidate_id','body_candidate_id','passive_interface_id')}
    installed_id=identity(dict(**refs,physical_layout_id=candidate_layout['physical_layout_id'],
        repeating_cell_physical_id=unit['repeating_cell_physical_id']))
    value=dict(schema='osr-candidate-propulsion-layout-quantities/1',**refs,
        layout_id=candidate_layout['layout_id'],physical_layout_id=candidate_layout['physical_layout_id'],
        installed_primary_candidate_id=installed_id,
        primary_unit_definition_id=unit['motor_component_id'],repeating_cell_physical_id=unit['repeating_cell_physical_id'],
        unit_quantity_scope=unit['quantity_scope'],
        stock=stock,installed_length_m=metres,faces_already_counted=2,
        module_pieces=candidate_layout['totals']['module_pieces'],
        stator_face_module_joints=candidate_layout['totals']['stator_face_module_joints'],
        independently_terminated_bank_ends=candidate_layout['totals']['independently_terminated_bank_ends'],
        installed_total_mass_kg=None,complete_installed_quantities=False,
        additional_installation_accounts=[dict(account=n,installed_mass_kg=None,
            cost=None,required=True,status='unresolved-positive-or-bounded-design-account') for n in
            ('insulation-and-bobbins','joint-fasteners-and-retention','supports-and-civil-attachments',
             'cooling-and-heat-rejection','feeders-converters-switching-protection')],
        actual_available_force_N=None,current_to_thrust_map_id=None,
        thermal_equilibrium_C=None,full_installed_force_map_accepted=False,
        stock_scaling_is_force_evidence=False,source_sha256=sources,**FLAGS)
    value['evaluation_id']=identity(value);return value
