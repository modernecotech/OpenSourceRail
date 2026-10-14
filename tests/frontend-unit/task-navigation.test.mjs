import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { AREAS, areaFor, validateNavigation } from '../../docs/workbench/task-navigation.js';

test('all 25 existing native and OSR routes remain under six task areas',async()=>{
  const registry=JSON.parse(await readFile(new URL('../../docs/workbench/modules.json',import.meta.url)));
  validateNavigation(registry);
  const previous=['overview','verification','engineering-change','decision-readiness','design-options','studio','simulator',
    'service-planning','occ','operations','lifecycle','operating','erp','projects','tasks','procurement','receipts',
    'manufacturing','quality','stock','maintenance','issues','finance','people','fuxa'];
  for(const id of previous){
    assert.equal(registry.modules.filter(m=>m.id===id).length,1);
    assert.ok(AREAS.includes(areaFor(registry.modules,id)));
  }
  assert.equal(registry.modules.find(m=>m.id==='erp').path,'/app/opensourcerail');
  assert.equal(registry.modules.find(m=>m.id==='fuxa').path,'/home/');
  assert.equal(areaFor(registry.modules,'auto-design'),'Design');
});

test('duplicate or unowned routes cannot silently replace a capability',()=>{
  assert.throws(()=>validateNavigation({task_areas:AREAS,modules:[{id:'a',group:'Unknown',path:'/',service:'local'}]}));
  const row={id:'a',group:'Plan',path:'/',service:'local'};
  assert.throws(()=>validateNavigation({task_areas:AREAS,modules:[row,row]}));
});
