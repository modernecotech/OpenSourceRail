# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **63 trainsets at 13 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **55 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0115-0301-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0258-0288-s003349 | forward | revenue | 3 | pending |
| line-1 | line-1-0258-0288-s003349 | reverse | revenue | 3 | pending |
| line-1 | line-1-0312-0395-s006375 | forward | revenue | 3 | pending |
| line-1 | line-1-0312-0395-s006375 | reverse | revenue | 3 | pending |
| line-1 | line-1-0373-0372-s008718 | forward | revenue | 3 | pending |
| line-1 | line-1-0373-0372-s008718 | reverse | revenue | 2 | pending |
| line-1 | line-1-0445-0352-s011163 | reverse | revenue | 2 | pending |
| line-1 | line-1-0373-0372-s008718 | reverse | spare | 1 | pending |
| line-1 | line-1-0445-0352-s011163 | reverse | spare | 1 | pending |
| line-1 | line-1-0115-0301-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0381-0463-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0380-0336-s003018 | forward | revenue | 3 | pending |
| line-2 | line-2-0380-0336-s003018 | reverse | revenue | 3 | pending |
| line-2 | line-2-0421-0287-s005256 | forward | revenue | 3 | pending |
| line-2 | line-2-0421-0287-s005256 | reverse | revenue | 3 | pending |
| line-2 | line-2-0507-0274-s007496 | forward | revenue | 3 | pending |
| line-2 | line-2-0507-0274-s007496 | reverse | revenue | 2 | pending |
| line-2 | line-2-0679-0164-s011965 | reverse | revenue | 2 | pending |
| line-2 | line-2-0507-0274-s007496 | reverse | spare | 1 | pending |
| line-2 | line-2-0679-0164-s011965 | reverse | spare | 1 | pending |
| line-2 | line-2-0381-0463-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0333-0446-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0373-0372-s002272 | forward | revenue | 3 | pending |
| line-3 | line-3-0373-0372-s002272 | reverse | revenue | 3 | pending |
| line-3 | line-3-0295-0267-s005959 | reverse | revenue | 2 | pending |
| line-3 | line-3-0295-0267-s005959 | reverse | spare | 1 | pending |
| line-3 | line-3-0333-0446-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**33 trainsets exceed the reference platform envelope**, requiring **1,617.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0115-0301-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0258-0288-s003349 | 6 | 2 | 4 | 196.0 |
| line-1-0312-0395-s006375 | 6 | 2 | 4 | 196.0 |
| line-1-0373-0372-s008718 | 6 | 4 | 2 | 98.0 |
| line-1-0445-0352-s011163 | 3 | 2 | 1 | 49.0 |
| line-2-0380-0336-s003018 | 6 | 2 | 4 | 196.0 |
| line-2-0381-0463-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0421-0287-s005256 | 6 | 2 | 4 | 196.0 |
| line-2-0507-0274-s007496 | 6 | 2 | 4 | 196.0 |
| line-2-0679-0164-s011965 | 3 | 2 | 1 | 49.0 |
| line-3-0295-0267-s005959 | 3 | 2 | 1 | 49.0 |
| line-3-0333-0446-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0373-0372-s002272 | 6 | 4 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Dhamar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
