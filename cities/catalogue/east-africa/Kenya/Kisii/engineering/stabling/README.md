# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **52 trainsets at 12 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0433-0474-s000000 | forward | 3 | pending |
| line-1 | line-1-0371-0371-s002960 | forward | 3 | pending |
| line-1 | line-1-0371-0371-s002960 | reverse | 3 | pending |
| line-1 | line-1-0321-0298-s005038 | forward | 3 | pending |
| line-1 | line-1-0321-0298-s005038 | reverse | 2 | pending |
| line-1 | line-1-0274-0217-s007109 | reverse | 2 | pending |
| line-2 | line-2-0226-0282-s000000 | forward | 3 | pending |
| line-2 | line-2-0304-0366-s003002 | forward | 3 | pending |
| line-2 | line-2-0304-0366-s003002 | reverse | 3 | pending |
| line-2 | line-2-0371-0371-s004682 | forward | 2 | pending |
| line-2 | line-2-0371-0371-s004682 | reverse | 2 | pending |
| line-2 | line-2-0369-0293-s006259 | reverse | 2 | pending |
| line-3 | line-3-0027-0326-s000000 | forward | 4 | pending |
| line-3 | line-3-0252-0359-s006340 | forward | 4 | pending |
| line-3 | line-3-0252-0359-s006340 | reverse | 4 | pending |
| line-3 | line-3-0315-0414-s008361 | forward | 3 | pending |
| line-3 | line-3-0315-0414-s008361 | reverse | 3 | pending |
| line-3 | line-3-0375-0406-s010911 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kisii/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
