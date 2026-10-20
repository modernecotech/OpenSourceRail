"""Matched research registration, native subset honesty and independent controls."""
from copy import deepcopy
import shutil
import subprocess
import pytest
from engineering.twin_workflow import core
from engineering.panel_materials import study
from engineering.assembly_design import panel_adapter as adapter,reinforcement_options,civil_detail,families,baseline
from engineering.continuous_design import study_confirmation


@pytest.fixture(scope='module')
def examples():
    config,base=core.read(study.CONFIG),core.read(study.BASELINE)
    contexts,rows=study.generate_cases(config,base);byid={r['id']:r for r in rows};lookup={c['revision']:c for c in contexts}
    return [(config,base,lookup[row['context_revision']],row) for row in (byid[r['candidate_id']] for r in study.representatives(rows))]


def test_new_thermal_choices_retain_baseline_failures_and_unknown_complete_stack(examples):
    assert len(examples)==6
    for config,base,ctx,row in examples:
        if row['route'].startswith(('stiffened-aluminium','aluminium-sandwich')):
            assert row['variables']['thermal_backer_m']>.0 and row['screening_checks']['conduction_review']
        if row['kind']=='roof':assert row['core_grade']['continuous_max_temperature_c']==100
        assert row['mandatory_engineering_checks']['temperature-compatible complete stack and thermal-break attachment creep'] is None
        assert row['engineering_eligible'] is False and row['installed_cost_usd'] is None


@pytest.mark.parametrize('index',range(6))
def test_owned_section_geometry_is_reproducible_and_does_not_omit_installed_quantities(examples,index):
    config,base,ctx,row=examples[index];candidate,assessment=adapter.section(config,base,ctx,row)
    assert candidate['full_native_reconstruction'] is False
    assert candidate['complete_analytical_installed_mass_kg']==row['installed_mass_kg']
    mass=sum(p['properties']['mass_kg'] for p in candidate['contract']['parts'])
    assert mass<row['installed_mass_kg'] and candidate['unrepresented_mass_components']
    assert 'support_rails_brackets_fasteners' in candidate['unrepresented_mass_components']
    assert assessment['checks']['full-native-panel'] is None
    result=adapter.independent_controls(config,ctx,row,candidate)
    assert result['state']=='hold' if row['route']=='gfrp-sandwich' else all(result['checks'].values())
    broken=deepcopy(row);broken['installed_mass_kg']=0
    with pytest.raises(ValueError):adapter.section(config,base,ctx,broken)


def test_panel_adapter_is_registered_in_existing_qualified_runner():
    row=next(r for r in families.registry(core.read(baseline.DATA)) if r['id']=='body-panels')
    assert row['registered_for_bounded_design'] and row['execution']=='finite companion after registered queue'
    assert row['qualification']=='exact-source assembly qualification required'


def test_round_link_alternatives_include_bends_hooks_couplers_congestion_and_holds():
    snapshot=civil_detail.snapshot();result=reinforcement_options.build(snapshot['candidate'])
    assert len(result['alternatives'])==6
    assert {r['connection'] for r in result['alternatives']}=={'135-degree-hooks','two-U-bars-and-couplers'}
    for row in result['alternatives']:
        assert row['centreline_bend_radius_m']>row['diameter_m']/2
        assert row['proposed_bar_cut_length_m']==pytest.approx(row['rectangular_straights_m']+row['corner_arcs_m']+row['hook_arcs_m']+row['hook_tails_m'])
        assert row['bend_clearances'] and row['complete_installed_mass_kg'] is None
        assert row['eligible_for_cap_selection'] is False
        assert row['native_state'].startswith('hold')
        if row['couplers_per_link']:assert row['coupler_mass_each_kg'] is None


def test_native_metal_owned_section_mass_cg_inertia_and_reopen(tmp_path,examples):
    if not shutil.which('FreeCADCmd') and not shutil.which('freecadcmd'):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:
            pytest.skip('native FreeCAD unavailable')
    config,base,ctx,row=examples[0];candidate,assessment=adapter.section(config,base,ctx,row)
    path=tmp_path/'definition.json';core.write(path,candidate['contract'])
    proof,state,error=study_confirmation.native(path,tmp_path/'native')
    assert state=='passed',error
    assert proof['native_reopened'] and proof['step_volume_reconciled'] and proof['manufacturing_unit_ids_preserved']
    assert assessment['checks']['full-native-panel'] is None and not candidate['manufacturing_release']
