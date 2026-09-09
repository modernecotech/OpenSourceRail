# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **91 trainsets at 19 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0294-0029-s000000 | forward | 3 | pending |
| line-1 | line-1-0356-0080-s003014 | forward | 3 | pending |
| line-1 | line-1-0356-0080-s003014 | reverse | 3 | pending |
| line-1 | line-1-0375-0200-s006026 | forward | 3 | pending |
| line-1 | line-1-0375-0200-s006026 | reverse | 3 | pending |
| line-1 | line-1-0376-0285-s009028 | forward | 3 | pending |
| line-1 | line-1-0376-0285-s009028 | reverse | 2 | pending |
| line-1 | line-1-0369-0347-s011472 | forward | 2 | pending |
| line-1 | line-1-0369-0347-s011472 | reverse | 2 | pending |
| line-1 | line-1-0316-0388-s013394 | forward | 2 | pending |
| line-1 | line-1-0316-0388-s013394 | reverse | 2 | pending |
| line-1 | line-1-0255-0427-s015332 | reverse | 2 | pending |
| line-2 | line-2-0710-0450-s000000 | forward | 4 | pending |
| line-2 | line-2-0552-0402-s004630 | forward | 3 | pending |
| line-2 | line-2-0552-0402-s004630 | reverse | 3 | pending |
| line-2 | line-2-0446-0343-s007640 | forward | 3 | pending |
| line-2 | line-2-0446-0343-s007640 | reverse | 3 | pending |
| line-2 | line-2-0369-0347-s010215 | forward | 3 | pending |
| line-2 | line-2-0369-0347-s010215 | reverse | 3 | pending |
| line-2 | line-2-0311-0264-s013039 | forward | 3 | pending |
| line-2 | line-2-0311-0264-s013039 | reverse | 3 | pending |
| line-2 | line-2-0253-0189-s015878 | reverse | 3 | pending |
| line-3 | line-3-0205-0212-s000000 | forward | 3 | pending |
| line-3 | line-3-0283-0322-s003025 | forward | 3 | pending |
| line-3 | line-3-0283-0322-s003025 | reverse | 3 | pending |
| line-3 | line-3-0369-0347-s005669 | forward | 3 | pending |
| line-3 | line-3-0369-0347-s005669 | reverse | 3 | pending |
| line-3 | line-3-0415-0434-s007969 | forward | 3 | pending |
| line-3 | line-3-0415-0434-s007969 | reverse | 3 | pending |
| line-3 | line-3-0427-0530-s010296 | forward | 3 | pending |
| line-3 | line-3-0427-0530-s010296 | reverse | 3 | pending |
| line-3 | line-3-0492-0723-s014930 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Rwanda/Rubavu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
