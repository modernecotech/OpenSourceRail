from copy import deepcopy
import gzip
from hashlib import sha256
import json
import subprocess
import pytest

from engineering.outline import civil_evidence as ce
from engineering.station_rail.common import identity


def seal(value):
    value.pop('input_id',None);value['input_id']=identity(value);return value


@pytest.fixture
def prepared(tmp_path,monkeypatch):
    root=tmp_path/'repo';root.mkdir()
    subprocess.run(['git','-C',str(root),'init','-q'],check=True)
    directory=root/'cities/catalogue/region/country/Fixture/engineering/alignment';directory.mkdir(parents=True)
    grid=dict(width=5,height=2,cell_m=20.,bbox_west=1.,bbox_north=1.,m_per_deg_lat=100000.,m_per_deg_lon=100000.)
    data=(json.dumps(grid,sort_keys=True)+'\n').encode();(directory/'planning-grid.json').write_bytes(data)
    mask=bytes([0,100,0,255,0,0,0,0,0,0]);(directory/'planning-water-mask.bin.gz').write_bytes(gzip.compress(mask,mtime=0))
    receipt=dict(schema_version=2,city='fixture',mask_sha256=sha256(mask).hexdigest(),source='Synthetic independent test grid',
        sources_sha256={str((directory/'planning-grid.json').relative_to(root)):sha256(data).hexdigest()},limitations=[])
    (directory/'water-source-receipt.json').write_text(json.dumps(receipt))
    subprocess.run(['git','-C',str(root),'add','cities'],check=True)
    subprocess.run(['git','-C',str(root),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture'],check=True)
    revision=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    monkeypatch.setattr(ce,'PINNED_REVISION',revision)
    return ce.prepare(root,tmp_path/'cache')


def city():
    # Both endpoints are dry. Long segment crosses a wet and an unknown cell.
    return seal(dict(city=dict(slug='fixture'),lines=[dict(line_id='A',route_m=80.,
        coordinates=[[1.0001,.9999],[1.0009,.9999]],coordinate_chainages_m=[0.,80.],stops=[dict(id='retained')])],
        civil_segments=[dict(line_id='A',**{'class':'bridge'},from_m=0.,to_m=80.)],source_sha256={}))


def test_long_dry_endpoint_chord_detects_internal_water_and_unknown(prepared):
    report=ce.evaluate(city(),prepared)
    assert report['route_m_by_water_status']==pytest.approx(dict(dry=40.,wet=20.,unknown=20.))
    assert [(z['status'],round(z['from_m']),round(z['to_m'])) for z in report['lines'][0]['water_intervals']]==[
        ('dry',0,10),('wet',10,30),('dry',30,50),('unknown',50,70),('dry',70,80)]
    assert report['historical_revision']==prepared['revision']
    assert report['mask_raw_sha256']==prepared['cities']['fixture']['receipt']['mask_sha256']
    assert not report['physical_accepted'] and report['geometry_unchanged']


def test_revision_preserves_control_geometry_and_retains_nonzero_reserve_obligation(prepared):
    original=city();before=deepcopy(original);report=ce.evaluate(original,prepared);revised=ce.revise(original,report)
    assert original==before and revised['lines']==original['lines']
    assert revised['input_id']!=original['input_id']
    h=revised['civil_evidence_hypothesis']
    assert h['dry_legacy_bridge_obstruction_reserve_route_m']==pytest.approx(40.)
    assert h['nonzero_obstruction_reserve_or_hold_required'] and h['interface_holds']
    assert h['legacy_control_input_id']==original['input_id']
    assert not revised['selected_reference_changed']


def test_wet_tunnel_and_at_grade_are_preserved_with_interface_hold(prepared):
    value=city();value['civil_segments']=[dict(line_id='A',**{'class':k},from_m=a,to_m=b)
        for k,a,b in [('at-grade',0.,40.),('tunnel',40.,80.)]];seal(value)
    revised=ce.revise(value,ce.evaluate(value,prepared))
    assert {r['class'] for r in revised['civil_segments']}=={'at-grade','tunnel'}
    assert any(z['status']=='wet' for z in revised['civil_evidence_hypothesis']['interface_holds'])


def test_out_of_domain_never_becomes_dry(prepared):
    value=city();value['lines'][0].update(coordinates=[[.9998,.9999],[1.0012,.9999]],coordinate_chainages_m=[0.,140.],route_m=140.)
    value['civil_segments'][0]['to_m']=140.;seal(value)
    report=ce.evaluate(value,prepared)
    assert report['route_m_by_water_status']['out-of-domain']==pytest.approx(40.)
    revised=ce.revise(value,report)
    assert all(z['class']=='bridge' for z in revised['civil_segments'] if z['water_evidence_status']=='out-of-domain')


def test_actual_coordinates_not_stale_cells_and_vertex_counts_are_authoritative(prepared):
    value=city();value['lines'][0].update(coordinates=[[1.0001,.9997],[1.0005,.9997],[1.0009,.9997]],
        coordinate_chainages_m=[0.,40.,80.],cells=[[0,0],[0,4]],coordinate_basis=None);seal(value)
    assert ce.evaluate(value,prepared)['route_m_by_water_status']==pytest.approx(dict(dry=80.))


def test_cache_tampering_is_rejected(prepared):
    ce.evaluate(city(),prepared)
    obj=prepared['cities']['fixture']['objects']['mask'];path=__import__('pathlib').Path(prepared['cache'])/obj['oid']
    path.chmod(0o644);path.write_bytes(b'changed')
    with pytest.raises(ValueError,match='cache object'):ce.evaluate(city(),prepared)


def test_mask_receipt_mismatch_is_rejected(prepared):
    prepared['cities']['fixture']['receipt']['mask_sha256']='0'*64
    with pytest.raises(ValueError,match='receipt'):ce.evaluate(city(),prepared)


@pytest.mark.parametrize('change',[lambda x:x['lines'][0].update(coordinate_chainages_m=[0.,79.]),
    lambda x:x['civil_segments'][0].update(from_m=1.),lambda x:x['lines'][0].update(coordinates=[[float('nan'),1.],[1.,1.]])])
def test_incoherent_inputs_fail_instead_of_inventing_evidence(prepared,change):
    value=city();change(value)
    if str(value).find('nan')>=0:
        with pytest.raises(ValueError):seal(value)
    else:
        seal(value)
        with pytest.raises(ValueError):ce.evaluate(value,prepared)


def test_repeat_evaluation_and_cache_location_do_not_change_identity(prepared,tmp_path):
    a=ce.evaluate(city(),prepared)
    second=ce.prepare(prepared['root'],tmp_path/'other-cache')
    assert ce.evaluate(city(),second)==a
    wrong=deepcopy(a);wrong['evaluation_id']='0'*64
    with pytest.raises(ValueError):ce.revise(city(),wrong)
