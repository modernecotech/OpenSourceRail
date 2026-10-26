"""Continuous-domain RHS research definitions, not three fixed examples.

The current adapter's geometric construction bounds are explicit and revisable
model limits, not railway requirements. This sampler creates real four-wall
stock and derives its geometric mass/inertia. It never converts section EI into
an assumed whole-body deflection, strength, buckling or functional pass.
"""
from copy import deepcopy
from pathlib import Path
from . import body_revision as body
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import identity,digest

PRODUCER='engineering/design_search/section_proposals.py'
SEQUENCE_SEED=29
MAX_SAMPLES=256


def _radical_inverse(index,base):
    value=0.;factor=1./base
    while index:
        index,digit=divmod(index,base);value+=digit*factor;factor/=base
    return value


def _key(parameters):
    return tuple(parameters[n] for n in ('family','sill_width_m','sill_depth_m','sill_wall_m','material'))


def _source_map(root):
    root=Path(root)
    imported={PRODUCER:Path(__file__),body.PRODUCER:Path(body.__file__)}
    sources={name:digest(path) for name,path in imported.items()}
    if any(not (root/name).is_file() or digest(root/name)!=h for name,h in sources.items()):raise ValueError('Imported proposal/adapter source differs from declared root')
    return sources


def generate(reference,*,samples=12,root=ROOT):
    """Return extra definitions compatible with ``body_revision.materialize``.

    Existing three controls remain the caller's ``body.definitions(reference)``;
    none are repeated here. Focused redistribution seeds precede a shifted
    Halton(2,3) sequence over the adapter's declared depth/wall domain. Asking
    for more samples preserves the existing prefix and therefore its identities.
    One-micrometre parameter rounding is a serialization grid, not a machining
    tolerance or a claim that every sampled section is manufacturable.
    """
    body._reference(reference)
    if type(samples) is not int or not 0<=samples<=MAX_SAMPLES:raise ValueError('Explicit zero-to256 pure-definition sample budget required')
    sources=_source_map(root)
    if samples==0:return []
    controls=body.definitions(reference,root=root)
    finite=body.joint_body.materialize_finite_body(reference,root=root);old=body._sills(finite)
    seen={_key(row['parameters']) for row in controls};rows=[]
    depth_lo,depth_hi=body.LIMITS['sill_depth_m'];wall_lo,wall_hi=body.LIMITS['sill_wall_m'];width_lo,width_hi=body.LIMITS['sill_width_m']
    if width_lo!=width_hi:raise ValueError('This sampler requires the explicit current fixed-width RHS adapter; extend its dimensional sampler first')
    # These are research directions, not the complete search space or passing
    # structures. Thin/deep cases deliberately retain local buckling/HAZ holds.
    seeds=[(depth_hi,wall_lo,'deep-thin-domain-corner'),
        (depth_lo+(depth_hi-depth_lo)*5/6,wall_lo,'deep-thin-redistribution'),
        (depth_lo+(depth_hi-depth_lo)*2/3,wall_lo+(wall_hi-wall_lo)/12,'intermediate-stock-redistribution'),
        (depth_hi,wall_lo+(wall_hi-wall_lo)/3,'deep-moderate-wall-control')]
    sequence=0
    while len(rows)<samples:
        if sequence<len(seeds):
            depth,wall,reason=seeds[sequence];method='focused-material-redistribution';coordinates=None
        else:
            index=SEQUENCE_SEED+sequence-len(seeds)+1
            coordinates=[_radical_inverse(index,2),_radical_inverse(index,3)]
            depth=depth_lo+(depth_hi-depth_lo)*coordinates[0];wall=wall_lo+(wall_hi-wall_lo)*coordinates[1]
            method='shifted-Halton-2-3';reason='cover-unexplored-adapter-depth-wall-domain'
        p=dict(family='finite_area_backed_sill_redistribution',sill_width_m=width_lo,
            sill_depth_m=round(depth,6),sill_wall_m=round(wall,6),material='6082-T6-proposed')
        point=sequence;sequence+=1
        if sequence>MAX_SAMPLES*8:raise ValueError('Unique bounded proposal budget exhausted')
        body._parameters(p)
        if _key(p) in seen:continue
        seen.add(_key(p));stock=body._stock(old,p);metrics=body._metrics(old,stock)
        row=dict(schema='osr-body-redistribution-definition/1',
            name=f"180x{p['sill_depth_m']*1000:g}x{p['sill_wall_m']*1000:g}mm-generated",
            parent_candidate_id=reference['candidate_id'],parameters=p,selection_purpose='next_experiment',
            model_limits=deepcopy(body.LIMITS),geometry_metrics=metrics,missing_gates=deepcopy(body.MISSING),
            advisory_policy=deepcopy(controls[0]['advisory_policy']),
            generation=dict(method=method,sequence_seed=SEQUENCE_SEED,proposal_sequence_index=point,
                normalized_halton_coordinates=coordinates,rationale=reason,
                bounds_scope='Adapter geometry/mesh construction domain only; not an immutable transport requirement',
                sampling_grid_m=.000001,manufacturing_tolerance_claimed=False),
            definition_source_sha256=sources,physical_response_estimate=None,strength_screen='unknown',
            buckling_screen='unknown',dynamic_clearance_screen='unknown',manufacturing_feasibility='unknown',
            complete_installed_mass_kg=None,**FLAGS)
        row['definition_id']=identity(row);rows.append(row)
    if sources!=_source_map(root):raise ValueError('Proposal/adapter source changed during definition generation')
    return rows
