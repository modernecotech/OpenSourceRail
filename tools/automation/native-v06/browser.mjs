// Native FUXA observation and authenticated operator permission checks.
import { expect } from '@playwright/test';
import { launchBrowser } from '../tests/browser-launch.mjs';
import fs from 'node:fs';
const cfg=JSON.parse(fs.readFileSync(process.argv[2]));
const browser=await launchBrowser();
try {
  const page=await browser.newPage({viewport:{width:1400,height:1000}});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(cfg.url+'/home');
  const dialog=page.locator('mat-dialog-container');await dialog.waitFor();
  await dialog.locator('form input[type=text]').fill('operator');
  await dialog.locator('input[type=password]').fill(cfg.password);
  await dialog.getByRole('button',{name:'OK',exact:true}).click();
  await dialog.waitFor({state:'hidden'});
  await expect(page.locator('#'+cfg.widgets.connection)).toHaveText('5',{timeout:30000});
  await expect(page.locator('#'+cfg.widgets.value)).toHaveText('0',{timeout:30000});
  await expect(page.locator('#'+cfg.widgets.quality)).toHaveText('valid',{timeout:30000});
  await expect(page.locator('#'+cfg.widgets.timestamp)).not.toHaveText(/—|not received|unavailable/,{timeout:30000});
  await expect(page.locator('body')).toContainText('condition_code');
  const login=await page.request.post(cfg.url+'/api/signin',{data:{username:'operator',password:cfg.password}});
  const token=(await login.json()).data.token;
  const deny=await page.request.post(cfg.url+'/api/project',{headers:{'x-access-token':token},data:{}});
  expect([401,403]).toContain(deny.status());expect(errors).toEqual([]);
  await page.screenshot({path:cfg.screenshot,fullPage:true});
  console.log('PASS native FUXA current observation and operator configuration refusal');
} finally {await browser.close();}
