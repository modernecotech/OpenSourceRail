# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **126 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0558-1011-s000000 | forward | 4 | pending |
| line-1 | line-1-0618-0758-s007000 | forward | 4 | pending |
| line-1 | line-1-0618-0758-s007000 | reverse | 4 | pending |
| line-1 | line-1-0576-0638-s010005 | forward | 4 | pending |
| line-1 | line-1-0576-0638-s010005 | reverse | 4 | pending |
| line-1 | line-1-0562-0562-s012256 | forward | 4 | pending |
| line-1 | line-1-0562-0562-s012256 | reverse | 4 | pending |
| line-1 | line-1-0586-0490-s014149 | forward | 4 | pending |
| line-1 | line-1-0586-0490-s014149 | reverse | 4 | pending |
| line-1 | line-1-0536-0441-s016027 | forward | 4 | pending |
| line-1 | line-1-0536-0441-s016027 | reverse | 3 | pending |
| line-1 | line-1-0460-0278-s020919 | reverse | 3 | pending |
| line-2 | line-2-0841-0891-s000000 | forward | 4 | pending |
| line-2 | line-2-0771-0801-s003002 | forward | 4 | pending |
| line-2 | line-2-0771-0801-s003002 | reverse | 4 | pending |
| line-2 | line-2-0740-0671-s006414 | forward | 4 | pending |
| line-2 | line-2-0740-0671-s006414 | reverse | 4 | pending |
| line-2 | line-2-0711-0550-s009419 | forward | 4 | pending |
| line-2 | line-2-0711-0550-s009419 | reverse | 3 | pending |
| line-2 | line-2-0730-0490-s011041 | forward | 3 | pending |
| line-2 | line-2-0730-0490-s011041 | reverse | 3 | pending |
| line-2 | line-2-0696-0375-s014066 | forward | 3 | pending |
| line-2 | line-2-0696-0375-s014066 | reverse | 3 | pending |
| line-2 | line-2-0604-0297-s017075 | forward | 3 | pending |
| line-2 | line-2-0604-0297-s017075 | reverse | 3 | pending |
| line-2 | line-2-0558-0087-s023346 | reverse | 3 | pending |
| line-3 | line-3-0476-1027-s000000 | forward | 4 | pending |
| line-3 | line-3-0466-0862-s003499 | forward | 4 | pending |
| line-3 | line-3-0466-0862-s003499 | reverse | 4 | pending |
| line-3 | line-3-0481-0718-s007017 | forward | 4 | pending |
| line-3 | line-3-0481-0718-s007017 | reverse | 4 | pending |
| line-3 | line-3-0406-0611-s010123 | forward | 4 | pending |
| line-3 | line-3-0406-0611-s010123 | reverse | 4 | pending |
| line-3 | line-3-0374-0402-s014819 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Abha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
