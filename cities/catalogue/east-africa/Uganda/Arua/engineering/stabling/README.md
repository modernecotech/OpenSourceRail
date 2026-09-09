# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **77 trainsets at 16 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0252-0247-s000000 | forward | 3 | pending |
| line-1 | line-1-0327-0342-s003015 | forward | 3 | pending |
| line-1 | line-1-0327-0342-s003015 | reverse | 3 | pending |
| line-1 | line-1-0380-0381-s005022 | forward | 3 | pending |
| line-1 | line-1-0380-0381-s005022 | reverse | 3 | pending |
| line-1 | line-1-0467-0411-s007449 | forward | 2 | pending |
| line-1 | line-1-0467-0411-s007449 | reverse | 2 | pending |
| line-1 | line-1-0550-0499-s009897 | reverse | 2 | pending |
| line-2 | line-2-0405-0744-s000000 | forward | 4 | pending |
| line-2 | line-2-0421-0544-s004738 | forward | 4 | pending |
| line-2 | line-2-0421-0544-s004738 | reverse | 4 | pending |
| line-2 | line-2-0395-0458-s006702 | forward | 4 | pending |
| line-2 | line-2-0395-0458-s006702 | reverse | 4 | pending |
| line-2 | line-2-0380-0381-s008649 | forward | 4 | pending |
| line-2 | line-2-0380-0381-s008649 | reverse | 3 | pending |
| line-2 | line-2-0388-0126-s015010 | reverse | 3 | pending |
| line-3 | line-3-0109-0523-s000000 | forward | 3 | pending |
| line-3 | line-3-0232-0389-s004220 | forward | 3 | pending |
| line-3 | line-3-0232-0389-s004220 | reverse | 3 | pending |
| line-3 | line-3-0316-0402-s006222 | forward | 3 | pending |
| line-3 | line-3-0316-0402-s006222 | reverse | 3 | pending |
| line-3 | line-3-0380-0381-s008214 | forward | 3 | pending |
| line-3 | line-3-0380-0381-s008214 | reverse | 2 | pending |
| line-3 | line-3-0466-0360-s010520 | forward | 2 | pending |
| line-3 | line-3-0466-0360-s010520 | reverse | 2 | pending |
| line-3 | line-3-0549-0386-s012824 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Arua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
