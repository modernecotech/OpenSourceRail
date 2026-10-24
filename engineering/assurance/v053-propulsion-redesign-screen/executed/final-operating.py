"""Bounded40C coefficients for the final corner geometry; no whole-design pass."""
from pathlib import Path
from hashlib import sha256
import json
import run as r
if __name__=='__main__':
 result=json.loads((r.OUT/'results.json').read_bytes());assert result['source_sha256']==r.SOURCE==r.m.sources()
 fine=next(x for x in result['rows'] if x['id']=='resolved8mm-256-40')
 row=r.batch([dict(id='resolved8mm-128-40',changes=fine['changes'],temperature_c=40.,nx=128,depth_cells=32,margin_periods=.5)])[0];result['rows'].append(row)
 related=[x for x in result['rows'] if x['hypothesis_sha256']==fine['hypothesis_sha256']]
 study=r.operating(fine,related)
 study['geometry_eligible_over_applicable_sampled_coupons_only']=study.pop('geometry_eligible_over_all_retained_sampled_coupons')
 study['full_temperature_range_accepted']=False
 study['independent_grid_peak_convergence_established']=False
 study['no_canonical_or_whole_system_adoption']=True
 study['scope']+=' Operating samples are conditional40C undamaged-field quantities only; cold/warm coupons pass sampled checks but localpeak convergence, full0–80C range,3D field/material test and propulsion/lift/structural/system integration remain open. No unqualified operatingcapacity is promoted.'
 result['resolved_corner_operating']=study;result['resolved_corner_alternative']['all_sampled_material_current_screens_pass']=all(x.get('material_current_screen_pass') for x in related)
 result['historical_operating_estimates_superseded']=['results-prior192.json: 1mmchamfer operatingvaluesinvalidatedbyselected-256x48-cold']
 assert r.SOURCE==r.m.sources();r.write('results.json',result)
 files={p.relative_to(r.OUT).as_posix():sha256(p.read_bytes()).hexdigest() for p in r.OUT.rglob('*') if p.is_file() and p.suffix!='.log' and p.name!='manifest.json' and '__pycache__' not in p.parts}
 r.write('manifest.json',dict(schema='osr-ignored-propulsion-redesign-receipt/1',source_sha256=r.SOURCE,runner_sha256=sha256((r.OUT/'run.py').read_bytes()).hexdigest(),final_runner_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),files_sha256=files,production_sources_unchanged=True,**r.FLAGS))
 print('COMPLETE',len(result['rows']),'validconditional40Csamples',sum(x['map_valid_for_this_sample'] for x in study['operating_samples']),flush=True)
