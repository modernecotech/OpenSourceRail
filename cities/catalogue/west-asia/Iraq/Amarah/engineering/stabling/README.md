# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **101 trainsets at 17 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0313-0285-s000000 | forward | 4 | pending |
| line-1 | line-1-0415-0371-s003008 | forward | 4 | pending |
| line-1 | line-1-0415-0371-s003008 | reverse | 4 | pending |
| line-1 | line-1-0499-0487-s006024 | forward | 4 | pending |
| line-1 | line-1-0499-0487-s006024 | reverse | 4 | pending |
| line-1 | line-1-0584-0534-s008187 | forward | 4 | pending |
| line-1 | line-1-0584-0534-s008187 | reverse | 4 | pending |
| line-1 | line-1-0665-0508-s010112 | forward | 4 | pending |
| line-1 | line-1-0665-0508-s010112 | reverse | 4 | pending |
| line-1 | line-1-0734-0557-s012026 | forward | 4 | pending |
| line-1 | line-1-0734-0557-s012026 | reverse | 4 | pending |
| line-1 | line-1-1131-0749-s021569 | reverse | 3 | pending |
| line-2 | line-2-0709-0317-s000000 | forward | 3 | pending |
| line-2 | line-2-0678-0455-s003017 | forward | 3 | pending |
| line-2 | line-2-0678-0455-s003017 | reverse | 3 | pending |
| line-2 | line-2-0584-0534-s006602 | forward | 3 | pending |
| line-2 | line-2-0584-0534-s006602 | reverse | 3 | pending |
| line-2 | line-2-0475-0544-s009031 | forward | 3 | pending |
| line-2 | line-2-0475-0544-s009031 | reverse | 3 | pending |
| line-2 | line-2-0410-0512-s011023 | forward | 3 | pending |
| line-2 | line-2-0410-0512-s011023 | reverse | 2 | pending |
| line-2 | line-2-0329-0543-s013016 | reverse | 2 | pending |
| line-3 | line-3-0667-0658-s000000 | forward | 5 | pending |
| line-3 | line-3-0584-0534-s003530 | forward | 5 | pending |
| line-3 | line-3-0584-0534-s003530 | reverse | 4 | pending |
| line-3 | line-3-0522-0453-s006039 | forward | 4 | pending |
| line-3 | line-3-0522-0453-s006039 | reverse | 4 | pending |
| line-3 | line-3-0539-0186-s012012 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Amarah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
