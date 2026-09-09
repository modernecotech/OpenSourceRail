# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **156 trainsets at 23 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0076-0559-s000000 | forward | 4 | pending |
| line-1 | line-1-0335-0563-s006987 | forward | 4 | pending |
| line-1 | line-1-0335-0563-s006987 | reverse | 4 | pending |
| line-1 | line-1-0474-0540-s009991 | forward | 4 | pending |
| line-1 | line-1-0474-0540-s009991 | reverse | 4 | pending |
| line-1 | line-1-0535-0546-s011327 | forward | 4 | pending |
| line-1 | line-1-0535-0546-s011327 | reverse | 4 | pending |
| line-1 | line-1-0606-0548-s012996 | forward | 4 | pending |
| line-1 | line-1-0606-0548-s012996 | reverse | 4 | pending |
| line-1 | line-1-0726-0512-s016004 | forward | 3 | pending |
| line-1 | line-1-0726-0512-s016004 | reverse | 3 | pending |
| line-1 | line-1-0880-0438-s020048 | forward | 3 | pending |
| line-1 | line-1-0880-0438-s020048 | reverse | 3 | pending |
| line-1 | line-1-1043-0345-s024079 | reverse | 3 | pending |
| line-2 | line-2-0747-0635-s000000 | forward | 4 | pending |
| line-2 | line-2-0611-0599-s003018 | forward | 4 | pending |
| line-2 | line-2-0611-0599-s003018 | reverse | 4 | pending |
| line-2 | line-2-0535-0546-s006148 | forward | 4 | pending |
| line-2 | line-2-0535-0546-s006148 | reverse | 4 | pending |
| line-2 | line-2-0481-0472-s009040 | forward | 4 | pending |
| line-2 | line-2-0481-0472-s009040 | reverse | 4 | pending |
| line-2 | line-2-0534-0370-s012060 | forward | 4 | pending |
| line-2 | line-2-0534-0370-s012060 | reverse | 4 | pending |
| line-2 | line-2-0376-0240-s017344 | forward | 4 | pending |
| line-2 | line-2-0376-0240-s017344 | reverse | 4 | pending |
| line-2 | line-2-0356-0019-s022637 | reverse | 3 | pending |
| line-3 | line-3-0997-0136-s000000 | forward | 5 | pending |
| line-3 | line-3-0764-0262-s007019 | forward | 5 | pending |
| line-3 | line-3-0764-0262-s007019 | reverse | 4 | pending |
| line-3 | line-3-0637-0360-s010604 | forward | 4 | pending |
| line-3 | line-3-0637-0360-s010604 | reverse | 4 | pending |
| line-3 | line-3-0526-0387-s013615 | forward | 4 | pending |
| line-3 | line-3-0526-0387-s013615 | reverse | 4 | pending |
| line-3 | line-3-0359-0407-s017120 | forward | 4 | pending |
| line-3 | line-3-0359-0407-s017120 | reverse | 4 | pending |
| line-3 | line-3-0223-0491-s020642 | forward | 4 | pending |
| line-3 | line-3-0223-0491-s020642 | reverse | 4 | pending |
| line-3 | line-3-0134-0574-s023660 | forward | 4 | pending |
| line-3 | line-3-0134-0574-s023660 | reverse | 4 | pending |
| line-3 | line-3-0013-0648-s026780 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Damietta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
