# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **63 trainsets at 14 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0319-0148-s000000 | forward | 3 | pending |
| line-1 | line-1-0325-0276-s003004 | forward | 3 | pending |
| line-1 | line-1-0325-0276-s003004 | reverse | 3 | pending |
| line-1 | line-1-0381-0373-s005441 | forward | 3 | pending |
| line-1 | line-1-0381-0373-s005441 | reverse | 2 | pending |
| line-1 | line-1-0459-0399-s007406 | forward | 2 | pending |
| line-1 | line-1-0459-0399-s007406 | reverse | 2 | pending |
| line-1 | line-1-0531-0372-s009357 | reverse | 2 | pending |
| line-2 | line-2-0593-0351-s000000 | forward | 3 | pending |
| line-2 | line-2-0481-0364-s003016 | forward | 3 | pending |
| line-2 | line-2-0481-0364-s003016 | reverse | 3 | pending |
| line-2 | line-2-0381-0373-s005090 | forward | 3 | pending |
| line-2 | line-2-0381-0373-s005090 | reverse | 3 | pending |
| line-2 | line-2-0474-0480-s008544 | reverse | 3 | pending |
| line-3 | line-3-0340-0286-s000000 | forward | 4 | pending |
| line-3 | line-3-0381-0373-s002233 | forward | 3 | pending |
| line-3 | line-3-0381-0373-s002233 | reverse | 3 | pending |
| line-3 | line-3-0455-0427-s004195 | forward | 3 | pending |
| line-3 | line-3-0455-0427-s004195 | reverse | 3 | pending |
| line-3 | line-3-0542-0405-s006167 | forward | 3 | pending |
| line-3 | line-3-0542-0405-s006167 | reverse | 3 | pending |
| line-3 | line-3-0744-0445-s011517 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Soyo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
