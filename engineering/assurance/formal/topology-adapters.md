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
interface. The topology migration preserves the original fixture geometry. Subsequent proof
partitions and configuration compilation are described below. The normal
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
  --package osr-odometry --timeout 600 --output build/assurance/my-odometry
```

Timeouts and failed checks remain unproved. Independently accepted safety evidence,
consensus refinement, hardware integration and operating release remain separate.
Historical city simulation bundles still verify as historical artifacts; changed
Rust dependencies require new qualification before claiming current-source results.
Both successful [Samawah and Mosul design options](../../design-options/results.md)
were requalified against commit `a5edbbe84`: nominal service and all
eight degraded cases passed. Those bundles are historical evidence for that
commit; they do not qualify the later state-storage and arithmetic changes.

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

## Reusable calculation and state components

`AuthoritySnapshot::from_log` folds a committed prefix once. Call `authority` for
multiple trains against that owned state, then apply the next committed entry
with `apply_committed_entry` or append a committed suffix with `append_committed`.
The caller retains consensus ordering; this API does not validate or commit log
entries. Exclusive mutable access prevents concurrent reads during an update.
Generated tests compare batching and append operations with complete normal log
replay and movement-authority calculation.

Derived-state tables use `OrderedMap`, a sorted vector of keys and boxed values.
It preserves unique sorted keys and the existing JSON map representation.
Lookup is O(log n); insertion and removal are O(n), and repeated removal during
`retain` is O(n²) in the worst case. Each stored value adds an allocation. These
tradeoffs are explicit: no city-size bound is introduced, but throughput and
allocation behavior must be measured before deployment. Generated operation
sequences compare lookup, mutation, removal, iteration and serialization with
`BTreeMap`.

ATP accepts a reusable immutable `BrakeProfile`. `from_consist` applies the same
conservative braking-curve conversion as the existing consist adapter; `try_new`
rejects nonpositive deceleration. Compile a new profile when vehicle configuration
changes. Existing calls with `ConsistDescriptor` continue to compile the profile
for each evaluation. The determinism harness checks the fixture's compiled
profile against the real reference consist before evaluating twice. It retains
the original position, speed and time domains and compares complete outputs.

`forward_chain_view` borrows validated topology tables without allocating a
section vector. ATP distance and odometry advancement use it. The original
vector-returning walk remains available; generated comparisons cover linear and
ring traversal, direction mismatches, offsets and distance budgets. Movement
authority calculates its forward chain and footprint once per evaluation.

Odometry retains exact integer rounding and fallback behavior across full-width
inputs. Fast paths use narrower arithmetic only when it is equivalent to the
original expression. Boundary and generated tests compare speed and uncertainty
with the previous arithmetic, including zero elapsed time and extreme timestamp,
calibration and pulse values.

### Non-overlap proof partitions

The three-forward-section fixture contains both registered trains and both
symbolic head positions in every partition. One pair of harnesses checks the
following and leading train for each of four wayside conditions: missing,
Clear, Unknown and Present. Both downstream verdicts have the same condition in
each pair; arbitrary mixed verdicts are outside this bounded fixture.

The following train must end on section 1000. The leading train must end on 1002
when the downstream section is Clear, and on 1001 otherwise. On the linear
fixture these bounds imply disjoint authority sections. **All eight partitions
are required** to close this declared non-overlap evidence. Passing one half is
insufficient. The earlier fixture expected extension into 1002 without providing
a Clear verdict; that expectation contradicted fail-restrictive operation.
Ordinary tests now exercise clearance and occupancy independently.

### Execution budgets

The controlled runner defaults to 600 seconds per harness. Manual Kani workflow
dispatch can select 1800 seconds for each of the 48 declared harnesses across
eight packages. The default 4096 MiB per-process address-space limit can be raised
to 8192 MiB in manual dispatch (or configured with `--memory-mib` locally); the
limit is inherited by verifier children and recorded in the evidence. Memory
exhaustion remains a failed proof, and core dumps are disabled.
Timeouts fail the run and kill the verifier's entire process
group, including solver children left behind by the driver. Every completed
outcome retains its command, input hashes and log; interrupted runners may lack
a complete artifact and must be rerun. Kani remains pinned to 0.67.0.

## Current verification follow-through

ATP determinism and interlocking determinism passed on candidate `2bf8b7717`.
Odometry still timed out with 1800 seconds in CI. All eight non-overlap partitions
remain unresolved because the local model exhausted its recorded memory budget.
See the [execution register](results/README.md) for full records, the interrupted
CI interlocking job, reproduction instructions and source boundaries.

## Historical topology-migration verification

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

At that historical checkpoint, remaining timeouts were odometry determinism (`E4.4a`), ATP determinism (`E4.1a`),
interlocking non-overlap (`E1.1a`) and interlocking determinism (`E3.1a`). All four
also timed out in separate 900-second attempts on the shared development host.
These are unresolved proof obligations, not demonstrated counterexamples. Alternative
solver/cache experiments did not establish closure; Z3 also encountered an
internal verifier error on ATP. The reviewed default solver remains unchanged.

The full Rust workspace tests, Clippy with warnings denied, and 27 evidence and
release-packaging regression tests passed. These executions are local and
unattested; exact-commit CI and independent acceptance remain separate.

## Remaining proof work

The remaining properties exercise substantially more than fixture construction.
Odometry determinism compares complete states, including variable-time integer
speed division. Non-overlap also replays two trains into derived occupancy and
train maps. The compiled braking profile and map refactor closed the bounded ATP
and interlocking determinism checks; they did not close these other obligations.

The next design step is to isolate these calculations and state-replay contracts
with explicit input/output invariants, prove the contracts, then verify their
composition. Any such partition must preserve every original input case and
safety check. An assumed contract or a smaller input range cannot be counted as
closure of an existing obligation. The existing full harnesses remain the
reference checks while that work is developed.
