def step(tripped, i):
    healthy=sum(int(i[n])<<b for b,n in enumerate(('locked','earth_ok','fresh','supply_ok')))==15
    tripped=(not healthy) or (tripped and not (i['reset'] and i['stopped']))
    return {'tripped':tripped,'enabled':bool(i['request'] and healthy and not tripped)}
