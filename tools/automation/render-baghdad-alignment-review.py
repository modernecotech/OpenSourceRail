#!/usr/bin/env python3
"""Compare the immutable routed seed with the current core alignment concept."""
from pathlib import Path
import argparse
import gzip,json,tomllib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[2]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad';OUT=CITY/'engineering/alignment'
def main():
    global CITY,OUT
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--design',type=Path,default=CITY/'design.toml');args=parser.parse_args()
    CITY=args.design.resolve().parent;OUT=CITY/'engineering/alignment'
    seed=json.loads(gzip.decompress((OUT/'pre-rework-corridors.json.gz').read_bytes()))
    design=tomllib.loads((CITY/'design.toml').read_text());slug=design['city']['slug']
    current=json.loads((CITY/(slug+'.corridor.geojson')).read_text())
    grid=json.loads((OUT/'planning-grid.json').read_text());core=json.loads((OUT/'core-realignment.json').read_text())['core']
    design=tomllib.loads((CITY/'design.toml').read_text());routes={f['properties']['name']:f['geometry']['coordinates'] for f in current['features'] if f['geometry']['type']=='LineString'}
    cell=grid['cell_m'];latitude=grid['bbox_north'];longitude=grid['bbox_west']
    fig,axes=plt.subplots(1,2,figsize=(14,8),constrained_layout=True)
    for index,line in enumerate(seed['lines']):
        old=[(longitude+(c+0.5)*cell/grid['m_per_deg_lon'],latitude-(r+0.5)*cell/grid['m_per_deg_lat']) for r,c in line['cells']]
        for ax,coords in zip(axes,[old,routes[line['name']]]):
            x,y=zip(*coords);ax.plot(x,y,color=plt.cm.tab10(index),linewidth=1.5,label=line['name']);ax.set_aspect(grid['m_per_deg_lat']/grid['m_per_deg_lon'])
    for ax in axes:
        ax.add_patch(Rectangle((core['west'],core['south']),core['east']-core['west'],core['north']-core['south'],fill=False,linestyle='--',edgecolor='#333333',linewidth=1.4))
        ax.set(xlabel='Longitude °E',ylabel='Latitude °N');ax.grid(alpha=.15)
    axes[0].set_title('Before: street/raster-following core')
    axes[1].set_title(f"Current concept: {sum(l['length_m'] for l in design['lines'])/1000:.1f} km / {len(design['stations'])} stations")
    axes[1].legend(fontsize=8,loc='lower right')
    fig.suptitle(CITY.name+' — direct core radials and curved ring connections',fontsize=16)
    fig.supxlabel('Dashed box: controlled city-centre study area. Core land sections elevated; water crossings remain bridges. Property, clearance and survey approvals remain open.',fontsize=9)
    fig.savefig(OUT/'core-alignment-comparison.png',dpi=150);plt.close(fig)
if __name__=='__main__':main()
