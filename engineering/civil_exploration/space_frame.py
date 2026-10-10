"""Native 3D Timoshenko tracks, flexible transverse caps and finite bearings.

Uniform planning loads only. Saint-Venant/closed-cell torsion and linear soil
are screening formulations; warping, distortion and cyclic capacity stay open.
"""
from __future__ import annotations
import math

from osr_mech.civil.exploration import geometry,foundation_geometry,hollow_regions,rectangle,section_properties
from .model import takeoff,deck_physics,pier_physics,cement_area,mesh_positions
from .section_mechanics import matrix


def run(candidate,study,longitudinal,transverse,kn_m_per_track,loaded_tracks=2,mesh=8,*,braking_fraction=0.):
    import openseespy.opensees as ops
    if loaded_tracks not in (1,2) or type(mesh) is not int or not 4<=mesh<=64 or kn_m_per_track<0 or not 0<=braking_fraction<=1:raise ValueError('3D planning load/mesh outside domain')
    ops.wipe();ops.model('basic','-ndm',3,'-ndf',6)
    ops.geomTransf('Linear',1,0.,0.,1.);ops.geomTransf('Linear',2,1.,0.,0.)
    geo=geometry(candidate['definition']);q=takeoff(candidate,study);a=candidate['mass_allowances']
    span=candidate['definition']['deck']['span_m'];height=candidate['definition']['pier']['height_m']
    material=candidate['material'];support=candidate.get('support_material',material);foundation=candidate.get('foundation_material',support)
    records={'concrete':material,**candidate.get('material_records',{})};support_records={**records,'concrete':support}
    E=material['youngs_modulus_pa']*material['stiffness_factor'];G=E/(2*(1+material['poisson_ratio']))
    coordinates={};elements=[];links=[];fixed=[];gravity=[];line_gravity=[];node_id=element_id=mat_id=0
    def node(x,y,z):
        nonlocal node_id
        node_id+=1;ops.node(node_id,x,y,z);coordinates[node_id]=[x,y,z];return node_id
    def rigid(first,second,kind):
        ops.rigidLink('beam',first,second);links.append(dict(first=first,second=second,kind=kind))
    def spring(first,second,ks,dirs,kind):
        nonlocal element_id,mat_id
        tags=[]
        for k in ks:mat_id+=1;ops.uniaxialMaterial('Elastic',mat_id,k);tags.append(mat_id)
        element_id+=1;ops.element('zeroLength',element_id,first,second,'-mat',*tags,'-dir',*dirs)
        elements.append(dict(id=element_id,kind=kind,nodes=[first,second],stiffness=ks,directions=dirs))
    def beam(first,second,section,materials,kind,transf,closed=False,mass=0.):
        nonlocal element_id
        s=matrix(section,materials,closed);roles=section.get('material_roles',['concrete']*len(section['regions']))
        area=section['area_m2'];GAy=GAz=0.
        for r,role in zip(section['regions'],roles):
            m=materials[role];localE=m['youngs_modulus_pa']*m.get('stiffness_factor',1.);localG=localE/(2*(1+m['poisson_ratio']))
            RA=r['width_m']*r['height_m'];factor=m.get('stiffness_factor',1.)
            GAy+=(m['orthotropic']['gxy_pa']*factor if m.get('orthotropic') else localG)*RA*5/6
            GAz+=(m['orthotropic']['gxz_pa']*factor if m.get('orthotropic') else localG)*RA*section['shear_area_m2']/area
        element_id+=1
        ops.element('ElasticTimoshenkoBeam',element_id,first,second,E,G,s['EA_n']/E,s['GJ_nm2']/G,s['EIy_nm2']/E,s['EIz_nm2']/E,GAy/G,GAz/G,transf)
        stress_factor_y=max(m['youngs_modulus_pa']*m.get('stiffness_factor',1.)*(abs(r['z_m']-s['centroid_z_m'])+r['height_m']/2)/s['EIy_nm2'] for r,role in zip(section['regions'],roles) for m in [materials[role]])
        stress_factor_z=max(m['youngs_modulus_pa']*m.get('stiffness_factor',1.)*(abs(r['y_m']-s['centroid_y_m'])+r['width_m']/2)/s['EIz_nm2'] for r,role in zip(section['regions'],roles) for m in [materials[role]])
        stress_factor_n=max(materials[role]['youngs_modulus_pa']*materials[role].get('stiffness_factor',1.)/s['EA_n'] for role in roles)
        elements.append(dict(id=element_id,kind=kind,nodes=[first,second],properties=s,mass_kg_m=mass,
                             stress_factors=[stress_factor_n,stress_factor_y,stress_factor_z]))
        if mass and transf==1:
            length=math.dist(coordinates[first],coordinates[second]);line_gravity.append((element_id,mass*9.81,length,[(x+y)/2 for x,y in zip(coordinates[first],coordinates[second])]))
        return element_id
    bases=[];pier_tops=[];cap_seats=[];support_roots=[]
    for i in range(q['supports']):
        x=i*span;base=node(x,0.,0.);anchor=node(x,0.,0.);ops.fix(anchor,1,1,1,1,1,1);fixed.append(anchor);bases.append(base)
        Kx=longitudinal['lateral_stiffness_n_m'];Ky=transverse['lateral_stiffness_n_m'];Kz=longitudinal['axial_stiffness_n_m']
        cx=longitudinal['horizontal_rotation_coupling_n'];cy=transverse['horizontal_rotation_coupling_n']
        for stiffness,coupling,direction in ((Kx,cx,1),(Ky,cy,2)):
            offset=coupling/stiffness;aux=node(x,0.,-offset);root=node(x,0.,-offset);ops.fix(root,1,1,1,1,1,1);fixed.append(root)
            rigid(base,aux,'foundation-translation-rotation-coupling');spring(root,aux,[stiffness],[direction],'foundation-offset')
        krx=transverse['rotational_stiffness_nm_rad']-cy*cy/Ky;kry=longitudinal['rotational_stiffness_nm_rad']-cx*cx/Kx
        f=candidate['foundation'];kt=max(Kx,Ky)*(f['cap_length_m']**2+f['cap_width_m']**2)/12
        spring(anchor,base,[Kz,krx,kry,kt],[3,4,5,6],'foundation')
        support_roots.append(fixed[-3:])
        fg=foundation_geometry(f);gravity.append((base,(fg['cap_concrete_m3']+fg['pile_concrete_m3'])*(foundation['density_kg_m3']+a['reinforcement_kg_m3'])*9.81))
        previous=base
        for s in geo['pier']:
            current=node(x,0.,s['end_m']);properties=pier_physics(candidate,s);mass=properties['mass_kg_m']+a['reinforcement_kg_m3']*cement_area(s)
            beam(previous,current,s,support_records,'pier',2,closed=len(s['regions'])%4==0,mass=mass)
            weight=mass*(s['end_m']-s['start_m'])*9.81/2;gravity.extend([(previous,weight),(current,weight)]);previous=current
        pier_tops.append(previous)
        centre=node(x,0.,height+.6);rigid(previous,centre,'column-to-cap-centroid')
        cap_nodes={0.:centre};positions=sorted(set([-3.5,-3.25,*geo['track_centres_m'],0.,3.25,3.5]))
        for y in positions:
            if y:cap_nodes[y]=node(x,y,height+.6)
        for left,right in zip(positions,positions[1:]):
            is_end=abs((left+right)/2)>3.25
            regions=[rectangle(2.5,1.2,z=.6)] if is_end else hollow_regions(2.5,1.2,.2,.2,.25)
            section=dict(regions=regions,material_roles=['concrete']*len(regions),**section_properties(regions));section['shear_area_m2']=5*section['area_m2']/6
            beam(cap_nodes[left],cap_nodes[right],section,{'concrete':support},'cap',1,closed=not is_end,mass=section['area_m2']*(support['density_kg_m3']+a['reinforcement_kg_m3']))
        seats=[]
        z=height+geo['cap_height_m']+deck_physics(candidate,geo['deck'][1])['neutral_axis_z_m']
        for y in geo['track_centres_m']:
            seat=node(x,y,z);rigid(cap_nodes[y],seat,'cap-to-bearing-offset');seats.append(seat)
        cap_seats.append(seats)
    deck_spans=[];service_elements=[];previous_ends={}
    webs=[r for r in geo['deck'][1]['regions'] if r['height_m']>(geo['deck'][1]['top_m']-geo['deck'][1]['bottom_m'])/2]
    spacing=max(r['y_m'] for r in webs)-min(r['y_m'] for r in webs) if len(webs)>1 else 1.
    spacing=max(.5,min(2.9,spacing))
    bearing=study['bearing'];kb=[2*bearing['horizontal_stiffness_n_m']]*2+[2*bearing['vertical_stiffness_n_m'],bearing['vertical_stiffness_n_m']*spacing**2/2]
    for bay in range(q['spans']):
        positions=mesh_positions(span,mesh,(geo['deck'][0]['end_m'],geo['deck'][-1]['start_m']))
        for track,y in enumerate(geo['track_centres_m']):
            z=coordinates[cap_seats[bay][track]][2];nodes=[node(bay*span+p,y,z) for p in positions]
            if bay and study.get('connection_scheme')=='continuous':
                # Share the actual node to avoid chained multipoint constraints.
                unused=nodes[0];nodes[0]=previous_ends[track];ops.remove('node',unused);coordinates.pop(unused)
            else:spring(cap_seats[bay][track],nodes[0],kb,[1,2,3,4],'bearing')
            spring(cap_seats[bay+1][track],nodes[-1],kb,[1,2,3,4],'bearing');previous_ends[track]=nodes[-1]
            deck_spans.append(dict(bay=bay,track=track,nodes=nodes))
            for first,second,left,right in zip(nodes,nodes[1:],positions,positions[1:]):
                section=next(s for s in geo['deck'] if s['start_m']<=(left+right)/2<=s['end_m'])
                properties=deck_physics(candidate,section)
                mass=properties['mass_kg_m']+a['reinforcement_kg_m3']*cement_area(section)+a['prestress_kg_m']+a['superimposed_dead_kg_m_per_track']
                if section is not geo['deck'][1]:mass+=a['embedded_kg_per_beam']/(2*geo['deck'][0]['end_m'])
                tag=beam(first,second,section,records,'deck',1,closed=candidate['definition']['deck']['family'] in ('hollow-box','hybrid-shell','segmental-box') and len(section['regions'])==4,mass=mass)
                if track<loaded_tracks:service_elements.append((tag,kn_m_per_track*1000,math.dist(coordinates[first],coordinates[second]),[(v+w)/2 for v,w in zip(coordinates[first],coordinates[second])]))
    ops.timeSeries('Constant',1);ops.pattern('Plain',1,1)
    applied=[]
    for n,w in gravity:ops.load(n,0.,0.,-w,0.,0.,0.);applied.append((coordinates[n],-w,0.))
    for group,fraction in ((line_gravity,0.),(service_elements,braking_fraction)):
        for tag,w,length,centre in group:
            ops.eleLoad('-ele',tag,'-type','-beamUniform',0.,-w,w*fraction);applied.append((centre,-w*length,w*length*fraction))
    ops.constraints('Transformation');ops.numberer('RCM');ops.system('UmfPack');ops.algorithm('Linear');ops.integrator('LoadControl',1.);ops.analysis('Static')
    if ops.analyze(1):raise RuntimeError('3D static system did not converge')
    ops.reactions();actual=sum(ops.nodeReaction(n,3) for n in fixed);expected=-sum(w for _,w,_ in applied)
    if not math.isclose(actual,expected,rel_tol=1e-7,abs_tol=.1):raise ValueError('3D vertical load path does not balance')
    if not math.isclose(expected,q['installed_study_mass_kg']*9.81+study['route_length_m']*loaded_tracks*kn_m_per_track*1000,rel_tol=1e-8):raise ValueError('3D mass differs from whole-package quantities')
    if not math.isclose(sum(ops.nodeReaction(n,1) for n in fixed),-sum(f for _,_,f in applied),rel_tol=1e-7,abs_tol=.1):raise ValueError('3D braking load path does not balance')
    moments=[]
    for axis in (0,1):
        applied_moment=sum((p[1]*w if axis==0 else p[2]*fx-p[0]*w) for p,w,fx in applied)
        reaction_moment=sum(ops.nodeReaction(n,4+axis)+(coordinates[n][1]*ops.nodeReaction(n,3)-coordinates[n][2]*ops.nodeReaction(n,2) if axis==0 else coordinates[n][2]*ops.nodeReaction(n,1)-coordinates[n][0]*ops.nodeReaction(n,3)) for n in fixed)
        if not math.isclose(reaction_moment,-applied_moment,rel_tol=1e-7,abs_tol=1.):raise ValueError('3D moment equilibrium failed')
        moments.append(dict(axis='longitudinal' if axis==0 else 'transverse',applied_nm=applied_moment,reaction_nm=reaction_moment))
    relative=[]
    for span_nodes in deck_spans:
        nodes=span_nodes['nodes'];first,last=nodes[0],nodes[-1]
        for n in nodes:
            t=(coordinates[n][0]-coordinates[first][0])/span
            relative.append(abs(ops.nodeDisp(n,3)-(1-t)*ops.nodeDisp(first,3)-t*ops.nodeDisp(last,3)))
    fields=[dict(element=e['id'],kind=e['kind'],local_force=ops.eleResponse(e['id'],'localForce')) for e in elements if e['kind'] in ('deck','cap','pier')]
    for field in fields:
        if len(field['local_force'])!=12 or not all(math.isfinite(v) for v in field['local_force']):raise ValueError('3D native force field invalid')
        element=next(e for e in elements if e['id']==field['element']);n,my,mz=element['stress_factors'];f=field['local_force']
        field['gross_elastic_fibre_stress_pa']=max(abs(f[0]),abs(f[6]))*n+max(abs(f[4]),abs(f[10]))*my+max(abs(f[5]),abs(f[11]))*mz
    support_actions=[]
    for i,roots in enumerate(support_roots):
        # Sum all anchor reactions at the physical base, including offset couples.
        origin=coordinates[bases[i]]
        reactions=[ops.nodeReaction(n) for n in roots]
        support_actions.append(dict(support=i,vertical_n=sum(r[2] for r in reactions),
                                    horizontal_n=math.hypot(sum(r[0] for r in reactions),sum(r[1] for r in reactions)),
                                    moments_nm=[sum(r[3]+(coordinates[n][1]-origin[1])*r[2]-(coordinates[n][2]-origin[2])*r[1] for n,r in zip(roots,reactions)),
                                                sum(r[4]+(coordinates[n][2]-origin[2])*r[0]-(coordinates[n][0]-origin[0])*r[2] for n,r in zip(roots,reactions))]))
    return dict(schema='osr-civil-space-frame/1',loaded_tracks=loaded_tracks,braking_fraction=braking_fraction,mesh_per_span=mesh,
                peak_relative_deflection_m=max(relative),peak_deck_roll_rad=max(abs(ops.nodeDisp(n,4)) for s in deck_spans for n in s['nodes']),
                peak_foundation_settlement_m=max(abs(ops.nodeDisp(n,3)) for n in bases),
                peak_pier_top_horizontal_m=max(math.hypot(ops.nodeDisp(n,1),ops.nodeDisp(n,2)) for n in pier_tops),
                peak_support_vertical_n=max(abs(r['vertical_n']) for r in support_actions),support_actions=support_actions,
                peak_deck_gross_elastic_stress_pa=max(f['gross_elastic_fibre_stress_pa'] for f in fields if f['kind']=='deck'),
                peak_pier_gross_elastic_stress_pa=max(f['gross_elastic_fibre_stress_pa'] for f in fields if f['kind']=='pier'),
                peak_cap_bending_nm=max(max(abs(f['local_force'][4]),abs(f['local_force'][10])) for f in fields if f['kind']=='cap'),
                peak_deck_torsion_nm=max(max(abs(f['local_force'][3]),abs(f['local_force'][9])) for f in fields if f['kind']=='deck'),
                expected_vertical_n=expected,actual_vertical_n=actual,moment_equilibrium=moments,
                coordinates_m=coordinates,elements=elements,rigid_links=links,native_local_forces=fields,
                native_displacements={n:ops.nodeDisp(n) for n in coordinates},physical_release=False,
                coverage='3D linear shear-flexible beams, separate tracks, finite bearing translation/roll, flexible actual-section cap, coupled planar foundation matrices',
                uncovered=['moving/coupled train','open-section warping/distortion','foundation torsion calibration','interface/joint/cyclic failure','prestress/stage locking/seismic'])
