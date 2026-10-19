"""Revision-bound complete-kit gravity reaction research envelope.

Signed equilibrium is verified independently of component resistance. The two
track decks are idealised as independent, simply supported rigid transverse
distributors. This is not a stiffness, moving-axle, uplift-contact or ground model.
Unspecified actions are mandatory holds, never zero-load passing cases.
"""
import math

from engineering.twin_workflow import core
from engineering.continuous_design import civil_kit


SUPERSTRUCTURE = {'deck', 'track-support', 'walkway-parapet', 'service'}
SUBSTRUCTURE = {'bearing', 'pier-cap', 'pier', 'foundation-cap', 'pile', 'pile-cage'}
ACTION_HOLDS = {
    'braking-traction': 'Approved longitudinal train forces, restraint layout and combinations absent',
    'thermal-restraint': 'Free expansion alone gives no restraint force; bearing stiffness/fixed-guided-free layout absent',
    'wind': 'Site wind, aerodynamic coefficients and concurrent train criteria absent',
    'seismic': 'Site hazard, ground class, response spectrum and ductility model absent',
    'uplift-contact': 'Signed gravity forces retained; tension-capable details/contact analysis absent',
    'erection': 'Stage-specific support, lift/temporary loads, prestress and strength development absent',
    'railway-dynamic-axle-fatigue': 'Approved axle map, dynamic factors, passage histories and fatigue combinations absent',
    'ground-response': 'Site-zoned ground, settlement and pile-group resistance absent',
    'unrepresented-permanent-items': 'Complete rail, drainage contents, cables, finishes and connections need quantity reconciliation against retained allowances',
}


def _positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError('positive finite '+name+' required')
    return float(value)


def revisioned(value):
    """Bind an explicit provisional configuration without an approval implication."""
    return dict(value, revision=core.digest(value))


def _revision(value, name):
    if not isinstance(value, dict) or value.get('revision') != core.digest({k:v for k,v in value.items() if k != 'revision'}):
        raise ValueError(name+' revision/configuration differs')


def _centre(unit):
    return [(a+b)/2 for a,b in zip(*unit['bounds_m'])]


def _wrench(force, point, origin=(0.,0.,0.)):
    x,y,z = [a-b for a,b in zip(point,origin)];fx,fy,fz = force
    return list(force)+[y*fz-z*fy,z*fx-x*fz,x*fy-y*fx]


def _sum(rows):
    return [sum(row[i] for row in rows) for i in range(6)]


def distribute_vertical(force_n, point_m, bearings):
    """Bilinear signed point reaction; extrapolation preserves eccentric moments.

    Four rectangular supports are required. Negative reactions are retained;
    clipping a negative reaction would conceal loss of contact and equilibrium.
    """
    if len(bearings) != 4 or not math.isfinite(force_n) or len(point_m) != 3 or not all(math.isfinite(x) for x in point_m):
        raise ValueError('finite force/point and four supports required')
    xs=sorted({b['position_m'][0] for b in bearings});ys=sorted({b['position_m'][1] for b in bearings})
    if len(xs)!=2 or len(ys)!=2 or {(b['position_m'][0],b['position_m'][1]) for b in bearings}!={(x,y) for x in xs for y in ys}:
        raise ValueError('rectangular independent-track support configuration required')
    x,y,_=point_m
    return {b['id']:force_n*((xs[1]-x)/(xs[1]-xs[0]) if b['position_m'][0]==xs[0] else (x-xs[0])/(xs[1]-xs[0]))*
        ((ys[1]-y)/(ys[1]-ys[0]) if b['position_m'][1]==ys[0] else (y-ys[0])/(ys[1]-ys[0])) for b in bearings}


def envelope(kit, train, seat, *, expected_kit_revision, expected_train_revision):
    """Return complete retained mass ledger, explicit combinations and reactions.

    ``seat`` replaces each existing kit bearing unit with the exact represented
    seat candidate mass. This prevents adding the bought-out bearing twice.
    Section resultants include all substructure self-mass through pile toes;
    individual pile allocation and soil reaction remain unanalysed.
    """
    if core.digest(kit)!=expected_kit_revision:
        raise ValueError('civil kit revision differs')
    _revision(train,'train');_revision(seat,'seat')
    if train['revision']!=expected_train_revision:
        raise ValueError('train revision differs')
    required={'architecture','mass_cases_kg','cars','car_length_m','tracks','span_m','gravity_m_s2','permanent_factor','variable_factor','revision'}
    if set(train)!=required or train['architecture']!='baghdad-six-car' or train['cars']!=6 or train['tracks']!=2 or train['span_m']!=20.:
        raise ValueError('complete supported Baghdad train/configuration required')
    if set(seat)!={'candidate_revision','mass_kg','revision'} or not isinstance(seat['candidate_revision'],str) or len(seat['candidate_revision'])!=64 or any(c not in '0123456789abcdef' for c in seat['candidate_revision']):
        raise ValueError('exact seat candidate revision required')
    for name in ('car_length_m','gravity_m_s2','permanent_factor','variable_factor'):_positive(train[name],name)
    _positive(seat['mass_kg'],'seat mass')
    if not isinstance(train['mass_cases_kg'],list) or not train['mass_cases_kg']:
        raise ValueError('explicit train mass cases required')
    for mass in train['mass_cases_kg']:_positive(mass,'train mass')
    try:
        kit_valid=all(civil_kit.validate_kit(kit).values())
    except (KeyError,TypeError,ValueError,IndexError) as exc:
        raise ValueError('civil kit missing required load/revision/support record') from exc
    if not kit_valid:
        raise ValueError('civil kit incomplete, stale or invalid mass/support ledger')
    units={u['id']:u for u in kit['units']}
    if {u['category'] for u in units.values()}-SUPERSTRUCTURE-SUBSTRUCTURE:
        raise ValueError('unmapped civil load category; provide structural allocation')
    if kit['variables']['station_package']:
        raise ValueError('station load path requires its own controlled interface')
    bearings=[dict(id=u['id'],position_m=_centre(u),unit_revision=u['revision'],support_ids=u['support_ids']) for u in units.values() if u['category']=='bearing']
    if len(bearings)!=8 or any(len(b['support_ids'])!=1 for b in bearings):
        raise ValueError('eight bearings with exact cap connectivity required')
    tracks={track:[b for b in bearings if (b['position_m'][1]<0)==(track==1)] for track in (1,2)}
    # Assert rectangular support placement before evaluating any load case.
    for supports in tracks.values():distribute_vertical(1.,[10.,0.,0.],supports)
    parts={p['id']:p for p in kit['physical_contract']['parts']}
    ledger=[]
    for uid,u in sorted(units.items()):
        _positive(u['mass_kg'],'kit unit mass')
        point=_centre(u)
        if u['defined_mass_kg']>0:
            # Material centroid is retained; source allowances use the explicit
            # unit-envelope centroid and remain a separate uncertainty hold.
            point=[(sum(parts[p]['properties']['mass_kg']*parts[p]['properties']['cg_m'][i] for p in u['physical_part_ids'])+u['allocated_mass_kg']*point[i])/u['mass_kg'] for i in range(3)]
        replacement=u['category']=='bearing'
        ledger.append(dict(id=uid,unit_revision=u['revision'],category=u['category'],position_m=point,
            defined_mass_kg=u['defined_mass_kg'],allocated_mass_kg=u['allocated_mass_kg'],
            source_mass_kg=u['mass_kg'],applied_mass_kg=seat['mass_kg'] if replacement else u['mass_kg'],
            replacement_candidate_revision=seat['candidate_revision'] if replacement else None,
            allocation='Exact represented seat bundle replaces original bearing envelope' if replacement else 'Defined material plus retained source allowances',
            support_ids=u['support_ids']))
    if abs(sum(r['source_mass_kg'] for r in ledger)-kit['mass_ledger']['installed_study_mass_kg'])>1e-5:
        raise ValueError('complete permanent mass ledger differs')
    track_mass=sum(r['source_mass_kg'] for r in ledger if r['category']=='track-support')
    if abs(track_mass-kit['mass_ledger']['retained_track_budget_kg'])>1e-5:
        raise ValueError('retained rail/trackform mass missing or duplicated')
    combinations=[dict(id='permanent-characteristic',train_mass_kg=0.,G=1.,Q=0.,basis='Unfactored retained gravity, no live train')]
    for mass in train['mass_cases_kg']:
        combinations.extend([dict(id='planning-characteristic-'+str(mass),train_mass_kg=mass,G=1.,Q=1.,basis='Uniform simultaneous two-track planning train; no adopted railway combination'),
            dict(id='research-factored-'+str(mass),train_mass_kg=mass,G=train['permanent_factor'],Q=train['variable_factor'],basis='Explicit provisional screen factors; not a code-adopted combination')])
    cases=[];g=train['gravity_m_s2']
    for combination in combinations:
        forces={b['id']:0. for b in bearings};applied=[];entries=[]
        for row in ledger:
            if row['category'] not in SUPERSTRUCTURE|{'bearing'}:continue
            force=row['applied_mass_kg']*g*combination['G'];point=row['position_m']
            distribution={row['id']:force} if row['category']=='bearing' else distribute_vertical(force,point,tracks[1 if point[1]<0 else 2])
            for uid,value in distribution.items():forces[uid]+=value
            applied.append(_wrench([0.,0.,-force],point));entries.append(dict(load_id='G/'+row['id'],force_down_n=force,point_m=point,bearing_contributions_n=distribution))
        for track in (1,2):
            force=combination['train_mass_kg']*train['span_m']/(train['cars']*train['car_length_m'])*g*combination['Q']
            point=[10.,sum(b['position_m'][1] for b in tracks[track])/4,10.]
            distribution=distribute_vertical(force,point,tracks[track])
            for uid,value in distribution.items():forces[uid]+=value
            applied.append(_wrench([0.,0.,-force],point));entries.append(dict(load_id='Q/train-track-'+str(track),force_down_n=force,point_m=point,bearing_contributions_n=distribution))
        reactions=[dict(bearing_id=b['id'],unit_revision=b['unit_revision'],seat_candidate_revision=seat['candidate_revision'],position_m=b['position_m'],force_n=[0.,0.,forces[b['id']]],moment_nm=[0.,0.,0.]) for b in bearings]
        applied_wrench=_sum(applied);reaction_wrench=_sum([_wrench(r['force_n'],r['position_m']) for r in reactions]);residual=[a+b for a,b in zip(applied_wrench,reaction_wrench)]
        scale=max(1.,max(abs(x) for x in applied_wrench));balanced=max(abs(x) for x in residual)<=1e-10*scale
        # Retain signed wrenches at cap, column, foundation cap and pile-toe
        # reference cuts. Section transfer includes eccentricity rather than
        # silently assuming column/foundation moments to be zero.
        sections=[]
        for support,x in ((0,0.),(1,20.)):
            top=[r for r in reactions if r['bearing_id'].startswith('S'+str(support)+'-')]
            local=[r for r in ledger if r['id'].startswith('S'+str(support)+'-') and r['category']!='bearing']
            for name,categories,z in (
                ('pier-cap-base',{'pier-cap'},8.),
                ('column-base',{'pier-cap','pier'},0.),
                ('foundation-cap-base',{'pier-cap','pier','foundation-cap'},-1.5),
                ('pile-toes',{'pier-cap','pier','foundation-cap','pile','pile-cage'},min(u['bounds_m'][0][2] for u in units.values() if u['id'].startswith('S'+str(support)+'-') and u['category']=='pile'))):
                origin=[x,0.,z];wrenches=[_wrench([-v for v in r['force_n']],r['position_m'],origin) for r in top]
                wrenches += [_wrench([0.,0.,-r['applied_mass_kg']*g*combination['G']],r['position_m'],origin) for r in local if r['category'] in categories]
                sections.append(dict(support_id='S'+str(support),section=name,origin_m=origin,downstream_demand_wrench=_sum(wrenches),
                    included_self_mass_ids=[r['id'] for r in local if r['category'] in categories],
                    scope='Signed global section resultant only; member stiffness, individual cap/pile sharing and ground resistance not verified'))
        cases.append(dict(**combination,loads=entries,bearing_reactions=reactions,section_resultants=sections,
            global_applied_wrench=applied_wrench,global_reaction_wrench=reaction_wrench,equilibrium_residual=residual,
            equilibrium_pass=balanced,negative_reaction_bearing_ids=[uid for uid,value in forces.items() if value<0.]))
    demands={b['id']:dict(maximum_compression_n=max(c['bearing_reactions'][i]['force_n'][2] for c in cases),
        minimum_signed_reaction_n=min(c['bearing_reactions'][i]['force_n'][2] for c in cases)) for i,b in enumerate(bearings)}
    result=dict(schema='osr-civil-reaction-envelope/1',architecture=train['architecture'],kit_revision=expected_kit_revision,
        train_revision=train['revision'],seat_revision=seat['revision'],seat_candidate_revision=seat['candidate_revision'],
        unit_revisions={u['id']:u['revision'] for u in units.values()},permanent_load_ledger=ledger,
        track_support_mass_kg=track_mass,permanent_applied_mass_kg=sum(r['applied_mass_kg'] for r in ledger),
        combinations=cases,bearing_demands=demands,mandatory_action_holds=dict(ACTION_HOLDS),
        checks=dict(complete_retained_mass_ledger=True,retained_track_allocation=True,signed_gravity_equilibrium=all(c['equilibrium_pass'] for c in cases)),
        unresolved=['Retained allowances have provisional unit-envelope centroids', 'Independent transverse deck distribution is a hypothesis; torsion/stiffness/contact must be evaluated']+list(ACTION_HOLDS.values()),
        scope='Complete retained-kit gravity equilibrium under explicit provisional combinations; non-gravity, dynamic, construction and ground acceptance remain on hold',**core.FLAGS)
    result['revision']=core.digest(result)
    return result
