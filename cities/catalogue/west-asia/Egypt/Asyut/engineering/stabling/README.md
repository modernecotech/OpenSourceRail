# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **162 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **146 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0660-0667-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0606-0623-s001974 | forward | revenue | 4 | pending |
| line-1 | line-1-0606-0623-s001974 | reverse | revenue | 4 | pending |
| line-1 | line-1-0539-0559-s003931 | forward | revenue | 4 | pending |
| line-1 | line-1-0539-0559-s003931 | reverse | revenue | 4 | pending |
| line-1 | line-1-0415-0467-s007643 | reverse | revenue | 3 | pending |
| line-1 | line-1-0415-0467-s007643 | reverse | spare | 1 | pending |
| line-1 | line-1-0660-0667-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0606-0623-s001974 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0565-0462-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0539-0559-s002524 | forward | revenue | 7 | pending |
| line-2 | line-2-0539-0559-s002524 | reverse | revenue | 7 | pending |
| line-2 | line-2-0451-0605-s004952 | forward | revenue | 7 | pending |
| line-2 | line-2-0451-0605-s004952 | reverse | revenue | 7 | pending |
| line-2 | line-2-0458-0734-s008451 | forward | revenue | 7 | pending |
| line-2 | line-2-0458-0734-s008451 | reverse | revenue | 7 | pending |
| line-2 | line-2-0070-1066-s019747 | reverse | revenue | 7 | pending |
| line-2 | line-2-0565-0462-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0539-0559-s002524 | forward | spare | 1 | pending |
| line-2 | line-2-0539-0559-s002524 | reverse | spare | 1 | pending |
| line-2 | line-2-0451-0605-s004952 | forward | spare | 1 | pending |
| line-2 | line-2-0451-0605-s004952 | reverse | spare | 1 | pending |
| line-2 | line-2-0458-0734-s008451 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1023-1006-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0623-0679-s012022 | forward | revenue | 7 | pending |
| line-3 | line-3-0623-0679-s012022 | reverse | revenue | 7 | pending |
| line-3 | line-3-0556-0621-s013918 | forward | revenue | 7 | pending |
| line-3 | line-3-0556-0621-s013918 | reverse | revenue | 7 | pending |
| line-3 | line-3-0539-0559-s015806 | forward | revenue | 7 | pending |
| line-3 | line-3-0539-0559-s015806 | reverse | revenue | 7 | pending |
| line-3 | line-3-0533-0470-s018058 | forward | revenue | 6 | pending |
| line-3 | line-3-0533-0470-s018058 | reverse | revenue | 6 | pending |
| line-3 | line-3-0480-0214-s024352 | reverse | revenue | 6 | pending |
| line-3 | line-3-0533-0470-s018058 | forward | spare | 1 | pending |
| line-3 | line-3-0533-0470-s018058 | reverse | spare | 1 | pending |
| line-3 | line-3-0480-0214-s024352 | reverse | spare | 1 | pending |
| line-3 | line-3-1023-1006-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0623-0679-s012022 | forward | spare | 1 | pending |
| line-3 | line-3-0623-0679-s012022 | reverse | spare | 1 | pending |
| line-3 | line-3-0556-0621-s013918 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**124 trainsets exceed the reference platform envelope**, requiring **7,378.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0415-0467-s007643 | 4 | 2 | 2 | 119.0 |
| line-1-0539-0559-s003931 | 8 | 4 | 4 | 238.0 |
| line-1-0606-0623-s001974 | 9 | 2 | 7 | 416.5 |
| line-1-0660-0667-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0070-1066-s019747 | 7 | 2 | 5 | 297.5 |
| line-2-0451-0605-s004952 | 16 | 2 | 14 | 833.0 |
| line-2-0458-0734-s008451 | 15 | 2 | 13 | 773.5 |
| line-2-0539-0559-s002524 | 16 | 4 | 12 | 714.0 |
| line-2-0565-0462-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0480-0214-s024352 | 7 | 2 | 5 | 297.5 |
| line-3-0533-0470-s018058 | 14 | 4 | 10 | 595.0 |
| line-3-0539-0559-s015806 | 14 | 4 | 10 | 595.0 |
| line-3-0556-0621-s013918 | 15 | 2 | 13 | 773.5 |
| line-3-0623-0679-s012022 | 16 | 2 | 14 | 833.0 |
| line-3-1023-1006-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Asyut/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
