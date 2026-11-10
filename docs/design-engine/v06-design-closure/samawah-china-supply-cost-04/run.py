from __future__ import annotations
import gzip, json, hashlib
from pathlib import Path
from engineering.outline import city_project_cost, coordinator
from engineering.station_rail.common import digest, encoded, identity

ROOT = Path('/home/hayder/.local/state/opensourcerail/worktrees/v06-design-closure-20261108')
RUN = Path('/home/hayder/.local/state/opensourcerail/runs/v06-design-closure-20261108/samawah-china-supply-cost-04')
PRIOR = Path('/home/hayder/.local/state/opensourcerail/runs/v06-design-closure-20261108/samawah-line-demand-sensitivity-run-03')
CASE_PATH = PRIOR / 'cases/longest-line-lower-sensitivity.json.gz'
CITY_PATH = PRIOR / 'city-input.json.gz'
PRIOR_MANIFEST_PATH = PRIOR / 'manifest.json'


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_gz(path: Path):
    return json.loads(gzip.decompress(path.read_bytes()))

prior_manifest_raw = PRIOR_MANIFEST_PATH.read_bytes()
prior_manifest = json.loads(prior_manifest_raw)
assert prior_manifest['manifest_id'] == identity({k:v for k,v in prior_manifest.items() if k!='manifest_id'})
for rel,path in [('city-input.json.gz',CITY_PATH),('cases/longest-line-lower-sensitivity.json.gz',CASE_PATH)]:
    assert sha(path.read_bytes()) == prior_manifest['files_sha256'][rel], rel
case_raw=CASE_PATH.read_bytes();city_raw=CITY_PATH.read_bytes()
case=load_gz(CASE_PATH);city=load_gz(CITY_PATH)
assert city['input_id']==case['input_id']==case['service_evaluation']['city_input_id']
assert city['reference_candidate_ids']==case['reference_candidate_ids']
assert case['reference_candidate_ids']['candidate_id']=='756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
assert case['reference_candidate_ids']['body_candidate_id']=='9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117'
assert case['policy']['line_peak_demand_pphpd']=={
    'line-1':1200.0,'line-2':4000.0,'line-3':4000.0,'line-4':4000.0,'line-5':4000.0}
assert case['policy']['demand_source']=='One-line sensitivity only: lower-demand perturbation on the longest mapped line; not a local forecast.'
assert case['source_sha256']['engineering/outline/city_project_cost.py']==digest(ROOT/'engineering/outline/city_project_cost.py')
# Exact archived case source epoch was compared with all 58 current source pins before this run.
for rel,expected in case['source_sha256'].items():
    assert digest(ROOT/rel)==expected, rel
for rel,expected in case['service_evaluation']['source_sha256'].items():
    assert digest(ROOT/rel)==expected, rel
context=coordinator.prepare(ROOT)
assert context['vehicle']['candidate_id']==case['reference_candidate_ids']['candidate_id']
assert context['vehicle']['evaluation_id']==case['service_evaluation']['line_services'][0]['service']['reference_vehicle_evaluation_id']

records={}
for scenario in ('project-make-buy','china-bulk-buy'):
    value=city_project_cost.evaluate_city_cost(city,case['service_evaluation']['line_services'],context,
        policy={'project':{'pricing_scenario':scenario}},root=ROOT)
    assert value['city_input_id']==city['input_id']
    assert value['assumptions']['policy']['pricing_scenario']==scenario
    assert set(value['scope_totals_usd'])=={
        'rolling-stock','guideway','stations-power','factory-tooling','construction',
        'land-utilities-depot','fleet','energy','operations','maintenance','renewals',
        'recovery','reliability','disposal'}
    assert all(value.get(flag) is False for flag in (
        'physical_accepted','engineering_accepted','manufacturing_release','operating_release',
        'procurement_approved','selected_reference_changed','movement_authority'))
    records[scenario]=value

baseline=records['project-make-buy']
archived=case['cost']
for key in ('installed_capital_usd','whole_life_npv_usd','price_per_route_km_usd','scope_totals_usd'):
    assert baseline[key]==archived[key], f'baseline replay mismatch: {key}'
china=records['china-bulk-buy']
delta={s:{c:round(china['scope_totals_usd'][s][c]-baseline['scope_totals_usd'][s][c],2)
          for c in ('low','base','high')} for s in baseline['scope_totals_usd']}
summary={
    'schema':'osr-samawah-china-bulk-vs-project-make-buy/1',
    'case_name':'longest-line-lower-sensitivity',
    'city':'Samawah', 'city_input_id':city['input_id'],
    'demand_interpretation':'One-line planning sensitivity: line-1 1,200 pphpd; lines 2–5 4,000 pphpd; not surveyed.',
    'reference_candidate_ids':case['reference_candidate_ids'],
    'reference_vehicle_evaluation_id':context['vehicle']['evaluation_id'],
    'prior_case_evaluation_id':case['evaluation_id'],
    'prior_cost_evaluation_id':archived['evaluation_id'],
    'service_identity':case['service_evaluation']['evaluation_id'],
    'line_service':[{k:r[k] for k in ('line_id','requirements','service','propulsion_hypothesis')}
                    for r in case['service_evaluation']['line_services']],
    'same_physical_quantities_and_service':True,
    'city_route_km':sum(line['route_m'] for line in city['lines'])/1000,
    'active_and_reserve_trainsets':sum(r['service']['total_trainsets'] for r in case['service_evaluation']['line_services']),
    'supply_dataset_id':json.loads((ROOT/'engineering/outline/data/china-supply-20261104.json').read_text())['dataset_id'],
    'supply_dataset_observed_at':'2026-11-04 (repository observations; no supplier confirmation)',
    'scenarios':{},
    'base_scope_delta_usd_china_minus_project_make_buy':{s:v['base'] for s,v in delta.items()},
    'capital_delta_usd_china_minus_project_make_buy':{
        c:round(china['installed_capital_usd'][c]-baseline['installed_capital_usd'][c],2)
        for c in ('low','base','high')},
    'npv_delta_usd_china_minus_project_make_buy':{
        c:round(china['whole_life_npv_usd'][c]-baseline['whole_life_npv_usd'][c],2)
        for c in ('low','base','high')},
    'limitations':[
        'China advertised and statistical prices are provisional Class C inputs, not supplier-confirmed quotations or validity-backed offers.',
        'No additional negotiated bulk discount is supported by this comparison; dataset discounts, where present, are not a project-specific volume contract.',
        'The China-bulk-buy purchase route applies explicit modelled freight, insurance, duty, receiving/QA and local delivery allowances; commercial terms and actual logistics remain unverified.',
        'Project make/buy uses modeled landed material rates and Iraqi loaded labour/process assumptions plus factory/tooling allocations; it is not a local-factory quote.',
        'Only the source-matched Samawah five-line demand sensitivity is evaluated; it cannot be transferred to Baghdad or the other 264 city outlines.',
        'The physical reference is 756a/9489, not compact-drive 75075; all prices are conditional on the retained wheel-supported reference and its unqualified study service.',
        'This revalues the full fourteen cost accounts under the existing model but does not close alignment, demand, propulsion, braking, local site rates, city-catalogue or release gates.'
    ],
    'release_flags':{k:False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','procurement_approved','selected_reference_changed','movement_authority')}
}
for scenario,value in records.items():
    summary['scenarios'][scenario]={
        'cost_evaluation_id':value['evaluation_id'],
        'installed_capital_usd':value['installed_capital_usd'],
        'whole_life_npv_usd':value['whole_life_npv_usd'],
        'price_per_route_km_usd':value['price_per_route_km_usd'],
        'scope_totals_usd':value['scope_totals_usd'],
        'production_supply':value['production_supply'],
        'source_sha256':value['source_sha256']}
summary['summary_id']=identity(summary)
(RUN/'summary.json').write_bytes(encoded(summary))
# Full evaluated cost records are retained, source-bound by their own evaluation IDs.
(RUN/'cost-project-make-buy.json').write_bytes(encoded(baseline))
(RUN/'cost-china-bulk-buy.json').write_bytes(encoded(china))
request={
    'schema':'osr-samawah-china-bulk-cost-request/1',
    'source_commit':__import__('subprocess').check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
    'prior_sensitivity_source_commit':prior_manifest['source_commit'],
    'prior_sensitivity_manifest_id':prior_manifest['manifest_id'],
    'prior_sensitivity_manifest_sha256':sha(prior_manifest_raw),
    'prior_case_path':str(CASE_PATH), 'prior_case_sha256':sha(case_raw),
    'city_input_path':str(CITY_PATH), 'city_input_sha256':sha(city_raw),
    'case_evaluation_id':case['evaluation_id'],
    'city_input_id':city['input_id'], 'candidate_ids':case['reference_candidate_ids'],
    'demand_map_pphpd':case['policy']['line_peak_demand_pphpd'],
    'scenarios':['project-make-buy','china-bulk-buy'],
    'pricing_basis_description':{
        'project-make-buy':'Per-item modeled make/buy route at the committed city volume; owned local plant and common production setup charged once.',
        'china-bulk-buy':'Eligible manufactured stock purchased at repository China-origin benchmark/proxy rates, with modeled landing, receiving and local delivery allowances.'},
}
request['request_id']=identity(request)
(RUN/'request.json').write_bytes(encoded(request))
print(json.dumps({'summary_id':summary['summary_id'],'baseline_cost_evaluation_id':baseline['evaluation_id'],
    'china_cost_evaluation_id':china['evaluation_id'],'capital_base':summary['scenarios']['project-make-buy']['installed_capital_usd']['base'],
    'china_capital_base':summary['scenarios']['china-bulk-buy']['installed_capital_usd']['base'],
    'capital_delta_base':summary['capital_delta_usd_china_minus_project_make_buy']['base'],
    'npv_delta_base':summary['npv_delta_usd_china_minus_project_make_buy']['base'],
    'scope_delta_base':summary['base_scope_delta_usd_china_minus_project_make_buy']},sort_keys=True))
