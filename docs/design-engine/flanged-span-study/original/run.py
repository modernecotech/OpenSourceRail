from pathlib import Path
import json,traceback
from engineering.design_search import flanged_span as f
from engineering.station_rail.common import encoded, identity
root=Path('build/runtime-flanged-stage1')
def save(path,value):
    with path.open('xb') as handle: handle.write(encoded(value))
context=f.load_context();spec=f.default_spec()
for name in ('baseline','thick-web','thick-flange'):
    folder=root/name;folder.mkdir(exist_ok=False)
    candidate=f.generate(name)
    request=dict(schema='osr-flanged-span-stage1-request/1',candidate=candidate,context=context,assumptions=spec,
                 runtime_budget=dict(address_space_bytes=1073741824,cpu_seconds=240,wall_seconds=300,workers=1),
                 disposition='Research calculation; no approval or selected reference change')
    request['request_id']=identity(request);save(folder/'request.json',request)
    try:
        quantities=f.quantities(candidate,spec);analysis=f.evaluate(candidate,context,spec);cost=f.estimate(candidate,quantities,spec)
        output=dict(schema='osr-flanged-span-stage1-result/1',request_id=request['request_id'],candidate_id=candidate['candidate_id'],
                    quantities=quantities,analysis=analysis,cost=cost,execution='completed')
        output['result_id']=identity(output);save(folder/'result.json',output)
        print(name,output['result_id'],flush=True)
    except Exception:
        with (folder/'failure.txt').open('x') as handle:traceback.print_exc(file=handle)
        raise
