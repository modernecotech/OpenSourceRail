# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 105 at depots = 131 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0316-0690-s000000 | line-1 | declared-depot | 24 | 1,428.0 | 5 |
| line-2-0949-0887-s018371 | line-2 | declared-depot | 49 | 2,915.5 | 8 |
| line-3-0527-0507-s000000 | line-3 | declared-depot | 32 | 1,904.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0316-0690-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0401-0583-s003078 | station | forward | revenue | 1 |
| line-1 | line-1-0401-0583-s003078 | station | reverse | revenue | 1 |
| line-1 | line-1-0459-0511-s005140 | station | forward | revenue | 1 |
| line-1 | line-1-0459-0511-s005140 | station | reverse | revenue | 1 |
| line-1 | line-1-0559-0386-s008726 | station | forward | revenue | 1 |
| line-1 | line-1-0559-0386-s008726 | station | reverse | revenue | 1 |
| line-1 | line-1-0602-0332-s010279 | station | reverse | revenue | 2 |
| line-2 | line-2-0473-0257-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0559-0386-s003503 | station | forward | revenue | 1 |
| line-2 | line-2-0559-0386-s003503 | station | reverse | revenue | 1 |
| line-2 | line-2-0646-0515-s007015 | station | forward | revenue | 1 |
| line-2 | line-2-0646-0515-s007015 | station | reverse | revenue | 1 |
| line-2 | line-2-0949-0887-s018371 | station | reverse | revenue | 2 |
| line-3 | line-3-0014-0682-s013177 | station | reverse | revenue | 2 |
| line-3 | line-3-0271-0662-s006638 | station | forward | revenue | 1 |
| line-3 | line-3-0271-0662-s006638 | station | reverse | revenue | 1 |
| line-3 | line-3-0401-0583-s003267 | station | forward | revenue | 1 |
| line-3 | line-3-0401-0583-s003267 | station | reverse | revenue | 1 |
| line-3 | line-3-0527-0507-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0316-0690-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0316-0690-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0316-0690-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0949-0887-s018371 | depot | — | revenue | 43 |
| line-2 | line-2-0949-0887-s018371 | depot | — | spare | 5 |
| line-2 | line-2-0949-0887-s018371 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0527-0507-s000000 | depot | — | revenue | 28 |
| line-3 | line-3-0527-0507-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0527-0507-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/qena-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **131 trainsets at 13 stations**; largest initial station queue **20**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **117 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **105 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0316-0690-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0401-0583-s003078 | forward | revenue | 4 | pending |
| line-1 | line-1-0401-0583-s003078 | reverse | revenue | 4 | pending |
| line-1 | line-1-0459-0511-s005140 | forward | revenue | 4 | pending |
| line-1 | line-1-0459-0511-s005140 | reverse | revenue | 4 | pending |
| line-1 | line-1-0559-0386-s008726 | forward | revenue | 4 | pending |
| line-1 | line-1-0559-0386-s008726 | reverse | revenue | 3 | pending |
| line-1 | line-1-0602-0332-s010279 | reverse | revenue | 3 | pending |
| line-1 | line-1-0559-0386-s008726 | reverse | spare | 1 | pending |
| line-1 | line-1-0602-0332-s010279 | reverse | spare | 1 | pending |
| line-1 | line-1-0316-0690-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0401-0583-s003078 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0473-0257-s000000 | forward | revenue | 9 | pending |
| line-2 | line-2-0559-0386-s003503 | forward | revenue | 9 | pending |
| line-2 | line-2-0559-0386-s003503 | reverse | revenue | 9 | pending |
| line-2 | line-2-0646-0515-s007015 | forward | revenue | 8 | pending |
| line-2 | line-2-0646-0515-s007015 | reverse | revenue | 8 | pending |
| line-2 | line-2-0949-0887-s018371 | reverse | revenue | 8 | pending |
| line-2 | line-2-0646-0515-s007015 | forward | spare | 1 | pending |
| line-2 | line-2-0646-0515-s007015 | reverse | spare | 1 | pending |
| line-2 | line-2-0949-0887-s018371 | reverse | spare | 1 | pending |
| line-2 | line-2-0473-0257-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0559-0386-s003503 | forward | spare | 1 | pending |
| line-2 | line-2-0559-0386-s003503 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0527-0507-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0401-0583-s003267 | forward | revenue | 6 | pending |
| line-3 | line-3-0401-0583-s003267 | reverse | revenue | 6 | pending |
| line-3 | line-3-0271-0662-s006638 | forward | revenue | 6 | pending |
| line-3 | line-3-0271-0662-s006638 | reverse | revenue | 6 | pending |
| line-3 | line-3-0014-0682-s013177 | reverse | revenue | 6 | pending |
| line-3 | line-3-0527-0507-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0401-0583-s003267 | forward | spare | 1 | pending |
| line-3 | line-3-0401-0583-s003267 | reverse | spare | 1 | pending |
| line-3 | line-3-0271-0662-s006638 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**97 trainsets exceed the reference platform envelope**, requiring **5,771.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0316-0690-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0401-0583-s003078 | 9 | 4 | 5 | 297.5 |
| line-1-0459-0511-s005140 | 8 | 2 | 6 | 357.0 |
| line-1-0559-0386-s008726 | 8 | 4 | 4 | 238.0 |
| line-1-0602-0332-s010279 | 4 | 2 | 2 | 119.0 |
| line-2-0473-0257-s000000 | 10 | 2 | 8 | 476.0 |
| line-2-0559-0386-s003503 | 20 | 4 | 16 | 952.0 |
| line-2-0646-0515-s007015 | 18 | 2 | 16 | 952.0 |
| line-2-0949-0887-s018371 | 9 | 2 | 7 | 416.5 |
| line-3-0014-0682-s013177 | 6 | 2 | 4 | 238.0 |
| line-3-0271-0662-s006638 | 13 | 2 | 11 | 654.5 |
| line-3-0401-0583-s003267 | 14 | 4 | 10 | 595.0 |
| line-3-0527-0507-s000000 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Qena/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
