# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 90 at depots = 134 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0448-0937-s000000 | line-1 | declared-depot | 33 | 1,963.5 | 7 |
| line-2-0708-0058-s019460 | line-2 | declared-depot | 43 | 2,558.5 | 9 |
| line-3-0451-0402-s000000 | line-3 | declared-depot | 14 | 833.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0448-0937-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0521-0825-s003009 | station | forward | revenue | 1 |
| line-1 | line-1-0521-0825-s003009 | station | reverse | revenue | 1 |
| line-1 | line-1-0572-0698-s006018 | station | forward | revenue | 1 |
| line-1 | line-1-0572-0698-s006018 | station | reverse | revenue | 1 |
| line-1 | line-1-0610-0606-s008185 | station | forward | revenue | 1 |
| line-1 | line-1-0610-0606-s008185 | station | reverse | revenue | 1 |
| line-1 | line-1-0611-0603-s008253 | station | forward | revenue | 1 |
| line-1 | line-1-0611-0603-s008253 | station | reverse | revenue | 1 |
| line-1 | line-1-0674-0444-s011990 | station | forward | revenue | 1 |
| line-1 | line-1-0674-0444-s011990 | station | reverse | revenue | 1 |
| line-1 | line-1-0733-0298-s015469 | station | reverse | revenue | 2 |
| line-2 | line-2-0579-0808-s003011 | station | forward | revenue | 1 |
| line-2 | line-2-0579-0808-s003011 | station | reverse | revenue | 1 |
| line-2 | line-2-0601-0667-s006013 | station | forward | revenue | 1 |
| line-2 | line-2-0601-0667-s006013 | station | reverse | revenue | 1 |
| line-2 | line-2-0609-0917-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0610-0606-s007320 | station | forward | revenue | 1 |
| line-2 | line-2-0610-0606-s007320 | station | reverse | revenue | 1 |
| line-2 | line-2-0611-0603-s007388 | station | forward | revenue | 1 |
| line-2 | line-2-0611-0603-s007388 | station | reverse | revenue | 1 |
| line-2 | line-2-0622-0526-s009019 | station | forward | revenue | 1 |
| line-2 | line-2-0622-0526-s009019 | station | reverse | revenue | 1 |
| line-2 | line-2-0636-0437-s010915 | station | forward | revenue | 1 |
| line-2 | line-2-0636-0437-s010915 | station | reverse | revenue | 1 |
| line-2 | line-2-0651-0341-s012971 | station | forward | revenue | 1 |
| line-2 | line-2-0651-0341-s012971 | station | reverse | revenue | 1 |
| line-2 | line-2-0666-0244-s015035 | station | forward | revenue | 1 |
| line-2 | line-2-0666-0244-s015035 | station | reverse | revenue | 1 |
| line-2 | line-2-0708-0058-s019460 | station | reverse | revenue | 2 |
| line-3 | line-3-0451-0402-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0544-0420-s002009 | station | forward | revenue | 1 |
| line-3 | line-3-0544-0420-s002009 | station | reverse | revenue | 1 |
| line-3 | line-3-0636-0437-s003990 | station | forward | revenue | 1 |
| line-3 | line-3-0636-0437-s003990 | station | reverse | revenue | 1 |
| line-3 | line-3-0674-0444-s004808 | station | forward | revenue | 1 |
| line-3 | line-3-0674-0444-s004808 | station | reverse | revenue | 1 |
| line-3 | line-3-0781-0464-s007114 | station | reverse | revenue | 2 |
| line-1 | line-1-0448-0937-s000000 | depot | — | revenue | 28 |
| line-1 | line-1-0448-0937-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0448-0937-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0708-0058-s019460 | depot | — | revenue | 37 |
| line-2 | line-2-0708-0058-s019460 | depot | — | spare | 5 |
| line-2 | line-2-0708-0058-s019460 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0451-0402-s000000 | depot | — | revenue | 11 |
| line-3 | line-3-0451-0402-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0451-0402-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mbeya-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **134 trainsets at 22 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **120 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **90 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0448-0937-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0521-0825-s003009 | forward | revenue | 4 | pending |
| line-1 | line-1-0521-0825-s003009 | reverse | revenue | 4 | pending |
| line-1 | line-1-0572-0698-s006018 | forward | revenue | 4 | pending |
| line-1 | line-1-0572-0698-s006018 | reverse | revenue | 4 | pending |
| line-1 | line-1-0610-0606-s008185 | forward | revenue | 4 | pending |
| line-1 | line-1-0610-0606-s008185 | reverse | revenue | 3 | pending |
| line-1 | line-1-0611-0603-s008253 | forward | revenue | 3 | pending |
| line-1 | line-1-0611-0603-s008253 | reverse | revenue | 3 | pending |
| line-1 | line-1-0674-0444-s011990 | forward | revenue | 3 | pending |
| line-1 | line-1-0674-0444-s011990 | reverse | revenue | 3 | pending |
| line-1 | line-1-0733-0298-s015469 | reverse | revenue | 3 | pending |
| line-1 | line-1-0610-0606-s008185 | reverse | spare | 1 | pending |
| line-1 | line-1-0611-0603-s008253 | forward | spare | 1 | pending |
| line-1 | line-1-0611-0603-s008253 | reverse | spare | 1 | pending |
| line-1 | line-1-0674-0444-s011990 | forward | spare | 1 | pending |
| line-1 | line-1-0674-0444-s011990 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0609-0917-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0579-0808-s003011 | forward | revenue | 4 | pending |
| line-2 | line-2-0579-0808-s003011 | reverse | revenue | 4 | pending |
| line-2 | line-2-0601-0667-s006013 | forward | revenue | 3 | pending |
| line-2 | line-2-0601-0667-s006013 | reverse | revenue | 3 | pending |
| line-2 | line-2-0610-0606-s007320 | forward | revenue | 3 | pending |
| line-2 | line-2-0610-0606-s007320 | reverse | revenue | 3 | pending |
| line-2 | line-2-0611-0603-s007388 | forward | revenue | 3 | pending |
| line-2 | line-2-0611-0603-s007388 | reverse | revenue | 3 | pending |
| line-2 | line-2-0622-0526-s009019 | forward | revenue | 3 | pending |
| line-2 | line-2-0622-0526-s009019 | reverse | revenue | 3 | pending |
| line-2 | line-2-0636-0437-s010915 | forward | revenue | 3 | pending |
| line-2 | line-2-0636-0437-s010915 | reverse | revenue | 3 | pending |
| line-2 | line-2-0651-0341-s012971 | forward | revenue | 3 | pending |
| line-2 | line-2-0651-0341-s012971 | reverse | revenue | 3 | pending |
| line-2 | line-2-0666-0244-s015035 | forward | revenue | 3 | pending |
| line-2 | line-2-0666-0244-s015035 | reverse | revenue | 3 | pending |
| line-2 | line-2-0708-0058-s019460 | reverse | revenue | 3 | pending |
| line-2 | line-2-0601-0667-s006013 | forward | spare | 1 | pending |
| line-2 | line-2-0601-0667-s006013 | reverse | spare | 1 | pending |
| line-2 | line-2-0610-0606-s007320 | forward | spare | 1 | pending |
| line-2 | line-2-0610-0606-s007320 | reverse | spare | 1 | pending |
| line-2 | line-2-0611-0603-s007388 | forward | spare | 1 | pending |
| line-2 | line-2-0611-0603-s007388 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0451-0402-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0544-0420-s002009 | forward | revenue | 3 | pending |
| line-3 | line-3-0544-0420-s002009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0636-0437-s003990 | forward | revenue | 3 | pending |
| line-3 | line-3-0636-0437-s003990 | reverse | revenue | 3 | pending |
| line-3 | line-3-0674-0444-s004808 | forward | revenue | 2 | pending |
| line-3 | line-3-0674-0444-s004808 | reverse | revenue | 2 | pending |
| line-3 | line-3-0781-0464-s007114 | reverse | revenue | 2 | pending |
| line-3 | line-3-0674-0444-s004808 | forward | spare | 1 | pending |
| line-3 | line-3-0674-0444-s004808 | reverse | spare | 1 | pending |
| line-3 | line-3-0781-0464-s007114 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**74 trainsets exceed the reference platform envelope**, requiring **4,403.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0448-0937-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0521-0825-s003009 | 8 | 2 | 6 | 357.0 |
| line-1-0572-0698-s006018 | 8 | 2 | 6 | 357.0 |
| line-1-0610-0606-s008185 | 8 | 4 | 4 | 238.0 |
| line-1-0611-0603-s008253 | 8 | 4 | 4 | 238.0 |
| line-1-0674-0444-s011990 | 8 | 4 | 4 | 238.0 |
| line-1-0733-0298-s015469 | 3 | 2 | 1 | 59.5 |
| line-2-0579-0808-s003011 | 8 | 2 | 6 | 357.0 |
| line-2-0601-0667-s006013 | 8 | 2 | 6 | 357.0 |
| line-2-0609-0917-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0610-0606-s007320 | 8 | 4 | 4 | 238.0 |
| line-2-0611-0603-s007388 | 8 | 4 | 4 | 238.0 |
| line-2-0622-0526-s009019 | 6 | 2 | 4 | 238.0 |
| line-2-0636-0437-s010915 | 6 | 4 | 2 | 119.0 |
| line-2-0651-0341-s012971 | 6 | 2 | 4 | 238.0 |
| line-2-0666-0244-s015035 | 6 | 2 | 4 | 238.0 |
| line-2-0708-0058-s019460 | 3 | 2 | 1 | 59.5 |
| line-3-0451-0402-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0544-0420-s002009 | 6 | 2 | 4 | 238.0 |
| line-3-0636-0437-s003990 | 6 | 4 | 2 | 119.0 |
| line-3-0674-0444-s004808 | 6 | 4 | 2 | 119.0 |
| line-3-0781-0464-s007114 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Mbeya/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
