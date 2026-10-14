import { test, expect } from '@playwright/test';

// Interface fixtures exercise browser draft ownership. Actual scope/hash/source
// and solver behaviour are tested at the HTTP boundary in Python.
for (const lang of ['en', 'ar']) {
  test(`engineering draft retains candidate scope and renders ${lang}`, async ({ page }) => {
    const identity = {schema:'osr-design-identity/1',city:'samawah',project:'samawah',environment:'simulation',configuration_revision:'research-1',baseline_sha256:null,run_id:null,asset_id:null,part_id:null};
    const contractHash = 'a'.repeat(64);
    const candidate = {id:'fixture-candidate',metrics:{defined_mass_kg:123},checks:{geometry:{state:'passed',basis:'UI fixture only'}},definition:{contract:{parts:[{id:'fixture-part'}]},installed_register:{physical_definition_sha256:contractHash}}};
    let submitted;
    await page.route('**/api/ops-auth/session', route => route.fulfill({json:{actor:{username:'fixture-planner',display_name:'Browser fixture',csrf:'fixture-csrf'}}}));
    await page.route('**/api/design/**', route => {
      const path = new URL(route.request().url()).pathname;
      let json;
      if (path.endsWith('/problems')) json={problems:[{id:'fixture-problem',variables:{},budget:{evaluations:2},applicability:{function:'UI fixture only'}}],preflight:{'fixture-problem':{available:false,missing:['fixture has no solver']}}};
      else if (path.endsWith('/review-schema')) json={kinds:{appointment:['person_name']},accounts_configured:false};
      else if (path.endsWith('/parts')) json={sources:{},parts:[]};
      else if (path.endsWith('/jobs')) json={jobs:[{id:'fixture-job',status:'completed',phase:'completed',progress:100,source_state:'current',request:{identity,problem:{id:'fixture-problem'}}}]};
      else if (path.endsWith('/work-queue')) json={entries:[]};
      else if (path.endsWith('/comparison')) json={identity,source_state:'current',candidates:[candidate]};
      else if (path.endsWith('/qualification-draft')) {submitted=route.request().postDataJSON();json={state:'draft',physical_release:false,baseline_modified:false,missing_fields:['part_rules[0].basis_reference'],draft_sha256:'b'.repeat(64)};}
      else json={};
      return route.fulfill({json});
    });
    await page.goto(`http://127.0.0.1:4177/docs/design-engine/?city=samawah&environment=simulation&revision=research-1&view=jobs&lang=${lang}`);
    await page.getByRole('button',{name:'Inspect results',exact:true}).click();
    await page.getByRole('button',{name:'Inspect physical parts',exact:true}).click();
    const input=page.locator('#qualificationInput');
    await expect(input).toBeVisible();
    const original=JSON.parse(await input.inputValue());
    expect(original.part_rules[0].physical_id).toBe('fixture-part');
    expect(original.part_rules[0].stock_bounds_m).toEqual([null,null,null]);
    original.part_rules[0].basis_reference='Clearly labelled draft browser fixture';
    await input.fill(JSON.stringify(original,null,2));
    await page.reload();
    await page.getByRole('button',{name:'Inspect results',exact:true}).click();
    await page.getByRole('button',{name:'Inspect physical parts',exact:true}).click();
    expect(JSON.parse(await input.inputValue()).part_rules[0].basis_reference).toContain('browser fixture');
    await page.locator('#qualificationValidate').focus();
    await page.keyboard.press('Enter');
    await expect(page.locator('#qualificationOutput')).toContainText('"physical_release": false');
    expect(submitted.contract_sha256).toBe(contractHash);
    expect(submitted.identity).toEqual(identity);
    expect(submitted.kind).toBe('manufacturing');
    await expect(page.locator('html')).toHaveAttribute('dir',lang==='ar'?'rtl':'ltr');
    await page.evaluate(() => window.dispatchEvent(new MessageEvent('message',{origin:location.origin,source:window,data:{type:'osr:context',context:{city:'samawah',environment:'physical',revision:'research-1',baseline_sha256:null}}})));
    await expect(page.locator('#qualificationDraft')).toBeHidden();
    await expect(page.locator('#qualificationOutput')).toBeEmpty();
    expect(await page.locator('#qualificationInput').inputValue()).toBe('');
  });
}
