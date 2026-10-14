import {expect} from '@playwright/test';

// Follow the same visible task-area and module controls as a Workbench user.
export async function openWorkbenchModule(page, module) {
 const response=await page.request.get(new URL('/workbench/modules.json',page.url()).href);
 await expect(response).toBeOK();
 const registry=await response.json();
 const entry=registry.modules.find(row=>row.id===module);
 if(!entry)throw new Error('Unknown Workbench module: '+module);
 const area=page.locator(`[data-area="${entry.group}"]`);
 await expect(area).toBeVisible();
 await area.click();
 await expect(area).toHaveAttribute('aria-pressed','true');
 const button=page.locator(`[data-module="${module}"]`);
 await expect(button).toBeVisible();
 await button.click();
}
