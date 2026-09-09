# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **90 trainsets at 14 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **81 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0782-0630-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0683-0576-s003011 | forward | revenue | 5 | pending |
| line-1 | line-1-0683-0576-s003011 | reverse | revenue | 5 | pending |
| line-1 | line-1-0550-0551-s006258 | forward | revenue | 5 | pending |
| line-1 | line-1-0550-0551-s006258 | reverse | revenue | 5 | pending |
| line-1 | line-1-0468-0579-s009044 | forward | revenue | 5 | pending |
| line-1 | line-1-0468-0579-s009044 | reverse | revenue | 4 | pending |
| line-1 | line-1-0051-0779-s020226 | reverse | revenue | 4 | pending |
| line-1 | line-1-0468-0579-s009044 | reverse | spare | 1 | pending |
| line-1 | line-1-0051-0779-s020226 | reverse | spare | 1 | pending |
| line-1 | line-1-0782-0630-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0683-0576-s003011 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0693-0212-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0655-0372-s003843 | forward | revenue | 3 | pending |
| line-2 | line-2-0655-0372-s003843 | reverse | revenue | 3 | pending |
| line-2 | line-2-0556-0466-s006851 | forward | revenue | 3 | pending |
| line-2 | line-2-0556-0466-s006851 | reverse | revenue | 3 | pending |
| line-2 | line-2-0550-0551-s009106 | forward | revenue | 3 | pending |
| line-2 | line-2-0550-0551-s009106 | reverse | revenue | 3 | pending |
| line-2 | line-2-0550-0694-s012837 | reverse | revenue | 3 | pending |
| line-2 | line-2-0693-0212-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0655-0372-s003843 | forward | spare | 1 | pending |
| line-2 | line-2-0655-0372-s003843 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0771-0652-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0645-0645-s003015 | forward | revenue | 3 | pending |
| line-3 | line-3-0645-0645-s003015 | reverse | revenue | 3 | pending |
| line-3 | line-3-0550-0551-s005933 | forward | revenue | 3 | pending |
| line-3 | line-3-0550-0551-s005933 | reverse | revenue | 3 | pending |
| line-3 | line-3-0482-0431-s009479 | reverse | revenue | 3 | pending |
| line-3 | line-3-0645-0645-s003015 | forward | spare | 1 | pending |
| line-3 | line-3-0645-0645-s003015 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**56 trainsets exceed the reference platform envelope**, requiring **3,332.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0051-0779-s020226 | 5 | 2 | 3 | 178.5 |
| line-1-0468-0579-s009044 | 10 | 2 | 8 | 476.0 |
| line-1-0550-0551-s006258 | 10 | 4 | 6 | 357.0 |
| line-1-0683-0576-s003011 | 11 | 2 | 9 | 535.5 |
| line-1-0782-0630-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0550-0551-s009106 | 6 | 4 | 2 | 119.0 |
| line-2-0550-0694-s012837 | 3 | 2 | 1 | 59.5 |
| line-2-0556-0466-s006851 | 6 | 2 | 4 | 238.0 |
| line-2-0655-0372-s003843 | 8 | 2 | 6 | 357.0 |
| line-2-0693-0212-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0482-0431-s009479 | 3 | 2 | 1 | 59.5 |
| line-3-0550-0551-s005933 | 6 | 4 | 2 | 119.0 |
| line-3-0645-0645-s003015 | 8 | 2 | 6 | 357.0 |
| line-3-0771-0652-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Kumba/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
