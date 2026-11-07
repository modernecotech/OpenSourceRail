"""Catalogue-to-mass closure checks: no solver or installed-completeness claim."""
from copy import deepcopy
from itertools import product
from pathlib import Path
import gzip,json,math
import pytest
from engineering.station_pair import mass

@pytest.fixture(scope='module')
def bundle():return json.loads(gzip.decompress((mass.ROOT/mass.INPUT).read_bytes()))
@pytest.fixture(scope='module')
def result(bundle):return mass.reconcile(bundle,unknown_mass_kg_per_train=dict(low=2000,base=5000,high=10000))

def test_identity_and_seal(result):
 assert result['candidate_id']==mass.CANDIDATE_ID and result['source_bundle_id']==mass.BUNDLE_ID
 assert result['evaluation_id']==mass._identity({k:v for k,v in result.items() if k!='evaluation_id'})
 assert result['group_count']<=5000
 assert result['formation']['body_and_gap_length_m']==105.25
 assert result['formation']['wheelset_centres_car_x_m']==pytest.approx([-7.45,-5.35,5.35,7.45])

@pytest.mark.parametrize('key',['candidate_id','bundle_id','evaluation_id'])
def test_mixed_identity_rejected(bundle,key):
 b=deepcopy(bundle);b[key]='0'*64
 with pytest.raises(ValueError,match='Exact candidate'):mass.reconcile(b,unknown_mass_kg_per_train=dict(low=2,base=5,high=10))

def test_payload_and_flags_cannot_be_forged(bundle):
 b=deepcopy(bundle);b['parts'][0]['quantity_per_train']+=1
 with pytest.raises(ValueError,match='authenticated'):mass.reconcile(b,unknown_mass_kg_per_train=dict(low=2,base=5,high=10))
 for flag in mass.FLAGS:
  b=deepcopy(bundle);b[flag]=0
  with pytest.raises(ValueError,match='claim'):mass.reconcile(b,unknown_mass_kg_per_train=dict(low=2,base=5,high=10))

@pytest.mark.parametrize('reserve',[None,{},dict(low=None,base=None,high=None),dict(low=True,base=5,high=10),dict(low=2,base=1,high=10),dict(low=-1,base=5,high=10),dict(low=2,base=float('nan'),high=10)])
def test_reserve_required_and_finite(bundle,reserve):
 with pytest.raises(ValueError):mass.reconcile(bundle,unknown_mass_kg_per_train=reserve)

def test_counts_and_allocation_close(bundle,result):
 assert result['counted_leaf_multiplicity']==bundle['counted']['leaf_pieces_per_train']
 by={}
 for row in result['grouped_occurrences']:
  by[row['source_part_id']]=by.get(row['source_part_id'],0)+row['leaf_multiplicity']
  assert sum(x['fraction'] for x in row['car_shares'])==1
 for p in bundle['parts']:assert by[p['id']]==p['quantity_per_train']
 for k,case in enumerate(result['mass_scenarios']):
  name=case['case'];expected=bundle['nominal_mass_kg']['known_leaf_subtotal'][name]+result['reserve']['mass_kg_per_train'][name]
  assert case['conditional_accounted_train_mass_kg']==pytest.approx(expected)
  assert sum(case['per_car_mass_kg'])==pytest.approx(expected)
  assert case['mass_allocation_residual_kg']==pytest.approx(0,abs=1e-7)
  for car in result['cars']:
   c=car['mass_scenarios'][k]
   for e in c['support_endpoints']:
    assert e['left_support_force_N']+e['right_support_force_N']==pytest.approx(c['mass_kg']*9.80665)
    assert abs(e['force_residual_N'])<1e-7 and abs(e['moment_residual_Nm'])<1e-6


def test_shared_mass_is_counted_once_and_cost_unchanged(bundle,result):
 for c in mass.CASES:
  raw=sum(g['mass_kg'][c] for g in result['grouped_occurrences'] if g['owner']=='shared-intercar')
  assert result['shared_intercar_mass_kg'][c]==pytest.approx(raw)
  allocated=sum(r['mass_kg'][c] for car in result['cars'] for r in car['allocation_rows'] if 'connection-' in r['group_id'])
  assert allocated==pytest.approx(raw)
 assert result['procurement']['direct_parts_process_usd']==bundle['direct_parts_process_usd']
 assert not any(g['replaces_parent_account_ids'] for g in result['grouped_occurrences'])
 assert all(g['gross_stock_trim_deduction_kg']==0 for g in result['grouped_occurrences'])


def test_unknowns_do_not_become_installed_or_zero(result):
 assert result['actual_installed_positions_known'] is False
 assert result['reserve']['covers_all_unknowns'] is False
 assert result['rotating_scenario_required'] is True
 for key in ['rotating_inertia_kg_m2','rotating_equivalent_mass_kg','rotational_energy_J','installed_CG_m','installed_inertia_kg_m2','individual_axle_loads_N']:
  assert result[key] is None
 for row in result['grouped_occurrences']:assert row['actual_installed_transform'] is None
 for key in mass.FLAGS:assert result[key] is False


def test_explicit_zero_reserve_still_leaves_unknowns_open(bundle):
 r=mass.reconcile(bundle,unknown_mass_kg_per_train=dict(low=0,base=0,high=0))
 assert r['reserve']['covers_all_unknowns'] is False and r['installed_mass_complete'] is False


def test_nonlinear_CG_and_reaction_outer_bounds_contain_corner_cases():
 rows=[dict(mass_kg=dict(low=1,base=2,high=9),centroid_box_m=[[-8,-4],[-1,1],[0,2]]),dict(mass_kg=dict(low=2,base=3,high=12),centroid_box_m=[[3,7],[-.5,.5],[1,4]])]
 b=mass._outer_bounds(rows,[-6.4,6.4],9.80665)
 for m0,m1,x0,x1 in product([1,9],[2,12],[-8,-4],[3,7]):
  cg=(m0*x0+m1*x1)/(m0+m1);rr=9.80665*(m0*(x0+6.4)+m1*(x1+6.4))/12.8;ll=9.80665*(m0+m1)-rr
  assert b['CG_outer_box_m'][0][0]<=cg<=b['CG_outer_box_m'][0][1]
  assert b['left_support_force_outer_N'][0]-1e-8<=ll<=b['left_support_force_outer_N'][1]+1e-8
  assert b['right_support_force_outer_N'][0]-1e-8<=rr<=b['right_support_force_outer_N'][1]+1e-8


def test_reserve_scenarios_have_independent_evaluation_identity(bundle,result):
 r=mass.reconcile(bundle,unknown_mass_kg_per_train=dict(low=1000,base=3000,high=8000))
 assert r['candidate_id']==result['candidate_id'] and r['source_bundle_id']==result['source_bundle_id']
 assert r['evaluation_id']!=result['evaluation_id']
