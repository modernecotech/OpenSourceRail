# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 173 at depots = 217 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0215-0118-s026210 | line-1 | declared-depot | 64 | 3,808.0 | 11 |
| line-2-0265-0473-s000000 | line-2 | declared-depot | 47 | 2,796.5 | 9 |
| line-3-0383-0212-s000000 | line-3 | declared-depot | 62 | 3,689.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0118-s026210 | station | reverse | revenue | 2 |
| line-1 | line-1-0448-0475-s016480 | station | forward | revenue | 1 |
| line-1 | line-1-0448-0475-s016480 | station | reverse | revenue | 1 |
| line-1 | line-1-0539-0584-s013312 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0584-s013312 | station | reverse | revenue | 1 |
| line-1 | line-1-0612-0672-s010748 | station | forward | revenue | 1 |
| line-1 | line-1-0612-0672-s010748 | station | reverse | revenue | 1 |
| line-1 | line-1-0698-0776-s007745 | station | forward | revenue | 1 |
| line-1 | line-1-0698-0776-s007745 | station | reverse | revenue | 1 |
| line-1 | line-1-0758-0848-s005644 | station | forward | revenue | 1 |
| line-1 | line-1-0758-0848-s005644 | station | reverse | revenue | 1 |
| line-1 | line-1-0829-0908-s003556 | station | forward | revenue | 1 |
| line-1 | line-1-0829-0908-s003556 | station | reverse | revenue | 1 |
| line-1 | line-1-0914-1037-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0265-0473-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0371-0556-s003018 | station | forward | revenue | 1 |
| line-2 | line-2-0371-0556-s003018 | station | reverse | revenue | 1 |
| line-2 | line-2-0478-0639-s006045 | station | forward | revenue | 1 |
| line-2 | line-2-0478-0639-s006045 | station | reverse | revenue | 1 |
| line-2 | line-2-0584-0722-s009052 | station | forward | revenue | 1 |
| line-2 | line-2-0584-0722-s009052 | station | reverse | revenue | 1 |
| line-2 | line-2-0690-0805-s012059 | station | forward | revenue | 1 |
| line-2 | line-2-0690-0805-s012059 | station | reverse | revenue | 1 |
| line-2 | line-2-0795-0887-s015061 | station | forward | revenue | 1 |
| line-2 | line-2-0795-0887-s015061 | station | reverse | revenue | 1 |
| line-2 | line-2-0894-1095-s020388 | station | reverse | revenue | 2 |
| line-3 | line-3-0383-0212-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0506-0374-s004490 | station | forward | revenue | 1 |
| line-3 | line-3-0506-0374-s004490 | station | reverse | revenue | 1 |
| line-3 | line-3-0584-0485-s007508 | station | forward | revenue | 1 |
| line-3 | line-3-0584-0485-s007508 | station | reverse | revenue | 1 |
| line-3 | line-3-0662-0595-s010518 | station | forward | revenue | 1 |
| line-3 | line-3-0662-0595-s010518 | station | reverse | revenue | 1 |
| line-3 | line-3-0753-0724-s014028 | station | forward | revenue | 1 |
| line-3 | line-3-0753-0724-s014028 | station | reverse | revenue | 1 |
| line-3 | line-3-0844-0853-s017538 | station | forward | revenue | 1 |
| line-3 | line-3-0844-0853-s017538 | station | reverse | revenue | 1 |
| line-3 | line-3-1082-1083-s025140 | station | reverse | revenue | 2 |
| line-1 | line-1-0215-0118-s026210 | depot | — | revenue | 56 |
| line-1 | line-1-0215-0118-s026210 | depot | — | spare | 7 |
| line-1 | line-1-0215-0118-s026210 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0265-0473-s000000 | depot | — | revenue | 41 |
| line-2 | line-2-0265-0473-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0265-0473-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0383-0212-s000000 | depot | — | revenue | 55 |
| line-3 | line-3-0383-0212-s000000 | depot | — | spare | 6 |
| line-3 | line-3-0383-0212-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/pokhara-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **217 trainsets at 22 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **196 revenue, 18 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **173 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0914-1037-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0829-0908-s003556 | forward | revenue | 6 | pending |
| line-1 | line-1-0829-0908-s003556 | reverse | revenue | 5 | pending |
| line-1 | line-1-0758-0848-s005644 | forward | revenue | 5 | pending |
| line-1 | line-1-0758-0848-s005644 | reverse | revenue | 5 | pending |
| line-1 | line-1-0698-0776-s007745 | forward | revenue | 5 | pending |
| line-1 | line-1-0698-0776-s007745 | reverse | revenue | 5 | pending |
| line-1 | line-1-0612-0672-s010748 | forward | revenue | 5 | pending |
| line-1 | line-1-0612-0672-s010748 | reverse | revenue | 5 | pending |
| line-1 | line-1-0539-0584-s013312 | forward | revenue | 5 | pending |
| line-1 | line-1-0539-0584-s013312 | reverse | revenue | 5 | pending |
| line-1 | line-1-0448-0475-s016480 | forward | revenue | 5 | pending |
| line-1 | line-1-0448-0475-s016480 | reverse | revenue | 5 | pending |
| line-1 | line-1-0215-0118-s026210 | reverse | revenue | 5 | pending |
| line-1 | line-1-0829-0908-s003556 | reverse | spare | 1 | pending |
| line-1 | line-1-0758-0848-s005644 | forward | spare | 1 | pending |
| line-1 | line-1-0758-0848-s005644 | reverse | spare | 1 | pending |
| line-1 | line-1-0698-0776-s007745 | forward | spare | 1 | pending |
| line-1 | line-1-0698-0776-s007745 | reverse | spare | 1 | pending |
| line-1 | line-1-0612-0672-s010748 | forward | spare | 1 | pending |
| line-1 | line-1-0612-0672-s010748 | reverse | spare | 1 | pending |
| line-1 | line-1-0539-0584-s013312 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0265-0473-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0371-0556-s003018 | forward | revenue | 5 | pending |
| line-2 | line-2-0371-0556-s003018 | reverse | revenue | 5 | pending |
| line-2 | line-2-0478-0639-s006045 | forward | revenue | 5 | pending |
| line-2 | line-2-0478-0639-s006045 | reverse | revenue | 5 | pending |
| line-2 | line-2-0584-0722-s009052 | forward | revenue | 5 | pending |
| line-2 | line-2-0584-0722-s009052 | reverse | revenue | 5 | pending |
| line-2 | line-2-0690-0805-s012059 | forward | revenue | 4 | pending |
| line-2 | line-2-0690-0805-s012059 | reverse | revenue | 4 | pending |
| line-2 | line-2-0795-0887-s015061 | forward | revenue | 4 | pending |
| line-2 | line-2-0795-0887-s015061 | reverse | revenue | 4 | pending |
| line-2 | line-2-0894-1095-s020388 | reverse | revenue | 4 | pending |
| line-2 | line-2-0690-0805-s012059 | forward | spare | 1 | pending |
| line-2 | line-2-0690-0805-s012059 | reverse | spare | 1 | pending |
| line-2 | line-2-0795-0887-s015061 | forward | spare | 1 | pending |
| line-2 | line-2-0795-0887-s015061 | reverse | spare | 1 | pending |
| line-2 | line-2-0894-1095-s020388 | reverse | spare | 1 | pending |
| line-2 | line-2-0265-0473-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0383-0212-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0506-0374-s004490 | forward | revenue | 6 | pending |
| line-3 | line-3-0506-0374-s004490 | reverse | revenue | 6 | pending |
| line-3 | line-3-0584-0485-s007508 | forward | revenue | 6 | pending |
| line-3 | line-3-0584-0485-s007508 | reverse | revenue | 6 | pending |
| line-3 | line-3-0662-0595-s010518 | forward | revenue | 6 | pending |
| line-3 | line-3-0662-0595-s010518 | reverse | revenue | 6 | pending |
| line-3 | line-3-0753-0724-s014028 | forward | revenue | 6 | pending |
| line-3 | line-3-0753-0724-s014028 | reverse | revenue | 6 | pending |
| line-3 | line-3-0844-0853-s017538 | forward | revenue | 5 | pending |
| line-3 | line-3-0844-0853-s017538 | reverse | revenue | 5 | pending |
| line-3 | line-3-1082-1083-s025140 | reverse | revenue | 5 | pending |
| line-3 | line-3-0844-0853-s017538 | forward | spare | 1 | pending |
| line-3 | line-3-0844-0853-s017538 | reverse | spare | 1 | pending |
| line-3 | line-3-1082-1083-s025140 | reverse | spare | 1 | pending |
| line-3 | line-3-0383-0212-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0506-0374-s004490 | forward | spare | 1 | pending |
| line-3 | line-3-0506-0374-s004490 | reverse | spare | 1 | pending |
| line-3 | line-3-0584-0485-s007508 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**169 trainsets exceed the reference platform envelope**, requiring **10,055.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0118-s026210 | 5 | 2 | 3 | 178.5 |
| line-1-0448-0475-s016480 | 10 | 2 | 8 | 476.0 |
| line-1-0539-0584-s013312 | 11 | 2 | 9 | 535.5 |
| line-1-0612-0672-s010748 | 12 | 2 | 10 | 595.0 |
| line-1-0698-0776-s007745 | 12 | 4 | 8 | 476.0 |
| line-1-0758-0848-s005644 | 12 | 2 | 10 | 595.0 |
| line-1-0829-0908-s003556 | 12 | 2 | 10 | 595.0 |
| line-1-0914-1037-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0265-0473-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0371-0556-s003018 | 10 | 2 | 8 | 476.0 |
| line-2-0478-0639-s006045 | 10 | 2 | 8 | 476.0 |
| line-2-0584-0722-s009052 | 10 | 2 | 8 | 476.0 |
| line-2-0690-0805-s012059 | 10 | 4 | 6 | 357.0 |
| line-2-0795-0887-s015061 | 10 | 2 | 8 | 476.0 |
| line-2-0894-1095-s020388 | 5 | 2 | 3 | 178.5 |
| line-3-0383-0212-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0506-0374-s004490 | 14 | 2 | 12 | 714.0 |
| line-3-0584-0485-s007508 | 13 | 2 | 11 | 654.5 |
| line-3-0662-0595-s010518 | 12 | 2 | 10 | 595.0 |
| line-3-0753-0724-s014028 | 12 | 2 | 10 | 595.0 |
| line-3-0844-0853-s017538 | 12 | 2 | 10 | 595.0 |
| line-3-1082-1083-s025140 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Nepal/Pokhara/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
