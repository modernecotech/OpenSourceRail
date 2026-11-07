"""Disjoint installation patterns, mass moments and static support transfer.

Stock blanks, proposed envelope geometry and unmeasured material distributions
stay distinct. Position proposals are a new physical design, never inherited
installed geometry or qualification of the manufacturing catalogue.
"""
from copy import deepcopy
from math import fsum,prod,pi,sqrt,isfinite
from pathlib import Path
import gzip,json,re
from engineering.station_rail.common import identity,digest
from engineering.station_pair import mass as parent_mass
from . import ROOT,FLAGS

INPUT='docs/design-engine/vehicle-parts/manufacturing-bundle.json.gz'
POLICY='engineering/vehicle_installation/policy.json'
CASES=('low','base','high')
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
YAXIS=[[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]]
ZAXIS=[[0.,1.,0.],[0.,0.,1.],[1.,0.,0.]]
RX90=[[1.,0.,0.],[0.,0.,-1.],[0.,1.,0.]]
RZ90=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]
RZM90=[[0.,1.,0.],[-1.,0.,0.],[0.,0.,1.]]


def seal(value,key):value[key]=identity(value);return value

def policy(root=ROOT):
    p=json.loads((Path(root)/POLICY).read_bytes())
    if p.get('schema')!='osr-vehicle-installation-policy/1':raise ValueError('Explicit installation policy required')
    l=p['layout']
    if (l['cars'],l['car_length_m'],l['car_width_m'],l['floor_top_m'])!=(6,17.,2.65,1.):raise ValueError('Declared six-car interface required')
    def visit(v):
        if isinstance(v,dict):
            for x in v.values():visit(x)
        elif isinstance(v,list):
            for x in v:visit(x)
        elif type(v) in (int,float) and not isfinite(v):raise ValueError('Finite dimensions/rates required')
    visit(p)
    if l['seat_pitch_m']<l['seat_width_m'] or l['battery_modules_per_pod']!=5:raise ValueError('Overlapping seats or unsupported electrical grouping')
    if any(p['evaluation'][k] is not False for k in ('mass_moments_are_measured','material_densities_are_qualified','swept_envelopes_are_certified')):raise ValueError('An outline cannot grant qualification')
    return p


def load(root=ROOT):
    root=Path(root);raw=(root/INPUT).read_bytes()
    if digest(root/INPUT)!=parent_mass.INPUT_SHA256:raise ValueError('Externally pinned source bundle changed')
    b=json.loads(gzip.decompress(raw))
    if b['bundle_id']!=parent_mass.BUNDLE_ID or b['candidate_id']!=identity(b['physical_definition']):raise ValueError('Source bundle identity differs')
    return b


def sources(root=ROOT):
    root=Path(root);names=[INPUT,POLICY,'engineering/station_rail/common.py','engineering/station_pair/mass.py','engineering/station_rail/vehicle.py']
    names += [p.relative_to(root).as_posix() for p in (root/'engineering/vehicle_installation').glob('*.py')]
    return {n:digest(root/n) for n in sorted(names)}


def _price(masses,material,p):
    r=p['rates'];key='insulation_usd_kg' if 'thermal-barrier' in material else 'steel_usd_kg' if 'steel' in material else 'copper_usd_kg' if 'copper' in material else 'aluminium_usd_kg'
    return {c:(masses[c]/r['yield'][i]*r[key][i]+masses[c]*(r['process_hours_per_kg'][i]*r['labour_usd_h'][i]+r['machine_QA_usd_kg'][i]))*(1+r['overhead_fraction'][i]) for i,c in enumerate(CASES)}


def proposed_parts(bundle,p,battery_layout='thin-distributed'):
    if battery_layout not in ('thin-distributed','above-floor-control'):raise ValueError('Explicit proposed battery architecture required')
    rows=deepcopy(bundle['parts']);revisions=[];l=p['layout'];rho={m['id']:m['density_kg_m3'] for m in bundle['materials']}
    def replace(row,quantity,stock,reason,mass=None):
        old=deepcopy(row);row['id']='installation/'+old['id'];row['quantity_per_assembly']=quantity;row['quantity_per_train']=quantity*6;row['stock']=stock
        if mass is None:
            mass={c:prod(stock['size_m'])*rho[row['material_id']] for c in CASES}
        row['mass_each_kg']=mass;row['direct_cost_each_usd']=_price(mass,row['material_id'],p)
        row['cost_basis']='Calculated revision: declared material rate/yield plus process labour, machine/QA and overhead included once; excludes final integration, qualification, delivery and tax; no supplier quotation'
        row['mass_basis']=dict(kind='calculated-stock' if stock and stock['kind']=='box' else 'proposed-allowance',description=reason)
        row['component_definition_id']=identity({k:row[k] for k in ('id','assembly_id','stock','quantity_per_assembly','material_id')})
        revisions.append(dict(source_part_id=old['id'],proposed_part_id=row['id'],old_quantity_per_train=old['quantity_per_train'],new_quantity_per_train=row['quantity_per_train'],
            old_mass_per_train_kg={c:old['quantity_per_train']*old['mass_each_kg'][c] for c in CASES},new_mass_per_train_kg={c:row['quantity_per_train']*mass[c] for c in CASES},
            reason=reason,source_component_definition_id=old['component_definition_id']))
    for row in rows:
        row['source_part_id']=row['id']
        if battery_layout!='thin-distributed':continue
        n=row['id'];q=row['quantity_per_assembly'];reason='New fifteen distributed underfloor pods; replaces tall-cassette stock/count once, no inherited installed geometry'
        if n=='services/battery-side-panel':replace(row,30,dict(kind='box',size_m=[1.9,.194,.002]),reason)
        elif n=='services/battery-end-panel':replace(row,30,dict(kind='box',size_m=[.296,.194,.002]),reason)
        elif n=='services/battery-lid-panel':replace(row,15,dict(kind='box',size_m=[1.9,.3,.002]),reason)
        elif n=='services/battery-floor-panel':replace(row,15,dict(kind='box',size_m=[1.9,.3,.003]),reason)
        elif n=='services/battery-tray':replace(row,15,dict(kind='box',size_m=l['battery_support_tray_stock_m']), 'Proposed folded support tray blank; end forming and module restraint require drawing')
        elif n=='services/battery-cold-plate':replace(row,15,dict(kind='box',size_m=l['battery_cold_plate_stock_m']), 'Gross cold-plate machining blank; actual channels, pressure and cooling duty remain unverified')
        elif n=='services/battery-rack-support':replace(row,60,dict(kind='box',size_m=l['battery_bracket_stock_m']), 'Four folded hanger blanks per pod; two top bolts/hanger, separate enclosure attachment')
        elif n.startswith('services/battery-rack-fixing-'):
            factor=2 if n.endswith('washer') else 1;replace(row,120*factor,oldstock(row), 'Two upper attachment bolts per hanger; each fixing counted once',mass=row['mass_each_kg'])
        elif n.startswith('services/battery-enclosure-fixing-'):
            factor=2 if n.endswith('washer') else 1;replace(row,180*factor,oldstock(row),'Twelve fixings per pod: four retention feet plus eight lid fixings, separate from module bolts',mass=row['mass_each_kg'])
        elif n=='services/battery-lid-seal':replace(row,15,dict(kind='cut-length',length_m=4.4,profile_description='New1.9×.3m lid perimeter, compound/fire/joint unverified'), 'Fifteen lid perimeters, replacing three tall-cassette seals',mass={c:old*4.4/3.7 for c,old in row['mass_each_kg'].items()})
        elif n=='services/battery-pressure-vent':replace(row,15,oldstock(row),'One independently retained vent per pod; pressure/fire sizing unverified',mass=row['mass_each_kg'])
        elif n=='services/battery-busbar':replace(row,60,oldstock(row),'Four rigid internal links per five-module pod; twelve inter-pod connections replaced by flexible links',mass=row['mass_each_kg'])
        elif n=='services/battery-plate-hose':replace(row,18,dict(kind='cut-length',length_m=1.5,profile_description='Explicit average cut only; individual12×1m+6×2.5m lengths in occurrence layout'), 'Longer distributed-plate paths with retained eighteen pairs of hose ends',mass={c:v*3 for c,v in row['mass_each_kg'].items()})
    if battery_layout=='thin-distributed':
        row=deepcopy(next(r for r in rows if r.get('source_part_id')=='services/battery-busbar'))
        row.update(id='installation/battery-flexible-link',source_part_id=None,name='Insulated flexible inter-pod link',quantity_per_assembly=12,quantity_per_train=72,stock=dict(kind='cut-length',length_m=l['battery_flexible_link_length_m'],profile_description='Proposed120mm2 copper+insulation, ampacity/fire/terminations unverified'),material_id='services/copper')
        copper=l['battery_flexible_link_length_m']*l['battery_flexible_link_copper_area_mm2']*1e-6*8960
        row['mass_each_kg']={c: copper*l['battery_flexible_link_insulation_mass_factor']*f for c,f in zip(CASES,(.9,1.,1.2))}
        row['direct_cost_each_usd']=_price(row['mass_each_kg'],row['material_id'],p)
        row['cost_basis']='Calculated proposal includes material/yield, process labour, machine/QA and overhead once; copper rate conservatively applied to cable assembly mass including insulation; no supplier quotation'
        row['mass_basis']=dict(kind='proposed-allowance',description='Declared copper area/length plus insulation factor; no ampacity or thermal approval')
        row['component_definition_id']=identity({k:row[k] for k in ('id','stock','material_id','quantity_per_assembly')});rows.append(row)
        for label,quantity,size in (('side',30,[1.866,.015,.165]),('end',30,[.015,.266,.165]),('horizontal',30,[1.896,.296,.015])):
            liner=deepcopy(row);liner.update(id='installation/battery-thermal-barrier-'+label,source_part_id=None,name='Proposed 15mm thermal/fire barrier '+label,
                quantity_per_assembly=quantity,quantity_per_train=quantity*6,material_id='installation/thermal-barrier',stock=dict(kind='box',size_m=size))
            liner['mass_each_kg']={c:prod(size)*d for c,d in zip(CASES,p['evaluation']['insulation_density_kg_m3'])}
            liner['mass_basis']=dict(kind='calculated-proposed-material',description='Unqualified insulation/fire barrier; bounded density, no fire resistance or conductivity credit')
            liner['direct_cost_each_usd']=_price(liner['mass_each_kg'],liner['material_id'],p)
            liner['component_definition_id']=identity({k:liner[k] for k in ('id','stock','material_id','quantity_per_assembly')})
            liner['cost_basis']='Calculated proposal includes barrier material/yield, cutting/fitting labour, machine/QA and overhead once; no supplier or fire qualification'
            liner['manufacturing']=['Cut separate panels; fit without blocking vents/drains; supplier thermal and fire qualification required']
            liner['joining']='Mechanically captive inside enclosure; adhesive and thermal bridge details remain open'
            liner['maintenance_removal']='Isolate and lower pod; remove lid, modules and liner; inspect/replace after damage'
            rows.append(liner)
    return rows,revisions


def oldstock(row):return deepcopy(row['stock'])


def _seats(l,side):
    if side<0:
        segments=[(-6.7,-5.15,3),(-3.85,3.85,16),(5.15,6.7,3)]
    else:segments=[(-8.2,-5.25,5),(-3.75,3.75,12),(5.25,8.2,5)]
    positions=[]
    for lo,hi,count in segments:
        occupied=count*l['seat_pitch_m'];start=(lo+hi-occupied)/2+l['seat_pitch_m']/2
        positions.extend(start+i*l['seat_pitch_m'] for i in range(count))
    return positions


def anchors(assembly,p):
    l=p['layout'];aid=assembly['id'];q=assembly['quantity_per_train'];out=[]
    def add(car,local,name,**extra):out.append(dict(id=aid+'/'+name,car_allocation=[[car,1.]],at_m=[8.5+car*17.65+local[0],local[1],local[2]],local_origin_m=local,**extra))
    if aid in ('running/intercar-coupler','running/passenger-gangway','services/intercar-electrical','services/gangway-lighting'):
        for i in range(5):out.append(dict(id=aid+f'/joint-{i}',car_allocation=[[i,.5],[i+1,.5]],at_m=[17+i*17.65+.325,0.,.65 if 'coupler' in aid else 1.9],local_origin_m=[0,0,0],joint=i))
    elif aid in ('running/end-rescue-coupler','body/terminal-end','body/terminal-window'):
        for car,sgn in ((0,-1),(5,1)):add(car,[sgn*8.5,0.,.65 if 'coupler' in aid else 2.1],f'end-{car}',end_sign=sgn)
    elif aid=='body/passage-end':
        for i in range(5):
            add(i,[8.5,0,2.1],f'left-{i}',end_sign=1);add(i+1,[-8.5,0,2.1],f'right-{i}',end_sign=-1)
    elif aid.startswith('running/'):
        for car in range(6):
            for bogie,bx in enumerate(l['bogie_centres_local_x_m']):
                bi=2*car+bogie
                if aid in ('running/wheelset','running/axlebox','running/primary-suspension'):
                    for ax,dx in enumerate((-.5*l['bogie_wheelbase_m'],.5*l['bogie_wheelbase_m'])):
                        sides=(-1,1) if aid!='running/wheelset' else (0,)
                        for side in sides:add(car,[bx+dx,side*.98,.38 if aid!='running/primary-suspension' else .53],f'{car}-{bogie}-{ax}-{side}',bogie_index=bi,axle_index=4*car+2*bogie+ax,side=side)
                else:add(car,[bx,0.,.53],f'{car}-{bogie}',bogie_index=bi)
    else:
        for car in range(6):
            if aid=='body/chair':
                for side in (-1,1):
                    for i,x in enumerate(_seats(l,side)):add(car,[x,side*l['seat_y_m'],l['seat_pan_z_m']],f'{car}-{side}-{i}',side=side)
            elif aid=='body/wheelchair':
                for i,x in enumerate(l['door_centres_local_x_m']):add(car,[x,-.86,1.],f'{car}-{i}')
            elif aid in ('body/door-opening','services/door-electrical'):
                for i,x in enumerate(l['door_centres_local_x_m']):add(car,[x,1.315,1.],f'{car}-{i}',door=i)
            elif aid in ('body/door-leaf','body/door-window'):
                for d,x in enumerate(l['door_centres_local_x_m']):
                    for side in (-1,1):add(car,[x+side*.38,1.315,1.],f'{car}-{d}-{side}',door=d,leaf_side=side)
            elif aid=='services/hvac':
                for i,x in enumerate((-3.,3.)):add(car,[x,0.,3.4],f'{car}-{i}')
            else:add(car,[0.,0.,0.],str(car))
    if len(out)!=q:raise ValueError(f'Assembly expansion differs for {aid}: {len(out)} vs{q}')
    return out


def geometry(part):
    s=part['stock'];exact=s is not None and s['kind'] not in ('envelope','cut-length')
    if s and s['kind'] in ('box','envelope'):size=list(s['size_m'])
    elif s and s['kind'] in ('rhs','u_channel'):size=[s['length_m'],s['width_m'],s['depth_m']]
    elif s and s['kind'] in ('cylinder','annulus'):
        R=s.get('radius_m',s.get('outer_radius_m'));size=[s['length_m'],2*R,2*R]
    elif s and s['kind']=='cut-length':size=[min(s['length_m'],2.),.035,.035]
    else:
        m=part['mass_each_kg']['base'];size=[.06,.04,.03] if m<1 else [.20,.15,.12] if m<30 else [.4,.3,.25]
    if any(not isfinite(x) or x<=0 for x in size):raise ValueError('Positive proposed dimensions required')
    return dict(kind=s['kind'] if s else 'proposed-equipment-zone',size_m=size,
        definition_basis='exact-gross-stock' if exact else 'catalogue-equipment-envelope' if s and s['kind']=='envelope' else 'proposed-route-zone' if s else 'proposed-bounded-component-zone',
        exact_stock=exact,finished_geometry_verified=False,
        source_stock=deepcopy(s))


def _grid(j,n,sx,sy=0.):
    if n==1:return [0.,0.,0.]
    if sy==0:return [(j-(n-1)/2)*sx/max(1,n-1),0.,0.]
    cols=max(1,int(sqrt(n)));rows=(n+cols-1)//cols
    return [((j%cols)-(cols-1)/2)*sx/max(1,cols-1),((j//cols)-(rows-1)/2)*sy/max(1,rows-1),0.]


def _pod(l,index):
    slots=[(i,j,x,y) for j,y in enumerate(l['battery_y_m']) for i,x in enumerate(l['battery_x_m']) if [i,j]!=l['battery_vacant_slot']]
    return slots[index%15]


def placement(part,a,j,p,battery_layout):
    l=p['layout'];aid=part['assembly_id'];n=part.get('source_part_id') or part['id'];q=part['quantity_per_assembly'];R=I;local=[0.,0.,0.]
    under=l['floor_top_m']-l['floor_build_up_m']
    if aid=='body/underframe':
        if n.endswith('side-sill'):local=[0.,(-1 if j==0 else 1)*1.235,under-.175]
        elif n.endswith('floor-crossmember'):
            xs=sorted([-4.4,-2.8,-2.,-.4,.4,2.,2.8,4.4]+[-8.,-7.3,-6.8,-5.9,-5.2,-3.4,-1.3,-.7,.7,1.3,3.4,5.2,5.9,6.8,7.3,8.])
            local=[xs[j],0.,under-.08];R=RZ90
        elif n.endswith('body-bolster'):local=[l['bogie_centres_local_x_m'][j],0.,under-.1];R=YAXIS
        elif n.endswith('end-beam'):local=[(-1 if j==0 else 1)*8.4,0.,under-.125];R=RZ90
        elif n.endswith('floor-stringer'):local=[0.,-.9+j*.36,under-.21]
        else:local=_grid(j,q,15.,2.);local[2]=under-.1
    elif aid=='body/sideframe':
        if n.endswith('cantrail'):local=[0.,(-1 if j==0 else 1)*1.275,3.28]
        elif n.endswith('side-post'):
            local=[-7.7+(j%12)*15.4/11,(-1 if j<12 else 1)*1.275,2.175];R=ZAXIS
        elif n.endswith('door-pillar'):local=[l['door_centres_local_x_m'][j//2]+(-.82 if j%2==0 else .82),1.275,2.175];R=ZAXIS
        elif n.endswith('door-header'):local=[l['door_centres_local_x_m'][j],1.275,3.20]
        else:local=_grid(j,q,15.,0.);local[1]=(-1 if j%2==0 else 1)*1.27;local[2]=2.15
    elif aid=='body/roof':
        local=[-8.0+(j+.5)*16./max(q,1),0.,3.4]
        if n.endswith('roof-skin'):local=[-8.46+(j+.5)*.94,0.,3.401]
        elif n.endswith('roof-seam-cover'):local=[-7.52+j*.94,0.,3.403]
    elif aid=='body/floor':
        local=[-8.28+(j%18+.5)*.92,0.,.98]
        if n.endswith('top-skin'):local[2]=.99625
        elif n.endswith('bottom-skin'):local[2]=.960
        elif n.endswith('floor-core'):local[2]=.978
        elif 'closure' in n:local[1]=(-1 if j%2 else 1)*1.205
        elif 'bolt' in n:local[1]=(-1 if j%2 else 1)*1.1
    elif aid in ('body/cladding','body/interior','body/fittings','body/fixed-window','services/lighting','services/air-ducts','services/power','services/air','services/control','services/secondary','services/pv'):
        local=_grid(j,q,13.,1.8)
        if aid=='body/fixed-window':
            local=[(-6.,-3.,0.,3.,6.)[j%5],(-1 if j<q/2 else 1)*1.31,2.25];R=RX90
        elif aid=='body/cladding':local[1]=(-1 if j%2==0 else 1)*1.318;local[2]=2.15;R=RX90
        elif aid in ('services/lighting','services/air-ducts'):local[2]=3.15
        elif aid=='services/pv':local[2]=3.43
        elif aid=='services/secondary':
            # Preserve source passive fin, neck and spreader coordinates exactly.
            if n.endswith('secondary-fin'):local=[0.,0.,.10]
            elif n.endswith('secondary-neck'):local=[0.,0.,.26]
            elif n.endswith('secondary-spreader'):local=[0.,0.,.346]
            elif n.endswith('secondary-hanger'):local=[-4.05+.9*(j//2),(-1 if j%2==0 else 1)*.06,.53825]
            elif n.endswith('secondary-heat-fin'):
                ys=[-.145+i*.0094+.00075 for i in range(31) if abs(-.145+i*.0094+.00075)>=.0085]
                local=[0.,ys[j],.3125]
            else:local=[-4.05+.9*(j%10),(-1 if j%2==0 else 1)*.06,.73]
        elif aid=='services/air':local[2]=.45;local[1]=.45
        elif aid=='services/power':local[2]=.45;local[1]=-.45
        elif aid=='services/control':local=[-7.9+(j%2)*15.8,.7,.5]
        elif aid=='body/interior':local[2]=2.2
        else:local[2]=1.1
    elif aid=='services/battery':
        if battery_layout=='thin-distributed':
            per={'installation/battery-thermal-barrier-side':2,'installation/battery-thermal-barrier-end':2,'installation/battery-thermal-barrier-horizontal':2,'services/battery-module':5,'services/battery-insulator':5,'services/battery-clamp':10,'services/battery-module-retention-bolt':20,'services/battery-module-retention-washer':40,'services/battery-module-retention-nut':20,
                'services/battery-busbar':4,'services/battery-terminal-screw':10,'services/battery-terminal-washer':10,'services/battery-terminal-cover':10,'services/battery-side-panel':2,'services/battery-end-panel':2,'services/battery-rack-support':4,'services/battery-rack-fixing-bolt':8,'services/battery-rack-fixing-washer':16,'services/battery-rack-fixing-nut':8,
                'services/battery-enclosure-fixing-bolt':12,'services/battery-enclosure-fixing-washer':24,'services/battery-enclosure-fixing-nut':12}
            k=per.get(n,1);idx=j//k if n in per else j%15
            _,_,x,y=_pod(l,idx);z=.45;local=[x,y,z]
            if n=='services/battery-module':local=[x+(j%5-2)*l['battery_module_pitch_m'],y,.35+.003+.015+.003+.002+.125/2];R=RZ90
            elif n=='services/battery-insulator':local=[x+(j%5-2)*l['battery_module_pitch_m'],y,.3755]
            elif n=='services/battery-clamp':local=[x+((j%10)//2-2)*l['battery_module_pitch_m'],y+(-.105 if j%2==0 else .105),.38]
            elif n.startswith('services/battery-module-retention-'):
                m=(j%k)//(k//5);corner=(j%k)%(k//5);local=[x+(m-2)*l['battery_module_pitch_m']+(-.13 if corner%2==0 else .13),y+(-.11 if corner//2%2==0 else .11),.375]
            elif n in ('services/battery-terminal-screw','services/battery-terminal-washer','services/battery-terminal-cover'):
                m=(j%10)//2;local=[x+(m-2)*l['battery_module_pitch_m'],y+(-.07 if j%2==0 else .07),.51]
            elif n=='services/battery-busbar':local=[x+(j%4-1.5)*l['battery_module_pitch_m'],y,.515]
            elif n=='services/battery-side-panel':local=[x,y+(-.149 if j%2==0 else .149),.35+.003+.194/2];R=RX90
            elif n=='services/battery-end-panel':local=[x+(-.948 if j%2==0 else .948),y,.35+.003+.194/2];R=YAXIS
            elif n=='services/battery-floor-panel':local[2]=.3515
            elif n=='services/battery-lid-panel':local[2]=.549
            elif n=='services/battery-tray':local[2]=.373
            elif n=='services/battery-cold-plate':local[2]=.3695
            elif n=='installation/battery-thermal-barrier-side':local=[x,y+(-.1405 if j%2==0 else .1405),.4355]
            elif n=='installation/battery-thermal-barrier-end':local=[x+(-.9405 if j%2==0 else .9405),y,.4355]
            elif n=='installation/battery-thermal-barrier-horizontal':local=[x,y,.3605 if j%2==0 else .5405]
            elif n=='services/battery-rack-support':
                local=[x+(-.8 if j%4<2 else .8),y+(-.1 if j%2==0 else .1),.675];R=ZAXIS
            elif n in ('services/battery-bmu','services/battery-contactor','services/battery-disconnect','services/battery-string-fuse','services/battery-precharge','services/battery-current-sensor','services/battery-imd'):
                local=[3.6+(j%3-1)*.45,.975,.43]
            elif n=='services/battery-hv-harness':local=[0.,.65,.57]
            elif n=='services/battery-plate-hose':
                local[2]=.54
            elif n=='installation/battery-flexible-link':local=[x,y,.54]
            elif 'chiller' in n or n in ('services/battery-pump','services/battery-radiator','services/battery-expansion-pot'):
                local=[4.8,-.6+(j%3)*.6,.45]
        else:
            idx=(j//25)%3 if n=='services/battery-module' else j%3
            local=[(-7.3,-7.3,7.3)[idx],-.86,1.45+(.9 if idx==1 else 0.)]
            if n=='services/battery-module':local[0]+=(j%3-1)*.361;local[1]+=(j//3%3-1)*.19;local[2]+=(j//9%3-1)*.125;R=RZ90
    elif aid=='body/chair':
        R=RZM90 if a['side']>0 else RZ90
        if n.endswith('chair-back'):local=[0.,a['side']*.20,.30];R=RX90
        elif 'anchor' in n:local=[0.,0.,-.42]
        elif 'base' in n:local=[0.,0.,-.33]
        else:local=[0.,0.,0.]
    elif aid=='body/wheelchair':local=[0.,0.,.05 if 'floor' in n else .5]
    elif aid in ('body/door-opening','services/door-electrical'):
        local=_grid(j,q,1.2,.02);local[2]=2.25 if any(k in n for k in ('header','guide','roller','carriage','motor','drive','belt','reducer','coupling')) else .02 if any(k in n for k in ('bottom','threshold','drain')) else 1.2
        if n.endswith(('header-backplate','header-cover')):local=[0.,0.,2.25];R=RX90
    elif aid in ('body/door-leaf','body/door-window'):
        local=[0.,0.,1.08];R=RX90
    elif aid.startswith('running/'):
        local=_grid(j,q,1.9,1.8)
        if aid=='running/wheelset':
            if n.endswith('/wheel'):local=[0.,(-1 if j==0 else 1)*l['gauge_m']/2,0.];R=RZ90
            else:local=[0.,0.,0.];R=RZ90
        elif aid=='running/bogie-frame':
            if n.endswith('frame-side-rhs'):local=[0.,(-1 if j==0 else 1)*1.02,-.12]
            elif n.endswith('frame-transom-rhs'):local=[(-1 if j==0 else 1)*.42,0.,-.12];R=RZ90
            elif n.endswith('frame-end-tie'):local=[(-1 if j==0 else 1)*1.3,0.,-.12];R=RZ90
            else:local[2]=-.03
        elif aid=='running/secondary-support':
            if n.endswith('bolster-main-rhs'):local=[0.,0.,-.116];R=RZ90
            elif 'air-spring' in n:local=[0.,(-1 if j==0 else 1)*.75,.12]
            else:local[2]=.06
        elif aid=='running/bogie-brakes':
            local=[(-1 if j<q/2 else 1)*1.05,(-1 if j%2==0 else 1)*.5,-.15]
        elif aid in ('running/axlebox','running/primary-suspension'):local=_grid(j,q,.18,.12)
        elif 'coupler' in aid:local=_grid(j,q,.4,.25)
        elif aid=='running/passenger-gangway':local=_grid(j,q,.3,1.8);local[2]=.2
    elif aid=='services/hvac':local=_grid(j,q,1.2,.9);local[2]=.3
    else:local=_grid(j,q,.2,1.8)
    at=[a['at_m'][k]+local[k] for k in range(3)]
    return at,R


def transformed_size(size,R):return [sum(abs(R[a][b])*size[b] for b in range(3)) for a in range(3)]


def _local_I(g,m):
    s=g['source_stock'];a,b,c=g['size_m']
    if s and s['kind'] in ('cylinder','annulus'):
        ro=s.get('radius_m',s.get('outer_radius_m'));ri=s.get('inner_radius_m',0.)
        return [.5*m*(ro*ro+ri*ri),m*((ro*ro+ri*ri)/4+a*a/12),m*((ro*ro+ri*ri)/4+a*a/12)]
    if s and s['kind']=='rhs':
        t=s['wall_m'];outer=a*b*c;inner=a*(b-2*t)*(c-2*t);v=outer-inner
        return [m/v*(outer*x-inner*y)/12 for x,y in ((b*b+c*c,(b-2*t)**2+(c-2*t)**2),(a*a+c*c,a*a+(c-2*t)**2),(a*a+b*b,a*a+(b-2*t)**2))]
    return [m*(b*b+c*c)/12,m*(a*a+c*c)/12,m*(a*a+b*b)/12]


def _cg_bound(rows,axis,upper):
    xs=[r['centroid_m'][axis]+(r['uncertainty_m'][axis] if upper else -r['uncertainty_m'][axis]) for r in rows]
    lo,hi=min(xs),max(xs)
    for _ in range(70):
        mid=(lo+hi)/2
        total=fsum((r['mass_kg']['high'] if (x>mid)==upper else r['mass_kg']['low'])*(x-mid) for r,x in zip(rows,xs))
        if total>0:lo=mid
        else:hi=mid
    return (lo+hi)/2


def mass_properties(rows,case):
    M=fsum(r['mass_kg'][case] for r in rows)
    if M<=0:raise ValueError('Positive mass required')
    cg=[fsum(r['mass_kg'][case]*r['centroid_m'][a] for r in rows)/M for a in range(3)]
    tensor=[[0.]*3 for _ in range(3)]
    for r in rows:
        m=r['mass_kg'][case];d=[r['centroid_m'][a]-cg[a] for a in range(3)];S=r['shape_I_per_kg']
        for i in range(3):
            for j in range(3):tensor[i][j]+=m*(S[i][j]+((fsum(x*x for x in d) if i==j else 0.)-d[i]*d[j]))
    return dict(mass_kg=M,CG_m=cg,inertia_about_CG_kg_m2=tensor,
        scope='Mass-weighted proposed geometry/zone distribution; equipment envelopes use uniform-box inertia proxy, not measured installed inertia')


def _moments_for_pattern(part,a,positions,R,g,p):
    q=len(positions);center=[fsum(x[k] for x in positions)/q for k in range(3)]
    own=_local_I(g,1.)
    intrinsic=[[fsum(R[i][k]*own[k]*R[j][k] for k in range(3)) for j in range(3)] for i in range(3)]
    covariance=[[fsum((x[i]-center[i])*(x[j]-center[j]) for x in positions)/q for j in range(3)] for i in range(3)]
    total_variance=fsum(covariance[k][k] for k in range(3))
    J=[[intrinsic[i][j]+((total_variance if i==j else 0.)-covariance[i][j]) for j in range(3)] for i in range(3)]
    unc=p['evaluation']['gross_stock_position_uncertainty_m'] if g['exact_stock'] else p['evaluation']['envelope_position_uncertainty_m'] if g['kind']=='envelope' else p['evaluation']['unresolved_position_uncertainty_m']
    return dict(id=part['id']+'@'+a['id'],part_id=part['id'],source_part_id=part['source_part_id'],assembly_id=part['assembly_id'],assembly_occurrence_id=a['id'],
        car_allocation=deepcopy(a['car_allocation']),bogie_index=a.get('bogie_index'),count=q,
        positions_m=positions,rotation=deepcopy(R),geometry=g,
        centroid_m=center,uncertainty_m=[unc]*3,
        mass_kg={c:q*part['mass_each_kg'][c] for c in CASES},shape_I_per_kg=J,
        direct_cost_usd={c:q*part['direct_cost_each_usd'][c] for c in CASES},
        material_id=part['material_id'],make_buy=part['make_buy'],
        proposed_position_not_measurement=True)


def _scenario_rows(patterns,case_kind,p):
    rows=list(patterns);l=p['layout']
    # Unspecified installation mass remains a positive separate reserve, never
    # replacing or adding the earlier parent vehicle allocation.
    reserve=p['evaluation']['unlocated_installation_reserve_kg']
    for car in range(6):
        rows.append(dict(id=f'reserve/{car}',part_id=None,assembly_id='installation-reserve',car_allocation=[[car,1.]],bogie_index=None,
            centroid_m=[8.5+car*17.65,0.,1.9],uncertainty_m=[5.,1.,1.8],
            mass_kg={c:reserve[c]/6 for c in CASES},shape_I_per_kg=[[0.]*3 for _ in range(3)]))
    if case_kind!='tare':
        count=46 if case_kind=='normal' else 160
        for car in range(6):
            if case_kind=='normal':
                pos=[[8.5+car*17.65+x,side*l['seat_y_m'],p['evaluation']['seated_passenger_CG_z_m']] for side in (-1,1) for x in _seats(l,side)]
                pos += [[8.5+car*17.65+x,-.86,1.55] for x in l['door_centres_local_x_m']]
            else:pos=[[8.5+car*17.65-7.6+(j%20)*15.2/19,-.9+(j//20)*1.8/7,p['evaluation']['crowd_passenger_CG_z_m']] for j in range(count)]
            for j,x in enumerate(pos):rows.append(dict(id=f'{case_kind}-person/{car}/{j}',part_id=None,assembly_id='passengers',car_allocation=[[car,1.]],bogie_index=None,
                centroid_m=x,uncertainty_m=[.1,.1,.15],mass_kg={c:p['evaluation']['passenger_mass_kg'] for c in CASES},shape_I_per_kg=[[0.]*3 for _ in range(3)]))
    return rows


def reactions(rows,case,p):
    g=p['evaluation']['gravity_m_s2'];l=p['layout'];axles=[];cars=[]
    for car in range(6):
        cx=8.5+car*17.65;supports=[cx+x for x in l['bogie_centres_local_x_m']];body=[]
        for r in rows:
            fraction=next((f for c,f in r['car_allocation'] if c==car),0.)
            if fraction and r.get('bogie_index') is None:body.append((r['mass_kg'][case]*fraction,r['centroid_m'][0]))
        W=fsum(m*g for m,x in body);moment=fsum(m*g*(x-supports[0]) for m,x in body)
        right=moment/(supports[1]-supports[0]);left=W-right
        cars.append(dict(car=car,body_mass_kg=W/g,body_left_support_N=left,body_right_support_N=right))
        for side,load in enumerate((left,right)):
            bi=2*car+side;bx=supports[side];xa=bx-l['bogie_wheelbase_m']/2;xb=bx+l['bogie_wheelbase_m']/2
            own=[r for r in rows if r.get('bogie_index')==bi]
            weight=load+fsum(r['mass_kg'][case]*g for r in own)
            mom=load*(bx-xa)+fsum(r['mass_kg'][case]*g*(r['centroid_m'][0]-xa) for r in own)
            rb=mom/(xb-xa);ra=weight-rb
            for j,(x,F) in enumerate(((xa,ra),(xb,rb))):axles.append(dict(id=f'car-{car}/bogie-{side}/axle-{j}',x_m=x,vertical_force_N=F))
    total=fsum(r['mass_kg'][case] for r in rows);force=fsum(a['vertical_force_N'] for a in axles)
    first=fsum(r['mass_kg'][case]*g*r['centroid_m'][0] for r in rows);actual=fsum(a['vertical_force_N']*a['x_m'] for a in axles)
    return dict(axles=axles,cars=cars,force_residual_N=force-total*g,moment_residual_Nm=actual-first,
        minimum_axle_force_N=min(a['vertical_force_N'] for a in axles),
        scope='Static full-axle forces across bothrails; runninggear weight counted once; point secondary/axle supports, no suspension dynamics or strength rating')


def interfaces(p,battery_layout='thin-distributed'):
    l=p['layout'];slots=[_pod(l,i) for i in range(15)];checks=[];podsize=l['battery_pod_size_m'];under=l['floor_top_m']-l['floor_build_up_m']-.35
    for i,(_,row,x,y) in enumerate(slots):
        outer=abs(y)>.6;stroke=l['battery_removal_stroke_m'];end=abs(y)+stroke-podsize[1]/2
        deps=[k for k,(_,r,xx,yy) in enumerate(slots) if xx==x and yy*y>0 and abs(yy)>abs(y)]
        checks.append(dict(pod=i,centre_local_m=[x,y,l['battery_pod_bottom_m']+podsize[2]/2],
            bogie_zone_longitudinal_margin_m=5.-(abs(x)+podsize[0]/2),
            sill_vertical_margin_m=under-(l['battery_pod_bottom_m']+podsize[2]),
            nominal_ground_clearance_m=l['battery_pod_bottom_m'],
            central_corridor_margin_m=abs(y)-podsize[1]/2-l['reserved_central_corridor_halfwidth_m'],
            removal_stroke_m=stroke,removal_before_inner_pods=deps,
            complete_lateral_exit_margin_m=end-l['car_width_m']/2,
            swept_envelope_m=[[x-podsize[0]/2,min(y,y+(1 if y>0 else -1)*stroke)-podsize[1]/2,l['battery_pod_bottom_m']],
                [x+podsize[0]/2,max(y,y+(1 if y>0 else -1)*stroke)+podsize[1]/2,l['battery_pod_bottom_m']+podsize[2]]],
            removable_after_isolation_and_outer_pods= end>l['car_width_m']/2 and 5.-(abs(x)+podsize[0]/2)>0,
            lifting_table_required=True,tool_access_verified=False))
    clear=l['car_width_m']-2*.06-2*l['passenger_knee_projection_from_wall_m']
    angle=l['gangway_yaw_envelope_rad'];close=(l['car_width_m']/2)*2*__import__('math').sin(angle/2)
    return dict(battery_layout=battery_layout,battery_pod_checks=checks if battery_layout=='thin-distributed' else [],
        battery_control_scope='Above-floor legacy envelope control is not fully packed or access verified' if battery_layout!='thin-distributed' else None,
        passive_aluminium_secondary='Source services/secondary parts retained once: active fin z=.02–.18m, neck to.34m, spreader to.352m, hangers to.7245m; additional fixing proxies remain proposed, strength and LIM clearance not admitted',
        module_packaging=dict(modules_per_pod=5,internal_length_margin_m=1.9-.004-.030-(4*l['battery_module_pitch_m']+.361),
            internal_width_margin_m=.3-.004-.030-.19,terminal_height_allowance_m=l['battery_terminal_height_allowance_m'],
            remaining_height_after_terminal_allowance_m=.2-.005-.030-.003-.002-.125-l['battery_terminal_height_allowance_m'],
            manufacturing_tolerance_and_terminal_model_verified=False),
        normal_aisle_clear_width_m=clear,
        aisle_project_target_m=l['minimum_project_aisle_m'],aisle_target_passed=clear>=l['minimum_project_aisle_m'],
        door_clear_width_m=l['door_clear_width_m'],door_sides=1,doors_per_car=2,
        fixed_seats_per_car=44,wheelchair_places_per_car=2,
        gangway=dict(intercar_gap_m=l['intercar_gap_m'],relative_yaw_rad=angle,
            corner_closure_m=close,remaining_corner_gap_m=l['intercar_gap_m']-close-l['gangway_axial_stroke_m'],
            pitch_rad=l['gangway_pitch_envelope_rad'],flexible_cables_and_bellows_require_test=True),
        source_stock_intersections_are_not_final_penetrations=True,
        access_and_swept_envelopes_verified=False)


def build(root=ROOT,*,battery_layout='thin-distributed'):
    root=Path(root);before=sources(root);b=load(root);p=policy(root);parts,revisions=proposed_parts(b,p,battery_layout)
    templates={a['id']:anchors(a,p) for a in b['assemblies']};patterns=[]
    for part in parts:
        g=geometry(part)
        for a in templates[part['assembly_id']]:
            positions=[];rotations=[]
            for j in range(part['quantity_per_assembly']):
                at,R=placement(part,a,j,p,battery_layout);positions.append(at);rotations.append(R)
            # Parts of a type within one assembly share orientation in current
            # generators; split only where a future explicit rule varies it.
            if not all(R==rotations[0] for R in rotations):raise ValueError('Mixed orientation requires separate deterministic pattern')
            patterns.append(_moments_for_pattern(part,a,positions,rotations[0],g,p))
    if len(patterns)>p['evaluation']['maximum_patterns'] or sum(r['count'] for r in patterns)>p['evaluation']['maximum_occurrences']:raise ValueError('Installation expansion budget exceeded')
    physical=dict(schema='osr-installed-layout-physical/1',parent_candidate_id=b['candidate_id'],
        parent_physical_definition_id=identity(b['physical_definition']),battery_layout=battery_layout,
        coordinate_frame=dict(length_unit='m',axes=['nose-to-tail','left-to-right','rail-up'],train_origin='nose of first car, railhead z=0',car_origin='body centre at railhead; pitch17.65m'),
        layout=p['layout'],part_revisions=[{k:r[k] for k in ('source_part_id','proposed_part_id','old_quantity_per_train','new_quantity_per_train','reason')} for r in revisions],
        proposed_components=[dict(id=r['id'],source_part_id=r['source_part_id'],component_definition_id=r['component_definition_id'],quantity_per_train=r['quantity_per_train'],material_id=r['material_id'],stock=r['stock']) for r in parts],
        occurrence_patterns=[{k:r[k] for k in ('id','part_id','count','positions_m','rotation','geometry','car_allocation','bogie_index')} for r in patterns])
    cid=identity(physical);scenarios=[];outer={}
    for kind in ('tare','normal','crowd-control'):
        rows=_scenario_rows(patterns,'crowd' if kind=='crowd-control' else kind,p)
        cgbox=[[_cg_bound(rows,a,False),_cg_bound(rows,a,True)] for a in range(3)]
        inertia_upper=[fsum(r['mass_kg']['high']*(3*r['shape_I_per_kg'][a][a]+sum((max(abs(r['centroid_m'][j]-cgbox[j][0]),abs(r['centroid_m'][j]-cgbox[j][1]))+r['uncertainty_m'][j])**2 for j in range(3) if j!=a)) for r in rows) for a in range(3)]
        outer[kind]=dict(CG_outer_box_m=cgbox,inertia_diagonal_outer_intervals_kg_m2=[[0.,x] for x in inertia_upper],mass_interval_kg=[fsum(r['mass_kg'][c] for r in rows) for c in ('low','high')],
            scope='Conservative linear-fractional bounds under independent declared mass and centroid-zone hypotheses; not guaranteed measured physical limits')
        for case in CASES:
            props=mass_properties(rows,case);loads=reactions(rows,case,p)
            carprops=[]
            for car in range(6):
                allocated=[]
                for r in rows:
                    f=next((f for c,f in r['car_allocation'] if c==car),0.)
                    if f:allocated.append(dict(r,mass_kg={c:r['mass_kg'][c]*f for c in CASES}))
                carprops.append(dict(car=car,**mass_properties(allocated,case)))
            scenarios.append(dict(name=kind+'-'+case,case=case,load_kind=kind,train_mass_kg=props['mass_kg'],CG_m=props['CG_m'],inertia_about_CG_kg_m2=props['inertia_about_CG_kg_m2'],cars=carprops,
                axles=loads['axles'],static_supports=loads['cars'],force_residual_N=loads['force_residual_N'],moment_residual_Nm=loads['moment_residual_Nm'],minimum_axle_force_N=loads['minimum_axle_force_N'],
                lateral_acceleration_m_s2=p['evaluation']['lateral_acceleration_m_s2'],physical_accepted=False))
    direct={c:fsum(r['direct_cost_usd'][c] for r in patterns) for c in CASES}
    nominal={c:fsum(r['mass_kg'][c] for r in patterns) for c in CASES}
    source_counts={part['source_part_id'] for part in parts if part['source_part_id'] is not None}
    if source_counts!={r['id'] for r in b['parts']}:raise ValueError('Lost or invented source part coverage')
    for part in parts:
        if sum(r['count'] for r in patterns if r['part_id']==part['id'])!=part['quantity_per_train']:raise ValueError('Part quantity expanded more/less than once')
    result=dict(schema='osr-vehicle-installation/1',candidate_id=cid,physical_definition=physical,parent_candidate_id=b['candidate_id'],parent_bundle_id=b['bundle_id'],
        proposed_component_types=len(parts),source_component_types=len(b['parts']),assembly_occurrences=templates,
        materials=deepcopy(b['materials'])+([dict(id='installation/thermal-barrier',name='Proposed unspecified thermal/fire-barrier panel',
            density_cases_kg_m3=dict(zip(CASES,p['evaluation']['insulation_density_kg_m3'])),thickness_m=p['layout']['battery_insulation_thickness_m'],
            thermal_conductivity_W_mK=None,fire_classification=None,scope='Counted outline material hypothesis; supplier composition, conductivity and railway fire qualification are open')] if battery_layout=='thin-distributed' else []),
        patterns=patterns,parts=parts,revisions=revisions,mass_scenarios=scenarios,mass_uncertainty=outer,
        nominal_part_mass_kg=nominal,source_part_mass_kg=b['nominal_mass_kg']['known_leaf_subtotal'],
        direct_parts_process_usd=direct,source_direct_parts_process_usd=b['direct_parts_process_usd']['known_leaf_subtotal'],
        interface_screens=interfaces(p,battery_layout),assembly_plans=assembly_plans(b,parts,p,battery_layout),layout_definition_complete=True,source_part_coverage_complete=True,
        exact_stock_types=sum(geometry(r)['exact_stock'] for r in parts),
        unknown_finished_geometry_types=sum(not geometry(r)['exact_stock'] for r in parts),
        total_occurrences=sum(r['count'] for r in patterns),source_sha256=before,policy=p,
        assumptions=['Longitudinal seats are an explicit proposed architecture, not inherited seating geometry',
            'Stock blanks may intersect at proposed joints; drilling, machining, cuts, welds, adhesives and fitted shapes require detailed CAD',
            'Equipment/fastener envelopes and uniform-box inertia are declared layout proxies, not supplier shapes or measured mass distributions',
            'Reaction model is rigid static two-stage support transfer, no bogie/contact/curve/braking/crash/fatigue qualification',
            'Separate installation reserve remains positive and bounded; it does not claim to cover every missing item',
            'Module/hose/cable fire, charge, cooling, ampacity and hydraulic duty remain open; no electrical or physical approval follows',
            '15mm thermal/fire-barrier panels are an explicit unqualified material hypothesis, with positive mass/cost and no fire rating inherited',
            'All 605 source types are counted once; proposed zones are not supplier shape recovery or installation acceptance'],
        **FLAGS)
    if sources(root)!=before:raise ValueError('Installation source changed while computing; do not publish mixed evidence')
    return seal(result,'evaluation_id')


def axle_loads(result,*,system_candidate_id=None):
    if result['evaluation_id']!=identity({k:v for k,v in result.items() if k!='evaluation_id'}) or result['candidate_id']!=identity(result['physical_definition']):raise ValueError('Sealed same-body installation required')
    value=dict(schema='osr-pilot-axle-loads/1',candidate_id=system_candidate_id or result['candidate_id'],vehicle_candidate_id=result['candidate_id'],mass_evaluation_id=result['evaluation_id'],
        load_cases=[{k:deepcopy(r[k]) for k in ('name','train_mass_kg','axles','CG_m','lateral_acceleration_m_s2')} for r in result['mass_scenarios']],
        source_sha256=result['source_sha256'],scope='Static full-axle force across bothrails; civil dynamicfactor has not been applied',**FLAGS)
    return seal(value,'evaluation_id')


def assembly_plans(bundle,parts,p,battery_layout):
    """Count existing mechanisms and define finite motion/access proposals.

    These are engineering work instructions and necessary envelope checks, not
    an assertion that all generic component zones have cleared one another.
    """
    l=p['layout'];plans=[]
    for a in bundle['assemblies']:
        selected=[r for r in parts if r['assembly_id']==a['id']]
        categories={}
        for name,words in dict(bolts=('bolt',),nuts=('nut',),washers=('washer',),rivets=('rivet',),
                retainers=('circlip','retainer','tether','anti-lift'),bearings=('bearing','bush'),
                slides=('slide','guide-rail'),stops=('stop',),flexible_services=('hose','harness','cable','belt','bellows','seal')).items():
            matched=[r for r in selected if any(w in r['id'] for w in words)]
            categories[name]=dict(quantity_per_train=sum(r['quantity_per_train'] for r in matched),part_ids=[r['id'] for r in matched],
                scope='Inventory classification; purchased bearings may contain internal pieces not separately catalogued')
        plans.append(dict(assembly_id=a['id'],occurrences=a['quantity_per_train'],interfaces=deepcopy(a['interfaces']),
            component_type_ids=[r['id'] for r in selected],inventory_categories=categories,
            source_assembly_steps=deepcopy(a['assembly_steps']),source_removal_sequence=a['maintenance_removal'],
            tool_and_lifting_access=dict(required=True,verified=False,minimum_local_tool_radius_hypothesis_m=.15,
                lifting_points_and_load_rating_verified=False,retention_proof_required=True),
            open_tasks=deepcopy(a['open_tasks']),installation_accepted=False))
    doors=[]
    for car in range(6):
        for d,x in enumerate(l['door_centres_local_x_m']):
            cx=8.5+car*17.65+x
            for side in (-1,1):
                start=cx+side*.38;end=start+side*l['door_slide_m']
                doors.append(dict(id=f'car-{car}/door-{d}/leaf-{side}',joint='bounded-prismatic-slide',axis=[1,0,0],
                    travel_m=[0.,side*l['door_slide_m']],closed_center_m=[start,1.315,2.08],
                    swept_zone_m=[[min(start,end)-.38,1.27,1.],[max(start,end)+.38,1.36,3.16]],
                    header_end_margin_m=1.5-(.38+l['door_slide_m']+.38),
                    removal_sequence=['Isolate door drive and interlock; fit physical restraint','Remove header cover and support leaf on rated lifting table',
                        'Release belt clamp and retained roller pins, lift clear of bottom guides','Withdraw leaf outward into protected work area'],
                    removal_outward_stroke_m=.4,tool_radius_m=l['door_tool_clearance_m'],
                    flex_harness_travel_m=l['door_slide_m'],minimum_cable_radius_m=.05,
                    conductor_length_and_chain_protection_verified=False,anti_drop_retention_verified=False,entrapment_and_emergency_release_verified=False))
    pod_sequence=['Isolate string, verify absence of voltage, discharge retained energy and close cooling isolation valves',
        'Drain local circuit into recovery vessel; release keyed HV/LV and coolant connections',
        'Support pod on rated table; fit secondary restraint before releasing four feet and upper hanger attachments',
        'Remove outer pod first where listed; translate laterally 1.3m, then lower clear',
        'On refit leak-test, insulation-test, torque-mark, inspect seals/vent path and record part revision']
    return dict(plans=plans,door_motion=doors,
        motion_joints=dict(door_leaf_slides=24,bogie_yaw_interfaces=12,secondary_air_springs=24,gangway_floor_slides=10,
            gangway_floor_hinge_cartridges=10,intercar_spherical_bushes=10,source='Counts from six-car source assemblies; no unspecified internal bearing count invented'),
        bogie_finite_envelope=dict(yaw_rad=[-.08,.08],vertical_jounce_m=[-.04,.04],
            scope='Proposed finite screening domain only; frame/axlebox interference and loaded wheel clearance require actual component geometry',
            body_lift_before_bogie_removal_m=l['body_lifting_clearance_m'],joint_endstop_and_hose_flexibility_verified=False),
        battery_service=dict(layout=battery_layout,sequence=pod_sequence if battery_layout=='thin-distributed' else ['Legacy cabinet control requires separate access model'],
            connector_slack_m=l['battery_service_slack_m'],disconnect_before_translation=True,
            minimum_cable_radius_m=l['battery_cable_minimum_bend_radius_m'],minimum_hose_radius_m=l['battery_hose_minimum_bend_radius_m'],
            minimum_lifting_table_kg_hypothesis=l['battery_lifting_table_rated_kg_hypothesis'],fitting_coordinates_and_cooling_pressure_verified=False),
        interference_scope='Gross stock and proposed bounded zones may overlap. These are design refinement findings, not a collision-free finished assembly',
        accepted=False)
