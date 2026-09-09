# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **77 trainsets at 16 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **69 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0252-0247-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0327-0342-s003015 | forward | revenue | 3 | pending |
| line-1 | line-1-0327-0342-s003015 | reverse | revenue | 3 | pending |
| line-1 | line-1-0380-0381-s005022 | forward | revenue | 2 | pending |
| line-1 | line-1-0380-0381-s005022 | reverse | revenue | 2 | pending |
| line-1 | line-1-0467-0411-s007449 | forward | revenue | 2 | pending |
| line-1 | line-1-0467-0411-s007449 | reverse | revenue | 2 | pending |
| line-1 | line-1-0550-0499-s009897 | reverse | revenue | 2 | pending |
| line-1 | line-1-0380-0381-s005022 | forward | spare | 1 | pending |
| line-1 | line-1-0380-0381-s005022 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0405-0744-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0421-0544-s004738 | forward | revenue | 4 | pending |
| line-2 | line-2-0421-0544-s004738 | reverse | revenue | 4 | pending |
| line-2 | line-2-0395-0458-s006702 | forward | revenue | 3 | pending |
| line-2 | line-2-0395-0458-s006702 | reverse | revenue | 3 | pending |
| line-2 | line-2-0380-0381-s008649 | forward | revenue | 3 | pending |
| line-2 | line-2-0380-0381-s008649 | reverse | revenue | 3 | pending |
| line-2 | line-2-0388-0126-s015010 | reverse | revenue | 3 | pending |
| line-2 | line-2-0395-0458-s006702 | forward | spare | 1 | pending |
| line-2 | line-2-0395-0458-s006702 | reverse | spare | 1 | pending |
| line-2 | line-2-0380-0381-s008649 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0109-0523-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0232-0389-s004220 | forward | revenue | 3 | pending |
| line-3 | line-3-0232-0389-s004220 | reverse | revenue | 3 | pending |
| line-3 | line-3-0316-0402-s006222 | forward | revenue | 2 | pending |
| line-3 | line-3-0316-0402-s006222 | reverse | revenue | 2 | pending |
| line-3 | line-3-0380-0381-s008214 | forward | revenue | 2 | pending |
| line-3 | line-3-0380-0381-s008214 | reverse | revenue | 2 | pending |
| line-3 | line-3-0466-0360-s010520 | forward | revenue | 2 | pending |
| line-3 | line-3-0466-0360-s010520 | reverse | revenue | 2 | pending |
| line-3 | line-3-0549-0386-s012824 | reverse | revenue | 2 | pending |
| line-3 | line-3-0316-0402-s006222 | forward | spare | 1 | pending |
| line-3 | line-3-0316-0402-s006222 | reverse | spare | 1 | pending |
| line-3 | line-3-0380-0381-s008214 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**39 trainsets exceed the reference platform envelope**, requiring **1,911.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0252-0247-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0327-0342-s003015 | 6 | 2 | 4 | 196.0 |
| line-1-0380-0381-s005022 | 6 | 4 | 2 | 98.0 |
| line-1-0467-0411-s007449 | 4 | 2 | 2 | 98.0 |
| line-1-0550-0499-s009897 | 2 | 2 | 0 | 0.0 |
| line-2-0380-0381-s008649 | 7 | 4 | 3 | 147.0 |
| line-2-0388-0126-s015010 | 3 | 2 | 1 | 49.0 |
| line-2-0395-0458-s006702 | 8 | 2 | 6 | 294.0 |
| line-2-0405-0744-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0421-0544-s004738 | 8 | 2 | 6 | 294.0 |
| line-3-0109-0523-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0232-0389-s004220 | 6 | 2 | 4 | 196.0 |
| line-3-0316-0402-s006222 | 6 | 2 | 4 | 196.0 |
| line-3-0380-0381-s008214 | 5 | 4 | 1 | 49.0 |
| line-3-0466-0360-s010520 | 4 | 2 | 2 | 98.0 |
| line-3-0549-0386-s012824 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Arua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
