"""Independent geometry, accounting and receipt controls for unselected hubs."""
from copy import deepcopy
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path
import shutil

import pytest

from engineering.ferrite_maglev import interchange_hubs as hubs,operating_plan as op


def test_interval_union_counts_shared_connector_trunk_once():
    intervals=[[800.,0.],[200.,1000.],[1300.,1400.],[1400.,1300.],[2.,2.]]
    assert hubs.interval_union(intervals)==[[0.,1000.],[1300.,1400.]]
    assert sum(hi-lo for lo,hi in hubs.interval_union(intervals))==1100.


def test_disjoint_network_enumeration_never_uses_one_source_hub_twice():
    pairs=[('000','036'),('036','001'),('004','005'),('024','025'),('023','034'),('002','041'),('031','040')]
    edges=[dict(id=str(i),hub_ids=list(pair)) for i,pair in enumerate(pairs)]
    sets=hubs.disjoint_sets(edges)
    assert len(sets)==96 and max(map(len,sets))==6
    for selection in sets:
        ids=[h for edge in edges if edge['id'] in selection for h in edge['hub_ids']]
        assert len(ids)==len(set(ids))
    assert not any({'0','1'}<=set(selection) for selection in sets)


@pytest.mark.parametrize('length,area,spans,supports,parapet,rests',[(400.,1200.,16,17,800.,7),(750.,2250.,30,31,1500.,14)])
def test_connector_quantities_do_not_omit_structures_or_rest_positions(length,area,spans,supports,parapet,rests):
    q=hubs.bridge_quantities(length,hubs.load())
    assert q['deck_area_m2']==area==q['shade_roof_area_m2']
    assert (q['span_modules'],q['independent_support_positions'],q['parapet_length_m'],q['interior_rest_positions'])==(spans,supports,parapet,rests)
    assert q['capex_usd'] is None and not q['foundations_selected']


def test_independent_connector_links_keep_separate_spans_end_supports_and_rests():
    a=hubs.load()
    values=hubs.connector_quantities([dict(id='left',length_m=10.),dict(id='right',length_m=10.)],a)
    assert values['reference_horizontal_length_m']==20. and values['deck_area_m2']==60.
    assert values['span_modules']==2 and values['independent_support_positions']==4
    assert len(values['components'])==2 and not values['shared_end_support_or_foundation_credit']
    longer=hubs.connector_quantities([dict(id='one',length_m=400.),dict(id='two',length_m=750.)],a)
    assert longer['span_modules']==46 and longer['independent_support_positions']==48
    assert longer['interior_rest_positions']==21 and longer['deck_area_m2']==3450.


def geometry_fixture(lateral_m=0.):
    coordinate=lambda s:[math.degrees(s/op.EARTH_M),0.]
    path=dict(points=[coordinate(0.),coordinate(8000.)],cumulative_m=[0.,8000.],length_m=8000.)
    platforms=[];source=[]
    for identity,s in [('a',2000.),('b',2800.)]:
        shared=dict(id='x-'+identity,line='x',lon=coordinate(s)[0],lat=0.)
        cross=dict(id='y-'+identity,line='y',lon=coordinate(s)[0],lat=math.degrees(lateral_m/op.EARTH_M) if identity=='b' else 0.)
        platforms.extend([shared,cross]);source.append(dict(id=identity,lines=['x','y'],platforms=[shared['id'],cross['id']]))
    edge=dict(id='pair-a-b',hub_ids=['a','b'],source_hubs=source)
    context=dict(a=hubs.load(),stations={p['id']:p for p in platforms},lines={'x':dict(path=path,line=dict(shape='radial'),
        plan=dict(transfer_hubs=[dict(id='a',s_m=2000.),dict(id='b',s_m=2800.)]))})
    return context,edge,dict(line='x',from_hub='a',to_hub='b')


def test_midpoint_and_endpoint_place_actual_access_arms_preserving_crossline_platforms():
    context,edge,adjacency=geometry_fixture()
    midpoint=hubs.geometry_variant(context,edge,adjacency,'midpoint')
    endpoint=hubs.geometry_variant(context,edge,adjacency,'endpoint-a')
    assert midpoint['new_shared_line_stop_s_m']==2400.
    assert midpoint['maximum_reference_access_arm_m']==pytest.approx(400.)
    assert endpoint['maximum_reference_access_arm_m']==pytest.approx(800.)
    assert midpoint['independently_counted_unique_connector_length_m']==pytest.approx(800.)
    assert midpoint['maximum_crossline_platform_to_platform_via_hub_reference_walk_m']==pytest.approx(800.)
    assert midpoint['maximum_reference_access_minutes']['1.0']==pytest.approx(400/60)
    assert {p['id'] for p in midpoint['source_platform_records']}==set(context['stations'])
    assert all(p['original_crossline_boarding_platform_retained'] for p in midpoint['connectors'])
    assert not midpoint['true_compact_hub_geometry_demonstrated']


def test_offset_source_platform_geometry_cannot_be_hidden_by_hub_centroids():
    context,edge,adjacency=geometry_fixture(lateral_m=600.)
    value=hubs.geometry_variant(context,edge,adjacency,'midpoint')
    assert value['maximum_reference_access_arm_m']==pytest.approx(1000.,abs=.02)
    assert value['independently_counted_unique_connector_length_m']==pytest.approx(1400.,abs=.02)
    assert value['maximum_crossline_platform_to_platform_via_hub_reference_walk_m']==pytest.approx(1400.,abs=.02)
    assert value['long_walk_penalty']
    assert max(p['lateral_reference_branch_m'] for p in value['connectors'])==pytest.approx(600.,abs=.02)


@pytest.mark.parametrize('key,value',[('connector_clear_width_m',True),('walk_speeds_m_s',[0.]),('maximum_network_alternatives',True),('guideway_rerouting_allowed',True)])
def test_invalid_or_unbounded_policy_is_rejected(tmp_path,monkeypatch,key,value):
    text=hubs.INPUT.read_text();replacement=repr(value).lower() if not isinstance(value,list) else '[0.0]'
    import re
    text=re.sub(r'^'+key+r'\s*=.*$',key+' = '+replacement,text,flags=re.M)
    path=tmp_path/'input.toml';path.write_text(text);monkeypatch.setattr(hubs,'INPUT',path)
    with pytest.raises(ValueError):hubs.load()


@pytest.fixture(scope='module')
def packet(tmp_path_factory):
    directory=tmp_path_factory.mktemp('interchange-packet')
    hubs.publish(directory)
    return directory


def test_baghdad_bound_alternatives_preserve_source_ids_and_do_not_promote_hubs(packet):
    value=hubs.study();hubs.verify(packet)
    assert value['baseline']['operating_station_count']==273
    assert value['baseline']['canonical_city_summary_current']
    assert value['unique_pair_count']==7 and value['shared_line_adjacency_count']==8
    assert len(value['variants'])==24 and value['true_compact_candidate_count']==0
    assert value['matching_enumeration']['disjoint_pair_sets_including_empty']==96
    assert 8<=len(value['network_alternatives'])<=12
    assert len(value['source_access_platform_ids_preserved'])==159
    for variant in value['variants']:
        assert variant['complete_delta_cost_usd'] is None
        assert not variant['train_guideways_changed']
    for alternative in value['network_alternatives']:
        assert len(alternative['merged_interchange_ids'])==len(set(alternative['merged_interchange_ids']))
        assert not alternative['selected'] and alternative['complete_net_cost_delta_usd'] is None
        q=alternative['connector_quantity_screen']
        assert q['reference_horizontal_length_m']==pytest.approx(alternative['connector_reference_horizontal_length_m'])
        assert q['independent_support_positions']==sum(c['quantity_screen']['independent_support_positions'] for c in q['components'])
        assert not q['shared_end_support_or_foundation_credit']
    assert all(value[k] is False for k in hubs.FLAGS)


def test_compact_realignments_actually_meet_but_cannot_inherit_old_prices(packet):
    value=hubs.study();concepts=value['coordinated_realignment_concepts']
    assert len(concepts)==7
    for concept in concepts:
        assert concept['actual_internal_transfer_walk_m'] is None
        assert concept['fixed_line_guideways_physically_reach_common_h']
        assert concept['train_routing_switches']==0 and not concept['selected']
        for line in concept['line_proposals']:
            points=line['local_chord_coordinates']
            assert points[1]==concept['shared_hub_coordinate']
            assert line['proposed_local_chord_length_m']==pytest.approx(sum(op.distance(p,q) for p,q in zip(points,points[1:])))
            assert not line['old_price_reused'] and not line['existing_civil_classification_reused']
            assert line['required_station_tangent_m']==350. and not line['station_tangent_fitted']
            assert line['operational_profile'] is None and line['proposed_civil_cost_usd'] is None


def test_connector_threshold_excludes_fleet_and_unpriced_station_civil(packet):
    variant=next(v for v in hubs.study()['variants'] if v['id']=='pair-031-040/line-9/midpoint')
    c=variant['operating_and_cost_comparison'];length=c['connector_reference_horizontal_length_m']
    assert c['gross_station_electrical_target_credit_usd']==3075000.
    assert c['new_booster_and_mount_target_increment_usd']==0.
    assert c['priced_scope_connector_allowance_usd_per_reference_m']==pytest.approx(3075000./length)
    assert c['priced_scope_connector_allowance_usd_per_assumed_deck_m2']==pytest.approx(3075000./(3.*length))
    assert not c['cost_savings_proved'] and c['complete_net_cost_delta_usd'] is None
    prose=(packet/'README.md').read_text().split('031–040 on line 9 is a local midpoint case',1)[1].split('\n\n',1)[0]
    assert '$3,075,000' in prose
    assert f"${c['priced_scope_connector_allowance_usd_per_reference_m']:,.0f}/reference-m" in prose
    assert f"${c['priced_scope_connector_allowance_usd_per_assumed_deck_m2']:,.0f}/assumed-deck-m²" in prose


def test_presentation_words_and_dimensions_are_readable(packet):
    import xml.etree.ElementTree as ET
    text=' '.join(ET.parse(packet/'overview.svg').getroot().itertext())
    assert 'Green: 031–040' in text and 'about 471 m' in text
    assert 'Long arms at 024–025' in text and 'Shared 000–036–001' in text
    assert 'Purple: counterfactual 031–040' in text and '350 m tangents' in text
    prose=(packet/'README.md').read_text()
    assert 'The 350 m station tangent' in prose and 'The 100 m compact walk' in prose
    assert 'Walking sensitivities use 1.3, 1.0, 0.6 m/s' in prose
    assert 'The 3 m assumed passage' in prose and 'gives 96 people/min' in prose


def copied_packet(packet,tmp_path):
    output=tmp_path/'packet';shutil.copytree(packet,output);return output


def test_rehashed_numerical_tampering_is_rejected(packet,tmp_path):
    output=copied_packet(packet,tmp_path);value=json.loads(gzip.decompress((output/'study.json.gz').read_bytes()))
    value['variants'][0]['maximum_reference_access_arm_m']=1.
    value.pop('content_sha256');value['content_sha256']=sha256(hubs.encoded(value)).hexdigest()
    raw=hubs.encoded(value);compressed=gzip.compress(raw,mtime=0);(output/'study.json.gz').write_bytes(compressed)
    manifest=json.loads((output/'manifest.json').read_text());manifest.update(raw_bytes=len(raw),compressed_bytes=len(compressed),content_sha256=value['content_sha256'])
    manifest['files_sha256']['study.json.gz']=hubs.digest(output/'study.json.gz')
    (output/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='recalculated content'):hubs.verify(output)


def test_rehashed_presentation_tampering_is_rejected(packet,tmp_path):
    output=copied_packet(packet,tmp_path);(output/'overview.svg').write_text('<svg>approved</svg>')
    manifest=json.loads((output/'manifest.json').read_text());manifest['files_sha256']['overview.svg']=hubs.digest(output/'overview.svg')
    (output/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='presentation differs'):hubs.verify(output)


def test_actual_city_source_receipt_change_holds_publication(packet,monkeypatch):
    original=hubs.source_snapshot
    def changed(root):
        values=original(root);values['canonical-city-changed']='0'*64;return values
    monkeypatch.setattr(hubs,'source_snapshot',changed)
    with pytest.raises(ValueError,match='stale'):hubs.verify(packet)


def test_unknown_packet_inventory_and_release_claim_are_rejected(packet,tmp_path):
    output=copied_packet(packet,tmp_path);(output/'unowned.txt').write_text('x')
    with pytest.raises(ValueError,match='inventory'):hubs.verify(output)
    (output/'unowned.txt').unlink();manifest=json.loads((output/'manifest.json').read_text());manifest['engineering_accepted']=True
    (output/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='release'):hubs.verify(output)
