# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **84 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **75 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0406-0246-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0376-0373-s003096 | forward | revenue | 5 | pending |
| line-1 | line-1-0376-0373-s003096 | reverse | revenue | 5 | pending |
| line-1 | line-1-0464-0386-s005190 | forward | revenue | 4 | pending |
| line-1 | line-1-0464-0386-s005190 | reverse | revenue | 4 | pending |
| line-1 | line-1-0729-0702-s014641 | reverse | revenue | 4 | pending |
| line-1 | line-1-0464-0386-s005190 | forward | spare | 1 | pending |
| line-1 | line-1-0464-0386-s005190 | reverse | spare | 1 | pending |
| line-1 | line-1-0729-0702-s014641 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0608-0115-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0490-0327-s005475 | forward | revenue | 4 | pending |
| line-2 | line-2-0490-0327-s005475 | reverse | revenue | 3 | pending |
| line-2 | line-2-0376-0373-s008216 | forward | revenue | 3 | pending |
| line-2 | line-2-0376-0373-s008216 | reverse | revenue | 3 | pending |
| line-2 | line-2-0316-0470-s011064 | forward | revenue | 3 | pending |
| line-2 | line-2-0316-0470-s011064 | reverse | revenue | 3 | pending |
| line-2 | line-2-0216-0565-s013915 | reverse | revenue | 3 | pending |
| line-2 | line-2-0490-0327-s005475 | reverse | spare | 1 | pending |
| line-2 | line-2-0376-0373-s008216 | forward | spare | 1 | pending |
| line-2 | line-2-0376-0373-s008216 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0529-0442-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0408-0415-s003022 | forward | revenue | 3 | pending |
| line-3 | line-3-0408-0415-s003022 | reverse | revenue | 3 | pending |
| line-3 | line-3-0376-0373-s004284 | forward | revenue | 3 | pending |
| line-3 | line-3-0376-0373-s004284 | reverse | revenue | 3 | pending |
| line-3 | line-3-0231-0325-s007801 | forward | revenue | 3 | pending |
| line-3 | line-3-0231-0325-s007801 | reverse | revenue | 2 | pending |
| line-3 | line-3-0068-0325-s011314 | reverse | revenue | 2 | pending |
| line-3 | line-3-0231-0325-s007801 | reverse | spare | 1 | pending |
| line-3 | line-3-0068-0325-s011314 | reverse | spare | 1 | pending |
| line-3 | line-3-0529-0442-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**50 trainsets exceed the reference platform envelope**, requiring **2,450.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0376-0373-s003096 | 10 | 4 | 6 | 294.0 |
| line-1-0406-0246-s000000 | 5 | 2 | 3 | 147.0 |
| line-1-0464-0386-s005190 | 10 | 2 | 8 | 392.0 |
| line-1-0729-0702-s014641 | 5 | 2 | 3 | 147.0 |
| line-2-0216-0565-s013915 | 3 | 2 | 1 | 49.0 |
| line-2-0316-0470-s011064 | 6 | 2 | 4 | 196.0 |
| line-2-0376-0373-s008216 | 8 | 4 | 4 | 196.0 |
| line-2-0490-0327-s005475 | 8 | 2 | 6 | 294.0 |
| line-2-0608-0115-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0068-0325-s011314 | 3 | 2 | 1 | 49.0 |
| line-3-0231-0325-s007801 | 6 | 2 | 4 | 196.0 |
| line-3-0376-0373-s004284 | 6 | 4 | 2 | 98.0 |
| line-3-0408-0415-s003022 | 6 | 2 | 4 | 196.0 |
| line-3-0529-0442-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kitale/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
