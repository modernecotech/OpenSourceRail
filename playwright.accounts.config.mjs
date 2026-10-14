import {defineConfig} from '@playwright/test';
import base from './playwright.config.mjs';
export default defineConfig({...base,testDir:'./tests/acceptance',testMatch:'design-accounts.spec.mjs',outputDir:'./build/playwright/accounts/results',reporter:[['line'],['json',{outputFile:'build/playwright/accounts/report.json'}]],webServer:base.webServer.map(server=>server.command.includes('workbench-server.py')?{...server,command:server.command.replace('--db build/playwright/workbench.sqlite3','--db build/playwright/accounts/workbench.sqlite3 --users tests/fixtures/ops-users.json')}:server)});
