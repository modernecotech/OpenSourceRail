"""Independent strip verification of the rectangular plate formulation."""
from pathlib import Path
import hashlib,json,math,shutil,subprocess
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from .plate import stiffness


def strip(*,count=40,thickness=.02,young=210e9,poisson=.3,width=.2,length=1,pressure=2000):
    D=young*thickness**3/(12*(1-poisson**2))*np.array([[1,poisson,0],[poisson,1,0],[0,0,(1-poisson)/2]])
    S=np.ones(2)*(5/6)*young/(2*(1+poisson))*thickness
    # Cylindrical bending: both x-side nodes share w/theta_y; theta_x=0.
    n=2*(count+1);K=np.zeros((n,n));F=np.zeros(n)
    for j in range(count):
        k,f=stiffness(width,length/count,lambda x,y:(D,S));T=np.zeros((12,4))
        for i in range(4):
            row=0 if i in (0,1)else 2;T[3*i,row]=1;T[3*i+2,row+1]=1
        ids=[2*j,2*j+1,2*j+2,2*j+3];K[np.ix_(ids,ids)]+=T.T@k@T;F[ids]+=pressure*(T.T@f)
    free=list(set(range(n))-{0,2*count});u=np.zeros(n);u[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
    analytical=5*pressure*length**4/(384*D[1,1])+pressure*length**2/(8*S[1])
    return dict(maximum_deflection_m=float(max(u[::2])),analytical_deflection_m=float(analytical),analytical_relative_error=float(abs(max(u[::2])/analytical-1)),count=count)


def native(folder,*,count=40):
    """Actual independent CalculiX S8R homogeneous plate, cylindrical bending.

    Verifies the numerical element only; not a composite/joint calibration.
    """
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);width=.2;length=1.;thickness=.02;young=210e9;poisson=.3;pressure=2000
    nx=2;ny=count;coords={};elements=[];load={};tag=0
    # Native S8R nodes lie on a half-step lattice, omitting element centres.
    def node(i,j):
        nonlocal tag
        key=(i,j)
        if key not in coords:tag+=1;coords[key]=tag
        return coords[key]
    for j in range(ny):
        for i in range(nx):
            pairs=[(2*i,2*j),(2*i+2,2*j),(2*i+2,2*j+2),(2*i,2*j+2),(2*i+1,2*j),(2*i+2,2*j+1),(2*i+1,2*j+2),(2*i,2*j+1)]
            ids=[node(*p)for p in pairs];elements.append(ids);area=width/nx*length/ny
            for k,identity in enumerate(ids):load[identity]=load.get(identity,0)+pressure*area*(-1/12 if k<4 else 1/3)
    rows=['*HEADING','Homogeneous cylindrical plate research verification, SI units','*NODE']
    rows +=[f'{identity},{width*i/(2*nx):.12g},{length*j/(2*ny):.12g},0'for (i,j),identity in coords.items()]
    rows +=['*ELEMENT,TYPE=S8R,ELSET=BODY']+[f'{i+1},'+','.join(map(str,c))for i,c in enumerate(elements)]
    rows +=['*NSET,NSET=ALLN']+[','.join(map(str,list(coords.values())[i:i+12]))for i in range(0,len(coords),12)]
    rows +=['*MATERIAL,NAME=STEEL','*ELASTIC',f'{young},{poisson}','*SHELL SECTION,ELSET=BODY,MATERIAL=STEEL',str(thickness),'*BOUNDARY','ALLN,5,5']
    rows +=[f'{identity},3,3'for (i,j),identity in coords.items()if j in (0,2*ny)]
    rows +=[f'{coords[(0,0)]},1,2',f'{coords[(2*nx,0)]},2,2','*STEP','*STATIC','*CLOAD']+[f'{i},3,{f:.12g}'for i,f in load.items()]
    rows +=['*NODE PRINT,NSET=ALLN','U','*END STEP']
    deck=folder/'plate.inp';deck.write_text('\n'.join(rows)+'\n');binary=shutil.which('ccx')
    if not binary:raise RuntimeError('CalculiX required for independent plate verification')
    result=subprocess.run([binary,'-i','plate'],cwd=folder,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120);(folder/'plate.log').write_text(result.stdout)
    if result.returncode or '*ERROR' in result.stdout.upper():raise RuntimeError('native plate verification failed')
    displacements=[]
    for line in (folder/'plate.dat').read_text().splitlines():
        values=line.split()
        if len(values)==4 and values[0].isdigit():displacements.append(abs(float(values[3])))
    if not displacements:raise ValueError('native plate displacement output missing')
    theoretical=strip(count=count);actual=max(displacements);error=abs(actual/theoretical['maximum_deflection_m']-1)
    report=dict(schema='osr-native-plate-formulation-check/1',native_deflection_m=actual,plate=theoretical,native_relative_difference=error,
        numerical_screen_passed=error<.02 and theoretical['analytical_relative_error']<.002,
        physical_validation=False,scope='homogeneous cylindrical plate only; composite properties and clip/contact law unvalidated',
        evidence_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (deck,folder/'plate.dat',folder/'plate.log')})
    (folder/'verification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');return report
