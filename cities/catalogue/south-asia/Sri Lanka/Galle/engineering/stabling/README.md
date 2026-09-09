# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **177 trainsets at 20 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0880-1029-s000000 | forward | 4 | pending |
| line-1 | line-1-0746-0737-s006967 | forward | 4 | pending |
| line-1 | line-1-0746-0737-s006967 | reverse | 4 | pending |
| line-1 | line-1-0653-0648-s009968 | forward | 4 | pending |
| line-1 | line-1-0653-0648-s009968 | reverse | 4 | pending |
| line-1 | line-1-0615-0588-s011951 | forward | 4 | pending |
| line-1 | line-1-0615-0588-s011951 | reverse | 4 | pending |
| line-1 | line-1-0550-0551-s013918 | forward | 4 | pending |
| line-1 | line-1-0550-0551-s013918 | reverse | 4 | pending |
| line-1 | line-1-0553-0474-s015988 | forward | 4 | pending |
| line-1 | line-1-0553-0474-s015988 | reverse | 4 | pending |
| line-1 | line-1-0548-0379-s018129 | forward | 4 | pending |
| line-1 | line-1-0548-0379-s018129 | reverse | 4 | pending |
| line-1 | line-1-0492-0302-s020271 | forward | 3 | pending |
| line-1 | line-1-0492-0302-s020271 | reverse | 3 | pending |
| line-1 | line-1-0437-0220-s022407 | reverse | 3 | pending |
| line-2 | line-2-0346-0285-s000000 | forward | 8 | pending |
| line-2 | line-2-0443-0489-s006193 | forward | 8 | pending |
| line-2 | line-2-0443-0489-s006193 | reverse | 8 | pending |
| line-2 | line-2-0550-0551-s009303 | forward | 8 | pending |
| line-2 | line-2-0550-0551-s009303 | reverse | 8 | pending |
| line-2 | line-2-0567-0666-s012223 | forward | 8 | pending |
| line-2 | line-2-0567-0666-s012223 | reverse | 7 | pending |
| line-2 | line-2-0784-1025-s022688 | reverse | 7 | pending |
| line-3 | line-3-0306-1057-s000000 | forward | 6 | pending |
| line-3 | line-3-0431-0674-s010019 | forward | 6 | pending |
| line-3 | line-3-0431-0674-s010019 | reverse | 6 | pending |
| line-3 | line-3-0466-0604-s011931 | forward | 6 | pending |
| line-3 | line-3-0466-0604-s011931 | reverse | 5 | pending |
| line-3 | line-3-0550-0551-s014679 | forward | 5 | pending |
| line-3 | line-3-0550-0551-s014679 | reverse | 5 | pending |
| line-3 | line-3-0592-0495-s016640 | forward | 5 | pending |
| line-3 | line-3-0592-0495-s016640 | reverse | 5 | pending |
| line-3 | line-3-0621-0427-s018590 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Sri Lanka/Galle/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
