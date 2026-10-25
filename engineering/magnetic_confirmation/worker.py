"""One isolated case: parent enforces 300 s on this complete process group."""
import argparse
import json
from pathlib import Path
import subprocess
from . import analysis
from .formulation import formulation
from .runner import PLAN,encoded,file_hash,identity,legacy,source_snapshot,write


def execute(request_path,name,output):
    request=json.loads(Path(request_path).read_bytes());output=Path(output);root=Path(request['root'])
    if request['request_id']!=identity({k:v for k,v in request.items() if k!='request_id'}) or name not in request['cases'] or request['source_sha256']!=source_snapshot(root) or request['source']!=legacy.source_input(root):raise ValueError('worker request/source identity differs')
    if request['getdp']['sha256']!=file_hash(request['getdp']['path']):raise ValueError('worker GetDP binary differs')
    source=request['source'];value=analysis.validate_source(source);settings=PLAN[name];write(output/'source-input.json',source)
    row=dict(case=name,request_id=request['request_id'],candidate_id=source['vehicle_candidate_id'],magnet_component_id=value['physical_id'],settings=settings,execution_status='failed',force_credit=False,full_source_converged=False)
    try:
        reused=Path(request['reuse_mesh_root'])/name if request['reuse_mesh_root'] else None
        if reused is not None:
            receipt_path=reused.parent/(name+'-receipt.json')
            if reused.is_dir() and (reused/'coupon.msh').is_file():
                previous=json.loads(receipt_path.read_bytes())
                if json.loads((reused/'source-input.json').read_bytes())!=source or any(previous[k]!=expected for k,expected in dict(name=name,**settings).items()):raise ValueError('reused mesh physical source/settings differ')
                for filename in ('coupon.msh','coupon.brep','gmsh.log'):
                    raw=(reused/filename).read_bytes()
                    if file_hash(reused/filename)!=previous['files_sha256'][filename]:raise ValueError('reused mesh integrity differs')
                    (output/filename).write_bytes(raw)
                mesh=previous['mesh'];row['mesh_reuse']=dict(receipt_sha256=file_hash(receipt_path),mesh_sha256=file_hash(reused/'coupon.msh'),original_execution_status=previous.get('execution_status'),scope='Mesh bytes only; no old solve/convergence/force credit')
            else:reused=None
        if reused is None:mesh=legacy.mesh_case(value,output,margin=settings['margin_m'],h=settings['near_mesh_size_m'],gap_h=settings['gap_mesh_size_m'])
        row['mesh']=mesh;row['mesh_verification']=analysis.validate_mesh(output/'coupon.msh',mesh,value,settings['margin_m']);(output/'coupon.pro').write_text(formulation(value,mesh,request['contours_m']))
        command=[request['getdp']['path'],'coupon.pro','-msh','coupon.msh','-solve','Solve','-pos','Results'];row['solver_command']=command
        with (output/'getdp.stdout.log').open('wb') as stdout,(output/'getdp.stderr.log').open('wb') as stderr:
            process=subprocess.run(command,cwd=output,stdout=stdout,stderr=stderr)
        row['solver_returncode']=process.returncode;row['continuation']=analysis.parse_stages((output/'getdp.stdout.log').read_text(errors='replace'));row['full_source_converged']=row['continuation']['full_source_converged']
        if process.returncode:row['execution_status']='failed';row['error']='GetDP returned nonzero'
        elif not row['full_source_converged']:row['execution_status']='nonconverged';row['error']='Every source stage through full λ = 1 must converge'
        else:
            row['analysis']=analysis.analyze(output,source,mesh,request['contours_m'],legacy);row['force_credit']=True;row['execution_status']='completed'
    except Exception as error:row.update(execution_status='failed',force_credit=False,full_source_converged=False,error_type=type(error).__name__,error=str(error));row.pop('analysis',None)
    if request['source_sha256']!=source_snapshot(root) or request['getdp']['sha256']!=file_hash(request['getdp']['path']):raise ValueError('worker implementation/source/tool changed')
    write(output/'calculation.json',row);print(json.dumps(dict(case=name,execution_status=row['execution_status'],force_credit=row['force_credit'])),flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--request',type=Path,required=True);p.add_argument('--case',choices=tuple(PLAN),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();execute(a.request,a.case,a.output)


if __name__=='__main__':main()
