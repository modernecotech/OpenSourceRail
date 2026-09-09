# Station and depot overnight allocation

Plan: **42 trainsets at stations + 83 at depots = 125 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0404-0807-s019508 | 83 | 4,938.5 | 19 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0278-0667-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0367-0647-s003022 | station | forward | revenue | 1 |
| line-1 | line-1-0367-0647-s003022 | station | reverse | revenue | 1 |
| line-1 | line-1-0489-0616-s006026 | station | forward | revenue | 1 |
| line-1 | line-1-0489-0616-s006026 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0583-s007706 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0583-s007706 | station | reverse | revenue | 1 |
| line-1 | line-1-0603-0599-s009034 | station | forward | revenue | 1 |
| line-1 | line-1-0603-0599-s009034 | station | reverse | revenue | 1 |
| line-1 | line-1-0730-0541-s012054 | station | forward | revenue | 1 |
| line-1 | line-1-0730-0541-s012054 | station | reverse | revenue | 1 |
| line-1 | line-1-1072-0471-s019474 | station | reverse | revenue | 2 |
| line-2 | line-2-0032-0601-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0246-0611-s007011 | station | forward | revenue | 1 |
| line-2 | line-2-0246-0611-s007011 | station | reverse | revenue | 1 |
| line-2 | line-2-0341-0536-s010016 | station | forward | revenue | 1 |
| line-2 | line-2-0341-0536-s010016 | station | reverse | revenue | 1 |
| line-2 | line-2-0469-0531-s013026 | station | forward | revenue | 1 |
| line-2 | line-2-0469-0531-s013026 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0517-s014982 | station | forward | revenue | 1 |
| line-2 | line-2-0561-0517-s014982 | station | reverse | revenue | 1 |
| line-2 | line-2-0636-0491-s016920 | station | forward | revenue | 1 |
| line-2 | line-2-0636-0491-s016920 | station | reverse | revenue | 1 |
| line-2 | line-2-0687-0442-s018881 | station | reverse | revenue | 2 |
| line-3 | line-3-0404-0807-s019508 | station | reverse | revenue | 2 |
| line-3 | line-3-0433-0712-s017123 | station | forward | revenue | 1 |
| line-3 | line-3-0433-0712-s017123 | station | reverse | revenue | 1 |
| line-3 | line-3-0503-0654-s014732 | station | forward | revenue | 1 |
| line-3 | line-3-0503-0654-s014732 | station | reverse | revenue | 1 |
| line-3 | line-3-0555-0583-s012336 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0583-s012336 | station | reverse | revenue | 1 |
| line-3 | line-3-0563-0480-s010044 | station | forward | revenue | 1 |
| line-3 | line-3-0563-0480-s010044 | station | reverse | revenue | 1 |
| line-3 | line-3-0597-0344-s007019 | station | forward | revenue | 1 |
| line-3 | line-3-0597-0344-s007019 | station | reverse | revenue | 1 |
| line-3 | line-3-0598-0069-s000000 | station | forward | revenue | 2 |
| line-1 | line-3-0404-0807-s019508 | depot | — | revenue | 24 |
| line-1 | line-3-0404-0807-s019508 | depot | — | spare | 3 |
| line-1 | line-3-0404-0807-s019508 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0404-0807-s019508 | depot | — | revenue | 23 |
| line-2 | line-3-0404-0807-s019508 | depot | — | spare | 3 |
| line-2 | line-3-0404-0807-s019508 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0404-0807-s019508 | depot | — | revenue | 24 |
| line-3 | line-3-0404-0807-s019508 | depot | — | spare | 3 |
| line-3 | line-3-0404-0807-s019508 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (28 trains), line-2 (27 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **125 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **113 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **83 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0278-0667-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0367-0647-s003022 | forward | revenue | 4 | pending |
| line-1 | line-1-0367-0647-s003022 | reverse | revenue | 3 | pending |
| line-1 | line-1-0489-0616-s006026 | forward | revenue | 3 | pending |
| line-1 | line-1-0489-0616-s006026 | reverse | revenue | 3 | pending |
| line-1 | line-1-0555-0583-s007706 | forward | revenue | 3 | pending |
| line-1 | line-1-0555-0583-s007706 | reverse | revenue | 3 | pending |
| line-1 | line-1-0603-0599-s009034 | forward | revenue | 3 | pending |
| line-1 | line-1-0603-0599-s009034 | reverse | revenue | 3 | pending |
| line-1 | line-1-0730-0541-s012054 | forward | revenue | 3 | pending |
| line-1 | line-1-0730-0541-s012054 | reverse | revenue | 3 | pending |
| line-1 | line-1-1072-0471-s019474 | reverse | revenue | 3 | pending |
| line-1 | line-1-0367-0647-s003022 | reverse | spare | 1 | pending |
| line-1 | line-1-0489-0616-s006026 | forward | spare | 1 | pending |
| line-1 | line-1-0489-0616-s006026 | reverse | spare | 1 | pending |
| line-1 | line-1-0555-0583-s007706 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0032-0601-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0246-0611-s007011 | forward | revenue | 3 | pending |
| line-2 | line-2-0246-0611-s007011 | reverse | revenue | 3 | pending |
| line-2 | line-2-0341-0536-s010016 | forward | revenue | 3 | pending |
| line-2 | line-2-0341-0536-s010016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0469-0531-s013026 | forward | revenue | 3 | pending |
| line-2 | line-2-0469-0531-s013026 | reverse | revenue | 3 | pending |
| line-2 | line-2-0561-0517-s014982 | forward | revenue | 3 | pending |
| line-2 | line-2-0561-0517-s014982 | reverse | revenue | 3 | pending |
| line-2 | line-2-0636-0491-s016920 | forward | revenue | 3 | pending |
| line-2 | line-2-0636-0491-s016920 | reverse | revenue | 3 | pending |
| line-2 | line-2-0687-0442-s018881 | reverse | revenue | 3 | pending |
| line-2 | line-2-0246-0611-s007011 | forward | spare | 1 | pending |
| line-2 | line-2-0246-0611-s007011 | reverse | spare | 1 | pending |
| line-2 | line-2-0341-0536-s010016 | forward | spare | 1 | pending |
| line-2 | line-2-0341-0536-s010016 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0598-0069-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0597-0344-s007019 | forward | revenue | 4 | pending |
| line-3 | line-3-0597-0344-s007019 | reverse | revenue | 3 | pending |
| line-3 | line-3-0563-0480-s010044 | forward | revenue | 3 | pending |
| line-3 | line-3-0563-0480-s010044 | reverse | revenue | 3 | pending |
| line-3 | line-3-0555-0583-s012336 | forward | revenue | 3 | pending |
| line-3 | line-3-0555-0583-s012336 | reverse | revenue | 3 | pending |
| line-3 | line-3-0503-0654-s014732 | forward | revenue | 3 | pending |
| line-3 | line-3-0503-0654-s014732 | reverse | revenue | 3 | pending |
| line-3 | line-3-0433-0712-s017123 | forward | revenue | 3 | pending |
| line-3 | line-3-0433-0712-s017123 | reverse | revenue | 3 | pending |
| line-3 | line-3-0404-0807-s019508 | reverse | revenue | 3 | pending |
| line-3 | line-3-0597-0344-s007019 | reverse | spare | 1 | pending |
| line-3 | line-3-0563-0480-s010044 | forward | spare | 1 | pending |
| line-3 | line-3-0563-0480-s010044 | reverse | spare | 1 | pending |
| line-3 | line-3-0555-0583-s012336 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**79 trainsets exceed the reference platform envelope**, requiring **4,700.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0278-0667-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0367-0647-s003022 | 8 | 2 | 6 | 357.0 |
| line-1-0489-0616-s006026 | 8 | 2 | 6 | 357.0 |
| line-1-0555-0583-s007706 | 7 | 4 | 3 | 178.5 |
| line-1-0603-0599-s009034 | 6 | 2 | 4 | 238.0 |
| line-1-0730-0541-s012054 | 6 | 2 | 4 | 238.0 |
| line-1-1072-0471-s019474 | 3 | 2 | 1 | 59.5 |
| line-2-0032-0601-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0246-0611-s007011 | 8 | 2 | 6 | 357.0 |
| line-2-0341-0536-s010016 | 8 | 2 | 6 | 357.0 |
| line-2-0469-0531-s013026 | 6 | 2 | 4 | 238.0 |
| line-2-0561-0517-s014982 | 6 | 2 | 4 | 238.0 |
| line-2-0636-0491-s016920 | 6 | 2 | 4 | 238.0 |
| line-2-0687-0442-s018881 | 3 | 2 | 1 | 59.5 |
| line-3-0404-0807-s019508 | 3 | 2 | 1 | 59.5 |
| line-3-0433-0712-s017123 | 6 | 2 | 4 | 238.0 |
| line-3-0503-0654-s014732 | 6 | 2 | 4 | 238.0 |
| line-3-0555-0583-s012336 | 7 | 4 | 3 | 178.5 |
| line-3-0563-0480-s010044 | 8 | 2 | 6 | 357.0 |
| line-3-0597-0344-s007019 | 8 | 2 | 6 | 357.0 |
| line-3-0598-0069-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Hillah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
