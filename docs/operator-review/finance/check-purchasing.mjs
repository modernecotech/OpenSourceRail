import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {launchBrowser} from '../../../tools/automation/tests/browser-launch.mjs';

const browser = await launchBrowser();
try {
  const page = await browser.newPage({viewport:{width:1270,height:900}, locale:'en-US'});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.context().setOffline(true);
  const deliveredPage = process.argv.find(arg => arg.startsWith('--page='))?.slice(7);
  await page.goto(deliveredPage ? pathToFileURL(deliveredPage).href : new URL('purchasing.html', import.meta.url).href);
  const forms = page.locator('#offers section');
  async function fill(i, data) {
    const form = forms.nth(i);
    for (const [key, value] of Object.entries(data)) await form.locator('[name="' + key + '"]').fill(value);
    await form.locator('[name="matched"]').check();
  }
  await page.locator('#article').selectOption({label:'One accessible station'});
  assert.match(await page.locator('#quantity').innerText(), /64/);
  assert.match(await page.locator('#comparison').innerText(), /both returns/);
  const downloaded = page.waitForEvent('download');
  await page.locator('#enquiry').click();
  const spec = await readFile(await (await downloaded).path(), 'utf8');
  assert.match(spec, /One accessible station/);
  assert.match(spec, /station-and-box.svg · SHA-256 [a-f0-9]{64}/);
  await fill(0, {reference:'Illustration A', evidence:'Workshop example A', cash:'14000000',
    local:'5600000', imports:'7000000', terms:'Illustrative matched warranty and repair rights.'});
  await fill(1, {reference:'Illustration B', evidence:'Workshop example B', cash:'13750000',
    local:'6187500', imports:'6875000', terms:'Illustrative matched warranty and repair rights.'});
  assert.match(await forms.nth(1).locator('.summary').innerText(), /45%.*\$687,500/);
  assert.match(await page.locator('#comparison').innerText(), /-\$250,000.*\$587,500/);
  if (process.argv.includes('--capture')) {
    const offers = page.locator('#offers');
    await offers.scrollIntoViewIfNeeded();
    await offers.screenshot({path:fileURLToPath(new URL('supplier-returns.png', import.meta.url))});
  }
  const saved = page.waitForEvent('download');
  await forms.nth(1).locator('.save').click();
  const file = await (await saved).path();
  await forms.nth(0).locator('[name="imports"]').fill('14000000');
  assert.match(await forms.nth(0).locator('.summary').innerText(), /Check the amounts/);
  assert.match(await page.locator('#comparison').innerText(), /both returns/);
  await page.locator('#railway').selectOption('core');
  assert.equal(await forms.nth(0).locator('[name="cash"]').inputValue(), '');
  await forms.nth(0).locator('.load').setInputFiles(file);
  await forms.nth(0).locator('.message').getByText(/Select a saved return/).waitFor();
  await page.locator('#railway').selectOption('first');
  await page.locator('#article').selectOption({label:'One accessible station'});
  assert.equal(await forms.nth(1).locator('[name="cash"]').inputValue(), '13750000');
  await forms.nth(0).locator('.load').setInputFiles(file);
  await forms.nth(0).locator('.message').getByText(/Return opened/).waitFor();
  assert.equal(await forms.nth(0).locator('[name="matched"]').isChecked(), false);
  assert.equal(await forms.nth(0).locator('[name="cash"]').inputValue(), '13750000');
  const altered = JSON.parse(await readFile(file, 'utf8'));
  altered.basis.currency = 'IQD';
  await forms.nth(0).locator('.load').setInputFiles({name:'different-basis.json', mimeType:'application/json',
    buffer:Buffer.from(JSON.stringify(altered))});
  await forms.nth(0).locator('.message').getByText(/Select a saved return/).waitFor();
  assert.match(await forms.nth(0).locator('.summary').innerText(), /claimed/);
  assert.deepEqual(errors, []);
  console.log('Offline enquiry download, scoped comparison, origin reconciliation and return round-trip passed.');
} finally {
  await browser.close();
}
