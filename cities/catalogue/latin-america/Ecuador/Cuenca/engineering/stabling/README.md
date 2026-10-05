# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 152 at depots = 188 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0708-0006-s021089 | line-1 | declared-depot | 53 | 3,153.5 | 9 |
| line-2-0080-1074-s000000 | line-2 | declared-depot | 52 | 3,094.0 | 9 |
| line-3-0365-0456-s000000 | line-3 | declared-depot | 47 | 2,796.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0451-0897-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0489-0766-s003015 | station | forward | revenue | 1 |
| line-1 | line-1-0489-0766-s003015 | station | reverse | revenue | 1 |
| line-1 | line-1-0517-0677-s005027 | station | forward | revenue | 1 |
| line-1 | line-1-0517-0677-s005027 | station | reverse | revenue | 1 |
| line-1 | line-1-0544-0589-s007034 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0589-s007034 | station | reverse | revenue | 1 |
| line-1 | line-1-0593-0430-s010643 | station | forward | revenue | 1 |
| line-1 | line-1-0593-0430-s010643 | station | reverse | revenue | 1 |
| line-1 | line-1-0708-0006-s021089 | station | reverse | revenue | 2 |
| line-2 | line-2-0080-1074-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0347-0644-s012127 | station | forward | revenue | 1 |
| line-2 | line-2-0347-0644-s012127 | station | reverse | revenue | 1 |
| line-2 | line-2-0427-0502-s015771 | station | forward | revenue | 1 |
| line-2 | line-2-0427-0502-s015771 | station | reverse | revenue | 1 |
| line-2 | line-2-0470-0428-s017666 | station | forward | revenue | 1 |
| line-2 | line-2-0470-0428-s017666 | station | reverse | revenue | 1 |
| line-2 | line-2-0512-0354-s019575 | station | reverse | revenue | 2 |
| line-3 | line-3-0365-0456-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0427-0502-s001797 | station | forward | revenue | 1 |
| line-3 | line-3-0427-0502-s001797 | station | reverse | revenue | 1 |
| line-3 | line-3-0468-0533-s003002 | station | forward | revenue | 1 |
| line-3 | line-3-0468-0533-s003002 | station | reverse | revenue | 1 |
| line-3 | line-3-0544-0589-s005197 | station | forward | revenue | 1 |
| line-3 | line-3-0544-0589-s005197 | station | reverse | revenue | 1 |
| line-3 | line-3-0610-0638-s007122 | station | forward | revenue | 1 |
| line-3 | line-3-0610-0638-s007122 | station | reverse | revenue | 1 |
| line-3 | line-3-0676-0687-s009036 | station | forward | revenue | 1 |
| line-3 | line-3-0676-0687-s009036 | station | reverse | revenue | 1 |
| line-3 | line-3-1025-0987-s019169 | station | reverse | revenue | 2 |
| line-1 | line-1-0708-0006-s021089 | depot | — | revenue | 47 |
| line-1 | line-1-0708-0006-s021089 | depot | — | spare | 5 |
| line-1 | line-1-0708-0006-s021089 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0080-1074-s000000 | depot | — | revenue | 46 |
| line-2 | line-2-0080-1074-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0080-1074-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0365-0456-s000000 | depot | — | revenue | 41 |
| line-3 | line-3-0365-0456-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0365-0456-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/cuenca-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **188 trainsets at 18 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **170 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **152 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0451-0897-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0489-0766-s003015 | forward | revenue | 6 | pending |
| line-1 | line-1-0489-0766-s003015 | reverse | revenue | 6 | pending |
| line-1 | line-1-0517-0677-s005027 | forward | revenue | 6 | pending |
| line-1 | line-1-0517-0677-s005027 | reverse | revenue | 6 | pending |
| line-1 | line-1-0544-0589-s007034 | forward | revenue | 6 | pending |
| line-1 | line-1-0544-0589-s007034 | reverse | revenue | 6 | pending |
| line-1 | line-1-0593-0430-s010643 | forward | revenue | 6 | pending |
| line-1 | line-1-0593-0430-s010643 | reverse | revenue | 6 | pending |
| line-1 | line-1-0708-0006-s021089 | reverse | revenue | 5 | pending |
| line-1 | line-1-0708-0006-s021089 | reverse | spare | 1 | pending |
| line-1 | line-1-0451-0897-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0489-0766-s003015 | forward | spare | 1 | pending |
| line-1 | line-1-0489-0766-s003015 | reverse | spare | 1 | pending |
| line-1 | line-1-0517-0677-s005027 | forward | spare | 1 | pending |
| line-1 | line-1-0517-0677-s005027 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0080-1074-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0347-0644-s012127 | forward | revenue | 7 | pending |
| line-2 | line-2-0347-0644-s012127 | reverse | revenue | 7 | pending |
| line-2 | line-2-0427-0502-s015771 | forward | revenue | 7 | pending |
| line-2 | line-2-0427-0502-s015771 | reverse | revenue | 7 | pending |
| line-2 | line-2-0470-0428-s017666 | forward | revenue | 7 | pending |
| line-2 | line-2-0470-0428-s017666 | reverse | revenue | 7 | pending |
| line-2 | line-2-0512-0354-s019575 | reverse | revenue | 7 | pending |
| line-2 | line-2-0080-1074-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0347-0644-s012127 | forward | spare | 1 | pending |
| line-2 | line-2-0347-0644-s012127 | reverse | spare | 1 | pending |
| line-2 | line-2-0427-0502-s015771 | forward | spare | 1 | pending |
| line-2 | line-2-0427-0502-s015771 | reverse | spare | 1 | pending |
| line-2 | line-2-0470-0428-s017666 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0365-0456-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0427-0502-s001797 | forward | revenue | 5 | pending |
| line-3 | line-3-0427-0502-s001797 | reverse | revenue | 5 | pending |
| line-3 | line-3-0468-0533-s003002 | forward | revenue | 5 | pending |
| line-3 | line-3-0468-0533-s003002 | reverse | revenue | 5 | pending |
| line-3 | line-3-0544-0589-s005197 | forward | revenue | 5 | pending |
| line-3 | line-3-0544-0589-s005197 | reverse | revenue | 5 | pending |
| line-3 | line-3-0610-0638-s007122 | forward | revenue | 4 | pending |
| line-3 | line-3-0610-0638-s007122 | reverse | revenue | 4 | pending |
| line-3 | line-3-0676-0687-s009036 | forward | revenue | 4 | pending |
| line-3 | line-3-0676-0687-s009036 | reverse | revenue | 4 | pending |
| line-3 | line-3-1025-0987-s019169 | reverse | revenue | 4 | pending |
| line-3 | line-3-0610-0638-s007122 | forward | spare | 1 | pending |
| line-3 | line-3-0610-0638-s007122 | reverse | spare | 1 | pending |
| line-3 | line-3-0676-0687-s009036 | forward | spare | 1 | pending |
| line-3 | line-3-0676-0687-s009036 | reverse | spare | 1 | pending |
| line-3 | line-3-1025-0987-s019169 | reverse | spare | 1 | pending |
| line-3 | line-3-0365-0456-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**144 trainsets exceed the reference platform envelope**, requiring **8,568.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0451-0897-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0489-0766-s003015 | 14 | 2 | 12 | 714.0 |
| line-1-0517-0677-s005027 | 14 | 2 | 12 | 714.0 |
| line-1-0544-0589-s007034 | 12 | 4 | 8 | 476.0 |
| line-1-0593-0430-s010643 | 12 | 2 | 10 | 595.0 |
| line-1-0708-0006-s021089 | 6 | 2 | 4 | 238.0 |
| line-2-0080-1074-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0347-0644-s012127 | 16 | 2 | 14 | 833.0 |
| line-2-0427-0502-s015771 | 16 | 4 | 12 | 714.0 |
| line-2-0470-0428-s017666 | 15 | 2 | 13 | 773.5 |
| line-2-0512-0354-s019575 | 7 | 2 | 5 | 297.5 |
| line-3-0365-0456-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0427-0502-s001797 | 10 | 4 | 6 | 357.0 |
| line-3-0468-0533-s003002 | 10 | 2 | 8 | 476.0 |
| line-3-0544-0589-s005197 | 10 | 4 | 6 | 357.0 |
| line-3-0610-0638-s007122 | 10 | 2 | 8 | 476.0 |
| line-3-0676-0687-s009036 | 10 | 2 | 8 | 476.0 |
| line-3-1025-0987-s019169 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/latin-america/Ecuador/Cuenca/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
