"""Offline checks of actual retained Baghdad context estimates and controls."""
from copy import deepcopy
import json
import shutil

import numpy as np
import pytest

from engineering.assembly_design import site_context as s
from engineering.twin_workflow import core

DATA=core.ROOT/'engineering/assembly_design/data'


def test_population_counts_native_centres_half_open_and_nodata():
    p=dict(lon=np.array([44.1,44.2,44.6,44.3]),lat=np.array([33.2,33.5,33.2,33.3]),
           counts=np.array([5.,11.,13.,17.]),valid=np.array([True,True,True,False]))
    result=s.population_summary(p,s.BBOX)
    assert result['persons']==5 and result['valid_native_pixels']==1
    assert result['excluded_nodata_pixels']==1 and result['native_pixel_count']==2
    assert not result['resampled']
    p['counts'][0]=-1
    with pytest.raises(ValueError):s.population_summary(p,s.BBOX)


def test_land_water_quadrature_preserves_unknown_and_does_not_invent_current_water():
    grid=dict(height=2,width=2,cell_m=20.,bbox_north=1.,bbox_west=0.,m_per_deg_lat=100.,m_per_deg_lon=100.)
    classes=np.full((2,2,4),50,dtype=np.uint8);classes[0,0,:]=80;classes[1,1,:]=0
    r=s.land_summary(classes,grid,dict(west=0.,east=.4,south=.6,north=1.))
    counts={row['code']:row['samples'] for row in r['classifications']}
    assert counts=={0:4,50:8,80:4}
    assert r['total_samples']==16 and r['unknown_samples']==4
    assert r['permanent_water_fraction_of_known_samples']==pytest.approx(1/3)
    assert r['approximate_sampled_area_km2']==pytest.approx(.0016)
    assert not r['current_shoreline'] and not r['parcel_or_vacancy_inferred']


def test_terrain_excludes_void_nodes_preserves_extremes_and_does_not_infer_roofs():
    terrain=dict(lat=np.array([33.4,33.3]),lon=np.array([44.2,44.3]),
                 elevation_m=np.array([[31,36],[-32768,109]],dtype=np.int16))
    r=s.terrain_summary(terrain,s.BBOX)
    assert r['native_nodes']==4 and r['void_nodes']==1
    assert (r['minimum_m'],r['median_m'],r['maximum_m'])==(31,36,109)
    assert not r['ground_survey'] and not r['roof_heights']


def test_actual_source_estimates_and_scoped_comparisons_verify_offline():
    r=s.verify(DATA)
    assert r['verified'] and r['cells']==80
    context=s.read(DATA/'site-context.json')
    assert r['population']==pytest.approx(8_631_423.627875682,abs=1e-6)
    assert context['terrain']['source_sha256']==s.TERRAIN_SHA
    terrain=context['terrain']['summary']
    assert terrain['native_nodes']==2_595_241 and terrain['void_nodes']==0
    assert terrain['median_m']==36. and terrain['percentiles_m']=={'5':31.,'95':41.}
    land=context['land_water']
    assert land['missing_coverage_is_not_dry_land']
    assert land['missing_requested_longitude_range']==[44.1,44.2]
    assert land['summary']['built_up_fraction_of_known_samples']==pytest.approx(.311175023347706)
    assert land['summary']['permanent_water_fraction_of_known_samples']==pytest.approx(.02731241995234077)
    for name,comparison in context['population']['comparisons'].items():
        assert comparison['compared_extent']['west']==44.2
        assert comparison['selected_worldpop_on_same_extent']['persons']<r['population']
        assert comparison['summary']['persons']>0
    assert context['population']['source']['status'].startswith('alpha')
    assert all(context[k] is None for k in ('soil_parameters','groundwater_level_m','design_flood_level_m','roof_heights_m'))
    assert all(context[k] is False for k in core.FLAGS)


def test_context_cell_counts_conserve_actual_population_and_land_samples():
    report=s.read(DATA/'site-context.json');geo=s.read(DATA/'site-context.geojson')
    assert len(geo['features'])==80 and len({f['id']for f in geo['features']})==80
    pop=sum(f['properties']['worldpop_2026']['persons']for f in geo['features'])
    assert pop==pytest.approx(report['population']['summary']['persons'],abs=1e-6)
    classifications=sum(f['properties']['worldcover_2021']['total_samples'] for f in geo['features'])
    assert classifications==report['land_water']['summary']['total_samples']
    western=[f for f in geo['features'] if f['properties']['bbox']['east']<=44.2+1e-9]
    assert len(western)==16
    assert all(f['properties']['worldcover_2021']['total_samples']==0 for f in western)
    assert sum(f['properties']['worldpop_2026']['persons'] for f in western)>0


@pytest.mark.parametrize('failure',('native','summary','acceptance','geojson'))
def test_resealed_or_raw_tampering_never_becomes_site_evidence(tmp_path,failure):
    for name in ('site-context.json','site-context.geojson','site-context-worldpop.npz.gz','site-context-terrain.npz.gz'):
        shutil.copyfile(DATA/name,tmp_path/name)
    if failure=='native':
        p=tmp_path/'site-context-terrain.npz.gz';p.write_bytes(p.read_bytes()+b'corrupt')
    else:
        context=s.read(tmp_path/'site-context.json')
        if failure=='summary':context['population']['summary']['persons']+=1
        elif failure=='acceptance':context['ground_survey_accepted']=True
        else:
            geo=s.read(tmp_path/'site-context.geojson');geo['features'][0]['properties']['worldpop_2026']['persons']+=1
            s.write(tmp_path/'site-context.geojson',geo)
            context['portable_inputs_sha256']['site-context.geojson']=s.sha(tmp_path/'site-context.geojson')
        context.pop('revision');context['revision']=core.digest(context);s.write(tmp_path/'site-context.json',context)
    with pytest.raises(ValueError):s.verify(tmp_path)
