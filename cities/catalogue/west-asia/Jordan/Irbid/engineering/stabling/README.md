# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 89 at depots = 119 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0840-0623-s000000 | line-1 | declared-depot | 24 | 1,428.0 | 5 |
| line-2-0700-0815-s000000 | line-2 | declared-depot | 24 | 1,428.0 | 5 |
| line-3-0944-0336-s016363 | line-3 | declared-depot | 41 | 2,439.5 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0312-0567-s011024 | station | reverse | revenue | 2 |
| line-1 | line-1-0432-0580-s008516 | station | forward | revenue | 1 |
| line-1 | line-1-0432-0580-s008516 | station | reverse | revenue | 1 |
| line-1 | line-1-0552-0592-s006017 | station | forward | revenue | 1 |
| line-1 | line-1-0552-0592-s006017 | station | reverse | revenue | 1 |
| line-1 | line-1-0696-0608-s003004 | station | forward | revenue | 1 |
| line-1 | line-1-0696-0608-s003004 | station | reverse | revenue | 1 |
| line-1 | line-1-0840-0623-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0634-0323-s010387 | station | reverse | revenue | 2 |
| line-2 | line-2-0650-0439-s007934 | station | forward | revenue | 1 |
| line-2 | line-2-0650-0439-s007934 | station | reverse | revenue | 1 |
| line-2 | line-2-0665-0556-s005470 | station | forward | revenue | 1 |
| line-2 | line-2-0665-0556-s005470 | station | reverse | revenue | 1 |
| line-2 | line-2-0681-0672-s003017 | station | forward | revenue | 1 |
| line-2 | line-2-0681-0672-s003017 | station | reverse | revenue | 1 |
| line-2 | line-2-0700-0815-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0351-0708-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0471-0646-s003007 | station | forward | revenue | 1 |
| line-3 | line-3-0471-0646-s003007 | station | reverse | revenue | 1 |
| line-3 | line-3-0591-0584-s006026 | station | forward | revenue | 1 |
| line-3 | line-3-0591-0584-s006026 | station | reverse | revenue | 1 |
| line-3 | line-3-0712-0521-s009039 | station | forward | revenue | 1 |
| line-3 | line-3-0712-0521-s009039 | station | reverse | revenue | 1 |
| line-3 | line-3-0944-0336-s016363 | station | reverse | revenue | 2 |
| line-1 | line-1-0840-0623-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0840-0623-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0840-0623-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0700-0815-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0700-0815-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0700-0815-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0944-0336-s016363 | depot | — | revenue | 36 |
| line-3 | line-3-0944-0336-s016363 | depot | — | spare | 4 |
| line-3 | line-3-0944-0336-s016363 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/irbid-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **119 trainsets at 15 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **106 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **89 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0840-0623-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0696-0608-s003004 | forward | revenue | 4 | pending |
| line-1 | line-1-0696-0608-s003004 | reverse | revenue | 4 | pending |
| line-1 | line-1-0552-0592-s006017 | forward | revenue | 4 | pending |
| line-1 | line-1-0552-0592-s006017 | reverse | revenue | 4 | pending |
| line-1 | line-1-0432-0580-s008516 | forward | revenue | 4 | pending |
| line-1 | line-1-0432-0580-s008516 | reverse | revenue | 3 | pending |
| line-1 | line-1-0312-0567-s011024 | reverse | revenue | 3 | pending |
| line-1 | line-1-0432-0580-s008516 | reverse | spare | 1 | pending |
| line-1 | line-1-0312-0567-s011024 | reverse | spare | 1 | pending |
| line-1 | line-1-0840-0623-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0696-0608-s003004 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0700-0815-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0681-0672-s003017 | forward | revenue | 4 | pending |
| line-2 | line-2-0681-0672-s003017 | reverse | revenue | 4 | pending |
| line-2 | line-2-0665-0556-s005470 | forward | revenue | 4 | pending |
| line-2 | line-2-0665-0556-s005470 | reverse | revenue | 4 | pending |
| line-2 | line-2-0650-0439-s007934 | forward | revenue | 4 | pending |
| line-2 | line-2-0650-0439-s007934 | reverse | revenue | 3 | pending |
| line-2 | line-2-0634-0323-s010387 | reverse | revenue | 3 | pending |
| line-2 | line-2-0650-0439-s007934 | reverse | spare | 1 | pending |
| line-2 | line-2-0634-0323-s010387 | reverse | spare | 1 | pending |
| line-2 | line-2-0700-0815-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0681-0672-s003017 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0351-0708-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0471-0646-s003007 | forward | revenue | 6 | pending |
| line-3 | line-3-0471-0646-s003007 | reverse | revenue | 6 | pending |
| line-3 | line-3-0591-0584-s006026 | forward | revenue | 6 | pending |
| line-3 | line-3-0591-0584-s006026 | reverse | revenue | 6 | pending |
| line-3 | line-3-0712-0521-s009039 | forward | revenue | 6 | pending |
| line-3 | line-3-0712-0521-s009039 | reverse | revenue | 5 | pending |
| line-3 | line-3-0944-0336-s016363 | reverse | revenue | 5 | pending |
| line-3 | line-3-0712-0521-s009039 | reverse | spare | 1 | pending |
| line-3 | line-3-0944-0336-s016363 | reverse | spare | 1 | pending |
| line-3 | line-3-0351-0708-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0471-0646-s003007 | forward | spare | 1 | pending |
| line-3 | line-3-0471-0646-s003007 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**89 trainsets exceed the reference platform envelope**, requiring **5,295.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0312-0567-s011024 | 4 | 2 | 2 | 119.0 |
| line-1-0432-0580-s008516 | 8 | 2 | 6 | 357.0 |
| line-1-0552-0592-s006017 | 8 | 2 | 6 | 357.0 |
| line-1-0696-0608-s003004 | 9 | 2 | 7 | 416.5 |
| line-1-0840-0623-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0634-0323-s010387 | 4 | 2 | 2 | 119.0 |
| line-2-0650-0439-s007934 | 8 | 2 | 6 | 357.0 |
| line-2-0665-0556-s005470 | 8 | 2 | 6 | 357.0 |
| line-2-0681-0672-s003017 | 9 | 2 | 7 | 416.5 |
| line-2-0700-0815-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0351-0708-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0471-0646-s003007 | 14 | 2 | 12 | 714.0 |
| line-3-0591-0584-s006026 | 12 | 2 | 10 | 595.0 |
| line-3-0712-0521-s009039 | 12 | 2 | 10 | 595.0 |
| line-3-0944-0336-s016363 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Jordan/Irbid/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
