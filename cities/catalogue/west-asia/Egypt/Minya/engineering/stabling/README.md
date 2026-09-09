# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **114 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **102 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0342-0395-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0374-0465-s003012 | forward | revenue | 3 | pending |
| line-1 | line-1-0374-0465-s003012 | reverse | revenue | 3 | pending |
| line-1 | line-1-0504-0515-s006026 | forward | revenue | 3 | pending |
| line-1 | line-1-0504-0515-s006026 | reverse | revenue | 2 | pending |
| line-1 | line-1-0546-0564-s007838 | forward | revenue | 2 | pending |
| line-1 | line-1-0546-0564-s007838 | reverse | revenue | 2 | pending |
| line-1 | line-1-0513-0645-s009951 | forward | revenue | 2 | pending |
| line-1 | line-1-0513-0645-s009951 | reverse | revenue | 2 | pending |
| line-1 | line-1-0541-0714-s012054 | forward | revenue | 2 | pending |
| line-1 | line-1-0541-0714-s012054 | reverse | revenue | 2 | pending |
| line-1 | line-1-0607-0783-s014154 | forward | revenue | 2 | pending |
| line-1 | line-1-0607-0783-s014154 | reverse | revenue | 2 | pending |
| line-1 | line-1-0651-0859-s016234 | forward | revenue | 2 | pending |
| line-1 | line-1-0651-0859-s016234 | reverse | revenue | 2 | pending |
| line-1 | line-1-0684-0936-s018318 | reverse | revenue | 2 | pending |
| line-1 | line-1-0504-0515-s006026 | reverse | spare | 1 | pending |
| line-1 | line-1-0546-0564-s007838 | forward | spare | 1 | pending |
| line-1 | line-1-0546-0564-s007838 | reverse | spare | 1 | pending |
| line-1 | line-1-0513-0645-s009951 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0459-0399-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0546-0490-s003007 | forward | revenue | 4 | pending |
| line-2 | line-2-0546-0490-s003007 | reverse | revenue | 4 | pending |
| line-2 | line-2-0546-0564-s004686 | forward | revenue | 3 | pending |
| line-2 | line-2-0546-0564-s004686 | reverse | revenue | 3 | pending |
| line-2 | line-2-0546-0630-s006023 | forward | revenue | 3 | pending |
| line-2 | line-2-0546-0630-s006023 | reverse | revenue | 3 | pending |
| line-2 | line-2-0484-0747-s009036 | forward | revenue | 3 | pending |
| line-2 | line-2-0484-0747-s009036 | reverse | revenue | 3 | pending |
| line-2 | line-2-0323-1016-s017716 | reverse | revenue | 3 | pending |
| line-2 | line-2-0546-0564-s004686 | forward | spare | 1 | pending |
| line-2 | line-2-0546-0564-s004686 | reverse | spare | 1 | pending |
| line-2 | line-2-0546-0630-s006023 | forward | spare | 1 | pending |
| line-2 | line-2-0546-0630-s006023 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0681-0604-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0546-0564-s003713 | forward | revenue | 4 | pending |
| line-3 | line-3-0546-0564-s003713 | reverse | revenue | 4 | pending |
| line-3 | line-3-0471-0628-s006029 | forward | revenue | 3 | pending |
| line-3 | line-3-0471-0628-s006029 | reverse | revenue | 3 | pending |
| line-3 | line-3-0522-0743-s009039 | forward | revenue | 3 | pending |
| line-3 | line-3-0522-0743-s009039 | reverse | revenue | 3 | pending |
| line-3 | line-3-0507-0816-s011090 | forward | revenue | 3 | pending |
| line-3 | line-3-0507-0816-s011090 | reverse | revenue | 3 | pending |
| line-3 | line-3-0383-1021-s017162 | reverse | revenue | 3 | pending |
| line-3 | line-3-0471-0628-s006029 | forward | spare | 1 | pending |
| line-3 | line-3-0471-0628-s006029 | reverse | spare | 1 | pending |
| line-3 | line-3-0522-0743-s009039 | forward | spare | 1 | pending |
| line-3 | line-3-0522-0743-s009039 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**66 trainsets exceed the reference platform envelope**, requiring **3,927.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0342-0395-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0374-0465-s003012 | 6 | 2 | 4 | 238.0 |
| line-1-0504-0515-s006026 | 6 | 2 | 4 | 238.0 |
| line-1-0513-0645-s009951 | 5 | 2 | 3 | 178.5 |
| line-1-0541-0714-s012054 | 4 | 2 | 2 | 119.0 |
| line-1-0546-0564-s007838 | 6 | 4 | 2 | 119.0 |
| line-1-0607-0783-s014154 | 4 | 2 | 2 | 119.0 |
| line-1-0651-0859-s016234 | 4 | 2 | 2 | 119.0 |
| line-1-0684-0936-s018318 | 2 | 2 | 0 | 0.0 |
| line-2-0323-1016-s017716 | 3 | 2 | 1 | 59.5 |
| line-2-0459-0399-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0484-0747-s009036 | 6 | 2 | 4 | 238.0 |
| line-2-0546-0490-s003007 | 8 | 2 | 6 | 357.0 |
| line-2-0546-0564-s004686 | 8 | 4 | 4 | 238.0 |
| line-2-0546-0630-s006023 | 8 | 2 | 6 | 357.0 |
| line-3-0383-1021-s017162 | 3 | 2 | 1 | 59.5 |
| line-3-0471-0628-s006029 | 8 | 2 | 6 | 357.0 |
| line-3-0507-0816-s011090 | 6 | 2 | 4 | 238.0 |
| line-3-0522-0743-s009039 | 8 | 2 | 6 | 357.0 |
| line-3-0546-0564-s003713 | 8 | 4 | 4 | 238.0 |
| line-3-0681-0604-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Minya/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
