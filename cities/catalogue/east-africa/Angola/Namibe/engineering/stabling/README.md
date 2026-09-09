# Station and depot overnight allocation

Plan: **38 trainsets at stations + 46 at depots = 84 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0392-0605-s014962 | 46 | 2,254.0 | 13 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0350-0476-s012022 | station | forward | revenue | 1 |
| line-1 | line-1-0350-0476-s012022 | station | reverse | revenue | 1 |
| line-1 | line-1-0380-0370-s008449 | station | forward | revenue | 1 |
| line-1 | line-1-0380-0370-s008449 | station | reverse | revenue | 1 |
| line-1 | line-1-0392-0605-s014962 | station | reverse | revenue | 2 |
| line-1 | line-1-0395-0276-s006008 | station | forward | revenue | 1 |
| line-1 | line-1-0395-0276-s006008 | station | reverse | revenue | 1 |
| line-1 | line-1-0429-0142-s003002 | station | forward | revenue | 1 |
| line-1 | line-1-0429-0142-s003002 | station | reverse | revenue | 1 |
| line-1 | line-1-0535-0039-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0105-0497-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0233-0453-s003251 | station | forward | revenue | 1 |
| line-2 | line-2-0233-0453-s003251 | station | reverse | revenue | 1 |
| line-2 | line-2-0306-0393-s005279 | station | forward | revenue | 1 |
| line-2 | line-2-0306-0393-s005279 | station | reverse | revenue | 1 |
| line-2 | line-2-0380-0370-s007313 | station | forward | revenue | 1 |
| line-2 | line-2-0380-0370-s007313 | station | reverse | revenue | 1 |
| line-2 | line-2-0445-0392-s009255 | station | forward | revenue | 1 |
| line-2 | line-2-0445-0392-s009255 | station | reverse | revenue | 1 |
| line-2 | line-2-0545-0386-s012078 | station | reverse | revenue | 2 |
| line-3 | line-3-0133-0467-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0241-0382-s003450 | station | forward | revenue | 1 |
| line-3 | line-3-0241-0382-s003450 | station | reverse | revenue | 1 |
| line-3 | line-3-0372-0336-s006451 | station | forward | revenue | 1 |
| line-3 | line-3-0372-0336-s006451 | station | reverse | revenue | 1 |
| line-3 | line-3-0380-0370-s007666 | station | forward | revenue | 1 |
| line-3 | line-3-0380-0370-s007666 | station | reverse | revenue | 1 |
| line-3 | line-3-0427-0322-s009462 | station | forward | revenue | 1 |
| line-3 | line-3-0427-0322-s009462 | station | reverse | revenue | 1 |
| line-3 | line-3-0457-0230-s011603 | station | forward | revenue | 1 |
| line-3 | line-3-0457-0230-s011603 | station | reverse | revenue | 1 |
| line-3 | line-3-0484-0136-s013763 | station | reverse | revenue | 2 |
| line-1 | line-1-0392-0605-s014962 | depot | — | revenue | 15 |
| line-1 | line-1-0392-0605-s014962 | depot | — | spare | 2 |
| line-1 | line-1-0392-0605-s014962 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0392-0605-s014962 | depot | — | revenue | 10 |
| line-2 | line-1-0392-0605-s014962 | depot | — | spare | 2 |
| line-2 | line-1-0392-0605-s014962 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0392-0605-s014962 | depot | — | revenue | 12 |
| line-3 | line-1-0392-0605-s014962 | depot | — | spare | 2 |
| line-3 | line-1-0392-0605-s014962 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (13 trains), line-3 (15 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **84 trainsets at 19 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **75 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **46 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0535-0039-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0429-0142-s003002 | forward | revenue | 3 | pending |
| line-1 | line-1-0429-0142-s003002 | reverse | revenue | 3 | pending |
| line-1 | line-1-0395-0276-s006008 | forward | revenue | 3 | pending |
| line-1 | line-1-0395-0276-s006008 | reverse | revenue | 3 | pending |
| line-1 | line-1-0380-0370-s008449 | forward | revenue | 3 | pending |
| line-1 | line-1-0380-0370-s008449 | reverse | revenue | 3 | pending |
| line-1 | line-1-0350-0476-s012022 | forward | revenue | 2 | pending |
| line-1 | line-1-0350-0476-s012022 | reverse | revenue | 2 | pending |
| line-1 | line-1-0392-0605-s014962 | reverse | revenue | 2 | pending |
| line-1 | line-1-0350-0476-s012022 | forward | spare | 1 | pending |
| line-1 | line-1-0350-0476-s012022 | reverse | spare | 1 | pending |
| line-1 | line-1-0392-0605-s014962 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0105-0497-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0233-0453-s003251 | forward | revenue | 3 | pending |
| line-2 | line-2-0233-0453-s003251 | reverse | revenue | 2 | pending |
| line-2 | line-2-0306-0393-s005279 | forward | revenue | 2 | pending |
| line-2 | line-2-0306-0393-s005279 | reverse | revenue | 2 | pending |
| line-2 | line-2-0380-0370-s007313 | forward | revenue | 2 | pending |
| line-2 | line-2-0380-0370-s007313 | reverse | revenue | 2 | pending |
| line-2 | line-2-0445-0392-s009255 | forward | revenue | 2 | pending |
| line-2 | line-2-0445-0392-s009255 | reverse | revenue | 2 | pending |
| line-2 | line-2-0545-0386-s012078 | reverse | revenue | 2 | pending |
| line-2 | line-2-0233-0453-s003251 | reverse | spare | 1 | pending |
| line-2 | line-2-0306-0393-s005279 | forward | spare | 1 | pending |
| line-2 | line-2-0306-0393-s005279 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0133-0467-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0241-0382-s003450 | forward | revenue | 3 | pending |
| line-3 | line-3-0241-0382-s003450 | reverse | revenue | 2 | pending |
| line-3 | line-3-0372-0336-s006451 | forward | revenue | 2 | pending |
| line-3 | line-3-0372-0336-s006451 | reverse | revenue | 2 | pending |
| line-3 | line-3-0380-0370-s007666 | forward | revenue | 2 | pending |
| line-3 | line-3-0380-0370-s007666 | reverse | revenue | 2 | pending |
| line-3 | line-3-0427-0322-s009462 | forward | revenue | 2 | pending |
| line-3 | line-3-0427-0322-s009462 | reverse | revenue | 2 | pending |
| line-3 | line-3-0457-0230-s011603 | forward | revenue | 2 | pending |
| line-3 | line-3-0457-0230-s011603 | reverse | revenue | 2 | pending |
| line-3 | line-3-0484-0136-s013763 | reverse | revenue | 2 | pending |
| line-3 | line-3-0241-0382-s003450 | reverse | spare | 1 | pending |
| line-3 | line-3-0372-0336-s006451 | forward | spare | 1 | pending |
| line-3 | line-3-0372-0336-s006451 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**40 trainsets exceed the reference platform envelope**, requiring **1,960.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0350-0476-s012022 | 6 | 2 | 4 | 196.0 |
| line-1-0380-0370-s008449 | 6 | 4 | 2 | 98.0 |
| line-1-0392-0605-s014962 | 3 | 2 | 1 | 49.0 |
| line-1-0395-0276-s006008 | 6 | 2 | 4 | 196.0 |
| line-1-0429-0142-s003002 | 6 | 2 | 4 | 196.0 |
| line-1-0535-0039-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0105-0497-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0233-0453-s003251 | 6 | 2 | 4 | 196.0 |
| line-2-0306-0393-s005279 | 6 | 2 | 4 | 196.0 |
| line-2-0380-0370-s007313 | 4 | 4 | 0 | 0.0 |
| line-2-0445-0392-s009255 | 4 | 2 | 2 | 98.0 |
| line-2-0545-0386-s012078 | 2 | 2 | 0 | 0.0 |
| line-3-0133-0467-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0241-0382-s003450 | 6 | 2 | 4 | 196.0 |
| line-3-0372-0336-s006451 | 6 | 2 | 4 | 196.0 |
| line-3-0380-0370-s007666 | 4 | 4 | 0 | 0.0 |
| line-3-0427-0322-s009462 | 4 | 2 | 2 | 98.0 |
| line-3-0457-0230-s011603 | 4 | 2 | 2 | 98.0 |
| line-3-0484-0136-s013763 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Namibe/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
