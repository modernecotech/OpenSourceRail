# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **116 trainsets at 18 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0383-0392-s000000 | forward | 4 | pending |
| line-1 | line-1-0458-0474-s003014 | forward | 4 | pending |
| line-1 | line-1-0458-0474-s003014 | reverse | 4 | pending |
| line-1 | line-1-0542-0550-s006711 | forward | 4 | pending |
| line-1 | line-1-0542-0550-s006711 | reverse | 4 | pending |
| line-1 | line-1-0507-0644-s009043 | forward | 4 | pending |
| line-1 | line-1-0507-0644-s009043 | reverse | 3 | pending |
| line-1 | line-1-0531-0881-s014774 | reverse | 3 | pending |
| line-2 | line-2-0381-0736-s000000 | forward | 4 | pending |
| line-2 | line-2-0437-0636-s003010 | forward | 4 | pending |
| line-2 | line-2-0437-0636-s003010 | reverse | 4 | pending |
| line-2 | line-2-0480-0572-s005074 | forward | 4 | pending |
| line-2 | line-2-0480-0572-s005074 | reverse | 4 | pending |
| line-2 | line-2-0542-0550-s007127 | forward | 4 | pending |
| line-2 | line-2-0542-0550-s007127 | reverse | 4 | pending |
| line-2 | line-2-0615-0523-s009026 | forward | 4 | pending |
| line-2 | line-2-0615-0523-s009026 | reverse | 4 | pending |
| line-2 | line-2-0749-0422-s012543 | forward | 4 | pending |
| line-2 | line-2-0749-0422-s012543 | reverse | 4 | pending |
| line-2 | line-2-1065-0208-s021348 | reverse | 3 | pending |
| line-3 | line-3-0651-0932-s000000 | forward | 4 | pending |
| line-3 | line-3-0561-0644-s006880 | forward | 4 | pending |
| line-3 | line-3-0561-0644-s006880 | reverse | 4 | pending |
| line-3 | line-3-0542-0550-s009288 | forward | 4 | pending |
| line-3 | line-3-0542-0550-s009288 | reverse | 4 | pending |
| line-3 | line-3-0602-0468-s012246 | forward | 4 | pending |
| line-3 | line-3-0602-0468-s012246 | reverse | 4 | pending |
| line-3 | line-3-0593-0338-s015181 | forward | 4 | pending |
| line-3 | line-3-0593-0338-s015181 | reverse | 4 | pending |
| line-3 | line-3-0564-0202-s018141 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Nakuru/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
