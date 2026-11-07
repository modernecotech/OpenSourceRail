#!/usr/bin/env python3
"""Replot adjacent immutable plot-data.json. No raw-run paths or engineering replay.

Usage: python render-recorded-plots.py --output /path/to/fresh-directory
Requires matplotlib; reads only plot-data.json beside this script.
Unit scaling m->mm, kg->tonnes and IQD->million IQD is presentation only.
"""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='Fresh output directory; existing paths are refused')
    args=parser.parse_args()
    source=Path(__file__).resolve().with_name('plot-data.json')
    data=json.loads(source.read_bytes())
    if data.get('schema')!='osr-viaduct-presentation/1':
        parser.error('Unsupported recorded plot-data schema')
    rows=data.get('cad_cases'); fem=data.get('fem_cases')
    if not isinstance(rows,list) or len(rows)!=12 or not isinstance(fem,list):
        parser.error('The recorded twelve-case CAD and FEM arrays are required')
    if len({r['case_id'] for r in rows})!=12:
        parser.error('Recorded CAD case IDs must be unique')
    if {r['rail_interface_base_iqd'] for r in rows}!={52084000.0}:
        parser.error('Recorded rail-interface amounts differ from this presentation')
    P=args.output.expanduser().resolve()
    if P.exists():
        parser.error('Output path exists; refusing to overwrite any recorded or previous plots')
    P.mkdir(parents=True,exist_ok=False)
    colors=['#245c99','#009e73','#8c564b','#a14998','#d88900','#258e9b']
    families=['reference_box','ribbed_u','variable_depth_box','folded_plate','hybrid_steel_concrete','load_following_ribs']
    names=['Box','Ribbed U','Variable-depth box','Folded plate','Steel–concrete hybrid','Load-following ribs']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#253347','text.color':'#253347','axes.edgecolor':'#aab4c1','savefig.facecolor':'white'})
    fig,ax=plt.subplots(figsize=(13.6,8.2)); fig.subplots_adjust(left=.09,right=.97,top=.83,bottom=.23)
    fig.suptitle('Twelve exact span geometries: mass and structural factory cost',x=.09,ha='left',y=.97,fontsize=21,fontweight='bold')
    fig.text(.09,.90,'20 m single-track nominal stock • dated Iraqi benchmarks + Class C process assumptions',fontsize=12)
    fig.text(.09,.86,'No China quotation, procurement approval or complete installed bridge cost is implied.',fontsize=11,color='#59677a')
    offsets={('reference_box','reference'):(-72,-24),('reference_box','robust'):(-90,12),('ribbed_u','reference'):(-4,-34),('ribbed_u','robust'):(8,-12),('variable_depth_box','reference'):(-60,17),('variable_depth_box','robust'):(-23,18),('folded_plate','reference'):(12,-31),('folded_plate','robust'):(-100,5),('load_following_ribs','reference'):(-7,24),('load_following_ribs','robust'):(-30,-32),('hybrid_steel_concrete','reference'):(15,-12),('hybrid_steel_concrete','robust'):(15,6)}
    for fam,col,name in zip(families,colors,names):
     group=[r for r in rows if r['family']==fam]; group.sort(key=lambda r:r['nominal_stock_mass_kg'])
     ax.plot([r['nominal_stock_mass_kg']/1000 for r in group],[r['structural_factory_base_iqd']/1e6 for r in group],color=col,alpha=.35,lw=1.3)
     for r in group:
      x,y=r['nominal_stock_mass_kg']/1000,r['structural_factory_base_iqd']/1e6
      ax.scatter(x,y,s=110,marker='o' if r['profile']=='reference' else 'D',facecolor=col if r['profile']=='reference' else 'white',edgecolor=col,lw=1.8,zorder=3)
      ax.annotate(name+'\n'+r['profile'],(x,y),xytext=offsets[(fam,r['profile'])],textcoords='offset points',fontsize=9,color=col,arrowprops=dict(arrowstyle='-',color=col,alpha=.4,lw=.7))
    ax.set_yscale('log'); ax.set_yticks([12,16,20,40,80,160,220]);ax.yaxis.set_major_formatter(ScalarFormatter());ax.set_ylim(10,260);ax.set_xlim(25,75)
    ax.set_xlabel('Nominal concrete + structural steel stock (tonnes)');ax.set_ylabel('Structural factory-gate estimate (million IQD, base; logarithmic scale)');ax.grid(axis='y',which='major',color='#e5eaf0');ax.set_axisbelow(True)
    fig.text(.09,.14,'Separate common rail interface: IQD 52.084m per 20 m span',fontsize=13,fontweight='bold',bbox=dict(boxstyle='round,pad=.6',facecolor='#edf3f8',edgecolor='none'))
    fig.text(.09,.082,'Factory estimate includes provisional reinforcement/prestress, processes, QA, tooling allocation and one overhead uplift.\nNominal stock omits those unresolved installed items. Circle: reference profile; hollow diamond: robust profile.',fontsize=10,color='#59677a')
    fig.savefig(P/'mass-factory-cost.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13.6,7.4));fig.subplots_adjust(left=.075,right=.97,top=.76,bottom=.26,wspace=.24)
    fig.suptitle('Actual 20 m span FEM: coarse and fine displacement comparisons',x=.075,ha='left',y=.97,fontsize=20,fontweight='bold')
    fig.text(.075,.90,'SolidCraft geometry → Gmsh solid mesh → FieldCraft / CalculiX',fontsize=12)
    fig.text(.075,.85,'Bilateral bearing restraints • uncracked, perfectly bonded elastic research models',fontsize=11,color='#59677a')
    for ax,fam,title in zip(axes,['reference_box','folded_plate'],['Reference box — 54.720 t nominal','Folded plate — 32.480 t nominal']):
     group=[r for r in fem if r['family']==fam and r['vertical_deflection_m'] is not None]
     for solver,col,mark,dx in [('fieldcraft','#245c99','o',-.035),('calculix','#d06a28','s',.035)]:
      g=sorted([r for r in group if r['solver']==solver],key=lambda r:r['level']=='fine')
      xs=[(r['level']=='fine')+dx for r in g];ys=[r['vertical_deflection_m']*1000 for r in g]
      ax.plot(xs,ys,color=col,ls='-' if solver=='fieldcraft' else '--',marker=mark,ms=8,lw=1.8,label='FieldCraft' if solver=='fieldcraft' else 'CalculiX')
     for level in ['coarse','fine']:
      r=next(r for r in group if r['solver']=='fieldcraft' and r['level']==level)
      ax.annotate(f"{r['vertical_deflection_m']*1000:.4f} mm",((level=='fine')-.035,r['vertical_deflection_m']*1000),xytext=(0,13),textcoords='offset points',ha='center',fontsize=11,fontweight='bold',color='#245c99')
     ax.set_title(title,loc='left',fontsize=13,pad=16);ax.set_xticks([0,1],['Coarse mesh','Fine mesh']);ax.set_xlim(-.28,1.28);ax.grid(axis='y',color='#e5eaf0');ax.set_ylabel('Downward vertical displacement at observation node (mm)');ax.legend(loc='lower left',frameon=False,fontsize=10);ax.margins(y=.5)
     if fam=='reference_box':
      ax.text(.5,.06,'2 GiB fine FieldCraft: held\nFine blue point: separate fresh 3 GiB evaluation',transform=ax.transAxes,ha='center',va='bottom',fontsize=9,color='#8b4f20',bbox=dict(facecolor='#fff4e8',edgecolor='none',pad=6))
    fig.text(.075,.15,'Values from immutable recorded results; nearly coincident solver points are offset horizontally for visibility.',fontsize=10)
    fig.text(.075,.09,'Two mesh levels are a sensitivity check, not established mesh independence. Bearing contact, cracking, prestress,\nreinforcement resistance, construction stages and complete installed mass remain open. No physical qualification.',fontsize=10,color='#59677a')
    fig.savefig(P/'fem-deflection.png',dpi=180);plt.close(fig)
    print(json.dumps({'output':str(P),'plots':['mass-factory-cost.png','fem-deflection.png'],'engineering_replay':False},sort_keys=True))

if __name__=='__main__':
    main()
