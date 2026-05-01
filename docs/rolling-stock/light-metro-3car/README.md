# `light-metro-3car` shop-drawing package — v1 deliverable of RFC 0008

This directory holds the dimensioned specification for the
**light-metro-3car** trainset — the Samawah reference family per
[RFC 0003](../../rfcs/0003-samawah-reference-deployment.md) and the
default for populations 300 k – 1 M per [RFC 0008 §5](../../rfcs/0008-rolling-stock-reference-design.md#5-family-selection-policy).

This is the v1 deliverable: a **specification a domestic rolling-
stock fabricator can bid on** — dimensions, masses, interfaces,
sub-assembly tree, fabrication sequence, and a procurement BOM
skeleton. The design deliberately favours a modern low-capex
factory: COTS rail subsystems wherever possible, simple cut/bend/
weld fabrication for the primary frame, and composite non-structural
panels for sides, roof fairings, cabless cowls, and interior liners.
The v2 deliverable is the full CAD pack + detailed shop drawings per
EN 15085 weld classes, EN 45545 material certifications, and the
supplier installation drawings for selected COTS modules.

## Contents

| File | Scope |
|---|---|
| [`general-arrangement.md`](general-arrangement.md) | Overall envelope, gauge clearance, consist diagram, floor heights, door positions |
| [`fabrication-plan.md`](fabrication-plan.md) | Cut-bend-weld primary structure, composite cladding, COTS module installation sequence |
| [`bogie.md`](bogie.md) | 2-axle articulated bogie spec, wheel profile, suspension, brake mount |
| [`body.md`](body.md) | Welded steel underframe/spaceframe, composite side panels, end bulkheads, articulation joint |
| [`traction.md`](traction.md) | PMSM motor + SiC inverter + reduction gear, adhesion budget |
| [`interfaces.md`](interfaces.md) | Coupler, pantograph, platform gap, TCN-E connector, aux power |
| [`bom-skeleton.md`](bom-skeleton.md) | Procurement BOM lines (source-identified parts vs TBD) |
| [`compliance.md`](compliance.md) | Standards matrix: EN 15227, EN 45545, EN 14363, EN 50155, ISO 3095, EN 12299 |
| [`drawing-register.md`](drawing-register.md) | v2 drawing IDs, supplier documents, inspection evidence, release gates |

COTS passenger-facing modules are controlled by the supplier-neutral
envelope catalogue at
[`hardware/trainset-interiors/cots-catalogue.md`](../../../hardware/trainset-interiors/cots-catalogue.md).

## Reference envelope (from RFC 0008 §1)

| Parameter | Value |
|---|---|
| Cars | 3 (articulated) |
| Overall length (over sensor cowls / couplers) | 56.6 m |
| Tare mass | 102 t |
| Axle load (AW3 crush) | ≤ 14 t |
| Max speed | 25 m/s (90 km/h) |
| Seats | 60 longitudinal seats |
| Passenger capacity (AW2) | 330 (seated + standing) |
| Passenger capacity (AW3 crush) | 420 short-duration crush load |
| Onboard battery | 360 kWh Na-ion (120 kWh per self-contained car) |
| Peak onboard motor output | 1 800 kW |
| Floor height (above ToR) | Low-floor centre door zone; raised floor over standard bogies |
| Gauge | 1 435 mm (default) or 1 000 mm (variant) |

## What v1 does NOT include

- KiCad / MCAD / STEP files (v2).
- Detailed finite-element analysis (v3 — homologation phase).
- Paint-and-livery guidance (operator scope).
- Fire-load and smoke-extraction analysis for the battery bay
  (v2, paired with EN 45545-2 test campaign).

## How to execute this package

1. A fabricator reads [`general-arrangement.md`](general-arrangement.md)
   + [`interfaces.md`](interfaces.md) to size their production
   line tooling.
2. [`fabrication-plan.md`](fabrication-plan.md) defines the shop
   route: tube/plate cutting, press-brake bends, welding fixtures,
   composite bonding, and COTS module installation.
3. [`bom-skeleton.md`](bom-skeleton.md) gives the procurement team
   the source-identified parts (off-the-shelf commodity) and the
   TBD parts (where the fabricator bids on make-or-buy).
4. [`drawing-register.md`](drawing-register.md) turns the v2 CAD
   pack into controlled drawing IDs, supplier document requirements,
   and release gates.
5. [`compliance.md`](compliance.md) lists the test campaigns the
   type-approval needs; each is a separately-tendered scope with
   an accredited test house.
6. The v2 CAD pack (not yet produced) is the cut-list / NC code
   / welding-robot path artefact that goes on the shop floor.

## Licensing

v1 specification: CC-BY-SA 4.0.
v2 CAD + drawings: CERN-OHL-S v2, matching the hardware licensing
from [ARCHITECTURE.md §9](../../ARCHITECTURE.md#9-roadmap).
