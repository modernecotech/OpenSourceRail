'use strict';
const byId = id => document.getElementById(id);
const fields = ['reference', 'evidence', 'cash', 'local', 'imports', 'terms', 'matched'];
const money = new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD', maximumFractionDigits: 2});
const percent = new Intl.NumberFormat('en-US', {style: 'percent', maximumFractionDigits: 2});
const drafts = new Map();
const forms = [];
let current;
let network;

function download(filename, text, type) {
  const url = URL.createObjectURL(new Blob([text], {type}));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function values(form) {
  return Object.fromEntries(fields.map(key => {
    const input = form.querySelector('[name="' + key + '"]');
    return [key, key === 'matched' ? input.checked : input.value.trim()];
  }));
}

function restore(form, data) {
  for (const key of fields) {
    const input = form.querySelector('[name="' + key + '"]');
    if (key === 'matched') input.checked = data?.matched === true;
    else input.value = data?.[key] ?? '';
  }
}

function evaluateOffer(data) {
  if ([data.cash, data.local, data.imports].some(value => value === '')) {
    return {message: 'Enter all three amounts to reconcile the price.'};
  }
  const [cash, local, imports] = [data.cash, data.local, data.imports].map(Number);
  if (![cash, local, imports].every(Number.isFinite) || cash <= 0 || local < 0 || imports < 0 ||
      local + imports - cash > 0.000001) {
    return {message: 'Check the amounts. Origin totals must fit within a positive cash price.'};
  }
  const untraced = Math.max(0, cash - local - imports);
  const origin = data.evidence && data.matched ? ' documented ' : ' claimed ';
  return {cash, local, message: percent.format(local / cash) + origin + network.domestic +
    ' value · ' + money.format(untraced) + ' untraced.',
    matched: Boolean(data.matched && data.reference && data.evidence && data.terms)};
}

function compare() {
  const offers = forms.map(form => {
    const result = evaluateOffer(values(form));
    form.querySelector('.summary').textContent = result.message;
    return result;
  });
  let text = 'Comparison opens when both returns have reconciled prices, references, commercial terms and buyer confirmation.';
  if (offers.every(offer => offer.matched)) {
    const [a, b] = offers;
    const price = b.cash - a.cash;
    const local = b.local - a.local;
    text = 'Return B compared with A: ' + money.format(price) + ' cash difference and ' +
      money.format(local) + ' difference in documented ' + network.domestic + ' value. ';
    if (local > 0) text += money.format(price / local) + ' cash difference per extra dollar of documented local value.';
    else text += 'B offers no additional documented local value in dollars.';
  }
  byId('comparison').textContent = text;
}

function selectArticle() {
  if (current) drafts.set(current.revision, forms.map(values));
  network = railwayEnquiries[byId('railway').value];
  current = network.lots[Number(byId('article').value)];
  byId('scope').textContent = current.scope;
  byId('witness').textContent = current.witness;
  byId('quantity').textContent = 'Enquiry quantity: one. ' + (current.network_quantity == null ?
    'Agree repeat quantities from the surveyed design and lot boundaries.' :
    'Planning quantity across the railway: ' + current.network_quantity.toLocaleString('en-US') + '.');
  byId('revision').textContent = 'Package revision ' + current.revision;
  byId('records').replaceChildren(...Object.keys(current.records).map(path => {
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.href = '../../../' + path;
    link.textContent = path;
    item.append(link);
    return item;
  }));
  forms.forEach((form, i) => {
    form.querySelector('.domestic span').textContent = 'Documented ' + network.domestic + ' value (USD)';
    restore(form, drafts.get(current.revision)?.[i]);
    form.querySelector('.message').textContent = '';
  });
  compare();
}

function selectRailway() {
  const lots = railwayEnquiries[byId('railway').value].lots;
  byId('article').replaceChildren(...lots.map((lot, i) => new Option(lot.name, i)));
  selectArticle();
}

for (const label of ['A', 'B']) {
  const form = byId('offer').content.firstElementChild.cloneNode(true);
  form.querySelector('h3').textContent = 'Return ' + label;
  const local = document.createElement('input');
  local.name = 'local'; local.type = 'number'; local.min = '0'; local.step = 'any';
  form.querySelector('.domestic').append(document.createElement('span'), local);
  form.addEventListener('input', compare);
  form.querySelector('.save').onclick = () => {
    const record = {schema: 'osr-article-return/1', revision: current.revision, railway: network.name,
      article: current.name, basis: network.basis, return: values(form)};
    download('railway-return-' + current.revision.slice(0, 10) + '-' + label + '.json',
      JSON.stringify(record, null, 2), 'application/json');
  };
  form.querySelector('.load').onchange = async event => {
    const file = event.target.files[0];
    if (!file) return;
    const revision = current.revision;
    try {
      if (file.size > 1024 * 1024) throw Error('Select a return file under 1 MB.');
      const record = JSON.parse(await file.text());
      if (record.schema !== 'osr-article-return/1' || record.revision !== current.revision ||
          revision !== current.revision || record.railway !== network.name || record.article !== current.name ||
          !record.basis || Object.keys(record.basis).length !== Object.keys(network.basis).length ||
          !Object.entries(network.basis).every(([key, value]) => record.basis[key] === value) ||
          !record.return || !fields.every(key =>
            typeof record.return[key] === (key === 'matched' ? 'boolean' : 'string'))) {
        throw Error('Select a saved return for this railway, article and revision.');
      }
      restore(form, record.return);
      // A signed match is a judgement by the reviewing buyer. Reconfirm an imported return.
      form.querySelector('[name="matched"]').checked = false;
      form.querySelector('.message').textContent = 'Return opened. Review the evidence and confirm the match.';
      compare();
    } catch (error) {
      form.querySelector('.message').textContent = error instanceof SyntaxError ? 'Select a valid JSON return.' : error.message;
    }
    event.target.value = '';
  };
  byId('offers').append(form);
  forms.push(form);
}

for (const [id, rail] of Object.entries(railwayEnquiries)) byId('railway').add(new Option(rail.name, id));
byId('railway').onchange = selectRailway;
byId('article').onchange = selectArticle;
byId('print').onclick = () => window.print();
byId('enquiry').onclick = () => {
  const lines = [
    '# Supplier enquiry · ' + network.name + ' · ' + current.name, '', 'Package revision ' + current.revision,
    ...Object.entries(network.basis).map(([key, value]) => key + ': ' + value),
    '', '## Article and acceptance evidence', '', current.scope, current.witness, byId('quantity').textContent,
    '', '## Drawing and data schedule', '',
    ...Object.entries(current.records).map(([path, hash]) => '- ' + path + ' · SHA-256 ' + hash),
    '', '## Bidder return', '', 'Supplier, return date, validity, facility and accountable integration lead:',
    'First article delivered cash price (constant 2026 USD, ex-tax), manufacturing, QA, packing, freight, installation, tooling and buyer-retained costs separately:',
    'Repeat-unit price, order quantity, lead time, production rate, shop hours by trade and shared plant included in rates:',
    'Verified domestic value, documented imports and untraced value reconciling to the same first-article price. Attach tier invoices and origin evidence:',
    'Site assumptions, exclusions, interfaces, qualification holds, inspection witnesses and departures from the issued drawings:',
    'Warranty, spare parts, maintenance prices, repair and software rights, tooling ownership, training and independent repeat-build milestone:',
    'Optional financed offer alongside cash price, with currency, draw dates, fees, interest, grace, security and guarantees:',
    'Buyer scope review, evidence references and disposition:', ''
  ];
  download('railway-enquiry-' + current.revision.slice(0, 10) + '.md', lines.join('\n'), 'text/markdown');
};
selectRailway();
