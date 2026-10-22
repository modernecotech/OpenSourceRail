"""Exact drilled-stock alternatives on the existing full-mass rigid-car plant.

The source sandwich-body study stays primary. These two-spine material
alternatives do not replace it or establish joined-body/manufacturing acceptance.
"""
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import gzip
import io
import json
import math
import time
import tomllib

import scipy
from scipy.integrate import quad

from . import assembled_body,closure,geometry,model,moving_train,station
from engineering.factory_examples import models

ROOT=model.ROOT
INPUT=Path(__file__).with_name('body-stiffness.toml')
STAGED=Path(__file__).resolve().is_relative_to(ROOT/'build')
TEST=Path(__file__).with_name('test_body_stiffness.py') if STAGED else ROOT/'engineering/analysis/tests/test_ferrite_maglev_body_stiffness.py'
OUTPUT=ROOT/'build/steel-stringer-repair' if STAGED else ROOT/'docs/design-engine/ferrite-maglev/body-stiffness'
SCHEMA='osr-body-stiffness-study/1'
RUN_NAMES=('gfrp-control','steel-wall-003','steel-wall-004','steel-wall-005','steel-wall-006')
FILES={'study.json.gz','execution.json.gz','overview.svg','README.md',*(name+'.json.gz' for name in RUN_NAMES)}
MAX_FILE=32*1024*1024
MAX_RAW=128*1024*1024
COMPARISON_KEYS=('minimum_gap_m','maximum_gap_m','peak_coupler_force_n','peak_coupler_extension_m',
    'maximum_magnetic_phase_spread_degrees','maximum_longitudinal_relative_spread_m',
    'peak_module_force_n','peak_beam_displacement_m','completed_moving_steps','planned_moving_steps')
METRIC_EXCLUDE={'trace','trajectory','assumptions','coupler_step_witness'}


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(value):return sha256(value).hexdigest()


def source_paths():
    return sorted({Path(__file__),INPUT,TEST,*assembled_body.source_paths(),*(ROOT/name for name in moving_train.sources())})


def sources():return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in source_paths()}


def load():
    a=tomllib.loads(INPUT.read_text())
    if a.get('schema')!='osr-body-stiffness-assumptions/1' or a.get('steel_wall_m')!=[.003,.004,.005,.006]:raise ValueError('bounded four-wall stock family required')
    if any(a.get(k) is not False for k in ('material_properties_qualified','joined_body_accepted','automatic_adoption')):raise ValueError('unqualified stock alternatives required')
    if (a.get('phase_screen_degrees')!=5. or a.get('steel_young_pa')!=200e9 or a.get('steel_density_kg_m3')!=7850.
        or a.get('reference_car_mass_kg')!=moving_train.load()['car_mass_kg']
        or a.get('maximum_candidate_car_mass_kg')!=27000.
        or type(a.get('workers')) is not int or not 1<=a['workers']<=2):raise ValueError('source-bound mass, material and unchanged confirmation assumptions required')
    return a


def _stock(value):
    parts={p['id']:p for p in value['parts']};members=[]
    for side in (-1,1):
        member=next(m for m in value['members'] if m['id']==f'frame/lower-stringer-{side}')
        if member['axis']!=0 or member['size_m']!=[17.,.14,.22] or member['material']!='gfrp' or member['wall_m']!=.012:raise ValueError('exact current GFRP longitudinal stock required')
        walls=[parts[key] for key in member['part_ids']];drilled=[p for p in walls if p.get('holes')]
        if len(walls)!=4 or len(drilled)!=2:raise ValueError('four disjoint walls and two drilled y walls required')
        sets=[]
        for wall in drilled:
            if any(h['axis']!='y' or h['diameter_m']!=.013 for h in wall['holes']):raise ValueError('exact current through-hole grid required')
            sets.append(sorted([round(wall['at_m'][0]+h['x_m'],12),round(wall['at_m'][2]+h['z_m'],12),h['diameter_m']] for h in wall['holes']))
        if sets[0]!=sets[1] or len(sets[0])!=192 or len({tuple(h) for h in sets[0]})!=192:raise ValueError('two matching actual wall-hole grids required')
        by_x={}
        for x,z,d in sets[0]:by_x.setdefault(x,[]).append((z,d))
        xs=sorted(by_x)
        if len(xs)!=96 or any(len(v)!=2 for v in by_x.values()) or min(y-x for x,y in zip(xs,xs[1:]))<=.013:raise ValueError('96 nonoverlapping two-row axial sites required')
        members.append(dict(member=deepcopy(member),walls=deepcopy(walls),hole_axes=sets[0],x_sites_m=xs))
    spacers=[deepcopy(p) for p in value['parts'] if p['id'].endswith('/crush-spacer')]
    if len(spacers)!=384 or any(p['kind']!='cylinder' or p['material']!='steel' or p['cylinder_axis']!='y' or p['size_m']!=[.025,.025,.116] for p in spacers):raise ValueError('384 exact current crush spacers required')
    return members,spacers


def axial_properties(wall_m,young_pa,members):
    """Independent endpoint-aware quadrature of the actual cut section EA(x)."""
    if not 0<wall_m<.07 or not math.isfinite(young_pa) or young_pa<=0:raise ValueError('positive tube wall and modulus required')
    area=.14*.22-(.14-2*wall_m)*(.22-2*wall_m);radius=.013/2
    # At each source-derived x-site two z rows pierce both y walls. Their
    # circular chords remove material; no shell or unlocated strap is credited.
    minimum=area-2*wall_m*2*(2*radius)
    if minimum<=0:raise ValueError('positive drilled axial net area required')
    section=lambda x:area-2*wall_m*2*2*math.sqrt(max(0.,radius*radius-x*x))
    integral,error=quad(lambda x:1/section(x),-radius,radius,epsabs=1e-11,epsrel=2e-12,limit=200)
    transformed,error2=quad(lambda theta:radius*math.cos(theta)/section(radius*math.sin(theta)),-math.pi/2,math.pi/2,epsabs=1e-11,epsrel=2e-12,limit=200)
    if not math.isclose(integral,transformed,rel_tol=1e-11,abs_tol=1e-11):raise ValueError('independent hole quadratures disagree')
    compliances=[((m['member']['size_m'][0]-len(m['x_sites_m'])*2*radius)/area+len(m['x_sites_m'])*integral)/young_pa for m in members]
    stiffness=sum(1/v for v in compliances);joint=closure.load()['coupler']['target_stiffness_n_m']
    return dict(gross_area_m2=area,minimum_drilled_area_m2=minimum,young_pa=young_pa,
        single_site_inverse_area_integral_per_m=integral,transformed_integral_per_m=transformed,
        absolute_quadrature_error_per_m=max(error,error2),member_compliance_m_n=compliances,
        body_axial_stiffness_n_m=stiffness,body_axial_compliance_m_n=1/stiffness,
        unchanged_coupler_stiffness_n_m=joint,body_and_coupler_series_stiffness_n_m=1/(1/stiffness+1/joint),
        model='Two exact drilled tubes in parallel; one full-car-length axial path in series with existing coupler. Uniform axial load sharing and modulus are unqualified. No shell, connection or free stiffness credit.')


def geometry_variant(members,spacers,wall_m,material,density):
    regions=[];tube_formula=0.;hole_volume=0.
    for item in members:
        m=item['member'];holes=[dict(axis='y',centre_m=[x,m['at_m'][1]+m['size_m'][1]/2,z],diameter_m=d) for x,z,d in item['hole_axes']]
        regions.extend(assembled_body.tube_regions(m['id'],m['size_m'],m['at_m'],m['axis'],wall_m,material,'provisional-replaced-stringers',holes=holes))
        removed=2*wall_m*sum(math.pi*d*d/4 for _,_,d in item['hole_axes']);hole_volume+=removed
        tube_formula+=m['size_m'][0]*(.14*.22-(.14-2*wall_m)*(.22-2*wall_m))-removed
    tube_volume=sum(models.volume(p) for p in regions)
    if not math.isclose(tube_volume,tube_formula,rel_tol=1e-12,abs_tol=1e-12):raise ValueError('drilled material-region and independent tube volumes disagree')
    new_spacers=deepcopy(spacers);clear=.14-2*wall_m
    for p in new_spacers:
        centre=p['at_m'][1]+p['size_m'][2]/2;p['at_m'][1]=centre-clear/2;p['size_m'][2]=clear
        for h in p['holes']:h['length_m']=clear
        for old in ('volume_m3','density_assumption_kg_m3','production_released','revision'):p.pop(old,None)
    spacer_volume=sum(models.volume(p) for p in new_spacers)
    expected_spacer=len(new_spacers)*math.pi*(.025**2-.013**2)/4*clear
    if not math.isclose(spacer_volume,expected_spacer,rel_tol=1e-12,abs_tol=1e-12):raise ValueError('spacer volume does not equal actual annular stock')
    return dict(tube_regions=regions,crush_spacers=new_spacers,tube_count=2,spacer_count=len(spacers),
        wall_m=wall_m,material=material,assumed_density_kg_m3=density,
        tube_volume_m3=tube_volume,removed_hole_volume_m3=hole_volume,tube_mass_kg=tube_volume*density,
        spacer_length_m=clear,spacer_volume_m3=spacer_volume,spacer_mass_kg=spacer_volume*7850.,
        stock_and_spacer_mass_kg=tube_volume*density+spacer_volume*7850.,
        outer_envelope_unchanged=True,external_bolt_stack_unchanged=True,
        inner_spacer_endpoints_updated=True,native_export_executed=False)


def derivation():
    a=load();definition=assembled_body.definition();members,spacers=_stock(definition)
    current=closure.load();gfrp_e=current['materials']['gfrp_longitudinal_e_pa'];gfrp_rho=geometry.MATERIALS['gfrp']
    control_geometry=geometry_variant(members,spacers,.012,'gfrp',gfrp_rho)
    original_volume=sum(models.volume(p) for m in members for p in m['walls'])
    original_spacer=sum(models.volume(p) for p in spacers)
    if not math.isclose(original_volume,control_geometry['tube_volume_m3'],rel_tol=1e-12) or not math.isclose(original_spacer,control_geometry['spacer_volume_m3'],rel_tol=1e-12):raise ValueError('current GFRP/spacer material control failed')
    independent=axial_properties(.012,gfrp_e,members);prior=assembled_body.axial_screen()
    if not math.isclose(independent['body_and_coupler_series_stiffness_n_m'],prior['drilled_body_and_coupler_series_stiffness_n_m'],rel_tol=1e-6):raise ValueError('current independent axial control differs')
    variants=[]
    hardpoint_target=assembled_body.load()['hardpoint']['maximum_gross_car_mass_kg'];hardpoint=assembled_body.hardpoint_screen()
    for index,(name,wall,material,E,rho) in enumerate([
        ('gfrp-control',.012,'gfrp',gfrp_e,gfrp_rho),
        *((f'steel-wall-{round(t*1000):03d}',t,'steel',a['steel_young_pa'],a['steel_density_kg_m3']) for t in a['steel_wall_m'])]):
        stock=geometry_variant(members,spacers,wall,material,rho);axial=axial_properties(wall,E,members)
        delta=stock['stock_and_spacer_mass_kg']-control_geometry['stock_and_spacer_mass_kg'];mass=a['reference_car_mass_kg']+delta
        if delta<0 or mass>a['maximum_candidate_car_mass_kg']:raise ValueError('no negative/unbounded mass credit allowed')
        # The control uses exactly the previously retained Simpson-derived plant
        # coefficient; the independent quadrature quantifies its tiny error.
        coefficient=prior['drilled_body_and_coupler_series_stiffness_n_m'] if index==0 else axial['body_and_coupler_series_stiffness_n_m']
        variants.append(dict(id='OSR-STOCK-'+name.upper()+'-1',name=name,material_id=('GFRP-20GPa-1900-unqualified' if index==0 else 'STEEL-200GPa-7850-unqualified'),
            stock=stock,axial=axial,lumped_stiffness_used_n_m=coefficient,
            directly_replaced_control_mass_kg=control_geometry['stock_and_spacer_mass_kg'],
            incremental_stock_and_spacer_mass_kg=delta,full_aw3_car_mass_kg=mass,full_train_mass_kg=6*mass,
            existing_hardpoint_mass_target_kg=hardpoint_target,within_existing_hardpoint_mass_target=mass<=hardpoint_target,
            mass_ratio_to_existing_hardpoint_target=mass/hardpoint_target,
            existing_load_path_scaling=dict(reference_mass_kg=hardpoint_target,ratio=mass/hardpoint_target,
                maximum_interface_force_n=hardpoint['maximum_interface_force_n']*mass/hardpoint_target,
                shear_per_bolt_n=hardpoint['shear_per_bolt_n']*mass/hardpoint_target,
                tension_per_bolt_n=hardpoint['tension_per_bolt_n']*mass/hardpoint_target,
                calculation_only=True,thin_wall_joint_assessed=False,whole_joint_acceptance=False),
            material_properties_qualified=False,joined_body_accepted=False,automatic_adoption=False))
    return dict(schema='osr-drilled-longitudinal-stock-derivation/1',assumptions=a,
        original_definition_revision=definition['revision'],source_member_ids=[m['member']['id'] for m in members],
        member_geometry=members,source_crush_spacers=spacers,actual_bolt_axes=384,actual_wall_penetrations=768,
        x_sites_per_member=96,rows_per_site=2,gfrp_independent_axial=independent,gfrp_existing_axial=prior,
        current_gfrp_tube_mass_kg=control_geometry['tube_mass_kg'],current_spacer_mass_kg=control_geometry['spacer_mass_kg'],
        variants=variants,stock_controls_pass=True,**model.FLAGS)


def candidate(variant):
    a=dict(moving_train.candidate_assumptions(moving_train.load())[0])
    a.update(car_mass_kg=variant['full_aw3_car_mass_kg'],coupler_stiffness_n_m=variant['lumped_stiffness_used_n_m'])
    return a


def run_with_witness(executable,assumptions):
    """Run the unchanged chain with actual per-step midpoint-speed retention.

    The temporary subclass exists only in this worker process and delegates
    every state transition to the existing implementation. The original class
    is restored even if simulation fails. No plant force or criterion changes.
    """
    base=moving_train.CouplerChain;values=[]
    class RecordedChain(base):
        def step(self,external_relative_n):
            before=self.velocity.copy();result=super().step(external_relative_n)
            mid=(before+self.velocity)/2;values.append((mid[:-1]-mid[1:]).tolist())
            return result
    try:
        moving_train.CouplerChain=RecordedChain
        run=moving_train.simulate(Path(executable),assumptions=assumptions)
    finally:moving_train.CouplerChain=base
    run['coupler_step_witness']=dict(schema='osr-coupler-midpoint-witness/1',step_s=assumptions['step_s'],
        midpoint_relative_velocity_m_s=values,
        scope='Actual per-step relative midpoint speeds retained from the unchanged CouplerChain state transition; kinematic, constitutive-force and damping consistency only')
    return run


def _execute(value):
    executable,variant=value;started=time.monotonic();a=candidate(variant);run=run_with_witness(Path(executable),a)
    return run,dict(id=variant['id'],elapsed_wall_s=time.monotonic()-started,candidate_sha256=run['candidate_sha256'],
        controller_command=[str(executable),str(a['car_mass_kg']),str(round(a['step_s']*1e9)),str(a['gap_target_m']),str(a['gap_minimum_m']),str(a['gap_maximum_m'])],
        completed_moving_steps=run['completed_moving_steps'],planned_moving_steps=run['planned_moving_steps'])


def _holds():return [
    'Structurally participating GFRP sandwich remains the leading body study. Steel spines are an explicit alternative, not a hidden conventional complete underframe or adopted architecture.',
    'Full joined-body skin/frame participation, torsion, bending, buckling, fatigue and coupler/hardpoint compliance remain unqualified; this is a rigid-car lumped axial sensitivity.',
    'Thin steel wall bearing/pull-through, crushing, weld heat/distortion, tube splices, local buckling, corrosion, thermal expansion/magnetic interaction and dissimilar-material interfaces require independent design and tests.',
    'E=200GPa, density=7850kg/m3, GFRP properties and coupler100MN/m are assumptions. Actual supply, local fabrication, steel grade, dimensional tolerances, weld procedure and inspectability remain unverified.',
    'Full AW3 reference mass plus every added directly replaced tube/spacer kg is retained; equipment, payload and contingency reserves receive no removal credit. Baseline assumed roll/pitch inertias and ideal independently allocated thrust are unchanged.',
    'The existing hardpoint load hypothesis is26400kg/car. Alternatives above it need heavier-load re-evaluation as well as the new steel-wall joint design; a phase-screen pass does not close this gate.',
    'The 5 degree magnetic phase screen, physical gap/stroke/force controllers and numerical controls are unchanged. Passing them is not shared-field electromagnetic feasibility, a flexible-body confirmation, manufacturing or physical acceptance.']


def _summary(deriv,runs):
    return dict(schema=SCHEMA,derivation=deriv,
        cases=[dict(id=v['id'],name=v['name'],material_id=v['material_id'],candidate_sha256=r['candidate_sha256'],
            incremental_stock_and_spacer_mass_kg=v['incremental_stock_and_spacer_mass_kg'],full_aw3_car_mass_kg=v['full_aw3_car_mass_kg'],
            existing_hardpoint_mass_target_kg=v['existing_hardpoint_mass_target_kg'],within_existing_hardpoint_mass_target=v['within_existing_hardpoint_mass_target'],
            existing_load_path_scaling=v['existing_load_path_scaling'],
            full_train_mass_kg=v['full_train_mass_kg'],lumped_stiffness_n_m=v['lumped_stiffness_used_n_m'],
            metrics={k:r[k] for k in COMPARISON_KEYS},longitudinal_energy=r['longitudinal_energy'],
            gap_and_stroke_screen_pass=r['study_pass'],confirmation_screen_pass=moving_train.confirmation_eligible(r),
            raw_file=v['name']+'.json.gz',trace_rows=len(r['trace'])) for v,r in zip(deriv['variants'],runs)],
        phase_screen_passing_alternative_ids=[v['id'] for v,r in zip(deriv['variants'][1:],runs[1:]) if moving_train.confirmation_eligible(r)],
        selected_candidate_id=None,automatic_adoption=False,city_default_changed=False,study_pass=False,
        joined_body_accepted=False,physical_output_authorised=False,open_gates=_holds(),**model.FLAGS)


def study():
    before=sources();deriv=derivation();binary,build=moving_train.build_bridge();binary_hash=build['binary_sha256']
    with ProcessPoolExecutor(max_workers=load()['workers']) as pool:
        results=list(pool.map(_execute,[(str(binary),v) for v in deriv['variants']]))
    if sources()!=before or digest(binary.read_bytes())!=binary_hash:raise ValueError('body stiffness sources/binary changed during execution')
    runs=[v[0] for v in results];value=_summary(deriv,runs)
    value.update(source_sha256=before,source_unchanged_after_execution=True)
    execution=dict(schema='osr-body-stiffness-execution/1',build=build,executable=str(binary),python_scipy=scipy.__version__,
        runs=[v[1] for v in results],scope='Actual Rust controller bridge in each complete fresh moving six-car run; no native export or physical IO')
    return value,execution,runs


def readme(value):
    rows=['# Drilled longitudinal stock alternatives','',
        'Provisional rigid-car full-AW3 sensitivity. The existing GFRP sandwich remains the leading structural-body study. These two-spine alternatives are not adopted.','',
        '| Case | Added kg/car | Full kg/car | Series MN/m | Phase degrees | 5 degree screen |',
        '|---|---:|---:|---:|---:|---|']
    for c in value['cases']:rows.append(f"| {c['name']} | {c['incremental_stock_and_spacer_mass_kg']:.3f} | {c['full_aw3_car_mass_kg']:.3f} | {c['lumped_stiffness_n_m']/1e6:.6f} | {c['metrics']['maximum_magnetic_phase_spread_degrees']:.6f} | {'pass' if c['confirmation_screen_pass'] else 'hold'} |")
    rows+=['','[Exact source/stock derivation and metrics](study.json.gz) · [Compiler/run receipt](execution.json.gz) · [Overview](overview.svg) · [Checksums](manifest.json)','',
        'Each case retains its complete raw trace in the correspondingly named JSON.gz file. Two 17m tubes with a140×220mm envelope,384 bolt axes/768 wall cuts and384 length-corrected crush spacers are accounted for. Only directly replaced counted tube/spacer material is credited; all resulting mass increases are added to the full26200kg/car baseline.','',
        *[paragraph+'\n' for paragraph in value['open_gates']],
        'No city default, equipped-body mass, plant stiffness, manufacturing release or physical output is authorised.','']
    return '\n'.join(rows).encode()


def overview(value):
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="430" viewBox="0 0 1000 430"><rect width="1000" height="430" fill="#101827"/><g font-family="sans-serif" fill="#eff5ff"><text x="30" y="35" font-size="22">Full-mass drilled-stock sensitivity · unchanged 5 degree screen</text><text x="30" y="64" font-size="14">Rigid cars; material and joined-body acceptance open. No automatic adoption.</text>']
    scale=650/15
    for i,c in enumerate(value['cases']):
        y=100+i*57;phase=c['metrics']['maximum_magnetic_phase_spread_degrees'];colour='#38b89a' if c['confirmation_screen_pass'] else '#f29c65'
        parts.append(f'<text x="30" y="{y+19}" font-size="15">{c["name"]}</text><rect x="205" y="{y}" width="{phase*scale:.5f}" height="27" fill="{colour}"/><text x="{220+phase*scale:.5f}" y="{y+19}" font-size="14">{phase:.3f}deg; +{c["incremental_stock_and_spacer_mass_kg"]:.1f}kg/car</text>')
    parts.append(f'<path d="M{205+5*scale} 84 V391" stroke="#ffffff" stroke-dasharray="6 5"/><text x="30" y="414" font-size="13">Raw source-bound traces and exact material accounting accompany this study.</text></g></svg>')
    return ''.join(parts).encode()


def publish(output=OUTPUT):
    value,execution,runs=study();payload={'study.json.gz':gzip.compress(encoded(value),mtime=0),'execution.json.gz':gzip.compress(encoded(execution),mtime=0),'README.md':readme(value),'overview.svg':overview(value)}
    for name,run in zip(RUN_NAMES,runs):payload[name+'.json.gz']=gzip.compress(encoded(run),mtime=0)
    output=Path(output)
    if output.is_symlink():raise ValueError('ordinary body-stiffness output required')
    output.mkdir(parents=True,exist_ok=True)
    if {p.name for p in output.iterdir()}-FILES-{'manifest.json'} or any(p.is_symlink() for p in output.iterdir()):raise ValueError('body-stiffness output inventory differs')
    for name,data in payload.items():
        if len(data)>MAX_FILE:raise ValueError('bounded body-stiffness payload required')
        pending=output/(name+'.pending');pending.write_bytes(data);pending.replace(output/name)
    manifest=dict(schema='osr-body-stiffness-publication/1',source_sha256=value['source_sha256'],files_sha256={n:digest(v) for n,v in payload.items()},automatic_adoption=False,city_default_changed=False,joined_body_accepted=False,study_pass=False,**model.FLAGS)
    pending=output/'manifest.json.pending';pending.write_bytes(encoded(manifest));pending.replace(output/'manifest.json')
    return verify(output)


def _read(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_FILE:raise ValueError('bounded ordinary stock evidence required')
    return path.read_bytes()


def inflate(raw):
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as f:value=f.read(MAX_RAW+1)
    if len(value)>MAX_RAW:raise ValueError('bounded inflated stock evidence required')
    return json.loads(value)


def validate_trace_and_energy(run,a):
    """Bind retained claims to complete sampled state and its energy ledger."""
    trace=run.get('trace',[]);planned=round(a['runtime_s']/a['step_s']);completed=run['completed_moving_steps'];stride=max(1,round(a['trace_interval_s']/a['step_s']))
    if type(completed) is not int or not 0<completed<=planned:raise ValueError('bounded completed stock frames required')
    indices=list(range(0,completed,stride))
    if completed==planned and indices[-1]!=completed-1:indices.append(completed-1)
    if len(trace)!=len(indices):raise ValueError('stock trace cadence/count differs')
    def finite(value):
        if isinstance(value,dict):return all(finite(v) for v in value.values())
        if isinstance(value,list):return all(finite(v) for v in value)
        return not isinstance(value,float) or math.isfinite(value)
    if not finite(run):raise ValueError('finite stock numerical evidence required')
    wavelength=2*station.load()['vehicle']['pole_pitch_m'];phase=0.;stroke=0.
    offsets=[-a['body_length_m']/2-i*(a['body_length_m']+a['coupling_gap_m']) for i in range(6)]
    previous_x=offsets;previous_v=[0.]*6;previous_t=0.;sampled_drag=sampled_damping=0.
    resistance=run['trajectory']['resistance'];constant=resistance['constant_n_per_car'];quadratic=resistance['quadratic_n_per_car_per_m_s_squared']
    for row,index in zip(trace,indices):
        if not math.isclose(row['time_s'],(index+1)*a['step_s'],rel_tol=0.,abs_tol=1e-10):raise ValueError('stock trace timestamp differs')
        if any(len(row[k])!=n for k,n in [('car_centres_m',6),('car_relative_longitudinal_m',6),('car_velocity_m_s',6),('body_down_roll_pitch',6),('coupler_extension_m',5)]):raise ValueError('stock six-car trace shape differs')
        if any(len(v)!=3 for v in row['body_down_roll_pitch']):raise ValueError('stock rigid-car pose shape differs')
        relative=row['car_relative_longitudinal_m']
        if any(not math.isclose(row['coupler_extension_m'][i],relative[i]-relative[i+1],rel_tol=0.,abs_tol=1e-12) for i in range(5)):raise ValueError('stock trace coupler geometry differs')
        if any(not math.isclose(row['car_centres_m'][i],row['front_reference_m']+offsets[i]+relative[i],rel_tol=0.,abs_tol=1e-9) for i in range(6)):raise ValueError('stock trace train geometry differs')
        phase=max(phase,(max(relative)-min(relative))*360/wavelength);stroke=max(stroke,max(map(abs,row['coupler_extension_m'])))
        xs=row['car_centres_m'];vs=row['car_velocity_m_s'];time_s=row['time_s']
        sampled_drag+=math.fsum((2*constant+quadratic*(max(0.,previous_v[i])**2+max(0.,vs[i])**2))/2*(xs[i]-previous_x[i]) for i in range(6))
        sampled_damping+=a['coupler_damping_n_s_m']*(time_s-previous_t)/2*math.fsum((previous_v[i]-previous_v[i+1])**2+(vs[i]-vs[i+1])**2 for i in range(5))
        previous_x=xs;previous_v=vs;previous_t=time_s
    if run['maximum_magnetic_phase_spread_degrees']+1e-10<phase or run['peak_coupler_extension_m']+1e-12<stroke or run['minimum_gap_m']>min(r['minimum_gap_m'] for r in trace)+1e-12 or run['maximum_gap_m']<max(r['maximum_gap_m'] for r in trace)-1e-12:raise ValueError('stock raw extrema contradict trace')
    if not math.isclose(run['maximum_longitudinal_relative_spread_m'],run['maximum_magnetic_phase_spread_degrees']*wavelength/360,rel_tol=1e-12,abs_tol=1e-12):raise ValueError('stock phase/spread conversion differs')
    e=run['longitudinal_energy'];residual=e['kinetic_change_j']+e['final_spring_energy_j']-e['motor_signed_work_j']+e['drag_work_j']+e['coupler_damping_work_j']
    relative=abs(residual)/max(1.,abs(e['motor_signed_work_j']),abs(e['drag_work_j']))
    if not math.isclose(e['residual_j'],residual,rel_tol=1e-10,abs_tol=1e-8) or not math.isclose(e['relative_residual'],relative,rel_tol=1e-10,abs_tol=1e-14):raise ValueError('stock energy ledger differs')
    spring=.5*a['coupler_stiffness_n_m']*math.fsum(v*v for v in trace[-1]['coupler_extension_m'])
    kinetic=.5*a['car_mass_kg']*math.fsum(v*v for v in trace[-1]['car_velocity_m_s'])
    if not math.isclose(e['final_spring_energy_j'],spring,rel_tol=1e-9,abs_tol=1e-8) or not math.isclose(e['kinetic_change_j'],kinetic,rel_tol=1e-9,abs_tol=1e-8):raise ValueError('stock endpoint energy contradicts trace')
    # These are coarse retained-sample consistency checks, not a replacement
    # for the unchanged1e-5 integration-energy confirmation criterion. The
    # sampled states independently expose impossible zero/fabricated work.
    if abs(e['drag_work_j']-sampled_drag)>max(1.,abs(sampled_drag)*1e-4) or abs(e['coupler_damping_work_j']-sampled_damping)>max(.05,abs(sampled_damping)*.05):raise ValueError('stock sampled energy contradicts trace')
    witness=run.get('coupler_step_witness',{})
    if witness.get('schema')!='osr-coupler-midpoint-witness/1' or witness.get('step_s')!=a['step_s']:raise ValueError('actual midpoint coupler witness required')
    frames=witness.get('midpoint_relative_velocity_m_s',[])
    if len(frames)!=completed:raise ValueError('complete midpoint coupler witness required')
    ext=[0.]*5;relative_v=[0.]*5;maximum_force=maximum_stroke=maximum_phase=damping=0.;retained=dict(zip(indices,trace));dt=a['step_s']
    for index,mid in enumerate(frames):
        if not isinstance(mid,list) or len(mid)!=5 or any(type(v) not in (int,float) or not math.isfinite(v) for v in mid):raise ValueError('finite five-coupler midpoint state required')
        new_ext=[ext[i]+dt*mid[i] for i in range(5)];new_v=[2*mid[i]-relative_v[i] for i in range(5)]
        maximum_force=max(maximum_force,max(abs(a['coupler_stiffness_n_m']*(ext[i]+new_ext[i])/2+a['coupler_damping_n_s_m']*mid[i]) for i in range(5)))
        maximum_stroke=max(maximum_stroke,max(map(abs,new_ext)))
        relative_positions=[0.]
        for extension in new_ext:relative_positions.append(relative_positions[-1]-extension)
        maximum_phase=max(maximum_phase,(max(relative_positions)-min(relative_positions))*360/wavelength)
        damping+=a['coupler_damping_n_s_m']*math.fsum(v*v for v in mid)*dt
        if index in retained:
            row=retained[index]
            if any(not math.isclose(new_ext[i],row['coupler_extension_m'][i],rel_tol=0.,abs_tol=1e-10) or not math.isclose(new_v[i],row['car_velocity_m_s'][i]-row['car_velocity_m_s'][i+1],rel_tol=0.,abs_tol=1e-8) for i in range(5)):raise ValueError('midpoint witness contradicts retained end state')
        ext=new_ext;relative_v=new_v
    if not math.isclose(run['peak_coupler_force_n'],maximum_force,rel_tol=1e-10,abs_tol=1e-5) or not math.isclose(run['peak_coupler_extension_m'],maximum_stroke,rel_tol=1e-10,abs_tol=1e-10) or not math.isclose(run['maximum_magnetic_phase_spread_degrees'],maximum_phase,rel_tol=1e-10,abs_tol=1e-8):raise ValueError('midpoint force/extension/phase extrema differ')
    if not math.isclose(e['coupler_damping_work_j'],damping,rel_tol=1e-10,abs_tol=1e-8):raise ValueError('midpoint damping work differs')


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:raise ValueError('exact stock packet inventory required')
    manifest=json.loads(_read(output/'manifest.json'));payload={name:_read(output/name) for name in FILES}
    if manifest.get('schema')!='osr-body-stiffness-publication/1' or manifest.get('source_sha256')!=sources() or set(manifest.get('files_sha256',{}))!=FILES:raise ValueError('stock source/payload inventory differs')
    if any(digest(v)!=manifest['files_sha256'][k] for k,v in payload.items()):raise ValueError('stock payload checksum differs')
    value=inflate(payload['study.json.gz']);execution=inflate(payload['execution.json.gz']);deriv=derivation();runs=[]
    for record in (value,manifest):
        if any(record.get(k) is not False for k in (*model.FLAGS,'automatic_adoption','city_default_changed','joined_body_accepted','study_pass')):raise ValueError('stock authority exceeds scope')
    if value.get('source_sha256')!=manifest['source_sha256'] or value.get('source_unchanged_after_execution') is not True or value.get('derivation')!=deriv:raise ValueError('stock derivation/source differs')
    if execution.get('schema')!='osr-body-stiffness-execution/1' or execution.get('build',{}).get('build_command')!=moving_train.BUILD or not execution['build'].get('rustc','').startswith('rustc ') or len(execution['build'].get('binary_sha256',''))!=64 or len(execution.get('runs',[]))!=5:raise ValueError('stock actual compiler/run receipt required')
    for variant,name,receipt in zip(deriv['variants'],RUN_NAMES,execution['runs']):
        run=inflate(payload[name+'.json.gz']);a=candidate(variant)
        if run.get('schema')!='osr-moving-six-car-numerical/1' or run.get('assumptions')!=a or run.get('candidate_sha256')!=digest(moving_train.encoded(a)):raise ValueError('stock exact candidate differs')
        if run.get('feedback_enabled') is not True or run.get('sensor_bias_m')!=a['sensor_bias_m'] or run.get('configuration_revision')!=a['configuration_revision']:raise ValueError('stock coupled plant mode differs')
        if any(run.get(k) is not False for k in (*model.FLAGS,'physical_output_authorised','structural_acceptance')):raise ValueError('stock raw authority exceeds scope')
        if receipt.get('id')!=variant['id'] or receipt.get('candidate_sha256')!=run['candidate_sha256'] or receipt.get('completed_moving_steps')!=run['completed_moving_steps'] or receipt.get('planned_moving_steps')!=run['planned_moving_steps']:raise ValueError('stock execution identity differs')
        if receipt.get('controller_command')!=[execution.get('executable'),str(a['car_mass_kg']),str(round(a['step_s']*1e9)),str(a['gap_target_m']),str(a['gap_minimum_m']),str(a['gap_maximum_m'])]:raise ValueError('stock actual controller command differs')
        formation=dict(cars=6,body_length_m=a['body_length_m'],coupling_gap_m=a['coupling_gap_m'],car_mass_kg=variant['full_aw3_car_mass_kg'],nominal_body_length_m=6*a['body_length_m'],assumed_overall_length_m=6*a['body_length_m']+5*a['coupling_gap_m'])
        distance=station.load()['motion']['distance_m']
        trajectory=station.trajectory(distance_m=distance,runtime_s=a['runtime_s'],car_mass_kg=a['car_mass_kg'],cars=6,
            acceleration=a['acceleration_m_s2'],deceleration=a['deceleration_m_s2'],jerk=a['jerk_m_s3'],record_trace=False)
        beam=moving_train.MovingGuideway(a,distance,a['step_s'])
        if run['formation']!=formation or run['trajectory']!=trajectory or run['guideway']!=dict(span_m=beam.span,origin_m=beam.origin,spans=beam.count,basis=asdict(beam.assumptions)):raise ValueError('stock full AW3 trajectory/plant differs')
        expected_window=dict(start_time_s=0.,duration_s=a['runtime_s'],step_s=a['step_s'],settle_s=a['settle_s'])
        if run['window']!=expected_window or run['planned_moving_steps']!=round(a['runtime_s']/a['step_s']):raise ValueError('stock complete planned trajectory differs')
        if run['failure'] is None and (run['completed_moving_steps']!=run['planned_moving_steps'] or run['executed_duration_s']!=a['runtime_s']):raise ValueError('stock completion claim differs')
        validate_trace_and_energy(run,a)
        passed=(run['failure'] is None and not run['stop_seen'] and a['gap_minimum_m']<=run['minimum_gap_m']<=run['maximum_gap_m']<=a['gap_maximum_m'] and run['peak_coupler_extension_m']<=a['coupler_stroke_screen_m'])
        if run['study_pass'] is not bool(passed):raise ValueError('stock raw gap/stroke screen differs')
        runs.append(run)
    expected=_summary(deriv,runs);expected.update(source_sha256=sources(),source_unchanged_after_execution=True)
    if value!=expected:raise ValueError('stock derived result claims differ')
    if payload['README.md']!=readme(value) or payload['overview.svg']!=overview(value):raise ValueError('stock presentation differs')
    return dict(schema='osr-body-stiffness-verification/1',case_count=5,phase_screen_passing_alternatives=len(value['phase_screen_passing_alternative_ids']),
        gfrp_control_above_phase_limit=not value['cases'][0]['confirmation_screen_pass'],source_files=len(manifest['source_sha256']),
        selected_candidate_id=None,automatic_adoption=False,city_default_changed=False,joined_body_accepted=False,study_pass=False,**model.FLAGS)


def read_summary(output=OUTPUT):
    verification=verify(output);value=inflate(_read(Path(output)/'study.json.gz'))
    return dict(**verification,cases=value['cases'],open_gates=value['open_gates'],scope='Full AW3 rigid-car drilled-stock sensitivity; exact added tube/spacer mass, unchanged 5 degree screen; no joined/flexible-body or manufacturing acceptance')
