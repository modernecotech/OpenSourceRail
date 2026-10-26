#!/usr/bin/env python3
"""Compile compact P0 research evidence; large solver files stay in a local CAS.

This does not select a replacement, publish acceptance or regenerate city studies.
"""
from pathlib import Path
import argparse
from collections import defaultdict
from hashlib import sha256
import gzip
import io
import json
import math
import re
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.design_search import whole_system,guideway_tradeoff
from engineering.design_search.storage import atomic_immutable
from engineering.suspension_closure import operating_point
from engineering.thermal_closure import comfort_fixes
from engineering.development_baseline import selection

CODE='tools/automation/publish-physical-round.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,default_configuration_changed=False,economic_winner_established=False)


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):return atomic_immutable(p,v if isinstance(v,bytes) else selection.encoded(v))


def bundle(directory,essential_only=False):
    output=io.BytesIO();directory=Path(directory)
    with tarfile.open(fileobj=output,mode='w') as tar:
        for p in sorted(directory.rglob('*')):
            if not p.is_file():continue
            if p.is_symlink():raise ValueError('ordinary research artifacts required')
            if essential_only and not (p.suffix in ('.json','.pro','.log') or p.name in ('gmsh.log',)):
                continue
            data=p.read_bytes();info=tarfile.TarInfo(p.relative_to(directory).as_posix());info.size=len(data);info.mtime=0;info.mode=0o644
            tar.addfile(info,io.BytesIO(data))
    return gzip.compress(output.getvalue(),mtime=0)


def _merge(*mappings):
    result={}
    for m in mappings:
        for name,h in m.items():
            if name in result and result[name]!=h:raise ValueError('mixed producer revisions: '+name)
            result[name]=h
    return dict(sorted(result.items()))


def maturity(selected,support):
    common=dict(physical_accepted=False,manufacturing_released=False,prototype_correlated=False)
    def row(name,level,execution,missing):return dict(subsystem=name,maturity=level,execution=execution,missing=missing,**common)
    return dict(schema='osr-subsystem-maturity-register/1',selection_id=selected['selection_id'],
        candidate_id=selected['vehicle']['candidate_id'],
        levels=['concept','analytical','numerically_converged','cross_solver_confirmed','prototype_correlated','physically_qualified','manufacturing_released'],
        subsystems=[row('suspension','analytical','Five native scalar-potential zero-current FEM cases; force contours remain inconsistent',
            ['Converged force/moment maps','3D winding-current source','Stable multiaxis control and measured correlation']),
          row('capture','analytical','264 combined capture/roof cases, including failed controls',
            ['Measured loading/unloading curves','Upward pull-in and rebound retention','Body/beam loadpath and occupant pulse qualification']),
          row('roof','analytical','Nonlinear radiation/convection and counted coating/screen stock',
            ['Weathering/dust optics','Under-HVAC thermal field','Hot-panel strength, bonds and fire/adhesion']),
          row('civil','analytical','Counted alternative material/connection definitions and necessary local load/flux bounds',
            ['Coupled installed magnetic field','Cracked RC/shear/anchorage/fatigue','Global prestress, piers, foundations and erection']),
          row('equipped-vehicle','concept','Partial native material geometry with retained stock/reference/allocations',
            ['Complete located installed inventory','Full CG/inertia','Joined body stress/buckling/fatigue/modes']),
          row('propulsion','analytical','Required finite-zone thrust/power and protocol fixtures',
            ['Actual force/voltage/current/duty limits','Switching/phase handoff','Repeated thermal duty']),
          row('coupled-journey','concept','Ideal-force method journeys; selected physical-force trip unexecuted',
            ['Verified hover and3D control maps','Complete equipped body','Installed station/brake/thermal limits']),
          row('economics','analytical','Equal-service quantities, Pareto proxy comparison and symbolic break-even equations',
            ['Complete priced designs','Manufacturing/installation labour','Equal-service rail comparator and whole-life renewals'])],
        city_specific_decisions=dict(global_default_is_starting_candidate=True,local_adoption_verified=False,
            unevaluated=['Demand','Grades/terrain','Climate','Stations/access/evacuation','Ground/site works','Suppliers/costs']),
        qualification_rule='Research remains visible; delivery release requires applicable passed gates plus authenticated measured evidence and independent review.',**FLAGS)


def stock_summary(selected):
    car=selected['vehicle'];groups=defaultdict(float)
    for r in car['inventory']:groups[r['evidence_class']]+=r['mass_kg']
    return dict(selection_id=selected['selection_id'],candidate_id=car['candidate_id'],
        body_candidate_id=car['body_candidate_id'],magnet_component_id=car['magnet_component_id'],
        mass=car['mass'],accounted_mass_by_evidence_class_kg=dict(groups),inventory_occurrences=len(car['inventory']),
        missing_inventory=car['missing_inventory'],complete_installed_mass_CG_and_inertia_known=False,
        native_material_mass_kg=10198.35084288709,
        source='Exact selected native material assembly and accounted ledger; no unlocated reserve converted into a solid.',**FLAGS)


def figure(whole):
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['svg.hashsalt']='osr-physical-feasibility-round-1'
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
    colors={46:'#147D92',64:'#8C68A4',80:'#C47A25',120:'#6E777C'}
    for ax,c in zip(axes,whole['comparisons']):
        rows=[r for r in whole['scenarios'] if r['scenario_id'] in c['comparable_scenario_ids']]
        for p in (46,64,80,120):
            values=[r for r in rows if r['definition']['normal_people_per_car_hypothesis']==p]
            if values:ax.scatter([r['trainsets'] for r in values],[r['direction_winding_m']/1000 for r in values],c=colors[p],s=65,label=str(p)+' people/car',alpha=.8)
        for r in rows:
            if r['scenario_id'] in c['quantity_pareto_scenario_ids']:
                ax.annotate(f"{r['definition']['normal_people_per_car_hypothesis']} / {r['definition']['headway_s']:g}s",(r['trainsets'],r['direction_winding_m']/1000),xytext=(5,8),textcoords='offset points',fontsize=8)
        ax.set(title=f"At least {c['required_capacity_pphpd']:,.0f} pphpd; interval <=120s",xlabel='Analytical Baghdad trainsets',ylabel='Directional station winding (km)')
        ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.suptitle('Quantity tradeoffs - no priced or physically qualified winner',fontsize=13)
    data=io.StringIO();fig.savefig(data,format='svg',metadata={'Date':None});plt.close(fig)
    return data.getvalue().encode()


def human_markdown(text):
    """Format prose units without changing links, identifiers or commands."""
    text=text.replace('atc1abd724','at `c1abd724`')
    result=[];fenced=False
    for line in text.splitlines():
        if line.startswith('```'):
            fenced=not fenced;result.append(line);continue
        if fenced:result.append(line);continue
        chunks=re.split(r'(\[[^\]]*\]\([^)]*\)|`[^`]*`)',line)
        for i,part in enumerate(chunks):
            if part.startswith(('[','`')):continue
            part=re.sub(r'(?<=[a-z])(?=[23]D)', ' ',part)
            tokens={'3D':'__THREED__','2D':'__TWOD__','H60':'__HCORE__','HP60':'__HPCORE__','S8R':'__SHELL__','P0':'__PZERO__'}
            for a,b in tokens.items():part=part.replace(a,b)
            part=re.sub(r'(?<![A-Za-z])m3\b','m³',part)
            part=re.sub(r'(?<=[A-Za-z])(?=\d)',' ',part)
            part=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',part)
            for a,b in tokens.items():part=part.replace(b,a)
            chunks[i]=part
        result.append(''.join(chunks))
    return '\n'.join(result)+'\n'


def report(whole,civil,fixes,support,refinement,footprint,clearance):
    baseline=next(r for r in whole['scenarios'] if r['scenario_id']==whole['current_default_scenario_id'])
    lines=['# Coupled physical feasibility and whole-system review follow-up','',
      'OpenSourceRail seeks simple, low-cost, locally maintainable transport. This bounded research round tests the hardware and system consequences highlighted by the26October review. The selected six-car comfort design remains the starting candidate; no alternative here is a qualified or economic replacement.','',
      '[Selected development baseline](../current/README.md) · [Engineering ownership](../../../engineering/README.md) · [Maturity by subsystem](maturity.json) · [Source and payload receipt](manifest.json)','',
      '## What was executed','',
      f"- {whole['budget']['scenarios']} one-city service/load/zone alternatives, with equal-service comparisons at8,280 and14,400pphpd and maximum120s headway.",
      f"- {civil['counts']['executed']} counted guideway variants, each with40/70kN local load fixtures; {civil['counts']['conditional_necessary_survivors']} conditional necessary survivors and zero physically qualified replacements.",
      f"- {fixes['cases']['capture_cases'] if isinstance(fixes['cases'],dict) else 208} capture cases and56roof cases under declared material/thermal hypotheses.",
      '- Four new native GetDP PM/steel field solves and one independent finer-mesh check. These have no3D coil-current source and do not establish stable hover.','',
      '## Suspension and control: weight is only one part of the gap','',
      'At40mm/80C with the retained35mm facing, the two air contours calculate7.494 and9.147kN/module. The normal-load mean weight is8.502kN/module, between those values. The independent finer mesh gives7.256/9.420kN; contour spread grows from18.1% to23.0%. A solved PDE is therefore insufficient to credit a reliable force map.','',
      '| New scalar-PM state | Contour Fz, kN | Local steel peak, T |','|---|---:|---:|']
    for row in support['native_rows']:
        p=row.get('point',{});a=p.get('analysis');s=row['specification']['state']
        force='not available' if not a else ' / '.join(f"{x['force_N'][2]/1000:.3f}" for x in a['air_contour_results'])
        peak='unknown' if not a else f"{a['steel_B_peak_T']:.3f}"
        lines.append(f"| {s['gap_m']*1000:g}mm, {s['temperature_C']:g}C, {s['facing_thickness_m']*1000:g}mm facing | {force} | {peak} |")
    lines+=['',
      'Reducing the facing from35 to20mm gives similar lift at the sampled40mm/80C state, within the numerical disagreement, but raises the local steel peak to1.664T. This exceeds the civil study\'s declared1.6T screen ceiling. It cannot be treated as a validated thinner replacement.','',
      'Retained same-state2D diagnostics indicate that approximately1mm of gap disturbance can consume roughly14–16A of the entire±15A sampled common-current range. Opposed-current lateral authority is about2.35N/A at the retained80C state, while the installed3D roll/pitch/yaw derivatives and coupled controller remain unknown. A passenger cap reduces required steady support; it does not establish guidance, control reserve or fault stability.','',
      'The current native3D kernel is scalar potential without a free-current winding source. The next decisive model is a benchmarked current-capable3D formulation ([GetDP vector-potential example](https://www.getdp.info/doc/texinfo/getdp.html#Magnetostatic-3D-vector-potential-formulation)) with actual closed coils, followed by force/moment maps and control/thermal tests. Wider-gap force crossings are next-experiment diagnostics, not operating gaps.','',
      '## Civil structure: count the material traded away','',
      'The retained reference counts21.627t steel and42.5t prismatic concrete per25m span before remaining structural/site quantities. The continuous concrete-ledge family reduces counted steel to about11.495t but adds32.815m3 of concrete: the counted subtotal grows to about136.0t/span. Steel savings alone would conceal a worse span-mass result. Discrete-crosshead variants are included below as the next bounded physical revision.','',
      '| Rejected quantity-frontier control | Steel t/25m | Added concrete m3/25m | All support anchors/25m |','|---|---:|---:|---:|']
    for c in civil['shortlist']:
        name=c['physical_definition'].get('family',c['physical_definition'].get('architecture','candidate'))
        lines.append(f"| {name} | {c['steel_kg_per25m']/1000:.3f} | {c['additional_concrete_m3_per25m']:.3f} | {c['all_support_anchors_per25m']} |")
    lines+=['',
      'The lightest counted discrete alternative uses18integralRCcrossheads,35mm facings and a dual-purpose steel box. It counts14.103t steel,5.646m3 extra concrete and276support anchors per25m: about70.718t subtotal, still10.3%heavier than the old64.127t reference. Factory welding is about246.8m/span. No price or global-strength winner is established. These are parametric local necessary bounds, not global beam/prestress/anchor-fatigue approval. Facing, brake/capture connections, extra concrete, reinforcement and changed manufacture are counted where defined; piers, erection, strength details and installed prices remain open. Passing the single-return flux bound does not establish the native local peak field.','',
      'An independent six-case native CalculiX face fixture also ran. At ideal0.5m line supports,20mm steel under40kN reaches2.060mm maximum deflection and fails the1mm target;35mm reaches0.390mm at40kN and0.683mm at70kN. Refinement from8 to16longitudinal elements changes mean deflection by under0.005%. This does not qualify real anchors, RC heads or whole beams. [Native decks/logs/results](civil-native-evidence.tar.gz) · [Independent readback](civil-native-readback.json).','',
      '**Independent fit check: all five quantity-frontier alternatives fail the selected-car material-box test at the stated reference pose.** Continuous variants intersect102parts each; the discrete embedded variant intersects48; the lightest discrete box variant intersects20. Positive solid-box overlap is a known collision, not a passing envelope screen. The remaining cylinders and all motion states are unqualified. These alternatives need a joint body/carrier/beam rearrangement before any integrated selection. [Coupled proposal eligibility](proposal-eligibility.json) · [Exact collision counterexamples](civil-clearance.json) · [Geometry check source and receipt](civil-clearance-proof.tar.gz).','',
      '## Capture and roof: promising changes retain their costs and limits','',
      'The16-contact precrushed-target cartridge adds143.5kg and passes16/24 material/load/contact sensitivities. The32-contact target passes24/24, but adds432.8kg and produces about2.41g net upward acceleration in the nominal normal-load first arrest. These are declared crush-law targets; occupant limits, actual curves, rebound latch and body/beam load paths remain unknown. Magnetic pull-in toward the steel is a separate, unevaluated energy case. No capture gate is closed.','',
      'A counted [KARNAK white coating](https://www.karnakcorp.com/product/529-renu-white) adds47.8kg/car. Under the same new radiation model, the reference core temperature falls from76.44C to60.08C. The original sol-air control remains77.91C; that different model is retained separately. An aged-coating, low-convection/warm-surroundings case still reaches72.85C and fails the70C core limit. The126.3kg canopy proposal passes11 local cases only over its17.40m2 non-HVAC patch; temperatures beneath the HVAC/condenser regions remain unknown.','',
      '[Capture/roof summary](capture-roof-summary.json) · [Exact264-case record](capture-roof-result.json.gz)','',
      '## Equal-service economics and capacity','',
      f"The exact current one-city case reproduces **{baseline['trainsets']} trainsets and{baseline['direction_winding_m']/1000:.1f}km directional winding**. Holding the same comfort car and20m/s proposal at240s reduces the requirement to468sets, but also halves capacity to4,140pphpd. The old451set fleet is not an equal-service alternative to the new120s plan.",'',
      'At46people/car,14,400pphpd requires69s departures. None of the comfort-only cases meets14,400 under this bounded120s-or-better resource comparison. The80-person/120s load-layout hypothesis produces14,400pphpd,901sets and404.0km winding, but it requires a new verified interior/admission policy and carries more load. It does not silently replace the comfort layout.','',
      '![Fleet and winding quantities under common service floors](quantity-frontier.svg)','',
      'Every actual whole-life price remains unknown. Missing train, guideway, motor, station, depot, labour, energy and renewal prices never become zero. The continuous-traction reference is an ideal-kinematic fleet lower bound (862sets at the default frequency), not a designed/priced wheel-rail train. The linked equations expose what quotations and actual equipment designs are needed for an equal-service comparison.','',
      '[168-scenario summary and Pareto IDs](whole-system-summary.json) · [Detailed one-city results](whole-system-results.json.gz)','',
      '## Complete vehicle and model maturity','',
      '[Installed-stock accounting](vehicle-stock-summary.json) distinguishes counted material, supplier references and unlocated allocations. The exact selected material CAD remains a10.198t subset of the17.357t accounted tare. Complete installed stock, CG/inertia and joined-body modes remain unknown. No empty/normal/crowd journey is invented from the missing interfaces.','',
      'Maturity is recorded per subsystem using concept, analytical, numerically_converged, cross_solver_confirmed, prototype_correlated, physically_qualified and manufacturing_released. A native software/solver method does not promote every subsystem. The global default is a starting candidate; each city still needs demand, terrain, grade, climate, station, access, ground, procurement and cost validation.','',
      '## Repository and evidence storage','',
      f"The read-only audit confirms **{footprint['tree_entries']:,}tree entries and{footprint['tracked_blob_content_decimal_GB']:.3f}GB file content** atc1abd724; cities contain{100*footprint['ordinary_checkout_city_fraction']:.2f}%. These are HEAD contents, not packed-history or clone-transfer measurements. No published history or source-bound city payload was deleted.",'',
      'This packet keeps compact results, manifests, input/solver logs and reproduction code in Git. Full new native mesh/field packages are content-addressed in a local artifact store, recorded in [the artifact catalogue](artifacts.json). No remote durable store is configured, so raw download is explicitly unavailable from a fresh checkout. Full raw verification requires that object or re-execution. The compact results do not masquerade as a complete solver archive.','',
      '[Footprint audit and largest objects](footprint.json) · [Compact native inputs/logs](native-execution-proof.tar.gz)','',
      '## Next physical work and verification','',
      '1. Confirm force integration with independent method and mesh/domain/contour studies, then implement a benchmarked3D current source and stronger controllable guidance geometry.',
      '2. Develop discrete/changed-interface civil candidates jointly with those magnetic maps; compare global structure, factory work, erection and prices.',
      '3. Test actual crush and rebound/pull-in hardware, aged roof finish/core/HVAC regions and complete installed vehicle stock.',
      '4. Only then run the same-candidate hover,1.5/2km journey, receiving-power loss and support-power loss cases.',
      '5. Compare equal-service whole-life cost against a fully specified conventional rail alternative before adopting an economic reference.','',
      'Fast P0 regression checks and nightly native Chrono/GetDP/composite method jobs are configured. Cloud-green status is not inferred from local results; no Actions run was returned for the reviewed `c1abd724` HEAD. Physical qualification remains independently reviewed measured evidence.','',
      '```bash','python -m engineering.design_search.whole_system run --output build/reproduce/whole-system',
      'python -m engineering.design_search.guideway_tradeoff run --output build/reproduce/guideway',
      'python -m engineering.thermal_closure.comfort_fixes run --output build/reproduce/capture-roof',
      'python -m engineering.suspension_closure.operating_point run --output build/reproduce/support --getdp /path/to/getdp',
      'python tools/automation/publish-physical-round.py verify --output docs/design-engine/physical-feasibility-round',
      '```','']
    return human_markdown('\n'.join(lines).replace('the26October','the 26 October'))


def publish(output,inputs,root=ROOT):
    root=Path(root).resolve();output=Path(output).resolve();inputs=Path(inputs).resolve()
    selected=selection.load(root)
    checks=dict(whole_system=whole_system.verify(inputs/'whole-system',root,replay=False),
        guideway=guideway_tradeoff.verify(inputs/'guideway-v2',root,replay=False),
        capture_roof=comfort_fixes.verify(inputs/'capture-roof',root=root,replay=False),
        support=operating_point.verify(inputs/'support-map',root))
    whole=read(inputs/'whole-system/summary.json');civil=read(inputs/'guideway-v2/summary.json')
    fixes=read(inputs/'capture-roof/summary.json');support=read(inputs/'support-map/result.json')
    refinement=read(inputs/'support-map-refinement/result.json') if (inputs/'support-map-refinement/result.json').is_file() else None
    if refinement is None:raise ValueError('Independent refinement evidence required')
    refinement_input=read(inputs/'support-map-refinement/input.json')
    derived=operating_point._derived(inputs/'support-map-refinement',refinement_input,read(inputs/'support-map-refinement/point.json'))
    if derived!=refinement['point'] or refinement['parent_request_id']!=support['request_id']:
        raise ValueError('Independent refinement differs from raw state and parent')
    checks['refinement']=dict(native_raw_reverified=True,force_convergence_established=False,physical_accepted=False)
    footprint=read(inputs/'footprint.json')
    clearance=read(inputs/'guideway-clearance/result.json')
    if clearance['guideway_campaign_id']!=civil['campaign_id'] or clearance['body_candidate_id']!=selected['vehicle']['body_candidate_id']:
        raise ValueError('Clearance result belongs to another guideway/body')
    for v,vehicle_key,body_key,magnet_key in ((whole,'parent_candidate_id','parent_body_candidate_id','parent_magnet_component_id'),
        (civil,'parent_vehicle_candidate_id','body_candidate_id','magnet_component_id'),
        (fixes,'candidate_id','body_candidate_id','magnet_component_id'),
        (support,'vehicle_candidate_id','body_candidate_id','magnet_component_id')):
        if any(v[k]!=selected['vehicle'][expected] for k,expected in ((vehicle_key,'candidate_id'),(body_key,'body_candidate_id'),(magnet_key,'magnet_component_id'))):
            raise ValueError('Mixed physical components in research packet')
    values=(whole,civil,fixes,support)
    if any(v.get('selection_id',v.get('parent_selection_id'))!=selected['selection_id'] for v in values):raise ValueError('mixed research selections')
    for value in values:
        if value.get('physical_accepted') is not False:raise ValueError('research cannot grant physical acceptance')
    output.mkdir(parents=True,exist_ok=False)
    eligibility=dict(schema='osr-coupled-proposal-eligibility/1',selection_id=selected['selection_id'],
        parent_candidate_id=selected['vehicle']['candidate_id'],proposals=[dict(guideway_candidate_id=row['guideway_candidate_id'],
        local_necessary_screen='conditional-pass',selected_body_reference_fit=row['stated_pose_clearance_screen'],
        positive_material_intersections=row['material_box_intersections'],eligible_for_integrated_selection=False,
        manufacturing_release=False,physical_accepted=False,required_action='Revise body/carrier/guideway together and rerun geometry/structural/magnetic checks') for row in clearance['rows']],
        qualified_replacements=0,default_changed=False)
    payloads={'whole-system-summary.json':selection.encoded(whole),'guideway-summary.json':selection.encoded(civil),
        'capture-roof-summary.json':selection.encoded(fixes),'support-summary.json':selection.encoded(support),
        'maturity.json':selection.encoded(maturity(selected,support)),'vehicle-stock-summary.json':selection.encoded(stock_summary(selected)),
        'footprint.json':selection.encoded(footprint),'quantity-frontier.svg':figure(whole),
        'README.md':report(whole,civil,fixes,support,refinement,footprint,clearance).encode(),
        'whole-system-results.json.gz':(inputs/'whole-system/results.json.gz').read_bytes(),
        'guideway-result.json.gz':(inputs/'guideway-v2/result.json.gz').read_bytes(),
        'capture-roof-result.json.gz':(inputs/'capture-roof/result.json.gz').read_bytes(),
        'native-execution-proof.tar.gz':bundle(inputs/'support-map',True),
        'civil-native-evidence.tar.gz':bundle(inputs/'guideway-native'),
        'civil-native-readback.json':(inputs/'guideway-native-verification.json').read_bytes(),
        'proposal-eligibility.json':selection.encoded(eligibility),'civil-clearance.json':selection.encoded(clearance),'civil-clearance-proof.tar.gz':bundle(inputs/'guideway-clearance')}
    if refinement is not None:
        payloads['support-refinement.json']=selection.encoded(refinement)
        payloads['native-refinement-proof.tar.gz']=bundle(inputs/'support-map-refinement',True)
    objects=[]
    for label in ('support-map','support-map-refinement'):
        folder=inputs/label
        if not folder.is_dir():continue
        raw=bundle(folder);h=sha256(raw).hexdigest();path=inputs/'artifacts/sha256'/(h+'.tar.gz');write(path,raw)
        objects.append(dict(label=label,sha256=h,bytes=len(raw),local_path=path.relative_to(root).as_posix(),
            artifact_uri='osr-local-cas:sha256/'+h,remote_uri=None,remote_uploaded=False,
            git_contains_full_raw_output=False,retrievable_from_fresh_checkout=False))
    payloads['artifacts.json']=selection.encoded(dict(schema='osr-research-artifact-catalogue/1',objects=objects,
        remote_store_configured=False,raw_verification='Supply local CAS object or rerun exact native recipe; compact proof does not replace raw mesh/field validation'))
    for name,raw in payloads.items():write(output/name,raw)
    source_receipts=[read(inputs/name/'manifest.json') for name in ('whole-system','guideway-v2','capture-roof','support-map')]
    sources=_merge(*(v['source_sha256'] for v in source_receipts),{CODE:sha(root/CODE)})
    manifest=dict(schema='osr-physical-followup-publication/1',selection_id=selected['selection_id'],
        candidate_id=selected['vehicle']['candidate_id'],body_candidate_id=selected['vehicle']['body_candidate_id'],
        magnet_component_id=selected['vehicle']['magnet_component_id'],source_sha256=sources,
        files_sha256={n:sha256(raw).hexdigest() for n,raw in sorted(payloads.items())},production_readbacks=checks,
        native_raw_objects_available_in_ordinary_Git=False,**FLAGS)
    manifest['publication_id']=selection.identity(manifest);write(output/'manifest.json',manifest)
    return verify(output,root)


def verify(output,root=ROOT):
    output=Path(output);root=Path(root);m=read(output/'manifest.json');selected=selection.load(root)
    if m['publication_id']!=selection.identity({k:v for k,v in m.items() if k!='publication_id'}):raise ValueError('research publication identity differs')
    if m['selection_id']!=selected['selection_id']:raise ValueError('research selection differs')
    if any(m[k]!=selected['vehicle'][k] for k in ('candidate_id','body_candidate_id','magnet_component_id')):raise ValueError('research component identities differ')
    for name,h in m['source_sha256'].items():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or sha(root/p)!=h:raise ValueError('research source differs: '+name)
    for name,h in m['files_sha256'].items():
        if Path(name).name!=name or sha(output/name)!=h:raise ValueError('research output differs: '+name)
    if any(m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('research cannot grant release')
    return dict(publication_integrity_verified=True,publication_id=m['publication_id'],
        native_raw_reverified=False,native_raw_verification_requires='Local CAS object or exact recipe reexecution',**FLAGS)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('publish','verify'));p.add_argument('--output',type=Path,required=True)
    p.add_argument('--inputs',type=Path,default=ROOT/'build/physical-feasibility-round');a=p.parse_args()
    v=publish(a.output,a.inputs) if a.command=='publish' else verify(a.output)
    print(json.dumps(v,sort_keys=True))

if __name__=='__main__':main()
