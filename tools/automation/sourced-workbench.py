#!/usr/bin/env python3
"""Bounded read-only presentation over unchanged source-bound research records.

This adapter returns labelled display projections. Original records, hashes and
engineering acceptance are unchanged and remain available in the saved state.
"""
import argparse
from functools import lru_cache
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import gzip
from pathlib import Path
import sys
from urllib.parse import urlsplit,parse_qs

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from engineering.sourced_case import workbench as frozen
from engineering.sourced_case import FLAGS,identity

LABEL='Bounded display projection of saved source records; raw evidence remains offline. No engineering or operating approval.'
PAGE=frozen.PAGE.replace('</h1>','</h1><p><small>'+LABEL+'</small></p>',1)
# Keep chart labels outside the data and separate the position scale and legend.
PAGE=PAGE.replace('height="280"','height="325"').replace('clearRect(0,0,1100,280)','clearRect(0,0,1100,325)')
PAGE=PAGE.replace("c.fillText('m/s',8,42)","c.fillText('m/s',8,20)").replace("c.fillText('Position (m)',930,270)","c.fillText('Position (m)',930,318)")
PAGE=PAGE.replace('journeys.forEach((j,i)=>',"for(let n=0;n<=5;n++){c.fillStyle='#17303c';c.fillText(Math.round(n*selected.distance_m/5),40+n*200,260)}journeys.forEach((j,i)=>")
PAGE=PAGE.replace('258+Math.floor(i/5)*17','282+Math.floor(i/5)*17')
ARRAY_LIMIT=30
TRAJECTORY_LIMIT=1000
ROUTING_LIMIT=20
MAX_CLOSURE_BYTES=64*1024**2


def _sample(values,limit):
    if len(values)<=limit:return values[:]
    if limit==1:return values[:1]
    return [values[(i*(len(values)-1))//(limit-1)] for i in range(limit)]


def bounded(value,*,limit=ARRAY_LIMIT,depth=0):
    """Preserve scalar values and source points; expose original array counts."""
    if depth>=12 and isinstance(value,(dict,list)):
        return dict(display_projection='Nested source details omitted',original_count=len(value))
    if isinstance(value,list):return [bounded(v,limit=limit,depth=depth+1) for v in _sample(value,limit)]
    if isinstance(value,dict):
        result={}
        for key,item in list(value.items())[:200]:
            if key=='ERPNext_drafts':
                result['ERPNext_drafts_display']='Use manufacturing draft-status/count projection; raw drafts remain offline';continue
            result[key]=bounded(item,limit=limit,depth=depth+1)
            if isinstance(item,list):
                result[key+'_original_count']=len(item);result[key+'_display_count']=min(len(item),limit)
                result[key+'_display_sampling']='all source entries' if len(item)<=limit else 'deterministic source entries including endpoints'
            elif isinstance(item,str) and len(item)>4000:result[key+'_original_characters']=len(item)
        if len(value)>200:result['dictionary_original_key_count']=len(value);result['dictionary_display_key_count']=200
        return result
    if isinstance(value,str):return value if len(value)<=4000 else value[:4000]+' [display excerpt]'
    return value


def manufacturing_view(value):
    """Whitelist counts/status and twenty source routing groups before JSON."""
    routes=value.get('routings');draft=value.get('ERPNext_drafts')
    routes=routes if isinstance(routes,list) else None;draft=draft if isinstance(draft,dict) else {}
    keys=('schema','candidate_id','body_candidate_id','evaluation_id','net_counted_vehicle_stock_kg',
      'dimensioned_vehicle_blank_kg','removed_or_offcut_vehicle_stock_kg','known_vehicle_stock_process_cost_usd',
      'known_vehicle_labour_h','conditional_vehicle_labour_days','purchased_occurrences','purchased_module_processes_unknown',
      'complete_installed_cost_usd','tooling_cost_usd','whole_life_cost_usd','unknown_whole_life_scopes')
    result={key:bounded(value[key]) for key in keys if key in value}
    result.update(presentation_projection=LABEL,routing_groups_total=None if routes is None else len(routes),
      routing_groups_displayed=None if routes is None else min(ROUTING_LIMIT,len(routes)),
      routed_occurrences_total=None if routes is None else sum(r['quantity'] for r in routes),
      routing_groups=[] if routes is None else [bounded(r) for r in routes[:ROUTING_LIMIT]],
      civil_construction_slots_total=len(value['civil_construction_slots']) if isinstance(value.get('civil_construction_slots'),list) else None,
      unpriced_part_definitions_total=len(value['unpriced_part_ids']) if isinstance(value.get('unpriced_part_ids'),list) else None)
    statuskeys=('schema','candidate_id','export_id','submission_allowed','docstatus','items_disabled','active_BOMs',
       'external_transactions_performed','quantity_reconciliation','export_scope','field_mapping_and_permissions_review')
    status={key:bounded(draft[key]) for key in statuskeys if key in draft}
    for key in ('item_drafts','assembly_item_drafts','BOM_drafts','operation_drafts','routing_drafts','workstation_drafts',
                'rfq_drafts','production_orders','active_assets'):
        status[key+'_count']=len(draft[key]) if isinstance(draft.get(key),list) else None
    status['full_draft_payload_displayed']=False;result['ERPNext_draft_status']=status
    return result


def journey_view(rows):
    if not isinstance(rows,list):raise ValueError('Actual saved journey list required')
    out=[]
    for row in rows:
        raw=row['result'];result=bounded({k:v for k,v in raw.items() if k not in ('trajectory','electrical_duty','source_sha256')})
        points=raw.get('trajectory')
        if isinstance(points,list):
            fields=('time_s','front_m','speed_m_s','acceleration_m_s2','traction_N','brake_N','active_motor_count')
            result['trajectory']=[{k:p[k] for k in fields if k in p} for p in _sample(points,TRAJECTORY_LIMIT)]
            result['trajectory_display_fields']=list(fields)
            result['trajectory_original_count']=len(points);result['trajectory_display_count']=len(result['trajectory'])
            result['trajectory_display_sampling']='deterministic original points including endpoints; no interpolation'
        else:result['trajectory']=[];result['trajectory_original_count']=None;result['trajectory_display_count']=0
        if 'electrical_duty' in raw:result['electrical_duty']=bounded(raw['electrical_duty'])
        out.append(dict(name=row['name'],result=result))
    return out


def _ordinary(path,max_bytes):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>max_bytes:raise ValueError('Bounded ordinary saved display input required')
    return p


@lru_cache(maxsize=2)
def _read_closure(path,mtime_ns,size,inode,ctime_ns):
    p=_ordinary(path,MAX_CLOSURE_BYTES)
    try:
        opener=gzip.open if p.suffix=='.gz' else open
        with opener(p,'rb') as stream:raw=stream.read(MAX_CLOSURE_BYTES+1)
        if len(raw)>MAX_CLOSURE_BYTES:raise ValueError('Closure decompression budget exceeded')
        value=json.loads(raw)
    except (OSError,EOFError,UnicodeDecodeError,json.JSONDecodeError) as exc:
        raise ValueError('Malformed saved closure input') from exc
    if value.get('schema')!='osr-sourced-engineering-closure-dashboard/1' or value.get('evaluation_id')!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):raise ValueError('Saved closure report identity differs')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Closure display cannot grant release')
    return value


def _closure(report,run_id,candidate_id):
    if report is None:return None
    p=_ordinary(report,MAX_CLOSURE_BYTES);s=p.stat();value=_read_closure(str(p.resolve()),s.st_mtime_ns,s.st_size,s.st_ino,s.st_ctime_ns)
    if value.get('run_id')!=run_id:raise ValueError('Saved closure report belongs to another run')
    keys=('schema','evaluation_id','run_id','source_epoch_current','current_plan_coverage_verified','counts','phases','work_packages',
          'required_test_inputs','design_complete_percentage','limitations')
    result={k:bounded(value[k]) for k in keys if k in value}
    for key in ('journeys','manufacturing_exports'):
        rows=value.get(key,[])
        if isinstance(rows,list):result[key]=bounded([r for r in rows if r.get('candidate_id')==candidate_id])
    result['presentation_projection']=LABEL
    return result


def case_view(state,index,root=ROOT,closure_report=None):
    # The frozen contracts validate exact run/case identities; one saved case is
    # read, never a closure rebuild over the entire campaign.
    run=frozen.index_view(state,root);raw=frozen.case_view(state,index,root)
    row=run['cases'][index]
    if row.get('candidate_id')!=raw['candidate_id']:raise ValueError('Display/run candidate binding differs')
    result={k:bounded(raw[k]) for k in ('candidate_id','body_candidate_id','vehicle_id','variant','distance_m','distributed',
         'ambient_C','drive_configuration','vehicle_summary','partial_public_price','auxiliary_power','charging','conditional_arrivals') if k in raw}
    result['evaluation_id']=row['evaluation_id']
    result['presentation_projection']=dict(label=LABEL,source_evaluation_id=row['evaluation_id'],source_run_id=run['run_id'],
      display_identity_is_source_identity=False,raw_state_available_offline=True,
      limits=dict(routing_groups=ROUTING_LIMIT,nested_array_samples=ARRAY_LIMIT,trajectory_points_per_scenario=TRAJECTORY_LIMIT))
    result['manufacturing']=manufacturing_view(raw['manufacturing'])
    result['journeys']=journey_view(raw['journeys'])
    result['closure']=bounded(raw['closure'])
    saved=_closure(closure_report,run['run_id'],raw['candidate_id'])
    if saved is not None:result['closure']['saved_report_projection']=saved
    else:result['closure']['saved_report_projection']=None
    result.update(FLAGS)
    return result


def part_view(state,index,search='',root=ROOT):
    value=frozen.part_view(state,index,search,root)
    value=bounded(value,limit=30);value['presentation_projection']=LABEL
    return value


def handler(state,root=ROOT,closure_report=None):
    class ReadOnly(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            try:
                path=urlsplit(self.path)
                if len(self.path)>4096:raise ValueError('Bounded local query required')
                if path.path=='/' and not path.query:raw=PAGE.encode();kind='text/html; charset=utf-8'
                elif path.path=='/api/index' and not path.query:
                    value=frozen.index_view(state,root)
                    raw=json.dumps(value,allow_nan=False).encode();kind='application/json'
                elif path.path=='/api/case':
                    q=parse_qs(path.query,keep_blank_values=True)
                    if set(q)!={'index'} or len(q['index'])!=1:raise ValueError('One index required')
                    value=case_view(state,int(q['index'][0]),root,closure_report)
                    raw=json.dumps(value,allow_nan=False).encode();kind='application/json'
                elif path.path=='/api/parts':
                    q=parse_qs(path.query,keep_blank_values=True)
                    if set(q)!={'index','search'} or any(len(v)!=1 for v in q.values()):raise ValueError('One index andsearch required')
                    value=part_view(state,int(q['index'][0]),q['search'][0],root)
                    raw=json.dumps(value,allow_nan=False).encode();kind='application/json'
                else:self.send_error(404);return
                self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)))
                self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
                self.end_headers();self.wfile.write(raw)
            except (ValueError,KeyError,TypeError,OSError):self.send_error(400,'Saved evidence unavailable or invalid')
        def readonly(self):self.send_error(405,'Read-only saved evidence explorer')
        do_POST=do_PUT=do_PATCH=do_DELETE=readonly
    return ReadOnly


def serve(state,port=8772,root=ROOT,closure_report=None):
    if type(port) is not int or not 1<=port<=65535:raise ValueError('Valid local port required')
    p=Path(state)
    if p.is_symlink() or not p.is_dir():raise ValueError('Ordinary saved state directory required')
    frozen.index_view(state,root)
    print('Read-only bounded sourced design explorer: http://127.0.0.1:'+str(port),flush=True)
    ThreadingHTTPServer(('127.0.0.1',port),handler(state,root,closure_report)).serve_forever()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('serve',));parser.add_argument('--state',default=Path('build/sourced-cell'),type=Path)
    parser.add_argument('--port',type=int,default=8772);parser.add_argument('--closure-report',type=Path)
    a=parser.parse_args(argv);serve(a.state,a.port,closure_report=a.closure_report)


if __name__=='__main__':main()
