// Actual Desk UI, authenticated Frappe endpoints and native records. No routes are mocked.
import {chromium,expect as baseExpect} from '@playwright/test';
import fs from 'node:fs';
const expect=baseExpect.configure({timeout:30000});
const fixture=JSON.parse(fs.readFileSync('var/city-example/disposition-browser.json'));
const browser=await chromium.launch();const checks=[];const sessions={};
const pass=(id,after={})=>{checks.push({id,name:id,passed:true,after,level:'native-browser'});console.log('PASS '+id);};
const output='build/city-example/';
let report={passed:false,checks};
try{
 for(const role of ['proposer','reviewer','executor']){
  const context=await browser.newContext({viewport:{width:1600,height:1900}});const page=await context.newPage();
  await page.goto('http://127.0.0.1:8190/?module=erp&city=samawah');const frame=page.frameLocator('#moduleFrame');
  await frame.locator('#login_email').fill(fixture.users[role]);await frame.locator('#login_password').fill(fixture.passwords[role]);await frame.locator('.btn-login').click();
  await expect.poll(()=>frame.locator('body').evaluate(()=>window.frappe?.session?.user),{timeout:60000}).toBe(fixture.users[role]);
  await page.locator('[data-module=projects]').click();await expect.poll(()=>frame.locator('body').evaluate(()=>window.cur_frm?.doc?.name)).toBe(fixture.project);
  sessions[role]={page,frame};
 }
 pass('disposition.distinct-authenticated-users',{users:fixture.users});
 const call=async(role,method,args={})=>sessions[role].frame.locator('body').evaluate(async(element,{method,args})=>{
  const response=await fetch('/api/method/'+method,{method:'POST',headers:{'Content-Type':'application/json','X-Frappe-CSRF-Token':frappe.csrf_token},body:JSON.stringify(args)});
  return {status:response.status,data:await response.json()};
 },{method,args});
 const open=async role=>{
  const {frame}=sessions[role];await frame.getByRole('button',{name:'OpenSourceRail',exact:true}).click();await frame.getByText('Revision dispositions',{exact:true}).click();
  await expect(frame.locator('.modal.show').last()).toContainText('Revision dispositions');
 };
 const modal=role=>sessions[role].frame.locator('.modal.show').last();
 const row=role=>modal(role).locator('.well').filter({hasText:fixture.order});
 await open('proposer');await modal('proposer').getByRole('button',{name:'Propose disposition',exact:true}).click();
 await modal('proposer').locator('select[data-fieldname=mapping]').selectOption(fixture.mapping);
 const target={kind:'work-order',document:fixture.order};
 await modal('proposer').locator('select[data-fieldname=target]').selectOption(JSON.stringify(target));
 await modal('proposer').locator('select[data-fieldname=action]').selectOption('Request production stop');
 await modal('proposer').locator('input[data-fieldname=responsible]').fill(fixture.users.executor);
 await expect.poll(()=>sessions.proposer.frame.locator('body').evaluate(()=>window.cur_dialog?.title)).toBe('Propose revision disposition');
 await sessions.proposer.frame.locator('body').evaluate(()=>cur_dialog.set_value('due_date',frappe.datetime.add_days(frappe.datetime.get_today(),5)));
 await modal('proposer').locator('textarea[data-fieldname=rationale]').fill('Simulation browser acceptance: changed interfaces require production review.');
 await modal('proposer').locator('textarea[data-fieldname=references]').fill('simulation:unmocked-browser-disposition');
 await sessions.proposer.page.locator('#moduleFrame').evaluate(el=>el.scrollIntoView({block:'end'}));
 await modal('proposer').getByRole('button',{name:'Preview proposal',exact:true}).click();await expect(modal('proposer')).toContainText('This records a plan');
 await modal('proposer').getByRole('button',{name:'Record proposal',exact:true}).click();await expect(row('proposer')).toContainText('Awaiting independent review');
 const data=await sessions.reviewer.frame.locator('body').evaluate(async(element,project)=>(await frappe.call({method:'osr_erpnext.disposition.catalogue',args:{project},type:'GET'})).message,fixture.project);
 const proposal=data.dispositions.find(r=>r.proposal.target.document===fixture.order);expect(proposal).toBeTruthy();
 pass('disposition.browser-proposal-recorded',{proposal:proposal.name,order:fixture.order});
 const decision={outcome:'Endorse plan',rationale:'Independent browser review',references:['simulation:browser-independent-review']};
 const denied=await call('proposer','osr_erpnext.disposition.preview_decision',{disposition:proposal.name,decision});expect(denied.status).toBe(417);
 pass('disposition.self-endorsement-rejected');
 await open('reviewer');await row('reviewer').getByRole('button',{name:'Review plan',exact:true}).click();
 await modal('reviewer').locator('select[data-fieldname=outcome]').selectOption('Endorse plan');
 await modal('reviewer').locator('textarea[data-fieldname=rationale]').fill(decision.rationale);
 await modal('reviewer').locator('textarea[data-fieldname=references]').fill(decision.references[0]);
 await sessions.reviewer.page.locator('#moduleFrame').evaluate(el=>el.scrollIntoView({block:'end'}));
 await modal('reviewer').getByRole('button',{name:'Preview decision',exact:true}).click();await expect(modal('reviewer')).toContainText(fixture.users.reviewer);
 await modal('reviewer').getByRole('button',{name:'Record decision',exact:true}).click();await expect(row('reviewer')).toContainText('Endorse plan');
 pass('disposition.browser-independent-endorsement');
 const verification={key:'browser-'+Date.now(),rationale:'Native performed work checked',references:['simulation:browser-native-outcome']};
 const early=await call('reviewer','osr_erpnext.disposition_execution.preview',{disposition:proposal.name,verification});expect(early.status).toBe(417);
 pass('disposition.unperformed-action-rejected');
 let action=await call('executor','erpnext.manufacturing.doctype.work_order.work_order.stop_unstop',{work_order:fixture.order,status:'Stopped'});expect(action.status).toBe(200);
 pass('disposition.native-stop-through-authenticated-browser',{order:fixture.order});
 const self=await call('executor','osr_erpnext.disposition_execution.preview',{disposition:proposal.name,verification});expect(self.status).toBe(417);
 pass('disposition.executor-cannot-verify-own-action');
 await row('reviewer').getByRole('button',{name:'Verify native outcome',exact:true}).click();
 await modal('reviewer').locator('textarea[data-fieldname=rationale]').fill(verification.rationale);
 await modal('reviewer').locator('textarea[data-fieldname=references]').fill(verification.references[0]);
 await sessions.reviewer.page.locator('#moduleFrame').evaluate(el=>el.scrollIntoView({block:'end'}));
 await modal('reviewer').getByRole('button',{name:'Check native outcome',exact:true}).click();await expect(modal('reviewer')).toContainText('Stopped');
 await expect(modal('reviewer')).toContainText(fixture.users.reviewer);
 await modal('reviewer').getByRole('button',{name:'Record verification',exact:true}).click();await expect(row('reviewer')).toContainText('Native outcome verified');
 await sessions.reviewer.page.screenshot({path:output+'disposition-verified.png',fullPage:true});
 pass('disposition.browser-records-independent-verification');
 action=await call('executor','erpnext.manufacturing.doctype.work_order.work_order.stop_unstop',{work_order:fixture.order,status:'In Process'});expect(action.status).toBe(200);
 await sessions.reviewer.page.reload();await expect.poll(()=>sessions.reviewer.frame.locator('body').evaluate(()=>window.cur_frm?.doc?.name)).toBe(fixture.project);
 await open('reviewer');await expect(row('reviewer')).toContainText('Verification stale');
 await sessions.reviewer.page.screenshot({path:output+'disposition-stale.png',fullPage:true});
 pass('disposition.native-resume-makes-browser-evidence-stale');
 report={passed:true,checks,users:fixture.users,order:fixture.order,proposal:proposal.name,physical_acceptance:false};
}catch(error){report.error=String(error);for(const [role,{page}] of Object.entries(sessions))await page.screenshot({path:output+'disposition-failure-'+role+'.png',fullPage:true});throw error;}
finally{fs.writeFileSync(output+'disposition-report.json',JSON.stringify(report,null,2)+'\n');await browser.close();}
