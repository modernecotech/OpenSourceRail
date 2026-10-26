"""Independent graph controls; source records below are synthetic test fixtures."""
from copy import deepcopy
import pytest
from engineering.design_search import interface_graph as g


def evidence():return {'validity':'supported','source_id':'fixture'}

def quantity(value,unit):return dict(value=value,unit=unit,**evidence())


def graph():
    a=dict(occurrence_id='supply/1',part_id='power-module',component_definition_id='2'*64,inventory_status='located',functions=['supply-power'],function_evidence={'supply-power':evidence()},stock={'mass_kg':10.},ports=[dict(id='dc',kind='electrical',units={'voltage':'V','current':'A'},frame_id='car',direction='source',connector='DC-link',data_validity=evidence(),ranges={'voltage':[650.,750.]},capacity={'current':quantity(50.,'A')})])
    b=dict(occurrence_id='load/1',part_id='service-module',component_definition_id='3'*64,inventory_status='located',functions=['service-power'],function_evidence={'service-power':evidence()},stock={'mass_kg':5.},ports=[dict(id='dc',kind='electrical',units={'voltage':'V','current':'A'},frame_id='car',direction='sink',connector='DC-link',data_validity=evidence(),ranges={'voltage':[600.,800.]},demand={'current':quantity(20.,'A')})])
    return dict(schema=g.SCHEMA,candidate_id='1'*64,requirement_revision='INTERFACE-TEST-1',
        components=[a,b],connections=[dict(id='power',**{'from':['supply/1','dc'],'to':['load/1','dc']})],required_functions=['supply-power','service-power'],
        frames={'car':{'unit':'m','handedness':'right'}},sources={'fixture':dict(kind='verified-simulation',sha256='4'*64,locator='Synthetic contract fixture',numerical_validity='converged',model_domain='supported')},
        assembly=[dict(id='install-supply',occurrences=['supply/1'],requires=[],hours=1.,data_validity=evidence()),dict(id='install-load',occurrences=['load/1'],requires=['install-supply'],hours=2.,data_validity=evidence())])


def codes(result):return {i['code'] for i in result['issues']}


def test_supported_declared_interfaces_match_without_qualifying_product():
    result=g.assess(graph())
    assert result['compatibility_status']=='pass' and result['declared_functions_preserved']
    assert result['stock']['known_stock_mass_kg']==15.
    assert result['stock']['complete_installed_mass_kg'] is None and result['stock']['complete_installed_cost_USD'] is None
    assert result['integrated_suitability']=='unknown'
    assert all(result[k] is False for k in g.FLAGS)
    assert result['evaluation_id']==g.identity({k:v for k,v in result.items() if k!='evaluation_id'})


def test_identity_and_eliminated_endpoint_references_fail_closed():
    for change in ('candidate','duplicate','endpoint','definition'):
        value=graph()
        if change=='candidate':value['components'][0]['candidate_id']='f'*64
        elif change=='duplicate':value['components'][1]['occurrence_id']='supply/1'
        elif change=='endpoint':value['connections'][0]['to']=['deleted','dc']
        else:value['components'][0]['component_definition_id']='unresolved'
        with pytest.raises(ValueError):g.validate_identity(value)
    before=graph();after=deepcopy(before);after['requirement_revision']='REVISED-POLICY'
    after['components'][0]['ports'][0]['capacity']['current']['value']=40
    assert g.physical_identity(before)==g.physical_identity(after)
    assert g.assess(before)['evaluation_id']!=g.assess(after)['evaluation_id']


def test_units_frames_connectors_directions_and_mechanical_dofs_are_explicit():
    for field,value,code in [('units',{'voltage':'kV','current':'A'},'unit-mismatch'),('frame_id','another-frame','frame_id-mismatch'),('connector','different-family','connector-mismatch'),('direction','source','direction-mismatch')]:
        c=graph();c['components'][1]['ports'][0][field]=value
        assert code in codes(g.assess(c)) and g.assess(c)['compatibility_status']=='fail'
    c=graph();a,b=[q['ports'][0] for q in c['components']]
    a.update(kind='mechanical',required_dofs=['Fx','Fz','Mx']);b.update(kind='mechanical',supported_dofs=['Fx','Fz'])
    assert 'load-dof-mismatch' in codes(g.assess(c))


def test_voltage_range_intersection_is_insufficient_without_controlled_point():
    c=graph();c['components'][0]['ports'][0]['ranges']['voltage']=[650,900]
    assert 'range-mismatch' in codes(g.assess(c))
    c['components'][0]['ports'][0]['selected_values']={'voltage':750}
    assert g.assess(c)['compatibility_status']=='pass'
    c['components'][0]['ports'][0]['selected_values']['voltage']=850
    assert 'selected-value-outside-range' in codes(g.assess(c))


def test_thermal_and_shared_capacity_use_actual_demands_and_keep_unknowns():
    c=graph();a,b=[q['ports'][0] for q in c['components']]
    for p in (a,b):p.update(kind='thermal',units={'duty':'W'},ranges={})
    a['capacity']={};a['demand']={'duty':quantity(100,'W')};b['demand']={};b['capacity']={'duty':quantity(80,'W')}
    assert 'capacity-exceeded' in codes(g.assess(c))
    b['capacity']['duty']['value']=None
    r=g.assess(c);assert r['compatibility_status']=='unknown' and 'capacity-unknown' in codes(r)
    c=graph();extra=deepcopy(c['components'][1]);extra['occurrence_id']='load/2';extra['ports'][0]['demand']['current']['value']=40;c['components'].append(extra)
    c['connections'].append(dict(id='second-power',**{'from':['supply/1','dc'],'to':['load/2','dc']}))
    c['assembly'].append(dict(id='install-extra',occurrences=['load/2'],requires=['install-supply'],data_validity=evidence()))
    assert 'load-sharing-unknown' in codes(g.assess(c))
    c['simultaneous_demands']=True
    assert 'combined-capacity-exceeded' in codes(g.assess(c))


def test_openings_and_mating_envelopes_do_not_receive_implicit_clearance():
    c=graph();box=dict(frame_id='car',min_m=[0,0,0],max_m=[1,1,1],kind='occupied',data_validity=evidence())
    c['components'][0]['envelopes']=[box];c['components'][1]['envelopes']=[{**box,'min_m':[2,0,0],'max_m':[3,1,1]}]
    c['openings']=[dict(id='door-opening',frame_id='car',min_m=[.5,.5,.5],max_m=[1.5,1.5,1.5],data_validity=evidence())]
    assert 'opening-keepout-intersection' in codes(g.assess(c))
    c['openings'][0]['min_m']=[5,0,0];c['openings'][0]['max_m']=[6,1,1]
    assert g.assess(c)['compatibility_status']=='pass'
    a,b=[q['ports'][0] for q in c['components']]
    a['envelope']={**box,'role':'required'};b['envelope']={**box,'role':'available','max_m':[.8,1,1]}
    assert 'mating-envelope-does-not-fit' in codes(g.assess(c))


def test_function_integration_preserves_obligations_and_only_known_subtotals():
    before=graph();before['required_functions']=['PV-mount','duct','roof-structure']
    before['components'][0]['functions']=['PV-mount','roof-structure'];before['components'][1]['functions']=['duct']
    after=deepcopy(before);after['candidate_id']='a'*64;after['components']=after['components'][:1]
    after['components'][0].update(part_id='integrated-roof',component_definition_id='b'*64,functions=list(before['required_functions']),ports=[],stock={'mass_kg':13.})
    after['connections']=[];after['assembly']=[dict(id='fit-integrated-roof',occurrences=['supply/1'],requires=[],hours=1.5,data_validity=evidence())]
    r=g.compare_integration(before,after)
    assert r['declared_function_coverage']=='pass' and r['occurrence_count_delta']==-1
    assert r['known_stock_mass_delta_kg']==-2 and r['known_declared_assembly_hours_delta']==-1.5
    assert r['after_compatibility_status']=='unknown' and r['integrated_suitability']=='unknown'
    after['components'][0]['functions'].remove('duct')
    assert g.compare_integration(before,after)['declared_function_coverage']=='fail'
    after['components'][0]['stock']['mass_kg']=None
    assert g.compare_integration(before,after)['known_stock_mass_delta_kg'] is None
    after['candidate_id']=before['candidate_id']
    with pytest.raises(ValueError,match='new candidate'):g.compare_integration(before,after)


def test_cycles_absent_assembly_dependencies_and_unconnected_ports_are_not_accepted():
    c=graph();c['assembly'][0]['requires']=['install-load']
    assert 'assembly-cycle' in codes(g.assess(c))
    c=graph();c['assembly'][0]['requires']=['missing-cut-operation']
    assert 'assembly-dependency-missing' in codes(g.assess(c))
    c=graph();c['connections']=[];c['components'][0]['ports'][0]['connection_required']=True
    assert 'unconnected-required-port' in codes(g.assess(c))
    c=graph();c['assembly']=[]
    r=g.assess(c);assert r['compatibility_status']=='unknown' and r['stock']['unknown_assembly_hours_operations']


def test_unknown_evidence_unlocated_stock_and_hypotheses_never_turn_into_passes():
    for mutate in ('source','capacity','location','validity'):
        c=graph()
        if mutate=='source':c['sources']['fixture']['kind']='supplier-typical'
        elif mutate=='capacity':c['components'][0]['ports'][0]['capacity']['current']['value']=None
        elif mutate=='location':c['components'][1]['inventory_status']='unlocated'
        else:c['components'][0]['ports'][0]['data_validity']['validity']='outside-domain'
        r=g.assess(c);assert r['compatibility_status']=='unknown' and not r['physical_accepted']
