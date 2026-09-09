# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **79 trainsets at 13 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0204-0204-s000000 | forward | 5 | pending |
| line-1 | line-1-0316-0332-s003915 | forward | 5 | pending |
| line-1 | line-1-0316-0332-s003915 | reverse | 5 | pending |
| line-1 | line-1-0386-0374-s005818 | forward | 5 | pending |
| line-1 | line-1-0386-0374-s005818 | reverse | 5 | pending |
| line-1 | line-1-0728-0413-s014154 | reverse | 4 | pending |
| line-2 | line-2-0706-0380-s000000 | forward | 4 | pending |
| line-2 | line-2-0456-0355-s006845 | forward | 4 | pending |
| line-2 | line-2-0456-0355-s006845 | reverse | 3 | pending |
| line-2 | line-2-0386-0374-s008743 | forward | 3 | pending |
| line-2 | line-2-0386-0374-s008743 | reverse | 3 | pending |
| line-2 | line-2-0354-0390-s009970 | reverse | 3 | pending |
| line-3 | line-3-0586-0588-s000000 | forward | 4 | pending |
| line-3 | line-3-0435-0449-s004369 | forward | 4 | pending |
| line-3 | line-3-0435-0449-s004369 | reverse | 4 | pending |
| line-3 | line-3-0386-0374-s006595 | forward | 4 | pending |
| line-3 | line-3-0386-0374-s006595 | reverse | 4 | pending |
| line-3 | line-3-0262-0224-s010714 | forward | 4 | pending |
| line-3 | line-3-0262-0224-s010714 | reverse | 3 | pending |
| line-3 | line-3-0122-0114-s014860 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Naivasha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
