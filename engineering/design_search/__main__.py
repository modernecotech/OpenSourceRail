"""Command-line candidate campaigns and explicitly incomplete research twins."""
import argparse
import json
from pathlib import Path
import sys

from . import campaign


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    group = commands.add_parser('campaign').add_subparsers(dest='action', required=True)
    create = group.add_parser('create'); create.add_argument('specification', type=Path)
    create.add_argument('--state', type=Path, default=campaign.STATE)
    run = group.add_parser('run'); run.add_argument('campaign_id')
    run.add_argument('--state', type=Path, default=campaign.STATE)
    run.add_argument('--max-jobs', type=int)
    for name in ('compare', 'tasks', 'publish'):
        child = group.add_parser(name); child.add_argument('campaign_id')
        child.add_argument('--state', type=Path, default=campaign.STATE)
        if name == 'compare': child.add_argument('--full', action='store_true')
        if name == 'publish': child.add_argument('--output', type=Path, default=campaign.ROOT/'docs/design-engine/design-search')
    twin = commands.add_parser('twin').add_subparsers(dest='action', required=True)
    compile_command = twin.add_parser('compile'); compile_command.add_argument('candidate_id')
    compile_command.add_argument('--campaign', required=True, dest='campaign_id')
    compile_command.add_argument('--state', type=Path, default=campaign.STATE)
    compile_command.add_argument('--purpose', required=True, choices=('research',))
    compile_command.add_argument('--allow-incomplete', action='store_true')
    compile_command.add_argument('--without-native', action='store_true')
    compile_command.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if args.command == 'twin':
        from . import twin
        comparison = campaign.compare(args.campaign_id, state=args.state)
        choices = [row for row in comparison['candidates'] if row['candidate_id'] == args.candidate_id]
        if len(choices) != 1: raise ValueError('candidate is not an unambiguous member of this campaign')
        candidate = choices[0]
        evidence = [row for row in comparison['results']+comparison['confirmations'] if row['candidate_id'] == args.candidate_id]
        output = args.output or campaign.ROOT/'docs/design-engine/design-search-twins'/args.candidate_id
        answer = twin.compile(candidate, evidence, output=output, export_native=not args.without_native,
                              allow_incomplete=args.allow_incomplete)
    elif args.action == 'create':
        answer = campaign.create(args.specification, state=args.state)
    elif args.action == 'run':
        answer = campaign.run(args.campaign_id, state=args.state, max_jobs=args.max_jobs)
    elif args.action == 'tasks':
        campaign.definition(args.campaign_id, state=args.state)
        answer = json.loads((args.state/'campaigns'/args.campaign_id/'agent-tasks.json').read_bytes())
    elif args.action == 'publish':
        from .publication import publish
        answer = publish(args.campaign_id, state=args.state, output=args.output)
    else:
        value = campaign.compare(args.campaign_id, state=args.state)
        answer = value if args.full else dict(campaign_id=args.campaign_id,
            candidates=len(value['candidates']), evaluations=len(value['results']),
            confirmations=len(value['confirmations']), next_experiment=value['next_experiment'],
            integrated_baseline=value['integrated_baseline'], physical_accepted=False)
    print(json.dumps(answer, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, RuntimeError) as error:
        print('Candidate campaign held: ' + str(error), file=sys.stderr)
        sys.exit(2)
