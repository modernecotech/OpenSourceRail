"""Actual-section quadratic solid meshes and native CalculiX field exchange."""
from __future__ import annotations
import math
from pathlib import Path
import re
import shutil
import subprocess

import numpy as np
from osr_mech.civil.exploration import geometry
from engineering.analysis import solver_results
from .contracts import encoded,sha


def subdivide(boundaries, maximum):
    boundaries=sorted({round(float(v),12) for v in boundaries})
    positions=[]
    for a,b in zip(sorted(set(boundaries)),sorted(set(boundaries))[1:]):
        count=max(1,math.ceil((b-a)/maximum))
        positions += [a+(b-a)*i/count for i in range(count)]
    return sorted(set(positions+[max(boundaries)]))


def mesh(definition, size_m):
    if not .08 <= size_m <= 2.:raise ValueError('solid mesh outside bounded research resolution')
    sections=geometry(definition)['deck'];span=definition['deck']['span_m']
    load_plane=(sections[1]['regions'][0]['z_m']+sections[1]['regions'][0]['height_m']/2
                if definition['deck']['family']=='U-girder' else sections[1]['top_m'])
    xs=subdivide([0.,span/2,span]+[s['start_m'] for s in sections]+[s['end_m'] for s in sections],size_m)
    ys=subdivide([r['y_m']+sign*r['width_m']/2 for s in sections for r in s['regions'] for sign in (-1,1)]+[r['y_m'] for r in sections[1]['regions']]+[0.],size_m)
    zs=subdivide([r['z_m']+sign*r['height_m']/2 for s in sections for r in s['regions'] for sign in (-1,1)],size_m)
    nodes={};elements=[];top_loads={};volume=0.
    def node(point):
        key=tuple(round(float(v),12) for v in point)
        if key not in nodes:nodes[key]=len(nodes)+1
        return nodes[key]
    edges=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    for xa,xb in zip(xs,xs[1:]):
        section=next(s for s in sections if s['start_m'] <= (xa+xb)/2 <= s['end_m'])
        for ya,yb in zip(ys,ys[1:]):
            for za,zb in zip(zs,zs[1:]):
                index=next((i for i,r in enumerate(section['regions']) if abs((ya+yb)/2-r['y_m'])<r['width_m']/2+1e-12
                            and abs((za+zb)/2-r['z_m'])<r['height_m']/2+1e-12),None)
                if index is None:continue
                corners=np.asarray([(xa,ya,za),(xb,ya,za),(xb,yb,za),(xa,yb,za),(xa,ya,zb),(xb,ya,zb),(xb,yb,zb),(xa,yb,zb)])
                ids=[node(p) for p in corners]+[node((corners[i]+corners[j])/2) for i,j in edges]
                if len(set(ids))!=20:raise ValueError('collapsed quadratic solid element')
                elements.append(dict(id=len(elements)+1,nodes=ids,material=section['material_roles'][index],
                                     volume_m3=(xb-xa)*(yb-ya)*(zb-za),centroid_x_m=(xa+xb)/2))
                volume+=(xb-xa)*(yb-ya)*(zb-za)
                if math.isclose(zb,load_plane,abs_tol=1e-10):
                    # Exact consistent load for an 8-node serendipity face.
                    area=(xb-xa)*(yb-ya)
                    for local in (4,5,6,7):top_loads[ids[local]]=top_loads.get(ids[local],0.)-area/12
                    for local in (12,13,14,15):top_loads[ids[local]]=top_loads.get(ids[local],0.)+area/3
    expected=sum(s['area_m2']*(s['end_m']-s['start_m']) for s in sections)
    if not math.isclose(volume,expected,rel_tol=1e-10):raise ValueError('solid mesh volume differs from canonical geometry')
    if not math.isclose(sum(top_loads.values()),span*2.9,rel_tol=1e-10):raise ValueError('solid distributed service-load coverage mismatch')
    return dict(nodes={i:point for point,i in nodes.items()},elements=elements,top_face_weights_m2=top_loads,
                concrete_or_matrix_volume_m3=volume,span_m=span,top_m=load_plane)


def stress_fields(path):
    """Versioned CalculiX stress blocks: element/integration-point allocation."""
    active=False;time=None;rows=[]
    for line in path.read_text().splitlines():
        if line.strip().lower().startswith('stresses '):
            active=True
            match=re.search(r'time\s+([-+0-9.EeDd]+)',line,re.I);time=float(match[1].replace('D','E')) if match else None
            continue
        if not active:continue
        fields=line.split()
        if len(fields)==8 and fields[0].isdigit() and fields[1].isdigit():
            values=[float(v.replace('D','E')) for v in fields[2:]]
            if not all(math.isfinite(v) for v in values):raise ValueError('nonfinite native stress')
            xx,yy,zz,xy,xz,yz=values
            mises=math.sqrt(.5*((xx-yy)**2+(yy-zz)**2+(zz-xx)**2)+3*(xy*xy+xz*xz+yz*yz))
            rows.append(dict(element_id=int(fields[0]),integration_point=int(fields[1]),time=time,
                             stress_pa=dict(zip(('xx','yy','zz','xy','xz','yz'),values)),von_mises_pa=mises))
        elif line.strip() and not line.strip().startswith(('elem','int','xx','(')):
            active=False
    if not rows:raise ValueError('native stress block missing or unsupported')
    if len({(r['element_id'],r['integration_point'],r['time']) for r in rows})!=len(rows):
        raise ValueError('duplicate native stress point')
    return rows


def run(candidate, study, size_m, output,*,additional_service_kn_m=0.):
    if type(additional_service_kn_m) not in (int,float) or not math.isfinite(additional_service_kn_m) or additional_service_kn_m<0:
        raise ValueError('solid service intensity must be finite and nonnegative')
    output.mkdir(parents=True,exist_ok=False)
    model=mesh(candidate['definition'],size_m)
    nodes=model['nodes'];span=model['span_m']
    section=geometry(candidate['definition'])['deck'][1]
    webs=sorted([r for r in section['regions'] if r['height_m'] > (section['top_m']-section['bottom_m'])/2],key=lambda r:r['y_m'])
    lands=[webs[0],webs[-1]] if len(webs)>1 else section['regions'][:1]
    supports=[n for n,(x,y,z) in nodes.items() if math.isclose(z,0.,abs_tol=1e-10)
              and (math.isclose(x,0.,abs_tol=1e-10) or math.isclose(x,span,abs_tol=1e-10))
              and any(abs(y-r['y_m']) <= r['width_m']/2+1e-10 for r in lands)]
    left=[n for n in supports if math.isclose(nodes[n][0],0.,abs_tol=1e-10)]
    right=[n for n in supports if math.isclose(nodes[n][0],span,abs_tol=1e-10)]
    middle=[n for n,(x,y,z) in nodes.items() if math.isclose(x,span/2,abs_tol=1e-10) and math.isclose(z,model['top_m'],abs_tol=1e-10)]
    if not supports or not left or not middle:raise ValueError('solid support/result allocation missing')
    material={'concrete':candidate['material'],**candidate.get('material_records',{})}
    additional_density=(span*candidate['mass_allowances']['prestress_kg_m']+candidate['mass_allowances']['embedded_kg_per_beam'])/model['concrete_or_matrix_volume_m3']
    text=['*HEADING','Actual civil research section; elastic solid, no prestress or strength acceptance','*NODE']
    text += [f'{i},'+','.join(f'{v:.12g}' for v in point) for i,point in nodes.items()]
    for role in sorted({e['material'] for e in model['elements']}):
        if role not in material:raise ValueError('missing detailed material: '+role)
        text += [f'*ELEMENT,TYPE=C3D20R,ELSET=E_{role.upper()}']
        for e in model['elements']:
            if e['material']==role:
                text += [f'{e["id"]},'+','.join(str(n) for n in e['nodes'][:15])+',',','.join(str(n) for n in e['nodes'][15:])]
        m=material[role]
        if m.get('orthotropic'):
            from .orthotropic import elastic_lines
            elastic=elastic_lines(m['orthotropic'])
        else:elastic=['*ELASTIC',f'{m["youngs_modulus_pa"]*m.get("stiffness_factor",1.)},{m["poisson_ratio"]}']
        text += [f'*MATERIAL,NAME=M_{role.upper()}',*elastic,
                 '*DENSITY',str(m['density_kg_m3']+(candidate['mass_allowances']['reinforcement_kg_m3'] if role in ('concrete','uhpc') else 0.)+additional_density),
                 f'*SOLID SECTION,ELSET=E_{role.upper()},MATERIAL=M_{role.upper()}']
    def ids(values):return [','.join(str(n) for n in values[i:i+16]) for i in range(0,len(values),16)]
    text += ['*NSET,NSET=MID',*ids(middle),'*NSET,NSET=SUPPORTS',*ids(supports),
             '*ELSET,ELSET=ALL','1,'+str(len(model['elements']))+',1' if len(model['elements'])>1 else '1']
    # The ALL set is generated, not a list containing only the two end IDs.
    text[-2]='*ELSET,ELSET=ALL,GENERATE'
    text += ['*BOUNDARY','SUPPORTS,3,3',f'{left[0]},1,2',f'{right[0]},2,2','*STEP','*STATIC','*DLOAD','ALL,GRAV,9.81,0.,0.,-1.','*CLOAD']
    pressure=(candidate['mass_allowances']['superimposed_dead_kg_m_per_track']*9.81+additional_service_kn_m*1000)/2.9
    text += [f'{node},3,{-pressure*area:.12g}' for node,area in model['top_face_weights_m2'].items() if area]
    text += ['*NODE PRINT,NSET=MID','U','*NODE PRINT,NSET=SUPPORTS','RF','*EL PRINT,ELSET=ALL','S','*END STEP']
    deck=output/'solid.inp';deck.write_text('\n'.join(text)+'\n')
    binary=shutil.which('ccx')
    if not binary:raise RuntimeError('native CalculiX is required')
    try:result=subprocess.run([binary,'solid'],cwd=output,capture_output=True,text=True,timeout=180)
    except subprocess.TimeoutExpired as error:
        def log(value):return value.decode(errors='replace') if isinstance(value,bytes) else value or ''
        (output/'stdout.log').write_text(log(error.stdout));(output/'stderr.log').write_text(log(error.stderr))
        raise RuntimeError('native solid exceeded its 180-second limit; partial outputs retained') from error
    (output/'stdout.log').write_text(result.stdout);(output/'stderr.log').write_text(result.stderr)
    if result.returncode or 'Job finished' not in result.stdout:raise RuntimeError('native CalculiX solid failed; logs retained')
    dat=output/'solid.dat';rows=stress_fields(dat)
    selector=dict(asset_id=candidate['id'],load_case_id='dead-service',metric='midspan_displacement',path='solid.dat',
                  node_id=min(middle,key=lambda n:abs(nodes[n][1])),dof=3,time=1.,step=1,set_name='MID',quantity='displacement',operation='signed')
    spec=dict(parser_id=solver_results.PARSERS['calculix'],model_sha256=sha(deck),model_units={'displacement':'m'},files={'solid.dat':{}},selectors=[selector])
    register=dict(criteria={'calculix':[dict(asset_id=candidate['id'],load_case_id='dead-service',metric='midspan_displacement',unit='m')]},native_output_spec={'calculix':spec})
    native=dict(input_sha256=sha(deck),native_output_paths=['solid.dat'],output_hashes={'solid.dat':sha(dat)},native_parser=solver_results.parser_provenance('calculix',spec))
    exchange=solver_results.extract_results(native,output,register,'calculix');solver_results.write_exchange(output/'native-exchange.csv',exchange)
    central={e['id']:e for e in model['elements'] if span/4<=e['centroid_x_m']<=3*span/4}
    points=[r for r in rows if r['element_id'] in central]
    from collections import Counter
    counts=Counter(r['element_id'] for r in points)
    if not points or any(counts[eid]!=8 for eid in central):raise ValueError('central stress integration coverage incomplete')
    rms=math.sqrt(math.fsum(r['von_mises_pa']**2*central[r['element_id']]['volume_m3']/8 for r in points)/math.fsum(e['volume_m3'] for e in central.values()))
    summary=dict(schema='osr-civil-solid/1',candidate_id=candidate['id'],mesh_m=size_m,node_count=len(nodes),element_count=len(model['elements']),
                 source_volume_m3=model['concrete_or_matrix_volume_m3'],midspan_displacement_m=abs(exchange[0]['value']),
                 peak_von_mises_pa=max(r['von_mises_pa'] for r in rows),central_rms_von_mises_pa=rms,
                 stress_convergence_basis='volume-weighted eight-point RMS in central half-span; support singular peaks retained separately',
                 native_register=register,native_receipt=native,
                 stress_parser='calculix-integration-stress/1',stress_parser_sha256=sha(Path(__file__)),
                 native_binary_sha256=sha(Path(binary)),physical_release=False,
                 applicability='actual-section linear elastic C3D20R solids; idealized end supports, no prestress/contact/strength acceptance')
    summary['mass_model']='matrix density plus rebar allowance; prestress/inserts spread as explicit bulk mass, not structural reinforcement'
    if additional_service_kn_m:
        summary['additional_static_planning_kn_m']=additional_service_kn_m
        summary['planning_load_is_not_actual_axle_envelope']=True
    (output/'stress-fields.json').write_bytes(encoded(rows));(output/'result.json').write_bytes(encoded(summary))
    return summary
