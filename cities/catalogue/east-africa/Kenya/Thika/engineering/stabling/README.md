# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 216 at depots = 256 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0016-0869-s026109 | line-1 | declared-depot | 71 | 4,224.5 | 12 |
| line-2-0665-0928-s000000 | line-2 | declared-depot | 54 | 3,213.0 | 10 |
| line-3-1020-0216-s000000 | line-3 | declared-depot | 67 | 3,986.5 | 11 |
| line-4-0655-0716-s000000 | line-4 | declared-depot | 14 | 833.0 | 3 |
| line-5-0694-0928-s000000 | line-5 | declared-depot | 10 | 595.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0016-0869-s026109 | station | reverse | revenue | 2 |
| line-1 | line-1-0394-0608-s015215 | station | forward | revenue | 1 |
| line-1 | line-1-0394-0608-s015215 | station | reverse | revenue | 1 |
| line-1 | line-1-0553-0519-s011157 | station | forward | revenue | 1 |
| line-1 | line-1-0553-0519-s011157 | station | reverse | revenue | 1 |
| line-1 | line-1-0748-0409-s006170 | station | forward | revenue | 1 |
| line-1 | line-1-0748-0409-s006170 | station | reverse | revenue | 1 |
| line-1 | line-1-0901-0237-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0553-0519-s012556 | station | forward | revenue | 1 |
| line-2 | line-2-0553-0519-s012556 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0326-s017726 | station | forward | revenue | 1 |
| line-2 | line-2-0561-0326-s017726 | station | reverse | revenue | 1 |
| line-2 | line-2-0586-0120-s022917 | station | reverse | revenue | 2 |
| line-2 | line-2-0596-0694-s007849 | station | forward | revenue | 1 |
| line-2 | line-2-0596-0694-s007849 | station | reverse | revenue | 1 |
| line-2 | line-2-0655-0716-s005617 | station | forward | revenue | 1 |
| line-2 | line-2-0655-0716-s005617 | station | reverse | revenue | 1 |
| line-2 | line-2-0665-0928-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0694-0928-s000580 | station | forward | revenue | 1 |
| line-2 | line-2-0694-0928-s000580 | station | reverse | revenue | 1 |
| line-3 | line-3-0341-0923-s023755 | station | reverse | revenue | 2 |
| line-3 | line-3-0596-0694-s015134 | station | forward | revenue | 1 |
| line-3 | line-3-0596-0694-s015134 | station | reverse | revenue | 1 |
| line-3 | line-3-0677-0606-s012481 | station | forward | revenue | 1 |
| line-3 | line-3-0677-0606-s012481 | station | reverse | revenue | 1 |
| line-3 | line-3-1020-0216-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0655-0716-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0676-0608-s005717 | station | reverse | revenue | 2 |
| line-5 | line-5-0694-0928-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0837-0938-s004214 | station | reverse | revenue | 2 |
| line-1 | line-1-0016-0869-s026109 | depot | — | revenue | 63 |
| line-1 | line-1-0016-0869-s026109 | depot | — | spare | 7 |
| line-1 | line-1-0016-0869-s026109 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0665-0928-s000000 | depot | — | revenue | 47 |
| line-2 | line-2-0665-0928-s000000 | depot | — | spare | 6 |
| line-2 | line-2-0665-0928-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1020-0216-s000000 | depot | — | revenue | 60 |
| line-3 | line-3-1020-0216-s000000 | depot | — | spare | 6 |
| line-3 | line-3-1020-0216-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0655-0716-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0655-0716-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0655-0716-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0694-0928-s000000 | depot | — | revenue | 8 |
| line-5 | line-5-0694-0928-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0694-0928-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/thika-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **256 trainsets at 20 stations**; largest initial station queue **26**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **230 revenue, 21 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **216 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0901-0237-s000000 | forward | revenue | 10 | pending |
| line-1 | line-1-0748-0409-s006170 | forward | revenue | 9 | pending |
| line-1 | line-1-0748-0409-s006170 | reverse | revenue | 9 | pending |
| line-1 | line-1-0553-0519-s011157 | forward | revenue | 9 | pending |
| line-1 | line-1-0553-0519-s011157 | reverse | revenue | 9 | pending |
| line-1 | line-1-0394-0608-s015215 | forward | revenue | 9 | pending |
| line-1 | line-1-0394-0608-s015215 | reverse | revenue | 9 | pending |
| line-1 | line-1-0016-0869-s026109 | reverse | revenue | 9 | pending |
| line-1 | line-1-0748-0409-s006170 | forward | spare | 1 | pending |
| line-1 | line-1-0748-0409-s006170 | reverse | spare | 1 | pending |
| line-1 | line-1-0553-0519-s011157 | forward | spare | 1 | pending |
| line-1 | line-1-0553-0519-s011157 | reverse | spare | 1 | pending |
| line-1 | line-1-0394-0608-s015215 | forward | spare | 1 | pending |
| line-1 | line-1-0394-0608-s015215 | reverse | spare | 1 | pending |
| line-1 | line-1-0016-0869-s026109 | reverse | spare | 1 | pending |
| line-1 | line-1-0901-0237-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0665-0928-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0694-0928-s000580 | forward | revenue | 5 | pending |
| line-2 | line-2-0694-0928-s000580 | reverse | revenue | 5 | pending |
| line-2 | line-2-0655-0716-s005617 | forward | revenue | 5 | pending |
| line-2 | line-2-0655-0716-s005617 | reverse | revenue | 5 | pending |
| line-2 | line-2-0596-0694-s007849 | forward | revenue | 5 | pending |
| line-2 | line-2-0596-0694-s007849 | reverse | revenue | 5 | pending |
| line-2 | line-2-0553-0519-s012556 | forward | revenue | 5 | pending |
| line-2 | line-2-0553-0519-s012556 | reverse | revenue | 5 | pending |
| line-2 | line-2-0561-0326-s017726 | forward | revenue | 5 | pending |
| line-2 | line-2-0561-0326-s017726 | reverse | revenue | 5 | pending |
| line-2 | line-2-0586-0120-s022917 | reverse | revenue | 5 | pending |
| line-2 | line-2-0694-0928-s000580 | forward | spare | 1 | pending |
| line-2 | line-2-0694-0928-s000580 | reverse | spare | 1 | pending |
| line-2 | line-2-0655-0716-s005617 | forward | spare | 1 | pending |
| line-2 | line-2-0655-0716-s005617 | reverse | spare | 1 | pending |
| line-2 | line-2-0596-0694-s007849 | forward | spare | 1 | pending |
| line-2 | line-2-0596-0694-s007849 | reverse | spare | 1 | pending |
| line-2 | line-2-0553-0519-s012556 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1020-0216-s000000 | forward | revenue | 12 | pending |
| line-3 | line-3-0677-0606-s012481 | forward | revenue | 12 | pending |
| line-3 | line-3-0677-0606-s012481 | reverse | revenue | 11 | pending |
| line-3 | line-3-0596-0694-s015134 | forward | revenue | 11 | pending |
| line-3 | line-3-0596-0694-s015134 | reverse | revenue | 11 | pending |
| line-3 | line-3-0341-0923-s023755 | reverse | revenue | 11 | pending |
| line-3 | line-3-0677-0606-s012481 | reverse | spare | 1 | pending |
| line-3 | line-3-0596-0694-s015134 | forward | spare | 1 | pending |
| line-3 | line-3-0596-0694-s015134 | reverse | spare | 1 | pending |
| line-3 | line-3-0341-0923-s023755 | reverse | spare | 1 | pending |
| line-3 | line-3-1020-0216-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0677-0606-s012481 | forward | spare | 1 | pending |
| line-3 | line-3-0677-0606-s012481 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0655-0716-s000000 | forward | revenue | 8 | pending |
| line-4 | line-4-0676-0608-s005717 | reverse | revenue | 8 | pending |
| line-4 | line-4-0655-0716-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0676-0608-s005717 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0694-0928-s000000 | forward | revenue | 6 | pending |
| line-5 | line-5-0837-0938-s004214 | reverse | revenue | 6 | pending |
| line-5 | line-5-0694-0928-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0837-0938-s004214 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**202 trainsets exceed the reference platform envelope**, requiring **12,019.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0016-0869-s026109 | 10 | 2 | 8 | 476.0 |
| line-1-0394-0608-s015215 | 20 | 2 | 18 | 1,071.0 |
| line-1-0553-0519-s011157 | 20 | 4 | 16 | 952.0 |
| line-1-0748-0409-s006170 | 20 | 2 | 18 | 1,071.0 |
| line-1-0901-0237-s000000 | 11 | 2 | 9 | 535.5 |
| line-2-0553-0519-s012556 | 11 | 4 | 7 | 416.5 |
| line-2-0561-0326-s017726 | 10 | 2 | 8 | 476.0 |
| line-2-0586-0120-s022917 | 5 | 2 | 3 | 178.5 |
| line-2-0596-0694-s007849 | 12 | 4 | 8 | 476.0 |
| line-2-0655-0716-s005617 | 12 | 4 | 8 | 476.0 |
| line-2-0665-0928-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0694-0928-s000580 | 12 | 4 | 8 | 476.0 |
| line-3-0341-0923-s023755 | 12 | 2 | 10 | 595.0 |
| line-3-0596-0694-s015134 | 24 | 4 | 20 | 1,190.0 |
| line-3-0677-0606-s012481 | 26 | 4 | 22 | 1,309.0 |
| line-3-1020-0216-s000000 | 13 | 2 | 11 | 654.5 |
| line-4-0655-0716-s000000 | 9 | 2 | 7 | 416.5 |
| line-4-0676-0608-s005717 | 9 | 2 | 7 | 416.5 |
| line-5-0694-0928-s000000 | 7 | 2 | 5 | 297.5 |
| line-5-0837-0938-s004214 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Thika/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
