"""Calibration/holdout contracts, physical test protocols and promotion gates."""
from __future__ import annotations
from pathlib import Path
import math

from engineering.analysis import structural_release
from .contracts import encoded,identity,load,sha,ROOT
from .workflow import verify

TESTS=['concrete-and-frp-coupons','connector-bond-slip-fatigue','tendon-anchorage-losses','pier-cyclic-ductility',
       'pile-axial-lateral-instrumented','representative-assembly-load-test','transport-and-first-lift',
       'durability-fire-and-inspection']
METHODS={
 'concrete-and-frp-coupons':('Actual batches/orientations; compression, tension, creep and temperature sweeps',['load','strain','temperature','age','failure mode']),
 'connector-bond-slip-fatigue':('Representative connection geometry; normal/shear cycles, bond/slip and fatigue',['normal load','shear load','slip','strain','crack opening','cycles']),
 'tendon-anchorage-losses':('Supplier tendon/anchorage system; transfer, slip, relaxation and staged losses',['tendon force','anchor slip','concrete strain','time','end-zone cracking']),
 'pier-cyclic-ductility':('Actual reinforcement/confinement and axial force; reviewed lateral cyclic protocol',['axial force','moment','drift','residual drift','strain','joint opening']),
 'pile-axial-lateral-instrumented':('Site ground investigation and installed pile method; axial/lateral instrumented tests',['load','head settlement','lateral displacement','depth strain','groundwater','time']),
 'representative-assembly-load-test':('Complete span/pier/foundation representative assembly and reviewed train/thermal cases',['reactions','deflection','acceleration','strain','bearing motion','settlement']),
 'transport-and-first-lift':('Weighed member and actual route, rigging, crane/launcher chart and supports',['mass','centre of gravity','sling forces','ground pressure','movement','temporary strain']),
 'durability-fire-and-inspection':('Actual exposure/material system; reviewed deterioration/fire and repair/inspection trials',['temperature history','residual stiffness','bond','degradation','inspection access','repair effectiveness'])}


def fit_and_holdout(dataset):
    required={'schema','property','unit','specimen_batch','source','source_sha256','measurement_uncertainty','calibration','holdout'}
    if set(dataset)!=required or dataset['schema']!='osr-civil-validation-data/1' or dataset['property']!='youngs_modulus' or dataset['unit']!='Pa':
        raise ValueError('validation dataset contract mismatch')
    source=(ROOT/dataset['source']).resolve()
    if not source.is_relative_to(ROOT) or not source.is_file() or sha(source)!=dataset['source_sha256']:
        raise ValueError('physical dataset source is missing or stale')
    if not dataset['specimen_batch'] or type(dataset['measurement_uncertainty']) not in (int,float) or not math.isfinite(dataset['measurement_uncertainty']) or dataset['measurement_uncertainty']<0:
        raise ValueError('batch or measurement uncertainty absent')
    calibration,holdout=dataset['calibration'],dataset['holdout']
    if len(calibration)<2 or len(holdout)<2:raise ValueError('independent calibration and holdout samples required')
    if {r['specimen_id'] for r in calibration}&{r['specimen_id'] for r in holdout}:
        raise ValueError('calibration/holdout specimen leakage')
    for row in calibration+holdout:
        if set(row)!={'specimen_id','strain','stress_pa'} or not row['specimen_id'] or not all(type(row[k]) in (int,float) and math.isfinite(row[k]) for k in ('strain','stress_pa')):
            raise ValueError('invalid specimen measurement')
    denominator=sum(r['strain']**2 for r in calibration)
    if not denominator:raise ValueError('zero calibration strain')
    modulus=sum(r['strain']*r['stress_pa'] for r in calibration)/denominator
    if modulus<=0:raise ValueError('nonpositive fitted modulus')
    error=math.sqrt(sum((modulus*r['strain']-r['stress_pa'])**2 for r in holdout)/len(holdout))
    scale=math.sqrt(sum(r['stress_pa']**2 for r in holdout)/len(holdout))
    return dict(fitted_modulus_pa=modulus,holdout_rmse_pa=error,normalised_holdout_rmse=error/scale if scale else None,
                uncertainty_pa=dataset['measurement_uncertainty'],dataset_sha256=identity(dataset),
                calibration_specimens=[r['specimen_id'] for r in calibration],holdout_specimens=[r['specimen_id'] for r in holdout],
                physical_acceptance=False,limits_required=True)


def protocols(output,candidate_ids):
    if output.exists():raise ValueError('test protocol output must be new')
    output.mkdir(parents=True)
    rows=[]
    for name in TESTS:
        rows.append(dict(test=name,candidates=list(candidate_ids),owner=None,laboratory=None,
                         investigation=METHODS[name][0],required_measurements=METHODS[name][1],
                         stop_conditions='To be set by the responsible engineer/laboratory before any physical loading',
                         specimens=None,controlled_standard=None,acceptance_limits=None,instrument_calibration=None,
                         calibration_holdout_plan=None,source_rights=None,measurement_uncertainty=None,
                         observed_results=None,independent_review=None,status='awaiting-project-inputs'))
    packet=dict(schema='osr-civil-test-programme/1',tests=rows,procurement_released=False,physical_release=False)
    (output/'test-programme.json').write_bytes(encoded(packet))
    return packet


def promotion(bundle,output,*,design=None,receipt_manifest=None,evidence_root=None):
    """Produce a sealed proposal and invoke the existing gate when supplied.

    This command never writes canonical products, finances or ERP records.
    Missing project evidence is an explicit blocked result, not a fabricated pass.
    """
    if output.exists():raise ValueError('promotion packet must be new')
    manifest=verify(bundle);study=load(bundle/'study.json')
    if not manifest['complete']:raise ValueError('incomplete campaign cannot be handed over')
    ids=[c['candidate_id'] for c in manifest['cases']]
    output.mkdir(parents=True)
    native_inventory={item['path']:item['sha256'] for item in manifest['evaluations']}
    packet=dict(schema='osr-civil-promotion-proposal/1',candidate_ids=ids,study_sha256=manifest['study_sha256'],
                campaign_manifest_sha256=sha(bundle/'manifest.json'),native_records=native_inventory,
                impacts=['CAD/IFC revisions','reinforcement/material catalogue','BOM and supplier selection','construction sequence and equipment',
                         'cost and finance inputs','maintenance and inspection','city-specific structural release'],
                existing_change_workflow='tools/automation/engineering-change.py',physical_release=False,operating_release=False)
    gate=None
    supplied=[design,receipt_manifest,evidence_root]
    if any(supplied) and not all(supplied):raise ValueError('design, receipt manifest and evidence root must be supplied together')
    if all(supplied):
        gate=structural_release.build_report(design,receipt_manifest,evidence_root,inspect=True)
    packet['existing_structural_gate']=gate
    candidate_outcomes=[load((bundle/item['path']).parent/'result.json') for item in manifest['evaluations']
                        if load(bundle/item['path'])['status']=='completed']
    qualified=bool(candidate_outcomes) and all(r.get('engineering_feasibility')=='feasible' and r.get('physical_validation') is True for r in candidate_outcomes)
    packet['status']='blocked-awaiting-physical-and-independent-evidence' if gate is None or not gate['authority_accepted'] or not qualified else 'reviewed-proposal-ready-for-existing-change-process'
    packet['candidate_specific_qualification']=qualified
    packet['physical_release']=False
    packet['unresolved_inputs']=['accepted project requirements and code editions','measured material and soil datasets','supplier train/equipment/price records',
                                 'instrumented physical validation','independent structural/geotechnical review','existing authority acceptance'] if gate is None else gate['missing_technical_roles']
    (output/'proposal.json').write_bytes(encoded(packet))
    (output/'seal.json').write_bytes(encoded(dict(schema='osr-civil-proposal-seal/1',files={'proposal.json':sha(output/'proposal.json')},
                                                 accepted=False,signature=None)))
    return packet
