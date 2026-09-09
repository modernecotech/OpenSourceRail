# Station and depot overnight allocation

Plan: **34 trainsets at stations + 72 at depots = 106 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0588-0273-s020690 | 72 | 4,284.0 | 16 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0428-1076-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0516-0762-s007009 | station | forward | revenue | 1 |
| line-1 | line-1-0516-0762-s007009 | station | reverse | revenue | 1 |
| line-1 | line-1-0532-0335-s018386 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0335-s018386 | station | reverse | revenue | 1 |
| line-1 | line-1-0536-0476-s014010 | station | forward | revenue | 1 |
| line-1 | line-1-0536-0476-s014010 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0556-s011952 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0556-s011952 | station | reverse | revenue | 1 |
| line-1 | line-1-0567-0633-s010012 | station | forward | revenue | 1 |
| line-1 | line-1-0567-0633-s010012 | station | reverse | revenue | 1 |
| line-1 | line-1-0587-0404-s016057 | station | forward | revenue | 1 |
| line-1 | line-1-0587-0404-s016057 | station | reverse | revenue | 1 |
| line-1 | line-1-0588-0273-s020690 | station | reverse | revenue | 2 |
| line-2 | line-2-0363-0499-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0468-0556-s003002 | station | forward | revenue | 1 |
| line-2 | line-2-0468-0556-s003002 | station | reverse | revenue | 1 |
| line-2 | line-2-0555-0556-s005417 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0556-s005417 | station | reverse | revenue | 1 |
| line-2 | line-2-0615-0436-s009024 | station | forward | revenue | 1 |
| line-2 | line-2-0615-0436-s009024 | station | reverse | revenue | 1 |
| line-2 | line-2-0738-0390-s012729 | station | reverse | revenue | 2 |
| line-3 | line-3-0697-0571-s003016 | station | forward | revenue | 1 |
| line-3 | line-3-0697-0571-s003016 | station | reverse | revenue | 1 |
| line-3 | line-3-0717-0651-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0768-0382-s007964 | station | forward | revenue | 1 |
| line-3 | line-3-0768-0382-s007964 | station | reverse | revenue | 1 |
| line-3 | line-3-0796-0040-s016430 | station | reverse | revenue | 2 |
| line-1 | line-1-0588-0273-s020690 | depot | — | revenue | 23 |
| line-1 | line-1-0588-0273-s020690 | depot | — | spare | 3 |
| line-1 | line-1-0588-0273-s020690 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0588-0273-s020690 | depot | — | revenue | 14 |
| line-2 | line-1-0588-0273-s020690 | depot | — | spare | 2 |
| line-2 | line-1-0588-0273-s020690 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0588-0273-s020690 | depot | — | revenue | 24 |
| line-3 | line-1-0588-0273-s020690 | depot | — | spare | 3 |
| line-3 | line-1-0588-0273-s020690 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (17 trains), line-3 (28 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **106 trainsets at 17 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **95 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **72 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0428-1076-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0516-0762-s007009 | forward | revenue | 3 | pending |
| line-1 | line-1-0516-0762-s007009 | reverse | revenue | 3 | pending |
| line-1 | line-1-0567-0633-s010012 | forward | revenue | 3 | pending |
| line-1 | line-1-0567-0633-s010012 | reverse | revenue | 3 | pending |
| line-1 | line-1-0555-0556-s011952 | forward | revenue | 3 | pending |
| line-1 | line-1-0555-0556-s011952 | reverse | revenue | 3 | pending |
| line-1 | line-1-0536-0476-s014010 | forward | revenue | 3 | pending |
| line-1 | line-1-0536-0476-s014010 | reverse | revenue | 3 | pending |
| line-1 | line-1-0587-0404-s016057 | forward | revenue | 3 | pending |
| line-1 | line-1-0587-0404-s016057 | reverse | revenue | 3 | pending |
| line-1 | line-1-0532-0335-s018386 | forward | revenue | 2 | pending |
| line-1 | line-1-0532-0335-s018386 | reverse | revenue | 2 | pending |
| line-1 | line-1-0588-0273-s020690 | reverse | revenue | 2 | pending |
| line-1 | line-1-0532-0335-s018386 | forward | spare | 1 | pending |
| line-1 | line-1-0532-0335-s018386 | reverse | spare | 1 | pending |
| line-1 | line-1-0588-0273-s020690 | reverse | spare | 1 | pending |
| line-1 | line-1-0428-1076-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0363-0499-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0468-0556-s003002 | forward | revenue | 3 | pending |
| line-2 | line-2-0468-0556-s003002 | reverse | revenue | 3 | pending |
| line-2 | line-2-0555-0556-s005417 | forward | revenue | 3 | pending |
| line-2 | line-2-0555-0556-s005417 | reverse | revenue | 3 | pending |
| line-2 | line-2-0615-0436-s009024 | forward | revenue | 3 | pending |
| line-2 | line-2-0615-0436-s009024 | reverse | revenue | 3 | pending |
| line-2 | line-2-0738-0390-s012729 | reverse | revenue | 3 | pending |
| line-2 | line-2-0363-0499-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0468-0556-s003002 | forward | spare | 1 | pending |
| line-2 | line-2-0468-0556-s003002 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0717-0651-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0697-0571-s003016 | forward | revenue | 6 | pending |
| line-3 | line-3-0697-0571-s003016 | reverse | revenue | 5 | pending |
| line-3 | line-3-0768-0382-s007964 | forward | revenue | 5 | pending |
| line-3 | line-3-0768-0382-s007964 | reverse | revenue | 5 | pending |
| line-3 | line-3-0796-0040-s016430 | reverse | revenue | 5 | pending |
| line-3 | line-3-0697-0571-s003016 | reverse | spare | 1 | pending |
| line-3 | line-3-0768-0382-s007964 | forward | spare | 1 | pending |
| line-3 | line-3-0768-0382-s007964 | reverse | spare | 1 | pending |
| line-3 | line-3-0796-0040-s016430 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**68 trainsets exceed the reference platform envelope**, requiring **4,046.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0428-1076-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0516-0762-s007009 | 6 | 2 | 4 | 238.0 |
| line-1-0532-0335-s018386 | 6 | 2 | 4 | 238.0 |
| line-1-0536-0476-s014010 | 6 | 2 | 4 | 238.0 |
| line-1-0555-0556-s011952 | 6 | 4 | 2 | 119.0 |
| line-1-0567-0633-s010012 | 6 | 2 | 4 | 238.0 |
| line-1-0587-0404-s016057 | 6 | 2 | 4 | 238.0 |
| line-1-0588-0273-s020690 | 3 | 2 | 1 | 59.5 |
| line-2-0363-0499-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0468-0556-s003002 | 8 | 2 | 6 | 357.0 |
| line-2-0555-0556-s005417 | 6 | 4 | 2 | 119.0 |
| line-2-0615-0436-s009024 | 6 | 2 | 4 | 238.0 |
| line-2-0738-0390-s012729 | 3 | 2 | 1 | 59.5 |
| line-3-0697-0571-s003016 | 12 | 2 | 10 | 595.0 |
| line-3-0717-0651-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0768-0382-s007964 | 12 | 2 | 10 | 595.0 |
| line-3-0796-0040-s016430 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Diwaniyah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
