"""Declared three-point follow-up; does not modify the frozen family catalogue."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from engineering.vehicle_optimisation import magnets as m
from engineering.passive_suspension import fields

before=m.sources()
parent=next(v for v in m.candidates() if v['sample_id']=='N35-H8')
parent_input=m.field_geometry(parent)
rows=[]

def direct_input(value):
    result=deepcopy(parent_input)
    for key in ('length_x_m','reference_gap_m','origin_yz_m','regions','circuits'):
        result[key]=deepcopy(value[key])
    assert value['grade_id']==parent['grade_id']
    assert value['materials']==parent['materials']
    return result

for name,volume in [('N35-H8-half-no-yoke',.006),('N35-H8-quarter-no-yoke',.003)]:
    entry=(name,'planar-halbach','Arnold-N35UH',dict(segments=8,magnet_volume_m3=volume,yoke_m=0.))
    value=m._build(entry)
    fg=direct_input(value)
    raw=fields.solve(fg,gap_m=.012,temperature_C=80.,settings=dict(mesh_size_m=.005,outer_margin_m=.25,max_nodes=180000,check_convergence=True,steel_model='linear_bound'))
    rows.append(dict(recipe=entry,candidate=value,field_geometry=fg,raw_result=raw,
                     lineage=dict(parent_physical_ids=[parent['physical_id']],operation='counted-PM-volume-reduction',
                                  reason='Bring zero-current hot lift closer to the declared14–16kN necessary-load band'),
                     catalogue_admission='Not admitted by the unchanged catalogue; explicit derived experimental recipe',
                     physical_accepted=False,adopted=False))

selected=min(rows,key=lambda row:abs(row['raw_result']['F_z_N']-15000.))
zero=selected['raw_result']
raw=fields.solve(selected['field_geometry'],gap_m=.012,temperature_C=80.,currents_A={'array-control':20.},
    settings=dict(mesh_size_m=.005,outer_margin_m=.25,max_nodes=180000,check_convergence=True,steel_model='linear_bound'))
area=selected['candidate']['circuits'][0]['conductor_area_m2']
resistance=raw['coil_R_ohm']['array-control']
authority=dict(selected_physical_id=selected['candidate']['physical_id'],sample_id=selected['candidate']['sample_id'],
    policy='Minimum absolute difference between12mm80Czero-current lift and15000N; next experiment only',
    zero_current_result_id=zero['result_id'],raw_result=raw,
    delta_F_z_N=raw['F_z_N']-zero['F_z_N'],delta_F_z_fraction=(raw['F_z_N']-zero['F_z_N'])/zero['F_z_N'],
    mean_force_change_N_per_A=(raw['F_z_N']-zero['F_z_N'])/20,
    delta_flux_Wb_turn=raw['flux_linkage_Wb_turn']['array-control']-zero['flux_linkage_Wb_turn']['array-control'],
    one_sided_flux_increment_H=(raw['flux_linkage_Wb_turn']['array-control']-zero['flux_linkage_Wb_turn']['array-control'])/20,
    current_density_A_per_mm2=20/(area*1e6),DC_copper_power_W=400*resistance,
    unchanged_continuous_current_density_limit_A_per_mm2=3.75,
    continuous_current_density_screen_pass=20/(area*1e6)<=3.75,
    scope='Two checked field points only; no qualified derivative, controller, current limit, cooling or fault trajectory',
    physical_accepted=False,adopted=False)
assert m.sources()==before
result=dict(schema='osr-ndfeb-volume-refinements/1',source_sha256=before,
    recipe_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),parent_physical_id=parent['physical_id'],
    checked_point_count=3,campaign_checked_point_total=36,candidates=rows,authority=authority,
    physical_accepted=False,adopted=False)
result['refinement_id']=m.identity(result)
out=Path(__file__).with_name('refinements.json')
m.storage.atomic_immutable(out,m.encoded(result))
for row in rows:
    r=row['raw_result'];print(row['candidate']['sample_id'],'stockkg/car',row['candidate']['stock']['train_known_mass_kg_per_car'],
       'Fz',r['F_z_N'],'steel',r['steel_B_peak_T'],'PMmargin',r['PM_demagnetisation_margin_A_per_m'],'usable',r['interpolation_usable'],flush=True)
print('authority',m.encoded({k:v for k,v in authority.items() if k!='raw_result'}).decode(),flush=True)
print('artifact',str(out),'identity',result['refinement_id'],flush=True)
