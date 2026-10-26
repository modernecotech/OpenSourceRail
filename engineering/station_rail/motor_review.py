"""Read native motor results without promoting conditional fields into acceptance."""
from math import sqrt
from .common import identity
from . import FLAGS


def parallel_winding_options(full,dc_bus_V=750.):
    """Necessary arithmetic under equal flux allocation, not a circuit solution.

    Finite secondary overlap produces unequal coil fluxes. Dividing total
    series EMF does not establish the maximum branch EMF or current sharing.
    Preserve this as a lower-bound comparison until groups are spatially modelled.
    """
    if full.get('schema')!='osr-native-full-station-LIM-2D/1' or full.get('physical_accepted') is not False:
        raise ValueError('Unaccepted full-module research result required')
    n=full['configuration']['coils_per_phase_both_sides'];current=full['case']['current_RMS_A'];limit=dc_bus_V/sqrt(6)
    rows=[]
    for branches in (1,2,5,10,25,50):
        if n%branches:continue
        voltage=max(p['all_series_phase_voltage_RMS_V'] for p in full['phase_terminal_requirements'])/branches
        rows.append(dict(parallel_paths_per_phase=branches,series_coils_per_path=n//branches,
            current_RMS_A_each_path=current,total_converter_phase_current_RMS_A=current*branches,
            equal_flux_allocation_phase_voltage_RMS_V=voltage,
            dc_bus_V_hypothesis=dc_bus_V,ideal_inverter_phase_voltage_RMS_upper_bound_V=limit,
            arithmetic_voltage_screen='pass' if voltage<=limit else 'fail',
            actual_maximum_branch_voltage_RMS_V=None,actual_current_sharing_screen='unknown',
            primary_copper_loss_W=full['primary_copper_W'],
            additional_converter_switchgear_and_cable_mass_kg=None,
            converter_rating_and_thermal_screen='unknown',
            claim='Equal-group arithmetic only; actual finite-overlap branch fluxes require calculation'))
    return rows


def assess(short,full,required_force_N):
    if short['schema']!='osr-native-current-excited-LIM/1' or full['schema']!='osr-native-full-station-LIM-2D/1' or required_force_N<=0:
        raise ValueError('Declared native campaigns and positive force requirement required')
    if any(r.get(k) is not v for r in (short,full) for k,v in FLAGS.items()):raise ValueError('Method results cannot assert release')
    rows=short['cases'];coarse,medium,fine=rows[:3]
    force_change=abs(fine['force_N_finite_2D_primary']/medium['force_N_finite_2D_primary']-1)
    Bchange=abs(fine['maximum_steel_phasor_B_bound_T']/medium['maximum_steel_phasor_B_bound_T']-1)
    long_short=next(r for r in rows if r['case']['periods']==6)
    reverse=[r for r in rows if r['case']['speed_m_s']==0 and r['case']['frequency_Hz']==5]
    zero=next(r for r in rows if r['case']['current_peak_A']==0)
    forward=next(r for r in reverse if r['case']['phase_direction']==1);backward=next(r for r in reverse if r['case']['phase_direction']==-1)
    F=full['force_N_full9m_fin_2D'];B=full['maximum_steel_phasor_B_bound_T'];I=full['case']['current_peak_A']
    value=dict(schema='osr-LIM-native-assessment/1',short_evaluation_id=short['evaluation_id'],full_evaluation_id=full['evaluation_id'],
        full_motor_component_id=full['motor_component_id'],required_force_N_per_car=required_force_N,
        short_force_refinement_change_fraction=force_change,short_force_refinement_screen='pass' if force_change<.02 else 'fail',
        short_peak_field_refinement_change_fraction=Bchange,short_peak_field_refinement_screen='pass' if Bchange<.05 else 'fail',
        primary_length_force_per_m_ratio=(long_short['force_N_finite_2D_primary']/long_short['case']['active_length_m'])/(medium['force_N_finite_2D_primary']/medium['case']['active_length_m']),
        phase_reversal_relative_residual=abs(forward['force_N_finite_2D_primary']+backward['force_N_finite_2D_primary'])/abs(forward['force_N_finite_2D_primary']),
        zero_source_force_N=zero['force_N_finite_2D_primary'],
        maximum_relative_energy_residual=max(r['relative_energy_residual'] for r in [*rows,full]),
        force_N_full_geometry_2D=F,force_reserve_N=F-required_force_N,
        force_screen='pass' if F>=required_force_N else 'fail',
        linear_material_screen=full['linear_material_domain_screen'],
        conductor_current_screen=full['conductor_current_screen'],
        full_case_joint_necessary_screen='fail' if F<required_force_N or full['linear_material_domain_screen']=='fail' or full['conductor_current_screen']=='fail' else 'unknown',
        parallel_winding_comparisons=parallel_winding_options(full),
        local_peak_convergence_and_finite_height_confirmed=False,
        installed_available_force_N=None,next_selection_purpose='redesign or discriminating physical experiment',
        family_feasibility='This tested primary fails its declared screens; no conclusion that all LIM geometries fail.',
        **FLAGS)
    value['assessment_id']=identity(value);return value
