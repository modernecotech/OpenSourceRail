# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 68 at depots = 94 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0485-0820-s011238 | line-1 | declared-depot | 27 | 1,606.5 | 6 |
| line-2-0365-0585-s000000 | line-2 | declared-depot | 23 | 1,368.5 | 5 |
| line-3-0514-0433-s000000 | line-3 | declared-depot | 18 | 1,071.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0485-0820-s011238 | station | reverse | revenue | 2 |
| line-1 | line-1-0572-0745-s008642 | station | forward | revenue | 1 |
| line-1 | line-1-0572-0745-s008642 | station | reverse | revenue | 1 |
| line-1 | line-1-0660-0668-s006034 | station | forward | revenue | 1 |
| line-1 | line-1-0660-0668-s006034 | station | reverse | revenue | 1 |
| line-1 | line-1-0762-0580-s003018 | station | forward | revenue | 1 |
| line-1 | line-1-0762-0580-s003018 | station | reverse | revenue | 1 |
| line-1 | line-1-0863-0492-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0365-0585-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0452-0558-s001964 | station | forward | revenue | 1 |
| line-2 | line-2-0452-0558-s001964 | station | reverse | revenue | 1 |
| line-2 | line-2-0585-0516-s004983 | station | forward | revenue | 1 |
| line-2 | line-2-0585-0516-s004983 | station | reverse | revenue | 1 |
| line-2 | line-2-0815-0443-s010200 | station | reverse | revenue | 2 |
| line-3 | line-3-0514-0433-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0571-0552-s002899 | station | forward | revenue | 1 |
| line-3 | line-3-0571-0552-s002899 | station | reverse | revenue | 1 |
| line-3 | line-3-0619-0652-s005332 | station | forward | revenue | 1 |
| line-3 | line-3-0619-0652-s005332 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0751-s007756 | station | reverse | revenue | 2 |
| line-1 | line-1-0485-0820-s011238 | depot | — | revenue | 23 |
| line-1 | line-1-0485-0820-s011238 | depot | — | spare | 3 |
| line-1 | line-1-0485-0820-s011238 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0365-0585-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0365-0585-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0365-0585-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0514-0433-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0514-0433-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0514-0433-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/beni-suef-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **94 trainsets at 13 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **84 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **68 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0863-0492-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0762-0580-s003018 | forward | revenue | 4 | pending |
| line-1 | line-1-0762-0580-s003018 | reverse | revenue | 4 | pending |
| line-1 | line-1-0660-0668-s006034 | forward | revenue | 4 | pending |
| line-1 | line-1-0660-0668-s006034 | reverse | revenue | 4 | pending |
| line-1 | line-1-0572-0745-s008642 | forward | revenue | 4 | pending |
| line-1 | line-1-0572-0745-s008642 | reverse | revenue | 4 | pending |
| line-1 | line-1-0485-0820-s011238 | reverse | revenue | 4 | pending |
| line-1 | line-1-0762-0580-s003018 | forward | spare | 1 | pending |
| line-1 | line-1-0762-0580-s003018 | reverse | spare | 1 | pending |
| line-1 | line-1-0660-0668-s006034 | forward | spare | 1 | pending |
| line-1 | line-1-0660-0668-s006034 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0365-0585-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0452-0558-s001964 | forward | revenue | 5 | pending |
| line-2 | line-2-0452-0558-s001964 | reverse | revenue | 5 | pending |
| line-2 | line-2-0585-0516-s004983 | forward | revenue | 5 | pending |
| line-2 | line-2-0585-0516-s004983 | reverse | revenue | 4 | pending |
| line-2 | line-2-0815-0443-s010200 | reverse | revenue | 4 | pending |
| line-2 | line-2-0585-0516-s004983 | reverse | spare | 1 | pending |
| line-2 | line-2-0815-0443-s010200 | reverse | spare | 1 | pending |
| line-2 | line-2-0365-0585-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0514-0433-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0571-0552-s002899 | forward | revenue | 4 | pending |
| line-3 | line-3-0571-0552-s002899 | reverse | revenue | 4 | pending |
| line-3 | line-3-0619-0652-s005332 | forward | revenue | 4 | pending |
| line-3 | line-3-0619-0652-s005332 | reverse | revenue | 4 | pending |
| line-3 | line-3-0667-0751-s007756 | reverse | revenue | 3 | pending |
| line-3 | line-3-0667-0751-s007756 | reverse | spare | 1 | pending |
| line-3 | line-3-0514-0433-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0571-0552-s002899 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**68 trainsets exceed the reference platform envelope**, requiring **4,046.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0485-0820-s011238 | 4 | 2 | 2 | 119.0 |
| line-1-0572-0745-s008642 | 8 | 2 | 6 | 357.0 |
| line-1-0660-0668-s006034 | 10 | 2 | 8 | 476.0 |
| line-1-0762-0580-s003018 | 10 | 2 | 8 | 476.0 |
| line-1-0863-0492-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0365-0585-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0452-0558-s001964 | 10 | 2 | 8 | 476.0 |
| line-2-0585-0516-s004983 | 10 | 2 | 8 | 476.0 |
| line-2-0815-0443-s010200 | 5 | 2 | 3 | 178.5 |
| line-3-0514-0433-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0571-0552-s002899 | 9 | 2 | 7 | 416.5 |
| line-3-0619-0652-s005332 | 8 | 2 | 6 | 357.0 |
| line-3-0667-0751-s007756 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Beni-Suef/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
