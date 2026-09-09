# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **87 trainsets at 16 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **78 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0143-0732-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0267-0590-s004716 | forward | revenue | 3 | pending |
| line-1 | line-1-0267-0590-s004716 | reverse | revenue | 3 | pending |
| line-1 | line-1-0342-0483-s007726 | forward | revenue | 3 | pending |
| line-1 | line-1-0342-0483-s007726 | reverse | revenue | 3 | pending |
| line-1 | line-1-0384-0378-s011295 | forward | revenue | 3 | pending |
| line-1 | line-1-0384-0378-s011295 | reverse | revenue | 3 | pending |
| line-1 | line-1-0463-0382-s013520 | forward | revenue | 3 | pending |
| line-1 | line-1-0463-0382-s013520 | reverse | revenue | 2 | pending |
| line-1 | line-1-0556-0341-s015753 | reverse | revenue | 2 | pending |
| line-1 | line-1-0463-0382-s013520 | reverse | spare | 1 | pending |
| line-1 | line-1-0556-0341-s015753 | reverse | spare | 1 | pending |
| line-1 | line-1-0143-0732-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0648-0466-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0546-0435-s003016 | forward | revenue | 3 | pending |
| line-2 | line-2-0546-0435-s003016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0421-0430-s006028 | forward | revenue | 3 | pending |
| line-2 | line-2-0421-0430-s006028 | reverse | revenue | 3 | pending |
| line-2 | line-2-0384-0378-s007450 | forward | revenue | 3 | pending |
| line-2 | line-2-0384-0378-s007450 | reverse | revenue | 3 | pending |
| line-2 | line-2-0277-0213-s012303 | reverse | revenue | 2 | pending |
| line-2 | line-2-0277-0213-s012303 | reverse | spare | 1 | pending |
| line-2 | line-2-0648-0466-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0546-0435-s003016 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0732-0095-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0512-0297-s007013 | forward | revenue | 4 | pending |
| line-3 | line-3-0512-0297-s007013 | reverse | revenue | 4 | pending |
| line-3 | line-3-0422-0313-s010021 | forward | revenue | 3 | pending |
| line-3 | line-3-0422-0313-s010021 | reverse | revenue | 3 | pending |
| line-3 | line-3-0384-0378-s011702 | forward | revenue | 3 | pending |
| line-3 | line-3-0384-0378-s011702 | reverse | revenue | 3 | pending |
| line-3 | line-3-0315-0459-s014008 | reverse | revenue | 3 | pending |
| line-3 | line-3-0422-0313-s010021 | forward | spare | 1 | pending |
| line-3 | line-3-0422-0313-s010021 | reverse | spare | 1 | pending |
| line-3 | line-3-0384-0378-s011702 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**49 trainsets exceed the reference platform envelope**, requiring **2,401.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0143-0732-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0267-0590-s004716 | 6 | 2 | 4 | 196.0 |
| line-1-0342-0483-s007726 | 6 | 2 | 4 | 196.0 |
| line-1-0384-0378-s011295 | 6 | 4 | 2 | 98.0 |
| line-1-0463-0382-s013520 | 6 | 2 | 4 | 196.0 |
| line-1-0556-0341-s015753 | 3 | 2 | 1 | 49.0 |
| line-2-0277-0213-s012303 | 3 | 2 | 1 | 49.0 |
| line-2-0384-0378-s007450 | 6 | 4 | 2 | 98.0 |
| line-2-0421-0430-s006028 | 6 | 2 | 4 | 196.0 |
| line-2-0546-0435-s003016 | 7 | 2 | 5 | 245.0 |
| line-2-0648-0466-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0315-0459-s014008 | 3 | 2 | 1 | 49.0 |
| line-3-0384-0378-s011702 | 7 | 4 | 3 | 147.0 |
| line-3-0422-0313-s010021 | 8 | 2 | 6 | 294.0 |
| line-3-0512-0297-s007013 | 8 | 2 | 6 | 294.0 |
| line-3-0732-0095-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Jinja/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
