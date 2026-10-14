"""Reviewed desktop definition changes invalidate dependent evidence explicitly."""

from copy import deepcopy
from .contracts import fingerprint
from engineering.design_consistency.contracts import validate


def definition_diff(original, proposed):
    validate(original)
    validate(proposed)
    old = {p["id"]: p for p in original["parts"]}
    new = {p["id"]: p for p in proposed["parts"]}
    changed = sorted(
        k for k in old.keys() & new.keys() if fingerprint(old[k]) != fingerprint(new[k])
    )
    materials_changed = fingerprint(original["materials"]) != fingerprint(
        proposed["materials"]
    )
    return dict(
        schema="osr-reviewed-definition-diff/1",
        original_sha256=fingerprint(original),
        proposed_sha256=fingerprint(proposed),
        physical_ids_retained=sorted(old.keys() & new.keys()),
        changed=changed,
        added=sorted(new.keys() - old.keys()),
        removed=sorted(old.keys() - new.keys()),
        materials_changed=materials_changed,
        changed_definition=fingerprint(original) != fingerprint(proposed),
        invalidated=(
            [
                "geometry",
                "mass-cg-inertia",
                "BOM",
                "solver inputs",
                "screens",
                "fault/holdout confirmation",
                "inspection/review",
            ]
            if fingerprint(original) != fingerprint(proposed)
            else []
        ),
        candidate_draft=deepcopy(proposed),
        baseline_overwrite_permitted=False,
        physical_release=False,
        production_released=False,
    )


def desktop_file_state(recorded_sha256, current_sha256):
    return dict(
        state="current" if recorded_sha256 == current_sha256 else "stale",
        definition_diff_required=recorded_sha256 != current_sha256,
        unreviewed_geometry_accepted=False,
        physical_release=False,
    )
