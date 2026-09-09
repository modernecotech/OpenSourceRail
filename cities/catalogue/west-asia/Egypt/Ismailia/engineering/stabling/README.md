# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **119 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **106 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0601-0847-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0578-0714-s003007 | forward | revenue | 3 | pending |
| line-1 | line-1-0578-0714-s003007 | reverse | revenue | 3 | pending |
| line-1 | line-1-0550-0652-s006018 | forward | revenue | 3 | pending |
| line-1 | line-1-0550-0652-s006018 | reverse | revenue | 3 | pending |
| line-1 | line-1-0546-0559-s008210 | forward | revenue | 3 | pending |
| line-1 | line-1-0546-0559-s008210 | reverse | revenue | 3 | pending |
| line-1 | line-1-0527-0507-s010648 | forward | revenue | 3 | pending |
| line-1 | line-1-0527-0507-s010648 | reverse | revenue | 3 | pending |
| line-1 | line-1-0443-0438-s013087 | forward | revenue | 2 | pending |
| line-1 | line-1-0443-0438-s013087 | reverse | revenue | 2 | pending |
| line-1 | line-1-0417-0352-s015517 | reverse | revenue | 2 | pending |
| line-1 | line-1-0443-0438-s013087 | forward | spare | 1 | pending |
| line-1 | line-1-0443-0438-s013087 | reverse | spare | 1 | pending |
| line-1 | line-1-0417-0352-s015517 | reverse | spare | 1 | pending |
| line-1 | line-1-0601-0847-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0179-0919-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0365-0785-s007018 | forward | revenue | 3 | pending |
| line-2 | line-2-0365-0785-s007018 | reverse | revenue | 3 | pending |
| line-2 | line-2-0421-0694-s010034 | forward | revenue | 3 | pending |
| line-2 | line-2-0421-0694-s010034 | reverse | revenue | 3 | pending |
| line-2 | line-2-0434-0624-s011908 | forward | revenue | 3 | pending |
| line-2 | line-2-0434-0624-s011908 | reverse | revenue | 3 | pending |
| line-2 | line-2-0495-0578-s013509 | forward | revenue | 3 | pending |
| line-2 | line-2-0495-0578-s013509 | reverse | revenue | 3 | pending |
| line-2 | line-2-0546-0559-s014981 | forward | revenue | 3 | pending |
| line-2 | line-2-0546-0559-s014981 | reverse | revenue | 3 | pending |
| line-2 | line-2-0600-0537-s016513 | forward | revenue | 3 | pending |
| line-2 | line-2-0600-0537-s016513 | reverse | revenue | 3 | pending |
| line-2 | line-2-0659-0493-s018528 | forward | revenue | 3 | pending |
| line-2 | line-2-0659-0493-s018528 | reverse | revenue | 3 | pending |
| line-2 | line-2-0749-0477-s020544 | forward | revenue | 3 | pending |
| line-2 | line-2-0749-0477-s020544 | reverse | revenue | 2 | pending |
| line-2 | line-2-0777-0419-s022545 | reverse | revenue | 2 | pending |
| line-2 | line-2-0749-0477-s020544 | reverse | spare | 1 | pending |
| line-2 | line-2-0777-0419-s022545 | reverse | spare | 1 | pending |
| line-2 | line-2-0179-0919-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0365-0785-s007018 | forward | spare | 1 | pending |
| line-2 | line-2-0365-0785-s007018 | reverse | spare | 1 | pending |
| line-2 | line-2-0421-0694-s010034 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0805-0639-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0683-0575-s003015 | forward | revenue | 4 | pending |
| line-3 | line-3-0683-0575-s003015 | reverse | revenue | 4 | pending |
| line-3 | line-3-0546-0559-s006400 | forward | revenue | 3 | pending |
| line-3 | line-3-0546-0559-s006400 | reverse | revenue | 3 | pending |
| line-3 | line-3-0411-0543-s009637 | reverse | revenue | 3 | pending |
| line-3 | line-3-0546-0559-s006400 | forward | spare | 1 | pending |
| line-3 | line-3-0546-0559-s006400 | reverse | spare | 1 | pending |
| line-3 | line-3-0411-0543-s009637 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**71 trainsets exceed the reference platform envelope**, requiring **4,224.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0417-0352-s015517 | 3 | 2 | 1 | 59.5 |
| line-1-0443-0438-s013087 | 6 | 2 | 4 | 238.0 |
| line-1-0527-0507-s010648 | 6 | 2 | 4 | 238.0 |
| line-1-0546-0559-s008210 | 6 | 4 | 2 | 119.0 |
| line-1-0550-0652-s006018 | 6 | 2 | 4 | 238.0 |
| line-1-0578-0714-s003007 | 6 | 2 | 4 | 238.0 |
| line-1-0601-0847-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0179-0919-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0365-0785-s007018 | 8 | 2 | 6 | 357.0 |
| line-2-0421-0694-s010034 | 7 | 2 | 5 | 297.5 |
| line-2-0434-0624-s011908 | 6 | 2 | 4 | 238.0 |
| line-2-0495-0578-s013509 | 6 | 2 | 4 | 238.0 |
| line-2-0546-0559-s014981 | 6 | 4 | 2 | 119.0 |
| line-2-0600-0537-s016513 | 6 | 2 | 4 | 238.0 |
| line-2-0659-0493-s018528 | 6 | 2 | 4 | 238.0 |
| line-2-0749-0477-s020544 | 6 | 2 | 4 | 238.0 |
| line-2-0777-0419-s022545 | 3 | 2 | 1 | 59.5 |
| line-3-0411-0543-s009637 | 4 | 2 | 2 | 119.0 |
| line-3-0546-0559-s006400 | 8 | 4 | 4 | 238.0 |
| line-3-0683-0575-s003015 | 8 | 2 | 6 | 357.0 |
| line-3-0805-0639-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Ismailia/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
