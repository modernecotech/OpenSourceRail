"""Independent sandwich physics and quantity checks; no physical qualification."""
import copy,hashlib,importlib.util,json,math,sys
from pathlib import Path
import pytest
from osr_mech.rolling_stock import composite_panels as p
ROOT=Path(__file__).resolve().parents[3]
CONFIG=ROOT/'engineering/composite_panels/config/development.json'
def config():return json.loads(CONFIG.read_text())
def test_illustrative_two_skin_sandwich_is_7_4_kg_per_square_metre():
 # Independent user example, excluding installed features and bond/finish.
 assert 2*.0015*1800+.025*80==pytest.approx(7.4)
 c=config();q=p.panel_quantities(c,1,1,.0015,.0246)
 a=q['solid_land_area_m2'];holes=4*math.pi*.02**2
 expected_glass=5.4+a*.0246*1800
 expected_foam=(q['foam_area_m2']-holes)*.0246*80
 assert q['mass_kg']['glass']==pytest.approx(expected_glass)
 assert q['mass_kg']['core']==pytest.approx(expected_foam)
 assert q['installed_mass_kg']>q['mass_kg']['glass']+q['mass_kg']['core']
 assert q['cost_usd'] is None and not q['qualified']
def test_abd_matches_isotropic_faces_closed_form_and_has_zero_coupling():
 e=20e9;nu=.25;t=.0015;core=.025;bond=.0002
 material=dict(e1_pa=e,e2_pa=e,g12_pa=e/(2*(1+nu)),poisson12=nu)
 abd=p.laminate_abd(p.balanced_skin(t),core,bond,material)
 centre=core/2+bond+t/2
 d=2*e/(1-nu**2)*(t**3/12+t*centre**2)
 assert abd['D'][0][0]==pytest.approx(d)
 assert max(abs(x) for row in abd['B'] for x in row)<1e-6
 response=p.strip_response(abd,2000,1,core,30e6)
 # Free transverse moment yields E (rather than E/(1-nu²)) strip stiffness.
 assert response['bending_stiffness_nm']==pytest.approx(d*(1-nu**2))
 assert response['shear_deflection_m']==pytest.approx(2000/(8*30e6*.025))
def test_fibre_rotation_changes_anisotropic_stiffness_and_pressure_is_linear():
 c=config();q0=p.transformed_q(c['glass'],0);q90=p.transformed_q(c['glass'],90)
 assert q0[0][0]==pytest.approx(q90[1][1]);assert q0[0][0]>q90[0][0]
 abd=p.laminate_abd(p.balanced_skin(.0015),.0246,.0002,c['glass'])
 a=p.strip_response(abd,1000,1,.0246,30e6);b=p.strip_response(abd,2000,1,.0246,30e6)
 assert b['total_deflection_m']==pytest.approx(2*a['total_deflection_m'])
 aged=p.strip_response(abd,2000,1,.0246,30e6,stiffness_factor=.65,shear_factor=.5)
 assert aged['total_deflection_m']>b['total_deflection_m']
def test_overlapping_apertures_are_not_counted_twice_and_shared_edges_are_not_seals():
 cells=p.remaining_rectangles(2,2,[(0,0,1,1),(.5,.5,1.5,1.5)])
 assert p.area(cells)==pytest.approx(4-(1+1-.25))
 assert p.perimeter(p.remaining_rectangles(2,2,[(3,3,4,4)]))==pytest.approx(8)
 assert p.area(p.remaining_rectangles(1,1,[(-1,0,.2,1)]))==pytest.approx(.8)
def test_curved_roof_has_arc_area_and_real_layer_volumes():
 c=config();arc=p.roof_arc(2.35,.05)
 assert arc['arc_length_m']>2.35
 flat=p.cad_layers(c,width=.994,height=3.45,skin=.0015,core=.0246)
 roof=p.cad_layers(c,width=.994,height=2.35,skin=.0015,core=.0246,crown=.05)
 assert flat.volume/1e9==pytest.approx(.994*3.45*.0283)
 expected=.994*arc['arc_length_m']*(.0283+.0003*(.014+.00015)/arc['radius_m'])
 assert roof.volume/1e9==pytest.approx(expected)
 assert sum('GFRP ply' in obj.label for obj in flat.children)==16
 assert sum('metal insert' in obj.label for obj in flat.children)==4
 assert any('reinforced solid' in obj.label for obj in roof.children)
@pytest.mark.parametrize('value',[0,-1,float('nan'),float('inf'),True])
def test_invalid_dimensions_do_not_create_a_candidate(value):
 with pytest.raises(ValueError):p.balanced_skin(value)
def test_evidence_requires_current_candidate_units_and_original_file_hash(tmp_path):
 spec=importlib.util.spec_from_file_location('panelstudy',ROOT/'tools/automation/composite-panel-study.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 c=config();a=m.candidate(c,.0015,.0246,80,1,1,0,'side');changed=copy.deepcopy(c);changed['screen']['pressure_pa']=1000
 assert m.candidate(changed,.0015,.0246,80,1,1,0,'side')['candidate_id']!=a['candidate_id']
 f=tmp_path/'test.csv';f.write_text('Original independent measured result')
 r=json.loads((ROOT/'engineering/composite_panels/evidence/register.json').read_text())
 r['tests']=[dict(candidate_id=a['candidate_id'],source_path=f.name,source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),condition='dry',measurement='strip_deflection_m',measured_value=.004,uncertainty_m=.0001,units='m')]
 result=m.evidence_report(r,[a],tmp_path)
 assert result['correlations'][0]['residual_m']==pytest.approx(a['dry']['total_deflection_m']-.004)
 assert not result['release_accepted']
 f.write_text('Changed result')
 with pytest.raises(ValueError,match='changed'):m.evidence_report(r,[a],tmp_path)

def test_rib_mass_is_not_a_free_stiffness_improvement_and_fatigue_needs_data():
 rib=p.rib_quantities(1,.02,.0015,.015,2,1800)
 assert rib['mass_kg']==pytest.approx(2*.0015*(.015+.04)*1800)
 assert rib['stiffness_credit']==0 and not rib['bond_line_qualified']
 assert p.fatigue_sensitivity(10e6,1e6,None)['damage'] is None
 with pytest.raises(ValueError):p.fatigue_sensitivity(10e6,1e6,{})
 curve=dict(measured_evidence_sha256='a'*64,reference_stress_range_pa=20e6,reference_cycles=1e6,slope=3)
 assert p.fatigue_sensitivity(10e6,1e6,curve)['damage']==pytest.approx(1/8)
