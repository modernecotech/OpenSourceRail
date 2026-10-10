"""Native Gmsh/CalculiX bolted solid/contact/pretension verification adapter.

The explicit coupon geometry is a solver fixture, not an installation solid or
an accepted fastener specification. Full-scale loads preserve their identity.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
from pathlib import Path
import shutil
import subprocess
import numpy as np
from osr_mech.engineering_definition import fingerprint


def load_case(result, joint_id, train_id):
    rows = [dict(time_s=h['time_s'], **j) for h in result['history'] for j in h['joints']
            if j['joint'] == joint_id and j['train'] == train_id]
    if not rows:
        raise ValueError('dynamic joint identity not present in the supplied result')
    # One simultaneous vector; componentwise envelope would destroy correlation.
    row = max(rows, key=lambda r: np.linalg.norm(r['force_moment_si'][:3]))
    return dict(joint_id=joint_id, train_id=train_id, time_s=row['time_s'],
        force_moment_si=row['force_moment_si'],
        dynamic_result_sha256=fingerprint(result),
        hardware_definition_sha256=result['hardware_definition_sha256'],
        selection='largest simultaneous force magnitude, moments at the same timestep')


def mesh_geo(size):
    if not .003 <= size <= .012:
        raise ValueError('joint coupon mesh outside declared budget')
    return f'''SetFactory("OpenCASCADE");
Box(1) = {{-.04,-.03,0,.08,.06,.02}};
Cylinder(2) = {{0,0,-.001,0,0,.022,.011}};
up[] = BooleanDifference{{ Volume{{1}}; Delete; }}{{ Volume{{2}}; Delete; }};
Box(3) = {{-.04,-.03,-.02,.08,.06,.02}};
Cylinder(4) = {{0,0,-.021,0,0,.022,.011}};
lo[] = BooleanDifference{{ Volume{{3}}; Delete; }}{{ Volume{{4}}; Delete; }};
Cylinder(5) = {{0,0,0,0,0,.02,.01}};
Cylinder(6) = {{0,0,.02,0,0,.005,.017}};
bu[] = BooleanUnion{{ Volume{{5}}; Delete; }}{{ Volume{{6}}; Delete; }};
Cylinder(7) = {{0,0,-.02,0,0,.02,.01}};
Cylinder(8) = {{0,0,-.025,0,0,.005,.017}};
bl[] = BooleanUnion{{ Volume{{7}}; Delete; }}{{ Volume{{8}}; Delete; }};
bolt[] = BooleanFragments{{ Volume{{bu[]}}; Delete; }}{{ Volume{{bl[]}}; Delete; }};
Physical Volume("UPPER", 1) = {{up[]}};
Physical Volume("LOWER", 2) = {{lo[]}};
Physical Volume("BOLT", 3) = {{bolt[]}};
Mesh.MeshSizeMin = {size}; Mesh.MeshSizeMax = {size};
Mesh.ElementOrder = 2; Mesh.MshFileVersion = 2.2;
Mesh.SecondOrderLinear = 0;
'''


def parse_msh(path):
    lines=path.read_text().splitlines();nodes={};elements={}
    start=lines.index('$Nodes');count=int(lines[start+1])
    for line in lines[start+2:start+2+count]:
        fields=line.split();nodes[int(fields[0])]=np.asarray(list(map(float,fields[1:])))
    start=lines.index('$Elements');count=int(lines[start+1])
    for line in lines[start+2:start+2+count]:
        fields=list(map(int,line.split()));eid,kind,ntags=fields[:3]
        if kind==11:
            elements[eid]=dict(role=fields[3],nodes=fields[3+ntags:])
    if not elements or {e['role'] for e in elements.values()}!={1,2,3}:
        raise ValueError('Gmsh did not return quadratic tetrahedra for all three solids')
    used={n for e in elements.values() for n in e['nodes']}
    return {n:p for n,p in nodes.items() if n in used},elements


def surface(elements,nodes,role,z,upper_half=False):
    faces=[]
    for eid,e in elements.items():
        if e['role']!=role:continue
        if upper_half and np.mean([nodes[n][2] for n in e['nodes'][:4]])<=0:continue
        for number,local in enumerate(((0,1,2),(0,3,1),(1,3,2),(2,3,0)),1):
            ids=[e['nodes'][i] for i in local]
            if all(abs(nodes[n][2]-z)<1e-9 for n in ids):faces.append((eid,number,ids))
    if not faces:raise ValueError('required native contact/pretension face missing')
    return faces


def parse_dat(path):
    """Separate U, RF and S headers; a force row must never become displacement."""
    blocks=[];current=None
    for line in Path(path).read_text().splitlines():
        header=re.search(r'(displacements|forces|stresses).*for set (\w+) and time\s+([\d.E+\-]+)',line)
        if header:
            current=dict(quantity=header[1],set_name=header[2],time_s=float(header[3]),rows=[]);blocks.append(current)
            continue
        if current:
            fields=line.split()
            expected=8 if current['quantity']=='stresses' else 4
            if len(fields)!=expected:continue
            try:
                row=[float(x) for x in fields]
                if not np.isfinite(row).all():raise ValueError('nonfinite native joint output')
                current['rows'].append(row)
            except ValueError:
                if fields[0].lstrip('-').isdigit():raise
    return blocks


def run(output,model,case,*,size=.009,preload_n=30000.,gmsh_command=None):
    output=Path(output).resolve()
    if output.exists():raise ValueError('native joint evidence directory already exists')
    if case['hardware_definition_sha256']!=fingerprint(model) or case['joint_id'] not in {j['id'] for j in model['joints']}:
        raise ValueError('native submodel load and shared joint definition disagree')
    if not math.isfinite(preload_n) or preload_n<=0:raise ValueError('positive declared pretension required')
    output.mkdir(parents=True);geo=output/'coupon.geo';geo.write_text(mesh_geo(size))
    native_gmsh=shutil.which('gmsh')
    command=gmsh_command or ([native_gmsh] if native_gmsh else
        ['flatpak','run',f'--filesystem={output}', '--command=gmsh','org.freecad.FreeCAD'])
    mesh_command=[*command,str(geo),'-3','-format','msh2','-o',str(output/'coupon.msh'),'-nt','1']
    result=subprocess.run(mesh_command,capture_output=True,text=True,timeout=120)
    (output/'gmsh.stdout.log').write_text(result.stdout);(output/'gmsh.stderr.log').write_text(result.stderr)
    if result.returncode:raise RuntimeError('native Gmsh failed; mesh/log evidence retained')
    nodes,elements=parse_msh(output/'coupon.msh');dummy=max(nodes)+1
    text=['*HEADING','Synthetic bolted solid contact coupon; installation/release open','*NODE']
    text += [f'{n},'+','.join(f'{v:.12g}' for v in p) for n,p in nodes.items()]+[f'{dummy},0,0,0']
    for role,name in ((1,'UPPER'),(2,'LOWER'),(3,'BOLT')):
        text += [f'*ELEMENT,TYPE=C3D10,ELSET={name}']
        # Gmsh and CalculiX use the same C3D10 edge order except the final two edges.
        for eid,e in elements.items():
            if e['role']==role:
                ids=e['nodes'].copy();ids[8],ids[9]=ids[9],ids[8]
                text.append(f'{eid},'+','.join(map(str,ids)))
        text += [f'*SOLID SECTION,ELSET={name},MATERIAL=STEEL']
    text += ['*MATERIAL,NAME=STEEL','*ELASTIC','210e9,.3']
    surfaces={
        'UP_BOTTOM':surface(elements,nodes,1,0.),'LO_TOP':surface(elements,nodes,2,0.),
        'UP_TOP':surface(elements,nodes,1,.02),'HEAD_BOTTOM':surface(elements,nodes,3,.02),
        'LO_BOTTOM':surface(elements,nodes,2,-.02),'NUT_TOP':surface(elements,nodes,3,-.02),
        'CUT':surface(elements,nodes,3,0.,True)}
    for name,faces in surfaces.items():
        text += [f'*SURFACE,NAME={name},TYPE=ELEMENT']+[f'{eid},S{face}' for eid,face,_ in faces]
    text += ['*SURFACE INTERACTION,NAME=CONTACT','*SURFACE BEHAVIOR,PRESSURE-OVERCLOSURE=LINEAR','1e14',
             '*FRICTION','.3,1e13']
    for slave,master in (('UP_BOTTOM','LO_TOP'),('HEAD_BOTTOM','UP_TOP'),('NUT_TOP','LO_BOTTOM')):
        text += ['*CONTACT PAIR,INTERACTION=CONTACT,TYPE=SURFACE TO SURFACE',f'{slave},{master}']
    text += [f'*PRE-TENSION SECTION,SURFACE=CUT,NODE={dummy}','0.,0.,-1.']
    role_nodes={role:{n for e in elements.values() if e['role']==role for n in e['nodes']} for role in (1,2,3)}
    supports=[n for n in role_nodes[2] if abs(nodes[n][2]+.02)<1e-9]
    upper=[n for n in role_nodes[1] if abs(nodes[n][2]-.02)<1e-9]
    # The fixture restrains the lower plate and bolt rigid modes explicitly.
    for name,ids in (('SUPPORT',supports),('TOP',upper),('PRETENSION',[dummy])):
        text += [f'*NSET,NSET={name}']+[','.join(map(str,ids[i:i+16])) for i in range(0,len(ids),16)]
    nut=[n for n in role_nodes[3] if abs(nodes[n][2]+.025)<1e-9]
    anchor=min(nut,key=lambda n:float(nodes[n]@nodes[n]));other=max(nut,key=lambda n:nodes[n][0])
    text += ['*NSET,NSET=ANCHORS',f'{anchor},{other}', '*BOUNDARY','SUPPORT,1,3',f'{anchor},1,2',f'{other},2,2']
    text += ['*STEP,NLGEOM,INC=200','*STATIC','.1,1.,1e-6,.1','*CLOAD',f'{dummy},1,{preload_n}',
             '*NODE PRINT,NSET=PRETENSION','U,RF','*NODE PRINT,NSET=SUPPORT','RF',
             '*NODE PRINT,NSET=TOP','U','*EL PRINT,ELSET=BOLT','S','*END STEP']
    binary=shutil.which('ccx')
    if not binary:raise RuntimeError('native CalculiX unavailable')
    def solve(job):
        try:result=subprocess.run([binary,job],cwd=output,capture_output=True,text=True,timeout=180)
        except subprocess.TimeoutExpired as error:
            (output/f'{job}.timeout.log').write_text(str(error))
            raise RuntimeError('native joint solve exceeded its 180-second budget; partial evidence retained') from error
        (output/f'{job}.stdout.log').write_text(result.stdout);(output/f'{job}.stderr.log').write_text(result.stderr)
        if result.returncode or 'Job finished' not in result.stdout:raise RuntimeError('native joint solve failed; logs retained')
    (output/'preload.inp').write_text('\n'.join(text)+'\n');solve('preload')
    preload_blocks=parse_dat(output/'preload.dat')
    reference=[r[1] for b in preload_blocks if b['quantity']=='displacements' and b['set_name']=='PRETENSION' and abs(b['time_s']-1.)<1e-6 for r in b['rows']]
    if len(reference)!=1:raise RuntimeError('pretension displacement needed to lock the bolt was not retained')
    # Preserve the full force/moment vector with minimum-norm nodal allocation.
    xyz=np.asarray([nodes[n] for n in upper]);centre=xyz.mean(axis=0);B=np.zeros((6,3*len(upper)))
    from .spatial_structure import skew
    for i,r in enumerate(xyz-centre):B[:3,3*i:3*i+3]=np.eye(3);B[3:,3*i:3*i+3]=skew(r)
    force=np.asarray(case['force_moment_si'],dtype=float)
    if force.shape!=(6,) or not np.isfinite(force).all():raise ValueError('six finite simultaneous joint resultants required')
    nodal=B.T@np.linalg.solve(B@B.T,force)
    text += ['*STEP,NLGEOM,INC=200','*STATIC','.1,1.,1e-6,.1','*BOUNDARY',f'{dummy},1,1,{reference[0]:.12g}',
             '*CLOAD',f'{dummy},1,0.']
    text += [f'{node},{dof+1},{nodal[3*i+dof]:.12g}' for i,node in enumerate(upper) for dof in range(3)]
    text += ['*NODE PRINT,NSET=SUPPORT','RF','*NODE PRINT,NSET=ANCHORS','RF','*NODE PRINT,NSET=TOP','U','*EL PRINT,ELSET=BOLT','S','*END STEP']
    deck=output/'joint.inp';deck.write_text('\n'.join(text)+'\n');solve('joint')
    blocks=parse_dat(output/'joint.dat')
    displacement=[r[1:4] for b in blocks if b['quantity']=='displacements' and b['set_name']=='TOP' for r in b['rows']]
    from osr_mech.freecad_fea import _von_mises
    stresses=[_von_mises(r[2:8]) for b in blocks if b['quantity']=='stresses' for r in b['rows']]
    if not displacement or not stresses:raise RuntimeError('native joint results missing')
    reaction=np.zeros(6)
    for b in blocks:
        if b['quantity']=='forces' and b['set_name'] in ('SUPPORT','ANCHORS') and abs(b['time_s']-2.)<1e-6:
            for row in b['rows']:
                f=np.asarray(row[1:]);reaction[:3]+=f;reaction[3:]+=np.cross(nodes[int(row[0])]-centre,f)
    force_error=float(np.linalg.norm(reaction[:3]+force[:3])/max(np.linalg.norm(force[:3]),1.))
    moment_scale=max(float(np.linalg.norm(force[3:])),float(np.linalg.norm(force[:3]))*.08,1.)
    moment_error=float(np.linalg.norm(reaction[3:]+force[3:])/moment_scale)
    shank=[(eid,e) for eid,e in elements.items() if e['role']==3 and .005<=abs(float(np.mean([nodes[n][2] for n in e['nodes'][:4]])))<=.015]
    volumes={eid:abs(float(np.linalg.det(np.column_stack([nodes[e['nodes'][i]]-nodes[e['nodes'][0]] for i in (1,2,3)]))))/6 for eid,e in shank}
    stress_rows=[row for b in blocks if b['quantity']=='stresses' and abs(b['time_s']-2.)<1e-6 for row in b['rows'] if int(row[0]) in volumes]
    if not stress_rows or set(int(r[0]) for r in stress_rows)!=set(volumes):raise RuntimeError('shank stress coverage incomplete')
    shank_rms=math.sqrt(sum(_von_mises(r[2:8])**2*volumes[int(r[0])]/4 for r in stress_rows)/sum(volumes.values()))
    report=dict(schema='osr-native-joint-submodel/1',load_case=case,mesh_m=size,nodes=len(nodes),elements=len(elements),
        geometry_basis='80x60mm two 20mm plates, 22mm holes, 20mm shank, 34mm cylindrical head/nut; synthetic coupon',
        native_mesher='Gmsh',native_solver='CalculiX',native_binary_sha256=hashlib.sha256(Path(binary).read_bytes()).hexdigest(),
        pretension_n=preload_n,pretension_control='force preload, then lock measured reference displacement for the external load step',
        locked_pretension_reference_displacement_m=reference[0],
        contact_model='unilateral face-to-face penalty contact, Coulomb friction 0.3',
        nodal_force_moment_relative_error=float(np.linalg.norm(B@nodal-force)/max(np.linalg.norm(force),1.)),
        maximum_displacement_m=max(float(np.linalg.norm(v)) for v in displacement),
        peak_bolt_von_mises_pa=max(stresses),
        support_force_moment_si=reaction.tolist(),
        force_equilibrium_relative_error=force_error,moment_equilibrium_relative_error=moment_error,
        numerical_equilibrium_passed=force_error<1e-3 and moment_error<1e-3,
        shank_volume_weighted_rms_von_mises_pa=shank_rms,
        stress_convergence_basis='four-point volume-weighted RMS in shank 5–15mm from pretension cut; singular peak retained separately',
        native_solve_completed=True,physical_validation=False,engineering_released=False,
        open_gates=['actual grip/fastener/head/retention geometry and material', 'measured preload and friction',
                    'mesh/contact-stiffness convergence', 'strength/fatigue limits and independent review'])
    report['outputs_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()}
    (output/'result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return report
