"""Real CalculiX/Gmsh section benchmark; retains inputs, raw outputs and failures."""
from __future__ import annotations
import hashlib,json,math,re,shutil,subprocess
from pathlib import Path
from osr_mech.section_contract import rhs,calculix_box
from osr_mech.engineering_definition import fingerprint


def _run(folder,stem):
    executable=shutil.which('ccx')
    if not executable:raise RuntimeError('CalculiX required; no simulated solver receipt')
    result=subprocess.run([executable,'-i',stem],cwd=folder,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
    (folder/(stem+'.log')).write_text(result.stdout)
    if result.returncode or '*ERROR' in result.stdout.upper() or not (folder/(stem+'.dat')).is_file():raise RuntimeError('CalculiX failed; inspect '+str(folder/(stem+'.log')))
    text=(folder/(stem+'.dat')).read_text();values=[]
    for line in text.splitlines():
        fields=line.split()
        if len(fields)==4 and fields[0].isdigit():
            try:values.append([float(v)for v in fields[1:]])
            except ValueError:pass
    if not values:raise RuntimeError('missing real nodal displacement output')
    return dict(mean_tip_uz_m=sum(v[2]for v in values)/len(values),maximum_tip_displacement_m=max(math.sqrt(sum(x*x for x in v))for v in values),tip_output_count=len(values))


def section_benchmark(folder,*,width=.16,height=.28,wall=.008,length=4,load_n=1000,mesh_size=.06):
    import gmsh
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    sec=rhs(width,height,wall,density_kg_m3=7850);young=210e9;nu=.3
    beam_nodes=[(i+1,length*i/80,0,0)for i in range(81)]
    header=['*HEADING','OSR actual hollow section benchmark, SI units','*NODE']
    lines=header+[f'{i},{x},0,0'for i,x,y,z in beam_nodes]+['*ELEMENT,TYPE=B32R,ELSET=MEMBER']+[f'{i+1},{2*i+1},{2*i+2},{2*i+3}'for i in range(40)]
    lines+=['*MATERIAL,NAME=STEEL','*ELASTIC',f'{young},{nu}','*BEAM SECTION,ELSET=MEMBER,MATERIAL=STEEL,SECTION=BOX',calculix_box(sec,units='m'),'0,1,0','*NSET,NSET=TIP','81','*BOUNDARY','1,1,6','*STEP','*STATIC','*CLOAD',f'81,3,{-load_n}','*NODE PRINT,NSET=TIP','U','*END STEP']
    (folder/'beam.inp').write_text('\n'.join(lines)+'\n');beam=_run(folder,'beam')
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal',0);gmsh.model.add('manufactured-hollow-member')
        outer=gmsh.model.occ.addBox(0,-width/2,-height/2,length,width,height)
        inner=gmsh.model.occ.addBox(-.01,-width/2+wall,-height/2+wall,length+.02,width-2*wall,height-2*wall)
        volumes,_=gmsh.model.occ.cut([(3,outer)],[(3,inner)]);gmsh.model.occ.synchronize()
        geometric_volume=sum(gmsh.model.occ.getMass(d,t)for d,t in volumes)
        if not math.isclose(geometric_volume,sec['area_m2']*length,rel_tol=1e-9):raise ValueError('mesh CAD differs from manufacturing section')
        gmsh.option.setNumber('Mesh.MeshSizeMin',mesh_size/2);gmsh.option.setNumber('Mesh.MeshSizeMax',mesh_size);gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2)
        tags,coords,_=gmsh.model.mesh.getNodes();coords=coords.reshape(-1,3);nodes={int(i):list(map(float,x))for i,x in zip(tags,coords)}
        fixed=[i for i,x in nodes.items()if abs(x[0])<1e-8];tip=[i for i,x in nodes.items()if abs(x[0]-length)<1e-8]
        kinds,elementtags,connectivity=gmsh.model.mesh.getElements(3);elements=[]
        for kind,ids,conn in zip(kinds,elementtags,connectivity):
            if kind!=11:raise ValueError('C3D10 tetrahedron mesh required')
            elements.extend((int(i),list(map(int,c[[0,1,2,3,4,5,6,7,9,8]])))for i,c in zip(ids,conn.reshape(-1,10)))
        gmsh.write(str(folder/'solid.msh'))
    finally:gmsh.finalize()
    lines=header+[str(i)+','+','.join(f'{v:.12g}'for v in x)for i,x in sorted(nodes.items())]+['*ELEMENT,TYPE=C3D10,ELSET=MEMBER']+[str(i)+','+','.join(map(str,c))for i,c in elements]
    lines+=['*MATERIAL,NAME=STEEL','*ELASTIC',f'{young},{nu}','*SOLID SECTION,ELSET=MEMBER,MATERIAL=STEEL','*NSET,NSET=TIP']
    lines +=[','.join(map(str,tip[i:i+12]))for i in range(0,len(tip),12)]+['*BOUNDARY']+[f'{i},1,3'for i in fixed]+['*STEP','*STATIC','*CLOAD']+[f'{i},3,{-load_n/len(tip):.14g}'for i in tip]+['*NODE PRINT,NSET=TIP','U','*END STEP']
    (folder/'solid.inp').write_text('\n'.join(lines)+'\n');solid=_run(folder,'solid')
    analytical=load_n*length**3/(3*young*sec['iy_m4']);difference=abs(beam['mean_tip_uz_m']/solid['mean_tip_uz_m']-1)
    paths=[folder/(stem+suffix)for stem in ('beam','solid')for suffix in ('.inp','.dat','.log')]
    report=dict(schema='osr-real-section-benchmark/1',section=sec,length_m=length,load_n=load_n,
        section_sha256=fingerprint(sec),manufacturing_volume_m3=geometric_volume,beam=beam,solid=solid,
        mesh_size_m=mesh_size,solid_nodes=len(nodes),solid_elements=len(elements),euler_bernoulli_tip_deflection_m=analytical,
        beam_solid_relative_difference=difference,agreement_screen_passed=difference<.1,
        evidence_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},
        scope='clamped cantilever bending only; no joint/contact or torsion qualification',physical_validation=False,production_released=False)
    (folder/'benchmark.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');return report
