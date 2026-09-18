"""Execute a controlled edit of tracked native geometry and real solver reruns.

Run only inside FreeCADCmd. CONFIG and OUTPUT are supplied by the host runner.
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import FreeCAD as App
import Part

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/component-catalogue/src'))
from osr_mech.freecad_assembly_review import _canonicalise_fcstd
from osr_mech.freecad_fea import _parse_dat_fields


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def quantities(doc,config):
    leaves=[o for o in doc.Objects if o.TypeId=='Part::Feature' and hasattr(o,'OSRId')]
    target=doc.getObject(config['object'])
    if target is None or getattr(target,'OSRId',None)!=config['component']:raise ValueError('CAD component identity differs')
    box=target.Shape.BoundBox
    if not leaves or target not in leaves:raise ValueError('Controlled native product solid missing')
    for obj in leaves:
        if obj.Shape.isNull() or not obj.Shape.isValid() or obj.Shape.Volume<=0:raise ValueError('Invalid CAD solid')
    aggregate=doc.getObject('PartGeometry')
    if aggregate is not None and not math.isclose(aggregate.Shape.Volume,sum(o.Shape.Volume for o in leaves),rel_tol=1e-9):
        raise ValueError('Aggregate display geometry differs from controlled leaves')
    volume=target.Shape.Volume
    if not math.isclose(volume,box.XLength*box.YLength*box.ZLength,rel_tol=1e-9):
        raise ValueError('This screened member must be a full rectangular solid')
    convert=config['density_kg_m3']*1e-9
    return dict(component=config['component'],object=target.Name,primitive=target.PrimitiveId,
        width_mm=box.XLength,length_mm=box.YLength,depth_mm=box.ZLength,
        member_volume_mm3=volume,kit_volume_mm3=sum(o.Shape.Volume for o in leaves),
        member_mass_kg=volume*convert,other_solids_mass_kg=sum(o.Shape.Volume for o in leaves if o!=target)*convert,
        member_purchase_kg=round(volume*convert*(1+config['purchase_allowance']),6),
        other_purchase_kg=round(sum(o.Shape.Volume for o in leaves if o!=target)*convert*(1+config['purchase_allowance']),6),
        solids={o.Name:dict(volume_mm3=o.Shape.Volume,brep_sha256=hashlib.sha256(o.Shape.exportBrepToString().encode()).hexdigest()) for o in leaves},
        basis='Gross design-reference solid volumes, not measured mass or fabricated hollow-section quantities')


def solve(q,config,out):
    out.mkdir();results=[];length=q['length_mm'];width=q['width_mm'];depth=q['depth_mm']
    e=config['youngs_modulus_mpa'];nu=config['poisson_ratio'];force=config['screening_point_load_n']
    inertia=width*depth**3/12;area=width*depth;shear=e/(2*(1+nu))
    # Midspan displacement for a simply supported, centre-loaded rectangular
    # beam. Include Timoshenko shear with rectangular kappa=5/6.
    analytical=force*length**3/(48*e*inertia)+force*length/(4*(5/6)*shear*area)
    for n in config['mesh_elements']:
        folder=out/str(n);folder.mkdir()
        # B32 quadratic beams expanded by CalculiX to quadratic solids.
        nodes=[f'{i+1},{length*i/(2*n):.12g},0,0' for i in range(2*n+1)]
        lines=['*HEADING','OSR controlled member screening; mm N MPa','*NODE',*nodes,
            '*ELEMENT,TYPE=B32,ELSET=MEMBER',*[f'{i+1},{2*i+1},{2*i+2},{2*i+3}' for i in range(n)],
            '*NSET,NSET=MID',str(n+1),'*MATERIAL,NAME=STEEL','*ELASTIC',f'{e},{nu}',
            '*BEAM SECTION,ELSET=MEMBER,MATERIAL=STEEL,SECTION=RECT',f'{width:.12g},{depth:.12g}',
            '0,1,0','*BOUNDARY','1,1,4,0',f'{2*n+1},2,3,0',
            '*STEP','*STATIC','*CLOAD',f'{n+1},3,{-force}',
            '*NODE PRINT,NSET=MID','U','*EL PRINT,ELSET=MEMBER','S','*END STEP','']
        deck=folder/'member.inp';deck.write_text('\n'.join(lines))
        result=subprocess.run(['ccx','member'],cwd=folder,capture_output=True,text=True,timeout=120)
        # Empty SPOOLES scratch is excluded by repository policy; retain the
        # solver deck, actual result fields, convergence data and full log.
        (folder/'spooles.out').unlink(missing_ok=True)
        (folder/'solver.log').write_text(result.stdout+result.stderr)
        if result.returncode:raise RuntimeError('CalculiX failed; inspect solver.log')
        fields=_parse_dat_fields(folder/'member.dat')
        if n+1 not in fields.displacements or not fields.element_von_mises_mpa:raise ValueError('Missing solver fields')
        displacement=abs(fields.displacements[n+1][2])
        results.append(dict(elements=n,midspan_displacement_mm=displacement,
            max_von_mises_mpa=max(fields.element_von_mises_mpa.values()),deck_sha256=sha(deck),
            result_sha256=sha(folder/'member.dat')))
    relative=abs(results[-1]['midspan_displacement_mm']/results[-2]['midspan_displacement_mm']-1)
    error=abs(results[-1]['midspan_displacement_mm']/analytical-1)
    passed=relative<=config['mesh_relative_tolerance'] and error<=config['analytical_relative_tolerance']
    result=dict(schema='osr-member-screening/1',passed=passed,maturity='screening',
        analytical_displacement_mm=analytical,analytical_relative_error=error,
        mesh_relative_change=relative,meshes=results,
        limitations=config['scope'],independently_accepted=False)
    write(out/'summary.json',result)
    if not passed:raise ValueError('Mesh or analytical benchmark failed')
    return result


def main(config,output):
    output=Path(output);source=ROOT/config['source_cad'];source_hash=sha(source)
    document=App.openDocument(str(source));baseline=quantities(document,config)
    target=document.getObject(config['object']);box=target.Shape.BoundBox
    scale=config['candidate_depth_mm']/box.ZLength
    matrix=App.Matrix();matrix.A33=scale;matrix.A34=(1-scale)*box.ZMin
    target.Shape=target.Shape.transformGeometry(matrix)
    target.addProperty('App::PropertyLength','CandidateDepth','OSR controlled change');target.CandidateDepth=config['candidate_depth_mm']
    document.recompute();candidate=output/'candidate.FCStd';document.saveAs(str(candidate));App.closeDocument(document.Name)
    _canonicalise_fcstd(candidate)
    document=App.openDocument(str(candidate));changed=quantities(document,config);App.closeDocument(document.Name)
    assert math.isclose(changed['depth_mm'],config['candidate_depth_mm'],rel_tol=1e-9)
    assert all(changed['solids'][name]==row for name,row in baseline['solids'].items() if name!=config['object'])
    assert sha(source)==source_hash,'Canonical CAD must remain unchanged'
    for name,q in [('baseline',baseline),('candidate',changed)]:
        write(output/(name+'-quantities.json'),q)
        solve(q,config,output/(name+'-analysis'))
    versions=dict(freecad='.'.join(App.Version()[:3]),calculix=subprocess.run(['ccx','-v'],capture_output=True,text=True).stdout.strip())
    write(output/'cad-results.json',dict(passed=True,source_sha256=source_hash,candidate_sha256=sha(candidate),tools=versions,
        baseline=baseline,candidate=changed,physical_release=False))
