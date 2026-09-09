# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **109 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0479-0844-s000000 | forward | 3 | pending |
| line-1 | line-1-0548-0731-s003003 | forward | 3 | pending |
| line-1 | line-1-0548-0731-s003003 | reverse | 3 | pending |
| line-1 | line-1-0582-0615-s006020 | forward | 3 | pending |
| line-1 | line-1-0582-0615-s006020 | reverse | 3 | pending |
| line-1 | line-1-0551-0552-s007713 | forward | 3 | pending |
| line-1 | line-1-0551-0552-s007713 | reverse | 3 | pending |
| line-1 | line-1-0485-0509-s009876 | forward | 2 | pending |
| line-1 | line-1-0485-0509-s009876 | reverse | 2 | pending |
| line-1 | line-1-0431-0448-s012039 | forward | 2 | pending |
| line-1 | line-1-0431-0448-s012039 | reverse | 2 | pending |
| line-1 | line-1-0393-0371-s014212 | reverse | 2 | pending |
| line-2 | line-2-1084-0152-s000000 | forward | 5 | pending |
| line-2 | line-2-0716-0478-s011431 | forward | 5 | pending |
| line-2 | line-2-0716-0478-s011431 | reverse | 5 | pending |
| line-2 | line-2-0597-0518-s014439 | forward | 5 | pending |
| line-2 | line-2-0597-0518-s014439 | reverse | 4 | pending |
| line-2 | line-2-0551-0552-s016256 | forward | 4 | pending |
| line-2 | line-2-0551-0552-s016256 | reverse | 4 | pending |
| line-2 | line-2-0497-0607-s018215 | forward | 4 | pending |
| line-2 | line-2-0497-0607-s018215 | reverse | 4 | pending |
| line-2 | line-2-0406-0600-s020192 | forward | 4 | pending |
| line-2 | line-2-0406-0600-s020192 | reverse | 4 | pending |
| line-2 | line-2-0274-0567-s024135 | reverse | 4 | pending |
| line-3 | line-3-0676-0728-s000000 | forward | 4 | pending |
| line-3 | line-3-0631-0604-s003010 | forward | 4 | pending |
| line-3 | line-3-0631-0604-s003010 | reverse | 3 | pending |
| line-3 | line-3-0551-0552-s005434 | forward | 3 | pending |
| line-3 | line-3-0551-0552-s005434 | reverse | 3 | pending |
| line-3 | line-3-0537-0433-s008357 | forward | 3 | pending |
| line-3 | line-3-0537-0433-s008357 | reverse | 3 | pending |
| line-3 | line-3-0454-0347-s011302 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Sylhet/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
