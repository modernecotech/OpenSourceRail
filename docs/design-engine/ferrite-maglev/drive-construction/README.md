# Active support/guidance and station launch construction

This package develops the electrical path missing from the ideal-force train model. It is a provisional construction and purchasing design, with actual Rust current/commutation tests. It does not qualify a complete magnetic actuator or an installed controller.

## What actively holds and guides the train

Ferrite magnets supply bias flux. Attraction changes with gap and is not passively stable. Two measured lift gaps and two lateral measurements per cartridge feed local gap/position feedback. Car-level Rust allocation requests forces and moments; a calibrated gap/current/temperature/shared-flux map must turn these into winding-current requests. A local MCU samples current and controls each H-bridge. Semiconductor switches regulate coil current; they are electrical switches, not rotating traction motors.

There are 24 cartridge positions per car. This candidate adds one lift winding and two opposed guidance windings at each position. The two guidance windings form one series-opposed circuit: **72 physical coils and 48 independently controlled current circuits per car; 432 coils and 288 circuits per six-car train**. A physical magnetic design must establish that the proposed independent lift and lateral functions are achievable together.

The SBC handles supervision, car-level allocation and recording. Local MCU boards own the proposed 20 kHz current loop and 1 kHz local gap loop. Independent comparators, driver interlocks, watchdogs and segregated support power remain separate. Ordinary Linux scheduling is not a current-loop deadline guarantee. A lost supervisory computer must invoke an engineered local support/controlled-stop arrangement; zeroing an LSM command or stale PWM is not a levitation fallback.

## Support coil and power assembly

The compact coil candidate has 50 turns of 16 mm² rectangular copper, a 508 mm mean turn length, 120 x 80 mm inner clearance and 174 x 134 x 60 mm envelope. Each coil contains **3.641 kg copper**. Copper alone totals **262.2 kg/car** and **1573.1 kg/train**. These are child quantities within support equipment, not additional mass silently added to the existing vehicle allowance. Formers, insulation, yokes, drivers, harnesses and cooling remain additional quantities to close.

At the assumed 8 mm gap, 0.55 T bias and ideal two-gap circuit, the AW3 lift-current screen gives 47.49 A per lift circuit. These values derive from an ideal reluctance equation, not a measured PM module. The 96 V bus, 60 A continuous / 120 A pulse envelope and coil thermal screen are design candidates. The calculated current slew is checked against the allocator's old ideal 2 MN/s force slew; a current limit or a passed arithmetic screen does not establish closed-loop vehicle stability.

The **compact 60 mm pack passes the declared depth and packing screens**. The retained 85 mm/60-turn version fails cavity depth; the 35-turn version exceeds continuous current and the 20 kN pulse-current limit. Compact winding reduces copper but increases heat; it is a provisional construction choice without changing the operating vehicle's mass ledger. A 4 x 4 mm bare conductor is a starting forming reference for 16 mm²: enamel, bend radii, layer arrangement, leads, former and creepage still need actual drawings and winding trials. Material volume alone does not establish complete fit. Machine and inspect the former, wind with controlled tension and counted turns, join qualified leads, impregnate, fit temperature sensing and strain relief, then measure resistance, inductance, insulation, polarity, force and heating. Fixed capture, essential-load power and residual PM force after drive loss need separate qualification.

| Support variant | Turns | Copper mm² | Depth mm | Copper kg/train | AW3 lift copper W/car | Declared screens |
|---|---:|---:|---:|---:|---:|---|
| compact-primary | 50 | 16 | 60 | 1573.1 | 1947 | True |
| larger-pack | 60 | 20 | 85 | 2359.6 | 1298 | False |
| lower-turn | 35 | 25 | 60 | 1720.5 | 1780 | False |

## Launch / receive hardware

The current urban/suburban studies use **350 m powered station zones per direction**. The supplied 200 m proposal remains a separate 1 km benchmark; it is not substituted for the current corridor. At 250 mm pole pitch and 2.5 m cassette length, a face cassette contains 30 slots and 15 single-layer full-pitch coils, five per phase. The supplied winding schedule pairs every slot exactly once. Magnetic origins must be indexed to the 500 mm electrical wavelength.

Two fixed 175 m groups per direction require four independently controlled three-phase bridges per two-direction station. The primary counted bill is **560 face cassettes, 56 jointed 12.5 m sections and 8400 bar coils**. A section has five cassettes per face; it is not a separately switched converter. One-turn 350 mm² copper gives **39.514 t copper/station** before joints, terminals and production waste. The 200 m benchmark retains 320 face cassettes and 32 sections. More turns reduce required current but increase back-EMF and inductive voltage; the retained 1/2/4-turn and R/L/material alternatives show the actual trade-offs.

One long series group must carry its real phase current. Parallel branches with unequal magnetic overlap have unequal back-EMF and cannot be assumed to share current from one bridge. The study calculates each group's overlap, periodic flux linkage, phase current, dq voltage, copper heat and power identity on the exact 2 km/140 s and 5 km/375 s AW3 trajectories. Inductance is an explicit sensitivity, not a solved winding map. The suburban booster is outside this terminal-station bill and its nonzero powered demand is reported as omitted scope.

The corridor's **2400 V DC hypothesis exceeds a single 1700 V switch rating**. The purchasing envelope therefore counts a custom higher-voltage converter, with semiconductor class, parallel positions and isolated gate/protection assemblies explicit. The cited catalogue drives are integration references, not selected 2400 V products. Before ordering, establish transient blocking, current sharing, SOA, diode/recovery, switch losses, cooling, creepage/clearance and fault isolation.

The common DC system needs rectification/supply conversion, protected film-capacitor banks, precharge, fuses/isolators, discharge, insulation monitoring and independently available braking sinks. Receiving requires the resistor/chopper ready even when no other train can absorb energy. Capacitor energy and MW braking duty are not interchangeable; a small DC link cannot absorb a complete arrival. Services charging is a separately rated load. No train battery or grid saving is credited merely through common-bus energy exchange.

For the urban trajectory, the loss-free arrival envelope is 1.584 MW and 14.322 MJ per train. Each independent resistor path must retain that event rating; two simultaneous arrivals require 3.169 MW common-bus handling. Four proposed 20 mF banks provide only 29.7 kJ between 2400 and 2550 V, equivalent to 9.37 ms at the two-arrival peak. That does not establish protection clearing or an energy sink. The study retains suburban duties too; grid sizing must include winding losses, conversion, charging and diversity without assuming a receptive departing train.

### Winding alternatives on the exact current trajectories

Here L is the one-turn whole-group assumption, scaled by turns squared. Voltage is phase peak against the 1316 V modulation screen. These are fixed-group electrical screens, not motor acceptance; failed alternatives remain visible. Terminal observations are two departure groups and two arrival groups, not simultaneous operation of four directions. Midway booster equipment requires its own quantities.

| Duty | Turns | One-turn L (µH) | Peak phase A | Peak phase V | Terminal copper kWh | Current/voltage screen |
|---|---:|---:|---:|---:|---:|---|
| urban | 1 | 25 | 3919 | 1211 | 7.18 | True |
| urban | 1 | 150 | 3919 | 1213 | 7.18 | True |
| urban | 1 | 1500 | 3919 | 1392 | 7.18 | False |
| urban | 2 | 25 | 1960 | 2302 | 3.59 | False |
| urban | 2 | 150 | 1960 | 2304 | 3.59 | False |
| urban | 2 | 1500 | 1960 | 2670 | 3.59 | False |
| urban | 4 | 25 | 980 | 4535 | 1.80 | False |
| urban | 4 | 150 | 980 | 4536 | 1.80 | False |
| urban | 4 | 1500 | 980 | 5227 | 1.80 | False |
| suburban | 1 | 25 | 1941 | 1304 | 5.04 | True |
| suburban | 1 | 150 | 1941 | 1304 | 5.04 | True |
| suburban | 1 | 1500 | 1941 | 1310 | 5.04 | True |
| suburban | 2 | 25 | 971 | 2607 | 2.52 | False |
| suburban | 2 | 150 | 971 | 2607 | 2.52 | False |
| suburban | 2 | 1500 | 971 | 2607 | 2.52 | False |
| suburban | 4 | 25 | 485 | 5214 | 1.26 | False |
| suburban | 4 | 150 | 485 | 5214 | 1.26 | False |
| suburban | 4 | 1500 | 485 | 5213 | 1.26 | False |

## Software and evidence

`crates/osr-maglev-control/src/drives.rs` supplies allocation-free bipolar PI, Clarke/Park transforms, bounded dq current regulation, phase uncertainty admission, average-voltage duty calculation, anti-windup and latched sensor/current/time/temperature/bus/authority/receiver faults. It compares dual current chains and checks three-phase current residuals. Reset needs fresh healthy, stopped/secured, zero-demand inputs. A wayside fault never requests onboard support shutdown. These Boolean facts still need authenticated physical sources.

Actual execution: three 4000-frame current-tracking runs and fourteen adverse controls, plus nine Rust regression tests. The independent RL/alpha-beta plant uses a standard-library trigonometric oracle. The 40 A commutation coupon is **not the multi-kA station converter**. Neither that RL plant nor the assumed reluctance screen has been substituted into the moving rigid-car/beam model. Rust hardware adapters, ADC timing, PWM/deadtime, protection trip timing, HIL and magnetic/load rigs remain required.

```sh
./osr design drives
cargo test --locked -p osr-maglev-control --test drives
cargo run --locked -p osr-maglev-control --example winding_replay
```

## Construction BOM

Quantities are purchasing families, not released PCB components. Parents and material children overlap; do not sum them as separate mass. Quoted prices and confirmed origins remain null/unconfirmed. Local assembly, winding, copper forming, cabinets, wiring, Rust and test processes are candidates; semiconductor and sensor origins retain their real imported content.

| ID | Construction / purchasing item | Per car | Per six-car train | Per two-direction station |
|---|---|---:|---:|---:|
| SUP-COIL | 50-turn rectangular copper coil: one lift and two opposed guide coils/module | 72 | 432 | 0 |
| SUP-COPPER | Bare copper conductor; material inside SUP-COIL, not extra mass | 1828.8 | 10972.8 | 0 |
| SUP-FORMER | Insulating former, interlayer insulation and impregnation kit | 72 | 432 | 0 |
| SUP-YOKE | Lift/guide pole and return-path assembly; new magnetic fit unresolved | 24 | 144 | 0 |
| SUP-BRIDGE | 96 V bipolar full H-bridge current circuit | 48 | 288 | 0 |
| SUP-SWITCH | 200 V-class MOSFET position; exact die/parallel count requires SOA and layout | 192 | 1152 | 0 |
| SUP-GATE | Dual isolated gate-driver IC; gate peak amps are not winding amps | 96 | 576 | 0 |
| SUP-GATE-SUPPLY | Isolated driver power domain; two per H-bridge | 96 | 576 | 0 |
| SUP-HALL | Isolated primary current measurement | 48 | 288 | 0 |
| SUP-SHUNT | Independent shunt/isolated conversion measurement | 48 | 288 | 0 |
| SUP-GAP | Two lift and two lateral gap chains/module; exact full-range probe unselected | 96 | 576 | 0 |
| SUP-MCU | Local acquisition/current/gap controller board, not complete released PCB | 24 | 144 | 0 |
| SUP-TRIP | Independent comparator/watchdog/latched driver-disable network | 24 | 144 | 0 |
| SUP-TEMP | One embedded temperature sensor per physical coil | 72 | 432 | 0 |
| SUP-PROTECTION | Local fused branch, DC capacitor, clamp and discharge kit | 24 | 144 | 0 |
| SUP-ZONE | Six-module isolated-power/protection/cooling distribution zone | 4 | 24 | 0 |
| SUP-SBC | SBC supervisor per car, excluding one train standby | 1 | 6 | 0 |
| SUP-STANDBY | Train supervisory standby, not a proven automatic transfer | 0 | 1 | 0 |
| SUP-NETWORK | Segregated local control link and supervisory network harness | 1 | 6 | 0 |
| SUP-COOLING | Coldplate, insulated mounts, coolant/air fittings and service connections | 24 | 144 | 0 |
| SUP-INDEPENDENT-POWER | Independent support/capture power path; capacity not sized by copper alone | 0 | 1 | 0 |
| LSM-CASSETTE | 2.5 m face cassette with 30 slots and 15 full-pitch coils | 0 | 0 | 560 |
| LSM-COIL | One-turn 350 mm2 copper bar coil; N alternatives retained | 0 | 0 | 8400 |
| LSM-COPPER | Bare bar length inside LSM-COIL; no second copper-mass credit | 0 | 0 | 12600.0 |
| LSM-INSULATION | Slot liner, phase separator, former, potting and stress-relief kit | 0 | 0 | 560 |
| LSM-CONNECTION | Phase terminals and indexed series links; creepage/clearance unqualified | 0 | 0 | 560 |
| LSM-BRIDGE | Custom 3-phase 2400 V DC group converter; not a catalogue drive rating | 0 | 0 | 4 |
| LSM-IGBT | 3.3 kV-class single-switch modules, 4 parallel/position, 6 positions/group; unselected | 0 | 0 | 96 |
| LSM-DRIVER | Module-specific isolated gate/protection assembly | 0 | 0 | 96 |
| LSM-CURRENT | Two independent chains for each of three group phase currents | 0 | 0 | 24 |
| LSM-LOCAL-MCU | Per-group local sensored dq/current controller | 0 | 0 | 4 |
| LSM-POSITION | Independent position/phase reference chains per direction; outdoor hardware unselected | 0 | 0 | 4 |
| LSM-DC-VOLTAGE | Dual independent DC sensing chains per group | 0 | 0 | 8 |
| LSM-DC-CAP | Per-group assumed 20 mF film-capacitor bank; ripple/fault design open | 0 | 0 | 4 |
| LSM-DC-PROTECTION | Precharge, isolators, fuses, discharge, IMD and protection coordination | 0 | 0 | 1 |
| LSM-RESISTOR | Independent braking chopper/resistor path per direction; common-bus losses not sole sink | 0 | 0 | 2 |
| LSM-SUPPLY | Transformer, supply converter and supply protection; rated grid study required | 0 | 0 | 1 |
| LSM-CHARGE | Separately rated train services charger/interface per direction | 0 | 0 | 2 |
| LSM-SBC | Station supervision and standby; field authority remains a separate function | 0 | 0 | 2 |
| LSM-THERMAL | Group liquid cooling, earth bonding, cabinet and field harness | 0 | 0 | 4 |

## British manufacture and specialist references

Primary sources checked 2026-10-22. UK capability does not establish the origin of a particular order. No supplier has quoted or endorsed this railway design.

- [Raspberry Pi 5 / Sony Pencoed](https://www.sonypencoed.co.uk/the-latest-raspberry-pi-5-rolls-off-production-lines-at-sony-uk-tec/): SBC supervisor and logging reference; no PWM or sole support protection. Origin: UK manufacture documented for Raspberry Pi 5; exact order origin to confirm.
- [Rotary Engineering W10/W20/W30 family](https://www.rotary.co.uk/equipment-details/coil-winding-machines/): Factory winding-machine candidates; 4x4 mm compact support conductor and 5x4 mm comparison require specific tooling trials. Origin: Designed and manufactured in Sheffield per supplier; European-origin motors disclosed.
- [Nidec Drives / Unidrive M700](https://moen.nidec.com/en/drives/Products/High-Performance-Drives/Unidrive-M700): Common-DC/linear-motor industrial reference; catalogue voltage does not qualify the 2400 V hypothesis. Origin: UK manufacturing capability in Newtown; exact drive/configuration origin unconfirmed.
- [API Capacitors](https://www.api-capacitors.com/): Custom DC-link film-capacitor bank candidate. Origin: UK design/manufacturing capability documented; exact capacitor origin requires quote.
- [Cressall](https://www.cressall.com/company/all-about-cressall-resistors/): Custom pulse/repetitive-duty brake resistor and load-bank candidate. Origin: UK manufacturing capability; exact resistor build and input origins unconfirmed.
- [ST STM32G474](https://www.st.com/en/microcontrollers-microprocessors/stm32g474mb.html): Local current/PWM acquisition MCU reference, Rust no_std kernel target. Origin: Imported semiconductor; assembly/test country unconfirmed.
- [TI UCC21520](https://www.ti.com/product/UCC21520): 96 V support H-bridge dual isolated gate-driver reference. Origin: Imported semiconductor; origin unconfirmed.
- [Infineon 3.3 kV IGBT module class](https://www.infineon.com/product-table/igbt-modules): Custom high-voltage launch bridge design envelope; exact module and sharing/SOA remain open. Origin: Imported power semiconductor; exact origin unconfirmed.
- [Micro-Epsilon eddyNCDT 3300](https://www.micro-epsilon.com/fileadmin/download/manuals/man--eddyNCDT-3300--en.pdf): Bench gap-sensor reference; range/start offset and steel/field/temperature calibration require selection. Origin: UK supply available; UK manufacture not evidenced.
- [TI sensored FOC reference](https://www.ti.com/lit/pdf/tidub03): Independent current-control architecture reference. Origin: Technical reference; no purchasing or local-content credit.

## Verification and release gates

The [full study](study.json.gz), [executed output](execution.json.gz), [BOM](bom.csv), [winding schedule](winding-schedule.csv), [connections](connections.csv) and [source receipt](manifest.json) retain exact inputs and results. The [architecture](architecture.svg) and [construction drawing](construction.svg) are generated from this package. Verification repeats the Rust execution and independently recomputes the quantities and screens; rehashed altered results are rejected.

- PM support needs active gap/guidance correction; permanent magnets do not provide qualified passive stability or a guaranteed safe residual after power loss.
- SBC supervision, local fast MCU current/gap loops and independent protection are different responsibilities. No hardware adapter, gate drive, target timing or authenticated field transport is implemented.
- Support reluctance/force and LSM fundamental flux/R/L are explicit hypotheses. Saturation, shared flux, end effects, normal-force disturbance, eddy losses, temperature and demagnetisation require measured maps.
- The local current-loop RL coupons are separate from the retained ideal-force moving train. No actuator-lag stability or complete electromagnetic/vehicle integration is claimed.
- The compact coil passes declared volume/depth screens only; conductor routing, insulation, lead exits, magnetic steel, clearances, fastening and cooling remain open. The larger rejected pack is retained.
- Long fixed groups need multi-kA bridges and voltage/inductance confirmation. Parallel unequal-back-EMF branches are not accepted as a free current reduction.
- The 2400 V corridor bus cannot use a lone 1700 V device as a two-level switch. Catalog industrial drives and the 40 A software coupon do not qualify a full station converter.
- Station supply, protection coordination, fault clearing, chopper/resistor redundancy, EMC, fire, cooling and physical acceptance remain open.
- All quantities are purchasing/construction candidates, not a released PCB/Gerber or production drawing set. Unit quotations, complete installed cost and local-value percentages remain unknown.

All engineering/physical release flags remain false. No city cost, mass, headway or hardware acceptance is promoted.
