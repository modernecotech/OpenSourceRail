import json, hashlib, subprocess, time
from pathlib import Path
from engineering.station_rail.common import encoded, identity
from engineering.outline import city_project_cost
RUN=Path(__file__).parent
ROOT=Path('/home/hayder/.local/state/opensourcerail/worktrees/v06-design-closure-20261108')
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
summary=json.loads((RUN/'summary.json').read_bytes())
base=json.loads((RUN/'cost-project-make-buy.json').read_bytes())
china=json.loads((RUN/'cost-china-bulk-buy.json').read_bytes())
assert base['source_sha256']==china['source_sha256']
assert base['evaluation_id']==identity({k:v for k,v in base.items() if k!='evaluation_id'})
assert china['evaluation_id']==identity({k:v for k,v in china.items() if k!='evaluation_id'})
stdout=RUN/'stdout.log';stderr=RUN/'stderr.log'
exe={
 'schema':'osr-samawah-china-bulk-cost-execution/1',
 'execution_time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
 'source_commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
 'candidate_ids':summary['reference_candidate_ids'],
 'case_evaluation_id':summary['prior_case_evaluation_id'],
 'service_evaluation_id':summary['service_identity'],
 'cost_evaluation_ids':{k:v['cost_evaluation_id'] for k,v in summary['scenarios'].items()},
 'request_id':json.loads((RUN/'request.json').read_bytes())['request_id'],
 'summary_id':summary['summary_id'],
 'source_sha256':base['source_sha256'],
 'source_pin_count':len(base['source_sha256']),
 'resources':{'cpu_time_limit_s':120,'address_space_limit_bytes':1073741824,'wall_timeout_s':120,
     'observed_elapsed_wall_s':2.65,'observed_user_cpu_s':2.42,'observed_max_rss_kib':273828},
 'execution_boundary':{'cad_or_fem_invoked':False,'gis_invoked':False,'erpnext_transactions':0,
     'external_supplier_lookup_invoked':False,'network_lookup_invoked':False,'network_blocked':False,
     'os_sandbox_enforced':False,'process_limits_applied':True,
     'note':'Only the deterministic city cost evaluator ran. Network was not blocked; no client or supplier lookup was invoked.'},
 'stdout_sha256':h(stdout),'stderr_sha256':h(stderr),
 'release_flags':summary['release_flags']}
exe['execution_id']=identity(exe)
(RUN/'execution.json').write_bytes(encoded(exe))

low=summary['scenarios']['project-make-buy'];high=summary['scenarios']['china-bulk-buy']
lines=[]
lines += ['# Samawah China bulk purchase vs project make/buy — bounded cost case','',
 'This private, source-bound sample revalues one existing five-line Samawah sensitivity under two supply scenarios. It is not a local demand forecast, supplier quotation, or complete/accepted railway design. The physical reference is `756a6887…` / body `9489e4f2…`; the newer compact-drive candidate `75075d…` is not mixed into this result.','',
 '## Same-candidate scope','',
 '- Candidate: `'+summary['reference_candidate_ids']['candidate_id']+'` (body `'+summary['reference_candidate_ids']['body_candidate_id']+'`).',
 '- City input: `'+summary['city_input_id']+'`; route: '+f"{summary['city_route_km']:.3f} km"+' across five mapped lines.',
 '- Planning sensitivity: line-1 at 1,200 passengers/hour/direction; lines 2–5 at 4,000. This was inherited from the source-bound Samawah five-line sensitivity and is explicitly **not surveyed demand**.',
 '- Service, fleet, physical quantities and alignment are held identical between pricing cases. '+str(summary['active_and_reserve_trainsets'])+' total trainsets are present in this service scenario.',
 '- Fourteen cost scopes are recalculated. The reference project-make/buy run exactly reproduces the archived longest-line sensitivity CAPEX, NPV, price/km and scope totals before the China case is compared.',
 '',
 '## Calculated low/base/high totals (USD)','',
 '| Scenario | Installed CAPEX | Whole-life NPV | CAPEX per route-km |',
 '| --- | ---: | ---: | ---: |']
for name in ('project-make-buy','china-bulk-buy'):
 s=summary['scenarios'][name]
 def tri(x): return f"${x['low']:,.0f} / ${x['base']:,.0f} / ${x['high']:,.0f}"
 lines.append(f"| `{name}` | {tri(s['installed_capital_usd'])} | {tri(s['whole_life_npv_usd'])} | {tri(s['price_per_route_km_usd'])} |")
lines += ['',
 f"At the base case, China-bulk-buy is **${summary['capital_delta_usd_china_minus_project_make_buy']['base']:,.0f} higher CAPEX** (+{summary['capital_delta_usd_china_minus_project_make_buy']['base']/low['installed_capital_usd']['base']*100:.2f}%) and **${summary['npv_delta_usd_china_minus_project_make_buy']['base']:,.0f} higher 30-year NPV** (+{summary['npv_delta_usd_china_minus_project_make_buy']['base']/low['whole_life_npv_usd']['base']*100:.2f}%) in this modeled case. China-bulk-buy is not a saving in these inputs.",
 '', '## Base-case delta by cost scope (China bulk minus project make/buy)','',
 '| Scope | Delta USD |','| --- | ---: |']
for scope,delta in summary['base_scope_delta_usd_china_minus_project_make_buy'].items():
 lines.append(f"| `{scope}` | ${delta:,.0f} |")
lines += ['',
 '## What the prices represent','',
 '- The source bundle `engineering/outline/data/china-supply-20261104.json` has dataset ID `'+summary['supply_dataset_id']+'`, 13 repository observations dated 4 November 2026. They include China-origin advertised prices/statistical inputs, not confirmed offers. The model marks these as unconfirmed and unqualified.',
 '- `china-bulk-buy` uses the repository’s China-origin benchmark and calculated finished-stock proxies. The model adds explicit freight, insurance, duty, receiving/QA and local-delivery allowances where applicable. No project-specific supplier contract, Incoterm, container fit, customs quote, or negotiated fleet-volume discount was available to this calculation.',
 '- `project-make-buy` chooses the modeled least-cost make or buy route at this city volume, with local labour/process assumptions and shared plant/tooling charged through the project accounts. Material inputs are still modeled from landed benchmark rates; this is not an Iraqi factory quotation.',
 '- This does not price 266 cities at aggregated purchasing volume. No additional blanket discount was invented. A real multi-city consolidated order may change economics, but it needs matched quantities, logistics, financing, factory capacity and sourced volume tiers.',
 '- The large uncertainty range remains: both project cases are cost-model outputs, not calibrated project estimates. The result only answers which of these two existing assumptions ranks lower for this one sensitivity.',
 '',
 '## Evidence and limits','',
 '- Reproducible cost evaluator source pins: '+str(exe['source_pin_count'])+' files; exact input case and city hashes are in `request.json`.',
 '- Reference project make/buy replay matches the prior sealed case exactly; all 14 scope totals are included in `cost-project-make-buy.json` and `cost-china-bulk-buy.json`.',
 '- The service uses the common outline control where not perturbed. Passenger forecast, completed alignment, available propulsion force, independent brake map, grades, local site rates and operating performance remain unverified.',
 '- The comparison changes pricing assumptions only; no selected baseline changed and all engineering, manufacturing, procurement and operating-release flags remain false.',
 '- Execution limits: 120 s CPU, 1 GiB address space, 120 s timeout; measured 2.65 s wall, 273,828 KiB peak RSS. No CAD, FEM, GIS or external transaction ran. Network was not OS-blocked, but no network client was invoked.',
 '- Failed execution attempts 01–03 are retained beside this successful run. They are not used as evidence; the successful run is `04`.',
 '',
 'Artifacts: `request.json`, `summary.json`, two full cost records, `execution.json`, `run.py`, `run.sh`, and captured logs. `manifest.json` seals the packet.']
(RUN/'README.md').write_text('\n'.join(lines)+'\n')
files={p.relative_to(RUN).as_posix():h(p) for p in sorted(RUN.iterdir()) if p.is_file() and p.name!='manifest.json'}
manifest={
 'schema':'osr-samawah-china-bulk-cost-packet/1',
 'request_id':json.loads((RUN/'request.json').read_bytes())['request_id'],
 'summary_id':summary['summary_id'],'execution_id':exe['execution_id'],
 'candidate_ids':summary['reference_candidate_ids'],
 'source_commit':exe['source_commit'],'source_sha256':exe['source_sha256'],
 'files_sha256':files,'file_count':len(files),'release_flags':summary['release_flags']}
manifest['manifest_id']=identity(manifest)
(RUN/'manifest.json').write_bytes(encoded(manifest))
print(json.dumps({'manifest_id':manifest['manifest_id'],'files':len(files),'base_capex_delta':summary['capital_delta_usd_china_minus_project_make_buy']['base'],'base_npv_delta':summary['npv_delta_usd_china_minus_project_make_buy']['base']}))
