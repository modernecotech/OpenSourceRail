import {expect,test} from '@playwright/test';
const base='http://127.0.0.1:4177';
const asset={asset_id:'SAM-ST-001:charger',name:'Charger',city:'samawah',environment:'simulation',engineering_revision:'rev1',lifecycle_state:'as-designed',erp_project:'P1',installations:[],evidence:[],readings:{},alarms:[],commands_audit:[],commands:{}};
test('city navigation filters ERP and targets the city FUXA display',async({page})=>{
  await page.route('**/api/workbench/city?**',r=>{
    const city=new URL(r.request().url()).searchParams.get('city');
    return r.fulfill({json:{city,erp:{project:city==='mosul'?'P2':'P1',routes:{tasks:'/app/task?project='+(city==='mosul'?'P2':'P1')}},supervision:{sites:[city==='mosul'?'MOS-PLANT-001':'SAM-PLANT-001',city==='mosul'?'MOS-ST-001':'SAM-ST-001'],preferred_site:city==='mosul'?'MOS-ST-001':'SAM-ST-001'}}});
  });
  await page.route('http://127.0.0.1:8080/**',r=>r.fulfill({body:'ERP'}));
  await page.route('http://127.0.0.1:1881/**',r=>r.fulfill({body:'FUXA'}));
  await page.goto(base+'/?module=tasks&city=samawah');
  await expect(page.locator('#moduleFrame')).toHaveAttribute('src','http://127.0.0.1:8080/app/task?project=P1');
  await page.locator('#citySelector').selectOption('mosul');
  await expect(page.locator('#moduleFrame')).toHaveAttribute('src','http://127.0.0.1:8080/app/task?project=P2');
  await page.locator('[data-module=fuxa]').click();
  await expect(page.locator('#moduleFrame')).toHaveAttribute('src',/viewName=mosul/);
  expect(new URL(await page.locator('#moduleFrame').getAttribute('src')).searchParams.get('viewName')).toBe('mosul · MOS-ST-001 · simulation');
});
test('evidence review retries its immutable ID and is discarded on asset change',async({page})=>{
  const calls=[];
  await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[asset,{...asset,asset_id:'SAM-ST-001:battery'}],outbox:[]}}));
  await page.route('**/api/lifecycle/evidence',r=>{
    calls.push(r.request().postDataJSON());
    return r.fulfill(calls.length===1?{status:503,json:{error:'Reply unavailable'}}:{json:{id:calls.at(-1).id,created:false}});
  });
  await page.goto(base+'/docs/lifecycle/?city=samawah&asset='+asset.asset_id);
  await page.locator('#evidenceEditor summary').click();
  await page.locator('#evidenceKind').selectOption('analysis');
  await page.locator('#evidenceReferences').fill('sha256:reviewed-model');
  await page.locator('#previewEvidence').click();
  await expect(page.locator('#evidencePayload')).toContainText('rev1');
  await page.locator('#evidenceToken').fill('engineer-fixture');
  await page.locator('#saveEvidence').click();
  await expect(page.locator('#evidenceStatus')).toContainText('Reply unavailable');
  await page.locator('#saveEvidence').click();
  await expect(page.locator('#evidenceStatus')).toContainText('already recorded');
  expect(calls[0]).toEqual(calls[1]);
  expect(calls[0]).toMatchObject({city:'samawah',asset_id:asset.asset_id,engineering_revision:'rev1',references:['sha256:reviewed-model']});
  await page.locator('#previewEvidence').click();
  await page.locator('#asset').selectOption('SAM-ST-001:battery');
  await expect(page.locator('#evidenceReview')).toBeHidden();
  await expect(page.locator('#evidenceReferences')).toHaveValue('');
});
test('serial tracing stays in the current scope and opens a matching asset',async({page})=>{
  let url;
  await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[asset],outbox:[]}}));
  await page.route('**/api/lifecycle/affected?**',r=>{url=r.request().url();return r.fulfill({json:[{scope:'samawah|simulation|SAM-ST-001:charger',serial:'S1',batch:'B1',removed:null,revision:'rev1'}]});});
  await page.goto(base+'/docs/lifecycle/?city=samawah');
  await page.locator('#serialTrace summary').click();
  await page.locator('#traceBatch').fill('B1');
  await page.locator('#traceForm button').click();
  await expect(page.locator('#traceResults')).toContainText('Currently installed');
  expect(new URL(url).searchParams.get('environment')).toBe('simulation');
  expect(new URL(url).searchParams.get('city')).toBe('samawah');
  await page.locator('#traceResults button').click();
  await expect(page.locator('#asset')).toHaveValue(asset.asset_id);
});
test('physical commissioning release cannot be submitted from the local evidence editor',async({page})=>{
  await page.route('**/api/lifecycle/snapshot?**',r=>r.fulfill({json:{assets:[{...asset,environment:'physical'}],outbox:[]}}));
  await page.goto(base+'/docs/lifecycle/?city=samawah&environment=physical');
  await page.locator('#evidenceEditor summary').click();
  await page.locator('#evidenceKind').selectOption('commissioning-release');
  await expect(page.locator('#previewEvidence')).toBeDisabled();
  await expect(page.locator('#evidenceReview')).toBeHidden();
});
test('failed city resolution clears the previous city native records',async({page})=>{
  await page.route('**/api/workbench/city?**',r=>new URL(r.request().url()).searchParams.get('city')==='mosul'
    ?r.fulfill({status:503,json:{error:'offline'}})
    :r.fulfill({json:{erp:{project:'P1',routes:{tasks:'/app/task?project=P1'}},supervision:{sites:[]}}}));
  await page.route('http://127.0.0.1:8080/**',r=>r.fulfill({body:'Samawah records'}));
  await page.goto(base+'/?module=tasks&city=samawah');
  await expect(page.frameLocator('#moduleFrame').locator('body')).toContainText('Samawah records');
  await page.locator('#citySelector').selectOption('mosul');
  await expect(page.locator('#moduleScope')).toContainText('status unavailable');
  await expect(page.locator('#moduleFrame')).toHaveAttribute('src','about:blank');
  await expect(page.locator('#openNative')).not.toHaveAttribute('href',/.+/);
});
