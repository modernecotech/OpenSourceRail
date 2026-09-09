# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **92 trainsets at 15 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **82 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0151-0084-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0350-0329-s006913 | forward | revenue | 4 | pending |
| line-1 | line-1-0350-0329-s006913 | reverse | revenue | 3 | pending |
| line-1 | line-1-0462-0446-s010181 | forward | revenue | 3 | pending |
| line-1 | line-1-0462-0446-s010181 | reverse | revenue | 3 | pending |
| line-1 | line-1-0551-0546-s012918 | forward | revenue | 3 | pending |
| line-1 | line-1-0551-0546-s012918 | reverse | revenue | 3 | pending |
| line-1 | line-1-0639-0634-s015419 | forward | revenue | 3 | pending |
| line-1 | line-1-0639-0634-s015419 | reverse | revenue | 3 | pending |
| line-1 | line-1-0655-0732-s017944 | forward | revenue | 3 | pending |
| line-1 | line-1-0655-0732-s017944 | reverse | revenue | 3 | pending |
| line-1 | line-1-0703-0822-s020445 | reverse | revenue | 3 | pending |
| line-1 | line-1-0350-0329-s006913 | reverse | spare | 1 | pending |
| line-1 | line-1-0462-0446-s010181 | forward | spare | 1 | pending |
| line-1 | line-1-0462-0446-s010181 | reverse | spare | 1 | pending |
| line-1 | line-1-0551-0546-s012918 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0449-0338-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0527-0456-s003006 | forward | revenue | 4 | pending |
| line-2 | line-2-0527-0456-s003006 | reverse | revenue | 4 | pending |
| line-2 | line-2-0551-0546-s005171 | forward | revenue | 4 | pending |
| line-2 | line-2-0551-0546-s005171 | reverse | revenue | 4 | pending |
| line-2 | line-2-0814-0509-s012041 | reverse | revenue | 3 | pending |
| line-2 | line-2-0814-0509-s012041 | reverse | spare | 1 | pending |
| line-2 | line-2-0449-0338-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0527-0456-s003006 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0861-0445-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0683-0521-s004728 | forward | revenue | 4 | pending |
| line-3 | line-3-0683-0521-s004728 | reverse | revenue | 4 | pending |
| line-3 | line-3-0551-0546-s007744 | forward | revenue | 3 | pending |
| line-3 | line-3-0551-0546-s007744 | reverse | revenue | 3 | pending |
| line-3 | line-3-0590-0702-s011237 | reverse | revenue | 3 | pending |
| line-3 | line-3-0551-0546-s007744 | forward | spare | 1 | pending |
| line-3 | line-3-0551-0546-s007744 | reverse | spare | 1 | pending |
| line-3 | line-3-0590-0702-s011237 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**56 trainsets exceed the reference platform envelope**, requiring **3,332.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0151-0084-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0350-0329-s006913 | 8 | 2 | 6 | 357.0 |
| line-1-0462-0446-s010181 | 8 | 2 | 6 | 357.0 |
| line-1-0551-0546-s012918 | 7 | 4 | 3 | 178.5 |
| line-1-0639-0634-s015419 | 6 | 2 | 4 | 238.0 |
| line-1-0655-0732-s017944 | 6 | 2 | 4 | 238.0 |
| line-1-0703-0822-s020445 | 3 | 2 | 1 | 59.5 |
| line-2-0449-0338-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0527-0456-s003006 | 9 | 2 | 7 | 416.5 |
| line-2-0551-0546-s005171 | 8 | 4 | 4 | 238.0 |
| line-2-0814-0509-s012041 | 4 | 2 | 2 | 119.0 |
| line-3-0551-0546-s007744 | 8 | 4 | 4 | 238.0 |
| line-3-0590-0702-s011237 | 4 | 2 | 2 | 119.0 |
| line-3-0683-0521-s004728 | 8 | 2 | 6 | 357.0 |
| line-3-0861-0445-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Sukkur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
