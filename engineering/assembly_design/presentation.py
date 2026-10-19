"""Read-only native-solid pictures; no invented geometry or acceptance claims."""
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile

from engineering.twin_workflow import core


def preview(cad,output,kind):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgb
    before=core.sha(cad)
    with tempfile.TemporaryDirectory(prefix='.mesh-',dir=Path(output).parent) as temporary:
        temporary=Path(temporary);script=temporary/'export.py';mesh=temporary/'mesh.json'
        source=core.ROOT/'engineering/design_delivery/visuals.py'
        script.write_text('import runpy\nrunpy.run_path('+repr(str(source))+')["export_mesh"]('+repr(str(cad))+','+repr(str(mesh))+')\n')
        binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
        command=[binary] if binary else ['flatpak','run','--filesystem='+str(Path(cad).parent),'--filesystem='+str(temporary),'--filesystem='+str(core.ROOT),'--command=FreeCADCmd','org.freecad.FreeCAD']
        subprocess.run([*command,str(script)],check=True,capture_output=True,timeout=120)
        model=core.read(mesh,maximum=60_000_000)
    az,el=np.deg2rad([25,28]);right=np.array([np.cos(az),np.sin(az),0]);forward=np.array([-np.sin(az),np.cos(az),0]);up=-np.sin(el)*forward+np.array([0,0,np.cos(el)]);camera=np.cos(el)*forward+np.array([0,0,np.sin(el)])
    polygons=[];depth=[];colors=[]
    for part in model['parts']:
        points=np.array(part['vertices']);faces=points[np.array(part['faces'])]
        normals=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
        shade=.6+.4*np.abs(normals@np.array([-.3,-.4,.866]))
        color='#d69b55' if 'connector' in part['id'] or 'procurement' in part['id'] else '#a36b48' if 'conductor' in part['id'] else '#86a6b8'
        polygons.extend(np.stack([faces@right,faces@up],axis=2));depth.extend(faces@camera);colors.extend(shade[:,None]*np.array(to_rgb(color)))
    rasterize=runpy.run_path(str(core.ROOT/'tools/automation/design-progress.py'))['rasterize']
    fig=plt.figure(figsize=(10,6),dpi=110,facecolor='#f5f7fa');ax=fig.add_axes([.03,.18,.94,.66]);ax.axis('off');ax.imshow(rasterize(polygons,depth,colors,width=1000,height=440))
    fig.text(.04,.93,kind+' — retained native model',fontsize=17,color='#18384c')
    fig.text(.04,.87,str(len(model['parts']))+' represented part identities; orange = purchased coordination envelope',fontsize=10)
    fig.text(.04,.10,'Provisional assembly design. Native correspondence/static overlap only.',fontsize=10)
    fig.text(.04,.05,'Connections, moving paths, supplier configurations and physical qualification remain open.',fontsize=10)
    fig.savefig(output);plt.close(fig)
    if core.sha(cad)!=before:raise ValueError('CAD changed while making preview')
