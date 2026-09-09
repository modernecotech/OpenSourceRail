# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **49 trainsets at 10 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0425-0237-s000000 | forward | 5 | pending |
| line-1 | line-1-0381-0373-s003463 | forward | 4 | pending |
| line-1 | line-1-0381-0373-s003463 | reverse | 4 | pending |
| line-1 | line-1-0463-0411-s006024 | forward | 4 | pending |
| line-1 | line-1-0463-0411-s006024 | reverse | 4 | pending |
| line-1 | line-1-0707-0423-s012342 | reverse | 4 | pending |
| line-2 | line-2-0418-0315-s000000 | forward | 3 | pending |
| line-2 | line-2-0381-0373-s001575 | forward | 3 | pending |
| line-2 | line-2-0381-0373-s001575 | reverse | 3 | pending |
| line-2 | line-2-0367-0469-s003929 | reverse | 3 | pending |
| line-3 | line-3-0391-0244-s000000 | forward | 3 | pending |
| line-3 | line-3-0381-0373-s002852 | forward | 3 | pending |
| line-3 | line-3-0381-0373-s002852 | reverse | 3 | pending |
| line-3 | line-3-0396-0442-s004879 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Tabora/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
