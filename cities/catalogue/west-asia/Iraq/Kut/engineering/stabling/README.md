# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **101 trainsets at 16 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0432-0235-s000000 | forward | 5 | pending |
| line-1 | line-1-0484-0323-s002226 | forward | 5 | pending |
| line-1 | line-1-0484-0323-s002226 | reverse | 5 | pending |
| line-1 | line-1-0563-0402-s004460 | forward | 5 | pending |
| line-1 | line-1-0563-0402-s004460 | reverse | 5 | pending |
| line-1 | line-1-0559-0540-s007746 | forward | 5 | pending |
| line-1 | line-1-0559-0540-s007746 | reverse | 5 | pending |
| line-1 | line-1-0643-0608-s010494 | forward | 5 | pending |
| line-1 | line-1-0643-0608-s010494 | reverse | 4 | pending |
| line-1 | line-1-1038-0979-s022368 | reverse | 4 | pending |
| line-2 | line-2-0399-0481-s000000 | forward | 3 | pending |
| line-2 | line-2-0476-0540-s002029 | forward | 3 | pending |
| line-2 | line-2-0476-0540-s002029 | reverse | 3 | pending |
| line-2 | line-2-0559-0540-s004070 | forward | 3 | pending |
| line-2 | line-2-0559-0540-s004070 | reverse | 3 | pending |
| line-2 | line-2-0629-0472-s006033 | forward | 3 | pending |
| line-2 | line-2-0629-0472-s006033 | reverse | 3 | pending |
| line-2 | line-2-0742-0465-s009399 | reverse | 2 | pending |
| line-3 | line-3-0717-0891-s000000 | forward | 4 | pending |
| line-3 | line-3-0549-0663-s006860 | forward | 4 | pending |
| line-3 | line-3-0549-0663-s006860 | reverse | 4 | pending |
| line-3 | line-3-0559-0540-s009668 | forward | 4 | pending |
| line-3 | line-3-0559-0540-s009668 | reverse | 4 | pending |
| line-3 | line-3-0491-0463-s012158 | forward | 4 | pending |
| line-3 | line-3-0491-0463-s012158 | reverse | 3 | pending |
| line-3 | line-3-0403-0375-s014647 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Kut/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
