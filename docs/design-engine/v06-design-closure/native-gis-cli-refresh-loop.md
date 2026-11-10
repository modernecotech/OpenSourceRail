# Native GIS refresh command audit

## Result

The current RustGIS CLI now has a single bounded `reprice --refreshed-output`
path for importing a saved native edit, verifying its retained bytes and
canonical planning request, waiting for the child city study, and exporting
and verifying a new RustGIS project bound to that completed study. Import custody remains in
`build/rustgis-imports`; the refreshed archive is written to a fresh caller
directory. A no-op produces no child study and therefore no refreshed export.

The CLI behavior was checked with synthetic service/export doubles, not a real
city or native RustGIS editor:

```text
tools/automation/osr-python -m pytest -q tests/test_rustgis_cli.py tests/test_rustgis_revision.py
29 passed in 0.21s
```

The regression suite covers typed route/station edits, source and unit guards,
retained failures, import verification, and CLI orchestration through a
completed child study and verified-export response. It does not prove native
project editing, a fresh city calculation, or a native export round trip.

## Runtime boundary

`./osr gis audit` confirms the pinned RustGIS 0.5.0 CLI/desktop binaries are
installed and match the repository's checksums. At the latest disk sample,
5,683,367,936 bytes were free, below the engineering worktree's required
8,589,934,592-byte reserve. The complete native edit → city recalculation →
refreshed-project export was therefore not run. The source-stale run07 proposal
remains unadmitted; its earlier 8 GiB preflight also failed.

## Gate disposition

This closes a CLI orchestration/usability gap only. The native GIS return-path
gate remains **open** until a fresh current-source edited project is processed,
its completed city study and export are independently verified, and its
candidate, service, geography and pricing limits are reviewed. A GIS planning
revision does not revise or validate the train's physical candidate.
