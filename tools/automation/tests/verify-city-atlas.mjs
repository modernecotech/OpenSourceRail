import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {launchBrowser} from './browser-launch.mjs';
if(process.argv[2]==='--cached-native-upload-only'){
  assert.equal(process.argv.length,4,'Provide one private authenticated case descriptor');
  const {runCachedNativeUpload}=await import('./cached-native-upload.mjs');
  await runCachedNativeUpload({root:process.env.OSR_ROOT||process.cwd(),python:process.env.OSR_PYTHON||'/home/hayder/Documents/OpenSourceRail/.venv/bin/python',descriptorPath:resolve(process.argv[3])});
}else{
const root=process.env.OSR_ROOT||process.cwd(),python=process.env.OSR_PYTHON||'/home/hayder/Documents/OpenSourceRail/.venv/bin/python';
const out=resolve(root,'build/city-atlas-browser');await mkdir(out,{recursive:true});
const server=spawn(python,['-u','tools/automation/default-design-workbench.py','--port','8097'],{cwd:root,stdio:['ignore','pipe','pipe']});
let log='',browser;server.stdout.on('data',c=>log+=c);server.stderr.on('data',c=>log+=c);
try {
  const deadline=Date.now()+30000;
  while(!log.includes('http://127.0.0.1:8097')&&Date.now()<deadline)await new Promise(r=>setTimeout(r,100));
  assert(log.includes('http://127.0.0.1:8097'),log);
  browser=await launchBrowser();
  const page=await browser.newPage({viewport:{width:1500,height:1100}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8097/docs/workbench/current/?outlineCity=samawah');
  await page.locator('.atlas-service-table tbody tr').first().waitFor({timeout:60000});
  assert.equal(await page.locator('.atlas-service-table tbody tr').count(),5);
  assert((await page.locator('#city-atlas').innerText()).includes('Samawah'));
  const gisLink=page.getByRole('link',{name:'Download editable RustGIS project and source tables'});
  const gisPath=await gisLink.getAttribute('href');
  assert.match(gisPath,/^\/api\/rustgis\/samawah\/[a-f0-9]{64}\.zip$/);
  const gisResponse=await page.request.get('http://127.0.0.1:8097'+gisPath);
  assert.equal(gisResponse.status(),200);
  assert.equal(gisResponse.headers()['content-type'],'application/zip');
  assert.equal((await gisResponse.body()).subarray(0,2).toString(),'PK');
  await page.locator('#city-atlas').screenshot({path:out+'/samawah.png'});
  // Real current-data journey inspection, not historical average-speed substitution.
  const journey=await page.evaluate(()=>{
    const p=window.__cityAtlasTestPacket;
    return !!window.OSRCityJourneys;
  });assert(journey);
  await page.selectOption('#city-outline-select','baghdad');
  await page.waitForFunction(()=>document.querySelector('.atlas-title')?.textContent?.includes('Baghdad') || document.querySelector('#city-atlas h3')?.textContent?.includes('Baghdad'),{timeout:60000});
  await page.waitForFunction(()=>document.querySelectorAll('.atlas-service-table tbody tr').length===14);
  await page.locator('#city-atlas').screenshot({path:out+'/baghdad.png'});
  // Two rapid selections must leave only the most recently requested city.
  await page.selectOption('#city-outline-select','samawah');await page.selectOption('#city-outline-select','baghdad');
  await page.waitForFunction(()=>document.querySelectorAll('.atlas-service-table tbody tr').length===14);
  assert((await page.locator('#city-atlas').innerText()).includes('Baghdad'));
  await page.selectOption('#city-outline-select','samawah');
  await page.waitForFunction(()=>document.querySelectorAll('.atlas-service-table tbody tr').length===5);
  await page.locator('.atlas-map-controls button').first().click();
  await page.getByRole('button',{name:'Fit network',exact:true}).click();
  await page.locator('.atlas-station-picker select').selectOption({index:1});
  await page.locator('.atlas-finance summary').click();
  await page.locator('.atlas-finance input').nth(0).fill('1000000');
  await page.locator('.atlas-finance input').nth(1).fill('1');
  await page.getByRole('button',{name:'Calculate fare and whole-life scenario'}).click();
  assert((await page.locator('.atlas-finance').innerText()).includes('cost-covering average fare'));
  await page.locator('#city-study-options input[name="peak_demand_pphpd"]').fill('5200');
  await page.locator('#city-study-options select[name="selection"]').selectOption('anchor-preserving-chord-research');
  const calculatedResponse=page.waitForResponse(response=>response.url().includes('/api/city-atlas/study/')&&response.status()===200);
  await page.locator('#city-study-start').click();
  await page.waitForFunction(()=>!document.querySelector('#city-study-result').hidden,{timeout:180000});
  const status=await page.locator('#city-outline-status').innerText();assert(status.includes('recalculated study'),status);
  const calculated=await (await calculatedResponse).json();
  assert.equal(calculated.identity.selected_alignment_kind,'anchor-preserving-chord-research');
  assert.equal(calculated.lines[0].metrics.peak_demand_pphpd,5200);
  assert((await page.locator('#city-atlas').textContent()).includes(calculated.identity.outline_evaluation_id));
  assert((await page.locator('.atlas-service-table').innerText()).includes('5,200'));
  assert.equal(await page.locator('.atlas-service-table tbody tr').count(),5);
  const revisedGIS=page.getByRole('link',{name:'Download editable RustGIS project and source tables'});
  assert.equal(await revisedGIS.count(),1);
  const revisedGISPath=await revisedGIS.getAttribute('href');
  assert.match(revisedGISPath,new RegExp('^/api/rustgis/study/[a-f0-9]{32}/'+calculated.packet_id+'\\.zip$'));
  const revisedGISResponse=await page.request.get('http://127.0.0.1:8097'+revisedGISPath);
  assert.equal(revisedGISResponse.status(),200);
  assert.equal((await revisedGISResponse.body()).subarray(0,2).toString(),'PK');
  const record=await page.request.get('http://127.0.0.1:8097/api/city-atlas/samawah');assert.equal(record.status(),200);
  const p=await record.json();assert.equal(p.physical_accepted,false);
  await page.setViewportSize({width:390,height:844});
  await page.locator('#city-atlas').screenshot({path:out+'/mobile.png'});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+2);assert.equal(overflow,false);
  assert.deepEqual(errors,[]);
  // Exercise the published HTTPS/static path without relying on local API routes.
  const published=await browser.newPage();let tamper=false;
  await published.route('https://atlas.test/**',async route=>{
    const url=new URL(route.request().url());
    if(url.pathname.startsWith('/api/'))return route.fulfill({status:404,json:{error:'Static publication'}});
    let pathname=decodeURIComponent(url.pathname);if(pathname.endsWith('/'))pathname+='index.html';
    const file=resolve(root,'.'+pathname);
    if(!file.startsWith(resolve(root)+'/'))return route.fulfill({status:404,body:''});
    try {
      let body=await readFile(file);
      if(tamper&&pathname.endsWith('/city-atlas/cities/samawah.json.gz')){body=Buffer.from(body);body[10]^=1;}
      const type=pathname.endsWith('.js')?'application/javascript':pathname.endsWith('.css')?'text/css':pathname.endsWith('.html')?'text/html':pathname.endsWith('.gz')?'application/gzip':'application/json';
      await route.fulfill({status:200,contentType:type,body});
    }catch{await route.fulfill({status:404,json:{error:'Unknown static asset'}});}
  });
  await published.goto('https://atlas.test/docs/workbench/current/?outlineCity=samawah');
  await published.locator('.atlas-service-table tbody tr').first().waitFor({timeout:60000});
  assert.equal(await published.locator('.atlas-service-table tbody tr').count(),5);
  assert((await published.locator('.atlas-attribution').innerText()).includes('source bytes verified'));
  tamper=true;await published.reload();
  await published.waitForFunction(()=>document.querySelector('#city-outline-status')?.textContent.includes('payload differs'),{timeout:60000});
  assert.equal(await published.locator('.atlas-service-table').count(),0);
  await published.close();
  await writeFile(out+'/result.json',JSON.stringify({passed:true,cities:['samawah','baghdad'],recalculation_updates_map:true,static_publication_and_tamper_check:true,rapid_selection_guard:true,mobile_no_overflow:true,physical_accepted:false},null,2));
  console.log('Atlas browser checks passed');
} finally {
  await writeFile(out+'/server.log',log);
  if(browser)await browser.close();server.kill('SIGTERM');
}

}
