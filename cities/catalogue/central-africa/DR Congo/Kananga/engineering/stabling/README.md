# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **36 trainsets at 14 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1244-1036-s000000 | forward | 3 | pending |
| line-1 | line-1-1101-0959-s003498 | forward | 3 | pending |
| line-1 | line-1-1101-0959-s003498 | reverse | 3 | pending |
| line-1 | line-1-0992-0866-s007016 | forward | 3 | pending |
| line-1 | line-1-0992-0866-s007016 | reverse | 3 | pending |
| line-1 | line-1-0935-0749-s010321 | forward | 3 | pending |
| line-1 | line-1-0935-0749-s010321 | reverse | 2 | pending |
| line-1 | line-1-0855-0751-s012170 | forward | 2 | pending |
| line-1 | line-1-0855-0751-s012170 | reverse | 2 | pending |
| line-1 | line-1-0788-0713-s015879 | reverse | 2 | pending |
| line-2 | line-2-0801-0801-s000000 | forward | 1 | pending |
| line-2 | line-2-0801-0801-s000000 | reverse | 1 | pending |
| line-2 | line-2-0814-0932-s003009 | reverse | 1 | pending |
| line-2 | line-2-0797-1060-s006024 | forward | 1 | pending |
| line-2 | line-2-0830-1056-s009030 | forward | 1 | pending |
| line-2 | line-2-0825-0977-s010999 | forward | 1 | pending |
| line-2 | line-2-0825-0977-s010999 | reverse | 1 | pending |
| line-2 | line-2-0876-0899-s012981 | reverse | 1 | pending |
| line-2 | line-2-0855-0751-s016569 | forward | 1 | pending |
| line-2 | line-2-0788-0713-s020302 | forward | 1 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Kananga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
