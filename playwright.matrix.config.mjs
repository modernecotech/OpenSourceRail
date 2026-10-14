import { defineConfig } from '@playwright/test';
import base from './playwright.config.mjs';

export default defineConfig({
  ...base,
  testMatch:['**/design-engine.spec.mjs','**/design-responsive.spec.mjs','**/engineering-change.spec.mjs'],
  outputDir:'./build/playwright/matrix/results',
  reporter:[['line'],['json',{outputFile:'build/playwright/matrix/report.json'}]],
  projects:['chromium','firefox','webkit'].map(browserName=>({name:browserName,use:{...base.use,browserName,serviceWorkers:'allow'}})),
});
