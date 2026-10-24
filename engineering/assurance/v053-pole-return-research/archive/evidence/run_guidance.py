"""Physically bounded guide-winding/mass-feedback sensitivities; no adoption."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util,json,math,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));OUT=Path(__file__).resolve().parent

def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
r=imported('pole_research',OUT/'run.py');top=imported('pole_topology',OUT/'run_topology.py');ctrl=imported('pole_controls',OUT/'run_controls.py');cm=r.cm


def winding_context(width,scale,turns,area,large=False):
    context=top.topology(r.context_for(width,scale,140.,23.5),1.);a,v,m,*tail=deepcopy(context);v.update(turns_guide=turns,copper_guide_mm2=area)
    outer=[.72 if large else .62,.188];inner=[.16*scale+.02,.10];height=.073;z=-.0765
    oldparts=[p for p in m['parts'] if not p['id'].startswith('winding/guide-')];newcoils=[];added=[]
    for side in (-1,1):
        coil=cm._coil(f'winding/guide-{side}',inner,outer,height,turns,area,z,.30*side,a)
        pack_volume=(outer[0]*outer[1]-inner[0]*inner[1])*height
        wire_side=math.sqrt(area*1e-6);enamel_t=m['cooling']['enamel_thickness_m']
        enamel_volume=coil['conductor_length_m']*((wire_side+2*enamel_t)**2-wire_side**2)
        fluid_volume=pack_volume-coil['copper_volume_m3']-enamel_volume
        if fluid_volume<0:raise ValueError('wire+enamel exceeds actual pack volume')
        copper=coil['copper_mass_kg'];enamel_mass=enamel_volume*1400.;fluid_mass=fluid_volume*m['cooling']['fluid_density_kg_m3'];packmass=copper+enamel_mass+fluid_mass
        coil.update(accounted_enamel_m3=enamel_volume,accounted_enamel_kg=enamel_mass,accounted_fluid_m3=fluid_volume,accounted_fluid_kg=fluid_mass,
            pack_volume_m3=pack_volume,total_accounted_pack_kg=packmass,wire_shape='Declared square-wire geometric hypothesis; actual conductor/bend/termination/packing unqualified',
            enamel_density_assumption_kg_m3=1400.,no_credit_against_retained_global_fluid_allocation=True)
        mixture_parts=[]
        for p in coil['parts']:
            mixture_parts.append(cm._box(p['id'],p['size_m'],p['at_m'],'counted-copper-enamel-fluid-pack',packmass/pack_volume,'new-winding',
                mixture=True,representation_scope='Actual pack envelope; countedCu/enamel/fluid mixture, not resolved individualturnCAD'))
        coil['parts']=mixture_parts;added.extend(mixture_parts)
        # Explicit1mm insulating sleeve and end flanges retain5mm total axial
        # stock clearance (73mm winding+2mm flanges inside80mm returnleg).
        def ring(identity,ins,outs,h,z0):
            tx=(outs[0]-ins[0])/2;ty=(outs[1]-ins[1])/2;cy=.3*side
            for sign in (-1,1):
                added.append(cm._box(identity+f'/x-{sign}',[tx,outs[1],h],[-outs[0]/2 if sign<0 else ins[0]/2,cy-outs[1]/2,z0],'glass-epoxy',1900.,'new-guide-bobbin'))
                added.append(cm._box(identity+f'/y-{sign}',[ins[0],ty,h],[-ins[0]/2,cy-outs[1]/2 if sign<0 else cy+ins[1]/2,z0],'glass-epoxy',1900.,'new-guide-bobbin'))
        inner_bobbin=[inner[0]-.002,inner[1]-.002]
        ring(f'guide-bobbin/{side}/sleeve',inner_bobbin,inner,height,z)
        for end,z0 in [('lower',z-.001),('upper',z+height)]:ring(f'guide-bobbin/{side}/{end}',inner_bobbin,[outer[0]+.002,outer[1]+.002],.001,z0)
        newcoils.append(coil)
    if large:
        relocated=[]
        for p in oldparts:
            if p['id'].startswith('connector/isolated-'):
                at=list(p['at_m']);at[0]=.37
                p=cm._box(p['id'],p['size_m'],at,p['material'],p['mass_kg']/p['volume_m3'],p['component_scope'],rated_current_a=120.,origin_confirmed=False,relocated_for_winding=True)
            relocated.append(p)
        oldparts=relocated
        # Count both30mmextensions of the original900mm cover/coldplate;
        # inherited rods/holes remain at±400mm, not erased by a new full box.
        for side in (-1,1):
            for name,thick,z0,scope in [('coldplate',.008,-.38,'new-cooling'),('cover',.002,-.372,'new-housing')]:
                added.append(cm._box(f'extended-{name}/{side}',[.03,.8,thick],[-.48 if side<0 else .45,-.4,z0],'aluminium',2700.,scope))
    m['coils']=[m['coils'][0],*newcoils];m['parts']=oldparts+added;m['mass_kg']=sum(p['mass_kg'] for p in m['parts'])
    # Actual newcoil/bobbin boxes are checked against every remaining source
    # stock/envelope box. This is nominalAABB fit, not tolerances or nativeCAD.
    changed=[p for p in m['parts'] if p['id'].startswith(('winding/guide-','guide-bobbin/'))];collisions=[]
    for p in changed:
        for q in m['parts']:
            if p['id']==q['id']:continue
            lo=np.maximum(p['at_m'],q['at_m']);hi=np.minimum(np.array(p['at_m'])+p['size_m'],np.array(q['at_m'])+q['size_m']);overlap=float(np.prod(np.maximum(0.,hi-lo)))
            if overlap>1e-12:collisions.append(dict(first=p['id'],second=q['id'],aabb_overlap_m3=overlap))
    fit=dict(nominal_aabb_clear=not collisions,collisions=collisions,turns_guide=turns,conductor_area_mm2=area,inner_m=inner,outer_m=outer,
        winding_height_m=height,bobbin_flange_m=.001,total_axial_margin_m=.08-height-.002,
        minimum_connector_x_clearance_m=(.37 if large else .32)-(outer[0]+.002)/2,cover_x_envelope_m=.96 if large else .9,
        winding_pair_copper_kg=sum(c['copper_mass_kg'] for c in newcoils),winding_pair_enamel_kg=sum(c['accounted_enamel_kg'] for c in newcoils),
        winding_pair_fluid_kg=sum(c['accounted_fluid_kg'] for c in newcoils),bobbin_kg=sum(p['mass_kg'] for p in added if p['component_scope']=='new-guide-bobbin'),
        source_guide_cooling_w_k=v['cooling_w_k'][1],qualified=False,
        holds=['Nominal pack-and-stock AABB only; not actual woundconductor routing/bends, tolerances, pressure/manifold/hose, native interference or physical fit.',
            'Existing globalfluid/manifold allocation retained; all new winding fluid/enamel is grosscounted without removalcredit. Enamel density1400kg/m3 and squarewire are explicit unqualified mass hypotheses.',
            'Guide cooling remains source18W/K unqualified; no improved conductance assumed from larger coil. Connector currentderating, harness/protection and higherturn RL/busvoltage remain open.'])
    return (a,v,m,*tail),fit


def main():
    start=time.monotonic();before=cm.sources();drivers={Path(p).relative_to(ROOT).as_posix():cm.digest(p) for p in (__file__,r.__file__,top.__file__,ctrl.__file__)};parent=cm.definition();rows=[]
    for width,scale in ((.0225,2.2),(.0225,2.4),(.025,2.4),(.0275,2.4)):
        for turns,area,large in ((140.,16.5,False),(200.,11.5,False),(200.,13.4,True),(280.,9.5,True),(200.,14.5,True)):
            identity=f'guide-w{width*1000:04.1f}-s{scale:.2f}-n{int(turns)}-a{area:.1f}-'+('wide'if large else 'fit')
            context,fit=winding_context(width,scale,turns,area,large);a,v,m,*_=context;aw3=parent['controlled_aw3_kg']+24*(m['mass_kg']-parent['module']['mass_kg']);target=aw3*r.G/24
            with r.installed(context):
                points=[ctrl.asymmetric(context,mult*target,lat*target) for mult,lat in ((1.,0.),(1.3,0.),(1.,.1),(1.3,.1))]
                fill=bool(max(c['fill_fraction'] for c in m['coils'])<=a['coil_fill_limit'])
                joint=points[2]
                screen=bool(fit['nominal_aabb_clear'] and fill and joint['map_valid'] and joint['continuous_current_density_screen'] and joint['constant_current_thermal_screen'])
                hypothesis=dict(id=identity,width_m=width,core_scale=scale,guide_turns=turns,guide_conductor_area_mm2=area,wide_pack=large,module_geometry=m,fit=fit)
                row=dict(hypothesis=hypothesis,research_hypothesis_sha256=sha256(cm.encoded(hypothesis)).hexdigest(),module_mass_kg=m['mass_kg'],controlled_aw3_kg=aw3,target_n_per_module=target,
                    coil_fill_fractions=[float(c['fill_fraction']) for c in m['coils']],coil_fill_pass=fill,simultaneous_points=points,conditional_nominal_aw3_lateral_screen=screen,
                    topology_sensitivity=True,source_flux_allocation='Useful-only lift andguide pole path sensitivity; unqualified3D topology',configuration_adopted=False,complete_system_feasible=False,**cm.FLAGS)
                rows.append(row);print(json.dumps(dict(id=identity,mass=m['mass_kg'],aw3=aw3,fit=fit['nominal_aabb_clear'],fill=fill,I=joint['required_current_a'],B=joint['max_core_b_t'],map=joint['map_valid'],J=joint['current_density_a_mm2'],thermal=joint['constant_current_thermal_equilibrium_c'],screen=screen)),flush=True)
    assert before==cm.sources() and all(cm.digest(ROOT/p)==h for p,h in drivers.items())
    result=dict(schema='osr-pole-return-guidance-winding-research/1',source_sha256={**before,**drivers},source_unchanged=True,cases=rows,executed_cases=len(rows),elapsed_s=time.monotonic()-start,
        configuration_adopted=False,complete_system_feasible=False,interpretation='Extra realwinding/bobbin/insulation/fluid/cover mass feeds24module AW3 before lift+lateral currents. Overfilled controls retained. Nominal fit and numerical screens do not establish3D maps, control, manufacturing or physical feasibility.',**cm.FLAGS)
    r.save('guidance-results.json',result);r.save('guidance-source-manifest.json',dict(source_sha256=result['source_sha256'],files_sha256={name:cm.digest(OUT/name) for name in ('run.py','run_topology.py','run_controls.py','run_guidance.py','guidance-results.json')},**cm.FLAGS));print('FINAL '+json.dumps(dict(cases=len(rows),screen=sum(row['conditional_nominal_aw3_lateral_screen'] for row in rows),elapsed_s=result['elapsed_s'])),flush=True)

if __name__=='__main__':main()
