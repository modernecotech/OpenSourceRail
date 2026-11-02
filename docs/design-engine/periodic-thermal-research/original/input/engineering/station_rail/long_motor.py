"""One full12.5m station primary against the actual9m train fin (2D research).

This separate adapter preserves the short-primary campaign and includes the
finite secondary ends. Finite-height return current, nonlinear steel, actual
end turns and converter transients remain unvalidated.
"""
from pathlib import Path
from math import sqrt,ceil
import json,os,re,subprocess
from . import ROOT,FLAGS
from .common import encoded,identity,digest,source_map
from . import station_motor as short
PRODUCER='engineering/station_rail/long_motor.py'


def configuration():
    d=short.definition();L=d['addressed_module_length_m'];fin=d['secondary_length_m']
    g=dict(primary_length_m=L,secondary_length_m=fin,secondary_start_x_m=(L-fin)/2,
        secondary_end_x_m=(L+fin)/2,periods=25,primary_sides=2,
        wavelength_m=d['wavelength_m'],active_height_m=d['active_height_m'],
        secondary_thickness_m=d['secondary_thickness_m'],gap_each_side_m=.015,
        slot_width_m=d['slot_width_m'],slot_depth_m=d['slot_depth_m'],backiron_m=d['backiron_m'],
        turns_per_coil=d['turns_per_coil'],conductor_area_m2=d['conductor_area_m2'],
        coils_per_phase_both_sides=50,phase_coils_connection='all50series per phase for terminal voltage calculation',
        steel_kg=L*d['primary_steel_kg_per_m'],copper_kg=L*d['copper_kg_per_m'],
        excludes='Cooling/supports/fasteners, laminated insulation, switchgear, inverters, cable and installation')
    g['motor_component_id']=identity(g);return g


def case():
    c=short.case(frequency_Hz=50.,current_peak_A=140.,mesh_m=.01)
    c.pop('case_id');c.update(periods=25,active_length_m=12.5,secondary_length_m=9.,
        secondary_start_x_m=1.75,secondary_end_x_m=10.75,plate_gap_mesh_m=.00375,
        transverse_outer_air_margin_m=.20,outer_margin_m=.5,
        domain='Finite12.5m primary with centred9m secondary; no length extrapolation')
    c['case_id']=identity(c);return c


def mesh(folder,c,d):
    import gmsh
    gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1)
    try:
        gmsh.model.add('full_station_LIM');occ=gmsh.model.occ;L=c['active_length_m'];margin=c['outer_margin_m'];half=d['secondary_thickness_m']/2
        face=half+c['gap_each_side_m'];outer=face+d['slot_depth_m']+d['backiron_m'];Y=outer+c['transverse_outer_air_margin_m']
        air=occ.addRectangle(-margin,-Y,0,L+2*margin,2*Y)
        fin=occ.addRectangle(c['secondary_start_x_m'],-half,0,c['secondary_length_m'],2*half)
        iron=[occ.addRectangle(0,face,0,L,d['slot_depth_m']+d['backiron_m']),occ.addRectangle(0,-outer,0,L,d['slot_depth_m']+d['backiron_m'])]
        slots=[]
        for side in (-1,1):
            for k in range(c['periods']*6):
                x=(k+.5)*d['slot_pitch_m'];y=face if side>0 else -face-d['slot_depth_m']
                slots.append((occ.addRectangle(x-d['slot_width_m']/2,y,0,d['slot_width_m'],d['slot_depth_m']),k%6))
        out,maps=occ.fragment([(2,air)],[(2,fin),*[(2,x) for x in iron],*[(2,x[0]) for x in slots]]);occ.synchronize()
        surf=lambda mapping:{t for dim,t in mapping if dim==2}
        plate=surf(maps[1]);steel=surf(maps[2])|surf(maps[3]);phases={100+k:set() for k in range(6)}
        for i,(_,phase) in enumerate(slots):phases[100+phase]|=surf(maps[4+i])
        coils=set().union(*phases.values());steel-=coils;allfaces={t for dim,t in out if dim==2}
        for tag,faces in [(1,allfaces-plate-steel-coils),(2,plate),(3,steel),*phases.items()]:gmsh.model.addPhysicalGroup(2,sorted(faces),tag)
        boundaries=[t for dim,t in gmsh.model.getBoundary([(2,t) for t in allfaces],combined=True,oriented=False)]
        gmsh.model.addPhysicalGroup(1,boundaries,901)
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0),c['mesh_m'])
        bulk=gmsh.model.mesh.field.add('Box');gmsh.model.mesh.field.setNumber(bulk,'VIn',c['mesh_m']);gmsh.model.mesh.field.setNumber(bulk,'VOut',.05)
        for n,v in dict(XMin=-.05,XMax=L+.05,YMin=-outer-.01,YMax=outer+.01).items():gmsh.model.mesh.field.setNumber(bulk,n,v)
        near=gmsh.model.mesh.field.add('Box');gmsh.model.mesh.field.setNumber(near,'VIn',c['plate_gap_mesh_m']);gmsh.model.mesh.field.setNumber(near,'VOut',.05)
        for n,v in dict(XMin=-.05,XMax=L+.05,YMin=-face,YMax=face).items():gmsh.model.mesh.field.setNumber(near,n,v)
        minimum=gmsh.model.mesh.field.add('Min');gmsh.model.mesh.field.setNumbers(minimum,'FieldsList',[bulk,near]);gmsh.model.mesh.field.setAsBackgroundMesh(minimum)
        gmsh.option.setNumber('Mesh.MeshSizeMin',c['plate_gap_mesh_m']);gmsh.option.setNumber('Mesh.MeshSizeMax',.05);gmsh.option.setNumber('Mesh.MshFileVersion',2.2)
        gmsh.model.mesh.generate(2);gmsh.write(str(Path(folder)/'motor.msh'))
        return dict(gmsh_version=gmsh.__version__,node_count=len(gmsh.model.mesh.getNodes()[0]),slot_count=len(slots),
            plate_gap_target_layers=c['gap_each_side_m']/c['plate_gap_mesh_m'],transverse_outer_halfwidth_m=Y,
            axial_mesh_max_inside_primary_m=c['mesh_m'],wavelength_elements_min=d['wavelength_m']/c['mesh_m'])
    finally:gmsh.finalize()


def formulation(c,d):
    text=short.formulation(c,d)
    needle='Coils=Region[{100,101,102,103,104,105}];'
    if text.count(needle)!=1:raise ValueError('Versioned primary formulation interface changed')
    text=text.replace(needle,needle+'PhaseA=Region[{100,103}];PhaseB=Region[{102,105}];PhaseC=Region[{101,104}];')
    quantities=''.join('{Name Phase'+p+'Power;Value {Integral {[.5*CompZ[js[]]*Conj[CompZ[Dt[{a}]]]];In Phase'+p+';Jacobian Vol;Integration Gauss;}}}\n' for p in 'ABC')
    text=text.replace(' {Name NetJ;',quantities+' {Name NetJ;')
    text=text.replace(' Print[NetJ[Plate]', ''.join(' Print[Phase'+p+'Power[Phase'+p+'],OnGlobal,File "phase'+p+'.txt",Format Table];\n' for p in 'ABC')+' Print[NetJ[Plate]')
    return text


def run(output,root=ROOT,*,getdp=None):
    root=Path(root).resolve();output=Path(output).resolve()
    if output.exists():raise ValueError('Retain immutable run; use a fresh directory')
    output.mkdir(parents=True);source=source_map(root,(PRODUCER,short.PRODUCER));c=case();d=short.definition();g=configuration()
    getdp=Path(getdp) if getdp else root/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp';exe_sha=digest(getdp)
    (output/'input.json').write_bytes(encoded(dict(case=c,configuration=g,definition=d,source_sha256=source,getdp_binary_sha256=exe_sha)))
    meta=mesh(output,c,d);(output/'mesh.json').write_bytes(encoded(meta));(output/'motor.pro').write_text(formulation(c,d))
    command=[str(getdp),'motor.pro','-msh','motor.msh','-solve','Solve','-pos','Result','-v','4']
    proc=subprocess.run(command,cwd=output,capture_output=True,text=True,timeout=180,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
    (output/'stdout.log').write_text(proc.stdout);(output/'stderr.log').write_text(proc.stderr)
    if proc.returncode:raise RuntimeError('Full module native solve failed; logs preserved')
    h=d['active_height_m'];force=short._scalar(output/'force.txt').real*h;normal=short._scalar(output/'normal.txt').real*h;heat=short._scalar(output/'joule.txt').real*h;power=short._scalar(output/'power.txt')*h
    values=[]
    for group in re.findall(r'S(?:T|Q|P)\([^)]*\)\{([^}]+)\}',(output/'steelB.pos').read_text()):values.extend(float(x) for x in group.split(','))
    B=max(values) if values else None
    rho=d['copper_resistivity_20C_ohm_m_hypothesis']*(1+d['copper_temperature_coefficient_K_inv_hypothesis']*(c['temperature_C']-20))
    R=rho*d['wire_length_m_per_coil']/d['conductor_area_m2'];Irms=c['current_RMS_A'];cu_phase=Irms**2*R*50;phases=[]
    for phase in 'ABC':
        S=short._scalar(output/('phase'+phase+'.txt'))*h
        phases.append(dict(phase=phase,field_real_W=S.real,field_reactive_var=-S.imag,copper_W=cu_phase,
            all_series_phase_voltage_RMS_V=abs(complex(S.real+cu_phase,-S.imag))/Irms))
    copper=3*cu_phase;net=short._scalar(output/'netcurrent.txt');residual=power.real-heat-force*c['speed_m_s']
    result=dict(schema='osr-native-full-station-LIM-2D/1',execution='completed',motor_component_id=g['motor_component_id'],configuration=g,case=c,mesh=meta,
        force_N_full9m_fin_2D=force,normal_force_N_full9m_fin_2D=normal,secondary_Joule_W=heat,
        source_field_real_W=power.real,source_field_reactive_var=-power.imag,primary_copper_W=copper,
        estimated_real_input_W=power.real+copper,mechanical_W=force*c['speed_m_s'],
        relative_energy_residual=abs(residual)/max(1.,abs(power.real),heat,abs(force*c['speed_m_s'])),
        net_secondary_current_A_per_m_height=[net.real,net.imag],maximum_steel_phasor_B_bound_T=B,
        linear_material_domain_screen='pass' if B is not None and B<=d['linear_steel_peak_field_limit_T_hypothesis'] else 'fail',
        slot_fill_fraction=d['slot_fill_fraction'],RMS_wire_density_A_mm2=c['wire_current_density_RMS_A_mm2'],
        conductor_current_screen='pass' if c['wire_current_density_RMS_A_mm2']<=4 else 'fail',
        phase_terminal_requirements=phases,
        all_series_750Vdc_upper_voltage_bound_V=750/sqrt(6),
        all_series_750Vdc_screen='pass' if max(p['all_series_phase_voltage_RMS_V'] for p in phases)<=750/sqrt(6) else 'fail',
        circuit_note='Exactly50coil series/phase assumed for induced+resistive voltage. Parallel regrouping requires individual flux/circuit and current-sharing evaluation; not credited here.',
        installed_available_force_N=None,thermal_equilibrium_C=None,physical_accepted=False,
        missing_confirmation=['Finite-height secondary current return and 3D force/moments','Steel nonlinear BH/hysteresis','Actual end turns and leakage','Mesh/outer-boundary confirmation at full length','Full inverter transient/cooling/handoff model'],
        source_sha256=source,getdp_binary_sha256=exe_sha,
        getdp_version=re.search(r'\[GetDP ([^,\]]+)',proc.stdout).group(1) if re.search(r'\[GetDP ([^,\]]+)',proc.stdout) else 'see execution log',
        **{k:v for k,v in FLAGS.items() if k!='physical_accepted'})
    if source_map(root,(PRODUCER,short.PRODUCER))!=source or digest(getdp)!=exe_sha:raise ValueError('Full primary sources changed during execution')
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result))
    m=dict(schema='osr-native-full-primary-package/1',source_sha256=source,files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()},**FLAGS)
    m['manifest_id']=identity(m);(output/'manifest.json').write_bytes(encoded(m));return result


def verify(output,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Full primary receipt differs')
    if any(digest(Path(root)/n)!=h for n,h in m['source_sha256'].items()):raise ValueError('Full primary source differs')
    if {p.relative_to(output).as_posix():digest(p) for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Full primary payload differs')
    if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Full primary result differs')
    if any(r.get(k) is not v or m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Research cannot qualify equipment')
    return dict(verified=True,evaluation_id=r['evaluation_id'],physical_accepted=False)
