"""Native correspondence and explicitly scoped numerical study confirmations."""
from pathlib import Path
import shutil
import subprocess

from engineering.twin_workflow import core
from . import beam_confirmation,evidence


def native(contract,output):
    output.mkdir(parents=True)
    script=output/'generate.py'
    script.write_text('import sys,runpy\nsys.path[:0]='+repr([str(core.ROOT),str(core.ROOT/'design/component-catalogue/src')])+
        '\nmodule=runpy.run_path('+repr(str(core.ROOT/'engineering/design_engine/native_cad.py'))+')\nmodule["native"]('+
        repr(str(contract.resolve()))+','+repr(str(output.resolve()))+')\n')
    script.write_text(script.read_text()+
        'import json,hashlib\nfrom pathlib import Path\nimport FreeCAD as App\n'+
        'definition=json.loads(Path('+repr(str(contract.resolve()))+').read_text())\n'+
        'unit_map={p["id"]:p["manufacturing_unit_id"] for p in definition["parts"] if p.get("manufacturing_unit_id")}\n'+
        'if unit_map:\n'+
        '    path=Path('+repr(str(output.resolve()))+')\n'+
        '    doc=App.openDocument(str(path/"candidate.FCStd"))\n'+
        '    for obj in doc.Objects:\n'+
        '        if hasattr(obj,"PhysicalPartId") and obj.PhysicalPartId in unit_map:\n'+
        '            if not hasattr(obj,"ManufacturingUnitId"): obj.addProperty("App::PropertyString","ManufacturingUnitId")\n'+
        '            obj.ManufacturingUnitId=unit_map[obj.PhysicalPartId]\n'+
        '    doc.save();App.closeDocument(doc.Name)\n'+
        '    doc=App.openDocument(str(path/"candidate.FCStd"))\n'+
        '    actual={obj.PhysicalPartId:obj.ManufacturingUnitId for obj in doc.Objects if hasattr(obj,"PhysicalPartId") and hasattr(obj,"ManufacturingUnitId")}\n'+
        '    App.closeDocument(doc.Name)\n'+
        '    proof=json.loads((path/"native-cad.json").read_text());proof["manufacturing_unit_ids_preserved"]=(actual==unit_map)\n'+
        '    proof["files_sha256"]={name:hashlib.sha256((path/name).read_bytes()).hexdigest() for name in proof["files_sha256"]}\n'+
        '    (path/"native-cad.json").write_text(json.dumps(proof,sort_keys=True,indent=2)+"\\n")\n')
    try:
        binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
        command=[binary] if binary else ['flatpak','run','--filesystem='+str(core.ROOT),
            '--filesystem='+str(output.parent.resolve()),'--command=FreeCADCmd','org.freecad.FreeCAD']
        with (output/'freecad.log').open('w') as log:
            subprocess.run([*command,str(script)],stdout=log,stderr=subprocess.STDOUT,timeout=600,check=True)
        proof=core.read(output/'native-cad.json',maximum=10_000_000)
        if proof['input_sha256']!=core.sha(contract) or not all(proof[k] for k in ('physical_ids_preserved','native_reopened','step_volume_reconciled')) or proof.get('manufacturing_unit_ids_preserved') is False:
            return None,'failed','native child identity/correspondence failed'
        return proof,'passed',None
    except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as exc:
        log=output/'freecad.log'
        text=log.read_text(errors='replace') if log.exists() else ''
        failures=('native physical correspondence failed','defined materials collide','native reopen changed identities','STEP round-trip occupied volume differs')
        state='failed' if any(message in text for message in failures) else 'hold'
        return None,state,str(exc)


def numerical(kind,physics,values,output):
    checks={};record={}
    if kind=='mechanical-roof-study':
        import numpy as np
        from engineering.civil_exploration.constitutive import laminate
        glass=physics['glass']
        plies=[dict(thickness_m=p['thickness_m'],angle_deg=p['angle_deg'],E1_pa=glass['e1_pa'],E2_pa=glass['e2_pa'],
            G12_pa=glass['g12_pa'],nu12=glass['poisson12']) for p in physics['plies']]
        skin=laminate(plies)
        shift=physics['core_m']/2+physics['bond_m']+sum(p['thickness_m'] for p in plies)/2
        # Registered schedules are symmetric; the reflected outer face gives B=0.
        first=np.asarray(skin['A_n_m']);b=np.asarray(skin['B_n']);d=np.asarray(skin['D_nm'])
        recovered=dict(A=2*first,B=np.zeros((3,3)),D=2*(d+shift**2*first)-4*shift*b)
        for key,array in recovered.items():
            target=np.asarray(physics['abd'][key])
            checks['independent-laminate-'+key]=bool(np.allclose(array,target,rtol=1e-7,atol=1e-6))
        record=dict(reference_skin=skin,scope='Independent face-ply ABD comparison only; curved roof shell/contact/strength remain open')
    elif kind=='mechanical-equipment-study':
        from .zone_thermal import solve
        beam=physics['beam']
        fine=beam_confirmation.solve(1.2,[0.,1.2],beam['ei_nm2'],uniform=beam['force_n']/1.2,divisions=32)
        checks['carrier-beam-independent-solution']=abs(fine['maximum_nodal_deflection_m']/beam['deflection_m']-1)<.02
        checks['carrier-equilibrium']=fine['force_balance_relative_error']<1e-7
        refined=solve(physics['hvac_inputs'],module_count=values['hvac_modules'],failed_modules=1,
            flow_m3_s=values['flow_m3_s'],duct_area_m2=values['duct_area_m2'],layout=values['duct_layout'],step_s=5.)
        checks['two-zone-time-refinement']=abs(refined['maximum_temperature_c']-physics['hvac_failed']['maximum_temperature_c'])<.1
        checks['sensible-heat-conservation']=abs(refined['sensible_energy_balance_residual_j'])<1e-5
        checks['water-conservation']=abs(refined['moisture_balance_residual_kg'])<1e-8
        record=dict(beam=fine,refined_zones=refined,scope='Ideal supported gross beam and declared two-zone heat/moisture balance; no joint stress or CFD')
    else:
        from engineering.civil_exploration.model import System
        candidate,study=physics['candidate'],physics['study']
        refined=System(candidate,study,study['ground_scenarios'][0],8).static_envelope()
        for key in ('deck_displacement_m','bending_moment_nm'):
            first=physics['response']['envelope'][key];second=refined['envelope'][key]
            checks['static-mesh/'+key]=abs(first-second)/max(abs(second),1e-12)<study['analysis']['convergence_relative_limit']
        record=dict(refined_static=refined,scope='Existing 2D elastic bridge/pier/foundation springs and moving load statics; material, perfect bond, ground and dynamics unqualified')
        if kind=='civil-kit-study':
            from .construction_stage import handling
            from . import civil_kit
            checks['manufactured-unit-contract']=all(civil_kit.validate_kit(physics['kit']).values())
            controls=[]
            for unit in physics['handling']['units']:
                for stage in unit['stages']:
                    length=stage['length_m'];q=stage['uniform_n_m']
                    solved=beam_confirmation.solve(length,stage['picks_m'],stage['ei_nm2'],uniform=q,divisions=32)
                    checks[unit['unit_id']+'/'+stage['stage']+'/independent-reactions']=all(abs(r['value']-q*length/2)/max(q*length,1)<1e-7 for r in solved['reactions'])
                    checks[unit['unit_id']+'/'+stage['stage']+'/mesh-refinement']=abs(solved['maximum_nodal_deflection_m']-stage['maximum_deflection_m'])/max(solved['maximum_nodal_deflection_m'],1e-12)<.03
            record['scope']+='; unit/revision mass mapping, gross handling beam controls and refinement only. Actual temporary works, connections, QA and strength development remain open.'
    checks['independent-beam-controls']=all(row['passed'] for row in beam_confirmation.benchmarks())
    report=dict(checks=checks,record=record,physical_release=False)
    core.write(output/'study-numerical-confirmation.json',report,exclusive=True)
    return report


def evaluate(envelope,output,children):
    if len(children)!=1:raise ValueError('one exact multidisciplinary child required')
    child=children[0]
    folder=Path(child['folder'])/'output'
    contract=core.read(folder/'physical-contract.json',maximum=20_000_000)
    physics=core.read(folder/'physics.json',maximum=20_000_000)
    if child['result'].get('physical_contract_sha256')!=core.sha(folder/'physical-contract.json') or child['result'].get('physics_sha256')!=core.sha(folder/'physics.json'):
        raise ValueError('exact physical/analysis child correspondence required')
    core.write(output/'physical-contract.json',contract,exclusive=True)
    proof,state,error=native(output/'physical-contract.json',output/'cad')
    checked=numerical(child['task']['kind'],physics,child['task']['parameters']['variables'],output)
    numeric=all(checked['checks'].values())
    levels={level:dict(state='not_run',checks=[]) for level in evidence.LEVELS}
    levels['analytical_screening']=dict(state='passed' if child['result']['study_pass'] else 'failed',checks=['original_study'])
    levels['native_geometry']=dict(state=state,checks=['native_exact_child'])
    for level in ('numerical_confirmation','numerical_robustness'):
        levels[level]=dict(state='passed' if numeric else 'failed',checks=list(checked['checks']),scope=checked['record']['scope'])
    checks=dict(checked['checks'],original_study=child['result']['study_pass'],native_exact_child=True if state=='passed' else False if state=='failed' else None)
    return dict(study_pass=all(value is True for value in checks.values()),checks=checks,
        failed_checks=[key for key,value in checks.items() if value is False],held_checks=[key for key,value in checks.items() if value is None],
        verification=dict(evaluated_level='numerical_robustness',levels=levels,independent_physics_rerun=True,
            scope=checked['record']['scope']),metrics=dict(native_part_count=len(contract['parts']) if proof else None),
        errors=[error] if error else [],children=[dict(key=child['key'],kind=child['task']['kind'],study_pass=child['result']['study_pass'])],
        scope='Native solids and bounded discipline-specific numerical confirmation; no full manufacturing/physical qualification',**core.FLAGS)
