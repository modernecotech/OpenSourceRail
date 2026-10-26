import pytest
from engineering.design_search import material_database as m


def record(result,name):return next(r for r in result['matches'] if r['id']==name)


def test_database_preserves_directional_supplier_facts_and_unknown_allowables():
    db=m.catalogue();r=next(r for r in db['records'] if r['id']=='core.al_5052_criii_31')
    assert r['properties']['shear_modulus_LT_Pa']['value']!=r['properties']['shear_modulus_WT_Pa']['value']
    assert r['properties']['shear_modulus_LT_Pa']['direction']=='LT'
    assert r['complete_orthotropic_matrix'] is None and r['strength_design_allowables'] is None
    assert r['hot_wet_design_allowables'] is None and r['fatigue_model'] is None
    assert all(x['installed_price_USD'] is None and x['unit_price_USD_per_kg'] is None for x in db['records'])
    assert all(not s['adapter_retrieved_document'] and not s['raw_bytes_independently_reverified'] for s in db['sources'].values())
    assert db['database_id']==m.identity({n:v for n,v in db.items() if n!='database_id'})


def test_function_form_density_and_process_filter_reports_partial_compatibility_only():
    result=m.search(dict(function='sandwich-core',forms=['foam-core'],maximum_density_kg_m3=100.,operating_temperature_C=23.),
        available_processes=['core-cutting','bonded-sandwich'])
    pet=record(result,'core.pet_t92_80');assert pet['status']=='compatible'
    assert not pet['automatic_substitution_eligible'] and not pet['physical_accepted']
    assert record(result,'joining.polycarbonate-flat-window')['status']=='excluded'
    assert result['selected_record_id'] is None


def test_continuous_temperature_claim_is_not_hot_strength_or_complete_model():
    req=dict(function='sandwich-core',operating_temperature_C=80.,require_hot_wet=True,
        property_requirements=[dict(name='compression_modulus_T_Pa',unit='Pa',value=10e6,direction='T')])
    result=m.search(req)
    assert record(result,'core.pvc_h80')['status']=='excluded'
    pet=record(result,'core.pet_t92_80');assert pet['status']=='unknown'
    assert 'no-temperature-extrapolation:compression_modulus_T_Pa' in pet['unknown']
    assert 'required-evidence-unavailable:hot_wet_design_allowables' in pet['unknown']
    result=m.search(dict(function='sandwich-core',require_complete_orthotropic_matrix=True,require_design_allowables=True))
    assert all(r['status']!='compatible' for r in result['matches'])


def test_direction_fire_and_cure_requirements_cannot_inherit_unrelated_evidence():
    r=m.search(dict(function='sandwich-core',property_requirements=[dict(name='shear_modulus_LT_Pa',unit='Pa',value=1.,direction='WT')]))
    assert 'direction-not-supported:shear_modulus_LT_Pa' in record(r,'core.al_5052_criii_31')['unknown']
    r=m.search(dict(function='window-pane',require_rail_fire=True))
    assert record(r,'joining.fire-retardant-flat-window')['status']=='unknown'
    assert 'required-evidence-unavailable:rail_fire_acceptance' in record(r,'joining.fire-retardant-flat-window')['unknown']
    r=m.search(dict(function='sandwich-insert'),available_processes=['ambient-bonding'])
    assert record(r,'joining.potted-core-insert-ec3500')['status']=='excluded'
    assert any('mandatory' in x for x in record(r,'joining.potted-core-insert-ec3500')['excluded'])
    r=m.search(dict(function='novel-integrated-roof-role'))
    assert all(x['status']=='unknown' for x in r['matches']) # New use is an evaluation task, not a physical ban.


def test_unit_mismatch_unsupported_conditions_and_cte_extrapolation_are_explicit():
    for req in ({'function':'sandwich-core','unrecognized_hard_requirement':True},
        {'function':'sandwich-core','functions':['window-pane']},{'function':'sandwich-core','require_fatigue':'yes'},
        {'function':'sandwich-core','maximum_density_kg_m3':float('nan')}):
        with pytest.raises(ValueError):m.search(req)
    with pytest.raises(ValueError,match='unit mismatch'):
        m.search(dict(function='sandwich-core',property_requirements=[dict(name='density_kg_m3',unit='g/cm3',value=1.)]))
    r=m.search(dict(function='window-pane',operating_temperature_C=70.,property_requirements=[dict(name='thermal_expansion_per_K',unit='1/K',value=.001,operator='<=')]))
    pane=record(r,'joining.polycarbonate-flat-window')
    assert pane['status']=='unknown' and 'no-temperature-extrapolation:thermal_expansion_per_K' in pane['unknown']
