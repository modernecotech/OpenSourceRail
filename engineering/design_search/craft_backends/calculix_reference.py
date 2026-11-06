"""Independent, bounded CalculiX controls for the optional Craft backend pilot.

SI decks are built without importing FieldCraft's recipe or result code. C3D20
uses full integration and consistent quadratic-face nodal traction weights.
These are numerical controls, not railway beam/body/shuttle qualification.
Reference: https://www.dhondt.de/ccx_2.23.pdf (*ELEMENT, *NODE PRINT, T3D2).
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import fsum, isfinite
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import signal
import subprocess
import time

SOURCE = 'engineering/design_search/craft_backends/calculix_reference.py'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False)
SCREENS = dict(theory_relative=.01, refinement_relative=.005, force_relative=1e-6)
CORNERS = ((0,0,0),(2,0,0),(2,2,0),(0,2,0),
           (0,0,2),(2,0,2),(2,2,2),(0,2,2))
EDGES = ((1,0,0),(2,1,0),(1,2,0),(0,1,0),
         (1,0,2),(2,1,2),(1,2,2),(0,1,2),
         (0,0,1),(2,0,1),(2,2,1),(0,2,1))


def _encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def _digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _numbers(values):
    return [','.join(map(str,values[i:i+15])) for i in range(0,len(values),15)]


def cantilever_deck(divisions=(8,2,2)):
    """Full-integration 20-node hexes; integrated constant end-face traction."""
    if not isinstance(divisions,(tuple,list)) or len(divisions)!=3 or any(type(n) is not int for n in divisions) or tuple(divisions) not in ((8,2,2),(16,4,4)):
        raise ValueError('Only predeclared coarse/fine C3D20 pilot meshes are supported')
    nx,ny,nz=divisions
    index={};xyz={}
    for i in range(2*nx+1):
        for j in range(2*ny+1):
            for k in range(2*nz+1):
                if (i%2)+(j%2)+(k%2)>1:
                    continue
                node=len(index)+1;index[i,j,k]=node
                xyz[node]=[i/(2*nx),j*.1/(2*ny),k*.1/(2*nz)]
    elements=[]
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                elements.append([index[2*i+a,2*j+b,2*k+c] for a,b,c in CORNERS+EDGES])
    loads={}
    # Integral of serendipity Q8 shape functions: corner -A/12,
    # edge midpoint A/3. Negative corner forces are mathematically required;
    # equal nodal forces would represent a different traction distribution.
    face=((0,0,-1/12),(2,0,-1/12),(2,2,-1/12),(0,2,-1/12),
          (1,0,1/3),(2,1,1/3),(1,2,1/3),(0,1,1/3))
    for j in range(ny):
        for k in range(nz):
            for a,b,weight in face:
                n=index[2*nx,2*j+a,2*k+b]
                loads.setdefault(n,[]).append(-1000*weight/(ny*nz))
    loads={n:fsum(v) for n,v in loads.items()}
    root=[n for (i,j,k),n in index.items() if i==0]
    tip=index[2*nx,ny,nz]
    lines=['*HEADING','Independent Craft pilot elastic control; SI m-kg-s-N-Pa',
           '** L=1m b=h=0.1m E=70e9Pa nu=0 Fz=-1000N', '*NODE']
    lines += [str(n)+','+','.join(f'{v:.17g}' for v in p) for n,p in xyz.items()]
    lines += ['*ELEMENT,TYPE=C3D20,ELSET=SOLID']
    for e,nodes in enumerate(elements,1):
        lines += [','.join(map(str,[e]+nodes[:15]))+',', ','.join(map(str,nodes[15:]))]
    lines += ['*NSET,NSET=ROOT',*_numbers(root),'*NSET,NSET=TIP',str(tip),
              '*MATERIAL,NAME=ELASTIC','*ELASTIC','70000000000,0',
              '*SOLID SECTION,ELSET=SOLID,MATERIAL=ELASTIC',
              '*BOUNDARY','ROOT,1,3','*STEP','*STATIC','*CLOAD']
    lines += [f'{n},3,{f:.17g}' for n,f in sorted(loads.items())]
    lines += ['*NODE PRINT,NSET=TIP','U','*NODE PRINT,NSET=ROOT','RF','*END STEP','']
    E=70e9;I=.1*.1**3/12;G=E/2
    theory=-1000/(3*E*I)-1000/((5/6)*G*.1*.1)
    definition=dict(case='cantilever',units='m-kg-s-N-Pa',divisions=list(divisions),
        element_kind='C3D20',element_count=len(elements),node_count=len(xyz),
        node_xyz_m={str(n):p for n,p in xyz.items()},root_nodes=root,tip_node=tip,
        applied_N=[0.,0.,fsum(loads.values())],tip_load_N={str(n):[0.,0.,f] for n,f in loads.items()},
        theory_displacement_m=theory,component=2,
        assumptions=dict(length_m=1.,width_m=.1,depth_m=.1,young_Pa=E,poisson=0.,
                         traction='constant tip-face transverse traction; Q8 consistent integration',
                         analytical='Timoshenko cantilever; shear correction 5/6'))
    return '\n'.join(lines),definition


def axial_deck():
    """Independent linear T3D2 rod; transverse rigid translation restrained."""
    lines=['*HEADING','Independent Craft pilot axial control; SI m-kg-s-N-Pa',
        '*NODE','1,0,0,0','2,0.3,0,0','*ELEMENT,TYPE=T3D2,ELSET=ROD','1,1,2',
        '*NSET,NSET=ROOT','1','*NSET,NSET=TIP','2','*MATERIAL,NAME=ELASTIC',
        '*ELASTIC','70000000000,0.3','*SOLID SECTION,ELSET=ROD,MATERIAL=ELASTIC',
        '0.0001','*BOUNDARY','1,1,3','2,2,3','*STEP','*STATIC','*CLOAD','2,1,1000',
        '*NODE PRINT,NSET=TIP','U','*NODE PRINT,NSET=ROOT','RF','*END STEP','']
    return '\n'.join(lines),dict(case='axial',units='m-kg-s-N-Pa',element_kind='T3D2',
        node_count=2,element_count=1,node_xyz_m={'1':[0.,0.,0.],'2':[.3,0.,0.]},
        root_nodes=[1],tip_node=2,applied_N=[1000.,0.,0.],tip_load_N={'2':[1000.,0.,0.]},
        theory_displacement_m=1000*.3/(70e9*1e-4),component=0,
        assumptions=dict(length_m=.3,area_m2=1e-4,young_Pa=70e9,poisson=.3,analytical='F*L/(E*A)'))


def parse_dat(text,definition):
    """Read only declared TIP U and ROOT RF blocks; never sum applied-load RF."""
    if len(text.encode())>16*1024**2:
        raise ValueError('CalculiX DAT exceeds pilot parser budget')
    rows={'u':{},'rf':{}};active=None
    for line in text.splitlines():
        low=line.lower()
        if 'displacements' in low:
            active='u' if re.search(r'\bset\s+tip\b',low) else None
        elif 'forces' in low:
            active='rf' if re.search(r'\bset\s+root\b',low) else None
        elif active:
            fields=line.split()
            if len(fields)==4 and fields[0].isdigit():
                values=[float(v.replace('D','E').replace('d','e')) for v in fields[1:]]
                if any(not isfinite(v) for v in values):
                    raise ValueError('Nonfinite native displacement/reaction')
                node=int(fields[0])
                if node in rows[active]:
                    raise ValueError('Multiple result increments are outside this static control')
                rows[active][node]=values
    if set(rows['u'])!={definition['tip_node']} or set(rows['rf'])!=set(definition['root_nodes']):
        raise ValueError('Missing or unexpected declared tip/root native outputs')
    displacement=rows['u'][definition['tip_node']]
    reaction=[fsum(v[d] for v in rows['rf'].values()) for d in range(3)]
    moment=[]
    for d,a,b in ((0,1,2),(1,2,0),(2,0,1)):
        moment.append(fsum(definition['node_xyz_m'][str(n)][a]*f[b]-definition['node_xyz_m'][str(n)][b]*f[a] for n,f in rows['rf'].items()))
    theory=definition['theory_displacement_m']
    error=abs(displacement[definition['component']]-theory)/abs(theory)
    residual=max(abs(a+b) for a,b in zip(reaction,definition['applied_N']))/max(map(abs,definition['applied_N']))
    return dict(units=dict(length='m',force='N',pressure='Pa'),displacement_m=displacement,
        tip_xyz_m=definition['node_xyz_m'][str(definition['tip_node'])],reaction_N=reaction,
        reaction_moment_Nm=moment,applied_N=definition['applied_N'],
        theoretical_displacement_m=theory,relative_theory_error=error,
        force_equilibrium_relative_residual=residual,
        numerical_screen_passed=error<=SCREENS['theory_relative'] and residual<=SCREENS['force_relative'],**FLAGS)


def _limits(timeout_s,memory_mb):
    def apply():
        resource.setrlimit(resource.RLIMIT_AS,(memory_mb*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CPU,(timeout_s,)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,)*2)
    return apply


def _execute(folder,deck,definition,tools,timeout_s,memory_mb):
    folder.mkdir();(folder/'control.inp').write_text(deck)
    (folder/'definition.json').write_bytes(_encoded(definition))
    request=dict(deck_sha256=_digest(folder/'control.inp'),definition_sha256=_digest(folder/'definition.json'),
        timeout_s=timeout_s,memory_mb=memory_mb,threads=1,**FLAGS)
    (folder/'request.json').write_bytes(_encoded(request))
    argv=[tools['time'],'-v','-o',str(folder/'resources.log'),tools['bwrap'],
        '--die-with-parent','--unshare-net','--ro-bind','/','/','--dev','/dev',
        '--bind',str(folder),str(folder),'--chdir',str(folder),'--',tools['ccx'],'control']
    started=time.perf_counter();state='completed';error=None
    env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','CCX_NPROC_RESULTS':'1','CCX_NPROC_EQUATION_SOLVER':'1'}
    proc=subprocess.Popen(argv,cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        env=env,preexec_fn=_limits(timeout_s,memory_mb),start_new_session=True)
    try:
        stdout,stderr=proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid,signal.SIGKILL);stdout,stderr=proc.communicate();state='interrupted';error='wall timeout'
    (folder/'stdout.log').write_bytes(stdout);(folder/'stderr.log').write_bytes(stderr)
    process=dict(argv=argv,exit_code=proc.returncode,elapsed_seconds=time.perf_counter()-started,
                 state=state,resource_enforcement='bwrap read-only host, private writable run directory, no network; POSIX RLIMIT_AS/RLIMIT_CPU/RLIMIT_FSIZE; wall timeout kills process group')
    usage=(folder/'resources.log').read_text() if (folder/'resources.log').exists() else ''
    rss=re.search(r'Maximum resident set size \(kbytes\):\s*(\d+)',usage)
    process['peak_rss_KiB']=int(rss[1]) if rss else None
    result=dict(state=state,request=request,process=process,**FLAGS)
    if state=='completed':
        try:
            if proc.returncode or '*ERROR' in stdout.decode(errors='replace').upper():
                raise ValueError('Native CalculiX execution failed')
            result['comparison']=parse_dat((folder/'control.dat').read_text(),definition)
        except (OSError,ValueError) as exc:
            result['state']='failed';error=str(exc)
    if error:result['error']=error
    (folder/'result.json').write_bytes(_encoded(result))
    result['files_sha256']={p.name:_digest(p) for p in sorted(folder.iterdir()) if p.is_file()}
    return result


def run(output_dir,timeout_s=120,memory_mb=2048):
    """Run exactly three bounded native solves; retain all failed execution files."""
    if type(timeout_s) is not int or not 1<=timeout_s<=120 or type(memory_mb) is not int or not 128<=memory_mb<=2048:
        raise ValueError('Pilot resources require 1..120s and 128..2048MiB per solve')
    folder=Path(output_dir).absolute()
    if folder.exists() or folder.is_symlink():
        raise ValueError('Fresh CalculiX reference directory required')
    folder.mkdir(parents=True)
    tools={name:shutil.which(name) for name in ('ccx','bwrap','time')}
    record=dict(schema='osr-craft-calculix-reference/1',scope='Independent SI linear controls only; no railway assembly or physical qualification',
        state='held' if not all(tools.values()) else 'completed',sources_sha256={SOURCE:_digest(__file__)},
        tool_paths={k:str(Path(v).resolve()) for k,v in tools.items() if v},
        tool_sha256={k:_digest(Path(v).resolve()) for k,v in tools.items() if v},
        python=platform.python_version(),screens=SCREENS,cases={},**FLAGS)
    if not all(tools.values()):
        record['hold_reason']='Missing native executable(s): '+','.join(k for k,v in tools.items() if not v)
    else:
        for name,recipe in [('cantilever-coarse',lambda:cantilever_deck((8,2,2))),
                            ('cantilever-fine',lambda:cantilever_deck((16,4,4))),('axial',axial_deck)]:
            deck,definition=recipe()
            try:
                record['cases'][name]=_execute(folder/name,deck,definition,tools,timeout_s,memory_mb)
            except OSError as exc:
                failure=dict(state='failed',error=str(exc),**FLAGS)
                (folder/name/'failure.json').write_bytes(_encoded(failure));record['cases'][name]=failure
        if any(c['state']!='completed' for c in record['cases'].values()):
            record['state']='failed'
        else:
            a,b=[record['cases'][n]['comparison']['displacement_m'][2] for n in ('cantilever-coarse','cantilever-fine')]
            change=abs(b-a)/abs(b) if b else None
            record['refinement']=dict(relative_tip_change=change,tolerance=SCREENS['refinement_relative'],
                screen_passed=change is not None and change<=SCREENS['refinement_relative'],mesh_independence_established=False)
            record['numerical_screens_passed']=all(c['comparison']['numerical_screen_passed'] for c in record['cases'].values()) and record['refinement']['screen_passed']
    record['evaluation_id']=sha256(_encoded(record)).hexdigest()
    (folder/'result.json').write_bytes(_encoded(record))
    return record
