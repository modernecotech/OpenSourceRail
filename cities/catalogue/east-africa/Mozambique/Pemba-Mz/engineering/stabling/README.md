# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 37 at depots = 75 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0354-0699-s011145 | line-1 | declared-depot | 12 | 588.0 | 4 |
| line-2-0634-0455-s000000 | line-2 | declared-depot | 9 | 441.0 | 3 |
| line-3-0353-0455-s000000 | line-3 | declared-depot | 10 | 490.0 | 3 |
| line-4-0327-0375-s000000 | line-4 | declared-depot | 6 | 294.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0316-0192-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0325-0346-s003155 | station | forward | revenue | 1 |
| line-1 | line-1-0325-0346-s003155 | station | reverse | revenue | 1 |
| line-1 | line-1-0326-0364-s003523 | station | forward | revenue | 1 |
| line-1 | line-1-0326-0364-s003523 | station | reverse | revenue | 1 |
| line-1 | line-1-0326-0369-s003623 | station | forward | revenue | 1 |
| line-1 | line-1-0326-0369-s003623 | station | reverse | revenue | 1 |
| line-1 | line-1-0327-0375-s003751 | station | forward | revenue | 1 |
| line-1 | line-1-0327-0375-s003751 | station | reverse | revenue | 1 |
| line-1 | line-1-0354-0699-s011145 | station | reverse | revenue | 2 |
| line-1 | line-1-0361-0538-s007444 | station | forward | revenue | 1 |
| line-1 | line-1-0361-0538-s007444 | station | reverse | revenue | 1 |
| line-2 | line-2-0365-0597-s006927 | station | reverse | revenue | 2 |
| line-2 | line-2-0486-0527-s003810 | station | forward | revenue | 1 |
| line-2 | line-2-0486-0527-s003810 | station | reverse | revenue | 1 |
| line-2 | line-2-0634-0455-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0353-0455-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0487-0527-s003391 | station | forward | revenue | 1 |
| line-3 | line-3-0487-0527-s003391 | station | reverse | revenue | 1 |
| line-3 | line-3-0645-0634-s007644 | station | reverse | revenue | 2 |
| line-4 | line-4-0325-0346-s000663 | station | forward | revenue | 1 |
| line-4 | line-4-0325-0346-s000663 | station | reverse | revenue | 1 |
| line-4 | line-4-0326-0364-s000228 | station | forward | revenue | 1 |
| line-4 | line-4-0326-0364-s000228 | station | reverse | revenue | 1 |
| line-4 | line-4-0326-0369-s000128 | station | forward | revenue | 1 |
| line-4 | line-4-0326-0369-s000128 | station | reverse | revenue | 1 |
| line-4 | line-4-0327-0375-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0437-0363-s003867 | station | forward | revenue | 1 |
| line-4 | line-4-0437-0363-s003867 | station | reverse | revenue | 1 |
| line-4 | line-4-0463-0437-s005562 | station | reverse | revenue | 2 |
| line-1 | line-1-0354-0699-s011145 | depot | — | revenue | 9 |
| line-1 | line-1-0354-0699-s011145 | depot | — | spare | 2 |
| line-1 | line-1-0354-0699-s011145 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0634-0455-s000000 | depot | — | revenue | 7 |
| line-2 | line-2-0634-0455-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0634-0455-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0353-0455-s000000 | depot | — | revenue | 8 |
| line-3 | line-3-0353-0455-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0353-0455-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0327-0375-s000000 | depot | — | revenue | 4 |
| line-4 | line-4-0327-0375-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0327-0375-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/pemba-mz-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **75 trainsets at 19 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **66 revenue, 5 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **37 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0316-0192-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0325-0346-s003155 | forward | revenue | 2 | pending |
| line-1 | line-1-0325-0346-s003155 | reverse | revenue | 2 | pending |
| line-1 | line-1-0326-0364-s003523 | forward | revenue | 2 | pending |
| line-1 | line-1-0326-0364-s003523 | reverse | revenue | 2 | pending |
| line-1 | line-1-0326-0369-s003623 | forward | revenue | 2 | pending |
| line-1 | line-1-0326-0369-s003623 | reverse | revenue | 2 | pending |
| line-1 | line-1-0327-0375-s003751 | forward | revenue | 2 | pending |
| line-1 | line-1-0327-0375-s003751 | reverse | revenue | 2 | pending |
| line-1 | line-1-0361-0538-s007444 | forward | revenue | 2 | pending |
| line-1 | line-1-0361-0538-s007444 | reverse | revenue | 2 | pending |
| line-1 | line-1-0354-0699-s011145 | reverse | revenue | 1 | pending |
| line-1 | line-1-0354-0699-s011145 | reverse | spare | 1 | pending |
| line-1 | line-1-0316-0192-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0325-0346-s003155 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0634-0455-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0486-0527-s003810 | forward | revenue | 3 | pending |
| line-2 | line-2-0486-0527-s003810 | reverse | revenue | 3 | pending |
| line-2 | line-2-0365-0597-s006927 | reverse | revenue | 3 | pending |
| line-2 | line-2-0486-0527-s003810 | forward | spare | 1 | pending |
| line-2 | line-2-0486-0527-s003810 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0353-0455-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0487-0527-s003391 | forward | revenue | 4 | pending |
| line-3 | line-3-0487-0527-s003391 | reverse | revenue | 3 | pending |
| line-3 | line-3-0645-0634-s007644 | reverse | revenue | 3 | pending |
| line-3 | line-3-0487-0527-s003391 | reverse | spare | 1 | pending |
| line-3 | line-3-0645-0634-s007644 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0327-0375-s000000 | forward | revenue | 2 | pending |
| line-4 | line-4-0326-0369-s000128 | forward | revenue | 2 | pending |
| line-4 | line-4-0326-0369-s000128 | reverse | revenue | 2 | pending |
| line-4 | line-4-0326-0364-s000228 | forward | revenue | 2 | pending |
| line-4 | line-4-0326-0364-s000228 | reverse | revenue | 2 | pending |
| line-4 | line-4-0325-0346-s000663 | forward | revenue | 2 | pending |
| line-4 | line-4-0325-0346-s000663 | reverse | revenue | 1 | pending |
| line-4 | line-4-0437-0363-s003867 | forward | revenue | 1 | pending |
| line-4 | line-4-0437-0363-s003867 | reverse | revenue | 1 | pending |
| line-4 | line-4-0463-0437-s005562 | reverse | revenue | 1 | pending |
| line-4 | line-4-0325-0346-s000663 | reverse | spare | 1 | pending |
| line-4 | line-4-0437-0363-s003867 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**20 trainsets exceed the reference platform envelope**, requiring **980.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0316-0192-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0325-0346-s003155 | 5 | 4 | 1 | 49.0 |
| line-1-0326-0364-s003523 | 4 | 4 | 0 | 0.0 |
| line-1-0326-0369-s003623 | 4 | 4 | 0 | 0.0 |
| line-1-0327-0375-s003751 | 4 | 4 | 0 | 0.0 |
| line-1-0354-0699-s011145 | 2 | 2 | 0 | 0.0 |
| line-1-0361-0538-s007444 | 4 | 2 | 2 | 98.0 |
| line-2-0365-0597-s006927 | 3 | 2 | 1 | 49.0 |
| line-2-0486-0527-s003810 | 8 | 4 | 4 | 196.0 |
| line-2-0634-0455-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0353-0455-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0487-0527-s003391 | 8 | 4 | 4 | 196.0 |
| line-3-0645-0634-s007644 | 4 | 2 | 2 | 98.0 |
| line-4-0325-0346-s000663 | 4 | 4 | 0 | 0.0 |
| line-4-0326-0364-s000228 | 4 | 4 | 0 | 0.0 |
| line-4-0326-0369-s000128 | 4 | 4 | 0 | 0.0 |
| line-4-0327-0375-s000000 | 2 | 2 | 0 | 0.0 |
| line-4-0437-0363-s003867 | 3 | 2 | 1 | 49.0 |
| line-4-0463-0437-s005562 | 1 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Pemba-Mz/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
