# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **61 trainsets at 11 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **54 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0685-0401-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0427-0424-s005898 | forward | revenue | 4 | pending |
| line-1 | line-1-0427-0424-s005898 | reverse | revenue | 4 | pending |
| line-1 | line-1-0376-0370-s007839 | forward | revenue | 4 | pending |
| line-1 | line-1-0376-0370-s007839 | reverse | revenue | 4 | pending |
| line-1 | line-1-0168-0334-s013573 | reverse | revenue | 4 | pending |
| line-1 | line-1-0427-0424-s005898 | forward | spare | 1 | pending |
| line-1 | line-1-0427-0424-s005898 | reverse | spare | 1 | pending |
| line-1 | line-1-0376-0370-s007839 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0349-0364-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0356-0298-s002589 | forward | revenue | 3 | pending |
| line-2 | line-2-0356-0298-s002589 | reverse | revenue | 3 | pending |
| line-2 | line-2-0280-0235-s005188 | reverse | revenue | 2 | pending |
| line-2 | line-2-0280-0235-s005188 | reverse | spare | 1 | pending |
| line-2 | line-2-0349-0364-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0401-0363-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0387-0293-s002312 | forward | revenue | 3 | pending |
| line-3 | line-3-0387-0293-s002312 | reverse | revenue | 3 | pending |
| line-3 | line-3-0419-0202-s004608 | forward | revenue | 3 | pending |
| line-3 | line-3-0419-0202-s004608 | reverse | revenue | 3 | pending |
| line-3 | line-3-0572-0072-s009213 | reverse | revenue | 3 | pending |
| line-3 | line-3-0401-0363-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0387-0293-s002312 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**37 trainsets exceed the reference platform envelope**, requiring **1,813.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0168-0334-s013573 | 4 | 2 | 2 | 98.0 |
| line-1-0376-0370-s007839 | 9 | 4 | 5 | 245.0 |
| line-1-0427-0424-s005898 | 10 | 2 | 8 | 392.0 |
| line-1-0685-0401-s000000 | 5 | 2 | 3 | 147.0 |
| line-2-0280-0235-s005188 | 3 | 2 | 1 | 49.0 |
| line-2-0349-0364-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0356-0298-s002589 | 6 | 2 | 4 | 196.0 |
| line-3-0387-0293-s002312 | 7 | 2 | 5 | 245.0 |
| line-3-0401-0363-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0419-0202-s004608 | 6 | 2 | 4 | 196.0 |
| line-3-0572-0072-s009213 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Meru-Ke/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
