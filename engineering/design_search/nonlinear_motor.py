"""Nonlinear DC method fixture and explicit finite-primary overlap controls.

The ideal MMF-driven gapped circuit benchmarks a reversible nonlinear operator
against an independent scalar circuit solution. It is not a LIM thrust model.
Moving nonlinear A-u and full3D/core-loss/thermal capability remain refused.
"""
from pathlib import Path
from math import pi,sqrt
import json,re,subprocess,os,time,resource
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import encoded,identity,digest,source_map
from engineering.station_rail import long_motor,station_motor
from . import lim_materials as mat
PRODUCER='engineering/design_search/nonlinear_motor.py'
TOOLS=Path('/home/hayder/Documents/OpenSourceRail');GETDP=TOOLS/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp'
PRODUCERS=(PRODUCER,'engineering/design_search/lim_materials.py',mat.DATA,long_motor.PRODUCER,station_motor.PRODUCER)
MU0=4e-7*pi


def benchmark_case(*,gap_m=.001,NI_Aturn=1500.,mesh_m=.005,linear=False):
    c=dict(kind='ideal-current-MMF-gapped-circuit',gap_m=gap_m,core_length_m=.1,section_height_m=.02,depth_m=.05,
        NI_Aturn=NI_Aturn,mesh_m=mesh_m,linear=linear,linear_mu_relative=1000.,temperature_C=None,
        scope='Uniform no-fringing ideal winding-MMF fixture; no train, motor or material qualification')
    c['case_id']=identity(c);return c


def _benchmark_mesh(output,c):
    import gmsh
    gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1)
    try:
        o=gmsh.model.occ;core=o.addRectangle(0,0,0,c['core_length_m'],c['section_height_m']);gap=o.addRectangle(c['core_length_m'],0,0,c['gap_m'],c['section_height_m'])
        _,maps=o.fragment([(2,core)],[(2,gap)]);o.synchronize()
        for tag,mp in enumerate(maps,1):gmsh.model.addPhysicalGroup(2,[t for dim,t in mp if dim==2],tag)
        for tag,x in ((101,0.),(102,c['core_length_m']+c['gap_m'])):
            lines=[]
            for dim,t in gmsh.model.getEntities(1):
                bb=gmsh.model.getBoundingBox(dim,t)
                if abs(bb[0]-x)<1e-7 and abs(bb[3]-x)<1e-7:lines.append(t)
            gmsh.model.addPhysicalGroup(1,lines,tag)
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0),min(c['mesh_m'],c['gap_m']/3));gmsh.option.setNumber('Mesh.MshFileVersion',2.2)
        gmsh.model.mesh.generate(2);gmsh.write(str(output/'model.msh'))
        return dict(nodes=len(gmsh.model.mesh.getNodes()[0]),gmsh_version=gmsh.__version__)
    finally:gmsh.finalize()


def _coenergy_expression(curve):
    h=curve['H_A_m'];b=curve['B_T'];total=0.;parts=[]
    for i in range(len(h)-1):
        slope=(b[i+1]-b[i])/(h[i+1]-h[i]);delta=f'($1-{h[i]:.17g})'
        expr=f'({total:.17g}+{b[i]:.17g}*{delta}+.5*{slope:.17g}*{delta}^2)'
        parts.append((h[i+1],expr));total+=.5*(b[i]+b[i+1])*(h[i+1]-h[i])
    # Outside values are never admitted: iteration guard precedes evaluation.
    result=parts[-1][1]
    for high,expr in reversed(parts[:-1]):result=f'($1<={high:.17g}?{expr}:{result})'
    return result


def benchmark_formulation(c,curve):
    pairs=','.join(f'{h:.17g},{b:.17g}' for h,b in zip(curve['H_A_m'],curve['B_T']))
    initial=curve['B_T'][1]/curve['H_A_m'][1]
    law=f'''bb[]=InterpolationLinear[$1]{{{pairs}}}; db[]=dInterpolationLinear[$1]{{{pairs}}};
 mm[]=Norm[$1]<1.e-10?{initial:.17g}:bb[Norm[$1]]/Norm[$1];
 tangent[]=Norm[$1]<1.e-10?TensorDiag[1,1,1]*{initial:.17g}:TensorDiag[1,1,1]*mm[$1]+(db[Norm[$1]]-mm[$1])/SquNorm[$1]*SquDyadicProduct[$1];
 ww[]={_coenergy_expression(curve)};
 mu[Core]=$initial?{initial:.17g}:mm[$1]; jac[Core]=$initial?TensorDiag[1,1,1]*{initial:.17g}:tangent[$1];
 co[Core]=ww[Norm[$1]];'''
    if c['linear']:law='mu[Core]=mu0*1000; jac[Core]=TensorDiag[1,1,1]*mu0*1000; co[Core]=.5*mu0*1000*SquNorm[$1];'
    text=r'''
mu0=4.e-7*Pi;
Group{Core=Region[1];Gap=Region[2];Domain=Region[{1,2}];Left=Region[101];Right=Region[102];}
Function{mu[Gap]=mu0;jac[Gap]=TensorDiag[1,1,1]*mu0;co[Gap]=.5*mu0*SquNorm[$1];@LAW@}
Constraint{{Name Fix;Case{{Region Left;Value @NI@;}{Region Right;Value 0.;}}}}
Jacobian{{Name Vol;Case{{Region All;Jacobian Vol;}}}}
Integration{{Name Gauss;Case{{Type Gauss;Case{{GeoElement Triangle;NumberOfPoints 7;}}}}}}
FunctionSpace{{Name Phi;Type Form0;BasisFunction{{Name sn;NameOfCoef pn;Function BF_Node;Support Domain;Entity NodesOf[All];}}Constraint{{NameOfCoef pn;EntityType NodesOf;NameOfConstraint Fix;}}}}
Formulation{{Name Mag;Type FemEquation;Quantity{{Name p;Type Local;NameOfSpace Phi;}}
 Equation{
 Integral{[-mu[-{d p}]*{d p},{d p}];In Domain;Jacobian Vol;Integration Gauss;}
 Integral{[-jac[-{d p}]*Dof{d p},{d p}];In Domain;Jacobian Vol;Integration Gauss;}
 Integral{[jac[-{d p}]*{d p},{d p}];In Domain;Jacobian Vol;Integration Gauss;}
 }}}
Resolution{{Name Solve;System{{Name S;NameOfFormulation Mag;}}Operation{
 Evaluate[$initial=1];InitSolution[S];Generate[S];Solve[S];PostOperation[Guard];Test[#10>@HMAX@]{Error["Material table domain exceeded before nonlinear evaluation"];}
 Evaluate[$initial=0];Generate[S];GetResidual[S,$r0];Evaluate[$r=$r0,$i=0];
 While[$r>1.e-10 && $r/Max[$r0,1.e-30]>1.e-8 && $i<40]{Solve[S];PostOperation[Guard];Test[#10>@HMAX@]{Error["Material table domain exceeded before nonlinear evaluation"];}Generate[S];GetResidual[S,$r];Evaluate[$i=$i+1];Print[{$i,$r,$r/Max[$r0,1.e-30]},Format "NL %g %.16g %.16g"];}
 Test[$r>1.e-8 && $r/Max[$r0,1.e-30]>1.e-7]{Error["Nonlinear residual did not converge"];}
 SaveSolution[S];
 }}}
PostProcessing{{Name Results;NameOfFormulation Mag;Quantity{
 {Name H;Value{Term{[Norm[{d p}]];In Core;Jacobian Vol;}}}
 {Name Flux;Value{Integral{[Norm[-mu[-{d p}]*{d p}]];In Gap;Jacobian Vol;Integration Gauss;}}}
 {Name Coenergy;Value{Integral{[co[-{d p}]];In Domain;Jacobian Vol;Integration Gauss;}}}
 {Name HB;Value{Integral{[mu[-{d p}]*SquNorm[{d p}]];In Domain;Jacobian Vol;Integration Gauss;}}}
 }}}
PostOperation{
 {Name Guard;NameOfPostProcessing Results;Operation{Print[H,OnElementsOf Core,StoreMaxInRegister 10,File "Hguard.pos"];}}
 {Name Result;NameOfPostProcessing Results;Operation{
 Print[Flux[Gap],OnGlobal,File "flux.txt",Format Table];Print[Coenergy[Domain],OnGlobal,File "coenergy.txt",Format Table];Print[HB[Domain],OnGlobal,File "HB.txt",Format Table];Print[H,OnElementsOf Core,File "H.pos"];
 }}
}
'''
    return text.replace('@LAW@',law).replace('@NI@',str(c['NI_Aturn'])).replace('@HMAX@',str(curve['H_A_m'][-1]))


def _limits():
    old=resource.getrlimit(resource.RLIMIT_AS);cap=min([3*1024**3,*[x for x in old if x!=resource.RLIM_INFINITY]]);resource.setrlimit(resource.RLIMIT_AS,(cap,cap))


def _seal(output,result,sources):
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result))
    m=dict(source_sha256=sources,files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()},**FLAGS);m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m));return result


def run_benchmark(c,output,*,root=ROOT):
    output=Path(output);root=Path(root)
    if output.exists():raise ValueError('Fresh immutable output required')
    output.mkdir(parents=True);curve=mat.material();sources=source_map(root,PRODUCERS)
    (output/'input.json').write_bytes(encoded(dict(case=c,material=curve,source_sha256=sources,getdp_sha256=digest(GETDP))))
    result=dict(kind='nonlinear-magnetostatic-method-benchmark',case=c,material_id=curve['material_id'],execution='planned',numerical_validity='unknown',
        selected_rail_steel_qualified=False,moving_nonlinear_LIM_validated=False,core_loss_thermal_3D_accepted=False,**FLAGS)
    try:
        exact=mat.circuit(curve,c['NI_Aturn'],c['gap_m'],c['core_length_m'],c['section_height_m']*c['depth_m'])
        result['independent_circuit_reference']=exact
        if c['linear']:
            b=c['NI_Aturn']/(c['core_length_m']/(MU0*1000)+c['gap_m']/MU0);exact=dict(B_T=b,attraction_N=c['section_height_m']*c['depth_m']*b*b/(2*MU0))
        result['mesh']=_benchmark_mesh(output,c);(output/'model.pro').write_text(benchmark_formulation(c,curve))
        proc=subprocess.run([str(GETDP),'model.pro','-msh','model.msh','-solve','Solve','-pos','Result','-v','4'],cwd=output,capture_output=True,text=True,timeout=90,preexec_fn=_limits,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        (output/'stdout.log').write_text(proc.stdout);(output/'stderr.log').write_text(proc.stderr)
        if proc.returncode:raise RuntimeError('GetDP returned'+str(proc.returncode))
        B=station_motor._scalar(output/'flux.txt').real/(c['gap_m']*c['section_height_m']);co=station_motor._scalar(output/'coenergy.txt').real*c['depth_m'];hb=station_motor._scalar(output/'HB.txt').real*c['depth_m'];work=c['NI_Aturn']*B*c['section_height_m']*c['depth_m']
        result.update(execution='completed',B_T=B,coenergy_J=co,attraction_from_gap_stress_N=c['section_height_m']*c['depth_m']*B*B/(2*MU0),
            reference_relative_B_error=abs(B-exact['B_T'])/exact['B_T'],weak_flux_work_relative_residual=abs(hb-work)/max(1.,work),
            nonlinear_iterations=[line for line in proc.stdout.splitlines() if 'NL ' in line],numerical_validity='valid' if abs(B-exact['B_T'])/exact['B_T']<.005 and abs(hb-work)/max(1.,work)<1e-6 else 'invalid')
    except ValueError as error:result.update(execution='refused',reason=str(error))
    except Exception as error:result.update(execution='tool_error',reason=str(error))
    if sources!=source_map(root,PRODUCERS):raise ValueError('Source changed during execution')
    return _seal(output,result,sources)


def overlap_case(position='centred',*,current_peak_A=50.):
    d=station_motor.definition();L=.5;fin=.3;start={'entry':-.15,'centred':.10,'exit':.35}[position]
    c=dict(speed_m_s=10.,frequency_Hz=30.,current_peak_A=current_peak_A,current_RMS_A=current_peak_A/sqrt(2),phase_direction=1,temperature_C=80.,
        gap_each_side_m=.015,periods=1,active_length_m=L,secondary_length_m=fin,secondary_start_x_m=start,secondary_end_x_m=start+fin,
        mesh_m=.01,plate_gap_mesh_m=.00375,transverse_outer_air_margin_m=.2,outer_margin_m=.5,aluminium_conductivity_S_m=20e6,
        wire_current_density_RMS_A_mm2=current_peak_A/sqrt(2)/25.)
    c['position']=position;c['case_id']=identity(c);return c


def run_overlap(c,output,*,root=ROOT,nonlinear=False):
    output=Path(output);root=Path(root)
    if output.exists():raise ValueError('Fresh immutable output required')
    output.mkdir(parents=True);sources=source_map(root,PRODUCERS);d=station_motor.definition();d.update(secondary_length_m=c['secondary_length_m'])
    (output/'input.json').write_bytes(encoded(dict(case=c,definition=d,source_sha256=sources,getdp_sha256=digest(GETDP))))
    r=dict(kind='linear-finite-overlap-method-control',case=c,execution='planned',numerical_validity='unknown',available_installed_force_N=None,
        force_scaling_applied=False,nonlinear_machine_gate='held',supplier_material_gate='held',loss_thermal_3D_gate='held',**FLAGS)
    if nonlinear:r.update(execution='refused',reason='Moving nonlinear A-u transient/circuit/energy/force implementation not independently validated; constant-mu phasor substitution prohibited');return _seal(output,r,sources)
    try:
        r['mesh']=long_motor.mesh(output,c,d);(output/'motor.pro').write_text(long_motor.formulation(c,d))
        proc=subprocess.run([str(GETDP),'motor.pro','-msh','motor.msh','-solve','Solve','-pos','Result','-v','4'],cwd=output,capture_output=True,text=True,timeout=90,preexec_fn=_limits,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        (output/'stdout.log').write_text(proc.stdout);(output/'stderr.log').write_text(proc.stderr)
        if proc.returncode:raise RuntimeError('GetDP returned'+str(proc.returncode))
        force=station_motor._scalar(output/'force.txt').real*d['active_height_m'];heat=station_motor._scalar(output/'joule.txt').real*d['active_height_m'];power=station_motor._scalar(output/'power.txt').real*d['active_height_m']
        B=[]
        for v in re.findall(r'S(?:T|Q|P)\([^)]*\)\{([^}]+)\}',(output/'steelB.pos').read_text()):B.extend(float(x) for x in v.split(','))
        peak=max(B);res=abs(power-heat-force*c['speed_m_s'])/max(1.,abs(power),heat,abs(force*c['speed_m_s']))
        r.update(execution='completed',force_N_actual_small_geometry=force,secondary_Joule_W=heat,source_real_W=power,maximum_steel_phasor_B_bound_T=peak,
            field_model_domain='within-linear-hypothesis' if peak<=1.3 else 'outside-linear-hypothesis',relative_energy_residual=res,numerical_validity='valid' if res<1e-6 else 'invalid')
    except Exception as error:r.update(execution='tool_error',reason=str(error))
    if sources!=source_map(root,PRODUCERS):raise ValueError('Source changed during execution')
    return _seal(output,r,sources)
