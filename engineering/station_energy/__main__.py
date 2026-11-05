"""Build, run and independently replay the bounded Rust station-energy screen."""
import argparse
import json
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.design_search.native_search import _parse, _read
from . import examples, runner


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('build', 'examples', 'run', 'verify'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--request', type=Path)
    args = parser.parse_args(argv)
    if args.action == 'build':
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
