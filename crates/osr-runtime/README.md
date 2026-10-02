# osr-runtime

Thin synthetic process hosts for existing consensus, committed interlocking,
ATP, ATO and brake evaluators. No second authority or protection calculator.
See [RFC 0033](../../docs/rfcs/0033-tacs-runtime-and-resource-control.md) and the
[process-reference package](../../engineering/assurance/tacs/README.md).

`osr-train-agent` and `osr-wayside-agent` use newline-framed JSON local I/O ports;
the application messages exchanged through them are signed versioned postcard
packets and existing signed consensus proposals. Filesystem writes precede
outbound effects. Reference keys are intentionally public fixtures; operational
deployment is rejected. Hardware safety outputs and production radio adapters
remain explicit qualification work.

Train binaries require `--safety-channel A|B` and separate journal paths. A owns
network publication; B evaluates committed inputs without duplicate proposals.
The paired-only safety-output port accepts `feed_pair` with optional A/B feeds;
missing either channel trips. `DualGuard` requires exact requests from both and
latches discrepancy, stale/replayed feeds, emergency and either feedback failure.
Only stopped authorised fresh recovery clears a trip. The coordinator feeds at
50 ms against a 100 ms deadline. A late feed latches even without prior sampling.

The output port still blocks on input and samples virtual time. Independent
real-clock sampling, channel-local clocks, source-issued output identities,
power/output isolation and physical braking response are open integration work.
See the [default policy](../../docs/certification/redundancy-policy.json); other
local protection pairs remain open. No availability claim follows from A loss.
