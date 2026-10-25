"""Owned Workbench subprocess; executes only a validated fixed action catalogue."""
import argparse
from pathlib import Path
import resource
import sys
import traceback

from engineering.design_search.contracts import encoded, identity
from engineering.design_search.storage import atomic_immutable
from .interactive import (MAX_BODY, MAX_FILE, _no_acceptance, _read, check_request,
                          tool_snapshot, verify_snapshot, verify_tools)


def execute(request_path, output, root):
    output, request_path, root = Path(output).resolve(), Path(request_path).resolve(), Path(root).resolve()
    if request_path != output / 'request.json' or output.name != _read(request_path, output, 2 * MAX_BODY)['job_id']:
        raise ValueError('server-owned request/output identity required')
    request = check_request(_read(request_path, output, 2 * MAX_BODY))
    result = None
    disposition = 'error'
    try:
        verify_snapshot(request['source_snapshot'], root)
        verify_tools(request['tools'])
        print('Starting ' + request['action'] + ' for job ' + request['job_id'], flush=True)
        from . import experiments
        result = experiments.execute(dict(action=request['action'], parameters=request['parameters']),
                                     output=output / 'outputs', root=root)
        if not isinstance(result, dict):
            raise ValueError('experiment must return a JSON object')
        _no_acceptance(result)
        verify_snapshot(request['source_snapshot'], root)
        verify_tools(request['tools'], allow_setup=request['action'] == 'setup-tools')
        disposition = 'completed'
        print('Calculation completed; physical acceptance remains false', flush=True)
    except Exception as error:
        traceback.print_exc(file=sys.stderr)
        result = dict(execution_status='error', error_type=type(error).__name__, error=str(error),
                      engineering_accepted=False, physical_accepted=False)
    value = dict(schema='osr-trip-interactive-worker-result/1', job_id=request['job_id'],
                 request_id=request['request_id'], execution_status=disposition, result=result,
                 tool_setup_authorised=request['action'] == 'setup-tools',
                 tools_before=request['tools'],
                 tools_after=tool_snapshot(root, request['tools']['worker_python'].get('invocation_path', request['tools']['worker_python']['path'])),
                 engineering_accepted=False, physical_accepted=False)
    value['result_sha256'] = identity(value)
    atomic_immutable(output / 'result.json', encoded(value))
    return 0 if disposition == 'completed' else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args(argv)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    request = check_request(_read(args.request, args.output, 2 * MAX_BODY))
    file_limit = 1024**3 if request['action'] == 'setup-tools' else MAX_FILE
    resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
    return execute(args.request, args.output, args.root)


if __name__ == '__main__':
    sys.exit(main())
