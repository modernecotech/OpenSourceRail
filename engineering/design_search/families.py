"""First counted carrier/guidebeam families using current native stock and plant."""
from copy import deepcopy
from functools import lru_cache
import math

from .contracts import UnknownInstalledStock, identity, inventory_summary, make_candidate, mass_properties, validate_candidate

EYE=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
DEFAULT_REQUIREMENT_REVISION='BAGHDAD-CANDIDATE-REQUIREMENTS-1'


class UnsupportedCandidateDomain(ValueError):
    """A valid physical bundle which these registered native adapters cannot solve."""


@lru_cache(maxsize=1)
def _native():
    from engineering.ferrite_maglev import candidate_magnetics as magnetic, candidate_structures as structures
    definition=magnetic.definition();mass=structures.mass_properties(definition)
    return definition,mass


def physical_module(module):
    # Reluctance core-path allocations/leakage hypotheses are evaluator inputs,
    # never new pieces of steel or a new physical candidate identity.
    return {key:deepcopy(module[key]) for key in ('parts','coils','permanent_magnet','stationary_return_rail',
        'lift_pole_area_m2','guide_pole_area_m2','mass_kg')}


def _box(uid,size,at,material='carrier-steel',density=7850.,*,role=None):
    volume=math.prod(size);mass=volume*density;cg=[at[i]+size[i]/2 for i in range(3)]
    inertia=[[mass*sum(size[k]**2 for k in range(3) if k!=i)/12 if i==j else 0. for j in range(3)] for i in range(3)]
    geometry=dict(id=uid,kind='box',frame_id='vehicle',material_id=material,size_m=list(size),at_m=list(at))
    if role is not None:geometry['role']=role
    item=dict(id=uid,geometry_id=uid,scope='vehicle-per-car',frame_id='vehicle',quantity=1,status='known',
        unit_mass_kg=mass,cg_m=cg,inertia_kg_m2=inertia,basis='exact solid-box integral at declared material density')
    return geometry,item


def _tube(uid,length,at,axis,wall):
    # Four disjoint rectangular walls: no fictitious solid RHS mass.
    breadth,depth=.08,.12;u,v=[i for i in range(3) if i!=axis];parts=[]
    for side in (0,1):
        size=[0.,0.,0.];size[axis]=length;size[u]=wall;size[v]=depth;pos=list(at);pos[u]+=side*(breadth-wall)
        parts.append(_box(uid+'/u'+str(side),size,pos,role='added-carrier-stock'))
    for side in (0,1):
        size=[0.,0.,0.];size[axis]=length;size[u]=breadth-2*wall;size[v]=wall;pos=list(at);pos[u]+=wall;pos[v]+=side*(depth-wall)
        parts.append(_box(uid+'/v'+str(side),size,pos,role='added-carrier-stock'))
    return parts


def _carrier_stock(mode,count,wall=.006):
    if mode=='rigid-existing-hardpoints':return [],[]
    positions=[-5.5+i for i in range(12)];groups=[]
    small,extra=divmod(12,count);start=0
    for index in range(count):
        n=small+(index<extra);groups.append(positions[start:start+n]);start+=n
    geometry=[];inventory=[]
    for number,group in enumerate(groups):
        left,right=min(group)-.46,max(group)+.46;length=right-left
        # Crossbars own the end regions; longitudinal members terminate before
        # them, avoiding double-counted welded intersection material.
        for side in (-1,1):
            for part,item in _tube(f'carrier/{number}/long/{side}',length-.16,[left+.08,side*.88-.04,-.64],0,wall):geometry.append(part);inventory.append(item)
        for end in (left,right-.08):
            for part,item in _tube(f'carrier/{number}/cross/{end:g}',2.8,[end,-1.4,-.64],1,wall):geometry.append(part);inventory.append(item)
        geometry.append(dict(id=f'carrier/{number}/joint-envelope',kind='unresolved-interface',frame_id='vehicle',material_id='unresolved-equipment',
            pivot_m=[sum(group)/len(group),0.,-.50],degree_of_freedom='yaw' if mode=='fixed-yaw-pivots' else 'yaw-and-lateral-slide'))
        for system in (['yaw-bearing-and-retention'] if mode=='fixed-yaw-pivots' else ['yaw-bearing-and-retention','lateral-slide-drive-and-capture']):
            inventory.append(dict(id=f'carrier/{number}/'+system,geometry_id=f'carrier/{number}/joint-envelope',scope='vehicle-per-car',
                frame_id='vehicle',quantity=1,status='unknown',unit_mass_kg=None,cg_m=None,inertia_kg_m2=None,
                basis='Installed bearing/actuator/protection stock is not designed or weighed; no zero-mass credit.'))
    return geometry,inventory


def _build(mode,count,section_id,*,requirement_revision,wall=.006,lineage=None,span_m=25.):
    if mode not in ('rigid-existing-hardpoints','fixed-yaw-pivots','yaw-and-lateral-slide'):
        raise UnsupportedCandidateDomain('unsupported carrier architecture')
    if type(count) is not int or (count!=1 if mode=='rigid-existing-hardpoints' else not 2<=count<=5):
        raise UnsupportedCandidateDomain('unsupported carrier count')
    if type(wall) not in (int,float) or not any(math.isclose(wall,value,rel_tol=0.,abs_tol=1e-12) for value in (.006,.008,.010)):
        raise UnsupportedCandidateDomain('unsupported carrier stock wall')
    if mode=='rigid-existing-hardpoints' and wall!=.006:
        raise UnsupportedCandidateDomain('rigid reference has no added RHS wall variable')
    from engineering.ferrite_maglev import candidate_structures as structures
    definition,native_mass=_native();a=structures.load();section=next(row for row in a['beam_sections'] if row['id']==section_id)
    materials=[dict(id='source-region',density_kg_m3=None,basis='Current native signed-stock integrals; per-region source density retained'),
        dict(id='carrier-steel',density_kg_m3=7850.,basis='Declared current structural steel density; unqualified material'),
        dict(id='concrete',density_kg_m3=a['concrete']['density_kg_m3'],basis='Current45MPa concrete study hypothesis'),
        dict(id='unresolved-equipment',density_kg_m3=None,basis='Unresolved installed interface/equipment, not zero mass')]
    frames=[dict(id='vehicle',parent_id=None,origin_m=[0.,0.,0.],rotation_matrix=EYE,axes=['longitudinal','left','up']),
        dict(id='guidebeam',parent_id=None,origin_m=[0.,0.,0.],rotation_matrix=EYE,axes=['span','left','up'])]
    geometry=[dict(id='magnetic-module',kind='assembly',frame_id='vehicle',material_id='source-region',definition=physical_module(definition['module'])),
        dict(id='propulsion-band',kind='assembly',frame_id='vehicle',material_id='source-region',definition=deepcopy(definition['propulsion_band']))]
    inventory=[]
    for region in native_mass['regions']:
        uid='native/'+region['id'];unlocated=region['id']=='unlocated-retained-allocation'
        geom=dict(id=uid,kind='unlocated-mass-budget' if unlocated else 'native-stock-region',frame_id='vehicle',material_id='source-region')
        if not unlocated:
            geom['definition']={key:deepcopy(region[key]) for key in ('size_m','gravity_projection') if key in region}
        geometry.append(geom)
        inventory.append(dict(id=uid,geometry_id=uid,scope='vehicle-per-car',frame_id='vehicle',quantity=1,status='known',
            unit_mass_kg=region['mass_kg'],cg_m=None if unlocated else region['cg_m'],inertia_kg_m2=None if unlocated else region['inertia_kg_m2'],
            basis='Retained unlocated mass is counted; actual installed CG/inertia unknown.' if unlocated else region['distribution']))
    added_parts,added_inventory=_carrier_stock(mode,count,wall);geometry+=added_parts;inventory+=added_inventory
    if type(span_m) not in (float,int) or not 15.<=span_m<=35.:raise UnsupportedCandidateDomain('bounded15..35m span required')
    span=float(span_m);b,h,tw,tf=[section[key] for key in ('width_m','depth_m','web_m','flange_m')]
    geometry.append(dict(id='guidebeam/section-definition',kind='hollow-concrete-section',frame_id='guidebeam',material_id='concrete',definition=deepcopy(section)))
    top=a['rail_support']['beam_top_z_m'];end=a['concrete']['end_block_length_m']
    concrete_parts=[([span,b,tf],[-span/2,-b/2,top-tf]),([span,b,tf],[-span/2,-b/2,top-h]),
        ([span,tw,h-2*tf],[-span/2,-b/2,top-h+tf]),([span,tw,h-2*tf],[-span/2,b/2-tw,top-h+tf]),
        ([end,b-2*tw,h-2*tf],[-span/2,-b/2+tw,top-h+tf]),
        ([end,b-2*tw,h-2*tf],[span/2-end,-b/2+tw,top-h+tf])]
    for number,(size,at) in enumerate(concrete_parts):
        part,item=_box('guidebeam/concrete/'+str(number),size,at,'concrete',a['concrete']['density_kg_m3'],role='guidebeam-concrete-stock');part['frame_id']='guidebeam';item['frame_id']='guidebeam';item['scope']='guideway-per-span'
        geometry.append(part);inventory.append(item)
    for system in ('reinforcement-and-prestress-detail','return-rail-anchors-and-bearing-detail'):
        inventory.append(dict(id='guidebeam/'+system,scope='guideway-per-span',frame_id='guidebeam',quantity=1,status='unknown',
            unit_mass_kg=None,cg_m=None,inertia_kg_m2=None,basis='Requires candidate-specific selected-beam design; no unpriced or unweighed zero-stock credit.'))
    architecture=dict(carrier=dict(mode=mode,count_per_car=count,wall_m=wall,module_count_per_car=24,rows_y_m=[-.88,.88],module_centres_x_m=[-5.5+i for i in range(12)]),
        guidebeam=dict(section_id=section_id,span_m=span),cars=6,body_length_m=17.,car_pitch_m=17.5,
        native_variant_id=definition['variant_id'],magnetic_architecture='physical-shared-stem-two-PM-branches-three-coils',passenger_payload_kg_per_car=12000.)
    return make_candidate(requirement_revision=requirement_revision,architecture=architecture,frames=frames,materials=materials,geometry=geometry,
        interfaces=[dict(id='module-carrier',frame_id='vehicle',source_positions_m=definition['module_placements_m'],qualified=False),
                    dict(id='carrier-body',frame_id='vehicle',mode=mode,qualified=False),dict(id='return-rail-guidebeam',frame_id='guidebeam',qualified=False)],
        installed_inventory=inventory,lineage=lineage,label=mode+'/'+section_id,
        source_bindings=dict(source_candidate_configuration_sha256=definition['configuration_sha256'],source_sha256=definition['source_sha256']))


def initial_families(requirement_revision=DEFAULT_REQUIREMENT_REVISION,*,family=None):
    if family=='wheel_rail_station_lim':
        from .wheel_families import initial_families as wheel
        return wheel(requirement_revision)
    if family not in (None,'pm_maglev_station_powered'):raise UnsupportedCandidateDomain('Unknown physical family')
    return [_build(mode,count,section,requirement_revision=requirement_revision,span_m=span) for mode,count,section,span in (
        ('rigid-existing-hardpoints',1,'narrow-deep-reference',25.),
        ('fixed-yaw-pivots',4,'narrow-shallow-rejected-control',25.),
        ('yaw-and-lateral-slide',5,'wider-intermediate',20.))]


@lru_cache(maxsize=128)
def _supported_identity(mode,count,section_id,span_m,wall):
    # Context metadata is deliberately absent: the physical identity is shared
    # by requirement/lineage variants and by numerical flux hypotheses.
    return _build(mode,count,section_id,requirement_revision='adapter-domain-check',wall=wall,span_m=span_m)['candidate_id']


def validate_supported(candidate):
    """Reject valid but unsupported physical edits rather than ignoring them.

    The current adapters support only counted instances of the registered
    source-stock families. New dimensions, materials, frames, equipment or
    closures require a registered physical adapter before evaluation/export.
    """
    validate_candidate(candidate)
    if candidate['architecture'].get('family')=='wheel_rail_station_lim':
        from .wheel_families import validate_supported as wheel
        return wheel(candidate)
    try:
        carrier=candidate['architecture']['carrier'];beam=candidate['architecture']['guidebeam']
        expected=_supported_identity(carrier['mode'],carrier['count_per_car'],beam['section_id'],beam['span_m'],carrier['wall_m'])
    except (KeyError,StopIteration,TypeError) as error:
        raise UnsupportedCandidateDomain('candidate is outside the registered physical family domain') from error
    if candidate['candidate_id']!=expected:
        raise UnsupportedCandidateDomain('physical stock/material/inventory differs from the declared registered family; no canonical geometry substitution is permitted')
    return candidate


def materialize(candidate,*,allow_incomplete=False):
    if candidate['architecture'].get('family')=='wheel_rail_station_lim':
        from .wheel_families import materialize as wheel
        value=wheel(candidate)
        if not allow_incomplete:raise UnknownInstalledStock('Wheel research twin retains unknown installed stock and mass distribution')
        return value
    validate_supported(candidate);source,_=_native();geometry={row['id']:row for row in candidate['geometry']}
    if geometry['magnetic-module']['definition']!=physical_module(source['module']) or geometry['propulsion-band']['definition']!=source['propulsion_band']:
        raise ValueError('changed magnetic geometry needs an explicit new physical adapter')
    span=candidate['architecture']['guidebeam']['span_m']
    beam_stock=[part for part in candidate['geometry'] if part['id'].startswith('guidebeam/concrete/')]
    if len(beam_stock)!=6 or any(abs(part['size_m'][0]-span)>1e-10 for part in beam_stock[:4]):raise ValueError('physical beam stock and selected span differ')
    props=mass_properties(candidate);whole=inventory_summary(candidate)
    if not allow_incomplete and not whole['complete_installed_distribution']:raise UnknownInstalledStock('unresolved installed stock or CG/inertia: '+str(whole))
    value=deepcopy(source);value['source_candidate_configuration_sha256']=source['configuration_sha256'];value['candidate_id']=candidate['candidate_id'];value['configuration_sha256']=candidate['candidate_id']
    value['controlled_aw3_kg']=props['known_mass_subtotal_kg'];value['controlled_tare_kg']=props['known_mass_subtotal_kg']-value['passenger_payload_kg']
    value['mass_is_lower_bound']=props['total_mass_kg'] is None;value['unknown_installed_stock_ids']=whole['unknown_stock_ids'];value['complete_installed_distribution']=whole['complete_installed_distribution']
    value['inventory_by_scope']=whole['scopes']
    inventory={row['geometry_id']:row for row in candidate['installed_inventory'] if row.get('geometry_id') is not None and row['status']=='known'}
    eligible={part['id']:part for part in candidate['geometry'] if part.get('kind')=='box' and part.get('frame_id')=='vehicle'
        and part.get('material_id')=='carrier-steel' and part['id'] in inventory
        and inventory[part['id']]['scope']=='vehicle-per-car' and inventory[part['id']]['frame_id']=='vehicle'}
    labelled={part['id']:part for part in candidate['geometry'] if part.get('role')=='added-carrier-stock'}
    if set(labelled)!=set(eligible):
        raise UnsupportedCandidateDomain('carrier-stock role differs from actual vehicle/material/inventory scope')
    value['additional_physical_regions']=[deepcopy(part) for part in candidate['geometry'] if part['id'] in eligible]
    value['architecture']=deepcopy(candidate['architecture'])
    value['design_search_bundle']=deepcopy(candidate)
    value['allow_incomplete_diagnostic']=allow_incomplete
    value['diagnostic_mass_state']=known_mass_state(candidate)
    materials={row['id']:row for row in candidate['materials']}
    value['additional_stock']=[]
    for part in value['additional_physical_regions']:
        item=inventory[part['id']];material_id=part['material_id'];density=materials[material_id]['density_kg_m3']
        value['additional_stock'].append(dict(id=part['id'],kind=part['kind'],size_m=part['size_m'],at_m=part['at_m'],
            material='declared-carrier-steel',material_id=material_id,density_kg_m3=density,volume_m3=math.prod(part['size_m']),mass_kg=item['unit_mass_kg'],cg_m=item['cg_m'],inertia_kg_m2=item['inertia_kg_m2']))
        value['manufacturing_bom'].append(dict(id=part['id'],component_scope='added-carrier-stock',quantity_per_car=1,unit='part',mass_kg=item['unit_mass_kg'],
            material='declared-carrier-steel',material_id=material_id,geometry_part_ids=[part['id']],origin_confirmed=False,price_is_quote=False,qa_requirements=['Countedstockonly; joint/bearing/installedfit and qualification remain open.']))
    # Component identity hashes actual component geometry, independent of the
    # whole candidate, requirement revision or numerical core-path hypothesis.
    beam_component=dict(selection=candidate['architecture']['guidebeam'],
        geometry=[part for part in candidate['geometry'] if part['id'].startswith('guidebeam/')],
        materials=[row for row in candidate['materials'] if row['id']=='concrete'],
        installed_inventory=[row for row in candidate['installed_inventory'] if row['scope']=='guideway-per-span'])
    value['component_ids']=dict(magnetic_module=identity(physical_module(source['module'])),propulsion_band=identity(source['propulsion_band']),guidebeam=identity(beam_component))
    from engineering.ferrite_maglev import candidate_magnetics, candidate_structures
    span=candidate['architecture']['guidebeam']['span_m'];guideway=candidate_magnetics.guideway_definition(span,variant_id=source['variant_id'])
    guideway['source_configuration_sha256']=source['configuration_sha256'];guideway['configuration_sha256']=candidate['candidate_id'];guideway['candidate_id']=candidate['candidate_id'];guideway['span_m']=span
    guideway['guideway_source_module_sha256']=candidate_structures.sha256(candidate_structures.encoded(value['module'])).hexdigest()
    guideway['component_id']=identity(dict(parts=guideway['parts'],faces=guideway['faces']));value['guideway_definition']=guideway
    return value


def with_beam_selection(candidate,*,section_id=None,span_m=None):
    validate_supported(candidate);carrier=candidate['architecture']['carrier'];beam=candidate['architecture']['guidebeam']
    return _build(carrier['mode'],carrier['count_per_car'],section_id or beam['section_id'],
        requirement_revision=candidate['requirement_revision'],wall=carrier['wall_m'],span_m=beam['span_m'] if span_m is None else span_m,
        lineage=dict(parent_candidate_ids=[candidate['candidate_id']],operation='physical-beam-revision',reason='Rebuild actual section/span stock; recalculate selected-beam loads and all downstream quantities.'))


def known_mass_state(candidate,*,unlocated_height_m=1.):
    """Disclosed evaluation-only placement, never a completed physical inventory."""
    validate_supported(candidate);value=deepcopy(candidate)
    for row in value['installed_inventory']:
        if row['status']=='known' and row.get('cg_m') is None:
            row['cg_m']=[0.,0.,unlocated_height_m];m=row['unit_mass_kg'];size=[17.,2.65,2.5]
            row['inertia_kg_m2']=[[m*sum(size[k]**2 for k in range(3) if k!=i)/12 if i==j else 0. for j in range(3)] for i in range(3)]
    # Do not manufacture a physical candidate from assumed unknown equipment.
    # Aggregate the known rows through the same SI integral after omitting only
    # the explicitly enumerated unknown rows from this *diagnostic* subtotal.
    unknown=[row['id'] for row in value['installed_inventory'] if row['status']=='unknown']
    value['installed_inventory']=[row for row in value['installed_inventory'] if row['status']=='known']
    geometry={row['id']:row for row in candidate['geometry']};regions=[]
    for row in value['installed_inventory']:
        if row['scope']!='vehicle-per-car':continue
        part=geometry[row['geometry_id']];definition=part.get('definition',{})
        region=dict(id=row['id'],mass_kg=row['unit_mass_kg'],cg_m=row['cg_m'],inertia_kg_m2=row['inertia_kg_m2'],
            size_m=part.get('size_m',definition.get('size_m',[17.,2.65,2.5] if part['kind']=='unlocated-mass-budget' else [.02,.02,.02])))
        if 'gravity_projection' in definition:region['gravity_projection']=deepcopy(definition['gravity_projection'])
        elif part['kind']=='box':region['gravity_projection']=dict(part=dict(kind='box',size_m=part['size_m'],at_m=part['at_m']),density_kg_m3=row['unit_mass_kg']/math.prod(part['size_m']))
        regions.append(region)
    # Reuse the current signed-stock composition rather than inventing a
    # temporary physical candidate for an explicitly diagnostic placement.
    from engineering.ferrite_maglev import candidate_structures as structures
    laden=structures._combine(regions);empty=structures._combine([row for row in regions if row['id']!='native/AW3-passengers'])
    from .contracts import UNITS
    return dict(schema='osr-design-diagnostic-mass-state/1',units=deepcopy(UNITS),requirement_revision=candidate['requirement_revision'],
        candidate_id=candidate['candidate_id'],source_inventory_sha256=identity(candidate['installed_inventory']),
        empty=empty,laden=laden,
        diagnostic_known_stock_only=True,unknown_stock_ids=unknown,unlocated_height_assumption_m=unlocated_height_m,
        complete_installed_distribution=False,regions=regions,physical_accepted=False)


def selected_beam(candidate):
    from engineering.ferrite_maglev import candidate_structures as structures
    validate_candidate(candidate);native=materialize(candidate,allow_incomplete=True);selection=candidate['architecture']['guidebeam'];a=structures.load()
    if hasattr(structures,'selected_beam'):
        bundle=structures.selected_beam(native,selection=selection,allow_incomplete=True)
        bundle.update(section_id=selection['section_id'],span_m=selection['span_m'],candidate_id=candidate['candidate_id'],
            section=next(row for row in candidate['geometry'] if row['id']=='guidebeam/section-definition')['definition'],mass_is_diagnostic_lower_bound=True)
        return bundle
    section=next(row for row in candidate['geometry'] if row['id']=='guidebeam/section-definition')['definition']
    if section['id']!=selection['section_id']:raise ValueError('physical beam section and selected name differ')
    a['concrete']['span_m']=selection['span_m'];a['beam_sections']=[deepcopy(section)]
    mass=known_mass_state(candidate);loads=structures.load_cases(native,mass,a)
    canonical=deepcopy(_native()[0]);rail=structures.return_rail_and_attachments(canonical,selection['span_m'],a)
    rail['guideway']=native['guideway_definition']
    beams=structures.beam_design(native,loads,rail,a)
    matches=[row for row in beams if row['id']==selection['section_id']]
    if len(matches)!=1:raise ValueError('exact selected beam required')
    beam=matches[0];beam['candidate_id']=candidate['candidate_id'];beam['configuration_sha256']=candidate['candidate_id'];beam['span_m']=selection['span_m']
    return dict(beam=beam,rail_and_attachments=rail,assumptions=a,selection=deepcopy(selection),
        section_id=selection['section_id'],span_m=selection['span_m'],section=deepcopy(section),
        candidate_id=candidate['candidate_id'],configuration_sha256=candidate['candidate_id'],mass_is_diagnostic_lower_bound=True)


def propose_revision(candidate,results,*,trial_index=0):
    if candidate['architecture'].get('family')=='wheel_rail_station_lim':
        from .wheel_families import propose_revision as wheel
        return wheel(candidate,results,trial_index=trial_index)
    validate_supported(candidate)
    if type(trial_index) is not int or not 0<=trial_index<2:return None
    failures=[row for row in results if row.get('candidate_id')==candidate['candidate_id'] and row.get('screen_status')=='fail']
    if not failures:return None
    carrier=candidate['architecture']['carrier'];beam=candidate['architecture']['guidebeam'];section=beam['section_id'];wall=carrier['wall_m'];reason=None
    if any(row['request']['evaluator_id']=='civil' for row in failures) and section=='narrow-shallow-rejected-control':
        section='narrow-deep-reference';reason='Failed selected shallow-beam screen: increase counted section depth, recount concrete and repeat actual moving loads.'
    elif any(row['request']['evaluator_id']=='mechanical' for row in failures) and carrier['mode']!='rigid-existing-hardpoints' and wall<.010:
        wall+=.002;reason='Failed counted carrier/hardpoint screen: increase RHS wall by2mm, recount steel and repeat loads; joints remain unknown.'
    if reason is None:return None  # Canonical magnetic self-weight failure has no gain-only repair.
    return _build(carrier['mode'],carrier['count_per_car'],section,requirement_revision=candidate['requirement_revision'],wall=wall,
        span_m=beam['span_m'],lineage=dict(parent_candidate_ids=[candidate['candidate_id']],operation='bounded-result-driven-revision',reason=reason,trial_index=trial_index))
