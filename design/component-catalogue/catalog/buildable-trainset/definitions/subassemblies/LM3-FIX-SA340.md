# LM3-FIX-SA340 — common service-rail, captive-fastener, and fixture-adapter installation

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | interior pre-fit and final assembly cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `concept` |

## Children

- `LM3-FIX-P010`
- `LM3-FIX-P020`
- `LM3-FIX-P030`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-FIX-SA340 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | common extruded aluminium passenger/service datum rail, supplier-controlled external component, calculated passenger-fixture saddle and adapter family |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze
- Inspection methods: child acceptance evidence review, rail datum survey, fastener-family audit, fixture load-evidence check, service/removal demonstration
- Tooling basis: FIX-LM3-FIX-SA340, KIT-LM3-FIX-SA340, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-FIX-P010` — OSR-RAIL-42 common ceiling, waist, and seat-zone service rail kit

- Placement zone: saloon interior, PRM aisle, ceiling, and service-panel zone
- Interfaces: `mechanical datum`
- Join classes: `service-rail-captive-fastener`
- Torque authority: released OSR small-component standard plus accepted hardware batch and calibrated-tool procedure
- Joint release status: `standard-hardware-release-required`
- Verification:
  - rail datum survey
  - end-deburr check
  - isolation/finish inspection
  - representative pull/slip test

### 2. `LM3-FIX-P020` — four-family captive fastener, floating nut, isolator, and access-fastener kit

- Placement zone: common OSR-RAIL-42 interior datum and keyed low-voltage service zone
- Interfaces: `mechanical datum`
- Join classes: `service-rail-captive-fastener`
- Torque authority: released OSR small-component standard plus accepted hardware batch and calibrated-tool procedure
- Joint release status: `standard-hardware-release-required`
- Verification:
  - supplier certificate
  - batch/finish trace
  - installed-grip gauge
  - locking and captive-part audit

### 3. `LM3-FIX-P030` — standard passenger-fixture saddle and equipment adapter kit

- Placement zone: common OSR-RAIL-42 interior datum and keyed low-voltage service zone
- Interfaces: `mechanical datum`
- Join classes: `service-rail-captive-fastener`
- Torque authority: released OSR small-component standard plus accepted hardware batch and calibrated-tool procedure
- Joint release status: `standard-hardware-release-required`
- Verification:
  - adapter gauge
  - fixture-specific load calculation
  - proof-load sample
  - egress and snag check


## Hold points

- rail datum survey
- fastener-family audit
- fixture load-evidence check
- service/removal demonstration

## Source references

- `small_components.py`
- `LM3-INT-230`
