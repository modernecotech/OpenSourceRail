# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **105 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0529-0080-s000000 | forward | 4 | pending |
| line-1 | line-1-0524-0338-s005648 | forward | 4 | pending |
| line-1 | line-1-0524-0338-s005648 | reverse | 4 | pending |
| line-1 | line-1-0525-0460-s008665 | forward | 4 | pending |
| line-1 | line-1-0525-0460-s008665 | reverse | 4 | pending |
| line-1 | line-1-0549-0550-s010942 | forward | 3 | pending |
| line-1 | line-1-0549-0550-s010942 | reverse | 3 | pending |
| line-1 | line-1-0568-0607-s013452 | forward | 3 | pending |
| line-1 | line-1-0568-0607-s013452 | reverse | 3 | pending |
| line-1 | line-1-0571-0716-s015956 | reverse | 3 | pending |
| line-2 | line-2-0628-0393-s000000 | forward | 4 | pending |
| line-2 | line-2-0589-0478-s002105 | forward | 4 | pending |
| line-2 | line-2-0589-0478-s002105 | reverse | 4 | pending |
| line-2 | line-2-0549-0550-s004203 | forward | 4 | pending |
| line-2 | line-2-0549-0550-s004203 | reverse | 4 | pending |
| line-2 | line-2-0455-0604-s007622 | forward | 4 | pending |
| line-2 | line-2-0455-0604-s007622 | reverse | 3 | pending |
| line-2 | line-2-0294-0806-s014449 | reverse | 3 | pending |
| line-3 | line-3-0591-1029-s000000 | forward | 4 | pending |
| line-3 | line-3-0601-0731-s007015 | forward | 4 | pending |
| line-3 | line-3-0601-0731-s007015 | reverse | 4 | pending |
| line-3 | line-3-0531-0650-s010035 | forward | 4 | pending |
| line-3 | line-3-0531-0650-s010035 | reverse | 4 | pending |
| line-3 | line-3-0549-0550-s013202 | forward | 4 | pending |
| line-3 | line-3-0549-0550-s013202 | reverse | 4 | pending |
| line-3 | line-3-0491-0458-s015643 | forward | 4 | pending |
| line-3 | line-3-0491-0458-s015643 | reverse | 4 | pending |
| line-3 | line-3-0480-0367-s018333 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Raqqa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
