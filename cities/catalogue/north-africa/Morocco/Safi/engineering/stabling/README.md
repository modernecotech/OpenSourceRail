# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **86 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0929-1021-s000000 | forward | 4 | pending |
| line-1 | line-1-0653-0671-s010014 | forward | 4 | pending |
| line-1 | line-1-0653-0671-s010014 | reverse | 4 | pending |
| line-1 | line-1-0578-0612-s013038 | forward | 4 | pending |
| line-1 | line-1-0578-0612-s013038 | reverse | 4 | pending |
| line-1 | line-1-0553-0553-s014466 | forward | 4 | pending |
| line-1 | line-1-0553-0553-s014466 | reverse | 4 | pending |
| line-1 | line-1-0519-0519-s016045 | forward | 3 | pending |
| line-1 | line-1-0519-0519-s016045 | reverse | 3 | pending |
| line-1 | line-1-0443-0496-s017916 | forward | 3 | pending |
| line-1 | line-1-0443-0496-s017916 | reverse | 3 | pending |
| line-1 | line-1-0400-0426-s019811 | reverse | 3 | pending |
| line-2 | line-2-0398-0611-s000000 | forward | 3 | pending |
| line-2 | line-2-0490-0576-s002191 | forward | 3 | pending |
| line-2 | line-2-0490-0576-s002191 | reverse | 3 | pending |
| line-2 | line-2-0553-0553-s004099 | forward | 3 | pending |
| line-2 | line-2-0553-0553-s004099 | reverse | 3 | pending |
| line-2 | line-2-0639-0513-s006831 | forward | 3 | pending |
| line-2 | line-2-0639-0513-s006831 | reverse | 3 | pending |
| line-2 | line-2-0760-0495-s010364 | reverse | 2 | pending |
| line-3 | line-3-0543-0652-s000000 | forward | 3 | pending |
| line-3 | line-3-0553-0553-s002186 | forward | 3 | pending |
| line-3 | line-3-0553-0553-s002186 | reverse | 3 | pending |
| line-3 | line-3-0654-0562-s004474 | forward | 3 | pending |
| line-3 | line-3-0654-0562-s004474 | reverse | 2 | pending |
| line-3 | line-3-0754-0544-s006779 | forward | 2 | pending |
| line-3 | line-3-0754-0544-s006779 | reverse | 2 | pending |
| line-3 | line-3-0835-0476-s009080 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Safi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
