# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **139 trainsets at 14 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0724-0363-s000000 | forward | 5 | pending |
| line-1 | line-1-0610-0471-s003666 | forward | 5 | pending |
| line-1 | line-1-0610-0471-s003666 | reverse | 5 | pending |
| line-1 | line-1-0550-0553-s006122 | forward | 5 | pending |
| line-1 | line-1-0550-0553-s006122 | reverse | 4 | pending |
| line-1 | line-1-0495-0609-s008598 | forward | 4 | pending |
| line-1 | line-1-0495-0609-s008598 | reverse | 4 | pending |
| line-1 | line-1-0429-0827-s014944 | reverse | 4 | pending |
| line-2 | line-2-1012-0957-s000000 | forward | 9 | pending |
| line-2 | line-2-0665-0583-s012432 | forward | 8 | pending |
| line-2 | line-2-0665-0583-s012432 | reverse | 8 | pending |
| line-2 | line-2-0550-0553-s016052 | forward | 8 | pending |
| line-2 | line-2-0550-0553-s016052 | reverse | 8 | pending |
| line-2 | line-2-0510-0484-s018168 | forward | 8 | pending |
| line-2 | line-2-0510-0484-s018168 | reverse | 8 | pending |
| line-2 | line-2-0122-0216-s028691 | reverse | 8 | pending |
| line-3 | line-3-0550-0083-s000000 | forward | 7 | pending |
| line-3 | line-3-0500-0368-s007009 | forward | 7 | pending |
| line-3 | line-3-0500-0368-s007009 | reverse | 6 | pending |
| line-3 | line-3-0429-0492-s010094 | forward | 6 | pending |
| line-3 | line-3-0429-0492-s010094 | reverse | 6 | pending |
| line-3 | line-3-0320-0751-s016424 | reverse | 6 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Gulu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
