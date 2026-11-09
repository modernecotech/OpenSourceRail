"""Invented tiny CAD leaves only; never export the retained actual R4 coupon."""
from copy import deepcopy
import json
from math import pi, prod
import subprocess
import sys
from types import SimpleNamespace

import pytest

from engineering import chair_native_geometry as c


@pytest.fixture(autouse=True)
def forbid_actual_producers(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Actual source/native producer forbidden in tiny tests')
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    monkeypatch.setitem(sys.modules, 'engineering.chair_installation', SimpleNamespace(
        chair_coupon=forbidden, compile_proposal=forbidden, volume_centroid=forbidden))


def box(*, bores=None):
    return dict(id='invented/plate', shape='box', material='invented/al',
                center_m=[2., 3., 4.], size_m=[2., 4., 6.], bores=bores or [])


def hole(axis=2, *, face=None, depth=1., center=None):
    h = dict(axis=axis, center_m=center or [2., 3., 4.], diameter_m=.2)
    if face is not None: h.update(depth_m=depth, entry_face=face)
    return h


def round_part(axis=0, inner=0.):
    return dict(id='invented/round', shape='cylinder', material='invented/al', axis=axis,
                start_m=[-.31, .27, -.91], length_m=.3, radius_m=.02, inner_radius_m=inner)


def fixture(entities=None):
    entities = deepcopy([box()] if entities is None else entities)
    recipe = dict(units='m', materials={'invented/al': dict(density_kg_m3=2700., rate_usd_kg=[1., 2., 3.])})
    # Fixture arithmetic deliberately does not import either source evaluator.
    def volume(e):
        if e['shape'] == 'cylinder':
            return pi*(e['radius_m']**2-e['inner_radius_m']**2)*e['length_m']
        return prod(e['size_m'])-sum(pi*(b['diameter_m']/2)**2*b.get('depth_m', e['size_m'][b['axis']]) for b in e['bores'])
    stock = [dict(id='invented/stock/'+str(i), material=e['material'], entity_ids=[e['id']],
                  net_volume_m3=volume(e), gross_volume_m3=volume(e)+.01,
                  scrap_volume_m3=.01, price_usd=10., tooling_allocation_usd=None) for i, e in enumerate(entities)]
    coupon = dict(schema='osr.chair-installation-proposal/1', recipe_id=c.identity(recipe),
        entities=entities, stock=stock, consumables=dict(welds=[],
            powder_coating=dict(net_mass_kg=[.01, .02, .03], centroid_hypothesis_m=[0., 0., 0.])),
        status=deepcopy(c.FLAGS))
    return coupon, recipe


def export(coupon=None, recipe=None, *, binding_change=None, units='m', pin=None):
    if coupon is None: coupon, recipe = fixture()
    a, b = c.encoded(coupon), c.encoded(recipe)
    binding = dict(source_commit='a'*40, source_module_sha256='b'*64,
        source_packet_manifest_sha256='c'*64, coupon_sha256=c.sha256(a).hexdigest(),
        recipe_sha256=c.sha256(b).hexdigest(),
        source_physical_definition_id=c.identity(c.source_physical_projection(coupon)),
        source_execution_id='d'*64)
    if binding_change: binding_change(binding)
    return c.export_definition(a, b, binding=binding, tool_pin=deepcopy(c.TOOL) if pin is None else pin, units=units)


def test_centered_box_corner_conversion_and_unchanged_local_datum():
    out = export()
    s = out['case']['entities'][0]; o = out['expected'][s['id']]
    assert s['corner_m'] == [1., 1., 1.] and o['volume_m3'] == 48.
    assert o['center_of_mass_m'] == [2., 3., 4.]
    assert o['bbox_m'] == dict(min=[1., 1., 1.], max=[3., 5., 7.])
    cmd = next(q for q in out['commands']['commands'] if q['command'] == 'solid.box')
    assert cmd['params']['corner'] == [1000., 1000., 1000.]
    assert out['numerical_domain']['stock_translation_m'] == [0., 0., 0.]
    assert out['actual_native_calls'] == 0 and all(out[k] is False for k in c.FLAGS)
    assert out['bounded_nonprimitive_allowances']['volume_m3'] is None
    assert out['bounded_nonprimitive_allowances']['included_in_native_material_solids'] is False


@pytest.mark.parametrize('axis', [0, 1, 2])
@pytest.mark.parametrize('face', [-1, 1, None])
def test_all_axes_through_and_both_blind_faces_have_true_start_and_centroid(axis, face):
    e = box(bores=[hole(axis, face=face)]); a, b = fixture([e]); out = export(a, b)
    o = out['expected'][e['id']]; solid = out['case']['entities'][0]
    depth = e['size_m'][axis] if face is None else 1.
    start = e['center_m'][axis]-e['size_m'][axis]/2 if face != 1 else e['center_m'][axis]+e['size_m'][axis]/2-depth
    assert solid['cuts'][0]['base_m'][axis] == start
    v = pi*.1**2*depth; hc = start+depth/2
    assert o['volume_m3'] == pytest.approx(48.-v, abs=1e-12)
    assert o['center_of_mass_m'][axis] == pytest.approx((48.*e['center_m'][axis]-v*hc)/(48.-v), abs=1e-12)
    cut = next(q for q in out['commands']['commands'] if q['command'] == 'solid.cylinder')
    assert cut['params']['base'][axis] == start*1000.
    assert cut['params']['height'] == depth*1000.
    assert cut['params']['axis'] == [float(k == axis) for k in range(3)]
    assert cut['params']['targets'] == [e['id']]


@pytest.mark.parametrize('axis', [0, 1, 2])
@pytest.mark.parametrize('inner', [0., .01])
def test_all_round_stock_axes_and_annuli(axis, inner):
    e = round_part(axis, inner); a, b = fixture([e]); out = export(a, b)
    o = out['expected'][e['id']]
    assert o['volume_m3'] == pytest.approx(pi*(.02**2-inner**2)*.3)
    assert o['center_of_mass_m'][axis] == pytest.approx(e['start_m'][axis]+.15)
    assert o['bbox_m']['min'][axis] == e['start_m'][axis]
    assert o['bbox_m']['max'][axis] == pytest.approx(e['start_m'][axis]+.3)
    cmds = [q['params'] for q in out['commands']['commands'] if q['command'] == 'solid.cylinder']
    assert len(cmds) == (2 if inner else 1)
    assert cmds[0]['base'] == [v*1000 for v in e['start_m']]
    if inner: assert cmds[1]['operation'] == 'cut' and cmds[1]['targets'] == [e['id']]


def test_nonzero_local_below_pan_round_datum_is_not_lifted():
    e = round_part(2, .01); out = export(*fixture([e]))
    assert out['case']['entities'][0]['start_m'][2] == -.91
    assert out['expected'][e['id']]['center_of_mass_m'][2] == pytest.approx(-.76)


def test_opposing_blind_bores_touching_at_end_are_disjoint_and_counted_once():
    e = box(bores=[hole(2, face=-1, depth=3.), hole(2, face=1, depth=3.)])
    _, o = c.solid_oracle(e)
    assert o['volume_m3'] == pytest.approx(48.-pi*.1**2*6.)


@pytest.mark.parametrize('mutate', [
    lambda e: e.update(shape='unresolved-envelope'),
    lambda e: e.update(size_m=[0., 1., 1.]),
    lambda e: e.update(size_m=[True, 1., 1.]),
    lambda e: e.update(center_m=[float('nan'), 0., 0.]),
    lambda e: e.update(unresolved_cut='unknown'),
    lambda e: e.update(bores=[hole(), hole()]),
    lambda e: e.update(bores=[hole(0), hole(2)]),
    lambda e: e.update(bores=[hole(2, face=1, depth=7.)]),
    lambda e: e.update(bores=[hole(2, face=True)]),
    lambda e: e.update(bores=[hole(2, center=[3.1, 3., 4.])]),
    lambda e: e.update(bores=[dict(axis=2, center_m=[2., 3., 4.], diameter_m=.2, depth_m=1.)]),
])
def test_invalid_or_unresolved_geometry_is_never_silently_omitted(mutate):
    e = box(); mutate(e)
    with pytest.raises(ValueError): c.solid_oracle(e)


@pytest.mark.parametrize('axis', [-1, 3, True, 'x', [1., 0., 0.]])
def test_legacy_axis_contract_is_explicit(axis):
    with pytest.raises(ValueError): c.solid_oracle(round_part(axis))


@pytest.mark.parametrize('mutate', [
    lambda a, b: a['entities'].append(deepcopy(a['entities'][0])),
    lambda a, b: a['entities'][0].update(id=''),
    lambda a, b: a['entities'][0].update(material='missing'),
    lambda a, b: a['stock'][0].update(entity_ids=[]),
    lambda a, b: a['stock'][0].update(material='wrong'),
    lambda a, b: a['stock'][0].update(net_volume_m3=2.),
    lambda a, b: a['stock'][0].update(gross_volume_m3=1.),
    lambda a, b: a['stock'].append(deepcopy(a['stock'][0])),
    lambda a, b: a.update(stock=[]),
    lambda a, b: b['materials']['invented/al'].update(density_kg_m3=-1.),
    lambda a, b: a['status'].update(physical_accepted=True),
    lambda a, b: b.update(units='mm'),
])
def test_identity_material_stock_units_and_status_refusals(mutate):
    a, b = fixture(); mutate(a, b); a['recipe_id'] = c.identity(b)
    with pytest.raises(ValueError): export(a, b)


@pytest.mark.parametrize('key', ['source_commit', 'source_module_sha256', 'coupon_sha256',
                                 'recipe_sha256', 'source_physical_definition_id', 'source_execution_id'])
def test_exact_source_binding_refuses_mismatches(key):
    with pytest.raises(ValueError): export(binding_change=lambda b: b.update({key: 'wrong'}))


def test_price_qa_tooling_metadata_never_changes_physical_geometry():
    a, b = fixture(); first = export(a, b)
    a['stock'][0].update(price_usd=9000., qa_hours=99., tooling_allocation_usd=120.)
    b['materials']['invented/al']['rate_usd_kg'] = [3., 6., 9.]
    a['recipe_id'] = c.identity(b); second = export(a, b)
    assert first['case']['source_physical_definition_id'] == second['case']['source_physical_definition_id']
    assert first['case']['component_geometry_id'] == second['case']['component_geometry_id']
    assert first['evaluation_id'] != second['evaluation_id']
    assert first['commands'] == second['commands']


def test_unknown_density_stays_unknown_without_losing_material():
    a, b = fixture(); b['materials']['invented/al']['density_kg_m3'] = None
    a['recipe_id'] = c.identity(b); out = export(a, b)
    assert out['expected']['invented/plate']['nominal_material_mass_kg'] is None
    assert not any(q['command'] == 'material.assign' for q in out['commands']['commands'])
    assert len(out['case']['entities']) == 1


def test_wrong_native_pin_and_units_refused():
    with pytest.raises(ValueError): export(pin=dict(c.TOOL, version='unreviewed'))
    with pytest.raises(ValueError): export(units='mm')


def test_script_refuses_tampered_geometry_identity():
    case = export()['case']; case['entities'][0]['corner_m'][2] += .15
    with pytest.raises(ValueError): c.script_for(case)


@pytest.mark.parametrize('mutate', [
    lambda x: x['entities'][0]['size_m'].__setitem__(0, -1.),
    lambda x: x['entities'][0].update(shape='unknown'),
    lambda x: x['entities'][0].update(unresolved_finish='not a material solid'),
    lambda x: x['entities'].append(deepcopy(x['entities'][0])),
    lambda x: x['entities'][0].update(material='missing'),
    lambda x: x['materials']['invented/al'].update(density_kg_m3=float('inf')),
    lambda x: x['entities'][0].update(cuts=[dict(axis=2, base_m=[2., 3., 2.], length_m=1., radius_m=.1)]),
])
def test_resealing_does_not_bypass_normalized_geometry_validation(mutate):
    case = export()['case']; mutate(case)
    case['component_geometry_id'] = c.identity({k: deepcopy(case[k]) for k in ('schema', 'units', 'frame', 'entities')})
    with pytest.raises(ValueError): c.script_for(case)


def test_source_and_new_component_geometry_identity_are_separate():
    out = export()
    assert out['case']['component_geometry_id'] != out['case']['source_physical_definition_id']
    assert out['native_comparison_plan']['SC'] == 'Tessellation diagnostic only'
    assert 'separate verdict' in out['native_comparison_plan']['strict_native_names']
