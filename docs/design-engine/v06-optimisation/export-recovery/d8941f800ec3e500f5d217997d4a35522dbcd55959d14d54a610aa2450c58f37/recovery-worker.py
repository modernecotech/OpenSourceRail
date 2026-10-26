
from pathlib import Path
import json,time
import ifcopenshell,ifcopenshell.geom
from ifcopenshell.util.element import get_pset
from ifcopenshell.util.shape import get_volume
from engineering.station_rail.twin_recovery import check_occurrences,FLAGS
from engineering.station_rail.common import encoded,identity
out=Path(__file__).parent;started=time.monotonic()
data=json.loads((out/'native-input.json').read_bytes());native=json.loads((out/'native-result.json').read_bytes())
f=ifcopenshell.open(str(out/'wheel-stock.ifc'));rows=[]
for obj in f.by_type('IfcBuildingElementProxy'):
    ps=get_pset(obj,'OSR_Research_Identity');shape=ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(),obj)
    rows.append(dict(id=obj.Name,candidate_id=ps.get('candidate_id'),occurrence_id=ps.get('occurrence_id'),frame=ps.get('frame'),
        physical_accepted=ps.get('physical_accepted'),complete_installed_twin=ps.get('complete_installed_twin'),volume_m3=abs(get_volume(shape.geometry))))
value=check_occurrences(data['candidate_id'],data['parts'],native,rows)
value.update(schema='osr-wheel-twin-recovery-IFC-audit/1',candidate_id=data['candidate_id'],execution='completed',
    method='Every occurrence reopened through IfcOpenShell geometry kernel; identity and native BRep-volume comparison',
    ifcopenshell_version=ifcopenshell.version,elapsed_s=time.monotonic()-started,native_reopened=True,**FLAGS)
value['audit_id']=identity(value);(out/'recovery-ifc-audit.json').write_bytes(encoded(value))
