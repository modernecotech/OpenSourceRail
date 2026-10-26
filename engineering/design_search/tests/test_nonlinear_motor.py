import pytest
from engineering.design_search import lim_materials as m,nonlinear_motor as n


def test_full_reference_law_is_bounded_and_has_positive_differential_mu():
    c=m.material();assert len(c['B_T'])==49 and c['supplier_grade'] is None
    for h in (0.,10.,100.,1000.,100000.):
        assert m.differential_mu(c,h)>0
        assert m.field_for_B(c,m.B(c,h))==pytest.approx(h)
    with pytest.raises(ValueError):m.B(c,c['H_A_m'][-1]+1)
    with pytest.raises(ValueError):m.field_for_B(c,2.5)
    with pytest.raises(ValueError):m.validate(dict(B_T=[0.,1.,2.],H_A_m=[0.,10.,100.]))


def test_nonlinear_circuit_force_matches_fixed_current_coenergy_gradient():
    c=m.material();g=.001;delta=1e-7;a=m.circuit(c,1500,g-delta);b=m.circuit(c,1500,g);d=m.circuit(c,1500,g+delta)
    assert -(d['coenergy_J']-a['coenergy_J'])/(2*delta)==pytest.approx(b['attraction_N'],rel=1e-5)
    with pytest.raises(ValueError):m.circuit(c,1e9,g)


def test_overlap_positions_generate_real_distinct_finite_geometry():
    rows=[n.overlap_case(p) for p in ('entry','centred','exit')]
    assert [r['secondary_start_x_m'] for r in rows]==[-.15,.10,.35]
    assert all(r['secondary_length_m']==.3 for r in rows)
    assert len({r['case_id'] for r in rows})==3


def test_native_tool_location_is_relative_to_the_imported_repository():
    assert n.TOOLS==n.ROOT
    assert n.GETDP==n.ROOT/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp'


def test_historical_snapshot_verification_needs_no_git_branch(tmp_path):
    from engineering.station_rail.common import encoded,identity,digest
    snapshot=tmp_path/'snapshot';snapshot.mkdir();(snapshot/'producer.py').write_text('retained source\n')
    raw=tmp_path/'raw';raw.mkdir();r=dict(execution='refused',**n.FLAGS);r['evaluation_id']=identity(r);(raw/'result.json').write_bytes(encoded(r))
    receipt=dict(source_sha256={'producer.py':digest(snapshot/'producer.py')},files_sha256={'result.json':digest(raw/'result.json')},**n.FLAGS)
    receipt['manifest_id']=identity(receipt);(raw/'manifest.json').write_bytes(encoded(receipt))
    assert n.verify(raw,root=tmp_path/'no-repository',source_snapshot=snapshot)['verified']
    (snapshot/'producer.py').write_text('modified source\n')
    with pytest.raises(ValueError,match='source differs'):n.verify(raw,source_snapshot=snapshot)
    with pytest.raises(ValueError,match='one historical'):n.verify(raw,source_snapshot=snapshot,source_revision='revision')
