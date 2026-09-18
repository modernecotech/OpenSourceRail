import { expect, test } from '@playwright/test';

test('Workbench compares scoped city options and retains their release boundary', async ({ page }) => {
  await page.goto('http://127.0.0.1:4177/?module=design-options&city=samawah&environment=simulation&mode=design');
  const view=page.frameLocator('#moduleFrame');
  await expect(view.locator('#status')).toContainText('samawah · simulation');
  await expect(view.locator('#options')).toContainText('Recorded artifact hashes verified');
  await expect(view.locator('#options')).toContainText('Costs have not been recalculated');
  await expect(view.locator('#options')).toContainText('operating release');
  await expect(view.locator('#options section').first().locator('table tr').nth(1)).toContainText('Pass');
  await page.locator('#citySelector').selectOption('mosul');
  await expect(view.locator('#status')).toContainText('mosul · simulation');
  await expect(view.locator('#options')).toContainText('line-2');
  await expect(view.locator('#options')).toContainText('storage modules');
  await expect(view.locator('#options')).not.toContainText('line-1-dwell');
  await page.goto('http://127.0.0.1:4177/engineering/design-options/?city=nampula&environment=simulation');
  await expect(page.locator('#status')).toContainText('No recorded design options');
  await expect(page.locator('#options section')).toHaveCount(0);
  await page.goto('http://127.0.0.1:4177/engineering/design-options/?city=samawah&environment=physical');
  await expect(page.locator('#status')).toContainText('No recorded design options');
  await expect(page.locator('#options section')).toHaveCount(0);
});

test('A mislabelled city cannot display another city evidence', async ({ page }) => {
  await page.route('**/engineering/design-options/catalogue.json', async route=>{
    const response=await route.fetch(), doc=await response.json();
    doc.entries=[{...doc.entries.find(e=>e.city==='samawah'),city:'mosul'}];
    await route.fulfill({response,json:doc});
  });
  await page.goto('http://127.0.0.1:4177/engineering/design-options/?city=mosul');
  await expect(page.locator('#status')).toContainText('Evidence does not match the selected city');
  await expect(page.locator('#options section')).toHaveCount(0);
});

test('Altered resource evidence is rejected before it is displayed', async ({ page }) => {
  await page.route('**/engineering/design-options/examples/*/changes.json', async route=>{
    const response=await route.fetch(), doc=await response.json();
    doc.resource_delta.additional_trainsets=999;
    await route.fulfill({response,json:doc});
  });
  await page.goto('http://127.0.0.1:4177/engineering/design-options/?city=samawah');
  await expect(page.locator('#status')).toContainText('Changed option evidence');
  await expect(page.locator('#options section')).toHaveCount(0);
});
