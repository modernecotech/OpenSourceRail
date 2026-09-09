# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **76 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0538-0267-s000000 | forward | 3 | pending |
| line-1 | line-1-0456-0328-s003020 | forward | 3 | pending |
| line-1 | line-1-0456-0328-s003020 | reverse | 3 | pending |
| line-1 | line-1-0384-0396-s005220 | forward | 3 | pending |
| line-1 | line-1-0384-0396-s005220 | reverse | 3 | pending |
| line-1 | line-1-0429-0465-s007719 | forward | 3 | pending |
| line-1 | line-1-0429-0465-s007719 | reverse | 2 | pending |
| line-1 | line-1-0440-0568-s010031 | forward | 2 | pending |
| line-1 | line-1-0440-0568-s010031 | reverse | 2 | pending |
| line-1 | line-1-0406-0668-s012325 | reverse | 2 | pending |
| line-2 | line-2-0550-0738-s000000 | forward | 3 | pending |
| line-2 | line-2-0511-0559-s004314 | forward | 3 | pending |
| line-2 | line-2-0511-0559-s004314 | reverse | 3 | pending |
| line-2 | line-2-0411-0495-s007332 | forward | 3 | pending |
| line-2 | line-2-0411-0495-s007332 | reverse | 3 | pending |
| line-2 | line-2-0384-0396-s010681 | forward | 3 | pending |
| line-2 | line-2-0384-0396-s010681 | reverse | 3 | pending |
| line-2 | line-2-0298-0391-s012702 | forward | 3 | pending |
| line-2 | line-2-0298-0391-s012702 | reverse | 3 | pending |
| line-2 | line-2-0217-0397-s014734 | reverse | 3 | pending |
| line-3 | line-3-0271-0514-s000000 | forward | 3 | pending |
| line-3 | line-3-0342-0432-s003016 | forward | 3 | pending |
| line-3 | line-3-0342-0432-s003016 | reverse | 3 | pending |
| line-3 | line-3-0384-0396-s004354 | forward | 3 | pending |
| line-3 | line-3-0384-0396-s004354 | reverse | 2 | pending |
| line-3 | line-3-0469-0419-s006620 | forward | 2 | pending |
| line-3 | line-3-0469-0419-s006620 | reverse | 2 | pending |
| line-3 | line-3-0557-0472-s008869 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Kigoma/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
