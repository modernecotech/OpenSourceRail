import { expect, test } from '@playwright/test';

test('Workbench shows city-scoped CAD and native production evidence', async ({ page }) => {
  await page.goto('http://127.0.0.1:4177/?module=engineering-change&city=samawah&environment=simulation&mode=design');
  const view=page.frameLocator('#moduleFrame');
  await expect(view.locator('#status')).toContainText('samawah · simulation · 1 recorded change');
  await expect(view.locator('#changes')).toContainText('11 native ERP checks passed');
  await expect(view.locator('#changes')).toContainText('baseline superseded; candidate screening-current');
  await expect(view.locator('#changes')).toContainText('273.6');
  await expect(view.locator('#changes')).toContainText('0.047185');
  // Default fixture ERP differs from the recorded deployment: suppress native links.
  await expect(view.locator('#nativeLinks')).toHaveCount(0);
  await page.locator('#citySelector').selectOption('mosul');
  await expect(view.locator('#status')).toContainText('mosul · simulation · 1 recorded change');
  await expect(view.locator('#changes')).toContainText('MOS-RS-L1-001');
  await expect(view.locator('#changes')).toContainText('250');
  await expect(view.locator('#changes')).not.toContainText('SAM-RS-L1-001');
  await page.locator('#citySelector').selectOption('samawah');
  await expect(view.locator('#changes')).toContainText('11 native ERP checks passed');
  await page.goto('http://127.0.0.1:4177/engineering/changes/?city=nampula&environment=simulation');
  await expect(page.locator('#status')).toContainText('No recorded engineering change for nampula');
  await expect(page.locator('#changes section')).toHaveCount(0);
  await page.goto('http://127.0.0.1:4177/engineering/changes/?city=samawah&environment=physical');
  await expect(page.locator('#changes section')).toHaveCount(0);
  await expect(page.locator('#status')).toContainText('No recorded engineering change');
});

test('Mislabelled catalogue evidence cannot expose another city', async ({ page }) => {
  await page.route('**/engineering/changes/catalogue.json', async route => {
    const response=await route.fetch();const catalogue=await response.json();
    catalogue.entries=[{...catalogue.entries.find(e=>e.city==='samawah'),city:'mosul'}];
    await route.fulfill({response,json:catalogue});
  });
  await page.goto('http://127.0.0.1:4177/engineering/changes/?city=mosul&environment=simulation');
  await expect(page.locator('#status')).toContainText('Evidence does not match the selected city');
  await expect(page.locator('#changes section')).toHaveCount(0);
});

test('Native searches remain bound to the run when a deployment reuses document IDs', async ({ page }) => {
  const catalogue=await (await page.request.get('http://127.0.0.1:4177/engineering/changes/catalogue.json')).json();
  const entry=catalogue.entries.find(e=>e.city==='samawah'&&e.environment==='simulation');
  await page.route('**/api/workbench/services', route=>route.fulfill({json:{erp:entry.erp_origin}}));
  await page.goto('http://127.0.0.1:4177/engineering/changes/?city=samawah&environment=simulation');
  const report=await (await page.request.get(new URL(entry.native_report,'http://127.0.0.1:4177/engineering/changes/').href)).json();
  const project=page.getByRole('link',{name:'Find recorded project',exact:true});
  await expect(project).toBeVisible();
  expect(new URL(await project.getAttribute('href')).searchParams.get('project_name')).toBe('OSR simulation CAD change '+report.run);
  const workOrder=new URL(await page.getByRole('link',{name:'Find held baseline work order',exact:true}).getAttribute('href'));
  expect(workOrder.searchParams.get('name')).toBe(report.work_orders.baseline);
  expect(workOrder.searchParams.get('production_item')).toBe('CAD-KIT-'+report.run);
  const bom=new URL(await page.getByRole('link',{name:'Find revised BOM',exact:true}).getAttribute('href'));
  expect(bom.origin).toBe(entry.erp_origin);
  expect(bom.searchParams.get('name')).toBe(report.boms.candidate.kit);
  expect(bom.searchParams.get('item')).toBe('CAD-KIT-'+report.run);
});

test('A mismatched ERP origin never links reused native document identifiers', async ({ page }) => {
  const catalogue=await (await page.request.get('http://127.0.0.1:4177/engineering/changes/catalogue.json')).json();
  const origin=new URL(catalogue.entries.find(e=>e.city==='samawah').erp_origin);
  origin.port=origin.port==='8180'?'8284':'8180';
  await page.route('**/api/workbench/services', route=>route.fulfill({json:{erp:origin.origin}}));
  await page.goto('http://127.0.0.1:4177/engineering/changes/?city=samawah&environment=simulation');
  await expect(page.locator('#changes')).toContainText('native ERP checks passed');
  await expect(page.getByRole('link',{name:'Find recorded project',exact:true})).toHaveCount(0);
  await expect(page.locator('#nativeLinks')).toHaveCount(0);
  await expect(page.locator('#changes')).toContainText('another recorded deployment');
});
