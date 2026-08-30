# Station assembly traveler — `interchange-elevated`

Generated from `lib/templates/stations.toml` and the canonical mechanical
platform/canopy geometry. This is an unsigned template; deployment survey,
engineering approvals, supplier documents, and inspector signatures are required.

## Configuration

| Parameter | Value |
|---|---:|
| `platform_count` | 4 |
| `platform_layout` | stacked |
| `platform_length_m` | 59.5 |
| `platform_l_units` | 80 |
| `at_grade_track_channel_count` | 0 |
| `at_grade_slab_panels` | 0 |
| `guideway_edge_modules` | 0 |
| `canopy_bays_per_platform` | 10 |
| `total_canopy_bays` | 40 |
| `platform_canopy_area_m2` | 1008.0 |
| `site_canopy_target_m2` | 3200.0 |
| `auxiliary_canopy_required_area_m2` | 2192.0 |
| `auxiliary_canopy_module_area_m2` | 187.0 |
| `auxiliary_canopy_module_count` | 12 |
| `auxiliary_canopy_installed_area_m2` | 2244.0 |
| `auxiliary_canopy_target_overbuild_m2` | 52.0 |
| `auxiliary_canopy_kwp` | 381.5 |
| `charging_power_kw` | 500 |
| `dwell_seconds` | 60 |
| `tpss_kva` | 1000 |
| `access_type` | elevated-transfer-concourse-with-pedestrian-overbridge |
| `turnout_count` | 0 |
| `turnout_tangent` | none |
| `turnout_total_length_m` | 0 |
| `turnout_switch_blade_length_m` | 0 |
| `turnout_sleeper_count` | 0 |
| `depot_archetype` | none |
| `depot_reference_stalls` | 0 |
| `depot_throat_turnouts` | 0 |

## `STN-CIV-SA100` — site, foundation, drainage, and track/depot interface works

Work cell: civil works.

### BOM release

| Engineering ID | Qty | Unit | Route | Maturity |
|---|---:|---|---|---|
| `STN-CIV-P030` | 238 | m | `MAKE` | `release-candidate` |
| `STN-CNP-P020` | 44 | column kit | `MAKE` | `release-candidate` |
| `STN-CNP-P070` | 26 | column kit | `MAKE` | `buildable-after-site-structural-release` |

### Work instructions

1. release survey, utilities, geotechnical report, drainage outfall, and temporary-works plan.
2. set out platform, track, canopy-column, cabinet, and access datums.
3. construct drainage, footing reinforcement, anchor templates, and concrete works.
4. cure, test, survey, and release foundations before precast or steel placement.

### Hold points

- [ ] survey/geotechnical release — inspector/signature/date: __________
- [ ] pre-pour inspection — inspector/signature/date: __________
- [ ] foundation and drainage survey — inspector/signature/date: __________

## `STN-PLT-SA200` — platform, guideway-channel, and boarding-edge assembly

Work cell: civil/platform construction.

### BOM release

| Engineering ID | Qty | Unit | Route | Maturity |
|---|---:|---|---|---|
| `STN-CIV-P010` | 80 | ea | `MAKE` | `release-candidate` |
| `STN-CIV-P020` | 4 | platform kit | `MAKE` | `release-candidate` |
| `STN-PLT-P010` | 238 | m | `SOURCE` | `release-candidate` |

### Work instructions

1. inspect delivery certificates, lifting points, and platform datum.
2. place elevated L-units on the released structure using the approved lifting plan.
3. install and survey guideway edge modules where required, maintaining the 350 mm platform-to-ToR datum.
4. grout bearing lands and complete non-critical closure pours.
5. install coping, tactile strip, warning line, and edge markers.
6. survey height, horizontal gap, straightness, crossfall, and egress width.

### Hold points

- [ ] first-unit placement — inspector/signature/date: __________
- [ ] grout/cure release — inspector/signature/date: __________
- [ ] boarding-interface survey — inspector/signature/date: __________

## `STN-CNP-SA300` — modular canopy, roof, and PV assembly

Work cell: steel erection and solar.

### BOM release

| Engineering ID | Qty | Unit | Route | Maturity |
|---|---:|---|---|---|
| `STN-CNP-P010` | 40 | bay kit | `MAKE` | `release-candidate` |
| `STN-CNP-P030` | 40 | ea | `BID` | `buildable-after-supplier-freeze` |
| `STN-CNP-P040` | 4 | platform kit | `BID` | `buildable-after-supplier-freeze` |
| `STN-CNP-P050` | 12 | 187 m2 module | `BID` | `buildable-after-supplier-and-structural-release` |
| `STN-CNP-P060` | 13 | shared frame | `MAKE` | `buildable-after-structural-calculation-and-drawing-release` |
| `STN-CNP-P080` | 2 | string group | `BID` | `buildable-after-electrical-and-supplier-freeze` |
| `STN-CNP-P090` | 12 | roof-bay kit | `SOURCE` | `buildable-after-site-and-supplier-freeze` |

### Work instructions

1. verify foundation/anchor survey and incoming galvanised-steel certificates.
2. erect columns, rafters, braces, and temporary stability system bay by bay.
3. complete structural bolt torque/marking and frame plumb survey.
4. lift and fasten factory roof panels using the released panel clamp plan.
5. connect PV strings, combiner, isolation, bonding, lightning protection, and downlinks.
6. erect auxiliary shared truss frames and roof bays to the released site layout, including drainage and safe-access systems.
7. complete roof water test and PV insulation/polarity/commissioning records.

### Hold points

- [ ] first portal plumb/torque — inspector/signature/date: __________
- [ ] structural frame release — inspector/signature/date: __________
- [ ] roof/PV electrical release — inspector/signature/date: __________

## `STN-MEP-SA400` — station mechanical, electrical, drainage-services, and fire assembly

Work cell: MEP installation.

### BOM release

| Engineering ID | Qty | Unit | Route | Maturity |
|---|---:|---|---|---|
| `STN-MEP-P010` | 1 | station kit | `MAKE` | `release-candidate` |
| `STN-MEP-P020` | 1 | station kit | `BID` | `buildable-after-supplier-freeze` |
| `STN-MEP-P030` | 80 | luminaire point | `SOURCE` | `release-candidate` |
| `STN-MEP-P040` | 1 | station kit | `SOURCE` | `release-candidate` |

### Work instructions

1. install and anchor the service cabinet after civil release.
2. install LV distribution, UPS, earthing, lighting, fire, and communications containment.
3. install charging/TPSS equipment only after supplier and utility release.
4. terminate, label, inspect, energise, and execute discipline test sheets.

### Hold points

- [ ] cabinet/plinth release — inspector/signature/date: __________
- [ ] electrical safe-to-energise — inspector/signature/date: __________
- [ ] MEP integrated test — inspector/signature/date: __________

## `STN-CHG-SA700` — station charging and traction-power interface assembly

Work cell: traction power and charging.

### BOM release

| Engineering ID | Qty | Unit | Route | Maturity |
|---|---:|---|---|---|
| `STN-CHG-P010` | 500 | kW installed | `BID` | `buildable-after-supplier-freeze` |
| `STN-CHG-P020` | 1000 | kVA installed | `BID` | `buildable-after-utility-and-supplier-freeze` |

### Work instructions

1. release utility, protection, vehicle-interface, and supplier drawings.
2. install charging cabinet, TPSS equipment, containment, earthing, and physical guards.
3. complete FAT record review, cable tests, protection injection, and safe energisation.
4. run vehicle alignment, handshake, charge, abort, isolation, and emergency-release tests.

### Hold points

- [ ] utility/supplier release — inspector/signature/date: __________
- [ ] safe-to-energise — inspector/signature/date: __________
- [ ] vehicle charging SAT — inspector/signature/date: __________

## `STN-PAX-SA500` — passenger systems, fare, information, security, and amenity assembly

Work cell: systems fit-out.

### BOM release

| Engineering ID | Qty | Unit | Route | Maturity |
|---|---:|---|---|---|
| `STN-PAX-P010` | 1 | ea | `SOURCE` | `release-candidate` |
| `STN-PAX-P020` | 8 | display point | `SOURCE` | `release-candidate` |
| `STN-PAX-P030` | 4 | platform kit | `BID` | `buildable-after-supplier-freeze` |
| `STN-PAX-P040` | 8 | lane/validator | `BID` | `buildable-after-supplier-freeze` |
| `STN-PAX-P050` | 4 | ea | `BID` | `buildable-after-supplier-freeze` |
| `STN-PAX-P060` | 4 | platform kit | `SOURCE` | `release-candidate` |
| `STN-PAX-P070` | 8 | lane plinth | `MAKE` | `release-candidate` |
| `STN-PAX-P080` | 4 | TVM plinth | `MAKE` | `release-candidate` |

### Work instructions

1. install the S-SBC from its controlled hardware BOM and record image/configuration hashes.
2. install fare, PIS, CCTV, PA, help-point, LAN, seating, and signage equipment.
3. verify accessible reach, circulation, sightlines, audio coverage, and emergency messages.
4. run station self-test and end-to-end OCC communications/alarms.

### Hold points

- [ ] control-electronics/configuration release — inspector/signature/date: __________
- [ ] accessibility walkdown — inspector/signature/date: __________
- [ ] station systems SAT — inspector/signature/date: __________

## `STN-ACC-SA600` — station access and vertical-circulation assembly

Work cell: access works.

### BOM release

| Engineering ID | Qty | Unit | Route | Maturity |
|---|---:|---|---|---|
| `STN-ACC-P010` | 1 | station kit | `MAKE` | `release-candidate` |
| `STN-ACC-P020` | 4 | core | `BID` | `buildable-after-site-and-supplier-freeze` |
| `STN-ACC-P030` | 2 | ea | `BID` | `buildable-after-site-and-supplier-freeze` |

### Work instructions

1. release pedestrian desire-line, boundary, road-crossing, and egress interfaces.
2. construct direct paths, kerbs, ramps, bridge/concourse, and step-free cores as applicable.
3. commission lifts, protected crossings, lighting, drainage, and emergency recall.
4. complete independent step-free and evacuation-route walkdowns.

### Hold points

- [ ] access geometry release — inspector/signature/date: __________
- [ ] vertical-circulation certification — inspector/signature/date: __________
- [ ] egress acceptance — inspector/signature/date: __________

## `STN-STATION-A900` — complete commissioned station

Work cell: station integration.

### BOM release

| Engineering ID | Qty | Unit | Route | Maturity |
|---|---:|---|---|---|
| `STN-CIV-SA100` | 1 | assembly | `RELEASED CHILD` | `traveler required` |
| `STN-PLT-SA200` | 1 | assembly | `RELEASED CHILD` | `traveler required` |
| `STN-CNP-SA300` | 1 | assembly | `RELEASED CHILD` | `traveler required` |
| `STN-MEP-SA400` | 1 | assembly | `RELEASED CHILD` | `traveler required` |
| `STN-CHG-SA700` | 1 | assembly | `RELEASED CHILD` | `traveler required` |
| `STN-PAX-SA500` | 1 | assembly | `RELEASED CHILD` | `traveler required` |
| `STN-ACC-SA600` | 1 | assembly | `RELEASED CHILD` | `traveler required` |

### Work instructions

1. confirm every child traveler, NCR, certificate, survey, and as-built drawing is closed.
2. perform integrated passenger-flow, accessibility, fire, power-loss, charging, and OCC tests.
3. compile asset register, spares, maintenance instructions, configuration baseline, and handover pack.

### Hold points

- [ ] construction completion — inspector/signature/date: __________
- [ ] integrated SAT — inspector/signature/date: __________
- [ ] operator/AOR handover — inspector/signature/date: __________

## Baseline exclusions and open release conditions

- platform screen doors are optional for light-metro-3car and are not included
- site survey, geotechnical design, utilities, permits, and stamped calculations remain deployment-specific
- auxiliary canopy requires deployment structural, foundation, drainage, egress, and electrical release

## Final signoff

| Role | Name | Date | Signature |
|---|---|---|---|
| Civil/AOR |  |  |  |
| MEP lead |  |  |  |
| Systems integrator |  |  |  |
| Quality/inspection |  |  |  |
| Operator acceptance |  |  |  |
