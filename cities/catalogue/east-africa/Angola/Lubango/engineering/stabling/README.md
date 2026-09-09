# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **119 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0445-0353-s000000 | forward | 3 | pending |
| line-1 | line-1-0460-0463-s003013 | forward | 3 | pending |
| line-1 | line-1-0460-0463-s003013 | reverse | 3 | pending |
| line-1 | line-1-0545-0560-s006308 | forward | 3 | pending |
| line-1 | line-1-0545-0560-s006308 | reverse | 3 | pending |
| line-1 | line-1-0612-0623-s008849 | forward | 3 | pending |
| line-1 | line-1-0612-0623-s008849 | reverse | 3 | pending |
| line-1 | line-1-0592-0728-s011164 | forward | 3 | pending |
| line-1 | line-1-0592-0728-s011164 | reverse | 3 | pending |
| line-1 | line-1-0593-0842-s013502 | forward | 3 | pending |
| line-1 | line-1-0593-0842-s013502 | reverse | 3 | pending |
| line-1 | line-1-0647-0895-s015818 | reverse | 3 | pending |
| line-2 | line-2-0818-0385-s000000 | forward | 4 | pending |
| line-2 | line-2-0713-0491-s003267 | forward | 4 | pending |
| line-2 | line-2-0713-0491-s003267 | reverse | 4 | pending |
| line-2 | line-2-0623-0464-s006292 | forward | 4 | pending |
| line-2 | line-2-0623-0464-s006292 | reverse | 4 | pending |
| line-2 | line-2-0581-0543-s008757 | forward | 4 | pending |
| line-2 | line-2-0581-0543-s008757 | reverse | 4 | pending |
| line-2 | line-2-0545-0560-s010016 | forward | 4 | pending |
| line-2 | line-2-0545-0560-s010016 | reverse | 4 | pending |
| line-2 | line-2-0486-0597-s011764 | forward | 4 | pending |
| line-2 | line-2-0486-0597-s011764 | reverse | 3 | pending |
| line-2 | line-2-0396-0679-s014764 | forward | 3 | pending |
| line-2 | line-2-0396-0679-s014764 | reverse | 3 | pending |
| line-2 | line-2-0145-0992-s024048 | reverse | 3 | pending |
| line-3 | line-3-0533-0317-s000000 | forward | 4 | pending |
| line-3 | line-3-0574-0441-s003009 | forward | 3 | pending |
| line-3 | line-3-0574-0441-s003009 | reverse | 3 | pending |
| line-3 | line-3-0545-0560-s005830 | forward | 3 | pending |
| line-3 | line-3-0545-0560-s005830 | reverse | 3 | pending |
| line-3 | line-3-0633-0604-s008528 | forward | 3 | pending |
| line-3 | line-3-0633-0604-s008528 | reverse | 3 | pending |
| line-3 | line-3-0654-0714-s011212 | forward | 3 | pending |
| line-3 | line-3-0654-0714-s011212 | reverse | 3 | pending |
| line-3 | line-3-0725-0794-s013896 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Lubango/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
