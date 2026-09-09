# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **58 trainsets at 14 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0252-0535-s000000 | forward | 3 | pending |
| line-1 | line-1-0289-0468-s003000 | forward | 3 | pending |
| line-1 | line-1-0289-0468-s003000 | reverse | 3 | pending |
| line-1 | line-1-0363-0437-s005090 | forward | 3 | pending |
| line-1 | line-1-0363-0437-s005090 | reverse | 3 | pending |
| line-1 | line-1-0376-0379-s007160 | forward | 2 | pending |
| line-1 | line-1-0376-0379-s007160 | reverse | 2 | pending |
| line-1 | line-1-0408-0296-s009233 | forward | 2 | pending |
| line-1 | line-1-0408-0296-s009233 | reverse | 2 | pending |
| line-1 | line-1-0446-0235-s011333 | reverse | 2 | pending |
| line-2 | line-2-0525-0434-s000000 | forward | 3 | pending |
| line-2 | line-2-0448-0389-s002213 | forward | 3 | pending |
| line-2 | line-2-0448-0389-s002213 | reverse | 3 | pending |
| line-2 | line-2-0376-0379-s004451 | forward | 3 | pending |
| line-2 | line-2-0376-0379-s004451 | reverse | 2 | pending |
| line-2 | line-2-0337-0279-s007085 | forward | 2 | pending |
| line-2 | line-2-0337-0279-s007085 | reverse | 2 | pending |
| line-2 | line-2-0305-0177-s009718 | reverse | 2 | pending |
| line-3 | line-3-0269-0312-s000000 | forward | 4 | pending |
| line-3 | line-3-0376-0379-s003427 | forward | 3 | pending |
| line-3 | line-3-0376-0379-s003427 | reverse | 3 | pending |
| line-3 | line-3-0370-0499-s006026 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Iringa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
