"""Transportable station assemblies and explicit dead/crowd/plant load paths.

A manufactured geometry/quantity hypothesis is not a verified reinforced or
prestressed concrete design. Ground, capacity, seismic, erection, accessibility
and actual plant interfaces retain independent engineering holds.
"""
from pathlib import Path
from copy import deepcopy
from math import pi,ceil,fsum,isfinite
from . import ROOT,FLAGS,identity,digest

CODE='engineering/railway_progress/civil.py'
G=9.80665
RAIL_TOP_GLOBAL_Z_M=8.99


def _sha(x):return isinstance(x,str) and len(x)==64 and all(c in '0123456789abcdef' for c in x)


def uniform_reactions(start,end,weight,beam_start,beam_end):
    if not all(type(x) in (int,float) and isfinite(x) for x in (start,end,weight,beam_start,beam_end)) or end<=start or beam_end<=beam_start or weight<0:raise ValueError('Finite positive intervals and nonnegative load required')
    lo=max(start,beam_start);hi=min(end,beam_end)
    if hi<=lo:return 0.,0.
    F=weight*(hi-lo)/(end-start);center=(lo+hi)/2
    return F*(beam_end-center)/(beam_end-beam_start),F*(center-beam_start)/(beam_end-beam_start)


def _physical(rows):
    keys=('id','assembly','role','kind','dimensions_m','at_m','geometry','material_grade','manufacturing')
    return [{k:p.get(k) for k in keys} for p in rows]


def geometry_definition(vehicle,distance_m,alternative,*,platform_crowd_pressure_Pa=5000.,root=ROOT):
    if distance_m not in (1500.,2000.) or type(platform_crowd_pressure_Pa) not in (int,float) or not isfinite(platform_crowd_pressure_Pa) or platform_crowd_pressure_Pa<0:raise ValueError('Owned route and explicit crowd pressure hypothesis required')
    if vehicle.get('evaluation_id')!=identity({k:v for k,v in vehicle.items() if k!='evaluation_id'}):raise ValueError('Current owned vehicle required')
    if alternative.get('evaluation_id')!=identity({k:v for k,v in alternative.items() if k!='evaluation_id'}) or alternative['body_candidate_id']!=vehicle['candidate_id'] or alternative['physical_definition']['service']['distance_m']!=distance_m:
        raise ValueError('Same vehicle and route alternative required')
    rows=[];unknown=[];station_records=[];guideway_records=[];known_plant=[];unknown_plant=[]
    def solid(name,assembly,role,dims,at,grade='research-C40/50-concrete',density=2500.,*,kind='box',volume=None,geometry=None,process='form-reinforce-cast-cure-inspect'):
        V=dims[0]*dims[1]*dims[2] if volume is None else volume
        if V<=0:raise ValueError('Positive net solid volume required')
        r=dict(id=name,assembly=assembly,role=role,kind=kind,dimensions_m=list(dims),at_m=list(at),
            geometry=deepcopy(geometry or dict(kind=kind,dimensions_m=list(dims))),material_grade=grade,
            nominal_density_kg_m3=density,net_volume_m3=V,calculated_mass_kg=V*density,
            mass_bounds_kg=[V*density,V*density],mass_basis='calculated-hypothesis-not-measured',manufacturing=process,
            structural_accepted=False,supplier_origin=None)
        r['physical_definition_id']=identity(_physical([r])[0]);rows.append(r);return r
    def purchased(name,assembly,role,dimensions,at,bounds,method='procure-inspect-install; supplier drawing pending'):
        r=dict(id=name,assembly=assembly,role=role,kind='purchased-envelope',dimensions_m=dimensions,at_m=at,
            geometry=dict(kind='purchased-envelope',dimensions_m=dimensions),material_grade=None,
            nominal_density_kg_m3=None,net_volume_m3=None,calculated_mass_kg=None,mass_bounds_kg=bounds,
            mass_basis='explicit-research-bounds' if bounds is not None else 'unknown',manufacturing=method,
            structural_accepted=False,supplier_origin=None)
        r['physical_definition_id']=identity(_physical([r])[0]);rows.append(r)
        if bounds is None:unknown.append(name)
        return r
    # Ordinary directional interstation spans retain explicit net hollow geometry.
    start=-120.;end=distance_m+20.;L=20.;n=int(round((end-start)/L))
    for i in range(n):
        x=start+i*L;assembly=f'guideway/span/{i}'
        outer=[L,1.8,.8];inner=[L,1.5,.5];duct_volume=12*pi*.0125**2*L;volume=L*(1.8*.8-1.5*.5)-duct_volume
        beam=solid(assembly+'/box',assembly,'guideway-beam',outer,[x,-.9,8.],kind='hollow-box',volume=volume,
            geometry=dict(kind='hollow-box',outer_dimensions_m=outer,void_dimensions_m=inner,void_offset_m=[0.,.15,.15],ducts=dict(count=12,diameter_m=.025,length_m=L,net_void_volume_m3=duct_volume)))
        # Explicit area/mass and envelope; wire twist and anchor detailing remain open.
        for k in range(12):solid(assembly+f'/strand/{k}',assembly,'prestressing-strand',[L,.0152,.0152],[x,-.66+k*.12,8.07],
            'research-strand-1770-grade-not-qualified',7850.,kind='strand-equivalent-metal',volume=.00014*L,
            geometry=dict(kind='strand-equivalent-metal',length_m=L,metal_area_m2=.00014,envelope_diameter_m=.0152),process='tension-anchor-cast-cure-release; losses and anchor qualification pending')
        solid(assembly+'/strand-duct-grout',assembly,'duct-grout',[L,.025,.025],[x,0.,8.07],
            'research-duct-grout',2200.,kind='equivalent-grout-annuli',volume=duct_volume-12*.00014*L,
            geometry=dict(kind='twelve-duct-annuli-minus-counted-strand-metal',duct_count=12,duct_diameter_m=.025,length_m=L,strand_metal_area_m2=.00014),
            process='pressure-grout-inspect; actual strand/grout/void qualification pending')
        for y in (-.7175,.7175):
            purchased(assembly+f'/rail/{y}',assembly,'rail',[L,.15,.172],[x,y-.075,8.818],[60.*L,65.*L])
            for k in range(34):solid(assembly+f'/baseplate/{y}/{k}',assembly,'rail-baseplate',[.24,.17,.018],[x+k*L/34,y-.085,8.8],
                'research-structural-steel',7850.,process='cut-drill-coat-anchor-inspect')
        for side in (-1,1):purchased(assembly+f'/bearing/{side}',assembly,'guideway-bearing',[.35,.35,.06],[x,side*.55,7.94],[20.,60.])
        guideway_records.append(dict(id=assembly,start_m=x,end_m=x+L))
    for i in range(n+1):
        x=start+i*L;assembly=f'guideway/support/{i}'
        for role,dims,at in [('footing',[4.,4.,1.2],[x-2.,-2.,-1.2]),('pier',[.9,.9,7.4],[x-.45,-.45,0.]),('headstock',[1.2,2.6,.54],[x-.6,-1.3,7.4])]:solid(assembly+'/'+role,assembly,'guideway-'+role,dims,at)
    # Floor level follows the actual placed primitive, not a nominal rail offset.
    defs={p['physical_definition_id']:p for p in vehicle['registry']['parts']}
    floor=[o['transform'][2][3]+defs[o['part_definition_id']]['geometry']['dimensions_m'][2]/2
           for o in vehicle['registry']['occurrences'] if o['occurrence_id'].startswith('car-1/') and 'FLOOR-FACE' in defs[o['part_definition_id']]['part_id']]
    floor_top=max(floor) if floor else vehicle.get('interfaces',{}).get('floor_top_above_rail_m')
    if floor_top is None:raise ValueError('Actual vehicle floor primitive or explicit owned floor interface required')
    door_side=-1 if vehicle.get('interfaces',{}).get('door_side_y_m',-1.4)<0 else 1
    y0=-5.95 if door_side<0 else 1.45;rows_y=[y0+.15,y0+4.35];top=RAIL_TOP_GLOBAL_Z_M+floor_top
    cassette_L=5.5;width=4.5;thickness=.18;bay=11.;bay_count=10
    for station,origin in enumerate((-110.,distance_m-110.)):
        station_id=f'station/{station}';cassettes=[];girders=[];supports=[]
        for j in range(20):
            x=origin+j*cassette_L;assembly=station_id+f'/cassette/{j}'
            steel=[];cover=.035;d=.012;area=pi*d*d/4
            for layer,z in enumerate((top-thickness+cover+d/2,top-cover-d/2)):
                for k in range(30):
                    name=assembly+f'/x-bar/{layer}/{k}';length=cassette_L-2*cover
                    at=[x+cover,y0+cover+k*(width-2*cover)/29,z]
                    steel.append(solid(name,assembly,'cassette-rebar',[length,d,d],at,'research-B500-rebar',7850.,kind='straight-bar',volume=area*length,
                        geometry=dict(kind='straight-circular-bar',axis='x',length_m=length,diameter_m=d),process='cut-tie-inspect; anchorage/cover design pending'))
                transverse_z=z+(d if layer==0 else -d)
                for k in range(37):
                    name=assembly+f'/y-bar/{layer}/{k}';length=width-2*cover;at=[x+cover+k*(cassette_L-2*cover)/36,y0+cover,transverse_z]
                    steel.append(solid(name,assembly,'cassette-rebar',[d,length,d],at,'research-B500-rebar',7850.,kind='straight-bar',volume=area*length,
                        geometry=dict(kind='straight-circular-bar',axis='y',length_m=length,diameter_m=d),process='cut-tie-inspect; anchorage/cover design pending'))
            steel_V=fsum(p['net_volume_m3'] for p in steel);gross=cassette_L*width*thickness
            deck=solid(assembly+'/concrete',assembly,'station-cassette',[cassette_L,width,thickness],[x,y0,top-thickness],volume=gross-steel_V,
                kind='reinforced-panel-net-concrete',geometry=dict(kind='box-minus-owned-rebar-volumes',outer_dimensions_m=[cassette_L,width,thickness],
                    excluded_rebar_ids=[p['id'] for p in steel],excluded_rebar_volume_m3=steel_V),process='repeatable-cassette-mould-mesh-cast-cure-lift-inspect')
            for side,yy in enumerate(rows_y):
                for xx in (x+.15,x+cassette_L-.15):purchased(assembly+f'/pad/{side}/{xx}',assembly,'deck-pad',[.20,.15,.02],[xx,yy,top-thickness-.02],[1.,3.])
            for k in range(4):purchased(assembly+f'/lifting-insert/{k}',assembly,'lifting-insert',[.06,.06,.12],[x+(.7 if k<2 else cassette_L-.7),rows_y[k%2],top-.12],[2.,5.])
            for side in (0,1):purchased(assembly+f'/joint/{side}',assembly,'cassette-joint-and-retention',[.02,width,.04],[x+side*cassette_L,y0,top-.04],None)
            cassettes.append(dict(id=assembly,start_m=x,end_m=x+cassette_L,width_m=width,area_m2=cassette_L*width,
                known_dead_weight_N=fsum(p['mass_bounds_kg'][0] for p in rows if p['assembly']==assembly and p['mass_bounds_kg'] is not None)*G,
                purchased_and_joint_mass_basis='Calculated net stock plus explicit C purchased lower bounds; unbounded joints remain unknown',
                crowd_load_N=cassette_L*width*platform_crowd_pressure_Pa,
                bearing_rows_y_m=rows_y,concrete_net_volume_m3=deck['net_volume_m3'],steel_volume_m3=steel_V,
                gross_outer_volume_m3=gross,transport_dimensions_m=[cassette_L,width,thickness],casting_mould_id='platform-5.5x4.5x.18'))
        capital_h=.55;column_h=top-thickness-.02-.65-.06-capital_h
        for side,y in enumerate(rows_y):
            for j in range(bay_count):
                x=origin+j*bay;assembly=station_id+f'/girder/{side}/{j}'
                girder=solid(assembly+'/concrete',assembly,'station-longitudinal-girder',[bay,.45,.65],[x,y-.225,top-thickness-.02-.65],process='precast-station-girder; prestress/shear schedule pending')
                for end_index,xx in enumerate((x,x+bay)):purchased(assembly+f'/bearing/{end_index}',assembly,'station-girder-bearing',[.4,.4,.06],[xx,y-.2,top-thickness-.02-.65-.06],[25.,80.])
                girders.append(dict(id=assembly,start_m=x,end_m=x+bay,row=side,known_own_weight_N=fsum(p['mass_bounds_kg'][0] for p in rows if p['assembly']==assembly and p['mass_bounds_kg'] is not None)*G))
            for j in range(bay_count+1):
                x=origin+j*bay;assembly=station_id+f'/support/{side}/{j}';parts=[]
                for role,dims,at in [('footing',[2.8,2.8,1.1],[x-1.4,y-1.4,-1.1]),('column',[.55,.55,column_h],[x-.275,y-.275,0.]),('capital',[.9,.9,capital_h],[x-.45,y-.45,column_h])]:
                    parts.append(solid(assembly+'/'+role,assembly,'station-'+role,dims,at))
                supports.append(dict(id=assembly,x_m=x,row=side,known_self_weight_N=fsum(p['calculated_mass_kg'] for p in parts)*G,
                    footing_area_m2=2.8**2,soil_allowable_Pa=None,settlement_limit_m=None))
        station_records.append(dict(id=station_id,origin_m=origin,cassettes=cassettes,girders=girders,supports=supports,
            platform_top_above_declared_rail_m=floor_top,platform_side=door_side,boarding_gap_hypothesis_m=.05,boarding_accessibility_qualified=False))
    # Materialized propulsion masses keep actual longitudinal definitions. Unknown
    # motor/cooling/fixture masses remain unknown and cannot disappear into zero.
    for p in alternative['inventory']:
        if p['installation']!='wayside':continue
        mass=p.get('calculated_mass_kg',p.get('mass_kg'))
        if mass is None:mass=p.get('catalogue_mass_kg')
        if p.get('distributed_mass_model'):
            d=p['distributed_mass_model'];known_plant.append(dict(id=p['part_id'],start_m=d['start_m'],end_m=d['end_m'],
                mass_kg=(d['end_m']-d['start_m'])*d['straight_return_legs']*d['mass_kg_per_m'],kind='uniform-interval',provenance='catalogue-mass-with-declared-two-leg-routing'))
            wrap=d['end_wrap_length_m']*d['mass_kg_per_m']/2
            known_plant.extend(dict(id=p['part_id']+'/wrap/'+str(i),x_m=x,mass_kg=wrap,kind='point-mounting-hypothesis') for i,x in enumerate((d['start_m'],d['end_m'])))
        elif p.get('longitudinal_instance_centres_m') is not None:
            centres=p['longitudinal_instance_centres_m']
            if len(centres)!=p['count']:raise ValueError('Plant count/location mismatch')
            for i,x in enumerate(centres):
                target=unknown_plant if mass is None else known_plant
                target.append(dict(id=p['part_id']+'/'+str(i),x_m=x,mass_kg=mass,kind='unknown-point-mass' if mass is None else 'point-mounting-hypothesis',provenance=p.get('placement_basis')))
        elif mass is not None and p.get('at_m') is not None:
            x=p['at_m'][0];size=p.get('size_m')
            known_plant.append(dict(id=p['part_id'],start_m=x,end_m=x+size[0],mass_kg=mass,kind='uniform-interval') if size else dict(id=p['part_id'],x_m=x,mass_kg=mass,kind='point-mounting-hypothesis'))
        else:unknown_plant.append(dict(id=p['part_id'],x_m=None,mass_kg=None,kind='unlocated-or-unknown-mass'))
    geometry=dict(route_interval_m=[start,end],rail_top_global_z_m=RAIL_TOP_GLOBAL_Z_M,distance_m=distance_m,guideway_spans=guideway_records,
        station_platform_transport_length_m=cassette_L,station_longitudinal_bay_m=bay,
        station_count=2,stations=[{k:s[k] for k in ('id','origin_m','platform_side','platform_top_above_declared_rail_m')} for s in station_records],
        stock_geometry=_physical(rows),alternative_physical_definition=alternative['physical_definition'])
    geo_id=identity(geometry)
    value=dict(schema='osr-progress-civil-definition/1',body_candidate_id=vehicle['candidate_id'],alternative_candidate_id=alternative['candidate_id'],
        distance_m=distance_m,geometry=geometry,physical_geometry_id=geo_id,geometry_definition_id=geo_id,
        stock=rows,station_records=station_records,guideway_records=guideway_records,known_plant_loads=known_plant,
        unknown_plant_loads=unknown_plant,unknown_mass_items=unknown,platform_crowd_pressure_Pa=platform_crowd_pressure_Pa,
        input_vehicle_evaluation_id=vehicle['evaluation_id'],input_alternative_evaluation_id=alternative['evaluation_id'],
        source_sha256={CODE:digest(Path(root)/CODE),'engineering/railway_progress/alternatives.py':digest(Path(root)/'engineering/railway_progress/alternatives.py'),'engineering/railway_progress/data/alternatives-sources.json':digest(Path(root)/'engineering/railway_progress/data/alternatives-sources.json')},**FLAGS)
    value['definition_id']=identity(value);return value


def generate(candidate_id,definition,*,root=ROOT):
    if not _sha(candidate_id) or definition.get('schema')!='osr-progress-civil-definition/1' or definition.get('definition_id')!=identity({k:v for k,v in definition.items() if k!='definition_id'}):raise ValueError('Exact candidate and immutable civil definition required')
    if any(digest(Path(root)/n)!=h for n,h in definition['source_sha256'].items()):raise ValueError('Civil definition source epoch differs')
    if identity(definition['geometry'])!=definition['physical_geometry_id'] or definition['physical_geometry_id']!=definition['geometry_definition_id'] or _physical(definition['stock'])!=definition['geometry']['stock_geometry']:
        raise ValueError('Civil physical geometry identity differs')
    stations=[];station_known_dead=station_crowd=station_to_ground=0.
    stock=deepcopy(definition['stock'])
    for p in stock:p['candidate_id']=candidate_id
    for station in definition['station_records']:
        columns={s['id']:dict(s,known_superstructure_dead_N=0.,crowd_N=0.,unknown_supplemental_dead_mass=True) for s in station['supports']}
        girder_results=[]
        for g in station['girders']:
            left=right=g['known_own_weight_N']/2;crowd_left=crowd_right=0.
            for deck in station['cassettes']:
                a,b=uniform_reactions(deck['start_m'],deck['end_m'],deck['known_dead_weight_N']/2,g['start_m'],g['end_m']);left+=a;right+=b
                a,b=uniform_reactions(deck['start_m'],deck['end_m'],deck['crowd_load_N']/2,g['start_m'],g['end_m']);crowd_left+=a;crowd_right+=b
            j=int(round((g['start_m']-station['origin_m'])/11));key=station['id']+f'/support/{g["row"]}/'
            columns[key+str(j)]['known_superstructure_dead_N']+=left;columns[key+str(j+1)]['known_superstructure_dead_N']+=right
            columns[key+str(j)]['crowd_N']+=crowd_left;columns[key+str(j+1)]['crowd_N']+=crowd_right
            girder_results.append(dict(id=g['id'],known_dead_reactions_N=[left,right],crowd_reactions_N=[crowd_left,crowd_right],qualified_capacity_Nm=None))
        deck_dead=fsum(d['known_dead_weight_N'] for d in station['cassettes']);girder_dead=fsum(g['known_own_weight_N'] for g in station['girders']);crowd=fsum(d['crowd_load_N'] for d in station['cassettes'])
        for row in columns.values():
            row['known_total_dead_to_ground_N']=row['known_superstructure_dead_N']+row['known_self_weight_N']
            row['conditional_known_pressure_with_crowd_Pa']=(row['known_total_dead_to_ground_N']+row['crowd_N'])/row['footing_area_m2']
            row['complete_service_pressure_Pa']=None;row['bearing_accepted']=False
        total_ground=fsum(s['known_total_dead_to_ground_N'] for s in columns.values());selfdead=fsum(s['known_self_weight_N'] for s in columns.values())
        stations.append(dict(id=station['id'],cassettes=station['cassettes'],girders=girder_results,supports=list(columns.values()),
            known_superstructure_dead_N=deck_dead+girder_dead,crowd_N=crowd,known_self_dead_N=selfdead,known_to_ground_N=total_ground,
            dead_force_residual_N=total_ground-(deck_dead+girder_dead+selfdead),crowd_force_residual_N=fsum(s['crowd_N'] for s in columns.values())-crowd,
            live_load_is_unapproved_hypothesis=True,complete_installed_station_mass_kg=None))
        station_known_dead+=deck_dead+girder_dead+selfdead;station_crowd+=crowd;station_to_ground+=total_ground
    spans=definition['guideway_records'];react=[0.]*(len(spans)+1);plant_mapped=0.;unknown_supports=set();span_results=[]
    known_plant=definition['known_plant_loads'];unknown_plant=definition['unknown_plant_loads']
    for i,g in enumerate(spans):
        local=[p for p in stock if p['assembly']==g['id']];own=fsum(p['mass_bounds_kg'][0] for p in local if p['mass_bounds_kg'] is not None)*G
        left=right=own/2
        for p in known_plant:
            if p['kind']=='uniform-interval':a,b=uniform_reactions(p['start_m'],p['end_m'],p['mass_kg']*G,g['start_m'],g['end_m'])
            elif g['start_m']<=p['x_m']<g['end_m'] or i==len(spans)-1 and p['x_m']==g['end_m']:
                a=p['mass_kg']*G*(g['end_m']-p['x_m'])/(g['end_m']-g['start_m']);b=p['mass_kg']*G-a
            else:a=b=0.
            left+=a;right+=b;plant_mapped+=a+b
        for p in unknown_plant:
            if p.get('x_m') is None or g['start_m']<=p['x_m']<=g['end_m']:unknown_supports.update((i,i+1))
        react[i]+=left;react[i+1]+=right
        span_results.append(dict(id=g['id'],known_dead_reactions_N=[left,right],unknown_installed_load=True,qualified_capacity_Nm=None))
    known_guideway_dead=fsum(p['mass_bounds_kg'][0]*G for p in stock if p['assembly'].startswith('guideway/span/') and p['mass_bounds_kg'] is not None)
    plant_weight=fsum(p['mass_kg']*G for p in known_plant)
    construction=[]
    for station in stations:
        for deck in station['cassettes']:
            construction.append(dict(asset_id=deck['id'],candidate_id=candidate_id,transport_dimensions_m=deck['transport_dimensions_m'],
                known_lower_hook_mass_kg=deck['known_dead_weight_N']/G,rigging_mass_kg=None,complete_hook_mass_kg=None,
                mould_id=deck['casting_mould_id'],curing_hours=None,crew_hours=None,predecessors=['approved-ground-and-foundations','erect-station-columns-and-girders'],
                sequence=['reinforcement-and-cast-in-record','cast','cure-to-measured-release-strength','inspect','transport','rated-four-point-lift','survey-bearing-joint-retain'],QA_certificate=None))
    mass_known=fsum(p['calculated_mass_kg'] for p in stock if p['calculated_mass_kg'] is not None)
    bound_lo=fsum(p['mass_bounds_kg'][0] for p in stock if p['mass_bounds_kg'] is not None);bound_hi=fsum(p['mass_bounds_kg'][1] for p in stock if p['mass_bounds_kg'] is not None)
    result=dict(schema='osr-modular-station-civil-evaluation/1',candidate_id=candidate_id,body_candidate_id=definition['body_candidate_id'],alternative_candidate_id=definition['alternative_candidate_id'],
        physical_geometry_id=definition['physical_geometry_id'],geometry_definition_id=definition['geometry_definition_id'],definition_id=definition['definition_id'],stock=stock,
        known_material_mass_kg=mass_known,known_mass_bounds_kg=[bound_lo,bound_hi],unknown_mass_items=definition['unknown_mass_items'],
        known_plant_mass_kg=plant_weight/G,unknown_plant_mass_items=[p['id'] for p in unknown_plant],
        station_count=2,station_cassette_count=40,station_support_count=sum(len(s['supports']) for s in stations),stations=stations,
        station_known_dead_weight_N=station_known_dead,station_crowd_weight_N=station_crowd,station_known_to_ground_N=station_to_ground,
        station_dead_force_residual_N=station_to_ground-station_known_dead,guideway_span_count=len(spans),guideway_span_reactions=span_results,
        guideway_known_support_reactions_N=react,guideway_supports_with_unknown_plant_mass=sorted(unknown_supports),
        known_guideway_force_residual_N=fsum(react)-known_guideway_dead-plant_weight,known_plant_assignment_residual_N=plant_mapped-plant_weight,
        load_distribution_hypothesis='Uniform net cassette dead load split equally to two longitudinal girders; exact simple-support reactions for this declared load model, not validated deck stiffness/contact response',
        known_reaction_mass_basis='Calculated stock and C purchased lower bounds; unknown station joints/plant and full installed upper loads remain held',
        operational_drive_force_requests=None,actual_dynamic_wheel_rail_or_plant_forces_validated=False,
        source_sha256=definition['source_sha256'],construction_sequence=construction,complete_installed_mass_kg=None,
        complete_civil_installed_cost_usd=None,physical_capacity_accepted=False,
        open_items=['Qualified strength/prestress/shear/punching/torsion, real material/anchorage and joint fatigue/cover',
            'Actual geotechnics, ground/utility fit, settlement/seismic/flood/lateral/erection and station supports',
            'Unpriced/unweighed joint, bearing, rigging, supply/cooling plant and actual crane/crew/access windows',
            'Rail profile/seat/TOR, boarding gap/height/dynamics, ramps/lifts/stairs, containment and evacuation qualification',
            'Unknown plant masses remain open; known support reactions are not complete foundation loads'],**FLAGS)
    result['evaluation_id']=identity(result);return result
