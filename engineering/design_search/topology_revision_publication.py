"""Portable archival verification of explicit topology revisions; no FE dispatch.

Recorded tools remain original evidence. Current producer bytes and algebraic
quantities/costs must reproduce, while new numerical worker reuse stays strict.
The authenticated parent is the published packet, never its old absolute path.
"""
import argparse
from copy import deepcopy
from html import escape
import json
from math import isfinite
from pathlib import Path
import shutil
import tempfile

import numpy as np

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,encoded,identity
from . import civil_topology as parent, civil_topology_publication as previous
from . import topology_revision_campaign as campaign, topology_revisions as revisions
from . import topology_geometry as geometry, topology_cost, topology_system_cost, quality_diversity

PRODUCER='engineering/design_search/topology_revision_publication.py'
OUTPUT='docs/design-engine/civil-topology-revisions'
FLAGS=campaign.FLAGS


def sources(root=ROOT,configured=None):
    root=Path(root)
    context=None if configured is None else configured['parent_plan']['load_context']
    return dict(sorted({**parent.sources(root,context),**{name:digest(root/name) for name in
        (PRODUCER,campaign.PRODUCER,revisions.PRODUCER,previous.PRODUCER,
         'engineering/design_search/quality_diversity.py',parent.OUTPUT+'/manifest.json')}}.items()))


def _payload(folder):return previous._payload(folder)


def _ordinary_tree(folder):
    folder=campaign._ordinary(folder)
    if (not folder.is_dir() or any(p.is_symlink() or not (p.is_file() or p.is_dir()) for p in folder.rglob('*'))):
        raise ValueError('Ordinary unlinked revision publication tree required')
    return folder


def _check(folder):
    folder=_ordinary_tree(folder);record=campaign._read(folder/'manifest.json');parent._sealed(record,'manifest_id')
    if (record.get('schema')!='osr-topology-revision-publication/1' or record['files_sha256']!=_payload(folder)
            or any(record.get(k) is not False for k in FLAGS)):
        raise ValueError('Revision publication payload or disposition differs')
    return record


def _parent_context(root):
    """Authenticate original records once, retaining only bounded ancestry data."""
    folder=Path(root)/parent.OUTPUT;manifest=previous._check(folder)
    if manifest['source_sha256']!=previous.sources(root):raise ValueError('Original topology publication producer epoch differs')
    state=campaign._read(folder/'state.json');configured=state['plan'];parent._sealed(configured,'campaign_id')
    parent._sealed(configured['tool_context'],'tool_context_id')
    current=parent.plan(root)
    if ({k:v for k,v in current.items() if k not in ('campaign_id','tool_context')}
            !={k:v for k,v in configured.items() if k not in ('campaign_id','tool_context')}):
        raise ValueError('Published parent configuration/current source differs')
    expected={t['trial_id'] for t in configured['trials']};done=[a['trial_id'] for a in state['completed']]
    if (state.get('schema')!='osr-civil-topology-state/1' or state['pending_trial_ids']
            or len(done)!=7 or len(set(done))!=7 or set(done)!=expected):
        raise ValueError('Exact seven terminal published parent attempts required')
    if digest(folder/'baseline.json.gz')!=state['baseline']['file_sha256']:raise ValueError('Published parent baseline bytes differ')
    baseline=campaign._read(folder/'baseline.json.gz',True)
    if baseline['baseline_id']!=state['baseline']['baseline_id'] or baseline['load_context']!=configured['load_context']:
        raise ValueError('Published baseline/load identity differs')
    topology_system_cost.validate_baseline(baseline,root,require_current_tools=False)
    records={};trials={t['trial_id']:t for t in configured['trials']}
    for attempt in state['completed']:
        if trials[attempt['trial_id']]['kind']=='full-solid-reference':
            if parent._read_attempt(folder,attempt,configured,state['baseline']) is None:
                raise ValueError('Original reference attempt must be intact')
            continue
        result,mask,rho,passive,metadata=campaign._parent_data(folder,attempt,configured,state['baseline'])
        records[attempt['trial_id']]=(metadata,dict(physical_geometry=result['physical_geometry'],
            representative_poses=result['representative_poses']),mask,rho,passive)
        del result
    if len(records)!=6:raise ValueError('Six original failed optimized parents required')
    binding=dict(path=parent.OUTPUT,manifest_id=manifest['manifest_id'],manifest_sha256=digest(folder/'manifest.json'),
        state_sha256=digest(folder/'state.json'),campaign_id=configured['campaign_id'])
    return state,baseline,records,binding


def _validate_plan(configured,original,records,binding,root):
    parent._sealed(configured,'campaign_id')
    path=configured.get('parent_state_path')
    if not isinstance(path,str) or not Path(path).is_absolute() or '..' in Path(path).parts:
        raise ValueError('Original execution path must remain recorded absolute provenance')
    children=[]
    for key in sorted(records):
        for strategy in revisions.STRATEGIES:
            child=dict(records[key][0],strategy=strategy);campaign._seal(child,'trial_id');children.append(child)
    current_sources=parent.sources(root,original['plan']['load_context'])
    current_sources.update({name:digest(Path(root)/name) for name in (campaign.PRODUCER,revisions.PRODUCER)})
    expected=dict(schema='osr-topology-revision-plan/1',parent_state_path=path,
        parent_state_sha256=binding['state_sha256'],parent_plan=original['plan'],parent_campaign_id=original['plan']['campaign_id'],
        baseline=original['baseline'],source_sha256=dict(sorted(current_sources.items())),tool_context=original['plan']['tool_context'],
        resources=dict(campaign.RESOURCES),proposal_policy=dict(campaign.PROPOSAL_POLICY),children=children,
        parent_count=6,maximum_children=12,SIMP_reexecuted=False,selection_purpose='next-experiment',**FLAGS)
    campaign._seal(expected,'campaign_id')
    if configured!=expected:raise ValueError('Revision plan differs from exact published parent ancestry/current source')


def _numerics(result,spec):
    """Check every recorded residual and two-mesh summary without a new solve."""
    labels=[];policy=spec['replay']
    limits={k:policy[v] for k,v in (
        ('free_residual_relative','relative_linear_residual_tolerance'),
        ('constraint_residual_relative','relative_linear_residual_tolerance'),
        ('relative_force_equilibrium_residual','relative_equilibrium_tolerance'),
        ('relative_moment_equilibrium_residual','relative_equilibrium_tolerance'),
        ('relative_energy_residual','relative_energy_tolerance'))}
    for name in ('coarse_replay','fine_replay'):
        replay=result[name]
        if replay['execution']!='completed':labels.append(None);continue
        labels.append(campaign._labels(replay['cases']))
        for row in replay['cases']:
            for key in (*limits,'compliance_J','strain_energy_J','maximum_absolute_displacement_m','maximum_vertical_displacement_m'):
                value=row[key]
                if type(value) not in (float,int) or not isfinite(value) or value<0:
                    raise ValueError('Finite nonnegative recorded numerical metric required: '+key)
        met=all(row[k]<=limit for row in replay['cases'] for k,limit in limits.items())
        if replay['declared_residual_request_met'] is not met:raise ValueError('Recorded residual gate differs from all 81 cases')
        if replay['maximum_free_residual_relative']!=max(row['free_residual_relative'] for row in replay['cases']):
            raise ValueError('Recorded maximum residual differs')
        if (replay.get('void_stiffness_credited') is not False or replay.get('physical_acceptance_limit_available') is not False
                or replay.get('contact_stiffness_and_load_sharing_qualified') is not False or any(replay.get(k) is not False for k in parent.FLAGS)):
            raise ValueError('Numerical replay cannot assert physical/model qualification')
    changes=None
    if all(labels):
        if labels[0]!=labels[1]:raise ValueError('Two-mesh case identities/order differ')
        if all(result[k]['declared_residual_request_met'] for k in ('coarse_replay','fine_replay')):
            changes=[abs(a['compliance_J']-b['compliance_J'])/max(abs(b['compliance_J']),1e-20)
                for a,b in zip(result['coarse_replay']['cases'],result['fine_replay']['cases'])]
    status=('mesh-unresolved' if changes is None or max(changes)>policy['two_mesh_compliance_change_target']
        else 'two-mesh-comparison-within-declared-target')
    if result['compliance_relative_changes']!=changes or result['numerical_refinement_status']!=status:
        raise ValueError('Two-mesh changes/refinement status do not reproduce')


def _recalculate(result,child,original,mask,rho,passive,configured,baseline,root):
    proposal=revisions.propose(child['parent_input'],original['physical_geometry'],mask,rho,passive,
        strategy=child['strategy'],**configured['proposal_policy'])
    if proposal!=result['proposal']:raise ValueError('Explicit stock revision does not reproduce')
    if result['execution']=='proposal-rejected':
        if proposal['execution']!='proposal-rejected' or result['system_cost'] is not None or result['physical_geometry'] is not None:
            raise ValueError('Rejected proposal cannot carry a physical result')
        return
    spec=configured['parent_plan']['specification'];cs=configured['parent_plan']['cost_specification'];candidate=proposal['proposed_geometry']
    if result['execution']!='completed' or candidate!=result['physical_geometry']:raise ValueError('Revision completion/physical geometry differs')
    geometry.validate(candidate);elastic=spec['elastic_hypotheses']
    quantity=geometry.quantities(candidate,dict(steel=elastic['steel_density_kg_m3'],concrete=elastic['concrete_density_kg_m3']),
        reserves_kg=cs['reserve_mass_kg'],module_length_m=cs['module_length_m'])
    cost=topology_cost.estimate(candidate,quantity,cs,baseline['assumptions'])
    support=parent.support_demands(candidate,quantity,baseline,spec)
    system=topology_system_cost.compare(candidate,quantity,cost,baseline,support,root=root,require_current_tools=False)
    if (quantity!=result['quantities'] or cost!=result['span_cost'] or support!=result['support_demands']
            or previous._system_semantics(system)!=previous._system_semantics(result['system_cost'])
            or result['composition_candidate_id']!=system['candidate_id'] or result['representative_poses']!=original['representative_poses']
            or result['load_context_id']!=baseline['load_context_id']):
        raise ValueError('Revision quantities, costs, support, service or load identities do not reproduce')
    from .model_cost import SCOPES
    if (set(system['cases'])!={'low','base','high'} or any(set(row['scope_totals_iqd'])!=set(SCOPES)
            or any(len(v)!=3 for v in row['scope_totals_iqd'].values()) for row in system['cases'].values())):
        raise ValueError('Three mass x three financial cases and all fourteen scopes required')
    _numerics(result,spec)


def _replay_summary(result,name):
    value=result[name]
    if value['execution']!='completed':return dict(execution=value['execution'],failure_reason=value.get('failure_reason'),residual_request_met=False,case_count=0,maximum_vertical_displacement_m=None)
    return dict(execution='completed',residual_request_met=value['declared_residual_request_met'],case_count=len(value['cases']),
        numerical_validity=value.get('numerical_validity'),
        maximum_vertical_displacement_m=max(r['maximum_vertical_displacement_m'] for r in value['cases']),
        maximum_free_residual_relative=value['maximum_free_residual_relative'],
        maximum_residuals={key:max(r[key] for r in value['cases']) for key in ('free_residual_relative','constraint_residual_relative',
            'relative_force_equilibrium_residual','relative_moment_equilibrium_residual','relative_energy_residual')})


def _displacement_links(path,result,spec):
    """Authenticate summary maxima against preserved arrays, without a solve."""
    with np.load(path,allow_pickle=False) as arrays:
        for name,factor in (('coarse',1),('fine',2)):
            replay=result[name+'_replay']
            if replay['execution']!='completed':continue
            values=arrays[name+'_displacements'];s=spec['search']
            ndof=2*(s['nx']*factor+1)*(s['nz']*factor+1)
            if values.shape!=(ndof,81) or not np.isfinite(values).all():raise ValueError('Complete finite 81-RHS displacement arrays required')
            for index,row in enumerate(replay['cases']):
                if (float(np.max(np.abs(values[:,index])))!=row['maximum_absolute_displacement_m']
                        or float(np.max(np.abs(values[1::2,index])))!=row['maximum_vertical_displacement_m']):
                    raise ValueError('Preserved displacement arrays and numerical summary differ')


def _row(attempt,result,child):
    row=dict(trial_id=attempt['trial_id'],request_id=attempt['request_id'],attempt_id=attempt['attempt_id'],
        execution=attempt['execution'],runtime_seconds=attempt['runtime_seconds'],strategy=child['strategy'],
        parent_trial_id=child['parent_trial_id'],parent_request_id=child['parent_request_id'],parent_evaluation_id=child['parent_evaluation_id'],
        parent_candidate_id=child['parent_candidate_id'],parent_arrays_package_sha256=child['parent_input']['original_arrays_package_sha256'],
        candidate_id=None,evaluation_id=None,proposal_execution=None,refinement_status=None,system_cost=None,
        coarse_replay=None,fine_replay=None,binary_replay_admitted_to_archive=False,
        physical_model_or_material_strength_qualified=False,installed_mass_complete=False,**FLAGS)
    if result is None:return row,None
    proposal=result['proposal'];row.update(evaluation_id=result['evaluation_id'],proposal_execution=proposal['execution'],
        revision_id=proposal['revision_id'],added_cell_ids=proposal['added_cell_ids'],removed_cell_ids=proposal['removed_cell_ids'],
        failure_reason=result.get('failure_reason'))
    if result['execution']!='completed':return row,None
    candidate=result['physical_geometry'];q=result['quantities']['quantities'];coarse=_replay_summary(result,'coarse_replay');fine=_replay_summary(result,'fine_replay')
    valid=(coarse['execution']==fine['execution']=='completed' and coarse['residual_request_met'] and fine['residual_request_met']
        and candidate['web_geometry']['one_finite_edge_component'] is True and candidate['web_geometry']['corner_only_contacts']==0)
    row.update(candidate_id=candidate['candidate_id'],composition_candidate_id=result['composition_candidate_id'],
        quantity_evaluation_id=result['quantities']['evaluation_id'],nominal_stock_mass_kg=q['nominal_mass_kg'],steel_net_mass_kg=q['steel_net_mass_kg'],
        coarse_replay=coarse,fine_replay=fine,compliance_relative_changes=result['compliance_relative_changes'],
        refinement_status=result['numerical_refinement_status'],binary_replay_admitted_to_archive=valid,
        span_installed_cost_iqd={r['case']:r['scoped_installed_iqd'] for r in result['span_cost']['cases']},
        factory_person_hours={r['case']:r['total_factory_person_hours'] for r in result['span_cost']['cases']},
        system_cost=previous._cost_summary(result['system_cost']))
    elite=None
    if valid:
        fraction=q['steel_net_mass_kg']/q['steel_full_stock_envelope_kg']
        elite=dict(candidate_id=candidate['candidate_id'],descriptor=dict(material='steel-concrete',manufacture='cut-plate-and-precast-deck',solid_fraction_band=min(4,int(fraction*5))),
            metrics=dict(nominal_stock_mass_kg=q['nominal_mass_kg'],base_whole_life_npv_iqd=previous._base_npv(result['system_cost']),
                maximum_recorded_vertical_displacement_m=fine['maximum_vertical_displacement_m']))
    return row,elite


def _drawing(index,row,result):
    y=125*index+25;parts=[f'<text x="12" y="{y}" font-size="13">{escape(row["trial_id"][:12]+" "+row["strategy"])}</text>']
    if result is None or result['execution']!='completed':parts.append(f'<text x="12" y="{y+25}" font-size="13">{escape(row["execution"]+" / "+str(row.get("failure_reason") or "no completed binary record"))}</text>')
    else:
        parts.append(f'<rect x="12" y="{y+10}" width="1000" height="9" fill="#9caeb8"/>')
        for a,b,d,e in result['physical_geometry']['web_geometry']['rectangles_xz_m']:
            parts.append(f'<rect x="{12+50*a:.5f}" y="{y+19+50*(-.18-e):.5f}" width="{50*(b-a):.5f}" height="{50*(e-d):.5f}" fill="#297895"/>')
        parts.append(f'<text x="12" y="{y+105}" font-size="12">{escape(row["refinement_status"]+"; physical model and strength unqualified")}</text>')
    return ''.join(parts)


def _reproduce(folder,root):
    original,baseline,parents,binding=_parent_context(root)
    state=campaign._read(Path(folder)/'state.json');configured=state['plan'];_validate_plan(configured,original,parents,binding,root)
    source=sources(root,configured)
    if state.get('schema')!='osr-topology-revision-state/1' or state['baseline']!=configured['baseline'] or digest(Path(folder)/'baseline.json.gz')!=state['baseline']['file_sha256']:
        raise ValueError('Revision copied baseline/state differs')
    done=[a['trial_id'] for a in state['completed']];children={c['trial_id']:c for c in configured['children']}
    if state['pending_trial_ids'] or len(done)!=12 or len(set(done))!=12 or set(done)!=set(children):raise ValueError('All twelve terminal revision attempts required')
    trials=Path(folder)/'trials'
    if not trials.is_dir() or {p.name for p in trials.iterdir()}!=set(done):raise ValueError('Exact child attempt directory coverage required')
    rows=[];elites={};drawings=[]
    for attempt in state['completed']:
        child=children[attempt['trial_id']];result=campaign._read_attempt(folder,attempt,configured)
        if result is not None:
            _,parent_result,mask,rho,passive=parents[child['parent_trial_id']]
            _recalculate(result,child,parent_result,mask,rho,passive,configured,baseline,root)
            if result['execution']=='completed':
                _displacement_links(Path(folder)/'trials'/attempt['trial_id']/'arrays.npz',result,configured['parent_plan']['specification'])
        row,elite=_row(attempt,result,child);rows.append(row);drawings.append(_drawing(len(rows)-1,row,result))
        if elite is not None:
            if elite['candidate_id'] in elites and elite!=elites[elite['candidate_id']]:raise ValueError('Duplicate physical layout has inconsistent archive metrics')
            elites.setdefault(elite['candidate_id'],elite)
        del result
    archive=quality_diversity.archive(list(elites.values()),['nominal_stock_mass_kg','base_whole_life_npv_iqd','maximum_recorded_vertical_displacement_m'],['material','manufacture','solid_fraction_band'])
    value=dict(schema='osr-topology-revision-portfolio/1',campaign_id=configured['campaign_id'],parent_publication=binding,
        baseline_id=baseline['baseline_id'],load_context_id=baseline['load_context_id'],selection_id=baseline['selected']['selection_id'],
        selected_vehicle_candidate_id=baseline['selected']['candidate_id'],vehicle_evaluation_id=baseline['selected']['vehicle_evaluation_id'],
        trial_count=len(rows),unique_realized_candidate_count=len({r['candidate_id'] for r in rows if r['candidate_id']}),
        archive_eligible_candidate_count=len(elites),attempts=rows,archive=archive,integrated_selection=None,
        archive_eligible_attempt_count=sum(r['binary_replay_admitted_to_archive'] for r in rows),
        residual_gate_failed_attempt_count=sum(any(r[name] is not None and r[name]['execution']=='completed'
            and not r[name]['residual_request_met'] for name in ('coarse_replay','fine_replay')) for r in rows),
        mesh_unresolved_attempt_count=sum(r['refinement_status']=='mesh-unresolved' for r in rows),
        ranking_scope='Next-experiment only; unqualified 2D elastic model and conditional Class C same-service costs',
        numerical_reexecuted_by_verifier=False,host_tool_equality_required_for_archival_verification=False,
        physical_model_or_material_strength_qualified=False,**FLAGS)
    campaign._seal(value,'portfolio_id')
    svg='<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Explicit steel-web revisions; unqualified research geometry" viewBox="0 0 1030 '+str(len(rows)*125+15)+'"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" fill="#182b38">'+''.join(drawings)+'</g></svg>\n'
    if sources(root,configured)!=source:raise ValueError('Revision publication producer/parent epoch changed during verification')
    return value,svg,source


def _readme(value):
    lines=['# Explicit physical revisions of steel-web topology experiments','',
        'Twelve bounded children retain or connect the stock of six failed original layouts. Every addition and removal is explicit, with immutable parent and child request, evaluation and physical identities. Original failed attempts remain unchanged in the [parent publication](../civil-topology/README.md). The selected six-car v0.6 railway is unchanged.','',
        f'There are {value["trial_count"]} terminal attempts, {value["unique_realized_candidate_count"]} distinct realized geometries and {value["archive_eligible_candidate_count"]} geometries eligible for the next-experiment archive. Archive eligibility means connected geometry and both declared numerical residual gates; unresolved mesh sensitivity is retained. It is not an engineering pass.','',
        f'{value.get("residual_gate_failed_attempt_count", 0)} attempts fail a declared numerical residual gate; {value.get("mesh_unresolved_attempt_count", 0)} retain unresolved mesh sensitivity. All physical-model and material-strength requirements remain open.','',
        '![Explicit stock revisions](revisions.svg)','','| Child / strategy | Steel stock (kg) | Coarse maximum vertical displacement (mm) | Fine maximum vertical displacement (mm) | Refinement | Physical model / strength |','|---|---:|---:|---:|---|---|']
    for row in value['attempts']:
        def disp(name):
            replay=row[name];v=None if replay is None else replay['maximum_vertical_displacement_m']
            return '—' if v is None else format(v*1000,'.6g')
        mass='—' if row.get('steel_net_mass_kg') is None else format(row['steel_net_mass_kg'],'.6g')
        lines.append('| '+row['trial_id'][:12]+' / '+row['strategy']+' | '+mass+' | '+disp('coarse_replay')+' | '+disp('fine_replay')+' | '+str(row['refinement_status'] or row['execution'])+' | Unqualified |')
    lines+=['','Maximum displacements include all 81 preserved representative cases without caps. They are demands from an unqualified linear elastic plane model, not allowable deflections. Large displacements can invalidate small-displacement assumptions. Both meshes remove void stiffness and retain floating-stock, point-contact and other failures. The three representative train positions do not bound every train position or an actual journey. Equal web sharing, finite mean bearing translations and finite wheel patches remain hypotheses; bearing contact, lateral/torsional response, buckling, fatigue, connections and material strength remain unqualified.','',
        'The SIMP density is original proposal evidence only. These children do not rerun SIMP or credit density as installed stock. A changed union has a new physical identity; subdivision of the same union preserves it. Refinement and evaluation identities remain separate. Failed, timed-out, rejected and unresolved attempts remain in the packet.','',
        'Scoped span prices are separate from whole-system costs. Every completed comparison preserves three vehicle-mass cases, three financial cases and all fourteen Class C scopes against the same six-kilometre, three-station service baseline. Complete ledgers, assumptions, rates, support-gravity calculations and receipts are retained. Production and civil work use two 8-hour shifts; operating hours and eventual two-to-three-shift operations remain distinct scenarios. Provisional gravity sizing does not qualify foundations or installed-mass closure.','',
        'The diversity archive ranks next experiments within material/manufacturing/solid-fraction cells. It grants no integrated selection, physical acceptance, manufacturing release or movement authority. The computational workflow can finish while physical obligations remain open.','',
        'Archival verification authenticates the original recorded tools and published parent artifacts, requires current producer sources, and recomputes proposals, geometry, quantities, support and complete costs. It performs no FE solve and does not require the CI host to possess the recorded binary paths. New worker execution and reuse retain the strict exact-tool contract. Resource receipts describe actual worker limits; no filesystem or network sandbox is claimed.','',
        '```bash','python -m engineering.design_search.topology_revision_publication publish --state build/runtime-civil-topology-revisions-v1','python -m engineering.design_search.topology_revision_publication verify','```','',
        '[Portfolio and every terminal outcome](result.json) · [Source, ancestry and payload manifest](manifest.json)','']
    return '\n'.join(lines)


def publish(folder,*,root=ROOT,output=None):
    root=Path(root).resolve();folder=_ordinary_tree(folder);out=campaign._ordinary(root/OUTPUT if output is None else output)
    if folder==out or folder in out.parents or out in folder.parents:raise ValueError('Publication and numerical state must be disjoint')
    out.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.topology-revisions-',dir=out.parent))
    try:
        for name in ('state.json','baseline.json.gz'):shutil.copyfile(folder/name,stage/name)
        shutil.copytree(folder/'trials',stage/'trials')
        # One complete staged verification/recomputation; no preliminary full
        # state/cost replay and no second copy of all large ledgers in memory.
        value,svg,source=_reproduce(stage,root)
        (stage/'result.json').write_bytes(encoded(value));(stage/'revisions.svg').write_text(svg);(stage/'README.md').write_text(_readme(value))
        manifest=dict(schema='osr-topology-revision-publication/1',portfolio_id=value['portfolio_id'],parent_publication=value['parent_publication'],
            source_sha256=source,files_sha256=_payload(stage),**FLAGS);campaign._seal(manifest,'manifest_id')
        (stage/'manifest.json').write_bytes(encoded(manifest));_check(stage)
        report=_report(manifest,value)
        if out.exists():
            old=_check(out)
            if old==manifest:return report
            backup=root/'build/topology-revision-publication/replaced'/old['manifest_id']
            if backup.exists():raise ValueError('Prior revision publication already retained; inspect replacement')
            backup.parent.mkdir(parents=True,exist_ok=True);out.rename(backup)
        stage.rename(out)
        return report
    finally:
        if stage.exists():shutil.rmtree(stage)


def _report(manifest,value):
    return dict(verified=True,manifest_id=manifest['manifest_id'],portfolio_id=value['portfolio_id'],trial_count=value['trial_count'],
        realized_candidates=value['unique_realized_candidate_count'],archive_eligible_candidates=value['archive_eligible_candidate_count'],
        numerical_reexecuted=False,**FLAGS)


def verify(*,root=ROOT,output=None):
    root=Path(root).resolve();out=root/OUTPUT if output is None else Path(output);manifest=_check(out)
    value,svg,source=_reproduce(out,root)
    if (manifest['source_sha256']!=source or manifest['parent_publication']!=value['parent_publication']
            or manifest['portfolio_id']!=value['portfolio_id'] or campaign._read(out/'result.json')!=value
            or (out/'revisions.svg').read_text()!=svg or (out/'README.md').read_text()!=_readme(value)):
        raise ValueError('Revision source-bound portfolio does not reproduce')
    return _report(manifest,value)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('publish','verify'));parser.add_argument('--state',type=Path)
    args=parser.parse_args(argv)
    if args.action=='publish':
        if args.state is None:raise ValueError('Publish requires immutable --state')
        result=publish(args.state)
    else:result=verify()
    print(json.dumps(result,sort_keys=True,allow_nan=False));return 0


if __name__=='__main__':raise SystemExit(main())
