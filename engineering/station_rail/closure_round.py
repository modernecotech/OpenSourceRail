"""Publish bounded native follow-up evidence without promoting a physical design.

The raw solver directories are immutable inputs. Compact exports explicitly say
which bulky field files remain local, and cannot masquerade as full raw packages.
"""
from pathlib import Path
import argparse,json,shutil,tempfile
from . import ROOT,FLAGS
from .common import encoded,identity,digest,source_map
from . import evaluation,vehicle,braking,station_motor,long_motor,motor_review,body_frame,body_solid_frame,body_floor_fit
OUTPUT='docs/design-engine/v06-physical-closure'
PRODUCER='engineering/station_rail/closure_round.py'


def summary(record,short,full,coarse,fine,frame,solid,fit):
    v=record['vehicle'];profile=record['service']['selected_scenario']['profile']
    if any(x.get(k) is not val for x in (short,full,coarse,fine,frame,solid,fit) for k,val in FLAGS.items()):raise ValueError('Research evidence must preserve all holds')
    if any(x['candidate_id']!=v['candidate_id'] for x in (coarse,fine,frame)) or any(x['parent_candidate_id']!=v['candidate_id'] for x in (solid,fit)):raise ValueError('Follow-up parent differs')
    cm={(c['load'],c['case']):c for c in coarse['cases']};fm={(c['load'],c['case']):c for c in fine['cases']}
    if cm.keys()!=fm.keys():raise ValueError('Brake refinement scenarios differ')
    brake=[]
    for key,c in fm.items():
        previous=cm[key]
        if c['state']!=previous['state']:raise ValueError('Brake timestep changes outcome')
        brake.append({k:c[k] for k in ('load','case','state','stop_distance_m','failure_reason','adhesion_hypothesis','grade_down_fraction','working_discs_per_car','lumped_disc_temperature_C_hypothesis','energy_residual_J')})
        brake[-1]['timestep_stop_difference_m']=None if c['stop_distance_m'] is None else c['stop_distance_m']-previous['stop_distance_m']
    motor=motor_review.assess(short,full,profile['peak_launch_force_N_per_car'])
    value=dict(schema='osr-v06-native-followup/1',**{k:record[k] for k in evaluation.IDS},
        parent_evaluation_id=record['evaluation_id'],execution='completed',selection_purpose='Diagnose failures and choose next prototype experiments',
        default_geometry_changed=False,complete_station_to_station_journey=False,
        rotors=braking.rotating_stock(v),reference_profile={k:profile[k] for k in ('profile_id','runtime_s','peak_launch_force_N_per_car','launch_mechanical_energy_kWh_train','receiving_mechanical_energy_kWh_train','braking_distance_m')},
        motor=motor,motor_primary_bare_stock_kg_per_m=(full['configuration']['copper_kg']+full['configuration']['steel_kg'])/full['configuration']['primary_length_m'],
        motor_missing=full['missing_confirmation'],brake_cases=brake,brake_native_executions=len(cm)+len(fm),brake_timestep_s=[coarse['cases'][0]['dt_s'],fine['cases'][0]['dt_s']],
        brake_scope=fine['scope'],brake_hardware_qualified=False,
        frame=dict(evaluation_id=frame['evaluation_id'],disposition='Invalid native rotational-MPC frame interface; no design performance may be inferred',
            alternatives=[{k:a[k] for k in ('alternative_id','added_mass_kg','both_roof_chords_connected','supported_member_count','member_count') if k in a} for a in frame['alternatives']]),
        solid_frame=dict(evaluation_id=solid['evaluation_id'],execution=solid['execution'],independent_benchmark=solid['independent_benchmark'],
            refinement=solid['refinement'],cases=solid['cases'],scope=solid['scope'],physical_acceptance='unknown',rejected_previous_formulation=solid.get('rejected_previous_formulation'),next_experiment_stock_options=solid.get('next_experiment_stock_options',[])),
        floor_fit=dict(evaluation_id=fit['evaluation_id'],alternative_id=fit['alternative_id'],net_material_mass_delta_kg=fit['net_material_mass_delta_kg'],
            fit_subset_clash_screen=fit['fit_subset_clash_screen'],CAD=fit['CAD'],whole_vehicle_clearance_screen=fit['whole_vehicle_clearance_screen']),
        maturity=dict(motor=dict(execution='completed',numerical_validity='outside_linear_material_domain; full-length convergence unknown',engineering_screen='fail',evidence_maturity='analytical'),frame=dict(execution='completed',numerical_validity='benchmark and reaction/refinement checked; rigid contact hypotheses',engineering_screen='frame-only stiffness fail; full body unknown',evidence_maturity='verified_simulation'),braking=dict(execution='completed',numerical_validity='valid reduced rolling model with timestep/energy checks',engineering_screen='hardware unknown; degraded stopping failures retained',evidence_maturity='verified_simulation'),floor_fit=dict(execution='completed',numerical_validity='native subset volumes and reopen checked',engineering_screen='subset clearance pass; installed body unknown',evidence_maturity='analytical')),
        gates=dict(motor='fail',frame_only_stiffness='fail',body_structure='unknown',brake_hardware='unknown',physical_journey='held',economics='unknown',city_regeneration='held'),**FLAGS)
    value['followup_id']=identity(value);return value


def readme(s):
    motor=s['motor'];p=s['reference_profile'];fit=s['floor_fit'];normal=[c for c in s['brake_cases'] if c['load']=='normal']
    lines=['# v0.6 native physical follow-up','',
        'OpenSourceRail pursues simple, locally repairable transport with passive wheel bogies and station-powered propulsion. This bounded campaign tests the current six-car comfort reference; it retains failed and numerically invalid results. **No physical train journey, manufacturing release or operating acceptance is established.** The [current design](../current/README.md) remains the reference geometry.','',
        '## What was executed','',
        '| Work | Result | Interpretation |','|---|---|---|',
        '| Station motor | 17 current-excited GetDP cases plus one full 12.5 m primary / 9 m secondary | Real winding geometry; finite 2D height assumption and linear steel remain limitations |',
        f"| Full motor | {motor['force_N_full_geometry_2D']/1000:.3f} kN/car versus {motor['required_force_N_per_car']/1000:.3f} kN required | Force reserve {motor['force_reserve_N']/1000:.3f} kN; tested geometry fails |",
        '| Numerical controls | Zero-current, phase reversal, current-squared and energy balance | Successful method checks do not qualify the motor |',
        '| Peak steel field | 2.240 T versus the declared 1.3 T linear-domain limit | Out of model domain; nonlinear material and further convergence required |',
        '| Braking | 24 actual Chrono executions at 10 ms and 5 ms | Six rigid bodies with pure rolling analytically reduced; no real wheel slide or WSP plant |',
        '| Body | Member connectivity, native beam/solid fixtures and counted floor fit-up | Invalid interfaces remain rejected; no whole-body structural release |','',
        '## Corrected rolling energy and launch requirement','',
        f"Counted wheels, axles and brake discs add **{s['rotors']['equivalent_inertial_mass_kg_per_car']:.3f} kg/car of equivalent rotational inertia**. This changes acceleration, coast and braking energy; it adds no static axle weight. The 2 km normal-load reference is now **{p['runtime_s']:.3f} s**, with **{p['launch_mechanical_energy_kWh_train']:.3f} kWh/train** launch work. These are requirements under declared resistance assumptions, not demonstrated trips.",'',
        '## Station LIM: failed geometry, useful next experiment','',
        f"The full test uses 140 A peak, 50 Hz, 20 m/s and 15 mm gaps at the 80°C conductor hypothesis. It calculates 143.5 kW mechanical output, 52.1 kW secondary heat and 43.6 kW primary copper heat per engaged module. Energy closes in the solver, but steel saturation, finite-height return currents, moving entry/exit, boundary/mesh convergence and repeated thermal duty remain unresolved. Installed available thrust stays **unknown**.",'',
        f"Bare primary copper and steel are **{s['motor_primary_bare_stock_kg_per_m']:.3f} kg/m**, or **{s['motor_primary_bare_stock_kg_per_m']*900/1000:.1f} t per 900 m directional winding**. This excludes supports, insulation, cooling, converters, cables and installation. Station-only propulsion must earn its whole-system cost advantage.",'',
        'All-series winding voltage exceeds a 750 V DC inverter bound. Ten parallel paths would meet only the equal-flux arithmetic voltage bound at about 990 A RMS per phase. Finite overlap creates unequal coil flux; actual branch voltage, current sharing, converters, cable mass and cooling remain unknown. Reconnection does not repair the force deficit or steel-field failure.','',
        f"Short-primary force changes {motor['short_force_refinement_change_fraction']*100:.2f}% on the last refinement, while the peak field changes {motor['short_peak_field_refinement_change_fraction']*100:.1f}%. Doubling primary length changes thrust per metre by {(motor['primary_length_force_per_m_ratio']-1)*100:.1f}%; length extrapolation is therefore not usable as an accepted force map. The tested primary fails; this is not a proof that every LIM design fails.",'',
        'Next compare a larger magnetic cross-section, different slot/turn/connection designs and reduced air-gap only where the real suspension/rail clearance budget permits it. Use nonlinear steel data, independent finite-height confirmation and measured thrust/temperature before selecting a replacement. Lower speed or sparse boosters are explicit service alternatives, with complete journey and cost consequences.','',
        '## Independent braking and authority','',
        'The current brake model uses eight counted discs/car, opposed 100 mm piston hypotheses, 0.6 MPa pressure, pad friction 0.35, one-second response and a 0.4-second pressure-rise constant. These are research inputs, not supplier-qualified brake hardware. An ideal instantaneous adhesion limiter preserves rolling; actual slip/WSP latency and fade remain unknown. Receiving propulsion, aerodynamic drag and rolling resistance receive no emergency braking credit.','',
        '| Normally loaded train, initial 20 m/s | Stop distance | Lumped disc temperature |','|---|---|---|']
    for c in normal:
        distance='Cannot stop' if c['stop_distance_m'] is None else f"{c['stop_distance_m']:.1f} m"
        lines.append(f"| {c['case']} | {distance} | {c['lumped_disc_temperature_C_hypothesis']:.1f}°C hypothesis |")
    lines += ['',
        'Wet/downhill means adhesion 0.05 on a 2% downgrade. The failed-channel case retains four working discs/car and heat capacity from those discs alone. At adhesion 0.03 on a 4% downgrade, gravity prevents stopping in this model. The crowd-load failed-channel run needs over 3 km. Halving the timestep changes stopped-case positions by about 0.05 m; energy balances use trapezoidal velocity work and record the native position integration bias separately.','',
        'A nominal receiving zone is not an independent stopping envelope. Dispatch needs qualified brake curves, earlier fault detection, protected overrun distance or lower route speed, plus recovery and evacuation. A seating/admission policy does not remove crowd and degraded-brake checks. The [HydroAct brochure](https://rail.knorr-bremse.com/media/2000_products/2900d_product_broschures/p-1236_hydroact.pdf) is an RFQ comparator; it does not qualify the model actuator, pressure system, disc or fade curve.','',
        '## Body connections and numerical validity','',
        'The retained upper frame lacks positive-volume connections to the lower chassis. Twenty post-base feet/risers add 66.143 kg of material. Connecting the upper frame requires real floor penetrations, not overlapping stock. The new fit-up subtracts actual skin/core/bond cutouts and counts 72 collar pieces, omitting eight door-adjacent flanges.','',
        f"The resulting proposal adds **{fit['net_material_mass_delta_kg']:.3f} kg/car**, before unknown weld/fastener/seal hardware. Native FreeCAD checks changed stock volumes, reopen and STEP export. The checked subset has **{len(fit['CAD']['positive_volume_clashes'])} positive-volume clashes**; full-car installation, floor-cap strength, joints, fire, fatigue and repair access remain open. The proposed connection is not silently added to the selected vehicle. Frame calculations include 66.143 kg of post connectors; the separate floor-fit alternative adds a further 11.011 kg. They are not one composed installed vehicle or a qualified common structural model.",'',
        'The earlier B32R offset-joint run returned a successful process code but failed force balance and refinement. An independent two-beam fixture exposed the unsupported native rotational interface. Those results are **numerically invalid**, not evidence that the complete car passes or fails. [CalculiX documentation](https://www.dhondt.de/ccx_2.23.pdf) constrains rotational equations on expanded beams; algebraic rigid-motion checks alone were insufficient.','',
        'The corrected replacement meshes actual hollow walls with full-integration C3D20 solids and translational equations only at contact, load and support planes. A reduced-integration solid trial also showed an unphysical local mode in thin connector feet despite balanced reactions. It is rejected. The final full-integration model records separate slender-cantilever, load/reaction and mesh-refinement checks; the beam-only and reduced-integration failures remain independently identified. **The frame-only stiffness screen still fails:** connecting the upper frame improves deflection, but cannot establish adequate stiffness by itself. Actual joins, composite-panel shear contribution, local stress, buckling, fatigue and flexible-body modes remain unqualified. Detailed case values and model domains are retained in the summary.','',
        '## Evidence, storage and reproduction','',
        '[Machine-readable summary](summary.json) · [Source and payload manifest](manifest.json) · [Motor inputs/logs/scalars](motor-short.tar.gz) · [Full motor inputs/logs/scalars](motor-full.tar.gz) · [Braking 10 ms](brakes-10ms.tar.gz) · [Braking 5 ms](brakes-5ms.tar.gz) · [Invalid native frame](frame-invalid.tar.gz) · [Explicit-solid frame](frame-solid.tar.gz) · [Floor fit-up CAD](floor-fit.tar.gz)','',
        'Motor and frame compact archives retain the complete original SHA-256 index, exact model inputs, logs and scalar outputs. Bulky mesh/field files remain in ignored local run directories; remote artifact storage is not configured. A compact archive can verify its retained bytes but cannot replace full raw native verification. Reproduction commands and exact tools are in the retained inputs/logs and source below. No raw evidence was rewritten to make a screen pass.','',
        '```bash','.venv/bin/python -m engineering.station_rail.closure_round --verify',
        '# Reproduce native workers into fresh directories, then publish:',
        '# station_motor.run(...), long_motor.run(...), braking.native_run(...),',
        '# body_solid_frame.run(...), body_floor_fit.run(...)',
        '# Chrono workers require build/trip-dynamics/environment/chrono/bin/python',
        '.venv/bin/python -m engineering.station_rail.closure_round --publish','```','',
        'All 266 city maps/geographies are preserved. City performance regeneration, equal-service economics and the physically coupled launch–coast–arrival demonstration remain held. v0.5 evidence and v0.6.0 tag remain unchanged.','']
    body_lines=['| Full-integration frame-only case | Maximum vertical displacement | Screen versus 25.6 mm |','|---|---|---|']
    for case in s['solid_frame']['cases']:
        if case['case'] in ('normal-fine','empty','crowd','asymmetric-braking'):
            body_lines.append(f"| {case['variant']} / {case['case']} | {1000*case['maximum_vertical_displacement_m']:.2f} mm | {case['necessary_deflection_screen']} |")
    at=lines.index('## Evidence, storage and reproduction');lines[at:at]=body_lines+['', 'Deeper side-sill alternatives are counted in the summary as next experiments. They add material and change underside clearance; none has a passed structural/swept-clearance screen or is adopted. A participating composite shell is another explicit stiffness alternative requiring its own load-transfer model.','']
    return '\n'.join(lines)


def publish(root=ROOT,runs=None,solid_name='body-solid-r4',fit_name='body-floor-fit-r2'):
    from . import closure_artifacts
    root=Path(root);runs=root/'build/v06-closure-round' if runs is None else Path(runs);v=vehicle.build(root);record=evaluation.build(root)
    paths=dict(short=runs/'motor-native',full=runs/'full-motor-native',coarse=runs/'brakes-native-10ms-r2',fine=runs/'brakes-native-5ms',frame=runs/'body-native-r2',solid=runs/solid_name,fit=runs/fit_name)
    station_motor.verify(paths['short'],root);long_motor.verify(paths['full'],root)
    braking.verify(paths['coarse'],v,root);braking.verify(paths['fine'],v,root);body_frame.verify(paths['frame'],v,root)
    body_solid_frame.verify(paths['solid'],v,root);body_floor_fit.verify(paths['fit'],v,root)
    raws={key:json.loads((p/'result.json').read_bytes()) for key,p in paths.items()};s=summary(record,**raws)
    target=root/OUTPUT;target.parent.mkdir(parents=True,exist_ok=True)
    out=Path(tempfile.mkdtemp(prefix='v06-followup-',dir=root/'build/v06-closure-round'))
    (out/'summary.json').write_bytes(encoded(s));(out/'README.md').write_text(readme(s))
    names=dict(short='motor-short',full='motor-full',coarse='brakes-10ms',fine='brakes-5ms',frame='frame-invalid',solid='frame-solid',fit='floor-fit')
    archive_records={}
    for key,path in paths.items():
        name=names[key]+'.tar.gz'
        compact=closure_artifacts.export(path,out/name,include_all=key in ('coarse','fine','fit'),root=root)
        archive_records[key]=dict(archive_name=name,compact_manifest_id=compact['compact_manifest_id'],archive_sha256=digest(out/name),retained_raw_payload_complete=compact['retained_raw_payload_complete'])
    sources={PRODUCER:digest(root/PRODUCER),**record['source_sha256']}
    for raw in raws.values():
        for name,h in raw['source_sha256'].items():
            if name in sources and sources[name]!=h:raise ValueError('Mixed source definitions')
            sources[name]=h
    sources.update(source_map(root,('engineering/station_rail/motor_review.py','engineering/station_rail/closure_artifacts.py')))
    manifest=dict(schema='osr-v06-followup-publication/1',source_sha256=sources,parent_candidate_id=v['candidate_id'],followup_id=s['followup_id'],
        archives=archive_records,files_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'},**FLAGS)
    manifest['manifest_id']=identity(manifest);(out/'manifest.json').write_bytes(encoded(manifest))
    if target.exists():
        previous=root/'build/v06-closure-round/replaced-publications'/digest(target/'manifest.json');previous.parent.mkdir(parents=True,exist_ok=True)
        if previous.exists():shutil.rmtree(target)
        else:shutil.move(target,previous)
    shutil.move(out,target);return verify(root)


def verify(root=ROOT):
    from . import closure_artifacts
    root=Path(root);out=root/OUTPUT;m=json.loads((out/'manifest.json').read_bytes());s=json.loads((out/'summary.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}) or s['followup_id']!=identity({k:v for k,v in s.items() if k!='followup_id'}):raise ValueError('Follow-up identities differ')
    if {p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Follow-up payload differs')
    for name,h in m['source_sha256'].items():
        if digest(root/name)!=h:raise ValueError('Follow-up source differs: '+name)
    record=evaluation.build(root)
    if s['parent_evaluation_id']!=record['evaluation_id'] or any(s[k]!=record[k] for k in evaluation.IDS):raise ValueError('Follow-up parent differs')
    for name,metadata in m['archives'].items():
        result=closure_artifacts.verify(out/metadata['archive_name'],root=root)
        if result['compact_manifest_id']!=metadata['compact_manifest_id']:raise ValueError('Compact identity differs')
    if any(x.get(k) is not val for x in (s,m) for k,val in FLAGS.items()) or s['complete_station_to_station_journey'] is not False:raise ValueError('Follow-up cannot release a train')
    return dict(verified=True,followup_id=s['followup_id'],native_motor_cases=18,native_brake_executions=24,physical_journey_completed=False,**FLAGS)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');p.add_argument('--verify',action='store_true');p.add_argument('--solid-name',default='body-solid-r4');p.add_argument('--fit-name',default='body-floor-fit-r2');a=p.parse_args()
    print(json.dumps(publish(solid_name=a.solid_name,fit_name=a.fit_name) if a.publish else verify(),indent=2))
