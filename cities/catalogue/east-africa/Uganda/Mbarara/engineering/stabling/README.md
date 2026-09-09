# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **113 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0522-0784-s000000 | forward | 3 | pending |
| line-1 | line-1-0547-0656-s003018 | forward | 3 | pending |
| line-1 | line-1-0547-0656-s003018 | reverse | 3 | pending |
| line-1 | line-1-0574-0595-s004635 | forward | 3 | pending |
| line-1 | line-1-0574-0595-s004635 | reverse | 3 | pending |
| line-1 | line-1-0549-0555-s006277 | forward | 3 | pending |
| line-1 | line-1-0549-0555-s006277 | reverse | 3 | pending |
| line-1 | line-1-0545-0512-s007644 | forward | 3 | pending |
| line-1 | line-1-0545-0512-s007644 | reverse | 2 | pending |
| line-1 | line-1-0696-0354-s013231 | reverse | 2 | pending |
| line-2 | line-2-0262-0243-s000000 | forward | 4 | pending |
| line-2 | line-2-0456-0427-s007013 | forward | 4 | pending |
| line-2 | line-2-0456-0427-s007013 | reverse | 3 | pending |
| line-2 | line-2-0470-0513-s009087 | forward | 3 | pending |
| line-2 | line-2-0470-0513-s009087 | reverse | 3 | pending |
| line-2 | line-2-0549-0555-s011169 | forward | 3 | pending |
| line-2 | line-2-0549-0555-s011169 | reverse | 3 | pending |
| line-2 | line-2-0611-0608-s013122 | forward | 3 | pending |
| line-2 | line-2-0611-0608-s013122 | reverse | 3 | pending |
| line-2 | line-2-0626-0697-s015059 | reverse | 3 | pending |
| line-3 | line-3-0954-0263-s000000 | forward | 5 | pending |
| line-3 | line-3-0724-0466-s007007 | forward | 5 | pending |
| line-3 | line-3-0724-0466-s007007 | reverse | 5 | pending |
| line-3 | line-3-0613-0549-s010032 | forward | 5 | pending |
| line-3 | line-3-0613-0549-s010032 | reverse | 5 | pending |
| line-3 | line-3-0549-0555-s011849 | forward | 4 | pending |
| line-3 | line-3-0549-0555-s011849 | reverse | 4 | pending |
| line-3 | line-3-0492-0607-s013972 | forward | 4 | pending |
| line-3 | line-3-0492-0607-s013972 | reverse | 4 | pending |
| line-3 | line-3-0427-0681-s016119 | forward | 4 | pending |
| line-3 | line-3-0427-0681-s016119 | reverse | 4 | pending |
| line-3 | line-3-0129-0892-s024662 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Mbarara/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
