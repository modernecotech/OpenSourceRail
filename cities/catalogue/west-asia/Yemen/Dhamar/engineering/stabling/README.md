# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **63 trainsets at 13 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0115-0301-s000000 | forward | 4 | pending |
| line-1 | line-1-0258-0288-s003349 | forward | 3 | pending |
| line-1 | line-1-0258-0288-s003349 | reverse | 3 | pending |
| line-1 | line-1-0312-0395-s006375 | forward | 3 | pending |
| line-1 | line-1-0312-0395-s006375 | reverse | 3 | pending |
| line-1 | line-1-0373-0372-s008718 | forward | 3 | pending |
| line-1 | line-1-0373-0372-s008718 | reverse | 3 | pending |
| line-1 | line-1-0445-0352-s011163 | reverse | 3 | pending |
| line-2 | line-2-0381-0463-s000000 | forward | 4 | pending |
| line-2 | line-2-0380-0336-s003018 | forward | 3 | pending |
| line-2 | line-2-0380-0336-s003018 | reverse | 3 | pending |
| line-2 | line-2-0421-0287-s005256 | forward | 3 | pending |
| line-2 | line-2-0421-0287-s005256 | reverse | 3 | pending |
| line-2 | line-2-0507-0274-s007496 | forward | 3 | pending |
| line-2 | line-2-0507-0274-s007496 | reverse | 3 | pending |
| line-2 | line-2-0679-0164-s011965 | reverse | 3 | pending |
| line-3 | line-3-0333-0446-s000000 | forward | 4 | pending |
| line-3 | line-3-0373-0372-s002272 | forward | 3 | pending |
| line-3 | line-3-0373-0372-s002272 | reverse | 3 | pending |
| line-3 | line-3-0295-0267-s005959 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Dhamar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
