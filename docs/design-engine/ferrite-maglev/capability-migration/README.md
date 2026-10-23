# v0.4 capability migration to station-powered maglev

Migration of the actual v0.4 feature table. Tested scope is stated per row; missing features are not marked complete.

Baseline: v0.4.0 commit `205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e`, README feature table. Historical product quantities and wheelset geometry are not current inputs.

| Capability | Disposition | Accountable function | Current evidence and limits |
|---|---|---|---|
| Deterministic city generation | retained-and-tested | City planning | Current266city planning; former route editor is not restored. [cities.py](../../../../engineering/ferrite_maglev/cities.py) |
| Generatable project digital twin | replaced | Delivery engineering | Pilot resource schedule, procurement and monthly cash replace the old delivery model; catalogue-wide ERP twins remain open. [delivery_schedule.py](../../../../engineering/ferrite_maglev/delivery_schedule.py) |
| Integrated Workbench | retained-but-unconnected | Platform integration | Current evidence review plus isolated native pilot; full former GIS/OCC/HR navigation is unconnected. [maglev-workbench.py](../../../../tools/automation/maglev-workbench.py) |
| Business execution and embedded maintenance | retained-and-tested | Owner/operator platform | Test scope is serial cartridge and beam simulation in native ERPNext/FUXA; entire-city HR/accounts and evaluator bindings remain open. [pilot_lifecycle.py](../../../../engineering/ferrite_maglev/pilot_lifecycle.py) |
| Interactive network and service planning | missing | GIS and transport planning | The current front door is read-only; the former16layer editor and OD revision UI are absent. [cities.py](../../../../engineering/ferrite_maglev/cities.py) |
| Software in the loop | replaced | Control integration | Current Rust support/current/launch loops and bounded plant replace wheel-specific interfaces; physical plant validation stays open. [pilot_actuators.py](../../../../engineering/ferrite_maglev/pilot_actuators.py) |
| Independent operations cross-check | missing | Operations modelling | Independent SUMO timing cross-check is not migrated; Rust/Python comparisons are not SUMO evidence. [pilot_corridor.py](../../../../engineering/ferrite_maglev/pilot_corridor.py) |
| Civil BIM, GIS and field evidence | retained-but-unconnected | Civil information management | Current plans retain geography; complete IFC4.3/IDS/BCF and field acceptance federation is unconnected. [cities.py](../../../../engineering/ferrite_maglev/cities.py) |
| Station and civil product geometry | replaced | Station and civil engineering | Current guidebeam/hub definitions replace old platform and bogie-change products; all45former families are not reproduced. [shared_hub_layout.py](../../../../engineering/ferrite_maglev/shared_hub_layout.py); [pilot_product.py](../../../../engineering/ferrite_maglev/pilot_product.py) |
| Station engineering screens | replaced | Station engineering | Current structural/access screens replace old benchmarks; complete fire/drainage/thermal qualification remains open. [station_native.py](../../../../engineering/ferrite_maglev/station_native.py); [hub_access.py](../../../../engineering/ferrite_maglev/hub_access.py) |
| Buildable modular trainset | replaced | Mechanical product engineering | Current composite body and magnetic bays replace the [historical wheel/traction product](https://github.com/modernecotech/OpenSourceRail/blob/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/README.md); stock geometry is not a manufactured train release. [assembled_body.py](../../../../engineering/ferrite_maglev/assembled_body.py); [pilot_product.py](../../../../engineering/ferrite_maglev/pilot_product.py) |
| Automatic cost propagation | replaced | Project economics | Pilot quantities and computed launch losses feed cash/revenue/debt sensitivities; catalogue allowances retain their separate identity. [delivery_schedule.py](../../../../engineering/ferrite_maglev/delivery_schedule.py); [launch_optimisation.py](../../../../engineering/ferrite_maglev/launch_optimisation.py) |
| Operations and assurance | retained-and-tested | Independent assurance | Executed authority and maglev refusal properties are source-bound; they do not provide physical or operational acceptance. [pilot_assurance.py](../../../../engineering/ferrite_maglev/pilot_assurance.py) |
| Deterministic integrated testing | replaced | Platform verification | Current disposable native scenario exercises ERPNext/FUXA/Workbench with faults/recovery; broad former editor coverage is not restored. [pilot-lifecycle-native.py](../../../../tools/automation/pilot-lifecycle-native.py) |

## Three products

**Owner/builder/operator delivery platform** — Planning, procurement, simulated QA/serial execution, evidence and maintenance with business-owned permissions. Controlled pilot planning and training before rolling-stock certification; no movement authority.

**Reference hardware and factories** — Mechanical/civil candidates, methods, origin-accounted suppliers, QA and serial definitions. Digital pilot kits for review and supplier engagement; manufacture requires independent release.

**Open GOA4 control platform** — Rust authority/control kernels, supervision, offline plant and refusal tests. Replay and hardware-in-loop development; no live train or safety authorisation.

The first adoptable product is the simulated owner/builder/operator delivery workflow. It may be used for controlled planning and training before rolling-stock certification; legal entities, calendars, permissions and real equipment bindings remain deployment inputs.
The read-only maglev evidence Workbench and the authenticated native lifecycle application have different responsibilities. Neither grants movement authority or accepts manufactured hardware.
