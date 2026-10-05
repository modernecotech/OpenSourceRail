# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 132 at depots = 176 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0811-0508-s000000 | line-1 | declared-depot | 24 | 1,428.0 | 6 |
| line-2-0185-1002-s021988 | line-2 | declared-depot | 54 | 3,213.0 | 10 |
| line-3-0123-0580-s000000 | line-3 | declared-depot | 54 | 3,213.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0395-0236-s011136 | station | reverse | revenue | 2 |
| line-1 | line-1-0471-0286-s009096 | station | forward | revenue | 1 |
| line-1 | line-1-0471-0286-s009096 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0336-s007036 | station | forward | revenue | 1 |
| line-1 | line-1-0548-0336-s007036 | station | reverse | revenue | 1 |
| line-1 | line-1-0625-0386-s004988 | station | forward | revenue | 1 |
| line-1 | line-1-0625-0386-s004988 | station | reverse | revenue | 1 |
| line-1 | line-1-0631-0390-s004849 | station | forward | revenue | 1 |
| line-1 | line-1-0631-0390-s004849 | station | reverse | revenue | 1 |
| line-1 | line-1-0698-0434-s003025 | station | forward | revenue | 1 |
| line-1 | line-1-0698-0434-s003025 | station | reverse | revenue | 1 |
| line-1 | line-1-0811-0508-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0185-1002-s021988 | station | reverse | revenue | 2 |
| line-2 | line-2-0440-0721-s012554 | station | forward | revenue | 1 |
| line-2 | line-2-0440-0721-s012554 | station | reverse | revenue | 1 |
| line-2 | line-2-0516-0584-s009043 | station | forward | revenue | 1 |
| line-2 | line-2-0516-0584-s009043 | station | reverse | revenue | 1 |
| line-2 | line-2-0580-0466-s006036 | station | forward | revenue | 1 |
| line-2 | line-2-0580-0466-s006036 | station | reverse | revenue | 1 |
| line-2 | line-2-0619-0395-s004223 | station | forward | revenue | 1 |
| line-2 | line-2-0619-0395-s004223 | station | reverse | revenue | 1 |
| line-2 | line-2-0625-0386-s003993 | station | forward | revenue | 1 |
| line-2 | line-2-0625-0386-s003993 | station | reverse | revenue | 1 |
| line-2 | line-2-0668-0308-s001995 | station | forward | revenue | 1 |
| line-2 | line-2-0668-0308-s001995 | station | reverse | revenue | 1 |
| line-2 | line-2-0711-0229-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0123-0580-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0372-0521-s007016 | station | forward | revenue | 1 |
| line-3 | line-3-0372-0521-s007016 | station | reverse | revenue | 1 |
| line-3 | line-3-0491-0460-s010018 | station | forward | revenue | 1 |
| line-3 | line-3-0491-0460-s010018 | station | reverse | revenue | 1 |
| line-3 | line-3-0619-0395-s013163 | station | forward | revenue | 1 |
| line-3 | line-3-0619-0395-s013163 | station | reverse | revenue | 1 |
| line-3 | line-3-0631-0390-s013451 | station | forward | revenue | 1 |
| line-3 | line-3-0631-0390-s013451 | station | reverse | revenue | 1 |
| line-3 | line-3-0785-0311-s017332 | station | forward | revenue | 1 |
| line-3 | line-3-0785-0311-s017332 | station | reverse | revenue | 1 |
| line-3 | line-3-0927-0228-s021222 | station | reverse | revenue | 2 |
| line-1 | line-1-0811-0508-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0811-0508-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0811-0508-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0185-1002-s021988 | depot | — | revenue | 47 |
| line-2 | line-2-0185-1002-s021988 | depot | — | spare | 6 |
| line-2 | line-2-0185-1002-s021988 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0123-0580-s000000 | depot | — | revenue | 47 |
| line-3 | line-3-0123-0580-s000000 | depot | — | spare | 6 |
| line-3 | line-3-0123-0580-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/baqubah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **176 trainsets at 22 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **158 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **132 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0811-0508-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0698-0434-s003025 | forward | revenue | 3 | pending |
| line-1 | line-1-0698-0434-s003025 | reverse | revenue | 3 | pending |
| line-1 | line-1-0631-0390-s004849 | forward | revenue | 3 | pending |
| line-1 | line-1-0631-0390-s004849 | reverse | revenue | 3 | pending |
| line-1 | line-1-0625-0386-s004988 | forward | revenue | 3 | pending |
| line-1 | line-1-0625-0386-s004988 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0336-s007036 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0336-s007036 | reverse | revenue | 3 | pending |
| line-1 | line-1-0471-0286-s009096 | forward | revenue | 3 | pending |
| line-1 | line-1-0471-0286-s009096 | reverse | revenue | 2 | pending |
| line-1 | line-1-0395-0236-s011136 | reverse | revenue | 2 | pending |
| line-1 | line-1-0471-0286-s009096 | reverse | spare | 1 | pending |
| line-1 | line-1-0395-0236-s011136 | reverse | spare | 1 | pending |
| line-1 | line-1-0811-0508-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0698-0434-s003025 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0711-0229-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0668-0308-s001995 | forward | revenue | 5 | pending |
| line-2 | line-2-0668-0308-s001995 | reverse | revenue | 5 | pending |
| line-2 | line-2-0625-0386-s003993 | forward | revenue | 5 | pending |
| line-2 | line-2-0625-0386-s003993 | reverse | revenue | 5 | pending |
| line-2 | line-2-0619-0395-s004223 | forward | revenue | 5 | pending |
| line-2 | line-2-0619-0395-s004223 | reverse | revenue | 5 | pending |
| line-2 | line-2-0580-0466-s006036 | forward | revenue | 4 | pending |
| line-2 | line-2-0580-0466-s006036 | reverse | revenue | 4 | pending |
| line-2 | line-2-0516-0584-s009043 | forward | revenue | 4 | pending |
| line-2 | line-2-0516-0584-s009043 | reverse | revenue | 4 | pending |
| line-2 | line-2-0440-0721-s012554 | forward | revenue | 4 | pending |
| line-2 | line-2-0440-0721-s012554 | reverse | revenue | 4 | pending |
| line-2 | line-2-0185-1002-s021988 | reverse | revenue | 4 | pending |
| line-2 | line-2-0580-0466-s006036 | forward | spare | 1 | pending |
| line-2 | line-2-0580-0466-s006036 | reverse | spare | 1 | pending |
| line-2 | line-2-0516-0584-s009043 | forward | spare | 1 | pending |
| line-2 | line-2-0516-0584-s009043 | reverse | spare | 1 | pending |
| line-2 | line-2-0440-0721-s012554 | forward | spare | 1 | pending |
| line-2 | line-2-0440-0721-s012554 | reverse | spare | 1 | pending |
| line-2 | line-2-0185-1002-s021988 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0123-0580-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0372-0521-s007016 | forward | revenue | 5 | pending |
| line-3 | line-3-0372-0521-s007016 | reverse | revenue | 5 | pending |
| line-3 | line-3-0491-0460-s010018 | forward | revenue | 5 | pending |
| line-3 | line-3-0491-0460-s010018 | reverse | revenue | 5 | pending |
| line-3 | line-3-0619-0395-s013163 | forward | revenue | 5 | pending |
| line-3 | line-3-0619-0395-s013163 | reverse | revenue | 5 | pending |
| line-3 | line-3-0631-0390-s013451 | forward | revenue | 5 | pending |
| line-3 | line-3-0631-0390-s013451 | reverse | revenue | 5 | pending |
| line-3 | line-3-0785-0311-s017332 | forward | revenue | 5 | pending |
| line-3 | line-3-0785-0311-s017332 | reverse | revenue | 5 | pending |
| line-3 | line-3-0927-0228-s021222 | reverse | revenue | 5 | pending |
| line-3 | line-3-0372-0521-s007016 | forward | spare | 1 | pending |
| line-3 | line-3-0372-0521-s007016 | reverse | spare | 1 | pending |
| line-3 | line-3-0491-0460-s010018 | forward | spare | 1 | pending |
| line-3 | line-3-0491-0460-s010018 | reverse | spare | 1 | pending |
| line-3 | line-3-0619-0395-s013163 | forward | spare | 1 | pending |
| line-3 | line-3-0619-0395-s013163 | reverse | spare | 1 | pending |
| line-3 | line-3-0631-0390-s013451 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**120 trainsets exceed the reference platform envelope**, requiring **7,140.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0395-0236-s011136 | 3 | 2 | 1 | 59.5 |
| line-1-0471-0286-s009096 | 6 | 2 | 4 | 238.0 |
| line-1-0548-0336-s007036 | 6 | 2 | 4 | 238.0 |
| line-1-0625-0386-s004988 | 6 | 4 | 2 | 119.0 |
| line-1-0631-0390-s004849 | 6 | 4 | 2 | 119.0 |
| line-1-0698-0434-s003025 | 7 | 2 | 5 | 297.5 |
| line-1-0811-0508-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0185-1002-s021988 | 5 | 2 | 3 | 178.5 |
| line-2-0440-0721-s012554 | 10 | 2 | 8 | 476.0 |
| line-2-0516-0584-s009043 | 10 | 2 | 8 | 476.0 |
| line-2-0580-0466-s006036 | 10 | 2 | 8 | 476.0 |
| line-2-0619-0395-s004223 | 10 | 4 | 6 | 357.0 |
| line-2-0625-0386-s003993 | 10 | 4 | 6 | 357.0 |
| line-2-0668-0308-s001995 | 10 | 2 | 8 | 476.0 |
| line-2-0711-0229-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0123-0580-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0372-0521-s007016 | 12 | 2 | 10 | 595.0 |
| line-3-0491-0460-s010018 | 12 | 2 | 10 | 595.0 |
| line-3-0619-0395-s013163 | 12 | 4 | 8 | 476.0 |
| line-3-0631-0390-s013451 | 11 | 4 | 7 | 416.5 |
| line-3-0785-0311-s017332 | 10 | 2 | 8 | 476.0 |
| line-3-0927-0228-s021222 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Baqubah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
