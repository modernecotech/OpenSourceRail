# RFC 0026 — Charging Connector and DC-Link Reconciliation

**Status:** Draft — reconciles [RFC 0010](0010-station-design-standard.md) and [RFC 0021 §6](0021-battery-traction.md#6-charging-interface)
**Date:** 2026-04-26
**Depends on:** [RFC 0010 Station Design Standard](0010-station-design-standard.md), [RFC 0021 Battery Traction](0021-battery-traction.md)

## 1. Summary

The current spec contains an internal inconsistency:

- [RFC 0010 §1](0010-station-design-standard.md) commits **1 000 kW**
  charging at `terminal` and `depot-terminal` archetypes, and **500 kW**
  at `major` and `interchange`.
- [RFC 0021 §6.1](0021-battery-traction.md#6-charging-interface) specifies
  a **210 kW CCS2** receptacle per car at depot stalls (3 receptacles in
  parallel = 630 kW per consist).
- [RFC 0021 §6.2](0021-battery-traction.md#6-charging-interface) specifies
  a **100 kW** plug-in charger at `depot-terminal` for opportunity charging.

The 210 kW CCS2 spec is internally consistent with itself — CCS2's HPC
envelope reaches ~350 kW per Combo 2 connector, so 210 kW is well
inside the standard. The mismatch is between the **station-archetype
power figures in RFC 0010** and the **connector spec in RFC 0021 §6**:
no connector currently in RFC 0021 reaches the 1 000 kW target the
station archetype assumes, and CCS2 cannot scale to 1 MW.

This RFC commits a **two-tier charging-connector architecture** that
covers both ends of the power range.

## 2. Non-goals

- **Not a re-spec of station archetypes.** RFC 0010's archetype
  power targets remain canonical.
- **Not a re-spec of pack chemistry or charge-acceptance limits.**
  Per-cell rates remain as RFC 0021 §3 + [RFC 0024](0024-battery-thermal-high-ambient.md).
- **Not a hydrogen-refuelling or battery-swap RFC.** Both remain
  out of scope per RFC 0021 §6.3.

## 3. Power-tier architecture

| Tier | Power | Connector | Use case |
|---|---|---|---|
| **Tier 1: depot stall** | 210 kW × 3 receptacles per consist = 630 kW | CCS2 (per RFC 0021 §6.1) | Overnight + scheduled depot charging. **Unchanged.** |
| **Tier 2: terminal turnback** | 500 kW–1 000 kW per consist | **Side-pin** (primary) or **pantograph-down** (alternate) | `major`, `interchange`, `terminal`, `depot-terminal` opportunity charging during turnback dwell |

CCS2 stays as the depot connector — it is correct for that role and
the per-receptacle handling is well-understood. The terminal-tier
connector is the new piece this RFC commits.

## 4. Tier 2 — side-pin (primary)

| Aspect | Choice | Rationale |
|---|---|---|
| Architecture | Passive copper bus-bar at platform edge; train extends a side-mounted pin to contact | Matches OSR's level-boarding philosophy — the platform-edge geometry already aligns the pin without additional alignment hardware |
| Voltage / current | 1 000 V DC × 1 000 A = 1 MW class | Matches RFC 0010 `terminal` archetype |
| Connector | Schaltbau-class high-current side connector + actuated pin | Schaltbau, Stäubli, Mersen all produce 1 000 A class units |
| Actuation | Pneumatic or electric linear actuator on the train | Same actuator family as RFC 0023 doors — commodity industrial silicon |
| Safety interlock | Pin retraction interlocked with door-close + brake-applied via [`osr-occ`](../../crates/osr-occ/) | No live contact while doors are open or train is moving |
| DC-link cabinet | 1 MW rectifier at platform end (ABB Terra HP, Heliox FLEX 600, or Star Charge / TGOOD tier-2) | Common cabinet across all Tier 2 sites |

**Why side-pin over pantograph:** OSR is already a level-boarding system
(350 mm low floor, platform-edge gap < 100 mm). The platform-edge
geometry is dimensionally controlled to ± 5 mm by the precast L-unit
([RFC 0010](0010-station-design-standard.md)). The side-pin reuses
this precision rather than adding a roof-level alignment problem.
Pantograph-down also imposes a structural-load case on the canopy
that the current portal-frame catenary-free design ([RFC 0010 §X](0010-station-design-standard.md))
explicitly avoids.

## 5. Tier 2 alternate — pantograph-down (OppCharge)

For sites where platform-edge geometry doesn't suit a side-pin (e.g.
mid-line `major` archetype with island platform and offset
canopy), specify pantograph-down per the ABB OppCharge / Siemens
HPC150 reference.

| Aspect | Choice |
|---|---|
| Power | 600 kW continuous |
| Pantograph | 1 m roof-mounted, single-arm, lift-down |
| Overhead bus-bar | Mounted to canopy portal beam, 5.5 m above rail head |
| Reference | ABB OppCharge ID, Siemens HPC150 |

Pantograph-down does require a structural-load case on the canopy,
but the existing portal-frame design ([RFC 0010 §X](0010-station-design-standard.md))
has spare load capacity in the bay between two PV panels.

## 6. Tier 2 explicitly out of scope

- **MCS (Megawatt Charging System).** Reviewed and rejected for
  Tier 2 because (a) it is a CCS-evolved connector intended for
  heavy-vehicle plug-in, requiring a heavy cable and an operator,
  which is incompatible with the GoA 4 architecture (no driver to
  plug in), and (b) the standardisation is recent (2024) — the
  installed base is too thin for a regional spares pipeline.
- **Inductive / wireless charging.** Per RFC 0021 §6.3.

## 7. Selection rule

```text
   archetype                Tier 1 (depot)   Tier 2 (terminal)
   ─────────────────        ───────────────  ──────────────────────
   halt                     —                —
   standard                 —                —
   major                    —                pantograph-down (alt)
   interchange              —                pantograph-down (alt)
   terminal                 —                side-pin (primary)
   depot-terminal           CCS2 (RFC 0021)  side-pin (primary)
```

`terminal` and `depot-terminal` carry a Tier 2 connector by default.
`major` and `interchange` carry it only when the line's operations
plan ([RFC 0013](0013-operations-rulebook.md)) requires opportunity
charging at that stop.

## 8. Cost impact (USD OECD-base, per Tier 2 site)

Rectifier sourced from tier-2 (TGOOD / Star Charge / Heliox), not
European tier-1 (ABB / Siemens). Tier-1 rectifiers list ~$400 k
for the same 1 MW class — see [RFC 0021](0021-battery-traction.md)
sourcing matrix.

| Item | Side-pin | Pantograph-down |
|---|---|---|
| Train-side connector + actuator | $40 k | $80 k (pantograph) |
| Platform-side bus-bar / overhead bar | $25 k | $35 k |
| Rectifier cabinet (1 MW, tier-2) | $250 k | $250 k |
| Civil + cabling | $80 k | $120 k |
| **Total per site** | **~$395 k** | **~$485 k** |

A 12-station line with 2 Tier 2 sites (one terminal, one
depot-terminal): **~$790 k side-pin** vs **~$970 k pantograph**.
Country-cost multipliers from
[`lib/templates/country-costs.toml`](../../lib/templates/country-costs.toml)
apply to civil + integration shares downstream.

## 9. Open questions

1. Side-pin actuator failure mode — what happens to a train that
   docks but cannot retract? Recovery procedure to be elaborated
   in RFC 0013.
2. Whether the side-pin can be the *only* charging path for a
   small deployment, removing CCS2 from the depot — simpler spares
   pipeline at the cost of one connector standard.
3. DC-link redundancy at Tier 2 — single cabinet vs N+1.

## 10. Revision history

| Date | Version | Change |
|---|---|---|
| 2026-04-26 | v0 | Stub. Two-tier architecture (CCS2 depot + side-pin/pantograph terminal), reconciles RFC 0010 ↔ RFC 0021 §6. |
