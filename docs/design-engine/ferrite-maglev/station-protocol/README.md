# Station launch and controller executable evidence

[Actual offline replay](replay.json) · [Compressed JSON execution transcript](executed-tests.txt.gz) · [Source/payload receipt](manifest.json)

9 controller counterexamples and 13 named Rust protocol tests executed successfully. The transcript retains exact commands, return codes, stdout and stderr, including the compiler artifact and binary identity.

The existing resource log now folds atomic corridor/receiving-berth/overlap preparation, a distinct launch commit, held arrivals and complete-consist bundle clearance. Permission expiry cannot free a committed arrival. Individual-clear bypass, failed partial reservation, duplicate/replayed events, persisted restart and missing/replayed tail evidence are exercised.

The controller replay exercises timestamped position/phase prediction, declared overlap and scalar force/current/voltage/loss hypotheses, zero-thrust coast and resistor-braking readiness. Physical outputs stay disabled; a fault never requests removal of onboard support.

**Limits:** one local controller and at most 32 resources, external synthetic readiness/integrity/clearance assertions, no automatic restart resumption, measured motor map, cross-car magnetic phase proof, qualified emergency brake, MCU deadline or physical I/O. Retained ownership cannot make a failed receiver work. Checksums establish record consistency, not authenticated independent acceptance. No engineering, manufacturing or physical release is claimed.
