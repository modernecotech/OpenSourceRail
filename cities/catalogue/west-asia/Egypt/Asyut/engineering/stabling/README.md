# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **162 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0660-0667-s000000 | forward | 5 | pending |
| line-1 | line-1-0606-0623-s001974 | forward | 5 | pending |
| line-1 | line-1-0606-0623-s001974 | reverse | 4 | pending |
| line-1 | line-1-0539-0559-s003931 | forward | 4 | pending |
| line-1 | line-1-0539-0559-s003931 | reverse | 4 | pending |
| line-1 | line-1-0415-0467-s007643 | reverse | 4 | pending |
| line-2 | line-2-0565-0462-s000000 | forward | 8 | pending |
| line-2 | line-2-0539-0559-s002524 | forward | 8 | pending |
| line-2 | line-2-0539-0559-s002524 | reverse | 8 | pending |
| line-2 | line-2-0451-0605-s004952 | forward | 8 | pending |
| line-2 | line-2-0451-0605-s004952 | reverse | 8 | pending |
| line-2 | line-2-0458-0734-s008451 | forward | 8 | pending |
| line-2 | line-2-0458-0734-s008451 | reverse | 7 | pending |
| line-2 | line-2-0070-1066-s019747 | reverse | 7 | pending |
| line-3 | line-3-1023-1006-s000000 | forward | 8 | pending |
| line-3 | line-3-0623-0679-s012022 | forward | 8 | pending |
| line-3 | line-3-0623-0679-s012022 | reverse | 8 | pending |
| line-3 | line-3-0556-0621-s013918 | forward | 8 | pending |
| line-3 | line-3-0556-0621-s013918 | reverse | 7 | pending |
| line-3 | line-3-0539-0559-s015806 | forward | 7 | pending |
| line-3 | line-3-0539-0559-s015806 | reverse | 7 | pending |
| line-3 | line-3-0533-0470-s018058 | forward | 7 | pending |
| line-3 | line-3-0533-0470-s018058 | reverse | 7 | pending |
| line-3 | line-3-0480-0214-s024352 | reverse | 7 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Asyut/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
