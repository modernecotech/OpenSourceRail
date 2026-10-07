# Station assembly traveler — `interchange-elevated`

Generated from `lib/templates/stations.toml` and the canonical mechanical
platform/canopy geometry. This is an unsigned template; deployment survey,
engineering approvals, supplier documents, and inspector signatures are required.

## Configuration

| Parameter | Value |
|---|---:|
| `platform_count` | 2 |
| `boarding_face_count` | 4 |
| `track_count` | 4 |
| `elevation` | elevated |
| `platform_width_m` | 8.0 |
| `layout_exception_reason` |  |
| `layout` | {'layout': 'stacked', 'elevation': 'elevated', 'platforms': ({'id': 'platform-1', 'level': 'platform-1', 'y_mm': 0.0, 'base_z_mm': 9000.0, 'width_mm': 8000.0}, {'id': 'platform-2', 'level': 'platform-2', 'y_mm': 0.0, 'base_z_mm': 17000.0, 'width_mm': 8000.0}), 'faces': ({'id': 'face-1', 'platform_id': 'platform-1', 'level': 'platform-1', 'platform_face_y_mm': -4000.0, 'track_centre_y_mm': -5500.0, 'boarding_z_mm': 9420.0, 'top_of_rail_z_mm': 9070.0, 'direction': 1, 'door_side': 'left', 'psd_side': 'left', 'static_vehicle_to_platform_gap_mm': 75.0, 'dynamic_envelope_review_margin_mm': 15.0}, {'id': 'face-2', 'platform_id': 'platform-1', 'level': 'platform-1', 'platform_face_y_mm': 4000.0, 'track_centre_y_mm': 5500.0, 'boarding_z_mm': 9420.0, 'top_of_rail_z_mm': 9070.0, 'direction': -1, 'door_side': 'left', 'psd_side': 'left', 'static_vehicle_to_platform_gap_mm': 75.0, 'dynamic_envelope_review_margin_mm': 15.0}, {'id': 'face-3', 'platform_id': 'platform-2', 'level': 'platform-2', 'platform_face_y_mm': -4000.0, 'track_centre_y_mm': -5500.0, 'boarding_z_mm': 17420.0, 'top_of_rail_z_mm': 17070.0, 'direction': 1, 'door_side': 'left', 'psd_side': 'left', 'static_vehicle_to_platform_gap_mm': 75.0, 'dynamic_envelope_review_margin_mm': 15.0}, {'id': 'face-4', 'platform_id': 'platform-2', 'level': 'platform-2', 'platform_face_y_mm': 4000.0, 'track_centre_y_mm': 5500.0, 'boarding_z_mm': 17420.0, 'top_of_rail_z_mm': 17070.0, 'direction': -1, 'door_side': 'left', 'psd_side': 'left', 'static_vehicle_to_platform_gap_mm': 75.0, 'dynamic_envelope_review_margin_mm': 15.0}), 'equipment': ({'id': 'platform-1-lift-1', 'kind': 'lift', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': -17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-1-lift-2', 'kind': 'lift', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': 17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-1-shaft-1', 'kind': 'shaft', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': -17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-1-shaft-2', 'kind': 'shaft', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': 17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-1-escalator-1', 'kind': 'escalator', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': -9750.0, 'y_mm': 0.0, 'width_mm': 1800, 'length_mm': 10000}, {'id': 'platform-1-escalator-2', 'kind': 'escalator', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': 9750.0, 'y_mm': 0.0, 'width_mm': 1800, 'length_mm': 10000}, {'id': 'platform-1-staircase-1', 'kind': 'staircase', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': -24250.0, 'y_mm': 0.0, 'width_mm': 3000, 'length_mm': 10000}, {'id': 'platform-1-staircase-2', 'kind': 'staircase', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': 24250.0, 'y_mm': 0.0, 'width_mm': 3000, 'length_mm': 10000}, {'id': 'platform-2-lift-1', 'kind': 'lift', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': -17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-2-lift-2', 'kind': 'lift', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': 17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-2-shaft-1', 'kind': 'shaft', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': -17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-2-shaft-2', 'kind': 'shaft', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': 17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-2-escalator-1', 'kind': 'escalator', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': -9750.0, 'y_mm': 0.0, 'width_mm': 1800, 'length_mm': 10000}, {'id': 'platform-2-escalator-2', 'kind': 'escalator', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': 9750.0, 'y_mm': 0.0, 'width_mm': 1800, 'length_mm': 10000}, {'id': 'platform-2-staircase-1', 'kind': 'staircase', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': -24250.0, 'y_mm': 0.0, 'width_mm': 3000, 'length_mm': 10000}, {'id': 'platform-2-staircase-2', 'kind': 'staircase', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': 24250.0, 'y_mm': 0.0, 'width_mm': 3000, 'length_mm': 10000}), 'entrances': ({'id': 'entrance-1', 'x_mm': -29750.0, 'y_mm': 0.0, 'level': 'street', 'connected_to': 'concourse', 'surveyed': False}, {'id': 'entrance-2', 'x_mm': 29750.0, 'y_mm': 0.0, 'level': 'street', 'connected_to': 'concourse', 'surveyed': False}), 'transfer_connections': ({'from_level': 'platform-1', 'to_level': 'platform-2', 'via': 'concourse-upper', 'qualification': 'unreleased'},), 'minimum_clear_width_mm': 2250.0, 'level_elevations_mm': {'street': 0.0, 'platform-1': 9420.0, 'platform-2': 17420.0, 'concourse': 4500.0, 'concourse-upper': 13000.0}, 'concourse_decks': ({'id': 'concourse', 'level': 'concourse', 'z_mm': 4500.0, 'x_mm': 0.0, 'y_mm': 0.0, 'length_mm': 59500.0, 'width_mm': 10000.0, 'thickness_mm': 350.0}, {'id': 'concourse-upper', 'level': 'concourse-upper', 'z_mm': 13000.0, 'x_mm': 0.0, 'y_mm': 0.0, 'length_mm': 59500.0, 'width_mm': 10000.0, 'thickness_mm': 350.0}), 'qualification': 'study-only-access-flow-egress-and-structure-unreleased', 'quantities': {'platform_count': 2, 'boarding_face_count': 4, 'track_count': 4, 'lift_count': 4, 'escalator_count': 4, 'staircase_count': 4, 'shaft_count': 4}, 'equipment_geometry_contained': True, 'street_access_accepted': False} |
| `levels_m` | [9.0, 17.0] |
| `elevated_height_m` | 9.0 |
| `access_equipment` | [{'id': 'platform-1-lift-1', 'kind': 'lift', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': -17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-1-lift-2', 'kind': 'lift', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': 17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-1-shaft-1', 'kind': 'shaft', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': -17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-1-shaft-2', 'kind': 'shaft', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': 17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-1-escalator-1', 'kind': 'escalator', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': -9750.0, 'y_mm': 0.0, 'width_mm': 1800, 'length_mm': 10000}, {'id': 'platform-1-escalator-2', 'kind': 'escalator', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': 9750.0, 'y_mm': 0.0, 'width_mm': 1800, 'length_mm': 10000}, {'id': 'platform-1-staircase-1', 'kind': 'staircase', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': -24250.0, 'y_mm': 0.0, 'width_mm': 3000, 'length_mm': 10000}, {'id': 'platform-1-staircase-2', 'kind': 'staircase', 'served_levels': ('street', 'concourse', 'platform-1'), 'x_mm': 24250.0, 'y_mm': 0.0, 'width_mm': 3000, 'length_mm': 10000}, {'id': 'platform-2-lift-1', 'kind': 'lift', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': -17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-2-lift-2', 'kind': 'lift', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': 17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-2-shaft-1', 'kind': 'shaft', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': -17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-2-shaft-2', 'kind': 'shaft', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': 17000.0, 'y_mm': 0.0, 'width_mm': 3500, 'length_mm': 3500}, {'id': 'platform-2-escalator-1', 'kind': 'escalator', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': -9750.0, 'y_mm': 0.0, 'width_mm': 1800, 'length_mm': 10000}, {'id': 'platform-2-escalator-2', 'kind': 'escalator', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': 9750.0, 'y_mm': 0.0, 'width_mm': 1800, 'length_mm': 10000}, {'id': 'platform-2-staircase-1', 'kind': 'staircase', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': -24250.0, 'y_mm': 0.0, 'width_mm': 3000, 'length_mm': 10000}, {'id': 'platform-2-staircase-2', 'kind': 'staircase', 'served_levels': ('platform-1', 'concourse-upper', 'platform-2'), 'x_mm': 24250.0, 'y_mm': 0.0, 'width_mm': 3000, 'length_mm': 10000}] |
| `entrances` | [{'id': 'entrance-1', 'x_mm': -29750.0, 'y_mm': 0.0, 'level': 'street', 'connected_to': 'concourse', 'surveyed': False}, {'id': 'entrance-2', 'x_mm': 29750.0, 'y_mm': 0.0, 'level': 'street', 'connected_to': 'concourse', 'surveyed': False}] |
| `minimum_clear_width_m` | 1.5 |
| `platform_layout` | stacked |
| `platform_length_m` | 59.5 |
| `platform_l_units` | 80 |
| `at_grade_track_channel_count` | 0 |
| `at_grade_slab_panels` | 0 |
| `guideway_edge_modules` | 0 |
| `canopy_bays_per_platform` | 10 |
| `total_canopy_bays` | 20 |
| `platform_canopy_area_m2` | 1104.0 |
| `site_canopy_target_m2` | 3200.0 |
| `auxiliary_canopy_required_area_m2` | 2096.0 |
| `auxiliary_canopy_module_area_m2` | 187.0 |
| `auxiliary_canopy_module_count` | 12 |
| `auxiliary_canopy_installed_area_m2` | 2244.0 |
| `auxiliary_canopy_target_overbuild_m2` | 148.0 |
| `auxiliary_canopy_kwp` | 381.5 |
| `charging_power_kw` | 500 |
| `dwell_seconds` | 60 |
| `tpss_kva` | 1000 |
| `access_type` | stacked-level-transfer-concourse |
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
| `STN-CNP-P020` | 22 | column kit | `MAKE` | `release-candidate` |
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
| `STN-CIV-P020` | 2 | platform kit | `MAKE` | `release-candidate` |
| `STN-CIV-P050` | 238 | m2 | `MAKE` | `study-only` |
| `STN-CIV-P060` | 238 | track m | `MAKE` | `study-only` |
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
| `STN-CNP-P010` | 20 | bay kit | `MAKE` | `release-candidate` |
| `STN-CNP-P030` | 20 | ea | `BID` | `buildable-after-supplier-freeze` |
| `STN-CNP-P040` | 2 | platform kit | `BID` | `buildable-after-supplier-freeze` |
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
| `STN-MEP-P030` | 40 | luminaire point | `SOURCE` | `release-candidate` |
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
| `STN-PAX-P020` | 4 | display point | `SOURCE` | `release-candidate` |
| `STN-PAX-P030` | 2 | platform kit | `BID` | `buildable-after-supplier-freeze` |
| `STN-PAX-P040` | 8 | lane/validator | `BID` | `buildable-after-supplier-freeze` |
| `STN-PAX-P050` | 4 | ea | `BID` | `buildable-after-supplier-freeze` |
| `STN-PAX-P060` | 2 | platform kit | `SOURCE` | `release-candidate` |
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
| `STN-ACC-P040` | 4 | ea | `BID` | `study-only` |
| `STN-ACC-P050` | 4 | ea | `BID` | `study-only` |
| `STN-ACC-P060` | 4 | ea | `BID` | `study-only` |

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
