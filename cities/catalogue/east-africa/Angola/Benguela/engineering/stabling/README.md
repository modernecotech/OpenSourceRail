# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 113 at depots = 151 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0800-0524-s020499 | line-1 | declared-depot | 47 | 2,796.5 | 9 |
| line-2-0447-0786-s000000 | line-2 | declared-depot | 38 | 2,261.0 | 8 |
| line-3-0555-0587-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0065-1050-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0302-0864-s007007 | station | forward | revenue | 1 |
| line-1 | line-1-0302-0864-s007007 | station | reverse | revenue | 1 |
| line-1 | line-1-0415-0787-s010057 | station | forward | revenue | 1 |
| line-1 | line-1-0415-0787-s010057 | station | reverse | revenue | 1 |
| line-1 | line-1-0463-0755-s011353 | station | forward | revenue | 1 |
| line-1 | line-1-0463-0755-s011353 | station | reverse | revenue | 1 |
| line-1 | line-1-0581-0674-s014560 | station | forward | revenue | 1 |
| line-1 | line-1-0581-0674-s014560 | station | reverse | revenue | 1 |
| line-1 | line-1-0625-0644-s015764 | station | forward | revenue | 1 |
| line-1 | line-1-0625-0644-s015764 | station | reverse | revenue | 1 |
| line-1 | line-1-0691-0598-s017565 | station | forward | revenue | 1 |
| line-1 | line-1-0691-0598-s017565 | station | reverse | revenue | 1 |
| line-1 | line-1-0800-0524-s020499 | station | reverse | revenue | 2 |
| line-2 | line-2-0447-0786-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0463-0755-s000753 | station | forward | revenue | 1 |
| line-2 | line-2-0463-0755-s000753 | station | reverse | revenue | 1 |
| line-2 | line-2-0512-0663-s003022 | station | forward | revenue | 1 |
| line-2 | line-2-0512-0663-s003022 | station | reverse | revenue | 1 |
| line-2 | line-2-0564-0563-s005535 | station | forward | revenue | 1 |
| line-2 | line-2-0564-0563-s005535 | station | reverse | revenue | 1 |
| line-2 | line-2-0621-0456-s008299 | station | forward | revenue | 1 |
| line-2 | line-2-0621-0456-s008299 | station | reverse | revenue | 1 |
| line-2 | line-2-0683-0347-s011075 | station | forward | revenue | 1 |
| line-2 | line-2-0683-0347-s011075 | station | reverse | revenue | 1 |
| line-2 | line-2-0743-0111-s016590 | station | reverse | revenue | 2 |
| line-3 | line-3-0555-0587-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0625-0644-s001999 | station | forward | revenue | 1 |
| line-3 | line-3-0625-0644-s001999 | station | reverse | revenue | 1 |
| line-3 | line-3-0726-0726-s004935 | station | forward | revenue | 1 |
| line-3 | line-3-0726-0726-s004935 | station | reverse | revenue | 1 |
| line-3 | line-3-0901-0910-s010843 | station | reverse | revenue | 2 |
| line-1 | line-1-0800-0524-s020499 | depot | — | revenue | 41 |
| line-1 | line-1-0800-0524-s020499 | depot | — | spare | 5 |
| line-1 | line-1-0800-0524-s020499 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0447-0786-s000000 | depot | — | revenue | 33 |
| line-2 | line-2-0447-0786-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0447-0786-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0555-0587-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0555-0587-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0555-0587-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/benguela-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **151 trainsets at 19 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **136 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **113 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0065-1050-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0302-0864-s007007 | forward | revenue | 4 | pending |
| line-1 | line-1-0302-0864-s007007 | reverse | revenue | 4 | pending |
| line-1 | line-1-0415-0787-s010057 | forward | revenue | 4 | pending |
| line-1 | line-1-0415-0787-s010057 | reverse | revenue | 4 | pending |
| line-1 | line-1-0463-0755-s011353 | forward | revenue | 4 | pending |
| line-1 | line-1-0463-0755-s011353 | reverse | revenue | 4 | pending |
| line-1 | line-1-0581-0674-s014560 | forward | revenue | 4 | pending |
| line-1 | line-1-0581-0674-s014560 | reverse | revenue | 4 | pending |
| line-1 | line-1-0625-0644-s015764 | forward | revenue | 4 | pending |
| line-1 | line-1-0625-0644-s015764 | reverse | revenue | 4 | pending |
| line-1 | line-1-0691-0598-s017565 | forward | revenue | 4 | pending |
| line-1 | line-1-0691-0598-s017565 | reverse | revenue | 4 | pending |
| line-1 | line-1-0800-0524-s020499 | reverse | revenue | 4 | pending |
| line-1 | line-1-0302-0864-s007007 | forward | spare | 1 | pending |
| line-1 | line-1-0302-0864-s007007 | reverse | spare | 1 | pending |
| line-1 | line-1-0415-0787-s010057 | forward | spare | 1 | pending |
| line-1 | line-1-0415-0787-s010057 | reverse | spare | 1 | pending |
| line-1 | line-1-0463-0755-s011353 | forward | spare | 1 | pending |
| line-1 | line-1-0463-0755-s011353 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0447-0786-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0463-0755-s000753 | forward | revenue | 4 | pending |
| line-2 | line-2-0463-0755-s000753 | reverse | revenue | 4 | pending |
| line-2 | line-2-0512-0663-s003022 | forward | revenue | 4 | pending |
| line-2 | line-2-0512-0663-s003022 | reverse | revenue | 4 | pending |
| line-2 | line-2-0564-0563-s005535 | forward | revenue | 4 | pending |
| line-2 | line-2-0564-0563-s005535 | reverse | revenue | 4 | pending |
| line-2 | line-2-0621-0456-s008299 | forward | revenue | 4 | pending |
| line-2 | line-2-0621-0456-s008299 | reverse | revenue | 4 | pending |
| line-2 | line-2-0683-0347-s011075 | forward | revenue | 4 | pending |
| line-2 | line-2-0683-0347-s011075 | reverse | revenue | 4 | pending |
| line-2 | line-2-0743-0111-s016590 | reverse | revenue | 3 | pending |
| line-2 | line-2-0743-0111-s016590 | reverse | spare | 1 | pending |
| line-2 | line-2-0447-0786-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0463-0755-s000753 | forward | spare | 1 | pending |
| line-2 | line-2-0463-0755-s000753 | reverse | spare | 1 | pending |
| line-2 | line-2-0512-0663-s003022 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0555-0587-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0625-0644-s001999 | forward | revenue | 6 | pending |
| line-3 | line-3-0625-0644-s001999 | reverse | revenue | 5 | pending |
| line-3 | line-3-0726-0726-s004935 | forward | revenue | 5 | pending |
| line-3 | line-3-0726-0726-s004935 | reverse | revenue | 5 | pending |
| line-3 | line-3-0901-0910-s010843 | reverse | revenue | 5 | pending |
| line-3 | line-3-0625-0644-s001999 | reverse | spare | 1 | pending |
| line-3 | line-3-0726-0726-s004935 | forward | spare | 1 | pending |
| line-3 | line-3-0726-0726-s004935 | reverse | spare | 1 | pending |
| line-3 | line-3-0901-0910-s010843 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**101 trainsets exceed the reference platform envelope**, requiring **6,009.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0065-1050-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0302-0864-s007007 | 10 | 2 | 8 | 476.0 |
| line-1-0415-0787-s010057 | 10 | 4 | 6 | 357.0 |
| line-1-0463-0755-s011353 | 10 | 4 | 6 | 357.0 |
| line-1-0581-0674-s014560 | 8 | 2 | 6 | 357.0 |
| line-1-0625-0644-s015764 | 8 | 4 | 4 | 238.0 |
| line-1-0691-0598-s017565 | 8 | 2 | 6 | 357.0 |
| line-1-0800-0524-s020499 | 4 | 2 | 2 | 119.0 |
| line-2-0447-0786-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0463-0755-s000753 | 10 | 4 | 6 | 357.0 |
| line-2-0512-0663-s003022 | 9 | 2 | 7 | 416.5 |
| line-2-0564-0563-s005535 | 8 | 4 | 4 | 238.0 |
| line-2-0621-0456-s008299 | 8 | 2 | 6 | 357.0 |
| line-2-0683-0347-s011075 | 8 | 2 | 6 | 357.0 |
| line-2-0743-0111-s016590 | 4 | 2 | 2 | 119.0 |
| line-3-0555-0587-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0625-0644-s001999 | 12 | 4 | 8 | 476.0 |
| line-3-0726-0726-s004935 | 12 | 2 | 10 | 595.0 |
| line-3-0901-0910-s010843 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Benguela/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
