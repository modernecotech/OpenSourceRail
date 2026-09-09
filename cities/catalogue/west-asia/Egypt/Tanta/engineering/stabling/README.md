# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **176 trainsets at 20 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **158 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0334-0571-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0407-0527-s003006 | forward | revenue | 3 | pending |
| line-1 | line-1-0407-0527-s003006 | reverse | revenue | 3 | pending |
| line-1 | line-1-0476-0534-s004607 | forward | revenue | 3 | pending |
| line-1 | line-1-0476-0534-s004607 | reverse | revenue | 3 | pending |
| line-1 | line-1-0547-0549-s006262 | forward | revenue | 3 | pending |
| line-1 | line-1-0547-0549-s006262 | reverse | revenue | 3 | pending |
| line-1 | line-1-0587-0564-s007616 | forward | revenue | 3 | pending |
| line-1 | line-1-0587-0564-s007616 | reverse | revenue | 3 | pending |
| line-1 | line-1-0678-0497-s010253 | forward | revenue | 3 | pending |
| line-1 | line-1-0678-0497-s010253 | reverse | revenue | 3 | pending |
| line-1 | line-1-0786-0445-s012879 | forward | revenue | 3 | pending |
| line-1 | line-1-0786-0445-s012879 | reverse | revenue | 2 | pending |
| line-1 | line-1-0950-0251-s018153 | reverse | revenue | 2 | pending |
| line-1 | line-1-0786-0445-s012879 | reverse | spare | 1 | pending |
| line-1 | line-1-0950-0251-s018153 | reverse | spare | 1 | pending |
| line-1 | line-1-0334-0571-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0407-0527-s003006 | forward | spare | 1 | pending |
| line-1 | line-1-0407-0527-s003006 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0222-0124-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0432-0358-s007005 | forward | revenue | 6 | pending |
| line-2 | line-2-0432-0358-s007005 | reverse | revenue | 6 | pending |
| line-2 | line-2-0537-0435-s010025 | forward | revenue | 6 | pending |
| line-2 | line-2-0537-0435-s010025 | reverse | revenue | 6 | pending |
| line-2 | line-2-0547-0549-s013008 | forward | revenue | 6 | pending |
| line-2 | line-2-0547-0549-s013008 | reverse | revenue | 6 | pending |
| line-2 | line-2-0635-0655-s016038 | forward | revenue | 6 | pending |
| line-2 | line-2-0635-0655-s016038 | reverse | revenue | 5 | pending |
| line-2 | line-2-0853-1088-s027821 | reverse | revenue | 5 | pending |
| line-2 | line-2-0635-0655-s016038 | reverse | spare | 1 | pending |
| line-2 | line-2-0853-1088-s027821 | reverse | spare | 1 | pending |
| line-2 | line-2-0222-0124-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0432-0358-s007005 | forward | spare | 1 | pending |
| line-2 | line-2-0432-0358-s007005 | reverse | spare | 1 | pending |
| line-2 | line-2-0537-0435-s010025 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1031-0151-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0623-0434-s011009 | forward | revenue | 6 | pending |
| line-3 | line-3-0623-0434-s011009 | reverse | revenue | 6 | pending |
| line-3 | line-3-0574-0488-s013085 | forward | revenue | 6 | pending |
| line-3 | line-3-0574-0488-s013085 | reverse | revenue | 6 | pending |
| line-3 | line-3-0547-0549-s015181 | forward | revenue | 6 | pending |
| line-3 | line-3-0547-0549-s015181 | reverse | revenue | 6 | pending |
| line-3 | line-3-0521-0613-s017023 | forward | revenue | 6 | pending |
| line-3 | line-3-0521-0613-s017023 | reverse | revenue | 6 | pending |
| line-3 | line-3-0068-0951-s028946 | reverse | revenue | 6 | pending |
| line-3 | line-3-1031-0151-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0623-0434-s011009 | forward | spare | 1 | pending |
| line-3 | line-3-0623-0434-s011009 | reverse | spare | 1 | pending |
| line-3 | line-3-0574-0488-s013085 | forward | spare | 1 | pending |
| line-3 | line-3-0574-0488-s013085 | reverse | spare | 1 | pending |
| line-3 | line-3-0547-0549-s015181 | forward | spare | 1 | pending |
| line-3 | line-3-0547-0549-s015181 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**130 trainsets exceed the reference platform envelope**, requiring **7,735.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0334-0571-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0407-0527-s003006 | 8 | 2 | 6 | 357.0 |
| line-1-0476-0534-s004607 | 6 | 2 | 4 | 238.0 |
| line-1-0547-0549-s006262 | 6 | 4 | 2 | 119.0 |
| line-1-0587-0564-s007616 | 6 | 2 | 4 | 238.0 |
| line-1-0678-0497-s010253 | 6 | 2 | 4 | 238.0 |
| line-1-0786-0445-s012879 | 6 | 2 | 4 | 238.0 |
| line-1-0950-0251-s018153 | 3 | 2 | 1 | 59.5 |
| line-2-0222-0124-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0432-0358-s007005 | 14 | 2 | 12 | 714.0 |
| line-2-0537-0435-s010025 | 13 | 2 | 11 | 654.5 |
| line-2-0547-0549-s013008 | 12 | 4 | 8 | 476.0 |
| line-2-0635-0655-s016038 | 12 | 2 | 10 | 595.0 |
| line-2-0853-1088-s027821 | 6 | 2 | 4 | 238.0 |
| line-3-0068-0951-s028946 | 6 | 2 | 4 | 238.0 |
| line-3-0521-0613-s017023 | 12 | 2 | 10 | 595.0 |
| line-3-0547-0549-s015181 | 14 | 4 | 10 | 595.0 |
| line-3-0574-0488-s013085 | 14 | 2 | 12 | 714.0 |
| line-3-0623-0434-s011009 | 14 | 2 | 12 | 714.0 |
| line-3-1031-0151-s000000 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Tanta/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
