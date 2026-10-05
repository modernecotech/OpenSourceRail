# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 127 at depots = 165 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0308-0707-s000000 | line-1 | declared-depot | 39 | 2,320.5 | 8 |
| line-2-0332-0209-s022687 | line-2 | declared-depot | 56 | 3,332.0 | 10 |
| line-3-0424-0761-s000000 | line-3 | declared-depot | 32 | 1,904.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0308-0707-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0390-0672-s001965 | station | forward | revenue | 1 |
| line-1 | line-1-0390-0672-s001965 | station | reverse | revenue | 1 |
| line-1 | line-1-0472-0637-s003918 | station | forward | revenue | 1 |
| line-1 | line-1-0472-0637-s003918 | station | reverse | revenue | 1 |
| line-1 | line-1-0547-0605-s005719 | station | forward | revenue | 1 |
| line-1 | line-1-0547-0605-s005719 | station | reverse | revenue | 1 |
| line-1 | line-1-0623-0572-s007524 | station | forward | revenue | 1 |
| line-1 | line-1-0623-0572-s007524 | station | reverse | revenue | 1 |
| line-1 | line-1-0832-0482-s012531 | station | forward | revenue | 1 |
| line-1 | line-1-0832-0482-s012531 | station | reverse | revenue | 1 |
| line-1 | line-1-1041-0391-s017547 | station | reverse | revenue | 2 |
| line-2 | line-2-0332-0209-s022687 | station | reverse | revenue | 2 |
| line-2 | line-2-0433-0339-s018969 | station | forward | revenue | 1 |
| line-2 | line-2-0433-0339-s018969 | station | reverse | revenue | 1 |
| line-2 | line-2-0537-0466-s015263 | station | forward | revenue | 1 |
| line-2 | line-2-0537-0466-s015263 | station | reverse | revenue | 1 |
| line-2 | line-2-0623-0572-s012197 | station | forward | revenue | 1 |
| line-2 | line-2-0623-0572-s012197 | station | reverse | revenue | 1 |
| line-2 | line-2-0685-0648-s010011 | station | forward | revenue | 1 |
| line-2 | line-2-0685-0648-s010011 | station | reverse | revenue | 1 |
| line-2 | line-2-0769-0752-s007000 | station | forward | revenue | 1 |
| line-2 | line-2-0769-0752-s007000 | station | reverse | revenue | 1 |
| line-2 | line-2-0980-0964-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0424-0761-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0472-0637-s002913 | station | forward | revenue | 1 |
| line-3 | line-3-0472-0637-s002913 | station | reverse | revenue | 1 |
| line-3 | line-3-0499-0564-s004620 | station | forward | revenue | 1 |
| line-3 | line-3-0499-0564-s004620 | station | reverse | revenue | 1 |
| line-3 | line-3-0537-0466-s006930 | station | forward | revenue | 1 |
| line-3 | line-3-0537-0466-s006930 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0193-s013463 | station | reverse | revenue | 2 |
| line-1 | line-1-0308-0707-s000000 | depot | — | revenue | 34 |
| line-1 | line-1-0308-0707-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0308-0707-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0332-0209-s022687 | depot | — | revenue | 49 |
| line-2 | line-2-0332-0209-s022687 | depot | — | spare | 6 |
| line-2 | line-2-0332-0209-s022687 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0424-0761-s000000 | depot | — | revenue | 28 |
| line-3 | line-3-0424-0761-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0424-0761-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sialkot-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **165 trainsets at 19 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **149 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **127 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0308-0707-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0390-0672-s001965 | forward | revenue | 4 | pending |
| line-1 | line-1-0390-0672-s001965 | reverse | revenue | 4 | pending |
| line-1 | line-1-0472-0637-s003918 | forward | revenue | 4 | pending |
| line-1 | line-1-0472-0637-s003918 | reverse | revenue | 4 | pending |
| line-1 | line-1-0547-0605-s005719 | forward | revenue | 4 | pending |
| line-1 | line-1-0547-0605-s005719 | reverse | revenue | 4 | pending |
| line-1 | line-1-0623-0572-s007524 | forward | revenue | 4 | pending |
| line-1 | line-1-0623-0572-s007524 | reverse | revenue | 4 | pending |
| line-1 | line-1-0832-0482-s012531 | forward | revenue | 4 | pending |
| line-1 | line-1-0832-0482-s012531 | reverse | revenue | 4 | pending |
| line-1 | line-1-1041-0391-s017547 | reverse | revenue | 4 | pending |
| line-1 | line-1-0308-0707-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0390-0672-s001965 | forward | spare | 1 | pending |
| line-1 | line-1-0390-0672-s001965 | reverse | spare | 1 | pending |
| line-1 | line-1-0472-0637-s003918 | forward | spare | 1 | pending |
| line-1 | line-1-0472-0637-s003918 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0980-0964-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0769-0752-s007000 | forward | revenue | 6 | pending |
| line-2 | line-2-0769-0752-s007000 | reverse | revenue | 6 | pending |
| line-2 | line-2-0685-0648-s010011 | forward | revenue | 5 | pending |
| line-2 | line-2-0685-0648-s010011 | reverse | revenue | 5 | pending |
| line-2 | line-2-0623-0572-s012197 | forward | revenue | 5 | pending |
| line-2 | line-2-0623-0572-s012197 | reverse | revenue | 5 | pending |
| line-2 | line-2-0537-0466-s015263 | forward | revenue | 5 | pending |
| line-2 | line-2-0537-0466-s015263 | reverse | revenue | 5 | pending |
| line-2 | line-2-0433-0339-s018969 | forward | revenue | 5 | pending |
| line-2 | line-2-0433-0339-s018969 | reverse | revenue | 5 | pending |
| line-2 | line-2-0332-0209-s022687 | reverse | revenue | 5 | pending |
| line-2 | line-2-0685-0648-s010011 | forward | spare | 1 | pending |
| line-2 | line-2-0685-0648-s010011 | reverse | spare | 1 | pending |
| line-2 | line-2-0623-0572-s012197 | forward | spare | 1 | pending |
| line-2 | line-2-0623-0572-s012197 | reverse | spare | 1 | pending |
| line-2 | line-2-0537-0466-s015263 | forward | spare | 1 | pending |
| line-2 | line-2-0537-0466-s015263 | reverse | spare | 1 | pending |
| line-2 | line-2-0433-0339-s018969 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0424-0761-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0472-0637-s002913 | forward | revenue | 5 | pending |
| line-3 | line-3-0472-0637-s002913 | reverse | revenue | 5 | pending |
| line-3 | line-3-0499-0564-s004620 | forward | revenue | 5 | pending |
| line-3 | line-3-0499-0564-s004620 | reverse | revenue | 5 | pending |
| line-3 | line-3-0537-0466-s006930 | forward | revenue | 5 | pending |
| line-3 | line-3-0537-0466-s006930 | reverse | revenue | 4 | pending |
| line-3 | line-3-0658-0193-s013463 | reverse | revenue | 4 | pending |
| line-3 | line-3-0537-0466-s006930 | reverse | spare | 1 | pending |
| line-3 | line-3-0658-0193-s013463 | reverse | spare | 1 | pending |
| line-3 | line-3-0424-0761-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0472-0637-s002913 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**115 trainsets exceed the reference platform envelope**, requiring **6,842.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0308-0707-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0390-0672-s001965 | 10 | 2 | 8 | 476.0 |
| line-1-0472-0637-s003918 | 10 | 4 | 6 | 357.0 |
| line-1-0547-0605-s005719 | 8 | 2 | 6 | 357.0 |
| line-1-0623-0572-s007524 | 8 | 4 | 4 | 238.0 |
| line-1-0832-0482-s012531 | 8 | 2 | 6 | 357.0 |
| line-1-1041-0391-s017547 | 4 | 2 | 2 | 119.0 |
| line-2-0332-0209-s022687 | 5 | 2 | 3 | 178.5 |
| line-2-0433-0339-s018969 | 11 | 2 | 9 | 535.5 |
| line-2-0537-0466-s015263 | 12 | 4 | 8 | 476.0 |
| line-2-0623-0572-s012197 | 12 | 4 | 8 | 476.0 |
| line-2-0685-0648-s010011 | 12 | 2 | 10 | 595.0 |
| line-2-0769-0752-s007000 | 12 | 2 | 10 | 595.0 |
| line-2-0980-0964-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0424-0761-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0472-0637-s002913 | 11 | 4 | 7 | 416.5 |
| line-3-0499-0564-s004620 | 10 | 2 | 8 | 476.0 |
| line-3-0537-0466-s006930 | 10 | 4 | 6 | 357.0 |
| line-3-0658-0193-s013463 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Sialkot/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
