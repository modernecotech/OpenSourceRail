# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **122 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0694-0708-s000000 | forward | 4 | pending |
| line-1 | line-1-0624-0618-s003014 | forward | 4 | pending |
| line-1 | line-1-0624-0618-s003014 | reverse | 4 | pending |
| line-1 | line-1-0551-0542-s006084 | forward | 4 | pending |
| line-1 | line-1-0551-0542-s006084 | reverse | 4 | pending |
| line-1 | line-1-0521-0478-s008145 | forward | 4 | pending |
| line-1 | line-1-0521-0478-s008145 | reverse | 4 | pending |
| line-1 | line-1-0505-0387-s010210 | forward | 4 | pending |
| line-1 | line-1-0505-0387-s010210 | reverse | 4 | pending |
| line-1 | line-1-0566-0133-s016982 | reverse | 4 | pending |
| line-2 | line-2-0302-0278-s000000 | forward | 5 | pending |
| line-2 | line-2-0436-0480-s005162 | forward | 5 | pending |
| line-2 | line-2-0436-0480-s005162 | reverse | 5 | pending |
| line-2 | line-2-0510-0581-s008166 | forward | 5 | pending |
| line-2 | line-2-0510-0581-s008166 | reverse | 4 | pending |
| line-2 | line-2-0551-0542-s010016 | forward | 4 | pending |
| line-2 | line-2-0551-0542-s010016 | reverse | 4 | pending |
| line-2 | line-2-0631-0561-s012785 | forward | 4 | pending |
| line-2 | line-2-0631-0561-s012785 | reverse | 4 | pending |
| line-2 | line-2-0702-0663-s015881 | forward | 4 | pending |
| line-2 | line-2-0702-0663-s015881 | reverse | 4 | pending |
| line-2 | line-2-0938-0810-s022386 | reverse | 4 | pending |
| line-3 | line-3-0871-0768-s000000 | forward | 5 | pending |
| line-3 | line-3-0575-0754-s006948 | forward | 5 | pending |
| line-3 | line-3-0575-0754-s006948 | reverse | 5 | pending |
| line-3 | line-3-0498-0671-s009954 | forward | 5 | pending |
| line-3 | line-3-0498-0671-s009954 | reverse | 5 | pending |
| line-3 | line-3-0383-0664-s012312 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Nampula/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
