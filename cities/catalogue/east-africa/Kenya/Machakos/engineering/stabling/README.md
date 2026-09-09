# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **63 trainsets at 14 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **56 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0020-0297-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0301-0382-s006506 | forward | revenue | 3 | pending |
| line-1 | line-1-0301-0382-s006506 | reverse | revenue | 3 | pending |
| line-1 | line-1-0376-0374-s008219 | forward | revenue | 3 | pending |
| line-1 | line-1-0376-0374-s008219 | reverse | revenue | 3 | pending |
| line-1 | line-1-0449-0374-s010201 | forward | revenue | 3 | pending |
| line-1 | line-1-0449-0374-s010201 | reverse | revenue | 3 | pending |
| line-1 | line-1-0528-0329-s012182 | reverse | revenue | 2 | pending |
| line-1 | line-1-0528-0329-s012182 | reverse | spare | 1 | pending |
| line-1 | line-1-0020-0297-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0301-0382-s006506 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0431-0420-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0376-0374-s001720 | forward | revenue | 3 | pending |
| line-2 | line-2-0376-0374-s001720 | reverse | revenue | 3 | pending |
| line-2 | line-2-0390-0236-s004686 | forward | revenue | 2 | pending |
| line-2 | line-2-0390-0236-s004686 | reverse | revenue | 2 | pending |
| line-2 | line-2-0413-0102-s007646 | reverse | revenue | 2 | pending |
| line-2 | line-2-0390-0236-s004686 | forward | spare | 1 | pending |
| line-2 | line-2-0390-0236-s004686 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0208-0369-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0291-0339-s002061 | forward | revenue | 3 | pending |
| line-3 | line-3-0291-0339-s002061 | reverse | revenue | 2 | pending |
| line-3 | line-3-0376-0374-s004114 | forward | revenue | 2 | pending |
| line-3 | line-3-0376-0374-s004114 | reverse | revenue | 2 | pending |
| line-3 | line-3-0412-0270-s006574 | forward | revenue | 2 | pending |
| line-3 | line-3-0412-0270-s006574 | reverse | revenue | 2 | pending |
| line-3 | line-3-0390-0161-s009055 | reverse | revenue | 2 | pending |
| line-3 | line-3-0291-0339-s002061 | reverse | spare | 1 | pending |
| line-3 | line-3-0376-0374-s004114 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**29 trainsets exceed the reference platform envelope**, requiring **1,421.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0020-0297-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0301-0382-s006506 | 7 | 2 | 5 | 245.0 |
| line-1-0376-0374-s008219 | 6 | 4 | 2 | 98.0 |
| line-1-0449-0374-s010201 | 6 | 2 | 4 | 196.0 |
| line-1-0528-0329-s012182 | 3 | 2 | 1 | 49.0 |
| line-2-0376-0374-s001720 | 6 | 4 | 2 | 98.0 |
| line-2-0390-0236-s004686 | 6 | 2 | 4 | 196.0 |
| line-2-0413-0102-s007646 | 2 | 2 | 0 | 0.0 |
| line-2-0431-0420-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0208-0369-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0291-0339-s002061 | 6 | 2 | 4 | 196.0 |
| line-3-0376-0374-s004114 | 5 | 4 | 1 | 49.0 |
| line-3-0390-0161-s009055 | 2 | 2 | 0 | 0.0 |
| line-3-0412-0270-s006574 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Machakos/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
