"""Run a bounded, manufactured nonlinear3D GetDP method fixture.

This is a uniform-flux series air/nonlinear slab, meshed as3D tetrahedra.
Its analytical constitutive law is deliberately manufactured, not steel data.
The reported force is air Maxwell pressure on a parallel face, not train lift.
"""
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import time


def run(output, getdp, *, timeout_s=300):
    import gmsh
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    getdp=Path(getdp).resolve()
    if not getdp.is_file():raise ValueError('explicit existing GetDP executable required')
    if not 0<timeout_s<=300:raise ValueError('fixture timeout must be bounded to300s')
    fixture=Path(__file__).parent
    src={name:sha256((fixture/name).read_bytes()).hexdigest() for name in ('slab.geo','slab.pro','run_fixture.py')}
    mu0=4e-7*math.pi;B=mu0*1000+1.5*math.tanh(1000/1500)
    exact_force=B*B/(2*mu0)*.01
    records=[]
    for name,h in [('coarse',.025),('fine',.0125)]:
        directory=output/name;directory.mkdir(exist_ok=False)
        geo=(fixture/'slab.geo').read_text().replace('h = {0.025}',f'h = {{{h:.17g}}}')
        (directory/'slab.geo').write_text(geo)
        shutil.copyfile(fixture/'slab.pro',directory/'slab.pro')
        started=time.monotonic()
        gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.logger.start()
        try:
            gmsh.open(str(directory/'slab.geo'));gmsh.model.mesh.generate(3)
            mesh=directory/'slab.msh';gmsh.write(str(mesh))
            types,tags,_=gmsh.model.mesh.getElements(3)
            tetrahedra=sum(len(t) for kind,t in zip(types,tags) if kind==4)
            if not tetrahedra:raise ValueError('actual3D tetrahedra required')
            (directory/'gmsh.log').write_text('\n'.join(gmsh.logger.get())+'\n')
        finally:
            gmsh.logger.stop();gmsh.finalize()
        command=[str(getdp),'slab.pro','-msh','slab.msh','-solve','Solve','-pos','Results']
        process=subprocess.run(command,cwd=directory,capture_output=True,text=True,timeout=timeout_s)
        (directory/'getdp.stdout.log').write_text(process.stdout)
        (directory/'getdp.stderr.log').write_text(process.stderr)
        if process.returncode:raise RuntimeError('GetDP fixture failed; retained logs in '+str(directory))
        residuals=re.findall(r'PICARD\s+(\d+)\s+([\deE+.-]+)\s+([\deE+.-]+)',process.stdout)
        if not residuals:raise ValueError('nonlinear iteration record missing')
        iterations,absolute,relative=residuals[-1]
        converged=float(absolute)<=1e-10 or float(relative)<=1e-10
        bz=float((directory/'mean-Bz.txt').read_text().split()[-1])
        force=float((directory/'air-force.txt').read_text().split()[-1])
        record=dict(name=name,mesh_size_m=h,tetrahedra=tetrahedra,command=command,
            returncode=process.returncode,nonlinear_iterations=int(iterations),residual_absolute=float(absolute),
            residual_relative=float(relative),nonlinear_converged=converged,mean_air_Bz_T=bz,
            air_pressure_force_N=force,relative_B_error=abs(bz/B-1),relative_force_error=abs(force/exact_force-1),
            elapsed_s=time.monotonic()-started,
            files_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in directory.iterdir() if p.is_file()})
        records.append(record)
    if src!={name:sha256((fixture/name).read_bytes()).hexdigest() for name in src}:raise ValueError('fixture source changed')
    difference=abs(records[0]['air_pressure_force_N']-records[1]['air_pressure_force_N'])/exact_force
    value=dict(schema='osr-nonlinear3d-method-fixture/1',source_sha256=src,
        getdp_executable_sha256=sha256(getdp.read_bytes()).hexdigest(),
        getdp_version=(lambda p:(p.stdout+p.stderr).strip())(subprocess.run([str(getdp),'-version'],capture_output=True,text=True,check=True)),gmsh_version=gmsh.__version__,
        exact_B_T=B,exact_air_pressure_force_N=exact_force,
        manufactured_law='B(H)=mu0*H+1.5T*tanh(H/1500A_per_m)',
        records=records,relative_mesh_force_difference=difference,
        passed=all(r['nonlinear_converged'] and r['relative_force_error']<1e-6 and r['relative_B_error']<1e-6 for r in records) and difference<1e-6,
        source_reference='https://getdp.info/doc/texinfo/getdp.html',
        scope='Manufactured uniform-flux nonlinear3D tetrahedral scalar-potential method check; air Maxwell pressure integral, not net train/body force',
        candidate_id=None,candidate_force_map_generated=False,physical_accepted=False,
        limitations=['No actual PM/coil/steel grade','No fringing/open-boundary validation','No candidate3D geometry','No field/force/loss map or journey qualified'])
    (output/'receipt.json').write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    return value


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--getdp',type=Path,required=True)
    args=parser.parse_args();r=run(args.output,args.getdp);print(json.dumps({k:r[k] for k in ('passed','exact_B_T','exact_air_pressure_force_N','relative_mesh_force_difference')},indent=2))
