# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 124 at depots = 164 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0594-0760-s000000 | line-1 | declared-depot | 32 | 1,904.0 | 6 |
| line-2-0785-0507-s017696 | line-2 | declared-depot | 41 | 2,439.5 | 8 |
| line-3-0698-0406-s000000 | line-3 | declared-depot | 27 | 1,606.5 | 5 |
| line-4-0609-0660-s000000 | line-4 | declared-depot | 12 | 714.0 | 3 |
| line-5-0673-0403-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0412-0263-s012992 | station | reverse | revenue | 2 |
| line-1 | line-1-0481-0384-s009554 | station | forward | revenue | 1 |
| line-1 | line-1-0481-0384-s009554 | station | reverse | revenue | 1 |
| line-1 | line-1-0541-0549-s005637 | station | forward | revenue | 1 |
| line-1 | line-1-0541-0549-s005637 | station | reverse | revenue | 1 |
| line-1 | line-1-0594-0760-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0609-0660-s002124 | station | forward | revenue | 1 |
| line-1 | line-1-0609-0660-s002124 | station | reverse | revenue | 1 |
| line-2 | line-2-0169-0808-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0307-0732-s003510 | station | forward | revenue | 1 |
| line-2 | line-2-0307-0732-s003510 | station | reverse | revenue | 1 |
| line-2 | line-2-0423-0637-s007025 | station | forward | revenue | 1 |
| line-2 | line-2-0423-0637-s007025 | station | reverse | revenue | 1 |
| line-2 | line-2-0541-0549-s010531 | station | forward | revenue | 1 |
| line-2 | line-2-0541-0549-s010531 | station | reverse | revenue | 1 |
| line-2 | line-2-0699-0487-s015375 | station | forward | revenue | 1 |
| line-2 | line-2-0699-0487-s015375 | station | reverse | revenue | 1 |
| line-2 | line-2-0785-0507-s017696 | station | reverse | revenue | 2 |
| line-3 | line-3-0191-0361-s010591 | station | reverse | revenue | 2 |
| line-3 | line-3-0481-0384-s004522 | station | forward | revenue | 1 |
| line-3 | line-3-0481-0384-s004522 | station | reverse | revenue | 1 |
| line-3 | line-3-0673-0403-s000525 | station | forward | revenue | 1 |
| line-3 | line-3-0673-0403-s000525 | station | reverse | revenue | 1 |
| line-3 | line-3-0698-0406-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0609-0660-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0761-0763-s004496 | station | reverse | revenue | 2 |
| line-5 | line-5-0488-0315-s005511 | station | reverse | revenue | 2 |
| line-5 | line-5-0588-0314-s003470 | station | forward | revenue | 1 |
| line-5 | line-5-0588-0314-s003470 | station | reverse | revenue | 1 |
| line-5 | line-5-0673-0403-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0594-0760-s000000 | depot | — | revenue | 28 |
| line-1 | line-1-0594-0760-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0594-0760-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0785-0507-s017696 | depot | — | revenue | 36 |
| line-2 | line-2-0785-0507-s017696 | depot | — | spare | 4 |
| line-2 | line-2-0785-0507-s017696 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0698-0406-s000000 | depot | — | revenue | 23 |
| line-3 | line-3-0698-0406-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0698-0406-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0609-0660-s000000 | depot | — | revenue | 10 |
| line-4 | line-4-0609-0660-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0609-0660-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0673-0403-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0673-0403-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0673-0403-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/rangpur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **164 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **147 revenue, 12 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **124 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0594-0760-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0609-0660-s002124 | forward | revenue | 5 | pending |
| line-1 | line-1-0609-0660-s002124 | reverse | revenue | 5 | pending |
| line-1 | line-1-0541-0549-s005637 | forward | revenue | 5 | pending |
| line-1 | line-1-0541-0549-s005637 | reverse | revenue | 5 | pending |
| line-1 | line-1-0481-0384-s009554 | forward | revenue | 5 | pending |
| line-1 | line-1-0481-0384-s009554 | reverse | revenue | 4 | pending |
| line-1 | line-1-0412-0263-s012992 | reverse | revenue | 4 | pending |
| line-1 | line-1-0481-0384-s009554 | reverse | spare | 1 | pending |
| line-1 | line-1-0412-0263-s012992 | reverse | spare | 1 | pending |
| line-1 | line-1-0594-0760-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0609-0660-s002124 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0169-0808-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0307-0732-s003510 | forward | revenue | 5 | pending |
| line-2 | line-2-0307-0732-s003510 | reverse | revenue | 5 | pending |
| line-2 | line-2-0423-0637-s007025 | forward | revenue | 5 | pending |
| line-2 | line-2-0423-0637-s007025 | reverse | revenue | 5 | pending |
| line-2 | line-2-0541-0549-s010531 | forward | revenue | 5 | pending |
| line-2 | line-2-0541-0549-s010531 | reverse | revenue | 5 | pending |
| line-2 | line-2-0699-0487-s015375 | forward | revenue | 5 | pending |
| line-2 | line-2-0699-0487-s015375 | reverse | revenue | 4 | pending |
| line-2 | line-2-0785-0507-s017696 | reverse | revenue | 4 | pending |
| line-2 | line-2-0699-0487-s015375 | reverse | spare | 1 | pending |
| line-2 | line-2-0785-0507-s017696 | reverse | spare | 1 | pending |
| line-2 | line-2-0169-0808-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0307-0732-s003510 | forward | spare | 1 | pending |
| line-2 | line-2-0307-0732-s003510 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0698-0406-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0673-0403-s000525 | forward | revenue | 5 | pending |
| line-3 | line-3-0673-0403-s000525 | reverse | revenue | 5 | pending |
| line-3 | line-3-0481-0384-s004522 | forward | revenue | 5 | pending |
| line-3 | line-3-0481-0384-s004522 | reverse | revenue | 5 | pending |
| line-3 | line-3-0191-0361-s010591 | reverse | revenue | 5 | pending |
| line-3 | line-3-0673-0403-s000525 | forward | spare | 1 | pending |
| line-3 | line-3-0673-0403-s000525 | reverse | spare | 1 | pending |
| line-3 | line-3-0481-0384-s004522 | forward | spare | 1 | pending |
| line-3 | line-3-0481-0384-s004522 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0609-0660-s000000 | forward | revenue | 7 | pending |
| line-4 | line-4-0761-0763-s004496 | reverse | revenue | 7 | pending |
| line-4 | line-4-0609-0660-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0761-0763-s004496 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0673-0403-s000000 | forward | revenue | 4 | pending |
| line-5 | line-5-0588-0314-s003470 | forward | revenue | 4 | pending |
| line-5 | line-5-0588-0314-s003470 | reverse | revenue | 4 | pending |
| line-5 | line-5-0488-0315-s005511 | reverse | revenue | 4 | pending |
| line-5 | line-5-0673-0403-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0588-0314-s003470 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**112 trainsets exceed the reference platform envelope**, requiring **6,664.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0412-0263-s012992 | 5 | 2 | 3 | 178.5 |
| line-1-0481-0384-s009554 | 10 | 4 | 6 | 357.0 |
| line-1-0541-0549-s005637 | 10 | 4 | 6 | 357.0 |
| line-1-0594-0760-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0609-0660-s002124 | 11 | 4 | 7 | 416.5 |
| line-2-0169-0808-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0307-0732-s003510 | 12 | 2 | 10 | 595.0 |
| line-2-0423-0637-s007025 | 10 | 2 | 8 | 476.0 |
| line-2-0541-0549-s010531 | 10 | 4 | 6 | 357.0 |
| line-2-0699-0487-s015375 | 10 | 2 | 8 | 476.0 |
| line-2-0785-0507-s017696 | 5 | 2 | 3 | 178.5 |
| line-3-0191-0361-s010591 | 5 | 2 | 3 | 178.5 |
| line-3-0481-0384-s004522 | 12 | 4 | 8 | 476.0 |
| line-3-0673-0403-s000525 | 12 | 4 | 8 | 476.0 |
| line-3-0698-0406-s000000 | 6 | 2 | 4 | 238.0 |
| line-4-0609-0660-s000000 | 8 | 2 | 6 | 357.0 |
| line-4-0761-0763-s004496 | 8 | 2 | 6 | 357.0 |
| line-5-0488-0315-s005511 | 4 | 2 | 2 | 119.0 |
| line-5-0588-0314-s003470 | 9 | 2 | 7 | 416.5 |
| line-5-0673-0403-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Rangpur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
