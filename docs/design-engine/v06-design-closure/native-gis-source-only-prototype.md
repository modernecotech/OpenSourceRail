# Native GIS source-only import prototype

This prototype addresses project bytecode-cache reads and bootstrap output
boundary failures for the RustGIS return-path research. It is an import-policy
adapter only; it is not an OS sandbox, runtime supervisor or completed GIS
round trip.

## Code and verification

The source additions were integrated into this closure worktree as:

- `a3076be009` — authenticated source-only importer;
- `69aa344fe7` — pinned Python bootstrap;
- `a05ad7f3f6` — shared-software CI tests;
- `1479ac3962` — no-follow result boundary and preflight-failure correction.

The corrected bootstrap pins exact source bytes and rejects symlinked source
roots and result parents. It opens an exclusive result file only after manifest,
source-root and external-output boundaries pass. Earlier failures return a
canonical stdout report without creating a result or importing project modules.
The importer compiles the authenticated `.py` bytes itself; it does not use
Python's normal bytecode cache path. The external command still requires a
separately trusted hash pin.

The coordinator independently checked the exact corrected source commit
`f0fc5a7662dc5e8a50a856e97fee83868565d857` in a temporary snapshot:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -p no:cacheprovider engineering/rustgis/tests/test_source_only_import.py
# 20 passed
PYTHONDONTWRITEBYTECODE=1 python3 -B tools/automation/tests/test_source_only_entry.py
# 21 passed
```

An independent read-only review also passed five earlier-bootstrap regression
probes covering valid and invalid result boundaries, stale loader and argv
failures, relative output, and a symlink-root alias. Those probes created no
result file and imported no project module on failure. The corrected bootstrap
SHA256 is `f8cf2ed625ea9fb8836e48e3acf4ad11afbc09f75efb2884aad14a83756dd1bf`;
the unchanged loader SHA256 is
`224ec888d94780b0f53428cd684e6689e7e69a37b3eca1f1a39315f81d5c2634`.

## Remaining gate work

No GIS project was opened, edited, exported or recalculated with this adapter.
The source-only run-07 proposal is retained privately as
`UNEXECUTED_NOT_ADMITTED`; it has no authorization or execution receipt. The
published native project still has no verified edit → geometry validation →
service/fleet/cost/delivery recalculation → export → second native-edit round
trip. The `-I -B` command flags and Python import policy do not restrict trusted
code's filesystem, network, subprocess or native-library access. Live resource
containment and runtime supervision remain external work.

The earlier Amendment 06 failure remains historical evidence and is not
rewritten. This prototype does not make that attempt pass, replace its packet,
or close the `native-gis-return-path` gate.
