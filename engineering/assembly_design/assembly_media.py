"""Revision-bound construction-stage media from exact retained native triangles.

Parts appear at their final coordinates in a dependency-ordered sequence. No
insertion trajectory, collision, crane movement or structural verification is
inferred from this visibility animation.
"""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile

import numpy as np
from engineering.twin_workflow import core

SCOPE = ('Native CAD construction-stage visibility sequence at final coordinates; '
         'not a motion, collision, crane or construction-load simulation')


def stages(candidate):
    parts = {p['id'] for p in candidate['contract']['parts']}
    rows = candidate['metadata']['assembly_sequence']
    seen, prior = set(), set()
    if not rows:
        raise ValueError('explicit assembly stages required')
    for row in rows:
        if not row['id'] or row['id'] in prior or not row['title']:
            raise ValueError('unique named assembly stage required')
        ids = row['part_ids']
        if not ids or len(set(ids)) != len(ids) or not set(ids) <= parts or seen.intersection(ids):
            raise ValueError('assembly stages must partition exact physical parts')
        if not set(row['requires']) <= prior:
            raise ValueError('assembly stage depends on a missing or later stage')
        seen.update(ids)
        prior.add(row['id'])
    if seen != parts:
        raise ValueError('assembly sequence omits physical parts')
    return rows


def decode(path):
    binary = shutil.which('ffprobe')
    if not binary:
        raise ValueError('ffprobe required to verify assembly video')
    result = subprocess.run([binary, '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=codec_name,nb_frames,width,height', '-of', 'json', str(path)],
        check=True, capture_output=True, text=True, timeout=30)
    streams = json.loads(result.stdout)['streams']
    if len(streams) != 1:
        raise ValueError('assembly video must have exactly one video stream')
    return streams[0]


def build(candidate, mesh_path, output):
    rows = stages(candidate)
    mesh_path, output = Path(mesh_path), Path(output)
    mesh = core.read(mesh_path, maximum=60_000_000)
    parts = {p['id'] for p in candidate['contract']['parts']}
    if len(mesh['parts']) != len(parts) or {p['id'] for p in mesh['parts']} != parts:
        raise ValueError('assembly video mesh identities differ')
    binary, probe = shutil.which('ffmpeg'), shutil.which('ffprobe')
    if not binary or not probe:
        return dict(state='hold', reason='ffmpeg/ffprobe unavailable', scope=SCOPE, **core.FLAGS)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    az, el = np.deg2rad([28., 24.])
    right = np.array([np.cos(az), np.sin(az), 0.])
    forward = np.array([-np.sin(az), np.cos(az), 0.])
    up = -np.sin(el)*forward + np.array([0., 0., np.cos(el)])
    camera = np.cos(el)*forward + np.array([0., 0., np.sin(el)])
    triangles, stage_index, depth, colors = [], [], [], []
    membership = {identity: i for i, row in enumerate(rows) for identity in row['part_ids']}
    palette = np.asarray([[.36, .60, .72], [.72, .61, .43], [.48, .63, .51], [.66, .69, .73]])
    for part in mesh['parts']:
        vertices = np.asarray(part['vertices'], dtype=float)
        faces = np.asarray(part['faces'], dtype=int)
        if vertices.ndim != 2 or vertices.shape[1] != 3 or not np.isfinite(vertices).all():
            raise ValueError('invalid native vertices for assembly video')
        if faces.ndim != 2 or faces.shape[1] != 3 or np.any(faces < 0) or np.any(faces >= len(vertices)):
            raise ValueError('invalid native triangles for assembly video')
        points = vertices[faces]
        normal = np.cross(points[:, 1]-points[:, 0], points[:, 2]-points[:, 0])
        normal /= np.maximum(np.linalg.norm(normal, axis=1)[:, None], 1e-12)
        shade = .55 + .45*np.abs(normal @ np.array([-.3, -.4, .866]))
        index = membership[part['id']]
        triangles.extend(np.stack([points @ right, points @ up], axis=2))
        depth.extend(np.mean(points @ camera, axis=1))
        stage_index.extend([index]*len(faces))
        colors.extend(shade[:, None]*palette[index % len(palette)])
    triangles, depth, colors = np.asarray(triangles), np.asarray(depth), np.asarray(colors)
    stage_index = np.asarray(stage_index)
    if not len(triangles) or len(triangles) > 750000:
        raise ValueError('assembly media triangle budget exceeded')
    lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
    margin = np.maximum((hi-lo)*.05, .01)
    lo, hi = lo-margin, hi+margin
    # One geometrically distinct frame per stage, repeated by the encoder.
    # Frame count remains deterministic, without rerendering identical meshes.
    with tempfile.TemporaryDirectory(prefix='.assembly-', dir=output) as temporary:
        temporary = Path(temporary)
        for index, row in enumerate(rows):
            order = np.argsort(depth[stage_index <= index])
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100, facecolor='#f5f7fa')
            fig.subplots_adjust(left=.03, right=.97, bottom=.17, top=.81)
            ax.add_collection(PolyCollection(triangles[stage_index <= index][order],
                facecolors=colors[stage_index <= index][order], edgecolors='none', rasterized=True))
            ax.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), aspect='equal')
            ax.axis('off')
            fig.text(.04, .94, candidate['kind']+' — native construction stages', fontsize=15)
            fig.text(.04, .88, f'{index+1}/{len(rows)}  '+row['title'], fontsize=11)
            fig.text(.04, .10, 'Provisional design • Parts shown at final coordinates in declared dependency order.', fontsize=10)
            fig.text(.04, .05, 'No motion, collision, crane or construction-load verification is claimed.', fontsize=10)
            path = temporary/f'{index:03d}.png'
            fig.savefig(path)
            plt.close(fig)
            if index == len(rows)-1:
                shutil.copyfile(path, output/'assembly-stages.png')
            if index == max(0, len(rows)//2-1):
                shutil.copyfile(path, output/'assembly-intermediate.png')
        subprocess.run([binary, '-loglevel', 'error', '-y', '-framerate', '1',
            '-i', str(temporary/'%03d.png'), '-vf', 'fps=6', '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output/'assembly-sequence.mp4')],
            check=True, capture_output=True, timeout=120)
    decoded = decode(output/'assembly-sequence.mp4')
    if decoded['codec_name'] != 'h264' or int(decoded['nb_frames']) != 6*len(rows):
        raise ValueError('assembly stage video did not decode to expected frames')
    return dict(state='executed', candidate_revision=candidate['revision'],
        native_mesh_sha256=core.sha(mesh_path), stages=rows, frames=6*len(rows),
        frames_per_second=6, decoded_video=decoded,
        files_sha256={name: core.sha(output/name) for name in (
            'assembly-sequence.mp4', 'assembly-stages.png', 'assembly-intermediate.png')},
        ffmpeg_sha256=core.sha(Path(binary).resolve()), ffprobe_sha256=core.sha(Path(probe).resolve()),
        scope=SCOPE, **core.FLAGS)


def verify(candidate, mesh_path, output, result):
    if any(result.get(k) is not False for k in core.FLAGS) or result.get('scope') != SCOPE:
        raise ValueError('assembly media cannot assert engineering release')
    rows = stages(candidate)
    if result['state'] == 'hold':
        if not result.get('reason'):
            raise ValueError('held media requires reason')
        return result
    if result['state'] != 'executed' or result['candidate_revision'] != candidate['revision']:
        raise ValueError('assembly media candidate differs')
    if result['native_mesh_sha256'] != core.sha(mesh_path) or result['stages'] != rows:
        raise ValueError('assembly media geometry or stages differ')
    if result['frames'] != 6*len(rows) or result['frames_per_second'] != 6:
        raise ValueError('assembly media timing differs')
    expected = {'assembly-sequence.mp4', 'assembly-stages.png', 'assembly-intermediate.png'}
    if set(result['files_sha256']) != expected or any(core.sha(Path(output)/n) != h for n, h in result['files_sha256'].items()):
        raise ValueError('assembly media bytes differ')
    decoded = decode(Path(output)/'assembly-sequence.mp4')
    if decoded != result['decoded_video'] or decoded['codec_name'] != 'h264' or int(decoded['nb_frames']) != result['frames']:
        raise ValueError('assembly media decoded stream differs')
    return result
