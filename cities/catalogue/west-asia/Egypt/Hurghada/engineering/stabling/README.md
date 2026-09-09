# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **80 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0155-0041-s000000 | forward | 3 | pending |
| line-1 | line-1-0228-0160-s003013 | forward | 3 | pending |
| line-1 | line-1-0228-0160-s003013 | reverse | 3 | pending |
| line-1 | line-1-0316-0272-s006017 | forward | 3 | pending |
| line-1 | line-1-0316-0272-s006017 | reverse | 3 | pending |
| line-1 | line-1-0395-0376-s009125 | forward | 3 | pending |
| line-1 | line-1-0395-0376-s009125 | reverse | 3 | pending |
| line-1 | line-1-0476-0468-s011960 | forward | 3 | pending |
| line-1 | line-1-0476-0468-s011960 | reverse | 3 | pending |
| line-1 | line-1-0553-0553-s014455 | reverse | 3 | pending |
| line-2 | line-2-0729-0464-s000000 | forward | 3 | pending |
| line-2 | line-2-0612-0409-s003009 | forward | 3 | pending |
| line-2 | line-2-0612-0409-s003009 | reverse | 3 | pending |
| line-2 | line-2-0483-0386-s006012 | forward | 3 | pending |
| line-2 | line-2-0483-0386-s006012 | reverse | 3 | pending |
| line-2 | line-2-0395-0376-s008759 | forward | 3 | pending |
| line-2 | line-2-0395-0376-s008759 | reverse | 3 | pending |
| line-2 | line-2-0344-0267-s011708 | forward | 3 | pending |
| line-2 | line-2-0344-0267-s011708 | reverse | 3 | pending |
| line-2 | line-2-0242-0142-s015180 | reverse | 3 | pending |
| line-3 | line-3-0460-0535-s000000 | forward | 3 | pending |
| line-3 | line-3-0386-0435-s003027 | forward | 3 | pending |
| line-3 | line-3-0386-0435-s003027 | reverse | 3 | pending |
| line-3 | line-3-0395-0376-s004630 | forward | 3 | pending |
| line-3 | line-3-0395-0376-s004630 | reverse | 2 | pending |
| line-3 | line-3-0462-0323-s006986 | forward | 2 | pending |
| line-3 | line-3-0462-0323-s006986 | reverse | 2 | pending |
| line-3 | line-3-0552-0311-s009332 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Hurghada/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
