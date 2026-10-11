"""Join existing catalogue/factory definitions to an executable open programme."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import tomllib
from osr_mech.common import ConsistFamily
from osr_mech.buildable_trainset import buildable_trainset_design,_item_payload,factory_release_work_package_payload
from osr_mech.engineering_definition import validate,fingerprint,catalogue_template
from osr_mech.rolling_stock.inspection_plan import factory_inspection_plan_payload
from osr_mech.rolling_stock.manufacturing_controls import manufacturing_control_payload
from .common import ROOT,load_definition
from .production import traveler_template,assess_traveler
from .assembly import battery_fixture,schedule,tolerance_stack
from .materials import panel_screen,thermal_layers,train_energy
from .commissioning import fault_campaign

DATA=ROOT/'engineering/industrialisation/modernisation'


def build_package(model,pack):
    validate(model);programme=load_definition(DATA/'programme.json');sources=load_definition(DATA/'sources.json')
    design=buildable_trainset_design(ConsistFamily(model['family']));products={p.id:_item_payload(p) for p in design.product_items if p.quantity_per_trainset>0}
    factory=factory_release_work_package_payload(design);inspection=factory_inspection_plan_payload(factory)
    controls=manufacturing_control_payload();allocation=catalogue_template(design)
    known=set(products)|{a.id for a in design.assemblies};source_ids={s['id'] for s in sources['sources']}
    by_part={}
    for row in model['instances']:by_part.setdefault(row['part_id'],[]).append(row['id'])
    features=[]
    for feature in programme['features']:
        if not set(feature['parts'])<=known or feature['source'] not in source_ids:raise ValueError('feature refers to an unknown part or source')
        features.append(dict(**feature,instances=sorted(i for p in feature['parts'] for i in by_part.get(p,[])),
            required_interface_domains=['mechanical','electrical','thermal-fluid','control'],
            evidence_status='open-design/supplier/physical-evidence',engineering_accepted=False))
    passports=[];routes=[]
    with (ROOT/'lib/templates/trainset-manufacturing-methods.toml').open('rb') as f:methods=tomllib.load(f)
    for part,row in sorted(products.items()):
        ownership=[p for p in factory['packages'] if part in p['product_ids']]
        passports.append(dict(material_id=part+'/material',part_id=part,candidate_spec=row['material_spec'],released_grade=None,
            unit=row['unit'],required_evidence=list(row['material_spec']['evidence_required']),
            qualification_domains=['strength/stiffness','fatigue','fire/smoke/toxicity','corrosion/galvanic isolation','temperature/ageing','repair/removal','recycled content and EPD'],
            certificate=None,measured_properties=None,repair_procedure=None,environmental_factors=None,material_accepted=False))
        routes.append(dict(part_id=part,quantity_per_trainset=row['quantity_per_trainset'],unit=row['unit'],
            source_process=row['process_spec'],factory_packages=[p['id'] for p in ownership],
            control_ids=sorted({c for p in ownership for c in p['reference_control_ids']}),
            planning_method_ids=[m['id'] for m in methods['method'] if part in m['product_ids']],
            representation='existing family route pattern; transfer review required',production_data_released=False))
    instances={r['id']:r for r in model['instances']};operations=[];terminal={};preparation={}
    for row in model['instances']:
        identifier=row['id'];item=products.get(row['part_id']);made=item is not None and item['route']=='MAKE'
        special=made and any('weld' in p or 'cure' in p or 'bond' in p for p in item['process_spec']['primary_processes'])
        steps=[('receipt','material receipt / revision / source checks','incoming',['material','drawing'],False),
            ('prepare','qualified fabrication or supplier preparation','fabrication' if made else 'fit',['procedure','measurement'],special),
            ('install','datum fit, isolation and controlled attachment','assembly',['procedure','measurement'],False),
            ('review','independent quality / genealogy / handback','quality',['record'],False)]
        if item is None:
            steps=[('prepare','reconcile residual aggregate with real child allocations','assembly',['drawing','record'],False),
                   ('review','carbody/bogie marriage and full child handback','quality',['record','measurement'],False)]
        previous=None
        for suffix,title,resource,evidence,is_special in steps:
            operation_id=identifier+'/'+suffix
            operations.append(dict(id=operation_id,title=title,instance_id=identifier,part_id=row['part_id'],part_revision=row['revision'],
                serial=row['serial'],batch=row['batch'],resource=resource,predecessors=[] if previous is None else [previous],
                duration_minutes=None,minimum_wait_minutes=None,required_evidence_kinds=evidence,special_process=is_special,
                released_process_window=None,required_competencies=['qualified operator for selected process','independent quality inspector'],
                acceptance_limits=None,drawings_issued=False))
            previous=operation_id
        terminal[identifier]=previous;preparation[identifier]=identifier+'/prepare'
    by_op={o['id']:o for o in operations}
    for row in model['instances']:
        parent=row['parent']
        if parent in instances:
            installation=by_op[row['id']+'/install']
            installation['predecessors'].append(preparation[parent])
            by_op[terminal[parent]]['predecessors'].append(terminal[row['id']])
    # Validate dependency identities and cycles independent of unavailable shop times.
    topology=schedule([dict(o,duration_minutes=1.,minimum_wait_minutes=0.) for o in operations],
        {'incoming':1,'fabrication':1,'fit':1,'assembly':1,'quality':1})
    route_coverage=len(allocation['instances']);unresolved=route_coverage-len({r['id'] for r in allocation['instances'] if r['part_id'] in by_part})
    production=dict(schema='osr-factory-execution-package/1',configuration_sha256=fingerprint(model),family=model['family'],
        state=model['state'],asset_id=model['asset_id'],operations=operations,full_component_coverage=False,
        required_allocation_count=route_coverage,unmapped_part_family_allocation_count=unresolved,
        physical_component_coverage_note='Part-family matches do not resolve kit/area allocations or reconcile every physical slot',
        family_transfer_review_required=model['family']!='light-metro-3car',
        source_factory_packages=[p['id'] for p in factory['packages']],
        topology_validated=len(topology['operations'])==len(operations),planning_times_released=False,production_released=False)
    traveler=traveler_template(production);assessment=assess_traveler(production,traveler)
    fixture=battery_fixture(pack)
    commissioning=fault_campaign()
    design_gates=[dict(id=f['id'],status='open',required_verification=f['verification']) for f in features]
    protocols=dict(schema='osr-industrialisation-protocols/1',quality=programme['quality_protocols'],commissioning=[
        dict(id='OSR-IM-C'+str(i+1).zfill(2),scope=scope,status='unexecuted-physical-protocol') for i,scope in enumerate([
            'wake/sleep/self-diagnosis','door/station/obstacle interlocks','redundant power/control/wiring and common-cause faults',
            'bearing/brake/temperature/communications degraded conditions','depot entry/exit and washing','bounded auxiliary reset and critical lockout',
            'energy/HVAC/acoustic duty and emergency systems','supported full-train dynamic service envelope'])],physical_validation=False)
    paths=[*sorted((ROOT/'engineering/industrialisation').glob('*.py')),DATA/'programme.json',DATA/'sources.json',
        ROOT/'lib/templates/trainset-manufacturing-methods.toml',ROOT/'lib/templates/rolling-stock.toml',
        *sorted((ROOT/'design/component-catalogue/src/osr_mech').rglob('*.py'))]
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    summary=dict(schema='osr-industrialisation-expansion-review/1',configuration_sha256=fingerprint(model),family=model['family'],
        source_sha256=hashes,work_packages=[dict(**w,status='implemented-software-and-protocols',physical_status='open') for w in programme['work_packages']],
        design_feature_count=len(features),material_passport_count=len(passports),process_route_count=len(routes),
        assembly_operation_count=len(operations),factory_package_count=len(factory['packages']),
        existing_first_article_characteristic_count=inspection['characteristic_count'],
        existing_manufacturing_control_count=len(controls['controls']),required_allocation_count=route_coverage,
        fixture_constraint_rank=fixture['checks']['constraint_rank'],blank_traveler_ready_for_review=assessment['ready_for_independent_quality_review'],
        commissioning_contract_checks_passed=commissioning['contract_checks_passed'],
        remaining_physical_gates=programme['open_physical_gates'],production_released=False,physical_validation=False)
    return dict(review=summary,design_requirements=dict(features=features,gates=design_gates),material_passports=passports,
        process_routes=routes,assembly_package=fixture,production_package=production,traveler_template=traveler,
        blank_traveler_assessment=assessment,quality_protocols=protocols,commissioning_protocols=protocols['commissioning'],commissioning_campaign=commissioning,
        source_register=sources,programme=programme)


def demonstrations():
    """Declared synthetic coupons/duties; none are selected supplier properties."""
    geometry=dict(length_m=.2,width_m=.4,thickness_m=.004);demand=dict(tip_force_n=100.,deflection_limit_m=.002)
    candidates=[dict(id='research-steel',density_kg_m3=7850.,longitudinal_modulus_pa=210e9,allowable_stress_pa=None),
                dict(id='research-aluminium',density_kg_m3=2700.,longitudinal_modulus_pa=70e9,allowable_stress_pa=None),
                dict(id='research-gfrp',density_kg_m3=1900.,longitudinal_modulus_pa=20e9,allowable_stress_pa=None)]
    duty=[dict(duration_s=30.,speed_start_m_s=0.,speed_end_m_s=15.,grade_ratio=0.,aerodynamic_force_n=1000.),
          dict(duration_s=60.,speed_start_m_s=15.,speed_end_m_s=15.,grade_ratio=0.,aerodynamic_force_n=1000.),
          dict(duration_s=30.,speed_start_m_s=15.,speed_end_m_s=0.,grade_ratio=0.,aerodynamic_force_n=1000.)]
    energy={str(e):train_energy(duty,200000.,e,.7,80000.,.002) for e in (.9,.95)}
    example_ops=[dict(id='prepare',predecessors=[],duration_minutes=10.,minimum_wait_minutes=0.,resource='fit'),
        dict(id='bond',predecessors=['prepare'],duration_minutes=15.,minimum_wait_minutes=0.,resource='bond'),
        dict(id='inspect-after-hold',predecessors=['bond'],duration_minutes=10.,minimum_wait_minutes=60.,resource='quality')]
    return dict(basis='Synthetic method-verification examples; not released OSR material grades, cure recipes, duty or efficiency maps',
        material_screening=[panel_screen(c,geometry,demand) for c in candidates],energy_comparison=energy,
        thermal_screening=thermal_layers([dict(thickness_m=.02,conductivity_w_m_k=.04)],1.,30.),
        planning_schedule=schedule(example_ops,dict(fit=1,bond=1,quality=1)),
        material_selected=None,manufacturer_saving_claim_verified=False,physical_validation=False)
