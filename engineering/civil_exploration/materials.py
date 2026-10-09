"""Material-region matrices with explicit perfect-bond screening assumptions."""
from __future__ import annotations
import math


def elastic_matrix(section, records, reference_E):
    """Transformed area/inertia; every region must have an explicit material."""
    regions = section['regions']; roles = section['material_roles']
    missing = set(roles)-records.keys()
    if missing:
        raise ValueError('missing material records: '+', '.join(sorted(missing)))
    rows = []
    for r, role in zip(regions, roles):
        m = records[role]
        if m.get('orthotropic'):
            from .orthotropic import validate
            validate(m['orthotropic'])
            if not math.isclose(m['youngs_modulus_pa'],m['orthotropic']['ex_pa']):raise ValueError('frame longitudinal modulus differs from orthotropic matrix')
        for field in ('youngs_modulus_pa', 'density_kg_m3'):
            if type(m[field]) not in (float, int) or not math.isfinite(m[field]) or m[field] <= 0:
                raise ValueError('invalid material property: '+field)
        if not 0 <= m['poisson_ratio'] < .5 or not m['basis']:
            raise ValueError('material requires a valid Poisson ratio and provenance basis')
        A = r['width_m']*r['height_m']; E = m['youngs_modulus_pa']*m.get('stiffness_factor', 1.)
        rows.append((r, m, A, E))
    EA = math.fsum(a*e for _, _, a, e in rows)
    neutral = math.fsum(a*e*r['z_m'] for r, _, a, e in rows)/EA
    EI = math.fsum(e*a*(r['height_m']**2/12+(r['z_m']-neutral)**2) for r, _, a, e in rows)
    Gref=reference_E/(2*(1+records['concrete']['poisson_ratio']))
    GA=math.fsum((m['orthotropic']['gxz_pa']*m.get('stiffness_factor',1.) if m.get('orthotropic') else e/(2*(1+m['poisson_ratio'])))*a for _,m,a,e in rows)
    return dict(area_m2=EA/reference_E, inertia_y_m4=EI/reference_E, neutral_axis_z_m=neutral,
                effective_EA_n=EA,effective_EI_nm2=EI,
                shear_area_m2=section['shear_area_m2']*GA/(Gref*section['area_m2']),
                fibre_stress_per_moment= max(e*max(abs(r['z_m']-r['height_m']/2-neutral),abs(r['z_m']+r['height_m']/2-neutral))/EI for r,_,a,e in rows),
                fibre_stress_per_axial=max(e/EA for _,_,a,e in rows),
                mass_kg_m=math.fsum(a*m['density_kg_m3'] for _, m, a, _ in rows),
                region_properties=[dict(material=role, **m) for role, (_, m, _, _) in zip(roles, rows)],
                bond_model='perfect-bond screening', physical_validation=False,
                uncovered=['interface slip', 'orthotropic local failure', 'creep and fatigue', 'connection resistance'])


def prestress(section, inputs):
    """Transparent analytical loss budget and gross-section stress/camber."""
    required = {'initial_force_n', 'tendon_area_m2', 'tendon_modulus_pa', 'eccentricity_m', 'span_m',
                'friction_mu', 'angular_change_rad', 'wobble_per_m', 'anchor_slip_m',
                'shortening_strain', 'creep_strain', 'shrinkage_strain', 'relaxation_fraction', 'concrete_modulus_pa', 'basis'}
    if set(inputs) != required:
        raise ValueError('prestress input coverage mismatch')
    if any(type(v) not in (int, float) or not math.isfinite(v) for k, v in inputs.items() if k != 'basis'):
        raise ValueError('nonfinite prestress input')
    if not inputs['basis'] or min(inputs[k] for k in ('initial_force_n','tendon_area_m2','tendon_modulus_pa','span_m','concrete_modulus_pa')) <= 0:
        raise ValueError('prestress needs positive dimensions/properties and a basis')
    if any(inputs[k] < 0 for k in ('friction_mu','angular_change_rad','wobble_per_m','anchor_slip_m','shortening_strain','creep_strain','shrinkage_strain')) or not 0 <= inputs['relaxation_fraction'] < 1:
        raise ValueError('invalid loss input')
    P, Ap, Ep, length = (inputs[k] for k in ('initial_force_n','tendon_area_m2','tendon_modulus_pa','span_m'))
    losses = dict(friction_n=P*(1-math.exp(-inputs['friction_mu']*inputs['angular_change_rad']-inputs['wobble_per_m']*length)),
                  anchorage_n=Ap*Ep*inputs['anchor_slip_m']/length,
                  shortening_n=Ap*Ep*inputs['shortening_strain'], creep_n=Ap*Ep*inputs['creep_strain'],
                  shrinkage_n=Ap*Ep*inputs['shrinkage_strain'], relaxation_n=P*inputs['relaxation_fraction'])
    effective = P-math.fsum(losses.values())
    if effective <= 0:
        raise ValueError('losses consume all prestress')
    e = inputs['eccentricity_m']; A, I = section['area_m2'], section['inertia_y_m4']
    return dict(losses=losses, effective_force_n=effective,
                top_stress_pa=-effective/A+effective*e*(section['top_m']-section['centroid_z_m'])/I,
                bottom_stress_pa=-effective/A-effective*e*(section['centroid_z_m']-section['bottom_m'])/I,
                camber_m=effective*e*length**2/(8*inputs['concrete_modulus_pa']*I),
                assumptions='constant eccentricity, gross elastic section, user-supplied loss strains; no design acceptance',
                physical_release=False)


def fatigue_damage(cycles, sn_points):
    """Miner damage for supplied stress-range counts and measured S-N records."""
    if len(sn_points) < 2 or any(min(r['range_pa'], r['cycles']) <= 0 for r in sn_points):
        raise ValueError('S-N curve needs positive measured points')
    points = sorted(sn_points, key=lambda r: r['range_pa'])
    damage = 0.; unresolved = []
    for cycle in cycles:
        stress, count = cycle['range_pa'], cycle['count']
        if not math.isfinite(stress+count) or stress < 0 or count < 0:
            raise ValueError('invalid fatigue cycle')
        if stress == 0:
            continue
        pair = next(((a, b) for a, b in zip(points, points[1:]) if a['range_pa'] <= stress <= b['range_pa']), None)
        if pair is None:
            unresolved.append(cycle); continue
        a, b = pair
        fraction = math.log(stress/a['range_pa'])/math.log(b['range_pa']/a['range_pa'])
        life = math.exp(math.log(a['cycles'])+fraction*math.log(b['cycles']/a['cycles']))
        damage += count/life
    return dict(miner_damage=damage if not unresolved else None, uncovered_cycles=unresolved,
                model='supplied cycle spectrum; log-log interpolation, no extrapolation or automatic fatigue acceptance')
