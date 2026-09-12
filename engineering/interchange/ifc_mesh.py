#!/usr/bin/env python3
"""Tessellate indexed IFC solids into bounded, hash-bound browser chunks.

IfcOpenShell geometry API: https://docs.ifcopenshell.org/ifcopenshell-python/geometry_processing.html
Coordinates are metres in the IFC engineering frame, including object placement.
Map conversion is retained in the source IFC; it is not applied a second time.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import ifcopenshell
import ifcopenshell.geom

SCHEMA = 'org.opensourcerail.ifc-mesh.v1'
MAX_CHUNK_BYTES = 3_500_000

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def tessellate(ifc_path: Path, index_path: Path, output: Path) -> dict:
    index = json.loads(index_path.read_text())
    source_hash = digest(ifc_path)
    if index.get('ifc_sha256') != source_hash:
        raise ValueError('IFC mesh input does not match the object index hash')
    model = ifcopenshell.open(str(ifc_path))
    settings = ifcopenshell.geom.settings()
    settings.set('use-world-coords', True)
    meshes, missing = [], []
    for item in sorted(index['objects'], key=lambda row: row['asset_id']):
        element = model.by_guid(item['ifc_guid'])
        if not element:
            raise ValueError(f"Missing IFC object {item['ifc_guid']}")
        # Virtual interfaces have no physical representation. Keep them visible
        # as explicitly identified envelopes in the index viewer.
        if not getattr(element, 'Representation', None):
            missing.append({'asset_id': item['asset_id'], 'reason': 'no-physical-representation'})
            continue
        try:
            shape = ifcopenshell.geom.create_shape(settings, element)
            vertices = [round(float(v), 6) for v in shape.geometry.verts]
            faces = [int(v) for v in shape.geometry.faces]
        except RuntimeError as error:
            raise ValueError(f"IFC tessellation failed for {item['asset_id']}: {error}") from error
        if not vertices or not faces or len(vertices) % 3 or len(faces) % 3:
            raise ValueError(f"IFC object {item['asset_id']} has no valid triangles")
        if any(not math.isfinite(v) for v in vertices) or any(v < 0 or v >= len(vertices)//3 for v in faces):
            raise ValueError('Invalid mesh coordinates or triangle indices')
        meshes.append({'asset_id': item['asset_id'], 'ifc_guid': item['ifc_guid'], 'vertices': vertices, 'triangles': faces})
    output.mkdir(parents=True, exist_ok=True)
    chunks, group = [], []
    def write_chunk(objects):
        content = {'schema': SCHEMA, 'ifc_sha256': source_hash, 'objects': objects}
        data = encode(content)
        if len(data) > MAX_CHUNK_BYTES:
            raise ValueError('One IFC object exceeds the bounded browser mesh size')
        name = f'civil-mesh-{len(chunks):04d}.json'
        (output/name).write_bytes(data+b'\n')
        chunks.append({'file': name, 'sha256': digest(output/name), 'object_count': len(objects)})
    for mesh in meshes:
        if group and len(encode({'schema':SCHEMA,'ifc_sha256':source_hash,'objects':group+[mesh]})) > MAX_CHUNK_BYTES:
            write_chunk(group);group=[]
        group.append(mesh)
    if group: write_chunk(group)
    report = {'schema':SCHEMA, 'ifc_sha256':source_hash, 'index_sha256':digest(index_path),
              'generator_sha256':digest(__file__), 'engine':f'IfcOpenShell {ifcopenshell.version}',
              'coordinate_frame':'IFC engineering coordinates, metres; object placements applied',
              'object_count':len(meshes), 'triangle_count':sum(len(m['triangles'])//3 for m in meshes),
              'chunks':chunks, 'non_geometric_objects':missing, 'deployment_release_ready':False}
    (output/'civil-mesh-manifest.json').write_bytes(encode(report)+b'\n')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ifc',type=Path,required=True);p.add_argument('--index',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args();r=tessellate(a.ifc,a.index,a.out_dir)
    print(f"{r['object_count']} objects, {r['triangle_count']} triangles, {len(r['chunks'])} chunks")

if __name__=='__main__':main()
