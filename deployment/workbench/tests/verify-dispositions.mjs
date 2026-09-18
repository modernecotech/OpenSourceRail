// Real ERP Desk widgets inside Workbench; mocked business replies prevent persistent test plans.
// Actual transaction, permission, stale-review and idempotency checks live in verify-lifecycle.py.
import {chromium,expect} from '@playwright/test';
import fs from 'node:fs';
const browser=await chromium.launch();
let page;
try {
 page=await browser.newPage();page.setDefaultTimeout(30000);
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const env=Object.fromEntries(fs.readFileSync('var/erpnext/local.env','utf8').trim().split('\n').map(l=>[l.split('=')[0],l.slice(l.indexOf('=')+1)]));
 await page.goto('http://127.0.0.1:8090/?module=erp&city=samawah');
 const frame=page.frameLocator('#moduleFrame');
 await frame.locator('#login_email').fill('Administrator');
 await frame.locator('#login_password').fill(env.ADMIN_PASSWORD);
 await frame.locator('.btn-login').click();
 await expect.poll(()=>frame.locator('body').evaluate(()=>window.frappe?.session?.user),{timeout:60000}).toBe('Administrator');
 await page.locator('[data-module=projects]').click();
 await expect(page.locator('#moduleFrame')).toHaveAttribute('src','http://127.0.0.1:8080/app/project/PROJ-0001');
 const target={kind:'work-order',document:'UI-FIXTURE-WO'};
 let proposed,recorded=false,decided=false,decision;const calls=[];
 await page.route('**/api/method/osr_erpnext.disposition.*',async route=>{
   const name=new URL(route.request().url()).pathname.split('.').at(-1);
   const args=new URLSearchParams(route.request().postData() || '');calls.push(name);
   let message;
   if(name==='catalogue') message={can_propose:true,can_review:true,actions:{'work-order':['Request production stop']},
     reviews:[{mapping:{name:'UI-MAP',component_type_id:'fixture',engineering_revision:'R1'},targets:[{target,record:{name:target.document}}]}],
     dispositions:recorded?[{name:'UI-DISPOSITION',proposal:proposed,responsible:proposed.responsible,due_date:proposed.due_date,current:true,decision:decided?{outcome:decision.outcome}:null}]:[]};
   else if(name==='preview') {
     proposed=JSON.parse(args.get('proposal'));
     expect(proposed).toMatchObject({mapping:'UI-MAP',target,action:'Request production stop',responsible:'Administrator',references:['fixture:drawing-R2']});
     expect(proposed.key).toMatch(/^[a-f0-9-]{36}$/);
     message={proposal:proposed,exposure_sha256:'a'.repeat(64),warnings:[],target_record:{name:target.document,qty:2},fingerprint:'proposal-preview'};
   } else if(name==='record') {
     expect(JSON.parse(args.get('proposal'))).toEqual(proposed);expect(args.get('fingerprint')).toBe('proposal-preview');
     recorded=true;message={name:'UI-DISPOSITION',created:true};
   } else if(name==='preview_decision') {
     decision=JSON.parse(args.get('decision'));expect(args.get('disposition')).toBe('UI-DISPOSITION');
     expect(decision).toEqual({outcome:'Endorse plan',rationale:'UI fixture independent review',references:['fixture:review-1']});
     message={decision,reviewer:'fixture-reviewer',current_exposure_sha256:'a'.repeat(64),original_target:{name:target.document,qty:2},fingerprint:'decision-preview'};
   } else if(name==='record_decision') {
     expect(args.get('fingerprint')).toBe('decision-preview');expect(JSON.parse(args.get('decision'))).toEqual(decision);
     decided=true;message={name:'UI-DISPOSITION',created:true};
   } else throw new Error('Unexpected disposition method: '+name);
   await route.fulfill({json:{message}});
 });
 const modal=()=>frame.locator('.modal:visible').last();
 await frame.getByRole('button',{name:'OpenSourceRail',exact:true}).click();
 await frame.getByText('Revision dispositions',{exact:true}).click();
 await modal().getByRole('button',{name:'Propose disposition',exact:true}).click();
 await expect.poll(()=>frame.locator('body').evaluate(()=>window.cur_dialog?.title)).toBe('Propose revision disposition');
 await modal().locator('select[data-fieldname="mapping"]').selectOption('UI-MAP');
 await modal().locator('select[data-fieldname="target"]').selectOption(JSON.stringify(target));
 await modal().locator('select[data-fieldname="action"]').selectOption('Request production stop');
 await modal().locator('input[data-fieldname="responsible"]').fill('Administrator');
 await frame.locator('body').evaluate(()=>window.cur_dialog.set_value('due_date','2026-10-01'));
 await modal().locator('textarea[data-fieldname="rationale"]').fill('UI fixture revised engineering interfaces');
 await modal().locator('textarea[data-fieldname="references"]').fill('fixture:drawing-R2');
 // Workbench's tool frame can be taller than this small outer viewport.
 await page.locator('#moduleFrame').evaluate(el=>el.scrollIntoView({block:'end'}));
 await modal().getByRole('button',{name:'Preview proposal',exact:true}).click();
 await expect(modal()).toContainText('This records a plan and assignment.');
 await modal().getByRole('button',{name:'Record proposal',exact:true}).click();
 await modal().getByRole('button',{name:'Review plan',exact:true}).click();
 await modal().locator('select[data-fieldname="outcome"]').selectOption('Endorse plan');
 await modal().locator('textarea[data-fieldname="rationale"]').fill('UI fixture independent review');
 await modal().locator('textarea[data-fieldname="references"]').fill('fixture:review-1');
 await modal().getByRole('button',{name:'Preview decision',exact:true}).click();
 await expect(modal()).toContainText('Originally reviewed record:');
 await modal().getByRole('button',{name:'Record decision',exact:true}).click();
 await expect(modal()).toContainText('Endorse plan · Exposure current · execution unverified');
 expect(calls).toEqual(['catalogue','preview','record','catalogue','preview_decision','record_decision','catalogue']);
 expect(errors).toEqual([]);
 console.log('PASS native ERP disposition dialogs: typed proposal, explicit preview, independent decision and unverified-execution label (mocked business replies)');
}catch(error){
 if(page){
   await page.screenshot({path:'build/disposition-dialog-failure.png',fullPage:true});
   console.log(await page.frameLocator('#moduleFrame').locator('body').evaluate(()=>({height:innerHeight,
     modals:[...document.querySelectorAll('.modal.show')].map(m=>({rect:m.getBoundingClientRect().toJSON(),
       body:m.querySelector('.modal-body').getBoundingClientRect().toJSON(),
       button:m.querySelector('.btn-modal-primary')?.getBoundingClientRect().toJSON()}))})));
 }
 throw error;
}finally{await browser.close();}
