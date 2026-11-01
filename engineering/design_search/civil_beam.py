"""Deterministic gross-elastic simply supported Euler--Bernoulli response.

The inputs explicitly prescribe positive stepped EI, nonnegative distributed
loads and downward point loads. Support reactions and moment extrema follow
equilibrium. Virtual work uses exact-order Gaussian quadrature on every smooth
piece; there is no averaged section, nonlinear material model or acceptance gate.
"""
from math import fsum, isfinite, sqrt


SCOPE = ("Simply supported, small-displacement, gross-elastic Euler-Bernoulli beam; "
    "prescribed piecewise constant EI, downward loads only. Excludes shear deformation, "
    "torsion, cracking, prestress, creep, dynamics, buckling, composite-action validation "
    "and physical or structural acceptance. Exact-order polynomial quadrature is subject "
    "to floating-point roundoff, not a directed-rounding numerical certificate.")


def _finite(value, name, *, positive=False, nonnegative=False):
    message = "Finite " + ("positive " if positive else "nonnegative " if nonnegative else "") + name + " required"
    try:
        converted = float(value) if type(value) in (int,float) else float("nan")
    except (OverflowError,ValueError) as exc:
        raise ValueError(message) from exc
    if (not isfinite(converted) or positive and converted<=0 or nonnegative and converted<0):
        raise ValueError(message)
    return converted


def _sum(values, name):
    """Reject overflow/nonfinite arithmetic rather than publishing a response."""
    try:
        result = fsum(values)
    except (OverflowError,ValueError) as exc:
        raise ValueError("Finite derived " + name + " required") from exc
    return _finite(result,"derived " + name)


def _cells(value):
    if not isinstance(value,(list,tuple)) or not value:
        raise ValueError("A nonempty ordered list of stepped beam cells required")
    rows = []
    for cell in value:
        if not isinstance(cell,dict) or any(key not in cell for key in
                ("x_start_m","x_end_m","EI_Nm2","distributed_load_N_m")):
            raise ValueError("Explicit cell intervals, EI and distributed load required")
        start = _finite(cell["x_start_m"],"cell start")
        end = _finite(cell["x_end_m"],"cell end")
        if end<=start or rows and start!=rows[-1][1]:
            raise ValueError("Positive, exactly contiguous, ordered cell intervals required")
        _finite(end-start,"cell length",positive=True)
        rows.append((start,end,_finite(cell["EI_Nm2"],"EI",positive=True),
            _finite(cell["distributed_load_N_m"],"distributed load",nonnegative=True)))
    _finite(rows[-1][1]-rows[0][0],"beam span",positive=True)
    return tuple(rows)


def _points(value, start, end):
    if not isinstance(value,(list,tuple)):
        raise ValueError("An explicit list of downward point loads required")
    rows = []
    for point in value:
        if not isinstance(point,dict) or "x_m" not in point or "force_N" not in point:
            raise ValueError("Explicit point position and downward force required")
        x = _finite(point["x_m"],"point position")
        force = _finite(point["force_N"],"point force",nonnegative=True)
        if not start<=x<=end:
            raise ValueError("Point load outside supported span")
        rows.append((x,force))
    return tuple(sorted(rows))


def _position(value,start,end):
    x = _finite(value,"observation position")
    if not start<=x<=end:
        raise ValueError("Observation outside supported span")
    return x


def _reactions(cells,points):
    start,end = cells[0][0],cells[-1][1]
    total = _sum([q*(b-a) for a,b,ei,q in cells]+[force for x,force in points],"total load")
    moment = _sum([q*(b-a)*(a-start+(b-a)/2) for a,b,ei,q in cells]
        +[force*(x-start) for x,force in points],"load moment")
    right = _finite(moment/(end-start),"derived right reaction")
    return _finite(total-right,"derived left reaction"),right,total,moment


def _moment(cells,points,left,x):
    start = cells[0][0]
    distributed = []
    for a,b,ei,q in cells:
        length = max(0.,min(x,b)-a)
        distributed.append(q*length*(x-a-length/2))
    return _sum([left*(x-start),-_sum(distributed,"distributed moment"),
        -_sum((force*(x-position) for position,force in points if position<x),"point-load moment")],"bending moment")


def _shear_right(cells,points,left,x):
    return _sum([left,-_sum((q*max(0.,min(x,b)-a) for a,b,ei,q in cells),"distributed shear"),
        -_sum((force for position,force in points if position<=x),"point-load shear")],"shear")


def _unit_moment(x,position,start,end):
    return ((end-position)/(end-start)*(x-start)-max(0.,x-position))


def _integrate(cells, splits, integrand, order=2):
    start,end = cells[0][0],cells[-1][1]
    breaks = sorted({start,end,*(a for a,b,ei,q in cells),
        *(b for a,b,ei,q in cells),*splits})
    if order==2:
        nodes_weights = ((-1/sqrt(3),1.),(1/sqrt(3),1.))
    elif order==3:
        nodes_weights = ((-sqrt(3/5),5/9),(0.,8/9),(sqrt(3/5),5/9))
    else:
        raise ValueError("Declared two- or three-point Gaussian order required")
    terms = []
    cell_index = 0
    for a,b in zip(breaks,breaks[1:]):
        half = (b-a)/2
        middle = a+half
        while cell_index<len(cells)-1 and middle>cells[cell_index][1]:
            cell_index += 1
        ei = cells[cell_index][2]
        terms.append(half*_sum((weight*integrand(middle+half*node)/ei for node,weight in nodes_weights),"quadrature integrand"))
    return _sum(terms,"integral")


def deflection_influence(cells,observation_x_m):
    """Return callable ``x -> downward m/N`` for a unit point force at x.

    Reciprocity is evaluated by virtual work with the actual stepped EI. The
    distributed-load field is validated but does not enter this unit influence.
    """
    rows = _cells(cells)
    start,end = rows[0][0],rows[-1][1]
    observation = _position(observation_x_m,start,end)
    def influence(x_m):
        x = _position(x_m,start,end)
        return _integrate(rows,(observation,x),lambda s:
            _unit_moment(s,observation,start,end)*_unit_moment(s,x,start,end))
    return influence


def deflection_upper_bound(cells,point_loads):
    """Bound downward deflection at every observation within this beam model.

    For all observation y, its unit-load moment satisfies
    ``0 <= m_y(s) <= (s-a)*(b-s)/(b-a)``. Downward loads imply nonnegative
    sagging moment, hence integrating M times this envelope over EI bounds
    every observation. Three-point Gauss integrates each quartic piece exactly
    to floating-point roundoff; this is not an interval-arithmetic certificate.
    """
    rows = _cells(cells)
    start,end = rows[0][0],rows[-1][1]
    points = _points(point_loads,start,end)
    left,right,total,moment = _reactions(rows,points)
    return _integrate(rows,[x for x,force in points],lambda s:
        _moment(rows,points,left,s)*(s-start)*(end-s)/(end-start),order=3)


def analyse(cells,point_loads,observation_x_m=None):
    """Calculate static response without promoting any engineering status.

    Observation may be one coordinate or a nonempty list; omitted means span
    midpoint. Positive moment is sagging, positive shear acts upward on the
    left cut face, and reported deflection is positive downwards. Support point
    loads affect reactions but cancel from the internal beam response.
    """
    rows = _cells(cells)
    start,end = rows[0][0],rows[-1][1]
    points = _points(point_loads,start,end)
    left,right,total,load_moment = _reactions(rows,points)
    scalar = not isinstance(observation_x_m,(list,tuple))
    observations = [start+(end-start)/2 if observation_x_m is None else observation_x_m] if scalar else list(observation_x_m)
    if not observations:
        raise ValueError("At least one observation required")
    observations = [_position(x,start,end) for x in observations]
    breaks = sorted({start,end,*(a for a,b,ei,q in rows),
        *(b for a,b,ei,q in rows),*(x for x,force in points)})
    extrema = set(breaks)
    shear_values = []
    cell_index = 0
    for a,b in zip(breaks,breaks[1:]):
        middle = a+(b-a)/2
        while cell_index<len(rows)-1 and middle>rows[cell_index][1]:
            cell_index += 1
        q = rows[cell_index][3]
        va = _shear_right(rows,points,left,a)
        vb = _finite(va-q*(b-a),"derived cell-end shear")
        shear_values.extend((va,vb))
        if q>0:
            root = a+va/q
            if a<root<b:
                extrema.add(root)
    moment_values = [(x,_moment(rows,points,left,x)) for x in sorted(extrema)]
    maximum_x,maximum = max(moment_values,key=lambda item:(item[1],-item[0]))
    per_cell_extrema = []
    for a,b,ei,q in rows:
        cell_x,cell_maximum = max((item for item in moment_values if a<=item[0]<=b),
            key=lambda item:(item[1],-item[0]))
        per_cell_extrema.append(dict(x_start_m=a,x_end_m=b,
            maximum_sagging_moment_Nm=cell_maximum,maximum_sagging_moment_x_m=cell_x))
    deflections = []
    for x in observations:
        displacement = _integrate(rows,[x,*[p for p,force in points]],lambda s:
            _moment(rows,points,left,s)*_unit_moment(s,x,start,end))
        deflections.append(dict(x_m=x,downward_deflection_m=displacement))
    return dict(schema="osr-stepped-elastic-beam-response/1",span_m=end-start,support_x_m=[start,end],
        reaction_left_N=left,reaction_right_N=right,
        maximum_sagging_moment_Nm=maximum,maximum_sagging_moment_x_m=maximum_x,
        per_cell_extrema=per_cell_extrema,
        maximum_absolute_shear_N=max(abs(x) for x in shear_values),
        deflections=deflections,deflection_at_observation_m=(deflections[0]["downward_deflection_m"] if scalar
            else [row["downward_deflection_m"] for row in deflections]),
        force_residual_N=_sum((left,right,-total),"force residual"),
        moment_residual_Nm=_sum((right*(end-start),-load_moment),"moment residual"),
        right_support_internal_moment_residual_Nm=_moment(rows,points,left,end),
        integration="two-point Gauss per cell/point-load/observation interval; cubic exact-order virtual work",
        sign_convention="positive sagging moment; shear upward on left cut face; downward deflection positive",
        scope=SCOPE,physical_accepted=False,engineering_accepted=False)
