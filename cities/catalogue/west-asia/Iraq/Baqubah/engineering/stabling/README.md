# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **130 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0811-0508-s000000 | forward | 5 | pending |
| line-1 | line-1-0664-0504-s003001 | forward | 5 | pending |
| line-1 | line-1-0664-0504-s003001 | reverse | 4 | pending |
| line-1 | line-1-0558-0516-s005381 | forward | 4 | pending |
| line-1 | line-1-0558-0516-s005381 | reverse | 4 | pending |
| line-1 | line-1-0490-0409-s009008 | forward | 4 | pending |
| line-1 | line-1-0490-0409-s009008 | reverse | 4 | pending |
| line-1 | line-1-0395-0236-s015558 | reverse | 4 | pending |
| line-2 | line-2-0711-0229-s000000 | forward | 5 | pending |
| line-2 | line-2-0640-0311-s003018 | forward | 5 | pending |
| line-2 | line-2-0640-0311-s003018 | reverse | 5 | pending |
| line-2 | line-2-0582-0422-s006024 | forward | 5 | pending |
| line-2 | line-2-0582-0422-s006024 | reverse | 5 | pending |
| line-2 | line-2-0558-0516-s008324 | forward | 5 | pending |
| line-2 | line-2-0558-0516-s008324 | reverse | 4 | pending |
| line-2 | line-2-0493-0669-s012034 | forward | 4 | pending |
| line-2 | line-2-0493-0669-s012034 | reverse | 4 | pending |
| line-2 | line-2-0185-1002-s021939 | reverse | 4 | pending |
| line-3 | line-3-0123-0580-s000000 | forward | 4 | pending |
| line-3 | line-3-0379-0535-s007013 | forward | 4 | pending |
| line-3 | line-3-0379-0535-s007013 | reverse | 4 | pending |
| line-3 | line-3-0499-0473-s010013 | forward | 4 | pending |
| line-3 | line-3-0499-0473-s010013 | reverse | 4 | pending |
| line-3 | line-3-0558-0516-s011730 | forward | 4 | pending |
| line-3 | line-3-0558-0516-s011730 | reverse | 4 | pending |
| line-3 | line-3-0603-0480-s013018 | forward | 4 | pending |
| line-3 | line-3-0603-0480-s013018 | reverse | 3 | pending |
| line-3 | line-3-0709-0428-s016024 | forward | 3 | pending |
| line-3 | line-3-0709-0428-s016024 | reverse | 3 | pending |
| line-3 | line-3-0733-0315-s018483 | forward | 3 | pending |
| line-3 | line-3-0733-0315-s018483 | reverse | 3 | pending |
| line-3 | line-3-0927-0228-s023376 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Baqubah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
