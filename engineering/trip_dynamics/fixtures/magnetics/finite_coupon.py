"""Bounded actual finite N35UH coupon at80C/zero current; not a force map.

Reads the exact published half-volume no-yoke stock/grade. Nominal touching
longitudinal PM blocks are represented by their continuous region union.
Copper/aluminium are mu_r=1 and carry no current: their geometry is retained
in inputs but does not create spurious magnetic interfaces. Steel uses the
retained digitised50Hz J(H) proxy, not invented DC material measurements.
"""
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import subprocess
import time


MU0=4e-7*math.pi


def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(v):return sha256(encoded(v)).hexdigest()


def source_input(root):
    path=Path(root)/'docs/design-engine/vehicle-optimisation/refinements.json'
    summary=Path(root)/'docs/design-engine/vehicle-optimisation/summary.json'
    data=json.loads(path.read_bytes());value=next(x['candidate'] for x in data['candidates'] if x['candidate']['sample_id']=='N35-H8-half-no-yoke')
    s=json.loads(summary.read_bytes())
    return dict(value=value,vehicle_candidate_id=s['next_experiment']['selected_candidate_id'],
                source_sha256={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in (path,summary)})


def mesh_case(value,directory,*,margin,h,gap_h):
    import gmsh
    L=value['length_x_m'];regions=value['regions'];pm=[r for r in regions if r['material']==value['grade_id']]
    steel=next(r for r in regions if r['group']=='guideway')
    source_bounds=[]
    gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.logger.start()
    try:
        gmsh.model.add('finite-published-coupon')
        # Only magnetic contrasts need fragmentation at static zero current.
        tools=[]
        for r in [*pm,steel]:
            a,b,c,d=r['bounds_yz_m'];tag=gmsh.model.occ.addBox(-L/2,a,c,L,b-a,d-c)
            tools.append((3,tag));source_bounds.append(dict(id=r['id'],box_m=[-L/2,a,c,L,b-a,d-c]))
        ymin=min(r['bounds_yz_m'][0] for r in regions)-margin
        ymax=max(r['bounds_yz_m'][1] for r in regions)+margin
        zmin=min(r['bounds_yz_m'][2] for r in regions)-margin
        zmax=max(r['bounds_yz_m'][3] for r in regions)+margin
        box=[-L/2-margin,ymin,zmin,L+2*margin,ymax-ymin,zmax-zmin]
        air=gmsh.model.occ.addBox(*box)
        result,mapping=gmsh.model.occ.fragment([(3,air)],tools)
        gmsh.model.occ.synchronize()
        assigned=set();physical=[]
        for i,entities in enumerate(mapping[1:]):
            volumes=[tag for dim,tag in entities if dim==3]
            if not volumes:raise ValueError('source stock disappeared during3D fragmentation')
            pg=100+i if i<len(pm) else 200
            gmsh.model.addPhysicalGroup(3,volumes,pg);assigned.update(volumes);physical.append(pg)
        airs=[tag for dim,tag in result if dim==3 and tag not in assigned]
        gmsh.model.addPhysicalGroup(3,airs,300)
        external=[]
        for _,tag in gmsh.model.getEntities(2):
            bounds=gmsh.model.getBoundingBox(2,tag)
            for axis in range(3):
                if (abs(bounds[axis]-box[axis])<1e-6 and abs(bounds[axis+3]-box[axis])<1e-6 or
                    abs(bounds[axis]-(box[axis]+box[axis+3]))<1e-6 and abs(bounds[axis+3]-(box[axis]+box[axis+3]))<1e-6):
                    external.append(tag);break
        gmsh.model.addPhysicalGroup(2,external,400)
        gmsh.option.setNumber('Mesh.MeshSizeMin',gap_h);gmsh.option.setNumber('Mesh.MeshSizeMax',.09)
        f=gmsh.model.mesh.field.add('Box');gmsh.model.mesh.field.setNumber(f,'VIn',h);gmsh.model.mesh.field.setNumber(f,'VOut',.09)
        for key,v in dict(XMin=-L/2-.02,XMax=L/2+.02,YMin=-.28,YMax=.28,ZMin=-.065,ZMax=.055).items():gmsh.model.mesh.field.setNumber(f,key,v)
        g=gmsh.model.mesh.field.add('Box');gmsh.model.mesh.field.setNumber(g,'VIn',gap_h);gmsh.model.mesh.field.setNumber(g,'VOut',.09)
        for key,v in dict(XMin=-L/2-.005,XMax=L/2+.005,YMin=-.195,YMax=.195,ZMin=-.013,ZMax=.001).items():gmsh.model.mesh.field.setNumber(g,key,v)
        minimum=gmsh.model.mesh.field.add('Min');gmsh.model.mesh.field.setNumbers(minimum,'FieldsList',[f,g]);gmsh.model.mesh.field.setAsBackgroundMesh(minimum)
        gmsh.option.setNumber('Mesh.MeshSizeFromPoints',0);gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary',0)
        gmsh.option.setNumber('Mesh.MshFileVersion',2.2)
        gmsh.model.mesh.generate(3);gmsh.write(str(directory/'coupon.msh'));gmsh.write(str(directory/'coupon.brep'))
        _,nodes,_=gmsh.model.mesh.getNodes();types,tags,_=gmsh.model.mesh.getElements(3)
        count=sum(len(t) for kind,t in zip(types,tags) if kind==4)
        if count>1000000:raise ValueError('tetrahedral trial budget exceeded')
        (directory/'gmsh.log').write_text('\n'.join(gmsh.logger.get())+'\n')
    finally:
        gmsh.logger.stop();gmsh.finalize()
    return dict(nodes=len(nodes)//3,tetrahedra=count,outer_box_m=box,magnetic_stock=source_bounds,pm_regions=pm,physical_pm=physical[:-1])


def formulation(value,mesh,contours,*,method="newton",max_iterations=60):
    if method not in ("newton","picard") or not isinstance(max_iterations,int) or not 1<=max_iterations<=100:
        raise ValueError("bounded declared nonlinear method/iterations required")
    steel_equations=" Integral{[-mu[-{d p}]*Dof{d p},{d p}];In Steel;Jacobian V;Integration I;}"
    if method=="newton":
        steel_equations=" Integral{[-mu[-{d p}]*{d p},{d p}];In Steel;Jacobian V;Integration I;}\n Integral{[-dbdh[-{d p}]*Dof{d p},{d p}];In Steel;Jacobian V;Integration I;}\n Integral{[dbdh[-{d p}]*{d p},{d p}];In Steel;Jacobian V;Integration I;}"
    grade=value['materials'][value['grade_id']];steel=value['materials']['steel']
    mu_r=grade['recoil_relative_permeability'];scale=1+grade['br_temperature_coefficient_per_k']*60
    pairs=','.join(f'{x:.17g},{y:.17g}' for x,y in zip(steel['h_a_m'],steel['j_t']))
    pm_groups=','.join(str(x) for x in mesh['physical_pm'])
    br='\n'.join(f'br[Region[{pg}]]=Vector[0,{r["Br_y_T"]*scale:.17g},{r["Br_z_T"]*scale:.17g}];\n dir[Region[{pg}]]=Vector[0,{r["Br_y_T"]/grade["br_20c_t"]:.17g},{r["Br_z_T"]/grade["br_20c_t"]:.17g}];' for pg,r in zip(mesh['physical_pm'],mesh['pm_regions']))
    prints=[]
    for index,c in enumerate(contours):
        lo,hi=c;counts=[64,24,12]
        for axis in range(3):
            others=[i for i in range(3) if i!=axis]
            for side in (0,1):
                a=list(lo);a[axis]=hi[axis] if side else lo[axis]
                b=a.copy();b[others[0]]=hi[others[0]]
                d=a.copy();d[others[1]]=hi[others[1]]
                pts=' '.join('{'+','.join(f'{x:.17g}' for x in p)+'}' for p in (a,b,d))
                prints.append(f'Print[B,OnPlane{{{pts}}}{{{counts[others[0]]},{counts[others[1]]}}},File "face-{index}-{axis}-{side}.txt",Format SimpleTable];')
    return f'''mu0=4.e-7*Pi;
Group{{Air=Region[300];Steel=Region[200];PM=Region[{{{pm_groups}}}];Domain=Region[{{Air,Steel,PM}}];Outer=Region[400];}}
Function{{
 j[] = InterpolationLinear[Min[Norm[$1],100000.]]{{{pairs}}};
 dj[] = Norm[$1]>100000. ? 0. : dInterpolationLinear[Norm[$1]]{{{pairs}}};
 mu[Air]=mu0;mu[PM]={mu_r:.17g}*mu0;
 mu[Steel]=Norm[$1]<1.e-6 ? mu0+0.0025 : mu0+j[$1]/Norm[$1];
 dbdh[Steel]=mu[$1]*TensorDiag[1,1,1]+(dj[$1]-j[$1]/Max[Norm[$1],1.e-6])/Max[SquNorm[$1],1.e-12]*SquDyadicProduct[$1];
 br[Air]=Vector[0,0,0];br[Steel]=Vector[0,0,0];
 {br}
}}
Constraint{{{{Name Zero;Case{{{{Region Outer;Value 0.;}}}}}}}}
Jacobian{{{{Name V;Case{{{{Region All;Jacobian Vol;}}}}}}}}
Integration{{{{Name I;Case{{{{Type Gauss;Case{{{{GeoElement Tetrahedron;NumberOfPoints 4;}}}}}}}}}}}}
FunctionSpace{{{{Name Potential;Type Form0;BasisFunction{{{{Name sn;NameOfCoef pn;Function BF_Node;Support Domain;Entity NodesOf[All];}}}}Constraint{{{{NameOfCoef pn;EntityType NodesOf;NameOfConstraint Zero;}}}}}}}}
Formulation{{{{Name Magnet3D;Type FemEquation;Quantity{{{{Name p;Type Local;NameOfSpace Potential;}}}}
Equation{{
 Integral{{[-mu[]*Dof{{d p}},{{d p}}];In Region[{{Air,PM}}];Jacobian V;Integration I;}}
 Integral{{[br[],{{d p}}];In PM;Jacobian V;Integration I;}}
{steel_equations}
}}}}}}
Resolution{{{{Name Solve;System{{{{Name S;NameOfFormulation Magnet3D;}}}}Operation{{
 InitSolution[S];Generate[S];Solve[S];Generate[S];GetResidual[S,$initial];Evaluate[$res=$initial,$iter=0];
 While[$res>1.e-9 && $res/$initial>1.e-7 && $iter<{max_iterations}]{{Solve[S];Generate[S];GetResidual[S,$res];Evaluate[$iter=$iter+1];Print[{{$iter,$res,$res/$initial}},Format "NONLINEAR %g %.15e %.15e"];}}
 SaveSolution[S];
}}}}}}
PostProcessing{{{{Name Results;NameOfFormulation Magnet3D;Quantity{{
 {{Name B;Value{{Term{{[-mu[-{{d p}}]*{{d p}}+br[]];In Domain;Jacobian V;}}}}}}
 {{Name Hparallel;Value{{Term{{[-{{d p}}*dir[]];In PM;Jacobian V;}}}}}}
 {{Name SteelB;Value{{Term{{[Norm[mu[-{{d p}}]*{{d p}}]];In Steel;Jacobian V;}}}}}}
}}}}}}
PostOperation{{{{Name Results;NameOfPostProcessing Results;Operation{{
 {' '.join(prints)}
 Print[Hparallel,OnElementsOf PM,Depth 0,File "PM-H.txt",Format SimpleTable];
 Print[SteelB,OnElementsOf Steel,Depth 0,File "steel-B.txt",Format SimpleTable];
}}}}}}
'''


def maxwell(directory,contours):
    import numpy as np
    result=[]
    for index,(lo,hi) in enumerate(contours):
        force=np.zeros(3);moment=np.zeros(3)
        for axis in range(3):
            others=[i for i in range(3) if i!=axis]
            for side in (0,1):
                a=np.loadtxt(directory/f'face-{index}-{axis}-{side}.txt')
                if a.ndim!=2 or a.shape[1]!=6 or not np.isfinite(a).all():raise ValueError('incomplete air-face vector field')
                # OnPlane emits unique nodal samples in SimpleTable.
                points,indices=np.unique(np.round(a[:,:3],12),axis=0,return_index=True);B=a[indices,3:]
                grids=[np.unique(points[:,k]) for k in others]
                if len(points)!=len(grids[0])*len(grids[1]):raise ValueError('incomplete air contour sampling grid')
                normal=np.zeros(3);normal[axis]=1 if side else -1
                traction=(B*(B@normal)[:,None]-.5*np.sum(B*B,axis=1)[:,None]*normal)/MU0
                area=(hi[others[0]]-lo[others[0]])*(hi[others[1]]-lo[others[1]])
                weights=np.ones(len(points))
                for k,grid in zip(others,grids):weights[(abs(points[:,k]-grid[0])<1e-10)|(abs(points[:,k]-grid[-1])<1e-10)]*=.5
                weighted=traction*(weights*area/((len(grids[0])-1)*(len(grids[1])-1)))[:,None]
                force+=weighted.sum(axis=0);moment+=np.cross(points,weighted).sum(axis=0)
        result.append(dict(force_N=force.tolist(),moment_Nm=moment.tolist(),moment_origin_m=[0.,0.,0.]))
    return result


def run(root,output,getdp,*,cases=3,timeout_s=300,reuse_mesh_root=None,method="newton",max_iterations=60):
    if not 0<timeout_s<=300:raise ValueError('solve timeout must be bounded to300s')
    root=Path(root).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    source=source_input(root);value=source['value'];driver_bytes=Path(__file__).read_bytes();before=sha256(driver_bytes).hexdigest()
    (output/'driver-executed.py').write_bytes(driver_bytes)
    binary_sha256=sha256(Path(getdp).read_bytes()).hexdigest()
    version=(lambda p:(p.stdout+p.stderr).strip())(subprocess.run([str(getdp),'-version'],capture_output=True,text=True,check=True))
    train=[p for p in value['stock_parts'] if p['group']=='train']
    lo=[min(p['at_m'][k] for p in train) for k in range(3)]
    hi=[max(p['at_m'][k]+p['size_m'][k] for p in train) for k in range(3)]
    contours=[[[v-d for v in lo],[v+d for v in hi]] for d in (.0042,.0066)]
    rows=[]
    plan=[('coarse',.15,.023,.008),('fine',.15,.017,.006),('expanded',.25,.017,.006)][:cases]
    for name,margin,h,gh in plan:
        directory=output/name;directory.mkdir(exist_ok=False);started=time.monotonic()
        row=dict(name=name,margin_m=margin,near_mesh_size_m=h,gap_mesh_size_m=gh)
        (directory/'source-input.json').write_bytes(encoded(source))
        try:
            reused=Path(reuse_mesh_root)/name if reuse_mesh_root else None
            if reused and (reused/'coupon.msh').is_file():
                receipt=json.loads((Path(reuse_mesh_root)/(name+'-receipt.json')).read_bytes())
                original=json.loads((reused/'source-input.json').read_bytes())
                if original!=source or any(receipt[k]!=row[k] for k in ('name','margin_m','near_mesh_size_m','gap_mesh_size_m')):
                    raise ValueError('reused mesh source/settings mismatch')
                for filename in ('coupon.msh','coupon.brep','gmsh.log'):
                    raw=(reused/filename).read_bytes()
                    if sha256(raw).hexdigest()!=receipt['files_sha256'][filename]:raise ValueError('reused mesh bytes changed')
                    (directory/filename).write_bytes(raw)
                mesh=receipt['mesh'];row['reused_mesh_source_sha256']=receipt['files_sha256']['coupon.msh']
            else:
                mesh=mesh_case(value,directory,margin=margin,h=h,gap_h=gh)
            row['mesh']=mesh
            (directory/'coupon.pro').write_text(formulation(value,mesh,contours,method=method,max_iterations=max_iterations))
            command=[str(Path(getdp).resolve()),'coupon.pro','-msh','coupon.msh','-solve','Solve','-pos','Results']
            process=subprocess.run(command,cwd=directory,capture_output=True,text=True,timeout=timeout_s)
            (directory/'getdp.stdout.log').write_text(process.stdout);(directory/'getdp.stderr.log').write_text(process.stderr)
            row['returncode']=process.returncode
            if process.returncode:raise RuntimeError('GetDP failed; retained exact input/log')
            iterations=re.findall(r'NONLINEAR\s+(\d+)\s+([\deE+.-]+)\s+([\deE+.-]+)',process.stdout)
            if not iterations:raise ValueError('nonlinear residuals absent')
            i,absolute,relative=iterations[-1];row.update(iterations=int(i),residual_absolute=float(absolute),residual_relative=float(relative),
                nonlinear_converged=float(absolute)<1e-9 or float(relative)<1e-7)
            row['air_contour_results']=maxwell(directory,contours)
            import numpy as np
            row['PM_Hparallel_min_A_per_m']=float(np.loadtxt(directory/'PM-H.txt')[:,-1].min())
            row['steel_B_peak_T']=float(np.loadtxt(directory/'steel-B.txt')[:,-1].max())
            row['execution_status']='executed'
            row['valid_for_force_map']=False  # one point cannot establish mesh/domain or derivative validity
        except subprocess.TimeoutExpired as error:
            for name_log,content in [('stdout',error.stdout),('stderr',error.stderr)]:
                if content is not None:(directory/('getdp.'+name_log+'.log')).write_bytes(content if isinstance(content,bytes) else content.encode())
            row.update(execution_status='interrupted',error_type=type(error).__name__,error=str(error),nonlinear_converged=False)
        except Exception as error:
            row.update(execution_status='refused',error_type=type(error).__name__,error=str(error))
        row['elapsed_s']=time.monotonic()-started
        row['files_sha256']={p.name:sha256(p.read_bytes()).hexdigest() for p in directory.iterdir() if p.is_file()}
        rows.append(row);(output/(name+'-receipt.json')).write_bytes(encoded(row));print(name,row['execution_status'],row.get('air_contour_results',row.get('error')),flush=True)
        if row['execution_status']!='executed':break
    if sha256(Path(__file__).read_bytes()).hexdigest()!=before:raise ValueError('finite coupon driver source changed')
    if sha256(Path(getdp).read_bytes()).hexdigest()!=binary_sha256:raise ValueError('GetDP executable changed during execution')
    result=dict(schema='osr-finite-coupon3d-diagnostic/1',source=source,driver_sha256=before,nonlinear_method=method,maximum_nonlinear_iterations=max_iterations,
        getdp_executable_sha256=binary_sha256,getdp_version=version,
        frame=dict(handedness='right',axes=dict(x='travel',y='transverse-left',z='up'),moment_origin_m=[0.,0.,0.]),
        candidate_id=source['vehicle_candidate_id'],magnet_component_id=value['physical_id'],temperature_C=80.,currents_A={},
        material_hypothesis='Published N35UH minimum Br/Hcj and recoil1.05; retained SIWATT50Hz J(H)proxy with isotropic interpolation',
        magnetic_geometry='Finite1m PM-array region union and finite same-length steel facing, not an entire guideway',
        contours_m=contours,rows=rows,force_map_generated=False,physical_accepted=False,
        limitations=['No current closure solved: zero-current only','Nominal touching PM joints, no actual adhesive gaps',
                     'No temperature-dependent steel data','Finite Dirichlet air box; mesh/domain evidence must be assessed',
                     'No repeated thermal, guidance/roll envelope, speed losses, fault or journey claim'])
    (output/'receipt.json').write_bytes(encoded(result));return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--getdp',type=Path,required=True);p.add_argument('--cases',type=int,choices=(1,2,3),default=3);p.add_argument('--reuse-mesh-root',type=Path);p.add_argument('--method',choices=('newton','picard'),default='newton');p.add_argument('--max-iterations',type=int,default=60)
    a=p.parse_args();run(a.root,a.output,a.getdp,cases=a.cases,reuse_mesh_root=a.reuse_mesh_root,method=a.method,max_iterations=a.max_iterations)
