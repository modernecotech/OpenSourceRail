# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **147 trainsets at 18 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1075-0993-s000000 | forward | 7 | pending |
| line-1 | line-1-0649-0674-s013165 | forward | 7 | pending |
| line-1 | line-1-0649-0674-s013165 | reverse | 7 | pending |
| line-1 | line-1-0630-0577-s015263 | forward | 7 | pending |
| line-1 | line-1-0630-0577-s015263 | reverse | 7 | pending |
| line-1 | line-1-0560-0589-s017356 | forward | 7 | pending |
| line-1 | line-1-0560-0589-s017356 | reverse | 7 | pending |
| line-1 | line-1-0554-0516-s019190 | forward | 7 | pending |
| line-1 | line-1-0554-0516-s019190 | reverse | 7 | pending |
| line-1 | line-1-0435-0467-s022198 | forward | 7 | pending |
| line-1 | line-1-0435-0467-s022198 | reverse | 6 | pending |
| line-1 | line-1-0286-0224-s029156 | reverse | 6 | pending |
| line-2 | line-2-0375-0639-s000000 | forward | 4 | pending |
| line-2 | line-2-0505-0594-s003020 | forward | 4 | pending |
| line-2 | line-2-0505-0594-s003020 | reverse | 4 | pending |
| line-2 | line-2-0560-0589-s004334 | forward | 4 | pending |
| line-2 | line-2-0560-0589-s004334 | reverse | 4 | pending |
| line-2 | line-2-0520-0535-s006032 | forward | 3 | pending |
| line-2 | line-2-0520-0535-s006032 | reverse | 3 | pending |
| line-2 | line-2-0576-0495-s007636 | forward | 3 | pending |
| line-2 | line-2-0576-0495-s007636 | reverse | 3 | pending |
| line-2 | line-2-0568-0383-s010639 | forward | 3 | pending |
| line-2 | line-2-0568-0383-s010639 | reverse | 3 | pending |
| line-2 | line-2-0644-0312-s014031 | reverse | 3 | pending |
| line-3 | line-3-0804-0635-s000000 | forward | 4 | pending |
| line-3 | line-3-0697-0528-s003026 | forward | 4 | pending |
| line-3 | line-3-0697-0528-s003026 | reverse | 4 | pending |
| line-3 | line-3-0648-0426-s005472 | forward | 4 | pending |
| line-3 | line-3-0648-0426-s005472 | reverse | 4 | pending |
| line-3 | line-3-0636-0308-s007932 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Nasiriyah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
