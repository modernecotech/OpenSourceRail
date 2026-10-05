# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 145 at depots = 183 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0332-0510-s000000 | line-1 | declared-depot | 41 | 2,439.5 | 8 |
| line-2-0249-0063-s000000 | line-2 | declared-depot | 48 | 2,856.0 | 9 |
| line-3-1046-0061-s021993 | line-3 | declared-depot | 56 | 3,332.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0332-0510-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0421-0502-s001846 | station | forward | revenue | 1 |
| line-1 | line-1-0421-0502-s001846 | station | reverse | revenue | 1 |
| line-1 | line-1-0521-0493-s003933 | station | forward | revenue | 1 |
| line-1 | line-1-0521-0493-s003933 | station | reverse | revenue | 1 |
| line-1 | line-1-0621-0483-s006027 | station | forward | revenue | 1 |
| line-1 | line-1-0621-0483-s006027 | station | reverse | revenue | 1 |
| line-1 | line-1-0711-0475-s007893 | station | forward | revenue | 1 |
| line-1 | line-1-0711-0475-s007893 | station | reverse | revenue | 1 |
| line-1 | line-1-1086-0483-s016328 | station | reverse | revenue | 2 |
| line-2 | line-2-0249-0063-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0354-0346-s007011 | station | forward | revenue | 1 |
| line-2 | line-2-0354-0346-s007011 | station | reverse | revenue | 1 |
| line-2 | line-2-0421-0502-s010733 | station | forward | revenue | 1 |
| line-2 | line-2-0421-0502-s010733 | station | reverse | revenue | 1 |
| line-2 | line-2-0462-0598-s013016 | station | forward | revenue | 1 |
| line-2 | line-2-0462-0598-s013016 | station | reverse | revenue | 1 |
| line-2 | line-2-0497-0678-s014929 | station | forward | revenue | 1 |
| line-2 | line-2-0497-0678-s014929 | station | reverse | revenue | 1 |
| line-2 | line-2-0531-0757-s016814 | station | forward | revenue | 1 |
| line-2 | line-2-0531-0757-s016814 | station | reverse | revenue | 1 |
| line-2 | line-2-0581-0875-s019624 | station | reverse | revenue | 2 |
| line-3 | line-3-0486-0828-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0531-0757-s001910 | station | forward | revenue | 1 |
| line-3 | line-3-0531-0757-s001910 | station | reverse | revenue | 1 |
| line-3 | line-3-0581-0679-s003978 | station | forward | revenue | 1 |
| line-3 | line-3-0581-0679-s003978 | station | reverse | revenue | 1 |
| line-3 | line-3-0631-0601-s006034 | station | forward | revenue | 1 |
| line-3 | line-3-0631-0601-s006034 | station | reverse | revenue | 1 |
| line-3 | line-3-0711-0475-s009322 | station | forward | revenue | 1 |
| line-3 | line-3-0711-0475-s009322 | station | reverse | revenue | 1 |
| line-3 | line-3-1046-0061-s021993 | station | reverse | revenue | 2 |
| line-1 | line-1-0332-0510-s000000 | depot | — | revenue | 36 |
| line-1 | line-1-0332-0510-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0332-0510-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0249-0063-s000000 | depot | — | revenue | 42 |
| line-2 | line-2-0249-0063-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0249-0063-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1046-0061-s021993 | depot | — | revenue | 49 |
| line-3 | line-3-1046-0061-s021993 | depot | — | spare | 6 |
| line-3 | line-3-1046-0061-s021993 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/bafoussam-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **183 trainsets at 19 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **165 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **145 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0332-0510-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0421-0502-s001846 | forward | revenue | 5 | pending |
| line-1 | line-1-0421-0502-s001846 | reverse | revenue | 5 | pending |
| line-1 | line-1-0521-0493-s003933 | forward | revenue | 5 | pending |
| line-1 | line-1-0521-0493-s003933 | reverse | revenue | 5 | pending |
| line-1 | line-1-0621-0483-s006027 | forward | revenue | 5 | pending |
| line-1 | line-1-0621-0483-s006027 | reverse | revenue | 5 | pending |
| line-1 | line-1-0711-0475-s007893 | forward | revenue | 5 | pending |
| line-1 | line-1-0711-0475-s007893 | reverse | revenue | 4 | pending |
| line-1 | line-1-1086-0483-s016328 | reverse | revenue | 4 | pending |
| line-1 | line-1-0711-0475-s007893 | reverse | spare | 1 | pending |
| line-1 | line-1-1086-0483-s016328 | reverse | spare | 1 | pending |
| line-1 | line-1-0332-0510-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0421-0502-s001846 | forward | spare | 1 | pending |
| line-1 | line-1-0421-0502-s001846 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0249-0063-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0354-0346-s007011 | forward | revenue | 5 | pending |
| line-2 | line-2-0354-0346-s007011 | reverse | revenue | 5 | pending |
| line-2 | line-2-0421-0502-s010733 | forward | revenue | 5 | pending |
| line-2 | line-2-0421-0502-s010733 | reverse | revenue | 5 | pending |
| line-2 | line-2-0462-0598-s013016 | forward | revenue | 5 | pending |
| line-2 | line-2-0462-0598-s013016 | reverse | revenue | 5 | pending |
| line-2 | line-2-0497-0678-s014929 | forward | revenue | 5 | pending |
| line-2 | line-2-0497-0678-s014929 | reverse | revenue | 4 | pending |
| line-2 | line-2-0531-0757-s016814 | forward | revenue | 4 | pending |
| line-2 | line-2-0531-0757-s016814 | reverse | revenue | 4 | pending |
| line-2 | line-2-0581-0875-s019624 | reverse | revenue | 4 | pending |
| line-2 | line-2-0497-0678-s014929 | reverse | spare | 1 | pending |
| line-2 | line-2-0531-0757-s016814 | forward | spare | 1 | pending |
| line-2 | line-2-0531-0757-s016814 | reverse | spare | 1 | pending |
| line-2 | line-2-0581-0875-s019624 | reverse | spare | 1 | pending |
| line-2 | line-2-0249-0063-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0354-0346-s007011 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0486-0828-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0531-0757-s001910 | forward | revenue | 6 | pending |
| line-3 | line-3-0531-0757-s001910 | reverse | revenue | 6 | pending |
| line-3 | line-3-0581-0679-s003978 | forward | revenue | 6 | pending |
| line-3 | line-3-0581-0679-s003978 | reverse | revenue | 6 | pending |
| line-3 | line-3-0631-0601-s006034 | forward | revenue | 6 | pending |
| line-3 | line-3-0631-0601-s006034 | reverse | revenue | 6 | pending |
| line-3 | line-3-0711-0475-s009322 | forward | revenue | 6 | pending |
| line-3 | line-3-0711-0475-s009322 | reverse | revenue | 6 | pending |
| line-3 | line-3-1046-0061-s021993 | reverse | revenue | 6 | pending |
| line-3 | line-3-0531-0757-s001910 | forward | spare | 1 | pending |
| line-3 | line-3-0531-0757-s001910 | reverse | spare | 1 | pending |
| line-3 | line-3-0581-0679-s003978 | forward | spare | 1 | pending |
| line-3 | line-3-0581-0679-s003978 | reverse | spare | 1 | pending |
| line-3 | line-3-0631-0601-s006034 | forward | spare | 1 | pending |
| line-3 | line-3-0631-0601-s006034 | reverse | spare | 1 | pending |
| line-3 | line-3-0711-0475-s009322 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**133 trainsets exceed the reference platform envelope**, requiring **7,913.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0332-0510-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0421-0502-s001846 | 12 | 4 | 8 | 476.0 |
| line-1-0521-0493-s003933 | 10 | 2 | 8 | 476.0 |
| line-1-0621-0483-s006027 | 10 | 2 | 8 | 476.0 |
| line-1-0711-0475-s007893 | 10 | 4 | 6 | 357.0 |
| line-1-1086-0483-s016328 | 5 | 2 | 3 | 178.5 |
| line-2-0249-0063-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0354-0346-s007011 | 11 | 2 | 9 | 535.5 |
| line-2-0421-0502-s010733 | 10 | 4 | 6 | 357.0 |
| line-2-0462-0598-s013016 | 10 | 2 | 8 | 476.0 |
| line-2-0497-0678-s014929 | 10 | 2 | 8 | 476.0 |
| line-2-0531-0757-s016814 | 10 | 4 | 6 | 357.0 |
| line-2-0581-0875-s019624 | 5 | 2 | 3 | 178.5 |
| line-3-0486-0828-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0531-0757-s001910 | 14 | 4 | 10 | 595.0 |
| line-3-0581-0679-s003978 | 14 | 2 | 12 | 714.0 |
| line-3-0631-0601-s006034 | 14 | 2 | 12 | 714.0 |
| line-3-0711-0475-s009322 | 13 | 4 | 9 | 535.5 |
| line-3-1046-0061-s021993 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Bafoussam/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
