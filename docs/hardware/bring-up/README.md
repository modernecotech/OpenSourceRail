# Hardware bring-up — v1 deliverable of RFC 0007

This directory holds the bring-up procedures for the five physical
host classes of OpenSourceRail. Each file is a **step-by-step
runbook** an engineer with the relevant dev kit can execute and
produce a bring-up report at the end of.

Per [RFC 0007](../../rfcs/0007-hardware-reference-designs.md)
Raspberry Pi + Radxa only:

| Class | Dev kit | Runbook |
|---|---|---|
| **T-ECU/S safety MCU** | Raspberry Pi Pico 2 (RP2350) × 2 | [t-ecu-s.md](t-ecu-s.md) |
| **T-ECU/A application** | Raspberry Pi CM5 IO Board | [t-ecu-a.md](t-ecu-a.md) |
| **T-OBS obstacle detection** | Pico 2 × 2 + Raspberry Pi CM5 IO Board + sensor eval modules | [hardware/t-obs/diy-assembly](../../../hardware/t-obs/diy-assembly/) |
| **W-SBC wayside** | Radxa CM5 IO Board | [w-sbc.md](w-sbc.md) |
| **S-SBC station** | Raspberry Pi CM5 + Waveshare CM5-IO | [s-sbc.md](s-sbc.md) |

## Reporting format

Each runbook ends with a **bring-up report** template. After
completing the steps, copy the template into the deployment's own
tree (e.g. `deployments/<country>/<city>/hardware/bring-up/`) and
fill in the pass/fail results per-step. The template carries the
commit hash of the runbook so a later auditor can reconstruct
what was tested.

## What a pass means

A dev-kit bring-up is "passed" when every mandatory step produces
the expected outcome. Failures are classified:

- **FAIL-HW** — the hardware itself is faulty or the vendor dev
  kit is DOA. Replace and retry.
- **FAIL-SW** — the OSR Rust stack has a bug on the target
  platform. File an issue against the corresponding crate.
- **FAIL-DOC** — the runbook is wrong / incomplete. File an issue
  against this doc.

No step is optional unless explicitly marked `(optional)`. Skipping
mandatory steps invalidates the bring-up.

## Where this sits in the roadmap

These procedures are RFC 0007 v1 ([rollout table](../../rfcs/0007-hardware-reference-designs.md#11-rollout)).
v2 of the hardware rollout is the custom baseboard schematics; v3
is compliance testing. Everything here is prelude — making sure
the vendor silicon and the Rust stack meet before we commit a
baseboard design.
