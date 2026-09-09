# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **57 trainsets at 13 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0530-0342-s000000 | forward | 3 | pending |
| line-1 | line-1-0449-0371-s002061 | forward | 3 | pending |
| line-1 | line-1-0449-0371-s002061 | reverse | 3 | pending |
| line-1 | line-1-0374-0375-s004109 | forward | 2 | pending |
| line-1 | line-1-0374-0375-s004109 | reverse | 2 | pending |
| line-1 | line-1-0365-0303-s006173 | forward | 2 | pending |
| line-1 | line-1-0365-0303-s006173 | reverse | 2 | pending |
| line-1 | line-1-0318-0258-s008245 | reverse | 2 | pending |
| line-2 | line-2-0644-0475-s000000 | forward | 4 | pending |
| line-2 | line-2-0408-0437-s005715 | forward | 4 | pending |
| line-2 | line-2-0408-0437-s005715 | reverse | 3 | pending |
| line-2 | line-2-0374-0375-s007350 | forward | 3 | pending |
| line-2 | line-2-0374-0375-s007350 | reverse | 3 | pending |
| line-2 | line-2-0278-0389-s009874 | forward | 3 | pending |
| line-2 | line-2-0278-0389-s009874 | reverse | 3 | pending |
| line-2 | line-2-0210-0463-s012395 | reverse | 3 | pending |
| line-3 | line-3-0330-0343-s000000 | forward | 3 | pending |
| line-3 | line-3-0374-0375-s001415 | forward | 3 | pending |
| line-3 | line-3-0374-0375-s001415 | reverse | 3 | pending |
| line-3 | line-3-0454-0260-s004710 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Garissa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
