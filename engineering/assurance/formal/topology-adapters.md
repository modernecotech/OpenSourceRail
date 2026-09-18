# Read-only topology adapters

The movement-authority, ATP braking and odometry evaluators share a small
`TrackTopology` interface: line count, borrowed forward/reverse section ordering,
ring status and section lookup. This separates the safety calculation from how a
city stores its geometry. A bounded fixture can use prevalidated constants, so
the verifier spends less work constructing unrelated map and station metadata
before it reaches the property being checked.

## Two storage forms, one evaluator

- `Network` retains the existing city schema, maps, station metadata and normal
  simulator/control callers. Its adapter delegates section lookup to the original
  method and borrows the original line arrays.
- `StaticTopology` borrows immutable section and line tables. Construction and
  lookup allocate nothing. `try_new` rejects duplicate section IDs and dangling
  forward/reverse references. It can validate runtime slices or run at compile
  time for constant tables. Private fields prevent bypassing that constructor.

The constructor checks ID uniqueness and reference integrity. Surveyed alignment,
section dimensions, direction pairing and operating speed limits still require
their own engineering validation.

Both preserve unknown-section lookup failure. The static adapter performs a linear
section search; it is useful for small fixed configurations and bounded verification,
not a measured performance improvement for the full city simulator. It does not
make the existing crates `no_std`, remove allocations from the evaluators, or
constitute a deployed embedded image.

The public interface requires stable line views and unique section resolution.
A new adapter needs its own validation. No ERPNext document, FUXA tag, city schema,
railway command format or deployed control setting is changed by choosing a Rust
storage implementation.

## Verification scope

The Kani fixtures use constant, validated tables with the same two/three forward
sections, paired reverse sections, lengths, directions and speed limits as their
previous network fixtures. Station business metadata is outside the evaluator's
interface. Input assumptions and property assertions remain unchanged. The normal
static lookup and normal evaluator code execute under Kani; there are no stubs,
unverified function contracts or disabled safety/unwinding checks.

A proof over these fixtures establishes the property within their stated bounds.
It is not a proof for every topology adapter, arbitrary city geometry or the Rust
standard library's map implementation. The default `Network` adapter is additionally
compared with static tables through generated tests of movement authorities,
braking outcomes, track advancement and sensor fusion. These cover reversed table
order, forward/reverse tracks, direction mismatches, rings, position/speed
uncertainty, expired authorities and GNSS/balise inputs. Constructor tests reject
malformed tables. Finite comparison tests are not a universal refinement proof.

Proof outcomes are recorded by the existing source-bound runner:

```sh
python3 tools/automation/assurance-evidence.py run \
  --package osr-odometry --timeout 300 --output build/assurance/my-odometry
```

Timeouts and failed checks remain unproved. Independently accepted safety evidence,
consensus refinement, hardware integration and operating release remain separate.
Historical city simulation bundles still verify as historical artifacts; changed
Rust dependencies require new qualification before claiming current-source results.
Both successful [Samawah and Mosul design options](../../design-options/results.md)
have now been requalified against the changed source: nominal service and all
eight degraded cases pass, with every detailed outcome matching the earlier run.

## Reusing the interface

Existing calls with `&Network` keep their behaviour and city serialization. A
consumer with fixed geometry can build borrowed tables and pass the checked
adapter to those same functions:

```rust
use osr_core::{StaticTopology, TrackLine};

// `network` is an existing, validated city Network.
let sections: Vec<_> = network.sections.values().cloned().collect();
let lines: Vec<_> = network.lines.iter().map(TrackLine::from).collect();
let topology = StaticTopology::try_new(&lines, &sections)?;
// compute_self_ma(..., &topology, ...)
// atp_evaluate(..., &topology, ...)
// odom_step(..., &topology)
```

The example allocates its input vectors; the adapter itself only borrows them.
Fixed deployments can instead use constant arrays, as the Kani fixtures do.
Storage selection is a Rust integration choice, not an operator setting or a
change to the ERP/FUXA control boundary.

## Recorded verification

The complete local 300-second run executed all **41 declared properties** with
Kani 0.67.0: **37 passed and four timed out**. The newly completed properties are
odometry forward non-regression (`E4.4b`, 14.3 seconds), uncertainty monotonicity
(`E4.4c`, 15.4 seconds), and GNSS conservatism (`E4.4e`, 52.9 seconds). The existing
balise-reset proof also passes. Compared with the previous 34/41 result, input
ranges, assertions and unwind limits are unchanged.

The [machine-readable summary](results/static-topology-2026-09-18.json) and
[complete log archive](results/static-topology-2026-09-18.tar.gz) retain all
41 outcomes, eight execution manifests, input hashes, the source patch and
regression-test logs. See the [reproduction notes](results/README.md).

Remaining timeouts are odometry determinism (`E4.4a`), ATP determinism (`E4.1a`),
interlocking non-overlap (`E1.1a`) and interlocking determinism (`E3.1a`). All four
also timed out in separate 900-second attempts on the shared development host.
These are unresolved proof obligations, not demonstrated counterexamples. Alternative
solver/cache experiments did not establish closure; Z3 also encountered an
internal verifier error on ATP. The reviewed default solver remains unchanged.

The full Rust workspace tests, Clippy with warnings denied, and 27 evidence and
release-packaging regression tests passed. These executions are local and
unattested; exact-commit CI and independent acceptance remain separate.

## Next proof work

The remaining properties exercise substantially more than fixture construction.
Odometry determinism compares complete states, including variable-time integer
speed division. ATP determinism compares two full topology/envelope evaluations.
The interlocking properties also replay logs into derived occupancy and train
maps. Changing the topology adapter alone does not remove those costs.

The next design step is to isolate these calculations and state-replay contracts
with explicit input/output invariants, prove the contracts, then verify their
composition. Any such partition must preserve every original input case and
safety check. An assumed contract or a smaller input range cannot be counted as
closure of an existing obligation. The existing full harnesses remain the
reference checks while that work is developed.
