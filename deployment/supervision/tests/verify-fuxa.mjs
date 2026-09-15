// Run from repository root against the local simulation deployment.
import {chromium} from '@playwright/test';import fs from 'node:fs';
const browser=await chromium.launch();const page=await browser.newPage({viewport:{width:1500,height:1050}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:1881/home');const dialog=page.locator('mat-dialog-container');await dialog.waitFor();
const cfg=JSON.parse(fs.readFileSync('var/supervision/fuxa.json'));
await dialog.locator('form input[type=text]').fill('operator');await dialog.locator('input[type=password]').fill(cfg.operator_password);await dialog.getByRole('button',{name:'OK',exact:true}).click();
await dialog.waitFor({state:'hidden'});await page.waitForTimeout(6000);
await page.screenshot({path:'build/supervision-fuxa.png',fullPage:true});
console.log('values',await page.locator('g[type="svg-ext-value"]').allTextContents());console.log('errors',errors);
const signin=await page.request.post('http://127.0.0.1:1881/api/signin',{data:{username:'operator',password:cfg.operator_password}});const data=await signin.json();
const deny=await page.request.post('http://127.0.0.1:1881/api/project',{headers:{'x-access-token':data.data.token},data:{}});console.log('operator config denied',deny.status());
await browser.close();
