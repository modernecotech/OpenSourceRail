"""Exact canonical 20 m prism stock for the optional native viaduct comparison.

No smoothing, reinforcement or installed-mass credit is introduced. The physical
candidate remains the civil geometry producer's identity; this wrapper identifies
only a CAD evaluation input and its explicitly counted stock occurrences.
"""
from copy import deepcopy
from math import fsum
from pathlib import Path
from engineering.station_rail.common import identity,digest
from engineering.design_search import civil_shape_geometry as geometry
from .cases import FLAGS

ROOT=Path(__file__).resolve().parents[3]
PRODUCER='engineering/design_search/craft_backends/viaduct_cases.py'
PROFILES=('reference','robust')


def sources(root=ROOT):
    return {n:digest(Path(root)/n) for n in (PRODUCER,
        'engineering/design_search/civil_shape_geometry.py',
        'engineering/station_rail/common.py','engineering/design_search/craft_backends/cases.py')}


def build(family,profile='reference',*,root=ROOT):
    if family not in geometry.FAMILIES or profile not in PROFILES:
        raise ValueError('Registered canonical family and reference/robust profile required')
    physical=geometry.generate(family,profile);quantities=geometry.quantities(physical)
    entities=[];measures={};mass={}
    for cell in physical['cells']:
        start,end=cell['x_start_m'],cell['x_end_m'];length=end-start
        for section in cell['sections']:
            name=cell['id']+'/'+section['id'];p=section['polygon_yz_m'];prop=geometry._properties(p)
            g=dict(at_m=[start,0.,0.],points_yz_m=deepcopy(p),length_m=length)
            e=dict(id=name,shape='profile',geometry=g,material=section['material'],
                source_cell_id=cell['id'],source_section_id=section['id'],
                basis='Exact source convex-polygon prism; physical stepping retained',
                source_candidate_id=physical['candidate_id'])
            volume=prop['area_m2']*length
            measures[name]=dict(volume_m3=volume,centroid_m=[(start+end)/2,*prop['centroid_yz_m']],
                bounds_m=[[start,min(y for y,z in p),min(z for y,z in p)],
                    [end,max(y for y,z in p),max(z for y,z in p)]])
            mass[name]=volume*physical['materials'][section['material']]['density_kg_m3']
            entities.append(e)
    volume=fsum(p['volume_m3'] for p in measures.values());stockmass=fsum(mass.values())
    if abs(volume-quantities['total_nominal_volume_m3'])>1e-9 or abs(stockmass-quantities['total_nominal_stock_mass_kg'])>1e-7:
        raise ValueError('Independent occurrence stock and canonical quantities differ')
    projection=dict(schema='osr-civil-cad-geometry/1',units='m',
        entities=[{k:e[k] for k in ('id','shape','geometry','material')} for e in entities])
    value=dict(schema='osr-viaduct-craft-case/1',case_id=family+'--'+profile,
        family=family,profile=profile,candidate_id=physical['candidate_id'],
        component_geometry_id=identity(projection),physical_definition=physical,
        units=dict(length='m',volume='m3',mass='kg',density='kg/m3'),
        coordinate_frame=deepcopy(physical['coordinate_frame']),span_m=20.,deck_width_m=2.,
        materials=deepcopy(physical['materials']),entities=entities,
        expected=dict(part_count=len(entities),part_measures=measures,
            total_volume_m3=volume,part_nominal_material_masses_kg=mass,
            total_nominal_stock_mass_kg=stockmass,
            centroid_m=[fsum(p['volume_m3']*p['centroid_m'][i] for p in measures.values())/volume for i in range(3)],
            nominal_material_centroid_m=[fsum(mass[n]*p['centroid_m'][i] for n,p in measures.items())/stockmass for i in range(3)]),
        canonical_quantities=quantities,source_sha256=sources(root),
        scope='Nominal material stock only; separate occurrence sums, not fused installed assembly',
        manufacturing_basis=dict(stock_geometry_exact=True,mould_design_verified=False,
            boundary_surface_is_not_mould_contact=True,
            physical_stepping_retained=True,smooth_surface_equivalence_claimed=False,
            complete_installed_mass_kg=None,complete_installed_cost=None),
        unresolved_installed_items=deepcopy(physical['unresolved_installed_items']),
        analysis_assumptions_supplied=False,reinforcement_or_composite_stiffness_credit=False,
        presentation_offset_applied=False,**FLAGS)
    value['case_definition_id']=identity(value)
    return value


def validate(value,*,root=ROOT):
    if value.get('schema')!='osr-viaduct-craft-case/1':raise ValueError('Canonical SI viaduct CAD case required')
    if value.get('case_definition_id')!=identity({k:v for k,v in value.items() if k!='case_definition_id'}):
        raise ValueError('Viaduct case definition seal differs')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('CAD stock cannot grant release')
    expected=build(value.get('family'),value.get('profile'),root=root)
    if value!=expected:raise ValueError('Canonical candidate, stock quantities, sources or unresolved scope differ')
    return True


def portfolio(*,root=ROOT):
    return [build(f,p,root=root) for f in geometry.FAMILIES for p in PROFILES]
