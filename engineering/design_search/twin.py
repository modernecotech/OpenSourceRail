"""Candidate-bound research exports through the actual native and IFC toolchain.

An incomplete candidate may produce a next-experiment stock/coupon twin only
when explicitly requested. Missing installed geometry and mass remain enumerated.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from engineering.ferrite_maglev import candidate_manufacturing as manufacturing
from engineering.ferrite_maglev import bim_field, delivery_platform
from engineering.factory_examples import native
from . import contracts, families

ROOT = Path(__file__).resolve().parents[2]
FLAGS = dict(configuration_adopted=False, engineering_accepted=False,
             physical_validation=False, physical_release=False,
             complete_installed_twin=False, integrated_baseline_ready=False)


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def digest(value):
    return sha256(encoded(value)).hexdigest()


def sources():
    paths={Path(__file__),Path(contracts.__file__),Path(families.__file__),Path(native.__file__),
        Path(native.__file__).with_name('models.py'),Path(delivery_platform.__file__),
        *manufacturing.source_paths(),*bim_field.source_paths()}
    return {str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def _default_plan():
    value=delivery_platform.baseline(ROOT/'cities/catalogue/west-asia/Iraq/Baghdad')
    # Common, actual retained geography for every candidate. The bounded pilot
    # is declared here; the other city lines are not silently claimed delivered.
    value['lines']=[deepcopy(min(value['lines'],key=lambda row:(row['length_m'],row['id'])))]
    value['comparison_scope']='One shortest retained Baghdad line for bounded common-geography planning; no city-wide or surveyed acceptance.'
    return delivery_platform.seal(value)


def _additional_materials(materialized):
    rates=manufacturing.structures.load()['rates'];rows=[]
    for part in materialized.get('additional_stock',[]):
        rows.append(manufacturing._line(part['id']+'/material','added-carrier-steel','kg',part['mass_kg'],
            rates['fabricated_structural_steel_usd_kg'],[part['id']],
            'cut exact counted wall stock, fixture and weld; bearing/slide interfaces remain unqualified',
            waste=.08,mass=part['mass_kg'],lead=60))
    return rows


def _assembly(candidate,products,parts,additional_materials):
    ids={part['id'] for part in parts};steps=[]
    for product in products['products']:
        source_ids=product['geometry_source_ids']
        # Launch windings and reinforcement may have a counted cut schedule
        # while exact installed geometry remains a separate design hold.
        steps.append(dict(product_id=product['product_id'],product_revision_sha256=product['product_revision_sha256'],
            geometry_sha256=product['geometry_sha256'],available_native_part_ids=sorted(set(source_ids)&ids),
            unmodelled_geometry_references=sorted(set(source_ids)-ids),
            cut_schedule=product['cut_schedule'],procedure=manufacturing.procedures(product),
            performed=False,manufacturing_release=False))
    added=sorted({part_id for row in additional_materials for part_id in row['geometry_part_ids']})
    if added:
        steps.append(dict(product_id='COUNTED-CARRIER-STOCK',product_revision_sha256=digest(additional_materials),
            geometry_sha256=digest([part for part in parts if part['id'] in added]),available_native_part_ids=added,
            unmodelled_geometry_references=[],cut_schedule=additional_materials,
            procedure=dict(steps=[dict(sequence=1,operation='Cut the enumerated RHS wall stock to exact retained dimensions.',performed=False),
                dict(sequence=2,operation='Fixture the counted carrier walls at their source-frame datums; qualify welds and inspect distortion.',performed=False),
                dict(sequence=3,operation='Hold final assembly until bearings, slides, retention, wiring and protection have actual designs and accepted fit.',performed=False)]),
            performed=False,manufacturing_release=False))
    return dict(schema='osr-candidate-assembly-plan/1',candidate_id=candidate['candidate_id'],
        requirement_revision=candidate['requirement_revision'],bounded_products=steps,
        unknown_installed_stock_ids=[row['id'] for row in candidate['installed_inventory'] if row['status']=='unknown'],
        scope='Exact known stock/coupon instructions; view translations are not installed assembly transforms. No fabricated, inspected or accepted assembly is inferred.',
        **FLAGS)


def compile(candidate,evaluations,*,output,plan=None,export_native=True,allow_incomplete=False):
    """Export a selected candidate; callers must explicitly permit research gaps.

    FCStd/STEP are generated/reopened by FreeCAD; IFC/IDS/BCF are generated and
    reopened by their native libraries. No format-shaped placeholder is written.
    """
    contracts.validate_candidate(candidate)
    if type(export_native) is not bool or type(allow_incomplete) is not bool:
        raise ValueError('explicit native-execution and incomplete-stock choices required')
    if not isinstance(evaluations,list):raise ValueError('candidate evaluation list required')
    for value in evaluations:
        contracts.validate_result(value)
        if value['candidate_id']!=candidate['candidate_id'] or value['requirement_revision']!=candidate['requirement_revision']:
            raise ValueError('mixed candidate or requirement evaluation cannot enter a twin')
    if len({row['evaluation_id'] for row in evaluations})!=len(evaluations):raise ValueError('duplicate twin evaluation identity')
    materialized=families.materialize(candidate,allow_incomplete=allow_incomplete)
    if materialized['configuration_sha256']!=candidate['candidate_id']:
        raise ValueError('materialized physical candidate identity differs')
    beam=manufacturing.selected_beam(materialized,allow_incomplete=allow_incomplete)
    selected=candidate['architecture']['guidebeam']
    if any(beam['selection'][key]!=selected[key] for key in ('section_id','span_m')):
        raise ValueError('candidate and exported beam selection differ')
    output=Path(output)
    if output.is_symlink() or any(parent.is_symlink() for parent in output.parents):raise ValueError('ordinary twin output required')
    if output.exists() and any(output.iterdir()):raise ValueError('fresh owned twin output directory required')
    output.mkdir(parents=True,exist_ok=True)
    before=sources();planning=deepcopy(_default_plan() if plan is None else plan);delivery_platform.validate(planning)
    products=manufacturing.product_definition(materialized,beam=beam,allow_incomplete=allow_incomplete)
    package=manufacturing.lifecycle_package(materialized,beam=beam,allow_incomplete=allow_incomplete)
    additional=_additional_materials(materialized)
    parts=bim_field.exchange_parts(materialized,beam=beam,include_rail_and_supports=True,allow_incomplete=allow_incomplete)
    if len({part['id'] for part in parts})!=len(parts):raise ValueError('unique twin stock parts required')
    geometry=dict(schema='osr-candidate-native-stock-definition/1',candidate_id=candidate['candidate_id'],
        configuration_sha256=candidate['candidate_id'],selected_beam=beam['selection'],
        retain_native_tessellation=True,interference_roles=[],
        parts=[dict(part,role=part.get('role','selected-candidate-stock'),
                    basis='Candidate '+candidate['candidate_id']+'; '+part['exchange_scope']) for part in parts],
        scope='One module coupon, one selected beam/span and per-car known carrier stock in declared review-layout poses. Missing installed stock is not replaced by boxes.',**FLAGS)
    geometry_path=output/'native-definition.json';geometry_path.write_bytes(encoded(geometry))
    files={'candidate.json':candidate,'materialized-candidate.json':materialized,'evaluations.json':evaluations,
        'selected-beam.json':beam,'manufacturing-bom.json':dict(configuration_sha256=candidate['candidate_id'],
            bounded_products=products,additional_known_stock_lines=additional,installed_inventory=candidate['installed_inventory'],
            unknown_installed_stock_ids=materialized['unknown_installed_stock_ids'],complete_product_cost=False),
        'lifecycle-package.json':package,'assembly.json':_assembly(candidate,products,parts,additional),'planning-revision.json':planning}
    native_result=dict(execution_status='not-run',files=[],scope='Native CAD execution was explicitly disabled; no CAD/STEP substitute is issued.')
    if export_native:
        suffix=sha256(str(output.resolve()).encode()).hexdigest()[:8]
        folder=output/('native-'+candidate['candidate_id'][:12]+'-'+suffix)
        receipt=native.generate(geometry_path,folder,ROOT)
        if receipt.get('fcstd_reopened') is not True or receipt.get('step_reopened') is not True:
            raise ValueError('actual native CAD/STEP reopen evidence required')
        if receipt['input_sha256']!=sha256(geometry_path.read_bytes()).hexdigest() or receipt['part_count']!=len(parts):
            raise ValueError('native selected-candidate stock coverage differs')
        native_result=dict(execution_status='executed',relative_directory=folder.relative_to(output).as_posix(),receipt=receipt,
            files=sorted(receipt['files_sha256']),scope='Actual FreeCAD FCStd/STEP export and reopening for the exact known review-layout stock; no installed fit or physical qualification.')
    bim_folder=output/'bim';bim_field.publish(bim_folder,materialized,beam=beam,include_rail_and_supports=True,allow_incomplete=allow_incomplete)
    bim_check=bim_field.verify(bim_folder,materialized,beam=beam,include_rail_and_supports=True,allow_incomplete=allow_incomplete)
    delivery=delivery_platform.project_twin(planning,configuration_sha256=candidate['candidate_id'],
        unit_costs=dict(guidebeam=products['products'][1]['estimated_material_process_cost_usd']),
        beam_span_m=beam['selection']['span_m'],procurement_lead_days=dict(
            guidebeam=max(row['lead_time_days'] for row in products['products'][1]['cut_schedule'])))
    files['delivery.json']=delivery
    unmodelled=sorted({reference for product in products['products'] for reference in product['geometry_source_ids']} - {part['id'] for part in parts})
    summary=dict(schema='osr-candidate-research-twin/1',candidate_id=candidate['candidate_id'],
        requirement_revision=candidate['requirement_revision'],purpose='next-experiment' if allow_incomplete else 'definition',
        selected_beam=beam['selection'],selected_beam_sha256=products['selected_beam_sha256'],
        geometry_sha256=digest(geometry),native=native_result,bim=bim_check,
        known_native_parts=len(parts),unmodelled_manufacturing_geometry_references=unmodelled,
        unknown_installed_stock_ids=materialized['unknown_installed_stock_ids'],
        complete_installed_distribution=materialized.get('complete_installed_distribution',False),
        evaluation_ids=[row['evaluation_id'] for row in evaluations],
        retained_failed_or_unknown_evaluations=[row['evaluation_id'] for row in evaluations if row['screen_status']!='pass'],
        digital_exports_executed=export_native and bim_check['verified'],
        registered_delivery_scope_priced=delivery['registered_scope_priced'],
        complete_cost_known=False,manufacturing_release=False,
        scope='Source-bound next-experiment stock/coupon twin and common-geography planned delivery. Missing installed parts, unknown mass/CG/inertia, failed engineering screens, native stock gaps and independent acceptance remain holds.',**FLAGS)
    files['twin.json']=summary
    for name,value in files.items():(output/name).write_bytes(encoded(value))
    if sources()!=before:raise ValueError('twin engineering sources changed during export')
    all_files={path.relative_to(output).as_posix():sha256(path.read_bytes()).hexdigest()
               for path in output.rglob('*') if path.is_file()}
    manifest=dict(schema='osr-candidate-research-twin-manifest/1',candidate_id=candidate['candidate_id'],
        requirement_revision=candidate['requirement_revision'],source_sha256=before,files_sha256=all_files,
        native_execution_requested=export_native,allow_incomplete=allow_incomplete,**FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest))
    return read_retained(output)


def read_retained(output):
    """Check retained bytes, candidate identity and actual export receipts."""
    output=Path(output);manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest.get('schema')!='osr-candidate-research-twin-manifest/1' or any(manifest.get(flag) is not False for flag in FLAGS):
        raise ValueError('unreleased research twin manifest required')
    if manifest['source_sha256']!=sources():raise ValueError('retained twin sources stale')
    paths=list(output.rglob('*'))
    if any(path.is_symlink() for path in paths) or {path.relative_to(output).as_posix() for path in paths if path.is_file()}!=set(manifest['files_sha256'])|{'manifest.json'}:
        raise ValueError('exact ordinary twin file inventory required')
    for name,expected in manifest['files_sha256'].items():
        path=output/name
        if '..' in Path(name).parts or Path(name).is_absolute() or sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('retained twin payload differs')
    candidate=contracts.validate_candidate(json.loads((output/'candidate.json').read_bytes()))
    summary=json.loads((output/'twin.json').read_bytes())
    if summary['candidate_id']!=candidate['candidate_id'] or manifest['candidate_id']!=candidate['candidate_id']:
        raise ValueError('retained twin candidate differs')
    allow_incomplete=manifest['allow_incomplete']
    materialized=families.materialize(candidate,allow_incomplete=allow_incomplete)
    if encoded(materialized)!=(output/'materialized-candidate.json').read_bytes():raise ValueError('retained materialized stock or mass state differs')
    beam=manufacturing.selected_beam(materialized,allow_incomplete=allow_incomplete)
    if summary['selected_beam']!=beam['selection'] or any(summary.get(flag) is not False for flag in FLAGS):
        raise ValueError('retained twin selection or acceptance differs')
    products=manufacturing.product_definition(materialized,beam=beam,allow_incomplete=allow_incomplete)
    if summary['selected_beam_sha256']!=products['selected_beam_sha256']:
        raise ValueError('retained twin selected geometry/quantity revision differs')
    package=manufacturing.lifecycle_package(materialized,beam=beam,allow_incomplete=allow_incomplete)
    if encoded(package)!=(output/'lifecycle-package.json').read_bytes():raise ValueError('retained lifecycle candidate/product revision differs')
    evaluations=json.loads((output/'evaluations.json').read_bytes())
    for value in evaluations:
        contracts.validate_result(value)
        if value['candidate_id']!=candidate['candidate_id'] or value['requirement_revision']!=candidate['requirement_revision']:
            raise ValueError('retained twin contains mixed evaluation identities')
    if summary['evaluation_ids']!=[value['evaluation_id'] for value in evaluations]:raise ValueError('retained twin evaluation inventory differs')
    geometry=json.loads((output/'native-definition.json').read_bytes())
    parts=bim_field.exchange_parts(materialized,beam=beam,include_rail_and_supports=True,allow_incomplete=allow_incomplete)
    if summary['geometry_sha256']!=digest(geometry) or geometry['candidate_id']!=candidate['candidate_id']:
        raise ValueError('retained twin native definition identity differs')
    expected_parts=[dict(part,role=part.get('role','selected-candidate-stock'),
        basis='Candidate '+candidate['candidate_id']+'; '+part['exchange_scope']) for part in parts]
    if encoded(geometry['parts'])!=encoded(expected_parts):raise ValueError('retained native/IFC selected stock geometry differs')
    if summary['native']['execution_status']=='executed':
        relative=Path(summary['native']['relative_directory'])
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('owned native export directory required')
        folder=output/relative;receipt=json.loads((folder/'native-cad.json').read_bytes())
        if receipt!=summary['native']['receipt'] or receipt['input_sha256']!=sha256((output/'native-definition.json').read_bytes()).hexdigest() or not receipt['fcstd_reopened'] or not receipt['step_reopened']:
            raise ValueError('retained actual native export receipt differs')
        for name,expected in receipt['files_sha256'].items():
            if sha256((folder/name).read_bytes()).hexdigest()!=expected:raise ValueError('retained native CAD/STEP bytes differ')
    elif manifest['native_execution_requested']:
        raise ValueError('requested native execution lacks its receipt')
    bim_field.verify(output/'bim',materialized,beam=beam,include_rail_and_supports=True,allow_incomplete=allow_incomplete)
    return summary
