"""Sparse 3D Timoshenko deck/rail/cap/pier/foundation assembly and modal ports."""
from __future__ import annotations
import math
import numpy as np
from scipy.sparse import coo_matrix,csc_matrix
from scipy.sparse.linalg import eigsh,splu
from osr_mech.civil.exploration import geometry,rectangle,section_properties
from .model import deck_physics,pier_physics,cement_area
from .section_mechanics import matrix as section_matrix
from .train_bridge import beam_matrices,hermite


def skew(v):
    x,y,z=v
    return np.asarray([[0.,-z,y],[z,0.,-x],[-y,x,0.]])


def rotation_frame(first,second):
    ex=np.asarray(second)-first;length=np.linalg.norm(ex)
    if length<=1e-8:raise ValueError('3D beam has coincident ends')
    ex=ex/length;reference=np.array([0.,0.,1.]) if abs(ex[2])<.9 else np.array([1.,0.,0.])
    ey=np.cross(reference,ex);ey/=np.linalg.norm(ey);ez=np.cross(ex,ey)
    return np.asarray([ex,ey,ez]),float(length)


def element_matrices(first,second,properties):
    R,L=rotation_frame(np.asarray(first),np.asarray(second));K=np.zeros((12,12));M=np.zeros_like(K)
    EA,EIy,EIz,GJ,GAy,GAz,mass,polar=(properties[k] for k in ('EA_n','EIy_nm2','EIz_nm2','GJ_nm2','GAy_n','GAz_n','mass_kg_m','polar_mass_kg_m'))
    if min(EA,EIy,EIz,GJ,GAy,GAz,mass,polar)<=0:raise ValueError('positive 3D section stiffness and mass required')
    for indices,stiffness,line_mass in [([0,6],EA/L,mass),([3,9],GJ/L,polar)]:
        K[np.ix_(indices,indices)]+=stiffness*np.asarray([[1.,-1.],[-1.,1.]])
        M[np.ix_(indices,indices)]+=line_mass*L/6*np.asarray([[2.,1.],[1.,2.]])
    for indices,EI,GA,sign in [([1,5,7,11],EIz,GAy,np.ones(4)),([2,4,8,10],EIy,GAz,np.array([1.,-1.,1.,-1.]))]:
        phi=12*EI/(GA*L*L)
        local=EI/(L**3*(1+phi))*np.array([[12,6*L,-12,6*L],[6*L,(4+phi)*L*L,-6*L,(2-phi)*L*L],[-12,-6*L,12,-6*L],[6*L,(2-phi)*L*L,-6*L,(4+phi)*L*L]])
        m,_=beam_matrices(L,EI,mass);D=np.diag(sign)
        K[np.ix_(indices,indices)]+=D@local@D;M[np.ix_(indices,indices)]+=D@m@D
    T=np.zeros((12,12))
    for i in range(4):T[3*i:3*i+3,3*i:3*i+3]=R
    return T.T@M@T,T.T@K@T,R,L


class Route:
    """Exact circular horizontal alignment and linear cant/vertical grade ramps."""
    def __init__(self,record):
        required={'radius_m','cant_rad','cant_start_m','cant_end_m','grade_rad','basis'}
        if set(record)-{'vertical_radius_m'}!=required or not record['basis']:raise ValueError('spatial route fields/basis missing')
        for k,v in record.items():
            if k!='basis' and (type(v) not in (int,float) or not math.isfinite(v)):raise ValueError('finite route geometry required')
        if record['radius_m']!=0 and abs(record['radius_m'])<100:raise ValueError('reduced spatial adapter requires radius >=100 m')
        if record.get('vertical_radius_m',0.)!=0 and abs(record['vertical_radius_m'])<1000:raise ValueError('vertical curve radius must be >=1000 m')
        if abs(record['cant_rad'])>.2 or abs(record['grade_rad'])>.1 or record['cant_end_m']<=record['cant_start_m']:
            raise ValueError('route outside spatial adapter angular range')
        self.record=record

    def frame(self,s):
        r=self.record;angle=s/r['radius_m'] if r['radius_m'] else 0.;grade=r['grade_rad']+(s/r['vertical_radius_m'] if r.get('vertical_radius_m') else 0.)
        if abs(grade)>.1:raise ValueError('vertical alignment outside grade domain')
        cant=r['cant_rad']*np.clip((s-r['cant_start_m'])/(r['cant_end_m']-r['cant_start_m']),0.,1.)
        tangent=np.array([math.cos(angle)*math.cos(grade),math.sin(angle)*math.cos(grade),math.sin(grade)])
        lateral=np.array([-math.sin(angle),math.cos(angle),0.]);normal=np.cross(tangent,lateral)
        y=math.cos(cant)*lateral+math.sin(cant)*normal;z=np.cross(tangent,y)
        return np.column_stack([tangent,y,z])

    def position(self,s,y=0.,z=0.):
        r=self.record;h=1/r['radius_m'] if r['radius_m'] else 0.;v=1/r['vertical_radius_m'] if r.get('vertical_radius_m') else 0.;g=r['grade_rad']
        def ci(f,p):return (math.sin(f*s+p)-math.sin(p))/f if f else s*math.cos(p)
        def si(f,p):return (math.cos(p)-math.cos(f*s+p))/f if f else s*math.sin(p)
        centre=np.array([.5*(ci(h-v,-g)+ci(h+v,g)),.5*(si(h+v,g)+si(h-v,-g)),si(v,g)])
        return centre+self.frame(s)@np.array([0.,y,z])


class SpatialStructure:
    def __init__(self,bridge,route,*,deck_mesh=4,rail_step=1.,modes=24):
        if type(deck_mesh) is not int or not 2<=deck_mesh<=24 or not .25<=rail_step<=2. or type(modes) is not int or not 6<=modes<=128:
            raise ValueError('spatial discretisation outside registered budget')
        self.route=route;self.candidate=bridge['candidate'];self.study=bridge['study'];self.geo=geometry(self.candidate['definition'])
        span=self.candidate['definition']['deck']['span_m'];count=bridge['span_count'];self.length=span*count
        scheme=self.study.get('connection_scheme','simple-span')
        if scheme not in ('simple-span','continuous','link-slab'):raise ValueError('unknown spatial span connection scheme')
        if not 1<=count<=8:raise ValueError('bounded spatial span count required')
        self.approach=5.;self.gauge=1.435;self.tracks=list(self.geo['track_centres_m'])
        if len(self.tracks)!=2:raise ValueError('spatial common structure requires two track centres')
        self.coordinates=[];self.elements=[];self.rails={};self.decks={};self.springs=[];self.fixed=[]
        self._kr=[];self._kc=[];self._kv=[];self._mr=[];self._mc=[];self._mv=[]
        material=self.candidate['material'];records={'concrete':material,**self.candidate.get('material_records',{})}
        allowance=self.candidate['mass_allowances'];self.dead_forces={}
        def node(point):
            identifier=len(self.coordinates);self.coordinates.append(np.asarray(point));return identifier
        self._node=node
        def section(section,materials,mass_extra=0.,closed=False):
            p=section_matrix(section,materials,closed);rho_mass=0.;polar=0.;GAy=GAz=0.
            for region,role in zip(section['regions'],section.get('material_roles',['concrete']*len(section['regions']))):
                m=materials[role];area=region['width_m']*region['height_m'];E=m['youngs_modulus_pa']*m.get('stiffness_factor',1.)
                G=E/(2*(1+m['poisson_ratio']));rho_mass+=area*m['density_kg_m3']
                polar+=area*m['density_kg_m3']*((region['width_m']**2+region['height_m']**2)/12+(region['y_m']-p['centroid_y_m'])**2+(region['z_m']-p['centroid_z_m'])**2)
                GAy+=5/6*area*(m.get('orthotropic',{}).get('gxy_pa',G));GAz+=area*(m.get('orthotropic',{}).get('gxz_pa',G))*section['shear_area_m2']/section['area_m2']
            return {**p,'GAy_n':GAy,'GAz_n':GAz,'mass_kg_m':rho_mass+mass_extra,'polar_mass_kg_m':polar*(1+mass_extra/rho_mass)}
        self._section=section
        def beam(a,b,p,kind,station_start=None,station_end=None,track=None):
            M,K,R,L=element_matrices(self.coordinates[a],self.coordinates[b],p)
            dofs=list(range(6*a,6*a+6))+list(range(6*b,6*b+6));self._block(dofs,K,self._kr,self._kc,self._kv);self._block(dofs,M,self._mr,self._mc,self._mv)
            self.elements.append(dict(nodes=[a,b],dofs=dofs,properties=p,kind=kind,R=R,length=L,
                station_start=station_start,station_end=station_end,track=track,K=K))
            for n in (a,b):self.dead_forces[6*n+2]=self.dead_forces.get(6*n+2,0.)-p['mass_kg_m']*L*9.81/2
            return self.elements[-1]
        self._beam=beam
        local=sorted({round(float(x),10) for x in np.linspace(0,span,deck_mesh+1)}|{s['start_m'] for s in self.geo['deck']}|{s['end_m'] for s in self.geo['deck']})
        deck_centroid=self.geo['deck'][1]['centroid_z_m']-self.geo['deck'][1]['top_m']-.2
        self.deck_centroid=deck_centroid;self.deck_ends={}
        for track,y in enumerate(self.tracks):
            self.decks[track]=[];self.deck_ends[track]=[]
            for index in range(count):
                nodes=[self.deck_ends[track][-1][1]] if scheme=='continuous' and index else [node(route.position(index*span+local[0],y,deck_centroid))]
                nodes += [node(route.position(index*span+x,y,deck_centroid)) for x in local[1:]]
                self.deck_ends[track].append((nodes[0],nodes[-1]))
                for j,(a,b) in enumerate(zip(nodes,nodes[1:])):
                    middle=(local[j]+local[j+1])/2;s=next(s for s in self.geo['deck'] if s['start_m']<=middle<s['end_m'])
                    extra=cement_area(s)*allowance['reinforcement_kg_m3']+allowance['prestress_kg_m']+allowance['superimposed_dead_kg_m_per_track']
                    if s is not self.geo['deck'][1]:extra+=allowance['embedded_kg_per_beam']/(2*self.geo['deck'][0]['end_m'])
                    closed=self.candidate['definition']['deck']['family'] in ('hollow-box','segmental-box','hybrid-shell')
                    e=beam(a,b,section(s,records,extra,closed),'deck',index*span+local[j],index*span+local[j+1],track)
                    self.decks[track].append(e)
            if scheme=='link-slab':
                record=bridge.get('span_connection')
                if not record or not record.get('basis'):raise ValueError('link slab requires an explicit equivalent connector and basis')
                Klink=np.asarray(record['stiffness_si'],dtype=float)
                if Klink.shape!=(6,6) or not np.isfinite(Klink).all() or not np.allclose(Klink,Klink.T) or np.linalg.eigvalsh(Klink).min()<0:
                    raise ValueError('link slab needs a passive symmetric six-direction law')
                for index in range(1,count):
                    self._spring([self.deck_ends[track][index-1][1],self.deck_ends[track][index][0]],
                                 [np.eye(6),-np.eye(6)],Klink,'span-connection')
        self.support_nodes=[]
        support=self.candidate.get('support_material',material);support_records={**records,'concrete':support}
        cap_regions=[rectangle(self.geo['cap_concrete_m3']/self.geo['cap_width_m']/self.geo['cap_height_m'],self.geo['cap_height_m'])]
        cap_section={**section_properties(cap_regions),'regions':cap_regions}
        cap_section['shear_area_m2']=5*cap_section['area_m2']/6
        cap_p=section(cap_section,support_records)
        ground=self.study['ground_scenarios'][0];bearing=self.study['bearing']
        for index in range(count+1):
            s=index*span;top=node(route.position(s,0.,deck_centroid));base=node(route.position(s,0.,deck_centroid-self.candidate['definition']['pier']['height_m']))
            self.support_nodes.append(base)
            # Actual tapered pier regions retain their own element stiffness/mass.
            heights=sorted({0.,self.candidate['definition']['pier']['height_m'],*(x['start_m'] for x in self.geo['pier']),*(x['end_m'] for x in self.geo['pier'])})
            pier_nodes=[base]+[node(route.position(s,0.,deck_centroid-self.candidate['definition']['pier']['height_m']+h)) for h in heights[1:-1]]+[top]
            for j,(a,b) in enumerate(zip(pier_nodes,pier_nodes[1:])):
                h=(heights[j]+heights[j+1])/2;sec=next(r for r in self.geo['pier'] if r['start_m']<=h<r['end_m'])
                beam(a,b,section(sec,support_records),'pier')
            foundation=self.candidate['foundation'];fm=self.candidate.get('foundation_material',support)
            cap_mass=foundation['cap_depth_m']*foundation['cap_length_m']*foundation['cap_width_m']*fm['density_kg_m3']
            self._block(list(range(6*base,6*base+6)),np.diag([cap_mass]*3+[cap_mass*(foundation['cap_length_m']**2+foundation['cap_width_m']**2)/12]*3),self._mr,self._mc,self._mv)
            self.dead_forces[6*base+2]-=cap_mass*9.81
            foundation_K=np.asarray(bridge.get('foundation_stiffness_si',np.diag([ground['lateral_stiffness_n_m']]*2+[ground['axial_stiffness_n_m']]+[ground['rotational_stiffness_nm_rad']]*3)),dtype=float)
            if foundation_K.shape!=(6,6) or not np.isfinite(foundation_K).all() or not np.allclose(foundation_K,foundation_K.T) or np.linalg.eigvalsh(foundation_K).min()<=0:
                raise ValueError('foundation requires a positive symmetric six-direction matrix')
            self._spring([base],[np.eye(6)],foundation_K,'foundation')
            for track,y in enumerate(self.tracks):
                seat=node(route.position(s,y,deck_centroid));beam(top,seat,cap_p,'cap')
                ends=([self.deck_ends[track][index-1][1]] if index else [])+([self.deck_ends[track][index][0]] if index<count else [])
                k=np.diag([bearing['horizontal_stiffness_n_m']]*2+[bearing['vertical_stiffness_n_m']]+[bearing.get('rotational_stiffness_nm_rad',1e6)]*3)
                for end in dict.fromkeys(ends):self._spring([end,seat],[np.eye(6),-np.eye(6)],k,'bearing')
        rail_x=np.linspace(-self.approach,self.length+self.approach,math.ceil((self.length+2*self.approach)/rail_step)+1)
        rail_p=dict(EA_n=210e9*.0153,EIy_nm2=bridge['track']['EI_nm2']/2,EIz_nm2=bridge['track'].get('lateral_EI_nm2',2e6)/2,
                    GJ_nm2=bridge['track'].get('torsional_GJ_nm2',.2e6)/2,GAy_n=65e9*.0153,GAz_n=65e9*.0153,
                    mass_kg_m=bridge['track']['mass_kg_m']/2,polar_mass_kg_m=bridge['track']['mass_kg_m']/2*.005)
        for track,y in enumerate(self.tracks):
            for side in (-1,1):
                nodes=[node(route.position(s,y+side*self.gauge/2,0.)) for s in rail_x];self.rails[(track,side)]=[]
                self.fixed.extend(range(6*nodes[0],6*nodes[0]+6));self.fixed.extend(range(6*nodes[-1],6*nodes[-1]+6))
                for j,(a,b) in enumerate(zip(nodes,nodes[1:])):
                    self.rails[(track,side)].append(beam(a,b,rail_p,'rail',float(rail_x[j]),float(rail_x[j+1]),track))
                for j,(s,n) in enumerate(zip(rail_x,nodes)):
                    tributary=(rail_x[min(j+1,len(rail_x)-1)]-rail_x[max(j-1,0)])/2
                    localK=np.diag([bridge['track'].get('longitudinal_pad_n_m2',4e6),bridge['track'].get('lateral_pad_n_m2',8e6),bridge['track']['pad_stiffness_n_m'],0.,0.,0.])*tributary/2
                    R=route.frame(s);G=np.zeros((6,6));G[:3,:3]=R;G[3:,3:]=R;localK=G@localK@G.T
                    if 0<=s<=self.length:
                        deck=self.deck_port(float(s),track,point=route.position(s,y+side*self.gauge/2,0.))
                        indices=list(range(6*n,6*n+6))+deck['dofs'];J=np.hstack([np.eye(6),-deck['H']])
                        self._block(indices,J.T@localK@J,self._kr,self._kc,self._kv)
                    else:self._spring([n],[np.eye(6)],localK,'approach-pad')
        size=6*len(self.coordinates)
        if size>20000:raise ValueError('spatial FEM node budget exceeded')
        self.K=coo_matrix((self._kv,(self._kr,self._kc)),shape=(size,size)).tocsc();self.M=coo_matrix((self._mv,(self._mr,self._mc)),shape=(size,size)).tocsc()
        self.free=np.array([i for i in range(size) if i not in set(self.fixed)]);K=self.K[self.free,:][:,self.free];M=self.M[self.free,:][:,self.free]
        self.factor=splu(K);self.dead_load=np.zeros(size)
        for i,f in self.dead_forces.items():self.dead_load[i]=f
        self.dead_displacement=np.zeros(size);self.dead_displacement[self.free]=self.factor.solve(self.dead_load[self.free])
        values,vectors=eigsh(K,k=modes,M=M,sigma=0.,v0=np.ones(len(self.free)),tol=1e-8)
        order=np.argsort(values);values=values[order];vectors=vectors[:,order]
        if values[0]<=0:raise ValueError('spatial structure has a free/unstable mode')
        self.omega=np.sqrt(values);self.Phi=np.zeros((size,modes));self.Phi[self.free]=vectors
        self.modal_mass_error=float(np.max(np.abs(vectors.T@(M@vectors)-np.eye(modes))))
        if self.modal_mass_error>1e-5:raise ValueError('spatial modes lack mass orthogonality')
        self.modal_K=np.diag(values);self.modal_C=np.diag(2*self.study['analysis']['damping_ratio']*self.omega)

    @staticmethod
    def _block(indices,block,rows,columns,values):
        for i,j in zip(*np.nonzero(block)):
            rows.append(indices[i]);columns.append(indices[j]);values.append(float(block[i,j]))

    def _spring(self,nodes,matrices,K,kind):
        indices=[d for n in nodes for d in range(6*n,6*n+6)];J=np.hstack(matrices)
        self._block(indices,J.T@K@J,self._kr,self._kc,self._kv)
        self.springs.append(dict(kind=kind,nodes=nodes,dofs=indices,J=J,K=K))

    def _port(self,e,s,point=None):
        u=np.clip((s-e['station_start'])/(e['station_end']-e['station_start']),0.,1.);L=e['length'];N,dN=hermite(u*L,0.,L)
        H=np.zeros((6,12));H[0,[0,6]]=[1-u,u];H[1,[1,5,7,11]]=N;H[2,[2,4,8,10]]=N*np.array([1.,-1.,1.,-1.])
        H[3,[3,9]]=[1-u,u];H[4,[2,4,8,10]]=-dN*np.array([1.,-1.,1.,-1.]);H[5,[1,5,7,11]]=dN
        R=e['R'];T=np.zeros((12,12));G=np.zeros((6,6))
        for i in range(4):T[3*i:3*i+3,3*i:3*i+3]=R
        G[:3,:3]=R.T;G[3:,3:]=R.T;H=G@H@T
        centre=(1-u)*self.coordinates[e['nodes'][0]]+u*self.coordinates[e['nodes'][1]]
        if point is not None:
            offset=np.asarray(point)-centre;H[:3]-=skew(offset)@H[3:]
        return dict(dofs=e['dofs'],H=H,point=centre if point is None else np.asarray(point))

    def deck_port(self,s,track,point=None):
        e=next((e for e in self.decks[track] if e['station_start']<=s<e['station_end']),self.decks[track][-1])
        return self._port(e,s,point)

    def rail_port(self,s,track,side,lateral_offset=0.):
        if not -self.approach<=s<=self.length+self.approach:return None
        e=next((e for e in self.rails[(track,side)] if e['station_start']<=s<e['station_end']),self.rails[(track,side)][-1])
        point=self.route.position(s,self.tracks[track]+side*self.gauge/2+lateral_offset,0.)
        port=self._port(e,s,point);port['modal_H']=port['H']@self.Phi[port['dofs']]
        port['dead_pose']=port['H']@self.dead_displacement[port['dofs']]
        return port

    def virtual_work_check(self,port,force,modal_velocity):
        force=np.asarray(force);velocity=np.asarray(modal_velocity)
        point_power=force@(port['modal_H']@velocity);modal_power=(port['modal_H'].T@force)@velocity
        return float(abs(point_power-modal_power))

    def member_demands(self,modal_displacement):
        return self.full_member_demands(self.dead_displacement+self.Phi@modal_displacement)

    def full_member_demands(self,u):
        """Recover all six resultants from the actual full-FE displacement."""
        if np.asarray(u).shape!=(self.K.shape[0],):raise ValueError('full spatial displacement required')
        rows=[]
        for e in self.elements:
            if e['kind']=='rail':continue
            forces=e['K']@u[e['dofs']];R=e['R'];local=np.concatenate([R@forces[i:i+3] for i in (0,3,6,9)])
            rows.append(dict(kind=e['kind'],station_start=e['station_start'],track=e['track'],axial_n=float(local[0]),
                shear_y_n=float(local[1]),shear_z_n=float(local[2]),torsion_nm=float(local[3]),moment_y_nm=float(local[4]),moment_z_nm=float(local[5])))
        return rows


def native_beam_benchmark():
    """Independent OpenSees 3D shear-flexible cantilever, no railway acceptance."""
    import openseespy.opensees as ops
    E=210e9;G=E/2.6;A=.08;Iy=.0006;Iz=.0012;J=.0008;Ay=.06;Az=.05;L=4.
    p=dict(EA_n=E*A,EIy_nm2=E*Iy,EIz_nm2=E*Iz,GJ_nm2=G*J,GAy_n=G*Ay,GAz_n=G*Az,
           mass_kg_m=628.,polar_mass_kg_m=4.)
    _,K,_,_=element_matrices([0.,0.,0.],[L,0.,0.],p)
    F=np.asarray([500.,1000.,2000.,300.,0.,0.]);u=np.linalg.solve(K[6:,6:],F)
    expected=np.asarray([F[0]*L/(E*A),F[1]*(L**3/(3*E*Iz)+L/(G*Ay)),
                         F[2]*(L**3/(3*E*Iy)+L/(G*Az)),F[3]*L/(G*J),
                         -F[2]*L*L/(2*E*Iy),F[1]*L*L/(2*E*Iz)])
    ops.wipe();ops.model('basic','-ndm',3,'-ndf',6)
    try:
        ops.node(1,0.,0.,0.);ops.node(2,L,0.,0.);ops.fix(1,1,1,1,1,1,1)
        ops.geomTransf('Linear',1,0.,0.,1.)
        ops.element('ElasticTimoshenkoBeam',1,1,2,E,G,A,J,Iy,Iz,Ay,Az,1)
        ops.timeSeries('Linear',1);ops.pattern('Plain',1,1);ops.load(2,*F)
        ops.constraints('Plain');ops.numberer('Plain');ops.system('BandGeneral')
        ops.test('NormDispIncr',1e-12,10);ops.algorithm('Linear');ops.integrator('LoadControl',1.);ops.analysis('Static')
        if ops.analyze(1)!=0:raise RuntimeError('native 3D beam benchmark failed')
        native=np.asarray(ops.nodeDisp(2));native_error=float(np.max(np.abs(native-u))/np.max(np.abs(u)))
        analytic_error=float(np.max(np.abs(expected-u))/np.max(np.abs(u)))
    finally:ops.wipe()
    return dict(schema='osr-spatial-beam-benchmark/1',native_solver='OpenSees ElasticTimoshenkoBeam',
        analytic_relative_error=analytic_error,native_relative_error=native_error,
        numerical_benchmark_passed=native_error<1e-9 and analytic_error<1e-9,physical_validation=False)
