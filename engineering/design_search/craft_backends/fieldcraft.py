"""Explicit-SI FieldCraft 0.7.5 numerical controls, never railway qualification.

Command recipes follow the pinned upstream axial-rod and hex20 cantilever
controls (MIT OR Apache-2.0). Geometry-linked set names are deliberate: changing
mesh density must not require inventing new support/load locations.
"""
from __future__ import annotations

import json
from math import isfinite, prod

UNITS = 'm-kg-s-N-Pa'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False)
# Declared before native measurements. These compare a 3D elastic continuum
# with a beam idealisation; they are not bridge/body acceptance criteria.
CANTILEVER = dict(length_m=1., width_m=.1, depth_m=.1, young_Pa=70e9,
                  poisson=0., tip_force_N=-1000., shear_factor=5/6,
                  theory_relative_tolerance=.02,
                  refinement_relative_tolerance=.005,
                  equilibrium_relative_tolerance=1e-7)
AXIAL = dict(length_m=.3, area_m2=1e-4, young_Pa=70e9, poisson=.3,
             tip_force_N=1000., theory_relative_tolerance=1e-9,
             equilibrium_relative_tolerance=1e-9)


def _cmd(command, **params):
    return dict(command=command, params=params)


def _divisions(value):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError('Three bounded integer mesh divisions required')
    if any(type(n) is not int or not 1 <= n <= 64 for n in value) or prod(value) > 1024:
        raise ValueError('Pilot mesh exceeds the declared 1024 hex20 element budget')
    return list(value)


def cantilever_theory():
    c = CANTILEVER
    L, b, h, E, nu, P = (c[k] for k in ('length_m', 'width_m', 'depth_m', 'young_Pa', 'poisson', 'tip_force_N'))
    I = b*h**3/12
    G = E/(2*(1+nu))
    return P*L**3/(3*E*I) + P*L/(c['shear_factor']*G*b*h)


def _cantilever_mesh(divisions):
    c = CANTILEVER; L, b, h = c['length_m'], c['width_m'], c['depth_m']
    return _cmd('mesh.block', body='OSR-Elastic-Control', kind='hex20',
        corners=[[0,0,0],[L,0,0],[L,b,0],[0,b,0],
                 [0,0,h],[L,0,h],[L,b,h],[0,b,h]],
        divisions=_divisions(divisions), faces={'6':'root','4':'tip'})


def _cantilever_queries():
    c = CANTILEVER
    return [_cmd('model.check'), _cmd('solve.static', step='Bend'),
            _cmd('solve.probe', step='Bend', at=[[c['length_m'],c['width_m']/2,c['depth_m']/2]]),
            _cmd('results.reactions', step='Bend', sets=['root']), _cmd('model.info')]


def cantilever_commands(divisions=(8, 2, 2)):
    """1m cantilever, explicit SI, hex20 and a total 1000N transverse load."""
    c = CANTILEVER
    return [_cmd('model.units', system=UNITS), _cantilever_mesh(divisions),
        *[_cmd('model.set.create', name=n, geometry=[dict(body='OSR-Elastic-Control', **({} if n=='all' else dict(face=n)))]) for n in ('all','root','tip')],
        _cmd('model.material.create', name='DeclaredElastic', elastic=dict(type='isotropic',young=c['young_Pa'],poisson=c['poisson'])),
        _cmd('model.section.create', name='solid', set='all', material='DeclaredElastic',kind=dict(type='solid')),
        _cmd('model.boundary_condition.create', name='clamp',type='fixed',target=dict(set='root')),
        _cmd('model.load.create', name='P',type='force',target=dict(set='tip'),vector=[0,0,c['tip_force_N']],distribution='total'),
        _cmd('model.step.create',name='Bend',procedure=dict(type='static'),boundary_conditions=['clamp'],loads=['P']),
        *_cantilever_queries()]


def remesh_cantilever_commands(divisions=(16, 4, 4)):
    """Replace only mesh: retain the named material/section/support/load/step.

    An empty ``mesh.clear`` only clears partition-stale bodies in 0.7.5; it
    does not clear this manually constructed block. Name the body explicitly.
    """
    return [_cmd('mesh.clear',bodies=['OSR-Elastic-Control']), _cantilever_mesh(divisions), *_cantilever_queries()]


def axial_commands():
    """A 0.3m axial rod with known EA, restrained transverse rigid modes."""
    c = AXIAL
    return [_cmd('model.units',system=UNITS),
        _cmd('mesh.node.add',label=1,xyz=[0,0,0]),
        _cmd('mesh.node.add',label=2,xyz=[c['length_m'],0,0]),
        _cmd('mesh.element.add',label=1,kind='rod2',nodes=[1,2]),
        _cmd('model.set.create',name='Rod',elements=[1]),
        _cmd('model.set.create',name='Root',nodes=[1]),
        _cmd('model.set.create',name='Tip',nodes=[2]),
        _cmd('model.set.create',name='AllNodes',nodes=[1,2]),
        _cmd('model.material.create',name='DeclaredElastic',elastic=dict(type='isotropic',young=c['young_Pa'],poisson=c['poisson'])),
        _cmd('model.section.create',name='AxialSection',set='Rod',material='DeclaredElastic',kind=dict(type='rod',area=c['area_m2'])),
        _cmd('model.boundary_condition.create',name='AxialSupport',type='displacement',target=dict(set='Root'),values=[0,None,None,None,None,None]),
        _cmd('model.boundary_condition.create',name='NoTransverseMotion',type='displacement',target=dict(set='AllNodes'),values=[None,0,0,None,None,None]),
        _cmd('model.load.create',name='Pull',type='force',target=dict(set='Tip'),vector=[c['tip_force_N'],0,0],distribution='total'),
        _cmd('model.step.create',name='Axial',procedure=dict(type='static'),boundary_conditions=['AxialSupport','NoTransverseMotion'],loads=['Pull']),
        _cmd('model.check'),_cmd('solve.static',step='Axial'),
        _cmd('solve.probe',step='Axial',at=[[c['length_m'],0,0]]),
        _cmd('results.reactions',step='Axial',sets=['Root']),_cmd('model.info')]


def batch_results(value, expected_count=None):
    """Decode raw MCP, a tool result, or a decoded batch; reject partial/error output."""
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict) or 'error' in value:
        raise ValueError('Successful structured FieldCraft response required')
    if 'result' in value:
        value = value['result']
    if not isinstance(value, dict):
        raise ValueError('Structured FieldCraft tool result required')
    if value.get('isError'):
        raise ValueError('FieldCraft reported a tool failure')
    if 'content' in value:
        if not isinstance(value['content'], list):
            raise ValueError('Structured FieldCraft content required')
        texts = [c['text'] for c in value['content'] if isinstance(c,dict) and c.get('type')=='text' and 'text' in c]
        if len(texts) != 1:
            raise ValueError('One structured batch result required')
        value = json.loads(texts[0])
    if not isinstance(value,dict) or value.get('ok') is not True or value.get('failed') is not None:
        raise ValueError('FieldCraft batch did not complete')
    results = value.get('results')
    if not isinstance(results,list) or type(value.get('completed')) is not int or value['completed']!=len(results):
        raise ValueError('Incomplete FieldCraft batch results')
    if expected_count is not None and len(results)!=expected_count:
        raise ValueError('FieldCraft result count differs from submitted commands')
    try:
        json.dumps(results, allow_nan=False)
    except (ValueError,TypeError) as exc:
        raise ValueError('Nonfinite or non-JSON FieldCraft results') from exc
    return results


def _vector(value):
    if not isinstance(value,list) or len(value)!=3 or any(type(x) not in (int,float) or not isfinite(x) for x in value):
        raise ValueError('Finite native SI vector required')
    return value


def _parse(results, *, step, tip, axis, theory, tolerance, equilibrium_tolerance, applied, root, kind):
    if len(results)<5:
        raise ValueError('Static solve, probe, reactions and model information required')
    check, solve, probe, reaction, info = results[-5:]
    if any(not isinstance(row, dict) for row in (check,solve,probe,reaction,info)):
        raise ValueError('Structured FieldCraft numerical readbacks required')
    if check.get('errors') != 0 or check.get('ready') is not True:
        raise ValueError('FieldCraft model check did not permit solving')
    if info.get('display_units')!=UNITS or info.get('own_units') is not True:
        raise ValueError('Explicit SI model units were not retained')
    for row in (solve,probe,reaction):
        if row.get('step')!=step:
            raise ValueError('Mixed FieldCraft step results')
    if solve.get('units')!=dict(length='m',force='N',pressure='Pa'):
        raise ValueError('Solve units must be metres, newtons and pascals')
    if probe.get('units',{}).get('displacement')!='m' or probe.get('units',{}).get('xyz')!='m':
        raise ValueError('Probe units must be metres')
    if reaction.get('units')!=dict(force='N',length='m',moment='N·m') or reaction.get('stale') is not False:
        raise ValueError('Current SI reactions required')
    nodes=probe.get('nodes',[])
    if not isinstance(nodes,list) or len(nodes)!=1 or not isinstance(nodes[0],dict) or max(abs(a-b) for a,b in zip(_vector(nodes[0].get('xyz')),tip))>1e-10:
        raise ValueError('Probe must resolve the exact declared physical point')
    displacement=_vector(nodes[0].get('displacement'))
    if not isinstance(reaction.get('total'),dict):
        raise ValueError('Native reaction totals required')
    total=_vector(reaction.get('total',{}).get('force'))
    moment=_vector(reaction['total'].get('moment'))
    if _vector(reaction.get('about'))!=[0,0,0]:
        raise ValueError('Reaction moment origin must be the declared root origin')
    sets=reaction.get('sets')
    if not isinstance(sets,list) or len(sets)!=1 or not isinstance(sets[0],dict) or sets[0].get('set')!=root:
        raise ValueError('Declared support reaction set required')
    support_force=_vector(sets[0].get('force'))
    support_moment=_vector(sets[0].get('moment'))
    if max(abs(a-b) for a,b in zip(support_force,total))>1e-7 or max(abs(a-b) for a,b in zip(support_moment,moment))>1e-7:
        raise ValueError('Support and total reaction readbacks disagree')
    supplied=_vector(reaction.get('applied'))
    if max(abs(a-b) for a,b in zip(supplied,applied)) > max(1e-9,max(map(abs,applied))*1e-12):
        raise ValueError('Native applied load differs from the declared control')
    solver_reaction=_vector(solve.get('reaction_total'))
    if max(abs(a-b) for a,b in zip(total,solver_reaction))>max(1e-8,max(map(abs,applied))*equilibrium_tolerance):
        raise ValueError('Independent reaction readbacks disagree')
    error=abs(displacement[axis]-theory)/abs(theory)
    residual=max(abs(a+b) for a,b in zip(total,applied))/max(map(abs,applied))
    applied_moment=[tip[1]*applied[2]-tip[2]*applied[1],
                    tip[2]*applied[0]-tip[0]*applied[2],
                    tip[0]*applied[1]-tip[1]*applied[0]]
    moment_residual=max(abs(a+b) for a,b in zip(moment,applied_moment))/max(1.,max(map(abs,applied_moment)))
    if type(info.get('nodes')) is not int or info['nodes']<2:
        raise ValueError('Native mesh counts required')
    elements=info.get('elements')
    if not isinstance(elements,dict) or set(elements)!={kind} or any(type(n) is not int or n<1 for n in elements.values()):
        raise ValueError('Positive native element counts required')
    return dict(scope='linear-isotropic numerical control; not a railway component qualification',
        step=step,units=dict(length='m',force='N',pressure='Pa'),
        displacement_m=displacement,probe_xyz_m=tip,reaction_N=total,applied_N=applied,
        reaction_moment_Nm=moment,support_set=root,
        theoretical_displacement_m=theory,relative_theory_error=error,
        force_equilibrium_relative_residual=residual,
        moment_equilibrium_relative_residual=moment_residual,
        numerical_screen_passed=error<=tolerance and max(residual,moment_residual)<=equilibrium_tolerance,
        comparison_tolerances=dict(theory_relative=tolerance,equilibrium_relative=equilibrium_tolerance),
        nodes=info['nodes'],elements=elements,declared_set_count=info.get('definitions',{}).get('sets'),
        geometry_linked_sets=kind=='hex20',
        warnings=solve.get('warnings',[]),**FLAGS)


def parse_cantilever_result(value, expected_count=None):
    results=batch_results(value,expected_count)
    c=CANTILEVER
    return _parse(results,step='Bend',tip=[c['length_m'],c['width_m']/2,c['depth_m']/2],axis=2,
        theory=cantilever_theory(),tolerance=c['theory_relative_tolerance'],
        equilibrium_tolerance=c['equilibrium_relative_tolerance'],applied=[0,0,c['tip_force_N']],root='root',kind='hex20')


def parse_axial_result(value, expected_count=None):
    c=AXIAL
    return _parse(batch_results(value,expected_count),step='Axial',tip=[c['length_m'],0,0],axis=0,
        theory=c['tip_force_N']*c['length_m']/(c['young_Pa']*c['area_m2']),
        tolerance=c['theory_relative_tolerance'],equilibrium_tolerance=c['equilibrium_relative_tolerance'],
        applied=[c['tip_force_N'],0,0],root='Root',kind='rod2')


def compare_refinement(coarse, fine):
    for row in (coarse,fine):
        if row.get('step')!='Bend' or row.get('units')!=dict(length='m',force='N',pressure='Pa'):
            raise ValueError('Equivalent SI bending controls required')
        if row.get('probe_xyz_m')!=[1.,.05,.05] or row.get('applied_N')!=[0,0,-1000.]:
            raise ValueError('Refinement must preserve load and probe interfaces')
        if any(row.get(k) is not False for k in FLAGS):
            raise ValueError('Research results cannot promote acceptance')
    if not fine['displacement_m'][2]:
        raise ValueError('Nonzero refinement displacement required')
    if fine['nodes']<=coarse['nodes']:
        raise ValueError('Fine mesh must contain more nodes')
    relative=abs(fine['displacement_m'][2]-coarse['displacement_m'][2])/abs(fine['displacement_m'][2])
    return dict(relative_tip_change=relative,tolerance=CANTILEVER['refinement_relative_tolerance'],
        refinement_screen_passed=relative<=CANTILEVER['refinement_relative_tolerance'],
        both_numerical_screens_passed=coarse['numerical_screen_passed'] and fine['numerical_screen_passed'],
        mesh_independence_established=False,qualification_scope='Two mesh levels are a bounded sensitivity check, not general convergence or physical validation',**FLAGS)
