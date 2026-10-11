"""Strict ingestion of nominal CONTACT benchmark profiles, without adoption."""
from pathlib import Path
import hashlib,json,re,math

DATA=Path(__file__).parent/'data/contact'


def parse(name):
    meta=json.loads((DATA/'provenance.json').read_text())
    if name not in meta['files']:raise ValueError('unregistered profile example')
    raw=(DATA/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=meta['files'][name]['sha256']:raise ValueError('nominal profile source bytes changed')
    fields={};points=[];active=False
    for original in raw.decode().splitlines():
        line=original.split('!',1)[0].strip()
        if line=='point.begin':active=True;continue
        if line=='point.end':active=False;continue
        if active and line:
            f=line.split()
            if len(f) not in (2,3):raise ValueError('unsupported profile coordinate row')
            row=[float(v) for v in f]
            if not all(math.isfinite(v) for v in row):raise ValueError('finite profile coordinates required')
            points.append(row[:2]);continue
        match=re.fullmatch(r'([\w.]+)\s*=\s*([+\-\d.eE]+)',line)
        if match:fields[match[1]]=float(match[2])
    required={'units.len.f','units.ang.f','shift.y','shift.z','rotate','mirror.y','mirror.z','inversion'}
    if not required<=fields.keys() or fields['units.len.f']<=0 or fields['units.ang.f']<=0 or len(points)<3:raise ValueError('explicit profile transformations and coordinate data required')
    if any(fields[k] not in (0.,1.) for k in ('mirror.y','mirror.z','inversion')):raise ValueError('unsupported profile reflection/order flags')
    return dict(schema='osr-nominal-profile-ingestion/1',source=meta['files'][name],profile_type='wheel' if name.endswith('.prw') else 'rail',raw_points=points,
        length_unit_factor_per_m=fields['units.len.f'],angle_unit_factor_per_rad=fields['units.ang.f'],processing=fields,
        source_point_count=len(points),curve_adopted=False,physical_validation=False,
        open_domains=['CONTACT axis/side/datum convention transformation','already-canted rail metadata','profile spline and normal/curvature verification','flange/multiple-patch contact support','project approved profiles and independent contact comparison'])
