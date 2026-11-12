# Retained v0.6 engineering ledger implementation context

These are the original source bytes identified by the still-open v0.6 design
closure ledger, authenticated against published commit
`5cfe89488a64549b37d4a7fd3ea9e3d3a8923aea`. The `.source` suffix prevents
archived Python tests from being collected as current tests. SHA-256 values and
original paths are unchanged. `status-before-retention.json` retains the ledger
before relocation; `manifest.json` records all 197 inspected evidence rows and
the three original source files that differ from the current implementation.

This preserves historical implementation context, not current-source execution.
All seven engineering gate states, blockers, reviews and release flags remain
unchanged. Current v0.7 GIS execution is separate evidence.

The deterministic migration was generated with:

```sh
python -m engineering.v06_design_closure.retain_sources \
  --source-revision 5cfe89488a64549b37d4a7fd3ea9e3d3a8923aea --write
```

Omit `--write` for a read-only inventory and authentication proposal. The helper
refuses an original hash that cannot be authenticated, differing existing
archive bytes, unsafe paths, or a different historical revision on rerun.
