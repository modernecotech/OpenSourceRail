# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 76 at depots = 106 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0438-0661-s000000 | line-1 | declared-depot | 18 | 1,071.0 | 4 |
| line-2-0393-0351-s009824 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0512-0772-s000000 | line-3 | declared-depot | 22 | 1,309.0 | 5 |
| line-4-0518-0544-s000000 | line-4 | declared-depot | 14 | 833.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0438-0661-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0542-0625-s002402 | station | forward | revenue | 1 |
| line-1 | line-1-0542-0625-s002402 | station | reverse | revenue | 1 |
| line-1 | line-1-0641-0591-s004698 | station | forward | revenue | 1 |
| line-1 | line-1-0641-0591-s004698 | station | reverse | revenue | 1 |
| line-1 | line-1-0761-0550-s007462 | station | reverse | revenue | 2 |
| line-2 | line-2-0393-0351-s009824 | station | reverse | revenue | 2 |
| line-2 | line-2-0473-0425-s007167 | station | forward | revenue | 1 |
| line-2 | line-2-0473-0425-s007167 | station | reverse | revenue | 1 |
| line-2 | line-2-0555-0508-s004530 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0508-s004530 | station | reverse | revenue | 1 |
| line-2 | line-2-0641-0591-s001876 | station | forward | revenue | 1 |
| line-2 | line-2-0641-0591-s001876 | station | reverse | revenue | 1 |
| line-2 | line-2-0701-0650-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0433-0500-s009451 | station | reverse | revenue | 2 |
| line-3 | line-3-0512-0772-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0518-0544-s006618 | station | forward | revenue | 1 |
| line-3 | line-3-0518-0544-s006618 | station | reverse | revenue | 1 |
| line-3 | line-3-0542-0625-s004295 | station | forward | revenue | 1 |
| line-3 | line-3-0542-0625-s004295 | station | reverse | revenue | 1 |
| line-4 | line-4-0339-0513-s005654 | station | reverse | revenue | 2 |
| line-4 | line-4-0518-0544-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0438-0661-s000000 | depot | — | revenue | 15 |
| line-1 | line-1-0438-0661-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0438-0661-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0393-0351-s009824 | depot | — | revenue | 19 |
| line-2 | line-2-0393-0351-s009824 | depot | — | spare | 2 |
| line-2 | line-2-0393-0351-s009824 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0512-0772-s000000 | depot | — | revenue | 19 |
| line-3 | line-3-0512-0772-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0512-0772-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0518-0544-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0518-0544-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0518-0544-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hodeidah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **106 trainsets at 15 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **95 revenue, 7 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **76 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0438-0661-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0542-0625-s002402 | forward | revenue | 4 | pending |
| line-1 | line-1-0542-0625-s002402 | reverse | revenue | 4 | pending |
| line-1 | line-1-0641-0591-s004698 | forward | revenue | 4 | pending |
| line-1 | line-1-0641-0591-s004698 | reverse | revenue | 4 | pending |
| line-1 | line-1-0761-0550-s007462 | reverse | revenue | 3 | pending |
| line-1 | line-1-0761-0550-s007462 | reverse | spare | 1 | pending |
| line-1 | line-1-0438-0661-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0542-0625-s002402 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0701-0650-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0641-0591-s001876 | forward | revenue | 4 | pending |
| line-2 | line-2-0641-0591-s001876 | reverse | revenue | 4 | pending |
| line-2 | line-2-0555-0508-s004530 | forward | revenue | 4 | pending |
| line-2 | line-2-0555-0508-s004530 | reverse | revenue | 4 | pending |
| line-2 | line-2-0473-0425-s007167 | forward | revenue | 3 | pending |
| line-2 | line-2-0473-0425-s007167 | reverse | revenue | 3 | pending |
| line-2 | line-2-0393-0351-s009824 | reverse | revenue | 3 | pending |
| line-2 | line-2-0473-0425-s007167 | forward | spare | 1 | pending |
| line-2 | line-2-0473-0425-s007167 | reverse | spare | 1 | pending |
| line-2 | line-2-0393-0351-s009824 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0512-0772-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0542-0625-s004295 | forward | revenue | 5 | pending |
| line-3 | line-3-0542-0625-s004295 | reverse | revenue | 5 | pending |
| line-3 | line-3-0518-0544-s006618 | forward | revenue | 4 | pending |
| line-3 | line-3-0518-0544-s006618 | reverse | revenue | 4 | pending |
| line-3 | line-3-0433-0500-s009451 | reverse | revenue | 4 | pending |
| line-3 | line-3-0518-0544-s006618 | forward | spare | 1 | pending |
| line-3 | line-3-0518-0544-s006618 | reverse | spare | 1 | pending |
| line-3 | line-3-0433-0500-s009451 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0518-0544-s000000 | forward | revenue | 8 | pending |
| line-4 | line-4-0339-0513-s005654 | reverse | revenue | 8 | pending |
| line-4 | line-4-0518-0544-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0339-0513-s005654 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**66 trainsets exceed the reference platform envelope**, requiring **3,927.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0438-0661-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0542-0625-s002402 | 9 | 4 | 5 | 297.5 |
| line-1-0641-0591-s004698 | 8 | 4 | 4 | 238.0 |
| line-1-0761-0550-s007462 | 4 | 2 | 2 | 119.0 |
| line-2-0393-0351-s009824 | 4 | 2 | 2 | 119.0 |
| line-2-0473-0425-s007167 | 8 | 2 | 6 | 357.0 |
| line-2-0555-0508-s004530 | 8 | 2 | 6 | 357.0 |
| line-2-0641-0591-s001876 | 8 | 4 | 4 | 238.0 |
| line-2-0701-0650-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0433-0500-s009451 | 5 | 2 | 3 | 178.5 |
| line-3-0512-0772-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0518-0544-s006618 | 10 | 4 | 6 | 357.0 |
| line-3-0542-0625-s004295 | 10 | 4 | 6 | 357.0 |
| line-4-0339-0513-s005654 | 9 | 2 | 7 | 416.5 |
| line-4-0518-0544-s000000 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Hodeidah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
