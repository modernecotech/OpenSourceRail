# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 98 at depots = 124 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0703-0822-s020752 | line-1 | declared-depot | 54 | 3,213.0 | 10 |
| line-2-0449-0338-s000000 | line-2 | declared-depot | 23 | 1,368.5 | 4 |
| line-3-0861-0445-s000000 | line-3 | declared-depot | 21 | 1,249.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0151-0084-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0327-0332-s007005 | station | forward | revenue | 1 |
| line-1 | line-1-0327-0332-s007005 | station | reverse | revenue | 1 |
| line-1 | line-1-0452-0496-s011578 | station | forward | revenue | 1 |
| line-1 | line-1-0452-0496-s011578 | station | reverse | revenue | 1 |
| line-1 | line-1-0534-0603-s014585 | station | forward | revenue | 1 |
| line-1 | line-1-0534-0603-s014585 | station | reverse | revenue | 1 |
| line-1 | line-1-0591-0676-s016646 | station | forward | revenue | 1 |
| line-1 | line-1-0591-0676-s016646 | station | reverse | revenue | 1 |
| line-1 | line-1-0648-0750-s018704 | station | forward | revenue | 1 |
| line-1 | line-1-0648-0750-s018704 | station | reverse | revenue | 1 |
| line-1 | line-1-0703-0822-s020752 | station | reverse | revenue | 2 |
| line-2 | line-2-0449-0338-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0571-0395-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0571-0395-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0814-0509-s008927 | station | reverse | revenue | 2 |
| line-3 | line-3-0590-0702-s008381 | station | reverse | revenue | 2 |
| line-3 | line-3-0676-0620-s005736 | station | forward | revenue | 1 |
| line-3 | line-3-0676-0620-s005736 | station | reverse | revenue | 1 |
| line-3 | line-3-0861-0445-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0703-0822-s020752 | depot | — | revenue | 47 |
| line-1 | line-1-0703-0822-s020752 | depot | — | spare | 6 |
| line-1 | line-1-0703-0822-s020752 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0449-0338-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0449-0338-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0449-0338-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0861-0445-s000000 | depot | — | revenue | 18 |
| line-3 | line-3-0861-0445-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0861-0445-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sukkur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **124 trainsets at 13 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **111 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **98 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0151-0084-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0327-0332-s007005 | forward | revenue | 5 | pending |
| line-1 | line-1-0327-0332-s007005 | reverse | revenue | 5 | pending |
| line-1 | line-1-0452-0496-s011578 | forward | revenue | 5 | pending |
| line-1 | line-1-0452-0496-s011578 | reverse | revenue | 5 | pending |
| line-1 | line-1-0534-0603-s014585 | forward | revenue | 5 | pending |
| line-1 | line-1-0534-0603-s014585 | reverse | revenue | 5 | pending |
| line-1 | line-1-0591-0676-s016646 | forward | revenue | 5 | pending |
| line-1 | line-1-0591-0676-s016646 | reverse | revenue | 5 | pending |
| line-1 | line-1-0648-0750-s018704 | forward | revenue | 5 | pending |
| line-1 | line-1-0648-0750-s018704 | reverse | revenue | 5 | pending |
| line-1 | line-1-0703-0822-s020752 | reverse | revenue | 5 | pending |
| line-1 | line-1-0327-0332-s007005 | forward | spare | 1 | pending |
| line-1 | line-1-0327-0332-s007005 | reverse | spare | 1 | pending |
| line-1 | line-1-0452-0496-s011578 | forward | spare | 1 | pending |
| line-1 | line-1-0452-0496-s011578 | reverse | spare | 1 | pending |
| line-1 | line-1-0534-0603-s014585 | forward | spare | 1 | pending |
| line-1 | line-1-0534-0603-s014585 | reverse | spare | 1 | pending |
| line-1 | line-1-0591-0676-s016646 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0449-0338-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0571-0395-s003006 | forward | revenue | 7 | pending |
| line-2 | line-2-0571-0395-s003006 | reverse | revenue | 6 | pending |
| line-2 | line-2-0814-0509-s008927 | reverse | revenue | 6 | pending |
| line-2 | line-2-0571-0395-s003006 | reverse | spare | 1 | pending |
| line-2 | line-2-0814-0509-s008927 | reverse | spare | 1 | pending |
| line-2 | line-2-0449-0338-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0861-0445-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0676-0620-s005736 | forward | revenue | 6 | pending |
| line-3 | line-3-0676-0620-s005736 | reverse | revenue | 6 | pending |
| line-3 | line-3-0590-0702-s008381 | reverse | revenue | 6 | pending |
| line-3 | line-3-0861-0445-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0676-0620-s005736 | forward | spare | 1 | pending |
| line-3 | line-3-0676-0620-s005736 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**96 trainsets exceed the reference platform envelope**, requiring **5,712.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0151-0084-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0327-0332-s007005 | 12 | 2 | 10 | 595.0 |
| line-1-0452-0496-s011578 | 12 | 2 | 10 | 595.0 |
| line-1-0534-0603-s014585 | 12 | 2 | 10 | 595.0 |
| line-1-0591-0676-s016646 | 11 | 4 | 7 | 416.5 |
| line-1-0648-0750-s018704 | 10 | 2 | 8 | 476.0 |
| line-1-0703-0822-s020752 | 5 | 2 | 3 | 178.5 |
| line-2-0449-0338-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0571-0395-s003006 | 14 | 2 | 12 | 714.0 |
| line-2-0814-0509-s008927 | 7 | 2 | 5 | 297.5 |
| line-3-0590-0702-s008381 | 6 | 2 | 4 | 238.0 |
| line-3-0676-0620-s005736 | 14 | 2 | 12 | 714.0 |
| line-3-0861-0445-s000000 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Sukkur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
