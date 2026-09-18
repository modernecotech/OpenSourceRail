import assert from 'node:assert/strict';
import test from 'node:test';
import {selectExecutionReviews} from '../../docs/lifecycle/execution-impact.js';

test('revision exposure isolates city, project, company, component and reviewed revisions', () => {
  const asset = {asset_id:'A',city:'samawah',erp_project:'P1',component_type_id:'charger',engineering_revision:'R2'};
  const review = {scope:{city:'samawah',project:'P1',company:'OSR'},mapping:{component_type_id:'charger',engineering_revision:'R1'}};
  const snapshot = {city:'samawah',project:'P1',company:'OSR',execution:{revision_reviews:[review,
    {...review,scope:{...review.scope,city:'mosul'}}, {...review,scope:{...review.scope,company:'OTHER'}},
    {...review,mapping:{...review.mapping,engineering_revision:'R0'}},
    {...review,mapping:{...review.mapping,component_type_id:'other'}}]}};
  assert.deepEqual(selectExecutionReviews(snapshot,asset),[]);
  const impact={baseline_engineering_revision:'R1',proposed_engineering_revision:'R2',equipment_changes:[{asset_id:'A'}]};
  assert.deepEqual(selectExecutionReviews(snapshot,asset,impact),[review]);
  assert.deepEqual(selectExecutionReviews({...snapshot,project:'P2'},asset,impact),[]);
  assert.deepEqual(selectExecutionReviews({...snapshot,city:'mosul'},asset,impact),[]);
});

test('factory methods select their declared product mappings without item-name guessing', () => {
  const asset={asset_id:'F',city:'samawah',erp_project:'P1',engineering_revision:'R1',manufacturing_method:{product_ids:['panel']}};
  const review={scope:{city:'samawah',project:'P1',company:'OSR'},mapping:{component_type_id:'panel',engineering_revision:'R1'}};
  const snapshot={city:'samawah',project:'P1',company:'OSR',execution:{revision_reviews:[review]}};
  assert.deepEqual(selectExecutionReviews(snapshot,asset),[review]);
  assert.deepEqual(selectExecutionReviews(snapshot,{...asset,manufacturing_method:undefined}),[]);
});
