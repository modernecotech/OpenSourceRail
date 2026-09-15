"""Load inside FreeCAD, Bonsai/Blender or QGIS; no desktop credentials are needed.

The reviewed link file maps tool-owned object identities to OSR city positions.
Selection only opens the local Workbench; it never changes geometry or releases work.
"""
import json
from pathlib import Path
from urllib.parse import urlencode
import webbrowser


def resolve(link_file, application, object_id):
    package = json.loads(Path(link_file).read_text())
    candidates = [r for r in package['bindings'] if str(object_id) in r.get(application, [])]
    if len(candidates) != 1:
        raise ValueError('Select an object with exactly one binding in this city link package')
    row = candidates[0]
    return 'http://127.0.0.1:8090/docs/lifecycle/?' + urlencode(dict(city=package['city'], environment=package['environment'], asset=row['asset_id']))


def freecad(link_file):
    import FreeCADGui
    selected = FreeCADGui.Selection.getSelection()
    if len(selected) != 1:
        raise ValueError('Select one FreeCAD object')
    webbrowser.open(resolve(link_file, 'freecad', selected[0].Name))


def bonsai(link_file):
    import bpy
    import bonsai.tool as tool
    obj = bpy.context.active_object
    entity = tool.Ifc.get_entity(obj) if obj else None
    if entity is None:
        raise ValueError('Select one IFC object in Bonsai')
    webbrowser.open(resolve(link_file, 'ifc', entity.GlobalId))


def qgis(link_file, iface):
    layer = iface.activeLayer()
    selected = layer.selectedFeatures() if layer else []
    if len(selected) != 1 or 'id' not in layer.fields().names():
        raise ValueError('Select one OSR GIS feature with its source id')
    webbrowser.open(resolve(link_file, 'gis', selected[0]['id']))
