# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **59 trainsets at 14 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0584-0390-s000000 | forward | 3 | pending |
| line-1 | line-1-0468-0406-s003012 | forward | 3 | pending |
| line-1 | line-1-0468-0406-s003012 | reverse | 3 | pending |
| line-1 | line-1-0383-0377-s004992 | forward | 3 | pending |
| line-1 | line-1-0383-0377-s004992 | reverse | 3 | pending |
| line-1 | line-1-0298-0414-s007690 | forward | 2 | pending |
| line-1 | line-1-0298-0414-s007690 | reverse | 2 | pending |
| line-1 | line-1-0181-0377-s010370 | reverse | 2 | pending |
| line-2 | line-2-0280-0408-s000000 | forward | 3 | pending |
| line-2 | line-2-0383-0377-s003485 | forward | 3 | pending |
| line-2 | line-2-0383-0377-s003485 | reverse | 3 | pending |
| line-2 | line-2-0482-0364-s006028 | forward | 3 | pending |
| line-2 | line-2-0482-0364-s006028 | reverse | 3 | pending |
| line-2 | line-2-0581-0385-s008222 | reverse | 2 | pending |
| line-3 | line-3-0693-0552-s000000 | forward | 3 | pending |
| line-3 | line-3-0591-0446-s003242 | forward | 3 | pending |
| line-3 | line-3-0591-0446-s003242 | reverse | 3 | pending |
| line-3 | line-3-0462-0431-s006256 | forward | 3 | pending |
| line-3 | line-3-0462-0431-s006256 | reverse | 3 | pending |
| line-3 | line-3-0383-0377-s008530 | forward | 2 | pending |
| line-3 | line-3-0383-0377-s008530 | reverse | 2 | pending |
| line-3 | line-3-0336-0362-s010338 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Lahij/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
