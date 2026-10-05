# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 89 at depots = 121 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0840-0623-s000000 | line-1 | declared-depot | 24 | 1,428.0 | 5 |
| line-2-0700-0815-s000000 | line-2 | declared-depot | 24 | 1,428.0 | 5 |
| line-3-0944-0336-s016699 | line-3 | declared-depot | 41 | 2,439.5 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0312-0567-s011024 | station | reverse | revenue | 2 |
| line-1 | line-1-0441-0581-s008328 | station | forward | revenue | 1 |
| line-1 | line-1-0441-0581-s008328 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0594-s005620 | station | forward | revenue | 1 |
| line-1 | line-1-0571-0594-s005620 | station | reverse | revenue | 1 |
| line-1 | line-1-0672-0605-s003509 | station | forward | revenue | 1 |
| line-1 | line-1-0672-0605-s003509 | station | reverse | revenue | 1 |
| line-1 | line-1-0840-0623-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0634-0323-s010387 | station | reverse | revenue | 2 |
| line-2 | line-2-0664-0546-s005678 | station | forward | revenue | 1 |
| line-2 | line-2-0664-0546-s005678 | station | reverse | revenue | 1 |
| line-2 | line-2-0672-0605-s004432 | station | forward | revenue | 1 |
| line-2 | line-2-0672-0605-s004432 | station | reverse | revenue | 1 |
| line-2 | line-2-0681-0672-s003017 | station | forward | revenue | 1 |
| line-2 | line-2-0681-0672-s003017 | station | reverse | revenue | 1 |
| line-2 | line-2-0700-0815-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0351-0708-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0471-0646-s003007 | station | forward | revenue | 1 |
| line-3 | line-3-0471-0646-s003007 | station | reverse | revenue | 1 |
| line-3 | line-3-0571-0594-s005520 | station | forward | revenue | 1 |
| line-3 | line-3-0571-0594-s005520 | station | reverse | revenue | 1 |
| line-3 | line-3-0664-0546-s007825 | station | forward | revenue | 1 |
| line-3 | line-3-0664-0546-s007825 | station | reverse | revenue | 1 |
| line-3 | line-3-0712-0521-s009039 | station | forward | revenue | 1 |
| line-3 | line-3-0712-0521-s009039 | station | reverse | revenue | 1 |
| line-3 | line-3-0944-0336-s016699 | station | reverse | revenue | 2 |
| line-1 | line-1-0840-0623-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0840-0623-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0840-0623-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0700-0815-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0700-0815-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0700-0815-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0944-0336-s016699 | depot | — | revenue | 36 |
| line-3 | line-3-0944-0336-s016699 | depot | — | spare | 4 |
| line-3 | line-3-0944-0336-s016699 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/irbid-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **121 trainsets at 16 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **108 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **89 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0840-0623-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0672-0605-s003509 | forward | revenue | 4 | pending |
| line-1 | line-1-0672-0605-s003509 | reverse | revenue | 4 | pending |
| line-1 | line-1-0571-0594-s005620 | forward | revenue | 4 | pending |
| line-1 | line-1-0571-0594-s005620 | reverse | revenue | 4 | pending |
| line-1 | line-1-0441-0581-s008328 | forward | revenue | 4 | pending |
| line-1 | line-1-0441-0581-s008328 | reverse | revenue | 3 | pending |
| line-1 | line-1-0312-0567-s011024 | reverse | revenue | 3 | pending |
| line-1 | line-1-0441-0581-s008328 | reverse | spare | 1 | pending |
| line-1 | line-1-0312-0567-s011024 | reverse | spare | 1 | pending |
| line-1 | line-1-0840-0623-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0672-0605-s003509 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0700-0815-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0681-0672-s003017 | forward | revenue | 4 | pending |
| line-2 | line-2-0681-0672-s003017 | reverse | revenue | 4 | pending |
| line-2 | line-2-0672-0605-s004432 | forward | revenue | 4 | pending |
| line-2 | line-2-0672-0605-s004432 | reverse | revenue | 4 | pending |
| line-2 | line-2-0664-0546-s005678 | forward | revenue | 4 | pending |
| line-2 | line-2-0664-0546-s005678 | reverse | revenue | 3 | pending |
| line-2 | line-2-0634-0323-s010387 | reverse | revenue | 3 | pending |
| line-2 | line-2-0664-0546-s005678 | reverse | spare | 1 | pending |
| line-2 | line-2-0634-0323-s010387 | reverse | spare | 1 | pending |
| line-2 | line-2-0700-0815-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0681-0672-s003017 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0351-0708-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0471-0646-s003007 | forward | revenue | 5 | pending |
| line-3 | line-3-0471-0646-s003007 | reverse | revenue | 5 | pending |
| line-3 | line-3-0571-0594-s005520 | forward | revenue | 5 | pending |
| line-3 | line-3-0571-0594-s005520 | reverse | revenue | 5 | pending |
| line-3 | line-3-0664-0546-s007825 | forward | revenue | 5 | pending |
| line-3 | line-3-0664-0546-s007825 | reverse | revenue | 5 | pending |
| line-3 | line-3-0712-0521-s009039 | forward | revenue | 5 | pending |
| line-3 | line-3-0712-0521-s009039 | reverse | revenue | 4 | pending |
| line-3 | line-3-0944-0336-s016699 | reverse | revenue | 4 | pending |
| line-3 | line-3-0712-0521-s009039 | reverse | spare | 1 | pending |
| line-3 | line-3-0944-0336-s016699 | reverse | spare | 1 | pending |
| line-3 | line-3-0351-0708-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0471-0646-s003007 | forward | spare | 1 | pending |
| line-3 | line-3-0471-0646-s003007 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**77 trainsets exceed the reference platform envelope**, requiring **4,581.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0312-0567-s011024 | 4 | 2 | 2 | 119.0 |
| line-1-0441-0581-s008328 | 8 | 2 | 6 | 357.0 |
| line-1-0571-0594-s005620 | 8 | 4 | 4 | 238.0 |
| line-1-0672-0605-s003509 | 9 | 4 | 5 | 297.5 |
| line-1-0840-0623-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0634-0323-s010387 | 4 | 2 | 2 | 119.0 |
| line-2-0664-0546-s005678 | 8 | 4 | 4 | 238.0 |
| line-2-0672-0605-s004432 | 8 | 4 | 4 | 238.0 |
| line-2-0681-0672-s003017 | 9 | 2 | 7 | 416.5 |
| line-2-0700-0815-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0351-0708-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0471-0646-s003007 | 12 | 2 | 10 | 595.0 |
| line-3-0571-0594-s005520 | 10 | 4 | 6 | 357.0 |
| line-3-0664-0546-s007825 | 10 | 4 | 6 | 357.0 |
| line-3-0712-0521-s009039 | 10 | 2 | 8 | 476.0 |
| line-3-0944-0336-s016699 | 5 | 2 | 3 | 178.5 |

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
