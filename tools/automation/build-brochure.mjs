#!/usr/bin/env node
// Publish the current HTML brochure and retain verifiable source/output hashes.
import { chromium } from '@playwright/test';
import { createHash } from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const source = 'docs/open-source-rail-brochure.html';
const outputs = ['OpenSourceRail-Brochure.pdf'];
const receiptPath = path.join(root, 'docs/brochure-publication.json');
const digest = async relative => createHash('sha256').update(await fs.readFile(path.join(root, relative))).digest('hex');
const html = await fs.readFile(path.join(root, source), 'utf8');
const sources = new Set(['tools/automation/build-brochure.mjs', source]);
for (const match of html.matchAll(/src="([^"]+)"/g)) {
  const asset = path.resolve(root, 'docs', match[1]);
  if (!asset.startsWith(root + path.sep)) throw new Error('Brochure asset outside repository');
  sources.add(path.relative(root, asset).split(path.sep).join('/'));
}
const hashes = async names => Object.fromEntries(await Promise.all([...names].sort().map(async name => [name, await digest(name)])));
const arguments_ = process.argv.slice(2);
if (arguments_.length && (arguments_.length !== 1 || arguments_[0] !== '--check')) {
  throw new Error('Usage: node tools/automation/build-brochure.mjs [--check]');
}
if (arguments_[0] === '--check') {
  const saved = JSON.parse(await fs.readFile(receiptPath, 'utf8'));
  if (JSON.stringify(saved.sources_sha256) !== JSON.stringify(await hashes(sources)) ||
      JSON.stringify(saved.outputs_sha256) !== JSON.stringify(await hashes(outputs))) {
    throw new Error('Brochure source or PDF changed; regenerate the publication');
  }
  console.log('Brochure source and PDF hashes pass');
} else {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    await page.goto(pathToFileURL(path.join(root, source)).href, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const missing = await page.locator('img').evaluateAll(images => images.filter(i => !i.complete || !i.naturalWidth).map(i => i.src));
    if (missing.length) throw new Error('Missing brochure images: ' + missing.join(', '));
    if (await page.locator('.page').count() !== 2) throw new Error('Expected two brochure pages');
    await page.pdf({ path: path.join(root, outputs[0]), preferCSSPageSize: true, printBackground: true });
  } finally {
    await browser.close();
  }
  await fs.writeFile(receiptPath, JSON.stringify({ schema_version: 1, sources_sha256: await hashes(sources), outputs_sha256: await hashes(outputs) }, null, 2) + '\n');
  console.log('Published current two-page brochure with repository QR');
}
