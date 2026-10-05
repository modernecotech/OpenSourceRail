# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 134 at depots = 168 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0335-0312-s022955 | line-1 | declared-depot | 56 | 3,332.0 | 10 |
| line-2-0876-0538-s000000 | line-2 | declared-depot | 31 | 1,844.5 | 6 |
| line-3-0354-0936-s000000 | line-3 | declared-depot | 47 | 2,796.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0335-0312-s022955 | station | reverse | revenue | 2 |
| line-1 | line-1-0399-0380-s020842 | station | forward | revenue | 1 |
| line-1 | line-1-0399-0380-s020842 | station | reverse | revenue | 1 |
| line-1 | line-1-0464-0450-s018716 | station | forward | revenue | 1 |
| line-1 | line-1-0464-0450-s018716 | station | reverse | revenue | 1 |
| line-1 | line-1-0528-0518-s016603 | station | forward | revenue | 1 |
| line-1 | line-1-0528-0518-s016603 | station | reverse | revenue | 1 |
| line-1 | line-1-0621-0617-s013595 | station | forward | revenue | 1 |
| line-1 | line-1-0621-0617-s013595 | station | reverse | revenue | 1 |
| line-1 | line-1-0821-0831-s007014 | station | forward | revenue | 1 |
| line-1 | line-1-0821-0831-s007014 | station | reverse | revenue | 1 |
| line-1 | line-1-0939-1100-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0412-0236-s012368 | station | reverse | revenue | 2 |
| line-2 | line-2-0643-0386-s006212 | station | forward | revenue | 1 |
| line-2 | line-2-0643-0386-s006212 | station | reverse | revenue | 1 |
| line-2 | line-2-0756-0460-s003198 | station | forward | revenue | 1 |
| line-2 | line-2-0756-0460-s003198 | station | reverse | revenue | 1 |
| line-2 | line-2-0876-0538-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0354-0936-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0425-0682-s007012 | station | forward | revenue | 1 |
| line-3 | line-3-0425-0682-s007012 | station | reverse | revenue | 1 |
| line-3 | line-3-0485-0559-s010028 | station | forward | revenue | 1 |
| line-3 | line-3-0485-0559-s010028 | station | reverse | revenue | 1 |
| line-3 | line-3-0545-0436-s013032 | station | forward | revenue | 1 |
| line-3 | line-3-0545-0436-s013032 | station | reverse | revenue | 1 |
| line-3 | line-3-0605-0314-s016039 | station | forward | revenue | 1 |
| line-3 | line-3-0605-0314-s016039 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0201-s018785 | station | reverse | revenue | 2 |
| line-1 | line-1-0335-0312-s022955 | depot | — | revenue | 49 |
| line-1 | line-1-0335-0312-s022955 | depot | — | spare | 6 |
| line-1 | line-1-0335-0312-s022955 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0876-0538-s000000 | depot | — | revenue | 27 |
| line-2 | line-2-0876-0538-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0876-0538-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0354-0936-s000000 | depot | — | revenue | 41 |
| line-3 | line-3-0354-0936-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0354-0936-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/taif-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **168 trainsets at 17 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **151 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **134 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0939-1100-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0821-0831-s007014 | forward | revenue | 6 | pending |
| line-1 | line-1-0821-0831-s007014 | reverse | revenue | 6 | pending |
| line-1 | line-1-0621-0617-s013595 | forward | revenue | 5 | pending |
| line-1 | line-1-0621-0617-s013595 | reverse | revenue | 5 | pending |
| line-1 | line-1-0528-0518-s016603 | forward | revenue | 5 | pending |
| line-1 | line-1-0528-0518-s016603 | reverse | revenue | 5 | pending |
| line-1 | line-1-0464-0450-s018716 | forward | revenue | 5 | pending |
| line-1 | line-1-0464-0450-s018716 | reverse | revenue | 5 | pending |
| line-1 | line-1-0399-0380-s020842 | forward | revenue | 5 | pending |
| line-1 | line-1-0399-0380-s020842 | reverse | revenue | 5 | pending |
| line-1 | line-1-0335-0312-s022955 | reverse | revenue | 5 | pending |
| line-1 | line-1-0621-0617-s013595 | forward | spare | 1 | pending |
| line-1 | line-1-0621-0617-s013595 | reverse | spare | 1 | pending |
| line-1 | line-1-0528-0518-s016603 | forward | spare | 1 | pending |
| line-1 | line-1-0528-0518-s016603 | reverse | spare | 1 | pending |
| line-1 | line-1-0464-0450-s018716 | forward | spare | 1 | pending |
| line-1 | line-1-0464-0450-s018716 | reverse | spare | 1 | pending |
| line-1 | line-1-0399-0380-s020842 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0876-0538-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0756-0460-s003198 | forward | revenue | 6 | pending |
| line-2 | line-2-0756-0460-s003198 | reverse | revenue | 6 | pending |
| line-2 | line-2-0643-0386-s006212 | forward | revenue | 6 | pending |
| line-2 | line-2-0643-0386-s006212 | reverse | revenue | 6 | pending |
| line-2 | line-2-0412-0236-s012368 | reverse | revenue | 5 | pending |
| line-2 | line-2-0412-0236-s012368 | reverse | spare | 1 | pending |
| line-2 | line-2-0876-0538-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0756-0460-s003198 | forward | spare | 1 | pending |
| line-2 | line-2-0756-0460-s003198 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0354-0936-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0425-0682-s007012 | forward | revenue | 6 | pending |
| line-3 | line-3-0425-0682-s007012 | reverse | revenue | 6 | pending |
| line-3 | line-3-0485-0559-s010028 | forward | revenue | 5 | pending |
| line-3 | line-3-0485-0559-s010028 | reverse | revenue | 5 | pending |
| line-3 | line-3-0545-0436-s013032 | forward | revenue | 5 | pending |
| line-3 | line-3-0545-0436-s013032 | reverse | revenue | 5 | pending |
| line-3 | line-3-0605-0314-s016039 | forward | revenue | 5 | pending |
| line-3 | line-3-0605-0314-s016039 | reverse | revenue | 5 | pending |
| line-3 | line-3-0658-0201-s018785 | reverse | revenue | 5 | pending |
| line-3 | line-3-0485-0559-s010028 | forward | spare | 1 | pending |
| line-3 | line-3-0485-0559-s010028 | reverse | spare | 1 | pending |
| line-3 | line-3-0545-0436-s013032 | forward | spare | 1 | pending |
| line-3 | line-3-0545-0436-s013032 | reverse | spare | 1 | pending |
| line-3 | line-3-0605-0314-s016039 | forward | spare | 1 | pending |
| line-3 | line-3-0605-0314-s016039 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**134 trainsets exceed the reference platform envelope**, requiring **7,973.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0335-0312-s022955 | 5 | 2 | 3 | 178.5 |
| line-1-0399-0380-s020842 | 11 | 2 | 9 | 535.5 |
| line-1-0464-0450-s018716 | 12 | 2 | 10 | 595.0 |
| line-1-0528-0518-s016603 | 12 | 2 | 10 | 595.0 |
| line-1-0621-0617-s013595 | 12 | 2 | 10 | 595.0 |
| line-1-0821-0831-s007014 | 12 | 2 | 10 | 595.0 |
| line-1-0939-1100-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0412-0236-s012368 | 6 | 2 | 4 | 238.0 |
| line-2-0643-0386-s006212 | 12 | 2 | 10 | 595.0 |
| line-2-0756-0460-s003198 | 14 | 2 | 12 | 714.0 |
| line-2-0876-0538-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0354-0936-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0425-0682-s007012 | 12 | 2 | 10 | 595.0 |
| line-3-0485-0559-s010028 | 12 | 2 | 10 | 595.0 |
| line-3-0545-0436-s013032 | 12 | 2 | 10 | 595.0 |
| line-3-0605-0314-s016039 | 12 | 2 | 10 | 595.0 |
| line-3-0658-0201-s018785 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Taif/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
