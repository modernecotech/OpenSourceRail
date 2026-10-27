"""Strict vector magnetic maps and honest adapters to current retained evidence.

No scalar/2D publication is converted into a3D journey force map here. Missing
lateral forces, moments, loss, thermal or velocity information remain unknown.
"""
from __future__ import annotations

from bisect import bisect_left
from copy import deepcopy
import gzip
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path
import re
from typing import TypedDict

from engineering import research_ancestry
from engineering.station_rail.history import REVISION as RETAINED_SOURCE_REVISION

SCHEMA="osr-magnetic-force-map/1"
IDENTITY_KEYS=("candidate_id","geometry_id","material_id","evaluation_id")
REQUIRED_AXES=("gap_m","lateral_m","longitudinal_m","roll_rad","pitch_rad","yaw_rad","temperature_C","v_m_s")
UNITS=dict(position="m",angle="rad",current="A",temperature="degC",velocity="m/s",force="N",moment="N*m")
FRAME=dict(name="module-local",handedness="right",axes=dict(x="travel",y="transverse-left",z="up"),
           rotation_convention="intrinsic-XYZ-roll-pitch-yaw",gap_positive="train-away-from-guideway",moment_origin_m=[0.,0.,0.])
G=9.80665
CODE='engineering/trip_dynamics/magnetic_maps.py'
# These are the unchanged retained receipts at RETAINED_SOURCE_REVISION.
PUBLICATION_PINS={
    'docs/design-engine/ferrite-maglev/candidate-magnetics':'599cc8f6a6d48a60b55b5e02c893deb2afea16f96aa4eaf3871d746317188059',
    'docs/design-engine/passive-suspension':'9d1d2eb9dd24248d259c97b39195eeed83f29f3776afe17a1436f61654bb8c33',
    'docs/design-engine/vehicle-optimisation':'d0dd60c6081128a88d2041adc1982c076d7e338b0be8147a7758f89a3804ef5e',
}


class MapIdentity(TypedDict):
    candidate_id:str
    geometry_id:str
    material_id:str
    evaluation_id:str


class MapError(ValueError):pass
class MapDomainError(MapError):pass


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def _number(value,name):
    if type(value) not in (int,float) or not math.isfinite(value):raise MapError(name+" must be finite")
    return float(value)


def _vector(value,name,*,nonnegative=False):
    if not isinstance(value,list) or len(value)!=3:raise MapError(name+" must have three explicit components")
    values=[_number(x,name) for x in value]
    if nonnegative and min(values)<0:raise MapError(name+" must be nonnegative")
    return values


def _identity(value):
    if not isinstance(value,dict) or set(value)!=set(IDENTITY_KEYS):raise MapError("complete candidate/geometry/material/evaluation identity required")
    if any(not isinstance(value[k],str) or not re.fullmatch('[0-9a-f]{64}',value[k]) for k in IDENTITY_KEYS):
        raise MapError("source-bound64-character identities required")


def seal_force_map(value):
    """Content seal only; callers must supply actual evidence and all dimensions."""
    result=deepcopy(value);result.pop('map_id',None);result['map_id']=identity(result)
    validate_force_map(result)
    return result


def validate_force_map(value,*,expected_identity=None):
    if not isinstance(value,dict) or value.get('schema')!=SCHEMA:raise MapError("strict magnetic force-map schema required")
    raw=deepcopy(value);digest=raw.pop('map_id',None)
    if digest!=identity(raw):raise MapError("force-map content digest differs")
    _identity(value.get('identity'))
    sources=value.get('source_sha256',{})
    if not isinstance(sources,dict) or not sources or any(not isinstance(k,str) or Path(k).is_absolute() or '..' in Path(k).parts or not isinstance(v,str) or not re.fullmatch('[0-9a-f]{64}',v) for k,v in sources.items()):
        raise MapError("relative evaluator/material source bindings required")
    if expected_identity is not None:
        if not isinstance(expected_identity,dict) or set(expected_identity)-set(IDENTITY_KEYS):raise MapError("unknown expected identity field")
        if any(value['identity'][k]!=v for k,v in expected_identity.items()):raise MapError("force-map identity mismatch")
    if value.get('units')!=UNITS:raise MapError("explicit SI map units required")
    frame=value.get('frame',{})
    if any(frame.get(k)!=v for k,v in FRAME.items() if k!='moment_origin_m'):raise MapError("unsupported magnetic coordinate frame/convention")
    _vector(frame.get('moment_origin_m'),'moment origin')
    if value.get('execution_status')!='executed' or value.get('numerical_status')!='converged':raise MapError("map must be executed and numerically converged")
    physics=value.get('physics',{})
    if physics.get('spatial_dimension')!=3 or physics.get('nonlinear_material_solve') is not True:raise MapError("actual nonlinear3D map required; scalar2D evidence is not promotable")
    if value.get('evidence_kind') not in ('candidate-nonlinear3d','manufactured-fixture','synthetic-test'):raise MapError("explicit map evidence kind required")
    if value.get('physical_accepted') is not False:raise MapError("research map cannot confer physical acceptance")
    validation=value.get('validation',{})
    for key in ('mesh','domain'):
        if validation.get(key,{}).get('state')!='pass' or not validation[key].get('reason'):raise MapError(key+" validation must pass with its reason")
    if validation.get('material_model',{}).get('state')!='pass' or not validation['material_model'].get('reason'):
        raise MapError("declared constitutive/recoil-domain check must pass")
    for key,error_key,tolerance_key in [('force','component_absolute_error_N','component_tolerance_N'),('moment','component_absolute_error_Nm','component_tolerance_Nm')]:
        check=validation.get(key,{})
        if check.get('state')!='pass' or not check.get('reason'):raise MapError(key+" vector convergence must pass with its reason")
        error=_vector(check.get(error_key),key+' error',nonnegative=True)
        tolerance=_vector(check.get(tolerance_key),key+' tolerance',nonnegative=True)
        if any(t<=0 or e>t for e,t in zip(error,tolerance)):raise MapError(key+" vector uncertainty exceeds declared convergence tolerance")
    axes=value.get('axes',{});currents=value.get('current_axes')
    if not isinstance(currents,dict) or any(not isinstance(k,str) or not k or not isinstance(v,str) or not v.endswith('_A') for k,v in currents.items()):
        raise MapError("every current circuit requires an explicit named current axis")
    if len(set(currents.values()))!=len(currents):raise MapError("current axes must be independent")
    if set(axes)!=set(REQUIRED_AXES)|set(currents.values()) or not len(axes)<=16:raise MapError("missing or undeclared force-map dimensions")
    for name,coordinates in axes.items():
        if not isinstance(coordinates,list) or not coordinates:raise MapError("nonempty validity axes required")
        values=[_number(v,name) for v in coordinates]
        if values!=sorted(set(values)):raise MapError("strictly increasing unique axis coordinates required")
        if name=='gap_m' and min(values)<=0:raise MapError("positive gaps required")
        if name=='v_m_s' and min(values)<0:raise MapError("nonnegative speed required")
    ports=value.get('ports',{})
    if set(ports)!={'field_energy_J','flux_linkage_Wb_turn','losses_W'} or any(v not in ('available','unknown') for v in ports.values()):
        raise MapError("energy, flux and loss availability must be explicit")
    if any(v!=0 for v in axes['v_m_s']):
        if physics.get('velocity_dependent') is not True or ports['losses_W']!='available':
            raise MapError("moving states require explicit velocity-dependent forces and loss model")
    expected_count=math.prod(map(len,axes.values()))
    if expected_count>100000 or len(value.get('rows',[]))!=expected_count:raise MapError("complete bounded Cartesian map required")
    seen=set()
    for row in value['rows']:
        if row.get('identity')!=value['identity']:raise MapError("mixed row identities")
        if row.get('numerical_status')!='converged':raise MapError("nonconverged row refused")
        q=row.get('coordinates',{})
        if set(q)!=set(axes):raise MapError("row lacks explicit map dimensions")
        coordinate=tuple(_number(q[k],k) for k in axes)
        if coordinate in seen or any(x not in axes[k] for k,x in zip(axes,coordinate)):raise MapError("duplicate or off-grid force row")
        seen.add(coordinate)
        _vector(row.get('force_N'),'force');_vector(row.get('moment_Nm'),'moment')
        for port,status in ports.items():
            content=row.get(port)
            if status=='unknown':
                if content is not None:raise MapError("unknown magnetic port cannot silently become zero")
            elif port=='flux_linkage_Wb_turn':
                if not isinstance(content,dict) or set(content)!=set(currents):raise MapError("all circuit flux linkages required")
                for x in content.values():_number(x,port)
            elif _number(content,port)<0:raise MapError("stored energy and losses must be nonnegative")
    return deepcopy(value)


class ForceMap:
    """Piecewise multilinear vector interpolation inside the complete envelope."""
    def __init__(self,value,*,expected_identity=None):
        self._value=validate_force_map(value,expected_identity=expected_identity)
        self._axes=self._value['axes']
        self._rows={tuple(row['coordinates'][k] for k in self._axes):row for row in self._value['rows']}

    @property
    def metadata(self):return deepcopy({k:v for k,v in self._value.items() if k!='rows'})

    def sample(self,coordinates):
        if not isinstance(coordinates,dict) or set(coordinates)!=set(self._axes):raise MapDomainError("query must explicitly supply every map coordinate")
        brackets=[]
        for key,axis in self._axes.items():
            x=_number(coordinates[key],key)
            if not axis[0]<=x<=axis[-1]:raise MapDomainError(key+" outside retained validity envelope; extrapolation refused")
            i=bisect_left(axis,x)
            if i<len(axis) and x==axis[i]:brackets.append([(axis[i],1.)])
            else:
                a,b=axis[i-1],axis[i];weight=(x-a)/(b-a)
                brackets.append([(a,1-weight),(b,weight)])
        force=[0.,0.,0.];moment=[0.,0.,0.]
        ports=self._value['ports'];energy=0. if ports['field_energy_J']=='available' else None
        losses=0. if ports['losses_W']=='available' else None
        flux={c:0. for c in self._value['current_axes']} if ports['flux_linkage_Wb_turn']=='available' else None
        for cell in product(*brackets):
            weight=math.prod(p[1] for p in cell);row=self._rows[tuple(p[0] for p in cell)]
            for i in range(3):force[i]+=weight*row['force_N'][i];moment[i]+=weight*row['moment_Nm'][i]
            if energy is not None:energy+=weight*row['field_energy_J']
            if losses is not None:losses+=weight*row['losses_W']
            if flux is not None:
                for circuit in flux:flux[circuit]+=weight*row['flux_linkage_Wb_turn'][circuit]
        return dict(force_N=force,moment_Nm=moment,field_energy_J=energy,losses_W=losses,flux_linkage_Wb_turn=flux,
                    ports=deepcopy(ports),frame=deepcopy(self._value['frame']),identity=deepcopy(self._value['identity']),
                    map_id=self._value['map_id'],coordinates=deepcopy(coordinates),physical_accepted=False)


def _path(root,relative):
    relative=Path(relative)
    if relative.is_absolute() or not relative.parts or '..' in relative.parts:
        raise ValueError('ordinary retained evidence path required')
    root=Path(root).resolve();path=root/relative
    if any(p.is_symlink() for p in (path,*path.parents) if p!=root and p.is_relative_to(root)):
        raise ValueError('linked retained evidence path refused')
    if not path.resolve().is_relative_to(root):raise ValueError('evidence path escapes explicit root')
    return path


def _json(path):
    data=path.read_bytes()
    if path.suffix=='.gz':data=gzip.decompress(data)
    return json.loads(data)


def _publication(root,relative,needed):
    base=_path(root,relative);manifest_path=_path(root,relative+'/manifest.json')
    if sha256(manifest_path.read_bytes()).hexdigest()!=PUBLICATION_PINS[relative]:
        raise ValueError('pinned retained magnetic publication receipt differs')
    manifest=_json(manifest_path);data={};bindings={}
    for name in needed:
        path=_path(base,name)
        digest=sha256(path.read_bytes()).hexdigest()
        if manifest['files_sha256'].get(name)!=digest:raise ValueError('retained publication file digest differs: '+str(path))
        bindings[path.relative_to(root).as_posix()]=digest;data[name]=_json(path)
    # Historical producer bytes authenticate the archived point results. They
    # are ancestry; current reader code and all live data remain a separate epoch.
    ancestry=research_ancestry.verify(root,manifest.get('source_sha256',{}),
        source_revision=RETAINED_SOURCE_REVISION)
    bindings.update(ancestry['source_sha256'])
    bindings[CODE]=sha256(Path(__file__).read_bytes()).hexdigest()
    for name,digest in bindings.items():
        if sha256(_path(root,name).read_bytes()).hexdigest()!=digest:
            raise ValueError('executing magnetic reader or live input differs: '+name)
    for flag in ('physical_accepted','engineering_accepted','configuration_adopted','physical_validation','physical_release'):
        if manifest.get(flag,False) is not False:raise ValueError('unexpected accepted publication')
    bindings[(base/'manifest.json').relative_to(root).as_posix()]=sha256((base/'manifest.json').read_bytes()).hexdigest()
    return data,bindings,ancestry


def current_magnetic_evidence(root:Path)->dict:
    """Read actual publications from an explicit repository; never fabricate maps.

    Source/file mismatch is retained as an error/unknown evidence state. Records
    keep their own candidate and mass ledger, including distinct material floors.
    """
    root=Path(root).resolve();records=[];bindings={};errors=[];ancestry={}
    def load(relative,needed):
        try:
            data,bound,origin=_publication(root,relative,needed)
            for name,digest in bound.items():
                if name in bindings and bindings[name]!=digest:raise ValueError('mixed magnetic reader/input source epochs: '+name)
                bindings[name]=digest
            ancestry[relative]=origin;return data
        except (OSError,ValueError,KeyError) as error:
            errors.append(dict(publication=relative,error=str(error)));return None
    canonical=load('docs/design-engine/ferrite-maglev/candidate-magnetics',['definition.json.gz','study.json.gz'])
    if canonical:
        d,s=canonical['definition.json.gz'],canonical['study.json.gz']
        variant=next(x for x in s['variant_comparison']['variants'] if x['configuration_sha256']==d['configuration_sha256'])
        peak=variant['positive_peak_current_sample']
        records.append(dict(candidate_id=d['configuration_sha256'],configuration_sha256=d['configuration_sha256'],
            family='canonical-ferrite',label=variant['id'],module_geometry_id=identity(d['module']),modules_per_car=len(d['module_placements_m']),
            mass_ledger_id=identity(dict(tare=d['controlled_tare_kg'],aw3=d['controlled_aw3_kg'],configuration=d['configuration_sha256'])),
            mass_empty_kg_band=[d['controlled_tare_kg']]*2,mass_aw3_kg_band=[d['controlled_aw3_kg']]*2,
            mass_basis='Canonical controlled comparison; no complete qualified installed distribution',installed_mass_complete=False,
            points=[dict(force_z_N=peak['upward_n'],gap_m=d['nominal_gap_m'],temperature_C=40.,
                         currents_A=dict(lift=peak['lift_current_a'],guidance=peak['guidance_current_a']),
                         numerical_usable=variant['static_map_valid'],method='reluctance-network; not FE/measured validated',
                         published_support_screen_pass=variant['screen_pass'])],
            published_aw3_requirement_N=peak['required_aw3_upward_n'],thermal_screen_pass=variant['thermal']['thermal_screen_pass'],
            thermal_required_lift_reference=deepcopy(variant['thermal']),
            guidance_validated=False,source='docs/design-engine/ferrite-maglev/candidate-magnetics/study.json.gz'))
    passive=load('docs/design-engine/passive-suspension',['summary.json'])
    if passive:
        s=passive['summary.json']
        for r in s['reports']:
            f=r.get('reference_field');mass=r['mass_comparison']
            if not f:continue
            records.append(dict(candidate_id=r['candidate_id'],family='passive-ferrite',label=r['sample_id'],
                module_geometry_id=f['geometry_id'],modules_per_car=r['units_per_car'],mass_ledger_id=identity(mass),
                mass_empty_kg_band=[mass['material_subtotal_tare_kg_per_car']]*2,
                mass_aw3_kg_band=[mass['material_subtotal_aw3_kg_per_car']]*2,mass_basis=mass['scope'],installed_mass_complete=False,
                points=[dict(force_z_N=f['F_z_N'],gap_m=f['operating_point']['gap_m'],temperature_C=f['operating_point']['temperature_C'],
                             currents_A=f['operating_point']['currents_A'],numerical_usable=f['interpolation_usable'],method=f['validity_scope'],
                             observed_force_variation_N=max(abs(f['F_z_N']-q['F_z_N']) for q in f['diagnostics']['contour_forces']))],
                guidance_validated=False,thermal_screen_pass=None,source='docs/design-engine/passive-suspension/summary.json'))
    vehicle=load('docs/design-engine/vehicle-optimisation',['summary.json','magnetic-worker.json','refinements.json'])
    if vehicle:
        s=vehicle['summary.json'];worker=vehicle['magnetic-worker.json'];ref=vehicle['refinements.json']
        geometries={v['physical_id']:v for v in worker['candidates']}
        points={v['sample_id']:[] for v in geometries.values()}
        for r in worker['rows']:
            if r['execution_status']=='executed':points[r['sample_id']].append(r['raw_result'])
        for r in ref['candidates']:
            v=r['candidate'];geometries[v['physical_id']]=v;points[v['sample_id']]=[r['raw_result']]
        for r in s['comparisons']:
            v=geometries[r['magnet_id']];mass=r['mass_ledger'];payload=mass['payload_kg']
            records.append(dict(candidate_id=r['candidate_id'],family='vehicle-NdFeB-or-ferrite',label=r['sample_id']+' / '+r['mode'],
                magnet_id=r['magnet_id'],material_grade=v['grade_id'],module_geometry_id=points[v['sample_id']][0]['geometry_id'],
                modules_per_car=v['packing']['modules_per_car'],mass_ledger_id=mass['ledger_id'],
                mass_empty_kg_band=[x-payload for x in r['comparison_aw3_mass_band_kg']],mass_aw3_kg_band=r['comparison_aw3_mass_band_kg'],
                mass_basis=mass['scope'],installed_mass_complete=False,winding_fill_pass=all(x['pass_screen'] for x in r['winding']),
                points=[dict(force_z_N=f['F_z_N'],gap_m=f['operating_point']['gap_m'],temperature_C=f['operating_point']['temperature_C'],
                             currents_A=f['operating_point']['currents_A'],numerical_usable=f['interpolation_usable'],method=f['validity_scope'],
                             observed_force_variation_N=r['hot_field_quality'].get('observed_force_variation_N',0.) if f['operating_point']['temperature_C']==80. and r.get('hot_field_quality') else None)
                        for f in points[v['sample_id']]],
                published_hot_support_bounds=r['hot_support_bounds'],guidance_validated=False,thermal_screen_pass=None,
                source='docs/design-engine/vehicle-optimisation/summary.json'))
    # Source bindings are repository-relative. A checkout path is provenance
    # of the caller, not a physical/evaluation property of this evidence.
    result=dict(schema='osr-current-magnetic-evidence/1',records=records,force_maps=[],errors=errors,
                source_sha256=bindings,retained_source_ancestry=ancestry,full_journey_executed=False,physical_accepted=False,
                limitations=['Existing scalar/network/transverse2D diagnostics are not nonlinear3D journey force maps',
                             'Absent guidance, moment, velocity/drag or repeated thermal duty is unknown, never zero'])
    result['evidence_id']=identity(result);return result


def assess_magnetic_readiness(evidence:dict,vehicle:dict,scenario:dict)->list[dict]:
    """Candidate/mass/scenario admission gates; an adequate lift scalar is insufficient."""
    gates=[]
    def gate(name,state,reason,**values):gates.append(dict(id=name,state=state,reason=reason,values=values))
    cid=vehicle.get('candidate_id',vehicle.get('configuration_sha256'))
    scenario_candidate=scenario.get('candidate_id')
    valid_cid=isinstance(cid,str) and re.fullmatch('[0-9a-f]{64}',cid) is not None
    gate('magnetic-scenario-binding','fail' if not valid_cid else 'unknown' if scenario_candidate is None else 'pass' if scenario_candidate==cid else 'fail',
         'Route/load/environment scenario must bind this same physical candidate; scenario_id is a separate identity',
         vehicle_candidate_id=cid,scenario_candidate_id=scenario_candidate)
    records=[r for r in evidence.get('records',[]) if r['candidate_id']==cid]
    if len(records)!=1:
        gate('magnetic-evidence-identity','unknown','No unique publication record matches this exact physical candidate',candidate_id=cid)
        record=None
    else:
        record=records[0];gate('magnetic-evidence-identity','pass','Publication candidate identity matches',candidate_id=cid,label=record['label'])
    load=scenario.get('load_case','AW3');temp=scenario.get('temperature_C');mass_key='mass_empty_kg_band' if load=='empty' else 'mass_aw3_kg_band'
    if record:
        mass=vehicle.get('comparison_empty_kg_per_car' if load=='empty' else 'comparison_aw3_kg_per_car',
                         vehicle.get('controlled_tare_kg' if load=='empty' else 'controlled_aw3_kg'))
        band=record[mass_key]
        mismatch=(scenario_candidate not in (None,cid) or mass is None or type(mass) not in (float,int) or not math.isfinite(mass) or not band[0]-1e-7<=mass<=band[1]+1e-7
                  or vehicle.get('mass_ledger_id')!=record['mass_ledger_id'])
        gate('magnetic-mass-ledger','unknown' if mismatch else 'pass',
             'Vehicle mass must match its own published comparison ledger' if mismatch else 'Matching comparison mass; installed unknowns remain',
             supplied_mass_kg=mass,published_mass_band_kg=band,mass_ledger_id=record['mass_ledger_id'])
        points=[p for p in record['points'] if p['temperature_C']==temp and (scenario.get('gap_m') is None or p['gap_m']==scenario['gap_m'])]
        if record['family']=='canonical-ferrite':
            p=record['points'][0]
            matched = temp == p['temperature_C'] and not mismatch and load != 'asymmetric'
            gate('published-canonical-support-screen','fail' if matched else 'unknown',
                 'Retained canonical peak-current support screen fails at its published condition; other temperatures are unevaluated, not extrapolated',
                 force_N=p['force_z_N'],published_AW3_requirement_N=record['published_aw3_requirement_N'],point_temperature_C=p['temperature_C'],point_currents_A=p['currents_A'],requested_temperature_C=temp,condition_matches=matched)
        if not points or mismatch or load=='asymmetric':
            gate('magnetic-load-support','unknown','No matching temperature/gap/mass/asymmetric distribution supports a load assessment; no extrapolation',temperature_C=temp,load_case=load)
        else:
            usable=[p for p in points if p['numerical_usable']]
            if not usable:gate('magnetic-load-support','unknown','Matching point exists but numerical/material validity is held')
            else:
                p=max(usable,key=lambda q:q['force_z_N']);required=mass*G/record['modules_per_car'];variation=p.get('observed_force_variation_N')
                state='fail' if p['force_z_N']<required else 'unknown'
                gate('magnetic-load-support',state,'Published scalar capacity diagnostic only; force balance, stability and installed mass remain unproved',
                     force_N=p['force_z_N'],required_mean_force_N=required,observed_force_variation_N=variation,
                     gap_m=p['gap_m'],temperature_C=p['temperature_C'],modules_per_car=record['modules_per_car'])
        if record.get('winding_fill_pass') is False:gate('magnetic-winding-fill','fail','Counted winding exceeds retained fill screen')
        if record.get('thermal_screen_pass') is False:
            gate('magnetic-thermal-duty','unknown',
                 'The retained required-lift thermal screen failed at its own current/duty; this journey has no matched thermal execution',
                 published_required_lift_screen_pass=False, published_reference=record.get('thermal_required_lift_reference'))
    valid_maps=[]
    for value in evidence.get('force_maps',[]):
        try:
            validated=validate_force_map(value,expected_identity={'candidate_id':cid})
            if validated['evidence_kind']=='candidate-nonlinear3d':valid_maps.append(validated)
        except (MapError,KeyError,TypeError):continue
    gate('magnetic-nonlinear3d-map','pass' if valid_maps else 'unknown',
         'Matching nonlinear3D map supplied; operational queries must remain within its full envelope' if valid_maps else 'No matching nonlinear3D vector force/moment map;2D lift is not a substitute',map_ids=[v['map_id'] for v in valid_maps])
    gate('magnetic-guidance-roll','unknown','Finite-displacement lateral force, all moments, multisupport stability and asymmetric response are not established')
    if not any(g['id']=='magnetic-thermal-duty' for g in gates):gate('magnetic-thermal-duty','unknown','No matched current/RMS repeated thermal, cooling and protection duty established')
    gate('magnetic-moving-losses','unknown','Finite ends/joints and speed-dependent drag/losses are not established; absence is not zero',requested_speed_m_s=scenario.get('max_speed_m_s'))
    gate('magnetic-fault-response','unknown','Support/guidance fault trajectories and landing/protection response are not established',fault=scenario.get('fault'))
    if evidence.get('errors'):gate('magnetic-publication-integrity','unknown','Some required current publications are missing/stale/corrupt',errors=evidence['errors'])
    return gates
