# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 138 at depots = 182 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0835-0580-s000000 | line-1 | declared-depot | 39 | 2,320.5 | 8 |
| line-2-0769-0425-s000000 | line-2 | declared-depot | 35 | 2,082.5 | 7 |
| line-3-0646-0668-s016547 | line-3 | declared-depot | 40 | 2,380.0 | 8 |
| line-4-0546-0468-s000000 | line-4 | declared-depot | 12 | 714.0 | 3 |
| line-5-0567-0509-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0224-0492-s016498 | station | reverse | revenue | 2 |
| line-1 | line-1-0302-0526-s014170 | station | forward | revenue | 1 |
| line-1 | line-1-0302-0526-s014170 | station | reverse | revenue | 1 |
| line-1 | line-1-0415-0524-s011861 | station | forward | revenue | 1 |
| line-1 | line-1-0415-0524-s011861 | station | reverse | revenue | 1 |
| line-1 | line-1-0596-0568-s007165 | station | forward | revenue | 1 |
| line-1 | line-1-0596-0568-s007165 | station | reverse | revenue | 1 |
| line-1 | line-1-0672-0571-s005104 | station | forward | revenue | 1 |
| line-1 | line-1-0672-0571-s005104 | station | reverse | revenue | 1 |
| line-1 | line-1-0835-0580-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0439-0983-s014602 | station | reverse | revenue | 2 |
| line-2 | line-2-0518-0804-s010140 | station | forward | revenue | 1 |
| line-2 | line-2-0518-0804-s010140 | station | reverse | revenue | 1 |
| line-2 | line-2-0630-0636-s005659 | station | forward | revenue | 1 |
| line-2 | line-2-0630-0636-s005659 | station | reverse | revenue | 1 |
| line-2 | line-2-0672-0571-s003923 | station | forward | revenue | 1 |
| line-2 | line-2-0672-0571-s003923 | station | reverse | revenue | 1 |
| line-2 | line-2-0769-0425-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0288-0012-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0453-0282-s007017 | station | forward | revenue | 1 |
| line-3 | line-3-0453-0282-s007017 | station | reverse | revenue | 1 |
| line-3 | line-3-0546-0468-s011602 | station | forward | revenue | 1 |
| line-3 | line-3-0546-0468-s011602 | station | reverse | revenue | 1 |
| line-3 | line-3-0567-0509-s012619 | station | forward | revenue | 1 |
| line-3 | line-3-0567-0509-s012619 | station | reverse | revenue | 1 |
| line-3 | line-3-0596-0568-s014063 | station | forward | revenue | 1 |
| line-3 | line-3-0596-0568-s014063 | station | reverse | revenue | 1 |
| line-3 | line-3-0630-0636-s015737 | station | forward | revenue | 1 |
| line-3 | line-3-0630-0636-s015737 | station | reverse | revenue | 1 |
| line-3 | line-3-0646-0668-s016547 | station | reverse | revenue | 2 |
| line-4 | line-4-0462-0387-s004536 | station | reverse | revenue | 2 |
| line-4 | line-4-0546-0468-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0567-0509-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0711-0390-s004448 | station | reverse | revenue | 2 |
| line-1 | line-1-0835-0580-s000000 | depot | — | revenue | 34 |
| line-1 | line-1-0835-0580-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0835-0580-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0769-0425-s000000 | depot | — | revenue | 30 |
| line-2 | line-2-0769-0425-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0769-0425-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0646-0668-s016547 | depot | — | revenue | 35 |
| line-3 | line-3-0646-0668-s016547 | depot | — | spare | 4 |
| line-3 | line-3-0646-0668-s016547 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0546-0468-s000000 | depot | — | revenue | 10 |
| line-4 | line-4-0546-0468-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0546-0468-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0567-0509-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0567-0509-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0567-0509-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/dodoma-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **182 trainsets at 22 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **163 revenue, 14 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **138 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0835-0580-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0672-0571-s005104 | forward | revenue | 5 | pending |
| line-1 | line-1-0672-0571-s005104 | reverse | revenue | 5 | pending |
| line-1 | line-1-0596-0568-s007165 | forward | revenue | 5 | pending |
| line-1 | line-1-0596-0568-s007165 | reverse | revenue | 5 | pending |
| line-1 | line-1-0415-0524-s011861 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0524-s011861 | reverse | revenue | 4 | pending |
| line-1 | line-1-0302-0526-s014170 | forward | revenue | 4 | pending |
| line-1 | line-1-0302-0526-s014170 | reverse | revenue | 4 | pending |
| line-1 | line-1-0224-0492-s016498 | reverse | revenue | 4 | pending |
| line-1 | line-1-0415-0524-s011861 | reverse | spare | 1 | pending |
| line-1 | line-1-0302-0526-s014170 | forward | spare | 1 | pending |
| line-1 | line-1-0302-0526-s014170 | reverse | spare | 1 | pending |
| line-1 | line-1-0224-0492-s016498 | reverse | spare | 1 | pending |
| line-1 | line-1-0835-0580-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0769-0425-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0672-0571-s003923 | forward | revenue | 5 | pending |
| line-2 | line-2-0672-0571-s003923 | reverse | revenue | 5 | pending |
| line-2 | line-2-0630-0636-s005659 | forward | revenue | 5 | pending |
| line-2 | line-2-0630-0636-s005659 | reverse | revenue | 5 | pending |
| line-2 | line-2-0518-0804-s010140 | forward | revenue | 5 | pending |
| line-2 | line-2-0518-0804-s010140 | reverse | revenue | 5 | pending |
| line-2 | line-2-0439-0983-s014602 | reverse | revenue | 5 | pending |
| line-2 | line-2-0769-0425-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0672-0571-s003923 | forward | spare | 1 | pending |
| line-2 | line-2-0672-0571-s003923 | reverse | spare | 1 | pending |
| line-2 | line-2-0630-0636-s005659 | forward | spare | 1 | pending |
| line-2 | line-2-0630-0636-s005659 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0288-0012-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0453-0282-s007017 | forward | revenue | 4 | pending |
| line-3 | line-3-0453-0282-s007017 | reverse | revenue | 4 | pending |
| line-3 | line-3-0546-0468-s011602 | forward | revenue | 4 | pending |
| line-3 | line-3-0546-0468-s011602 | reverse | revenue | 4 | pending |
| line-3 | line-3-0567-0509-s012619 | forward | revenue | 4 | pending |
| line-3 | line-3-0567-0509-s012619 | reverse | revenue | 4 | pending |
| line-3 | line-3-0596-0568-s014063 | forward | revenue | 4 | pending |
| line-3 | line-3-0596-0568-s014063 | reverse | revenue | 4 | pending |
| line-3 | line-3-0630-0636-s015737 | forward | revenue | 4 | pending |
| line-3 | line-3-0630-0636-s015737 | reverse | revenue | 4 | pending |
| line-3 | line-3-0646-0668-s016547 | reverse | revenue | 4 | pending |
| line-3 | line-3-0453-0282-s007017 | forward | spare | 1 | pending |
| line-3 | line-3-0453-0282-s007017 | reverse | spare | 1 | pending |
| line-3 | line-3-0546-0468-s011602 | forward | spare | 1 | pending |
| line-3 | line-3-0546-0468-s011602 | reverse | spare | 1 | pending |
| line-3 | line-3-0567-0509-s012619 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0546-0468-s000000 | forward | revenue | 7 | pending |
| line-4 | line-4-0462-0387-s004536 | reverse | revenue | 7 | pending |
| line-4 | line-4-0546-0468-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0462-0387-s004536 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0567-0509-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0711-0390-s004448 | reverse | revenue | 7 | pending |
| line-5 | line-5-0567-0509-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0711-0390-s004448 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**122 trainsets exceed the reference platform envelope**, requiring **7,259.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0224-0492-s016498 | 5 | 2 | 3 | 178.5 |
| line-1-0302-0526-s014170 | 10 | 2 | 8 | 476.0 |
| line-1-0415-0524-s011861 | 10 | 2 | 8 | 476.0 |
| line-1-0596-0568-s007165 | 10 | 4 | 6 | 357.0 |
| line-1-0672-0571-s005104 | 10 | 4 | 6 | 357.0 |
| line-1-0835-0580-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0439-0983-s014602 | 5 | 2 | 3 | 178.5 |
| line-2-0518-0804-s010140 | 10 | 2 | 8 | 476.0 |
| line-2-0630-0636-s005659 | 12 | 4 | 8 | 476.0 |
| line-2-0672-0571-s003923 | 12 | 4 | 8 | 476.0 |
| line-2-0769-0425-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0288-0012-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0453-0282-s007017 | 10 | 2 | 8 | 476.0 |
| line-3-0546-0468-s011602 | 10 | 4 | 6 | 357.0 |
| line-3-0567-0509-s012619 | 9 | 4 | 5 | 297.5 |
| line-3-0596-0568-s014063 | 8 | 4 | 4 | 238.0 |
| line-3-0630-0636-s015737 | 8 | 4 | 4 | 238.0 |
| line-3-0646-0668-s016547 | 4 | 2 | 2 | 119.0 |
| line-4-0462-0387-s004536 | 8 | 2 | 6 | 357.0 |
| line-4-0546-0468-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0567-0509-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0711-0390-s004448 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Dodoma/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
