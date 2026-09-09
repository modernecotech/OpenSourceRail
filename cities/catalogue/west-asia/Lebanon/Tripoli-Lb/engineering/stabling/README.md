# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **99 trainsets at 20 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0437-0368-s000000 | forward | 3 | pending |
| line-1 | line-1-0506-0476-s003018 | forward | 3 | pending |
| line-1 | line-1-0506-0476-s003018 | reverse | 3 | pending |
| line-1 | line-1-0556-0550-s005091 | forward | 3 | pending |
| line-1 | line-1-0556-0550-s005091 | reverse | 3 | pending |
| line-1 | line-1-0605-0651-s007583 | forward | 3 | pending |
| line-1 | line-1-0605-0651-s007583 | reverse | 3 | pending |
| line-1 | line-1-0706-0705-s010074 | forward | 2 | pending |
| line-1 | line-1-0706-0705-s010074 | reverse | 2 | pending |
| line-1 | line-1-0793-0767-s012575 | reverse | 2 | pending |
| line-2 | line-2-0296-0968-s000000 | forward | 3 | pending |
| line-2 | line-2-0388-0832-s003515 | forward | 3 | pending |
| line-2 | line-2-0388-0832-s003515 | reverse | 3 | pending |
| line-2 | line-2-0439-0678-s007018 | forward | 3 | pending |
| line-2 | line-2-0439-0678-s007018 | reverse | 3 | pending |
| line-2 | line-2-0481-0592-s009086 | forward | 3 | pending |
| line-2 | line-2-0481-0592-s009086 | reverse | 3 | pending |
| line-2 | line-2-0556-0550-s011177 | forward | 3 | pending |
| line-2 | line-2-0556-0550-s011177 | reverse | 3 | pending |
| line-2 | line-2-0632-0547-s013033 | forward | 3 | pending |
| line-2 | line-2-0632-0547-s013033 | reverse | 3 | pending |
| line-2 | line-2-0750-0503-s015935 | forward | 3 | pending |
| line-2 | line-2-0750-0503-s015935 | reverse | 3 | pending |
| line-2 | line-2-0805-0404-s018834 | reverse | 2 | pending |
| line-3 | line-3-0575-0388-s000000 | forward | 4 | pending |
| line-3 | line-3-0555-0469-s002305 | forward | 3 | pending |
| line-3 | line-3-0555-0469-s002305 | reverse | 3 | pending |
| line-3 | line-3-0556-0550-s004198 | forward | 3 | pending |
| line-3 | line-3-0556-0550-s004198 | reverse | 3 | pending |
| line-3 | line-3-0634-0604-s006274 | forward | 3 | pending |
| line-3 | line-3-0634-0604-s006274 | reverse | 3 | pending |
| line-3 | line-3-0706-0669-s008334 | forward | 3 | pending |
| line-3 | line-3-0706-0669-s008334 | reverse | 3 | pending |
| line-3 | line-3-0927-0774-s014203 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Lebanon/Tripoli-Lb/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
