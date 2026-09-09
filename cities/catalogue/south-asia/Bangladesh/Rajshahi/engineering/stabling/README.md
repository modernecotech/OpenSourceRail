# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **93 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0585-0779-s000000 | forward | 5 | pending |
| line-1 | line-1-0545-0671-s003019 | forward | 5 | pending |
| line-1 | line-1-0545-0671-s003019 | reverse | 5 | pending |
| line-1 | line-1-0550-0553-s005482 | forward | 5 | pending |
| line-1 | line-1-0550-0553-s005482 | reverse | 5 | pending |
| line-1 | line-1-0529-0397-s009065 | forward | 5 | pending |
| line-1 | line-1-0529-0397-s009065 | reverse | 4 | pending |
| line-1 | line-1-0540-0014-s017955 | reverse | 4 | pending |
| line-2 | line-2-0616-0676-s000000 | forward | 3 | pending |
| line-2 | line-2-0579-0588-s003006 | forward | 3 | pending |
| line-2 | line-2-0579-0588-s003006 | reverse | 3 | pending |
| line-2 | line-2-0550-0553-s004252 | forward | 3 | pending |
| line-2 | line-2-0550-0553-s004252 | reverse | 2 | pending |
| line-2 | line-2-0490-0568-s006010 | forward | 2 | pending |
| line-2 | line-2-0490-0568-s006010 | reverse | 2 | pending |
| line-2 | line-2-0454-0620-s008178 | forward | 2 | pending |
| line-2 | line-2-0454-0620-s008178 | reverse | 2 | pending |
| line-2 | line-2-0372-0609-s010334 | reverse | 2 | pending |
| line-3 | line-3-0185-0604-s000000 | forward | 4 | pending |
| line-3 | line-3-0361-0575-s004856 | forward | 3 | pending |
| line-3 | line-3-0361-0575-s004856 | reverse | 3 | pending |
| line-3 | line-3-0480-0563-s007879 | forward | 3 | pending |
| line-3 | line-3-0480-0563-s007879 | reverse | 3 | pending |
| line-3 | line-3-0550-0553-s009770 | forward | 3 | pending |
| line-3 | line-3-0550-0553-s009770 | reverse | 3 | pending |
| line-3 | line-3-0567-0472-s011934 | forward | 3 | pending |
| line-3 | line-3-0567-0472-s011934 | reverse | 3 | pending |
| line-3 | line-3-0577-0391-s014089 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Rajshahi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
