# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **67 trainsets at 14 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **60 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0632-0366-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0490-0366-s003327 | forward | revenue | 3 | pending |
| line-1 | line-1-0490-0366-s003327 | reverse | revenue | 3 | pending |
| line-1 | line-1-0371-0378-s006019 | forward | revenue | 3 | pending |
| line-1 | line-1-0371-0378-s006019 | reverse | revenue | 3 | pending |
| line-1 | line-1-0271-0362-s008476 | forward | revenue | 3 | pending |
| line-1 | line-1-0271-0362-s008476 | reverse | revenue | 2 | pending |
| line-1 | line-1-0171-0406-s010935 | forward | revenue | 2 | pending |
| line-1 | line-1-0171-0406-s010935 | reverse | revenue | 2 | pending |
| line-1 | line-1-0059-0424-s013390 | reverse | revenue | 2 | pending |
| line-1 | line-1-0271-0362-s008476 | reverse | spare | 1 | pending |
| line-1 | line-1-0171-0406-s010935 | forward | spare | 1 | pending |
| line-1 | line-1-0171-0406-s010935 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0547-0484-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0423-0421-s003025 | forward | revenue | 3 | pending |
| line-2 | line-2-0423-0421-s003025 | reverse | revenue | 3 | pending |
| line-2 | line-2-0371-0378-s004800 | forward | revenue | 2 | pending |
| line-2 | line-2-0371-0378-s004800 | reverse | revenue | 2 | pending |
| line-2 | line-2-0339-0471-s007474 | reverse | revenue | 2 | pending |
| line-2 | line-2-0371-0378-s004800 | forward | spare | 1 | pending |
| line-2 | line-2-0371-0378-s004800 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0439-0080-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0374-0313-s006167 | forward | revenue | 3 | pending |
| line-3 | line-3-0374-0313-s006167 | reverse | revenue | 3 | pending |
| line-3 | line-3-0371-0378-s007558 | forward | revenue | 3 | pending |
| line-3 | line-3-0371-0378-s007558 | reverse | revenue | 3 | pending |
| line-3 | line-3-0242-0424-s010965 | reverse | revenue | 3 | pending |
| line-3 | line-3-0374-0313-s006167 | forward | spare | 1 | pending |
| line-3 | line-3-0374-0313-s006167 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**33 trainsets exceed the reference platform envelope**, requiring **1,617.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0059-0424-s013390 | 2 | 2 | 0 | 0.0 |
| line-1-0171-0406-s010935 | 6 | 2 | 4 | 196.0 |
| line-1-0271-0362-s008476 | 6 | 2 | 4 | 196.0 |
| line-1-0371-0378-s006019 | 6 | 4 | 2 | 98.0 |
| line-1-0490-0366-s003327 | 6 | 2 | 4 | 196.0 |
| line-1-0632-0366-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0339-0471-s007474 | 2 | 2 | 0 | 0.0 |
| line-2-0371-0378-s004800 | 6 | 4 | 2 | 98.0 |
| line-2-0423-0421-s003025 | 6 | 2 | 4 | 196.0 |
| line-2-0547-0484-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0242-0424-s010965 | 3 | 2 | 1 | 49.0 |
| line-3-0371-0378-s007558 | 6 | 4 | 2 | 98.0 |
| line-3-0374-0313-s006167 | 8 | 2 | 6 | 294.0 |
| line-3-0439-0080-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Nepal/Biratnagar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
