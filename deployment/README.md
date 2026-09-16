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

## Business operating services

[ERPNext deployment](erpnext/README.md) runs on an ordinary business server,
separate from the five railway control host classes. It provides the operating
platform without adding ERP dependencies to onboard or wayside images.

## Equipment supervision

[ERPNext + FUXA lifecycle deployment](supervision/README.md) provides generated city equipment packages, a durable telemetry/event gateway and a simulated station pilot.
Its prepared-package review traces design and embedded contract changes through
installed/evidence/business identities before a baseline can be replaced.
The [operating-readiness audit](../docs/operating/readiness.md) compiles all 266
tracked city asset registers through the supervision package and all 266 ERP and
component profiles, while retaining operator and physical commissioning inputs
as explicit fail-closed states.

The `integrated-stack` CI workflow builds a clean, disposable Samawah/Mosul
deployment from these checked-in inputs. It exercises native ERP transactions,
the gateway, embedded simulator, pinned FUXA application and Workbench together,
including a gateway outage and recovery, then removes the evaluation volumes.
This is software integration evidence; it does not replace commissioning or
hardware-in-the-loop acceptance.
