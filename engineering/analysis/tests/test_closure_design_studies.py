"""Companion evidence keeps exclusions, exact source and portable copies."""
from copy import deepcopy
import pytest
from engineering.assembly_design import baseline,contracts,design_studies as studies,system_design,workflow
from engineering.twin_workflow import core


def test_choose_cannot_win_by_a_light_failed_variant():
    def item(revision,mass,fail):
        return (dict(revision=revision,contract=dict(parts=[dict(properties=dict(mass_kg=mass))])),
                dict(failed_checks=fail,held_checks=['external']))
    passed=item('passed',100.,[]);failed=item('failed',1.,['load'])
    assert studies._choose([failed,passed])==passed
    assert studies._choose([failed])==failed  # Diagnostic only; _model vetoes eligibility.


@pytest.mark.parametrize('first_state',('failed','hold'))
def test_native_failure_tries_next_alternative_but_tool_hold_stops(tmp_path,monkeypatch,first_state):
    variants=[(dict(kind='fixture',revision=identity,contract=dict(parts=[dict(properties=dict(mass_kg=mass))])),
               dict(failed_checks=[],held_checks=['external'])) for identity,mass in (('a',1.),('b',2.))]
    calls=[]
    def model(candidate,assessment,folder):
        calls.append(candidate['revision']);folder.mkdir()
        state=first_state if len(calls)==1 else 'passed'
        result=dict(native_state=state,eligible_for_research=state=='passed')
        core.write(folder/'result.json',result);return result
    monkeypatch.setattr(studies,'_model',model)
    pair,result,diagnostics=studies.confirm_alternatives(variants,tmp_path)
    if first_state=='failed':
        assert calls==['a','b'] and result['eligible_for_research'] and len(diagnostics)==1
        assert (tmp_path/diagnostics[0]['path']/'result.json').exists()
    else:assert calls==['a'] and result['native_state']=='hold' and not diagnostics


def test_ifc_geometry_drift_is_rejected_even_if_information_still_passes(tmp_path):
    import ifcopenshell
    from engineering.assembly_design import bim,structural_bay
    policy=core.read(baseline.DATA);candidate=structural_bay.build(policy,next(studies.models.candidates(policy,'structural-bay')))
    mesh=dict(parts=[dict(id=p['id'],vertices=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],faces=[[0,1,2]]) for p in candidate['contract']['parts']])
    bim.export(candidate,None,tmp_path,meshdata=mesh);core.write(tmp_path/'native-mesh.json',mesh)
    studies.verify_exchange_mesh(candidate,tmp_path)
    model=ifcopenshell.open(str(tmp_path/'assembly.ifc'));points=model.by_type('IfcCartesianPointList3D')[0]
    coords=list(points.CoordList);coords[0]=(9.,9.,9.);points.CoordList=coords;model.write(str(tmp_path/'assembly.ifc'))
    assert bim.verify(candidate,tmp_path/'assembly.ifc')['state']=='information-pass'
    with pytest.raises(ValueError,match='native triangles'):studies.verify_exchange_mesh(candidate,tmp_path)


@pytest.fixture
def package(tmp_path,monkeypatch):
    from engineering.assembly_design import civil_detail
    policy=baseline.validate(core.read(baseline.DATA));prepared=dict(policy=policy,prototype=contracts.prototype_configuration(),
        source_sha256={'fixture.py':'f'*64})
    monkeypatch.setattr(baseline,'sources',lambda:prepared['source_sha256'])
    config=system_design.defaults();config['duration_s']=10.;case=system_design.simulate(config)
    def report():
        v=dict(schema='fixture',electrical=system_design.electrical_architecture(),duty_cases=[case],refinement={},circuit=system_design.circuit_benchmark(),**core.FLAGS)
        v['revision']=core.digest(v);return v
    monkeypatch.setattr(system_design,'report',report)
    monkeypatch.setattr(studies,'_duty_media',lambda *args:dict(state='hold',reason='fixture excludes rendering'))
    monkeypatch.setattr(studies.study_confirmation,'native',lambda *args:(None,'hold','fixture deliberately unavailable'))
    monkeypatch.setattr(civil_detail,'candidates',lambda:[dict(bar_diameter_m=.020,bars_per_layer=10,link_spacing_m=.25)])
    original_candidates=studies.models.candidates
    monkeypatch.setattr(studies.models,'candidates',lambda policy,kind:iter([dict(rail_wall_m=.003,crossmember_count=2,floor_thickness_m=.016)]) if kind=='structural-bay' else original_candidates(policy,kind))
    original=studies.itertools.product
    monkeypatch.setattr(studies.itertools,'product',lambda *values,**kw:original(*values,**kw) if len(values)!=3 or values[0]!=(.003,.006,.009) else iter([(.009,.006,.25)]))
    folder=tmp_path/'studies';value=studies.build(prepared,folder)
    return folder,prepared,value


def reseal(folder,prepared):
    (folder/'receipt.json').unlink()
    workflow.seal(folder,dict(schema='osr-closure-studies-receipt/1',epoch=core.digest(prepared)))


def test_build_retains_three_models_unissued_requests_and_native_holds(package):
    folder,prepared,value=package
    assert len(value['models'])==3 and all(v['native_state']=='hold' and not v['eligible_for_research'] for v in value['models'])
    requests=core.read(folder/'prototype-test-requests.json')
    assert len(requests)==3 and all(r['component_revision'] and not r['issued'] and not r['build_authorised'] for r in requests)
    assert studies.verify(folder,prepared)==value
    assert (folder/'parts.csv').read_text().count('\n')>200


@pytest.mark.parametrize('defect',('source','promoted','presentation','hidden-failure','fake-native','part-mass','qa','rfq','search'))
def test_resealed_inner_inconsistency_fails(package,defect):
    folder,prepared,value=package
    if defect=='source':
        value['sources_sha256']={};core.write(folder/'summary.json',value)
    elif defect=='presentation':(folder/'index.html').write_text('Complete designs')
    elif defect=='hidden-failure':
        model=value['models'][0];path=folder/model['kind']/'assessment.json';r=core.read(path)
        r['checks']['unexpected-mandatory-failure']=False;core.write(path,r)
    elif defect=='promoted':
        value['models'][0]['eligible_for_research']=True;core.write(folder/'summary.json',value)
        core.write(folder/value['models'][0]['kind']/'result.json',value['models'][0])
        (folder/'index.html').write_text(studies.report_html(value))
    elif defect=='fake-native':
        value['models'][0]['native_state']='passed';core.write(folder/'summary.json',value)
        core.write(folder/value['models'][0]['kind']/'result.json',value['models'][0])
        (folder/'index.html').write_text(studies.report_html(value))
    elif defect=='part-mass':(folder/'parts.csv').write_text('forged mass')
    elif defect=='qa':core.write(folder/value['models'][0]['kind']/'qa-plan.json',[])
    elif defect=='rfq':
        r=core.read(folder/'prototype-test-requests.json');r[0]['included_component_scope']='Complete qualified viaduct';core.write(folder/'prototype-test-requests.json',r)
    else:
        r=core.read(folder/'search.json');r['eligible_research_revisions']=['invented'];core.write(folder/'search.json',r)
    reseal(folder,prepared)
    with pytest.raises((ValueError,FileNotFoundError,KeyError)):studies.verify(folder,prepared)


def test_changed_source_rejected_even_if_receipts_resealed(package):
    folder,prepared,_=package;changed=deepcopy(prepared);changed['source_sha256']['new.py']='1'*64
    with pytest.raises(ValueError):studies.verify(folder,changed)
