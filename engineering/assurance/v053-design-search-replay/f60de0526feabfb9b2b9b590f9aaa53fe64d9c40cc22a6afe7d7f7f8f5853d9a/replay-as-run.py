"""Independent data-only archive replay. Never invokes campaign.run/evaluators."""
import sys
sys.dont_write_bytecode=True
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path,PurePosixPath
import tarfile
import tempfile

ROOT=Path('/home/hayder/Documents/OpenSourceRail')
PUBLICATION=ROOT/'docs/design-engine/design-search'
ARCHIVE=PUBLICATION/'run-evidence.tar.gz'
EXPECTED=json.loads((ROOT/'build/carrier-beam-campaign-definition.json').read_bytes())['campaign_id']
MAX_FILE=64*1024**2
MAX_COMPARISON=256*1024**2
MAX_TOTAL=1024**3
MAX_MEMBERS=20000


def digest(path):
    value=sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024**2),b''):value.update(block)
    return value.hexdigest()


if not ARCHIVE.is_file():raise SystemExit('Archive not ready')
archive_digest=digest(ARCHIVE)
receipt=json.loads((PUBLICATION/'manifest.json').read_bytes())
if receipt['campaign_id']!=EXPECTED or receipt['files_sha256']['run-evidence.tar.gz']!=archive_digest:
    raise ValueError('archive has not been sealed for the current expected campaign')
folder=Path(tempfile.mkdtemp(prefix='osr-independent-design-replay-'))
seen=set();total=0
with tarfile.open(ARCHIVE,mode='r:gz') as archive:
    for member in archive:
        name=member.name;path=PurePosixPath(name)
        maximum=MAX_COMPARISON if len(path.parts)==3 and path.parts[0]=='campaigns' and path.name=='comparison.json' else MAX_FILE
        if (not name or path.is_absolute() or '..' in path.parts or '\\' in name or path.as_posix()!=name or
                name in seen or not member.isfile() or member.size<0 or member.size>maximum):
            raise ValueError('unsafe, duplicate or unbounded archive member: '+name)
        seen.add(name);total+=member.size
        if len(seen)>MAX_MEMBERS or total>MAX_TOTAL:raise ValueError('archive inventory/expansion limit exceeded')
        target=folder.joinpath(*path.parts);target.parent.mkdir(parents=True,exist_ok=True)
        stream=archive.extractfile(member)
        if stream is None:raise ValueError('missing ordinary archive data')
        copied=0
        with stream,target.open('xb') as output:
            while block:=stream.read(1024**2):
                copied+=len(block)
                if copied>member.size:raise ValueError('archive member exceeds declared size')
                output.write(block)
        if copied!=member.size:raise ValueError('archive member expansion differs')
if archive_digest!=digest(ARCHIVE):raise ValueError('archive changed while extracting')
before={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()}
sys.path.insert(0,str(ROOT))
from engineering.design_search import campaign,contracts,publication
checked=publication.verify(PUBLICATION)
value=campaign.compare(EXPECTED,state=folder)
after={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()}
if before!=after:raise ValueError('comparison reconstructed or mutated supposedly complete retained state')
definition=campaign.definition(EXPECTED,state=folder)
journal=json.loads((folder/'campaigns'/EXPECTED/'journal.json').read_bytes())
rows=value['results']+value['confirmations']
attempts={}
for row in rows:
    cache=json.loads((folder/'cache-receipts'/(row['evaluation_id']+'.json')).read_bytes())
    attempt=campaign._relative_attempt(folder,cache['attempt_path'])
    result,record=campaign._validate_attempt(attempt,row['request'])
    if result!=row:raise ValueError('independently loaded worker result differs')
    attempts[cache['attempt_path']]=record
report=dict(schema='osr-independent-retained-campaign-replay/1',campaign_id=EXPECTED,
    extracted_state=str(folder),archive_sha256=archive_digest,archive_members=len(seen),archive_raw_bytes=total,
    extracted_state_unchanged=True,publication_verifier=checked,
    source_files_checked=len(definition['source_sha256']),source_epoch_matches=definition['source_sha256']==campaign.source_epoch(),
    candidate_count=len(value['candidates']),initial_candidate_count=len(definition['candidate_context_ids']),
    primary_count=len(value['results']),confirmation_count=len(value['confirmations']),unique_sealed_attempts=len(attempts),
    cross_campaign_attempts=sum(not path.startswith('campaigns/'+EXPECTED+'/') for path in attempts),
    primary_execution_states=dict(Counter(row['execution_status'] for row in value['results'])),
    primary_numerical_states=dict(Counter(row['numerical_status'] for row in value['results'])),
    primary_screen_states=dict(Counter(row['screen_status'] for row in value['results'])),
    confirmation_screen_states=dict(Counter(row['screen_status'] for row in value['confirmations'])),
    confirmation_scopes=dict(Counter(row['request']['settings'].get('verification_scope') for row in value['confirmations'])),
    worker_readonly_enforcement=dict(Counter(str(record['os_read_only_input_enforced']) for record in attempts.values())),
    watchdog_enforced=sum(bool(record['resource_limits'].get('watchdog_process_group_cleanup')) for record in attempts.values()),
    journal_state=journal['state'],runtime_used_s=journal['runtime_used_s'],runtime_budget_s=definition['specification']['budget']['total_runtime_s'],
    active_runtime_lease=journal.get('active_runtime_lease'),
    next_experiment_candidate=value['next_experiment']['selected_candidate_id'],
    integrated_baseline_status=value['integrated_baseline']['status'],integrated_baseline_candidate=value['integrated_baseline']['selected_candidate_id'],
    complete_installed_candidates=sum(contracts.inventory_summary(candidate)['complete_installed_distribution'] for candidate in value['candidates']),
    requirement_disposition=value['qualification'],
    flags={key:value[key] for key in contracts.FLAGS},solver_execution=False)
(folder/'independent-replay-report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,indent=2,sort_keys=True))
