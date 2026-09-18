"""Bind change-review observations across domains without granting engineering release."""
from datetime import datetime, timezone
import hashlib
import json


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def assess(root, package, engineering, portfolio, *, now=None, max_age_seconds=300):
    now=now or datetime.now(timezone.utc)
    blockers=[];observations=[];artifacts=[]
    city=package['city'];revision=package['engineering_revision']
    scopes=sorted({(row.get('erp_project',''),row.get('company_id','')) for row in package['equipment']})
    for project,company in scopes:
        matches=[r for r in (portfolio or {}).get('snapshots',[]) if r.get('city')==city and r.get('project')==project and r.get('company')==company]
        if not project or not company or len(matches)!=1:
            blockers.append(f'ERP scope {project or "unmapped"}: missing or ambiguous city/company observation');continue
        row=matches[0];fresh=False
        try:
            observed=datetime.fromisoformat(row['observed_at'].replace('Z','+00:00'))
            age=(now-observed).total_seconds();fresh=-60<=age<=max_age_seconds
        except (KeyError,TypeError,ValueError):pass
        if not fresh:blockers.append(f'ERP scope {project}: refresh its snapshot before cross-domain review')
        if row.get('engineering_revision')!=revision:blockers.append(f'ERP scope {project}: engineering revision differs')
        observations.append(dict(project=project,company=company,observed_at=row.get('observed_at'),fresh=fresh,sha256=digest(row)))
    if not engineering or engineering.get('city')!=city or engineering.get('engineering_revision')!=revision or not engineering.get('artifacts'):
        blockers.append('Engineering package missing or differs from the proposed revision')
    else:
        for artifact in engineering['artifacts']:
            relative=artifact.get('path','');path=(root/relative).resolve()
            # Paths in operator-prepared evidence must still remain within public roots.
            inside=path.is_relative_to(root.resolve())
            parts=path.relative_to(root.resolve()).parts if inside else ()
            allowed=bool(parts) and parts[0] in {'design','engineering','cities','crates','docs'}
            valid=allowed and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==artifact.get('sha256')
            artifacts.append(dict(path=relative,sha256=artifact.get('sha256'),current=valid))
            if not valid:blockers.append('Engineering artifact changed, unavailable or outside public roots: '+relative)
    result=dict(schema='osr-change-context/1',city=city,environment=package['environment'],package_sha256=package['sha256'],
        engineering_revision=revision,erp=observations,artifacts=artifacts,observations_current=not blockers,blockers=blockers,
        engineering_release_ready=False,remaining=['Complete CAD dependency and solver reruns','Independently accept engineering rework','Supersede and independently accept affected formal evidence'],
        scope='Point-in-time observations. Native ERP must revalidate before actions; supervisory apply does not close engineering release.')
    result['sha256']=digest(result)
    return result
