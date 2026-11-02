from pathlib import Path
import json
from engineering.design_search.matched_renewal_research import compare
root=Path.cwd()
r=compare('/home/hayder/.local/state/opensourcerail/worktrees/planning-context-20261031/docs/design-engine/flanged-system-cost-study',root=root,expected_publication_manifest_id='8304503b6b409692552846c046d44dfe659c8c9bc8527f1d5289e954b8d70a79',expected_topology_manifest_id='294de81f3b1cca8215a95704287cfedf74ddfac596232027dee3c030163fdc43',expected_flanged_manifest_id='c6c10afa4889de76b64a806d3b0d6fc9f13ae4d4d40981284a7161c94618605a')
Path('build/matched-renewal-research/epoch-v4/result.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
print('evaluation_id',r['evaluation_id'])
