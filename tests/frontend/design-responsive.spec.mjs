import { expect,test } from '@playwright/test';

test('task navigation supports keyboard, mobile reflow and Arabic RTL',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto('http://127.0.0.1:4177/?module=auto-design&city=samawah&environment=simulation');
  await page.keyboard.press('Tab');await expect(page.locator('.skip-link')).toBeFocused();
  await page.getByRole('button',{name:'Design task area',exact:true}).focus();
  await expect(page.getByRole('button',{name:'Design task area',exact:true})).toBeFocused();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.locator('#language').selectOption('ar');
  await expect(page.locator('html')).toHaveAttribute('dir','rtl');await expect(page.locator('html')).toHaveAttribute('lang','ar');
  await expect(page.getByRole('button',{name:'التصميم مجال العمل',exact:true})).toBeVisible();
  const view=page.frameLocator('#moduleFrame');await expect(view.locator('html')).toHaveAttribute('dir','rtl');
  await expect(view.getByRole('button',{name:'التنفيذ على هذا الجهاز',exact:true})).toBeVisible();
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%';});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
});

test('verification matrix never substitutes selected formal success for open obligations',async({request})=>{
  const response=await request.get('http://127.0.0.1:4177/api/design/verification-matrix?city=samawah&environment=simulation');
  expect(response.ok()).toBe(true);const data=await response.json();
  expect(data.formal_obligations.length).toBeGreaterThan(40);
  expect(data.selected_proof_success_closes_other_obligations).toBe(false);
  expect(data.physical_release).toBe(false);
  expect(data.checks.some(c=>c.state==='unknown'&&c.appointed_person===null)).toBe(true);
});
