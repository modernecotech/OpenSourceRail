# Reusable Civil Type Release Register

> Status: **definition seed — not issued for fabrication or construction**.

This register reconciles every reusable type in the reference civil IFC with one accountable release lane. Planning/RFQ definition only. Fabrication or construction release requires project survey, geotechnical model, checked calculations, reinforcement/prestress design, supplier data, temporary-works design and signed engineering acceptance.

## Coverage

| Measure | Count |
|---|---:|
| ifc reusable types | 19 |
| ifc occurrences | 138 |
| civil owned types | 9 |
| controlled interface types | 10 |
| release packages | 6 |
| drawing definition briefs | 9 |
| tooling and gauge families | 17 |

## Type Register

| IFC type | Asset class | Occurrences | Release lane | Package | Drawing brief | Disposition |
|---|---|---:|---|---|---|---|
| `OSR-TYPE-0B5DD2286469` | `civil.trackform` | 2 | civil-structure-owned | `CIV-FRP-130` | `CIV-ATG-400` | long-panel transition/interface geometry |
| `OSR-TYPE-15CA3C9B2913` | `station.platform-interface` | 1 | station-interface | `CIV-INT-210` | `CIV-INT-510` | guideway edge and platform clearance interface |
| `OSR-TYPE-239C28547990` | `civil.station-deck-interface` | 1 | civil-structure-owned | `CIV-INT-200` | `CIV-INT-500` | coordination-only virtual deck interface; not a structural product |
| `OSR-TYPE-24181B037817` | `station.platform-interface` | 1 | station-interface | `CIV-INT-210` | `CIV-INT-510` | mirrored guideway edge and platform clearance interface |
| `OSR-TYPE-33216A9A4A24` | `civil.trackform` | 2 | civil-structure-owned | `CIV-FRP-130` | `CIV-ATG-400` | reusable at-grade slab envelope; project ground treatment |
| `OSR-TYPE-38460DD866EF` | `track.turnout` | 1 | track-supplier-interface | `CIV-INT-200` | `CIV-INT-500` | supplier turnout interface |
| `OSR-TYPE-3FD9673EF391` | `civil.pier-cap` | 9 | civil-structure-owned | `CIV-FRP-110` | `CIV-SUB-210` | reusable hollow/precast-shell cap definition |
| `OSR-TYPE-4891C9E3C493` | `station.solar-canopy` | 2 | station-interface | `CIV-INT-210` | `CIV-INT-510` | canopy clearance/load interface controlled by station package |
| `OSR-TYPE-6336CC3F3205` | `station.platform-interface` | 1 | station-interface | `CIV-INT-210` | `CIV-INT-510` | platform product interface controlled by station package |
| `OSR-TYPE-661239622B15` | `rolling-stock.trainset` | 2 | vehicle-envelope-interface | `CIV-INT-210` | `CIV-INT-510` | vehicle swept/envelope interface; not a civil product |
| `OSR-TYPE-7406FA0925A0` | `station.platform-interface` | 1 | station-interface | `CIV-INT-210` | `CIV-INT-510` | platform product interface controlled by station package |
| `OSR-TYPE-7BF63285B921` | `station.solar-canopy` | 2 | station-interface | `CIV-INT-210` | `CIV-INT-510` | canopy clearance/load interface controlled by station package |
| `OSR-TYPE-99A11C1DC30D` | `civil.pier-column` | 9 | civil-structure-owned | `CIV-FRP-110` | `CIV-SUB-200` | catalogue column envelope; project reinforcement and foundation |
| `OSR-TYPE-C966BC7372EC` | `civil.bearing` | 36 | civil-structure-owned | `CIV-FRP-120` | `CIV-BRG-300` | supplier-configured bearing and jacking interface |
| `OSR-TYPE-D36A7871D9B7` | `civil.decked-pi-beam` | 12 | civil-structure-owned | `CIV-FRP-100` | `CIV-SUP-100` | reusable precast product definition |
| `OSR-TYPE-D4376465ACD5` | `civil.trackform` | 12 | civil-structure-owned | `CIV-FRP-100` | `CIV-SUP-110` | reusable elevated deck/trackform definition |
| `OSR-TYPE-EACE63284F07` | `track.rail` | 8 | track-supplier-interface | `CIV-INT-200` | `CIV-INT-500` | supplier rail and fastening interface |
| `OSR-TYPE-F2832317E733` | `track.rail` | 24 | track-supplier-interface | `CIV-INT-200` | `CIV-INT-500` | supplier rail and fastening interface |
| `OSR-TYPE-FDB074324FD0` | `civil.walkway-cassette` | 12 | civil-structure-owned | `CIV-FRP-100` | `CIV-EGR-120` | reusable walkway cassette definition |

## Release Boundary

The hashes identify deterministic coordination geometry. They are not drawing revisions, certificates, approvals, or permission to build. A geometry change intentionally fails generation until its new type is classified.
