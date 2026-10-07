#!/usr/bin/env python3
"""Reclassify and reprice the same controlled alignment using native local geometry."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('capex_refresh',ROOT/'tools/automation/recalculate-city-capex.py')
capex=importlib.util.module_from_spec(spec);spec.loader.exec_module(capex)


def refresh(path,report_only=False):
    original=path.read_bytes();design=tomllib.loads(original.decode());slug=design['city']['slug']
    with tempfile.TemporaryDirectory(prefix='osr-local-civil-') as folder:
        output=Path(folder)/'civil.json'
        subprocess.run([str(ROOT/'target/release/osr-design'),'--slug',slug,
            '--sidecar',str(ROOT/f'.cache/osr-pipeline/rasters/{slug}.grid.json'),
            '--out-dir',str(path.parent),'--civil-register-out',str(output)],
            cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        native=json.loads(output.read_text())
        for relative,compiled in native['compiled_sources'].items():
            if (ROOT/relative).read_bytes()!=compiled.encode():
                raise ValueError('Native civil generator build is stale: '+relative)
        rows=native['segments']
    def length_by_class(rows):
        result={}
        for r in rows:
            key=(r['line'],r['class']);result[key]=result.get(key,0.)+r['to_station_m']-r['from_station_m']
        return result
    blocks=[]
    omitted_empty_intervals=0
    for row in rows:
        # Canonical registers use millimetre precision. Native endpoint
        # subtraction can leave a submillimetre interval which rounds to
        # exactly zero; it contributes no length or cost at that precision.
        if round(row['from_station_m'],3)==round(row['to_station_m'],3):
            omitted_empty_intervals+=1
            continue
        block=['[[civil_segments]]']
        for key,value in row.items():
            if value is None:continue
            block.append(f'{key} = '+(json.dumps(value) if isinstance(value,str) else f'{value:.3f}'))
        blocks.append('\n'.join(block)+'\n\n')
    text=original.decode();matches=list(re.finditer(r'^\[\[civil_segments\]\]\n.*?(?=^\[|\Z)',text,re.M|re.S))
    if not matches:raise ValueError('No civil register: '+slug)
    # Refuse non-contiguous edits so unrelated controlled data cannot be removed.
    if any(a.end()!=b.start() for a,b in zip(matches,matches[1:])):raise ValueError('Noncontiguous civil register')
    updated=text[:matches[0].start()]+''.join(blocks)+text[matches[-1].end():]
    revised=tomllib.loads(updated)
    before=length_by_class(design['civil_segments']);after=length_by_class(revised['civil_segments'])
    if before.keys()!=after.keys() or any(abs(before[k]-after[k])>.2 for k in before):
        raise ValueError('Controlled civil class length changed: '+slug)
    for line in revised['lines']:
        parts=[r for r in revised['civil_segments'] if r['line']==line['name']]
        if not parts or abs(parts[-1]['to_station_m']-line['length_m'])>.0001:
            raise ValueError('Civil endpoint differs from controlled line: '+slug+': '+line['name'])
        if any(abs(a['to_station_m']-b['from_station_m'])>.0001 for a,b in zip(parts,parts[1:])):
            raise ValueError('Civil register has a gap: '+slug)
    old_control={k:v for k,v in design.items() if k not in {'civil_segments','costs'}}
    new_control={k:v for k,v in revised.items() if k not in {'civil_segments','costs'}}
    if old_control!=new_control:raise ValueError('Noncivil controlled data changed: '+slug)
    if report_only:
        if revised['civil_segments']!=design['civil_segments']:
            raise ValueError('Native civil register differs; controlled reclassification required: '+slug)
        # Recompute capital in an isolated copy and reject an actual budget
        # change. This refresh is proof of the unchanged design, not a retag.
        with tempfile.TemporaryDirectory(prefix='osr-civil-budget-check-') as folder:
            candidate=Path(folder)/'design.toml';candidate.write_bytes(original)
            (Path(folder)/(slug+'.toml')).write_bytes((path.parent/(slug+'.toml')).read_bytes())
            capex.recalculate(candidate)
            recalculated=tomllib.loads(candidate.read_text())
            if recalculated['costs']!=design['costs']:
                raise ValueError('Civil budget changed; controlled regeneration required: '+slug)
        final=design
    else:
        path.write_text(updated);capex.recalculate(path)
        final=tomllib.loads(path.read_text())
    quality=path.parent/(slug+'.design-quality.yaml')
    if quality.is_file() and not report_only:
        content=quality.read_text()
        quantities={key:sum(r['to_station_m']-r['from_station_m'] for r in final['civil_segments'] if r['class']==key) for key in ('at-grade','elevated','bridge')}
        products={key:sum(r['to_station_m']-r['from_station_m'] for r in final['civil_segments'] if r.get('viaduct_product') in names) for key,names in {
            'osr_pi20_pi25':('OSR-Pi20','OSR-Pi25'),'osr_us':('OSR-US',),'special':('OSR-SP',),'realign':('REALIGN-OR-SPECIAL',)}.items()}
        values={'at_grade':quantities['at-grade'],'elevated':quantities['elevated'],'bridge':quantities['bridge'],**products,
            'max_elevated_cost_multiplier':max((r.get('elevated_cost_multiplier',1.) for r in final['civil_segments']),default=1.)}
        for key,value in values.items():
            content=re.sub(r'(?m)^(\s*'+key+r':\s*)[^\n]+$',lambda m:m[1]+f'{value:.3f}',content)
        quality.write_text(content)
    receipt=dict(schema='local-civil-cost-refresh/1',city=slug,
        design_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        native_generator_sha256=hashlib.sha256((ROOT/'target/release/osr-design').read_bytes()).hexdigest(),
        native_compiled_sources_verified=True,
        omitted_zero_length_intervals_at_mm_precision=omitted_empty_intervals,
        previous_design_sha256=hashlib.sha256(original).hexdigest(),
        previous_capital_allowance_usd=design['costs']['total_usd'],
        current_base_capital_allowance_usd=final['costs']['total_usd'],
        route_station_fleet_data_preserved=True,civil_class_lengths_preserved=True,
        search_penalties_are_monetary=False,complete_installed_budget=False,
        special_structure_increment_usd=None,unpriced_scope=['local special/segmental structure increments',
            'actual foundations','transport and erection qualification','land/rights/utilities',
            'charging/grid installation upgrades','tax/duty/escalation/risk'],
        sources_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
            'crates/osr-routing/src/civil.rs','crates/osr-design/src/main.rs','crates/osr-design/src/emit.rs',
            'tools/automation/refresh-local-civil-costs.py','tools/automation/recalculate-city-capex.py',
            'lib/templates/civil-cost-model.toml')})
    dest=path.parent/'engineering/local-civil-costs';dest.mkdir(exist_ok=True,parents=True)
    existing=dest/'summary.json'
    if existing.is_file():
        previous=json.loads(existing.read_text())
        for key in ('previous_design_sha256','previous_capital_allowance_usd'):
            receipt[key]=previous[key]
    (dest/'summary.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(slug, f"base allowance {receipt['current_base_capital_allowance_usd']/1e9:.3f}bn; installed total unresolved",flush=True)
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--city');p.add_argument('--jobs',type=int,default=2)
    p.add_argument('--report-only',action='store_true',help='verify native civil/register budget in an isolated copy; preserve canonical design')
    args=p.parse_args();paths=[p for p in sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml'))
        if not args.city or tomllib.loads(p.read_text())['city']['slug'] in args.city.split(',')]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:list(pool.map(lambda path:refresh(path,args.report_only),paths))
if __name__=='__main__':main()
