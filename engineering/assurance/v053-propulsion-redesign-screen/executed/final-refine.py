"""One selected refinement; preserve earlier result, never promote a design."""
from pathlib import Path
from hashlib import sha256
import json,time
import run as r

if __name__=='__main__':
 start=time.monotonic();result=json.loads((r.OUT/'results.json').read_bytes())
 assert result['source_sha256']==r.m.sources()==r.SOURCE
 r.write('results-prior-final-refine.json',result)
 selected=next(x for x in result['rows'] if x['id']=='selected-192-40')
 jobs=[dict(id='selected-256x48-'+tag,changes=selected['changes'],temperature_c=T,nx=256,depth_cells=48,margin_periods=.5) for tag,T in [('cold',0.),('40',40.)]]
 result['rows']+=r.batch(jobs)
 related=[x for x in result['rows'] if x['hypothesis_sha256']==selected['hypothesis_sha256'] and not x['id'].startswith('selected-256-')]
 if all(x.get('state')=='executed' and x.get('coupon_numerically_valid') for x in related):
  result['operating']=r.operating(next(x for x in related if x['id']=='selected-256x48-40'),related)
 else:
  result['operating']=None
 result['refinement_elapsed_host_s']=time.monotonic()-start
 result['limitations'].append('Refined local demagnetisation peaks, not only fundamental field, determine eligibility; a failed finer coupon invalidates older operating estimates retained only in results-prior192.json.')
 assert r.SOURCE==r.m.sources()
 r.write('results.json',result)
 files={p.relative_to(r.OUT).as_posix():sha256(p.read_bytes()).hexdigest() for p in r.OUT.rglob('*') if p.is_file() and p.name not in ('manifest.json','run.log','refine.log','final-refine.log') and '__pycache__' not in p.parts}
 r.write('manifest.json',dict(schema='osr-ignored-propulsion-redesign-receipt/1',source_sha256=r.SOURCE,runner_sha256=sha256((r.OUT/'run.py').read_bytes()).hexdigest(),refinement_runner_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),files_sha256=files,production_sources_unchanged=True,**r.FLAGS))
 print('COMPLETE',len(result['rows']),'coupons','elapsed',time.monotonic()-start,'eligible',result['operating'] and result['operating']['geometry_eligible_over_all_retained_sampled_coupons'],flush=True)
