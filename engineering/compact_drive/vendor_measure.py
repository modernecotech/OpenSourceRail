"""One private officialSTEP measurement; no proprietary geometry publication."""
from pathlib import Path
import argparse,json
from engineering.design_search.craft_backends import freecad_reference as ref
from engineering.station_rail.common import digest,identity
from . import FLAGS
from .common import vendor,sources,write


def run(step,output):
    out=Path(output);facts=vendor();before=sources()
    if digest(Path(step))!=facts['STEP']['sha256']:raise ValueError('Exact officialSTEP byte identity required')
    # Extend the worker in memory only; the retained referenceproducer source is
    # untouched. Actualcircle/cylinder datums can be compared to6M10PCD94mm.
    extra="""    circles=[]
    for obj in doc.Objects:
        if not hasattr(obj,'Shape'):continue
        for edge in obj.Shape.Edges:
            c=edge.Curve
            if isinstance(c,Part.Circle):
                circles.append(dict(radius_m=c.Radius*.001,centre_m=[c.Center.x*.001,c.Center.y*.001,c.Center.z*.001],axis=[c.Axis.x,c.Axis.y,c.Axis.z]))
    result['circular_edge_datums']=circles
"""
    original=ref.WORKER
    ref.WORKER=original.replace("    bodies.sort(key=lambda row: row['id'])",extra+"    bodies.sort(key=lambda row: row['id'])")
    try:result=ref.run(step,out,timeout_s=120,memory_mb=3072)
    finally:ref.WORKER=original
    report=dict(schema='osr-compact-drive-vendor-measurement/1',source_before=before,source_after=sources(),source_unchanged=before==sources(),native_execution=result['execution'],source_STEP_sha256=result['source_step_sha256'],native_result_sha256=digest(out/'result.json'),official_dimension_image_sha256=facts['dimension_image']['sha256'],native_units='mm converted explicitly to SI by worker',CAD_model_is_simplified=True,model_B_datasheet_C_compatibility='HOLD: mechanicaldrawing andcommercialconfiguration revision match requires manufacturer confirmation; externalgeometry measurements do not prove electrical/thermal capability',mount_bore_and_pilot_comparison='Actualcircular-edge datums retained; classify6xM10-PCD94mm,75mm pilot and24mm shaft against dimensions before interface admission; no fabricated datums',redistribution_licence_verified=False,publish_vendor_STEP=False,**FLAGS)
    report['evaluation_id']=identity(report);write(out/'compatibility.json',report);return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--step',required=True);p.add_argument('--output',required=True);a=p.parse_args();print(json.dumps(run(a.step,a.output)))
