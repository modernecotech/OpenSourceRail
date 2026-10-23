"""Exact counted actuator alternative linked to corridor cost, duty and finance.

The frozen GFRP/50turn planning case remains separate. A local numerical pass
never supplies its mass or price to a different product configuration.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import io
import json
import math
import tomllib

from . import body_stiffness, corridor, drive_design, launch_optimisation as launch, model, pilot_actuators as actuators, pilot_corridor as pilot, pilot_product as product, pilot_limits

ROOT=model.ROOT
INPUT=Path(__file__).with_name('pilot-variants.toml')
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_pilot_variants.py'
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/pilot-variants'
SCHEMA='osr-pilot-variant-finance/1'
FLAGS={**model.FLAGS,'automatic_adoption':False,'engineering_accepted':False,'financial_close':False}
MEDIA={'definition':'candidate-bay-definition.json.gz','poster':'candidate-bay-poster.png','video':'candidate-bay-replacement.mp4','events':'candidate-bay-translation-events.json','receipt':'candidate-bay-visual-receipt.json','views':'candidate-bay-views.svg'}
MEDIA_VERIFICATION=dict(method='independent-projected-material-footprint/1',poster_boundary_pixels=1,video_boundary_pixels=2,video_rgb_tolerance=32,max_missing_interior_fraction=.025,max_extra_colour_fraction=.035,video_frames=41,max_decoded_frames=42,size_px=[1100,650],frames_per_second=12,duration_tolerance_s=.002,max_raw_decode_bytes=90090000,font_and_encoder_bytes_are_oracles=False,scope='Raster footprint consistency only; pixel allowances are not engineering dimensional tolerances or physical acceptance.')
FILES={'study.json.gz','part-volume-audit.json.gz','overview.svg','README.md',*MEDIA.values()}
MAX_RAW=32*1024*1024

def encoded(v):return product.encoded(v)
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def source_paths():
    return sorted({Path(__file__),INPUT,TEST,Path(pilot_limits.__file__),*pilot.source_paths(),*actuators.source_paths(),
        *(p/name for p in (pilot.OUTPUT,actuators.OUTPUT) for name in ('manifest.json','study.json.gz')),actuators.OUTPUT/'candidate-bay.json.gz'})
def sources():return {p.relative_to(ROOT).as_posix():digest(p) for p in source_paths()}
def load():
    a=tomllib.loads(INPUT.read_text())
    selected=actuators.load()
    if a['schema']!='osr-pilot-variant-input/1' or a['body_variant']!=selected['preferred_body_variant'] or a['winding_variant']!=selected['preferred_winding_variant']:raise ValueError('exact declared counted candidate required')
    if a['automatic_adoption'] is not False or a['source_hotel_allowance_removal_credit_kw']!=0 or a['removed_gfrp_cost_credit_usd']!=0:raise ValueError('no unidentified allocation/removal credit allowed')
    if any(type(a[k]) not in (int,float) or not math.isfinite(a[k]) or a[k]<=0 for k in ('fabricated_steel_usd_per_kg','fabricated_spacer_usd_per_kg','fabricated_mount_usd_per_kg','cooling_auxiliary_w_per_module')):raise ValueError('finite positive component planning rates required')
    return a

def power_stage_changes(cfg):
    """Count declared converter and observer equipment without re-pricing mass."""
    stage=cfg['support_power_stage'];components=stage.get('components',[]);rows=[]
    if not components and (stage['additional_mass_kg_per_car'] or stage['additional_unquoted_cost_usd_per_car']):raise ValueError('power-stage component split required')
    for part in components:
        count=part['count_per_car'];mass=part['mass_kg_each'];cost=part['unquoted_cost_usd_each']
        if type(count) is not int or count<=0 or any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in (mass,cost)):raise ValueError('finite counted power-stage component required')
        rows.append(dict(id=part['id'],mass_change_kg_per_car=count*mass,priced_quantity_per_car=count,unit='unit',unit_mass_kg=mass,unit_rate_usd=cost,additional_cost_usd_per_car=count*cost,scope=stage['scope'],quote=False))
    if len({r['id'] for r in rows})!=len(rows) or not math.isclose(sum(r['mass_change_kg_per_car'] for r in rows),stage['additional_mass_kg_per_car'],abs_tol=1e-8) or not math.isclose(sum(r['additional_cost_usd_per_car'] for r in rows),stage['additional_unquoted_cost_usd_per_car'],abs_tol=1e-6):raise ValueError('power-stage component totals differ from exact configuration')
    auxiliary=stage['additional_auxiliary_kw_per_car'] if components else stage.get('additional_auxiliary_kw_per_car',0.)
    if type(auxiliary) not in (int,float) or not math.isfinite(auxiliary) or auxiliary<0:raise ValueError('finite power-stage auxiliary power required')
    return rows,auxiliary

def component_changes(cfg,drive,a=None):
    """Independent material/mass changes, with no invented aggregate credit."""
    a=load() if a is None else a;base=product.configuration_profile();rows=body_stiffness.derivation()['variants'];stock=next(r['stock'] for r in rows if r['name']==a['body_variant']);control=next(r['stock'] for r in rows if r['name']=='gfrp-control')
    coil=drive_design.support(drive);old=drive_design.support();m=cfg['magnetic'];rate=product.load()['support_copper_usd_per_kg'];items=[]
    def add(uid,mass,priced_quantity,unit_rate,scope):items.append(dict(id=uid,mass_change_kg_per_car=mass,priced_quantity_per_car=priced_quantity,unit='kg',unit_rate_usd=unit_rate,additional_cost_usd_per_car=priced_quantity*unit_rate,scope=scope,quote=False))
    add('replacement-steel-tubes',stock['tube_mass_kg']-control['tube_mass_kg'],stock['tube_mass_kg'],a['fabricated_steel_usd_per_kg'],'Exact drilled replacement stock; base body allowance remains, removed GFRP price is unidentified and receives no cost credit')
    add('changed-crush-spacers',stock['spacer_mass_kg']-control['spacer_mass_kg'],max(0.,stock['spacer_mass_kg']-control['spacer_mass_kg']),a['fabricated_spacer_usd_per_kg'],'Actual spacer lengths/material differences; no negative cost credit')
    add('additional-winding-copper',coil['copper_kg_per_car']-old['copper_kg_per_car'],max(0.,coil['copper_kg_per_car']-old['copper_kg_per_car']),rate,'All72physical support/guidance coils per car; copper increment replaces original winding mass once')
    add('additional-mount-stock',m['additional_mount_allowance_kg'],m['additional_mount_allowance_kg'],a['fabricated_mount_usd_per_kg'],'Counted module-mount allocation; detailed joints unqualified')
    hardware=cfg['bay_service_variant']['changed_hardware'];splice_mass=hardware['additional_stock_mass_kg_per_car']
    add('detachable-collector-splices',splice_mass,splice_mass,a['fabricated_mount_usd_per_kg'],'Exact added collector splice plates/bolts for24bays; no removed-stock mass or cost credit')
    items[-1]['hardware_counts_per_car']={k:24*hardware[k] for k in ('new_splice_plates','new_m8_bolts','reused_main_interface_m12_bolts')}
    cooling=m['additional_unquoted_copper_and_cooling_usd']-max(0.,m['incremental_winding_copper_kg'])*rate
    if cooling<0:raise ValueError('negative cooling allocation')
    items.append(dict(id='additional-cooling',mass_change_kg_per_car=m['additional_cooling_allowance_kg'],priced_quantity_per_car=24,unit='module',unit_rate_usd=cooling/24,additional_cost_usd_per_car=cooling,scope='Counted cooling/module allocation includes auxiliaries; no second pump cost added',quote=False))
    power_rows,power_auxiliary_kw=power_stage_changes(cfg);items.extend(power_rows)
    delta=sum(r['mass_change_kg_per_car'] for r in items)
    if not math.isclose(delta,cfg['controlled_aw3_kg']-base['controlled_aw3_kg'],abs_tol=1e-8):raise ValueError('candidate component mass changes do not reconcile')
    support_kw=72*cfg['magnetic']['support_winding']['continuous_current_a']**2*coil['coil']['resistance_hot_ohm']/1000
    auxiliary_kw=24*a['cooling_auxiliary_w_per_module']/1000
    return dict(rows=items,incremental_mass_kg_per_car=delta,additional_component_cost_usd_per_car=sum(r['additional_cost_usd_per_car'] for r in items),
        energy=dict(support_continuous_copper_ceiling_kw_per_car=support_kw,cooling_auxiliary_kw_per_car=auxiliary_kw,power_stage_auxiliary_kw_per_car=power_auxiliary_kw,additional_services_kw_per_car=support_kw+auxiliary_kw+power_auxiliary_kw,
            source_hotel_kw_per_car=pilot.load()['services_kw_per_car'],source_hotel_removed_kw=0.,all_physical_coils=72,base_hotel_support_split_known=False,
            scope='Conservative full60A continuous I²R ceiling across72coils plus counted cooling and power-stage/observer auxiliary allocations, added to retained60kW hotel allowance. Potential overlap with opaque hotel allowance is not credited. This is not measured consumption or the mixed support/wayside Rust heat; no LSM heat is added twice.'),
        removed_gfrp_cost_credit_usd=0.,mass_and_cost_are_distinct_ledgers=True,additional_non_vehicle_tooling_usd=hardware['tooling']['fixture_allowance_usd'],tooling=hardware['tooling'])

def selected_launch(profile,cfg,drive):
    # Cost the actual controller's group geometry and conductor/voltage choice.
    # A lower-cost separate launch search cannot supply this candidate's price.
    parameters=cfg['wayside_drive'];row=launch.loss_model(profile,**parameters,configuration_id=cfg['id'],_context=(launch.load(),drive,cfg));passing=row['feasible'] and row['controlled_mass_matches']
    return dict(candidate_count=1,feasible_count=int(passing),declared_executed_choice=parameters,selected=row if passing else None,
        rejection_screens=[] if passing else [dict(candidate=row['candidate'],limits=row['limits'])],independent_optimum_substituted=False,automatic_adoption=False)

def candidate_line(cfg,drive):
    line=deepcopy(pilot.city_line());profile=actuators.motion_profile(cfg);choice=selected_launch(profile,cfg,drive)
    if choice['selected'] is None:return None,choice
    loss=choice['selected'];old_mass=line['formation']['aw3_mass_kg']/6
    for event in line['duty']['arrival_events_per_circuit']:
        if event['terminal_loop_allowance']:
            event['station_traction_input_kwh']*=cfg['controlled_aw3_kg']/old_mass;event['energy_basis']='Mass-scaled retained short-loop allowance; exact curved-loop/short-zone electrical model held'
        else:
            if not math.isclose(event['distance_m'],profile['inputs']['distance_m'],abs_tol=.001):raise ValueError('candidate coupled profile differs from actual pilot mainline leg')
            event.update(moving_seconds=profile['inputs']['runtime_s'],station_traction_input_kwh=loss['dc_import_kwh'],launch_profile_sha256=loss['profile_sha256'])
    line['duty']['conservative_cycle_seconds']=sum(e['moving_seconds']+60. for e in line['duty']['arrival_events_per_circuit'])
    line.update(pilot_configuration=cfg,launch_profile=profile,launch_loss=loss);line['formation'].update(aw3_mass_kg=6*cfg['controlled_aw3_kg'],gross_storage_kwh=6*cfg['battery_kwh_per_car'])
    return line,choice

def apply_component_costs(economics,changes,fleet,a):
    value=deepcopy(economics);_,_,rates=model.load();integration=1+rates['rates']['vehicle_integration_reserve_fraction'];unreserved=changes['additional_component_cost_usd_per_car']*6*fleet*integration;tooling=changes.get('additional_non_vehicle_tooling_usd',0.);delta=(unreserved+tooling)*(1+a['design_risk_reserve_fraction'])
    value['vehicle_fleet_allowance_usd']+=unreserved;value['capital_with_reserve_usd']+=delta
    monthly=[dict(month=r['month'],capex_usd=r['capex_usd']) for r in value['finance']['monthly_construction_cash']]
    for fraction,day in ((.1,0),(.4,120),(.4,270),(.1,len(monthly)*30)):
        month=min(len(monthly)-1,max(0,math.ceil(day/30)-1));monthly[month]['capex_usd']+=unreserved*(1+a['design_risk_reserve_fraction'])*fraction
    monthly[0]['capex_usd']+=tooling*(1+a['design_risk_reserve_fraction'])
    value['annual_opex_usd']+=delta*a['maintenance_fraction_capital']
    value['finance']=pilot.finance(value['capital_with_reserve_usd'],value['annual_opex_usd'],value['synthetic_daily_paid_trips'],monthly,a=a)
    value['platform_budget']['compact_capital_sensitivity_usd']+=delta
    value['factory_startup_funding']['pooled_budget_usd']+=delta;value['factory_startup_funding']['standalone_budget_usd']+=delta
    value['variant_component_addition']=dict(unreserved_fleet_component_usd=unreserved,non_vehicle_fixture_usd=tooling,reserved_capital_delta_usd=delta,integration_reserve_multiplier=integration,design_risk_reserve_fraction=a['design_risk_reserve_fraction'],rows=changes['rows'])
    return value

def current_actuator_candidate(cfg):
    status=actuators.verify();_,packet=product.verify_packet(actuators.OUTPUT,actuators.SCHEMA,actuators.sources());matches=[r for r in packet['repair_candidates'] if r['configuration_sha256']==cfg['configuration_sha256']]
    if len(matches)!=1:raise ValueError('exact counted candidate missing from current executed actuator packet')
    run=matches[0];actuators.validate_run(run)
    return dict(configuration_sha256=run['configuration_sha256'],profile=run['profile'],profile_sha256=run['profile_sha256'],study_pass=run['study_pass'],failure=run['failure'],screens=run['screens'],
        completed_moving_steps=run['completed_moving_steps'],planned_moving_steps=run['planned_moving_steps'],full_duration=run['requested_duration_s']==run['profile']['inputs']['runtime_s'],packet_manifest_sha256=digest(actuators.OUTPUT/'manifest.json'),
        actual_module_force=pilot_limits.actual_module_force(run),any_full_candidate_feasible=status['any_full_candidate_feasible'],applicable_full_cases=status['applicable_full_cases'],all_negative_controls_held=status['all_negative_controls_held'],qualified_configuration_sha256=status['qualified_configuration_sha256'],control_configuration_sha256=status['control_configuration_sha256'],scope=run['scope'],physical_qualified=False)

def confirmed_profile(execution,profile):
    return bool(execution.get('any_full_candidate_feasible') is True and execution['study_pass'] and execution['full_duration'] and execution['completed_moving_steps']==execution['planned_moving_steps']
        and execution['profile']==profile and execution['profile_sha256']==sha256(encoded(profile)).hexdigest() and execution['actual_module_force']['passed'] is True)

def exact_controls_held(execution,cfg):
    return execution.get('all_negative_controls_held') is True and execution.get('qualified_configuration_sha256')==execution.get('control_configuration_sha256')==cfg['configuration_sha256']

def canonical_bay(cfg):
    """The current producer packet must supply the exact counted coil envelope."""
    path=actuators.OUTPUT/'candidate-bay.json.gz'
    if path.is_symlink() or path.stat().st_size>MAX_RAW:raise ValueError('bounded canonical candidate bay required')
    compressed=path.read_bytes()
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(MAX_RAW+1)
    if len(raw)>MAX_RAW:raise ValueError('bounded canonical candidate definition required')
    definition=json.loads(raw);expected=actuators.candidate_packaging(cfg['magnetic']['winding_variant'])['definition']
    if definition!=expected:raise ValueError('canonical bay differs from exact candidate geometry')
    return definition,compressed

def media_description(cfg,definition,compressed):
    events=product.animation_events(definition)
    return dict(files=MEDIA,configuration_sha256=cfg['configuration_sha256'],definition_sha256=sha256(encoded(definition)).hexdigest(),canonical_definition_gzip_sha256=sha256(compressed).hexdigest(),canonical_definition_source=(actuators.OUTPUT/'candidate-bay.json.gz').relative_to(ROOT).as_posix(),frames=len(events['frames']),frames_per_second=12,translation_m=definition['translation_m'],verification=MEDIA_VERIFICATION,scope='Exact larger candidate stock-bound straight-translation illustration. No measured motion, collision/handling qualification or physical assembly acceptance.',physical_accepted=False)

def render_stock_bound_animation(definition,configuration_sha):
    """Variant-only detail viewport; geometry cannot overpaint the annotations."""
    from PIL import Image,ImageDraw,ImageFont
    import subprocess
    import tempfile
    events=product.animation_events(definition);frames=[];background='#101c2b'
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    except OSError:font=ImageFont.load_default()
    # Physical axes, not image coordinates: Y=.25..2.80m, Z=-.80..+.40m.
    # Reference body bounds may leave this local view, but every primitive is
    # clipped inside the explicit scene frame before titles/notes are drawn.
    left,top,right,bottom=40.,90.,1060.,520.;yscale=(right-left)/2.55;zscale=(bottom-top)/1.2
    for event in events['frames']:
        im=Image.new('RGB',(1100,650),background);draw=ImageDraw.Draw(im)
        draw.rectangle([left,top,right,bottom],fill='#162b3c',outline='#7994a6')
        def rectangle(part,colour,shift=None):
            bounds=product.bounds(part)
            if not bounds[0][0]-.001<=.5<=bounds[1][0]+.001:return
            if shift:bounds=[[q[i]+shift[i] for i in range(3)] for q in bounds]
            x0=max(left,left+(bounds[0][1]-.25)*yscale);x1=min(right,left+(bounds[1][1]-.25)*yscale)
            y0=max(top,top+(.4-bounds[1][2])*zscale);y1=min(bottom,top+(.4-bounds[0][2])*zscale)
            if x0<=x1 and y0<=y1:draw.rectangle([x0,y0,x1,y1],fill=colour,outline='#d5e8ed',width=1)
        for part in definition['fixed_parts']:rectangle(part,'#405160')
        for part in definition['retained_parts']:rectangle(part,'#238f82',event['translation_m'])
        for part in definition['equipment']:
            if part['role']=='replaceable':rectangle(part,'#d99539',event['translation_m'])
        for y,text,colour in [(20,'Current 140 turn candidate: supported bay extraction','white'),
            (55,'Calculated front view at X = 0.5 m; surrounding body clipped inside view.','#c6d7e8'),
            (540,f'Outboard travel {event["translation_m"][1]:.3f} m /0.900 m; independently supported module.','white'),
            (570,'Stock bounds illustration; release services, splices and retention first.','#e3b66b'),
            (598,'Motion, collision, magnetic handling and physical assembly remain unqualified.','#e3b66b'),
            (626,'Exact candidate configuration: '+configuration_sha,'#c6d7e8')]:draw.text((25,y),text,font=font,fill=colour)
        frames.append(im)
    poster=io.BytesIO();frames[0].save(poster,format='PNG')
    with tempfile.TemporaryDirectory(prefix='osr-candidate-bay-') as folder:
        folder=Path(folder)
        for i,im in enumerate(frames):im.save(folder/f'{i:03d}.png')
        run=subprocess.run(['ffmpeg','-v','error','-y','-framerate','12','-i',str(folder/'%03d.png'),'-an','-c:v','libx264','-threads','2','-pix_fmt','yuv420p','-crf','22',str(folder/'candidate.mp4')],capture_output=True,text=True,timeout=120)
        if run.returncode:raise ValueError('candidate translation encoding failed: '+run.stderr[-1000:])
        video=(folder/'candidate.mp4').read_bytes()
    receipt=dict(schema='osr-pilot-bay-visuals/1',events_sha256=sha256(encoded(events)).hexdigest(),poster_sha256=sha256(poster.getvalue()).hexdigest(),video_sha256=sha256(video).hexdigest(),frames=len(frames),frames_per_second=12,source_geometry_sha256=events['definition_sha256'],viewport=dict(x_section_m=.5,y_range_m=[.25,2.8],z_range_m=[-.8,.4],pixel_clip_bounds=[left,top,right,bottom]),**FLAGS)
    return {'bay-poster.png':poster.getvalue(),'bay-replacement.mp4':video,'bay-translation-events.json':encoded(events),'visual-receipt.json':encoded(receipt)}

@lru_cache(maxsize=2)
def _render_candidate_media(definition_raw,compressed,configuration_sha):
    definition=json.loads(definition_raw)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(MAX_RAW+1)
    if len(raw)>MAX_RAW or json.loads(raw)!=definition:raise ValueError('media canonical definition differs')
    rendered=render_stock_bound_animation(definition,configuration_sha);receipt=visual_receipt(dict(configuration_sha256=configuration_sha),definition,compressed,rendered['bay-poster.png'],rendered['bay-replacement.mp4'])
    return {MEDIA['definition']:compressed,MEDIA['poster']:rendered['bay-poster.png'],MEDIA['video']:rendered['bay-replacement.mp4'],MEDIA['events']:rendered['bay-translation-events.json'],MEDIA['receipt']:encoded(receipt),MEDIA['views']:actuators.candidate_views(definition).encode()}

def render_candidate_media(cfg,definition,compressed):
    return _render_candidate_media(encoded(definition),compressed,cfg['configuration_sha256'])

def visual_receipt(cfg,definition,compressed,poster,video):
    events=product.animation_events(definition)
    return dict(schema='osr-pilot-bay-visuals/1',events_sha256=sha256(encoded(events)).hexdigest(),poster_sha256=sha256(poster).hexdigest(),video_sha256=sha256(video).hexdigest(),frames=len(events['frames']),frames_per_second=12,source_geometry_sha256=events['definition_sha256'],viewport=dict(x_section_m=.5,y_range_m=[.25,2.8],z_range_m=[-.8,.4],pixel_clip_bounds=[40.,90.,1060.,520.]),configuration_sha256=cfg['configuration_sha256'],canonical_definition_gzip_sha256=sha256(compressed).hexdigest(),verification=MEDIA_VERIFICATION,scope='Conservative stock-bound straight translation only; no measured motion, collision, magnetic handling or physical assembly acceptance.',**FLAGS)

@lru_cache(maxsize=2)
def _projected_stock(definition_raw):
    """Independent world-coordinate oracle; no encoder, font or raster text."""
    definition=json.loads(definition_raw);parts=[]
    for collection,colour,moves in [('fixed_parts',(64,81,96),False),('retained_parts',(35,143,130),True),('equipment',(217,149,57),True)]:
        for part in definition[collection]:
            if collection=='equipment' and part['role']!='replaceable':continue
            low,high=product.bounds(part)
            if low[0]-.001<=.5<=high[0]+.001:parts.append((low,high,colour,moves))
    return parts

def projected_scene(definition_raw,translation):
    import numpy as np
    scene=np.empty((431,1021,3),dtype=np.uint8);scene[:]=(22,43,60);scene[[0,-1],:]=(121,148,166);scene[:,[0,-1]]=(121,148,166)
    for low,high,colour,moves in _projected_stock(definition_raw):
        shift=translation if moves else (0.,0.,0.)
        x0=max(40.,40.+(low[1]+shift[1]-.25)*400.);x1=min(1060.,40.+(high[1]+shift[1]-.25)*400.)
        y0=max(90.,90.+(.4-high[2]-shift[2])*(430./1.2));y1=min(520.,90.+(.4-low[2]-shift[2])*(430./1.2))
        if x0>x1 or y0>y1:continue
        xa,xb,ya,yb=int(x0)-40,int(x1)-40,int(y0)-90,int(y1)-90
        scene[ya:yb+1,xa:xb+1]=colour
        scene[[ya,yb],xa:xb+1]=(213,232,237);scene[ya:yb+1,[xa,xb]]=(213,232,237)
    return scene

def _mask_neighbourhood(mask,distance,*,expand):
    import numpy as np
    result=mask.copy()
    for _ in range(distance):
        padded=np.pad(result,1,constant_values=False);neighbours=[padded[dy:dy+mask.shape[0],dx:dx+mask.shape[1]] for dy in range(3) for dx in range(3)]
        result=np.logical_or.reduce(neighbours) if expand else np.logical_and.reduce(neighbours)
    return result

def check_scene(actual,expected,*,lossy):
    """Per-material coverage preserves small coil areas despite large context.

    A whole-frame average could hide a missing coil in the surrounding body.
    Two edge pixels allow 4:2:0 chroma/rectangle rounding; flat material interiors
    permit32RGB levels and at most2.5% omissions/3.5% extra classified area.
    Poster colour tolerance is zero with a one-pixel boundary allowance. Text
    and font rasterisation outside this physical viewport are not an oracle.
    """
    import numpy as np
    edge=MEDIA_VERIFICATION['video_boundary_pixels'] if lossy else MEDIA_VERIFICATION['poster_boundary_pixels'];tolerance=MEDIA_VERIFICATION['video_rgb_tolerance'] if lossy else 0;actual=actual.astype(np.int16)
    for colour in ((64,81,96),(35,143,130),(217,149,57)):
        mask=np.all(expected==colour,axis=2);inside=_mask_neighbourhood(mask,edge,expand=False)
        if int(inside.sum())<50:raise ValueError('candidate material footprint too small for bounded semantic verification')
        observed=np.max(np.abs(actual-np.array(colour,dtype=np.int16)),axis=2)<=tolerance
        missed=int(np.count_nonzero(inside&~observed))/int(inside.sum())
        extra=int(np.count_nonzero(observed&~_mask_neighbourhood(mask,edge,expand=True)))/max(1,int(observed.sum()))
        if missed>MEDIA_VERIFICATION['max_missing_interior_fraction'] or extra>MEDIA_VERIFICATION['max_extra_colour_fraction']:raise ValueError('candidate geometry/material footprint differs from exact translation')

@lru_cache(maxsize=2)
def _verify_semantic_media(definition_raw,poster,video):
    from PIL import Image
    import numpy as np
    import subprocess
    import tempfile
    definition=json.loads(definition_raw);events=product.animation_events(definition)['frames']
    if len(events)!=41:raise ValueError('bounded41frame candidate sequence required')
    with Image.open(io.BytesIO(poster)) as image:
        if image.format!='PNG' or image.size!=(1100,650) or image.mode!='RGB':raise ValueError('candidate poster format/dimensions differ')
        pixels=np.asarray(image)
        check_scene(pixels[90:521,40:1061],projected_scene(definition_raw,events[0]['translation_m']),lossy=False)
    with tempfile.TemporaryDirectory(prefix='osr-verify-candidate-media-') as folder:
        path=Path(folder)/'candidate.mp4';path.write_bytes(video)
        probe=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,duration,nb_frames','-of','json',str(path)],capture_output=True,text=True,timeout=30)
        if probe.returncode:raise ValueError('candidate video probe failed')
        streams=json.loads(probe.stdout).get('streams',[])
        if len(streams)!=1:raise ValueError('candidate video requires one bounded video stream')
        stream=streams[0]
        try:duration=float(stream.get('duration','nan'))
        except (ValueError,TypeError):duration=float('nan')
        if (stream.get('codec_type'),stream.get('codec_name'),stream.get('width'),stream.get('height'),stream.get('r_frame_rate'),stream.get('avg_frame_rate'),str(stream.get('nb_frames')))!=('video','h264',1100,650,'12/1','12/1','41') or not math.isfinite(duration) or abs(duration-41/12)>.002:raise ValueError('candidate video metadata exceeds exact frame/dimension/rate/duration bounds')
        # Fixed-size output and42-frame cap bound raw output to90,090,000bytes,
        # even if compressed metadata lies about the actual frame count.
        decoded=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-vsync','0','-vf','scale=1100:650','-frames:v','42','-threads','2','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,timeout=60)
        frame_bytes=1100*650*3
        if decoded.returncode or len(decoded.stdout)!=len(events)*frame_bytes:raise ValueError('candidate video decoded frame count/dimensions differ')
        frames=np.frombuffer(decoded.stdout,dtype=np.uint8).reshape((len(events),650,1100,3))
        for frame,event in zip(frames,events):check_scene(frame[90:521,40:1061],projected_scene(definition_raw,event['translation_m']),lossy=True)
    return True

def verify_candidate_media(output,cfg,definition,compressed):
    p=Path(output);poster=(p/MEDIA['poster']).read_bytes();video=(p/MEDIA['video']).read_bytes();events=encoded(product.animation_events(definition))
    if len(poster)>MAX_RAW or len(video)>MAX_RAW:raise ValueError('candidate media compressed size exceeded')
    if (p/MEDIA['definition']).read_bytes()!=compressed or (p/MEDIA['events']).read_bytes()!=events or (p/MEDIA['views']).read_text()!=actuators.candidate_views(definition):raise ValueError('candidate media differs from exact geometry/translation source')
    if json.loads((p/MEDIA['receipt']).read_bytes())!=visual_receipt(cfg,definition,compressed,poster,video):raise ValueError('candidate visual receipt differs from retained hashes/configuration/source')
    _verify_semantic_media(encoded(definition),poster,video)

def part_volume_audit(definition):
    """Independent gross bounds; these cannot recover cut/drilled net solids."""
    rows=[];excluded=0
    for collection in ('retained_parts','fixed_parts','equipment'):
        for part in definition.get(collection,[]):
            if part.get('kind')!='box':excluded+=1;continue
            size=part.get('size_m');known=isinstance(size,(list,tuple)) and len(size)==3 and all(type(x) in (int,float) and math.isfinite(x) and x>0 for x in size)
            gross=math.prod(size) if known else None;reported=part.get('volume_m3');reported_known=type(reported) in (int,float) and math.isfinite(reported) and reported>=0
            tolerance=max(1e-10,gross*1e-8) if known else None;exceeded=known and reported_known and reported>gross+tolerance
            rows.append(dict(id=part['id'],collection=collection,placed_size_m=size,placed_origin_m=part.get('at_m'),gross_bound_volume_m3=gross,
                inherited_reported_net_volume_m3=reported if reported_known else None,comparison_tolerance_m3=tolerance,
                inherited_net_exceeds_placed_gross=bool(exceeded),net_manufactured_volume_m3=None,net_solid_reconciled=False))
    exceeded=[r['id'] for r in rows if r['inherited_net_exceeds_placed_gross']]
    return dict(schema='osr-placed-box-volume-audit/1',definition_sha256=sha256(encoded(definition)).hexdigest(),rows=rows,boxes_checked=len(rows),nonbox_parts_not_checked=excluded,
        inherited_volume_exceeds_bound_ids=exceeded,inherited_volume_exceeds_bound_count=len(exceeded),missing_reported_volume_count=sum(r['inherited_reported_net_volume_m3'] is None for r in rows),
        gross_bound_consistency='failed' if exceeded else 'hold' if any(r['gross_bound_volume_m3'] is None for r in rows) else 'passed',
        state='hold',net_manufacturing_quantities_reconciled=False,mass_or_cost_removal_credit_applied=False,
        scope='Placed box dimensions provide gross upper bounds only. Inherited net-volume metadata can be stale after segmentation; even a value below the bound does not verify holes/cuts/net material. Net-solid/manufacturing quantity reconciliation is held. Existing conservative full-base-stock plus additional-hardware mass/cost is preserved.')

def volume_audit_summary(audit):
    return {key:audit[key] for key in ('schema','definition_sha256','boxes_checked','nonbox_parts_not_checked','inherited_volume_exceeds_bound_ids','inherited_volume_exceeds_bound_count','missing_reported_volume_count','gross_bound_consistency','state','net_manufacturing_quantities_reconciled','mass_or_cost_removal_credit_applied','scope')}

def service_screens(run):
    separations=[b-a for row in run['mainline_segment_departures'] for a,b in zip(row['times_s'],row['times_s'][1:])]
    return dict(actual_berth_replay=run['berth_verification']['verified'],energy_balance=abs(run['event_energy_balance_kwh'])<1e-8,
        battery_window=all(r['battery_after_kwh']>=r['normal_minimum_kwh']-1e-9 for r in run['events']),
        protected_separation=all(v>=run['source_policy_headway_s']-1e-9 for v in separations),finite_dispatch=all(r['start_s']<run['horizon_s'] for r in run['events']))

@lru_cache(maxsize=2)
def _study(source):
    pilot.verify();base=pilot.study();a=load();cfg=actuators.selected_configuration();drive=drive_design.load();drive['support']=deepcopy(cfg['magnetic']['support_winding']);changes=component_changes(cfg,drive,a);execution=current_actuator_candidate(cfg);line,choice=candidate_line(cfg,drive);definition,compressed=canonical_bay(cfg);audit=part_volume_audit(definition)
    result=dict(schema=SCHEMA,source_sha256=json.loads(source),assumptions=a,base_configuration_sha256=base['configuration_sha256'],configuration_sha256=cfg['configuration_sha256'],configuration=cfg,
        base_reference=dict(capital_usd=base['economics']['capital_with_reserve_usd'],annual_opex_usd=base['economics']['annual_opex_usd'],hotel_kw_per_car=base['assumptions']['services_kw_per_car'],nominal_maximum_observed_gap_s=base['service_scenarios'][0]['maximum_observed_headway_s'],source_packet_manifest_sha256=digest(pilot.OUTPUT/'manifest.json'),role='Retained separate GFRP/50turn financial planning case; no actuator pass inherited'),
        component_changes=changes,actuator_execution=execution,launch_search=choice,part_volume_audit=audit,assembly_media=media_description(cfg,definition,compressed),selected_for_city_defaults=False,system_qualified=False,**FLAGS)
    if line is None:
        result.update(economics=None,service_scenarios=[],service_screens=[],full_coupled_profile_confirmed=False,system_feasible=False,system_gates=[dict(id='exact-candidate-corridor-launch',state='failed',reason='No current/voltage/thermal feasible launch candidate at counted mass')])
    else:
        assumptions=pilot.load();assumptions['services_kw_per_car']+=changes['energy']['additional_services_kw_per_car'];runs=[pilot.service(k,line=line,a=assumptions) for k in ('nominal','variable-dwell','withdrawal','receiver-failure','charger-failure','combined-recovery')]
        economics=apply_component_costs(pilot.economics(line,base['access'],base['synthetic_demand'],runs[0],assumptions),changes,runs[0]['fleet_total'],assumptions)
        profile_match=execution['profile']==line['launch_profile'] and execution['profile_sha256']==sha256(encoded(line['launch_profile'])).hexdigest();model_pass=confirmed_profile(execution,line['launch_profile'])
        screens=[dict(scenario=r['scenario'],checks=service_screens(r)) for r in runs];safe=all(all(r['checks'].values()) for r in screens);controls=exact_controls_held(execution,cfg)
        result.update(candidate_operating_assumptions=assumptions,service_scenarios=runs,service_screens=screens,economics=economics,full_coupled_profile_confirmed=bool(model_pass),system_feasible=bool(model_pass and controls and safe and not runs[0]['withdrawals']),
            system_gates=[dict(id='exact-candidate-corridor-actuator-model',state='passed' if model_pass else 'failed' if not execution['study_pass'] or execution['actual_module_force']['state']=='failed' or execution['any_full_candidate_feasible'] is False else 'hold',profile_matches=profile_match,full_duration=execution['full_duration'],study_pass=execution['study_pass']),
                dict(id='actual-support-module-force',**execution['actual_module_force']),
                dict(id='all-applicable-full-profile-sensitivities',state='passed' if execution['any_full_candidate_feasible'] is True else 'failed' if execution['any_full_candidate_feasible'] is False else 'hold',producer_full_candidate_feasible=execution['any_full_candidate_feasible'],cases=execution['applicable_full_cases']),
                dict(id='exact-candidate-control-negative-cases',state='passed' if controls else 'failed'),dict(id='candidate-launch-electrical-screen',state='passed'),dict(id='nominal-source-berth-and-battery-replay',state='passed' if not runs[0]['withdrawals'] else 'failed'),
                dict(id='terminal-loop-and-guidance-coupled-model',state='hold'),dict(id='steel-joined-body-material-fatigue-load-paths',state='hold'),dict(id='guideway-reactions-joints-foundations-at-candidate-load',state='hold'),dict(id='cooling-converter-hardware-and-service-duty',state='hold'),
                dict(id='observed-demand-site-land-and-financial-close',state='hold')],
            partial_model_chain_feasible=bool(model_pass and controls and not runs[0]['withdrawals']))
    if result['source_sha256']!=sources():raise ValueError('variant sources changed during calculation')
    result['system_gates'].append(dict(id='placed-box-net-solid-manufacturing-reconciliation',state='hold',inherited_volume_exceeds_bound_count=audit['inherited_volume_exceeds_bound_count'],scope=audit['scope']))
    return encoded(result)
def study():return json.loads(_study(json.dumps(sources(),sort_keys=True)))

def overview(v):
    e=v['economics'];cost='No feasible candidate launch' if e is None else f'Counted candidate: ${e["capital_with_reserve_usd"]/1e6:.3f}m capital; ${e["annual_opex_usd"]/1e6:.3f}m annual operation'
    state='Full coupled profile confirmed' if v['full_coupled_profile_confirmed'] else 'Full coupled profile NOT confirmed; planning costs do not establish an operable train'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="350"><rect width="1200" height="350" fill="#f4f7fa"/><g font-family="sans-serif" fill="#16314b"><text x="30" y="45" font-size="24">Separate exact steel / higher-copper pilot sensitivity</text><text x="30" y="105" font-size="19">{cost}</text><text x="30" y="160" font-size="18">AW3 {v["configuration"]["controlled_aw3_kg"]:,.3f} kg/car; exact declared equipment priced.</text><text x="30" y="220" font-size="17">{state}</text><text x="30" y="285" font-size="16">Unquoted costs; continuous heat ceiling; material, cooling, guidance, terminal, site and financial gates open.</text></g></svg>\n'
def readme(v):
    e=v['economics'];details='No launch candidate passes the implemented current/voltage/thermal screens.' if e is None else f'Candidate unquoted capital ${e["capital_with_reserve_usd"]:,.0f}; annual operating allowance ${e["annual_opex_usd"]:,.0f}. Exact component cost rows and procurement-linked capital cash, six service/fault replays and fresh debt/DSCR/funding gaps are retained.'
    stage=v['configuration']['support_power_stage'];details+=f'\n\nThe {stage["rated_bus_v"]:g}V support converter and observer equipment is counted separately: {stage["additional_mass_kg_per_car"]:g}kg/car and ${stage["additional_unquoted_cost_usd_per_car"]:,.0f}/car, with {stage["additional_auxiliary_kw_per_car"]:g}kW/car of additional auxiliary allowance. Component rows reconcile to the exact tested configuration; the auxiliary allowance enters service energy once. Hardware, sensing, maps and timing remain unqualified.'
    details+='\n\n[Current candidate extraction video]('+MEDIA['video']+') · [Poster]('+MEDIA['poster']+') · [Dimensioned stock bounds]('+MEDIA['views']+') · [Exact candidate definition]('+MEDIA['definition']+') · [Translation events]('+MEDIA['events']+') · [Visual/source receipt]('+MEDIA['receipt']+'). The larger140turn coil geometry comes from the exact canonical actuator candidate definition. This is a calculated conservative stock-bound straight-translation illustration, with the declared services/splices/retention released first; it is not measured motion or collision, lifting, magnetic handling or physical assembly acceptance. The source receipt binds retained hashes, candidate configuration, definition and events. Portable verification decodes all41frames and checks independently projected material footprints inside the viewport, with a bounded two-pixel edge allowance for lossy video. Font and encoder bytes are excluded from the oracle. The per-material check rejects a rehashed smaller-coil reference video; raster allowances are not engineering dimensional tolerances. Decoder metadata is checked first and output is capped at42fixed-size frames.'
    execution=v['actuator_execution'];confirmation=f'**Full coupled profile confirmed: {v["full_coupled_profile_confirmed"]}.** Executed {execution["completed_moving_steps"]:,}/{execution["planned_moving_steps"]:,} moving steps; retained failure: {execution["failure"]}. All applicable full-profile estimator sensitivities passed: {execution["any_full_candidate_feasible"]}. A completed planning DES or a nominal passing trajectory does not override a failed full-profile sensitivity.'
    return '# Separate counted actuator candidate: pilot cost and finance\n\n[Computed candidate and raw replays](study.json.gz) · [Placed-part volume audit](part-volume-audit.json.gz) · [Overview](overview.svg) · [Exact source receipt](manifest.json)\n\n'+confirmation+'\n\n'+details+'\n\nThe original GFRP/50turn financial study is preserved. The candidate has independently counted steel tubes/spacers, additional winding copper, mounts and cooling. Costs carry no unidentified GFRP removal credit. Vehicle integration and design reserves apply to the component additions; no overall capital multiplier substitutes for a BOM.\n\nMainline winding/section/voltage choices are recomputed at the candidate mass and exact retained coupled trajectory. Full-duration actuator evidence must have the same configuration and profile; a short or different-profile pass cannot close that gate. Terminal-loop/guidance motion and physical hardware remain held.\n\n'+f'The independent placed-box audit finds {v["part_volume_audit"]["inherited_volume_exceeds_bound_count"]} inherited net-volume records above the actual placed gross dimensional bound. Segmented collector metadata requires reconciliation. Gross bounds are not net manufactured material; all net-solid/manufacturing quantities remain held. The conservative full-base stock plus added hardware mass/cost remains unchanged.\n\n'+'The opaque60kW/car hotel allowance remains. A separately calculated60A continuous winding I²R ceiling and counted cooling auxiliaries are added conservatively; overlap with that unitemised allowance receives no removal credit. Mixed support/wayside Rust heat is not added to the independently computed LSM DC import. This power ceiling is not measured duty or a cooling qualification.\n\nAll prices are planning inputs. Neither candidate nor base is adopted or released for manufacture, passengers, physical operation or financial close.\n'
def publish(output=OUTPUT):
    v=study();p=Path(output);p.mkdir(parents=True,exist_ok=True)
    if p.is_symlink() or any(x.is_symlink() or x.name not in FILES|{'manifest.json'} for x in p.iterdir()):raise ValueError('owned variant packet required')
    raw=encoded(v)
    if len(raw)>MAX_RAW:raise ValueError('bounded variant payload required')
    definition,compressed=canonical_bay(v['configuration']);payload={'study.json.gz':gzip.compress(raw,mtime=0),'part-volume-audit.json.gz':gzip.compress(encoded(v['part_volume_audit']),mtime=0),'overview.svg':overview(v).encode(),'README.md':readme(v).encode(),**render_candidate_media(v['configuration'],definition,compressed)}
    if v['source_sha256']!=sources():raise ValueError('variant media sources changed during publication')
    for name,data in payload.items():(p/name).write_bytes(data)
    (p/'manifest.json').write_bytes(encoded(dict(schema=SCHEMA,source_sha256=v['source_sha256'],files_sha256={n:digest(p/n) for n in FILES},**FLAGS)));return verify(p)
def _verified_payload(output):
    p=Path(output)
    if p.is_symlink() or not p.is_dir() or {x.name for x in p.iterdir()}!=FILES|{'manifest.json'} or any(x.is_symlink() for x in p.iterdir()):raise ValueError('exact variant packet required')
    m=json.loads((p/'manifest.json').read_bytes())
    if m.get('source_sha256')!=sources() or any(m.get(k) is not False for k in FLAGS):raise ValueError('variant source/release flags differ')
    for name in FILES:
        if (p/name).stat().st_size>MAX_RAW or digest(p/name)!=m['files_sha256'][name]:raise ValueError('variant checksum/size differs')
    with gzip.GzipFile(fileobj=io.BytesIO((p/'study.json.gz').read_bytes())) as stream:raw=stream.read(MAX_RAW+1)
    value=study()
    if raw!=encoded(value) or (p/'part-volume-audit.json.gz').read_bytes()!=gzip.compress(encoded(value['part_volume_audit']),mtime=0) or (p/'README.md').read_text()!=readme(value) or (p/'overview.svg').read_text()!=overview(value):raise ValueError('variant recalculation/presentation differs')
    definition,compressed=canonical_bay(value['configuration']);verify_candidate_media(p,value['configuration'],definition,compressed)
    return m,value
def verify(output=OUTPUT):return _verified_payload(output)[0]
def read_summary(output=OUTPUT):
    _,v=_verified_payload(output);e=v['economics'];financial=None
    if e:
        f=e['finance'];financial=dict(capital_usd=e['capital_with_reserve_usd'],standalone_capital_usd=e['factory_startup_funding']['standalone_budget_usd'],annual_opex_usd=e['annual_opex_usd'],annual_energy_kwh=e['annual_energy_kwh'],station_assets_allowance_usd=e['station_electrical_allowance_usd'],vehicle_fleet_allowance_usd=e['vehicle_fleet_allowance_usd'],capital_delta_from_base_usd=e['capital_with_reserve_usd']-v['base_reference']['capital_usd'],annual_opex_delta_from_base_usd=e['annual_opex_usd']-v['base_reference']['annual_opex_usd'],comparison_capital_usd=e['comparison_capital_with_reserve_usd'],comparison_annual_opex_usd=e['comparison_energy_and_operation']['annual_opex_usd'],debt_principal_usd=f['debt_principal_usd'],annual_debt_service_usd=f['annual_repayment'][0]['debt_service_usd'],annual_cases=[{k:r[k] for k in ('fare_usd','year','dscr','annual_funding_gap_usd')} for r in f['annual_cases'] if r['year'] in (1,4)])
    return dict(schema=SCHEMA,candidate_name=v['configuration']['id'],configuration_sha256=v['configuration_sha256'],base_configuration_sha256=v['base_configuration_sha256'],controlled_aw3_kg=v['configuration']['controlled_aw3_kg'],actuator_model_pass=bool(v['actuator_execution']['study_pass'] and v['actuator_execution']['actual_module_force']['passed'] and v['actuator_execution']['any_full_candidate_feasible'] is True),all_full_profile_sensitivities_passed=v['actuator_execution']['any_full_candidate_feasible'],actual_module_force=v['actuator_execution']['actual_module_force'],partial_model_chain_feasible=v.get('partial_model_chain_feasible',False),system_feasible=v['system_feasible'],full_coupled_profile_confirmed=v['full_coupled_profile_confirmed'],system_gates=v['system_gates'],part_volume_audit=volume_audit_summary(v['part_volume_audit']),component_changes=v['component_changes'],assembly_media=v['assembly_media'],financial_view=financial,base_reference=v['base_reference'],selected_for_city_defaults=False,system_qualified=False,**FLAGS)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('publish','verify'),nargs='?',default='publish');args=parser.parse_args();print(json.dumps(globals()[args.action](),indent=2))
