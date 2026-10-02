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
