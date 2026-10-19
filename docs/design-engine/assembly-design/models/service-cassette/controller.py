def step(tripped, i):
    healthy=all((i['locked'],i['earth_ok'],i['fresh'],i['supply_ok']))
    tripped=(not healthy) or (tripped and not (i['reset'] and i['stopped']))
    return {'tripped':tripped,'enabled':bool(i['request'] and healthy and not tripped)}
