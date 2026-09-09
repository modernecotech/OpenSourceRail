# Station and depot overnight allocation

Plan: **28 trainsets at stations + 41 at depots = 69 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0354-0699-s014020 | 41 | 2,009.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0316-0192-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0329-0290-s003025 | station | forward | revenue | 1 |
| line-1 | line-1-0329-0290-s003025 | station | reverse | revenue | 1 |
| line-1 | line-1-0349-0574-s011167 | station | forward | revenue | 1 |
| line-1 | line-1-0349-0574-s011167 | station | reverse | revenue | 1 |
| line-1 | line-1-0354-0699-s014020 | station | reverse | revenue | 2 |
| line-1 | line-1-0378-0382-s005450 | station | forward | revenue | 1 |
| line-1 | line-1-0378-0382-s005450 | station | reverse | revenue | 1 |
| line-1 | line-1-0414-0486-s008304 | station | forward | revenue | 1 |
| line-1 | line-1-0414-0486-s008304 | station | reverse | revenue | 1 |
| line-2 | line-2-0365-0597-s007781 | station | reverse | revenue | 2 |
| line-2 | line-2-0440-0520-s005404 | station | forward | revenue | 1 |
| line-2 | line-2-0440-0520-s005404 | station | reverse | revenue | 1 |
| line-2 | line-2-0510-0460-s003013 | station | forward | revenue | 1 |
| line-2 | line-2-0510-0460-s003013 | station | reverse | revenue | 1 |
| line-2 | line-2-0634-0455-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0353-0455-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0378-0382-s002377 | station | forward | revenue | 1 |
| line-3 | line-3-0378-0382-s002377 | station | reverse | revenue | 1 |
| line-3 | line-3-0483-0436-s005131 | station | forward | revenue | 1 |
| line-3 | line-3-0483-0436-s005131 | station | reverse | revenue | 1 |
| line-3 | line-3-0645-0634-s010614 | station | reverse | revenue | 2 |
| line-1 | line-1-0354-0699-s014020 | depot | — | revenue | 14 |
| line-1 | line-1-0354-0699-s014020 | depot | — | spare | 2 |
| line-1 | line-1-0354-0699-s014020 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0354-0699-s014020 | depot | — | revenue | 7 |
| line-2 | line-1-0354-0699-s014020 | depot | — | spare | 1 |
| line-2 | line-1-0354-0699-s014020 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0354-0699-s014020 | depot | — | revenue | 12 |
| line-3 | line-1-0354-0699-s014020 | depot | — | spare | 2 |
| line-3 | line-1-0354-0699-s014020 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (9 trains), line-3 (15 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **69 trainsets at 14 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **61 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **41 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0316-0192-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0329-0290-s003025 | forward | revenue | 3 | pending |
| line-1 | line-1-0329-0290-s003025 | reverse | revenue | 3 | pending |
| line-1 | line-1-0378-0382-s005450 | forward | revenue | 3 | pending |
| line-1 | line-1-0378-0382-s005450 | reverse | revenue | 3 | pending |
| line-1 | line-1-0414-0486-s008304 | forward | revenue | 3 | pending |
| line-1 | line-1-0414-0486-s008304 | reverse | revenue | 2 | pending |
| line-1 | line-1-0349-0574-s011167 | forward | revenue | 2 | pending |
| line-1 | line-1-0349-0574-s011167 | reverse | revenue | 2 | pending |
| line-1 | line-1-0354-0699-s014020 | reverse | revenue | 2 | pending |
| line-1 | line-1-0414-0486-s008304 | reverse | spare | 1 | pending |
| line-1 | line-1-0349-0574-s011167 | forward | spare | 1 | pending |
| line-1 | line-1-0349-0574-s011167 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0634-0455-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0510-0460-s003013 | forward | revenue | 3 | pending |
| line-2 | line-2-0510-0460-s003013 | reverse | revenue | 3 | pending |
| line-2 | line-2-0440-0520-s005404 | forward | revenue | 2 | pending |
| line-2 | line-2-0440-0520-s005404 | reverse | revenue | 2 | pending |
| line-2 | line-2-0365-0597-s007781 | reverse | revenue | 2 | pending |
| line-2 | line-2-0440-0520-s005404 | forward | spare | 1 | pending |
| line-2 | line-2-0440-0520-s005404 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0353-0455-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0378-0382-s002377 | forward | revenue | 4 | pending |
| line-3 | line-3-0378-0382-s002377 | reverse | revenue | 3 | pending |
| line-3 | line-3-0483-0436-s005131 | forward | revenue | 3 | pending |
| line-3 | line-3-0483-0436-s005131 | reverse | revenue | 3 | pending |
| line-3 | line-3-0645-0634-s010614 | reverse | revenue | 3 | pending |
| line-3 | line-3-0378-0382-s002377 | reverse | spare | 1 | pending |
| line-3 | line-3-0483-0436-s005131 | forward | spare | 1 | pending |
| line-3 | line-3-0483-0436-s005131 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**35 trainsets exceed the reference platform envelope**, requiring **1,715.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0316-0192-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0329-0290-s003025 | 6 | 2 | 4 | 196.0 |
| line-1-0349-0574-s011167 | 6 | 4 | 2 | 98.0 |
| line-1-0354-0699-s014020 | 2 | 2 | 0 | 0.0 |
| line-1-0378-0382-s005450 | 6 | 4 | 2 | 98.0 |
| line-1-0414-0486-s008304 | 6 | 2 | 4 | 196.0 |
| line-2-0365-0597-s007781 | 2 | 2 | 0 | 0.0 |
| line-2-0440-0520-s005404 | 6 | 2 | 4 | 196.0 |
| line-2-0510-0460-s003013 | 6 | 2 | 4 | 196.0 |
| line-2-0634-0455-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0353-0455-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0378-0382-s002377 | 8 | 4 | 4 | 196.0 |
| line-3-0483-0436-s005131 | 8 | 2 | 6 | 294.0 |
| line-3-0645-0634-s010614 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Pemba-Mz/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
