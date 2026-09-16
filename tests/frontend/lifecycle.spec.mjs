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
