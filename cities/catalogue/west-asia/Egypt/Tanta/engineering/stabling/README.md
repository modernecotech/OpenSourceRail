# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **176 trainsets at 20 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0334-0571-s000000 | forward | 4 | pending |
| line-1 | line-1-0407-0527-s003006 | forward | 4 | pending |
| line-1 | line-1-0407-0527-s003006 | reverse | 4 | pending |
| line-1 | line-1-0476-0534-s004607 | forward | 3 | pending |
| line-1 | line-1-0476-0534-s004607 | reverse | 3 | pending |
| line-1 | line-1-0547-0549-s006262 | forward | 3 | pending |
| line-1 | line-1-0547-0549-s006262 | reverse | 3 | pending |
| line-1 | line-1-0587-0564-s007616 | forward | 3 | pending |
| line-1 | line-1-0587-0564-s007616 | reverse | 3 | pending |
| line-1 | line-1-0678-0497-s010253 | forward | 3 | pending |
| line-1 | line-1-0678-0497-s010253 | reverse | 3 | pending |
| line-1 | line-1-0786-0445-s012879 | forward | 3 | pending |
| line-1 | line-1-0786-0445-s012879 | reverse | 3 | pending |
| line-1 | line-1-0950-0251-s018153 | reverse | 3 | pending |
| line-2 | line-2-0222-0124-s000000 | forward | 7 | pending |
| line-2 | line-2-0432-0358-s007005 | forward | 7 | pending |
| line-2 | line-2-0432-0358-s007005 | reverse | 7 | pending |
| line-2 | line-2-0537-0435-s010025 | forward | 7 | pending |
| line-2 | line-2-0537-0435-s010025 | reverse | 6 | pending |
| line-2 | line-2-0547-0549-s013008 | forward | 6 | pending |
| line-2 | line-2-0547-0549-s013008 | reverse | 6 | pending |
| line-2 | line-2-0635-0655-s016038 | forward | 6 | pending |
| line-2 | line-2-0635-0655-s016038 | reverse | 6 | pending |
| line-2 | line-2-0853-1088-s027821 | reverse | 6 | pending |
| line-3 | line-3-1031-0151-s000000 | forward | 7 | pending |
| line-3 | line-3-0623-0434-s011009 | forward | 7 | pending |
| line-3 | line-3-0623-0434-s011009 | reverse | 7 | pending |
| line-3 | line-3-0574-0488-s013085 | forward | 7 | pending |
| line-3 | line-3-0574-0488-s013085 | reverse | 7 | pending |
| line-3 | line-3-0547-0549-s015181 | forward | 7 | pending |
| line-3 | line-3-0547-0549-s015181 | reverse | 7 | pending |
| line-3 | line-3-0521-0613-s017023 | forward | 6 | pending |
| line-3 | line-3-0521-0613-s017023 | reverse | 6 | pending |
| line-3 | line-3-0068-0951-s028946 | reverse | 6 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Tanta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
