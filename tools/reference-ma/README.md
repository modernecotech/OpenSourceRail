# reference-ma — Python reference interpreter for `osr-interlocking`

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Historical studies retain their own recorded configurations and results.

[Project introduction](../../README.md) · [Engineering approach and current status](../../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

Independent implementation of the Movement Authority state machine
used by the current [control architecture](../../docs/ARCHITECTURE.md).
The [Rust implementation](../../crates/osr-interlocking/) and this independent
Python oracle are unqualified research software. Differential fuzzing
compares the same committed-log cases across both implementations.
Synthetic regression fixtures are not accepted vehicle configurations.

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
