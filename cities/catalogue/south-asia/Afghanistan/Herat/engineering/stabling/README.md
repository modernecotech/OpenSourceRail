# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **108 trainsets at 17 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0423-0728-s000000 | forward | 4 | pending |
| line-1 | line-1-0466-0621-s003016 | forward | 3 | pending |
| line-1 | line-1-0466-0621-s003016 | reverse | 3 | pending |
| line-1 | line-1-0557-0586-s006029 | forward | 3 | pending |
| line-1 | line-1-0557-0586-s006029 | reverse | 3 | pending |
| line-1 | line-1-0601-0528-s009033 | forward | 3 | pending |
| line-1 | line-1-0601-0528-s009033 | reverse | 3 | pending |
| line-1 | line-1-0655-0505-s011487 | forward | 3 | pending |
| line-1 | line-1-0655-0505-s011487 | reverse | 3 | pending |
| line-1 | line-1-0707-0431-s013954 | reverse | 3 | pending |
| line-2 | line-2-0699-0615-s000000 | forward | 4 | pending |
| line-2 | line-2-0574-0595-s003007 | forward | 3 | pending |
| line-2 | line-2-0574-0595-s003007 | reverse | 3 | pending |
| line-2 | line-2-0550-0550-s004289 | forward | 3 | pending |
| line-2 | line-2-0550-0550-s004289 | reverse | 3 | pending |
| line-2 | line-2-0573-0521-s006015 | forward | 3 | pending |
| line-2 | line-2-0573-0521-s006015 | reverse | 3 | pending |
| line-2 | line-2-0476-0467-s009019 | forward | 3 | pending |
| line-2 | line-2-0476-0467-s009019 | reverse | 3 | pending |
| line-2 | line-2-0406-0262-s014286 | reverse | 3 | pending |
| line-3 | line-3-0289-0190-s000000 | forward | 6 | pending |
| line-3 | line-3-0401-0444-s007018 | forward | 6 | pending |
| line-3 | line-3-0401-0444-s007018 | reverse | 6 | pending |
| line-3 | line-3-0424-0582-s010019 | forward | 6 | pending |
| line-3 | line-3-0424-0582-s010019 | reverse | 6 | pending |
| line-3 | line-3-0401-0713-s012829 | forward | 6 | pending |
| line-3 | line-3-0401-0713-s012829 | reverse | 5 | pending |
| line-3 | line-3-0486-1078-s021292 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Herat/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
