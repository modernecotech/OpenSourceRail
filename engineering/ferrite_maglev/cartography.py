"""Offline SVG of attributed retained route geometry; no clearance inference."""
from html import escape
import json
import math
from pathlib import Path


def simplify(points,tolerance=.4):
    """Ramer–Douglas–Peucker; pixel tolerance affects illustration only."""
    if len(points)<3:return points
    a,b=points[0],points[-1];dx=b[0]-a[0];dy=b[1]-a[1];length=dx*dx+dy*dy
    greatest=-1;index=0
    for i,p in enumerate(points[1:-1],1):
        t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length)) if length else 0
        distance=(p[0]-a[0]-t*dx)**2+(p[1]-a[1]-t*dy)**2
        if distance>greatest:greatest=distance;index=i
    if greatest<=tolerance*tolerance:return [a,b]
    return simplify(points[:index+1],tolerance)[:-1]+simplify(points[index:],tolerance)


def render(design,geojson,output):
    data=json.loads(Path(geojson).read_text()) if Path(geojson).is_file() else {'features':[]}
    lines=[]
    for feature in data['features']:
        geometry=feature.get('geometry') or {};properties=feature.get('properties',{})
        if geometry.get('type')=='LineString':lines.append((properties.get('name','route'),geometry['coordinates']))
        if geometry.get('type')=='MultiLineString':
            lines.extend((properties.get('name','route'),points) for points in geometry['coordinates'])
    points=[p for _,coordinates in lines for p in coordinates]
    if not points:raise ValueError('geographic route lines required for map: '+design['city']['slug'])
    if any(len(p)<2 or not all(type(n) in (int,float) and math.isfinite(n) for n in p[:2]) or not -180<=p[0]<=180 or not -90<=p[1]<=90 for p in points):
        raise ValueError('invalid map coordinates')
    latitude=sum(p[1] for p in points)/len(points);cos=math.cos(math.radians(latitude))
    xmin,xmax=min(p[0]*cos for p in points),max(p[0]*cos for p in points)
    ymin,ymax=min(p[1] for p in points),max(p[1] for p in points)
    scale=min(1080/max(xmax-xmin,1e-8),680/max(ymax-ymin,1e-8))
    xoffset=60+(1080-(xmax-xmin)*scale)/2;yoffset=90+(680-(ymax-ymin)*scale)/2
    def project(p):return (xoffset+(p[0]*cos-xmin)*scale,yoffset+(ymax-p[1])*scale)
    palette=['#087f8c','#ba3b46','#6d4c91','#ba7510','#20703d','#315da8','#a73c85','#525b65']
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="840" viewBox="0 0 1200 840" role="img">',
        '<title>'+escape(design['name'])+' — maglev corridor planning</title>',
        '<rect width="1200" height="840" fill="#f4f7fa"/>',
        '<g font-family="sans-serif" fill="#173249"><text x="40" y="42" font-size="27">'+escape(design['name'])+' · ferrite-PM maglev</text>',
        '<text x="40" y="70" font-size="16">Retained geographic corridors; alignment, clearances, foundations and terminal loops remain unqualified</text></g>']
    for i,(name,coordinates) in enumerate(lines):
        coords=simplify([project(p) for p in coordinates]);d=' '.join(f'{x:.2f},{y:.2f}' for x,y in coords)
        rows.append(f'<polyline points="{d}" stroke="{palette[i%len(palette)]}" fill="none" stroke-width="3" stroke-linejoin="round"><title>{escape(name)}</title></polyline>')
    for station in design['stations']:
        x,y=project((station['lon'],station['lat']))
        rows.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.5" fill="white" stroke="#173249"><title>{escape(station["id"])}</title></circle>')
    rows+=['<text x="40" y="810" font-family="sans-serif" font-size="16" fill="#173249">Offline geographic illustration · no building/utility/water clearance or construction approval implied</text>','</svg>']
    Path(output).write_text('\n'.join(rows)+'\n')
