import json, math, resource, time, traceback
from pathlib import Path
import FreeCAD as App
import Part, Import

root = Path(__file__).resolve().parent
request = json.loads((root/'input.json').read_text())
started = time.monotonic()
doc = None
result = dict(schema='osr-freecad-step-reference/1', execution='failed',
              FreeCAD_version=list(App.Version()),
              OpenCASCADE_version=str(getattr(Part, 'OCC_VERSION', 'unknown')),
              native_units=dict(length='mm', area='mm2', volume='mm3'),
              units=dict(length='m', area='m2', volume='m3'),
              measurement_method='Exact imported OpenCASCADE B-rep; no tessellation',
              display_offsets_applied=False, installed_mass_complete=False,
              physical_accepted=False, engineering_accepted=False,
              manufacturing_release=False, operating_release=False,
              selected_reference_changed=False, movement_authority=False)
try:
    doc = App.newDocument('IndependentSTEPReference')
    Import.insert(str(root/'input.step'), doc.Name)
    doc.recompute()
    bodies = []
    imported = []
    for obj in doc.Objects:
        imported.append(dict(name=obj.Name, label=obj.Label, type_id=obj.TypeId))
        if not obj.isDerivedFrom('Part::Feature') or not hasattr(obj, 'Shape'):
            continue
        shape = obj.Shape
        if shape.isNull():
            continue
        solids = shape.Solids
        conservative_box = shape.BoundBox
        box = shape.optimalBoundingBox(False, False)
        center = shape.CenterOfMass
        bodies.append(dict(id=obj.Label, native_name=obj.Name, type_id=obj.TypeId,
            shape_type=shape.ShapeType, solid_count=len(solids),
            valid=bool(shape.isValid()), closed=bool(shape.isClosed()),
            all_solids_closed_valid=bool(solids) and all(s.isClosed() and s.isValid() and s.Volume > 0 for s in solids),
            volume_m3=shape.Volume*1e-9, area_m2=shape.Area*1e-6,
            center_of_mass_m=[center.x*.001, center.y*.001, center.z*.001],
            bbox_m=dict(min=[box.XMin*.001, box.YMin*.001, box.ZMin*.001],
                        max=[box.XMax*.001, box.YMax*.001, box.ZMax*.001]),
            bbox_method='OpenCASCADE optimalBoundingBox(False, False); no triangulation',
            conservative_bbox_m=dict(
                min=[conservative_box.XMin*.001, conservative_box.YMin*.001, conservative_box.ZMin*.001],
                max=[conservative_box.XMax*.001, conservative_box.YMax*.001, conservative_box.ZMax*.001]),
            mass_kg=None))
    bodies.sort(key=lambda row: row['id'])
    result.update(execution='completed', bodies=bodies, imported_objects=imported,
                  body_count=len(bodies), total_volume_m3=sum(b['volume_m3'] for b in bodies))
except BaseException as error:
    result.update(error=dict(type=type(error).__name__, message=str(error)),
                  traceback=traceback.format_exc())
finally:
    result['native_wall_seconds'] = time.monotonic()-started
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result['native_process_usage'] = dict(peak_rss_kib=usage.ru_maxrss,
        user_cpu_seconds=usage.ru_utime, system_cpu_seconds=usage.ru_stime,
        actual_address_space_limit_bytes=list(resource.getrlimit(resource.RLIMIT_AS)))
    if doc is not None:
        App.closeDocument(doc.Name)
    (root/'measurement.json').write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n')
