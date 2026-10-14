// Shared evidence semantics: completed execution never means physical acceptance.
export const evidenceStates = new Set(['draft','running','numerically-verified','physically-correlated','independently-accepted',
  'passed','failed','stale','unknown','not-run','outside-domain','unavailable','budget-exceeded','cancelled']);
export function stateLabel(state) { return evidenceStates.has(state) ? t(state,state.replaceAll('-', ' ')) : t('unknown'); }
export function quantityText(value,unit='') { return value === null || value === undefined ? t('unknown') : `${value} ${unit}`.trim(); }
export function scopeMatches(record,scope) {
  const value=record.identity || record.request?.identity || record;
  return value.city===scope.city && value.environment===scope.environment &&
    (!value.configuration_revision || value.configuration_revision===scope.configuration_revision);
}
export function element(tag,text='',attributes={}) {
  const node=document.createElement(tag);node.textContent=text;
  for(const [key,value]of Object.entries(attributes))node.setAttribute(key,String(value));
  return node;
}
export function evidenceBadge(state) { return element('span',stateLabel(state),{class:`evidence-state state-${evidenceStates.has(state)?state:'unknown'}`}); }
export function table(headers,rows) {
  const node=element('table');const head=element('thead');const row=element('tr');
  for(const header of headers)row.append(element('th',header,{scope:'col'}));head.append(row);node.append(head);
  const body=element('tbody');for(const values of rows){const row=element('tr');for(const value of values){const cell=element('td');cell.append(value instanceof Node?value:String(value));row.append(cell);}body.append(row);}node.append(body);return node;
}
import { translate as t } from '../workbench/i18n.js';
