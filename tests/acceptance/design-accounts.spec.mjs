import {expect,test} from '@playwright/test';

test('actual named approver verifies retained appointment evidence independently',async({page})=>{
  await page.goto('http://127.0.0.1:4177/docs/design-engine/?view=evidence&city=samawah');
  await page.getByText('Account for scoped records and independent verification',{exact:true}).click();
  async function signIn(username,password){await page.locator('#login input[name=username]').fill(username);await page.locator('#login input[name=password]').fill(password);await page.getByRole('button',{name:'Sign in',exact:true}).click();await expect(page.locator('#status')).toContainText('Local design tools ready');}
  await signIn('inspector','Inspector-pass-123!');
  await page.locator('#kind').selectOption('appointment');
  for(const [field,value]of [['Person name','Fixture named appointment'],['Organization','Test fixture only'],['Appointed role','Test executor'],['Project, responsibility and limits','Simulation fixture; no engineering release'],['Appointment valid until','2099-01-01']])await page.getByLabel(field,{exact:true}).fill(value);
  await page.locator('#evidenceFile').setInputFiles({name:'appointment-fixture.txt',mimeType:'text/plain',buffer:Buffer.from('Fixture retained appointment evidence; not a real appointment.\n')});
  await page.getByRole('button',{name:'Save draft record',exact:true}).click();
  await expect(page.locator('#status')).toContainText('Draft record retained');
  await page.getByRole('button',{name:'Verify exact record and evidence',exact:true}).first().click();
  await expect(page.locator('#status')).toContainText('authenticated record reviewer required');
  await signIn('approver','Approver-pass-123!');
  await page.getByRole('button',{name:'Verify exact record and evidence',exact:true}).first().click();
  await expect(page.locator('#status')).toContainText('Record verified by approver');
  await expect(page.locator('#records')).toContainText('Record verified-record');
  const response=await page.request.get('http://127.0.0.1:4177/api/design/records?city=samawah&environment=simulation');
  const record=(await response.json()).records.find(r=>r.payload.person_name==='Fixture named appointment');
  expect(record.creator).toBe('inspector');expect(record.verifier).toBe('approver');
  expect(record.physical_release).toBe(false);expect(record.independent_acceptance).toBe(false);
});
