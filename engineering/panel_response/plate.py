"""Rectangular MITC4 plate with discrete attachment springs and real rail sections.

SI units. Covariant edge shear tying removes transverse-shear locking. Faces
and lands contribute ABD from their manufactured thickness/angle coordinates;
core shear uses the coupled grade. Bond/finish in-plane stiffness is uncredited.
"""
from __future__ import annotations
import math
import warnings
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu,MatrixRankWarning
from osr_mech.engineering_definition import fingerprint
from osr_mech.rolling_stock.composite_panels import transformed_q
from engineering.design_consistency.contracts import validate,summary


def shape(xi,eta,hx,hy):
    signs=np.array([[-1,-1],[1,-1],[1,1],[-1,1]])
    n=(1+signs[:,0]*xi)*(1+signs[:,1]*eta)/4
    dx=signs[:,0]*(1+signs[:,1]*eta)/(2*hx)
    dy=signs[:,1]*(1+signs[:,0]*xi)/(2*hy)
    return n,dx,dy


def strain(xi,eta,hx,hy):
    n,dx,dy=shape(xi,eta,hx,hy);bend=np.zeros((3,12));shear=np.zeros((2,12))
    for i in range(4):
        bend[0,3*i+1]=dx[i];bend[1,3*i+2]=dy[i]
        bend[2,3*i+1]=dy[i];bend[2,3*i+2]=dx[i]
        shear[0,3*i]=dx[i];shear[0,3*i+1]=-n[i]
        shear[1,3*i]=dy[i];shear[1,3*i+2]=-n[i]
    return bend,shear


def stiffness(hx,hy,material):
    if min(hx,hy)<=0:raise ValueError('positive rectangular element required')
    k=np.zeros((12,12));force=np.zeros(12);q=1/math.sqrt(3)
    for xi in (-q,q):
        for eta in (-q,q):
            x=(xi+1)*hx/2;y=(eta+1)*hy/2;D,S=material(x,y)
            if np.linalg.eigvalsh(D).min()<=0 or min(S)<=0:raise ValueError('positive plate bending/shear stiffness required')
            bend,_=strain(xi,eta,hx,hy)
            shear=np.vstack([((1-eta)*strain(0,-1,hx,hy)[1][0]+(1+eta)*strain(0,1,hx,hy)[1][0])/2,
                ((1-xi)*strain(-1,0,hx,hy)[1][1]+(1+xi)*strain(1,0,hx,hy)[1][1])/2])
            weight=hx*hy/4;k+=(bend.T@D@bend+shear.T@np.diag(S)@shear)*weight
            force[::3]+=shape(xi,eta,hx,hy)[0]*weight
    return k,force


def primitive_contains(p,x,y):
    cx,cy,_=p['centre_m'];kind=p['kind']
    if kind in ('box','plate','perforated-plate'):
        a,b,_=p['dimensions_m']
        if not abs(x-cx)<a/2+1e-12 or not abs(y-cy)<b/2+1e-12:return False
        return kind=='box'or all(math.hypot(x-cx-hx,y-cy-hy)>p['hole_radius_m']for hx,hy in p['holes_xy_m'])
    if kind=='tube':return p['inner_radius_m']<math.hypot(x-cx,y-cy)<p['radius_m']
    return False


def regions(contract):
    validate(contract)
    if contract['panel_parameters']['crown_m']:raise ValueError('curved geometry needs a shell adapter; flat-plate credit prohibited')
    foam=[q for part in contract['parts']if part['material']=='foam'for q in part['manufacturing']['primitives']]
    for part in contract['parts']:
        if not part['id'].startswith('potting-'):continue
        insert=part['manufacturing']['primitives'][0];x,y,_=insert['centre_m'];r=insert['radius_m']
        cut=any(q['kind']=='perforated-plate'and q['hole_radius_m']==r and any(math.dist([q['centre_m'][0]+a,q['centre_m'][1]+b],[x,y])<1e-10 for a,b in q['holes_xy_m'])for q in foam)
        if not cut:raise ValueError('potted insert lacks a matching foam subtraction: '+part['id'])
    rows=[]
    for part in contract['parts']:
        if part['placement']['translation_m']!=[0,0,0]or part['placement']['rotation']!=np.eye(3).tolist():raise ValueError('flat plate adapter requires contract coordinates without extra placement')
        if part['id'].startswith(('support-','aperture-')):continue
        for p in part['manufacturing']['primitives']:
            if p['kind']=='tube':depth=p['length_m']
            else:depth=p['dimensions_m'][2]
            lower=p['centre_m'][2]-depth/2;upper=lower+depth
            q=None;mat=contract['materials'][part['material']]
            if 'laminate_ply'in part:q=np.asarray(transformed_q(mat,part['laminate_ply']['angle_deg']))
            elif part['material'] in ('gfrp','steel','potting'):
                E=mat['young_pa'];v=mat['poisson'];q=E/(1-v*v)*np.array([[1,v,0],[v,1,0],[0,0,(1-v)/2]])
            rows.append(dict(part=part,p=p,lower=lower,upper=upper,q=q))
    return rows


def constitutive(contract,rows,x,y):
    A=np.zeros((3,3));B=np.zeros((3,3));D=np.zeros((3,3));core_shear=None
    for row in rows:
        if not primitive_contains(row['p'],x,y):continue
        lo,hi=row['lower'],row['upper'];q=row['q'];part=row['part'];mat=contract['materials'][part['material']]
        if q is not None:A+=q*(hi-lo);B+=q*(hi*hi-lo*lo)/2;D+=q*(hi**3-lo**3)/3
        if part['id'].startswith(('core-','solid-land-','potting-','insert-')):
            G=mat.get('shear_pa',mat.get('young_pa',0)/(2*(1+mat.get('poisson',.3))))
            core_shear=G*(hi-lo)
    if np.linalg.eigvalsh(A).min()<=0:raise ValueError('uncovered laminate footprint')
    D=D-B.T@np.linalg.solve(A,B)
    if core_shear is None:core_shear=contract['materials']['gfrp']['g12_pa']*contract['panel_parameters']['skin_m']
    return D,np.array([core_shear,core_shear])


def grid(contract,mesh_size):
    if not math.isfinite(mesh_size)or mesh_size<=0:raise ValueError('positive finite mesh size required')
    c=contract['panel_parameters'];width=c['width_m'];height=c['height_m'];x={0,width};y={0,height}
    for a,b,d,e in c['holes']:x.update([a,d]);y.update([b,e])
    for a,b in contract['support_network']['panel_attachment_sites_m']:x.add(a);y.add(b)
    for part in contract['parts']:
        if part['id'].startswith(('core-','solid-land-')):
            p=part['manufacturing']['primitives'][0];cx,cy,_=p['centre_m'];dx,dy,_=p['dimensions_m'];x.update([cx-dx/2,cx+dx/2]);y.update([cy-dy/2,cy+dy/2])
    def subdivide(values):
        edges=sorted(set(round(v,12)for v in values));result=[]
        for a,b in zip(edges,edges[1:]):result.extend(np.linspace(a,b,max(1,math.ceil((b-a)/mesh_size))+1)[:-1])
        return np.array(result+[edges[-1]])
    xs=subdivide(x);ys=subdivide(y);nodes=[];index={};elements=[]
    for j in range(len(ys)-1):
        for i in range(len(xs)-1):
            cx=(xs[i]+xs[i+1])/2;cy=(ys[j]+ys[j+1])/2
            if any(a<cx<d and b<cy<e for a,b,d,e in c['holes']):continue
            cell=[]
            for pair in ((i,j),(i+1,j),(i+1,j+1),(i,j+1)):
                if pair not in index:index[pair]=len(nodes);nodes.append([xs[pair[0]],ys[pair[1]]])
                cell.append(index[pair])
            elements.append(cell)
    return np.array(nodes),elements


def solve(contract,*,mesh_size=.08,pressure_pa=2000,failed_clip=None,clip_stiffness_factor=1,_system=False):
    if not math.isfinite(pressure_pa)or pressure_pa<=0 or not 0<clip_stiffness_factor<=1:raise ValueError('invalid pressure/compliance sensitivity')
    rows=regions(contract);nodes,elements=grid(contract,mesh_size);ndof=3*len(nodes);triplets=[];F=np.zeros(ndof);attachments=[];rails=[];fixed=set();total_area=0.
    def add(ids,k):
        for i,a in enumerate(ids):
            for j,b in enumerate(ids):
                if k[i,j]:triplets.append((a,b,float(k[i,j])))
    for cell in elements:
        xy=nodes[cell];hx=xy[1,0]-xy[0,0];hy=xy[3,1]-xy[0,1];x0,y0=xy[0]
        k,f=stiffness(hx,hy,lambda x,y:constitutive(contract,rows,x+x0,y+y0))
        ids=[3*i+d for i in cell for d in range(3)];add(ids,k);F[ids]+=pressure_pa*f;total_area+=hx*hy
    # Two independent clip/insert springs connect each physical rail to its plate.
    # Simply supported bracket ends and series bolt/potting compliance are seeds.
    E=contract['materials']['fastener']['young_pa'];prm=contract['panel_parameters']
    bolt=next(p for p in contract['parts']if '-clip-bolt-'in p['id'])['manufacturing']['primitives'][0]
    potting=next(p for p in contract['parts']if p['id'].startswith('potting-'))['manufacturing']['primitives'][0]
    kbolt=E*math.pi*bolt['radius_m']**2/bolt['length_m']
    kpot=contract['materials']['potting']['young_pa']*math.pi*(potting['radius_m']**2-potting['inner_radius_m']**2)/potting['length_m']
    kclip=clip_stiffness_factor/(1/kbolt+1/kpot)
    for rail in contract['support_network']['rails']:
        a,b=rail['interval_m'];station=rail['station_m'];xpoints=[a,a+.2*(b-a),a+.8*(b-a),b];dofs=[]
        for point in xpoints:dofs.append((len(F),len(F)+1));F=np.r_[F,0.,0.]
        fixed.update([dofs[0][0],dofs[-1][0]])
        EI=contract['materials']['steel']['young_pa']*contract['support_network']['section']['iy_m4']
        for i in range(3):
            l=xpoints[i+1]-xpoints[i];k=EI/l**3*np.array([[12,6*l,-12,6*l],[6*l,4*l*l,-6*l,2*l*l],[-12,-6*l,12,-6*l],[6*l,2*l*l,-6*l,4*l*l]])
            add([*dofs[i],*dofs[i+1]],k)
        for slot in (1,2):
            point=np.array([xpoints[slot],station]);node=int(np.argmin(np.linalg.norm(nodes-point,axis=1)))
            if np.linalg.norm(nodes[node]-point)>1e-10:raise ValueError('attachment does not map exactly to plate mesh')
            identity=f'{rail["id"]}-clip-{slot-1}';active=identity!=failed_clip
            if active:add([3*node,dofs[slot][0]],kclip*np.array([[1,-1],[-1,1]]))
            attachments.append(dict(id=identity,physical_rail_id=rail['id'],plate_node=node,rail_dof=dofs[slot][0],active=active,stiffness_n_m=kclip))
        rails.append(dict(physical_part_id=rail['id'],bracket_dofs=[dofs[0][0],dofs[-1][0]],EI_nm2=EI,length_m=b-a))
    if failed_clip and failed_clip not in {r['id']for r in attachments}:raise ValueError('unknown failed physical clip')
    r,c,v=zip(*triplets);K=coo_matrix((v,(r,c)),shape=(len(F),len(F))).tocsr();free=np.array(sorted(set(range(len(F)))-fixed));u=np.zeros(len(F))
    with warnings.catch_warnings():
        warnings.simplefilter('error',MatrixRankWarning);lu=splu(K[free][:,free].tocsc());u[free]=lu.solve(F[free])
    if not np.isfinite(u).all():raise ValueError('singular/nonfinite plate response')
    residual=K@u-F;relative=float(np.linalg.norm(residual[free])/np.linalg.norm(F));reaction=sum(residual[i]for i in fixed)
    balance=abs(reaction+pressure_pa*total_area)/(pressure_pa*total_area)
    if relative>1e-6 or balance>1e-6:raise ValueError('plate/rail force equilibrium failed')
    for rail in rails:rail['bracket_reaction_n']=[float(residual[d])for d in rail['bracket_dofs']]
    for a in attachments:a['force_n']=float(kclip*(u[3*a['plate_node']]-u[a['rail_dof']]))if a['active']else 0.
    values=u[:ndof].reshape(-1,3);maximum=float(np.max(np.abs(values[:,0])))
    result=dict(schema='osr-clipped-panel-plate-response/1',contract_sha256=fingerprint(contract),mesh_size_m=mesh_size,
        nodes_m=nodes.tolist(),elements=elements,displacement_m=values[:,0].tolist(),node_count=len(nodes),element_count=len(elements),
        loaded_area_m2=total_area,pressure_pa=pressure_pa,applied_force_n=pressure_pa*total_area,
        attachments=attachments,rails=rails,maximum_deflection_m=maximum,maximum_clip_force_n=max(abs(a['force_n'])for a in attachments),
        failed_clip=failed_clip,force_balance_relative_error=balance,free_residual_relative_error=relative,
        plate_strain_energy_j=float(.5*u@(K@u)),external_work_j=float(u@F),
        deflection_screen='passed'if maximum<=.005 else'failed',physical_validation=False,production_released=False,
        installed_defined_mass_kg=summary(contract)['mass_kg'],
        assumptions=['MITC4 flat plate; no curved-shell stiffness credit','pointwise membrane-free ABD condensation',
            'bond/finish extensional stiffness uncredited','core shear from nominal room-temperature grade',
            'bilateral point clip/insert springs; no contact/peel/pull-out strength','simply supported rail ends; aperture frame anchorage assumed'],
        unknown_checks=['hot/wet constitutive calibration','clip contact/pull-out/fatigue/retention','aperture edge stress and bonds','bracket/frame weld capacity','complete-stack fire','physical correlation'])

    if _system:return result,dict(K=K,F=F,u=u,free=free,ndof=ndof,lu=lu)
    return result


def single_clip_envelope(contract,*,mesh_size=.04,pressure_pa=2000):
    """Every individual clip loss using exact rank-one linear spring removal.

    No pressure redistribution assumption: solve the coupled plate/rail system.
    A near-singular removal is recorded as instability rather than a finite pass.
    """
    baseline,system=solve(contract,mesh_size=mesh_size,pressure_pa=pressure_pa,_system=True)
    free=system['free'];lookup={d:i for i,d in enumerate(free)};rows=[]
    for attachment in baseline['attachments']:
        b=np.zeros(len(free));b[lookup[3*attachment['plate_node']]]=1;b[lookup[attachment['rail_dof']]]=-1
        v=system['lu'].solve(b);k=attachment['stiffness_n_m'];denominator=1-k*float(b@v)
        if denominator<=1e-10:
            rows.append(dict(failed_clip=attachment['id'],status='unstable',maximum_deflection_m=None,deflection_screen='failed'));continue
        u=system['u'].copy();u[free]+=k*v*float(b@u[free])/denominator
        residual=system['K']@u-system['F'];residual[free]-=k*b*float(b@u[free])
        relative=float(np.linalg.norm(residual[free])/np.linalg.norm(system['F']))
        maximum=float(max(abs(u[:system['ndof']:3])))
        if relative>1e-6:raise ValueError('rank-one clip-loss solution failed equilibrium')
        forces=[0. if a['id']==attachment['id']else a['stiffness_n_m']*(u[3*a['plate_node']]-u[a['rail_dof']])for a in baseline['attachments']]
        rows.append(dict(failed_clip=attachment['id'],status='solved',maximum_deflection_m=maximum,
            maximum_remaining_clip_force_n=float(max(abs(f)for f in forces)),free_residual_relative_error=relative,
            deflection_screen='passed'if maximum<=.005 else'failed'))
    worst=max(rows,key=lambda r:float('inf')if r['status']=='unstable'else r['maximum_deflection_m'])
    return dict(schema='osr-single-clip-loss-envelope/1',contract_sha256=fingerprint(contract),pressure_pa=pressure_pa,mesh_size_m=mesh_size,
        method='exact rank-one update of the factored linear coupled system',case_count=len(rows),cases=rows,worst=worst,
        physical_validation=False,production_released=False,clip_strength_qualified=False)
