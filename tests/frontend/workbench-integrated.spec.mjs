import { expect, test } from '@playwright/test';
const base='http://127.0.0.1:4177';
test('city switch clears railway authority and uses the selected city bundle',async({page})=>{
  await page.goto(base+'/?module=operations&city=samawah&mode=training&role=reviewer&selected_asset=SAM-ST-001&baseline_sha256='+'a'.repeat(64)+'&revision=osr-1234567890abcdef&run_id=run-1234567890abcdef');
  await page.locator('#citySelector').selectOption('mosul');
  await expect(page.locator('#contextCity')).toHaveText('mosul');
  await expect(page.locator('#contextAsset')).toHaveText('none');
  await expect(page.locator('#contextBaseline')).toHaveText('not approved');
  await expect(page.locator('#contextRun')).toHaveText('not run');
  await expect(page.locator('#moduleFrame')).toHaveAttribute('src',/mosul-operations/);
  await expect(page.locator('[data-module=occ]')).toBeDisabled();
  await expect(page.locator('[data-module=studio]')).toBeDisabled();
  await page.locator('[data-module=lifecycle]').click();
  await expect(page.locator('#moduleFrame')).toHaveAttribute('src',/city=mosul/);
});
test('business and supervision navigation stays inside the shell and rejects forged messages',async({page})=>{
  await page.route('**/api/workbench/city?**',r=>r.fulfill({json:{
    city:'mosul',environment:'simulation',
    erp:{state:'unavailable',project:null,stale:true,routes:{projects:'/app/project?custom_osr_city=mosul'}},
    supervision:{state:'prepared',sites:['MOS-ST-001'],preferred_site:'MOS-ST-001',equipment_count:4},
  }}));
  await page.route('http://127.0.0.1:8080/**',r=>r.fulfill({contentType:'text/html',body:'<h1>Native ERP authentication</h1>'}));
  await page.route('http://127.0.0.1:1881/**',r=>r.fulfill({contentType:'text/html',body:'<h1>Native supervision</h1>'}));
  await page.goto(base+'/?module=operating&city=mosul');
  const frame=page.frameLocator('#moduleFrame');
  await frame.locator('#workspace').click();
  await expect(page.locator('#moduleFrame')).toHaveAttribute('src','http://127.0.0.1:8080/app/opensourcerail');
  await expect(frame.locator('h1')).toHaveText('Native ERP authentication');
  await page.locator('[data-module=fuxa]').click();
  await expect(frame.locator('h1')).toHaveText('Native supervision');
  await page.evaluate(()=>window.postMessage({type:'osr:navigate',module:'occ',context:{city:'samawah',mode:'live',baseline_sha256:'a'.repeat(64)}},location.origin));
  await expect(page.locator('#contextCity')).toHaveText('mosul');
  await expect(page.locator('#mode')).toHaveValue('design');
});
test('an unconfigured city refuses FUXA navigation without retaining another city display',async({page})=>{
  let fuxaRequests=0;
  await page.route('**/api/workbench/city?**',r=>r.fulfill({json:{
    city:'basra',environment:'simulation',
    erp:{state:'unavailable',project:null,stale:true,routes:{projects:'/app/project?custom_osr_city=basra'}},
    supervision:{state:'unavailable',sites:[],equipment_count:0},
  }}));
  await page.route('http://127.0.0.1:1881/**',r=>{fuxaRequests++;return r.fulfill({body:'unexpected FUXA navigation'});});
  await page.goto(base+'/?module=operating&city=basra');
  const moduleFrame=page.locator('#moduleFrame');
  await expect(moduleFrame).toHaveAttribute('src',/\/docs\/operating\/.*city=basra/);
  const previous=await moduleFrame.getAttribute('src');
  await page.locator('[data-module=fuxa]').click();
  await expect(page.locator('#moduleScope')).toHaveText('No supervision package for basra / simulation.');
  await expect(moduleFrame).toHaveAttribute('src',previous);
  expect(fuxaRequests).toBe(0);
});
test('lifecycle action requires explicit credential and keeps the credential out of shell URLs',async({page})=>{
  let forwarded;
  await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[{
    asset_id:'SAM-ST-001:facilities',name:'Station facilities',city:'samawah',environment:'simulation',engineering_revision:'fixture',lifecycle_state:'as-designed',
    erp_project:'PROJ-0001',installations:[],readings:{},alarms:[],evidence:[],commands_audit:[],
    commands:{set_lighting:{parameter:'level',min:0,max:100,max_ttl_seconds:30,required_conditions:['local_remote_enabled']}},
  }],outbox:[]}}));
  await page.route('**/api/lifecycle/commands',async r=>{forwarded=r.request();await r.fulfill({json:{state:'requested'}});});
  await page.goto(base+'/?module=lifecycle&city=samawah&selected_asset=SAM-ST-001%3Afacilities');
  const frame=page.frameLocator('#moduleFrame');
  await frame.locator('#operatorActions summary').click();
  await expect(frame.locator('#commandForm')).toBeVisible();
  await frame.locator('#commandValue').fill('55');
  await frame.locator('#commandForm button').click();
  await expect(frame.locator('#actionStatus')).toContainText('Enter your scoped');
  expect(forwarded).toBeUndefined();
  await frame.locator('#operatorToken').fill('test-scoped-token');
  await frame.locator('#commandForm button').click();
  await expect(frame.locator('#actionStatus')).toContainText('requested');
  expect(forwarded.headers().authorization).toBe('Bearer test-scoped-token');
  expect(forwarded.postDataJSON()).toMatchObject({city:'samawah',environment:'simulation',asset_id:'SAM-ST-001:facilities',parameters:{level:55}});
  expect(page.url()).not.toContain('test-scoped-token');
  await frame.locator('#forgetToken').click();
  await expect(frame.locator('#operatorToken')).toHaveValue('');
});
