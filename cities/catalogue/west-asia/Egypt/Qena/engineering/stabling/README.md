# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **117 trainsets at 15 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **105 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0316-0690-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0446-0629-s004094 | forward | revenue | 3 | pending |
| line-1 | line-1-0446-0629-s004094 | reverse | revenue | 3 | pending |
| line-1 | line-1-0506-0601-s005695 | forward | revenue | 3 | pending |
| line-1 | line-1-0506-0601-s005695 | reverse | revenue | 3 | pending |
| line-1 | line-1-0546-0554-s007444 | forward | revenue | 3 | pending |
| line-1 | line-1-0546-0554-s007444 | reverse | revenue | 3 | pending |
| line-1 | line-1-0536-0502-s008705 | forward | revenue | 3 | pending |
| line-1 | line-1-0536-0502-s008705 | reverse | revenue | 2 | pending |
| line-1 | line-1-0602-0332-s012851 | reverse | revenue | 2 | pending |
| line-1 | line-1-0536-0502-s008705 | reverse | spare | 1 | pending |
| line-1 | line-1-0602-0332-s012851 | reverse | spare | 1 | pending |
| line-1 | line-1-0316-0690-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0473-0257-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0464-0442-s005032 | forward | revenue | 6 | pending |
| line-2 | line-2-0464-0442-s005032 | reverse | revenue | 6 | pending |
| line-2 | line-2-0546-0554-s008569 | forward | revenue | 6 | pending |
| line-2 | line-2-0546-0554-s008569 | reverse | revenue | 5 | pending |
| line-2 | line-2-0729-0759-s015056 | forward | revenue | 5 | pending |
| line-2 | line-2-0729-0759-s015056 | reverse | revenue | 5 | pending |
| line-2 | line-2-0949-0887-s020575 | reverse | revenue | 5 | pending |
| line-2 | line-2-0546-0554-s008569 | reverse | spare | 1 | pending |
| line-2 | line-2-0729-0759-s015056 | forward | spare | 1 | pending |
| line-2 | line-2-0729-0759-s015056 | reverse | spare | 1 | pending |
| line-2 | line-2-0949-0887-s020575 | reverse | spare | 1 | pending |
| line-2 | line-2-0473-0257-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0527-0507-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0477-0553-s003007 | forward | revenue | 6 | pending |
| line-3 | line-3-0477-0553-s003007 | reverse | revenue | 6 | pending |
| line-3 | line-3-0293-0655-s008838 | forward | revenue | 5 | pending |
| line-3 | line-3-0293-0655-s008838 | reverse | revenue | 5 | pending |
| line-3 | line-3-0014-0682-s015832 | reverse | revenue | 5 | pending |
| line-3 | line-3-0293-0655-s008838 | forward | spare | 1 | pending |
| line-3 | line-3-0293-0655-s008838 | reverse | spare | 1 | pending |
| line-3 | line-3-0014-0682-s015832 | reverse | spare | 1 | pending |
| line-3 | line-3-0527-0507-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**81 trainsets exceed the reference platform envelope**, requiring **4,819.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0316-0690-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0446-0629-s004094 | 6 | 2 | 4 | 238.0 |
| line-1-0506-0601-s005695 | 6 | 2 | 4 | 238.0 |
| line-1-0536-0502-s008705 | 6 | 4 | 2 | 119.0 |
| line-1-0546-0554-s007444 | 6 | 4 | 2 | 119.0 |
| line-1-0602-0332-s012851 | 3 | 2 | 1 | 59.5 |
| line-2-0464-0442-s005032 | 12 | 2 | 10 | 595.0 |
| line-2-0473-0257-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0546-0554-s008569 | 12 | 4 | 8 | 476.0 |
| line-2-0729-0759-s015056 | 12 | 2 | 10 | 595.0 |
| line-2-0949-0887-s020575 | 6 | 2 | 4 | 238.0 |
| line-3-0014-0682-s015832 | 6 | 2 | 4 | 238.0 |
| line-3-0293-0655-s008838 | 12 | 2 | 10 | 595.0 |
| line-3-0477-0553-s003007 | 12 | 2 | 10 | 595.0 |
| line-3-0527-0507-s000000 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Qena/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
