import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const root=new URL('../../../',import.meta.url);
const context={window:{}};vm.createContext(context);
vm.runInContext(await readFile(new URL('engineering/development_baseline/web/city-journeys.js',root),'utf8'),context);
const api=context.window.OSRCityJourneys;
const stop=(id,lat=31,lon=45)=>({id,lat,lon,dwell_s:30,source_stop_ids:[id]});
const line=(id,ids)=>({line_id:id,metrics:{headway_s:120},requirements:{headway_s:120},
  original_stops:ids.map(x=>stop(x)),operational_stops:ids.map(x=>stop(x)),station_complexes:[],
  legs:ids.slice(1).map((to,i)=>({from_stop:ids[i],to_stop:to,scheduled_runtime_s:100}))});
let p={schema:'osr-city-atlas/1',lines:[line('L1',['A','B','C'])],interchanges:[]};
let r=api.route(p,'L1::A','L1::C');
assert.equal(r.status,'reachable');assert.equal(r.duration_s,290);assert.equal(r.totals.dwell_s,30);assert.equal(r.totals.wait_s,60);
assert.equal(api.route(p,'L1::C','L1::A').duration_s,290);
p.lines.push(line('L2',['D','E']));
assert.equal(api.route(p,'L1::A','L2::E').status,'unreachable','Nearby coordinates alone cannot invent an interchange');
p.interchanges=[{id:'I1',lines:['L1','L2'],platforms:['B','D']}];
r=api.route(p,'L1::A','L2::E');
assert.equal(r.status,'reachable');assert.equal(r.boardings,2);assert.equal(r.duration_s,440);
assert.equal(r.physical_accepted,false);
console.log('Journey checks passed: actual timed legs, intermediate dwell, reverse hypothesis, explicit transfers, one wait per boarding, disconnected network');
