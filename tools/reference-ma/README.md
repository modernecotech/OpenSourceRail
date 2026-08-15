# reference-ma — Python reference interpreter for `osr-interlocking`

Independent implementation of the Movement Authority state machine
specified in
[RFC 0001 §7](../../docs/rfcs/0001-track-state-consensus.md) and
[RFC 0004 §M4](../../docs/rfcs/0004-osr-interlocking-plan.md). The
Rust crate [`osr-interlocking`](../../crates/osr-interlocking/) is the
production code; this Python twin exists so that differential fuzzing
against both implementations can catch bugs in either one.

The public surface mirrors `osr-interlocking`:

- `derive_state(entries)` → `DerivedState`
- `compute_self_ma(train_id, entries, network, now_ns)` → `MovementAuthority`
- `section_available_to(train_id, section, state)` → `bool`
- `forward_chain`, `footprint_from`, `far_end_of`, `locate_section`

Wire format is whatever `serde_json` produces for the Rust types — IDs
are plain `u64`s (`#[serde(transparent)]`), enums are externally
tagged when they carry data, and every struct is field-by-field. The
`__main__.py` CLI reads a case JSON on stdin and writes the same
`MovementAuthority` JSON shape to stdout. The Rust differential test
in
[`crates/osr-interlocking/tests/differential.rs`](../../crates/osr-interlocking/tests/differential.rs)
serialises random log prefixes and compares byte-for-byte.

## Running

Stdlib-only — no dependencies. Quick sanity run:

```bash
cd tools/reference-ma
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Full differential round-trip from the workspace root:

```bash
cargo test -p osr-interlocking --test differential
```

The Rust test skips itself if `python3` is missing or if
`OSR_SKIP_PY_DIFF=1` is set, so CI on hosts without a Python toolchain
still passes.

## CLI

Input (stdin or `--input case.json`):

```json
{
  "network":  { "stations": {...}, "sections": {...}, "lines": [...] },
  "entries":  [ { "entry_id": 1, "term": 1, "timestamp_ns": 0,
                  "payload": { "TrainRegistration": {...} } }, ... ],
  "train_id": 1,
  "now_ns":   1000000000
}
```

Output (stdout):

```json
{
  "train_id": 1,
  "end": { "section": 1001, "offset_mm": 1000000, "direction": "Forward" },
  "applicable_restrictions": [],
  "valid_until_ns": 4000000000,
  "derived_from_entry_id": 3,
  "has_known_position": true
}
```

## Status

| Entry variant         | Supported | Notes                                     |
|-----------------------|-----------|-------------------------------------------|
| `TrainRegistration`   | yes       | full                                      |
| `TrainPositionReport` | yes       | full                                      |
| `TrainDeparture`      | yes       | clears occupancy + route grants           |
| `SwitchObservation`   | yes       | full                                      |
| `RouteGrant` / Release| yes       | full                                      |
| `SpeedRestriction`    | yes       | v1 heuristic matches Rust                 |
| `MaintenanceOverride` | yes       | full                                      |
| `Heartbeat`           | yes       | monotonic-seq guard matches Rust          |
| `FormatVersion`       | yes       | stores `current`                          |
| `SwitchCommand`       | no-op     | advisory; matches Rust                    |
| `RouteRequest`        | no-op     | advisory; matches Rust                    |

The differential test currently covers registrations and position
reports under a fixed linear network. Expanding to include switches,
route grants, and multi-line networks is a straightforward next pass
— the primitives are all in place.
