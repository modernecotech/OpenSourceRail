"""Final one-geometry physical corner alternative; no canonical mutation."""
from pathlib import Path
from hashlib import sha256
import json,time
import run as r

if __name__=='__main__':
 start=time.monotonic();result=json.loads((r.OUT/'results.json').read_bytes());assert result['source_sha256']==r.SOURCE==r.m.sources()
 r.write('results-prior8mm.json',result)
 change=dict(next(x for x in result['rows'] if x['id']=='selected-256x48-cold')['changes']);change['propulsion_flux_shoe.corner_chamfer_m']=.008
 jobs=[dict(id='resolved8mm-'+tag,changes=change,temperature_c=T,nx=nx,depth_cells=d,margin_periods=.5) for tag,T,nx,d in [('128-cold',0.,128,32),('256-cold',0.,256,48),('256-40',40.,256,48)]]
 new=r.batch(jobs);result['rows']+=new
 for row in new:
  if row.get('state')!='executed':continue
  a=r.apply(change);q=a['propulsion_flux_shoe'];width=q['period_m']/4;cham=q['corner_chamfer_m'];nsegments=2*q['length_m']/q['period_m']*2
  area_removed=2*cham**2;volume_removed=area_removed*q['height_m']*nsegments
  row['physical_corner_alternative']=dict(chamfer_m=cham,finest_longitudinal_cells_across_chamfer=cham/row['coupon']['dx_m'],depth_cells_across_chamfer=cham/row['coupon']['dy_m'],
   analytic_removed_pm_volume_m3=volume_removed,analytic_removed_pm_mass_kg=volume_removed*a['materials']['ferrite']['density_kg_m3'],analytic_removed_pm_fraction=area_removed/(width*q['depth_m']),
   pde_removed_cell_fraction=row['coupon']['removed_corner_cell_volume_fraction'],mass_note='Physical4corner45degreechamfers extruded through0.2mheight, exactscalarvolumeonly; revisedCAD/centroid/inertia/retention remainunissued. Sourceboxmassupperboundnotanetassembledmass.')
  r.write('raw/'+row['id']+'.json',row)
 result['resolved_corner_alternative']=dict(hypothesis_sha256=new[0]['hypothesis_sha256'],all_sampled_coupons_executed=all(x['state']=='executed' for x in new),all_sampled_material_current_screens_pass=all(x.get('material_current_screen_pass') for x in new),
  fine_cold_margin_a_m=next(x.get('demag_margin_after_declared_current_bound_a_m') for x in new if x['id']=='resolved8mm-256-cold'),independent_grid_peak_convergence_established=False,canonical_adoption=False,physical_validation=False)
 result['corner_refinement_elapsed_host_s']=time.monotonic()-start
 result['limitations'].append('The8mm physicalcorneralternative isaseparatehypothesis; even4cellsacrosscornerisnotaformalgridconvergenceproof. No failedpointdiscarded andnomaterialdomainextrapolation.')
 assert r.SOURCE==r.m.sources();r.write('results.json',result)
 files={p.relative_to(r.OUT).as_posix():sha256(p.read_bytes()).hexdigest() for p in r.OUT.rglob('*') if p.is_file() and p.suffix!='.log' and p.name!='manifest.json' and '__pycache__' not in p.parts}
 r.write('manifest.json',dict(schema='osr-ignored-propulsion-redesign-receipt/1',source_sha256=r.SOURCE,runner_sha256=sha256((r.OUT/'run.py').read_bytes()).hexdigest(),corner_runner_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),files_sha256=files,production_sources_unchanged=True,**r.FLAGS))
 print('COMPLETE',len(result['rows']),'coupons',result['resolved_corner_alternative'],flush=True)
