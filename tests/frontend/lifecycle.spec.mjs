import {expect,test} from '@playwright/test';
const asset={asset_id:'SAM-ST-001:charger',name:'Test charger',city:'samawah',equipment_type:'charger',engineering_revision:'rev1',lifecycle_state:'as-designed',erp_project:'PROJ-0001',readings:{temperature_c:{value:82,unit:'degC',quality:'valid',source_time:1789500000}},alarms:[{rule:'cooling',active:1,incident:'i1',case_id:'ISS-1',erp_status:'Open',occurrences:1}],installations:[],evidence:[],commands_audit:[]};
test('Lifecycle preserves asset context and shows faults, quality and ERP case',async({page})=>{
 await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[asset],outbox:[{incident:'i1',state:'pending',attempts:2,error:'ERP unavailable'}]}}));
 await page.goto('http://127.0.0.1:4177/docs/lifecycle/?city=samawah&asset=SAM-ST-001:charger');
 await expect(page.locator('#measurements')).toContainText('82');
 await expect(page.locator('#alarms')).toContainText('Active');
 await expect(page.locator('#alarms a')).toHaveAttribute('href','http://127.0.0.1:8080/app/issue/ISS-1');
 await expect(page.locator('#queue')).toContainText('2 retries');
 await page.unroute('**/api/lifecycle/snapshot?**');
 await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({status:503,json:{error:'offline'}}));
 await page.locator('#refresh').click();
 await expect(page.locator('#measurements')).toContainText('disconnected');
 await expect(page.locator('#measurements')).not.toContainText('82');
});
test('Changing environment cannot leave simulated values labelled physical',async({page})=>{
 await page.route('**/api/lifecycle/snapshot?**',r=>r.request().url().includes('physical')?r.fulfill({status:503,json:{error:'unconfigured'}}):r.fulfill({json:{assets:[asset],outbox:[]}}));
 await page.goto('http://127.0.0.1:4177/docs/lifecycle/?city=samawah');
 await expect(page.locator('#measurements')).toContainText('82');
 await page.locator('#environment').selectOption('physical');
 await expect(page.locator('#mode')).toContainText('PHYSICAL');
 await expect(page.locator('#measurements')).toBeEmpty();
});
test('Engineering documents follow equipment identity within a city',async({page})=>{
 const vehicle={...asset,asset_id:'SAM-RS-L1-001:vehicle-cbm',parent_asset_id:'SAM-RS-L1-001',name:'Vehicle condition monitor'};
 let engineeringAsset='SAM-ST-001';
 await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[vehicle],outbox:[]}}));
 await page.route('**/api/lifecycle/engineering?**',r=>r.fulfill({json:{asset_id:engineeringAsset,artifacts:[{tool:'Bonsai',tool_version:'test',path:'model.ifc',sha256:'a'.repeat(64)}]}}));
 await page.goto('http://127.0.0.1:4177/docs/lifecycle/?city=samawah');
 await expect(page.locator('#engineering')).toContainText('No reviewed engineering package linked');
 await expect(page.locator('#engineering a')).toHaveCount(0);
 engineeringAsset='SAM-RS-L1-001';
 await page.locator('#refresh').click();
 await expect(page.locator('#engineering a')).toHaveText('model.ifc');
});
test('Prepared change review explains embedded, lifecycle and ERP impact without implying approval',async({page})=>{
 let mappingPresent=true;
 const reviewed={...asset,parent_asset_id:'SAM-ST-001',source_asset_ids:['SAM-ST-001'],erp_item_code:'STN-CHG-P010',source_crates:['osr-energy-site']};
 await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[reviewed],outbox:[]}}));
 await page.route('**/api/lifecycle/change-impact?**',r=>r.fulfill({json:{status:'review-required',baseline_sha256:'a'.repeat(64),proposed_sha256:'b'.repeat(64),authority:'Preview only: accepted baseline unchanged.',summary:{added:0,changed:1,removed:0,unchanged:3},application:{blockers:[]},equipment_changes:[{asset_id:reviewed.asset_id,name:reviewed.name,change_type:'changed',categories:['design-definition','telemetry-contract'],changed_values:[{path:'measurements.temperature_c.max',kind:'changed'}],dependencies:{component_type_ids:['station-charger'],source_crates:['osr-energy-site'],erp_projects:['PROJ-0001'],erp_item_codes:mappingPresent?['STN-CHG-P010']:[]},affected_records:{installations:[{}],evidence:[{},{}],open_alarms_or_cases:[{}],pending_commands:[]},required_reviews:['Review units and ranges.']}]}}));
 await page.route('**/api/operating/twins',r=>r.fulfill({json:{snapshots:[{project:'PROJ-0001',execution:{purchase_orders:[{item:'STN-CHG-P010'}],receipts:[],production:[{item:'STN-CHG-P010'}]}}]}}));
 await page.goto('http://127.0.0.1:4177/docs/lifecycle/?city=samawah');
 await expect(page.locator('#changeImpact')).toContainText('review-required');
 await expect(page.locator('#changeImpact')).toContainText('measurements.temperature_c.max');
 await expect(page.locator('#changeImpact')).toContainText('1 installation(s), 2 evidence record(s)');
 await expect(page.locator('#changeImpact')).toContainText('1 purchase-order line(s)');
 await expect(page.locator('#changeImpact')).toContainText('accepted baseline unchanged');
 mappingPresent=false;
 await page.locator('#refresh').click();
 await expect(page.locator('#changeImpact')).toContainText('0 purchase-order line(s)');
});
test('Alarm acknowledgement submits the displayed occurrence',async({page})=>{
  let request;
  const occurrenceAsset={...asset,alarms:[{...asset.alarms[0],occurrences:3}]};
  await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[occurrenceAsset],outbox:[]}}));
  await page.route('**/api/lifecycle/alarms/acknowledge',async r=>{request=r.request();await r.fulfill({json:{acknowledged:true,created:true,occurrence:3}});});
  await page.goto('http://127.0.0.1:4177/docs/lifecycle/?city=samawah');
  await page.locator('#operatorActions summary').click();
  await page.locator('#operatorToken').fill('scoped-token');
  await page.getByRole('button',{name:'Acknowledge occurrence 3'}).click();
  expect(request.headers().authorization).toBe('Bearer scoped-token');
  expect(request.postDataJSON()).toMatchObject({asset_id:'SAM-ST-001:charger',rule:'cooling',occurrence:3});
  await expect(page.locator('#actionStatus')).toContainText('occurrence 3 acknowledged');
});
test('Factory view uses reviewed ERP mappings and keeps quality release independent',async({page})=>{
 const factory={...asset,asset_id:'SAM-PLANT-001:factory-lm3-mfg-020',parent_asset_id:'SAM-PLANT-001',name:'Composite method',equipment_type:'factory-lm3-mfg-020',
  readings:{cycle_progress_pct:{value:42,unit:'%',quality:'valid',source_time:1789500000},quality_hold:{value:1,unit:'bool',quality:'valid',source_time:1789500000}},
  alarms:[],manufacturing_method:{method_id:'LM3-MFG-020',document_revision:'A-DRAFT',document_status:'design-reference-not-released',work_center:'composite cell',crew_size:3,planning_cycle_minutes:1440,product_ids:['LM3-BDY-P130'],tooling_ids:['LM3-TOOL-SIDE-MOULD'],steps:[{name:'Cure',hold_point:true}],release_gate:'Complete the cure record.',release_boundary:'Not a construction release.'}};
 await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[factory],outbox:[]}}));
 await page.route('**/api/operating/twins',r=>r.fulfill({json:{snapshots:[{project:'PROJ-0001',execution:{by_currency:{},receipts:[],execution_mappings:[{component_type_id:'LM3-BDY-P130',engineering_revision:'rev1',erp_item_code:'PANEL',production_bom:'BOM-PANEL'}],production:[{name:'WO-1',item:'PANEL',bom:'BOM-PANEL',status:'Completed',planned_qty:1,produced_qty:1,uom:'Nos'},{name:'WO-OTHER',item:'OTHER'}, {name:'WO-OLD-BOM',item:'PANEL',bom:'BOM-PANEL-REV0'}, {name:'WO-WRONG-ITEM',item:'OTHER',bom:'BOM-PANEL'}, {name:'WO-NO-BOM',item:'PANEL'}]}}]}}));
 await page.goto('http://127.0.0.1:4177/docs/lifecycle/?city=samawah');
 await expect(page.locator('#overview')).toContainText('LM3-MFG-020');
 await expect(page.locator('#overview')).toContainText('1 steps / 1 hold points');
 await expect(page.locator('#execution')).toContainText('1 reviewed product/method-to-ERP mapping(s) · 1 matching native Work Order(s)');
 await expect(page.locator('#execution')).toContainText('Engineering-accepted quantity: not asserted');
 for(const excluded of ['WO-OTHER','WO-OLD-BOM','WO-WRONG-ITEM','WO-NO-BOM']) await expect(page.locator('#execution')).not.toContainText(excluded);
});

test('Revision exposure shows scoped business records and downloads the observed review',async({page})=>{
 const mapped={...asset,component_type_id:'charger'};
 const review={schema:'osr-execution-revision-review/1',scope:{city:'samawah',project:'PROJ-0001',company:'OSR'},
  mapping:{name:'MAP-1',component_type_id:'charger',engineering_revision:'rev1',erp_item_code:'CHARGER',production_bom:'BOM-CHARGER'},sha256:'c'.repeat(64),
  purchase_orders:[{document:'PO-1',line:'PO-LINE-1',item:'RAW',status:'Draft',unreceived_qty:4,uom:'Nos',actionable:true}],
  work_orders:[{name:'WO-PARTIAL',item:'CHARGER',bom:'BOM-CHARGER',status:'In Process',produced_qty:1,planned_qty:2,uom:'Nos',actionable:true}],
  stock_movements:[{name:'SE-1',work_order:'WO-PARTIAL',purpose:'Manufacture',lines:[{item:'RAW',qty:2,uom:'Nos',source_warehouse:'Stores'}]}],
  warnings:['BOM unavailable to this reader: BOM-SUB'],limitations:['No record is changed, held, cancelled, accepted or released by this review.'],automatic_disposition:false};
 await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[mapped],outbox:[]}}));
 const disposition={name:'DISP-1',mapping:'MAP-1',city:'samawah',project:'PROJ-0001',company:'OSR',responsible:'planner@example.invalid',due_date:'2026-10-01',current:false,proposal:{action:'Request production stop',target:{document:'WO-PARTIAL'}},decision:{outcome:'Endorse plan'}};
 await page.route('**/api/operating/twins',r=>r.fulfill({json:{snapshots:[{city:'samawah',project:'PROJ-0001',company:'OSR',observed_at:'2026-09-18T09:00:00Z',execution:{by_currency:{},receipts:[],dispositions:[disposition,{...disposition,name:'DISP-OTHER-CITY',city:'mosul'}],revision_reviews:[review,{...review,scope:{...review.scope,city:'mosul'},mapping:{...review.mapping,erp_item_code:'OTHER-CITY'}}]}}]}}));
 await page.goto('http://127.0.0.1:4177/docs/lifecycle/?city=samawah');
 const view=page.locator('#executionImpact');
 await expect(view).toContainText('2026-09-18T09:00:00Z');
 await expect(view.locator('summary')).toHaveCount(1);
 await view.locator('summary').click();
 await page.waitForTimeout(5500); // A periodic snapshot refresh must keep an unchanged review open.
 await expect(view.locator('details')).toHaveJSProperty('open',true);
 await expect(view).toContainText('revision allocation unproven');
 await expect(view).toContainText('review unfinished production');
 await expect(view).toContainText('BOM unavailable to this reader');
 await expect(view.getByRole('link',{name:'WO-PARTIAL',exact:true})).toHaveAttribute('href','http://127.0.0.1:8080/app/work-order/WO-PARTIAL');
 await expect(view).not.toContainText('OTHER-CITY');
 await expect(view).toContainText('Endorse plan · Exposure changed or unavailable · execution unverified');
 await expect(view.getByRole('link',{name:'DISP-1',exact:true})).toHaveAttribute('href','http://127.0.0.1:8080/app/osr-revision-disposition/DISP-1');
 const downloaded=page.waitForEvent('download');
 await view.getByRole('button',{name:'Download revision exposure'}).click();
 const download=await downloaded;
 const fs=await import('node:fs/promises');
 const payload=JSON.parse(await fs.readFile(await download.path(),'utf8'));
 expect(payload.reviews).toHaveLength(1);
 expect(payload.reviews[0].sha256).toBe(review.sha256);
 expect(payload.reviews[0].automatic_disposition).toBe(false);
 disposition.verification={name:'VERIFICATION-1',status:'Native outcome verified',current:true,verifier:'checker@example.invalid',observed_at:'2026-09-18T10:00:00Z'};
 await page.locator('#refresh').click();
 await expect(view).toContainText('Exposure changed or unavailable · Native outcome verified');
 await expect(view).toContainText('checker@example.invalid');
 await expect(view).toContainText('railway release separate');
 await expect(view.getByRole('link',{name:'VERIFICATION-1',exact:true})).toHaveAttribute('href','http://127.0.0.1:8080/app/osr-disposition-execution/VERIFICATION-1');
 disposition.verification.status='Verification stale';disposition.verification.current=false;
 await page.locator('#refresh').click();
 await expect(view).toContainText('Verification stale');
 await expect(view).not.toContainText('Native outcome verified');
 await expect(view.getByRole('link',{name:'VERIFICATION-1',exact:true})).toBeVisible();
});

test('Cross-domain review keeps stale observations and engineering release visible',async({page})=>{
 await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[asset],outbox:[]}}));
 await page.route('**/api/lifecycle/change-impact?**',r=>r.fulfill({json:{status:'no-change',summary:{},equipment_changes:[],cross_domain:{observations_current:false,engineering_release_ready:false,sha256:'context-hash',blockers:['ERP scope P1: refresh its snapshot before cross-domain review'],remaining:['Independently accept engineering rework'],scope:'Point-in-time observations.'}}}));
 await page.goto('http://127.0.0.1:4177/docs/lifecycle/?city=samawah');
 await expect(page.locator('#changeImpact')).toContainText('Cross-domain engineering release: open');
 await expect(page.locator('#changeImpact')).toContainText('refresh its snapshot');
 await expect(page.locator('#changeImpact')).toContainText('Independently accept engineering rework');
 await expect(page.locator('#changeImpact')).toContainText('context-hash');
});

test('Lifecycle paginates equipment evidence and scoped delivery state',async({page})=>{
  const evidence=(id,cursor)=>({id,cursor,kind:'inspection',actor:'inspector',created:1789500000,body:'{}'});
  const current={...asset,environment:'simulation',evidence:[evidence('new-evidence',2)],evidence_page:{total:2,next_before:2}};
  await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[current],outbox:[],outbox_page:{total:500,pending:150,next_before:1}}}));
  await page.route('**/api/lifecycle/evidence?**',r=>{
    const q=new URL(r.request().url()).searchParams;
    expect(q.get('asset_id')).toBe(current.asset_id);expect(q.get('before')).toBe('2');
    return r.fulfill({json:{items:[evidence('older-evidence',1)],total:2,next_before:null}});
  });
  await page.route('**/api/lifecycle/outbox?**',r=>{
    const q=new URL(r.request().url()).searchParams;expect(q.get('asset_id')).toBe(current.asset_id);
    return r.fulfill({json:q.get('state')==='pending'?{items:[{state:'pending',attempts:7}],pending:1,total:1,next_before:null}:
      q.get('before')?{items:[{state:'pending',attempts:7}],pending:1,total:2,next_before:null}:
      {items:[{state:'delivered',attempts:0}],pending:1,total:2,next_before:2}});
  });
  await page.goto('http://127.0.0.1:4177/docs/lifecycle/?city=samawah');
  await expect(page.locator('#queue')).toContainText('1 pending · 2 total deliveries');
  await page.getByRole('button',{name:'Load older evidence'}).click();
  await expect(page.locator('#assurance')).toContainText('older-evidence');
  await expect(page.getByRole('button',{name:'Load older evidence'})).toBeHidden();
  await page.getByRole('button',{name:'Load older deliveries'}).click();
  await expect(page.locator('#queue')).toContainText('7 retries');
  await page.getByRole('button',{name:'Pending only'}).click();
  await expect(page.locator('#queue')).toContainText('1 pending · 1 pending deliveries');
  await expect(page.locator('#queue')).not.toContainText('delivered');
});
