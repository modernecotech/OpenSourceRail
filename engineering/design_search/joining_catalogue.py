"""Primary-source joining/component leads and counted research attachment plans.

Typical material/coupon data never becomes a vehicle-joint allowable. Entries
are sourcing and test inputs, not selected parts or physical acceptance. Raw
PDF hashes are explicitly unknown where the publisher refused byte retrieval.
"""
from copy import deepcopy
from hashlib import sha256
from math import isfinite,pi
import json
ACCESSED='2026-10-26'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,qualification_status='unknown',unit_price_USD=None)


def _id(value):return sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()


def _source(url,title,pages,revision=None,raw_sha256=None,media='application/pdf',locator=None):
    return dict(url=url,title=title,pages_one_based=pages,revision=revision,accessed_UTC_date=ACCESSED,
        raw_document_sha256=raw_sha256,media_type=media,locator=locator,
        snapshot_status='raw-bytes-retained' if raw_sha256 else 'web-extracted; raw byte retrieval unavailable',
        document_hash_unavailable_is_not_verified=True)


SOURCES={
 'dp490':_source('https://multimedia.3m.com/mws/media/2534142O/3m-scotch-weld-epoxy-adhesive-dp490-technical-data-sheet.pdf','3M DP490 Technical Data Sheet, English-Canada',[1,2,3,4],'July2024'),
 'potting':_source('https://multimedia.3m.com/mws/media/749716O/3m-scotch-weld-kern-und-randf-llmasse-ec-3500-2-b-a.pdf?fn=3500-2-PMF-TDS-En11.pdf','3M EC-3500-2 B/A and PMF Technical Data Sheet',[1,2,3]),
 'hexcel':_source('https://www.hexcel.com/wp-content/uploads/2026/01/Honeycomb_Sandwich_Design_Technology-1.pdf','HexWeb Honeycomb Sandwich Design Technology',[5,21],raw_sha256='53f08b6b89f87f1d1995edd38055a112d6af7bbfd5e76a359cc85526893162d5'),
 'diab-fastening':_source('https://www.diabgroup.com/media/dtiht4fc/diab-product-brochure-fastening-solutions-in-sandwich.pdf','DIAB Fastening Solutions in Sandwich',[2,3],raw_sha256='a6b14cd86a299316db648cd96305c555081e0562acb54f9b3665f275f82a7e95'),
 'diab-hp':_source('https://diab-media.azureedge.net/enygao3k/diab-divinycell-hp-may-2026-rev29-si.pdf','DIAB Divinycell HP SI Technical Data',[1,2],'May2026 rev29','f7bb703f15723fb05bb487f28b8e94471a1284808224c98f64268476120e3d40'),
 'extrusions':_source('https://aluminium.org.au/wp-content/uploads/2023/12/Aluminium-Extrusion-Manual-Dec23-1.pdf','Australian Aluminium Council Extrusion Manual',[60,61,85],'December2023','01c23639b7b79503b0dbceb963b39f680efbaee86ed74e56021ed21ce80322a3'),
 'clips':_source('https://fastmount.com/products/standard-range/pc-f1a-standard-clip-self-tapping-female/','Fastmount PC-F1A',[],media='text/html',locator='Product Summary; clip-pair selection required'),
 'captive':_source('https://southco.com/en_us_int/fasteners/captive-screws','Southco Captive Screws',[],media='text/html',locator='Product description and benefits'),
 'glazing':_source('https://www.polyvantis.com/files/polyvantis-content/dokumente/LEXAN%E2%84%A2%20SHEET%20%28technical%20datasheets%29/LEXAN%E2%84%A2%20SOLID%20SHEET/LEXAN%20MARGARD%20MR5E%20Sheet%20Datasheet%20-%20EUR-NPAC.pdf','POLYVANTIS LEXAN MARGARD MR5E EUR-NPAC',[1,2,3],'PV_DS_001_MR5E-MGD_ENG_08-24','bf18310753510c8692325b2d7c84a45fcca50d42c93830f72a0211516e2e318c'),
 'exolon':_source('https://www.exolongroup.com/index.php/fuseaction/download/lrn_file/mf0451_e_250704.pdf','Exolon FR AR Product Data Sheet',[1,2],'July2025','82130048878f37789833df0335bdc63bb98d05934b0410b0f2be29a261c3fe8d'),
 'hvac':_source('https://www.liebherr.com/en-int/aerospace-and-transportation-systems/solutions-and-services/solutions-for-railway/plug-play-hvac/plug-and-play-hvac-7174981','Liebherr Plug and Play HVAC',[],raw_sha256='697bc6c674cec0da759b4b5b64857c5b7bf8e8a87dae4ae524fa9ad8c2d1affa',media='text/html',locator='Technical advantages; supplier claims only'),
}


def catalogue():
    records=[
      dict(id='bonded-flange-dp490',sources=['dp490','hexcel'],family='bonded-flange',
        density_kg_m3=None,mixture_volume_B_to_A=[2,1],worklife_s=5400,worklife_temperature_C=22.,
        strength_time_reference_s=86400,strength_time_temperature_C=23.,strength_time_basis='Supplier coupon threshold1000psi, not an assembly release criterion',full_coupon_cure_s=604800,
        coupon=dict(kind='overlap shear',standard='ASTM D1002 / ISO4587 as printed',substrate='sandblasted aluminium',
          width_m=.025,overlap_m=.0127,bondline_m=[.00013,.00020],substrate_thickness_m=[.0013,.0016],
          test_temperature_C=22.,reported_psi=3336.,typical_stress_Pa=3336*6894.757293168),
        hot_coupon=dict(test_temperature_C=(180-32)*5/9,reported_psi=1378.,typical_stress_Pa=1378*6894.757293168),
        bell_peel_coupon=dict(standard='DIN EN1464',temperature_C=23.,reported_N_per_cm=34.49,typical_N_per_m=3449.),
        surface_process='Establish clean prepared substrate and resin-specific process; pinned coupon used sandblasted aluminium. Verify actual GFRP surface, primer, moisture and cure.',
        unsupported=['Coupon shear is not an allowable joint stress','Peel, cleavage, adherend bending, creep, fatigue, hot/wet and disbond load paths remain unknown','DP490 mixed/cured density not specified in the pinned July2024 sheet']),
      dict(id='hybrid-bond-positive-fasteners',sources=['dp490','diab-fastening','captive'],family='bond-plus-bolts',
        density_kg_m3=None,design_allowable_Pa=None,load_sharing_factor=None,
        principle='Count bond, flanges, inserts, bolts, nuts, washers, insulating sleeves and sealing separately. Fasteners are an explicit retention option, not a credited safe load path.',
        unsupported=['Bond and bolt strengths cannot be added','Preload loss, hole bearing, bypass, edge distance, peel and degraded-bond cases require tests']),
      dict(id='potted-core-insert-ec3500',sources=['potting','hexcel','diab-fastening'],family='potted-insert',
        density_kg_m3=650.,density_basis='Typical cured EC-3500-2 B/A; PMF is a distinct product',
        mix_ratio_mass_B_to_A=[1,1],mix_ratio_volume_B_to_A=[100,93],minimum_cure_temperature_C=125.,minimum_cure_time_s=3600,
        coupon=dict(standard='ISO604',size_m=[.0125,.0125,.025],cure_temperature_C=125.,cure_time_s=3600,
          test_temperature_C=23.,typical_compressive_Pa=63e6,hot_test_temperature_C=80.,hot_typical_compressive_Pa=53e6),
        unsupported=['Potting compression coupon does not establish insert pullout or joint strength','Heat cure must be checked against actual foam, skins, adhesive, pressure and tooling; no automatic compatibility claim']),
      dict(id='divinycell-hp60-current',sources=['diab-hp'],family='sandwich-core',density_kg_m3=65.,density_range_kg_m3=[62.,75.],
        properties_temperature_C=23.,minimum_compressive_Pa=.85e6,minimum_shear_Pa=.75e6,nominal_shear_modulus_Pa=20e6,
        continuous_temperature_C=[-200.,80.],maximum_processing_temperature_C=145.,
        unsupported=['HP60 grade name does not mean60kg/m3','No high-temperature continuous-load allowable inferred','Existing60kg/m3 source stock requires explicit mass revision before substituting this record']),
      dict(id='welded-al-extrusion-node',sources=['extrusions'],family='welded-node',
        proposed_stock_alloy='6082-T6 comparison stock',typical_density_kg_m3=2710.,density_basis='Manual Table29 p85; typical physical data only',
        processes=['GTAW/TIG','GMAW/MIG'],weld_HAZ_allowable_Pa=None,weld_fatigue_allowable_Pa=None,
        preparation='Qualify oxide removal, filler and edge preparation for actual alloy, wall thickness and process.',
        unsupported=['Unwelded T6 yield is not the welded-node allowable','Distortion, HAZ softening, weld defects and fatigue require weld-procedure and coupon evidence']),
      dict(id='removable-panel-retention',sources=['clips','captive'],family='clip-plus-positive-retention',
        clip_model_lead='Fastmount PC-F1A female plus explicitly selected mating clip',panel_gap_m=.004,
        supplier_pullout_classes_kg=[2.,5.,10.,15.],installed_retention_force_N=None,clip_mass_kg=None,
        positive_fastener_lead='Matched captive threaded screw/receptacle; variant and grip range remain unselected',
        unsupported=['Listed pullout classes are not rail design loads','Manufacturer pullout classes are labelled in kg; no allowable force conversion applied','Clip material/fire, substrate pullout, vibration, removal cycles and accidental-release tests remain open']),
      dict(id='polycarbonate-flat-window',sources=['glazing'],family='glazing',density_kg_m3=1200.,
        typical_tensile_modulus_Pa=2.3e9,thermal_expansion_per_K=7e-5,expansion_measurement_range_C=[23.,55.],
        applications='Flat UV/mar-resistant sheet comparison only',
        unsupported=['Rail glazing, fire/smoke, impact and emergency-egress compliance not established by listed automotive tests','Fastener slots, seals, abrasion, cleaning and pressure/thermal movement need design']),
      dict(id='fire-retardant-flat-window',sources=['exolon'],family='glazing',density_kg_m3=1200.,typical_tensile_modulus_Pa=2.35e9,
        thermal_expansion_per_K=65e-6,expansion_measurement_range_C=[23.,55.],supplier_fire_class='UL94V0 at>=3mm for specified clear8099 new sheet',
        unsupported=['Typical mechanical properties were measured on injection-moulded samples; not specification values','UL94V0 is not rail fire/smoke approval; purchased sheet certificates, mounting, ageing, impact and emergency egress require evidence']),
      dict(id='modular-rail-hvac',sources=['hvac'],family='HVAC',supplier_module_mass_kg=125.,supplier_profile_height_m=.220,
        cooling_capacity_at_50C_W=None,electrical_power_at_50C_W=None,installed_module_count=None,
        unsupported=['Module mass excludes unspecified ducts, condensate, filters, supports, wiring and service clearance','No Baghdad50C capacity or redundancy duty is inferred from promotional power-density claims']),
    ]
    for r in records:
        r.update(deepcopy(FLAGS));r['design_allowable_Pa']=None;r['automatic_substitution_eligible']=False
        r['facts_sha256']=_id({key:v for key,v in r.items() if key!='facts_sha256'})
    value=dict(schema='osr-primary-joining-catalogue/1',accessed_UTC_date=ACCESSED,sources=deepcopy(SOURCES),entries=records,
        scope='Primary-source research leads, dimensional takeoffs and validation work; no selected or qualified installed joint',**FLAGS)
    value['catalogue_id']=_id(value);return value


def attachment_plan(strategy,support_points_m,*,overlap_m=.1,width_m=.05,bondline_m=.0002,core_thickness_m=.02,
                    pot_outer_diameter_m=.030,insert_outer_diameter_m=.012,fasteners_per_support=2):
    """Count proposed stock at explicit supports; absent hardware is never zero.

    Dimensions are proposed research variables, not manufacturer instructions.
    All actual supplier drawings, local load paths and acceptance remain open.
    """
    allowed=('bonded-flange','bond-plus-bolts','potted-insert','clip-plus-positive-retention','welded-node')
    if strategy not in allowed or not isinstance(support_points_m,list) or not support_points_m:raise ValueError('Named joint strategy and explicit supports required')
    for p in support_points_m:
        if len(p)!=3 or any(type(x) not in (int,float) or not isfinite(x) for x in p):raise ValueError('Finite3D support coordinates required')
    for x in (overlap_m,width_m,bondline_m,core_thickness_m,pot_outer_diameter_m,insert_outer_diameter_m):
        if type(x) not in (int,float) or not isfinite(x) or x<=0:raise ValueError('Positive finite joint dimensions required')
    if type(fasteners_per_support) is not int or fasteners_per_support<1:raise ValueError('Positive counted fasteners required')
    if insert_outer_diameter_m>=pot_outer_diameter_m:raise ValueError('Positive potting annulus required')
    n=len(support_points_m);rows=[]
    def stock(name,quantity,volume=None,density=None,basis='Unselected installation hardware'):
        rows.append(dict(id=name,quantity=quantity,unit_volume_m3=volume,density_kg_m3=density,
            mass_kg=None if volume is None or density is None else quantity*volume*density,basis=basis,unit_price_USD=None))
    if strategy in ('bonded-flange','bond-plus-bolts'):
        stock('dp490-bond',n,overlap_m*width_m*bondline_m,None,'Proposed bondline volume; density absent from pinned source')
        stock('surface-treatment-and-primer',n);stock('flange-or-local-reinforcement',n)
    if strategy in ('bond-plus-bolts','potted-insert'):
        volume=pi/4*(pot_outer_diameter_m**2-insert_outer_diameter_m**2)*core_thickness_m
        stock('ec3500-potting',n*fasteners_per_support,volume,650.,'Proposed annulus; supplier typical cured density, no pullout allowable')
        stock('threaded-insert',n*fasteners_per_support);stock('positive-bolt',n*fasteners_per_support);stock('nut-or-selected-locking-feature',n*fasteners_per_support)
        stock('washers',2*n*fasteners_per_support);stock('insulating-bushings',n*fasteners_per_support)
        stock('seal-and-edge-closeout',n);stock('backing-or-load-spreading-plate',n)
    if strategy=='clip-plus-positive-retention':
        stock('matched-clip-pair',n);stock('captive-positive-fastener-and-receptacle',n*fasteners_per_support)
        stock('core-reinforcement-and-edge-seal',n)
    if strategy=='welded-node':
        stock('extrusion-node-stock',n);stock('weld-filler',n);stock('inspection-access-and-finish',n)
    tasks=[dict(id='joint-coupon',status='planned',support_points=deepcopy(support_points_m),
        work='Test actual substrate/preparation/cure; assess peel, shear, bearing, pullout and failure mode at room and hot/wet conditions.'),
      dict(id='joint-fatigue-and-failure',status='planned',work='Apply service spectrum, vibration, preload/creep, disbond/fastener-loss and retention cases; inspect damage and repairability.'),
      dict(id='process-fit',status='planned',work='Confirm cure/core compatibility, electrical/corrosion isolation, tolerances, installation tools, removal access, sealing and fire/thermal behaviour.')]
    value=dict(schema='osr-counted-attachment-research-plan/1',catalogue_id=catalogue()['catalogue_id'],source_entry_ids={'bonded-flange':['bonded-flange-dp490'],'bond-plus-bolts':['hybrid-bond-positive-fasteners','potted-core-insert-ec3500'],'potted-insert':['potted-core-insert-ec3500'],'clip-plus-positive-retention':['removable-panel-retention'],'welded-node':['welded-al-extrusion-node']}[strategy],strategy=strategy,support_points_m=deepcopy(support_points_m),
        proposed_geometry=dict(overlap_m=overlap_m,width_m=width_m,bondline_m=bondline_m,core_thickness_m=core_thickness_m,
            pot_outer_diameter_m=pot_outer_diameter_m,insert_outer_diameter_m=insert_outer_diameter_m),
        stock=rows,known_stock_mass_subtotal_kg=sum(r['mass_kg'] for r in rows if r['mass_kg'] is not None),
        unknown_mass_stock_ids=[r['id'] for r in rows if r['mass_kg'] is None],complete_installed_joint_mass_kg=None,
        removed_core_mass_kg=None,net_installed_mass_delta_kg=None,design_allowable_Pa=None,acceptance_load_N=None,
        validation_tasks=tasks,price_unknown_is_zero=False,**FLAGS)
    value['plan_id']=_id(value);return value


def glazing_plan(width_m,height_m,thickness_m,*,product='polycarbonate-flat-window',temperature_C=(23.,55.)):
    """Sheet takeoff and free thermal growth; mounting/whole-window mass unknown."""
    entries={e['id']:e for e in catalogue()['entries']};e=entries.get(product)
    if e is None or e['family']!='glazing':raise ValueError('Sourced glazing product required')
    values=(width_m,height_m,thickness_m,*temperature_C)
    if any(type(x) not in (int,float) or not isfinite(x) for x in values) or min(width_m,height_m,thickness_m)<=0:raise ValueError('Finite positive pane geometry and temperatures required')
    if len(temperature_C)!=2 or temperature_C[1]<temperature_C[0]:raise ValueError('Ordered temperature endpoints required')
    measured=e['expansion_measurement_range_C'];inside=temperature_C[0]>=measured[0] and temperature_C[1]<=measured[1]
    dt=temperature_C[1]-temperature_C[0]
    return dict(product=product,catalogue_id=catalogue()['catalogue_id'],sheet_mass_kg=width_m*height_m*thickness_m*e['density_kg_m3'],
        free_expansion_width_m=e['thermal_expansion_per_K']*width_m*dt if inside else None,
        free_expansion_height_m=e['thermal_expansion_per_K']*height_m*dt if inside else None,
        thermal_model_domain='within published CTE measurement range' if inside else 'outside published CTE range; no extrapolation',
        complete_window_mass_kg=None,frame_mass_kg=None,seals_mass_kg=None,retention_mass_kg=None,installed_price_USD=None,
        validation_tasks=['Differential frame/pane thermal movement and seal compression','Retention, impact, pressure and egress tests','Rail fire/smoke, abrasion, UV and cleaning compatibility'],**FLAGS)
