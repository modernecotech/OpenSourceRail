// Run from repository root against the local simulation deployment.
import {chromium,expect} from '@playwright/test';import fs from 'node:fs';import {execFileSync} from 'node:child_process';
const browser=await chromium.launch();const page=await browser.newPage({viewport:{width:1500,height:1050}});
const cfg=JSON.parse(fs.readFileSync('var/supervision/fuxa.json'));
const controls='var/supervision/simulator-control.json';
try {
 await page.goto('http://127.0.0.1:1881/home');const d=page.locator('mat-dialog-container');await d.waitFor();await d.locator('form input[type=text]').fill('operator');await d.locator('input[type=password]').fill(cfg.operator_password);await d.getByRole('button',{name:'OK',exact:true}).click();await d.waitFor({state:'hidden'});
 await expect(page.getByText('180',{exact:true})).toBeVisible({timeout:15000});
 fs.writeFileSync(controls,JSON.stringify({disconnected:true}));
 await expect(page.getByText('disconnected',{exact:true}).first()).toBeVisible({timeout:45000});
 await page.screenshot({path:'build/supervision-fuxa-disconnected.png',fullPage:true});console.log('PASS source loss shows disconnected quality');
 fs.writeFileSync(controls,'{}');await expect(page.getByText('180',{exact:true})).toBeVisible({timeout:15000});
 execFileSync('/home/hayder/bin/docker',['stop','osr-supervision-integration-1']);
 await expect(page.getByText('180',{exact:true})).not.toBeVisible({timeout:20000});
 console.log('PASS gateway outage hides cached values');await page.screenshot({path:'build/supervision-fuxa-gateway-outage.png',fullPage:true});
} finally {fs.writeFileSync(controls,'{}');execFileSync('/home/hayder/bin/docker',['start','osr-supervision-integration-1']);await browser.close();}
