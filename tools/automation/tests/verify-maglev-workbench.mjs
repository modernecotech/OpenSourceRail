// Exercise the actual primary server and default UI, including city changes.
import { chromium } from '@playwright/test';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import assert from 'node:assert/strict';

const root = resolve(import.meta.dirname, '../../..');
const output = resolve(process.argv[2] || 'build/maglev-workbench-browser');
await mkdir(output, { recursive: true });
const server = spawn('tools/automation/osr-python', ['tools/automation/maglev-workbench.py', '--port', '0'], {cwd:root, stdio:['ignore','pipe','pipe']});
let browser;
let stderr = '';
server.stderr.on('data', chunk => { stderr += String(chunk); });
try {
  const origin = await new Promise((accept,reject) => {
    const timer = setTimeout(() => reject(Error('Primary server startup timeout: '+stderr)),30000);
    server.stdout.on('data', chunk => {
      const match = String(chunk).match(/http:\/\/127\.0\.0\.1:\d+/);
      if (match) { clearTimeout(timer); accept(match[0]); }
    });
    server.once('exit', code => { clearTimeout(timer); reject(Error(`Server exited ${code}: ${stderr}`)); });
  });
  browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors=[], failures=[], external=[];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('requestfailed', request => failures.push(request.url()));
  page.on('request', request => { if (!request.url().startsWith(origin+'/')) external.push(request.url()); });
  await page.goto(origin+'/');
  await page.waitForURL('**/docs/workbench/maglev/**');
  await page.waitForFunction(() => document.querySelector('#city-status').textContent.includes('Baghdad'));
  assert.equal(await page.locator('#city option').count(),266);
  await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth>0));
  assert.equal(await page.locator('img').count(),4);
  await page.screenshot({path:output+'/desktop.png',fullPage:true});
  const exercised=[];
  for (const city of ['kisangani','lubumbashi','garissa','baghdad']) {
    await page.selectOption('#city',city);
    await page.waitForFunction(city => new URL(location.href).searchParams.get('city') === city,city);
    const link = await page.locator('#city-links a').last().getAttribute('href');
    const response = await page.request.get(new URL(link, origin).href);
    const summary = await response.json();
    assert.equal(summary.city,city);
    assert.equal(summary.architecture,'ferrite-pm-maglev-study');
    assert.equal(summary.physical_release,false);
    exercised.push(city);
  }
  for (const href of await page.locator('a').evaluateAll(nodes => nodes.map(node => node.href))) {
    const response = await page.request.get(href);
    assert.equal(response.status(),200,href);
  }
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth<=innerWidth),'mobile horizontal overflow');
  await page.screenshot({path:output+'/mobile.png',fullPage:true});
  for (const path of ['/.git/config','/var/ops-core.sqlite3','/build/maglev-workflow/latest.json']) {
    assert.equal((await page.request.get(origin+path)).status(),404);
  }
  assert.deepEqual(errors,[]); assert.deepEqual(failures,[]); assert.deepEqual(external,[]);
  const result={primary_ui:true,cities:266,exercised,images:4,links:true,mobile:true,private_paths_rejected:true,errors,external,physical_release:false};
  await writeFile(output+'/checks.json',JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result));
} finally {
  await browser?.close();
  server.kill('SIGTERM');
}
