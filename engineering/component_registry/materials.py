"""Grade/form/process master: published typical facts and explicit hypotheses.

No catalogue entry supplies design allowables, delivered-lot qualification,
rail fire acceptance, a purchase price or manufacturing release.
"""
from copy import deepcopy
from .registry import identity,FLAGS,_number,_id

SOURCES={
 'review-20261028':dict(kind='user-engineering-review',title='OpenSourceRail v0.6 end-to-end completion review, 28 October 2026',url=None,document_sha256=None,retrieved=False,
     scope='Indicative family density ranges and proposed applications; not certified material properties'),
 'hydro-6082':dict(kind='primary-manufacturer-datasheet',title='Hydro EN AW-6082 technical datasheet, extruded products',url='https://www.hydro.com/Document/Index?id=7824&name=Hydro+EN+AW+6082.PDF',document_sha256=None,retrieved=False,
     scope='Search-index numerical facts only; direct URL retrieval failed. Source/grade must be confirmed before design use'),
 'hulamin-6082':dict(kind='primary-manufacturer-datasheet',title='Hulamin 6082 rolled products data sheet',url='https://www.hulamin.com/sites/default/files/downloads/6082%20Data%20Sheet.pdf',document_sha256='17526abe0e4a1b0778a05708d7e451a487947976cc21babcdcdd86118af082a0',retrieved=True,checked_UTC='2026-10-28',
     scope='Published room-temperature physical properties and stated sheet/temper scope; not installed design allowables'),
 'gurit-kerdyn':dict(kind='primary-manufacturer-datasheet',title='Gurit Kerdyn structural foam core TDS 14-0524',url='https://www.gurit.com/wp-content/uploads/bsk-pdf-manager/2024/12/TDS-Kerdyn-14-0524.pdf',document_sha256='37513540751a0b147706138283e34a8b362a03bc0a10501917390fcc273afb3b',retrieved=True,checked_UTC='2026-10-28',
     scope='Nominal80kg/m3 and typical75–85kg/m3 from manufacturer TDS; density range is not delivered-lot acceptance'),
 'sabic-9030':dict(kind='primary-manufacturer-datasheet',title='LEXAN 9030 and 9030TG sheet product datasheet 2021',url='https://ff.sabic.eu/uploads/resources/LEXAN_9030_and_9030TG_POLYCARBONATE_DATASHEET_2021.pdf',document_sha256=None,retrieved=False,
     scope='Published typical resin-derived sheet properties, not railway glazing qualification'),
}


def _material(grade,family,form,density,bounds,source_id,*,properties=None,processes=(),hypothesis=True):
    source=deepcopy(SOURCES[source_id]);source['source_id']=identity(source)
    value=dict(grade_id=grade,revision='A',family=family,manufactured_form=form,
       density_kg_m3=dict(nominal=float(density),lower=float(bounds[0]),upper=float(bounds[1]),
           basis='explicit-research-search-bounds' if source_id!='gurit-kerdyn' else 'supplier-typical-density-range-not-lot-acceptance',
           source_id=source['source_id']),
       properties=deepcopy(properties or {}),source_records=[source],
       directional_model=dict(fibre_type='E-glass' if family=='GFRP' else None,
           fibre_volume_fraction=None,stacking_sequence=None,E1_Pa=None,E2_Pa=None,G12_Pa=None,
           tensile_allowable_Pa=None,compressive_allowable_Pa=None,interlaminar_allowable_Pa=None,
           hot_wet_retention=None,fatigue_law=None,creep_law=None),
       process=dict(candidate_routes=list(processes),tooling=None,cure_schedule=None,tolerance_m=None,yield_fraction=None,
           inspection_method=None,repair_method=None,process_qualified=False),
       temperature_limits_C=None,rail_fire_smoke_toxicity_acceptance=None,qualified_design_allowables=None,
       physical_lot_id=None,origin_country=None,supplier_quote_id=None,unit_price_usd=None,
       composition_is_design_hypothesis=hypothesis,automatic_substitution_eligible=False,**FLAGS)
    value['material_id']=identity(physical_definition(value))
    value['material_evaluation_id']=identity(value);return value


def catalogue():
    rows=[
      _material('GFRP-EGLASS-HYPOTHESIS-1','GFRP','laminate-panel',1800,(1650,2000),'review-20261028',processes=('vacuum-infusion','bonded-modular-assembly')),
      _material('PET-KERDYN-80','PET-foam','core-sheet',80,(75,85),'gurit-kerdyn',processes=('core-cutting','bonded-sandwich'),hypothesis=False),
      _material('AL-6082-T6-EXTRUSION','aluminium','extrusion',2710,(2690,2730),'hydro-6082',properties={'E_typical_Pa':70e9,'G_typical_Pa':26e9,'cp_typical_J_kg_K':897.,'linear_expansion_typical_per_K':23.1e-6},processes=('extrusion','cutting','machining','joining'),hypothesis=False),
      _material('AL-6082-T651-SHEET','aluminium','rolled-sheet',2700,(2680,2720),'hulamin-6082',properties={'E_typical_Pa':70e9,'linear_expansion_typical_per_K':24e-6,'resistivity_typical_ohm_m_20C':.038e-6},processes=('sheet-cutting','forming','joining'),hypothesis=False),
      _material('STEEL-S355-HYPOTHESIS','steel','plate-and-structural-stock',7850,(7800,7900),'review-20261028',processes=('cutting','welding','machining')),
      _material('COPPER-CU-ETP-HYPOTHESIS','copper','conductor',8960,(8900,9000),'review-20261028',processes=('drawing','insulating','winding','termination')),
      _material('GLASS-LAMINATED-HYPOTHESIS','laminated-glass','retained-pane',2500,(2450,2550),'review-20261028',processes=('pane-cutting','laminating','retained-glazing')),
      _material('PC-LEXAN-9030','polycarbonate','sheet',1200,(1180,1220),'sabic-9030',properties={'E_tensile_typical_Pa':2.3e9,'linear_expansion_typical_per_K':7e-5,'conductivity_typical_W_m_K':.2},processes=('sheet-cutting','thermoforming','retained-glazing'),hypothesis=False),
      _material('CONCRETE-C40-HYPOTHESIS','reinforced-concrete','precast',2450,(2400,2500),'review-20261028',processes=('batching','reinforcement','casting','curing','inspection','erection')),
      _material('ADHESIVE-EPOXY-HYPOTHESIS','adhesive','bondline',1200,(1100,1300),'review-20261028',processes=('surface-preparation','mixing','controlled-bonding','cure')),
      _material('ELASTOMER-EPDM-HYPOTHESIS','elastomer','seal-or-bushing',1200,(1100,1400),'review-20261028',processes=('moulding','cutting','retained-seal-installation')),
      _material('STEEL-FASTENER-HYPOTHESIS','steel-fastener','bolt-nut-washer',7850,(7800,7900),'review-20261028',processes=('heading','thread-forming','coating','torque-controlled-assembly')),
    ]
    for r in rows:validate_material(r)
    result=dict(schema='osr-material-grade-form-process-catalogue/1',materials=rows,unknown_is_zero=False,
        scope='Published typical properties and explicit research density ranges; no qualified design allowables, actual lot, supplier availability, price or rail acceptance',**FLAGS)
    result['catalogue_id']=identity(result);return result


def physical_definition(row):
    directional=row['directional_model']
    return dict(grade_id=row['grade_id'],family=row['family'],manufactured_form=row['manufactured_form'],
        composition=dict(fibre_type=directional.get('fibre_type'),fibre_volume_fraction=directional.get('fibre_volume_fraction'),stacking_sequence=directional.get('stacking_sequence')),
        physical_process_state=row.get('physical_process_state'))


def reseal(row):
    value=deepcopy(row);value.pop('material_id',None);value.pop('material_evaluation_id',None)
    value['material_id']=identity(physical_definition(value));value['material_evaluation_id']=identity(value)
    validate_material(value);return value


def validate_material(row):
    if row.get('material_id')!=identity(physical_definition(row)) or row.get('material_evaluation_id')!=identity({k:v for k,v in row.items() if k!='material_evaluation_id'}):raise ValueError('Material physical/evaluation identity differs')
    if not isinstance(row.get('grade_id'),str) or not row['grade_id']:raise ValueError('Specific grade or named research hypothesis required')
    d=row['density_kg_m3'];lo,nom,hi=[_number(d.get(k),'material density',positive=True) for k in ('lower','nominal','upper')]
    if not lo<=nom<=hi:raise ValueError('Ordered material density interval required')
    if row.get('automatic_substitution_eligible') is not False or any(row.get(k) is not False for k in FLAGS):raise ValueError('Catalogue is not qualified hardware or substitution acceptance')
    for s in row['source_records']:
        if s['source_id']!=identity({k:v for k,v in s.items() if k!='source_id'}):raise ValueError('Material source identity differs')
        if s.get('document_sha256') is not None and not _id(s['document_sha256']):raise ValueError('Source content digest invalid')
        if s.get('retrieved') and s.get('document_sha256') is None:raise ValueError('Retrieved document needs actual digest')
    if d['source_id'] not in {s['source_id'] for s in row['source_records']}:raise ValueError('Density source is not owned')
    return True


def lookup(grade_id):
    return next(r for r in catalogue()['materials'] if r['grade_id']==grade_id)
