import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { expect, test } from '@playwright/test';

test('six task areas retain deep links and show scoped design jobs',async({page},testInfo)=>{
  await page.goto('http://127.0.0.1:4177/?module=auto-design&city=samawah&environment=simulation');
  for(const name of ['Plan','Design','Deliver','Operate','Maintain','Assure'])await expect(page.getByRole('button',{name:name+' task area',exact:true})).toBeVisible();
  const view=page.frameLocator('#moduleFrame');
  await expect(view.locator('#status')).toContainText('Local design tools ready');
  await view.locator('#problem').selectOption('clipped-side-bay');
  await view.locator('[data-variable=grade_density]').selectOption('80');
  await view.locator('[data-variable=core_m]').selectOption('0.0246');
  await view.locator('[data-variable=support_span_m]').selectOption('0.2');
  const queued=page.waitForResponse(response=>response.url().endsWith('/api/design/jobs')&&response.request().method()==='POST');
  await view.getByRole('button',{name:'Run on this machine',exact:true}).click();
  const job=await (await queued).json();const card=view.locator('[data-job="'+job.id+'"]');
  await expect(view.locator('#status')).toContainText('Local job queued');
  await expect(async()=>{await view.getByRole('button',{name:'Refresh jobs',exact:true}).click();await expect(card).toContainText('Execution completed');}).toPass({timeout:60000});
  await card.getByRole('button',{name:'Inspect results',exact:true}).click();
  await expect(view.locator('#comparison')).toContainText('Complete installed mass');
  await expect(view.locator('#comparison')).toContainText('unknown');
  await expect(view.locator('#comparison')).toContainText('physical_correlation');
  await view.getByRole('button',{name:'Inspect physical parts',exact:true}).first().click();
  await expect(view.locator('#inspector')).toContainText('Physical definition');
  await expect(view.getByRole('combobox',{name:'Physical part'})).toBeVisible();
  const full=await page.request.get('http://127.0.0.1:4177/api/design/jobs/'+job.id+'/comparison?city=samawah&environment=simulation');
  const proposed=(await full.json()).candidates[0].definition.contract;proposed.revision='desktop-fixture';
  const bytes=Buffer.from(JSON.stringify(proposed));expect(bytes.length).toBeGreaterThan(256*1024);
  await view.locator('#revisedDefinition').setInputFiles({name:'revised-definition.json',mimeType:'application/json',buffer:bytes});
  await view.getByRole('button',{name:'Prepare definition diff and invalidation',exact:true}).click();
  await expect(view.locator('#definitionDiff')).toContainText('"changed_definition": true');
  await expect(view.locator('#definitionDiff')).toContainText('"baseline_overwrite_permitted": false');
  await view.getByRole('button',{name:'Jobs and comparisons',exact:true}).click();
  await card.getByRole('button',{name:'Inspect logs and artifacts',exact:true}).click();
  await expect(view.locator('#comparison')).toContainText('comparison.json');
  await card.getByRole('button',{name:'Export review package',exact:true}).click();
  await expect(view.locator('#comparison')).toContainText('Archive SHA256');
  const link=view.locator('#comparison a').first();await expect(link).toHaveAttribute('href',/\/download\?/);
  const expected=(await link.textContent()).match(/SHA256 ([a-f0-9]{64})/)[1];
  const waiting=page.waitForEvent('download');await link.click();const downloaded=await waiting;
  const output=testInfo.outputPath('review-chunk');await downloaded.saveAs(output);
  expect(createHash('sha256').update(await readFile(output)).digest('hex')).toBe(expected);
});

test('appointments remain drafts without authenticated independent record review',async({page})=>{
  await page.goto('http://127.0.0.1:4177/?module=evidence-intake&city=samawah&environment=simulation');
  const view=page.frameLocator('#moduleFrame');await expect(view.locator('#status')).toContainText('Local design tools ready');
  await view.locator('#kind').selectOption('appointment');
  await view.getByLabel('Person name',{exact:true}).fill('Browser fixture appointment');
  await view.getByLabel('Organization',{exact:true}).fill('Acceptance test fixture');
  await view.getByLabel('Appointed role',{exact:true}).fill('future test executor');
  await view.getByLabel('Project, responsibility and limits',{exact:true}).fill('simulation only');
  await view.getByLabel('Appointment valid until',{exact:true}).fill('2099-01-01');
  await page.reload();await expect(view.getByLabel('Person name',{exact:true})).toHaveValue('Browser fixture appointment');
  await view.getByRole('button',{name:'Save draft record',exact:true}).click();
  await expect(view.locator('#status')).toContainText('Draft record retained');
  await expect(view.locator('#records')).toContainText('Record draft');
  await expect(view.getByRole('button',{name:'Verify exact record and evidence',exact:true}).first()).toBeDisabled();
  await page.locator('#citySelector').selectOption('mosul');
  await expect(view.locator('#context')).toContainText('mosul');
  await expect(view.locator('#records')).not.toContainText('Browser fixture appointment');
  await expect(view.getByLabel('Person name',{exact:true})).toHaveValue('');
});


test('explicit production inputs respect procurement closures and shared equipment',async({page})=>{
  await page.goto('http://127.0.0.1:4177/?module=auto-design&city=samawah');
  const view=page.frameLocator('#moduleFrame');await expect(view.locator('#status')).toContainText('Local design tools ready');
  await view.getByText('Finite-resource production and installation draft',{exact:true}).click();
  await view.locator('#productionInput').fill(JSON.stringify({tasks:[{id:'fixture-lift',duration_hours:3,release_hour:4,closure_windows:[[0,6],[10,16]],predecessors:[],resources:{crane:1},productivity_source:'explicit acceptance fixture'}],resources:[{id:'crane',capacity:1,available_windows:[[11,15]]}]}));
  await view.getByRole('button',{name:'Calculate draft schedule',exact:true}).click();
  await expect(view.locator('#productionOutput')).toContainText('"start_hour": 11');
  await expect(view.locator('#productionOutput')).toContainText('"physical_release": false');
});
