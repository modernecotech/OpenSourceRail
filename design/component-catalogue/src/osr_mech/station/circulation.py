"""Connected longitudinal clearance in a 2D rectangular footprint model.

Configuration-space expansion tests a circular clearance envelope. End-to-end
connectivity is not an evacuation, entrance, bidirectional crowd-flow or rescue
acceptance. Site obstacles and boundary exclusions need controlled survey data.
"""
from collections import deque
import math


def continuous_path(bounds, obstacles, width_m):
    if not math.isfinite(width_m) or width_m<=0:
        raise ValueError('positive finite circulation clearance required')
    if any(not math.isfinite(v) for v in bounds):
        raise ValueError('finite circulation bounds required')
    x0,x1,y0,y1=bounds
    if x1<=x0 or y1<=y0:raise ValueError('positive circulation support envelope required')
    for a,b,c,d in obstacles:
        if any(not math.isfinite(v) for v in (a,b,c,d)) or not x0<=a<b<=x1 or not y0<=c<d<=y1:
            raise ValueError('circulation obstacle extends outside its support envelope')
    radius=max(0,width_m/2-1e-10)
    lo,hi,bottom,top=x0+radius,x1-radius,y0+radius,y1-radius
    if lo>=hi or bottom>=top:return False
    expanded=[(max(lo,a-radius),min(hi,b+radius),max(bottom,c-radius),min(top,d+radius))
        for a,b,c,d in set(obstacles)]
    expanded=[r for r in expanded if r[0]<r[1] and r[2]<r[3]]
    xs=sorted({lo,hi,*(r[0] for r in expanded),*(r[1] for r in expanded)})
    ys=sorted({bottom,top,*(r[2] for r in expanded),*(r[3] for r in expanded)})
    free=set()
    for i,(a,b) in enumerate(zip(xs,xs[1:])):
        for j,(c,d) in enumerate(zip(ys,ys[1:])):
            x,y=(a+b)/2,(c+d)/2
            if not any(l<x<r and low<y<high for l,r,low,high in expanded):free.add((i,j))
    seen={cell for cell in free if cell[0]==0};queue=deque(seen)
    while queue:
        i,j=queue.popleft()
        if i==len(xs)-2:return True
        for cell in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
            if cell in free and cell not in seen:seen.add(cell);queue.append(cell)
    return False


def continuous_clear_width(bounds, obstacles):
    low,high=0.,min(bounds[1]-bounds[0],bounds[3]-bounds[2])
    for _ in range(26):
        mid=(low+high)/2
        if continuous_path(bounds,obstacles,mid):low=mid
        else:high=mid
    return low
