// These are exported ERP observations, never permission to mutate native records.
export function selectExecutionReviews(snapshot, asset, impact) {
  if (!snapshot || snapshot.city !== asset.city || snapshot.project !== asset.erp_project) return [];
  const change = impact?.equipment_changes?.find(row => row.asset_id === asset.asset_id);
  const types = new Set([asset.component_type_id, ...(asset.manufacturing_method?.product_ids || []),
    ...(asset.manufacturing_method?.tooling_ids || []), ...(change?.dependencies?.component_type_ids || []),
    ...(change?.dependencies?.manufacturing_product_ids || []), ...(change?.dependencies?.manufacturing_tooling_ids || [])].filter(Boolean));
  const revisions = new Set([asset.engineering_revision, ...(change ? [impact.baseline_engineering_revision,
    impact.proposed_engineering_revision] : [])].filter(Boolean));
  return (snapshot.execution?.revision_reviews || []).filter(review =>
    review.scope?.city === asset.city && review.scope?.project === asset.erp_project &&
    review.scope?.company === snapshot.company && types.has(review.mapping?.component_type_id) &&
    revisions.has(review.mapping?.engineering_revision));
}

export function renderExecutionReviews({target, snapshot, asset, impact, erp, esc}) {
  const reviews = selectExecutionReviews(snapshot, asset, impact);
  const opened = new Set([...target.querySelectorAll('details[open]')].map(node => node.dataset.review));
  target.replaceChildren();
  if (!reviews.length) {
    target.textContent = 'No revision-bound ERP exposure snapshot is available for this equipment. Review its component mapping and ERP visibility; absence does not establish no impact.';
    return;
  }
  const link = (kind, name) => `<a href="${esc(erp)}/app/${kind}/${encodeURIComponent(name)}" target="_blank" rel="noopener">${esc(name)}</a>`;
  const info = document.createElement('p');
  info.textContent = `ERP observation: ${snapshot.observed_at || 'timestamp unavailable'}. Refresh the ERP snapshot after business changes; this is not a live inventory count.`;
  target.append(info);
  for (const review of reviews) {
    const details = document.createElement('details');
    details.dataset.review = review.sha256;
    details.open = opened.has(review.sha256);
    const summary = document.createElement('summary');
    summary.textContent = `${review.mapping.component_type_id} · ${review.mapping.engineering_revision} · ${review.purchase_orders.length} purchase lines · ${review.work_orders.length} Work Orders · ${review.stock_movements.length} stock movements`;
    const body = document.createElement('div');
    body.innerHTML = `<p>Reviewed Item ${esc(review.mapping.erp_item_code)} · BOM ${esc(review.mapping.production_bom || 'unmapped')}<br>Snapshot checksum <code>${esc(review.sha256)}</code></p>` +
      review.warnings.map(w => `<p class="bad">${esc(w)}</p>`).join('') +
      `<h4>Potential purchase exposure</h4>` + (review.purchase_orders.map(r => `<div class="record">${link('purchase-order', r.document)} · ${esc(r.item)} · ${esc(r.status)} · ${esc(r.unreceived_qty)} ${esc(r.uom)} unreceived · ${r.actionable ? 'review open commitment' : 'historical record'}<br>Line ${esc(r.line)} · revision allocation unproven</div>`).join('') || '<p>No matching purchase lines visible.</p>') +
      `<h4>Exact Item/BOM production matches</h4>` + (review.work_orders.map(r => `<div class="record">${link('work-order', r.name)} · ${esc(r.item)} · ${esc(r.bom)} · ${esc(r.status)}<br>${esc(r.produced_qty)} produced / ${esc(r.planned_qty)} ${esc(r.uom)} planned · ${r.actionable ? 'review unfinished production' : 'historical record'}</div>`).join('') || '<p>No matching Work Orders visible.</p>') +
      `<h4>Linked material movements</h4>` + (review.stock_movements.map(r => `<div class="record">${link('stock-entry', r.name)} · ${esc(r.purpose)} · ${esc(r.work_order)}<br>${r.lines.map(l => `${esc(l.item)}: ${esc(l.qty)} ${esc(l.uom)} · ${esc(l.source_warehouse || 'external')} → ${esc(l.target_warehouse || 'consumed')}`).join('<br>')}</div>`).join('') || '<p>No linked submitted stock movements visible.</p>') +
      review.limitations.map(w => `<p class="muted">${esc(w)}</p>`).join('');
    const dispositions=(snapshot.execution.dispositions || []).filter(row=>row.mapping===review.mapping.name &&
      row.city===asset.city && row.project===asset.erp_project && row.company===snapshot.company);
    body.innerHTML += '<h4>Recorded disposition plans</h4>' + (dispositions.map(row=>
      `<div class="record">${link('osr-revision-disposition',row.name)} · ${esc(row.proposal.action)} · ${esc(row.proposal.target.document)}<br>${esc(row.responsible)} · due ${esc(row.due_date)}<br>${esc(row.decision?.outcome || 'Awaiting independent review')} · ${row.current?'Exposure current':'Exposure changed or unavailable'} · execution unverified</div>`).join('') || '<p>No disposition plans visible.</p>') +
      `<p>${link('project',asset.erp_project)} → OpenSourceRail → Revision dispositions to propose or review a plan using your native ERP account.</p>`;
    details.append(summary, body); target.append(details);
  }
  const download = document.createElement('button');
  download.type = 'button'; download.textContent = 'Download revision exposure';
  download.onclick = () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify({schema:'osr-asset-execution-exposure/1',
      city:asset.city, asset_id:asset.asset_id, observed_at:snapshot.observed_at, reviews}, null, 2)], {type:'application/json'}));
    const anchor = document.createElement('a'); anchor.href = url;
    anchor.download = 'osr-revision-exposure.json'; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  target.append(download);
}
