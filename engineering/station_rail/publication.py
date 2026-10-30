"""Reproducible v0.6 reference publication; cities remain geographically indexed holds."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
from decimal import Decimal, ROUND_HALF_EVEN
import fcntl,gzip,io,json,os,shutil,subprocess,sys,tarfile,tempfile
from . import ROOT,FLAGS
from .common import encoded,identity,digest
from . import evaluation,exports,cities,comparison,figures
from .evaluation import IDS
OUTPUT='docs/design-engine/current'
WORKBENCH='docs/workbench/current'

def write(path,raw):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.tmp');tmp.write_bytes(raw);os.replace(tmp,path)
def archive(folder):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode='w') as tar:
        for p in sorted(Path(folder).rglob('*')):
            if p.is_file():
                data=p.read_bytes();item=tarfile.TarInfo(p.relative_to(folder).as_posix());item.size=len(data);item.mtime=0;item.mode=0o644;tar.addfile(item,io.BytesIO(data))
    return gzip.compress(raw.getvalue(),mtime=0)
def extract(path,folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    with tarfile.open(path) as tar:
        members=tar.getmembers()
        if sum(m.size for m in members)>512*1024**2:raise ValueError('bounded native archive required')
        for member in members:
            name=Path(member.name)
            if name.is_absolute() or '..' in name.parts or not(member.isfile() or member.isdir()):raise ValueError('ordinary relative native files required')
            if member.isfile():write(folder/name,tar.extractfile(member).read())
    return folder

def verify_package(path,root=ROOT):
    path=Path(path);m=json.loads((path/'manifest.json').read_bytes())
    if m.get('manifest_id')!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('native package identity differs')
    for name,expected in m['source_sha256'].items():
        if digest(Path(root)/name)!=expected:raise ValueError('native source differs: '+name)
    actual={p.relative_to(path).as_posix():digest(p) for p in path.rglob('*') if p.is_file() and p.relative_to(path).as_posix()!='manifest.json'}
    if actual!=m['files_sha256']:raise ValueError('native payload differs')
    if any(m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('native result cannot grant release')
    result=json.loads((path/'result.json').read_bytes())
    if any(result.get(k) is not v for k,v in FLAGS.items()):raise ValueError('native result disposition differs')
    if result.get('schema')=='osr-station-rail-native/1':
        from .vehicle import build
        v=build(root);cad=result['CAD']
        if (abs(cad['native_material_kg']-v['mass']['located_material_kg'])>1e-5
            or cad['part_count']!=len(v['geometry_parts']) or not cad['all_part_volumes_match']
            or not cad['reopened_volume_matches']):raise ValueError('Native CAD does not match selected material')
    if result.get('schema')=='osr-native-LIM-secondary-diffusion/1':
        if result['candidate_force_map'] is not False or result['actual_primary_current_map'] is not False:
            raise ValueError('A manufactured slab cannot qualify a complete motor')
        cases=result['cases']
        if [(c['nx'],c['ny']) for c in cases]!=[(40,4),(80,8),(160,16)]:raise ValueError('Native refinement case inventory differs')
        if result['convergence_screen']!='pass' or cases[-1]['relative_force_error']>=.02:raise ValueError('Native diffusion convergence does not pass')
    return result

def native_package(name,record,root=ROOT,output=None,provided=None):
    from . import native,controls
    root=Path(root);output=root/OUTPUT if output is None else Path(output)
    if name=='vehicle':check=lambda path:native.verify(path,root)
    elif name=='controls':check=lambda path:controls.verify(path,record,root)
    else:check=lambda path:verify_package(path,root)
    candidates=[]
    if provided:candidates.append(Path(provided))
    candidates += [root/'build/v06-development'/('native-vehicle-final' if name=='vehicle' else 'native-secondary-final' if name=='drive' else 'native-controls-'+record['evaluation_id'][:16]+'-'+identity(controls.sources(root))[:12])]
    for path in candidates:
        if (path/'manifest.json').is_file():
            try:check(path)
            except(ValueError,OSError,KeyError):
                if provided:raise
            else:return path
    retained=output/('native-'+name+'.tar.gz')
    if retained.is_file():
        target=root/'build/v06-development/cache'/('native-'+name+'-'+digest(retained)[:16])
        if not (target/'manifest.json').is_file():extract(retained,target)
        try:check(target)
        except (ValueError,OSError,KeyError):pass
        else:return target
    if name=='controls':
        target=candidates[-1]
        controls.run(target,record,root);check(target);return target
    raise ValueError('Required native '+name+' package unavailable; execute its source-bound worker into a fresh run directory')

def sources(root,record,index,delivery):
    root=Path(root);maps=[record['source_sha256'],index['source_sha256'],delivery['source_sha256']]
    names=['AGENTS.md','README.md','VERSION','Cargo.toml','Cargo.lock','package.json','package-lock.json','docs/ROADMAP.md','docs/ARCHITECTURE.md',
        'docs/first-adoptable-product.md','docs/open-source-rail-overview.md','docs/open-source-rail-overview.html','CONTRIBUTING.md',
        'deployment/erpnext/README.md','deployment/supervision/README.md','tools/README.md','crates/README.md','cities/catalogue/README.md',
        'tools/automation/generate-public-overview.py','tools/automation/generate-doc-index.py','tools/automation/check-readmes.py','docs/INDEX.md',
        'engineering/development-baseline.toml','engineering/readme_context.py','engineering/requirements.txt','.github/repository-metadata.yml','osr','install.sh',
        '.github/workflows/development-baseline.yml','tools/automation/default-design.py','tools/automation/default-design-workbench.py',
        'tools/automation/default-design-cycle.py','tools/automation/tests/verify-development-baseline.mjs','tools/automation/v06-native-benchmarks.py',
        'docs/design-engine/sourcing/README.md','docs/design-engine/sourcing/validation.json',
        'docs/design-engine/sourcing/validation-current.json',
        'engineering/sourcing/catalogue.py','engineering/sourcing/model.py',
        'engineering/sourcing/data/supplier-catalogue.json','engineering/sourcing/data/public-feeds.json',
        'tools/automation/architecture-native-benchmarks.py','tools/automation/generative-native-benchmarks.py',
        'tools/automation/coupled-native-benchmarks.py','tools/automation/moving-lim-benchmarks.py']
    names += [p.relative_to(root).as_posix() for p in (root/'engineering/sourcing').rglob('*')
        if p.is_file() and p.suffix in ('.py','.json','.md','.html','.js','.css')
        and 'tests' not in p.parts and '__pycache__' not in p.parts]
    names += [p.relative_to(root).as_posix() for p in (root/'docs/design-engine/sourcing/domestic-fabrication').rglob('*')
        if p.is_file() and '__pycache__' not in p.parts]
    names += [p.relative_to(root).as_posix() for p in (root/'docs/design-engine/sourcing/procurement-bom').rglob('*')
        if p.is_file() and '__pycache__' not in p.parts]
    names += ['campaigns/end-to-end-railway-closure.toml',
        'campaigns/practical-launch-comparison.toml','engineering/design_search/launch_options.py',
        'campaigns/simple-affordable-propulsion.toml','engineering/design_search/propulsion_layout.py',
        'campaigns/station-accelerator-development.toml','engineering/design_search/station_accelerators.py',
        'campaigns/end-to-end-digital-twin.toml','osr-twin',
        'campaigns/engineering-completion.toml','osr-complete','.github/workflows/engineering-closure.yml',
        'campaigns/sourced-reference-cell.toml','osr-cell','.github/workflows/reference-cell.yml',
        'tools/automation/reference-cell-geometry.py',
        'services/integration/osr_integration/reference_cell.py',
        'engineering/design_search/propulsion_storage.py','engineering/design_search/sparse_launch.py',
        'engineering/design_search/data/skeleton-102v94f-catalogue.json','engineering/design_search/data/tsa-type-x-drive-lead.json',
        'engineering/design_search/demonstration.py','engineering/design_search/route_bundle.py',
        'engineering/design_search/equipped_candidates.py','engineering/design_search/moving_lim.py',
        'engineering/design_search/moving_lim_publication.py','engineering/design_search/lim_transport.py',
        'engineering/design_search/fault_response.py','engineering/design_search/lim_critical_mesh.py',
        'engineering/design_search/test_readiness.py','engineering/design_search/data/wheel-LIM-test-program.json',
        'engineering/design_search/lim_static_benchmark.py','engineering/design_search/lim_static_publication.py']
    names += ['engineering/mass_ledger_audit.py',
        'docs/design-engine/mass-reconciliation/current/README.md',
        'docs/design-engine/mass-reconciliation/current/mass-ledger.json.gz',
        'docs/design-engine/mass-reconciliation/current/summary.json',
        'docs/design-engine/mass-reconciliation/current/manifest.json']
    for directory in ('engineering/station_rail','engineering/development_baseline'):
        names += [p.relative_to(root).as_posix() for p in (root/directory).rglob('*') if p.is_file() and p.suffix in ('.py','.toml','.js','.html','.css') and '__pycache__' not in p.parts]
    for directory in ('docs/assets/v0.6','docs/images/v06'):
        names += [p.relative_to(root).as_posix() for p in (root/directory).rglob('*') if p.is_file()]
    followup=root/'docs/design-engine/v06-physical-closure'
    if followup.is_dir():names += [p.relative_to(root).as_posix() for p in sorted(followup.iterdir()) if p.is_file()]
    names += [p.relative_to(root).as_posix() for p in (root/'engineering/railway_twin').glob('*.py')]
    names += [p.relative_to(root).as_posix() for p in (root/'engineering/railway_completion').glob('*.py')]
    for current_package in ('engineering/component_registry','engineering/reference_cell'):
        names += [p.relative_to(root).as_posix() for p in (root/current_package).rglob('*') if p.is_file() and p.suffix in ('.py','.json','.html','.js','.css') and 'tests' not in p.parts and '__pycache__' not in p.parts]
    for folder in ('v06-optimisation','v06-design-space','v06-architecture','v06-adaptive-design','generative-structure','coupled-railway','railway-closure','moving-lim-method','practical-launch','propulsion-layout','station-accelerators','digital-twin','engineering-closure','reference-cell'):
        campaign_folder=root/'docs/design-engine'/folder
        if campaign_folder.is_dir():names += [p.relative_to(root).as_posix() for p in sorted(campaign_folder.rglob('*')) if p.is_file()]
        if folder=='coupled-railway' and (campaign_folder/'manifest.json').is_file():maps.append(json.loads((campaign_folder/'manifest.json').read_bytes()).get('source_sha256',{}))
    return evaluation.merge(*maps,{n:digest(root/n) for n in sorted(set(names))})

def compact(record,index,natives,delivery):
    value=evaluation.summary(record);value.update(cities=dict(city_count=index['city_count'],summary=index['summary'],
        baghdad=None,default_city='baghdad',index_path=OUTPUT+'/cities.json',longest_gap=index['longest_gap']),
        native=dict(controls=natives['controls']['controls'],all_controls_pass=natives['controls']['all_controls_pass'],
            CAD=natives['vehicle']['CAD'],underframe_fixtures=natives['vehicle']['underframe_fixtures'],
            drive_convergence=natives['drive']['convergence_screen'],
            scope='Actual FreeCAD/STEP export and reopen, limited CalculiX underframe fixtures, GetDP manufactured conductive-slab convergence and Rust ATP/interface regressions. No complete physical train journey.',
            physical_train_simulated=False),known_gate_counts=dict(Counter(g['state'] for g in record['gates'])),
        current_outputs=dict(exports=OUTPUT+'/exports/manifest.json',reader='OpenSourceRail-Book.pdf',physical_followup='docs/design-engine/v06-physical-closure/README.md',
            mass_reconciliation='docs/design-engine/mass-reconciliation/current/README.md'),
        economics_acceptance='unknown',city_performance_packages_written=0)
    return value

def _sourcing_section(root,record):
    root=Path(root)
    validation=json.loads((root/'docs/design-engine/sourcing/validation-current.json').read_bytes())
    from engineering.sourcing.catalogue import load_catalogue
    from engineering.sourcing.model import identity as sourcing_identity
    catalogue=load_catalogue((root/'engineering/sourcing/data/supplier-catalogue.json',
                              root/'engineering/sourcing/data/public-feeds.json',
                              root/'engineering/sourcing/data/iraq-domestic-2026-july.json'))
    counts=validation.get('catalogue',{}).get('counts',{})
    if (validation.get('schema')!='osr-sourcing-current-validation/1'
        or validation.get('source_epoch_id')!=sourcing_identity(catalogue)
        or validation.get('catalogue',{}).get('offline_seed_record_count')!=len(catalogue)
        or counts.get('total')!=len(catalogue)):
        raise ValueError('Current sourcing validation does not match its offline catalogue epoch')
    # The compact current index names immutable packets. Resolve and validate
    # those packets here; validation.json remains the earlier 513-record snapshot.
    validation['source_epoch_sha256']=validation['source_epoch_id']
    validation['packets']=validation['review_packets']
    frame=validation['packets']['frame_vehicle']
    federated=validation['packets']['federated_manufacturing_groups']
    takeoff_path=root/'docs/design-engine/sourcing/material-takeoff/federated-v06-stock-takeoff-v5.json.gz'
    takeoff_packet=json.loads(gzip.decompress(takeoff_path.read_bytes()))
    takeoff_summary=takeoff_packet.get('summary',{})
    concrete_rollup=next((row for row in takeoff_packet.get('material_rollups',[])
                          if row.get('system')=='civil/concrete'
                          and row.get('material')=='concrete-hypothesis'
                          and row.get('stock_scope')=='nominal-stock'),{})
    takeoff={
        'path':'material-takeoff/federated-v06-stock-takeoff-v5.json.gz',
        'takeoff_id':takeoff_packet.get('takeoff_id'),
        'candidate_id':takeoff_packet.get('candidate_id'),
        'evaluation_id':takeoff_packet.get('evaluation_id'),
        'source_input_id':takeoff_packet.get('source_input_id'),
        'manufacturing_group_count':takeoff_summary.get('groups_with_known_gross_stock_mass'),
        'located_occurrence_count':takeoff_summary.get('located_occurrence_count'),
        'unlocated_account_count':takeoff_summary.get('unlocated_account_count'),
        'known_gross_stock_mass_kg':takeoff_summary.get('known_gross_stock_mass_kg'),
        'concrete_nominal_stock_volume_m3':concrete_rollup.get('nominal_stock_volume_m3'),
    }
    proc_index=validation.get('procurement_package_bom', {})
    procurement_path=root/proc_index.get('path', '')
    if not proc_index or not procurement_path.is_file():
        raise ValueError('Candidate procurement-package packet is missing')
    procurement_packet=json.loads(gzip.decompress(procurement_path.read_bytes()))
    sensitivity=validation.get('candidate_sourcing_sensitivity',{})
    if (sensitivity.get('schema')!='osr-candidate-sourcing-sensitivity/1'
        or sensitivity.get('procurement_packet_id')!=procurement_packet.get('packet_id')
        or sensitivity.get('candidate_id')!=procurement_packet.get('candidate_id')
        or sensitivity.get('evaluation_id')!=procurement_packet.get('evaluation_id')
        or sensitivity.get('source_input_id')!=procurement_packet.get('source_input_id')
        or sensitivity.get('sensitivity_id')!=sourcing_identity(
            {key:value for key,value in sensitivity.items() if key!='sensitivity_id'})):
        raise ValueError('Candidate sourcing sensitivity is not bound to the exact procurement packet')
    sensitivity_rank_text='; '.join(
        f"{row['scenario_spread_rank']}. {row['system']}/{row['material']}: "
        f"IQD {Decimal(row['scenario_spread_iqd'])/Decimal(1_000_000):,.2f}m spread"
        for row in sensitivity.get('ranked_partial_scenario_exposures',[]))
    sensitivity_unranked_count=len(sensitivity.get('unranked_scopes',[]))
    if (sensitivity.get('summary',{}).get('selection_margin') is not None
        or sensitivity.get('summary',{}).get('could_change_preferred') is not None
        or sensitivity.get('summary',{}).get('expected_value_of_information') is not None
        or sensitivity.get('summary',{}).get('unknown_is_zero') is not False):
        raise ValueError('Candidate sourcing sensitivity cannot infer preference or treat unknowns as zero')
    regional_index=validation.get('domestic_fabrication',{}).get('regional_cost_reference_2026_09',{})
    regional_packet_path=root/regional_index.get('path','')
    if not regional_index or not regional_packet_path.is_file():
        raise ValueError('September 2026 regional domestic-cost packet is missing')
    regional_packet=json.loads(regional_packet_path.read_bytes())
    regional_manifest_path=regional_packet_path.parent/'manifest.json'
    if not regional_manifest_path.is_file():
        raise ValueError('September 2026 regional cost manifest is missing')
    regional_manifest=json.loads(regional_manifest_path.read_bytes())
    regional_path=regional_index['path'].removeprefix('docs/design-engine/sourcing/')
    regional={**regional_index,
        'path':regional_path,
        'unit_rate_scenario_count':regional_index['regional_unit_rate_scenario_count'],
        'candidate_mapped_aluminium_scenario_count':regional_index['candidate_mapped_aluminium_stock_scenario_count'],
        'candidate_mapped_aluminium_rollup_count':2,
        'regional_concrete_takeoff_estimates':regional_packet.get('regional_concrete_takeoff_estimates',[]),
    }
    procurement={
        **proc_index,
        'path':proc_index['path'],
        'regional_cost_reference_path':regional_path,
        'regional_cost_reference_packet_id':regional_index['packet_id'],
        'domestic_cost_estimate_scenario_count':procurement_packet['summary']['domestic_cost_estimate_scenario_count'],
        'linked_unlocated_obligation_count':procurement_packet['summary']['linked_unlocated_obligation_count'],
        'unlinked_unlocated_obligation_count':procurement_packet['summary']['unlinked_unlocated_obligation_count'],
        'unlocated_obligation_package_association_count':procurement_packet['summary']['unlocated_obligation_package_association_count'],
        'material_demand_line_count':procurement_packet['summary']['material_demand_line_count'],
        'domestic_source_lead_association_count':sum(
            row.get('domestic_fabrication_lead_count',0)
            for row in procurement_packet.get('material_purchasing_lines',[])),
    }
    procurement_relative_path=Path(procurement['path']).relative_to(
        Path('docs/design-engine/sourcing')).as_posix()
    concrete=[{
        'path':f"domestic-fabrication/estimates/current/concrete-batch-{int(row['labour_hours_per_output']):02d}h-current.json",
        'candidate_id':row['process']['candidate_id'],
        'estimated_unit_cost':row['process']['estimated_unit_cost'],
        'wage_observation_period':'2026-09',
    } for row in regional_packet.get('unit_rate_estimates',[])
      if row.get('region_slug')=='baghdad' and row.get('family')=='concrete batching']
    mapped_concrete=[{
        'estimate_packet_id':row['estimate_packet_id'],
        'process_record_id':row['process_record_id'],
        'candidate_id':regional_packet['candidate_id'],
        'source_input_id':regional_packet['source_input_id'],
        'takeoff_id':regional_packet['takeoff_id'],
        'region':row['region'],
        'labour_hours_per_m3':row['labour_hours_per_nominal_m3'],
        'estimated_unit_cost':row['estimated_unit_cost_iqd_per_nominal_m3'],
        'estimated_total':row['estimated_total_iqd'],
        'mapped_group_count':row['mapped_group_count'],
        'mapped_occurrence_count':row['mapped_occurrence_count'],
        'path':row['estimate_file'],
    } for row in regional_packet.get('regional_concrete_takeoff_estimates',[])]
    historical_path='domestic-fabrication/regional-estimates-2025-v6/iraq-domestic-cost-reference-2025.json'
    historical_packet_path=root/'docs/design-engine/sourcing'/historical_path
    if not historical_packet_path.is_file():
        raise ValueError('Historical regional domestic-cost packet is missing')
    historical_packet=json.loads(historical_packet_path.read_bytes())
    historical_regional={
        'path':historical_path,
        'packet_id':historical_packet['packet_id'],
        'candidate_id':historical_packet['candidate_id'],
        'unit_rate_scenario_count':len(historical_packet.get('unit_rate_estimates',[])),
        'baghdad_concrete_takeoff_estimates':historical_packet.get('baghdad_concrete_takeoff_estimates',[]),
    }
    validation['domestic_fabrication_unit_rate_screens']=concrete
    validation['candidate_mapped_concrete_estimates']=mapped_concrete
    validation['regional_cost_reference']=historical_regional
    validation['regional_cost_reference_2026_09']=regional
    gfrp_index=validation['domestic_fabrication']['gfrp_local_fabrication_screen']
    validation['gfrp_local_fabrication_cost_screen']={
        **gfrp_index,
        'path':gfrp_index['path'].removeprefix('docs/design-engine/sourcing/'),
    }
    validation['procurement_package_bom']=procurement
    obligation_links=procurement_packet.get('unlocated_obligation_links', {})
    all_unlocated=set(procurement_packet.get('unlocated_obligation_ids', []))
    linked_ids=set()
    package_ids={row.get('package_id') for row in procurement_packet.get('packages', [])}
    link_integrity=True
    association_count=0
    for link in obligation_links.get('links', []):
        ids=link.get('unlocated_obligation_ids', [])
        targets=link.get('related_package_ids', [])
        if (not isinstance(ids, list) or not isinstance(targets, list)
            or not ids or not targets or len(ids)!=len(set(ids))
            or len(targets)!=len(set(targets))
            or any(value not in all_unlocated for value in ids)
            or linked_ids.intersection(ids)
            or any(value not in package_ids for value in targets)
            or link.get('association_is_package_membership') is not False
            or link.get('allocated_to_package_mass_or_quantity') is not False
            or link.get('quantity') is not None or link.get('priced') is not False
            or link.get('link_id')!=sourcing_identity({key:value for key,value in link.items() if key!='link_id'})):
            link_integrity=False
            break
        linked_ids.update(ids)
        association_count+=len(targets)
    unlinked_ids=set(obligation_links.get('unlinked_obligation_ids', []))
    if (procurement_packet.get('schema')!='osr-procurement-package-bom/1'
        or procurement_packet.get('packet_id')!=sourcing_identity(
            {key:value for key,value in procurement_packet.items() if key!='packet_id'})
        or procurement_packet.get('packet_id')!=procurement.get('packet_id')
        or procurement_packet.get('candidate_id')!=federated['candidate_id']
        or procurement_packet.get('source_input_id')!=takeoff.get('source_input_id')
        or procurement_packet.get('draft_package_count')!=procurement.get('draft_package_count')
        or procurement_packet.get('regional_cost_reference_packet_id')!=procurement.get('regional_cost_reference_packet_id')
        or procurement_packet.get('domestic_cost_estimate_scenario_count')!=procurement.get('domestic_cost_estimate_scenario_count')
        or obligation_links.get('all_source_obligations_preserved') is not True
        or obligation_links.get('source_obligation_count')!=len(all_unlocated)
        or obligation_links.get('linked_unique_obligation_count')!=procurement.get('linked_unlocated_obligation_count')
        or obligation_links.get('unlinked_obligation_count')!=procurement.get('unlinked_unlocated_obligation_count')
        or obligation_links.get('package_association_count')!=procurement.get('unlocated_obligation_package_association_count')
        or obligation_links.get('package_association_count')!=association_count
        or obligation_links.get('linked_unique_obligation_count')!=len(linked_ids)
        or len(obligation_links.get('unlinked_obligation_ids', []))!=len(unlinked_ids)
        or len(all_unlocated)!=procurement_packet.get('unlocated_obligation_count')
        or obligation_links.get('links_are_non_additive') is not True
        or not link_integrity
        or linked_ids.intersection(unlinked_ids)
        or linked_ids.union(unlinked_ids)!=all_unlocated
        or not procurement_packet.get('all_located_occurrences_assigned_exactly_once')):
        raise ValueError('Candidate procurement packages do not match their sealed source and coverage index')
    if not (root/'docs/design-engine/sourcing'/procurement.get('regional_cost_reference_path', '')).is_file():
        raise ValueError('Linked regional domestic-cost reference is missing')
    regional_packet_path=root/'docs/design-engine/sourcing'/regional.get('path', '')
    if takeoff['candidate_id']!=federated['candidate_id']:
        raise ValueError('Sourcing takeoff and federated evaluation candidate identities differ')
    if len(concrete)!=3 or any(row['candidate_id']!=federated['candidate_id'] for row in concrete):
        raise ValueError('September 2026 concrete screens must retain their research candidate identity')
    concrete_rates=sorted(int(row['estimated_unit_cost']) for row in concrete)
    selected_id=record['candidate_id']
    identity_note=(f"The current selected physical candidate is `{selected_id}`. The frame and federated sourcing runs instead use research candidates `{frame['candidate_id']}` and `{federated['candidate_id']}`. Their matching results, takeoff and cost screens do not transfer to the selected reference candidate."
        if selected_id!=federated['candidate_id'] else
        f"The federated sourcing run uses the selected physical candidate `{selected_id}`.")
    c=validation['catalogue']['counts']
    catalogue_line=(f"The current sourcing seed contains **{c['total']} immutable records**: {c['source']} sources, {c['product']} product observations, {c['offer']} published price offers, {c['fx']} FX observations and {c['benchmark']} benchmarks.")
    if len(mapped_concrete)!=6 or any(row['candidate_id']!=federated['candidate_id'] for row in mapped_concrete):
        raise ValueError('Mapped concrete scenarios must retain the takeoff research candidate identity')
    mapped_by_case={(row.get('region'),str(row.get('labour_hours_per_m3'))):row for row in mapped_concrete}
    regional_mapped=regional.get('regional_concrete_takeoff_estimates', [])
    regional_by_case={(row.get('region'),str(row.get('labour_hours_per_nominal_m3'))):row for row in regional_mapped}
    if (regional.get('candidate_id')!=federated['candidate_id']
        or regional.get('takeoff_id')!=takeoff.get('takeoff_id')
        or len(regional_mapped)!=6
        or set(mapped_by_case)!=set(regional_by_case)
        or any(row.get('candidate_id')!=federated['candidate_id'] for row in mapped_concrete)):
        raise ValueError('Regional cost scenarios must remain bound to the takeoff research candidate')
    for key,estimate in mapped_by_case.items():
        regional_estimate=regional_by_case[key]
        estimate_packet=json.loads((regional_packet_path.parent/regional_estimate['estimate_file']).read_bytes())
        if (estimate.get('estimate_packet_id')!=regional_estimate.get('estimate_packet_id')
            or estimate.get('process_record_id')!=regional_estimate.get('process_record_id')
            or estimate.get('estimated_unit_cost')!=regional_estimate.get('estimated_unit_cost_iqd_per_nominal_m3')
            or estimate.get('estimated_total')!=regional_estimate.get('estimated_total_iqd')
            or estimate.get('mapped_group_count')!=regional_estimate.get('mapped_group_count')
            or estimate.get('mapped_occurrence_count')!=regional_estimate.get('mapped_occurrence_count')
            or estimate.get('mapped_group_count')!=81 or estimate.get('mapped_occurrence_count')!=486
            or estimate_packet.get('candidate_id')!=federated['candidate_id']
            or estimate_packet.get('estimate_packet_id')!=estimate.get('estimate_packet_id')
            or estimate_packet.get('estimate',{}).get('record_id')!=estimate.get('process_record_id')
            or estimate_packet.get('estimate',{}).get('estimated_total')!=estimate.get('estimated_total')
            or estimate_packet.get('estimate',{}).get('candidate_takeoff_id')!=takeoff.get('takeoff_id')):
            raise ValueError('September regional and candidate-mapped concrete quantities differ')
    regional_count=len(regional_packet.get('unit_rate_estimates', []))
    aluminium_scenarios=regional_packet.get('candidate_mapped_aluminium_stock_scenarios', [])
    expected_aluminium_materials={
        'aluminium_reference':('vehicle/body','nominal-stock'),
        '6082-T6-proposed':('vehicle/passive-secondary','nominal-stock'),
    }
    expected_aluminium_forms={
        'Non-oxidized aluminium profiles','Oxidized aluminium profiles',
        'Spray-painted aluminium profiles','Hard aluminium sheet, 0.6–0.9 mm',
        'Hard aluminium sheet, 1 mm and above','Annealed aluminium sheet, 0.6–0.9 mm',
        'Annealed aluminium sheet, 1 mm and above',
    }
    expected_aluminium_cases={(material, form, hours)
        for material in expected_aluminium_materials
        for form in expected_aluminium_forms for hours in ('8','16','32')}
    actual_aluminium_cases=set()
    takeoff_path=root/'docs/design-engine/sourcing'/takeoff['path']
    material_takeoff=json.loads(gzip.decompress(takeoff_path.read_bytes()))
    rollups={(row.get('system'),row.get('material'),row.get('stock_scope')):row
             for row in material_takeoff.get('material_rollups',[])}
    benchmarks_by_id={row['record_id']:row for row in catalogue if row.get('kind')=='benchmark'}
    aluminium_totals={material:[] for material in expected_aluminium_materials}
    for scenario in aluminium_scenarios:
        material=scenario.get('material')
        form=scenario.get('material_form')
        hours=str(scenario.get('labour_hours_per_stock_tonne'))
        case=(material,form,hours)
        if case in actual_aluminium_cases:
            raise ValueError('Candidate aluminium stock sensitivity duplicates a material/form/hour case')
        actual_aluminium_cases.add(case)
        process=scenario.get('process',{})
        system,stock_scope=expected_aluminium_materials.get(material,(None,None))
        expected_rollup=rollups.get((system,material,stock_scope))
        if expected_rollup is None:
            raise ValueError('Candidate aluminium sensitivity targets an unknown material takeoff roll-up')
        mass_kg=Decimal(expected_rollup['known_gross_stock_mass_kg'])
        tonnes=mass_kg/Decimal(1000)
        if (scenario.get('region_slug')!='baghdad'
            or form not in expected_aluminium_forms
            or hours not in {'8','16','32'}
            or process.get('candidate_id')!=federated['candidate_id']
            or process.get('input_id')!=takeoff['source_input_id']
            or process.get('candidate_takeoff_id')!=takeoff['takeoff_id']
            or process.get('candidate_takeoff_scope')!={'system':system,'material':material,'stock_scope':stock_scope}
            or process.get('candidate_takeoff_group_count')!=expected_rollup['manufacturing_group_count']
            or process.get('candidate_takeoff_occurrence_count')!=expected_rollup['engineering_occurrence_count']
            or Decimal(process.get('candidate_takeoff_gross_mass_kg','-1'))!=mass_kg
            or Decimal(process.get('candidate_takeoff_mass_reconciliation_residual_kg','-1'))!=0
            or Decimal(process.get('output_quantity','-1'))!=tonnes
            or process.get('candidate_takeoff_mapped') is not True
            or process.get('candidate_takeoff_quantity_basis','').find('purchase yield')<0
            or process.get('uplift_fraction')!='0.2'
            or process.get('complete_process_cost') is not None
            or process.get('complete_installed_cost') is not None
            or process.get('whole_life_cost') is not None
            or process.get('unknown_is_zero') is not False):
            raise ValueError('Candidate aluminium mass/form estimate differs from exact source roll-up or open-cost boundary')
        material_lines=process.get('material_lines',[])
        labour_lines=process.get('labour_lines',[])
        if len(material_lines)!=1 or len(labour_lines)!=1:
            raise ValueError('Candidate aluminium screen must show one exact stock and wage line')
        material_line,labour_line=material_lines[0],labour_lines[0]
        material_benchmark=benchmarks_by_id.get(material_line.get('benchmark_id'))
        wage_benchmark=benchmarks_by_id.get(labour_line.get('benchmark_id'))
        expected_wage=next((row for row in catalogue if row.get('kind')=='benchmark'
            and row.get('benchmark_key')=='iq-cso-2026-09:baghdad:wage:skilled:hour-8h-day'),None)
        if (material_benchmark is None or wage_benchmark is None or expected_wage is None
            or wage_benchmark.get('record_id')!=expected_wage.get('record_id')
            or material_benchmark.get('quantity_unit')!='t'
            or material_benchmark.get('unit_price')!=material_line.get('unit_rate')
            or wage_benchmark.get('quantity_unit')!='h'
            or wage_benchmark.get('unit_price')!=labour_line.get('unit_rate')
            or Decimal(material_line.get('quantity','-1'))!=tonnes
            or Decimal(labour_line.get('person_hours','-1'))!=tonnes*Decimal(hours)):
            raise ValueError('Candidate aluminium material/wage extensions lack exact source benchmark correspondence')
        direct=tonnes*Decimal(material_benchmark['unit_price'])+tonnes*Decimal(hours)*Decimal(wage_benchmark['unit_price'])
        expected_total=direct*Decimal('1.20')
        if (Decimal(process.get('direct_cost','-1'))!=direct
            or Decimal(process.get('uplift_amount','-1'))!=direct*Decimal('0.20')
            or Decimal(process.get('estimated_total','-1'))!=expected_total
            or Decimal(scenario.get('estimated_total_iqd','-1'))!=expected_total
            or Decimal(scenario.get('estimated_unit_cost_iqd_per_tonne','-1'))!=expected_total/tonnes):
            raise ValueError('Candidate aluminium material + labour + 20% arithmetic differs')
        aluminium_totals[material].append(expected_total)
    if actual_aluminium_cases!=expected_aluminium_cases or len(aluminium_scenarios)!=42:
        raise ValueError('Candidate aluminium raw-stock form/hour scenario coverage differs')
    if (regional_count != regional.get('unit_rate_scenario_count')
        or regional_packet.get('packet_id') != regional.get('packet_id')
        or regional_packet.get('packet_id') != regional_manifest.get('packet_id')
        or regional_packet.get('candidate_id') != federated['candidate_id']
        or regional_packet.get('source_epoch_id')!=validation.get('source_epoch_sha256')
        or regional_manifest.get('candidate_takeoff_scenario_count')!=6
        or regional_manifest.get('mapped_group_count')!=81
        or regional_manifest.get('mapped_occurrence_count')!=486
        or regional_manifest.get('candidate_mapped_aluminium_scenario_count')!=42
        or regional_manifest.get('candidate_mapped_aluminium_rollup_count')!=2
        or regional.get('candidate_mapped_aluminium_scenario_count')!=42
        or regional.get('candidate_mapped_aluminium_rollup_count')!=2
        or regional_packet.get('complete_installed_cost') is not None
        or regional_packet.get('physical_qualification') is not None
        or regional_packet.get('unknown_is_zero') is not False
        or regional_manifest.get('manifest_id')!=sourcing_identity({k:v for k,v in regional_manifest.items() if k!='manifest_id'})):
        raise ValueError('Regional material/labour scenario index differs from its candidate-bound packet')
    expected_regional_files=regional_manifest.get('file_sha256',{})
    if (len(expected_regional_files)!=20
        or any(not (regional_packet_path.parent/name).is_file()
               or digest(regional_packet_path.parent/name)!=expected
               for name,expected in expected_regional_files.items())):
        raise ValueError('September regional packet payload differs from its sealed manifest')
    procurement_material_lines={
        (row.get('system'),row.get('material'),row.get('stock_scope')):row
        for row in procurement_packet.get('material_purchasing_lines',[])}
    linked_aluminium_count=0
    linked_aluminium_line_count=0
    for material,(system,stock_scope) in expected_aluminium_materials.items():
        key=(system,material,stock_scope)
        line=procurement_material_lines.get(key)
        source_rows=[row for row in aluminium_scenarios if row.get('material')==material]
        if line is None or len(source_rows)!=21:
            raise ValueError('Candidate aluminium sensitivity lacks its matching procurement material line')
        attached=line.get('domestic_raw_stock_sensitivity_scenarios',[])
        expected_by_process={row['process_record_id']:row for row in source_rows}
        actual_by_process={row.get('source_process_record_id'):row for row in attached}
        if (line.get('material_line_id')!=sourcing_identity({k:v for k,v in line.items() if k!='material_line_id'})
            or line.get('domestic_raw_stock_sensitivity_count')!=21
            or line.get('modeled_gross_stock_mass_kg')!=source_rows[0].get('input_gross_stock_mass_kg')
            or line.get('engineering_group_count')!=source_rows[0]['process']['candidate_takeoff_group_count']
            or line.get('engineering_occurrence_count')!=source_rows[0]['process']['candidate_takeoff_occurrence_count']
            or line.get('domestic_raw_stock_sensitivities_are_compatible_quotes') is not False
            or len(attached)!=21 or set(actual_by_process)!=set(expected_by_process)):
            raise ValueError('Procurement aluminium line differs from exact mass takeoff scenario set')
        for process_id,source_row in expected_by_process.items():
            actual=actual_by_process[process_id]
            if (actual.get('source_cost_reference_packet_id')!=regional_packet.get('packet_id')
                or actual.get('source_takeoff_id')!=takeoff.get('takeoff_id')
                or actual.get('estimated_total_iqd')!=source_row.get('estimated_total_iqd')
                or actual.get('estimated_unit_cost_iqd_per_tonne')!=source_row.get('estimated_unit_cost_iqd_per_tonne')
                or actual.get('material_form')!=source_row.get('material_form')
                or actual.get('labour_hours_per_stock_tonne')!=source_row.get('labour_hours_per_stock_tonne')
                or actual.get('product_form_compatibility') is not None
                or actual.get('purchase_yield_fraction') is not None
                or actual.get('complete_process_cost') is not None
                or actual.get('complete_installed_cost') is not None
                or actual.get('procurement_approved') is not False):
                raise ValueError('Procurement aluminium cost alternative differs from its source estimate')
        linked_aluminium_count+=len(attached)
        linked_aluminium_line_count+=1
    if (linked_aluminium_count!=42 or linked_aluminium_line_count!=2
        or procurement_packet.get('candidate_mapped_aluminium_demand_line_count')!=2
        or procurement_packet.get('candidate_mapped_aluminium_sensitivity_scenario_count')!=42):
        raise ValueError('Procurement BOM must link all 42 aluminium sensitivities to the two matching material lines')
    historical_count=len(historical_packet.get('unit_rate_estimates', []))
    if (historical_count!=historical_regional.get('unit_rate_scenario_count')
        or historical_packet.get('packet_id')!=historical_regional.get('packet_id')
        or historical_packet.get('candidate_id')!=federated['candidate_id']):
        raise ValueError('Historical regional cost reference differs from its source-bound index')
    regional_totals_miqd=sorted(float(row['estimated_total_iqd'])/1_000_000 for row in historical_regional.get('baghdad_concrete_takeoff_estimates', []))
    mapped_by_region={region:sorted(float(row['estimated_total'])/1_000_000 for row in mapped_concrete if row['region']==region)
                      for region in ('Baghdad','Al-Muthanna')}
    gfrp_index=validation.get('gfrp_local_fabrication_cost_screen', {})
    gfrp_path=root/'docs/design-engine/sourcing'/gfrp_index.get('path', '')
    if not gfrp_index or not gfrp_path.is_file():
        raise ValueError('Candidate-linked GFRP local-fabrication screen is missing')
    gfrp_packet=json.loads(gfrp_path.read_bytes())
    gfrp_studies=gfrp_packet.get('studies', [])
    expected_laminate={row['recipe']:row for row in validation['packets']['laminate_material_studies']}
    regional_wage_records={row.get('benchmark_key'):row for row in catalogue
                           if row.get('kind')=='benchmark'
                           and row.get('benchmark_key','').startswith('iq-cso-2026-09:')
                           and ':wage:skilled:hour-8h-day' in row.get('benchmark_key','')}
    regional_governorates={key.split(':')[1] for key in regional_wage_records}
    regional_scenario_total=sum(len(row.get('regional_scenarios',[])) for row in gfrp_studies)
    if (gfrp_packet.get('schema')!='osr-iraq-gfrp-local-fabrication-cost-screens/2'
        or gfrp_packet.get('packet_id')!=sourcing_identity({k:v for k,v in gfrp_packet.items() if k!='packet_id'})
        or gfrp_packet.get('packet_id')!=gfrp_index.get('packet_id')
        or gfrp_packet.get('catalogue_epoch_id')!=validation.get('source_epoch_sha256')
        or gfrp_index.get('catalogue_epoch_id')!=validation.get('source_epoch_sha256')
        or gfrp_packet.get('basis',{}).get('executable_fx') is not False
        or gfrp_packet.get('basis',{}).get('uplift_fraction')!='0.20'
        or gfrp_packet.get('basis',{}).get('wage_observation_period')!='2026-09'
        or len(regional_governorates)!=15
        or set(gfrp_packet.get('basis',{}).get('regional_governorates',[]))!=
           {row['governorate'] for row in gfrp_studies[0].get('regional_scenarios',[])}
        or len(gfrp_packet.get('basis',{}).get('regional_governorates',[]))!=15
        or regional_scenario_total!=gfrp_index.get('regional_scenario_count')
        or regional_scenario_total!=135
        or len(gfrp_studies)!=3
        or sum(len(row.get('scenarios',[])) for row in gfrp_studies)!=gfrp_index.get('scenario_count')
        or any(row.get('parent_candidate_id')!=federated['candidate_id'] for row in gfrp_studies)
        or any(len(row.get('regional_scenarios',[]))!=45 for row in gfrp_studies)
        or any(row.get('candidate_id')!=expected_laminate.get(row.get('recipe'),{}).get('candidate_id')
               or row.get('publication_id')!=expected_laminate.get(row.get('recipe'),{}).get('publication_id')
               or row.get('complete_fabrication_cost_iqd') is not None
               or row.get('unknown_is_zero') is not False
               for row in gfrp_studies)
        or gfrp_packet.get('complete_installed_cost_iqd') is not None
        or gfrp_packet.get('physical_qualification') is not None
        or gfrp_packet.get('unknown_is_zero') is not False):
        raise ValueError('GFRP local-fabrication packet differs from its source epoch, laminate studies or open-cost boundary')
    wage_by_region={key.split(':')[1]:row for key,row in regional_wage_records.items()}
    regional_hours=set(gfrp_packet['basis'].get('regional_labour_scenarios_hours_per_10m2',[]))
    if regional_hours!={'8','16','32'}:
        raise ValueError('Regional GFRP labour scenarios differ from their declared 8/16/32-hour basis')
    for study in gfrp_studies:
        source_material_iqd=Decimal(study['known_listed_material_subtotal_iqd_unrounded'])
        if source_material_iqd != Decimal(study['listed_material_subtotal_gbp'])*Decimal(gfrp_packet['basis']['fx_rate']):
            raise ValueError('GFRP regional estimate material conversion differs from source-listed GBP and CBI rate')
        seen=set()
        for scenario in study['regional_scenarios']:
            region=scenario.get('governorate_key')
            hours=scenario.get('labour_hours_per_10m2')
            wage=wage_by_region.get(region)
            if (wage is None or hours not in regional_hours or (region,hours) in seen
                or scenario.get('governorate') not in gfrp_packet['basis']['regional_governorates']
                or scenario.get('wage_benchmark_id')!=wage.get('record_id')
                or scenario.get('wage_benchmark_key')!=wage.get('benchmark_key')
                or scenario.get('wage_source_id')!=wage.get('source_id')
                or scenario.get('wage_rate_iqd_per_person_hour')!=wage.get('unit_price')
                or scenario.get('wage_employer_burden_included') is not False):
                raise ValueError('Regional GFRP wage scenario differs from its exact CSO benchmark')
            seen.add((region,hours))
            direct_labour=Decimal(hours)*Decimal(wage['unit_price'])
            direct=source_material_iqd+direct_labour
            screen=(direct*Decimal('1.20')).quantize(Decimal('0.01'),rounding=ROUND_HALF_EVEN)
            if (Decimal(scenario['direct_labour_iqd_unrounded'])!=direct_labour
                or Decimal(scenario['direct_labour_iqd'])!=direct_labour.quantize(Decimal('0.01'),rounding=ROUND_HALF_EVEN)
                or Decimal(scenario['direct_known_materials_plus_labour_iqd_unrounded'])!=direct
                or Decimal(scenario['direct_known_materials_plus_labour_iqd'])!=direct.quantize(Decimal('0.01'),rounding=ROUND_HALF_EVEN)
                or Decimal(scenario['partial_screen_iqd'])!=screen
                or scenario.get('uplift_fraction')!='0.20'
                or scenario.get('complete_material_cost_iqd') is not None
                or scenario.get('complete_fabrication_cost_iqd') is not None
                or scenario.get('unknown_is_zero') is not False):
                raise ValueError('Regional GFRP material/labour/uplift arithmetic or unknown-cost boundary differs')
        if seen!={(region,hours) for region in regional_governorates for hours in regional_hours}:
            raise ValueError('Regional GFRP scenarios do not cover every CSO governorate and declared labour case')
    gfrp_rows=[]
    gfrp_regional_rows=[]
    for row in gfrp_studies:
        amounts='/'.join(f"{float(x['partial_screen_iqd']):,.2f}" for x in row['scenarios'])
        material=float(row['known_listed_material_subtotal_iqd'])
        recipe_label=row['recipe'].replace('-600gsm','').replace('-',' ')
        gfrp_rows.append(
            f"| 10 m² {recipe_label} GFRP screen | IQD {material:,.2f} known listed materials; 8/16/32 assumed skilled hours | IQD {amounts} partial materials + labour + 20%; unpriced inputs remain open |")
        region_lines=[]
        for hours in sorted(regional_hours,key=int):
            totals=[Decimal(x['partial_screen_iqd']) for x in row['regional_scenarios']
                    if x['labour_hours_per_10m2']==hours]
            region_lines.append(f"{hours} h: IQD {min(totals):,.2f}–{max(totals):,.2f}")
        gfrp_regional_rows.append(
            f"| 10 m² {recipe_label} GFRP regional sensitivity | CSO skilled base wages in 15 listed governorates; hours are assumed, not measured | "
            + '; '.join(region_lines)+" after the 20% allowance; Kurdistan Region wage data are absent |")
    return [
      '## Sourcing and domestic cost coverage','',
      catalogue_line+' Iraqi source leads now include the Ministry industrial directory, rebar and rolled steel profile suppliers, ordinary and sulphate-resistant cement producers, aggregate suppliers, EPS and polyurethane foam producers, aluminium ingot/alloy supply, metal fabrication, cable and busbar production, transformers, electrical enclosures and panels, precast concrete, GRP and façade manufacturing, polymer/resin supply, local composite-material distributors, and aluminium extrusion. Hadeed Iraq also provides a rebar marketplace/RFQ directory; displayed figures are indicative seller listings, not a binding Hadeed offer. Recent leads include [Diwan](https://www.diwan.com.iq/en/about) for Iraqi cables and transformers, [RS Al Najaf/IPDCO](https://ipdco.iq/najaf-factory/index.htm) for electrical cabinets and distribution equipment, and [Ibn Majid](https://www.ibnmajid.industry.gov.iq/uploaded_files/1730632596.pdf) for heavy steel/aluminium fabrication. The reviewed pages provide no candidate-matched prices or capacities; they are discovery leads, not quotations, qualified products or confirmed production availability. See the [sourcing dossier](../sourcing/README.md) and [current source-bound coverage index](../sourcing/validation-current.json).','',
      identity_note,'',
      '| Research scope | Sourcing evidence | Cost disposition |','|---|---|---|',
      f"| Frame candidate `{frame['candidate_id'][:12]}` | {frame['input_requirement_count']:,} groups; {frame['compatible_matches']} compatible priced matches | Complete installed cost unknown |",
      f"| Federated candidate `{federated['candidate_id'][:12]}` | {federated['physical_scope_count']:,} physical scopes across {federated['input_requirement_count']:,} review requirements; {federated['evaluated']:,} evaluated, {federated['pending']:,} pending | {federated['compatible_matches']} compatible priced matches; nine RFQ drafts remain unsent |",
      f"| Material takeoff `{takeoff['candidate_id'][:12]}` | {takeoff['manufacturing_group_count']:,} groups retain {takeoff['located_occurrence_count']:,} located occurrences; {takeoff['unlocated_account_count']:,} unlocated accounts stay separate | {float(takeoff['known_gross_stock_mass_kg'])/1000:,.2f} t gross located stock and {float(takeoff['concrete_nominal_stock_volume_m3']):,.2f} m³ nominal concrete geometry are not installed mass or purchase quantities |",
      f"| Draft procurement-package BOM `{procurement['candidate_id'][:12]}` | {procurement['located_stock_occurrence_count']:,} located occurrences grouped into {procurement['draft_package_count']:,} draft packages and {procurement['material_demand_line_count']} purchasing/material lines; {procurement['domestic_source_lead_association_count']} domestic-source lead associations across seven families | {procurement['unlocated_obligation_count']:,} obligations remain separate; no supplier prices, commercial order quantities or complete assembly scope |",
      f"| Candidate sourcing sensitivity | {sensitivity['summary']['ranked_partial_scenario_exposure_count']} partial scenario spreads ranked; {sensitivity_unranked_count} material lines remain unranked. {sensitivity_rank_text} | Scenario spread is not a probability range, cost bound or value-of-information estimate; gross stock masses are context only; no preferred-design change can be inferred |",
      f"| Generic concrete fabrication screen | {len(concrete)} recipes using September 2026 Iraqi material and skilled-worker base-wage observations; 2/4/8 assumed person-hours per nominal m³ | IQD {concrete_rates[0]:,}–{concrete_rates[-1]:,}/m³ after materials + labour + 20%; not a designed mix or guideway-beam price |",
      f"| September 2026 concrete takeoff estimate | 81 exact concrete manufacturing groups and 486 engineering occurrences, with 2/4/8 assumed skilled h/m³ scenarios | Baghdad IQD {mapped_by_region['Baghdad'][0]:.1f}–{mapped_by_region['Baghdad'][-1]:.1f}m; Al-Muthanna IQD {mapped_by_region['Al-Muthanna'][0]:.1f}–{mapped_by_region['Al-Muthanna'][-1]:.1f}m, including 20%; ingredient screen, not a designed mix, precast beam price or installed cost |",
      *[f"| Candidate {material.replace('-', ' ')} raw-stock sensitivity | {len(aluminium_scenarios)//2} distinct product-form/hour alternatives; mass and occurrence counts reconcile to the sealed takeoff | IQD {float(min(values))/1_000_000:.1f}–{float(max(values))/1_000_000:.1f}m including direct material, assumed Baghdad base-wage labour and 20%; alloy/temper, product compatibility, purchase yield and process route remain unknown |"
        for material,values in aluminium_totals.items()],
      f"| 2025 Iraqi regional domestic-cost library | {historical_count} dated material/labour scenarios across concrete, rebar, aluminium profiles and four Ur sheet forms; concrete recipe prices available in 12 of 15 listed governorates | Three governorates have missing concrete material prices; all scenario hours are assumptions and the 20% uplift is unallocated |",
      f"| 2025 Baghdad concrete takeoff estimate | 81 exact concrete manufacturing groups and 486 engineering occurrences, costed at 2/4/8 declared skilled h/m³ scenarios | IQD {regional_totals_miqd[0]:.1f}–{regional_totals_miqd[-1]:.1f} million on the 2025 regional material rates; not a designed mix or installed span price |",
      f"| Unlocated obligation cross-references | {obligation_links['linked_unique_obligation_count']:,}/{obligation_links['source_obligation_count']:,} accounts linked by hierarchy to related car/bogie/span/bank scopes; {obligation_links['package_association_count']:,} non-additive associations | No package mass, quantity or cost allocation; {obligation_links['unlinked_obligation_count']} network-level infrastructure obligations remain unlinked |",
      '', '| GFRP study | Labour basis | Partial cost |','|---|---|---|',
      *gfrp_rows,'', '| Regional GFRP scenario | Wage basis | Partial cost sensitivity |','|---|---|---|',
      *gfrp_regional_rows,'',
      'The GFRP figures use listed Easy Composites UK material extensions converted at the 29 October 2026 CBI GBP/IQD reference and September 2026 CSO Baghdad or listed-governorate skilled-worker base-wage benchmarks. They are partial sensitivity screens: adhesives remain unresolved, sandwich-core prices are absent, and import, tooling, consumables, QA, fire/smoke, structural qualification and installation are excluded. The regional table covers only the 15 governorates in the CSO bulletin, excludes Kurdistan Region, and uses construction-worker wages as a proxy for composite-shop labour. They do not price a finished panel or transfer to the selected reference body.', '',
      'The September 2026, July 2026 and 2025 price views remain separately dated source-bound estimates. The September concrete takeoff preserves all 81 manufacturing groups and 486 occurrences across Baghdad and Al-Muthanna scenarios. The aluminium alternatives apply exact aggregate takeoff masses while retaining their group and occurrence identities through the takeoff ID; they do not assign a form or supplier SKU to individual occurrences. Material mix and labour hours remain assumptions, not measured process data; these scenarios do not establish a guideway beam, supplier match, complete installed mass or cost, or a cost for the selected reference candidate. The regional library also includes rebar cut/bend and profile/sheet raw-stock processing sensitivities; posted sheet rates do not establish structural grade or a completed manufacturing route.','',
      f"The separate five-bank, 100 m active-length research configuration now has a copper raw-stock sensitivity in the [candidate-bound procurement packet](../sourcing/{procurement_relative_path}): 9.354 t across five bank groups and ten retained occurrences, using a 2025 Iraqi CIF copper-wire unit-value benchmark, September 2026 Baghdad base wage, 8/16/32 assumed labour hours per tonne and a 20% uplift. The partial totals are IQD 90.19/91.03/92.72 million. They do not establish winding-conductor compatibility, a measured winding route, complete station-drive cost or the selected reference's approximately 900 m winding allocation. Supplier, force, current, heat-rejection and repeated-duty evidence remain open. Five source-bound unsent bank scopes and their comparable duty/evidence request are in the [station-drive RFQ draft](../sourcing/rfq-drafts/station-drive-banks-2026-10/README.md); the [current sourcing validation index](../sourcing/validation-current.json) records its candidate, quantities and open evidence gates.",'',
      'The [CSO 2024 construction-wage archive](../../../engineering/sourcing/data/iraq-construction-wages-2024.json) preserves Table 7 daily wage observations for 15 governorates and six categories, normalized here by an explicit 8-hour workday. Baghdad skilled labour is IQD 75,000/day or IQD 9,375/hour. This is historical base-wage context, excludes employer burden and Kurdistan Region, and is not used in current 2025/2026 estimates; the current fabrication screens use dated material and wage rates, assumed hours, then a 20% uplift.','',
      'The reference dossier\'s 900 m shared winding and the separate five-bank research layout (100 m active motor length) remain distinct propulsion configurations. Their force maps, electrical/thermal duties, plant quantities, procurement BOMs and installed costs are not shared.',''
    ]

def readme(record,summary,root=ROOT):
    v=record['vehicle'];m=v['mass'];o=record['service'];p=o['selected_scenario']['profile'];z=o['selected_station'];r=record['civil']['selected_reference'];e=o['electrical'];b=e['battery']
    mass_ledger_path=Path(root)/'docs/design-engine/mass-reconciliation/current/summary.json'
    mass_ledger=json.loads(mass_ledger_path.read_bytes())
    if any(mass_ledger.get(key)!=record[key] for key in ('candidate_id','body_candidate_id','selection_id')) or mass_ledger.get('selected_evaluation_id')!=record['evaluation_id']:
        raise ValueError('Mass reconciliation identities differ from current selected evaluation')
    lines=['# v0.6 station-powered freewheeling rail','',
      'OpenSourceRail aims for simple, affordable urban transport, repeated precast civil components and local manufacture and repair. Six lightweight comfort cars run on passive steel-wheel bogies and conventional rails. Station LIMs act on passive onboard aluminium secondaries; no onboard traction motor, traction battery or levitation magnet is fitted. Independent service power, braking and the existing station-led GoA4 architecture remain.','',
      '**Selected for reference engineering and prototype investigation. No physical, manufacturing or operating release.** The [selector](../../../engineering/development-baseline.toml) binds the same vehicle, body, support and propulsion identities through this packet, delivery records, Workbench and reader. [v0.5 maglev evidence](../../archives/v0.5-maglev/README.md) remains independently pinned.','',
      '| Item | Recalculated basis |','|---|---|',
      '| Formation and comfort | Six 17 m cars; 104.5 m overall; 44 seats + two wheelchair places/car; zero planned standing |',
      '| Running gear | 12 unpowered bogies, 24 axles, 48 wheels; independent friction/WSP/parking brake requirements |',
      '| Body/platform | Retained lightweight aluminium/GFRP stock with revised bogie load paths; 1.0 m reference floor above rail |',
      f"| Accounted tare / normal load | {m['accounted_tare_kg_per_car']/1000:.3f} / {m['accounted_cap_loaded_kg_per_car']/1000:.3f} t/car at 75 kg/person |",
      f"| Located material / remaining reference accounts | {m['located_material_kg']/1000:.3f} / {m['unlocated_or_reference_account_kg']/1000:.3f} t/car |",
      '| Complete installed mass, CG and inertia | Unknown; inherited service allocations may overlap new equipment and must be disaggregated |',
      f"| Mass reconciliation | [Occurrence-level ledger](../mass-reconciliation/current/README.md) and [closure worksheet](../mass-reconciliation/current/mass-closure-worksheet.json.gz) — {mass_ledger['closure_worksheet_record_count']:,} source, candidate-geometry and account-closure rows; installed mass remains unknown |",
      f"| Service-only battery | {b['gross_energy_kWh']:.1f} kWh, {b['mass_kg']:.0f} kg/car reference account; cooled installation and rail approval open |",
      '| Service targets | 72 km/h, 0.4 m/s² acceleration, 0.6 m/s² braking, 35 s dwell, 120 s headway; 8,280 pphpd arithmetic |','',
      '## Reference journey and power','',
      f"The 2 km, normal-load longitudinal requirement, including counted wheel/axle/disc rotational inertia, takes **{p['runtime_s']:.3f} s**, reaching 20 m/s and arriving at **{p['arrival_speed_before_braking_m_s']:.3f} m/s** before braking. Required peak launch force is **{p['peak_launch_force_N_per_car']/1000:.3f} kN/car**, mechanical power **{p['peak_launch_power_W_per_car']/1000:.1f} kW/car**. Actual available thrust, current, voltage and full motor efficiency remain unknown.",'',
      f"Full-train engagement requires **{z['required_shared_winding_m']:.1f} m** of shared launch/receiving winding; the library chooses **{z['length_m']:.0f} m**, **{z['sections_per_direction']} sections/direction** at 12.5 m and at least two independently controlled train branches. The **{z['nominal_resource_interval_s']:.2f} s** nominal berth interval is a necessary resource screen, not verified two-minute operation.",'',
      'Reference profiles cover empty, 46-person and 160-person structural-control loads at 1.5 and 2 km, with grade/wind, charge and independent wet/downhill stopping bounds. A 0.05 adhesion hypothesis on a 2% downgrade gives approximately 700 m stopping from 20 m/s including one second response. Supplier brakes, WSP, uncertainties and actual routes must establish the protection envelope. Receiving motor recovery receives no safety credit.','',
      'The 82.8 kWh service reference uses 75 industrial Type3-20 modules plus explicit enclosure/cooling/conversion accounts. The 200 kW charging target passes a catalogue voltage/current necessary bound; available charge power versus SOC/temperature remains unknown. A 50°C environment exceeds the module ambient catalogue range. Normal 35 kW/car hotel duty balances in the prototype calculation; 50 kW/car adverse duty needs more charging. Solar yield is not guaranteed or credited to make the balance pass.','',
      'The actual GetDP conductive-slab benchmark converges against its exact imposed-field solution. It has no real primary winding, steel/end geometry, current-to-force map or finite-height return currents. Its conditional thrust is not available station thrust. Active-plate-only and all-aluminium heat-capacity bounds expose the dependence on thermal connection; actual temperatures remain unknown.','',
      'The [native physical follow-up](../v06-physical-closure/README.md) adds 18 current-excited LIM cases, 24 reduced Chrono brake runs and native body-interface/fit-up experiments. The tested full primary fails force and steel-field screens. Its raw field calculations remain conditional; the default geometry and acceptance holds are unchanged.','',
      '[Prototype/fault test plan](prototype-test-plan.json) · [Full evaluation](evaluation.json.gz) · [Motor method evidence](native-drive.tar.gz) · [Speed requirement](service-profile.svg) · [Equal-service comparison](comparison.json)','',
      '## Vehicle and civil design','',
      'New bogie hardpoints, deep side sills and retained roof longitudinal members replace the magnetic carrier arrangement. The isolated side sills fail their declared stiffness screen; ideal whole-body chord coupling is an upper stiffness bound, with shear transfer, openings and joints unqualified. Native CAD is counted material geometry, not a complete installed or collision-free certified vehicle. Split battery cassettes, brakes, suspension, couplers, frame joints and maintenance paths still need detailed installation.','',
      'The roof proposal uses HP60 core and a counted white finish; long-term loaded hot strength, durable reflectance and HVAC performance remain open. Unchanged door, glass, floor and seat stock retains its source ancestry; the revised vehicle receives a new identity. Plastic glazing remains an unqualified alternative.','',
      f"Three conventional guideway families are compared across 15/20/25/30 m spans. The crowd-sized {r['span_m']:.0f} m box reference counts **{r['concrete_m3']:.3f} m³ concrete**, **{r['running_rail_kg']/1000:.3f} t running rail**, **{r['direct_fastener_sets']} fastener sets** and **{r['counted_steel_kg']/1000:.3f} t total preliminary steel including rail, fasteners, reinforcement, tendons and anchorages. Its **{r['total_counted_span_mass_kg']/1000:.2f} t** span account still excludes complete bearings, piers, foundations, access/containment and station equipment.",'',
      'New rails and fasteners are much lighter than the old magnetic interface stock, while concrete and remaining structural quantities have different boundaries. Lower installed cost is unproven. Each longitudinal section gets its own moving-load envelope; torsion, fatigue, unequal rail loads, prestress losses, erection and sites remain open. Twin and U sections retain their failures.','',
      '[Native vehicle material package](native-vehicle.tar.gz) · [Vehicle drawing](vehicle-overview.svg) · [Reference section](interface-section.svg) · [Civil alternatives](exports/civil.json) · [Partial native IFC](exports/selected-interface.ifc) · [IFC scope](exports/bim.json) · [BOM](exports/engineering-bom.json.gz) · [Processes](exports/manufacturing.json) · [Procurement](exports/procurement.json.gz) · [Assembly](exports/assembly.json) · [Controls](exports/controls.json)','',
      '## Automation, comparison and cities','',
      'Station-led GoA4, onboard ATP, OCC, TCMS, door control, interlocking and communications remain. New actual Rust wheel-interface fixtures check configuration/readiness and independent brake demands; existing ATP regressions remain software evidence. They use assumed readiness and have no physical brake plant or hardware outputs. Loss of propulsion leaves wheel support intact. Off-zone restart requires protected rescue/towing; mainline switches remain excluded, with depot exceptions only.','',
      'v0.6 is chosen for prototype investigation to remove the unproven levitation system and repeated magnetic-facing assemblies. It is heavier than the v0.5 accounted car and lighter than the optimistic stripped-v0.4 mass proxy. No same-service supplier-priced whole-life superiority is established. See the explicit comparison and open price coverage.','',
      f"All **{summary['cities']['city_count']} city geographies and maps are preserved**; **zero city performance packages are regenerated**. A metadata scan of 17,268 adjacent operating-stop gaps finds a longest retained gap of approximately 3 km in Faisalabad. Reference adverse cases test that distance; uphill unreachable cases and downhill speed-cap violations are retained. Historical city fleet, windings and finance figures are not v0.6 results.",'',
      '[Geographic catalogue and holds](cities.json) · [Workbench](../../workbench/current/index.html) · [Native controls](native-controls.tar.gz)','',
      '## Iterative alternatives','', 'The [failure-driven campaign](../v06-optimisation/README.md) generates body/motor/brake revisions, reruns native solvers, propagates the same mass into civil/service calculations and compiles matching research twins. The research winner is the next experiment; no qualified replacement is silently promoted. The comparison exposes normal/crowd deflection, additional mass and changed thrust requirements; conditional motor results remain outside their declared linear-steel domain. Participating-panel lateral displacement remains nonconverged under mesh refinement; its vertical values are diagnostic rather than validated full-body performance.','',
      'The [whole-railway architecture campaign](../v06-architecture/README.md) tests seven propulsion families, different speed/formation/powered-track arrangements and civil sections. It compares analytical demand and conditional quantities while keeping new equipment mass and actual motor capability unknown. Repaired finite-area joint/body and generic nonlinear magnetic method checks retain their independent numerical and engineering dispositions. No architecture is qualified, no city performance is regenerated and the selected v0.6 reference is preserved.','',
      'The [function-first adaptive generator](../v06-adaptive-design/README.md) separates mandatory obligations, advisory targets, revisable hypotheses and numerical model domains. Its extensible material/structure/joining/equipment/system variables drive coupled revision tasks. New thinner/deeper sill experiments redistribute counted material, with native normal/fine/crowd cases and matched mass, axle, demand and civil calculations. Provisional deflection alone neither rejects nor accepts a car; local stability, strength, joints, clearances and correlation remain open.','',
      'The [generative structural campaign](../generative-structure/README.md) composes different physical body arrangements, generates actual stock and interface graphs, diagnoses mechanisms and executes topology, layout and function-integration rewrites. Gross structure stock is not equipped vehicle tare. Native axial underfloor checks and CAD exports do not validate complete shell, laminate, joint or vehicle response; no integrated design is selected.','',
      'The [coordinated railway experiment](../coupled-railway/README.md) connects architecture, adaptive proposals, generated bodies, inventory, motor requirements, independent braking, civil loads, manufacturing and economic coverage through one versioned bundle and dependency graph. Changed body stock automatically triggers downstream evaluation. New three-dimensional metal-body research and conditional operating requirements retain their exact models and missing evidence; complete installed mass, available nonlinear LIM capability and a qualified journey remain open.','',
      'The [candidate-to-journey closure matrix](../railway-closure/README.md) propagates three distinct bodies through separate 1.5 km and 2 km station-only/recovery-research bundles, empty/normal/crowd/adverse demand, independent brake hypotheses, civil and cost quantities. Its fault journeys remain not-run. The [moving-conductor LIM experiment](../moving-lim-method/README.md) translates the actual secondary through a voltage-coupled field model; unresolved refinement and high-speed domain limits prevent force-map admission. Neither experiment supplies a complete equipped vehicle or physical journey.','',
      '## Readiness and reproduction','', '| Gate | State | Evidence still needed |','|---|---|---|']
    lines += [f"| {g['gate']} | **{g['state']}** | {g['reason']} |" for g in record['gates']]
    lines += ['','```bash','./osr status','./osr build','./osr verify','./osr test','./osr book --check','./osr sim baghdad  # explicit city evaluation hold','./osr legacy verify','```','',
      '[Source/payload receipt](manifest.json) · [README context](readme-coverage.md) · [Roadmap](../../ROADMAP.md) · [Project ethos](../../../README.md)','']
    for name in IDS:lines += [name.replace('_',' ').capitalize()+' `'+record[name]+'`','']
    marker=lines.index('## Automation, comparison and cities')
    lines[marker:marker]=_sourcing_section(root,record)
    return '\n'.join(lines)

def prototype_plan(record):
    cases=[]
    required=('position','speed','acceleration','motor_current','motor_thrust','electrical_power','secondary_temperature',
        'stator_temperature','wheel_and_axle_forces','brake_force_and_temperature','service_SOC','resource_occupancy','following_separation','failure_reason')
    for p in record['service']['profiles']:
        d=p['inputs']['distance_m'];load=p['inputs']['loading']
        fault=('receiving drive power lost' if load=='empty' else 'wet-rail braking' if load=='normal' else 'emergency stop')
        cases.append(dict(case_id=identity(dict(profile_id=p['profile_id'],fault=fault)),distance_m=d,loading=load,
            normal_analytical_profile_id=p['profile_id'],degraded_case=fault,
            reference_calculation_execution='completed',physical_run_execution='held',
            missing_inputs=['Validated station motor map','Qualified brake/WSP/adhesion map','Flexible body and wheel-rail dynamics'],
            physical_outputs={key:None for key in required}))
    return dict(schema='osr-v06-prototype-test-plan/1',**{k:record[k] for k in IDS},development_default=True,
        reference_cases=cases,longest_gap=record['service']['longest_retained_gap_context'],
        additional_faults=['Communications lost','Occupied or delayed receiving berth','Gradient overspeed','Train integrity/localisation lost',
            'One brake control channel lost','Missed charge','Station power lost during launch','Off-zone rescue and high-viaduct evacuation'],
        releases=dict(production_drawings=False,supplier_brakes=False,motor_map=False,structural_body=False,prototype_review=False),
        proof_rule='Method and reference calculations do not replace the same-candidate physical journey and independent qualification.',**FLAGS)

def seal(output,root=ROOT):
    root=Path(root);output=Path(output);record=evaluation.build(root);index=cities.read_catalogue(root);delivery=json.loads((output/'exports/manifest.json').read_bytes())
    m=dict(schema='osr-current-development-publication/2',**{k:record[k] for k in IDS},evaluation_id=record['evaluation_id'],development_default=True,
      source_sha256=sources(root,record,index,delivery),files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file() and p.relative_to(output).as_posix()!='manifest.json'},
      workbench_files_sha256={n:digest(root/WORKBENCH/n) for n in ('index.html','app.js','app.css')},**FLAGS)
    m['linked_artifacts_sha256']={n:digest(root/n) for n in ('OpenSourceRail-Book.pdf','OpenSourceRail-Book.receipt.json') if (root/n).is_file()}
    m['manifest_id']=identity(m);write(output/'manifest.json',encoded(m));return m

def publish(output=None,*,root=ROOT,native_dir=None,cities_dir=None):
    root=Path(root).resolve();output=root/OUTPUT if output is None else Path(output)
    for script in ('generate-public-overview.py','generate-doc-index.py'):
        subprocess.run([sys.executable,str(root/'tools/automation'/script)],cwd=root,check=True,capture_output=True)
    record=evaluation.build(root);natives={};packages={}
    from engineering import mass_ledger_audit
    mass_ledger_audit.verify(root)
    for name in ('vehicle','drive','controls'):
        packages[name]=native_package(name,record,root,output,native_dir if name=='vehicle' else None)
        natives[name]=verify_package(packages[name],root)
    if output.exists():
        previous=root/'build/v06-development/replaced-current'/digest(output/'manifest.json') if (output/'manifest.json').is_file() else root/'build/v06-development/replaced-current/incomplete'
        if previous.exists():shutil.rmtree(output)
        else:previous.parent.mkdir(parents=True,exist_ok=True);shutil.move(output,previous)
    output.mkdir(parents=True,exist_ok=True)
    index=cities.publish_all(root=root);delivery=exports.write(output/'exports',record,root,index,natives['vehicle'])
    compact_value=compact(record,index,natives,delivery)
    for name,raw in {'summary.json':encoded(compact_value),'evaluation.json.gz':gzip.compress(encoded(record),mtime=0),
       'comparison.json':encoded(comparison.evaluate(record,root)),'prototype-test-plan.json':encoded(prototype_plan(record)),'README.md':readme(record,compact_value,root).encode()}.items():write(output/name,raw)
    for name,path in packages.items():write(output/('native-'+name+'.tar.gz'),archive(path))
    figures.write(record,output)
    for name in ('index.html','app.js','app.css'):write(root/WORKBENCH/name,(root/'engineering/development_baseline/web'/name).read_bytes())
    seal(output,root)
    return dict(published=True,selection_id=record['selection_id'],evaluation_id=record['evaluation_id'],city_count=index['city_count'],city_performance_packages_written=0,**FLAGS)

def verify(output=None,*,root=ROOT,replay=True):
    root=Path(root).resolve();output=root/OUTPUT if output is None else Path(output)
    from engineering.development_baseline.entrypoint import read_packet
    value,m=read_packet(root,output.relative_to(root).as_posix())
    for script in ('generate-public-overview.py','generate-doc-index.py'):
        try:subprocess.run([sys.executable,str(root/'tools/automation'/script),'--check'],cwd=root,check=True,capture_output=True)
        except subprocess.CalledProcessError as error:raise ValueError('Current generated overview/navigation differs: '+script) from error
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('publication identity differs')
    record=evaluation.build(root)
    from engineering import mass_ledger_audit
    mass_ledger_audit.verify(root)
    if json.loads(gzip.decompress((output/'evaluation.json.gz').read_bytes()))!=record:raise ValueError('evaluation differs')
    citycheck=cities.verify_all(root=root,replay=replay);index=cities.read_catalogue(root);delivery=exports.verify(output/'exports',record,root,index)
    natives={}
    for name in ('vehicle','drive','controls'):
        path=native_package(name,record,root,output);natives[name]=verify_package(path,root)
    exported=json.loads((output/'exports/manifest.json').read_bytes())
    if value!=compact(record,index,natives,exported):raise ValueError('current summary differs')
    if (output/'README.md').read_text()!=readme(record,value,root):raise ValueError('current introduction differs')
    if json.loads((output/'comparison.json').read_bytes())!=comparison.evaluate(record,root):raise ValueError('comparison differs')
    if json.loads((output/'prototype-test-plan.json').read_bytes())!=prototype_plan(record):raise ValueError('prototype test plan differs')
    if m['source_sha256']!=sources(root,record,index,exported):raise ValueError('publication source set differs')
    from engineering import readme_context
    audit=readme_context.audit(root)
    if not audit['current'] or json.loads((output/'readme-coverage.json').read_bytes())!=audit:raise ValueError('README context differs')
    for name,expected in m['workbench_files_sha256'].items():
        if digest(root/WORKBENCH/name)!=expected:raise ValueError('Workbench changed')
    for name,expected in m['linked_artifacts_sha256'].items():
        if digest(root/name)!=expected:raise ValueError('reader changed')
    return dict(verified=True,replayed=replay,selection_id=record['selection_id'],evaluation_id=record['evaluation_id'],
       city_count=citycheck['city_count'],city_performance_packages_written=0,native_controls=natives['controls']['controls'],exports=delivery,**FLAGS)

def build(root=ROOT,force=False,output=None):
    root=Path(root);output=root/OUTPUT if output is None else Path(output);lock=root/'build/v06-development/build.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open('a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if not force:
            try:
                value=verify(output,root=root,replay=False)
                from .reader import build as reader
                reader(root=root,check=True);return dict(value,cached=True)
            except(ValueError,OSError,KeyError):pass
        from engineering import readme_context
        readme_context.write_owned(root);audit=readme_context.audit(root)
        if not audit['current']:raise ValueError('README context: '+'; '.join(audit['errors']))
        value=publish(output,root=root)
        audit=readme_context.audit(root)
        if not audit['current']:raise ValueError('README context after publication: '+'; '.join(audit['errors']))
        write(output/'readme-coverage.json',(json.dumps(audit,sort_keys=True,indent=2)+'\n').encode());write(output/'readme-coverage.md',readme_context.markdown(audit).encode());seal(output,root)
        from .reader import build as reader
        reader(root=root);seal(output,root)
        return dict(value,verification=verify(output,root=root),cached=False)
