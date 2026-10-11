#!/usr/bin/env python3
"""Render a source-bound station access map with explicit underserved sectors."""
import argparse,gzip,hashlib,json,tomllib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle
from mapping_evidence import encoded,load_population,radial_distances,sha
ROOT=Path(__file__).resolve().parents[2]


def run(design_path,check=False):
    design=tomllib.loads(design_path.read_text());city=design_path.parent;slug=design['city']['slug'];directory=city/'engineering/mapping'
    config_path=ROOT/f'design/network-planning/{slug}-mapping-sources.json';cfg=json.loads(config_path.read_text())
    population,receipt,inputs=load_population(directory,cfg['selected_population'])
    corridor_path=city/f'{slug}.corridor.geojson';summary_path=directory/'summary.json'
    inputs+=[config_path,design_path,corridor_path,summary_path,Path(__file__),Path(__file__).with_name('mapping_evidence.py')]
    image_path=directory/f'{slug}-population-access.png';manifest_path=directory/'map-source.json'
    sources={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    if check:
        manifest=json.loads(manifest_path.read_text())
        if manifest['sources_sha256']!=sources or sha(image_path)!=manifest['image_sha256']:raise ValueError('Stale population map source or artifact')
        return
    selected=population['valid']&(population['counts']>0)
    distance=radial_distances(population,design['stations'])
    corridors=json.loads(corridor_path.read_text());fig,axes=plt.subplots(1,2,figsize=(16,9),constrained_layout=True)
    bound=design['city']['bbox'];positive=population['counts'][selected];maximum=max(2.,float(np.percentile(positive,99.5)))
    for ax,unserved in zip(axes,[False,True]):
        keep=selected&(distance>1000 if unserved else True)
        layer=ax.scatter(population['lon'][keep],population['lat'][keep],c=population['counts'][keep],s=2.5,marker='s',cmap='YlOrRd',norm=LogNorm(vmin=1,vmax=maximum),rasterized=True)
        for feature in corridors['features']:
            if feature['geometry']['type']!='LineString':continue
            coords=np.asarray(feature['geometry']['coordinates']);name=feature['properties']['name'];number=int(name.split('-')[-1])
            ax.plot(coords[:,0],coords[:,1],color=plt.cm.tab20((number-1)%20),linewidth=1.15,alpha=.85)
        ax.scatter([s['lon'] for s in design['stations']],[s['lat'] for s in design['stations']],s=9,facecolor='white',edgecolor='#142f45',linewidth=.5,zorder=4)
        for sector in cfg['sectors']:
            ax.add_patch(Rectangle((sector['west'],sector['south']),sector['east']-sector['west'],sector['north']-sector['south'],fill=False,edgecolor='#123766',linestyle='--',linewidth=1.4))
            ax.text(sector['west']+.004,sector['north']-.008,sector['id'],fontsize=10,color='#123766',weight='bold',bbox=dict(facecolor='white',alpha=.8,edgecolor='none'))
        ax.set(xlim=(bound['west'],bound['east']),ylim=(bound['south'],bound['north']),xlabel='Longitude °E',ylabel='Latitude °N',title='Native population and proposed stations' if not unserved else 'Population outside 1 km station circles')
        ax.set_aspect(1/np.cos(np.radians((bound['south']+bound['north'])/2)));ax.grid(alpha=.12)
    fig.colorbar(layer,ax=axes,shrink=.6,label='Modelled people per native pixel (log scale; top 0.5% clipped in colour only)')
    fig.suptitle(f"Baghdad: {len(design['lines'])} proposed lines / {len(design['stations'])} stations — {receipt['dataset']}",fontsize=13)
    fig.supxlabel('WorldPop '+str(receipt['year'])+' alpha modelled estimate, not census. Circles are radial screens, not validated walking access. Dashed areas are planning sectors. Physical and operating release remain open.',fontsize=9)
    fig.savefig(image_path,dpi=150);plt.close(fig)
    manifest=dict(schema='osr-population-map/1',sources_sha256=sources,image_sha256=sha(image_path),population_year=receipt['year'],validated_walking_access=False)
    manifest_path.write_bytes(encoded(manifest));print(image_path.relative_to(ROOT).as_posix())

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--design',type=Path,required=True);parser.add_argument('--check',action='store_true');args=parser.parse_args();run(args.design.resolve(),args.check)
