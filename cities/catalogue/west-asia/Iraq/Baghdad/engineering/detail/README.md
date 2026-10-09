# Baghdad detailed component register

Generated from the current city design, six-car profile, engineering parts and software/ERP contracts. Engineering release remains **false**. Cost and finance rates remain unchanged; unknown unit costs are open rather than zero.

Reference allocation: **772 trainsets**, **4,632 cars**, **9,264 bogies**, **186 stations**, **164 energy sites** and **one** shared plant.

See [complete parts CSV](parts.csv), [source-bound register](register.json), [dimensioned ST6 reference](slab-reference.svg) and [design and Iraqi manufacturing plan](../../DETAILED-ENGINEERING.md). The two-bogie-per-car allocation and repeated mechanical kit quantities are reference architecture, subject to Metro-6car family release. Nested wheelsets, clips and batteries are not extra charges on top of complete bought assemblies.

## Track and parts quantities

The rail reference covers net mainline running length only. Actual procurement additionally needs alignment method zones, switches, stabling, depot track and cutting/weld/spares schedules. Slab panel totals remain **unassigned** until constrained zones are measured; rail-seat child quantities require a seat installation schedule.

| ID | Part / assembly | Basis | Per basis | Network reference | Route |
|---|---|---|---:|---:|---|
| TR-01 | 60E1 reference running rail | route-km (m) | 4000 | 1,915,889.6 | import-or-qualified-local-source |
| TR-02 | Resilient direct-fixation complete seat kit | rail-seat (each) | 1 | Open | import-first-local-assembly-later |
| TR-03 | Elastic clips | rail-seat (each) | 2 | Open | import-qualified |
| TR-04 | Rail pad / bonded resilient layer | rail-seat (each) | 1 | Open | import-qualified |
| TR-05 | Lateral rail insulators | rail-seat (each) | 2 | Open | import-qualified |
| TR-06 | Anchor assembly including insert, bolt and washer | rail-seat (set) | 2 | Open | local-inserts-after-qualification |
| TR-07 | Vertical/lateral adjustment and levelling kit | rail-seat (set) | 1 | Open | local-machining-after-qualification |
| TR-08 | OSR-ST6 precast slab panel | slab-panel (each) | 1 | Open | Iraqi-precast |
| TR-09 | ST6 concrete, base and plinths only | slab-panel (m3) | 5.0796 | Open | Iraqi-batching |
| TR-10 | ST6 reinforcement planning allowance | slab-panel (kg) | 761.94 | Open | Iraqi-cage-fabrication |
| TR-11 | ST6 bedding / levelling grout | slab-panel (m3) | 0.522 | Open | local-qualified-material |
| TR-12 | ST6 lifting sockets / engineered anchors | slab-panel (each) | 4 | Open | import-qualified-local-install |
| TR-13 | Drainage channel and removable cover | route-km (m) | 2000 | 957,944.8 | Iraqi-precast |
| TR-14 | Rail electrical continuity bond / monitored stray-current provision | project (set) | Open | Open | local-harness-import-terminals |
| TR-15 | Turnout slab bearer, point drive, detection and locking kit | project (set) | Open | Open | mixed |
| TR-16 | Rail/deck expansion interface and transition section | project (set) | Open | Open | mixed |
| TR-17 | Utility ducts, draw pits, barriers and fencing | project (set) | Open | Open | Iraqi-manufacture |
| ME-01 | Underframe and load-bearing car structure | car (each) | 1 | 4,632 | Iraqi-fabrication |
| ME-02 | Modular FRP cladding, end frames and service rails | car (each) | 1 | 4,632 | Iraqi-composite-and-metalwork |
| ME-03 | Powered bogie complete including frame, suspension and brakes | car (each) | 1 | 4,632 | import-first |
| ME-04 | Trailer bogie complete including frame, suspension and brakes | car (each) | 1 | 4,632 | import-first |
| ME-05 | Wheelset including wheels, axle, bearings and axleboxes | bogie (each) | 2 | 18,528 | included-in-bogie-import |
| ME-06 | Motor and traction inverter/controller set | car (each) | 2 | 9,264 | import-qualified |
| ME-07 | 225 kWh nameplate traction battery allocation | car (each) | 1 | 4,632 | import-cells-local-pack-after-qualification |
| ME-08 | Battery support, HV junction box, fuse, contactors and precharge | car (each) | 1 | 4,632 | mixed |
| ME-09 | Battery/inverter liquid cooling loop | car (each) | 1 | 4,632 | local-assembly-import-pump-and-chiller |
| ME-10 | HV-to-LV DC/DC and battery-backed auxiliary distribution | car (each) | 1 | 4,632 | import-qualified-local-harness |
| ME-11 | HVAC unit, ducts, filters, condensate and mounts | car (each) | 1 | 4,632 | mixed |
| ME-12 | Passenger door package including leaves, drive, locks and detection | car (each) | 4 | 18,528 | import-qualified-local-fitting |
| ME-13 | Side glazing, window frames, seals and adhesives | car (each) | Open | Open | import-glass-local-frame |
| ME-14 | Intercar coupler, gangway, jumper and air/electrical interfaces | trainset (each) | 5 | 3,860 | mixed |
| ME-15 | Train-end recovery coupler and sensor cowl | trainset (each) | 2 | 1,544 | mixed |
| ME-16 | Brake supply/control and parking brake package | car (each) | 1 | 4,632 | mixed |
| ME-17 | Roof PV, MPPT, mounts and protected DC wiring | car (each) | 1 | 4,632 | import-panels-local-mounts |
| ME-18 | Interior, seats, grab rails, lighting and accessibility kit | car (each) | 1 | 4,632 | Iraqi-assembly |
| ME-19 | Fire detection, alarm, segregation and suppression provisions | car (each) | 1 | 4,632 | mixed |
| ME-20 | HV/LV/data harness, connector and clamp schedule | car (each) | 1 | 4,632 | Iraqi-harness-production |
| ME-21 | Service consumables, fasteners, fluids and replacement spares | project (each) | Open | Open | mixed |
| EL-01 | T-ECU/S end host assembly | trainset (each) | 2 | 1,544 | import-electronics-Iraqi-integration |
| EL-02 | T-ECU/A application end host assembly | trainset (each) | 2 | 1,544 | import-electronics-Iraqi-integration |
| EL-03 | T-OBS end host and external sensor assembly | trainset (each) | 2 | 1,544 | import-electronics-Iraqi-integration |
| EL-04 | Safety evaluator MCU channel | t-obs (each) | 2 | 3,088 | import-electronics-Iraqi-integration |
| EL-05 | Independent hardware heartbeat watchdog | t-obs (each) | 2 | 3,088 | import-electronics-Iraqi-integration |
| EL-06 | Channel power conversion and voltage monitoring branch | t-obs (each) | 2 | 3,088 | import-electronics-Iraqi-integration |
| EL-07 | Application compute module and carrier | t-obs (each) | 1 | 1,544 | import-electronics-Iraqi-integration |
| EL-08 | Radar evaluation assembly and CAN interface adapter | t-obs (each) | 1 | 1,544 | import-electronics-Iraqi-integration |
| EL-09 | Lidar HAP TX candidate and data/power harness | t-obs (each) | 1 | 1,544 | import-electronics-Iraqi-integration |
| EL-10 | Stereo camera, carrier-compatible flex and rigid calibration bar | t-obs (each) | 2 | 3,088 | import-electronics-Iraqi-integration |
| EL-11 | Ultrasonic sensing position | t-obs (each) | 4 | 6,176 | import-electronics-Iraqi-integration |
| EL-12 | Isolated peer cross-check SPI link | t-obs (each) | 1 | 1,544 | import-electronics-Iraqi-integration |
| EL-13 | Hardware series permission contacts and independent coil drivers | t-obs (each) | 1 | 1,544 | import-electronics-Iraqi-integration |
| EL-14 | HV/LV input surge protection and branch fuse assemblies | t-obs (each) | 1 | 1,544 | import-electronics-Iraqi-integration |
| EL-15 | Enclosure, heat spreader, glands, vents and grounding hardware | t-obs (each) | 1 | 1,544 | import-electronics-Iraqi-integration |
| EL-16 | Train network switch, isolated CAN and external Ethernet controller set | trainset (each) | Open | Open | import-electronics-Iraqi-integration |
| EL-17 | Train-to-ground radios, modem carrier, antennas and surge arresters | trainset (each) | Open | Open | import-electronics-Iraqi-integration |
| EL-18 | W-SBC field cabinet and point/crossing I/O | project (each) | Open | Open | import-electronics-Iraqi-integration |
| EL-19 | S-SBC station host and protected UPS/network enclosure | station (each) | 1 | 186 | import-electronics-Iraqi-integration |
| EL-20 | Operator/server cluster, backup and disaster recovery | project (each) | Open | Open | import-electronics-Iraqi-integration |
| CI-01 | Pi20/Pi25 beam, pier cap, column and foundation package | project (each) | Open | Open | Iraqi-precast-and-site |
| CI-02 | Walkway, barrier, cable tray and access cassette | project (each) | Open | Open | Iraqi-fabrication |
| CI-03 | Station accessible platform, ramp/lift/stair and canopy package | station (each) | 1 | 186 | Iraqi-civil-and-metalwork |
| CI-04 | Station fire, water, drainage, power and earthing services | station (each) | 1 | 186 | mixed |
| CI-05 | Ticket validators, vending, gates and settlement terminals | station (each) | Open | Open | mixed |
| CI-06 | Station PA/PIS, CCTV, help points and telecom cabinet | station (each) | 1 | 186 | mixed |
| CI-07 | Charging contact, interlock, protection, DC/DC and site battery | site (each) | 1 | 164 | import-core-local-assembly |
| CI-08 | Depot lifts, pits, wheel service, wash and recovery equipment | project (each) | Open | Open | mixed |
| CI-09 | Precast plant moulds, cage jigs, batch/curing and survey tools | plant (each) | 1 | 1 | Iraqi-fabrication-import-special-tooling |
| CI-10 | Rail weld/clip/anchor tools and track survey trolley | plant (each) | 1 | 1 | mixed |
| CI-11 | Electrical bench, harness formboards and EMC/environmental test access | plant (each) | 1 | 1 | mixed |

## Corrected onboard power envelope

T-OBS simultaneous output allocation is **71.50 W**; at 90% efficiency, input is **79.44 W**. A 25% sizing margin requires **99.31 W**, selecting a **100 W reference capacity**. At the assumed 18 V minimum input, envelope current is **4.41 A**, or **5.52 A** including capacity margin. These are capacity assumptions, not energy-consumption measurements or qualified fuse/converter ratings.

## Software host allocation

All **60** workspace packages have exactly one disposition record. This verifies inventory, not physical HAL, sensor driver, firmware timing or operational safety.

| Component | Disposition | Hosts |
|---|---|---|
| osr-afc | composed-service | s-sbc |
| osr-afc-backoffice | deployable-endpoint | o-srv |
| osr-alignment | shared-library | design-tooling |
| osr-analytics | deployable-endpoint | o-srv |
| osr-ato | composed-service | t-ecu-a |
| osr-atp | composed-service | t-ecu-s |
| osr-aux-power | composed-service | t-ecu-a |
| osr-balise | composed-service | w-sbc |
| osr-bms | composed-service | t-ecu-s |
| osr-brake | composed-service | t-ecu-s |
| osr-cbm-backend | deployable-endpoint | o-srv |
| osr-cbm-onboard | composed-service | t-ecu-a |
| osr-city-studio | tooling | design-tooling |
| osr-consensus | composed-service | w-sbc, o-srv |
| osr-core | shared-library | all |
| osr-crypto | shared-library | all |
| osr-derailment | composed-service | t-ecu-s |
| osr-design | tooling | design-tooling |
| osr-door-control | composed-service | t-ecu-s |
| osr-energy-site | composed-service | w-sbc |
| osr-event-recorder | composed-service | t-ecu-a |
| osr-fire-safety | composed-service | t-ecu-s |
| osr-gui-shared | shared-library | o-srv, simulation |
| osr-historian | deployable-endpoint | o-srv |
| osr-hot-axle | composed-service | t-ecu-a |
| osr-hot-axle-wayside | composed-service | w-sbc |
| osr-hvac | composed-service | t-ecu-a |
| osr-interlocking | composed-service | w-sbc |
| osr-intrusion-detect | composed-service | w-sbc |
| osr-level-crossing | composed-service | w-sbc |
| osr-lifecycle-identity | shared-library | o-srv, design-tooling |
| osr-lighting | composed-service | t-ecu-a |
| osr-obstacle-detect | composed-service | t-obs |
| osr-onboard-routing | composed-service | t-ecu-s |
| osr-passenger-assist | composed-service | t-ecu-a |
| osr-occ | deployable-endpoint | o-srv |
| osr-occ-gui | deployable-endpoint | o-srv |
| osr-odometry | composed-service | t-ecu-s |
| osr-pis-onboard | composed-service | t-ecu-a |
| osr-pis-station | composed-service | s-sbc |
| osr-proto | shared-library | all |
| osr-psd | composed-service | s-sbc |
| osr-ptp | shared-library | t-ecu-s, t-ecu-a, t-obs, w-sbc, s-sbc |
| osr-regen | composed-service | t-ecu-a |
| osr-routing | shared-library | o-srv, design-tooling |
| osr-safety-case | tooling | assurance-tooling |
| osr-secbus | shared-library | all |
| osr-selftest | deployable-endpoint | t-ecu-s, t-ecu-a, t-obs, w-sbc, s-sbc |
| osr-sim | simulation | simulation |
| osr-sim-gui | simulation | simulation |
| osr-station-scada | composed-service | s-sbc |
| osr-supervision-contract | shared-library | o-srv, simulation |
| osr-t2g | composed-service | t-ecu-a |
| osr-tcms | composed-service | t-ecu-a |
| osr-runtime | shared-library | design-tooling |
| osr-tcn | shared-library | t-ecu-s, t-ecu-a, t-obs |
| osr-traction | composed-service | t-ecu-s |
| osr-trainset-image | deployable-endpoint | t-ecu-s, t-ecu-a, t-obs |
| osr-tvm | composed-service | s-sbc |
| osr-wayside-points | composed-service | w-sbc |

## ERP coverage

Validated workflow contracts: assignment, budget, maintenance, manufacturing, quality, replenishment, service, training.

Enabled profile instances: training/city-induction. Other workflows exist in the app but require real deployment inputs before enablement. A valid reusable profile does not mean that production orders, maintenance assignments or capital budgets have been activated.

Profiles/templates only; legal company, physical bindings, approved schedules, suppliers, stock and production BOMs remain deployment-owned. Reference parts are not auto-created as live ERP Items.

Source hashes bind this report to its exact inputs. Rebuild with `.venv/bin/python engineering/baghdad_detail.py`; verify with `--check`.
