# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **108 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **97 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0364-0285-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0487-0372-s004046 | forward | revenue | 4 | pending |
| line-1 | line-1-0487-0372-s004046 | reverse | revenue | 4 | pending |
| line-1 | line-1-0494-0481-s007068 | forward | revenue | 4 | pending |
| line-1 | line-1-0494-0481-s007068 | reverse | revenue | 4 | pending |
| line-1 | line-1-0542-0517-s010082 | forward | revenue | 3 | pending |
| line-1 | line-1-0542-0517-s010082 | reverse | revenue | 3 | pending |
| line-1 | line-1-0614-0584-s013090 | forward | revenue | 3 | pending |
| line-1 | line-1-0614-0584-s013090 | reverse | revenue | 3 | pending |
| line-1 | line-1-0774-0645-s017227 | forward | revenue | 3 | pending |
| line-1 | line-1-0774-0645-s017227 | reverse | revenue | 3 | pending |
| line-1 | line-1-0930-0771-s021391 | reverse | revenue | 3 | pending |
| line-1 | line-1-0542-0517-s010082 | forward | spare | 1 | pending |
| line-1 | line-1-0542-0517-s010082 | reverse | spare | 1 | pending |
| line-1 | line-1-0614-0584-s013090 | forward | spare | 1 | pending |
| line-1 | line-1-0614-0584-s013090 | reverse | spare | 1 | pending |
| line-1 | line-1-0774-0645-s017227 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0603-0186-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0549-0369-s005055 | forward | revenue | 3 | pending |
| line-2 | line-2-0549-0369-s005055 | reverse | revenue | 3 | pending |
| line-2 | line-2-0550-0459-s007102 | forward | revenue | 3 | pending |
| line-2 | line-2-0550-0459-s007102 | reverse | revenue | 3 | pending |
| line-2 | line-2-0546-0549-s009170 | forward | revenue | 2 | pending |
| line-2 | line-2-0546-0549-s009170 | reverse | revenue | 2 | pending |
| line-2 | line-2-0495-0609-s011079 | forward | revenue | 2 | pending |
| line-2 | line-2-0495-0609-s011079 | reverse | revenue | 2 | pending |
| line-2 | line-2-0419-0600-s013120 | forward | revenue | 2 | pending |
| line-2 | line-2-0419-0600-s013120 | reverse | revenue | 2 | pending |
| line-2 | line-2-0356-0657-s015183 | reverse | revenue | 2 | pending |
| line-2 | line-2-0546-0549-s009170 | forward | spare | 1 | pending |
| line-2 | line-2-0546-0549-s009170 | reverse | spare | 1 | pending |
| line-2 | line-2-0495-0609-s011079 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0376-0685-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0468-0626-s003012 | forward | revenue | 3 | pending |
| line-3 | line-3-0468-0626-s003012 | reverse | revenue | 3 | pending |
| line-3 | line-3-0546-0549-s005574 | forward | revenue | 3 | pending |
| line-3 | line-3-0546-0549-s005574 | reverse | revenue | 3 | pending |
| line-3 | line-3-0497-0462-s008223 | forward | revenue | 3 | pending |
| line-3 | line-3-0497-0462-s008223 | reverse | revenue | 3 | pending |
| line-3 | line-3-0512-0354-s010872 | forward | revenue | 2 | pending |
| line-3 | line-3-0512-0354-s010872 | reverse | revenue | 2 | pending |
| line-3 | line-3-0461-0244-s013506 | reverse | revenue | 2 | pending |
| line-3 | line-3-0512-0354-s010872 | forward | spare | 1 | pending |
| line-3 | line-3-0512-0354-s010872 | reverse | spare | 1 | pending |
| line-3 | line-3-0461-0244-s013506 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**60 trainsets exceed the reference platform envelope**, requiring **3,570.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0364-0285-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0487-0372-s004046 | 8 | 2 | 6 | 357.0 |
| line-1-0494-0481-s007068 | 8 | 4 | 4 | 238.0 |
| line-1-0542-0517-s010082 | 8 | 2 | 6 | 357.0 |
| line-1-0614-0584-s013090 | 8 | 2 | 6 | 357.0 |
| line-1-0774-0645-s017227 | 7 | 2 | 5 | 297.5 |
| line-1-0930-0771-s021391 | 3 | 2 | 1 | 59.5 |
| line-2-0356-0657-s015183 | 2 | 2 | 0 | 0.0 |
| line-2-0419-0600-s013120 | 4 | 2 | 2 | 119.0 |
| line-2-0495-0609-s011079 | 5 | 2 | 3 | 178.5 |
| line-2-0546-0549-s009170 | 6 | 4 | 2 | 119.0 |
| line-2-0549-0369-s005055 | 6 | 2 | 4 | 238.0 |
| line-2-0550-0459-s007102 | 6 | 2 | 4 | 238.0 |
| line-2-0603-0186-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0376-0685-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0461-0244-s013506 | 3 | 2 | 1 | 59.5 |
| line-3-0468-0626-s003012 | 6 | 2 | 4 | 238.0 |
| line-3-0497-0462-s008223 | 6 | 4 | 2 | 119.0 |
| line-3-0512-0354-s010872 | 6 | 2 | 4 | 238.0 |
| line-3-0546-0549-s005574 | 6 | 4 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Tanga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
