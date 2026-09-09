# Station and depot overnight allocation

Plan: **26 trainsets at stations + 44 at depots = 70 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0723-0266-s012357 | 44 | 2,618.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0558-0547-s004364 | station | forward | revenue | 1 |
| line-1 | line-1-0558-0547-s004364 | station | reverse | revenue | 1 |
| line-1 | line-1-0580-0580-s003009 | station | forward | revenue | 1 |
| line-1 | line-1-0580-0580-s003009 | station | reverse | revenue | 1 |
| line-1 | line-1-0608-0494-s006014 | station | forward | revenue | 1 |
| line-1 | line-1-0608-0494-s006014 | station | reverse | revenue | 1 |
| line-1 | line-1-0615-0713-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0723-0266-s012357 | station | reverse | revenue | 2 |
| line-2 | line-2-0569-0455-s003334 | station | forward | revenue | 1 |
| line-2 | line-2-0569-0455-s003334 | station | reverse | revenue | 1 |
| line-2 | line-2-0575-0330-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0588-0545-s006336 | station | forward | revenue | 1 |
| line-2 | line-2-0588-0545-s006336 | station | reverse | revenue | 1 |
| line-2 | line-2-0657-0561-s008063 | station | reverse | revenue | 2 |
| line-3 | line-3-0541-0610-s011521 | station | reverse | revenue | 2 |
| line-3 | line-3-0592-0549-s009229 | station | forward | revenue | 1 |
| line-3 | line-3-0592-0549-s009229 | station | reverse | revenue | 1 |
| line-3 | line-3-0715-0482-s006214 | station | forward | revenue | 1 |
| line-3 | line-3-0715-0482-s006214 | station | reverse | revenue | 1 |
| line-3 | line-3-0879-0306-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0723-0266-s012357 | depot | — | revenue | 14 |
| line-1 | line-1-0723-0266-s012357 | depot | — | spare | 2 |
| line-1 | line-1-0723-0266-s012357 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0723-0266-s012357 | depot | — | revenue | 8 |
| line-2 | line-1-0723-0266-s012357 | depot | — | spare | 1 |
| line-2 | line-1-0723-0266-s012357 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0723-0266-s012357 | depot | — | revenue | 14 |
| line-3 | line-1-0723-0266-s012357 | depot | — | spare | 2 |
| line-3 | line-1-0723-0266-s012357 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (10 trains), line-3 (17 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **70 trainsets at 13 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **62 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **44 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0615-0713-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0580-0580-s003009 | forward | revenue | 3 | pending |
| line-1 | line-1-0580-0580-s003009 | reverse | revenue | 3 | pending |
| line-1 | line-1-0558-0547-s004364 | forward | revenue | 3 | pending |
| line-1 | line-1-0558-0547-s004364 | reverse | revenue | 3 | pending |
| line-1 | line-1-0608-0494-s006014 | forward | revenue | 3 | pending |
| line-1 | line-1-0608-0494-s006014 | reverse | revenue | 3 | pending |
| line-1 | line-1-0723-0266-s012357 | reverse | revenue | 3 | pending |
| line-1 | line-1-0615-0713-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0580-0580-s003009 | forward | spare | 1 | pending |
| line-1 | line-1-0580-0580-s003009 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0575-0330-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0569-0455-s003334 | forward | revenue | 3 | pending |
| line-2 | line-2-0569-0455-s003334 | reverse | revenue | 3 | pending |
| line-2 | line-2-0588-0545-s006336 | forward | revenue | 3 | pending |
| line-2 | line-2-0588-0545-s006336 | reverse | revenue | 2 | pending |
| line-2 | line-2-0657-0561-s008063 | reverse | revenue | 2 | pending |
| line-2 | line-2-0588-0545-s006336 | reverse | spare | 1 | pending |
| line-2 | line-2-0657-0561-s008063 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0879-0306-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0715-0482-s006214 | forward | revenue | 4 | pending |
| line-3 | line-3-0715-0482-s006214 | reverse | revenue | 4 | pending |
| line-3 | line-3-0592-0549-s009229 | forward | revenue | 4 | pending |
| line-3 | line-3-0592-0549-s009229 | reverse | revenue | 3 | pending |
| line-3 | line-3-0541-0610-s011521 | reverse | revenue | 3 | pending |
| line-3 | line-3-0592-0549-s009229 | reverse | spare | 1 | pending |
| line-3 | line-3-0541-0610-s011521 | reverse | spare | 1 | pending |
| line-3 | line-3-0879-0306-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**40 trainsets exceed the reference platform envelope**, requiring **2,380.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0558-0547-s004364 | 6 | 2 | 4 | 238.0 |
| line-1-0580-0580-s003009 | 8 | 2 | 6 | 357.0 |
| line-1-0608-0494-s006014 | 6 | 2 | 4 | 238.0 |
| line-1-0615-0713-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0723-0266-s012357 | 3 | 2 | 1 | 59.5 |
| line-2-0569-0455-s003334 | 6 | 2 | 4 | 238.0 |
| line-2-0575-0330-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0588-0545-s006336 | 6 | 4 | 2 | 119.0 |
| line-2-0657-0561-s008063 | 3 | 2 | 1 | 59.5 |
| line-3-0541-0610-s011521 | 4 | 2 | 2 | 119.0 |
| line-3-0592-0549-s009229 | 8 | 4 | 4 | 238.0 |
| line-3-0715-0482-s006214 | 8 | 2 | 6 | 357.0 |
| line-3-0879-0306-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Aba-Ng/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
