# Host Deployment Baseline

This directory is the reproducible software-composition baseline for the five
hardware classes described by RFC 0005. It answers which workspace packages
belong on each host, their startup order, commissioning check, log policy, and
update/rollback contract.

- `hosts.toml` is the source of truth for host images.
- `components.toml` gives every Cargo workspace package a disposition.
- `config/*.toml` contains the non-secret configuration shipped in an image.
- `tools/automation/validate-host-manifests.py` validates the model against Cargo
  metadata and rejects incomplete or legacy-contaminated default images.

The current packages are linked evaluator/control libraries, not independently
supervised daemons. `osr-selftest` is the executable commissioning boundary.
An image builder must statically link the listed packages into its OS-specific
tasks and retain the manifest and Git revision beside the executable. Secrets,
device identities, trust anchors, calibration values, and site addresses are
provisioned after imaging and must never be committed here.

The manifests are an integration and release control. They are not evidence
that an image has passed a hardware-in-the-loop, EMC, environmental, or safety
assessment.

## Validation

```bash
python3 tools/automation/validate-host-manifests.py
cargo test -p osr-trainset-image --all-targets
```

The update contract is deliberately fail-safe: stage and verify an image,
activate it once, require the role self-test and external watchdog heartbeat,
and automatically return to the last-known-good slot if either fails.
