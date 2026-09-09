# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **117 trainsets at 15 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0316-0690-s000000 | forward | 4 | pending |
| line-1 | line-1-0446-0629-s004094 | forward | 3 | pending |
| line-1 | line-1-0446-0629-s004094 | reverse | 3 | pending |
| line-1 | line-1-0506-0601-s005695 | forward | 3 | pending |
| line-1 | line-1-0506-0601-s005695 | reverse | 3 | pending |
| line-1 | line-1-0546-0554-s007444 | forward | 3 | pending |
| line-1 | line-1-0546-0554-s007444 | reverse | 3 | pending |
| line-1 | line-1-0536-0502-s008705 | forward | 3 | pending |
| line-1 | line-1-0536-0502-s008705 | reverse | 3 | pending |
| line-1 | line-1-0602-0332-s012851 | reverse | 3 | pending |
| line-2 | line-2-0473-0257-s000000 | forward | 7 | pending |
| line-2 | line-2-0464-0442-s005032 | forward | 6 | pending |
| line-2 | line-2-0464-0442-s005032 | reverse | 6 | pending |
| line-2 | line-2-0546-0554-s008569 | forward | 6 | pending |
| line-2 | line-2-0546-0554-s008569 | reverse | 6 | pending |
| line-2 | line-2-0729-0759-s015056 | forward | 6 | pending |
| line-2 | line-2-0729-0759-s015056 | reverse | 6 | pending |
| line-2 | line-2-0949-0887-s020575 | reverse | 6 | pending |
| line-3 | line-3-0527-0507-s000000 | forward | 7 | pending |
| line-3 | line-3-0477-0553-s003007 | forward | 6 | pending |
| line-3 | line-3-0477-0553-s003007 | reverse | 6 | pending |
| line-3 | line-3-0293-0655-s008838 | forward | 6 | pending |
| line-3 | line-3-0293-0655-s008838 | reverse | 6 | pending |
| line-3 | line-3-0014-0682-s015832 | reverse | 6 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Qena/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
