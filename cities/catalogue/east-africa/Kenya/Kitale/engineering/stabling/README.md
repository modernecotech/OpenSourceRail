# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **84 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0406-0246-s000000 | forward | 5 | pending |
| line-1 | line-1-0376-0373-s003096 | forward | 5 | pending |
| line-1 | line-1-0376-0373-s003096 | reverse | 5 | pending |
| line-1 | line-1-0464-0386-s005190 | forward | 5 | pending |
| line-1 | line-1-0464-0386-s005190 | reverse | 5 | pending |
| line-1 | line-1-0729-0702-s014641 | reverse | 5 | pending |
| line-2 | line-2-0608-0115-s000000 | forward | 4 | pending |
| line-2 | line-2-0490-0327-s005475 | forward | 4 | pending |
| line-2 | line-2-0490-0327-s005475 | reverse | 4 | pending |
| line-2 | line-2-0376-0373-s008216 | forward | 4 | pending |
| line-2 | line-2-0376-0373-s008216 | reverse | 4 | pending |
| line-2 | line-2-0316-0470-s011064 | forward | 3 | pending |
| line-2 | line-2-0316-0470-s011064 | reverse | 3 | pending |
| line-2 | line-2-0216-0565-s013915 | reverse | 3 | pending |
| line-3 | line-3-0529-0442-s000000 | forward | 4 | pending |
| line-3 | line-3-0408-0415-s003022 | forward | 3 | pending |
| line-3 | line-3-0408-0415-s003022 | reverse | 3 | pending |
| line-3 | line-3-0376-0373-s004284 | forward | 3 | pending |
| line-3 | line-3-0376-0373-s004284 | reverse | 3 | pending |
| line-3 | line-3-0231-0325-s007801 | forward | 3 | pending |
| line-3 | line-3-0231-0325-s007801 | reverse | 3 | pending |
| line-3 | line-3-0068-0325-s011314 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kitale/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
