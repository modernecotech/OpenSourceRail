# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 160 at depots = 200 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0076-0559-s000000 | line-1 | declared-depot | 53 | 3,153.5 | 10 |
| line-2-0747-0635-s000000 | line-2 | declared-depot | 43 | 2,558.5 | 8 |
| line-3-0013-0648-s025831 | line-3 | declared-depot | 64 | 3,808.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0076-0559-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0334-0557-s006415 | station | forward | revenue | 1 |
| line-1 | line-1-0334-0557-s006415 | station | reverse | revenue | 1 |
| line-1 | line-1-0473-0530-s009419 | station | forward | revenue | 1 |
| line-1 | line-1-0473-0530-s009419 | station | reverse | revenue | 1 |
| line-1 | line-1-0532-0519-s010690 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0519-s010690 | station | reverse | revenue | 1 |
| line-1 | line-1-0612-0503-s012423 | station | forward | revenue | 1 |
| line-1 | line-1-0612-0503-s012423 | station | reverse | revenue | 1 |
| line-1 | line-1-0727-0481-s014905 | station | forward | revenue | 1 |
| line-1 | line-1-0727-0481-s014905 | station | reverse | revenue | 1 |
| line-1 | line-1-0841-0458-s017376 | station | forward | revenue | 1 |
| line-1 | line-1-0841-0458-s017376 | station | reverse | revenue | 1 |
| line-1 | line-1-1043-0345-s022348 | station | reverse | revenue | 2 |
| line-2 | line-2-0356-0019-s017266 | station | reverse | revenue | 2 |
| line-2 | line-2-0403-0247-s011652 | station | forward | revenue | 1 |
| line-2 | line-2-0403-0247-s011652 | station | reverse | revenue | 1 |
| line-2 | line-2-0568-0434-s006042 | station | forward | revenue | 1 |
| line-2 | line-2-0568-0434-s006042 | station | reverse | revenue | 1 |
| line-2 | line-2-0657-0534-s003023 | station | forward | revenue | 1 |
| line-2 | line-2-0657-0534-s003023 | station | reverse | revenue | 1 |
| line-2 | line-2-0747-0635-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0013-0648-s025831 | station | reverse | revenue | 2 |
| line-3 | line-3-0113-0597-s023517 | station | forward | revenue | 1 |
| line-3 | line-3-0113-0597-s023517 | station | reverse | revenue | 1 |
| line-3 | line-3-0164-0502-s021220 | station | forward | revenue | 1 |
| line-3 | line-3-0164-0502-s021220 | station | reverse | revenue | 1 |
| line-3 | line-3-0418-0399-s015145 | station | forward | revenue | 1 |
| line-3 | line-3-0418-0399-s015145 | station | reverse | revenue | 1 |
| line-3 | line-3-0544-0341-s012144 | station | forward | revenue | 1 |
| line-3 | line-3-0544-0341-s012144 | station | reverse | revenue | 1 |
| line-3 | line-3-0755-0242-s007010 | station | forward | revenue | 1 |
| line-3 | line-3-0755-0242-s007010 | station | reverse | revenue | 1 |
| line-3 | line-3-0997-0136-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0076-0559-s000000 | depot | — | revenue | 46 |
| line-1 | line-1-0076-0559-s000000 | depot | — | spare | 6 |
| line-1 | line-1-0076-0559-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0747-0635-s000000 | depot | — | revenue | 38 |
| line-2 | line-2-0747-0635-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0747-0635-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0013-0648-s025831 | depot | — | revenue | 56 |
| line-3 | line-3-0013-0648-s025831 | depot | — | spare | 7 |
| line-3 | line-3-0013-0648-s025831 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/damietta-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **200 trainsets at 20 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **180 revenue, 17 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **160 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0076-0559-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0334-0557-s006415 | forward | revenue | 5 | pending |
| line-1 | line-1-0334-0557-s006415 | reverse | revenue | 5 | pending |
| line-1 | line-1-0473-0530-s009419 | forward | revenue | 5 | pending |
| line-1 | line-1-0473-0530-s009419 | reverse | revenue | 5 | pending |
| line-1 | line-1-0532-0519-s010690 | forward | revenue | 5 | pending |
| line-1 | line-1-0532-0519-s010690 | reverse | revenue | 4 | pending |
| line-1 | line-1-0612-0503-s012423 | forward | revenue | 4 | pending |
| line-1 | line-1-0612-0503-s012423 | reverse | revenue | 4 | pending |
| line-1 | line-1-0727-0481-s014905 | forward | revenue | 4 | pending |
| line-1 | line-1-0727-0481-s014905 | reverse | revenue | 4 | pending |
| line-1 | line-1-0841-0458-s017376 | forward | revenue | 4 | pending |
| line-1 | line-1-0841-0458-s017376 | reverse | revenue | 4 | pending |
| line-1 | line-1-1043-0345-s022348 | reverse | revenue | 4 | pending |
| line-1 | line-1-0532-0519-s010690 | reverse | spare | 1 | pending |
| line-1 | line-1-0612-0503-s012423 | forward | spare | 1 | pending |
| line-1 | line-1-0612-0503-s012423 | reverse | spare | 1 | pending |
| line-1 | line-1-0727-0481-s014905 | forward | spare | 1 | pending |
| line-1 | line-1-0727-0481-s014905 | reverse | spare | 1 | pending |
| line-1 | line-1-0841-0458-s017376 | forward | spare | 1 | pending |
| line-1 | line-1-0841-0458-s017376 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0747-0635-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0657-0534-s003023 | forward | revenue | 6 | pending |
| line-2 | line-2-0657-0534-s003023 | reverse | revenue | 6 | pending |
| line-2 | line-2-0568-0434-s006042 | forward | revenue | 6 | pending |
| line-2 | line-2-0568-0434-s006042 | reverse | revenue | 6 | pending |
| line-2 | line-2-0403-0247-s011652 | forward | revenue | 6 | pending |
| line-2 | line-2-0403-0247-s011652 | reverse | revenue | 6 | pending |
| line-2 | line-2-0356-0019-s017266 | reverse | revenue | 6 | pending |
| line-2 | line-2-0747-0635-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0657-0534-s003023 | forward | spare | 1 | pending |
| line-2 | line-2-0657-0534-s003023 | reverse | spare | 1 | pending |
| line-2 | line-2-0568-0434-s006042 | forward | spare | 1 | pending |
| line-2 | line-2-0568-0434-s006042 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0997-0136-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0755-0242-s007010 | forward | revenue | 6 | pending |
| line-3 | line-3-0755-0242-s007010 | reverse | revenue | 6 | pending |
| line-3 | line-3-0544-0341-s012144 | forward | revenue | 6 | pending |
| line-3 | line-3-0544-0341-s012144 | reverse | revenue | 6 | pending |
| line-3 | line-3-0418-0399-s015145 | forward | revenue | 6 | pending |
| line-3 | line-3-0418-0399-s015145 | reverse | revenue | 6 | pending |
| line-3 | line-3-0164-0502-s021220 | forward | revenue | 6 | pending |
| line-3 | line-3-0164-0502-s021220 | reverse | revenue | 6 | pending |
| line-3 | line-3-0113-0597-s023517 | forward | revenue | 6 | pending |
| line-3 | line-3-0113-0597-s023517 | reverse | revenue | 5 | pending |
| line-3 | line-3-0013-0648-s025831 | reverse | revenue | 5 | pending |
| line-3 | line-3-0113-0597-s023517 | reverse | spare | 1 | pending |
| line-3 | line-3-0013-0648-s025831 | reverse | spare | 1 | pending |
| line-3 | line-3-0997-0136-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0755-0242-s007010 | forward | spare | 1 | pending |
| line-3 | line-3-0755-0242-s007010 | reverse | spare | 1 | pending |
| line-3 | line-3-0544-0341-s012144 | forward | spare | 1 | pending |
| line-3 | line-3-0544-0341-s012144 | reverse | spare | 1 | pending |
| line-3 | line-3-0418-0399-s015145 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**160 trainsets exceed the reference platform envelope**, requiring **9,520.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0076-0559-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0334-0557-s006415 | 10 | 2 | 8 | 476.0 |
| line-1-0473-0530-s009419 | 10 | 2 | 8 | 476.0 |
| line-1-0532-0519-s010690 | 10 | 2 | 8 | 476.0 |
| line-1-0612-0503-s012423 | 10 | 2 | 8 | 476.0 |
| line-1-0727-0481-s014905 | 10 | 2 | 8 | 476.0 |
| line-1-0841-0458-s017376 | 10 | 2 | 8 | 476.0 |
| line-1-1043-0345-s022348 | 4 | 2 | 2 | 119.0 |
| line-2-0356-0019-s017266 | 6 | 2 | 4 | 238.0 |
| line-2-0403-0247-s011652 | 12 | 2 | 10 | 595.0 |
| line-2-0568-0434-s006042 | 14 | 2 | 12 | 714.0 |
| line-2-0657-0534-s003023 | 14 | 2 | 12 | 714.0 |
| line-2-0747-0635-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0013-0648-s025831 | 6 | 2 | 4 | 238.0 |
| line-3-0113-0597-s023517 | 12 | 2 | 10 | 595.0 |
| line-3-0164-0502-s021220 | 12 | 2 | 10 | 595.0 |
| line-3-0418-0399-s015145 | 13 | 2 | 11 | 654.5 |
| line-3-0544-0341-s012144 | 14 | 2 | 12 | 714.0 |
| line-3-0755-0242-s007010 | 14 | 2 | 12 | 714.0 |
| line-3-0997-0136-s000000 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Damietta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
