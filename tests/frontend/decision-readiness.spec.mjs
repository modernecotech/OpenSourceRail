import { expect, test } from '@playwright/test';

test('Workbench separates reference qualification from city acceptance', async ({ page }) => {
  await page.goto('http://127.0.0.1:4177/?module=decision-readiness&city=samawah&mode=design');
  const view=page.frameLocator('#moduleFrame');
  await expect(view.locator('#scope')).toContainText('no deployment qualification for samawah');
  await expect(view.locator('[data-stage]')).toHaveCount(6);
  await expect(view.locator('#acceptedUse')).toContainText('No authenticated acceptance');
  await expect(view.locator('#measurements')).toContainText('No physical rig measurements supplied');
  await expect(view.locator('#basis')).toContainText('illustrative assumptions');
  await expect(view.locator('#quantitative')).toContainText('Cooling-loss time');
  await expect(view.locator('#quantitative')).toContainText('Steady-state function unavailability');
  await expect(view.locator('#quantitative')).toContainText('Screening inspection interval at the upper rate');
  const preview=await page.context().newPage();
  await preview.goto('http://127.0.0.1:4177/engineering/assurance/readiness/?city=samawah');
  await expect(preview.locator('[data-stage]')).toHaveCount(6);
  await preview.screenshot({path:'build/review-decision-readiness.png',fullPage:true});
  await preview.close();
  await page.locator('#citySelector').selectOption('mosul');
  await expect(view.locator('#scope')).toContainText('no deployment qualification for mosul');
  await expect(view.locator('#acceptedUse')).toContainText('No authenticated acceptance');
});

test('Mismatched readiness context fails closed', async ({ page }) => {
  await page.route('**/api/assurance/readiness?**',async route => {
    const response=await route.fetch();const payload=await response.json();
    payload.requested_context.city='another-city';
    await route.fulfill({response,json:payload});
  });
  await page.goto('http://127.0.0.1:4177/engineering/assurance/readiness/?city=mosul&environment=physical');
  await expect(page.locator('#scope')).toContainText('does not match the selected context');
  await expect(page.locator('[data-stage]')).toHaveCount(0);
  await expect(page.locator('#acceptedUse')).toContainText('Acceptance unavailable');
});

test('Changed evidence cannot leave a readiness result on screen', async ({ page }) => {
  await page.route('**/api/assurance/readiness?**',route=>route.fulfill({status:409,json:{error:'Raw measurements changed; qualification unresolved',release_ready:false}}));
  await page.goto('http://127.0.0.1:4177/engineering/assurance/readiness/?city=samawah');
  await expect(page.locator('#scope')).toContainText('Raw measurements changed');
  await expect(page.locator('#quantitative article')).toHaveCount(0);
});
