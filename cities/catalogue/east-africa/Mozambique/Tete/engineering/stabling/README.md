# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **81 trainsets at 12 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0297-0416-s000000 | forward | 4 | pending |
| line-1 | line-1-0354-0508-s002598 | forward | 4 | pending |
| line-1 | line-1-0354-0508-s002598 | reverse | 4 | pending |
| line-1 | line-1-0459-0541-s005195 | forward | 4 | pending |
| line-1 | line-1-0459-0541-s005195 | reverse | 4 | pending |
| line-1 | line-1-0548-0553-s007540 | forward | 4 | pending |
| line-1 | line-1-0548-0553-s007540 | reverse | 3 | pending |
| line-1 | line-1-0851-0539-s014495 | reverse | 3 | pending |
| line-2 | line-2-0745-0787-s000000 | forward | 5 | pending |
| line-2 | line-2-0589-0646-s005114 | forward | 5 | pending |
| line-2 | line-2-0589-0646-s005114 | reverse | 5 | pending |
| line-2 | line-2-0548-0553-s007430 | forward | 4 | pending |
| line-2 | line-2-0548-0553-s007430 | reverse | 4 | pending |
| line-2 | line-2-0329-0468-s012615 | reverse | 4 | pending |
| line-3 | line-3-0533-0514-s000000 | forward | 6 | pending |
| line-3 | line-3-0485-0647-s003504 | forward | 6 | pending |
| line-3 | line-3-0485-0647-s003504 | reverse | 6 | pending |
| line-3 | line-3-0262-0845-s010756 | reverse | 6 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Tete/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
