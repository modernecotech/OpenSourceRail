import assert from 'node:assert/strict';
import test from 'node:test';
import {stateLabel,quantityText,scopeMatches}from '../../docs/design-engine/components.js';

test('missing price and incomplete evidence stay distinct from zero and success',()=>{
  assert.equal(quantityText(null,'USD'),'unknown');assert.equal(quantityText(0,'USD'),'0 USD');
  assert.equal(stateLabel('not-run'),'not run');assert.equal(stateLabel('failed'),'failed');assert.equal(stateLabel('stale'),'stale');
  assert.equal(stateLabel('completed'),'unknown');
});
test('part/result inspectors reject a different city environment or revision',()=>{
  const scope={city:'samawah',environment:'simulation',configuration_revision:'r1'};
  assert.equal(scopeMatches({identity:scope},scope),true);
  for(const patch of [{city:'mosul'},{environment:'physical'},{configuration_revision:'r2'}])assert.equal(scopeMatches({identity:{...scope,...patch}},scope),false);
});
