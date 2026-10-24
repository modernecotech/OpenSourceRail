"""Counted support/cooling architecture research, separate from accepted design."""
from hashlib import sha256
import argparse
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

from . import magnetic_research_closure as retained

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/research-closure/support-architecture.json'
WORKER=Path(__file__).with_name('_support_architecture_sweep.py')
SOURCES=(str(retained.ARCHIVE/'manifest.json'),
    'engineering/maglev_research/magnetic_research_closure.py',
    'engineering/maglev_research/support_architecture.py',
    'engineering/maglev_research/_support_architecture_sweep.py')


def _same(actual,expected,label):
    if type(actual) not in (int,float) or not math.isfinite(actual) or not math.isclose(actual,expected,rel_tol=1e-9,abs_tol=1e-8):
        raise ValueError(label+' differs')


def validate(value,root=ROOT):
    if value.get('schema')!='osr-support-architecture-research/1':raise ValueError('support architecture schema required')
    sources=value.get('source_sha256',{})
    if set(sources)!=set(SOURCES):raise ValueError('complete support architecture source binding required')
    for name,expected in sources.items():
        if sha256((Path(root)/name).read_bytes()).hexdigest()!=expected:raise ValueError('stale support architecture source: '+name)
    for flag in ('complete_system_feasible','physical_validation','engineering_accepted','configuration_adopted'):
        if value.get(flag) is not False:raise ValueError('research cannot assert acceptance: '+flag)
    _,_,records,inputs,_=retained._load(root)
    parent=records['results.json']
    if value['parent_configuration_sha256']!=parent['parent_configuration_sha256']:raise ValueError('mixed support parent')
    expected_model={name:expected for name,expected in parent['source_sha256'].items() if not name.startswith('build/')}
    if value['source_model_sha256']!=expected_model:raise ValueError('support source model differs')
    base=value['canonical'];retained_mass=parent['parent_aw3_kg']-24*parent['parent_module_mass_kg']
    _same(base['retained_nonmodule_aw3_kg'],retained_mass,'retained nonmodule mass')
    _same(base['net_support_per_added_canonical_module_n'],base['module_max_sampled_force_n']-base['module_weight_n'],'canonical net support')
    if base['fulltrain_modules']!=144 or base['speed_cannot_resolve_static_support'] is not True:raise ValueError('canonical support scope differs')
    rows=value['cases']
    if len(rows)!=256 or value['executed_joint_model_cases']!=256:raise ValueError('complete256-case support inventory required')
    if len({row['id'] for row in rows})!=256:raise ValueError('unique support cases required')
    expected_constraints=dict(passenger_payload_kg_per_car=12000.,ambient_c=40.,maximum_copper_c=120.,current_limit_a=120.,
        current_density_limit_a_mm2=3.75,coil_fill_limit=.55,field_limit_t=2.2,nominal_lateral_aw3_fraction=.1,
        adverse_lift_aw3_factor=1.3,cars=6)
    if value['fixed_constraints']!=expected_constraints:raise ValueError('support acceptance constraints changed')
    plans=itertools.product((.0225,.025,.0275,.030),(2.2,2.4),(.188,.24),(False,True),(False,True),(24,28,30,32))
    cooler=value['cooler_design'];harness=value['extra_module_harness']
    _same(cooler['mass_kg'],sum(part['volume_m3']*part['density_kg_m3'] for part in cooler['parts']),'cooler stock mass')
    _same(harness['mass_kg'],sum(harness[name] for name in ('copper_kg','insulation_kg','hose_kg','fluid_kg','reinforcement_plate_kg')),'extra module harness')
    survivors=[];nominal_passes=0
    for number,(row,(width,scale,outer_y,cooled,sensitive,module_count)) in enumerate(zip(rows,plans)):
        inner=[.16*scale+.02,.10];outer=[.72,outer_y]
        expected_hypothesis=dict(width_m=width,core_scale=scale,guide_outer_m=outer,guide_turns=200.,
            guide_conductor_area_mm2=.549*((math.prod(outer)-math.prod(inner))*.073)/(200*(sum(inner)+sum(outer)))*1e6,
            cooling='counted-fin-tank-fan-targets' if cooled else 'retained-unqualified-conductance',
            topology='useful-only-poles-sensitivity' if sensitive else 'original-branch-flux',modules_per_car=module_count)
        if row['id']!=f'support-{number:03d}' or row['hypothesis']!=expected_hypothesis:raise ValueError('support fixed hypothesis grid differs')
        count=row['hypothesis']['modules_per_car']
        if count not in (24,28,30,32):raise ValueError('bounded module count required')
        _same(row['extra_harness_mass_kg_per_car'],max(0,count-24)*harness['mass_kg'],'extra harness feedback')
        _same(row['local_module_plus_cooler_kg'],row['module_stock_mass_kg']+row['added_cooler_mass_kg_per_module'],'local assembly mass')
        aw3=retained_mass+count*row['local_module_plus_cooler_kg']+row['extra_harness_mass_kg_per_car']
        _same(row['controlled_aw3_kg'],aw3,'support AW3 feedback')
        _same(row['controlled_tare_kg'],aw3-12000.,'unchanged passenger load')
        _same(row['six_car_aw3_kg'],6*aw3,'full train mass')
        if row['fulltrain_module_count']!=6*count:raise ValueError('fulltrain module inventory differs')
        span=count/2*row['module_longitudinal_envelope_m']+(count/2-1)*.05
        _same(row['array_row_length_m'],span,'module row packaging')
        if row['array_nominal_fit'] is not (span<=16.):raise ValueError('array packaging screen differs')
        target=aw3*retained.G/count
        hypothesis=row['hypothesis'];x=.16*hypothesis['core_scale']
        guide_inner=[x+.02,.10];guide_outer=hypothesis['guide_outer_m']
        wet_area=2*(2*sum(guide_outer)*.073+2*(math.prod(guide_outer)-math.prod(guide_inner)))
        if hypothesis['cooling']=='counted-fin-tank-fan-targets':
            _same(row['added_cooler_mass_kg_per_module'],cooler['mass_kg'],'counted cooler installation')
            fluid_g=cooler['fluid_h_target_w_m2_k']*cooler['wetted_fraction_target']*wet_area
            guide_g=1/(1/fluid_g+1/cooler['air_conductance_w_k']+1/cooler['wall_conductance_w_k']
                         +1/(2*cooler['airflow_target_kg_s']*cooler['air_specific_heat_j_kg_k']))
        elif hypothesis['cooling']=='retained-unqualified-conductance':
            _same(row['added_cooler_mass_kg_per_module'],0.,'retained cooler count')
            guide_g=18.
        else:raise ValueError('bounded support cooling architecture required')
        _same(row['guide_cooling_w_k'],guide_g,'series thermal conductance')
        areas=[23.5,hypothesis['guide_conductor_area_mm2']]
        lengths=[140*(2*x+.60),2*200*(sum(guide_inner)+sum(guide_outer))]
        cu=inputs['materials']['copper']
        r20=[length/(area*1e-6)*cu['resistivity_20c_ohm_m'] for length,area in zip(lengths,areas)]
        for point,mult in ((row['nominal_joint'],1.),(row['adverse_joint'],1.3)):
            if any(len(point[name])!=2 for name in ('target_n','actual_force_n','required_current_a','current_density_a_mm2','constant_current_thermal_equilibrium_c')):
                raise ValueError('two-circuit support joint fields required')
            for actual,expected in zip(point['target_n'],[mult*target,.1*target]):_same(actual,expected,'joint load target')
            for actual,expected in zip(point['actual_force_n'],point['target_n']):_same(actual,expected,'achieved joint load')
            current=point['required_current_a'];density=[abs(i)/area for i,area in zip(current,areas)]
            for actual,expected in zip(point['current_density_a_mm2'],density):_same(actual,expected,'support current density')
            if point['continuous_current_density_screen'] is not (max(density)<=3.75):raise ValueError('support density screen differs')
            if point['domain_valid'] is not (max(abs(i) for i in current)<=120.):raise ValueError('support current domain differs')
            map_valid=bool(point['domain_valid'] and point['canonical_converged'] and point['minimum_demag_margin_a_m']>0 and point['max_core_b_t']<2.2)
            if point['map_valid'] is not map_valid:raise ValueError('support field screen differs')
            equilibrium=[]
            for i,resistance,g in zip(current,r20,[24.,guide_g]):
                heat=i*i*resistance;feedback=heat*cu['resistance_temperature_coefficient_per_k']
                equilibrium.append(None if feedback>=g else 40+heat*(1+cu['resistance_temperature_coefficient_per_k']*20)/(g-feedback))
            for actual,expected in zip(point['constant_current_thermal_equilibrium_c'],equilibrium):
                if expected is None:
                    if actual is not None:raise ValueError('support thermal runaway differs')
                else:_same(actual,expected,'support thermal equilibrium')
            if point['constant_current_thermal_screen'] is not all(t is not None and t<=120. for t in equilibrium):raise ValueError('support thermal screen differs')
        point=row['nominal_joint']
        needed=[i*i*r*(1+cu['resistance_temperature_coefficient_per_k']*100)/80 for i,r in zip(point['required_current_a'],r20)]
        for actual,expected in zip(row['required_cooling_at120c_w_k'],needed):_same(actual,expected,'support required cooling')
        ratios=dict(current=max(abs(i) for i in point['required_current_a'])/120.,density=max(point['current_density_a_mm2'])/3.75,
            field=point['max_core_b_t']/2.2,thermal=max(required/available for required,available in zip(needed,[24.,guide_g])))
        if set(row['nominal_constraint_ratios'])!=set(ratios):raise ValueError('support ranking constraint inventory differs')
        for name,expected in ratios.items():_same(row['nominal_constraint_ratios'][name],expected,'support ranking ratio')
        _same(row['maximum_nominal_constraint_ratio'],max(ratios.values()),'support maximum violation')
        nominal=bool(row['module_nominal_fit'] and max(row['copper_fill_fractions'])<=.55 and point['map_valid']
                     and point['continuous_current_density_screen'] and point['constant_current_thermal_screen'])
        reserve=bool(row['adverse_joint']['map_valid'])
        passed=bool(nominal and reserve and row['array_nominal_fit'])
        if row['conditional_nominal_joint_pass'] is not nominal or row['conditional_1_3_peak_pass'] is not reserve or row['conditional_joint_support_coupon_pass'] is not passed:
            raise ValueError('combined support constraints differ')
        if row['configuration_adopted'] is not False or row['complete_system_feasible'] is not False or row['topology_independently_validated'] is not False:
            raise ValueError('conditional support cannot adopt or validate topology')
        nominal_passes+=nominal
        if passed:survivors.append(row)
    if value['nominal_joint_passes']!=nominal_passes or value['simultaneous_survivor_count']!=len(survivors):raise ValueError('support survivor inventory differs')
    for topology,key in [('original-branch-flux','original_topology_survivors'),('useful-only-poles-sensitivity','sensitivity_topology_survivors')]:
        if value[key]!=sum(row['hypothesis']['topology']==topology for row in survivors):raise ValueError('support topology count differs')
    if len(value['separate_guidance_bound_cases'])!=18:raise ValueError('complete separate-guidance bound inventory required')
    for row in value['separate_guidance_bound_cases']:
        if row['joint_guidance_model_executed'] is not False or row['complete_system_feasible'] is not False or row['configuration_adopted'] is not False:
            raise ValueError('separate guidance bound is not a joint model result')
        guide=row['guide_material_bound']
        expected=retained_mass+row['support_modules_per_car']*row['support_module_mass_kg']+row['guidance_units_per_car']*(guide['mass_kg_per_unit']+row['guide_cooler_mass_kg_per_unit'])+max(0,row['support_modules_per_car']-24)*harness['mass_kg']
        _same(row['controlled_aw3_lower_bound_kg'],expected,'separate guidance mass fixed point')
        _same(guide['copper_fill'],.549,'separate guidance pack fill')
        _same(guide['current_a']*guide['turns'],guide['airgap_ampere_turn_lower_bound'],'separate guidance airgap MMF')
        _same(guide['current_a']/guide['conductor_area_mm2'],3.75,'separate guidance unchanged current density')
    ranked=sorted(rows,key=lambda row:(not row['array_nominal_fit'],not row['conditional_joint_support_coupon_pass'],row['maximum_nominal_constraint_ratio'],row['six_car_aw3_kg']))
    if value['recommended_next_case_id']!=ranked[0]['id']:raise ValueError('support recommended case differs')
    return value


def study(root=ROOT):
    """Read and validate the retained independent support architecture study."""
    return validate(json.loads((Path(root)/OUTPUT.relative_to(ROOT)).read_bytes()),root)


def run(output=OUTPUT,root=ROOT):
    output=Path(output)
    if output.exists():raise ValueError('preserve prior support execution; choose a new output')
    archive,members,_,_,_=retained._load(root)
    snapshot={name:(Path(root)/name).read_bytes() for name in SOURCES}
    manifest=json.loads(snapshot[SOURCES[0]])
    with tempfile.TemporaryDirectory(prefix='osr-support-architecture-') as temporary:
        tree=Path(temporary)
        for name in members:
            if name.startswith('inputs/'):
                payload=(archive/name).read_bytes()
                if sha256(payload).hexdigest()!=manifest['files_sha256'][name]:raise ValueError('changed frozen source')
                path=tree/name.removeprefix('inputs/');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload)
        work=tree/'build/pole-return-research';work.mkdir(parents=True)
        for name in ('run.py','run_topology.py','run_controls.py','run_guidance.py'):
            payload=(archive/'evidence'/name).read_bytes()
            if sha256(payload).hexdigest()!=manifest['files_sha256']['evidence/'+name]:raise ValueError('changed frozen driver')
            (work/name).write_bytes(payload)
        (work/'support_sweep.py').write_bytes(snapshot[SOURCES[-1]])
        result=subprocess.run([sys.executable,str(work/'support_sweep.py')],cwd=tree,timeout=240,text=True,capture_output=True)
        if result.returncode:raise RuntimeError('isolated support study failed: '+result.stderr[-6000:])
        value=json.loads((work/'support-architecture.json').read_bytes())
    if any((Path(root)/name).read_bytes()!=payload for name,payload in snapshot.items()):raise ValueError('support sources changed during execution')
    value['source_sha256']={name:sha256(payload).hexdigest() for name,payload in snapshot.items()}
    validate(value,root)
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(retained._encoded(value))
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('run','check'))
    parser.add_argument('--output',type=Path,default=OUTPUT);args=parser.parse_args()
    value=run(args.output) if args.action=='run' else validate(json.loads(args.output.read_bytes()))
    print(json.dumps({key:value[key] for key in ('executed_joint_model_cases','nominal_joint_passes','simultaneous_survivor_count','original_topology_survivors','sensitivity_topology_survivors','configuration_adopted')}))


if __name__=='__main__':main()
