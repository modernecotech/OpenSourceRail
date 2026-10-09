"""Execute the software work packages and report every remaining external gate."""
from __future__ import annotations
from copy import deepcopy
import math
from pathlib import Path

from osr_mech.civil.exploration import geometry,deck_section,rectangle,assembly_cad
from .contracts import HERE,ROOT,encoded,load,sha,dependencies
from .workflow import candidate,run_campaign,verify
from . import bim,commercial,nonlinear,materials,detailed,search,validation,storage
from . import connections,vehicle,robustness,orthotropic


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(encoded(value))


def families(study):
    extra=[('conventional-I','Conventional twin prestressed I-girders with deck'),('U-girder','Open U-girder'),
           ('ribbed-deck','Ribbed concrete deck'),('uhpc-ribbed','Targeted UHPC ribs'),
           ('hybrid-shell','FRP shell and concrete compression flange'),('segmental-box','Segmental box, perfect-continuity screen')]
    records=deepcopy(study)
    records['material_records']={
        'uhpc':dict(name='illustrative-UHPC',youngs_modulus_pa=50e9,poisson_ratio=.2,density_kg_m3=2500.,
                    stiffness_factor=1.,basis='Unmeasured research elastic property record; no mix or strength adopted',measured=False),
        'frp':dict(name='illustrative-FRP-longitudinal',youngs_modulus_pa=25e9,poisson_ratio=.25,density_kg_m3=1900.,
                   stiffness_factor=1.,basis='Unmeasured longitudinal elastic research record; orthotropy/interface failure uncovered',measured=False)}
    records['material_records']['frp']['orthotropic']=dict(ex_pa=25e9,ey_pa=8e9,ez_pa=8e9,nu_xy=.25,nu_xz=.25,nu_yz=.3,gxy_pa=3e9,gxz_pa=3e9,gyz_pa=3e9)
    rows=[]
    for name,description in extra:
        design=deepcopy(study['candidates'][1]);design['deck']['family']=name
        c=candidate(design,records)
        model=__import__('engineering.civil_exploration.model',fromlist=['System']).System(c,records,records['ground_scenarios'][0],8)
        response=model.static_envelope()
        rows.append(dict(family=name,description=description,candidate=c,quantities=model.quantities,
                         response=response['envelope'],coverage='elastic perfect-bond reduced system only',
                         physical_release=False,required_tests=['material/section','connections','fatigue/durability','supplier/site qualification']))
    registry=dict(schema='osr-civil-option-registry/1',families=[dict(id=name,owner_role='structural/materials lead',
                  implemented_geometry=True,model_coverage='bounded elastic screening',qualification='research')
                  for name in ('pi','hollow-box',*[r[0] for r in extra])],
                  additional_options=[dict(id=name,qualification='unsupported-pending-data-and-adapter') for name in
                                      ('lightweight-concrete','double-skin-hybrid-pier','alternative-piling','recycled-secondary-parts')])
    from osr_mech.civil.foundation import foundation_catalog
    registry['existing_foundation_options']=foundation_catalog()['foundation_types']
    registry['ground_improvement_options']=foundation_catalog()['ground_improvement_types']
    registry['foundation_selection']='requires site-calibrated soil, installation constraints and independent review'
    return records,rows,registry


def component_campaign(output):
    p=load(HERE/'config/components.json');output.mkdir()
    curves=[]
    for name,regions in [('solid-pier',[rectangle(2.,1.5,z=.75)]),
                         ('hollow-deck',deck_section('hollow-box')['regions'])]:
        result=nonlinear.moment_curvature(regions,p['concrete'],p['steel'],output=output/(name+'-moment-curvature.csv'))
        write(output/(name+'-moment-curvature.json'),result);curves.append(result)
    pile=nonlinear.pile(p['pile'],output/'nonlinear-pile.csv');write(output/'nonlinear-pile.json',pile)
    second_order=nonlinear.pier_pdelta(8.,3.,.5625,30e9,100e6,1e5);write(output/'pier-pdelta.json',second_order)
    section=deck_section('pi')
    prestress_inputs=dict(initial_force_n=3e6,tendon_area_m2=.003,tendon_modulus_pa=195e9,eccentricity_m=.35,span_m=25.,
                         friction_mu=.15,angular_change_rad=.02,wobble_per_m=.001,anchor_slip_m=.004,
                         shortening_strain=.00005,creep_strain=.00015,shrinkage_strain=.0001,relaxation_fraction=.025,
                         concrete_modulus_pa=30e9,basis='Synthetic loss/camber sensitivity; no supplier prestress specification')
    prestress=materials.prestress(section,prestress_inputs);write(output/'prestress.json',prestress)
    fatigue=materials.fatigue_damage([dict(range_pa=50e6,count=1e5)],
                                    [dict(range_pa=25e6,cycles=1e7),dict(range_pa=100e6,cycles=1e5)])
    write(output/'fatigue-sensitivity.json',fatigue)
    joint=connections.friction_cycle(output/'friction-cycle.csv');write(output/'friction-cycle.json',joint)
    # A small moving mass converges to the independently derived moving-force
    # solution, providing a check on the coupled suspension/contact equations.
    vehicle_inputs=dict(sprung_mass_kg=50.,unsprung_mass_kg=5.,suspension_n_m=1e7,suspension_ns_m=0.,contact_n_m=1e9,
                        bridge_damping_ratio=0.,irregularity_amplitude_m=0.,irregularity_wavelength_m=10.,basis='small-mass analytical verification limit')
    moving=vehicle.run(5.4e9,3000.,20.,[0.],vehicle_inputs,speed=10.,dt=.001,output=output/'vehicle-verification.csv')
    from engineering.analysis.benchmarks.civil.exploration import moving_point_analytical
    import numpy as np
    expected=max(abs(moving_point_analytical(float(t),20.,10.,55*9.81,5.4e9,3000.,0.)) for t in np.arange(.001,2.001,.001))
    write(output/'vehicle-verification.json',dict(result=moving,expected_peak_m=expected,relative_error=abs(moving['peak_displacement_m']/expected-1.)))
    laminate=dict(ex_pa=25e9,ey_pa=8e9,ez_pa=8e9,nu_xy=.25,nu_xz=.25,nu_yz=.3,gxy_pa=3e9,gxz_pa=3e9,gyz_pa=3e9)
    coupon=orthotropic.coupon(laminate,output/'orthotropic-coupon')
    checks=[dict(name='concrete/steel initial section tangent',relative_error=abs(c['observed_initial_EI_nm2']/c['initial_EI_nm2']-1),
                 passed=abs(c['observed_initial_EI_nm2']/c['initial_EI_nm2']-1)<.001) for c in curves]
    checks += [dict(name='nonlinear pile full load reached',passed=pile['status']=='completed'),
               dict(name='P-delta amplification exceeds linear response',passed=second_order['amplification']>1.),
               dict(name='P-delta analytical beam-column agreement',passed=second_order['analytical_relative_error']<.002),
               dict(name='prestress losses conserve force',passed=math.isclose(prestress['effective_force_n']+sum(prestress['losses'].values()),3e6)),
               dict(name='S-N interpolation known power-law result',passed=math.isclose(fatigue['miner_damage'],.1,rel_tol=1e-8)),
               dict(name='cyclic friction Coulomb limit',passed=joint['benchmark_passed']),
               dict(name='coupled vehicle moving-force limit',passed=abs(moving['peak_displacement_m']/expected-1.)<.01),
               dict(name='orthotropic native coupon analytical extension',passed=coupon['passed'])]
    report=dict(schema='osr-civil-component-campaign/1',checks=checks,passed=all(c['passed'] for c in checks),
                sources={str((HERE/'config/components.json').relative_to(ROOT)):sha(HERE/'config/components.json')},
                physical_validation=False,physical_release=False)
    write(output/'component-verification.json',report)
    return report


def run(output,*,full=True,search_evaluations=32):
    if output.exists():raise ValueError('programme output already exists')
    if output.resolve().is_relative_to(ROOT) and not output.resolve().is_relative_to(ROOT/'build'):
        raise ValueError('programme outputs inside repository belong under build/')
    output.mkdir(parents=True)
    frozen_sources=dependencies()
    for relative,digest in frozen_sources.items():
        target=output/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/relative).read_bytes())
        if sha(target)!=digest:raise ValueError('source changed during programme preparation')
    study=load(HERE/'config/reference.json')
    requirements=load(HERE/'config/requirements.json');write(output/'requirements-register.json',requirements)
    components=component_campaign(output/'components')
    if not components['passed']:raise ValueError('component verification failed; refinement blocked')
    study_with_records,family_results,registry=families(study)
    write(output/'option-register.json',registry);write(output/'family-screening.json',family_results)
    study25=deepcopy(study);c=candidate(study25['candidates'][1],study25)
    receipt=bim.export(c,study25,output/'assembly/reference25.ifc')
    # Independent CAD-facade volume and IFC net quantities use the same source
    # solids. Neither is a fabrication or reinforcement drawing acceptance.
    cad=assembly_cad(c['definition'],c['foundation'],study25['route_length_m'])
    if not math.isclose(cad.volume/1e9,receipt['source_volume_m3'],rel_tol=1e-9):
        raise ValueError('CAD/IFC source quantity mismatch')
    rates=load(HERE/'config/commercial.json')
    quotes=[commercial.price(candidate(v,study),study,rates) for v in study['candidates']]
    write(output/'commercial.json',quotes)
    from .model import System
    stages=[]
    for scheme in ('simple-span','link-slab','continuous'):
        scenario=deepcopy(study);scenario['connection_scheme']=scheme
        model=System(c,scenario,scenario['ground_scenarios'][0],16)
        stages.append(dict(connection=scheme,quantities=model.quantities,dead=model.responses(),
                           thermal=model.thermal(25.,1e-5),physical_release=False))
    write(output/'construction-continuity-thermal.json',stages)
    vehicle_inputs=dict(sprung_mass_kg=8012.5,unsprung_mass_kg=800.,suspension_n_m=2e6,suspension_ns_m=30000.,contact_n_m=100e6,
                        bridge_damping_ratio=.02,irregularity_amplitude_m=.001,irregularity_wavelength_m=20.,
                        basis='Unverified suspension/contact/irregularity inputs; axle mass matches retained LM3 planning loads')
    section=geometry(c['definition'])['deck'][1]
    coupled=[]
    for step in (.004,.002,.001):
        coupled.append(vehicle.run(30e9*section['inertia_y_m4'],commercial.takeoff(c,study)['fabricated_beam_mass_kg']/25+1500,
                                   25.,study['train']['axle_offsets_m'],vehicle_inputs,dt=step,output=output/f'coupled-vehicle-dt{step:g}.csv'))
    write(output/'coupled-vehicle.json',coupled)
    coupled_convergence={key:abs(coupled[-1][key]/coupled[-2][key]-1.) for key in ('peak_displacement_m','peak_acceleration_m_s2')}
    write(output/'coupled-vehicle-convergence.json',dict(relative_changes=coupled_convergence,
          passed=all(e<=.05 for e in coupled_convergence.values()),relative_limit=.05))
    found=search.run(study,output/'search',evaluations=search_evaluations)
    # Confirm diverse shortlisted shapes with actual-section solids. Linear
    # local verification is distinct from strength/contact/physical validation.
    shortlist=found['shortlist'][:2]
    selected=[load(output/'search/candidates'/f'{identifier}.json') for identifier in shortlist]
    sensitivity=robustness.run([c,*selected],study,output/'uncertainty')
    solid=[]
    for identifier in shortlist:
        design=load(output/'search/candidates'/f'{identifier}.json')
        results=[detailed.run(design,study,size,output/'detailed'/identifier/f'mesh-{size:g}') for size in (.8,.4,.2)]
        profile=load(HERE/'config/components.json')
        curvature=nonlinear.moment_curvature(geometry(design['definition'])['deck'][1]['regions'],profile['concrete'],profile['steel'],
                                             axial_force_n=2.5e6,output=output/'detailed'/identifier/'moment-curvature.csv')
        write(output/'detailed'/identifier/'moment-curvature.json',dict(candidate_id=identifier,**curvature,
              loading_basis='unverified 2.5 MN constant axial prestress scenario; anchorage and tendon detailing not accepted'))
        error=abs(results[-1]['midspan_displacement_m']/results[-2]['midspan_displacement_m']-1.)
        solid.append(dict(candidate_id=identifier,meshes=results,nonlinear_section_status=curvature['status'],relative_displacement_change=error,
                          convergence_passed=error<=.05,physical_release=False))
    write(output/'detailed-confirmation.json',solid)
    protocols=validation.protocols(output/'physical-test-programme',shortlist)
    # Exercise immutable multipart retention and safe retrieval on the complete
    # component evidence; larger native campaigns use the same streaming path.
    storage.pack(output/'components',output/'artifact-store',maximum=1024*1024)
    retrieval=storage.restore(output/'artifact-store',output/'retrieved-components')
    write(output/'retrieval-verification.json',retrieval)
    if full:
        bundle=output/'reference-campaign'
        manifest=run_campaign(HERE/'config/reference.json',bundle)
        proposal=validation.promotion(bundle,output/'promotion')
    else:manifest=None;proposal=None
    audit=[]
    groups={1:'project requirements and actual loads',2:'contracts and lineage',3:'family compatibility/material matrices',
            4:'CAD/IFC and quantities',5:'numerical benchmark domains',6:'native result exchanges',7:'nonlinear pier/soil components',
            8:'moving/thermal/continuity/construction cases',9:'complete package pricing/equipment/lifecycle',10:'runner/CI/artifact retrieval',
            11:'multi-seed constrained search and random baseline',12:'native solids/material/joint refinements',
            13:'physical datasets/tests and independent validation',14:'sealed proposal and existing release gate'}
    for i,label in groups.items():
        audit.append(dict(id=f'C{i:02d}',scope=label,software_delivery='implemented research workflow' if i!=13 else 'implemented test/data workflow',
                          engineering_acceptance='awaiting-external-evidence',complete=False,
                          missing=['named acceptance owner','project-specific measured/approved inputs'] if i not in (13,14) else
                                  ['actual instrumented tests','independent review and authority acceptance']))
    report=dict(schema='osr-civil-programme/1',software_executed=True,all_document_items_complete=False,
                work_packages=audit,component_verification=components,search_summary=found,detailed_summary=solid,
                reference_evaluations=len(manifest['evaluations']) if manifest else 0,
                uncertainty_scenarios=len(robustness.SCENARIOS),ranking_reversals=sensitivity['ranking_reversals'],
                physical_tests_received=0,promotion_status=proposal['status'] if proposal else 'not-run',
                coupled_vehicle_convergence=coupled_convergence,
                numerical_verification_passed=components['passed'] and all(r['convergence_passed'] for r in solid) and all(e<=.05 for e in coupled_convergence.values())
                    and all(r['status']=='within-linear-contact-domain' for r in coupled),
                physical_release=False,source_hashes=frozen_sources,remaining_software_domains=['3D coupled vehicle/track dynamics',
                    'calibrated hybrid bond/contact/creep models','site nonlinear group/scour/seismic model selection'])
    write(output/'programme.json',report)
    if dependencies()!=frozen_sources:
        report['software_executed']=False;report['status']='invalidated-source-change';write(output/'programme.json',report)
        raise ValueError('programme source changed during execution; evidence retained but not accepted as current')
    lines=['# Civil exploration programme audit','','The software workflows below were executed. Engineering acceptance and physical evidence remain open.','',
           '| Work package | Software delivery | Acceptance |','|---|---|---|']
    lines += [f"| {r['id']} — {r['scope']} | {r['software_delivery']} | {r['engineering_acceptance']} |" for r in audit]
    lines += ['',f"Reference evaluation attempts: {report['reference_evaluations']}. Component checks: {len(components['checks'])}.",
              f"Search native designs: {found['unique_native_evaluations']}; {len(solid)} shortlisted packages received three native solid meshes.",
              '', 'No physical test, supplier commitment or independent engineering acceptance has been fabricated.','']
    (output/'programme.md').write_text('\n'.join(lines))
    if not report['numerical_verification_passed']:
        raise ValueError('programme numerical refinement failed; records and audit retained')
    return report
