"""Executed CalculiX composite method fixture, not an equipped-car model.

The synthetic [0/90/90/0] S8R cantilever has the same declared material and
cylindrical boundary as the retained analytical laminate coupon. Every ply has
an explicit orientation; no blank-orientation inheritance is relied upon.
"""
from hashlib import sha256
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

from . import ROOT,FLAGS
from .common import identity,write,sources

MANUAL='https://www.dhondt.de/ccx_2.23.pdf'
PROVENANCE=[dict(url=MANUAL,scope='CalculiX 2.23 *SHELL SECTION COMPOSITE, S8R, *ELASTIC ENGINEERING CONSTANTS; explicit ply orientations'),
            dict(url='https://github.com/Dhondtguido/CalculiX',scope='Primary solver source; no whole-car or material qualification transferred')]


def analytical():
    E1,E2,nu12,G12,rho=25e9,8e9,.25,4e9,1900.
    nu21=nu12*E2/E1;denominator=1-nu12*nu21
    Q11,Q22=E1/denominator,E2/denominator
    bounds=[-.002,-.001,0.,.001,.002]
    D11=sum((Q11 if angle==0 else Q22)*(bounds[i+1]**3-bounds[i]**3)/3 for i,angle in enumerate((0,90,90,0)))
    length,width,thickness,force=1.,.1,.004,.1;EI=width*D11
    return dict(length_m=length,width_m=width,thickness_m=thickness,tip_force_N=force,
        lamina=dict(E1_Pa=E1,E2_Pa=E2,E3_Pa=E2,nu12=nu12,nu13=nu12,nu23=.30,
                    G12_Pa=G12,G13_Pa=G12,G23_Pa=3e9,density_kg_m3=rho),
        ply_angles_deg=[0,90,90,0],ply_thickness_m=.001,D11_N_m=D11,EI_N_m2=EI,
        mass_kg=length*width*thickness*rho,tip_deflection_m=force*length**3/(3*EI),
        first_frequency_hz=1.875104068711961**2/(2*math.pi*length**2)*math.sqrt(EI/(rho*width*thickness)),
        scope='Classical-laminate cylindrical-bending thin-beam limit; synthetic constants, no certified GFRP, joints or equipped body')


def deck(nx,ny=2):
    if type(nx) is not int or nx not in (8,16) or ny!=2:raise ValueError('bounded 8/16 by 2 S8R meshes required')
    a=analytical();nodes={};lines=['*HEADING','OSR synthetic composite method fixture, SI m kg N s','*NODE']
    for j in range(2*ny+1):
        for i in range(2*nx+1):
            if i%2 and j%2:continue
            node=len(nodes)+1;nodes[i,j]=node
            lines.append(f'{node},{i*a["length_m"]/(2*nx):.16g},{j*a["width_m"]/(2*ny):.16g},0.')
    lines.append('*ELEMENT,TYPE=S8R,ELSET=EALL')
    element=0
    for j in range(0,2*ny,2):
        for i in range(0,2*nx,2):
            element+=1
            grid=((i,j),(i+2,j),(i+2,j+2),(i,j+2),(i+1,j),(i+2,j+1),(i+1,j+2),(i,j+1))
            lines.append(','.join(map(str,[element,*[nodes[p] for p in grid]])))
    tip=[n for (i,j),n in nodes.items() if i==2*nx];clamp=[n for (i,j),n in nodes.items() if i==0]
    for name,values in [('NALL',list(nodes.values())),('TIP',tip),('CLAMP',clamp)]:
        lines.append('*NSET,NSET='+name)
        for start in range(0,len(values),12):lines.append(','.join(map(str,values[start:start+12])))
    lines += ['*MATERIAL,NAME=PLY','*ELASTIC,TYPE=ENGINEERING CONSTANTS',
              '25.e9,8.e9,8.e9,.25,.25,.30,4.e9,4.e9','3.e9','*DENSITY','1900.',
              '*ORIENTATION,NAME=O0,SYSTEM=RECTANGULAR','1.,0.,0.,0.,1.,0.',
              '*ORIENTATION,NAME=O90,SYSTEM=RECTANGULAR','0.,1.,0.,-1.,0.,0.',
              '*SHELL SECTION,ELSET=EALL,COMPOSITE',
              '.001,,PLY,O0','.001,,PLY,O90','.001,,PLY,O90','.001,,PLY,O0',
              '*BOUNDARY','CLAMP,1,6','NALL,2,2','NALL,4,4','*STEP','*STATIC','*CLOAD']
    lines += [f'{node},3,{-a["tip_force_N"]/len(tip):.16g}' for node in tip]
    lines += ['*NODE PRINT,NSET=TIP','U','*NODE PRINT,NSET=CLAMP','RF','*END STEP',
              '*STEP','*FREQUENCY','4','*END STEP']
    return '\n'.join(lines)+'\n',dict(nx=nx,ny=ny,node_count=len(nodes),element_count=element,tip_nodes=tip,clamp_nodes=clamp)


def parse_dat(text,mesh):
    displacements={};reactions={};mode=None;frequencies=[];static_done=False
    for line in text.splitlines():
        lower=line.lower()
        if 'EIGENVALUEOUTPUT' in ''.join(line.upper().split()):static_done=True;mode=None;continue
        if not static_done and 'displacements' in lower and 'set tip' in lower:mode='u';continue
        if not static_done and 'forces' in lower and 'set clamp' in lower:mode='rf';continue
        if 'eigenvalue' in lower and 'frequency' in lower:mode='frequency';continue
        fields=line.split()
        if not fields or not fields[0].isdigit():continue
        try:values=[float(v.replace('D','E')) for v in fields[1:]]
        except ValueError:continue
        if mode in ('u','rf') and len(values)==3:
            (displacements if mode=='u' else reactions)[int(fields[0])]=values
        elif mode=='frequency' and len(values)==4:
            frequencies.append(values[2])
            if len(frequencies)==4:mode=None
    if set(displacements)!=set(mesh['tip_nodes']) or set(reactions)!=set(mesh['clamp_nodes']):raise ValueError('complete tip displacement and clamp reaction outputs required')
    if not frequencies or min(frequencies)<=0:raise ValueError('positive native frequencies required')
    return dict(mean_tip_displacement_z_m=sum(v[2] for v in displacements.values())/len(displacements),
        clamp_reaction_z_N=sum(v[2] for v in reactions.values()),frequencies_hz=frequencies,
        maximum_tip_transverse_variation_m=max(v[2] for v in displacements.values())-min(v[2] for v in displacements.values()))


def _inventory(directory,exclude=()):
    return {p.relative_to(directory).as_posix():sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(directory).rglob('*')) if p.is_file() and p.name not in exclude}


def run_structural_fixture(output,ccx=None,root=ROOT):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False);before=sources(root)
    tool=shutil.which('ccx') if ccx is None else str(Path(ccx).resolve())
    if tool is not None and (not Path(tool).is_file() or not os.access(tool,os.X_OK)):tool=None
    result=dict(schema='osr-native-composite-fixture/1',scope='benchmark-coupon',
        analytical=analytical(),provenance=PROVENANCE,rows=[],source_sha256=before,**FLAGS)
    if tool is None:
        result.update(execution_status='not-run',method_screen='unknown',reason='CalculiX executable unavailable',tool=None)
    else:
        probe=subprocess.run([tool,'-v'],capture_output=True,text=True,timeout=10)
        result['tool']=dict(path=tool,sha256=sha256(Path(tool).read_bytes()).hexdigest(),version_stdout=probe.stdout,version_stderr=probe.stderr,probe_returncode=probe.returncode)
        started=time.monotonic()
        for nx in (8,16):
            directory=output/f'mesh-{nx}';directory.mkdir();text,mesh=deck(nx);(directory/'coupon.inp').write_text(text)
            budget=min(120.,240.-(time.monotonic()-started));env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',CCX_NPROC_RESULTS='1',CCX_NPROC_EQUATION_SOLVER='1')
            execution=dict(command=[tool,'-i','coupon'],deadline_s=budget)
            row=dict(mesh=mesh,execution_status='not-run',numerical_validity='unknown',**FLAGS)
            if budget>0:
                trial=time.monotonic()
                with (directory/'stdout.log').open('wb') as stdout,(directory/'stderr.log').open('wb') as stderr:
                    process=subprocess.Popen(execution['command'],cwd=directory,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
                    try:code=process.wait(timeout=budget);timed=False
                    except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=5);code=process.returncode;timed=True
                execution.update(returncode=code,timed_out=timed,elapsed_s=time.monotonic()-trial)
                row['execution_status']='interrupted' if timed else 'completed' if code==0 else 'tool-error'
                if code==0:
                    try:
                        parsed=parse_dat((directory/'coupon.dat').read_text(),mesh);a=result['analytical']
                        row.update(native=parsed,numerical_validity='valid',tip_relative_error=abs(abs(parsed['mean_tip_displacement_z_m'])/a['tip_deflection_m']-1),
                            frequency_relative_error=abs(parsed['frequencies_hz'][0]/a['first_frequency_hz']-1),
                            force_balance_residual_N=abs(parsed['clamp_reaction_z_N']-a['tip_force_N']))
                    except (ValueError,OSError) as error:row.update(numerical_validity='invalid-output',error=str(error))
            row['execution']=execution;write(directory/'record.json',row);result['rows'].append(row)
        valid=all(r['numerical_validity']=='valid' for r in result['rows'])
        good=valid and all(r['tip_relative_error']<=.05 and r['frequency_relative_error']<=.05 and r['force_balance_residual_N']<=1e-6 for r in result['rows'])
        if valid:
            a,b=result['rows'];result['refinement']=dict(tip_change_relative=abs(b['native']['mean_tip_displacement_z_m']/a['native']['mean_tip_displacement_z_m']-1),
                first_frequency_change_relative=abs(b['native']['frequencies_hz'][0]/a['native']['frequencies_hz'][0]-1),
                accuracy_improves_or_small=all(b[k]<=a[k]+.001 for k in ('tip_relative_error','frequency_relative_error')))
            good=good and result['refinement']['accuracy_improves_or_small']
        result.update(execution_status='completed',method_screen='pass' if good else 'fail')
    if sources(root)!=before:raise ValueError('structural fixture sources changed during execution')
    result['evaluation_id']=identity(result);write(output/'result.json',result)
    write(output/'manifest.json',dict(source_sha256=before,files_sha256=_inventory(output,('manifest.json',)),evaluation_id=result['evaluation_id'],**FLAGS))
    return result


def verify_structural_fixture(output,root=ROOT):
    """Recompute native-output comparisons and exact input decks; no solve."""
    import json
    output=Path(output).resolve();value=json.loads((output/'result.json').read_bytes())
    manifest=json.loads((output/'manifest.json').read_bytes())
    if any(p.is_symlink() for p in output.rglob('*')):raise ValueError('ordinary retained structural files required')
    if value['source_sha256']!=sources(root) or manifest['source_sha256']!=value['source_sha256']:
        raise ValueError('structural source snapshot differs')
    if manifest['files_sha256']!=_inventory(output,('manifest.json',)):raise ValueError('structural payload differs')
    if value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}) or manifest['evaluation_id']!=value['evaluation_id']:
        raise ValueError('structural evaluation identity differs')
    if value['analytical']!=analytical() or value['provenance']!=PROVENANCE or value['scope']!='benchmark-coupon':raise ValueError('structural fixture definition differs')
    if any(value.get(k) is not v for k,v in FLAGS.items()):raise ValueError('coupon cannot qualify a car')
    if value['tool'] is None:
        if value['rows'] or value['method_screen']!='unknown' or value['execution_status']!='not-run':raise ValueError('unexecuted native fixture cannot pass')
        return dict(current=True,execution_status='not-run',method_screen='unknown',physical_accepted=False)
    if len(value['rows'])!=2 or value['execution_status']!='completed':raise ValueError('both bounded native meshes required')
    expected=[]
    for nx,row in zip((8,16),value['rows']):
        directory=output/f'mesh-{nx}';text,mesh=deck(nx)
        if (directory/'coupon.inp').read_text()!=text or row['mesh']!=mesh:raise ValueError('structural mesh, load, orientation or boundary input differs')
        if json.loads((directory/'record.json').read_bytes())!=row:raise ValueError('native record differs')
        if any(row.get(k) is not v for k,v in FLAGS.items()):raise ValueError('native method row cannot assert vehicle qualification')
        execution=row['execution']
        if execution['command']!=[value['tool']['path'],'-i','coupon'] or not 0<execution['deadline_s']<=120.:raise ValueError('bounded native execution differs')
        if row['numerical_validity']=='valid':
            if row['execution_status']!='completed' or execution['returncode']!=0 or execution['timed_out'] is not False:raise ValueError('successful native worker required for numerical credit')
            stdout=(directory/'stdout.log').read_text()
            if 'Job finished' not in stdout or '*ERROR' in stdout:raise ValueError('complete error-free native solver log required')
            parsed=parse_dat((directory/'coupon.dat').read_text(),mesh);a=analytical()
            derived=dict(native=parsed,tip_relative_error=abs(abs(parsed['mean_tip_displacement_z_m'])/a['tip_deflection_m']-1),
                frequency_relative_error=abs(parsed['frequencies_hz'][0]/a['first_frequency_hz']-1),
                force_balance_residual_N=abs(parsed['clamp_reaction_z_N']-a['tip_force_N']))
            if any(row[k]!=v for k,v in derived.items()):raise ValueError('native comparison does not reproduce archived output')
        elif any(k in row for k in ('native','tip_relative_error','frequency_relative_error','force_balance_residual_N')):
            raise ValueError('invalid native row cannot supply numerical credit')
        expected.append(row)
    valid=all(r['numerical_validity']=='valid' for r in expected)
    good=valid and all(r['tip_relative_error']<=.05 and r['frequency_relative_error']<=.05 and r['force_balance_residual_N']<=1e-6 for r in expected)
    if valid:
        a,b=expected;refinement=dict(tip_change_relative=abs(b['native']['mean_tip_displacement_z_m']/a['native']['mean_tip_displacement_z_m']-1),
            first_frequency_change_relative=abs(b['native']['frequencies_hz'][0]/a['native']['frequencies_hz'][0]-1),
            accuracy_improves_or_small=all(b[k]<=a[k]+.001 for k in ('tip_relative_error','frequency_relative_error')))
        if value.get('refinement')!=refinement:raise ValueError('native refinement trend differs')
        good=good and refinement['accuracy_improves_or_small']
    elif 'refinement' in value:raise ValueError('invalid native meshes cannot provide a refinement trend')
    if value['method_screen']!=('pass' if good else 'fail'):raise ValueError('native method disposition differs')
    return dict(current=True,execution_status=value['execution_status'],method_screen=value['method_screen'],physical_accepted=False)
