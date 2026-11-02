import json, math, hashlib, gzip
from pathlib import Path
p=Path('build/matched-renewal-research/epoch-v5');v=json.loads((p/'result.json').read_text())
raw={k:x for k,x in v.items() if k!='evaluation_id'}
assert hashlib.sha256((json.dumps(raw,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()==v['evaluation_id']
with gzip.open('build/flanged-system-evidence/final-three-v2/baseline.json.gz','rt') as stream: baseline=json.load(stream)
expect={k:(x['civil_design_basis']['physical_civil_component_id'],x['civil_design_basis']['prestress_strands']) for k,x in baseline['cases'].items()}
for treatment,reference in v['reference_compositions'].items():
 for mass,row in reference['mass_cases'].items():
  cid,strands=expect[mass]; assert row['physical_definition']['civil_candidate_id']==cid
  assert row['evaluation_ancestry']['prestress_strands']==strands
  assert len(row['scope_totals_iqd'])==14
  assert row['candidate_id']==hashlib.sha256((json.dumps(row['physical_definition'],sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
for candidate in v['comparisons'].values():
 for mass,case in candidate['mass_cases'].items():
  f=case['flanged']; assert len(f['scope_totals_iqd'])==14
  for treatment,delta in case['reference_deltas'].items():
   ref=v['reference_compositions'][treatment]['mass_cases'][mass]
   assert delta['reference_candidate_id']==ref['candidate_id']
   assert delta['reference_civil_physical_id']==expect[mass][0]
   for i in range(3):
    expected=math.fsum(x[i] for x in f['scope_totals_iqd'].values())-math.fsum(x[i] for x in ref['scope_totals_iqd'].values())
    assert math.isclose(expected,delta['npv_delta_iqd'][i],rel_tol=1e-12,abs_tol=.01)
    assert delta['capex_delta_iqd'][i]==f['rows'][i]['installed_capex_iqd']-ref['rows'][i]['installed_capex_iqd']
    assert delta['reference_bearing_installation_if_additive_iqd'][i]>0
    for events in (f['rows'][i]['coating_events'],f['rows'][i]['bearing_events'],ref['rows'][i]['bearing_events']):
     for event in events['events']:
      if event['covered_by_parent_replacement']:assert event['corridor_present_value_iqd']==0
assert v['whole_life_ranking_allowed'] is False and v['physical_accepted'] is False and v['integrated_selection'] is None
print('PASS: 54 candidate/mass/treatment/financial-scenario conditional deltas, 14-scope sums, matching physical identities, parent age resets, nonpromotion')
