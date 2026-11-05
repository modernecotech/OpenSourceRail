"""Build, run and independently replay the bounded Rust station-energy screen."""
import argparse
import json
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.design_search.native_search import _parse, _read
from . import examples, runner


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('build', 'examples', 'run', 'verify',
        'arrestor-build', 'arrestor-examples', 'arrestor-run', 'arrestor-verify', 'arrestor-reprice',
        'arrestor-publish', 'arrestor-reference-verify'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--request', type=Path)
    parser.add_argument('--from-state', type=Path, help='Exact-source cached arrestor physics for repricing')
    args = parser.parse_args(argv)
    if args.action.startswith('arrestor-'):
        from . import arrestor, arrestor_examples
        if args.action == 'arrestor-build':
            result = arrestor.build(root)
        elif args.action == 'arrestor-examples':
            result = arrestor_examples.request(root)
        elif args.action == 'arrestor-publish':
            if args.from_state is None:
                parser.error('--from-state is required')
            result = arrestor.publish_reference(args.from_state, root)
            arrestor.render_reference(root)
            result = dict(publication_id=result['publication_id'])
        elif args.action == 'arrestor-reference-verify':
            result = arrestor.verify_reference(root, state=args.from_state)
            result = dict(publication_id=result['publication_id'], verified=True)
        else:
            if args.output is None:
                parser.error('--output is required')
            if args.action == 'arrestor-verify':
                result = arrestor.verify(args.output, root)
            elif args.action == 'arrestor-reprice':
                if args.from_state is None:
                    parser.error('--from-state is required')
                result = arrestor.reprice(args.output, args.from_state, root)
            else:
                if args.request is None:
                    parser.error('--request is required')
                result = arrestor.run(args.output, _parse(_read(args.request,
                    runner.MAX_REQUEST_BYTES)), root)
    elif args.action == 'build':
        result = runner.build(root)
    elif args.action == 'examples':
        result = examples.request()
    else:
        if args.output is None:
            parser.error('--output is required')
        if args.action == 'verify':
            result = runner.verify(args.output, root)
        else:
            if args.request is None:
                parser.error('--request is required; use examples for explicit synthetic inputs')
            result = runner.run(args.output, _parse(_read(args.request,
                runner.MAX_REQUEST_BYTES)), root)
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
