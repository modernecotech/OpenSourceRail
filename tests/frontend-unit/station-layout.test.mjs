import test from 'node:test';
import assert from 'node:assert/strict';
import '../../crates/osr-city-studio/web/map-layout.js';

test('coincident interchange markers have distinct hit targets and preserve surveyed coordinates',()=>{
  const input=Array.from({length:12},(_,i)=>({id:'station-'+i,x:500,y:310}));
  const layout=globalThis.OSRStationMarkerLayout(input);
  assert.deepEqual(layout,globalThis.OSRStationMarkerLayout(input));
  assert.ok(layout.every(p=>p.sourceX===500&&p.sourceY===310));
  for(let i=0;i<layout.length;i++)for(let j=0;j<i;j++)assert.ok(Math.hypot(layout[i].x-layout[j].x,layout[i].y-layout[j].y)>=24-1e-8);
  assert.ok(input.every(p=>p.x===500&&p.y===310));
});

test('markers at the map edge remain clickable and well-separated',()=>{
  const layout=globalThis.OSRStationMarkerLayout([{id:'a',x:0,y:0},{id:'b',x:0,y:0},{id:'c',x:1000,y:620}]);
  assert.ok(layout.every(p=>p.x>=12&&p.x<=988&&p.y>=12&&p.y<=608));
  assert.equal(layout[0].sourceX,0);
});
