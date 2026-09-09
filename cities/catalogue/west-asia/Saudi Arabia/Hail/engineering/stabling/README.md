# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **133 trainsets at 21 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1040-0603-s000000 | forward | 4 | pending |
| line-1 | line-1-0746-0621-s007003 | forward | 4 | pending |
| line-1 | line-1-0746-0621-s007003 | reverse | 4 | pending |
| line-1 | line-1-0647-0590-s010015 | forward | 4 | pending |
| line-1 | line-1-0647-0590-s010015 | reverse | 4 | pending |
| line-1 | line-1-0547-0534-s013041 | forward | 3 | pending |
| line-1 | line-1-0547-0534-s013041 | reverse | 3 | pending |
| line-1 | line-1-0519-0476-s014621 | forward | 3 | pending |
| line-1 | line-1-0519-0476-s014621 | reverse | 3 | pending |
| line-1 | line-1-0410-0422-s017638 | forward | 3 | pending |
| line-1 | line-1-0410-0422-s017638 | reverse | 3 | pending |
| line-1 | line-1-0297-0456-s020179 | forward | 3 | pending |
| line-1 | line-1-0297-0456-s020179 | reverse | 3 | pending |
| line-1 | line-1-0231-0400-s022729 | forward | 3 | pending |
| line-1 | line-1-0231-0400-s022729 | reverse | 3 | pending |
| line-1 | line-1-0155-0354-s025289 | reverse | 3 | pending |
| line-2 | line-2-0832-0082-s000000 | forward | 4 | pending |
| line-2 | line-2-0650-0318-s007025 | forward | 4 | pending |
| line-2 | line-2-0650-0318-s007025 | reverse | 4 | pending |
| line-2 | line-2-0622-0424-s010031 | forward | 4 | pending |
| line-2 | line-2-0622-0424-s010031 | reverse | 4 | pending |
| line-2 | line-2-0596-0512-s013034 | forward | 4 | pending |
| line-2 | line-2-0596-0512-s013034 | reverse | 3 | pending |
| line-2 | line-2-0547-0534-s014317 | forward | 3 | pending |
| line-2 | line-2-0547-0534-s014317 | reverse | 3 | pending |
| line-2 | line-2-0487-0596-s016054 | forward | 3 | pending |
| line-2 | line-2-0487-0596-s016054 | reverse | 3 | pending |
| line-2 | line-2-0430-0695-s019179 | forward | 3 | pending |
| line-2 | line-2-0430-0695-s019179 | reverse | 3 | pending |
| line-2 | line-2-0391-0788-s021900 | reverse | 3 | pending |
| line-3 | line-3-0156-0494-s000000 | forward | 6 | pending |
| line-3 | line-3-0361-0574-s006444 | forward | 6 | pending |
| line-3 | line-3-0361-0574-s006444 | reverse | 5 | pending |
| line-3 | line-3-0475-0661-s009760 | forward | 5 | pending |
| line-3 | line-3-0475-0661-s009760 | reverse | 5 | pending |
| line-3 | line-3-0701-0794-s015926 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Hail/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
