# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **66 trainsets at 13 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0164-0517-s000000 | forward | 3 | pending |
| line-1 | line-1-0318-0426-s004410 | forward | 3 | pending |
| line-1 | line-1-0318-0426-s004410 | reverse | 3 | pending |
| line-1 | line-1-0373-0374-s006126 | forward | 3 | pending |
| line-1 | line-1-0373-0374-s006126 | reverse | 2 | pending |
| line-1 | line-1-0411-0321-s007771 | forward | 2 | pending |
| line-1 | line-1-0411-0321-s007771 | reverse | 2 | pending |
| line-1 | line-1-0466-0286-s009394 | reverse | 2 | pending |
| line-2 | line-2-0383-0281-s000000 | forward | 5 | pending |
| line-2 | line-2-0373-0374-s002356 | forward | 5 | pending |
| line-2 | line-2-0373-0374-s002356 | reverse | 4 | pending |
| line-2 | line-2-0269-0351-s004707 | forward | 4 | pending |
| line-2 | line-2-0269-0351-s004707 | reverse | 4 | pending |
| line-2 | line-2-0027-0511-s011741 | reverse | 4 | pending |
| line-3 | line-3-0421-0361-s000000 | forward | 4 | pending |
| line-3 | line-3-0373-0374-s001271 | forward | 4 | pending |
| line-3 | line-3-0373-0374-s001271 | reverse | 3 | pending |
| line-3 | line-3-0296-0391-s003003 | forward | 3 | pending |
| line-3 | line-3-0296-0391-s003003 | reverse | 3 | pending |
| line-3 | line-3-0045-0480-s009080 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Beni-Mellal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
