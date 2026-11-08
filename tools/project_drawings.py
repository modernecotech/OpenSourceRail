#!/usr/bin/env python3
"""Generate source-bound controlled research SVGs; no native CAD or business writes."""
import argparse
import gzip
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from engineering.railway_project import drawings
from engineering.station_rail.common import encoded


def load(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>64*1024**2:
        raise ValueError('Bounded ordinary sealed input required')
    if path.suffix=='.gz':
        with gzip.open(path,'rb') as stream:raw=stream.read(64*1024**2+1)
    else:raw=path.read_bytes()
    if len(raw)>64*1024**2:raise ValueError('Input exceeds decompressed byte budget')
    def pairs(rows):
        result={}
        for k,v in rows:
            if k in result:raise ValueError('Duplicate input JSON key')
            result[k]=v
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Finite input values required')))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['describe','export']);p.add_argument('--body',type=Path,required=True);p.add_argument('--proposal',type=Path,required=True)
    p.add_argument('--part',action='append',required=True,help='Exact part ID; at most twelve types');p.add_argument('--declarations',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();body=load(a.body);proposal=load(a.proposal)
    if a.action=='describe':
        value=drawings.describe(body,proposal,a.part)
        if a.output.exists() or any(x.is_symlink() for x in (a.output,*a.output.parents)):raise ValueError('Fresh ordinary scope output required')
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(encoded(value));print(json.dumps(dict(scope_file=str(a.output),selected_types=len(value['selected']))))
    else:
        if not a.declarations:p.error('export requires explicit --declarations from the describe geometry IDs')
        m=drawings.export(body,proposal,a.output,a.part,load(a.declarations));print(json.dumps(dict(manifest_id=m['manifest_id'],documented_part_ids=m['coverage']['documented_part_ids'],whole_vehicle_finished_drawing_coverage_complete=False)))


if __name__=='__main__':main()
