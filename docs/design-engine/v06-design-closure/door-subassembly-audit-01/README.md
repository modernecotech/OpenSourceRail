# Door-system inventory audit — research candidate 9f6d

This read-only audit covers the same-candidate proposed door-opening, door-leaf, door-window and door-electrical groups in the six-car installation. It counts materials, stock allowances, occurrence quantities, source dimensions and available static CAD nodes. It does not create a new door design or establish operation, accessibility, safety or manufacturing release.

## Candidate and result

- Body candidate: `9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba`
- Body evaluation / engineering revision: `dfb48ca3fac6ee9b702ae13b2e5e4e0c112d734263750deefb25ad5718fdb272`
- Matching delivery proposal: `7b88d05f9e0a16ada127d60e51d8ebfdc23b0dcb90ba0c906b2050d4e65a5775`
- Delivery bundle evaluation: `b0d332a0fe3883e5a0783057bf0bc93f99f5235fc9b9af3e83a5cb7cc7909c78`
- Scope: **93 proposed part types** and **10,296 listed pieces** across 12 openings, 24 leaves, 24 glazed door panels and 12 electrical operator sets.

| Provisional per-train allowance | Low | Base | High |
| --- | ---: | ---: | ---: |
| Door-group mass | 947.401 kg | 1,180.332 kg | 1,563.649 kg |
| Direct part/process cost | $13,154 | $33,260 | $87,654 |

These are counted proposal allowances, not measured installed mass or a complete door-system purchase price. All 93 part types have unverified finished geometry; the source proposal has zero controlled drawing references, zero inspection-release references and zero parts marked finished-geometry-verified.

## What the current model does and does not define

The inventory proposes a 1.4 m clear opening and two 0.76 × 2.16 m leaves, one 2.9 m guide per opening, one 5.8 m synchronous belt per opening, and a 24 V / 200 W motor envelope per opening. The leaf/belt kinematic path and the motor/reducer supplier interface are not resolved. The dimensions and positions are hypotheses in the source model.

The published GLB contains 83 door-named nodes/meshes, but has no door animation, swept-motion envelope, installation/removal path or door-specific SolidCraft/FieldCraft analysis. It is a static presentation export, not a parametric mechanism or verified assembly. Open work includes door force and duty, leaf motion and synchronisation, interlocks and obstruction behavior, seal and threshold tolerances, platform gap, accessible egress, cable routing, fastener/joint detail, tooling/access, inspection, maintenance and independent checks.

## Evidence and execution limits

`audit.json` preserves the complete part-level output and five input SHA-256 pins. All five pins were independently confirmed against this closure worktree. The audit was generated from source commit `661b8414a5f77a4184978ddd70d31b22f2545800`; the current branch later added documentation only, and those pinned source inputs still match. Its SHA-256 is `144d0fd96db4966699c223b3b47a0ddcf509d07d7b6eb167ba2796b1585ffb1a`.

`execution-boundary.json` records the limits accurately: this was read-only JSON/gzip/glTF parsing and grouped arithmetic, with no network/native CAD/FEA invocation or source change. The worker did not preserve a command log or measure runtime and applied no per-process timeout/RAM limit; OS sandbox enforcement was false. This audit is not qualification evidence.
