import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {launchBrowser} from '../../../tools/automation/tests/browser-launch.mjs';

const browser = await launchBrowser();
try {
    const page = await browser.newPage({viewport:{width:1360,height:940},locale:'en-US'});
    await page.goto(new URL('index.html',import.meta.url).href);
    assert.match(await page.locator('#opening').innerText(),/486\.4m/);
    await page.locator('#journeys').fill('100');
    await page.locator('#fare').fill('1');
    assert.match(await page.locator('#support').innerText(),/386\.4m/);
    await page.screenshot({path:fileURLToPath(new URL('baghdad-funding.png',import.meta.url))});
    await page.locator('#terms').selectOption('shorter_costlier_mixed_debt');
    assert.match(await page.locator('#opening').innerText(),/692\.1m/);
    await page.locator('#network').selectOption('metropolitan');
    assert.match(await page.locator('#opening').innerText(),/2,733\.1m/);
    await page.locator('#network').selectOption('core');
    await page.locator('#terms').selectOption('budget_only');
    assert.match(await page.locator('#opening').innerText(),/Year 5 needs \$30\.5m/);
    assert.equal(await page.locator('#rows tr').count(),34);
    await page.locator('#fare').fill('0');
    assert.match(await page.locator('#support').innerText(),/30\.5m to fund/);
    await page.locator('#journeys').fill('');
    assert.match(await page.locator('#support').innerText(),/Enter paid journeys/);
} finally {
    await browser.close();
}
