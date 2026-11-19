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
| TCMS and ATP to torque/braking interfaces | One logical TCMS readiness and one ATP permissive in this replay | Require both and the departure command gate for torque. Route ATP mechanical-brake requests independently. At a standstill retain parking hold across door release. Normal station stop sequencing, dual-channel arbitration and restart require separate implementation and testing. |
| Train/section to OCC | Train ID, time, berth, side, door aggregate, individual faults, traction inhibited, brake demand, section state and freshness | Publish as observations. The [gateway and FUXA](../../../../deployment/supervision/README.md) display and archive status. Define actual addresses, units, sequence checks, timeout budgets and gateway diagnostics in the vendor interface return. |

## Offline software replay

From a full checkout with Rust and the locked dependencies available, run

```sh
cargo run --locked --manifest-path cities/Baghdad/engineering/controls/Cargo.toml
```

The replay checks the source hashes in the Baghdad model result, reads its first-programme physical candidate and evaluation IDs, verifies the selected conductor case and reconciles the car and door count. It exercises the repository's [door evaluator](../../../../crates/osr-door-control/src/lib.rs), [protected-conductor TCMS](../../../../crates/osr-tcms/src/protected_conductor.rs) and [powered-wheel ATP adapter](../../../../crates/osr-atp/src/powered_wheel.rs) in the same process. The first twelve fixtures evaluate independent snapshots. Their assertions cover departure, release to either side, unknown station or side, reverse motion, a missing lock, a silent controller, isolation in motion, essential supply loss, mismatched train configuration and withdrawn authority.

With healthy synthetic proofs, the island release gives 24 motor-open requests on the platform side and zero on the opposite side. Torque stays inhibited in the release tick even while every lock contact is still made. Removing one lock or one controller requests an emergency brake in the adapter. This includes an unlocked door at a normal station stop. The present adapter has no boarding mode. Prove the parking hold and define the brake transition and reset sequence before dispatch integration. Section isolation during motion requests full service braking. These snapshot fixtures inject an upstream ATP release. Its output describes software demand. The replay has no field outputs or movement-authority generator. Braking distance, actual side determination, stopping accuracy, message timing, voting, hot restart and actuator response require separate evidence.

### Boarding, recovery and departure

The [stationary supervisor](src/boarding.rs) carries all 48 door-controller states across events. Each new supervisor starts tripped and requires fresh healthy feedback and keyed reset. Each exchange names the station, train, visit and platform side, with a sequence number and timestamp. The fixture requires consecutive sequence numbers, a known berth, zero reported speed, parking feedback and a fresh packet. A local clock also withdraws dispatch readiness after silence. Its 250 ms timeout and two independent sample times for lock confirmation are bench parameters. Route stopping and measured communication budgets must determine field settings.

| Station event | Required feedback | Result |
| --- | --- | --- |
| Berth and request opening | Matching visit and side, parking brake applied, stopped, all door slots present and locked | Retain parking hold and issue opening requests to the 24 platform-side controllers. |
| Observe open feedback | The bench changes the 24 platform-side open limits and drops their locks | The unmodified ATP requests emergency braking. The supervisor latches this demand and withdraws normal dispatch. This reproduces a normal passenger stop reaching the current adapter's mismatch. |
| Recover and reset | Simulated local recovery supplies independent closed and locked feedback. Valid configuration, line and service supply, ATP release, parking proof, fresh addressed reset and a local key must all be present. | Return to secured. The strongest brake demand observed during the trip persists until this point. Reset alone cannot issue a dispatch pulse. Physical relocking and resetting the brake require local procedures. |
| Prove berth again, close, verify locks twice and request dispatch | Fresh events in order, all 48 lock/closed pairs present, TCMS and ATP both permissive and independent brake demand released | Issue one simulated handover pulse. A duplicate request trips the supervisor. The fixture ends at standstill. A cancelled opening in which all locks stayed made can complete the same close/prove/dispatch sequence without emergency recovery. |

The physical boarding case still needs a validated stationary mode and independent brake/parking handover before the planned 35-second dwell can be claimed. The replay preserves the ATP demand through door release, service braking, emergency braking and reset attempts. Key state, communication freshness, sensor feedback and the act of physically relocking the doors are synthetic. Restart persistence, independent clocks, voter architecture, automatic brake actuation, transfer of parking hold to traction on a grade and emergency evacuation remain engineering work.

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
