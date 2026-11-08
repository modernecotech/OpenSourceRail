import argparse,json
from .search import run,verify,specifications,BUDGET

p=argparse.ArgumentParser(description='Bounded same-service station recovery economics')
p.add_argument('command',choices=('plan','run','verify'));p.add_argument('--output')
a=p.parse_args()
if a.command=='plan':value=dict(specifications=specifications(),budget=BUDGET)
elif not a.output:p.error('--output is required')
elif a.command=='run':value=run(a.output)
else:value=verify(a.output)
print(json.dumps(value,sort_keys=True))
