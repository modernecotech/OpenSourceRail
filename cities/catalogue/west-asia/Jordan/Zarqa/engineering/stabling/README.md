# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **227 trainsets at 20 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0400-1028-s000000 | forward | 8 | pending |
| line-1 | line-1-0461-0731-s007010 | forward | 8 | pending |
| line-1 | line-1-0461-0731-s007010 | reverse | 8 | pending |
| line-1 | line-1-0535-0616-s010034 | forward | 8 | pending |
| line-1 | line-1-0535-0616-s010034 | reverse | 8 | pending |
| line-1 | line-1-0576-0536-s012500 | forward | 8 | pending |
| line-1 | line-1-0576-0536-s012500 | reverse | 8 | pending |
| line-1 | line-1-0703-0488-s016055 | forward | 8 | pending |
| line-1 | line-1-0703-0488-s016055 | reverse | 8 | pending |
| line-1 | line-1-0810-0381-s019081 | forward | 7 | pending |
| line-1 | line-1-0810-0381-s019081 | reverse | 7 | pending |
| line-1 | line-1-1067-0037-s029681 | reverse | 7 | pending |
| line-2 | line-2-1078-0047-s000000 | forward | 7 | pending |
| line-2 | line-2-0857-0222-s007007 | forward | 7 | pending |
| line-2 | line-2-0857-0222-s007007 | reverse | 6 | pending |
| line-2 | line-2-0777-0335-s010012 | forward | 6 | pending |
| line-2 | line-2-0777-0335-s010012 | reverse | 6 | pending |
| line-2 | line-2-0670-0442-s013039 | forward | 6 | pending |
| line-2 | line-2-0670-0442-s013039 | reverse | 6 | pending |
| line-2 | line-2-0576-0536-s016381 | forward | 6 | pending |
| line-2 | line-2-0576-0536-s016381 | reverse | 6 | pending |
| line-2 | line-2-0477-0542-s019054 | forward | 6 | pending |
| line-2 | line-2-0477-0542-s019054 | reverse | 6 | pending |
| line-2 | line-2-0410-0650-s022055 | forward | 6 | pending |
| line-2 | line-2-0410-0650-s022055 | reverse | 6 | pending |
| line-2 | line-2-0192-0706-s027863 | reverse | 6 | pending |
| line-3 | line-3-0360-0400-s000000 | forward | 6 | pending |
| line-3 | line-3-0467-0450-s003026 | forward | 6 | pending |
| line-3 | line-3-0467-0450-s003026 | reverse | 6 | pending |
| line-3 | line-3-0576-0536-s006216 | forward | 6 | pending |
| line-3 | line-3-0576-0536-s006216 | reverse | 6 | pending |
| line-3 | line-3-0618-0641-s009034 | forward | 6 | pending |
| line-3 | line-3-0618-0641-s009034 | reverse | 6 | pending |
| line-3 | line-3-0626-0864-s014992 | reverse | 6 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Jordan/Zarqa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
