# Baghdad train and station electrical interfaces

The first-programme concept has six powered cars, 48 door openings, four shoe sets and two inverter control units per train. This design develops the wiring and software handover for one train arriving at a straight island platform. The equipment quantities come from the protected-conductor selection in the [Baghdad packet](../../system-results.json). Cabinet placement, circuit division and terminations below are proposals for quotation.

## Power distribution and mounting

| Assembly | Proposed arrangement and service boundary | Required evidence from the equipment supplier |
| --- | --- | --- |
| Wayside feeder and return | Grid protection cubicle feeds sectional DC switchgear. Section gateway mirrors local switch position, fault latch and access state to control. Provide accessible local isolation, test points and return continuity inspection at section limits. | Section single-line, both-direction feeds, backfeed through a train spanning a gap, bonding and stray-current study. Coordinate interruption and earthing with prospective fault current and feeder impedance. A gateway indication alone cannot establish an electrically safe worksite. |
| Train traction input | Four guarded shoe assemblies enter line-side isolation and fault protection. Divide converter controls into two supervised groups serving the 24 driven axles. Reserve disconnectable traction, control and bonding terminations at each removable bogie. | Supplier assigns shoes and axle modules to groups and shows cable lengths, routes, switching sequence, protective discrimination, converter cooling, lift clearance and safe stored-energy discharge. Assess one shoe unloaded, insulated gaps and a stalled train. |
| Essential service supply | Section-fed charger supplies the independent 65 kWh service battery. Two service power units feed separately protected control branches. Provide separate indication of battery contactor, charger available and downstream voltage at the brake/protection loads. | Quantify common failures at battery, transfer and return, cold restart, interruption on transfer, cell ageing, hot enclosure and repair isolation. Single-unit survival duty and cable voltage drop remain open. |
| Protection and communications | Allocate one protection channel and one radio to each train end. Separately label and route redundant power and signal looms through the inter-car connectors. Provide local test access and independent event timestamps. | Supply separation and common-cause analysis, power interruption limits, timebase, message age and train orientation handling. Prove command withdrawal at the inverter output and brake force at the wheel/rail interface. |
| Car I/O | Each car node serves eight door controllers and two bogie brake controllers. Put door motor protection and limit/lock terminals at each opening. Fit a labelled removable harness between each bogie and its car. | Return terminal plan, cable schedule by length and section, connector keys, earth straps, supports, ingress protection and clearance for withdrawal. Document reconnection and reversed-car checks. |
| Station dispatch | Local dispatch cabinet receives the independently established berth, train identity, direction and platform side. Transmit a train-specific release request. Isolate dispatch, station building services and the maintenance network. | Demonstrate loss of a stop marker, reversed direction, stale IDs, loss of radio and emergency egress with a physically blocked route. Evidence must cover stopping tolerance and accessible boarding. |

The 1.5 kV sensitivity uses 5.004 MW per train and yields 3.707 kA at 90% line voltage. It sizes a study point. Feeder cable sections, shoe sharing, fault levels and breaker settings require the installed topology and duty traces. The control inventory allocates **299 kg and 3.68 kW per train**, including 45 kg for common harnesses and enclosures. Terminations, brackets, cooling and feeder protection need itemised takeoffs. Reconcile them against their parent scopes before adding prices or declaring the remaining 51 kg available. The two-hour service battery duty has only 1.6 kWh between nominal usable energy and the modelled requirement. [Vehicle duty and power allowances](../../VEHICLE.md)

### Provisional low-voltage cabinet load schedule

| Proposed grouping | Quantity/train | Equipment per group | kg/group | W/group |
| --- | ---: | --- | ---: | ---: |
| Train-end control group | 2 | One ATP channel, radio, service-power unit and inverter supervisor | 58 | 950 |
| Distributed car group | 6 | One car node, eight door controllers and two brake controllers | 21 | 280 |
| Contact equipment status | 4 | One monitored shoe set | 3 | 25 |
| Distributed installation allowance | 1 | Harness, connectors, brackets and enclosures | 45 | Losses unmeasured |

These groupings reconcile the equipment budget as 2 × 950 + 6 × 280 + 4 × 25 = 3,680 W. They allocate procurement responsibility across cabinets and door/bogie modules. Separate the actual dissipation of the service-power converters from power delivered to their loads before specifying ventilation. Request the load profile, startup current, source impedance, cable voltage drop and longest permissible interruption at each branch. Cooling losses and installed wiring resistance remain unmeasured. [Unit allowances](../../system.toml)

## Signal handover at an island berth

| Origin and receiver | Logical points and multiplicity on one train | Proposed treatment |
| --- | --- | --- |
| Station to onboard protection and doors | Verified station identity, train identity, consist orientation, side, berth proof and zero-speed proof | Reconcile physical side with direction before binding `verified_platform_side` and each installed `door_side`. Reject an unknown side. Reverse motion also inhibits motor-open. The door crate expects the upstream berth/identity proofs as inputs. |
| Door switchgear to car node | 48 closed limits, 48 lock switches, 48 open limits, 48 obstruction indications and 48 motor-current values | Keep a fixed slot for every installed opening. Send sequence, timestamp and quality with each status. Suppress departure during a release request even if sensors momentarily still show locked. A silent slot invalidates the aggregate lock proof. |
| Car nodes to train protection | Six car summaries, twelve bogie brake controllers, two traction-controller reports and four shoe reports | Return individual fault and freshness diagnostics. Shoe contact, section permission and isolation are separate proofs. A de-energised line may still have a closed service battery contactor. Prove physical isolation before maintenance access. |
| TCMS and ATP to torque/braking interfaces | One logical TCMS readiness and one ATP permissive in this replay | Require both and the departure command gate for torque. Route ATP mechanical-brake requests independently. At a secured berth retain parking and independent brake hold across door release. The replay requires starting-effort feedback before transferring the hold. Dual-channel arbitration and physical restart remain open. |
| Train/section to OCC | Train ID, time, berth, side, door aggregate, individual faults, traction inhibited, brake demand, section state and freshness | Publish as observations. The [gateway and FUXA](../../../../deployment/supervision/README.md) display and archive status. Define actual addresses, units, sequence checks, timeout budgets and gateway diagnostics in the vendor interface return. |

## Offline software replay

From a full checkout with Rust and the locked dependencies available, run

```sh
cargo run --locked --manifest-path cities/Baghdad/engineering/controls/Cargo.toml
```

The replay checks the source hashes in the Baghdad model result, reads its first-programme physical candidate and evaluation IDs, verifies the selected conductor case and reconciles the car and door count. It exercises the repository's [door evaluator](../../../../crates/osr-door-control/src/lib.rs), [protected-conductor TCMS](../../../../crates/osr-tcms/src/protected_conductor.rs) and [powered-wheel ATP adapter](../../../../crates/osr-atp/src/powered_wheel.rs) in the same process. The first twelve fixtures evaluate independent snapshots. Their assertions cover departure, release to either side, unknown station or side, reverse motion, a missing lock, a silent controller, isolation in motion, essential supply loss, mismatched train configuration and withdrawn authority.

The movement evaluator still demands emergency braking for one unlocked or missing door, including at standstill outside an authorised release. Section isolation in motion demands full service braking. The secured-berth evaluator shares the movement evaluator’s identity, authority, integrity, supply and independent brake checks. It keeps traction inhibited and parking hold requested while the authorised doors are unlocked. The replay prints the train identity, system evaluation and a separate SHA-256 station replay identity covering those IDs, the fixtures, direct evaluator sources and the replay lockfile.

### Boarding, departure and recovery

The [station supervisor](src/boarding.rs) carries 48 door states across a visit. A station request names the station, train, arrival, platform side and expected direction of departure and carries a timestamp and consecutive sequence number. All inputs and outputs in this replay are synthetic. The first and last moving samples use the ordinary ATP evaluator.

| At the train | Proof or command exercised | Result in the replay |
| --- | --- | --- |
| Approaching the platform | Inject an upstream service brake demand with the train moving at 8 m/s. | No traction permission. The next berth event requires zero speed, parking-applied feedback, a separate applied-hold feedback and inverter-inhibit feedback. |
| Releasing the doors | Bind the release to the current visit and verified platform side. Check every controller is present and all locks are initially made. | The 24 platform-side doors receive opening requests. The other 24 stay locked. During boarding, loss of an offside lock, motion or loss of a holding proof trips the supervisor. |
| Closing and proving the train | Keep both holds applied. Continue closing while the platform-side doors are in transit. Observe all 48 closed-limit and lock pairs in two consecutive fresh reports. | A late platform-side lock delays readiness. Lost proof after the first complete sample trips the supervisor. Torque stays inhibited until dispatch. |
| Taking the load | Accept a fresh dispatch with route, supply, lock, ATP and TCMS proofs. Permit the drive to develop starting effort against the retained hold. Independently observe starting effort in the addressed direction and removal of the inverter inhibit with both brakes still proved applied. | Issue one handover pulse. A missing effort acknowledgement retains the hold and eventually trips. Premature brake release or movement trips immediately. Retain starting effort while parking and independent hold release. Both release indications may arrive on separate samples at zero speed. |
| Departing | With both holds released, require continued starting effort across the last zero-speed sample. Observe the first nonzero speed in the direction bound to the visit. The fixtures exercise forward and reverse departures with opposite-sign rollback in both cases. | Loss of starting effort before motion, rollback or motion against an applied brake trips the sequence. An unlocked door demands emergency braking in either direction. Beyond the first moving sample, ongoing direction supervision belongs to upstream ATP. This fixture stops at handover. |
| Restarting or recovering from a trip | Require fresh healthy closed-and-locked feedback followed by an addressed local keyed reset. | The strongest brake demand remains latched until reset. Clearing a fault or turning the key alone cannot dispatch the train. |

The replay uses a 250 ms station message timeout and a 500 ms maximum interval from dispatch request to the first moving sample. These fixture settings and the two lock samples need measured timing budgets. The 35-second passenger dwell, actuator response, deployment on a gradient and stopping distances remain unverified. The bench supplies approach and departure speeds, brake health, applied brake, parking, torque-inhibit and starting-effort feedback. It does not derive these from wheel force, pressure, line current or train motion.

### Physical handover test

Use the X2 and X3 terminals below to record the parking-applied contact, pressure or force on the independent brake, inverter inhibit, actual starting effort and wheel motion on a synchronised recorder. Exercise the sequence on a representative brake, parking actuator and traction rig under the maximum proposed load and gradient. Delay brake build-up and drive acknowledgement independently, disconnect one feedback channel, and interrupt power during transfer. Verify continued hold and measure rollback, release sequencing and brake build-up against independently agreed limits. The repository has no as-tested hardware traces or approved limits for this candidate.

### Termination schedule for the bench

Terminal numbers below are proposed fixture labels for one representative opening and one train end. Use a second independently protected input path for channel B. Size contacts, conductors, fuses and insulation from the selected devices, installation lengths, fault energy, earthing arrangement and segregation drawing.

| Terminal group | Proposed terminations | What to verify |
| --- | --- | --- |
| Door module X1, one set/opening | 1–2 closed limit and return, 3–4 independent lock contact and return, 5–6 open limit and return, 7–8 obstruction input and return, 9–10 motor-current transducer pair | Bring individual signals to an accessible test plug. Verify an open lead, short between channels and lost controller address at the car summary. Repeat for each installed side and orientation. |
| Protection cabinet X2, one set/end | 1–2 local service supply after branch protection, 3–4 isolated downstream supply indication, 5–6 parking-applied proof, 7–8 mechanical-brake feedback | Record converter dropout and actual brake/parking feedback separately. A command bit is insufficient evidence that the vehicle is held. |
| Inverter and brake bench X3, one set/end | 1–2 traction-inhibit output to load simulator, 3–4 torque-inhibited return, 5–6 brake request to independent controller simulator, 7–8 brake-applied return | Instrument command and feedback independently. Determine final service-demand encoding, emergency trip circuit and dual-channel topology from the equipment design. Keep actuator energy on a separately isolated circuit during these tests. |
| Local reset and train link X4 | 1–2 local keyed reset contact, 3–4 input-loop supply and return. Terminate train data on a separate keyed connector. | Exercise wrong train, platform, arrival and sequence, future and stale timestamps, loss of the train link and loss of parking feedback. Confirm a key alone cannot initiate motion. |

## Factory and site returns

Issue a cabinet general arrangement, connector-to-connector wiring schedule, branch protection schedule, terminal labels, replaceable-unit list and versioned signal dictionary with each bid. Identify which enclosures, looms, software builds, test fixtures and depot repairs an Iraqi team can perform, the imported parts they depend on, and the rights and equipment needed to repeat each task.

On the bench, wire a real opening, car node, both protection inputs, brake load simulator and inverter inhibit feedback. Open and short each sensor lead, interrupt each supply, remove one communications channel and interrupt contact while moving in simulation. Capture hardware timestamps from stimulus through torque removal and brake build-up. Set the permitted times from the route stopping analysis. Then instrument gap traversal, regenerative or dissipative braking under unavailable line receptivity, enclosure temperature during repeated peak service, and safe access after isolation. Log serials, wiring revision, software hash, as-tested settings, calibrated measurements and independent review against the physical candidate.
