# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **113 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **101 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0198-1067-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0401-0806-s007019 | forward | revenue | 4 | pending |
| line-1 | line-1-0401-0806-s007019 | reverse | revenue | 4 | pending |
| line-1 | line-1-0471-0694-s010022 | forward | revenue | 4 | pending |
| line-1 | line-1-0471-0694-s010022 | reverse | revenue | 4 | pending |
| line-1 | line-1-0529-0600-s013032 | forward | revenue | 4 | pending |
| line-1 | line-1-0529-0600-s013032 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0548-s014441 | forward | revenue | 3 | pending |
| line-1 | line-1-0550-0548-s014441 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0449-s017673 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0449-s017673 | reverse | revenue | 3 | pending |
| line-1 | line-1-0648-0369-s020673 | forward | revenue | 3 | pending |
| line-1 | line-1-0648-0369-s020673 | reverse | revenue | 3 | pending |
| line-1 | line-1-0737-0167-s026410 | reverse | revenue | 3 | pending |
| line-1 | line-1-0550-0548-s014441 | forward | spare | 1 | pending |
| line-1 | line-1-0550-0548-s014441 | reverse | spare | 1 | pending |
| line-1 | line-1-0548-0449-s017673 | forward | spare | 1 | pending |
| line-1 | line-1-0548-0449-s017673 | reverse | spare | 1 | pending |
| line-1 | line-1-0648-0369-s020673 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0375-0601-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0475-0547-s003014 | forward | revenue | 4 | pending |
| line-2 | line-2-0475-0547-s003014 | reverse | revenue | 4 | pending |
| line-2 | line-2-0550-0548-s005032 | forward | revenue | 4 | pending |
| line-2 | line-2-0550-0548-s005032 | reverse | revenue | 4 | pending |
| line-2 | line-2-0639-0486-s007636 | forward | revenue | 4 | pending |
| line-2 | line-2-0639-0486-s007636 | reverse | revenue | 4 | pending |
| line-2 | line-2-0928-0268-s015651 | reverse | revenue | 3 | pending |
| line-2 | line-2-0928-0268-s015651 | reverse | spare | 1 | pending |
| line-2 | line-2-0375-0601-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0475-0547-s003014 | forward | spare | 1 | pending |
| line-2 | line-2-0475-0547-s003014 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0487-0404-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0517-0516-s003003 | forward | revenue | 2 | pending |
| line-3 | line-3-0517-0516-s003003 | reverse | revenue | 2 | pending |
| line-3 | line-3-0550-0548-s004206 | forward | revenue | 2 | pending |
| line-3 | line-3-0550-0548-s004206 | reverse | revenue | 2 | pending |
| line-3 | line-3-0488-0597-s006296 | forward | revenue | 2 | pending |
| line-3 | line-3-0488-0597-s006296 | reverse | revenue | 2 | pending |
| line-3 | line-3-0445-0677-s008377 | forward | revenue | 2 | pending |
| line-3 | line-3-0445-0677-s008377 | reverse | revenue | 2 | pending |
| line-3 | line-3-0455-0763-s010463 | reverse | revenue | 2 | pending |
| line-3 | line-3-0517-0516-s003003 | forward | spare | 1 | pending |
| line-3 | line-3-0517-0516-s003003 | reverse | spare | 1 | pending |
| line-3 | line-3-0550-0548-s004206 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**69 trainsets exceed the reference platform envelope**, requiring **4,105.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0198-1067-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0401-0806-s007019 | 8 | 2 | 6 | 357.0 |
| line-1-0471-0694-s010022 | 8 | 2 | 6 | 357.0 |
| line-1-0529-0600-s013032 | 8 | 2 | 6 | 357.0 |
| line-1-0548-0449-s017673 | 8 | 2 | 6 | 357.0 |
| line-1-0550-0548-s014441 | 8 | 4 | 4 | 238.0 |
| line-1-0648-0369-s020673 | 7 | 2 | 5 | 297.5 |
| line-1-0737-0167-s026410 | 3 | 2 | 1 | 59.5 |
| line-2-0375-0601-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0475-0547-s003014 | 10 | 2 | 8 | 476.0 |
| line-2-0550-0548-s005032 | 8 | 4 | 4 | 238.0 |
| line-2-0639-0486-s007636 | 8 | 2 | 6 | 357.0 |
| line-2-0928-0268-s015651 | 4 | 2 | 2 | 119.0 |
| line-3-0445-0677-s008377 | 4 | 2 | 2 | 119.0 |
| line-3-0455-0763-s010463 | 2 | 2 | 0 | 0.0 |
| line-3-0487-0404-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0488-0597-s006296 | 4 | 2 | 2 | 119.0 |
| line-3-0517-0516-s003003 | 6 | 2 | 4 | 238.0 |
| line-3-0550-0548-s004206 | 5 | 4 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Maroua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
