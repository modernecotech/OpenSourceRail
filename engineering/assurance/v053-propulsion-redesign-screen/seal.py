"""Archive construction only: source-bound comparison and complete file receipt."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,tomllib
BASE=Path(__file__).resolve().parent

def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def write(name,value):(BASE/name).write_bytes(encoded(value))
if __name__=='__main__':
 original=json.loads((BASE/'executed/manifest.json').read_bytes());replay=json.loads((BASE/'selected-replay-receipt.json').read_bytes());boundary=json.loads((BASE/'executed/current-boundary-diagnostic.json').read_bytes())
 actual=next(r for r in boundary['rows'] if r['requested_q_current_a']==1349.)
 mass=replay['current_candidate_aw3_mass_kg_per_car'];force=actual['force_x_n_per_car']
 context={'engineering/ferrite_maglev/full-dynamics.toml':'comparison-context/engineering/ferrite_maglev/full-dynamics.toml','engineering/ferrite_maglev/station.toml':'comparison-context/engineering/ferrite_maglev/station.toml'}
 dynamics=tomllib.loads((BASE/context['engineering/ferrite_maglev/full-dynamics.toml']).read_text());station=tomllib.loads((BASE/context['engineering/ferrite_maglev/station.toml']).read_text());motion=station['motion'];resistance=motion['resistance_constant_n_per_car']+motion['resistance_quadratic_n_per_car']*20**2
 rows=[]
 for label,source,keys,acceleration in [('current full-dynamics route request','engineering/ferrite_maglev/full-dynamics.toml',['route_acceleration_m_s2'],dynamics['route_acceleration_m_s2']),('existing station-study setting','engineering/ferrite_maglev/station.toml',['motion','acceleration_m_s2'],motion['acceleration_m_s2']),('illustrative comparison only, not current requirement',None,[],1.)]:
  rows.append(dict(context=label,source_path=source,key_path=keys,acceleration_m_s2=acceleration,inertial_force_required_n_per_car=mass*acceleration,ideal_force_margin_n_per_car=force-mass*acceleration))
 write('acceleration-comparison.json',dict(schema='osr-propulsion-acceleration-comparison/1',parent_configuration_sha256=original['canonical_configuration_sha256'],hypothesis_sha256=boundary['hypothesis_sha256'],
   current_candidate_aw3_mass_kg_per_car=mass,conditional_force_n_per_car=force,ideal_acceleration_upper_bound_m_s2=force/mass,contexts=rows,new_hypothesis_mass_reconciled=False,
   inherited_resistance_proxy_at_20m_s_n_per_car=resistance,route02_margin_after_inherited_resistance_proxy_n_per_car=force-mass*dynamics['route_acceleration_m_s2']-resistance,
   scope='One conditional40C map at20m/s andactualfinitegroupoverlap,1349A. CurrentcanonicalAW3comparisonmassonly; no reconciledchangedhypothesismass. Resistanceproxyisolderunqualifiedstationcontext. No fullprofile,grade,phase,currenttransient,installedlength,sharing,cooling,duty,launchacceptance.',
   launch_profile_feasible=False,configuration_adopted=False,design_complete=False,physical_validation=False,manufacturing_release=False,physical_release=False))
 files={p.relative_to(BASE).as_posix():sha256(p.read_bytes()).hexdigest() for p in BASE.rglob('*') if p.is_file() and p.name!='archive-receipt.json'}
 commands=[line.strip() for line in (BASE/'executed/reproduction.txt').read_text().splitlines() if line.startswith('OPENBLAS_NUM_THREADS=')]
 receipt=dict(schema='osr-propulsion-redesign-archive/1',archived_utc=datetime.now(timezone.utc).isoformat(),files_sha256=files,
   original_manifest_sha256=sha256((BASE/'executed/manifest.json').read_bytes()).hexdigest(),original_working_directory='/home/hayder/Documents/OpenSourceRail',original_execution_directory='build/propulsion-redesign-screen',original_commands=commands,
   source_archive_mapping={name:'inputs/'+name for name in original['source_sha256']},executed_file_mapping={name:'executed/'+name for name in original['files_sha256']},comparison_context_mapping=context,
   parent_configuration_sha256=original['canonical_configuration_sha256'],selected_research_hypothesis_sha256=boundary['hypothesis_sha256'],
   source_unchanged_after_execution=original['production_sources_unchanged'],scope='Separate unreleasedresearchappendix; byte-identicaloriginalcampaignandactualselectedportablecouponreplay. No canonical/design/physicaladoption.',
   design_complete=False,physical_validation=False,manufacturing_release=False,physical_release=False,physical_output_authorised=False,engineering_accepted=False,canonical_adoption=False,configuration_adopted=False)
 write('archive-receipt.json',receipt)
 print(json.dumps(dict(files=len(files),archive_receipt_sha256=sha256((BASE/'archive-receipt.json').read_bytes()).hexdigest(),original_manifest_sha256=receipt['original_manifest_sha256'],ideal_acceleration_upper_bound_m_s2=force/mass)))
