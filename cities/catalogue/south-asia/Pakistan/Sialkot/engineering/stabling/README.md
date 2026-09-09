# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **134 trainsets at 20 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0308-0707-s000000 | forward | 4 | pending |
| line-1 | line-1-0396-0636-s003184 | forward | 4 | pending |
| line-1 | line-1-0396-0636-s003184 | reverse | 4 | pending |
| line-1 | line-1-0517-0622-s005720 | forward | 4 | pending |
| line-1 | line-1-0517-0622-s005720 | reverse | 4 | pending |
| line-1 | line-1-0551-0556-s007502 | forward | 4 | pending |
| line-1 | line-1-0551-0556-s007502 | reverse | 4 | pending |
| line-1 | line-1-0596-0515-s008742 | forward | 4 | pending |
| line-1 | line-1-0596-0515-s008742 | reverse | 4 | pending |
| line-1 | line-1-0729-0472-s011758 | forward | 4 | pending |
| line-1 | line-1-0729-0472-s011758 | reverse | 3 | pending |
| line-1 | line-1-1041-0391-s018669 | reverse | 3 | pending |
| line-2 | line-2-0980-0964-s000000 | forward | 5 | pending |
| line-2 | line-2-0722-0779-s007021 | forward | 5 | pending |
| line-2 | line-2-0722-0779-s007021 | reverse | 5 | pending |
| line-2 | line-2-0660-0682-s010045 | forward | 5 | pending |
| line-2 | line-2-0660-0682-s010045 | reverse | 5 | pending |
| line-2 | line-2-0592-0630-s011953 | forward | 4 | pending |
| line-2 | line-2-0592-0630-s011953 | reverse | 4 | pending |
| line-2 | line-2-0551-0556-s013848 | forward | 4 | pending |
| line-2 | line-2-0551-0556-s013848 | reverse | 4 | pending |
| line-2 | line-2-0490-0470-s016073 | forward | 4 | pending |
| line-2 | line-2-0490-0470-s016073 | reverse | 4 | pending |
| line-2 | line-2-0332-0209-s022602 | reverse | 4 | pending |
| line-3 | line-3-0424-0761-s000000 | forward | 4 | pending |
| line-3 | line-3-0511-0688-s003013 | forward | 4 | pending |
| line-3 | line-3-0511-0688-s003013 | reverse | 4 | pending |
| line-3 | line-3-0535-0617-s004632 | forward | 4 | pending |
| line-3 | line-3-0535-0617-s004632 | reverse | 4 | pending |
| line-3 | line-3-0551-0556-s005985 | forward | 3 | pending |
| line-3 | line-3-0551-0556-s005985 | reverse | 3 | pending |
| line-3 | line-3-0552-0474-s007633 | forward | 3 | pending |
| line-3 | line-3-0552-0474-s007633 | reverse | 3 | pending |
| line-3 | line-3-0658-0193-s014131 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Sialkot/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
