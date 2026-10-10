"""Connect spatial member histories to region laws, prestress and fatigue."""
from __future__ import annotations
from copy import deepcopy
from osr_mech.civil.exploration import geometry
from osr_mech.engineering_definition import fingerprint
from .constitutive import section_response,rainflow
from .materials import fatigue_damage,prestress


def assess(model,result,material_laws,*,age_days=28.,temperature_c=20.,prestress_inputs=None,sn_curves=None):
    if result['hardware_definition_sha256']!=fingerprint(model):raise ValueError('structural histories refer to a different shared definition')
    geo=geometry(model['bridge']['candidate']['definition']);span=model['bridge']['candidate']['definition']['deck']['span_m']
    groups={}
    for h in result['history']:
        for row in h['structural_member_demands']:
            if row['kind']!='deck':continue
            key=(row['track'],row['station_start'])
            groups.setdefault(key,[]).append(row)
    rows=[]
    for (track,start),history in groups.items():
        position=(start%span)+1e-8
        section=next(s for s in geo['deck'] if s['start_m']<=position<s['end_m'])
        row=max(history,key=lambda r:abs(r['moment_y_nm'])+abs(r['moment_z_nm']))
        demand={key:row[key] for key in ('axial_n','moment_y_nm','moment_z_nm')};losses=None
        if prestress_inputs is not None:
            losses=prestress(section,prestress_inputs)
            demand['axial_n']-=losses['effective_force_n']
            demand['moment_y_nm']+=losses['effective_force_n']*prestress_inputs['eccentricity_m']
        roles=section.get('material_roles',['concrete']*len(section['regions']));missing=sorted(set(roles)-set(material_laws))
        response=None if missing else section_response(section,material_laws,demand,age_days,temperature_c,fibers_per_region=4)
        # Signed elastic fibre spectrum for one declared gross-section location;
        # crack redistribution, local hot spots and multiaxial fatigue remain open.
        lever=section['top_m']-section['centroid_z_m']
        stress=[h['axial_n']/section['area_m2']+h['moment_y_nm']*lever/section['inertia_y_m4'] for h in history]
        cycles=rainflow(stress) if len(stress)>=2 else []
        fatigue={role:fatigue_damage(cycles,sn_curves[role]) if sn_curves and role in sn_curves else None for role in roles}
        rows.append(dict(track=track,station_start_m=start,material_roles=roles,missing_material_laws=missing,
            selected_simultaneous_demand=demand,section_response=response,prestress_loss_budget=losses,
            gross_fibre_cycles=cycles,fatigue=fatigue,capacity_accepted=False))
    return dict(schema='osr-spatial-assembled-materials/1',hardware_definition_sha256=fingerprint(model),
        dynamic_result_sha256=fingerprint(result),material_laws_sha256=fingerprint(material_laws),
        age_days=age_days,temperature_c=temperature_c,deck_sections=rows,
        physical_validation=False,engineering_released=False,
        open_gates=['history-dependent concrete unloading/crack redistribution', 'shear/torsion/local buckling',
                    'interfaces/anchorage and reinforcement detailing', 'pier/cap/foundation nonlinear capacity',
                    'measured material/S-N data and adopted limit states'])


def synthetic_laws(model):
    """Verification concrete with explicit synthetic age/temperature curves."""
    E=model['bridge']['candidate']['material']['youngs_modulus_pa'];fc=E*.001
    return dict(concrete=dict(type='concrete',basis='synthetic cubic/crack-band verification, no measured mix',
        age_modulus_pa=[[1.,E*.3],[28.,E],[365.,E*1.05]],
        age_strength_pa=[[1.,fc*.3],[28.,fc],[365.,fc*1.05]],
        temperature_modulus_factor=[[-20.,1.],[20.,1.],[80.,.8]],
        temperature_strength_factor=[[-20.,1.],[20.,1.],[80.,.8]],
        creep_coefficient=[[1.,0.],[28.,0.],[365.,1.5]],
        shrinkage_strain=[[1.,0.],[28.,0.],[365.,-.0002]],
        ft_pa=fc*.1,eps_c0=.002,eps_cu=.006,fracture_energy_n_m=100.,
        thermal_expansion_per_c=1e-5,reference_temperature_c=20.))
