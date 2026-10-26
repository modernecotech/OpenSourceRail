"""Current-excited slotted double-sided LIM research model.

Native 2D A-u magnetodynamics uses the actual primary teeth, backiron and
three-phase winding regions. It includes secondary motion and floating-current
closure. Linear steel, finite-height/end-turn fields and nonlinear harmonics
remain explicit limitations; this is not an accepted installed motor map.
"""
from __future__ import annotations
from pathlib import Path
from math import pi,sqrt,cos,sin,ceil
import json,os,re,subprocess,shutil
from . import ROOT,FLAGS
from .common import encoded,identity,digest,source_map
PRODUCER='engineering/station_rail/station_motor.py'
REFERENCE='https://getdp.info/doc/texinfo/getdp.html'
TEMPLATE='build/trip-dynamics/tools/getdp-3.5.0-Linux64/share/doc/getdp/templates/Lib_Magnetodynamics2D_av_Cir.pro'


def definition():
    d=dict(schema='osr-station-LIM-primary-definition/1',family='double-sided-slotted-LIM',
        wavelength_m=.5,slots_per_period=6,pole_pitch_m=.25,slot_pitch_m=.5/6,
        slot_width_m=.04,slot_depth_m=.055,backiron_m=.025,active_height_m=.16,
        secondary_thickness_m=.015,nominal_gap_each_side_m=.015,
        secondary_length_m=9.,addressed_module_length_m=12.5,
        turns_per_coil=40,conductor_area_m2=25e-6,
        phase_sequence=['A+','C-','B+','A-','C+','B-'],
        end_turn_extra_length_m=.05,steel_relative_permeability_hypothesis=1000.,
        linear_steel_peak_field_limit_T_hypothesis=1.3,
        copper_resistivity_20C_ohm_m_hypothesis=1.724e-8,
        copper_temperature_coefficient_K_inv_hypothesis=.00393,
        aluminium_conductivity_20C_S_m_hypothesis=32e6,
        aluminium_conductivity_80C_S_m_hypothesis=20e6,
        steel_density_kg_m3_hypothesis=7850.,copper_density_kg_m3_hypothesis=8960.,
        supported_domain='2D longitudinal/transverse current-excited finite primary, uniform extruded height; material hypotheses only',
        physical_accepted=False)
    d['slot_fill_fraction']=d['turns_per_coil']*d['conductor_area_m2']/(d['slot_width_m']*d['slot_depth_m'])
    length_per_coil=d['turns_per_coil']*(2*(d['active_height_m']+d['pole_pitch_m'])+d['end_turn_extra_length_m'])
    d['wire_length_m_per_coil']=length_per_coil
    d['coils_both_sides_per_m']=2*3/d['wavelength_m']
    d['copper_kg_per_m']=length_per_coil*d['conductor_area_m2']*8960*d['coils_both_sides_per_m']
    iron_area_two_sides=2*(d['backiron_m']+d['slot_depth_m']*(1-d['slot_width_m']/d['slot_pitch_m']))*d['active_height_m']
    d['primary_steel_kg_per_m']=iron_area_two_sides*7850
    d['bare_primary_stock_kg_per_m']=d['copper_kg_per_m']+d['primary_steel_kg_per_m']
    d['bare_900m_stock_kg_per_direction']=900*d['bare_primary_stock_kg_per_m']
    d['bare_12_5m_module_stock_kg_both_sides']=12.5*d['bare_primary_stock_kg_per_m']
    d['excluded_mass_and_cost']=['Laminations insulation and joints','Supports/fasteners/cooling','Inverters and sectional switchgear','Civil supports and station supply']
    d['motor_component_id']=identity(d)
    return d


def case(*,speed_m_s=20.,frequency_Hz=45.,current_peak_A=100.,gap_m=.015,
         temperature_C=80.,phase_direction=1,periods=3,mesh_m=.005,margin_m=.5):
    if speed_m_s<0 or frequency_Hz<=0 or current_peak_A<=0 or gap_m<=0 or temperature_C not in (20.,80.) or phase_direction not in (-1,1) or periods not in (3,6) or mesh_m<=0:
        raise ValueError('Declared positive motor research domain required')
    d=definition();r=dict(speed_m_s=speed_m_s,frequency_Hz=frequency_Hz,current_peak_A=current_peak_A,
        current_RMS_A=current_peak_A/sqrt(2),gap_each_side_m=gap_m,temperature_C=temperature_C,
        phase_direction=phase_direction,periods=periods,active_length_m=periods*d['wavelength_m'],
        mesh_m=mesh_m,outer_margin_m=margin_m,
        aluminium_conductivity_S_m=d['aluminium_conductivity_20C_S_m_hypothesis'] if temperature_C==20 else d['aluminium_conductivity_80C_S_m_hypothesis'],
        wire_current_density_RMS_A_mm2=current_peak_A/sqrt(2)/(d['conductor_area_m2']*1e6))
    r['case_id']=identity(r);return r


def evaluate(vehicle,root=ROOT):
    d=definition();m=vehicle['mass']['accounted_cap_loaded_kg_per_car']
    inertia=sum(.5*p['mass_kg']*(p['radius_m']**2+p.get('inner_radius_m',0.)**2)
        for p in vehicle['geometry_parts'] if p['id'].startswith('bogie/') and p['kind'] in ('cylinder','annular-cylinder'))
    equivalent=inertia/.38**2
    resist=.0025*m*9.80665+50+1.8*20**2
    return dict(schema='osr-station-LIM-primary-requirements/1',candidate_id=vehicle['candidate_id'],
        propulsion_component_id=vehicle['propulsion_component_id'],motor_component_id=d['motor_component_id'],definition=d,
        normal_required_force_N_per_car=.4*(m+equivalent)+resist,
        normal_rotational_inertia_kg_m2=inertia,equivalent_rotating_mass_kg_per_car=equivalent,
        no_wheel_adhesion_cap_on_direct_LIM_body_thrust=True,
        available_installed_force_N_per_car=None,actual_installed_thermal_and_inverter_screen='unknown',
        source_sha256=source_map(root,(PRODUCER,)),**FLAGS)


def mesh(folder,c,d):
    import gmsh
    folder=Path(folder);gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1)
    try:
        gmsh.model.add('station_LIM');occ=gmsh.model.occ
        L=c['active_length_m'];margin=c['outer_margin_m'];half=d['secondary_thickness_m']/2;face=half+c['gap_each_side_m'];outer=face+d['slot_depth_m']+d['backiron_m'];Y=outer+.12
        air=occ.addRectangle(-margin,-Y,0,L+2*margin,2*Y)
        secondary=occ.addRectangle(-margin,-half,0,L+2*margin,2*half)
        steel=[occ.addRectangle(0,face,0,L,d['slot_depth_m']+d['backiron_m']),occ.addRectangle(0,-outer,0,L,d['slot_depth_m']+d['backiron_m'])]
        slots=[]
        for side in (-1,1):
            for k in range(c['periods']*6):
                x=(k+.5)*d['slot_pitch_m'];y=face if side>0 else -face-d['slot_depth_m']
                slots.append((occ.addRectangle(x-d['slot_width_m']/2,y,0,d['slot_width_m'],d['slot_depth_m']),k%6,side))
        tools=[(2,secondary),*[(2,s) for s in steel],*[(2,s[0]) for s in slots]]
        out,maps=occ.fragment([(2,air)],tools);occ.synchronize()
        surf=lambda m:{t for dim,t in m if dim==2}
        sec=surf(maps[1]);iron=surf(maps[2])|surf(maps[3]);slotsets={100+k:set() for k in range(6)}
        for i,(_,phase,side) in enumerate(slots):slotsets[100+phase]|=surf(maps[4+i])
        coil=set().union(*slotsets.values());iron-=coil
        allfaces={t for dim,t in out if dim==2};airfaces=allfaces-sec-iron-coil
        for tag,faces in [(1,airfaces),(2,sec),(3,iron),*slotsets.items()]:gmsh.model.addPhysicalGroup(2,sorted(faces),tag)
        outercurves=[]
        for dim,tag in gmsh.model.getBoundary([(2,t) for t in allfaces],combined=True,oriented=False):
            bb=gmsh.model.getBoundingBox(dim,tag)
            if abs(bb[0]+margin)<1e-5 and abs(bb[3]+margin)<1e-5 or abs(bb[0]-L-margin)<1e-5 and abs(bb[3]-L-margin)<1e-5 or abs(bb[1]+Y)<1e-5 and abs(bb[4]+Y)<1e-5 or abs(bb[1]-Y)<1e-5 and abs(bb[4]-Y)<1e-5:outercurves.append(tag)
        gmsh.model.addPhysicalGroup(1,outercurves,901)
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0),c['mesh_m'])
        box=gmsh.model.mesh.field.add('Box');gmsh.model.mesh.field.setNumber(box,'VIn',c['mesh_m']);gmsh.model.mesh.field.setNumber(box,'VOut',.04)
        for name,val in dict(XMin=-.05,XMax=L+.05,YMin=-outer-.01,YMax=outer+.01).items():gmsh.model.mesh.field.setNumber(box,name,val)
        gmsh.model.mesh.field.setAsBackgroundMesh(box);gmsh.option.setNumber('Mesh.MeshSizeMin',c['mesh_m']/2);gmsh.option.setNumber('Mesh.MeshSizeMax',.04)
        gmsh.option.setNumber('Mesh.MshFileVersion',2.2);gmsh.model.mesh.generate(2);gmsh.write(str(folder/'motor.msh'))
        return dict(gmsh_version=gmsh.__version__,node_count=len(gmsh.model.mesh.getNodes()[0]),surface_count=len(allfaces),slot_count=len(slots),outer_boundary_curves=len(outercurves),magnetic_outer_halfwidth_m=Y)
    finally:gmsh.finalize()


def formulation(c,d):
    js=[]
    amp=d['turns_per_coil']*c['current_peak_A']/(d['slot_width_m']*d['slot_depth_m'])
    for k in range(6):
        a=-c['phase_direction']*2*pi*k/6
        js.append(f'js[Region[{100+k}]]=Vector[0,0,Complex[{amp*cos(a):.16g},{amp*sin(a):.16g}]];')
    s=r'''// A-u formulation follows the official GetDP magnetodynamics template.
mu0=4.e-7*Pi;Freq=@FREQ@;sigma=@SIGMA@;
Group { Air=Region[1];Plate=Region[2];Steel=Region[3];Coils=Region[{100,101,102,103,104,105}];Domain=Region[{Air,Plate,Steel,Coils}];Outer=Region[901]; }
Function {nu[Region[{Air,Plate,Coils}]]=1/mu0;nu[Steel]=1/(mu0*@MUR@);v[]=Vector[@SPEED@,0,0];@JS@}
Constraint {{Name Boundary;Case {{Region Outer;Value 0.;}}}}
Jacobian {{Name Vol;Case {{Region All;Jacobian Vol;}}}}
Integration {{Name Gauss;Case {{Type Gauss;Case {{GeoElement Triangle;NumberOfPoints 7;}}}}}}
FunctionSpace {
 {Name As;Type Form1P;BasisFunction {{Name sn;NameOfCoef an;Function BF_PerpendicularEdge;Support Domain;Entity NodesOf[All];}}Constraint {{NameOfCoef an;EntityType NodesOf;NameOfConstraint Boundary;}}}
 {Name Us;Type Form1P;BasisFunction {{Name sr;NameOfCoef ur;Function BF_RegionZ;Support Plate;Entity Region[Plate];}}}
}
Formulation {{Name Motor;Type FemEquation;Quantity {{Name a;Type Local;NameOfSpace As;}{Name u;Type Local;NameOfSpace Us;}}
 Equation {
 Integral {[nu[]*Dof{d a},{d a}];In Domain;Jacobian Vol;Integration Gauss;}
 Integral {DtDof [sigma*Dof{a},{a}];In Plate;Jacobian Vol;Integration Gauss;}
 Integral {[sigma*Dof{u},{a}];In Plate;Jacobian Vol;Integration Gauss;}
 Integral {[-sigma*(v[] /\ Dof{d a}),{a}];In Plate;Jacobian Vol;Integration Gauss;}
 Integral {[-js[],{a}];In Coils;Jacobian Vol;Integration Gauss;}
 Integral {DtDof [sigma*Dof{a},{u}];In Plate;Jacobian Vol;Integration Gauss;}
 Integral {[sigma*Dof{u},{u}];In Plate;Jacobian Vol;Integration Gauss;}
 Integral {[-sigma*(v[] /\ Dof{d a}),{u}];In Plate;Jacobian Vol;Integration Gauss;}
 }}}
Resolution {{Name Solve;System {{Name S;NameOfFormulation Motor;Type ComplexValue;Frequency Freq;}}Operation {Generate[S];Solve[S];SaveSolution[S];}}}
PostProcessing {{Name Result;NameOfFormulation Motor;Quantity {
 {Name Joule;Value {Integral {[.5*sigma*Re[CompZ[Dt[{a}]+{u}-(v[] /\ {d a})]*Conj[CompZ[Dt[{a}]+{u}-(v[] /\ {d a})]]]];In Plate;Jacobian Vol;Integration Gauss;}}}
 {Name ForceX;Value {Integral {[.5*sigma*Re[CompZ[Dt[{a}]+{u}-(v[] /\ {d a})]*Conj[CompY[{d a}]]]];In Plate;Jacobian Vol;Integration Gauss;}}}
 {Name ForceY;Value {Integral {[-.5*sigma*Re[CompZ[Dt[{a}]+{u}-(v[] /\ {d a})]*Conj[CompX[{d a}]]]];In Plate;Jacobian Vol;Integration Gauss;}}}
 {Name SourcePower;Value {Integral {[.5*CompZ[js[]]*Conj[CompZ[Dt[{a}]]]];In Coils;Jacobian Vol;Integration Gauss;}}}
 {Name NetJ;Value {Integral {[-sigma*CompZ[Dt[{a}]+{u}-(v[] /\ {d a})]];In Plate;Jacobian Vol;Integration Gauss;}}}
 {Name Bamp;Value {Term {[Sqrt[Re[CompX[{d a}]*Conj[CompX[{d a}]]+CompY[{d a}]*Conj[CompY[{d a}]]]]];In Steel;Jacobian Vol;}}}
 }}}
PostOperation {{Name Result;NameOfPostProcessing Result;Operation {
 Print[Joule[Plate],OnGlobal,File "joule.txt",Format Table];
 Print[ForceX[Plate],OnGlobal,File "force.txt",Format Table];
 Print[ForceY[Plate],OnGlobal,File "normal.txt",Format Table];
 Print[SourcePower[Coils],OnGlobal,File "power.txt",Format Table];
 Print[NetJ[Plate],OnGlobal,File "netcurrent.txt",Format Table];
 Print[Bamp,OnElementsOf Steel,File "steelB.pos",Depth 0];
 }}}
'''
    for name,value in {'@FREQ@':c['frequency_Hz'],'@SIGMA@':c['aluminium_conductivity_S_m'],'@MUR@':d['steel_relative_permeability_hypothesis'],'@SPEED@':c['speed_m_s'],'@JS@':'\n'.join(js)}.items():s=s.replace(name,str(value))
    return s


def _scalar(path):
    rows=[line for line in Path(path).read_text().splitlines() if line.strip() and not line.startswith('#')]
    v=[float(x) for x in rows[-1].split()];return complex(v[1],v[2] if len(v)>2 else 0.)


def solve(folder,c,d,getdp):
    folder=Path(folder);folder.mkdir(parents=True);(folder/'case.json').write_bytes(encoded(c));(folder/'definition.json').write_bytes(encoded(d))
    meta=mesh(folder,c,d);(folder/'mesh.json').write_bytes(encoded(meta));(folder/'motor.pro').write_text(formulation(c,d))
    command=[str(getdp),'motor.pro','-msh','motor.msh','-solve','Solve','-pos','Result','-v','4']
    proc=subprocess.run(command,cwd=folder,capture_output=True,text=True,timeout=180,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
    (folder/'stdout.log').write_text(proc.stdout);(folder/'stderr.log').write_text(proc.stderr)
    if proc.returncode:raise RuntimeError('Native primary solve failed; logs retained at '+str(folder))
    height=d['active_height_m'];f=_scalar(folder/'force.txt').real*height;fy=_scalar(folder/'normal.txt').real*height;joule=_scalar(folder/'joule.txt').real*height;power=_scalar(folder/'power.txt')*height
    vals=[]
    for group in re.findall(r'S(?:T|Q|P)\([^)]*\)\{([^}]+)\}',(folder/'steelB.pos').read_text()):vals += [float(x) for x in group.split(',')]
    B=max(vals) if vals else None
    phases_coils_each=c['periods']*2
    rho=d['copper_resistivity_20C_ohm_m_hypothesis']*(1+d['copper_temperature_coefficient_K_inv_hypothesis']*(c['temperature_C']-20))
    coilR=rho*d['wire_length_m_per_coil']/d['conductor_area_m2'];copper=c['current_RMS_A']**2*coilR*phases_coils_each*3
    scale=d['secondary_length_m']/c['active_length_m'];mechanical=f*c['speed_m_s'];residual=power.real-joule-mechanical
    result=dict(case=c,mesh=meta,execution='completed',force_N_finite_2D_primary=f,normal_force_N_finite_2D_primary=fy,
        secondary_Joule_W_finite_2D_primary=joule,source_field_real_power_W=power.real,source_field_reactive_power_var=-power.imag,
        mechanical_power_W=mechanical,field_energy_residual_W=residual,
        relative_energy_residual=abs(residual)/max(1.,abs(power.real),joule,abs(mechanical)),
        net_secondary_current_A_per_m_height=[_scalar(folder/'netcurrent.txt').real,_scalar(folder/'netcurrent.txt').imag],
        maximum_steel_phasor_B_bound_T=B,
        linear_material_domain_screen='pass' if B is not None and B<=d['linear_steel_peak_field_limit_T_hypothesis'] else 'fail',
        coil_resistance_ohm_at_temperature=coilR,primary_copper_loss_W_finite_model=copper,
        lumped_total_input_real_W=power.real+copper,
        implied_balanced_phase_voltage_RMS_V_lower_bound=abs(complex(power.real+copper,-power.imag))/(3*c['current_RMS_A']),
        conditional_9m_force_N=f*scale,conditional_9m_secondary_Joule_W=joule*scale,
        conditional_9m_primary_copper_loss_W=copper*scale,
        extrapolation='Finite2D primary force scaled by active length; actual9m ends, finite height, current returns and primary circuit not confirmed',
        installed_motor_available_force_N=None,thermal_equilibrium_C=None,
        slot_fill_screen='pass' if d['slot_fill_fraction']<=.6 else 'fail',
        copper_RMS_current_density_screen='pass' if c['wire_current_density_RMS_A_mm2']<=4. else 'fail',
        full_installed_force_map_accepted=False,**FLAGS)
    (folder/'result.json').write_bytes(encoded(result));return result


def campaign_cases():
    base=[case(mesh_m=h) for h in (.01,.005,.0025)]
    base += [case(speed_m_s=0.,frequency_Hz=5.),case(speed_m_s=0.,frequency_Hz=5.,phase_direction=-1),
       case(speed_m_s=10.,frequency_Hz=25.),case(current_peak_A=50.),case(current_peak_A=150.),
       case(temperature_C=20.),case(gap_m=.01),case(gap_m=.02),case(margin_m=1.),case(periods=6)]
    return base


def run(output,root=ROOT,*,getdp=None,cases=None):
    root=Path(root).resolve();output=Path(output).resolve()
    if output.exists():raise ValueError('Preserve previous native run; use a fresh directory')
    output.mkdir(parents=True);source=source_map(root,(PRODUCER,TEMPLATE));d=definition()
    getdp=Path(getdp) if getdp else root/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp'
    cases=campaign_cases() if cases is None else cases
    (output/'input.json').write_bytes(encoded(dict(definition=d,cases=cases,source_sha256=source)))
    rows=[]
    for i,c in enumerate(cases):rows.append(solve(output/f'case-{i:02d}-{c["case_id"][:8]}',c,d,getdp))
    if source_map(root,(PRODUCER,TEMPLATE))!=source:raise ValueError('Native motor source changed during execution')
    result=dict(schema='osr-native-current-excited-LIM/1',motor_component_id=d['motor_component_id'],definition=d,
        execution='completed',cases=rows,case_count=len(rows),source_sha256=source,
        numerical_validity='requires independent mesh, sign, power and boundary assessment',
        complete_installed_motor_map=False,actual_installed_force_N=None,**FLAGS)
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result))
    m=dict(schema='osr-native-primary-package/1',source_sha256=source,files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()},**FLAGS)
    m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m));return result


def verify(output,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Motor package identity differs')
    if any(digest(Path(root)/n)!=h for n,h in m['source_sha256'].items()):raise ValueError('Motor source differs')
    if {p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Motor payload differs')
    if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Motor result identity differs')
    if any(r.get(k) is not v or m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Research cannot grant release')
    return dict(verified=True,evaluation_id=r['evaluation_id'],case_count=r['case_count'],complete_installed_motor_map=False,physical_accepted=False)
