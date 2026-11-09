"""Nominal terminal hardware research proposals; not supplier hardware approval.

All lengths are metres. Part +X is the insertion axis; placements are proper
terminal-local UVW transforms. Thread major/pilot solids bound the unmodelled
helix, rather than pretending a cylindrical bore is a manufactured thread.
Only ``propose_local`` consumes an authenticated retained definition. The small
``prototype`` function is independent of OSR producers and is suitable for
invented source-development fixtures. Nothing here calls CAD, FEM or composer.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
import math
from typing import Any

CASES = ('low', 'base', 'high')
I = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
REVERSE = [[-1., 0., 0.], [0., -1., 0.], [0., 0., 1.]]
PREFIX = 'research/terminal-enclosure-land-and-stop-r1/'
SOURCE = dict(candidate_id='339689820cde417f85a426c5ac4dfee96fcdee9db6f69107776f17874caa878b',
              evaluation_id='91a013cdd8cc6757b06769f963f75d52499cc58c2de1936c7cc52685aa7d9ec0',
              raw_sha256='cdef7bfebda549f45a4e1c160c58b07f584c610782c56528c541bf8e43bcb82c')
FAMILIES = {
    'M6-nut': ('body/terminal-end-panel-nut', 24),
    'M6-washer': ('body/terminal-end-panel-washer', 48),
    'M5-glazing-bolt': ('body/terminal-window-retention-bolt', 12),
    'M5-glazing-insert': ('body/terminal-window-retention-thread-insert', 12),
    'M5-glazing-washer': ('body/terminal-window-retention-washer', 12),
    'M8-locknut': (PREFIX+'M8-body-locknut', 8),
    'M8-washer': (PREFIX+'M8-body-washer', 16),
    'thread-guard': (PREFIX+'thread-guard', 32),
    'glazing-retainer': ('body/terminal-window-retainer', 1),
    'glazing-seal': ('body/terminal-window-seal', 1),
    'glazing-bond': ('body/terminal-window-bond', 1),
}
HYPOTHESIS = 'Calculated 2026-11-09 nominal local manufacture; no quotation, conformity or volume discount'
MATERIALS = {
    'stainless-316L-hypothesis': {'density_kg_m3': [7760., 8000., 8240.], 'USD_kg': [4., 6., 10.]},
    'al5083': {'density_kg_m3': [2580.2, 2660., 2739.8], 'USD_kg': [3.5, 5., 8.]},
    'gfrp-machinable-hypothesis': {'density_kg_m3': [1800., 1900., 2000.], 'USD_kg': [6., 12., 25.]},
    'PEEK-unqualified': {'density_kg_m3': [1250., 1300., 1350.], 'USD_kg': [60., 100., 180.]},
    'EPDM-cellular-unqualified': {'density_kg_m3': [450., 550., 650.], 'USD_kg': [4., 8., 15.]},
    'structural-silicone-unqualified': {'density_kg_m3': [1050., 1100., 1150.], 'USD_kg': [8., 15., 30.]},
    'thread-retention-compound-unqualified': {'density_kg_m3': [1000., 1100., 1200.], 'USD_kg': [10., 20., 40.]},
}
RATES = {'labour_USD_h': [4., 8., 16.], 'machine_USD_h': [6., 12., 24.],
         'QA_USD_h': [5., 10., 20.], 'overhead_fraction': [.2, .2, .2]}
SERVICE_CONTROLS = dict(tool_envelope_radius_m=.015, tool_insertion_m=.10,
                        required_clearance_m=.001)
RING_ACCESS_DIAMETER_M = .012
RING_ACCESS_DIAMETER_TOLERANCE_M = .00005
RING_AXIS_POSITION_TOLERANCE_M = .0001
HOLDS = [
    'Nominal design proposal: actual forces, grades, thread/lock strength and tightening limits unqualified',
    'Thread helices, lead-ins/runout and locking deformation need controlled drawing/kernel support',
    'Glazing impact/retention, adhesive cure/primer/fire/creep and seal compression unqualified',
    'Insulation, galvanic corrosion, fatigue, thermal movement and water drainage need independent review',
    'Declared finite removal/tool envelopes require whole-assembly collision and continuous-sweep evaluation',
    'No installed assembly, canonical composition, native evaluator or physical acceptance',
]


def _hash(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _num(x, name, *, zero=False):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or (x < 0 if zero else x <= 0):
        raise ValueError(name+' must be finite '+('nonnegative' if zero else 'positive'))
    return float(x)


def _triple(xs, name, *, zero=False):
    if not isinstance(xs, (list, tuple)) or len(xs) != 3:
        raise ValueError(name+' requires low/base/high')
    ys = [_num(x, name, zero=zero) for x in xs]
    if ys != sorted(ys):
        raise ValueError(name+' must be ordered')
    return ys


def _vec(x):
    if not isinstance(x, (list, tuple)) or len(x) != 3:
        raise ValueError('three coordinates required')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in x):
        raise ValueError('finite coordinates required')
    return list(map(float, x))


def _close(a, b):
    if len(a) != len(b) or any(abs(x-y) > 1e-9 for x, y in zip(a, b)):
        raise ValueError('fixed dimensional interface changed')


def _cases(xs):
    return dict(zip(CASES, xs))


def _annulus(length, od, bore=0., x=0.):
    return dict(kind='annulus', at_m=[x, 0., 0.], rotation=copy.deepcopy(I),
                length_m=length, outer_diameter_m=od, inner_diameter_m=bore)


def _box(size, at):
    return dict(kind='box', size_m=list(size), at_m=list(at), rotation=copy.deepcopy(I))


def _hex(af, length, x):
    r = af/math.sqrt(3.)
    return dict(kind='profile-prism', length_m=length, at_m=[x, 0., 0.], rotation=copy.deepcopy(I),
                points_yz_m=[[r*math.cos(math.pi/6+i*math.pi/3), r*math.sin(math.pi/6+i*math.pi/3)] for i in range(6)])


def _minus(outer, cuts):
    return dict(kind='difference', outer=outer, cuts=cuts)


def _bounded_thread(outer, major, pilot, length, *, pitch, x=0., handedness='right', external=False):
    """Complete bounding material graphs, no thread-as-through-hole claim."""
    return dict(kind='thread-bounded-material', outer=outer,
                minimum_material=_minus(outer, [_annulus(length, major, x=x)]) if not external else _annulus(length, pilot, x=x),
                maximum_material=_minus(outer, [_annulus(length, pilot, x=x)]) if not external else outer,
                thread=dict(major_diameter_m=major, pilot_or_root_diameter_m=pilot,
                            pitch_m=pitch, length_m=length, at_m=[x, 0., 0.], axis=[1., 0., 0.],
                            handedness=handedness, external=external, exact_helix_supported=False))


def _part(key, material, geometry, gross, net, *, process, QA, machine=None, blank=None):
    if not (gross > 0 and 0 < net[0] <= net[1] <= gross+1e-12):
        raise ValueError('invalid paid blank/net bound')
    return dict(id=key, material=material, geometry=geometry, frame='part-X-insertion',
                gross_blank_volume_m3=gross, net_volume_bounds_m3=list(net),
                net_volume_base_m3=sum(net)/2., scrap_volume_bounds_m3=[max(0., gross-net[1]), gross-net[0]],
                paid_blank=blank or dict(kind='explicit bounded blank', volume_m3=gross),
                person_process_h=process, person_QA_h=QA,
                machine_h=machine if machine is not None else process,
                finish=dict(passivate=True) if material.startswith('stainless') else dict(clean=True),
                source_quote=False)


def _price(part, rates, materials):
    mat = materials[part['material']]
    rho = _triple(mat['density_kg_m3'], 'density')
    rate = _triple(mat['USD_kg'], 'material rate')
    ph = _triple(part['person_process_h'], 'process h')
    qh = _triple(part['person_QA_h'], 'QA h')
    mh = _triple(part['machine_h'], 'machine h')
    net = part['net_volume_bounds_m3']
    factor = part.get('mass_volume_factor', 1.)
    vols = [v*factor for v in [net[0], part['net_volume_base_m3'], net[1]]]
    gross = part['gross_blank_volume_m3']
    part['mass_kg'] = _cases([v*r for v, r in zip(vols, rho)])
    part['paid_stock_kg'] = _cases([gross*r for r in rho])
    part['scrap_kg_bounds'] = [(gross-net[1]*factor)*rho[0], (gross-net[0]*factor)*rho[2]]
    breakdown = []
    for i in range(3):
        cost = dict(material=gross*rho[i]*rate[i], process=ph[i]*rates['labour_USD_h'][i],
                    machine=mh[i]*rates['machine_USD_h'][i], QA=qh[i]*rates['QA_USD_h'][i])
        cost['overhead'] = sum(cost.values())*rates['overhead_fraction'][i]
        breakdown.append(cost)
    part['cost_USD'] = _cases([sum(v.values()) for v in breakdown])
    part['cost_breakdown_USD'] = dict(zip(CASES, breakdown))


def _rate_inputs(rates, materials):
    rates, materials = copy.deepcopy(rates), copy.deepcopy(materials)
    if set(rates) != set(RATES) or set(materials) != set(MATERIALS):
        raise ValueError('complete declared rate/material roster required')
    for key, val in rates.items():
        rates[key] = _triple(val, key, zero=key == 'overhead_fraction')
    for val in materials.values():
        if set(val) != {'density_kg_m3', 'USD_kg'}:
            raise ValueError('unknown material rate fields')
        _triple(val['density_kg_m3'], 'density'); _triple(val['USD_kg'], 'material rate')
    return rates, materials


def prototype(family: str, *, size: str | None = None, rates=None, materials=None) -> dict[str, Any]:
    """One finite part family. Counts are per source end, never global quantity."""
    if family not in FAMILIES:
        raise ValueError('unsupported family')
    rates, materials = _rate_inputs(RATES if rates is None else rates, MATERIALS if materials is None else materials)
    ss = 'stainless-316L-hypothesis'
    parts, mates = [], []
    machining = [.018, .03, .06]
    qa = [.004, .008, .016]
    if family.endswith('washer') or family in ('M6-nut', 'M8-locknut'):
        if family.endswith('washer'):
            od, bore, t = {'M6-washer': (.012, .0065, .002), 'M8-washer': (.016, .0085, .002),
                           'M5-glazing-washer': (.010, .0055, .001)}[family]
            gross = math.pi/4*od**2*t
            net = math.pi/4*(od**2-bore**2)*t
            parts.append(_part('washer', ss, _annulus(t, od, bore), gross, [net, net],
                               process=[.003, .006, .012], QA=qa,
                               blank=dict(kind='round punched disc', diameter_m=od, thickness_m=t)))
            mates.append(dict(kind='annular bearing faces', axial_span_m=[-t/2, t/2], bore_m=bore))
        else:
            af, length, major, pilot, pitch = (.010, .005, .006, .005, .001) if family == 'M6-nut' else (.013, .008, .008, .0068, .00125)
            area = math.sqrt(3)/2*af**2
            gross = area*length
            outer = _hex(af, length, 0.)
            geom = _bounded_thread(outer, major, pilot, length if family == 'M6-nut' else .006,
                                   pitch=pitch, x=0. if family == 'M6-nut' else -.001)
            low, high = gross-math.pi/4*major**2*length, gross-math.pi/4*pilot**2*length
            if family == 'M8-locknut':
                # Own 2 mm counterbore and inserted ring: disjoint installed solids.
                counter = _annulus(.002, .010, x=.003)
                geom['minimum_material']['cuts'].append(counter)
                geom['maximum_material']['cuts'].append(counter)
                # lower thread only 6mm; upper counterbore replaces its bore.
                low = gross-math.pi/4*(major**2*.006+.010**2*.002)
                high = gross-math.pi/4*(pilot**2*.006+.010**2*.002)
                rn = math.pi/4*(.0099**2-.0076**2)*.002
                parts.append(_part('prevailing-ring', 'PEEK-unqualified', _annulus(.002, .0099, .0076, x=.003),
                                   math.pi/4*.0099**2*.002, [rn, rn], process=[.01, .02, .04], QA=qa,
                                   blank=dict(kind='turned polymer ring', OD_m=.0099)))
                bv = math.pi/4*(.010**2-.0099**2)*.002
                parts.append(_part('ring-retention-bond', 'thread-retention-compound-unqualified',
                                   _annulus(.002, .010, .0099, x=.003), bv*1.15, [bv, bv],
                                   process=[.005, .01, .02], QA=qa))
                mates.append(dict(kind='owned counterbore/ring bonded slip fit', ring_id='prevailing-ring',
                                  radial_bondline_m=.00005, bond_part='ring-retention-bond',
                                  installed_stock_nonoverlap=True, locking_torque_Nm=None, retention_qualified=False))
            parts.append(_part('nut', ss, geom, gross, [low, high], process=machining, QA=qa,
                               blank=dict(kind='cut hex bar', across_flats_m=af, length_m=length)))
            mates.append(dict(kind='internal thread', major_m=major, pitch_m=pitch,
                              nominal_engagement_m=length if family == 'M6-nut' else .006,
                              tolerance_budget_m=.0003, strength_qualified=False))
    elif family == 'M5-glazing-bolt':
        length, af, head = .038, .008, .0035
        outer = _annulus(length, .005, x=length/2)
        shaft = _bounded_thread(outer, .005, .00402, length, pitch=.0008, x=length/2, external=True)
        hexhead = _hex(af, head, -head/2)
        geom = dict(kind='disjoint-material-union', pieces=[shaft, hexhead])
        headvol = math.sqrt(3)/2*af**2*head
        low, high = headvol+math.pi/4*.00402**2*length, headvol+math.pi/4*.005**2*length
        parts.append(_part('bolt', ss, geom, math.sqrt(3)/2*af**2*(length+head), [low, high],
                           process=[.025, .05, .10], QA=qa, blank=dict(kind='hex bar turned shank', AF_m=af, length_m=length+head)))
        mates.append(dict(kind='M5x0.8 bolt', underhead_partX_m=0., tip_partX_m=length,
                          nominal_insert_overlap_m=.007, tolerance_budget_m=.0003,
                          full_thread_after_runout_min_m=.0057, torque_Nm=None))
    elif family == 'M5-glazing-insert':
        # M8 external / M5 internal, no hidden flange into unchanged backing ring.
        gross = math.pi/4*.008**2*.008
        outer = _annulus(.008, .008)
        lo = _minus(_annulus(.008, .007), [_annulus(.008, .005)])
        hi = _minus(outer, [_annulus(.008, .0042)])
        # two finite end notches for a fork driver, removed by Boolean intersection.
        notches = [_box([.001, .002, .002], [.0035, y, 0.]) for y in (-.0035, .0035)]
        geom = dict(kind='double-thread-bounded-material', minimum_material=_minus(lo, notches),
                    maximum_material=_minus(hi, notches),
                    external_thread=dict(major_m=.008, root_m=.007, pitch_m=.001, length_m=.008,
                                         usable_full_thread_length_m=.007, end_runout_each_m=.0005),
                    internal_thread=dict(major_m=.005, pilot_m=.0042, pitch_m=.0008, length_m=.008),
                    exact_helix_supported=False,
                    notch_manufacturing_targets=dict(width_tolerance_m=.000025,depth_tolerance_m=.00005,
                                                     centre_position_tolerance_m=.000025,
                                                     datum='insert axis/endface'))
        lower = math.pi/4*(.007**2-.005**2)*.008-2*.001*.002*.002
        upper = math.pi/4*(.008**2-.0042**2)*.008
        parts.append(_part('insert', ss, geom, gross, [lower, upper], process=[.03, .06, .12], QA=qa,
                           blank=dict(kind='round bar', diameter_m=.008, length_m=.008)))
        # The compound occupies thread voids, whose helix is not resolved. Its
        # paid dose/net bounds are explicit; it cannot be treated as exact CSG.
        parts.append(_part('insert-retention-compound', 'thread-retention-compound-unqualified',
                           dict(kind='bounded-thread-void-fill', axis=[1., 0., 0.], axial_span_m=[-.004, .004],
                                outer_diameter_m=.008, root_diameter_m=.007, exact_distribution=None),
                           4e-8, [1e-8, 3e-8], process=[.005, .01, .02], QA=qa))
        mates.append(dict(kind='headless insert in stopped thread pocket with retained6mm through-void', receiver_major_m=.008, pilot_m=.007,
                          pocket_nominal_depth_m=.0087, depth_tolerance_m=.0003, maximum_depth_m=.009,
                          insert_length_m=.008, minimum_radial_wall_m=.001,
                          receiver_full_thread_min_m=.0067, mechanical_lock='thread compound unqualified',
                          fork_driver=dict(prong_spacing_m=.007, prong_width_m=.002, insertion_m=.001)))
    elif family == 'thread-guard':
        if size not in ('M6', 'M8'):
            raise ValueError('guard size M6/M8 must be explicit')
        major, pilot, od, length, pitch = (.006, .005, .010, .012, .001) if size == 'M6' else (.008, .0068, .012, .014, .00125)
        # closed end 1mm + 1mm tip clearance; optional unmodelled thread bounded.
        bore_length = length-.001
        gross = math.pi/4*od**2*length
        outer = _annulus(length, od, x=length/2)
        geom = _bounded_thread(outer, major, pilot, bore_length, pitch=pitch, x=bore_length/2)
        low = gross-math.pi/4*major**2*bore_length
        high = gross-math.pi/4*pilot**2*bore_length
        parts.append(_part('closed-thread-cap', 'gfrp-machinable-hypothesis', geom, gross, [low, high],
                           process=[.025, .05, .10], QA=qa,
                           blank=dict(kind='machinable rod', diameter_m=od, length_m=length)))
        mates.append(dict(kind='screw-on tip protection, not fastener lock', bolt_size=size, closed_wall_m=.001,
                          minimum_tip_clearance_m=.001, retention_force_N=None, glove_removal=True,
                          insertion_from_tip_m=length, thread_engagement_min_m=.003))
    else:
        # Single waterjet ring avoids an uncounted four-corner weld or mitre.
        dims = {'glazing-retainer': (.004, 1.64, 1.14, 1.56, 1.06, 'al5083'),
                'glazing-seal': (.002, 1.60, 1.10, 1.56, 1.06, 'EPDM-cellular-unqualified'),
                'glazing-bond': (.006, 1.60, 1.10, 1.56, 1.06, 'structural-silicone-unqualified')}
        t, w, h, wi, hi, material = dims[family]
        outer, cut = _box([t, w, h], [0., 0., 0.]), _box([t, wi, hi], [0., 0., 0.])
        net = (w*h-wi*hi)*t
        geom = _minus(outer, [cut])
        if family == 'glazing-retainer':
            holes = [_annulus(t, .0055) | {'at_m': [0., y, z]} for y, z in glazing_axes()]
            geom['cuts'] += holes
            net -= len(holes)*math.pi/4*.0055**2*t
            gross = t*w*h  # paid sheet incl. centre scrap; no nesting credit.
            ph, qh = [.5, 1., 2.], [.2, .4, .8]
            mates.append(dict(kind='twelve removable M5 fasteners', axes_yz_m=glazing_axes(),
                              bore_m=.0055, glass_overlap_m=.020, nominal_glass_to_shank_edge_gap_m=.0025))
        else:
            # Extruded/moulded continuous seal or dispensed bond: no paid full slab.
            gross = net*(1.25*1.10 if family == 'glazing-seal' else 1.15)
            ph, qh = ([.3, .6, 1.2], [.15, .3, .6]) if family == 'glazing-seal' else ([.4, .8, 1.6], [.25, .5, 1.])
            mates.append(dict(kind='one continuous moulded ring' if family == 'glazing-seal' else 'continuous dispensed cured bond ring',
                              four_corner_joins=0, material_compression_or_cure_qualified=False,
                              assembly_gap_m=t, free_seal_thickness_m=.0025 if family == 'glazing-seal' else None,
                              assumed_seal_compression_fraction=.20 if family == 'glazing-seal' else None))
        parts.append(_part(family, material, geom, gross, [net, net], process=ph, QA=qh,
                           machine=[.05, .10, .20], blank=dict(kind='paid whole sheet, centre retained as scrap' if family == 'glazing-retainer' else 'compound dose with positive waste allowance', volume_m3=gross)))
        if family == 'glazing-seal':
            parts[-1].update(mass_volume_factor=1.25, density_basis='free cellular EPDM state',
                             free_net_volume_m3=net*1.25, installed_bulk_density_multiplier=1.25,
                             free_shape=_minus(_box([.0025, w, h], [0., 0., 0.]),
                                               [_box([.0025, wi, hi], [0., 0., 0.])]),
                             deformation_model='Assumed cellular-void compression, constant material mass; not incompressible solid shrinkage')
    for part in parts:
        _price(part, rates, materials)
    physical_mates = [{k:v for k,v in m.items() if k not in ('strength_qualified','retention_qualified','material_compression_or_cure_qualified','locking_torque_Nm','torque_Nm','retention_force_N','fork_driver')} for m in mates]
    physical = dict(schema='osr-terminal-hardware-prototype-physical/1', family=family, size=size,
                    parts=[{k: v for k, v in p.items() if k not in ('cost_USD', 'cost_breakdown_USD', 'person_process_h', 'person_QA_h', 'machine_h', 'source_quote', 'mass_kg', 'paid_stock_kg', 'scrap_kg_bounds')} for p in parts],
                    mating=physical_mates, quantity_per_source_end=(24 if size=='M6' else 8) if family=='thread-guard' else FAMILIES[family][1])
    cid = _hash(physical)
    result = dict(schema='osr-terminal-hardware-prototype/1', candidate_id=cid, physical_definition=physical,
                family=family, size=size, parts=parts, mating=mates,
                manufactured_piece_count=len(parts), basis=HYPOTHESIS, rates=rates, materials=materials,
                mass_kg={c: sum(p['mass_kg'][c] for p in parts) for c in CASES},
                cost_USD={c: sum(p['cost_USD'][c] for p in parts) for c in CASES},
                approvals={k: False for k in ('physical_accepted', 'engineering_accepted', 'native_eligible', 'manufacturing_release', 'operating_release')},
                holds=copy.deepcopy(HOLDS))
    bounds = {
        'M6-washer': ([-.001, -.006, -.006], [.001, .006, .006]),
        'M8-washer': ([-.001, -.008, -.008], [.001, .008, .008]),
        'M5-glazing-washer': ([-.0005, -.005, -.005], [.0005, .005, .005]),
        'M6-nut': ([-.0025, -.010/math.sqrt(3), -.010/math.sqrt(3)], [.0025, .010/math.sqrt(3), .010/math.sqrt(3)]),
        'M8-locknut': ([-.004, -.013/math.sqrt(3), -.013/math.sqrt(3)], [.004, .013/math.sqrt(3), .013/math.sqrt(3)]),
        'M5-glazing-bolt': ([-.0035, -.008/math.sqrt(3), -.008/math.sqrt(3)], [.038, .008/math.sqrt(3), .008/math.sqrt(3)]),
        'M5-glazing-insert': ([-.004, -.004, -.004], [.004, .004, .004]),
        'glazing-retainer': ([-.002, -.82, -.57], [.002, .82, .57]),
        'glazing-seal': ([-.001, -.8, -.55], [.001, .8, .55]),
        'glazing-bond': ([-.003, -.8, -.55], [.003, .8, .55]),
    }
    result['nominal_material_AABB_m'] = bounds[family] if family != 'thread-guard' else ([0., -od/2, -od/2], [length, od/2, od/2])
    lo, hi = result['nominal_material_AABB_m']; ml, mh = result['mass_kg']['low'], result['mass_kg']['high']
    result['mass_property_bounds'] = dict(
        first_moment_kg_m=[[min(ml*a,mh*a,ml*b,mh*b),max(ml*a,mh*a,ml*b,mh*b)] for a,b in zip(lo,hi)],
        CG_containment_box_m=[lo,hi], exact_CG_m=None, exact_inertia_kg_m2=None,
        inertia_diagonal_kg_m2=[[0.,mh*sum(max(abs(lo[j]),abs(hi[j]))**2 for j in range(3) if j!=k)] for k in range(3)],
        basis='Conservative uniform-or-nonuniform material containment bounds; marginal intervals are not correlated low/base/high CG scenarios')
    result['evaluation_id'] = _hash(result)
    return result


def glazing_axes():
    return [[y, z] for z in (-.555, .555) for y in (-.6, -.2, .2, .6)]+[[y, z] for y in (-.805, .805) for z in (-.25, .25)]


def _service_controls(value):
    value=copy.deepcopy(SERVICE_CONTROLS if value is None else value)
    if set(value)!=set(SERVICE_CONTROLS):raise ValueError('Complete service-evaluation controls required')
    for key in value:value[key]=_num(value[key],key)
    return value


def front_service_screen(*, access_diameter_m=RING_ACCESS_DIAMETER_M,
                         diameter_tolerance_m=RING_ACCESS_DIAMETER_TOLERANCE_M,
                         required_clearance_m=.001,coaxial_offset_bound_m=RING_AXIS_POSITION_TOLERANCE_M):
    """Necessary nominal port/stock bounds, not contact/torque qualification.

    Tool/insert rotations are enclosed by cylinders; the port section bound is
    therefore valid for every intermediate angle/translation through this ring.
    It says nothing about other vehicle geometry, glass lifting or real threads.
    """
    D=_num(access_diameter_m,'access diameter');tol=_num(diameter_tolerance_m,'diameter tolerance',zero=True)
    gap=_num(required_clearance_m,'port clearance')
    offset=_num(coaxial_offset_bound_m,'coaxial offset',zero=True)
    if tol>=D:raise ValueError('Empty access tolerance domain')
    r=(D-tol)/2
    radii=dict(pilot_with_diameter_tolerance=.00705/2,
               insert_major_envelope=.008/2,
               retained_two_mm_fork_corner=math.hypot(.0035+.001,.001),
               own_hollow_fork_shaft_with_tolerance=.00955/2)
    residuals={k:r-v-gap-offset for k,v in radii.items()}
    # Source ring aperture1.56x1.06, outer1.7x1.2. All twelve source axes
    # are25mm from aperture and45mm from nearest outer edge.
    inner_ligament=.025-(D+tol)/2-offset
    outer_ligament=.045-(D+tol)/2-offset
    rows=[]
    for y,z in glazing_axes():
        # Exact interior-distance witness for the source rectangle rings.
        distance_to_aperture=max(abs(y)-.78,abs(z)-.53)
        distance_to_outer=min(.85-abs(y),.6-abs(z))
        assert abs(distance_to_aperture-.025)<1e-10 and abs(distance_to_outer-.045)<1e-10
        rows.append(dict(axis_yz_m=[y,z],radial_residuals_m=copy.deepcopy(residuals),
                         inner_ligament_m=distance_to_aperture-(D+tol)/2-offset,
                         outer_ligament_m=distance_to_outer-(D+tol)/2-offset))
    return dict(schema='osr-terminal-front-service-necessary-bounds/1',
        access_diameter_m=D,diameter_tolerance_m=tol,required_clearance_m=gap,
        coaxial_offset_bound_m=offset,coaxiality_basis='New matching-datum fixture/inspection target, not inherited source20mm allocation or measured fit',
        radial_residuals_m=residuals,inner_ligament_m=inner_ligament,outer_ligament_m=outer_ligament,
        source_axes=rows,necessary_port_screen_passed=min(residuals.values())>=0 and inner_ligament>0 and outer_ligament>0,
        intermediate_insert_translations_m=[0.,.001,.007,.009,.015,.020,.050],
        screw_motion=dict(pitch_m=.001,turns=[9*i/19 for i in range(20)],
                          translation_m=[.009*i/19 for i in range(20)],axis=[1.,0.,0.],
                          proper_rotation_U=[[[1.,0.,0.],[0.,math.cos(2*math.pi*9*i/19),-math.sin(2*math.pi*9*i/19)],
                                              [0.,math.sin(2*math.pi*9*i/19),math.cos(2*math.pi*9*i/19)]] for i in range(20)],
                          finite_pose_count=20,
                          convention='Own right-hand thread: positive rotation about+U paired with outward+U advance'),
        stage_conditions=['Remove retained glass/retainer/seal/bond and support/capture them first',
                          'Unthread outerM8 with captive innerM5 headless drawstud and separately fitted rear square key; do not translate an engaged rigid thread',
                          'Maintain tool axial engagement until outerthread free; retain via washer/mainnut/jamnut and withdraw through port',
                          'No backing-ring weld removal or captured-insert exemption'],
        exact_thread_contact_verified=False,tool_torque_qualified=False,
        complete_vehicle_sweep_verified=False,physical_accepted=False)


def support_topology_comparison():
    old=front_service_screen(access_diameter_m=.0055,diameter_tolerance_m=0.,coaxial_offset_bound_m=0.)
    new=front_service_screen(access_diameter_m=RING_ACCESS_DIAMETER_M,diameter_tolerance_m=RING_ACCESS_DIAMETER_TOLERANCE_M)
    return dict(schema='osr-terminal-service-topology-comparison/1',
        old_front=dict(necessary_port_screen_passed=old['necessary_port_screen_passed'],residuals_m=old['radial_residuals_m'],failure_preserved=True),
        front_enlarged_ports=dict(one_retained_ring_owner=True,new_ports=12,port_diameter_m=.012,
                                 necessary_port_screen_passed=new['necessary_port_screen_passed'],next_experiment=True),
        rear_unmodified=dict(source_through_bore_m=.006,insert_major_m=.008,
                             radial_residual_including_1mm_m=.003-.004-.001,
                             necessary_screen_passed=False,
                             reason='Unmodified rear6mm through-void cannot pass8mm insert; rear revision/access would be a different counted family'),
        captive_pre_ring=dict(initial_staging_may_be_possible=True,nondestructive_retained_ring_repair_demonstrated=False,
                              reason='Ring weld/removal/replacement/realignment is not free and is not defined by initial staging'),
        selection='Front port revision is a next research experiment, not an installed or qualified baseline')


def front_service_toolkit(*, rates=None, materials=None):
    """One shared workshop kit with staged headless stud and rear square key.

    The stud can rotate through the tool bore before the rear key is fitted.
    Key installation then positively couples stud/tool rotation. Jam-nut axial
    retention, torque and WLL are research obligations, never qualified claims.
    """
    rates,materials=_rate_inputs(RATES if rates is None else rates,MATERIALS if materials is None else materials)
    ss='stainless-316L-hypothesis';parts=[]
    af=.022;shaft_D=.0095;hole_D=.0055
    prongs=[_box([.0008,.001,.001],[.0004,y,0.]) for y in (-.00375,.00375)]
    outer=dict(kind='disjoint-material-union',pieces=[_hex(af,.010,-.030),_annulus(.025,shaft_D,x=-.0125),*prongs])
    cuts=[_annulus(.035,hole_D,x=-.0175)]
    for y in (-.008,.008):
        cuts.extend([dict(kind='finite-cylinder-cut',base_m=[-.035,y,0.],axis=[1.,0.,0.],diameter_m=.0025,length_m=.007),
                     dict(kind='thread-major-envelope-cut',base_m=[-.035,y,0.],axis=[1.,0.,0.],diameter_m=.003,length_m=.006,pitch_m=.0005)])
    geometry=_minus(outer,cuts)
    solid=math.sqrt(3)/2*af**2*.010+math.pi/4*shaft_D**2*.025+2*.0008*.001**2
    net=solid-math.pi/4*hole_D**2*.035
    # Pilot/major regions are nested unions, not additive overlapping cuts.
    low=net-2*math.pi/4*(.003**2*.006+.0025**2*.001)
    high=net-2*math.pi/4*.0025**2*.007
    parts.append(_part('hollow-fork-body',ss,geometry,math.sqrt(3)/2*af**2*.0368,[low,high],
        process=[.3,.6,1.2],QA=[.1,.2,.4],blank=dict(kind='single paidAF22hex bar',length_m=.0368,
        one_piece=True,finish_length_including_prongs_m=.0358,root_faces_continuous=True)))
    # HeadlessM5 round section53mm + rearAF3.5square6mm: both fit5.5bore.
    threaded=_bounded_thread(_annulus(.053,.005,x=-.0205),.005,.00402,.053,pitch=.0008,x=-.0205,external=True)
    square=_box([.006,.0035,.0035],[-.050,0.,0.])
    stud=dict(kind='disjoint-material-union',pieces=[threaded,square])
    parts.append(_part('M5-headless-drawstud',ss,stud,math.pi/4*.005**2*.060,
        [math.pi/4*.00402**2*.053+.0035**2*.006,math.pi/4*.005**2*.053+.0035**2*.006],
        process=[.05,.1,.2],QA=[.02,.04,.08],blank=dict(kind='round5mmrod',length_m=.060)))
    wv=math.pi/4*(.010**2-.0055**2)*.002
    parts.append(_part('M5-bearing-washer',ss,_annulus(.002,.010,.0055,x=-.036),math.pi/4*.010**2*.002,[wv,wv],
        process=[.004,.008,.016],QA=[.002,.004,.008]))
    for name,L,x in (('main',.004,-.039),('jam',.003,-.0425)):
        g=_bounded_thread(_hex(.008,L,x),.005,.0042,L,pitch=.0008,x=x)
        gross=math.sqrt(3)/2*.008**2*L
        parts.append(_part('M5-'+name+'-nut',ss,g,gross,[gross-math.pi/4*.005**2*L,gross-math.pi/4*.0042**2*L],
            process=[.02,.04,.08],QA=[.005,.01,.02]))
    plate=_box([.002,.026,.016],[-.050,0.,0.])
    pcuts=[_box([.002,.0036,.0036],[-.050,0.,0.])]
    for y in (-.008,.008):pcuts.append(_annulus(.002,.0032)|{'at_m':[-.050,y,0.]})
    pv=.002*(.026*.016-.0036**2-2*math.pi/4*.0032**2)
    parts.append(_part('rear-square-key-plate',ss,_minus(plate,pcuts),.002*.026*.016,[pv,pv],
        process=[.1,.2,.4],QA=[.03,.06,.12]))
    for side,y in (('minus',-.008),('plus',.008)):
        standoff=_annulus(.014,.0055,.0032)|{'at_m':[-.042,y,0.]}
        sv=math.pi/4*(.0055**2-.0032**2)*.014
        parts.append(_part('M3-'+side+'-standoff',ss,standoff,math.pi/4*.0055**2*.014,[sv,sv],
            process=[.015,.03,.06],QA=[.005,.01,.02]))
        shank=_bounded_thread(_annulus(.0225,.003,x=-.04025),.003,.002386,.0225,pitch=.0005,x=-.04025,external=True)
        # All children have explicit tool-frame offsets; Y translation applies
        # to the material union, not an unlocated fastener allowance.
        head=_hex(.0055,.002,-.0525)
        bolt=dict(kind='rigid-material-transform',at_m=[0.,y,0.],rotation=copy.deepcopy(I),
                  material=dict(kind='disjoint-material-union',pieces=[shank,head]))
        hv=math.sqrt(3)/2*.0055**2*.002
        parts.append(_part('M3-'+side+'-bolt',ss,bolt,math.sqrt(3)/2*.0055**2*.0245,
            [hv+math.pi/4*.002386**2*.0225,hv+math.pi/4*.003**2*.0225],process=[.025,.05,.1],QA=[.005,.01,.02]))
        washer=_annulus(.0005,.007,.0032)|{'at_m':[-.05125,y,0.]}
        v=math.pi/4*(.007**2-.0032**2)*.0005
        parts.append(_part('M3-'+side+'-washer',ss,washer,math.pi/4*.007**2*.0005,[v,v],
            process=[.003,.006,.012],QA=[.002,.004,.008]))
    for part in parts:_price(part,rates,materials)
    return dict(schema='osr-terminal-shared-front-service-kit/2',scope='ONE shared workshop kit, never per installed end',
        count_per_train=1,parts=parts,piece_count=len(parts),frame='toolX points toward insert (-U)',
        at_engagement_m=[.0455,0.,0.],rotation_at_engagement=copy.deepcopy(REVERSE),
        geometry=dict(stem_OD_m=shaft_D,stem_OD_tolerance_m=.00005,stem_length_m=.025,
            collar_AF_m=af,collar_axial_span_toolX_m=[-.035,-.025],through_bore_m=hole_D,
            prong_centres_Y_m=[-.00375,.00375],prong_width_m=.001,prong_width_tolerance_m=.000025,
            prong_centre_position_tolerance_m=.000025,installation_relative_alignment_bound_m=.000025,
            prong_depth_m=.0008,prong_depth_tolerance_m=.000025,seating_face_flatness_bound_m=.000025,
            headless_stud_tip_X_m=.006,headless_stud_rear_X_m=-.053,square_AF_m=.0035,square_axial_span_X_m=[-.053,-.047],
            key_square_AF_m=.0036,key_axial_span_X_m=[-.051,-.049],stud_square_clocking_max_turns=.125,
            M3_driver_outer_diameter_required_m=.008,
            main_nut_span_X_m=[-.041,-.037],jam_nut_span_X_m=[-.044,-.041],M3_boss_Y_m=[-.008,.008],
            M3_underhead_X_m=-.0515,M3_tip_X_m=-.029,M3_pilot_bottom_X_m=-.028),
        necessary_mating_bounds=dict(prong_root_inner_ligament_m=.00325-hole_D/2,
            prong_root_outer_ligament_m=shaft_D/2-math.hypot(.00425,.0005),
            minimum_prong_root_inner_ligament_m=.00375-.000025-(.001+.000025)/2-(hole_D+.00005)/2,
            minimum_prong_root_outer_ligament_m=(shaft_D-.00005)/2-math.hypot(.00375+.000025+(.001+.000025)/2,(.001+.000025)/2),
            minimum_notch_side_clearance_m=.00015,minimum_notch_depth_clearance_m=.0001,
            stud_square_to_bore_radial_clearance_bound_m=(.0055-.00005)/2-(.0035+.000025)/math.sqrt(2),
            key_square_face_clearance_bound_m=(.0036-.000025-.0035-.000025)/2,
            square_clocking_axial_allowance_m=.0001,capture_thread_nominal_m=.006,
            capture_full_thread_minimum_hypothesis_m=.0051,key_overlap_after_clocking_minimum_m=.0019,
            collar_nearest_U_m=.0705,ring_front_U_m=.0515,
            M3_engagement_nominal_m=.006,M3_full_thread_minimum_hypothesis_m=.0052,
            M3_bottom_clearance_minimum_m=.0007,M3_receiver_radial_land_m=.0015,
            nut_to_standoff_nominal_gap_m=.00125),
        assembly=['Remove and capture glazing/seal/bond; support tool and expose front workarea',
            'Seat unkeyed fork body; insert HEADLESS stud through5.5mm bore, turn rearAF3.5square to6mm M5engagement',
            'Clock square at most1/8turn (+/-0.1mm travel); hold square while fitting washer/mainnut/jamnut BEFORE standoffs/keyplate',
            'Slide rear3.6mm square-key plate over exposed square; fit2standoffs/2M3bolts/2washers into counted blind tool-collar receivers',
            'TurnAF22fork body: square plate positively co-rotates stud, fork co-rotates insert; no friction-based torsional load-sharing claim',
            'Keep axial seating untilM8 outerthread free after9turns/9mm; withdraw kit/insert through12mmport',
            'At bench support kit; remove rear keyplate/standoffs first, then unlock jamnuts/washer and unscrew stud for insert replacement'],
        hand_tools=dict(new_AF3p5_stud_spanner=1,new_AF8_jamnut_spanners=2,new_AF22_body_spanner=1,new_AF5p5_M3_driver=1),
        hand_tool_cost_scope='Remaining shared workshop allowance; existing glazingM5socket retained separately',
        mass_kg={c:sum(p['mass_kg'][c] for p in parts) for c in CASES},
        calculated_cost_USD={c:sum(p['cost_USD'][c] for p in parts) for c in CASES},
        tool_torque_capacity_Nm=None,capture_capacity_N=None,qualified=False,
        holds=['Actual insert/compound breakaway torque, prongs, square key, receivers and capture WLL unknown',
               'M5jamnut axial retention, tightening procedure and dimensional targets need bench verification; no unearned friction capacity',
               'Thread helices, grip/tolerance/thread-strength, whole-vehicle/tool/operator and glass-lifting proof remain open'])

def finite_sweep_bounds(part, placement, offsets):
    """Finite declared poses only. AABB is diagnostic, never a clash verdict."""
    T = _vec(placement['at_m']); R = placement['rotation']
    if R not in (I, REVERSE):
        raise ValueError('this family supports only its two explicit proper frames')
    if not isinstance(offsets, list) or not 2 <= len(offsets) <= 16:
        raise ValueError('bounded explicit finite pose roster required')
    lo, hi = part['nominal_material_AABB_m']; points = []
    for q in offsets:
        q = _vec(q)
        for x in (lo[0], hi[0]):
            for y in (lo[1], hi[1]):
                for z in (lo[2], hi[2]):
                    p = [x+q[0], y+q[1], z+q[2]]
                    points.append([T[k]+sum(R[k][j]*p[j] for j in range(3)) for k in range(3)])
    return dict(min_m=[min(p[k] for p in points) for k in range(3)],
                max_m=[max(p[k] for p in points) for k in range(3)],
                finite_pose_count=len(offsets), corner_count=len(points),
                diagnostic_conservative_AABB=True, exact_material_clash=False,
                continuous_sweep_verified=False, installed_access_accepted=False)


def _source_volume_geometry(source_entities):
    """Only fixed source interfaces, not an actual new part producer."""
    table = {e['id']: e for e in source_entities}
    for key in ('legacy/retained-glass', 'legacy/glazing-backing-ring'):
        if key not in table:
            raise ValueError('missing fixed glass/backing source')
    glass = table['legacy/retained-glass']['exact_CSG_entity']['geometry']
    if glass['kind'] != 'box': raise ValueError('fixed glass shape kind')
    _close(glass['at_m'], [.0635, 0., 0.]); _close(glass['size_m'], [1.6, 1.1, .012])
    if glass['rotation'] != [[0., 0., 1.], [1., 0., 0.], [0., 1., 0.]]:
        raise ValueError('fixed glass frame changed')
    ring = table['legacy/glazing-backing-ring']['exact_CSG_entity']
    if ring.get('material')!='al5083':raise ValueError('fixed source ring material')
    if ring['geometry']['kind'] != 'difference' or any(ring['geometry'][k]['kind'] != 'box' for k in ('outer','void')):
        raise ValueError('fixed backing ring shape kind')
    _close(ring['geometry']['outer']['at_m'], [.0485, 0., 0.])
    _close(ring['geometry']['outer']['size_m'], [.006, 1.7, 1.2])
    _close(ring['geometry']['void']['size_m'], [.006, 1.56, 1.06])
    _close(ring['geometry']['void']['at_m'], [.0485, 0., 0.])
    for name in ('outer', 'void'):
        if ring['geometry'][name]['rotation'] != I:
            raise ValueError('backing ring frame changed')
    if len(ring['holes']) != 12:
        raise ValueError('backing ring bore count')
    ops = []
    for n, (y, z) in enumerate(glazing_axes()):
        h = ring['holes'][n]
        _close(h['at_m'], [.0455, y, z]); _close(h['axis'], [1., 0., 0.])
        _close([h['diameter_m'], h['length_m']], [.0055, .006])
        hp = table['legacy/glazing-hardpoint/'+str(n)]['exact_CSG_entity']
        _close(hp['geometry']['at_m'], [.0395, y, z]); _close(hp['geometry']['size_m'], [.012, .025, .025])
        if hp['geometry']['kind'] != 'box' or hp['geometry']['rotation'] != I or len(hp['holes']) != 1 or hp['material'] != 'al5083':
            raise ValueError('hardpoint frame/bore count')
        if hp['insert_pocket_max_diameter_m'] < .008 or hp['insert_pocket_max_depth_m'] < .009:
            raise ValueError('declared insert pocket cannot contain own cut')
        old = hp['holes'][0]
        _close(old['at_m'], [.0335, y, z]); _close(old['axis'], [1., 0., 0.])
        _close([old['diameter_m'], old['length_m']], [.006, .012])
        ops.append(dict(id='insert-receiver/'+str(n), source_entity_id='legacy/glazing-hardpoint/'+str(n),
                        kind='hardpoint-thread-pocket',
                        mode='new-build finish retained paid source blank once; original through-void remains', source_geometry=copy.deepcopy(hp),
                        complete_void_union=dict(kind='union', pieces=[copy.deepcopy(old),
                            dict(kind='thread-bounded-cut', at_m=[.0455, y, z], axis=[-1., 0., 0.],
                                 pilot_diameter_m=.007, major_diameter_m=.008, depth_m=.0087, pitch_m=.001,
                                 full_thread_depth_m=.0077, depth_tolerance_m=.0003, flat_bottom=True)]),
                        source_cylinder_position_convention='at_m is base; signed axis points into cut',
                        unchanged_original_through_void=True,
                        incremental_removed_volume_bounds_m3=[math.pi/4*(.007**2-.006**2)*.0084,
                                                               math.pi/4*(.008**2-.006**2)*.009],
                        # A shorter thread envelope can move the removed mass
                        # centre away from the full-depth pilot midpoint.
                        # Unknown helix phase cannot establish radial-zero
                        # moments. Bound every removed point in this model.
                        incremental_removed_centroid_box_m=[[.0455-.009,y-.004,z-.004],
                                                            [.0455,y+.004,z+.004]],
                        removed_centroid_basis='Convex support of complete maximum pocket, including unknown thread phase; conservative marginal bounds, not a correlated actual thread model',
                        maximum_pocket_depth_m=.009, minimum_annular_rear_web_m=.003,
                        operations=['Enlarge known6mm through-bore locally with7mm flat-bottom pilot8.7+/-0.3mm',
                                    'M8x1 stopped thread,7.7mm nominal full-thread region; retain full original6mm through-void',
                                    'Deburr, clean, thread/depth gauge and inspect remaining annular wall'],
                        material='al5083', original_paid_blank_retained=True, source_credit_USD=0.,
                        person_process_h=[.02, .04, .08], person_QA_h=[.01, .02, .04],
                        independent_cut_union_and_mass_update_required=True))
    # ONE existing paid ring, twelve additional cuts. The old5.5mm bores and
    # aperture are explicitly retained inside the full new union. No12blank
    # procurement and no fill/un-cut of any known prior source void.
    new_bores=[]
    for n,(y,z) in enumerate(glazing_axes()):
        new_bores.append(dict(kind='cylinder-cut',at_m=[.0455,y,z],axis=[1.,0.,0.],
            diameter_m=RING_ACCESS_DIAMETER_M,length_m=.006,
            purpose='Own counted front-service access enlargement '+str(n)))
    D=RING_ACCESS_DIAMETER_M;dt=RING_ACCESS_DIAMETER_TOLERANCE_M
    radial_extent=(D+dt)/2+RING_AXIS_POSITION_TOLERANCE_M
    if (D-dt)/2 < .0055/2+RING_AXIS_POSITION_TOLERANCE_M or radial_extent>=.025:
        raise ValueError('Ring enlargement volume model requires contained prior bore and positive aperture ligament')
    removed=[12*math.pi/4*((D+s*dt)**2-.0055**2)*.006 for s in (-1,1)]
    ops.append(dict(id='backing-ring/front-service-ports',kind='ring-access-port-enlargement',
        source_entity_id='legacy/glazing-backing-ring',source_geometry=copy.deepcopy(ring),
        mode='Finish ONE retained paid new-build ring blank once;12enlargements, not12purchases',
        complete_void_union=dict(kind='union',pieces=[copy.deepcopy(ring['geometry']['void']),
                                                   *copy.deepcopy(ring['holes']),*new_bores]),
        source_cylinder_position_convention='at_m is base; signed axis points into cut',
        unchanged_original_voids=True,original_paid_blank_retained=True,
        blank_owner_count=1,new_stock_purchase_count=0,cut_count=12,
        access_diameter_m=D,diameter_tolerance_m=dt,axis_position_tolerance_m=RING_AXIS_POSITION_TOLERANCE_M,
        incremental_removed_volume_bounds_m3=removed,nominal_removed_centroid_m=[.0485,0.,0.],
        incremental_removed_centroid_box_m=[[.0485,-.805-radial_extent,-.555-radial_extent],
                                            [.0485,.805+radial_extent,.555+radial_extent]],
        moment_basis='Nominal equal bores symmetric; independent diameter tolerances do not inherit exactzero centroid. Conservative weighted-centre bounds retained.',
        material='al5083',source_credit_USD=0.,
        person_process_h=[.28,.50,1.0],person_QA_h=[.10,.20,.40],
        process_time_basis=dict(one_setup_h=[.10,.20,.40],each_of_12_bores_h=[.015,.025,.050],
                                one_QA_setup_h=[.04,.08,.16],each_of_12_bores_QA_h=[.005,.010,.020],
                                machine_h_basis='same bounded machining duration as process hours; no measured production rate'),
        operations=['Fixture ONE existing source-ring blank before assembly; preserve outer/aperture/datums',
                    'Enlarge all12existing5.5mmbores to12.00+/-0.05mm through6mmring',
                    'Deburr both faces, gauge all12diameters and0.1mmcoaxiality target, inspect18.875mmminimum aperture ligament',
                    'Install/attach ring under retained source joining obligations; no free ring-weld removal during service'],
        independent_cut_union_and_mass_update_required=True))
    return ops


def _placement(entity, family, index, tables):
    """Own nominal hardware placement, source anchors are provenance, not proof."""
    pos, rot = list(entity['at_m']), copy.deepcopy(I)
    if family.startswith('M5-glazing-'):
        old = entity['exact_CSG_entity']['id']
        n = int(old.rsplit('/', 1)[1]); y, z = glazing_axes()[n]
        _close(pos, [.0395, y, z])
        pos[0] = {'M5-glazing-bolt': .0765, 'M5-glazing-washer': .076, 'M5-glazing-insert': .0415}[family]
        if family == 'M5-glazing-bolt': rot = copy.deepcopy(REVERSE)
    elif family.startswith('glazing-'):
        pos = [{'glazing-retainer': .0735, 'glazing-seal': .0705, 'glazing-bond': .0545}[family], 0., 0.]
    elif family == 'thread-guard':
        # Source guards were unlocated at zero. Bind every guard to one real tip.
        if index < 24:
            bolt = tables['legacy/M6-bolt/'+str(index)]
            shaft = bolt['exact_CSG_entity']['geometry']['pieces'][0]
            _close([shaft['length_m'], shaft['outer_diameter_m']], [.18, .006])
            if shaft['rotation'] != REVERSE: raise ValueError('M6 bolt frame changed')
            nut = tables['legacy/M6-retained-nut/'+str(index)]
            pos = [-.115, bolt['at_m'][1], bolt['at_m'][2]]
            _close(nut['at_m'], [-.1125, pos[1], pos[2]])
            _close(shaft['at_m'], [-.0345, pos[1], pos[2]])
            rot = copy.deepcopy(REVERSE)
        else:
            bolts = sorted(k for k in tables if k.startswith('legacy/M8-bolt/'))
            bolt = tables[bolts[index-24]]
            shaft = bolt['exact_CSG_entity']['geometry']['pieces'][0]
            _close([shaft['length_m'], shaft['outer_diameter_m']], [.18, .008])
            if shaft['rotation'] != I: raise ValueError('M8 bolt frame changed')
            _close(shaft['at_m'], [-.098, bolt['at_m'][1], bolt['at_m'][2]])
            pos = [-.020, bolt['at_m'][1], bolt['at_m'][2]]
    return dict(at_m=pos, rotation=rot, frame='terminal-local-UVW')


def propose_local(raw: bytes, *, request_id: str, rates=None, materials=None, service_controls=None):
    """One new local research definition; explicit source pins, no canonical edit.

    This entry point must be separately authorised for retained data. It never
    invokes the terminal generator/adapter, composition, CAD, FEM or pricing app.
    """
    if not isinstance(raw, bytes) or len(raw) > 4*1024*1024 or hashlib.sha256(raw).hexdigest() != SOURCE['raw_sha256']:
        raise ValueError('exact retained run03 gzip required')
    if not isinstance(request_id, str) or len(request_id) != 64 or any(c not in '0123456789abcdef' for c in request_id):
        raise ValueError('explicit frozen request hash required')
    # Authenticated source is 306kB gzip / finite <64MiB decompressed, not arbitrary input.
    source = json.loads(gzip.decompress(raw))
    if source['candidate_id'] != SOURCE['candidate_id'] or source['evaluation_id'] != SOURCE['evaluation_id']:
        raise ValueError('retained definition identity mismatch')
    if any(source.get(k) is not False for k in ('physical_accepted', 'engineering_accepted', 'native_eligible', 'manufacturing_release', 'operating_release', 'selected_reference_changed')):
        raise ValueError('source maturity flags changed')
    return _compile(source, request_id, rates=RATES if rates is None else rates, materials=MATERIALS if materials is None else materials,
                    service_controls=service_controls)


def _compile(source, request_id, *, rates, materials, service_controls=None):
    """Internal implementation also tested on explicitly invented tiny rosters."""
    rates, materials = _rate_inputs(rates, materials)  # all preflight before emitting
    service_controls=_service_controls(service_controls)
    src = source['component_proposal']
    es = src['entities']; tables = {e['id']: e for e in es}
    if len(tables) != len(es): raise ValueError('duplicate source entity')
    groups=src['stock_groups'];group_ids=[g['id'] for g in groups]
    if len(group_ids)!=len(set(group_ids)):raise ValueError('duplicate source stock owner id')
    all_owned=[eid for g in groups for eid in g['entity_ids']]
    if any(not g['entity_ids'] for g in groups) or len(all_owned)!=len(set(all_owned)) or set(all_owned)!=set(tables):
        raise ValueError('source stock owner roster must cover each entity exactly once')
    ops = _source_volume_geometry(es)
    prototypes, occurrences, retirements, stock_replacements = {}, [], [], []
    for family, (part_id, count) in FAMILIES.items():
        old = sorted((e for e in es if e['part_id'] == part_id), key=lambda e: e['id'])
        if len(old) != count: raise ValueError('source family count mismatch: '+family)
        owners = [g for g in src['stock_groups'] if any(e['id'] in g['entity_ids'] for e in old)]
        if len(owners) != 1 or set(owners[0]['entity_ids']) != {e['id'] for e in old}:
            raise ValueError('exact source group retirement required')
        stock_replacements.append(dict(source_group=copy.deepcopy(owners[0]),
                                       source_group_id=owners[0]['id'], old_entity_ids=[e['id'] for e in old],
                                       successor_ids=['hardware/'+e['id'] for e in old],
                                       once_only=True, applied=False, source_price_not_added=True))
        for n, e in enumerate(old):
            if e['scope'] != 'installed' or e['exact_CSG_entity']['geometry'] is not None:
                raise ValueError('source unknown geometry/ownership changed')
            _vec(e['at_m']); _triple([e['mass_kg'][c] for c in CASES], 'source mass')
            size = ('M6' if n < 24 else 'M8') if family == 'thread-guard' else None
            key = family+('/'+size if size else '')
            if key not in prototypes:
                prototypes[key] = prototype(family, size=size, rates=rates, materials=materials)
            placement = _placement(e, family, n, tables)
            sign = -1. if family == 'M5-glazing-bolt' or family == 'M6-nut' or (family == 'M6-washer' and 'rear' in e['id']) or (family == 'M8-washer' and 'front' in e['id']) else 1.
            poses = [[0., 0., 0.], [sign*.020, 0., 0.], [sign*.050, 0., 0.]]
            occ = dict(id='hardware/'+e['id'], prototype_key=key,
                       placement=placement, old_entity_id=e['id'],
                       source_part_id=part_id, source_entity_sha256=_hash(e),
                       finite_motion_poses_part_m=poses,
                       finite_swept_diagnostic=finite_sweep_bounds(prototypes[key], placement, poses),
                       continuous_sweep_verified=False, required_clearance_m=service_controls['required_clearance_m'],
                       retention_and_repair='Capture loose hardware in counted tray; reverse assembly only after support/capture guard',
                       tool_envelope=dict(kind='axial cylinder', radius_m=service_controls['tool_envelope_radius_m'], insertion_m=service_controls['tool_insertion_m'],
                                          exact_socket_cavity_and_counterhold_required=True))
            occurrences.append(occ)
            retirements.append(dict(old_entity_id=e['id'], old_part_id=part_id, old_entity=copy.deepcopy(e),
                                    old_stock_group_id=owners[0]['id'],
                                    successor_occurrence_id=occ['id'], mode='prospective replace once, no applied source credit',
                                    old_mass_or_price_added_to_new=False, canonical_applied=False))
    for op in ops:
        owners=[g for g in groups if op['source_entity_id'] in g['entity_ids']]
        if len(owners)!=1:raise ValueError('one source machining stock owner required')
        op['source_stock_owner_id']=owners[0]['id']
        lo,hi=op['incremental_removed_volume_bounds_m3'];rho=materials['al5083']['density_kg_m3']
        mass=[lo*rho[0],hi*rho[2]];a,b=op['incremental_removed_centroid_box_m']
        op['incremental_removed_mass_bounds_kg']=mass
        op['incremental_removed_first_moment_bounds_kg_m']=[
            [min(m*x for m in mass for x in (a[k],b[k])),max(m*x for m in mass for x in (a[k],b[k]))] for k in range(3)]
        op['stock_mass_application']='Prospective subtraction from exact source owner once, gross paid stock unchanged; not applied or an exact installed saving'
        # Process only; existing paid source material is never bought twice.
        op['cost_USD'] = {c: (op['person_process_h'][i]*(rates['labour_USD_h'][i]+rates['machine_USD_h'][i])+
                              op['person_QA_h'][i]*rates['QA_USD_h'][i])*(1+rates['overhead_fraction'][i]) for i, c in enumerate(CASES)}
    physical_ops = []
    for op in ops:
        own = {k:copy.deepcopy(op[k]) for k in ('id','kind','source_entity_id','source_stock_owner_id','complete_void_union')}
        keys=('geometry','holes','material','insert_pocket_max_depth_m','insert_pocket_max_diameter_m') if op['kind']=='hardpoint-thread-pocket' else ('geometry','holes')
        own['source_material_geometry'] = {k:copy.deepcopy(op['source_geometry'][k]) for k in keys}
        if op['kind']=='hardpoint-thread-pocket':
            own.update({k:op[k] for k in ('maximum_pocket_depth_m','minimum_annular_rear_web_m')})
        else:own.update(access_diameter_m=op['access_diameter_m'],diameter_tolerance_m=op['diameter_tolerance_m'],
                        axis_position_tolerance_m=op['axis_position_tolerance_m'],material='al5083')
        physical_ops.append(own)
    physical = dict(schema='osr-terminal-hardware-local-physical/2', parent_candidate_id=SOURCE['candidate_id'],
                    fixed_source_interfaces=['retained-glass', 'backing-ring outer/aperture/pose (bores explicitly revised)', 'body frame'],
                    new_prototypes={k: v['physical_definition'] for k, v in prototypes.items()},
                    placements=[{k:copy.deepcopy(o[k]) for k in ('id','prototype_key','placement','old_entity_id','source_part_id')} for o in occurrences],
                    source_machining=physical_ops,
                    prospective_replacements=[dict(old=r['old_entity_id'], new=r['successor_occurrence_id']) for r in retirements])
    known = {c: sum(prototypes[o['prototype_key']]['cost_USD'][c] for o in occurrences)+sum(op['cost_USD'][c] for op in ops) for c in CASES}
    workshop = dict(scope='shared workshop equipment, not installed per end',
                    count=dict(captive_hardware_tray=1, M6_spanner=2, M8_spanner=2, M5_socket=1,
                               captive_fork_service_kit=1, AF3p5_stud_spanner=1,AF8_jamnut_spanners=2,
                               AF22_fork_spanner=1,AF5p5_service_driver=1,
                               compound_dispensing_gun=1, adhesive_cutting_wire=1,
                               glazing_suction_cups=2, glazing_support_cradle=1, receiver_depth_fixture=1,
                               ring_port_12mm_cutter=1, receiver_7mm_flatbottom_pilot=1, M8x1_tap=1,
                               port_diameter_gauge=1),
                    mass_kg=None, geometry=None, mass_and_access_required=True,
                    tooling_allowance_USD=_cases([120., 240., 480.]),
                    allocation='TRAIN-ONCE residual shared workshop allowance EXCLUDES separately calculated captive service kit; never per-end installed material',
                    prior_bf_allowance_USD=_cases([120.,240.,480.]),
                    prior_allowance_disposition='Superseded estimate, not an extra charge; revised scope excludes detailed service kit')
    toolkit=front_service_toolkit(rates=rates,materials=materials)
    service_access=front_service_screen(access_diameter_m=RING_ACCESS_DIAMETER_M,
        diameter_tolerance_m=RING_ACCESS_DIAMETER_TOLERANCE_M,required_clearance_m=service_controls['required_clearance_m'])
    service_access['coaxiality_target_verified']=False
    service_access['topology_comparison']=support_topology_comparison()
    service_access['predecessor_source_commit']='bf1035bc79e44c58cdcc59fe96d5c4d21255e391'
    service_access['independent_hold_review_id']='8bf79d76a7be1d452f1590ecc6e31df1b2bb5c1bc179493754323301a42e6466'
    tool_definition=dict(schema='osr-terminal-workshop-tool-physical/1',scope='One shared workshop kit, not installed railway material',
        parts=[dict(id=p['id'],material=p['material'],geometry=p['geometry'],paid_blank=p['paid_blank'],
                    gross_volume_m3=p['gross_blank_volume_m3'],net_volume_bounds_m3=p['net_volume_bounds_m3']) for p in toolkit['parts']])
    toolkit['lifecycle_definition_id']=_hash(tool_definition);toolkit['physical_definition']=tool_definition
    service_evaluation=dict(schema='osr-terminal-service-evaluation/1',controls=service_controls,access=service_access,
        tool_lifecycle_definition_id=toolkit['lifecycle_definition_id'],
        motions_and_envelopes=[dict(occurrence_id=o['id'],poses=o['finite_motion_poses_part_m'],
            finite_diagnostic=o['finite_swept_diagnostic'],tool=o['tool_envelope'],required_clearance_m=o['required_clearance_m']) for o in occurrences])
    service_evaluation['evaluation_id']=_hash(service_evaluation)
    repair_keys=('glazing-seal','glazing-bond','M5-glazing-insert')
    repair_consumables=dict(scope='ONE glazing strip/refit service event, not per insert or an assumed annual rate',
        counts=dict(new_seal_ring=1,new_bond_ring=1,insert_compound_dose_per_replaced_insert=1),
        seal_and_bond_replacement_cost_USD={c:sum(prototypes[k]['cost_USD'][c] for k in repair_keys[:2]) for c in CASES} if all(k in prototypes for k in repair_keys[:2]) else None,
        annual_event_frequency=None,staffing_person_hours=None,
        holds=['Seal/bond consumed during glazing removal, never presumed reusable or costfree',
               'Compound must be reversible-service grade; actual cure/breakaway torque and toolkit structural/capture capacity remain unknown',
               'Glazing lifting/support/operator/staffing and service frequency need a separate evaluated plan'])
    result = dict(schema='osr-terminal-hardware-local-proposal/1', candidate_id=_hash(physical), request_id=request_id,
                  physical_definition=physical, parent=copy.deepcopy(SOURCE), prototypes=prototypes,
                  occurrences=occurrences, replacement_plan=retirements, source_machining=ops,
                  source_stock_owner_replacements=stock_replacements,
                  source_machining_stock_owners={g['id']:copy.deepcopy(g) for g in groups if any(o['source_stock_owner_id']==g['id'] for o in ops)},
                  service_evaluation=service_evaluation,shared_workshop_service_kit=toolkit,
                  repair_consumables_per_glazing_service=repair_consumables,
                  new_parts_cost_USD=known, complete_installed_cost=False,
                  new_parts_mass_kg={c: sum(prototypes[o['prototype_key']]['mass_kg'][c] for o in occurrences) for c in CASES},
                  cost_scope='New hardware/glazing stock + finishing only. Existing source material retained; per-end subtotal is not full terminal price.',
                  original_source_accounting=copy.deepcopy(source['source_accounting_retained']),
                  original_source_coverage=copy.deepcopy(src['source_account_coverage']),
                  counted_joints=dict(panel_M6=24, body_M8=8, glazing_M5=12, threaded_guards=32,
                                      insert_external_M8=12, seal_ring=1, bond_ring=1, retainer_corner_welds=0),
                  wiring_cooling_and_bearings=dict(added_count=0, basis='These passive hardware families add no service circuits or rotating joints; retained equipment unchanged'),
                  workshop=workshop, assembly_sequence=[
                      'Fixture ONE paid source backing ring, enlarge12known5.5mmports to12mm before attachment; deburr/gauge both faces and retain source attachment obligations',
                      'Through enlarged ports, machine12own stopped receiver pockets in hardpoints while retaining every6mmthrough-void; gauge/depth/clean before glazing',
                      'Install12 slotted M8/M5 inserts with counted captive fork kit; cure specified compound under qualification hold',
                      'Apply6mm rear silicone ring with controlled temporary support; install fixed glass at unchanged57.5..69.5mm faces',
                      'Apply2.5mm free EPDM ring at front; compress to2mm using own4mm retainer and12 M5 bolts/washers',
                      'Fit panel/body source bolts with proposed nuts/washers; fit24 M6 and8 M8 closed thread caps after torque/inspection',
                      'Removal: support glass with2 cups+cradle, remove/capture caps, bolts, washers and retainer; peel seal/cut bond and extract glass before insert service',
                      'For insert repair, stage headlessM5drawstud/nuts then separately attach squarekeyplate/standoffs, unthread9turns/9mm and withdraw through12mmport; no free ring-weld removal',
                  ], holds=copy.deepcopy(HOLDS)+[
                      'Receiver cut union/incremental mass must be applied once to source hardpoints in a fresh physical composition',
                      'ONE backing-ring owner needs its12additional cut union/netmass/process update applied once; ring/adhesive/retention structural loads remain unqualified',
                      'Ring-only necessary geometric screen passes at declared dimensions; full vehicle/service-tool/helix/torque/capture qualification remains open',
                      'Glass temporary support, cure tooling and continuous extraction not collision-verified; no lifting capacity claim',
                      'Finite hardware poses are proposals and do not validate actual prior32 unlocated guard anchors',
                      'Original183 unoriented weld/89 joint obligations and all unmodified source assembly holds remain open',
                  ],
                  physical_accepted=False, engineering_accepted=False, native_eligible=False,
                  manufacturing_release=False, operating_release=False, composition_admitted=False,
                  selected_reference_changed=False, selection_id=None)
    result['evaluation_id'] = _hash(result)
    return result
