#!/usr/bin/env python3
"""Check the unreviewed development default; do not authorise hardware release."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = 'docs/certification/redundancy-policy.json'
FUNCTIONS = {'train-protection', 'point-proving-and-locking', 'crossing-protection',
             'doors-and-platform-protection', 'charging-isolation', 'obstacle-protection'}
COMMON_CAUSES = {'shared-software', 'shared-sensor-fixture', 'shared-host', 'shared-test-keys',
                'shared-clock', 'shared-comparator', 'unqualified-power-and-output-paths'}


def validate_policy(policy: dict) -> list[str]:
    expected = {'schema': 'osr-redundancy-policy/1', 'status': 'development-default-unreviewed',
                'logical_channels': ['A', 'B'], 'permission': 'two-out-of-two', 'trip': 'either-channel',
                'channel_loss': 'stop-affected-function', 'single_channel_operation': False,
                'automatic_takeover': False, 'raft_is_safety_redundancy': False,
                'physical_independence_qualified': False, 'operational_release_ready': False}
    issues = [f'redundancy default differs: {key}' for key, value in expected.items()
              if policy.get(key) != value or type(policy.get(key)) is not type(value)]
    functions = policy.get('functions', [])
    if {f.get('id') for f in functions} != FUNCTIONS or len(functions) != len(FUNCTIONS):
        issues.append('missing or duplicate protection function')
    for function in functions:
        state = 'logical-pair-executed' if function.get('id') == 'train-protection' else 'open'
        if function.get('reference_state') != state or function.get('physical_state') != 'open':
            issues.append('unexecuted/unqualified local pair claimed: ' + str(function.get('id')))
    if not COMMON_CAUSES <= set(policy.get('common_causes', [])):
        issues.append('missing common-cause boundary')
    if not policy.get('hardware_mapping'):
        issues.append('missing hardware/channel mapping obligation')
    return issues


def check_policy(root: Path = ROOT) -> list[str]:
    try:
        return validate_policy(json.loads((root/POLICY).read_text()))
    except (OSError, ValueError, TypeError, AttributeError) as error:
        return ['invalid redundancy policy: ' + str(error)]


if __name__ == '__main__':
    issues = check_policy()
    if issues:
        raise SystemExit('; '.join(issues))
    print('Two-channel development default coherent; physical pairs and operational release open')
