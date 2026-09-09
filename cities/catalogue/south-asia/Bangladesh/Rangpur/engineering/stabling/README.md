# Station and depot overnight allocation

Plan: **36 trainsets at stations + 63 at depots = 99 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0412-0263-s013371 | line-1 | storage-at-existing-powered-service-point | 18 | 1,071.0 | 0 |
| line-2-0785-0507-s017696 | line-2 | declared-depot | 23 | 1,368.5 | 15 |
| line-3-0191-0361-s014899 | line-3 | storage-at-existing-powered-service-point | 22 | 1,309.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0412-0263-s013371 | station | reverse | revenue | 2 |
| line-1 | line-1-0461-0336-s011196 | station | forward | revenue | 1 |
| line-1 | line-1-0461-0336-s011196 | station | reverse | revenue | 1 |
| line-1 | line-1-0495-0424-s009018 | station | forward | revenue | 1 |
| line-1 | line-1-0495-0424-s009018 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0543-s005827 | station | forward | revenue | 1 |
| line-1 | line-1-0548-0543-s005827 | station | reverse | revenue | 1 |
| line-1 | line-1-0592-0640-s003015 | station | forward | revenue | 1 |
| line-1 | line-1-0592-0640-s003015 | station | reverse | revenue | 1 |
| line-1 | line-1-0594-0760-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0169-0808-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0307-0732-s003510 | station | forward | revenue | 1 |
| line-2 | line-2-0307-0732-s003510 | station | reverse | revenue | 1 |
| line-2 | line-2-0423-0637-s007025 | station | forward | revenue | 1 |
| line-2 | line-2-0423-0637-s007025 | station | reverse | revenue | 1 |
| line-2 | line-2-0548-0543-s010721 | station | forward | revenue | 1 |
| line-2 | line-2-0548-0543-s010721 | station | reverse | revenue | 1 |
| line-2 | line-2-0626-0527-s013054 | station | forward | revenue | 1 |
| line-2 | line-2-0626-0527-s013054 | station | reverse | revenue | 1 |
| line-2 | line-2-0699-0487-s015375 | station | forward | revenue | 1 |
| line-2 | line-2-0699-0487-s015375 | station | reverse | revenue | 1 |
| line-2 | line-2-0785-0507-s017696 | station | reverse | revenue | 2 |
| line-3 | line-3-0191-0361-s014899 | station | reverse | revenue | 2 |
| line-3 | line-3-0428-0455-s009037 | station | forward | revenue | 1 |
| line-3 | line-3-0428-0455-s009037 | station | reverse | revenue | 1 |
| line-3 | line-3-0548-0543-s005766 | station | forward | revenue | 1 |
| line-3 | line-3-0548-0543-s005766 | station | reverse | revenue | 1 |
| line-3 | line-3-0608-0448-s003005 | station | forward | revenue | 1 |
| line-3 | line-3-0608-0448-s003005 | station | reverse | revenue | 1 |
| line-3 | line-3-0698-0406-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0412-0263-s013371 | depot | — | revenue | 15 |
| line-1 | line-1-0412-0263-s013371 | depot | — | spare | 2 |
| line-1 | line-1-0412-0263-s013371 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0785-0507-s017696 | depot | — | revenue | 19 |
| line-2 | line-2-0785-0507-s017696 | depot | — | spare | 3 |
| line-2 | line-2-0785-0507-s017696 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0191-0361-s014899 | depot | — | revenue | 19 |
| line-3 | line-3-0191-0361-s014899 | depot | — | spare | 2 |
| line-3 | line-3-0191-0361-s014899 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/rangpur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **99 trainsets at 18 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **89 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **63 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0594-0760-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0592-0640-s003015 | forward | revenue | 3 | pending |
| line-1 | line-1-0592-0640-s003015 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0543-s005827 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0543-s005827 | reverse | revenue | 3 | pending |
| line-1 | line-1-0495-0424-s009018 | forward | revenue | 3 | pending |
| line-1 | line-1-0495-0424-s009018 | reverse | revenue | 3 | pending |
| line-1 | line-1-0461-0336-s011196 | forward | revenue | 2 | pending |
| line-1 | line-1-0461-0336-s011196 | reverse | revenue | 2 | pending |
| line-1 | line-1-0412-0263-s013371 | reverse | revenue | 2 | pending |
| line-1 | line-1-0461-0336-s011196 | forward | spare | 1 | pending |
| line-1 | line-1-0461-0336-s011196 | reverse | spare | 1 | pending |
| line-1 | line-1-0412-0263-s013371 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0169-0808-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0307-0732-s003510 | forward | revenue | 3 | pending |
| line-2 | line-2-0307-0732-s003510 | reverse | revenue | 3 | pending |
| line-2 | line-2-0423-0637-s007025 | forward | revenue | 3 | pending |
| line-2 | line-2-0423-0637-s007025 | reverse | revenue | 3 | pending |
| line-2 | line-2-0548-0543-s010721 | forward | revenue | 3 | pending |
| line-2 | line-2-0548-0543-s010721 | reverse | revenue | 3 | pending |
| line-2 | line-2-0626-0527-s013054 | forward | revenue | 3 | pending |
| line-2 | line-2-0626-0527-s013054 | reverse | revenue | 3 | pending |
| line-2 | line-2-0699-0487-s015375 | forward | revenue | 2 | pending |
| line-2 | line-2-0699-0487-s015375 | reverse | revenue | 2 | pending |
| line-2 | line-2-0785-0507-s017696 | reverse | revenue | 2 | pending |
| line-2 | line-2-0699-0487-s015375 | forward | spare | 1 | pending |
| line-2 | line-2-0699-0487-s015375 | reverse | spare | 1 | pending |
| line-2 | line-2-0785-0507-s017696 | reverse | spare | 1 | pending |
| line-2 | line-2-0169-0808-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0698-0406-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0608-0448-s003005 | forward | revenue | 4 | pending |
| line-3 | line-3-0608-0448-s003005 | reverse | revenue | 4 | pending |
| line-3 | line-3-0548-0543-s005766 | forward | revenue | 4 | pending |
| line-3 | line-3-0548-0543-s005766 | reverse | revenue | 4 | pending |
| line-3 | line-3-0428-0455-s009037 | forward | revenue | 3 | pending |
| line-3 | line-3-0428-0455-s009037 | reverse | revenue | 3 | pending |
| line-3 | line-3-0191-0361-s014899 | reverse | revenue | 3 | pending |
| line-3 | line-3-0428-0455-s009037 | forward | spare | 1 | pending |
| line-3 | line-3-0428-0455-s009037 | reverse | spare | 1 | pending |
| line-3 | line-3-0191-0361-s014899 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**57 trainsets exceed the reference platform envelope**, requiring **3,391.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0412-0263-s013371 | 3 | 2 | 1 | 59.5 |
| line-1-0461-0336-s011196 | 6 | 2 | 4 | 238.0 |
| line-1-0495-0424-s009018 | 6 | 2 | 4 | 238.0 |
| line-1-0548-0543-s005827 | 6 | 4 | 2 | 119.0 |
| line-1-0592-0640-s003015 | 6 | 2 | 4 | 238.0 |
| line-1-0594-0760-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0169-0808-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0307-0732-s003510 | 6 | 2 | 4 | 238.0 |
| line-2-0423-0637-s007025 | 6 | 2 | 4 | 238.0 |
| line-2-0548-0543-s010721 | 6 | 4 | 2 | 119.0 |
| line-2-0626-0527-s013054 | 6 | 2 | 4 | 238.0 |
| line-2-0699-0487-s015375 | 6 | 2 | 4 | 238.0 |
| line-2-0785-0507-s017696 | 3 | 2 | 1 | 59.5 |
| line-3-0191-0361-s014899 | 4 | 2 | 2 | 119.0 |
| line-3-0428-0455-s009037 | 8 | 2 | 6 | 357.0 |
| line-3-0548-0543-s005766 | 8 | 4 | 4 | 238.0 |
| line-3-0608-0448-s003005 | 8 | 2 | 6 | 357.0 |
| line-3-0698-0406-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Rangpur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
