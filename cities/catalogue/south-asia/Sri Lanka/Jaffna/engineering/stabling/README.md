# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **131 trainsets at 19 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0619-0561-s000000 | forward | 3 | pending |
| line-1 | line-1-0532-0549-s002545 | forward | 3 | pending |
| line-1 | line-1-0532-0549-s002545 | reverse | 3 | pending |
| line-1 | line-1-0492-0514-s004258 | forward | 3 | pending |
| line-1 | line-1-0492-0514-s004258 | reverse | 3 | pending |
| line-1 | line-1-0436-0530-s005968 | forward | 3 | pending |
| line-1 | line-1-0436-0530-s005968 | reverse | 3 | pending |
| line-1 | line-1-0324-0544-s008616 | forward | 3 | pending |
| line-1 | line-1-0324-0544-s008616 | reverse | 3 | pending |
| line-1 | line-1-0207-0571-s011246 | forward | 3 | pending |
| line-1 | line-1-0207-0571-s011246 | reverse | 3 | pending |
| line-1 | line-1-0097-0569-s013905 | reverse | 3 | pending |
| line-2 | line-2-0544-0867-s000000 | forward | 6 | pending |
| line-2 | line-2-0586-0698-s003996 | forward | 6 | pending |
| line-2 | line-2-0586-0698-s003996 | reverse | 6 | pending |
| line-2 | line-2-0532-0549-s007550 | forward | 6 | pending |
| line-2 | line-2-0532-0549-s007550 | reverse | 5 | pending |
| line-2 | line-2-0552-0474-s009575 | forward | 5 | pending |
| line-2 | line-2-0552-0474-s009575 | reverse | 5 | pending |
| line-2 | line-2-0488-0421-s011613 | forward | 5 | pending |
| line-2 | line-2-0488-0421-s011613 | reverse | 5 | pending |
| line-2 | line-2-0216-0107-s022455 | reverse | 5 | pending |
| line-3 | line-3-0089-1001-s000000 | forward | 5 | pending |
| line-3 | line-3-0305-0798-s007012 | forward | 4 | pending |
| line-3 | line-3-0305-0798-s007012 | reverse | 4 | pending |
| line-3 | line-3-0427-0649-s011230 | forward | 4 | pending |
| line-3 | line-3-0427-0649-s011230 | reverse | 4 | pending |
| line-3 | line-3-0483-0595-s013178 | forward | 4 | pending |
| line-3 | line-3-0483-0595-s013178 | reverse | 4 | pending |
| line-3 | line-3-0532-0549-s015108 | forward | 4 | pending |
| line-3 | line-3-0532-0549-s015108 | reverse | 4 | pending |
| line-3 | line-3-0600-0518-s017052 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Sri Lanka/Jaffna/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
