# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 130 at depots = 174 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0840-0623-s000000 | line-1 | declared-depot | 37 | 2,201.5 | 8 |
| line-2-0700-0815-s000000 | line-2 | declared-depot | 24 | 1,428.0 | 5 |
| line-3-0944-0336-s016699 | line-3 | declared-depot | 44 | 2,618.0 | 8 |
| line-4-0502-0518-s000000 | line-4 | declared-depot | 14 | 833.0 | 3 |
| line-5-0690-0737-s000000 | line-5 | declared-depot | 11 | 654.5 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0312-0567-s015818 | station | reverse | revenue | 2 |
| line-1 | line-1-0477-0517-s010706 | station | forward | revenue | 1 |
| line-1 | line-1-0477-0517-s010706 | station | reverse | revenue | 1 |
| line-1 | line-1-0502-0518-s010142 | station | forward | revenue | 1 |
| line-1 | line-1-0502-0518-s010142 | station | reverse | revenue | 1 |
| line-1 | line-1-0602-0578-s006982 | station | forward | revenue | 1 |
| line-1 | line-1-0602-0578-s006982 | station | reverse | revenue | 1 |
| line-1 | line-1-0673-0623-s005189 | station | forward | revenue | 1 |
| line-1 | line-1-0673-0623-s005189 | station | reverse | revenue | 1 |
| line-1 | line-1-0736-0627-s003572 | station | forward | revenue | 1 |
| line-1 | line-1-0736-0627-s003572 | station | reverse | revenue | 1 |
| line-1 | line-1-0840-0623-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0634-0323-s010387 | station | reverse | revenue | 2 |
| line-2 | line-2-0664-0546-s005678 | station | forward | revenue | 1 |
| line-2 | line-2-0664-0546-s005678 | station | reverse | revenue | 1 |
| line-2 | line-2-0674-0624-s004035 | station | forward | revenue | 1 |
| line-2 | line-2-0674-0624-s004035 | station | reverse | revenue | 1 |
| line-2 | line-2-0690-0737-s001643 | station | forward | revenue | 1 |
| line-2 | line-2-0690-0737-s001643 | station | reverse | revenue | 1 |
| line-2 | line-2-0700-0815-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0351-0708-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0471-0646-s003007 | station | forward | revenue | 1 |
| line-3 | line-3-0471-0646-s003007 | station | reverse | revenue | 1 |
| line-3 | line-3-0602-0578-s006296 | station | forward | revenue | 1 |
| line-3 | line-3-0602-0578-s006296 | station | reverse | revenue | 1 |
| line-3 | line-3-0664-0546-s007825 | station | forward | revenue | 1 |
| line-3 | line-3-0664-0546-s007825 | station | reverse | revenue | 1 |
| line-3 | line-3-0944-0336-s016699 | station | reverse | revenue | 2 |
| line-4 | line-4-0477-0517-s000714 | station | forward | revenue | 1 |
| line-4 | line-4-0477-0517-s000714 | station | reverse | revenue | 1 |
| line-4 | line-4-0502-0518-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0563-0362-s006177 | station | reverse | revenue | 2 |
| line-5 | line-5-0690-0737-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0838-0762-s004293 | station | reverse | revenue | 2 |
| line-1 | line-1-0840-0623-s000000 | depot | — | revenue | 32 |
| line-1 | line-1-0840-0623-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0840-0623-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0700-0815-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0700-0815-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0700-0815-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0944-0336-s016699 | depot | — | revenue | 39 |
| line-3 | line-3-0944-0336-s016699 | depot | — | spare | 4 |
| line-3 | line-3-0944-0336-s016699 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0502-0518-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0502-0518-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0502-0518-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0690-0737-s000000 | depot | — | revenue | 9 |
| line-5 | line-5-0690-0737-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0690-0737-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/irbid-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **174 trainsets at 22 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **156 revenue, 13 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **130 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0840-0623-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0736-0627-s003572 | forward | revenue | 4 | pending |
| line-1 | line-1-0736-0627-s003572 | reverse | revenue | 4 | pending |
| line-1 | line-1-0673-0623-s005189 | forward | revenue | 4 | pending |
| line-1 | line-1-0673-0623-s005189 | reverse | revenue | 4 | pending |
| line-1 | line-1-0602-0578-s006982 | forward | revenue | 4 | pending |
| line-1 | line-1-0602-0578-s006982 | reverse | revenue | 4 | pending |
| line-1 | line-1-0502-0518-s010142 | forward | revenue | 4 | pending |
| line-1 | line-1-0502-0518-s010142 | reverse | revenue | 4 | pending |
| line-1 | line-1-0477-0517-s010706 | forward | revenue | 4 | pending |
| line-1 | line-1-0477-0517-s010706 | reverse | revenue | 3 | pending |
| line-1 | line-1-0312-0567-s015818 | reverse | revenue | 3 | pending |
| line-1 | line-1-0477-0517-s010706 | reverse | spare | 1 | pending |
| line-1 | line-1-0312-0567-s015818 | reverse | spare | 1 | pending |
| line-1 | line-1-0840-0623-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0736-0627-s003572 | forward | spare | 1 | pending |
| line-1 | line-1-0736-0627-s003572 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0700-0815-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0690-0737-s001643 | forward | revenue | 4 | pending |
| line-2 | line-2-0690-0737-s001643 | reverse | revenue | 4 | pending |
| line-2 | line-2-0674-0624-s004035 | forward | revenue | 4 | pending |
| line-2 | line-2-0674-0624-s004035 | reverse | revenue | 4 | pending |
| line-2 | line-2-0664-0546-s005678 | forward | revenue | 4 | pending |
| line-2 | line-2-0664-0546-s005678 | reverse | revenue | 3 | pending |
| line-2 | line-2-0634-0323-s010387 | reverse | revenue | 3 | pending |
| line-2 | line-2-0664-0546-s005678 | reverse | spare | 1 | pending |
| line-2 | line-2-0634-0323-s010387 | reverse | spare | 1 | pending |
| line-2 | line-2-0700-0815-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0690-0737-s001643 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0351-0708-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0471-0646-s003007 | forward | revenue | 6 | pending |
| line-3 | line-3-0471-0646-s003007 | reverse | revenue | 6 | pending |
| line-3 | line-3-0602-0578-s006296 | forward | revenue | 6 | pending |
| line-3 | line-3-0602-0578-s006296 | reverse | revenue | 6 | pending |
| line-3 | line-3-0664-0546-s007825 | forward | revenue | 6 | pending |
| line-3 | line-3-0664-0546-s007825 | reverse | revenue | 6 | pending |
| line-3 | line-3-0944-0336-s016699 | reverse | revenue | 6 | pending |
| line-3 | line-3-0471-0646-s003007 | forward | spare | 1 | pending |
| line-3 | line-3-0471-0646-s003007 | reverse | spare | 1 | pending |
| line-3 | line-3-0602-0578-s006296 | forward | spare | 1 | pending |
| line-3 | line-3-0602-0578-s006296 | reverse | spare | 1 | pending |
| line-3 | line-3-0664-0546-s007825 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0502-0518-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0477-0517-s000714 | forward | revenue | 5 | pending |
| line-4 | line-4-0477-0517-s000714 | reverse | revenue | 4 | pending |
| line-4 | line-4-0563-0362-s006177 | reverse | revenue | 4 | pending |
| line-4 | line-4-0477-0517-s000714 | reverse | spare | 1 | pending |
| line-4 | line-4-0563-0362-s006177 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0690-0737-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0838-0762-s004293 | reverse | revenue | 6 | pending |
| line-5 | line-5-0838-0762-s004293 | reverse | spare | 1 | pending |
| line-5 | line-5-0690-0737-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**110 trainsets exceed the reference platform envelope**, requiring **6,545.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0312-0567-s015818 | 4 | 2 | 2 | 119.0 |
| line-1-0477-0517-s010706 | 8 | 4 | 4 | 238.0 |
| line-1-0502-0518-s010142 | 8 | 4 | 4 | 238.0 |
| line-1-0602-0578-s006982 | 8 | 4 | 4 | 238.0 |
| line-1-0673-0623-s005189 | 8 | 4 | 4 | 238.0 |
| line-1-0736-0627-s003572 | 10 | 2 | 8 | 476.0 |
| line-1-0840-0623-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0634-0323-s010387 | 4 | 2 | 2 | 119.0 |
| line-2-0664-0546-s005678 | 8 | 4 | 4 | 238.0 |
| line-2-0674-0624-s004035 | 8 | 4 | 4 | 238.0 |
| line-2-0690-0737-s001643 | 9 | 4 | 5 | 297.5 |
| line-2-0700-0815-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0351-0708-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0471-0646-s003007 | 14 | 2 | 12 | 714.0 |
| line-3-0602-0578-s006296 | 14 | 4 | 10 | 595.0 |
| line-3-0664-0546-s007825 | 13 | 4 | 9 | 535.5 |
| line-3-0944-0336-s016699 | 6 | 2 | 4 | 238.0 |
| line-4-0477-0517-s000714 | 10 | 4 | 6 | 357.0 |
| line-4-0502-0518-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0563-0362-s006177 | 5 | 2 | 3 | 178.5 |
| line-5-0690-0737-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0838-0762-s004293 | 7 | 2 | 5 | 297.5 |

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
