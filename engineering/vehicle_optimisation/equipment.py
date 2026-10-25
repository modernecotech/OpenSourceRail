"""Finite chassis/door/window takeoffs; no installed vehicle acceptance.

Aluminium replacements are matched against section stiffness, never obtained by
changing density in the old frame. Exact retained frame IDs and two source-bound
equipment allowances are different removal accounts. HVAC is another owner's
account. Purchased door mechanism references remain references, not solid CAD or
a complete certified 1.4x2.1m door system.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "osr-vehicle-equipment-optimisation/1"
FLAGS = dict(engineering_accepted=False, physical_accepted=False,
             configuration_adopted=False, installed_mass_closed=False)
HYDRO = "https://www.hydro.com/globalassets/01-products--services/extruded-profiles/americas/ena-resources/alloy-data-sheets/hydro_2019_data_sheet_6005a_revise_1.pdf"
HYDRO_6082 = "https://www.hydro.com/globalassets/08-about-hydro/hydro-worldwide/austria/nenzing/alloy-data-sheets/hydro-en-aw-6082.pdf"
WELD_STUDY = "https://www.mdpi.com/1996-1944/11/8/1396"
BODE = "https://www.bode-global.com/en/products/door-systems/bidsr-s"
ES2 = "https://transitworld.wabtec.com/media/es2-datasheet"
ESP4C = "https://transitworld.wabtec.com/lrv-train-doors"
SOLAR = "https://www.saint-gobain-sekurit-transport.com/sites/hps-mac3-sekurit-transport/files/2021-12/Saint-Gobain%20Sekurit%20Transport%20-%20Thermocontrol%20Reflecting.pdf"
GLASS = "https://www.saint-gobain-sekurit.com/en-in/and-preserving-our-future/enabling-sustainable-mobility"
PC = "https://www.sabic.com/en/industries/mass-transportation/rail/rail-glazing"
REFERENCES = [dict(url=HYDRO, basis="Hydro2019 producer table:6061-T6 yield240MPa;6005A-T5 yield215MPa; product/thickness applicability must be confirmed"),
 dict(url=HYDRO_6082,basis="Hydro ENAW6082 extrusion table: T6 <=5mm yield250MPa; supplier geometry/temper qualification pending"),
 dict(url=WELD_STUDY,basis="Primary welded6082 experiment reports softened material; our0.5 proof-strength retention is a declared sensitivity, not grade-specific weld qualification"),
 dict(url=ES2,basis="1300mm double-door operator27kg plus hanger14kg; not complete door and not quoted1400mm installation"),
 dict(url=ESP4C,basis="1300mm double-door mechanism including hanger46kg;1400mm/2100mm integration unqualified"),
 dict(url=BODE,basis="BIDS-S full-system LRV reference approx120kg, width800..1400mm; not an exact-height supplier quotation"),
 dict(url=SOLAR,basis="Stationary plot approx.82 clear/.55 IR-reflecting,3/.7/3 laminated windshield; proposed side/door glazing transfer unqualified"),
 dict(url=GLASS,basis="Producer states4mm glass10kg/m2, equivalent density2500kg/m3"),
 dict(url=PC,basis="Rail polycarbonate application exists; coating/fire/scratch/deflection/retention unresolved, so no PC selection credit")]


def encoded(v):
    return (json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()


def _positive(x,name):
    if type(x) not in (int,float) or not math.isfinite(x) or x<=0:
        raise ValueError("finite positive "+name+" required")
    return float(x)


def _hash(v):return sha256(encoded(v)).hexdigest()


def sources(root=ROOT):
    from engineering.ferrite_maglev import candidate_magnetics as canonical
    root=Path(root)
    names=["engineering/ferrite_maglev/data/candidate-retained-body-stock.json",
           "engineering/ferrite_maglev/data/candidate-parent-94ad.json",
           "engineering/ferrite_maglev/station-structure.toml",
           "engineering/ferrite_maglev/station_structure.py",
           "engineering/ferrite_maglev/assembled_body.py",
           "engineering/ferrite_maglev/closure.py",
           "engineering/ferrite_maglev/candidate_magnetics.py",
           "engineering/ferrite_maglev/candidate-magnetics.toml",
           "engineering/vehicle_optimisation/equipment.py"]
    names=set(names)|{p.relative_to(canonical.ROOT).as_posix() for p in canonical.source_paths()}
    return {n:sha256((root/n).read_bytes()).hexdigest() for n in sorted(names)}


def rhs_properties(width_m,depth_m,wall_m):
    b,h,t=(_positive(v,n) for v,n in zip((width_m,depth_m,wall_m),("width","depth","wall")))
    if 2*t>=min(b,h):raise ValueError("RHS requires a nonempty bore")
    area=b*h-(b-2*t)*(h-2*t)
    iy=(b*h**3-(b-2*t)*(h-2*t)**3)/12
    iz=(h*b**3-(h-2*t)*(b-2*t)**3)/12
    return dict(area_m2=area,I_strong_m4=iy,I_weak_m4=iz,
                Z_vertical_m3=2*iy/h,flat_width_m=max(b,h)-2*t)


def same_stiffness_wall(width_m,depth_m,reference_EI,*,young_pa=69e9,min_wall_m=.0015):
    """Match BOTH section bending axes at fixed outer size, or reject."""
    b,h=width_m,depth_m;lo=min_wall_m;hi=min(b,h)/2*(1-1e-8)
    def enough(t):
        s=rhs_properties(b,h,t)
        return all(young_pa*s[k]>=reference_EI[i]*(1-1e-12)
                   for i,k in enumerate(("I_strong_m4","I_weak_m4")))
    if not enough(hi):raise ValueError("reference EI exceeds solid section limit")
    if enough(lo):return lo
    for _ in range(70):
        mid=(lo+hi)/2
        if enough(mid):hi=mid
        else:lo=mid
    return hi


def _stock(identity,volume,density,quantity=1,**kw):
    return dict(id=identity,quantity=quantity,volume_m3_each=volume,
        density_kg_m3=density,unit_mass_kg=volume*density,
        total_volume_m3=volume*quantity,total_mass_kg=volume*density*quantity,
        status="counted-material",**kw)


def _retained(root=ROOT):
    from engineering.ferrite_maglev import candidate_magnetics as canonical
    data=json.loads((Path(root)/"engineering/ferrite_maglev/data/candidate-retained-body-stock.json").read_text())
    rows=[]
    for p in data['parts']:
        mass,_,_=canonical._region_mass_properties(p)
        rows.append(dict(id=p['id'],role=p['role'],mass_kg=mass,part=p))
    if not math.isclose(math.fsum(r['mass_kg'] for r in rows),data['mass_kg_per_car'],abs_tol=1e-7):
        raise ValueError("retained exact signed-volume stock does not close")
    return data,rows


def _members(root=ROOT):
    _,rows=_retained(root);group=defaultdict(list)
    for row in rows:
        p=row['part']
        if p['role'] in ('primary-frame','provisional-replaced-stringers'):
            group[p['parent_member_id']].append(row)
    result=[]
    for name,rs in sorted(group.items()):
        ps=[r['part'] for r in rs]
        low=[min(p['at_m'][i] for p in ps) for i in range(3)]
        high=[max(p['at_m'][i]+p['size_m'][i] for p in ps) for i in range(3)]
        size=[high[i]-low[i] for i in range(3)];axis=max(range(3),key=lambda i:size[i]);cross=[i for i in range(3) if i!=axis]
        # For horizontal members, vertical depth is globalz. For vertical posts
        # both bending axes are retained without assuming a preferred direction.
        b,h=(size[i] for i in cross)
        wall=min(p['size_m'][i] for p in ps for i in cross)
        prop=rhs_properties(b,h,wall)
        material=ps[0]['material'];E={'gfrp':20e9,'aluminium':69e9,'steel':200e9}[material]
        result.append(dict(id=name,length_m=size[axis],width_m=b,depth_m=h,wall_m=wall,
            axis=axis,at_m=low,outer_size_m=size,material=material,young_pa=E,
            reference_EI_N_m2=[E*prop['I_strong_m4'],E*prop['I_weak_m4']],
            counted_net_mass_kg=math.fsum(r['mass_kg'] for r in rs),
            part_ids=[r['id'] for r in rs],holes=sum(len(p.get('holes',[])) for p in ps)))
    if len(result)!=65:raise ValueError("retained65-member reference changed; audit new topology")
    return result


def chassis_candidates(*,root=ROOT,comparison_mass_kg_per_car=37618.591500334303,
                       roof_support_modules=24):
    mass=_positive(comparison_mass_kg_per_car,'AW3 comparison mass')
    if type(roof_support_modules) is not int or roof_support_modules!=24:
        raise ValueError("this bounded roof support layout has24 local modules")
    original=_members(root);results=[]
    designs=[('6061-T6-envelope',240e6,1.,.0015),
             ('6082-T6-deep-stringers',250e6,1.35,.0015),
             ('6005A-T5-wide-stringers',215e6,1.,.002)]
    for identity,yield_pa,depth_scale,tmin in designs:
        members=[];stock=[]
        rho=2710. if identity.startswith('6082') else 2700.
        for old in original:
            b,h=old['width_m'],old['depth_m'];axis=old['axis']
            if 'lower-stringer' in old['id']:
                h*=depth_scale
                if identity.startswith('6005A'):b*=1.20
            if 'roof-longitudinal' in old['id']:
                # Dedicated hanging-load rail, kept inside the old outer top
                # and side datum. This is geometry, not a body-shell FE result.
                b,h=.12,.25
            wall=same_stiffness_wall(b,h,old['reference_EI_N_m2'],min_wall_m=tmin)
            if 'roof-longitudinal' in old['id']:wall=max(wall,.004)
            prop=rhs_properties(b,h,wall);length=old['length_m']
            q=_stock('extrusion/'+old['id'],prop['area_m2']*length,rho,
                kind='rectangular-hollow-extrusion',axis=axis,length_m=length,
                width_m=b,depth_m=h,wall_m=wall,
                original_part_ids=old['part_ids'],source_member=old['id'],
                drilling='Old holes not credited in gross new stock; drilling/HAZ/fatigue require detailing')
            # Preserve the top/outer side datum of roof rails, not their centre
            # after increasing section depth into the cabin.
            at=list(old['at_m']);cross=[i for i in range(3) if i!=axis]
            if 'lower-stringer' in old['id']:
                at[2]+=old['depth_m']-h
            if 'roof-longitudinal' in old['id']:
                at[2]+=old['depth_m']-h
                if at[1]>0:at[1]+=old['width_m']-b
            q['at_m']=at;stock.append(q)
            members.append(dict(id=old['id'],section=prop,wall_m=wall,width_m=b,depth_m=h,
                length_m=length,reference_EI_N_m2=old['reference_EI_N_m2'],
                proposed_EI_N_m2=[69e9*prop['I_strong_m4'],69e9*prop['I_weak_m4']],
                stiffness_necessary_pass=all(69e9*prop[k]>=old['reference_EI_N_m2'][i]*(1-1e-9)
                   for i,k in enumerate(('I_strong_m4','I_weak_m4')))))
        ends=2*len(members);bolts=4*ends
        # One countable but unqualified bolted/bonded end detail per member end.
        spreader_t=.018 if identity.startswith('6082') else .008
        stock.extend([
          _stock('joints/gusset',.16*.10*.004,2700,2*ends,kind='plate'),
          _stock('joints/M8-shank',math.pi*.008**2/4*.060,7850,bolts,kind='cylinder'),
          _stock('joints/M8-head-and-nut',math.pi*.014**2/4*.012,7850,bolts,kind='machining-stock-envelope',voids_not_credited=True),
          _stock('joints/crush-sleeve',math.pi*(.014**2-.009**2)/4*.060,7850,bolts,kind='tube'),
          _stock('joints/GFRP-isolation',.16*.10*.0015,1900,ends,kind='pad'),
          _stock('joints/bond-film',.16*.10*.0005,1200,ends,kind='bond-layer'),
          _stock('hardpoints/roof-spreader',.30*.22*spreader_t,2700,24,kind='plate',thickness_m=spreader_t),
          _stock('hardpoints/GFRP-isolator',.30*.22*.002,1900,24,kind='pad')])
        load=1.3*mass*9.80665/24;pitch=17/12
        roof=next(m for m in members if 'roof-longitudinal' in m['id']);s=roof['section']
        stress=load*pitch/4/s['Z_vertical_m3']
        deflection=load*pitch**3/(48*69e9*s['I_strong_m4'])
        # HAZ reduction is explicitly a hypothesis; mechanical fasteners avoid
        # deliberate welding but extrusion end processes/weld repairs stay open.
        haz_allowable=.5*yield_pa/1.5
        plate_sigma=6*(load*.08/2)/(.22*spreader_t**2)
        plate_allowable=80e6  # separate unqualified plate-detail study value
        compression=500000/2
        rails=[m for m in members if 'lower-stringer' in m['id']]
        rail=rails[0];si=rail['section'];local=4*math.pi**2*69e9/(12*(1-.33**2))*(rail['wall_m']/si['flat_width_m'])**2
        euler=lambda length:math.pi**2*69e9*min(si['I_strong_m4'],si['I_weak_m4'])/length**2
        result=dict(id=identity,material=dict(alloy=identity.split('-')[0],temper=identity.split('-')[1],
             density_kg_m3=rho,young_pa=69e9,proof_strength_pa=yield_pa,
             modulus_basis='Conservative69GPa study value;6082 producer nominal70GPa',
             weld_HAZ_retention_hypothesis=.5,qualified=False,
             source=HYDRO_6082 if identity.startswith('6082') else HYDRO),
             members=members,stock_parts=stock,member_count=len(members),member_end_count=ends,
             joint_bolt_count=bolts,roof_support_modules=24,
             counted_material_mass_kg=math.fsum(p['total_mass_kg'] for p in stock),
             removed_stock_ids=sorted(x for m in original for x in m['part_ids']),
             removed_counted_frame_kg=math.fsum(m['counted_net_mass_kg'] for m in original),
             screens=dict(comparison_aw3_kg_per_car=mass,normal_load_factor=1.3,
                roof_force_N_per_module=load,roof_pitch_m=pitch,roof_rail_stress_pa=stress,
                roof_rail_deflection_m=deflection,HAZ_allowable_pa=haz_allowable,
                roof_rail_elastic_pass=stress<=haz_allowable and deflection<=.002,
                spreader_plate_thickness_m=spreader_t,spreader_plate_stress_pa=plate_sigma,
                spreader_plate_allowable_pa=plate_allowable,
                spreader_plate_elastic_pass=plate_sigma<=plate_allowable,
                spreader_plate_material_certificate=False,
                coupler_compression_N_per_rail=compression,section_compression_pa=compression/si['area_m2'],
                local_plate_buckling_elastic_pa=local,
                local_buckling_necessary_pass=compression/si['area_m2']<=min(local,haz_allowable),
                euler_full_17m_N=euler(17),euler_assumed_2m_braced_N=euler(2),
                full_length_buckling_pass=compression<=euler(17),bracing_qualified=False),
             retained_interfaces=['GFRP sandwich panels','existing magnetic collectors/hardpoints/fasteners retained separately',
                                  'four1.4x2.1m door apertures','120AW2/160AW3 passengers per car'],
             unknown_installed_inventory=[dict(id='joint-load-transfer-fatigue',mass_kg=None),
                 dict(id='extrusion-end-splices-and-corrosion-protection',mass_kg=None),
                 dict(id='roof-magnetic-retention-and-multiaxis-fault-path',mass_kg=None)],
             installed_mass_kg=None,installed_cg_m=None,
             holds=['65member topology is an analytical extrusion proposal; global body shear/torsion/crash and joints not solved',
                    'Deep/wide stringer packaging, door mechanisms and GFRP bonding interfaces need collision/drawing checks',
                    'Roof rail elastic screen does not pass its spreader, mounting joint or whole load path',
                    'Pinned17m/assumed2m buckling cases are separate; unqualified bracing earns no installed pass',
                    'Manufacturer section/product/temper tolerances and postweld strength require certificates; fatigue remains unknown'],**FLAGS)
        result['proposal_sha256']=_hash(result);results.append(result)
    return results


def _glazing(kind):
    # Eight fixed side windows2x1.5m; eight door windows.5x1m.
    fixed,door=24.,4.;area=fixed+door;perimeter=8*7+8*3
    layers=[('glass',.008,2500)] if kind=='clear-tempered-8mm' else [('glass',.006,2500),('PVB',.00076,1070)]
    stock=[_stock('glazing/'+mat,area*t,rho,area_m2=area,thickness_m=t) for mat,t,rho in layers]
    stock.extend([_stock('glazing/retention-aluminium',perimeter*.020*.003,2700,kind='strip'),
                  _stock('glazing/EPDM-seal',perimeter*.00008,1200,kind='seal'),
                  _stock('glazing/bond',perimeter*.012*.003,1200,kind='bond')])
    return dict(id=kind,fixed_area_m2=fixed,door_area_m2=door,total_area_m2=area,
                fixed_window_count=8,fixed_window_size_m=[2.,1.5],door_window_count=8,
                door_window_size_m=[.5,1.],retention_perimeter_m=perimeter,
                solar_factor_g=.82 if kind=='clear-tempered-8mm' else .55,
                U_W_m2K=5.7,solar_basis='Rounded stationary transport windshield plot; side-window transfer unqualified',
                U_basis='Declared single-glazing heat-transfer screen, not a certified complete window value',
                stock_parts=stock,counted_material_mass_kg=math.fsum(r['total_mass_kg'] for r in stock),
                impact_fire_scratch_retention_qualified=False,opening_windows=False,
                emergency_ventilation_qualified=False,source=SOLAR,
                unknown_installed_inventory=[dict(id='window-certified-frame-coating-retention-and-egress',mass_kg=None)])


def equipment_candidates():
    rows=[]
    for door_kind,skin_t,skin_density,mechanism_mass,source in (
      ('aluminium-sandwich-ES2-reference',.0008,2700.,41.,ES2),
      ('GFRP-sandwich-ESP4C-reference',.0015,1900.,46.,ESP4C)):
        leaf_area=.7*2.1;glass_area=.5*1.;opaque=leaf_area-glass_area
        frame=rhs_properties(.030,.025,.002)
        parts=[_stock('doors/leaf-skins',2*opaque*skin_t,skin_density,8,kind='cut-skin',window_void_m2=glass_area),
               _stock('doors/leaf-core',opaque*.025,80.,8,kind='cut-core',window_void_m2=glass_area),
               _stock('doors/leaf-edge-RHS',frame['area_m2']*2*(.7+2.1),2700.,8,kind='extruded-RHS'),
               _stock('doors/seals',4*2*(1.4+2.1)*.0001,1200.,kind='seal'),
               _stock('doors/bond',8*opaque*.0004,1200.,kind='bond')]
        for glass_kind in ('clear-tempered-8mm','solar-laminated-6.76mm'):
            glazing=_glazing(glass_kind)
            known=math.fsum(r['total_mass_kg'] for r in parts)+glazing['counted_material_mass_kg']
            result=dict(id=door_kind+'/'+glass_kind,door=dict(id=door_kind,door_count=4,
                door_width_m=1.4,door_height_m=2.1,leaves_per_door=2,door_glazing_area_m2=4.,
                physical_leaf_stock_mass_kg=math.fsum(r['total_mass_kg'] for r in parts),
                mechanism_reference_mass_kg_each=mechanism_mass,mechanism_reference_count=4,
                mechanism_reference_mass_kg=4*mechanism_mass,mechanism_source=source,
                mechanism_reference_width_m=1.3,proposed_clear_width_m=1.4,
                complete_BODE_LRV_reference_mass_kg_each=120.,complete_reference_source=BODE,
                complete_door_mass_kg=None,fit_qualified=False),
                glazing=glazing,stock_parts=deepcopy(parts)+glazing['stock_parts'],
                counted_material_mass_kg=known,
                supplier_mechanism_reference_mass_kg=4*mechanism_mass,
                material_plus_reference_subtotal_kg=known+4*mechanism_mass,
                unknown_installed_inventory=glazing['unknown_installed_inventory']+[
                    dict(id='door1400x2100-mechanism-height-adaptation-interlocks-egress',mass_kg=None),
                    dict(id='door-sealing-crash-fire-anti-trap-qualified-assembly',mass_kg=None)],
                hvac_interface=dict(fixed_glazing_area_m2=24.,door_glazing_area_m2=4.,
                    total_glazing_area_m2=28.,solar_factor_g=glazing['solar_factor_g'],U_W_m2K=5.7,
                    platform_side_doors_open=2,open_area_m2=5.88,all_four_doors_area_m2=11.76,
                    open_duration_s=[30,45,60],station_recurrence_s=[120,180],
                    recurrence_is_headway=False,opening_window_cooling_credit=False),
                installed_mass_kg=None,installed_cost=None,payload_AW2=120,payload_AW3=160,
                rejected_polycarbonate=dict(considered=True,source=PC,adopted=False,
                    reason='Rail use is documented but no exact grade/coating thickness, fire/scratch, thermal solar, stiffness, emergency retention and lifetime proof for these2m spans'),**FLAGS)
            result['proposal_sha256']=_hash(result);rows.append(result)
    return rows


def allocation_audit(*,root=ROOT):
    """Prove the old500/500 equipment accounts remain separate from stock."""
    root=Path(root);parent=json.loads((root/'engineering/ferrite_maglev/data/candidate-parent-94ad.json').read_text())['configuration']
    checks={}
    for name in ('station-structure.toml','station_structure.py','closure.py'):
        key='engineering/ferrite_maglev/'+name
        checks[key]=parent['source_sha256'].get(key)==sha256((root/key).read_bytes()).hexdigest()
    if not all(checks.values()):raise ValueError('historical allocation source chain differs; no automatic allocation removal')
    a=tomllib.loads((root/'engineering/ferrite_maglev/station-structure.toml').read_text())
    central=a['body']['cases']['central']
    if (central['doors_kg'],central['fixed_glazing_kg'],a['vehicle']['hvac_kg'])!=(500.,500.,800.):
        raise ValueError('named central equipment allocation changed')
    return dict(source_chain_sha_matches=checks,eligible_removals=[
        dict(id='allocation/station-central/doors_kg',mass_kg=500.,includes='door glass and mechanisms',excludes='fixed side glazing and body aperture frame stock'),
        dict(id='allocation/station-central/fixed_glazing_kg',mass_kg=500.,includes='24m2 fixed side glazing',excludes='door glass')],
        forbidden_overlapping_removals=['5200kg equipped body aggregate','800kg primary load-path allowance',
             '400kg opening joints allowance','800kg HVAC owned separately'],
        basis='Historical parent binds exact station/closure sources. Detailed body stock omits door leaves/mechanisms/glazing; these central budgets survive in canonical unlocated residual.',
        hvac_owned_here=False)


def replacement_ledger(chassis=None,equipment=None,*,root=ROOT,external_removed_stock_ids=(),
                       external_removed_allocation_ids=()):
    from engineering.ferrite_maglev import candidate_magnetics as canonical
    old=canonical.definition();data,rows=_retained(root);audit=allocation_audit(root=root)
    banned=('structural_body_floor_doors_glazing_interior','equipped-body-total',
            'primary_load_paths_kg','opening_joints_inserts_kg')
    if any(any(token in name for token in banned) for name in external_removed_allocation_ids):
        raise ValueError('aggregate/consumed body allowances cannot be removed with counted frame stock')
    removed_ids=[] if chassis is None else list(chassis['removed_stock_ids'])
    eligible={r['id']:r for r in rows if r['role'] in ('primary-frame','provisional-replaced-stringers')}
    if len(set(removed_ids))!=len(removed_ids) or set(removed_ids)-set(eligible):
        raise ValueError('frame removals require exact eligible unique retained IDs')
    for proposal in (chassis,equipment):
        if proposal is not None:
            if proposal.get('proposal_sha256')!=_hash({k:v for k,v in proposal.items() if k!='proposal_sha256'}):
                raise ValueError('equipment proposal payload identity differs')
            if any(proposal.get(k) is not False for k in FLAGS):
                raise ValueError('equipment proposal cannot assert installed acceptance')
    if set(removed_ids)&set(external_removed_stock_ids):raise ValueError('overlapping/double stock removal')
    alloc=[] if equipment is None else deepcopy(audit['eligible_removals'])
    if {r['id'] for r in alloc}&set(external_removed_allocation_ids):raise ValueError('overlapping/double allocation removal')
    removed_stock=math.fsum(eligible[k]['mass_kg'] for k in removed_ids)
    removed_alloc=math.fsum(r['mass_kg'] for r in alloc)
    added_material=(0. if chassis is None else chassis['counted_material_mass_kg'])+(0. if equipment is None else equipment['counted_material_mass_kg'])
    added_reference=0. if equipment is None else equipment['supplier_mechanism_reference_mass_kg']
    delta=added_material+added_reference-removed_stock-removed_alloc
    return dict(source_configuration_sha256=old['configuration_sha256'],source_sha256=sources(root),
        original_tare_kg=old['controlled_tare_kg'],original_AW3_kg=old['controlled_aw3_kg'],
        removed_stock_ids=removed_ids,removed_counted_stock_kg=removed_stock,
        removed_allocation_accounts=alloc,removed_allocation_kg=removed_alloc,
        retained_body_stock_kg=data['mass_kg_per_car']-removed_stock,
        added_counted_material_kg=added_material,added_supplier_reference_kg=added_reference,
        conditional_mass_delta_kg=delta,
        conditional_tare_subtotal_kg=old['controlled_tare_kg']+delta,
        conditional_AW3_subtotal_kg=old['controlled_aw3_kg']+delta,
        old_unlocated_residual_kg=old['mass_accounting']['retained_unlocated_allocation_kg'],
        remaining_unlocated_residual_kg=old['mass_accounting']['retained_unlocated_allocation_kg']-removed_alloc,
        HVAC_removal_kg=0.,passenger_payload_kg=12000.,AW2_passengers=120,AW3_passengers=160,
        allocation_audit=audit,installed_tare_kg=None,installed_AW3_kg=None,installed_CG_m=None,
        scope='Conditional material+supplier-reference substitution; unknown installed equipment/joints and whole vehicle structure prevent a mass acceptance',**FLAGS)


def study(*,root=ROOT,comparison_mass_kg_per_car=37618.591500334303,roof_support_modules=24):
    before=sources(root)
    chassis=chassis_candidates(root=root,comparison_mass_kg_per_car=comparison_mass_kg_per_car,
                               roof_support_modules=roof_support_modules)
    equipment=equipment_candidates();combinations=[]
    for c in chassis:
        for e in equipment:
            ledger=replacement_ledger(c,e,root=root)
            combinations.append(dict(chassis_id=c['id'],equipment_id=e['id'],ledger=ledger,
                screening=c['screens'],installed_candidate_eligible=False))
    if before!=sources(root):raise ValueError('equipment source changed during study')
    return dict(schema=SCHEMA,source_sha256=before,references=REFERENCES,
        chassis=chassis,equipment=equipment,combinations=combinations,
        combination_count=len(combinations),sampled_not_global_optimum=True,
        allocation_audit=allocation_audit(root=root),comparison_mass_kg_per_car=comparison_mass_kg_per_car,
        payload=dict(cars=6,AW2_passengers_per_car=120,AW3_passengers_per_car=160,
                     passenger_mass_kg=75,door_count_per_car=4,door_aperture_m=[1.4,2.1]),
        installed_mass_kg=None,selected_integrated_candidate=None,**FLAGS)
