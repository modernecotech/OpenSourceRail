"""Deterministic isometric SVG from the same located SI assembly definition.

This vector projection preserves source geometry and IDs. It is not a measured
site drawing, a photorealistic claim or a replacement for native STEP geometry.
"""
from html import escape
from math import cos,sin,pi
from .assembly import scene


def svg(result):
    assembly=scene(result);faces=[];allpoints=[]
    palette={'research_concrete':'#ccd4dc','steel':'#57778b','bearing-assembly-envelope':'#1c8d90','rail-steel-envelope':'#3c5368','HDPE':'#c78737','grating-envelope':'#799e9f'}
    def project(v):
        x,y,z=v;return [.6*x+.8*y,-.297*x+.223*y+.928*z,-.743*x+.557*y+.371*z]
    def addface(points,material,id):
        uv=[project(v) for v in points];faces.append((sum(p[2] for p in uv)/len(uv),uv,palette.get(material,'#99aabb'),id));allpoints.extend(uv)
    for e in assembly['entities']:
        g=e['geometry'];x,y,z=g['at_m'];mat=e['material']
        if e['shape']=='box':
            a,b,c=g['size_m'];pts=[[x+dx,y+dy,z+dz] for dx,dy,dz in [(0,0,0),(a,0,0),(a,b,0),(0,b,0),(0,0,c),(a,0,c),(a,b,c),(0,b,c)]]
            for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:addface([pts[i] for i in f],mat,e['id'])
        elif e['shape']=='profile':
            poly=g['points_yz_m'];a=[[x,y+u,z+v] for u,v in poly];b=[[x+g['length_m'],y+u,z+v] for u,v in poly]
            addface(a,mat,e['id']);addface(b[::-1],mat,e['id'])
            for i in range(len(a)):j=(i+1)%len(a);addface([a[i],b[i],b[j],a[j]],mat,e['id'])
        elif e['shape'] in ('tube','cylinder'):
            axis=g['axis'];r=g['radius_m'];L=g['length_m'];a=[];b=[]
            for i in range(16):
                u=r*cos(2*pi*i/16);v=r*sin(2*pi*i/16)
                pt=[x,y+u,z+v] if axis[0]==1 else [x+u,y+v,z]
                a.append(pt);b.append([pt[j]+axis[j]*L for j in range(3)])
            addface(a,mat,e['id']);addface(b[::-1],mat,e['id'])
            for i in range(16):j=(i+1)%16;addface([a[i],b[i],b[j],a[j]],mat,e['id'])
    low=[min(p[i] for p in allpoints) for i in range(2)];high=[max(p[i] for p in allpoints) for i in range(2)]
    scale=min(2350/(high[0]-low[0]),1250/(high[1]-low[1]))
    def xy(p):return [200+(p[0]-low[0])*scale,1650-(p[1]-low[1])*scale]
    def points(vs):return ' '.join(f'{xy(v)[0]:.2f},{xy(v)[1]:.2f}' for v in vs)
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="1900" viewBox="0 0 3000 1900">',
         '<rect width="3000" height="1900" fill="#f5f7fa"/>',
         '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#173047}.title{font-size:66px;font-weight:700}.sub{font-size:32px}.note{font-size:28px}.metric{font-size:38px;font-weight:600}</style>',
         '<text x="100" y="105" class="title">Two-track viaduct · located research assembly</text>',
         '<text x="100" y="164" class="sub">20 m span · segmented erection · continuous post-tension · explicit soil and lifting assumptions</text>']
    for _,pts,color,id in sorted(faces,key=lambda v:v[0]):
        out.append(f'<polygon points="{points(pts)}" fill="{color}" stroke="#405769" stroke-width="1.4" stroke-linejoin="round"><title>{escape(id)}</title></polygon>')
    for p in assembly['definition_paths']:
        if p['kind']=='tendon-duct-centreline':
            out.append(f'<polyline points="{points([project(v) for v in p["path_xyz_m"]])}" fill="none" stroke="#b65b49" stroke-width="2" opacity=".72"><title>{escape(p["id"])} — placement unverified</title></polyline>')
    r=result['reinforcement'];t=result['prestress'];foot=result['foundation']
    lines=[f'{result["section"]["physical"]["family"].replace("_"," ")} · {result["quantities"]["accounted_superstructure_kg"]/1000:.1f} t accounted / beam',
        f'{t["strands"]} strands in 6 ducts · {r["stirrup_count"]} closed links / beam',
        f'Pier Ø{foot["column_diameter_m"]:.2f} m · footing {foot["width_m"]:.2f} × {foot["width_m"]:.2f} m',
        f'Route: 150 beams · 76 shared bents · 600 bearings',
        'Gross solids + equipment envelopes; reinforcement/duct paths are not proven fit.',
        'Joint keys, reinforcement anchorage and temporary-stage effects remain unverified.']
    out.append('<rect x="1710" y="1270" width="1190" height="405" rx="24" fill="#ffffff" stroke="#d2dce4" stroke-width="2"/>')
    for i,line in enumerate(lines):out.append(f'<text x="1750" y="{1332+i*56}" class="note">{escape(line)}</text>')
    out.extend([f'<text x="100" y="1772" class="note">Civil candidate {result["civil_candidate_id"][:24]} · system {result["system_candidate_id"][:24]}</text>',
        '<text x="100" y="1823" class="note">Deterministic projection of the source SI assembly. Native STEP/SC is separate. No construction or operating release.</text>',
        '</svg>'])
    return '\n'.join(out)+'\n'
