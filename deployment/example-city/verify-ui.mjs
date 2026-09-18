// Actual isolated services and records. No intercepted or mocked requests.
import {chromium,expect as baseExpect} from '@playwright/test';
const expect=baseExpect.configure({timeout:30000});
import fs from 'node:fs';
import {createHash} from 'node:crypto';
const output='build/city-example/';
const privateRoot='var/city-example/';
const setup=JSON.parse(fs.readFileSync(output+'setup.json'));
const records=JSON.parse(fs.readFileSync(output+'native-records.json'));
const env=Object.fromEntries(fs.readFileSync(privateRoot+'local.env','utf8').trim().split('\n').map(l=>[l.split('=')[0],l.slice(l.indexOf('=')+1)]));
const credentials=JSON.parse(fs.readFileSync(privateRoot+'integration.json'));
const fuxa=JSON.parse(fs.readFileSync(privateRoot+'fuxa.json'));
const browser=await chromium.launch();
const checks=[];
let page;
const passed=name=>{checks.push(name);console.log('PASS '+name);};
try {
 page=await browser.newPage({viewport:{width:1600,height:1100}});page.setDefaultTimeout(30000);
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8190/?module=erp&city=samawah');
 const frame=page.frameLocator('#moduleFrame');
 // A module switch replaces the iframe document while a poll may be reading it.
 // Retry that transient navigation; preserve all other evaluation errors.
 const frameState=async read=>{
   try{return await frame.locator('body').evaluate(read);}
   catch(error){if(/Execution context was destroyed|Frame was detached/.test(error.message))return null;throw error;}
 };
 const frontendState=()=>frameState(()=>window.__OSR_FRONTEND__);
 await frame.locator('#login_email').fill('Administrator');
 await frame.locator('#login_password').fill(env.ADMIN_PASSWORD);
 await frame.locator('.btn-login').click();
 await expect.poll(()=>frameState(()=>window.frappe?.session?.user),{timeout:60000}).toBe('Administrator');
 passed('Native ERP login inside isolated Workbench');
 await page.locator('[data-module=projects]').click();
 await expect(page.locator('#moduleFrame')).toHaveAttribute('src','http://127.0.0.1:8180/app/project/'+setup.projects.samawah);
 await frame.getByRole('button',{name:'OpenSourceRail',exact:true}).click();
 await frame.getByText('Connected lifecycle',{exact:true}).click();
 await expect(page.locator('#moduleFrame')).toHaveAttribute('src',/docs\/lifecycle/);
 passed('Configured ERP parent origin returns to the same Workbench');
 await frame.locator('#asset').selectOption('SAM-ST-001:charger');
 await expect(frame.locator('#overview')).toContainText(records.serials[1]);
 await expect(frame.locator('#executionImpact')).toContainText(records.work_order);
 await expect(frame.locator('#engineering')).toContainText('station-terminal.FCStd');
 await expect(frame.locator('#executionImpact')).toContainText(records.item);
 await expect(frame.locator('#links a[href*="/app/asset/"]')).toHaveAttribute('href','http://127.0.0.1:8180/app/asset/'+encodeURIComponent(records.asset));
 await frame.locator('#executionImpact details summary').first().click();
 const artifact=frame.locator('#engineering a').first();
 const response=await page.request.get(new URL(await artifact.getAttribute('href'),'http://127.0.0.1:8190').href);
 expect(response.ok()).toBeTruthy();expect((await response.body()).length).toBeGreaterThan(1000);
 await page.screenshot({path:output+'workbench-execution.png',fullPage:true});
 await frame.locator('body').evaluate(()=>window.scrollTo(0,0));
 await page.evaluate(()=>window.scrollTo(0,0));
 await page.screenshot({path:output+'workbench-lifecycle.png',fullPage:true});
 passed('Manufactured serial, native execution records and hashed CAD evidence share the asset context');
 await page.locator('[data-module=tasks]').click();
 await expect.poll(()=>frameState(()=>(window.cur_list?.filter_area?.get() || []).map(row=>row.slice(0,4)))).toContainEqual(['Task','project','=',setup.projects.samawah]);
 await page.screenshot({path:output+'workbench-erp.png',fullPage:true});
 passed('Native task filter follows the actual city project');
 await page.locator('#citySelector').selectOption('mosul');
 await expect(page.locator('#moduleFrame')).toHaveAttribute('src',new RegExp('task\\?project='+setup.projects.mosul));
 await page.locator('[data-module=fuxa]').click();
 const dialog=frame.locator('mat-dialog-container');await dialog.waitFor();
 await dialog.locator('form input[type=text]').fill('operator');
 await dialog.locator('input[type=password]').fill(fuxa.operator_password);
 await dialog.getByRole('button',{name:'OK',exact:true}).click();await dialog.waitFor({state:'hidden'});
 await expect(frame.locator('svg').filter({hasText:'MOS-ST-001'}).first()).toBeVisible();
 const mosulSnapshot=await page.request.get('http://127.0.0.1:8192/snapshot?city=mosul&environment=simulation',{headers:{Authorization:'Bearer '+credentials.principals.find(p=>p.role==='viewer').token}});
 expect(mosulSnapshot.ok()).toBeTruthy();
 const mosulCharger=(await mosulSnapshot.json()).assets.find(a=>a.asset_id==='MOS-ST-001:charger');
 const mosulPower=mosulCharger.readings.power_kw;
 const powerWidget='text_VAL_'+createHash('sha256').update(JSON.stringify([mosulCharger.fuxa_device_id,mosulCharger.fuxa_device_id+'__power_kw'])).digest('hex').slice(0,20);
 expect(mosulPower.quality).toBe('valid');
 await expect(frame.locator('#'+powerWidget)).toHaveText(String(mosulPower.value));
 await page.locator('#citySelector').selectOption('samawah');
 await expect(frame.locator('svg').filter({hasText:'SAM-ST-001'}).first()).toBeVisible();
 await expect(frame.locator('svg').filter({hasText:'SAM-ST-001'}).first()).toContainText('180');
 await page.screenshot({path:output+'workbench-fuxa.png',fullPage:true});
 passed('Native FUXA follows city selection and renders live controller power');
 const assetLink=frame.locator('svg a').filter({hasText:'Open asset, maintenance, engineering and history'}).first();
 await expect(assetLink).toHaveAttribute('href',/^http:\/\/127\.0\.0\.1:8190\/\?module=lifecycle&city=samawah&/);
 await assetLink.click();
 await expect(page).toHaveURL(/^http:\/\/127\.0\.0\.1:8190\/\?module=lifecycle&city=samawah&/);
 await expect(page.locator('#moduleFrame')).toHaveAttribute('src',/docs\/lifecycle/);
 passed('Native FUXA asset link returns to the same isolated Workbench');
 await frame.locator('#asset').selectOption('SAM-ST-001:facilities');
 await frame.locator('#operatorActions summary').click();
 await frame.locator('#operatorToken').fill(credentials.principals.find(p=>p.role==='operator').token);
 for (const level of [60,75]) {
   await frame.locator('#commandValue').fill(String(level));await frame.locator('#commandForm button').click();
   await expect(frame.locator('#actionStatus')).toContainText('requested');
   const request=(await frame.locator('#actionStatus').textContent()).match(/[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}/)[0];
   await expect(frame.locator('#commands .record').filter({hasText:request})).toContainText('completed');
   await expect(frame.locator('#measurements .metric').filter({hasText:'lighting_pct'}).locator('strong')).toHaveText(String(level)+' %');
 }
 await frame.locator('#forgetToken').click();
 passed('Workbench command reaches native controller and returns measured feedback');
 await page.locator('#mode').selectOption('design');
 await page.locator('#role').selectOption('designer');
 await page.locator('[data-module=studio]').click();
 await expect(frame.locator('#summary .summary-card').first()).toBeVisible({timeout:60000});
 await frame.locator('#network-map .station').first().click();
 const [materialized]=await Promise.all([
   page.waitForResponse(r=>new URL(r.url()).pathname.endsWith('/api/revisions') && r.request().method()==='POST'),
   frame.locator('#revision').click(),
 ]);
 expect(materialized.ok()).toBeTruthy();
 const {revision:approvedRevision}=await materialized.json();
 const revision=approvedRevision.revision_id;
 await expect(frame.locator('#revision')).toBeEnabled();
 await expect(page.locator('#contextRevision')).toHaveText(revision);
 await expect(frame.locator('#approval-revision')).toHaveValue(revision);
 await frame.locator('#approval-status').selectOption('approved');
 await frame.locator('#approval-reviewer').fill('Example simulation reviewer');
 await frame.locator('#approval-role').fill('Software acceptance');
 await frame.locator('#approval-date').fill('2026-09-18');
 await frame.locator('#approval-reference').fill('example-city:simulation-only');
 await frame.locator('#approval-comment').fill('Reproducible software scenario; no physical railway release.');
 const [approval]=await Promise.all([
   page.waitForResponse(r=>new URL(r.url()).pathname.endsWith('/api/approvals') && r.request().method()==='POST'),
   frame.locator('#approval-form button[type=submit]').click(),
 ]);
 expect(approval.ok()).toBeTruthy();
 expect(approval.request().postDataJSON().revision_id).toBe(revision);
 await expect(page.locator('#contextRevision')).toHaveText(revision);
 await expect(page.locator('#contextBaseline')).toHaveText(approvedRevision.content_sha256.slice(0,16));
 await frame.locator('#open-simulator').click();
 await expect.poll(frontendState,{timeout:120000}).toMatchObject({app:'simulator',ready:true,error:null,context:{revision,baseline_sha256:approvedRevision.content_sha256}});
 const simulated=await frame.locator('body').evaluate(()=>window.__OSR_FRONTEND__.details);
 for(const field of ['embeddedTicks','stationTicks','waysideTicks','backendSamples'])expect(simulated[field]).toBeGreaterThan(0);
 await expect(page.locator('#contextRun')).toHaveText(/^run-[a-f0-9]{16}$/);
 const run=await page.locator('#contextRun').textContent();
 await page.locator('#occHandoff').click();
 await expect.poll(frontendState,{timeout:120000}).toMatchObject({app:'occ',ready:true,error:null,context:{revision,baseline_sha256:approvedRevision.content_sha256,run_id:run}});
 await expect(page.locator('#contextRun')).toHaveText(run);
 passed('City Studio revision and simulation baseline reach native simulator and OCC replay');
 await page.locator('[data-module=operations]').click();
 await expect(frame.locator('#cityName')).toHaveText('Samawah');
 const workTitle='Example city railway inspection handoff '+run;
 await frame.locator('#coreTitle').fill(workTitle);
 await frame.locator('#coreDueDate').fill('2026-10-06');
 await frame.locator('button[form=workOrderForm]').click();
 await expect(frame.locator('#coreWorkTable')).toContainText(workTitle);
 const saved=await page.request.get('http://127.0.0.1:8190/api/ops-core/samawah');
 const task=(await saved.json()).state.workOrders.find(r=>r.title===workTitle);
 expect(task).toMatchObject({revision_id:revision,run_id:run,baseline_sha256:approvedRevision.content_sha256});
 await page.reload();await expect(frame.locator('#coreWorkTable')).toContainText(task.title);
 await page.screenshot({path:output+'workbench-osr-controls.png',fullPage:true});
 passed('OSR railway work persists with the same revision, baseline and simulation run');
 expect(errors).toEqual([]);passed('No browser runtime errors');
 fs.writeFileSync(output+'ui-report.json',JSON.stringify({passed:true,checks},null,2)+'\n');
}catch(error){
 fs.writeFileSync(output+'ui-report.json',JSON.stringify({passed:false,checks,error:String(error)},null,2)+'\n');
 if(page)await page.screenshot({path:output+'ui-failure.png',fullPage:true});
 throw error;
}finally{await browser.close();}
