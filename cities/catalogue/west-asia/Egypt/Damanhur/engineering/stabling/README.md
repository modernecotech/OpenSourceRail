# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **103 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0370-0539-s000000 | forward | 3 | pending |
| line-1 | line-1-0484-0544-s003019 | forward | 3 | pending |
| line-1 | line-1-0484-0544-s003019 | reverse | 3 | pending |
| line-1 | line-1-0549-0552-s005079 | forward | 3 | pending |
| line-1 | line-1-0549-0552-s005079 | reverse | 3 | pending |
| line-1 | line-1-0643-0586-s007241 | forward | 3 | pending |
| line-1 | line-1-0643-0586-s007241 | reverse | 3 | pending |
| line-1 | line-1-0731-0566-s009382 | reverse | 2 | pending |
| line-2 | line-2-0647-1100-s000000 | forward | 4 | pending |
| line-2 | line-2-0631-0792-s007005 | forward | 4 | pending |
| line-2 | line-2-0631-0792-s007005 | reverse | 4 | pending |
| line-2 | line-2-0585-0663-s010140 | forward | 4 | pending |
| line-2 | line-2-0585-0663-s010140 | reverse | 4 | pending |
| line-2 | line-2-0549-0552-s013208 | forward | 4 | pending |
| line-2 | line-2-0549-0552-s013208 | reverse | 4 | pending |
| line-2 | line-2-0558-0473-s015787 | forward | 4 | pending |
| line-2 | line-2-0558-0473-s015787 | reverse | 4 | pending |
| line-2 | line-2-0526-0378-s018262 | reverse | 4 | pending |
| line-3 | line-3-0740-0226-s000000 | forward | 4 | pending |
| line-3 | line-3-0596-0457-s006305 | forward | 4 | pending |
| line-3 | line-3-0596-0457-s006305 | reverse | 4 | pending |
| line-3 | line-3-0549-0552-s008988 | forward | 4 | pending |
| line-3 | line-3-0549-0552-s008988 | reverse | 4 | pending |
| line-3 | line-3-0533-0623-s011338 | forward | 4 | pending |
| line-3 | line-3-0533-0623-s011338 | reverse | 4 | pending |
| line-3 | line-3-0472-0788-s015557 | forward | 4 | pending |
| line-3 | line-3-0472-0788-s015557 | reverse | 4 | pending |
| line-3 | line-3-0354-0950-s019775 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Damanhur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
