#!/usr/bin/env python3
"""Synthetic consent decision table. Never executes an action or grants approval."""
import argparse
import json
from pathlib import Path

STATES = {'awaiting_approval', 'denied', 'expired', 'unknown',
          'transient_failure', 'ready', 'completed', 'executed'}


def decide(checkpoint, *, scope_approved=False, prerequisites_current=False,
           readback_authorized=False, readback_matches=False):
    state = checkpoint.get('state')
    if state not in STATES:
        raise ValueError('unknown checkpoint state')
    if not isinstance(checkpoint.get('operation_id'), str) or not checkpoint['operation_id']:
        raise ValueError('operation_id required')
    attempts = checkpoint.get('retry_count', 0)
    budget = checkpoint.get('retry_budget', 0)
    if type(attempts) is not int or type(budget) is not int or not 0 <= attempts <= budget <= 3:
        raise ValueError('retry counters must satisfy 0 <= count <= budget <= 3')
    if state == 'completed':
        return ('done', 'verified completion') if readback_matches else ('hold', 'completion lacks current evidence')
    if state in {'executed', 'unknown'}:
        if readback_authorized and readback_matches:
            return 'done', 'read-back matches exact target'
        return ('reconcile' if state == 'unknown' else 'verify', 'read-only check') if readback_authorized else ('hold', 'read-back not authorized')
    # An open prompt cannot be superseded by a second synthetic attempt.
    if state == 'awaiting_approval':
        return 'hold', 'approval prompt open'
    if not scope_approved:
        return 'hold', f'{state} approval' if state in {'denied', 'expired'} else 'scope not approved'
    if not prerequisites_current:
        return 'hold', 'prerequisites stale'
    if attempts >= budget:
        return 'hold', 'attempt budget exhausted'
    if state == 'transient_failure' and checkpoint.get('no_side_effect_evidence') is not True:
        return 'hold', 'failure outcome uncertain'
    return 'attempt', 'one scoped attempt; verify afterward'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkpoint', type=Path)
    parser.add_argument('--scope-approved', action='store_true')
    parser.add_argument('--prerequisites-current', action='store_true')
    parser.add_argument('--readback-authorized', action='store_true')
    parser.add_argument('--readback-matches', action='store_true')
    args = parser.parse_args()
    try:
        if args.checkpoint.stat().st_size > 16 * 1024:
            raise ValueError('checkpoint exceeds 16 KiB')
        action, reason = decide(json.loads(args.checkpoint.read_text()),
            scope_approved=args.scope_approved, prerequisites_current=args.prerequisites_current,
            readback_authorized=args.readback_authorized, readback_matches=args.readback_matches)
    except (ValueError, OSError, TypeError, AttributeError) as exc:
        parser.exit(1, f'{exc}\n')
    print(f'{action}: {reason}')


if __name__ == '__main__':
    main()
