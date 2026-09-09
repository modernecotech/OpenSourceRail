# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **87 trainsets at 18 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **78 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0517-0336-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0568-0338-s001954 | forward | revenue | 3 | pending |
| line-1 | line-1-0568-0338-s001954 | reverse | revenue | 3 | pending |
| line-1 | line-1-0563-0423-s003928 | forward | revenue | 2 | pending |
| line-1 | line-1-0563-0423-s003928 | reverse | revenue | 2 | pending |
| line-1 | line-1-0592-0495-s006007 | forward | revenue | 2 | pending |
| line-1 | line-1-0592-0495-s006007 | reverse | revenue | 2 | pending |
| line-1 | line-1-0614-0565-s008069 | forward | revenue | 2 | pending |
| line-1 | line-1-0614-0565-s008069 | reverse | revenue | 2 | pending |
| line-1 | line-1-0669-0645-s010737 | forward | revenue | 2 | pending |
| line-1 | line-1-0669-0645-s010737 | reverse | revenue | 2 | pending |
| line-1 | line-1-0761-0719-s013401 | reverse | revenue | 2 | pending |
| line-1 | line-1-0563-0423-s003928 | forward | spare | 1 | pending |
| line-1 | line-1-0563-0423-s003928 | reverse | spare | 1 | pending |
| line-1 | line-1-0592-0495-s006007 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0863-0415-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0734-0429-s003018 | forward | revenue | 3 | pending |
| line-2 | line-2-0734-0429-s003018 | reverse | revenue | 3 | pending |
| line-2 | line-2-0691-0483-s004630 | forward | revenue | 3 | pending |
| line-2 | line-2-0691-0483-s004630 | reverse | revenue | 2 | pending |
| line-2 | line-2-0614-0565-s007472 | forward | revenue | 2 | pending |
| line-2 | line-2-0614-0565-s007472 | reverse | revenue | 2 | pending |
| line-2 | line-2-0529-0610-s009613 | forward | revenue | 2 | pending |
| line-2 | line-2-0529-0610-s009613 | reverse | revenue | 2 | pending |
| line-2 | line-2-0476-0688-s011760 | reverse | revenue | 2 | pending |
| line-2 | line-2-0691-0483-s004630 | reverse | spare | 1 | pending |
| line-2 | line-2-0614-0565-s007472 | forward | spare | 1 | pending |
| line-2 | line-2-0614-0565-s007472 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0276-0370-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0473-0484-s005686 | forward | revenue | 4 | pending |
| line-3 | line-3-0473-0484-s005686 | reverse | revenue | 4 | pending |
| line-3 | line-3-0542-0523-s007703 | forward | revenue | 3 | pending |
| line-3 | line-3-0542-0523-s007703 | reverse | revenue | 3 | pending |
| line-3 | line-3-0614-0565-s009710 | forward | revenue | 3 | pending |
| line-3 | line-3-0614-0565-s009710 | reverse | revenue | 3 | pending |
| line-3 | line-3-0643-0792-s014803 | reverse | revenue | 3 | pending |
| line-3 | line-3-0542-0523-s007703 | forward | spare | 1 | pending |
| line-3 | line-3-0542-0523-s007703 | reverse | spare | 1 | pending |
| line-3 | line-3-0614-0565-s009710 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**45 trainsets exceed the reference platform envelope**, requiring **2,677.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0517-0336-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0563-0423-s003928 | 6 | 2 | 4 | 238.0 |
| line-1-0568-0338-s001954 | 6 | 2 | 4 | 238.0 |
| line-1-0592-0495-s006007 | 5 | 2 | 3 | 178.5 |
| line-1-0614-0565-s008069 | 4 | 4 | 0 | 0.0 |
| line-1-0669-0645-s010737 | 4 | 2 | 2 | 119.0 |
| line-1-0761-0719-s013401 | 2 | 2 | 0 | 0.0 |
| line-2-0476-0688-s011760 | 2 | 2 | 0 | 0.0 |
| line-2-0529-0610-s009613 | 4 | 2 | 2 | 119.0 |
| line-2-0614-0565-s007472 | 6 | 4 | 2 | 119.0 |
| line-2-0691-0483-s004630 | 6 | 2 | 4 | 238.0 |
| line-2-0734-0429-s003018 | 6 | 2 | 4 | 238.0 |
| line-2-0863-0415-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0276-0370-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0473-0484-s005686 | 8 | 2 | 6 | 357.0 |
| line-3-0542-0523-s007703 | 8 | 2 | 6 | 357.0 |
| line-3-0614-0565-s009710 | 7 | 4 | 3 | 178.5 |
| line-3-0643-0792-s014803 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Homs/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
