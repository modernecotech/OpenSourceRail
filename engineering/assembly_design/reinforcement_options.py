"""Round bent-link/coupler alternatives on the exact retained cap envelope.

Centreline schedules are design definitions, not fabricated or qualified bars.
Curved links are held out of native/cap selection until their geometry, hooks,
development, congestion, resistance and fabrication method are confirmed.
"""
import math
from engineering.twin_workflow import core


def build(candidate):
    if candidate['definition_sha256']!=core.digest({k:v for k,v in candidate.items() if k!='definition_sha256'}):
        raise ValueError('exact source cap-cage revision required')
    lo,hi=candidate['source_unit']['bounds_m'];W=hi[0]-lo[0];H=hi[2]-lo[2]
    cx=(lo[0]+hi[0])/2;cz=(lo[2]+hi[2])/2;diameter=.012;cover=.05
    rows=[]
    for mandrel_factor in (4.,6.,8.):
        radius=(mandrel_factor*diameter+diameter)/2
        width=W-2*cover-diameter;height=H-2*cover-diameter
        if 2*radius>=min(width,height):continue
        straight=2*(width+height-4*radius)
        arc=2*math.pi*radius
        for connection in ('135-degree-hooks','two-U-bars-and-couplers'):
            tails=2*10*diameter if connection=='135-degree-hooks' else 0.
            # Hook returns have their own135deg arcs, in addition to the four
            # rectangular corners. They are not silently counted as straight.
            hook_arc=2*math.radians(135)*radius if tails else 0.
            cut=straight+arc+tails+hook_arc
            arc_centres=[[cx+sx*(width/2-radius),cz+sz*(height/2-radius)] for sx,sz in ((-1,-1),(1,-1),(1,1),(-1,1))]
            clearances=[]
            for bar in candidate['metadata']['bars']:
                distances=[]
                for ax,az in arc_centres:
                    # A conservative full-circle exclusion around each bend;
                    # exact quarter-arc/hook/coupler placement remains open.
                    distance=abs(math.hypot(bar['x_m']-ax,bar['z_m']-az)-radius)
                    distances.append(distance-math.sqrt(bar['area_m2']/math.pi)-diameter/2)
                clearances.append(dict(bar_id=bar['id'],minimum_conservative_bend_clearance_m=min(distances)))
            rows.append(dict(id='round-link-'+str(int(mandrel_factor))+'d-'+connection,
                source_candidate_revision=candidate['revision'],diameter_m=diameter,
                mandrel_diameter_m=mandrel_factor*diameter,centreline_bend_radius_m=radius,
                mandrel_basis='Explicit fabrication hypotheses, not an adopted code minimum',
                centreline_width_m=width,centreline_height_m=height,
                quarter_arc_centres_xz_m=arc_centres,link_stations_y_m=candidate['metadata']['link_positions_y_m'],
                rectangular_straights_m=straight,corner_arcs_m=arc,hook_arcs_m=hook_arc,hook_tails_m=tails,
                proposed_bar_cut_length_m=cut,bar_mass_each_kg=math.pi*diameter**2/4*cut*7850.,
                hook_basis='Two135deg closures and10d tails are unqualified space reservations; exact overlap and development require issued bend detail',
                connection=connection,couplers_per_link=2 if connection=='two-U-bars-and-couplers' else 0,
                coupler_mass_each_kg=None,coupler_supplier=None,
                bend_clearances=clearances,existing_main_bar_layout_clear=min(r['minimum_conservative_bend_clearance_m'] for r in clearances)>=.002,
                assembly_sequence=(['Prebend round links on controlled mandrel','Thread main bars through links before end hardware','Tie, inspect cover and closures']
                    if connection=='135-degree-hooks' else ['Prebend two U-bars','Place around main bars from opposite sides','Complete exact rated couplers with tool access','Inspect engagement and lock marks']),
                inspections=['bar heat and ductility','mandrel and springback','bend dimensions and clear cover','hook development or coupler engagement','congestion and concrete placement access'],
                factory_hours=None,installed_cost_usd=None,complete_installed_mass_kg=None,
                native_state='hold-unimplemented-curved-bar-adapter',eligible_for_cap_selection=False,
                required_evidence=['native round-bar and closure geometry','actual end development and cap-segment joint',
                    'bend ductility and confinement','rail fatigue, seismic and connection applicability',
                    'bar repositioning and recalculated section response if congestion requires it'],**core.FLAGS))
    result=dict(schema='osr-cap-reinforcement-alternatives/1',source_candidate_revision=candidate['revision'],alternatives=rows,
        retained_fabricated_link_preserved=True,
        sources=[dict(url='https://www.fhwa.dot.gov/bridge/pubs/hif17019.pdf',
            applicability='Prefabricated bridge connection/coupler guidance only; railway and local adoption require review')],
        scope='Six explicit round bent-bar connection proposals; bar-only masses do not establish complete cap or installed savings. Congested bends remain rejected for the existing main-bar layout.',**core.FLAGS)
    result['revision']=core.digest(result);return result
