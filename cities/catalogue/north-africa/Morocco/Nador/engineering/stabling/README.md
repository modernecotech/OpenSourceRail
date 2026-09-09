# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **72 trainsets at 15 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0328-0422-s000000 | forward | 3 | pending |
| line-1 | line-1-0376-0367-s002017 | forward | 3 | pending |
| line-1 | line-1-0376-0367-s002017 | reverse | 3 | pending |
| line-1 | line-1-0392-0292-s004013 | forward | 3 | pending |
| line-1 | line-1-0392-0292-s004013 | reverse | 3 | pending |
| line-1 | line-1-0431-0209-s005996 | forward | 2 | pending |
| line-1 | line-1-0431-0209-s005996 | reverse | 2 | pending |
| line-1 | line-1-0440-0045-s009996 | reverse | 2 | pending |
| line-2 | line-2-0034-0117-s000000 | forward | 4 | pending |
| line-2 | line-2-0243-0279-s007024 | forward | 4 | pending |
| line-2 | line-2-0243-0279-s007024 | reverse | 3 | pending |
| line-2 | line-2-0327-0360-s010037 | forward | 3 | pending |
| line-2 | line-2-0327-0360-s010037 | reverse | 3 | pending |
| line-2 | line-2-0376-0367-s011599 | forward | 3 | pending |
| line-2 | line-2-0376-0367-s011599 | reverse | 3 | pending |
| line-2 | line-2-0429-0390-s013050 | forward | 3 | pending |
| line-2 | line-2-0429-0390-s013050 | reverse | 3 | pending |
| line-2 | line-2-0479-0445-s015368 | reverse | 3 | pending |
| line-3 | line-3-0619-0416-s000000 | forward | 4 | pending |
| line-3 | line-3-0493-0392-s003016 | forward | 3 | pending |
| line-3 | line-3-0493-0392-s003016 | reverse | 3 | pending |
| line-3 | line-3-0376-0367-s006546 | forward | 3 | pending |
| line-3 | line-3-0376-0367-s006546 | reverse | 3 | pending |
| line-3 | line-3-0313-0282-s008983 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Nador/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
