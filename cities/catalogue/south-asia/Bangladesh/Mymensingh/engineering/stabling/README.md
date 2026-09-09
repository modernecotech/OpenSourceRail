# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **92 trainsets at 15 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **82 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0420-0384-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0451-0487-s003008 | forward | revenue | 3 | pending |
| line-1 | line-1-0451-0487-s003008 | reverse | revenue | 3 | pending |
| line-1 | line-1-0552-0547-s006117 | forward | revenue | 3 | pending |
| line-1 | line-1-0552-0547-s006117 | reverse | revenue | 3 | pending |
| line-1 | line-1-0613-0614-s008850 | forward | revenue | 3 | pending |
| line-1 | line-1-0613-0614-s008850 | reverse | revenue | 3 | pending |
| line-1 | line-1-0712-0672-s011599 | reverse | revenue | 2 | pending |
| line-1 | line-1-0712-0672-s011599 | reverse | spare | 1 | pending |
| line-1 | line-1-0420-0384-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0451-0487-s003008 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0571-0334-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0589-0466-s003011 | forward | revenue | 3 | pending |
| line-2 | line-2-0589-0466-s003011 | reverse | revenue | 3 | pending |
| line-2 | line-2-0552-0547-s005672 | forward | revenue | 3 | pending |
| line-2 | line-2-0552-0547-s005672 | reverse | revenue | 3 | pending |
| line-2 | line-2-0471-0638-s008339 | forward | revenue | 2 | pending |
| line-2 | line-2-0471-0638-s008339 | reverse | revenue | 2 | pending |
| line-2 | line-2-0447-0711-s010996 | reverse | revenue | 2 | pending |
| line-2 | line-2-0471-0638-s008339 | forward | spare | 1 | pending |
| line-2 | line-2-0471-0638-s008339 | reverse | spare | 1 | pending |
| line-2 | line-2-0447-0711-s010996 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0164-1077-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0467-0606-s012698 | forward | revenue | 5 | pending |
| line-3 | line-3-0467-0606-s012698 | reverse | revenue | 5 | pending |
| line-3 | line-3-0552-0547-s014922 | forward | revenue | 5 | pending |
| line-3 | line-3-0552-0547-s014922 | reverse | revenue | 5 | pending |
| line-3 | line-3-0655-0533-s017325 | forward | revenue | 5 | pending |
| line-3 | line-3-0655-0533-s017325 | reverse | revenue | 4 | pending |
| line-3 | line-3-0762-0506-s019717 | reverse | revenue | 4 | pending |
| line-3 | line-3-0655-0533-s017325 | reverse | spare | 1 | pending |
| line-3 | line-3-0762-0506-s019717 | reverse | spare | 1 | pending |
| line-3 | line-3-0164-1077-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0467-0606-s012698 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**56 trainsets exceed the reference platform envelope**, requiring **3,332.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0420-0384-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0451-0487-s003008 | 7 | 2 | 5 | 297.5 |
| line-1-0552-0547-s006117 | 6 | 4 | 2 | 119.0 |
| line-1-0613-0614-s008850 | 6 | 2 | 4 | 238.0 |
| line-1-0712-0672-s011599 | 3 | 2 | 1 | 59.5 |
| line-2-0447-0711-s010996 | 3 | 2 | 1 | 59.5 |
| line-2-0471-0638-s008339 | 6 | 2 | 4 | 238.0 |
| line-2-0552-0547-s005672 | 6 | 4 | 2 | 119.0 |
| line-2-0571-0334-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0589-0466-s003011 | 6 | 2 | 4 | 238.0 |
| line-3-0164-1077-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0467-0606-s012698 | 11 | 2 | 9 | 535.5 |
| line-3-0552-0547-s014922 | 10 | 4 | 6 | 357.0 |
| line-3-0655-0533-s017325 | 10 | 2 | 8 | 476.0 |
| line-3-0762-0506-s019717 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Mymensingh/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
