"""Portable, offline inspection of exact provisional assembly exhibits.

``build(output, exhibits)`` writes index.html and explorer-data.json.  Exhibits
are JSON-compatible objects containing ``candidate`` (standard controlled assembly
candidate), ``assessment``, ``result``, ``path`` (directory relative to output),
and optionally ``mesh`` (decoded retained native-mesh.json).  The candidate's
metadata.assembly_sequence may contain {id, title, title_ar?, part_ids, requires}
rows.  Requires lists earlier stage IDs; parts are accumulated, never moved.

Only existing local assets are linked. Native mesh vertices produce 2D convex
outer envelopes for the interactive plan, explicitly distinct from solid renders
and motion/collision verification. No geometry is invented for missing meshes.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path, PurePosixPath
from urllib.parse import quote

SCHEMA = 'osr-offline-design-explorer/1'
MAX_DATA_BYTES = 4 * 1024 * 1024
ASSETS = (
    ('Native CAD', 'native/candidate.FCStd', 'file'),
    ('STEP', 'model.step.gz', 'file'),
    ('IFC', 'bim/assembly.ifc.gz', 'file'),
    ('Parts schedule', 'manufacturing-bom.csv', 'file'),
    ('Alternative recipes and failures', 'alternatives.csv', 'file'),
    ('Checks', 'assessment.json.gz', 'file'),
    ('Whole-frame numerical data', 'carbody-frame.json.gz', 'file'),
    ('Finite joint-stiffness sensitivities', 'joint-response.json.gz', 'file'),
    ('Exact simultaneous splice cuts', 'splice-demands.json.gz', 'file'),
    ('Inspection plan', 'qa-plan.json.gz', 'file'),
    ('Retained result', 'result.json', 'file'),
    ('Assembly definition', 'candidate.json.gz', 'file'),
    ('Native mesh', 'bim/native-mesh.json.gz', 'file'),
    ('Native model', 'overview.png', 'image'),
    ('Whole-frame response', 'frame-response.png', 'image'),
    ('Joint flexibility and frame response', 'joint-response.png', 'image'),
    ('Intermediate assembly stage', 'assembly-intermediate.png', 'image'),
    ('Final assembly stage', 'assembly-stages.png', 'image'),
    ('Inspection drawing', 'inspection.svg', 'image'),
    ('Represented splice section and defects', 'splice-section.svg', 'image'),
    ('Assembly sequence', 'assembly-sequence.mp4', 'video'),
    ('Cassette fixture movement', 'fixture-motion.mp4', 'video'),
)


def _path(value):
    if not isinstance(value, str) or not value or any(ord(c) < 32 for c in value) or any(c in value for c in '\\?#%'):
        raise ValueError('unsafe exhibit path')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != value:
        raise ValueError('unsafe exhibit path')
    return path


def _asset(root, relative, label, kind):
    path = root.joinpath(*_path(relative).parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('exhibit asset escapes output directory')
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError('exhibit asset is not a regular file')
    # Bind the gallery and downloads to the exact bytes that were inspected.
    digest = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return dict(label=label, path=relative, url=quote(relative, safe='/'), kind=kind,
                bytes=path.stat().st_size, sha256=digest.hexdigest())


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError('non-finite or invalid geometry/property number')
    return value


def _hull(points):
    """Monotone-chain convex hull, keeping native coordinate units in metres."""
    ordered = sorted(set(points))
    if len(ordered) <= 2:
        return ordered
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower = []
    for point in ordered:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(ordered):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1]+upper[:-1]


def _projection(mesh, part_ids):
    if mesh is None:
        return None
    rows = mesh.get('parts')
    if not isinstance(rows, list):
        raise ValueError('native mesh parts missing')
    identities = [row['id'] for row in rows]
    if len(set(identities)) != len(identities) or set(identities) != set(part_ids):
        raise ValueError('native mesh part identities differ from controlled assembly')
    azimuth, elevation = math.radians(25), math.radians(28)
    ca, sa, ce, se = math.cos(azimuth), math.sin(azimuth), math.cos(elevation), math.sin(elevation)
    projected = []
    bounds = [float('inf'), float('inf'), float('-inf'), float('-inf')]
    for row in rows:
        vertices = row.get('vertices')
        if not isinstance(vertices, list) or not vertices:
            raise ValueError('native mesh has no vertices')
        points = []
        for vertex in vertices:
            if not isinstance(vertex, (list, tuple)) or len(vertex) != 3:
                raise ValueError('native vertex must contain three coordinates')
            x, y, z = (_number(v) for v in vertex)
            u, v = x*ca+y*sa, -x*(-sa)*se-y*ca*se+z*ce
            if not math.isfinite(u) or not math.isfinite(v):
                raise ValueError('native projection overflow')
            # Rounding is for a picture only: original coordinates stay in CAD.
            point = (round(u, 7), round(v, 7))
            points.append(point)
            bounds = [min(bounds[0], point[0]), min(bounds[1], point[1]),
                      max(bounds[2], point[0]), max(bounds[3], point[1])]
        projected.append(dict(id=row['id'], envelope=_hull(points)))
    if not projected:
        return None
    return dict(scope='Projected native outer envelopes; openings and depth occlusion are not represented. Assembly visibility only; no motion, collision or physics simulation.',
                bounds_m=bounds, parts=projected)


def _stages(candidate, part_ids):
    raw = candidate.get('metadata', {}).get('assembly_sequence', [])
    if not raw:
        return [dict(id='all-parts', title='All represented parts', part_ids=list(part_ids), requires=[])], []
    stages, seen, covered = [], set(), set()
    for row in raw:
        identity, title = row.get('id'), row.get('title')
        if not isinstance(identity, str) or not identity or identity in seen or not isinstance(title, str) or not title:
            raise ValueError('assembly stage identity/title missing or duplicated')
        ids, requires = row.get('part_ids', []), row.get('requires', [])
        if (not isinstance(ids, list) or len(set(ids)) != len(ids) or not set(ids) <= set(part_ids)
                or not isinstance(requires, list) or not set(requires) <= seen):
            raise ValueError('assembly stage has unknown parts or nonpreceding dependencies')
        stage = dict(id=identity, title=title, part_ids=ids, requires=requires)
        if 'title_ar' in row:
            if not isinstance(row['title_ar'], str):
                raise ValueError('Arabic stage title must be text')
            stage['title_ar'] = row['title_ar']
        stages.append(stage)
        covered.update(ids)
        seen.add(identity)
    return stages, sorted(set(part_ids)-covered)


def _prepare(root, exhibit):
    candidate = exhibit['candidate']
    contract = candidate['contract']
    identity = candidate.get('kind', contract.get('name', 'Assembly'))
    revision = candidate.get('revision')
    if not isinstance(identity, str) or not identity or not isinstance(revision, str) or not revision:
        raise ValueError('controlled assembly identity/revision missing')
    rows = contract.get('parts')
    if not isinstance(rows, list) or not rows:
        raise ValueError('controlled assembly must contain parts')
    ids = [part['id'] for part in rows]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('controlled assembly part identities missing or duplicated')
    parts, total_mass, unknown_mass = [], 0., False
    for part in rows:
        mass = part.get('properties', {}).get('mass_kg')
        if mass is not None:
            mass = _number(mass)
            if mass < 0:
                raise ValueError('part mass must be nonnegative')
            total_mass += mass
        else:
            unknown_mass = True
        parts.append(dict(id=part['id'], revision=part.get('revision'), material=part.get('material'),
                          process=part.get('process_route'), mass_kg=mass,
                          role=part.get('geometric_role'), joints=part.get('joints', [])))
    folder = _path(exhibit['path']).as_posix()
    assets, missing = [], []
    for label, name, kind in ASSETS:
        found = _asset(root, folder+'/'+name, label, kind)
        if found:
            assets.append(found)
        else:
            missing.append(label)
    assessment, result = exhibit.get('assessment', {}), exhibit.get('result', {})
    if result.get('candidate_revision', revision) != revision:
        raise ValueError('exhibit result belongs to another candidate revision')
    if assessment.get('candidate_revision', revision) != revision:
        raise ValueError('exhibit checks belong to another candidate revision')
    stages, unassigned = _stages(candidate, ids)
    return dict(id=identity, revision=revision, title=exhibit.get('title', contract.get('name', identity)),
                scope=candidate.get('source_scope', 'Provisional represented assembly'),
                parts=parts, represented_mass_kg=None if unknown_mass else total_mass,
                native_state=result.get('native_state', 'not supplied'),
                failed_checks=assessment.get('failed_checks', []), held_checks=assessment.get('held_checks', []),
                open_requirements=[*candidate.get('open_requirements', []),
                    *['Unresolved packaging finding: '+json.dumps(issue, ensure_ascii=False, sort_keys=True)
                      for issue in assessment.get('measurements', {}).get('equipment_packaging', {}).get('issues', [])]],
                stages=stages, unassigned_part_ids=unassigned, assets=assets, unavailable_assets=missing,
                projection=_projection(exhibit.get('mesh'), ids),
                design_complete=False, manufacturing_release=False, physical_release=False)


def _script_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def build(output, exhibits, *, asset_root=None):
    """Write deterministic read-only UI; missing optional media remain visible gaps.

    asset_root optionally points to a separate retained package while the viewer
    is reconstructed for byte comparison. Its absolute path is never emitted.
    Existing assets are never modified. Unsafe paths/symlinks, stale result
    revisions, unknown stage parts and mesh identities fail before either output
    is written. File URLs work without a server or external dependencies.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    asset_root = output if asset_root is None else Path(asset_root)
    prepared = [_prepare(asset_root, exhibit) for exhibit in exhibits]
    if not prepared or len({row['id'] for row in prepared}) != len(prepared):
        raise ValueError('explorer needs at least one uniquely identified exhibit')
    data = dict(schema=SCHEMA, scope='Provisional design inspection; no engineering or manufacturing release.', exhibits=prepared)
    encoded = (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
    if len(encoded) > MAX_DATA_BYTES:
        raise ValueError('explorer data exceeds portable size budget')
    html = HTML.replace('__EXPLORER_DATA__', _script_json(data))
    (output/'explorer-data.json').write_bytes(encoded)
    (output/'index.html').write_text(html)
    return dict(schema=SCHEMA, exhibits=len(prepared), parts=sum(len(e['parts']) for e in prepared),
                data_sha256=sha256(encoded).hexdigest(), index_sha256=sha256(html.encode()).hexdigest(),
                path='index.html', design_complete=False, manufacturing_release=False, physical_release=False)


HTML = r'''<!doctype html>
<html lang="en" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; media-src 'self'; base-uri 'none'; object-src 'none'">
<title>OpenSourceRail · Design explorer</title><style>
:root{font-family:system-ui,sans-serif;color:#18344a;background:#f0f4f7;font-size:15px}*{box-sizing:border-box}body{margin:0}header{background:#123044;color:white;padding:24px max(24px,calc((100% - 1320px)/2))}header p{color:#c6d7e0;margin:8px 0}.brand{font-size:12px;font-weight:700;letter-spacing:.1em;color:#91d1ec}h1{font-size:28px;margin:8px 0}h2{font-size:19px;margin:0 0 14px}h3{font-size:16px}main{max-width:1368px;margin:auto;padding:24px}button,input,select{font:inherit}button,select{background:white;color:#18344a;border:1px solid #bac9d2;border-radius:6px;padding:8px 12px;cursor:pointer}button:focus,input:focus,select:focus{outline:3px solid #6eb1da}#language{float:inline-end}select{max-width:100%}.warning{padding:12px 16px;background:#fff2d5;border-inline-start:4px solid #ce910e;margin:16px 0;color:#684b08}.toolbar{display:flex;align-items:center;gap:16px;flex-wrap:wrap}.card{background:white;border:1px solid #dce4ea;border-radius:10px;padding:20px;margin-bottom:20px}.split{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(320px,1fr);gap:20px}.metrics{display:flex;gap:24px;flex-wrap:wrap;margin:16px 0}.metric strong{display:block;font-size:24px;color:#17627d}.metric span{font-size:12px;color:#547083}.muted{color:#5c7180;font-size:13px}.revision{font-family:monospace;overflow-wrap:anywhere;font-size:11px}canvas{display:block;width:100%;height:380px;background:#f5f8fa;border:1px solid #e1e8ed;border-radius:6px}input[type=range]{width:100%;margin:16px 0}input[type=search]{width:100%;padding:10px;border:1px solid #b6c7d1;border-radius:6px}.scroll{max-height:390px;overflow:auto}table{width:100%;border-collapse:collapse;font-size:12px;margin-top:12px}th,td{padding:9px 7px;border-bottom:1px solid #e1e8ed;text-align:start;overflow-wrap:anywhere}th{position:sticky;top:0;background:white}tr[data-id]{cursor:pointer}tr.selected{background:#dceff9}.checks{max-height:180px;overflow:auto;font-size:13px}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}.gallery figure{margin:0;border:1px solid #e1e8ed;border-radius:8px;overflow:hidden}.gallery img,.gallery video{display:block;width:100%;max-height:400px;object-fit:contain;background:#f5f8fa}.gallery figcaption{padding:10px;color:#456276;font-size:13px}.downloads{display:flex;gap:10px;flex-wrap:wrap}.downloads a{display:inline-block;padding:8px 12px;background:#e9f2f7;color:#165370;border-radius:5px;text-decoration:none}.empty{padding:16px;background:#f5f8fa;color:#667c8a}#part-detail{min-height:46px}.badge{display:inline-block;padding:4px 9px;background:#e6edf2;border-radius:4px;font-size:12px}footer{padding:10px 0;color:#637985;font-size:12px}ul{padding-inline-start:22px}@media(max-width:850px){.split{grid-template-columns:1fr}header{padding:20px}main{padding:16px}h1{font-size:23px}canvas{height:300px}}@media print{button,input,select{display:none}.scroll,.checks{max-height:none}.split{display:block}.card{break-inside:avoid}header{background:white;color:#18344a}header p{color:#456276}}
</style></head><body><header><button id="language" type="button" lang="ar">العربية</button><div class="brand">OPENSOURCERAIL · BAGHDAD</div><h1 data-i18n="title">Design explorer</h1><p data-i18n="subtitle">Inspect the represented parts, assembly stages and retained evidence.</p></header>
<main><div class="warning" data-i18n="warning">Provisional designs. Engineering acceptance, physical testing and manufacturing release remain open.</div>
<div class="toolbar card"><label for="assembly" data-i18n="assembly">Assembly</label><select id="assembly"></select><span id="native-state" class="badge"></span></div>
<div class="card"><h2 id="assembly-title"></h2><p id="scope"></p><div class="metrics"><div class="metric"><strong id="part-count"></strong><span data-i18n="parts">Represented part identities</span></div><div class="metric"><strong id="mass"></strong><span data-i18n="mass">Represented mass · not the complete installed system</span></div><div class="metric"><strong id="holds"></strong><span data-i18n="holds">Open checks</span></div></div><p class="revision" id="revision"></p></div>
<div class="split"><section class="card"><h2 data-i18n="sequence">Assembly stages</h2><canvas id="view" role="img" aria-label="Projected native part envelopes"></canvas><input id="stage" aria-label="Assembly stage" type="range" min="1" value="1"><strong id="stage-title"></strong><p id="stage-count" class="muted"></p><p id="projection-note" class="muted"></p><p class="muted" data-i18n="sequenceNote">Parts appear at their final positions. This is a sequence illustration, not a motion, collision or structural simulation.</p><div id="unassigned" class="warning" hidden></div></section>
<section class="card"><h2 data-i18n="bom">Parts schedule</h2><label class="muted" for="search" data-i18n="search">Find a part, material or process</label><input id="search" type="search" autocomplete="off"><div class="scroll"><table><thead><tr><th data-i18n="part">Part</th><th data-i18n="material">Material / process</th><th>kg</th></tr></thead><tbody id="bom"></tbody></table></div><p id="part-detail" class="muted"></p></section></div>
<section class="card"><h2 data-i18n="gallery">CAD images and assembly videos</h2><div id="gallery" class="gallery"></div></section><section class="card"><h2 data-i18n="evidence">Files and checks</h2><div id="downloads" class="downloads"></div><h3 data-i18n="failed">Failed checks</h3><div id="failed" class="checks"></div><h3 data-i18n="open">Open checks and requirements</h3><div id="open" class="checks"></div><p id="missing" class="muted"></p></section>
<footer data-i18n="footer">Offline viewer. Downloads retain their candidate revision; original evidence and acceptance records determine engineering status.</footer></main>
<script id="explorer-data" type="application/json">__EXPLORER_DATA__</script><script>
'use strict';
const data=JSON.parse(document.getElementById('explorer-data').textContent);
const $=id=>document.getElementById(id);let current=data.exhibits[0],selected=null,arabic=false;
const ar={title:'مستعرض التصاميم',subtitle:'استعرض الأجزاء الممثلة ومراحل التجميع والأدلة المحفوظة.',warning:'تصاميم أولية. لا يزال الاعتماد الهندسي والاختبار الفعلي والإذن بالتصنيع قيد الاستكمال.',assembly:'التجميع',parts:'هويات الأجزاء الممثلة',mass:'الكتلة الممثلة · ليست كتلة النظام المركب بالكامل',holds:'فحوص مفتوحة',sequence:'مراحل التجميع',sequenceNote:'تظهر الأجزاء في مواقعها النهائية. هذا عرض لتسلسل التجميع وليس محاكاة للحركة أو التصادم أو السلوك الإنشائي.',bom:'جدول الأجزاء',search:'ابحث عن جزء أو مادة أو عملية',part:'الجزء',material:'المادة / العملية',gallery:'صور التصميم وفيديوهات التجميع',evidence:'الملفات والفحوص',failed:'الفحوص غير الناجحة',open:'الفحوص والمتطلبات المفتوحة',footer:'مستعرض يعمل دون اتصال. تحتفظ الملفات بإصدار التصميم؛ وتحدد الأدلة الأصلية وسجلات الاعتماد الحالة الهندسية.'};
const english=new Map([...document.querySelectorAll('[data-i18n]')].map(e=>[e,e.textContent]));
const words=(en,arText)=>arabic?arText:en;
function text(el,value){el.textContent=value===null||value===undefined?'—':String(value)}
function list(el,items){el.replaceChildren();if(!items.length){text(el,words('None reported; this does not establish acceptance.','لا توجد عناصر مبلغ عنها؛ وهذا لا يثبت الاعتماد.'));return}const ul=document.createElement('ul');for(const item of items){const li=document.createElement('li');text(li,typeof item==='string'?item:JSON.stringify(item));ul.append(li)}el.append(ul)}
for(const exhibit of data.exhibits){const option=document.createElement('option');option.value=exhibit.id;text(option,exhibit.title);$('assembly').append(option)}
function load(){selected=null;current=data.exhibits.find(e=>e.id===$('assembly').value)||data.exhibits[0];text($('assembly-title'),current.title);text($('scope'),current.scope);text($('part-count'),current.parts.length);text($('mass'),current.represented_mass_kg===null?'—':current.represented_mass_kg.toFixed(2)+' kg');text($('holds'),current.held_checks.length);text($('native-state'),words('Native geometry: ','الهندسة الأصلية: ')+current.native_state);text($('revision'),words('Candidate revision: ','إصدار التصميم: ')+current.revision);$('stage').max=current.stages.length;$('stage').value=current.stages.length;$('search').value='';$('unassigned').hidden=!current.unassigned_part_ids.length;text($('unassigned'),words('Parts without an assigned assembly stage: ','أجزاء لم تحدد لها مرحلة تجميع: ')+current.unassigned_part_ids.join(', '));list($('failed'),current.failed_checks);list($('open'),[...current.held_checks,...current.open_requirements]);text($('missing'),words('Files not supplied: ','ملفات غير متاحة: ')+current.unavailable_assets.join(', '));assets();bom();draw()}
function assets(){$('gallery').replaceChildren();$('downloads').replaceChildren();for(const a of current.assets){if(a.kind==='file'){const link=document.createElement('a');link.href=a.url;link.title=a.sha256;link.setAttribute('download','');text(link,a.label);$('downloads').append(link);continue}const figure=document.createElement('figure');let media;if(a.kind==='video'){media=document.createElement('video');media.controls=true;media.preload='metadata';media.playsInline=true}else{media=document.createElement('img');media.alt=a.label;media.loading='lazy'}media.src=a.url;const caption=document.createElement('figcaption');text(caption,a.label);figure.append(media,caption);$('gallery').append(figure)}if(!$('gallery').children.length){const p=document.createElement('p');p.className='empty';text(p,words('No retained images or videos supplied for this exhibit.','لم تقدم صور أو فيديوهات محفوظة لهذا التصميم.'));$('gallery').append(p)}}
function bom(){const term=$('search').value.toLocaleLowerCase();$('bom').replaceChildren();for(const p of current.parts){if(![p.id,p.material,p.process].join(' ').toLocaleLowerCase().includes(term))continue;const tr=document.createElement('tr');tr.dataset.id=p.id;tr.tabIndex=0;tr.classList.toggle('selected',selected===p.id);const a=document.createElement('td'),b=document.createElement('td'),c=document.createElement('td');text(a,p.id);text(b,[p.material,p.process].filter(Boolean).join(' · '));text(c,p.mass_kg===null?'—':p.mass_kg.toFixed(3));tr.append(a,b,c);const choose=()=>{selected=p.id;text($('part-detail'),[p.id,p.revision,...p.joints].filter(Boolean).join(' · '));bom();draw()};tr.addEventListener('click',choose);tr.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();choose()}});$('bom').append(tr)}}
function draw(){const n=Number($('stage').value),stage=current.stages[n-1],visible=new Set(current.stages.slice(0,n).flatMap(s=>s.part_ids));text($('stage-title'),n+' / '+current.stages.length+' · '+(arabic&&stage.title_ar?stage.title_ar:stage.title));text($('stage-count'),visible.size+' / '+current.parts.length+' '+words('parts in the declared sequence','جزءاً في التسلسل المحدد'));const canvas=$('view'),scale=window.devicePixelRatio||1,w=canvas.clientWidth,h=canvas.clientHeight;canvas.width=Math.round(w*scale);canvas.height=Math.round(h*scale);const ctx=canvas.getContext('2d');ctx.scale(scale,scale);ctx.clearRect(0,0,w,h);if(!current.projection){text($('projection-note'),words('No retained native mesh supplied. See available CAD files and images.','لم تقدم شبكة أصلية محفوظة. راجع ملفات التصميم والصور المتاحة.'));return}text($('projection-note'),words('Native outer envelopes projected in metres. Openings and depth occlusion are not shown.','أغلفة خارجية مسقطة من الهندسة الأصلية بالمتر. لا تظهر الفتحات أو الحجب بالعمق.'));const bounds=current.projection.bounds_m,dx=Math.max(bounds[2]-bounds[0],1e-9),dy=Math.max(bounds[3]-bounds[1],1e-9),s=Math.min((w-40)/dx,(h-40)/dy),ox=(w-dx*s)/2,oy=(h-dy*s)/2;for(const p of current.projection.parts){if(!visible.has(p.id))continue;ctx.beginPath();p.envelope.forEach((v,i)=>{const x=ox+(v[0]-bounds[0])*s,y=h-oy-(v[1]-bounds[1])*s;i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.closePath();ctx.fillStyle=selected===p.id?'rgba(224,154,43,.7)':'rgba(76,132,161,.24)';ctx.strokeStyle=selected===p.id?'#a86400':'#547e97';ctx.lineWidth=selected===p.id?2:0.7;ctx.fill();ctx.stroke()}}
$('assembly').addEventListener('change',load);$('stage').addEventListener('input',draw);$('search').addEventListener('input',bom);window.addEventListener('resize',draw);$('language').addEventListener('click',()=>{arabic=!arabic;document.documentElement.lang=arabic?'ar':'en';document.documentElement.dir=arabic?'rtl':'ltr';for(const [el,en]of english)text(el,arabic?ar[el.dataset.i18n]:en);text($('language'),arabic?'English':'العربية');const previous=$('stage').value;load();$('stage').value=previous;draw()});load();
</script></body></html>
'''
